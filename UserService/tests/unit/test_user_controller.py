from src.dependencies import get_user_service
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import AsyncMock
from src.routes.UserController import router
from src.main import app


client = TestClient(app)

@pytest.fixture
def mock_user_service():
    """Create a mock UserService for dependency injection."""
    mock_service = AsyncMock()
    return mock_service

@pytest.fixture
def sample_user_response_inactive():
    """Create a sample inactive UserResponse"""
    from src.schemas import UserSchemas
    return UserSchemas.UserResponse(
        email="test@example.com",
        is_active=False
    )

@pytest.fixture
def sample_user_response_active():
    """Create a sample active UserResponse"""
    from src.schemas import UserSchemas
    return UserSchemas.UserResponse(
        email="test@example.com",
        is_active=True
    )

@pytest.fixture
def sample_reset_password():
    """Create a sample ResetPassword"""
    from src.schemas import UserSchemas
    return UserSchemas.ResetPassword(
        password="new_password",
        password_repeat="new_password"
    )

# Tests for get_user method
@pytest.mark.asyncio
async def test_get_user_success(mock_user_service, sample_user_response_inactive):
    """Test successful user retrieval."""
    # Setup mock to return a user
    mock_user_service.get_user.return_value = sample_user_response_inactive
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.get("/users", params={"email": "test@example.com"})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.get_user.assert_called_once_with(email=sample_user_response_inactive.email)
    
    # Assertions
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == sample_user_response_inactive.email
    assert user_data["is_active"] == sample_user_response_inactive.is_active

@pytest.mark.asyncio
async def test_get_user_user_not_found(mock_user_service):
    """Test user not found scenario."""
    # Import inside test function
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    mock_user_service.get_user.side_effect = ResourceNotFoundException(
        "User with email nonexistent@example.com not found"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.get("/users", params={"email": "nonexistent@example.com"})
    
    # Clean up the override - do this AFTER making the request
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.get_user.assert_called_once_with(email="nonexistent@example.com")
    
    # Assertions
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "User with email nonexistent@example.com not found" in error_data["error"]

@pytest.mark.asyncio
async def test_get_user_database_error(mock_user_service):
    """Test user not found scenario."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    mock_user_service.get_user.side_effect = BaseAppException(
        "Error getting user: Internal database error: SOME_ERROR"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.get("/users", params={"email": "test@example.com"})
    
    # Clean up the override - do this AFTER making the request
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.get_user.assert_called_once_with(email="test@example.com")
    
    # Assertions
    assert response.status_code == 500
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "Error getting user: Internal database error: SOME_ERROR" in error_data["error"]


# Tests for create_user method
@pytest.mark.asyncio
async def test_create_user_success(
    mock_user_service,
    sample_user_response_inactive
    ):
    """Test successful user creation."""
    # Setup mock to return a user
    mock_user_service.create_user.return_value = sample_user_response_inactive
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.post("/users/create-user", params={"email": sample_user_response_inactive.email})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.create_user.assert_called_once_with(email=sample_user_response_inactive.email)
    
    # Assertions
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == sample_user_response_inactive.email
    assert user_data["is_active"] == sample_user_response_inactive.is_active


@pytest.mark.asyncio
async def test_create_user_user_already_exists(
    mock_user_service,
    sample_user_response_inactive
    ):
    """Test user already exists scenario."""
    # Import inside test function
    from src.exceptions import ResourceAlreadyExistsException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    mock_user_service.create_user.side_effect = ResourceAlreadyExistsException(
        f"User with email {sample_user_response_inactive.email} already exists"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.post("/users/create-user", params={"email": sample_user_response_inactive.email})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.create_user.assert_called_once_with(email=sample_user_response_inactive.email)
    
    # Assertions
    assert response.status_code == 409
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert f"User with email {sample_user_response_inactive.email} already exists" in error_data["error"]

@pytest.mark.asyncio
async def test_create_user_other_integrity_error(
    mock_user_service,
    sample_user_response_inactive
    ):
    """Test create user with other integrity error."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise BaseAppException when get_user is called
    mock_user_service.create_user.side_effect = BaseAppException(
        "Error creating user: Database integrity error: SOME__ERROR"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.post("/users/create-user", params={"email": sample_user_response_inactive.email})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.create_user.assert_called_once_with(email=sample_user_response_inactive.email)
    
    # Assertions
    assert response.status_code == 500
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "Error creating user: Database integrity error: SOME__ERROR" in error_data["error"]

@pytest.mark.asyncio
async def test_create_user_database_error(
    mock_user_service,
    sample_user_response_inactive
    ):
    """Test create user with database error."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise BaseAppException when get_user is called
    mock_user_service.create_user.side_effect = BaseAppException(
        "Error creating user: Internal database error: SOME__ERROR"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.post("/users/create-user", params={"email": sample_user_response_inactive.email})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.create_user.assert_called_once_with(email=sample_user_response_inactive.email)
    
    # Assertions
    assert response.status_code == 500
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "Error creating user: Internal database error: SOME__ERROR" in error_data["error"]


# Tests for reset_password method
@pytest.mark.asyncio
async def test_reset_password_success(
    mock_user_service,
    sample_reset_password,
    sample_user_response_active
    ):
    """Test successful password reset."""
    # Setup mock to return a user
    mock_user_service.reset_password.return_value = sample_user_response_active
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.put(
            "/users/reset-password",
            params={"email": sample_user_response_active.email},
            json=sample_reset_password.model_dump()
        )
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.reset_password.assert_called_once_with(
        email=sample_user_response_active.email,
        reset_password=sample_reset_password
    )
    
    # Assertions
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == sample_user_response_active.email
    assert user_data["is_active"] == sample_user_response_active.is_active

@pytest.mark.asyncio
async def test_reset_password_user_not_found(
    mock_user_service,
    sample_reset_password
    ):
    """Test user not found scenario."""
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    mock_user_service.reset_password.side_effect = ResourceNotFoundException(
        "User with email nonexistent@example.com not found"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.put(
            "/users/reset-password",
            params={"email": "nonexistent@example.com"},
            json=sample_reset_password.model_dump()
        )
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.reset_password.assert_called_once_with(
        email="nonexistent@example.com",
        reset_password=sample_reset_password
    )
    
    # Assertions
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "User with email nonexistent@example.com not found" in error_data["error"]

@pytest.mark.asyncio
async def test_reset_password_database_error(
    mock_user_service,
    sample_user_response_inactive,
    sample_reset_password
    ):
    """Test reset password with database error."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise BaseAppException when get_user is called
    mock_user_service.reset_password.side_effect = BaseAppException(
        "Error updating user: Internal database error: SOME_ERROR"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.put(
            "/users/reset-password",
            params={"email": sample_user_response_inactive.email},
            json=sample_reset_password.model_dump()
        )
    
    # Clean up the override - do this AFTER making the request
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.reset_password.assert_called_once_with(
        email=sample_user_response_inactive.email,
        reset_password=sample_reset_password
    )

    # Assertions
    assert response.status_code == 500
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "Error updating user: Internal database error: SOME_ERROR" in error_data["error"]

# Tests for deactivate_user method
@pytest.mark.asyncio
async def test_deactivate_success(
    mock_user_service,
    sample_user_response_inactive
    ):
    """Test successful deactivate user."""
    # Setup mock to return a user
    mock_user_service.deactivate_user.return_value = sample_user_response_inactive
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.put(
            "/users/deactivate-user",
            params={"email": sample_user_response_inactive.email}
        )
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.deactivate_user.assert_called_once_with(
        email=sample_user_response_inactive.email
    )
    
    # Assertions
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == sample_user_response_inactive.email
    assert user_data["is_active"] == sample_user_response_inactive.is_active

@pytest.mark.asyncio
async def test_deactivate_user_not_found(
    mock_user_service
    ):
    """Test user not found scenario."""
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    mock_user_service.deactivate_user.side_effect = ResourceNotFoundException(
        "User with email nonexistent@example.com not found"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.put(
            "/users/deactivate-user",
            params={"email": "nonexistent@example.com"}
        )
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.deactivate_user.assert_called_once_with(
        email="nonexistent@example.com"
    )
    
    # Assertions
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "User with email nonexistent@example.com not found" in error_data["error"]

@pytest.mark.asyncio
async def test_deactivate_database_error(
    mock_user_service,
    sample_user_response_inactive
    ):
    """Test deactivate with database error."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise BaseAppException when get_user is called
    mock_user_service.deactivate_user.side_effect = BaseAppException(
        "Error updating user: Internal database error: SOME_ERROR"
    )
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.put(
            "/users/deactivate-user",
            params={"email": sample_user_response_inactive.email}
        )
    
    # Clean up the override - do this AFTER making the request
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.deactivate_user.assert_called_once_with(
        email=sample_user_response_inactive.email
    )

    # Assertions
    assert response.status_code == 500
    error_data = response.json()
    assert "error" in error_data # from our exception handler in /src/main.py
    assert "Error updating user: Internal database error: SOME_ERROR" in error_data["error"]