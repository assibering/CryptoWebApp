# src/db/factory.py
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_dynamodb import DynamoDBClient
from src.repository.interfaces.interface_UserRepository import UserRepository as UserRepositoryInterface
from src.repository.implementations.PostgreSQL.postgres_UserRepository import UserRepository as PostgresUserRepository
from src.repository.implementations.AWS_DynamoDB.awsdynamodb_UserRepository import UserRepository as DynamoUserRepository
from .settings import get_settings, DatabaseType
from typing import Union

def create_user_repository(db_context: Union[AsyncSession, DynamoDBClient]) -> UserRepositoryInterface:
    """
    Creates the appropriate repository based on configuration.
    For PostgreSQL: Uses the provided database session
    For DynamoDB: Ignores the database session parameter
    """
    settings = get_settings()
    
    if settings.DATABASE_TYPE == DatabaseType.POSTGRES:
        return PostgresUserRepository(db_context)
    elif settings.DATABASE_TYPE == DatabaseType.DYNAMODB:
        return DynamoUserRepository(db_context)
    else:
        raise ValueError(f"Unsupported database type: {settings.DATABASE_TYPE}")
