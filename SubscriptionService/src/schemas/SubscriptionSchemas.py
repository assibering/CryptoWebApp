from pydantic import BaseModel
from typing import Optional, Dict, Any


class Subscription(BaseModel):
    subscription_id: str
    subscription_type: Optional[str] = None
    email: str
    is_active: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    subscription_id: str
    subscription_type: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class CreateSubscription(BaseModel):
    subscription_type: str
    email: str

class Outbox(BaseModel):
    aggregatetype: str
    aggregateid: str
    eventtype_prefix: str
    payload: Dict[str, Any]