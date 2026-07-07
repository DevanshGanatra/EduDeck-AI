import asyncio
from sqlalchemy import text
from app.db.session import engine

async def migrate():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS vectorized_chunks INTEGER NOT NULL DEFAULT 0;"))
            print("vectorized_chunks column added (or already existed).")
        except Exception as e:
            print(f"Migration note: {e}")

asyncio.run(migrate())
