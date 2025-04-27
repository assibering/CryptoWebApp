# import asyncio
# import os
# import pytest
# from httpx import AsyncClient, ASGITransport
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# from src.db.database import Base
# from src.db.dependencies import get_async_db
# from src.main import app

# # Use test database URL from environment
# POSTGRES_DATABASE_URL_FOR_TESTING = os.getenv("POSTGRES_DATABASE_URL_FOR_TESTING")

# # Create test engine
# test_engine = create_async_engine(POSTGRES_DATABASE_URL_FOR_TESTING, echo=True)
# TestAsyncSessionLocal = async_sessionmaker(
#     bind=test_engine,
#     expire_on_commit=False,
#     class_=AsyncSession
# )

# @pytest.fixture(scope="session")
# async def setup_database():
#     """Set up the test database."""
#     # Create all tables
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
    
#     yield
    
#     # Clean up after tests
#     async with test_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

# @pytest.fixture
# async def db_session(setup_database):
#     """Create a fresh database session for each test."""
#     async with TestAsyncSessionLocal() as session:
#         # Start a nested transaction
#         async with session.begin():
#             # Use the session
#             yield session
#             # The transaction is automatically rolled back when the context exits

# @pytest.fixture
# async def db_session():
#     """Create a fresh database session for each test."""
#     connection = await test_engine.connect()
#     transaction = await connection.begin()
    
#     session = AsyncSession(bind=connection, expire_on_commit=False)
    
#     try:
#         yield session
#     finally:
#         await session.close()
#         await transaction.rollback()
#         await connection.close()

# # Override the get_async_db dependency for testing
# async def override_get_async_db():
#     async with TestAsyncSessionLocal() as session:
#         yield session

# @pytest.fixture
# async def async_client(setup_database):
#     """Create an async client for testing the API."""
#     # Get the current running loop if needed
#     loop = asyncio.get_running_loop()
#     # Override the dependency
#     app.dependency_overrides[get_async_db] = override_get_async_db
    
#     # Create the test client
#     transport = ASGITransport(app=app)
#     async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
#         yield client
    
#     # Clean up
#     app.dependency_overrides.clear()

import asyncio
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import boto3

from src.db.database import Base
from src.db.db_context import db_context
from src.main import app
from src.db.settings import get_settings, DatabaseType
from src.dependencies import get_user_repository

# Load settings
settings = get_settings()

# Setup for PostgreSQL test database
POSTGRES_DATABASE_URL_FOR_TESTING = os.getenv("POSTGRES_DATABASE_URL_FOR_TESTING")

if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
    test_engine = create_async_engine(POSTGRES_DATABASE_URL_FOR_TESTING, echo=True)
    TestAsyncSessionLocal = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    @pytest.fixture(scope="session")
    async def setup_database():
        """Set up the test database."""
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @pytest.fixture
    async def db_session(setup_database):
        """Create a fresh database session for each test."""
        async with TestAsyncSessionLocal() as session:
            async with session.begin():
                yield session

    # Override the db_context dependency for testing
    async def override_db_context():
        async with TestAsyncSessionLocal() as session:
            yield session

else:
    # For DynamoDB, setup boto3 client and table cleanup if needed
    @pytest.fixture(scope="session")
    def dynamodb_client():
        settings = get_settings()
        client = boto3.client(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT
        )
        yield client

    @pytest.fixture(scope="session")
    def setup_dynamodb_table(dynamodb_client):
        # Here you can add logic to create or clean up DynamoDB tables if needed
        # For example, delete all items or recreate the table
        yield

    @pytest.fixture
    def db_session():
        # DynamoDB does not use SQL sessions, so yield None or a mock if needed
        yield None

    async def override_db_context():
        # For DynamoDB, no async db session is needed
        yield None

# Async client fixture
@pytest.fixture
async def async_client():
    """Create an async client for testing the API."""
    # Override the db_context dependency
    app.dependency_overrides[db_context] = override_db_context
    
    # You can also directly override the repository for more control
    # For example, to use a mock repository:
    # app.dependency_overrides[get_user_repository] = lambda: mock_user_repository

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client

    app.dependency_overrides.clear()
