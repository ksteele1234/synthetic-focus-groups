from typing import List, Dict, Any
from .registry import get_backend

_backend = None

async def _ensure():
    global _backend
    if _backend is None:
        _backend = get_backend()
        await _backend.init()
    return _backend

async def index(study_id: str, msg_id: str, embedding: List[float], meta: Dict[str, Any]):
    v = await _ensure()
    await v.create_collection(f"study_{study_id}", dim=len(embedding))
    await v.upsert(f"study_{study_id}", [(msg_id, embedding, meta)])

async def search(study_id: str, embedding: List[float], top_k: int = 5):
    v = await _ensure()
    return await v.query(f"study_{study_id}", embedding, top_k=top_k)

