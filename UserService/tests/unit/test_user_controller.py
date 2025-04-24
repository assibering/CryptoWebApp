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
def sample_user_only_email():
    """Create a sample User (result from user_repo.get_user) for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.User(
        email="test@example.com"
    )

@pytest.fixture
def sample_user_inactive_nopw():
    """Create a sample User (result from user_repo.get_user) for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.User(
        email="test@example.com",
        is_active=False
    )

@pytest.fixture
def sample_user_active_nopw():
    """Create a sample User (result from user_repo.get_user) for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.User(
        email="test@example.com",
        is_active=True
    )

@pytest.fixture
def sample_user_active_pw():
    """Create a sample User to reset password for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.User(
        email="test@example.com",
        hashed_password="hashed_password_value",
        is_active=True
    )

@pytest.fixture
def sample_user_pw():
    """Create a sample User to reset password for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.User(
        email="test@example.com",
        hashed_password="hashed_password_value"
    )

@pytest.fixture
def sample_reset_password():
    """Create a sample ResetPassword for resetting password for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.ResetPassword(
        password="new_password",
        password_repeat="new_password"
    )

# Tests for get_user method
@pytest.mark.asyncio
async def test_get_user_success(mock_user_service, sample_user_inactive_nopw):
    """Test successful user retrieval."""
    # Setup mock to return a user
    mock_user_service.get_user.return_value = sample_user_inactive_nopw
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.get("/users", params={"email": "test@example.com"})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.get_user.assert_called_once_with(email=sample_user_inactive_nopw.email)
    
    # Assertions
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == sample_user_inactive_nopw.email
    assert user_data["is_active"] == sample_user_inactive_nopw.is_active

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
    assert "not found" in error_data["error"].lower()

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
    assert "error getting user:" in error_data["error"].lower()
    assert "internal database error:" in error_data["error"].lower()


# Tests for create_user method
@pytest.mark.asyncio
async def test_create_user_success(
    mock_user_service,
    sample_user_only_email,
    sample_user_inactive_nopw
    ):
    """Test successful user retrieval."""
    # Setup mock to return a user
    mock_user_service.create_user.return_value = sample_user_inactive_nopw
    
    # Override the dependency
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    
    # Make the request to the endpoint
    with TestClient(app) as client:
        response = client.post("/users/create-user", json={"email": sample_user_only_email.email})
    
    # Clean up the override
    app.dependency_overrides.clear()
    
    # Verify the service method was called correctly
    mock_user_service.create_user.assert_called_once_with(user_instance=sample_user_only_email)
    
    # Assertions
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == sample_user_inactive_nopw.email
    assert user_data["is_active"] == sample_user_inactive_nopw.is_active