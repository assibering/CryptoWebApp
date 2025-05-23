import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def user_service():
    """Create a UserService with a mocked repository."""
    from src.service.UserService import UserService
    from src.repository.interfaces.interface_UserRepository import UserRepository
    
    # Create a mock repository directly
    mock_repo = AsyncMock(spec=UserRepository)
    
    # Return the service with the mock repo
    return UserService(user_repository=mock_repo)


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
async def test_get_user_success(
    user_service,
    sample_user_inactive_nopw
    ):
    """Test successful user retrieval."""
    # Setup mock to return a User
    user_service.user_repository.get_user = AsyncMock(return_value=sample_user_inactive_nopw)
    
    # Call the method - returns UserResponse
    user = await user_service.get_user(sample_user_inactive_nopw.email)
    
    # Verify the repository method was called correctly
    user_service.user_repository.get_user.assert_called_once_with(sample_user_inactive_nopw.email)
    
    # Assertions
    assert user.email == sample_user_inactive_nopw.email
    assert user.is_active is False

@pytest.mark.asyncio
async def test_get_user_not_found(user_service):
    """Test user not found scenario."""
    # Import inside test function
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    user_service.user_repository.get_user = AsyncMock(
        side_effect=ResourceNotFoundException("User with email nonexistent@example.com not found")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await user_service.get_user("nonexistent@example.com")
    
    # Verify the repository method was called correctly
    user_service.user_repository.get_user.assert_called_once_with("nonexistent@example.com")
    
    assert "not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_user_database_error(user_service, sample_user_inactive_nopw):
    """Test database error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise BaseAppException when user_repo.get_user is called
    user_service.user_repository.get_user = AsyncMock(
        side_effect=BaseAppException("Internal database error: SOME_ERROR")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_service.get_user(sample_user_inactive_nopw.email)
    
    # Verify the repository method was called correctly
    user_service.user_repository.get_user.assert_called_once_with(sample_user_inactive_nopw.email)
    
    assert "Error getting user:" in str(exc_info.value)
    assert "Internal database error:" in str(exc_info.value)

# # Tests for create_user method
@pytest.mark.asyncio
async def test_create_user_success(
    user_service,
    sample_user_inactive_nopw
    ):
    """Test successful user creation."""
    from src.schemas import UserSchemas

    # Call the method
    await user_service.create_user(
        User_instance=UserSchemas.User(
            email = sample_user_inactive_nopw.email
        ),
        eventtype_prefix = "user_created"
    )

    # Verify the repository method was called correctly
    user_service.user_repository.create_user.assert_called_once_with(
        User_instance=UserSchemas.User(
            email=sample_user_inactive_nopw.email
        ),
        Outbox_instance = UserSchemas.Outbox(
            aggregatetype = "user",
            aggregateid = sample_user_inactive_nopw.email,
            eventtype_prefix = "user_created",
            payload = {
                "email": sample_user_inactive_nopw.email,
                "is_active": True if sample_user_inactive_nopw.is_active else False
            }
        )
    )

@pytest.mark.asyncio
async def test_create_user_already_exists(user_service, sample_user_inactive_nopw):
    """Test user already exists scenario."""
    # Import inside test function
    from src.exceptions import ResourceAlreadyExistsException
    from src.schemas import UserSchemas
    
    # Setup mock to raise ResourceNotFoundException when get_user is called
    user_service.user_repository.create_user = AsyncMock(
        side_effect=ResourceAlreadyExistsException("User with email test@example.com already exists")
    )

    # Test that the correct exception is raised
    with pytest.raises(ResourceAlreadyExistsException) as exc_info:
        # Call the method
        await user_service.create_user(
            User_instance=UserSchemas.User(
                email = sample_user_inactive_nopw.email
            ),
            eventtype_prefix = "user_created"
        )
    
    # Verify the repository method was called correctly
    user_service.user_repository.create_user.assert_called_once_with(
        User_instance=UserSchemas.User(
            email=sample_user_inactive_nopw.email
        ),
        Outbox_instance = UserSchemas.Outbox(
            aggregatetype = "user",
            aggregateid = sample_user_inactive_nopw.email,
            eventtype_prefix = "user_created",
            payload = {
                "email": sample_user_inactive_nopw.email,
                "is_active": True if sample_user_inactive_nopw.is_active else False
            }
        )
    )
    
    assert "already exists" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_user_other_integrity_error(user_service, sample_user_inactive_nopw):
    """Test other integrity error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    from src.schemas import UserSchemas

    # Setup mock to raise a different kind of IntegrityError
    user_service.user_repository.create_user = AsyncMock(
        side_effect=BaseAppException("Database integrity error: SOME_ERROR")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        # Call the method
        await user_service.create_user(
            User_instance=UserSchemas.User(
                email = sample_user_inactive_nopw.email
            ),
            eventtype_prefix = "user_created"
        )
    
    # Verify the repository method was called correctly
    user_service.user_repository.create_user.assert_called_once_with(
        User_instance=UserSchemas.User(
            email=sample_user_inactive_nopw.email
        ),
        Outbox_instance = UserSchemas.Outbox(
            aggregatetype = "user",
            aggregateid = sample_user_inactive_nopw.email,
            eventtype_prefix = "user_created",
            payload = {
                "email": sample_user_inactive_nopw.email,
                "is_active": True if sample_user_inactive_nopw.is_active else False
            }
        )
    )
    
    assert "Error creating user:" in str(exc_info.value)
    assert "Database integrity error:" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_user_general_exception(user_service, sample_user_inactive_nopw):
    """Test general exception handling during user creation."""
    # Import inside test function
    from src.exceptions import BaseAppException
    from src.schemas import UserSchemas
    
    # Setup mock to raise a different kind of IntegrityError
    user_service.user_repository.create_user = AsyncMock(
        side_effect=BaseAppException("Internal database error: SOME_ERROR")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        # Call the method
        await user_service.create_user(
            User_instance=UserSchemas.User(
                email = sample_user_inactive_nopw.email
            ),
            eventtype_prefix = "user_created"
        )
    
    # Verify the repository method was called correctly
    user_service.user_repository.create_user.assert_called_once_with(
        User_instance=UserSchemas.User(
            email=sample_user_inactive_nopw.email
        ),
        Outbox_instance = UserSchemas.Outbox(
            aggregatetype = "user",
            aggregateid = sample_user_inactive_nopw.email,
            eventtype_prefix = "user_created",
            payload = {
                "email": sample_user_inactive_nopw.email,
                "is_active": True if sample_user_inactive_nopw.is_active else False
            }
        )
    )
    
    assert "Error creating user:" in str(exc_info.value)
    assert "Internal database error:" in str(exc_info.value)

# Tests for reset_password method
@pytest.mark.asyncio
@patch("src.service.UserService.saltAndHashedPW")
async def test_password_reset_success(
    mock_saltAndHashedPW,
    user_service,
    sample_user_active_nopw,
    sample_reset_password,
    sample_user_active_pw
    ):

    """Test successful password update."""
    # Setup mock for saltAndHashedPW
    mock_saltAndHashedPW.return_value = "hashed_password_value"
    
    # Call the method
    await user_service.reset_password(sample_user_active_nopw.email, sample_reset_password)

    # Verify the repository method was called correctly
    user_service.user_repository.update_user.assert_called_once_with(sample_user_active_pw)

@pytest.mark.asyncio
@patch("src.service.UserService.saltAndHashedPW")
async def test_password_reset_user_not_found(
    mock_saltAndHashedPW,
    user_service,
    sample_reset_password
    ):

    """Test User not found password update."""
    # Import inside test function
    from src.schemas import UserSchemas
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock for saltAndHashedPW
    mock_saltAndHashedPW.return_value = "hashed_password_value"

    # Setup mock to raise ResourceNotFoundException when get_user is called
    user_service.user_repository.update_user = AsyncMock(
        side_effect=ResourceNotFoundException("User with email nonexistent@example.com not found")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await user_service.reset_password("nonexistent@example.com", sample_reset_password)
    
    # Verify the repository method was called correctly
    user_service.user_repository.update_user.assert_called_once_with(
        UserSchemas.User(
            email="nonexistent@example.com",
            hashed_password="hashed_password_value",
            is_active=True
        )
    )
    
    assert "not found" in str(exc_info.value)

@pytest.mark.asyncio
@patch("src.service.UserService.saltAndHashedPW")
async def test_password_reset_database_error(
    mock_saltAndHashedPW,
    user_service,
    sample_user_active_pw,
    sample_reset_password
    ):
    """Test database error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock for saltAndHashedPW
    mock_saltAndHashedPW.return_value = "hashed_password_value"

    # Setup mock to raise ResourceNotFoundException when get_user is called
    user_service.user_repository.update_user = AsyncMock(
        side_effect=BaseAppException("Internal database error: SOME_ERROR")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_service.reset_password(sample_user_active_pw.email, sample_reset_password)
    
    # Verify the repository method was called correctly
    user_service.user_repository.update_user.assert_called_once_with(sample_user_active_pw)
    
    assert "Error updating user:" in str(exc_info.value)
    assert "Internal database error:" in str(exc_info.value)

# Tests for deactivate_user method
@pytest.mark.asyncio
async def test_deactivate_success(
    user_service,
    sample_user_inactive_nopw,
    sample_user_active_nopw
    ):
    """Test successful deactivate update."""
    # Setup mock to return a User
    user_service.user_repository.update_user = AsyncMock(return_value=sample_user_inactive_nopw)
    
    # Call the method - return UserResponse
    user = await user_service.deactivate_user(sample_user_active_nopw.email)

    # Verify the repository method was called correctly
    user_service.user_repository.update_user.assert_called_once_with(sample_user_inactive_nopw)
    
    # Assertions
    assert user.email == sample_user_inactive_nopw.email
    assert user.is_active is False

@pytest.mark.asyncio
async def test_deactivate_user_not_found(
    user_service
    ):
    """Test User not found password update."""
    # Import inside test function
    from src.schemas import UserSchemas
    from src.exceptions import ResourceNotFoundException

    # Setup mock to raise ResourceNotFoundException when get_user is called
    user_service.user_repository.update_user = AsyncMock(
        side_effect=ResourceNotFoundException("User with email nonexistent@example.com not found")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await user_service.deactivate_user("nonexistent@example.com")
    
    # Verify the repository method was called correctly
    user_service.user_repository.update_user.assert_called_once_with(
        UserSchemas.User(
            email="nonexistent@example.com",
            is_active=False
        )
    )
    
    assert "not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_deactivate_database_error(
    user_service,
    sample_user_inactive_nopw
    ):
    """Test database error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException

    # Setup mock to raise ResourceNotFoundException when get_user is called
    user_service.user_repository.update_user = AsyncMock(
        side_effect=BaseAppException("Internal database error: SOME_ERROR")
    )
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_service.deactivate_user(sample_user_inactive_nopw.email)
    
    # Verify the repository method was called correctly
    user_service.user_repository.update_user.assert_called_once_with(sample_user_inactive_nopw)
    
    assert "Error deactivating user:" in str(exc_info.value)
    assert "Internal database error:" in str(exc_info.value)