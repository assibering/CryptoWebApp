import asyncio
import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.db.database import Base
from src.db.dependencies import get_async_db
from src.main import app

# Use test database URL from environment
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest.fixture(scope="session")
async def setup_database():
    """Set up the test database."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Clean up after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_database):
    """Create a fresh database session for each test."""
    async with TestAsyncSessionLocal() as session:
        # Start a nested transaction
        async with session.begin():
            # Use the session
            yield session
            # The transaction is automatically rolled back when the context exits

@pytest.fixture
async def db_session():
    """Create a fresh database session for each test."""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    session = AsyncSession(bind=connection, expire_on_commit=False)
    
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()

# Override the get_async_db dependency for testing
async def override_get_async_db():
    async with TestAsyncSessionLocal() as session:
        yield session

@pytest.fixture
async def async_client(setup_database):
    """Create an async client for testing the API."""
    # Get the current running loop if needed
    loop = asyncio.get_running_loop()
    # Override the dependency
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    # Create the test client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()