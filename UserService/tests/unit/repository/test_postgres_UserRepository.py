import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# Fixtures
@pytest.fixture
def mock_db():
    """Create a mock AsyncSession for testing."""
    mock = AsyncMock(spec=AsyncSession)
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
        salt="salt_value"
    )

@pytest.fixture
def db_user():
    """Create a sample UserORM object that would be returned from the database."""
    from src.repository.implementations.PostgreSQL.models.ORM_User import UserORM
    user = MagicMock(spec=UserORM)
    user.email = "test@example.com"
    user.is_active = True
    user.hashed_password = "hashed_password_value"
    user.salt = "salt_value"
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
async def test_create_user_success(user_repo, mock_db, sample_user):
    """Test successful user creation."""
    # Call the method
    result = await user_repo.create_user(sample_user)
    
    # Assertions
    assert result.email == sample_user.email
    assert result.is_active == sample_user.is_active
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_already_exists(user_repo, mock_db, sample_user):
    """Test user already exists scenario."""
    # Import inside test function
    from src.exceptions import ResourceAlreadyExistsException
    
    # Setup mock to raise IntegrityError with UniqueViolationError
    unique_violation = Exception("UniqueViolationError")
    integrity_error = IntegrityError("statement", "params", unique_violation)
    integrity_error.orig = unique_violation
    mock_db.commit.side_effect = integrity_error
    
    # Test that the correct exception is raised
    with pytest.raises(ResourceAlreadyExistsException) as exc_info:
        await user_repo.create_user(sample_user)
    
    assert "already exists" in str(exc_info.value)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_other_integrity_error(user_repo, mock_db, sample_user):
    """Test other integrity error handling."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a different kind of IntegrityError
    other_error = Exception("Other constraint violation")
    integrity_error = IntegrityError("statement", "params", other_error)
    integrity_error.orig = other_error
    mock_db.commit.side_effect = integrity_error
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_repo.create_user(sample_user)
    
    assert "Database integrity error" in str(exc_info.value)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_general_exception(user_repo, mock_db, sample_user):
    """Test general exception handling during user creation."""
    # Import inside test function
    from src.exceptions import BaseAppException
    
    # Setup mock to raise a general exception
    mock_db.commit.side_effect = Exception("Unexpected error")
    
    # Test that the correct exception is raised
    with pytest.raises(BaseAppException) as exc_info:
        await user_repo.create_user(sample_user)
    
    assert "Internal database error" in str(exc_info.value)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

# Tests for update_user method
@pytest.mark.asyncio
async def test_update_user_success(user_repo, mock_db, sample_user, db_user):
    """Test successful user update."""
    # Import inside test function
    from src.schemas import UserSchemas
    
    # Setup mock to return a user
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = db_user
    mock_db.execute.return_value = mock_result
    
    # Create an updated user
    updated_user = UserSchemas.User(
        email="test@example.com",
        is_active=False
    )
    
    # Mock the dict method to return the fields to update
    with patch.object(UserSchemas.User, 'dict', return_value={"is_active": False}):
        result = await user_repo.update_user(updated_user)
    
    # Assertions
    assert result.email == "test@example.com"
    assert result.is_active == False  # The mock db_user's value should be updated to false
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
