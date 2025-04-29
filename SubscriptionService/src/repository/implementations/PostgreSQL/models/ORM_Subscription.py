from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SubscriptionORM(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {"schema": "auth"}
    subscription_id = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    subscription_type = Column(String, nullable=True)
    email = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)