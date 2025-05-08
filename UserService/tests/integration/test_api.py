import pytest
from httpx import AsyncClient

# GET USER TESTS
# @pytest.mark.asyncio(loop_scope="session")
# async def test_get_user_success(async_client: AsyncClient):
#     """Test retrieving a user by email"""

#     test_user_data = {
#         "email": "0_test@example.com"
#     }

#     # First create a user by starting a subscription
#     await async_client.post(
#         "/users/create-user",
#         params=test_user_data
#     )
    
#     # Then retrieve the user
#     # ENDPOINT MUST BE /users?email="example@email.com"
#     response = await async_client.get(
#         "/users",
#         params=test_user_data
#     )
    
#     assert response.status_code == 200
#     data = response.json()
#     assert data["email"] == test_user_data["email"]
#     assert data["is_active"] == False

@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_user(async_client: AsyncClient):
    """Test retrieving a user that doesn't exist"""

    test_user_data = {
        "email": "nonexistent@example.com"
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
# @pytest.mark.asyncio(loop_scope="session")
# async def test_create_user_success(async_client: AsyncClient):
#     """Test creating a new user"""

#     test_user_data = {
#         "email": "1_test@example.com"
#     }

#     response = await async_client.post(
#         "/users/create-user",
#         params=test_user_data
#     )
    
#     assert response.status_code == 201
#     data = response.json()
#     assert data["email"] == test_user_data["email"]
#     assert data["is_active"] == False

# @pytest.mark.asyncio(loop_scope="session")
# async def test_create_user_already_exists(async_client: AsyncClient):
#     """Test creating the same user twice causing a conflict"""

#     test_user_data = {
#         "email": "2_test@example.com"
#     }

#     # First create a user
#     await async_client.post(
#         "/users/create-user",
#         params=test_user_data
#     )
#     # Then try to create the same user again
#     response = await async_client.post(
#         "/users/create-user",
#         params=test_user_data
#     )
    
#     assert response.status_code == 409
#     data = response.json()
#     assert 'error' in data
#     assert data["error"] == f"User with email {test_user_data['email']} already exists"

#RESET PASSWORD TESTS
# @pytest.mark.asyncio(loop_scope="session")
# async def test_reset_password_success(async_client: AsyncClient):
#     """Test reset a user's password"""

#     test_user_data = {
#         "email": "3_test@example.com"
#     }

#     test_reset_password_data = {
#         "password": "new_password",
#         "password_repeat": "new_password"
#     }

#     # First create a user
#     await async_client.post(
#         "/users/create-user",
#         params=test_user_data
#     )

#     response = await async_client.put(
#         "/users/reset-password",
#         params=test_user_data,
#         json=test_reset_password_data
#     )
    
#     assert response.status_code == 201
#     data = response.json()
#     assert data["email"] == test_user_data["email"]
#     assert data["is_active"] == True

@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_nonexistent_user(async_client: AsyncClient):
    """Test reset a non existent user's password"""

    test_user_data = {
        "email": "nonexistent@example.com"
    }

    test_reset_password_data = {
        "password": "new_password",
        "password_repeat": "new_password"
    }

    response = await async_client.put(
        "/users/reset-password",
        params=test_user_data,
        json=test_reset_password_data
    )
    
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data["error"] == f"User with email {test_user_data['email']} not found"

@pytest.mark.asyncio(loop_scope="session")
async def test_reset_password_validation_error(async_client: AsyncClient):
    """Test reset a user's password when passwords dont match"""

    test_user_data = {
        "email": "4_test@example.com"
    }

    test_reset_password_data = {
        "password": "password_1",
        "password_repeat": "password_2"
    }

    response = await async_client.put(
        "/users/reset-password",
        params=test_user_data,
        json=test_reset_password_data
    )
    
    assert response.status_code == 422
    data = response.json()
    assert 'detail' in data
    assert "Value error, Passwords do not match" in str(data["detail"])

#DEACTIVATE TESTS
# @pytest.mark.asyncio(loop_scope="session")
# async def test_deactivate_success(async_client: AsyncClient):
#     """Test deactivate a user"""

#     test_user_data = {
#         "email": "5_test@example.com"
#     }

#     test_reset_password_data = {
#         "password": "new_password",
#         "password_repeat": "new_password"
#     }

#     # First create a user
#     await async_client.post(
#         "/users/create-user",
#         params=test_user_data
#     )

#     # Then reset password to activate
#     response_create = await async_client.put(
#         "/users/reset-password",
#         params=test_user_data,
#         json=test_reset_password_data
#     )
    
#     # Assert user is now active
#     assert response_create.status_code == 201
#     data = response_create.json()
#     assert data["email"] == test_user_data["email"]
#     assert data["is_active"] == True

#     # Then deactivate
#     response_deactivate = await async_client.put(
#         "/users/deactivate-user",
#         params=test_user_data
#     )

#     # Assert user is now deactivated
#     assert response_deactivate.status_code == 201
#     data = response_deactivate.json()
#     assert data["email"] == test_user_data["email"]
#     assert data["is_active"] == False


@pytest.mark.asyncio(loop_scope="session")
async def test_deactivate_nonexistent_user(async_client: AsyncClient):
    """Test deactivate a non existent user"""

    test_user_data = {
        "email": "nonexistent@example.com"
    }

    response = await async_client.put(
        "/users/deactivate-user",
        params=test_user_data
    )
    
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data["error"] == f"User with email {test_user_data['email']} not found"