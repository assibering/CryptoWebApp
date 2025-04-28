import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# Fixtures
@pytest.fixture
def mock_db():
    """Create a mock AsyncSession for testing."""
    mock = AsyncMock(spec=AsyncSession)
    return mock

@pytest.fixture
def subscription_repo(mock_db):
    """Create a SubscriptionRepository instance with a mock db."""
    from src.repository.implementations.PostgreSQL.postgres_SubscriptionRepository import SubscriptionRepository
    return SubscriptionRepository(db=mock_db)

@pytest.fixture
def sample_subscription():
    """Create a sample Subscription schema for testing."""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.Subscription(
        subscription_id="1_unique_id",
        subscription_type="free_tier",
        email="test@example.com",
        is_active = True
    )

@pytest.fixture
def db_subscription():
    """Create a sample SubscriptionORM object that would be returned from the database."""
    from src.repository.implementations.PostgreSQL.models.ORM_Subscription import SubscriptionORM
    subscription = MagicMock(spec=SubscriptionORM)
    subscription.subscription_id = "1_unique_id"
    subscription.subscription_type= "free_tier"
    subscription.email = "test@example.com"
    subscription.is_active = True
    return subscription

# Tests for get_subscribtion method
@pytest.mark.asyncio
async def test_get_subscription_success(subscription_repo, mock_db, db_subscription):
    """Test successful subscription retrieval."""
    # Import inside test function to avoid early import
    from src.schemas import SubscriptionSchemas
    
    # Setup mock to return a subscription
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = db_subscription
    mock_db.execute.return_value = mock_result
    
    # Call the method
    subscription = await subscription_repo.get_subscription("1_unique_id")
    
    # Assertions
    assert subscription.subscription_id == "1_unique_id"
    assert subscription.subscription_type == "free_tier"
    assert subscription.email == "test@example.com"
    assert subscription.is_active is True
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_subscription_not_found(subscription_repo, mock_db):
    """Test subscription not found scenario."""
    # Import inside test function
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to return None (subscription not found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await subscription_repo.get_subscription("nonexistent_id")
    
    assert "not found" in str(exc_info.value)
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_subscription_database_error(subscription_repo, mock_db):
    """Test database error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise an exception
    mock_db.execute.side_effect = Exception("Database connection error")
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await subscription_repo.get_subscription("2_unique_id")
    
    assert "Internal database error" in str(exc_info.value)
    mock_db.execute.assert_called_once()

# Tests for create_subscription method
@pytest.mark.asyncio
async def test_create_subscription_success(subscription_repo, mock_db, sample_subscription):
    """Test successful subscription creation."""

    # Call the method
    result = await subscription_repo.create_subscription(sample_subscription)
    
    # Assertions
    assert result.subscription_type == sample_subscription.subscription_type 
    assert result.email == sample_subscription.email
    assert result.is_active == True
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_subscription_general_exception(subscription_repo, mock_db, sample_subscription):
    """Test general exception handling during subscription creation."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a general exception
    mock_db.commit.side_effect = Exception("Unexpected error")
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await subscription_repo.create_subscription(sample_subscription)
    
    assert "Internal database error" in str(exc_info.value)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

