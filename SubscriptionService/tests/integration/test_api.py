import pytest
from httpx import AsyncClient

# GET SUBSCRIPTION TESTS
@pytest.mark.asyncio(loop_scope="session")
async def test_get_subscription_success(async_client: AsyncClient):
    """Test retrieving a subscription by id"""

    test_create_data = {
        "subscription_type": "paid_tier",
        "email": "0_test@example.com"
    }

    # First create a subscription
    response_create = await async_client.post(
        "/subscriptions/create-subscription",
        json=test_create_data
    )
    
    response_create_data = response_create.json()

    # Then retrieve the subscription
    # ENDPOINT MUST BE /subscription?subscription_id="some_id"
    response_get = await async_client.get(
        "/subscriptions",
        params={"subscription_id": response_create_data["subscription_id"]}
    )
    
    assert response_get.status_code == 200
    data = response_get.json()
    assert data["subscription_type"] == test_create_data["subscription_type"]
    assert data["email"] == test_create_data["email"]
    assert data["is_active"] == True

@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_subscription(async_client: AsyncClient):
    """Test retrieving a subscription that doesn't exist"""

    response = await async_client.get(
        "/subscriptions",
        params={"subscription_id": "nonexistent_id"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data["error"] == f"Subscription with subscription_id nonexistent_id not found"


#CREATE USER TESTS
@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_success(async_client: AsyncClient):
    """Test creating a new subscription"""

    test_create_data = {
        "subscription_type": "premium_tier",
        "email": "1_test@example.com"
    }

    # First create a subscription
    response = await async_client.post(
        "/subscriptions/create-subscription",
        json=test_create_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["subscription_type"] == test_create_data["subscription_type"]
    assert data["email"] == test_create_data["email"]
    assert data["is_active"] == True