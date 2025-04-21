from fastapi import Depends
from src.repository.implementations.PostgreSQL.postgres_UserRepository import UserRepository
from src.service.UserService import UserService
from src.db.dependencies import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db)

async def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)
