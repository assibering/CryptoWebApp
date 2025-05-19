from src.dependencies import get_subscription_service
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.main import app


client = TestClient(app)

@pytest.fixture
def mock_subscription_service():
    """Create a mock UserService for dependency injection."""
    mock_service = AsyncMock()
    return mock_service

@pytest.fixture
def sample_subscriptionresponse_active():
    """Create a sample SubscriptionResponse"""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.SubscriptionResponse(
        subscription_id="1_unique_id",
        subscription_type="free_tier",
        email="test@example.com",
        is_active=True
    )

@pytest.fixture
def sample_subscriptionresponse_after_creation():
    """Create a sample SubscriptionResponse"""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.SubscriptionResponse(
        subscription_id="1_unique_id",
        subscription_type=None,
        email=None,
        is_active=None
    )

@pytest.fixture
def sample_createsubscription():
    """Create a sample User (result from user_repo.get_user) for testing."""
    from src.schemas import SubscriptionSchemas
    return SubscriptionSchemas.CreateSubscription(
        subscription_type="free_tier",
        email="test@example.com"
    )

# Tests for get_subscription method
@pytest.mark.asyncio
async def test_get_subscription_success(
    mock_subscription_service,
    sample_subscriptionresponse_active
    ):
    """Test successful subscription retrieval."""
    # Setup mock to return a user
    mock_subscription_service.get_subscription.return_value = sample_subscriptionresponse_active
    
    # Override the dependency
    app.dependency_overrides[get_subscription_service] = lambda: mock_subscription_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.get("/subscriptions", params={"subscription_id": "1_unique_id"})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_subscription_service.get_subscription.assert_called_once_with(subscription_id=sample_subscriptionresponse_active.subscription_id)
    
    # Assertions
    assert response.status_code == 200
    subscription_data = response.json()
    assert subscription_data["subscription_type"] == sample_subscriptionresponse_active.subscription_type
    assert subscription_data["email"] == sample_subscriptionresponse_active.email
    assert subscription_data["is_active"] == sample_subscriptionresponse_active.is_active

# Tests for create_subscription method
@pytest.mark.asyncio
async def test_create_subscription_success(
    mock_subscription_service,
    sample_createsubscription,
    sample_subscriptionresponse_after_creation
    ):
    """Test successful subscription creation."""
    # Setup mock to return a SubscriptionResponse
    mock_subscription_service.create_subscription.return_value = sample_subscriptionresponse_after_creation
    
    # Override the dependency
    app.dependency_overrides[get_subscription_service] = lambda: mock_subscription_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.post("/subscriptions/create-subscription", json=sample_createsubscription.model_dump())
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_subscription_service.create_subscription.assert_called_once_with(
        CreateSubscription_instance=sample_createsubscription,
        eventtype_prefix="subscription_created"
    )
    
    # Assertions
    assert response.status_code == 201
    subscription_data = response.json()
    assert subscription_data["subscription_id"] == sample_subscriptionresponse_after_creation.subscription_id
    assert subscription_data["subscription_type"] == sample_subscriptionresponse_after_creation.subscription_type
    assert subscription_data["email"] == sample_subscriptionresponse_after_creation.email
    assert subscription_data["is_active"] == sample_subscriptionresponse_after_creation.is_active