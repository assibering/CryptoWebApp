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
    from src.repository.implementations.PostgreSQL.postgres_SubscriptionRepository import SubscriptionRepository
    return SubscriptionRepository(db=mock_db)
