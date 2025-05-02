import uuid6
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, BigInteger, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SubscriptionORM(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "auth"}
    subscription_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, index= True, default=uuid6.uuid6)
    subscription_type = Column(String, nullable=True)
    email = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)

class SubscriptionsOutboxORM(Base):
    __tablename__ = "subscriptions_outbox"
    __table_args__ = {"schema": "auth"}  # Specifies the schema

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid6.uuid6)
    aggregatetype = Column(String, nullable=False)     # e.g., "subscription" -> TOPIC
    aggregateid = Column(String, nullable=False)       # e.g., "subscription_id"
    eventtype = Column(String, nullable=False)              # e.g., "subscription_created_success"
    payload = Column(JSON, nullable=False)             # Event data as JSON
    created_at = Column(BigInteger, nullable=False, default=lambda: int(datetime.now(timezone.utc).timestamp() * 1000))
    transaction_id = Column(String, nullable=True)     # Optional, for SAGA tracing