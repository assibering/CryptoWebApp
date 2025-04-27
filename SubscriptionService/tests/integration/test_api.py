import pytest
from httpx import AsyncClient

# GET SUBSCRIPTION TESTS
@pytest.mark.asyncio(loop_scope="session")
async def test_get_subscription_success(async_client: AsyncClient):
    """Test retrieving a user by email"""
    assert True