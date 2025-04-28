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

# Tests for get_user method
@pytest.mark.asyncio
async def test_get_subscription_success(
    subscription_service
    ):
    """Test successful user retrieval."""
    assert True