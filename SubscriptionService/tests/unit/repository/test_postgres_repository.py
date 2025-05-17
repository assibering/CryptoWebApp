import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# Fixtures
@pytest.fixture
def mock_db():
    """Create a mock AsyncSession for testing."""
    mock = AsyncMock(spec=AsyncSession)
    # Setup the async context manager for begin()
    context_manager = AsyncMock()
    mock.begin.return_value = context_manager
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
        is_active=True
    )

@pytest.fixture
def sample_outbox():
    """Create a sample Outbox schema for testing."""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.Outbox(
        aggregatetype = "subscription",
        aggregateid = "1_unique_id",
        eventtype_prefix = "subscription_created",
        payload = {
            "subscription_id": "1_unique_id",
            "email": "test@example.com",
        }
    )

@pytest.fixture
def db_subscription():
    """Create a sample SubscriptionORM object that would be returned from the database."""
    from src.repository.implementations.PostgreSQL.models.ORM_Subscription import SubscriptionORM
    subscription = MagicMock(spec=SubscriptionORM)
    subscription.subscription_id = "1_unique_id"
    subscription.subscription_type = "free_tier"
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
async def test_create_subscription_success(subscription_repo, mock_db, sample_subscription, sample_outbox):
    """Test successful subscription creation."""
    # Call the method
    await subscription_repo.create_subscription(sample_subscription, sample_outbox)
    
    # Verify that begin() was called for the transaction
    mock_db.begin.assert_called_once()
    
    # Verify that add() was called twice (subscription + outbox event)
    assert mock_db.add.call_count == 2

@pytest.mark.asyncio
async def test_create_subscription_already_exists(subscription_repo, mock_db, sample_subscription, sample_outbox):
    """Test subscription already exists scenario."""
    # Import inside test function
    from src.exceptions import ResourceAlreadyExistsException
    
    # Setup mock to raise IntegrityError with UniqueViolationError
    unique_violation = Exception("UniqueViolationError")
    integrity_error = IntegrityError("statement", "params", unique_violation)
    integrity_error.orig = unique_violation
    
    # Make the first transaction fail
    first_context = AsyncMock()
    first_context.__aenter__.return_value = None
    first_context.__aexit__.side_effect = integrity_error
    
    # Make the second transaction (for failure event) succeed
    second_context = AsyncMock()
    second_context.__aenter__.return_value = None
    second_context.__aexit__.return_value = None
    
    # Configure mock_db.begin() to return different context managers on consecutive calls
    mock_db.begin.side_effect = [first_context, second_context]
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceAlreadyExistsException) as exc_info:
        await subscription_repo.create_subscription(sample_subscription, sample_outbox)
    
    assert "already exists" in str(exc_info.value)
    
    # Verify begin() was called twice (initial attempt + failure event)
    assert mock_db.begin.call_count == 2
    
    # Verify add() was called twice (initial subscription + outbox) and once more for failure event
    assert mock_db.add.call_count == 3

@pytest.mark.asyncio
async def test_create_subscription_other_integrity_error(subscription_repo, mock_db, sample_subscription, sample_outbox):
    """Test other integrity error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a different kind of IntegrityError
    other_error = Exception("Other constraint violation")
    integrity_error = IntegrityError("statement", "params", other_error)
    integrity_error.orig = other_error
    
    # Make the first transaction fail
    first_context = AsyncMock()
    first_context.__aenter__.return_value = None
    first_context.__aexit__.side_effect = integrity_error
    
    # Make the second transaction (for failure event) succeed
    second_context = AsyncMock()
    second_context.__aenter__.return_value = None
    second_context.__aexit__.return_value = None
    
    # Configure mock_db.begin() to return different context managers on consecutive calls
    mock_db.begin.side_effect = [first_context, second_context]
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await subscription_repo.create_subscription(sample_subscription, sample_outbox)
    
    assert "Database integrity error" in str(exc_info.value)
    
    # Verify begin() was called twice (initial attempt + failure event)
    assert mock_db.begin.call_count == 2
    
    # Verify add() was called twice (initial subscription + outbox) and once more for failure event
    assert mock_db.add.call_count == 3

@pytest.mark.asyncio
async def test_create_subscription_general_exception(subscription_repo, mock_db, sample_subscription, sample_outbox):
    """Test general exception handling during subscription creation."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a general exception
    general_error = Exception("Unexpected error")
    
    # Make the first transaction fail
    first_context = AsyncMock()
    first_context.__aenter__.return_value = None
    first_context.__aexit__.side_effect = general_error
    
    # Make the second transaction (for failure event) succeed
    second_context = AsyncMock()
    second_context.__aenter__.return_value = None
    second_context.__aexit__.return_value = None
    
    # Configure mock_db.begin() to return different context managers on consecutive calls
    mock_db.begin.side_effect = [first_context, second_context]
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await subscription_repo.create_subscription(sample_subscription, sample_outbox)
    
    assert "Internal database error" in str(exc_info.value)
    
    # Verify begin() was called twice (initial attempt + failure event)
    assert mock_db.begin.call_count == 2
    
    # Verify add() was called twice (initial subscription + outbox) and once more for failure event
    assert mock_db.add.call_count == 3