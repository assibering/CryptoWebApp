from sqlalchemy import Column, String, Boolean
from src.db.database import Base

class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}  # <--- VERY IMPORTANT
    email = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    salt = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
