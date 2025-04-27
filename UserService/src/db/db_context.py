# src/db/context.py
from typing import Callable, AsyncGenerator, Any
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from .settings import get_settings, DatabaseType

# Type for a dependency that yields a value
ContextDependency = Callable[..., AsyncGenerator[Any, None]]

def get_db_context() -> ContextDependency:
    """
    Returns the appropriate database context dependency based on configuration.
    For PostgreSQL: Returns a dependency that yields a database session
    For DynamoDB: Returns a dependency that yields None
    """
    settings = get_settings()
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        # Return the PostgreSQL session dependency
        async def get_postgres_context() -> AsyncGenerator[AsyncSession, None]:
            async with AsyncSessionLocal() as session:
                yield session
        return get_postgres_context
    else:
        # Return a null context for DynamoDB (no session needed)
        async def get_dynamo_context() -> AsyncGenerator[None, None]:
            yield None
        return get_dynamo_context

# Create the context dependency based on current configuration
db_context = get_db_context()