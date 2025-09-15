import os
from .backend_pgvector import PgVector

def get_backend():
    provider = os.getenv("VECTOR_PROVIDER", "pgvector").lower()
    if provider == "pgvector":
        return PgVector()
    raise ValueError(f"Unsupported VECTOR_PROVIDER={provider}")
