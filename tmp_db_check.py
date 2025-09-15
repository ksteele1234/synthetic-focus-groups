import os, asyncio, asyncpg

url = os.environ.get('DATABASE_URL')

async def main():
    con = await asyncpg.connect(url)
    val = await con.fetchval('select 1')
    await con.close()
    print('DB OK:', val)

asyncio.run(main())
