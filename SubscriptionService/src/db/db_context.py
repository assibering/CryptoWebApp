# src/db/context.py
from typing import Callable, AsyncGenerator, Any
from sqlalchemy.ext.asyncio import AsyncSession
from .settings import get_settings, DatabaseType
from botocore.config import Config
from types_aiobotocore_dynamodb import DynamoDBClient
from fastapi import Request


# Type for a dependency that yields a value
ContextDependency = Callable[..., AsyncGenerator[Any, None]]

def get_db_context() -> ContextDependency:
    """
    Returns the appropriate database context dependency based on configuration.
    For PostgreSQL: Returns a dependency that yields a database session
    For DynamoDB: Returns a dependency that yields a DynamoDB resource
    """
    settings = get_settings()
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        # Return the PostgreSQL session dependency
        async def get_postgres_context(request: Request) -> AsyncGenerator[AsyncSession, None]:
            async_session_factory = request.app.state.postgres_session
            async with async_session_factory() as session:
                try:
                    yield session
                    await session.commit()  # Automatically commit if no exceptions
                except Exception:
                    await session.rollback()  # Rollback on exceptions
                    raise
        return get_postgres_context
    elif settings.DATABASE_TYPE == DatabaseType.DYNAMODB:
        # Return a DynamoDB context using the app-wide session
        async def get_dynamo_context(request: Request) -> AsyncGenerator[DynamoDBClient, None]:
            # Get the session from app state
            session = request.app.state.dynamodb_session
            
            # Create a client for this request using the shared session
            async with session.client(
                'dynamodb',
                endpoint_url=settings.AWS_ENDPOINT,
                config=Config(
                    connect_timeout=5.0,
                    read_timeout=10.0,
                    retries={'max_attempts': 3}
                )
            ) as dynamodb_client:
                dynamodb_client: DynamoDBClient
                yield dynamodb_client
        
        return get_dynamo_context
    else:
        raise ValueError("Invalid DATABASE_TYPE")

# Create the context dependency based on current configuration
db_context = get_db_context()

# Session for Kafka
async def get_db_session_for_background():
    """Creates a database session for background tasks like Kafka consumers"""
    settings = get_settings()
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        
        # Create engine and session factory
        engine = create_async_engine(settings.POSTGRES_DATABASE_URL)
        async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
        
        # Create and return a session
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    elif settings.DATABASE_TYPE == DatabaseType.DYNAMODB:
        import aioboto3
        session = aioboto3.Session()
        
        async with session.client(
            'dynamodb',
            endpoint_url=settings.AWS_ENDPOINT,
            config=Config(
                connect_timeout=5.0,
                read_timeout=10.0,
                retries={'max_attempts': 3}
            )
        ) as dynamodb_client:
            yield dynamodb_client
    else:
        raise ValueError("Invalid DATABASE_TYPE")

