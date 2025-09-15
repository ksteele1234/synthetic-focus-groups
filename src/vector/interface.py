from typing import List, Optional, Protocol, Tuple

class VectorBackend(Protocol):
    async def init(self) -> None: ...
    async def create_collection(self, collection: str, dim: int, metric: str = "cosine") -> None: ...
    async def upsert(
        self,
        collection: str,
        items: List[Tuple[str, List[float], Optional[dict]]],
    ) -> None: ...
    async def query(
        self,
        collection: str,
        vector: List[float],
        top_k: int = 10,
        filter: Optional[dict] = None,
    ) -> List[Tuple[str, float, Optional[dict]]]: ...
    async def delete(self, collection: str, ids: List[str]) -> int: ...

