import os, pytest, asyncio
os.environ.setdefault("VECTOR_PROVIDER","pgvector")
# Ensure DATABASE_URL is set in your test env (Postgres with pgvector)

from vector.registry import get_backend

@pytest.mark.asyncio
async def test_pgvector_roundtrip():
    v = get_backend()
    await v.init()
    await v.create_collection("t_coll", dim=3)
    await v.upsert("t_coll", [("m1", [0.1,0.2,0.3], {"k":"v"})])
    out = await v.query("t_coll", [0.1,0.2,0.3], top_k=1)
    assert out and out[0][0] == "m1"
    n = await v.delete("t_coll", ["m1"])
    assert n == 1

