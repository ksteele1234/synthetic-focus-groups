from typing import Optional
from .backend_pgvector import PgVector

_backend_singleton: Optional[PgVector] = None

def get_backend() -> PgVector:
    global _backend_singleton
    if _backend_singleton is None:
        _backend_singleton = PgVector()
    return _backend_singleton
