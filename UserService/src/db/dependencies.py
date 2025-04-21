from .database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session