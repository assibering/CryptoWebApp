from fastapi import Depends
from src.repository.implementations.PostgreSQL.postgres_UserRepository import UserRepository
from src.service.UserService import UserService
from src.db.dependencies import get_db
from sqlalchemy.orm import Session

def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_user_service(user_repository = Depends(get_user_repository)):
    return UserService(user_repository)