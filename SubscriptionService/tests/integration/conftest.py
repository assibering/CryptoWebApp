import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from types_aiobotocore_dynamodb import DynamoDBClient
from sqlalchemy import text
import boto3
import aioboto3

from src.repository.implementations.PostgreSQL.models.ORM_Subscription import Base
from src.db.db_context import db_context
from src.main import app
from src.db.settings import get_settings, DatabaseType


# Load settings
settings = get_settings()

# Define override_db_context at module level - will be set properly later
async def override_db_context():
    yield None

if settings.DATABASE_TYPE == DatabaseType.POSTGRES:

    test_engine = create_async_engine(settings.POSTGRES_DATABASE_URL_FOR_TESTING, echo=True)
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
        # Clear tables instead of dropping them
        async with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(text('TRUNCATE TABLE auth.subscriptions CASCADE'))

    @pytest.fixture
    async def db_session(setup_database):
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

    # Override the module-level function
    async def postgresql_context():
        async with TestAsyncSessionLocal() as session:
            yield session
    
    # Set the module-level function
    override_db_context = postgresql_context

elif settings.DATABASE_TYPE == DatabaseType.DYNAMODB:
    # Simple synchronous client for test cleanup
    @pytest.fixture(scope="session")
    def dynamodb_client():
        client = boto3.client(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID_FOR_TESTING,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_FOR_TESTING,
            region_name=settings.AWS_REGION_FOR_TESTING,
            endpoint_url=settings.AWS_ENDPOINT_FOR_TESTING
        )
        return client

    def cleanup_dynamodb_table(client, table_name):
        """Clean up all items in a DynamoDB table one by one."""
        try:
            # Scan to get all items
            response = client.scan(TableName=table_name)
            items = response.get('Items', [])
            
            if not items:
                return
            
            # Delete each item individually
            for item in items:
                client.delete_item(
                    TableName=table_name,
                    Key={'email': item['email']}
                )
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    @pytest.fixture(scope="session")
    def setup_database(dynamodb_client):
        # Table name
        table_name = "subscriptions"
        yield
        # Clean up after tests
        cleanup_dynamodb_table(dynamodb_client, table_name)

    @pytest.fixture
    def db_session():
        # DynamoDB does not use SQL sessions
        yield None

    # This is the key part - make sure it matches how your app expects to receive the client
    async def dynamodb_context():

        # Create a session specifically for testing
        test_session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID_FOR_TESTING,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_FOR_TESTING, 
            region_name=settings.AWS_REGION_FOR_TESTING
        )

        # Create a client using context manager
        async with test_session.client(
            'dynamodb',
            endpoint_url=settings.AWS_ENDPOINT_FOR_TESTING
        ) as client:
            # This client will be injected into your routes
            client: DynamoDBClient
            yield client
    
    # Set the module-level function
    override_db_context = dynamodb_context

else:
    raise ValueError(f"Invalid DATABASE_TYPE: {settings.DATABASE_TYPE}. Must be one of {[e.value for e in DatabaseType]}")

# Async client fixture
@pytest.fixture
async def async_client(setup_database):
    """Create an async client for testing the API."""

    # Override the db_context dependency
    app.dependency_overrides[db_context] = override_db_context
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        yield client

    # Clear all overrides
    app.dependency_overrides.clear()

