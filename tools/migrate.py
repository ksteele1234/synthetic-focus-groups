import os, glob, asyncpg, asyncio, pathlib

DB_URL = os.getenv("DATABASE_URL")
MIG_DIR = pathlib.Path("migrations")

async def main():
    if not DB_URL:
        raise SystemExit("DATABASE_URL not set")
    con = await asyncpg.connect(DB_URL)
    try:
        for path in sorted(glob.glob(str(MIG_DIR / "*.sql"))):
            sql = open(path, encoding="utf-8").read()
            print(f"Applying {path} ...")
            await con.execute(sql)
        print("✅ migrations applied")
    finally:
        await con.close()

if __name__ == "__main__":
    asyncio.run(main())
