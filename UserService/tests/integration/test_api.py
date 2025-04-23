import pytest
from httpx import AsyncClient
import json

# Sample user data for testing
test_user_data = {
    "email": "test@example.com"
}

test_user_data_1 = {
    "email": "test1@example.com"
}

test_user_data_2 = {
    "email": "test2@example.com"
}

@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(async_client: AsyncClient):
    """Test creating a new user"""
    response = await async_client.post(
        "/users/create-user",
        json=test_user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["is_active"] is False
    assert data["hashed_password"] is None

@pytest.mark.asyncio(loop_scope="session")
async def test_create_2_users(async_client: AsyncClient):
    """Test creating a new user"""
    response1 = await async_client.post(
        "/users/create-user",
        json=test_user_data_1
    )

    response2 = await async_client.post(
        "/users/create-user",
        json=test_user_data_2
    )
    
    assert response1.status_code == 201
    data1 = response1.json()
    assert data1["email"] == test_user_data_1["email"]
    assert data1["is_active"] is False
    assert data1["hashed_password"] is None

    assert response2.status_code == 201
    data2 = response2.json()
    assert data2["email"] == test_user_data_2["email"]
    assert data2["is_active"] is False
    assert data2["hashed_password"] is None

@pytest.mark.asyncio(loop_scope="session")
async def test_get_user(async_client: AsyncClient):
    """Test retrieving a user by email"""
    # First create a user
    await async_client.post(
        "/users/create-user",
        json={"email": "get_user@example.com"}
    )
    
    # Then retrieve the user
    # ENDPOINT MUST BE /users?email="example@email.com"
    response = await async_client.get(
        "/users",
        params={"email": "get_user@example.com"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "get_user@example.com"
    assert data["is_active"] is False
    assert data["hashed_password"] is None

@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_user(async_client: AsyncClient):
    """Test retrieving a user that doesn't exist"""
    response = await async_client.get(
        "/users",
        params={"email": "nonexistent@example.com"}
    )
    
    # Assuming your API returns 404 for non-existent users
    # If it returns a different status code, adjust this assertion
    assert response.status_code == 404




