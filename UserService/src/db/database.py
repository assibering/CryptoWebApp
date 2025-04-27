from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

POSTGRES_DATABASE_URL = os.getenv("POSTGRES_DATABASE_URL")


# Create an async engine
engine = create_async_engine(POSTGRES_DATABASE_URL, echo=True, future=True)

# Create an async sessionmaker factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # optional: objects stay active after commit
    class_=AsyncSession
)

# ORM Base class
Base = declarative_base()