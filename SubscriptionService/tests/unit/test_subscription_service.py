import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def subscription_service():
    """Create a UserService with a mocked repository."""
    from src.service.SubscriptionService import SubscriptionService
    from src.repository.interfaces.interface_SubscriptionRepository import SubscriptionRepository
    
    # Create a mock repository directly
    mock_repo = AsyncMock(spec=SubscriptionRepository)
    
    # Return the service with the mock repo
    return SubscriptionService(subscription_repository=mock_repo)

@pytest.fixture
def sample_subscription_active():
    """Create a sample User (result from user_repo.get_user) for testing."""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.Subscription(
        subscription_id="1_unique_id",
        subscription_type="free_tier",
        email="test@example.com",
        is_active=True
    )

@pytest.fixture
def sample_createsubscription():
    """Create a sample User (result from user_repo.get_user) for testing."""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.CreateSubscription(
        subscription_type="free_tier",
        email="test@example.com"
    )

# Tests for get_user method
@pytest.mark.asyncio
async def test_get_subscription_success(
    subscription_service,
    sample_subscription_active
    ):
    """Test successful subscription retrieval."""
    # Setup mock to return a Subscription
    subscription_service.subscription_repository.get_subscription = AsyncMock(return_value=sample_subscription_active)
    
    # Call the method - returns SubscriptionResponse
    subscription = await subscription_service.get_subscription(sample_subscription_active.subscription_id)
    
    # Verify the repository method was called correctly
    subscription_service.subscription_repository.get_subscription.assert_called_once_with(sample_subscription_active.subscription_id)
    
    # Assertions
    assert subscription.subscription_id == sample_subscription_active.subscription_id
    assert subscription.subscription_type == sample_subscription_active.subscription_type
    assert subscription.email == sample_subscription_active.email
    assert subscription.is_active == True

@pytest.mark.asyncio
async def test_get_subscription_not_found(subscription_service):
    """Test subscription not found scenario."""
    # Import inside test function
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    subscription_service.subscription_repository.get_subscription = AsyncMock(
        side_effect=ResourceNotFoundException("Subscription with subscription_id nonexistent_id not found")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await subscription_service.get_subscription("nonexistent_id")
    
    # Verify the repository method was called correctly
    subscription_service.subscription_repository.get_subscription.assert_called_once_with("nonexistent_id")
    
    assert "not found" in str(exc_info.value)

# Tests for create_subscription method
@pytest.mark.asyncio
@patch("src.service.SubscriptionService.generate_unique_id")
async def test_create_subscription_success(
    mock_uuid,
    subscription_service,
    sample_subscription_active,
    sample_createsubscription
    ):
    """Test successful subscription creation."""

    # Setup mock for saltAndHashedPW
    mock_uuid.return_value = "1_unique_id"

    # Setup mock to return a Subscription
    subscription_service.subscription_repository.create_subscription = AsyncMock(return_value=sample_subscription_active)

    # Call the method - return SubscriptionResponse
    subscription = await subscription_service.create_subscription(subscription_create=sample_createsubscription)

    # Verify the repository method was called correctly
    subscription_service.subscription_repository.create_subscription.assert_called_once_with(
        Subscription_instance=sample_subscription_active
    )
    
    # Assertions
    assert subscription.subscription_type == sample_subscription_active.subscription_type
    assert subscription.email == sample_subscription_active.email
    assert subscription.is_active == True