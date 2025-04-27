# src/dependencies.py
from fastapi import Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_dynamodb import DynamoDBClient
from src.repository.interfaces.interface_UserRepository import UserRepository as UserRepositoryInterface
from src.service.UserService import UserService
from src.db.factory import create_user_repository
from src.db.db_context import db_context
from typing import Union

async def get_user_repository(db: Union[AsyncSession, DynamoDBClient] = Depends(db_context)) -> UserRepositoryInterface:
    """
    Creates the appropriate repository based on configuration.
    The db parameter will be a database session for PostgreSQL or None for DynamoDB.
    """
    return create_user_repository(db)

async def get_user_service(user_repository: UserRepositoryInterface = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)
