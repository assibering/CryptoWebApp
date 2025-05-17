import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# Fixtures
@pytest.fixture
def mock_db():
    """Create a mock AsyncSession for testing."""
    mock = AsyncMock(spec=AsyncSession)
    # Setup the async context manager for begin()
    context_manager = AsyncMock()
    mock.begin.return_value = context_manager
    return mock

@pytest.fixture
def user_repo(mock_db):
    """Create a UserRepository instance with a mock db."""
    from src.repository.implementations.PostgreSQL.postgres_UserRepository import UserRepository
    return UserRepository(db=mock_db)

@pytest.fixture
def sample_user():
    """Create a sample User schema for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.User(
        email="test@example.com",
        is_active=True,
        hashed_password="hashed_password_value",
    )

@pytest.fixture
def sample_outbox():
    """Create a sample Outbox schema for testing."""
    from src.schemas import UserSchemas
    return UserSchemas.Outbox(
        aggregatetype = "user",
        aggregateid = "test@example.com",
        eventtype_prefix = "user_created",
        payload = {
            "email": "test@example.com",
            "is_active": True,
        }
    )

@pytest.fixture
def db_user():
    """Create a sample UserORM object that would be returned from the database."""
    from src.repository.implementations.PostgreSQL.models.ORM_User import UserORM
    user = MagicMock(spec=UserORM)
    user.email = "test@example.com"
    user.is_active = True
    user.hashed_password = "hashed_password_value"
    return user

# Tests for get_user method
@pytest.mark.asyncio
async def test_get_user_success(user_repo, mock_db, db_user):
    """Test successful user retrieval."""
    # Import inside test function to avoid early import
    from src.schemas import UserSchemas
    
    # Setup mock to return a user
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = db_user
    mock_db.execute.return_value = mock_result
    
    # Call the method
    user = await user_repo.get_user("test@example.com")
    
    # Assertions
    assert user.email == "test@example.com"
    assert user.is_active is True
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_not_found(user_repo, mock_db):
    """Test user not found scenario."""
    # Import inside test function
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to return None (user not found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await user_repo.get_user("nonexistent@example.com")
    
    assert "not found" in str(exc_info.value)
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_database_error(user_repo, mock_db):
    """Test database error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise an exception
    mock_db.execute.side_effect = Exception("Database connection error")
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_repo.get_user("test@example.com")
    
    assert "Internal database error" in str(exc_info.value)
    mock_db.execute.assert_called_once()

# Tests for create_user method
@pytest.mark.asyncio
async def test_create_user_success(user_repo, mock_db, sample_user, sample_outbox):
    """Test successful user creation."""
    # Call the method
    await user_repo.create_user(sample_user, sample_outbox)
    
    # Verify that begin() was called for the transaction
    mock_db.begin.assert_called_once()
    
    # Verify that add() was called twice (user + outbox event)
    assert mock_db.add.call_count == 2

@pytest.mark.asyncio
async def test_create_user_already_exists(user_repo, mock_db, sample_user, sample_outbox):
    """Test user already exists scenario."""
    # Import inside test function
    from src.exceptions import ResourceAlreadyExistsException
    
    # Setup mock to raise IntegrityError with UniqueViolationError
    unique_violation = Exception("UniqueViolationError")
    integrity_error = IntegrityError("statement", "params", unique_violation)
    integrity_error.orig = unique_violation
    
    # Make the first transaction fail
    first_context = AsyncMock()
    first_context.__aenter__.return_value = None
    first_context.__aexit__.side_effect = integrity_error
    
    # Make the second transaction (for failure event) succeed
    second_context = AsyncMock()
    second_context.__aenter__.return_value = None
    second_context.__aexit__.return_value = None
    
    # Configure mock_db.begin() to return different context managers on consecutive calls
    mock_db.begin.side_effect = [first_context, second_context]
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceAlreadyExistsException) as exc_info:
        await user_repo.create_user(sample_user, sample_outbox)
    
    assert "already exists" in str(exc_info.value)
    
    # Verify begin() was called twice (initial attempt + failure event)
    assert mock_db.begin.call_count == 2
    
    # Verify add() was called twice (initial user + outbox) and once more for failure event
    assert mock_db.add.call_count == 3

@pytest.mark.asyncio
async def test_create_user_other_integrity_error(user_repo, mock_db, sample_user, sample_outbox):
    """Test other integrity error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a different kind of IntegrityError
    other_error = Exception("Other constraint violation")
    integrity_error = IntegrityError("statement", "params", other_error)
    integrity_error.orig = other_error
    
    # Make the first transaction fail
    first_context = AsyncMock()
    first_context.__aenter__.return_value = None
    first_context.__aexit__.side_effect = integrity_error
    
    # Make the second transaction (for failure event) succeed
    second_context = AsyncMock()
    second_context.__aenter__.return_value = None
    second_context.__aexit__.return_value = None
    
    # Configure mock_db.begin() to return different context managers on consecutive calls
    mock_db.begin.side_effect = [first_context, second_context]
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_repo.create_user(sample_user, sample_outbox)
    
    assert "Database integrity error" in str(exc_info.value)
    
    # Verify begin() was called twice (initial attempt + failure event)
    assert mock_db.begin.call_count == 2
    
    # Verify add() was called twice (initial user + outbox) and once more for failure event
    assert mock_db.add.call_count == 3

@pytest.mark.asyncio
async def test_create_user_general_exception(user_repo, mock_db, sample_user, sample_outbox):
    """Test general exception handling during user creation."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a general exception
    general_error = Exception("Unexpected error")
    
    # Make the first transaction fail
    first_context = AsyncMock()
    first_context.__aenter__.return_value = None
    first_context.__aexit__.side_effect = general_error
    
    # Make the second transaction (for failure event) succeed
    second_context = AsyncMock()
    second_context.__aenter__.return_value = None
    second_context.__aexit__.return_value = None
    
    # Configure mock_db.begin() to return different context managers on consecutive calls
    mock_db.begin.side_effect = [first_context, second_context]
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_repo.create_user(sample_user, sample_outbox)
    
    assert "Internal database error" in str(exc_info.value)
    
    # Verify begin() was called twice (initial attempt + failure event)
    assert mock_db.begin.call_count == 2
    
    # Verify add() was called twice (initial user + outbox) and once more for failure event
    assert mock_db.add.call_count == 3

# Tests for update_user method
@pytest.mark.asyncio
async def test_update_user_success(user_repo, mock_db, db_user):
    """Test successful user update."""
    # Import inside test function
    from src.schemas import UserSchemas
    
    # Create an updated user
    updated_user = UserSchemas.User(
        email="test@example.com",
        is_active=False
    )
    
    # Mock the dict method to return the fields to update
    with patch.object(UserSchemas.User, 'dict', return_value={"is_active": False}):
        result = await user_repo.update_user(updated_user)
    
    # Assertions
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_update_user_not_found(user_repo, mock_db, sample_user):
    """Test user not found during update."""
    # Import inside test function
    from src.exceptions import ResourceNotFoundException
    
    # Setup mock to return None (user not found)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceNotFoundException) as exc_info:
        await user_repo.update_user(sample_user)
    
    assert "not found" in str(exc_info.value)
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
async def test_update_user_database_error(user_repo, mock_db, sample_user, db_user):
    """Test database error during user update."""
    # Import inside test function
    from src.exceptions import BaseAppException
    from src.schemas import UserSchemas
    
    # Setup mock to return a user but raise an exception on commit
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = db_user
    mock_db.execute.return_value = mock_result
    mock_db.commit.side_effect = Exception("Database error")
    
    # Mock the dict method
    with patch.object(UserSchemas.User, 'dict', return_value={"is_active": False}):
        # Test that the correct exception is raised
        with pytest.raises(BaseAppException) as exc_info:
            await user_repo.update_user(sample_user)
    
    assert "Internal database error" in str(exc_info.value)
    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
