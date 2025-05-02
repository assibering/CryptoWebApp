import uuid6
from datetime import datetime ,timezone
from sqlalchemy import Column, String, Boolean, BigInteger, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserORM(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}
    email = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

class UsersOutboxORM(Base):
    __tablename__ = "users_outbox"
    __table_args__ = {"schema": "auth"}  # Specifies the schema

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid6)
    aggregatetype = Column(String, nullable=False)     # e.g., "user" -> TOPIC
    aggregateid = Column(String, nullable=False)       # e.g., user_id
    type = Column(String, nullable=False)              # e.g., "user_created_success"
    payload = Column(JSON, nullable=False)             # Event data as JSON
    created_at = Column(BigInteger, nullable=False, default=lambda: int(datetime.now(timezone.utc).timestamp() * 1000))
    transaction_id = Column(String, nullable=True)     # Optional, for SAGA tracing
