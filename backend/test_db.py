import asyncio
import app.models # this should trigger __init__.py
from app.db.session import engine
from sqlalchemy.orm import configure_mappers

async def test_db():
    print("Configuring mappers...")
    configure_mappers()
    print("Mappers configured successfully!")
    print("Connecting to DB...")
    async with engine.begin() as conn:
        print("Connected successfully!")

if __name__ == "__main__":
    asyncio.run(test_db())
