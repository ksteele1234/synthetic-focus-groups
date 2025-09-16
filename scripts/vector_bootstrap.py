#!/usr/bin/env python3
"""
Bootstrap and demo commands for the vector backend (pgvector).

Usage (example):
  # Set env: DATABASE_URL=postgresql://user:pass@localhost:5432/yourdb
  py scripts\vector_bootstrap.py init
  py scripts\vector_bootstrap.py index_demo
  py scripts\vector_bootstrap.py search_demo "time saving automation"
"""
import os
import sys
import asyncio
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.vector.registry import get_backend

async def cmd_init():
    v = get_backend()
    await v.init()
    # Create a default collection for demos (384 dim typical for MiniLM)
    await v.create_collection('personas_demo', dim=384)
    print('Initialized vector backend and created collection personas_demo')

async def _fake_embed(text: str, dim: int = 384) -> List[float]:
    # Placeholder embedding generator for demo purposes
    import random
    random.seed(abs(hash(text)) % (2**32))
    return [random.random() for _ in range(dim)]

async def cmd_index_demo():
    v = get_backend()
    await v.init()
    await v.create_collection('personas_demo', dim=384)
    items = [
        ('sarah', await _fake_embed('Integrated tooling and predictable acquisition'), {'name':'Sarah','summary':'Agency owner needs integrated tooling and predictable acquisition'}),
        ('mike', await _fake_embed('Attribution clarity and CRM integration'), {'name':'Mike','summary':'Marketing manager needs attribution clarity and CRM integration'}),
        ('jenny', await _fake_embed('Automated client reporting and stable retainers'), {'name':'Jenny','summary':'Freelancer needs automated reporting and stable retainers'})
    ]
    await v.upsert('personas_demo', [(i[0], i[1], i[2]) for i in items])
    print('Indexed demo items into personas_demo')

async def cmd_search_demo(query: str):
    v = get_backend()
    await v.init()
    vec = await _fake_embed(query)
    results = await v.query('personas_demo', vec, top_k=3)
    for _id, score, meta in results:
        print(f'{_id}: score={score:.3f} meta={meta}')

async def amain(argv: List[str]):
    if not argv or argv[0] in ('-h','--help'):
        print(__doc__)
        return
    cmd = argv[0]
    if cmd == 'init':
        await cmd_init()
    elif cmd == 'index_demo':
        await cmd_index_demo()
    elif cmd == 'search_demo':
        q = ' '.join(argv[1:]) or 'automation'
        await cmd_search_demo(q)
    else:
        print('Unknown command')

if __name__ == '__main__':
    asyncio.run(amain(sys.argv[1:]))
