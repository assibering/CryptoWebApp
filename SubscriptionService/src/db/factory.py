# src/db/factory.py
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_dynamodb import DynamoDBClient
from src.repository.interfaces.interface_SubscriptionRepository import SubscriptionRepository as SubscriptionRepositoryInterface
from src.repository.implementations.PostgreSQL.postgres_SubscriptionRepository import SubscriptionRepository as PostgresSubscriptionRepository
from src.repository.implementations.AWS_DynamoDB.awsdynamodb_SubscriptionRepository import SubscriptionRepository as DynamoSubscriptionRepository
from .settings import get_settings, DatabaseType
from typing import Union

def create_user_repository(db_context: Union[AsyncSession, DynamoDBClient]) -> SubscriptionRepositoryInterface:
    """
    Creates the appropriate repository based on configuration.
    For PostgreSQL: Uses the provided database session
    For DynamoDB: Ignores the database session parameter
    """
    settings = get_settings()
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        return PostgresSubscriptionRepository(db_context)
    elif settings.DATABASE_TYPE == DatabaseType.DYNAMODB:
        return DynamoSubscriptionRepository(db_context)
    else:
        raise ValueError(f"Unsupported database type: {settings.DATABASE_TYPE}")
