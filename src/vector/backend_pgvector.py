import os, json, asyncpg
from typing import List, Optional, Tuple
from .interface import VectorBackend
import logging
from urllib.parse import urlparse

# Security: Validate DATABASE_URL format and credentials
def _validate_db_url(url: str) -> None:
    """Validate database URL format and security requirements."""
    if not url:
        raise ValueError("DATABASE_URL is required")
    
    parsed = urlparse(url)
    if parsed.scheme != "postgresql":
        raise ValueError("Only PostgreSQL connections supported")
    
    if not parsed.hostname:
        raise ValueError("Database hostname required")
    
    if not parsed.username or not parsed.password:
        raise ValueError("Database credentials required")
    
    # Security: Warn about localhost in production
    if parsed.hostname not in ["localhost", "127.0.0.1"] and not url.startswith("postgresql://"):
        logging.warning("Using non-localhost database connection")

DB_URL = os.getenv("DATABASE_URL")
if DB_URL:
    _validate_db_url(DB_URL)

class PgVector(VectorBackend):
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None
        # default ops use cosine distance; adjust in _ensure_table if you prefer ip/l2
        self.ops_class = "vector_cosine_ops"

    async def init(self) -> None:
        if not DB_URL:
            raise RuntimeError("DATABASE_URL not set")
        
        # Security: Create connection pool with security settings
        self.pool = await asyncpg.create_pool(
            DB_URL,
            min_size=1,
            max_size=10,
            max_queries=50000,
            max_inactive_connection_lifetime=300.0,  # 5 minutes
            command_timeout=60.0,  # 1 minute timeout
            server_settings={
                'application_name': 'synthetic_focus_groups_vector',
                'jit': 'off'  # Disable JIT for security
            }
        )
        
        # Verify vector extension is available
        async with self.pool.acquire() as con:
            try:
                await con.execute('SELECT 1::vector')
            except Exception as e:
                raise RuntimeError(f"pgvector extension not available: {e}")

    async def _ensure_table(self, collection: str, dim: int) -> None:
        # NOTE: you must enable pgvector in your DB once:
        #   CREATE EXTENSION IF NOT EXISTS vector;
        # Tables are created lazily per collection.
        
        # Security: Validate collection name to prevent SQL injection
        if not collection.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid collection name: {collection}. Only alphanumeric, underscore, and hyphen allowed.")
        
        if not (1 <= dim <= 2048):  # Reasonable embedding dimension limits
            raise ValueError(f"Invalid dimension: {dim}. Must be between 1 and 2048.")
        
        # Security: Use parameterized queries with validated identifiers
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            # Create table with parameterized dimension
            await con.execute(
                f'CREATE TABLE IF NOT EXISTS {asyncpg.utils._quote_ident(collection)} ('
                '  id TEXT PRIMARY KEY,'
                f'  embedding vector({dim}) NOT NULL,'
                '  meta JSONB'
                ')'
            )
            # Create index with validated identifiers
            await con.execute(
                f'CREATE INDEX IF NOT EXISTS {asyncpg.utils._quote_ident(f"idx_{collection}_embedding")} '
                f'ON {asyncpg.utils._quote_ident(collection)} '
                f'USING ivfflat (embedding {self.ops_class})'
            )

    async def create_collection(self, collection: str, dim: int, metric: str = "cosine") -> None:
        # You can switch ops class per collection if you want different metrics
        if metric == "cosine":
            self.ops_class = "vector_cosine_ops"
        elif metric in ("l2", "euclidean"):
            self.ops_class = "vector_l2_ops"
        elif metric in ("ip", "inner_product", "dot"):
            self.ops_class = "vector_ip_ops"
        else:
            raise ValueError(f"Unsupported metric: {metric}")
        await self._ensure_table(collection, dim)

    async def upsert(
        self,
        collection: str,
        items: List[Tuple[str, List[float], Optional[dict]]],
    ) -> None:
        if not items:
            return
        
        # Security: Validate inputs
        if not collection.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid collection name: {collection}")
        
        dim = len(items[0][1])
        await self._ensure_table(collection, dim)
        
        # Security: Use parameterized queries with quoted identifiers
        table_name = asyncpg.utils._quote_ident(collection)
        query = (
            f'INSERT INTO {table_name} (id, embedding, meta) '
            'VALUES ($1, $2, $3) '
            'ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding, meta = EXCLUDED.meta'
        )
        
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            async with con.transaction():
                for _id, vec, meta in items:
                    # Security: Validate vector dimensions
                    if len(vec) != dim:
                        raise ValueError(f"Vector dimension mismatch: expected {dim}, got {len(vec)}")
                    
                    await con.execute(
                        query,
                        _id,
                        vec,  # asyncpg maps list[float] -> pgvector
                        json.dumps(meta or {}, ensure_ascii=False),
                    )

    async def query(
        self,
        collection: str,
        vector: List[float],
        top_k: int = 10,
        filter: Optional[dict] = None,
    ) -> List[Tuple[str, float, Optional[dict]]]:
        # Security: Validate inputs
        if not collection.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid collection name: {collection}")
        
        if not (1 <= top_k <= 1000):  # Reasonable limit
            raise ValueError(f"Invalid top_k: {top_k}. Must be between 1 and 1000.")
        
        if not vector or not all(isinstance(x, (int, float)) for x in vector):
            raise ValueError("Vector must be a non-empty list of numbers")
        
        # Security: Use parameterized queries with quoted identifiers
        table_name = asyncpg.utils._quote_ident(collection)
        where_clause = ""
        params = [vector, top_k]
        
        if filter:
            where_clause = "WHERE meta @> $3::jsonb"
            params.append(json.dumps(filter, ensure_ascii=False))
        
        # cosine similarity = 1 - cosine distance (<=>)
        # For l2/ip you'd adjust formula; here we use the operator and return a similarity-style score.
        query = (
            f'SELECT id, 1 - (embedding <=> $1) AS score, meta '
            f'FROM {table_name} {where_clause} '
            f'ORDER BY embedding <=> $1 LIMIT $2'
        )
        
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            rows = await con.fetch(query, *params)
        
        return [
            (r["id"], float(r["score"]), dict(r["meta"]) if r["meta"] is not None else None)
            for r in rows
        ]

    async def delete(self, collection: str, ids: List[str]) -> int:
        if not ids:
            return 0
        
        # Security: Validate inputs
        if not collection.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid collection name: {collection}")
        
        if len(ids) > 1000:  # Reasonable batch limit
            raise ValueError(f"Too many IDs to delete: {len(ids)}. Maximum 1000 allowed.")
        
        # Security: Use parameterized queries with quoted identifiers
        table_name = asyncpg.utils._quote_ident(collection)
        query = f'DELETE FROM {table_name} WHERE id = ANY($1::text[])'
        
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            res = await con.execute(query, ids)
        
        # res looks like "DELETE 3"
        try:
            return int(res.split()[-1])
        except (ValueError, IndexError, AttributeError):
            logging.warning(f"Could not parse delete result: {res}")
            return 0


