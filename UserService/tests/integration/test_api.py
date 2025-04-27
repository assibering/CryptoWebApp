import pytest
from httpx import AsyncClient

# GET USER TESTS
@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_success(async_client: AsyncClient):
    """Test retrieving a user by email"""

    test_user_data = {
        "email": "0_test@example.com"
    }

    # First create a user
    await async_client.post(
        "/users/create-user",
        params=test_user_data
    )
    
    # Then retrieve the user
    # ENDPOINT MUST BE /users?email="example@email.com"
    response = await async_client.get(
        "/users",
        params=test_user_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["is_active"] == False

@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_user(async_client: AsyncClient):
    """Test retrieving a user that doesn't exist"""

    test_user_data = {
        "email": "0_nonexistent@example.com"
    }

    response = await async_client.get(
        "/users",
        params=test_user_data
    )
    
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data["error"] == f"User with email {test_user_data['email']} not found"


#CREATE USER TESTS
@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_success(async_client: AsyncClient):
    """Test creating a new user"""

    test_user_data = {
        "email": "1_test@example.com"
    }

    response = await async_client.post(
        "/users/create-user",
        params=test_user_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["is_active"] == False

@pytest.mark.asyncio(loop_scope="session")
async def test_create_user_already_exists(async_client: AsyncClient):
    """Test creating the same user twice causing a conflict"""

    test_user_data = {
        "email": "2_test@example.com"
    }

    # First create a user
    await async_client.post(
        "/users/create-user",
        params=test_user_data
    )
    # Then try to create the same user again
    response = await async_client.post(
        "/users/create-user",
        params=test_user_data
    )
    
    assert response.status_code == 409
    data = response.json()
    assert 'error' in data
    assert data["error"] == f"User with email {test_user_data['email']} already exists"

#RESET PASSWORD TESTS
@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_success(async_client: AsyncClient):
    """Test reset a user's password"""

    test_user_data = {
        "email": "3_test@example.com"
    }

    test_reset_password_data = {
        "password": "new_password",
        "password_repeat": "new_password"
    }

    # First create a user
    await async_client.post(
        "/users/create-user",
        params=test_user_data
    )

    response = await async_client.put(
        "/users/reset-password",
        params=test_user_data,
        json=test_reset_password_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["is_active"] == True





