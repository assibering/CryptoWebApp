# src/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_dynamodb import DynamoDBClient
from src.repository.interfaces.interface_SubscriptionRepository import SubscriptionRepository as SubscriptionRepositoryInterface
from src.service.SubscriptionService import SubscriptionService
from src.db.factory import create_user_repository
from src.db.db_context import db_context
from typing import Union

async def get_subscription_repository(db: Union[AsyncSession, DynamoDBClient] = Depends(db_context)) -> SubscriptionRepositoryInterface:
    """
    Creates the appropriate repository based on configuration.
    The db parameter will be a database session for PostgreSQL or None for DynamoDB.
    """
    return create_user_repository(db)

async def get_subscription_service(subscription_repository: SubscriptionRepositoryInterface = Depends(get_subscription_repository)) -> SubscriptionService:
    return SubscriptionService(subscription_repository)
