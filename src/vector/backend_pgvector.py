import os, json, asyncpg
from typing import List, Optional, Tuple
from .interface import VectorBackend

# Required env var: postgresql://user:pass@host:5432/db
DB_URL = os.getenv("DATABASE_URL")

class PgVector(VectorBackend):
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None
        # default ops use cosine distance; adjust in _ensure_table if you prefer ip/l2
        self.ops_class = "vector_cosine_ops"

    async def init(self) -> None:
        if not DB_URL:
            raise RuntimeError("DATABASE_URL not set")
        self.pool = await asyncpg.create_pool(DB_URL)

    async def _ensure_table(self, collection: str, dim: int) -> None:
        # NOTE: you must enable pgvector in your DB once:
        #   CREATE EXTENSION IF NOT EXISTS vector;
        # Tables are created lazily per collection.
        q = f"""
        CREATE TABLE IF NOT EXISTS "{collection}" (
          id   TEXT PRIMARY KEY,
          embedding vector({dim}) NOT NULL,
          meta JSONB
        );
        CREATE INDEX IF NOT EXISTS "idx_{collection}_embedding"
          ON "{collection}" USING ivfflat (embedding {self.ops_class});
        """
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            await con.execute(q)

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
        dim = len(items[0][1])
        await self._ensure_table(collection, dim)
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            async with con.transaction():
                for _id, vec, meta in items:
                    await con.execute(
                        f'INSERT INTO "{collection}" (id, embedding, meta) '
                        f'VALUES ($1, $2, $3) '
                        f'ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding, meta = EXCLUDED.meta',
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
        # cosine similarity = 1 - cosine distance (<=>)
        # For l2/ip you’d adjust formula; here we use the operator and return a similarity-style score.
        where = ""
        params = [vector, top_k]
        if filter:
            where = "WHERE meta @> $3::jsonb"
            params.append(json.dumps(filter))
        q = (
            f'SELECT id, 1 - (embedding <=> $1) AS score, meta '
            f'FROM "{collection}" {where} '
            f'ORDER BY embedding <=> $1 LIMIT $2'
        )
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            rows = await con.fetch(q, *params)
        return [
            (r["id"], float(r["score"]), dict(r["meta"]) if r["meta"] is not None else None)
            for r in rows
        ]

    async def delete(self, collection: str, ids: List[str]) -> int:
        if not ids:
            return 0
        q = f'DELETE FROM "{collection}" WHERE id = ANY($1::text[])'
        async with self.pool.acquire() as con:  # type: ignore[arg-type]
            res = await con.execute(q, ids)
        # res looks like "DELETE 3"
        try:
            return int(res.split()[-1])
        except Exception:
            return 0


