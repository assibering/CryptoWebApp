from pydantic import BaseModel, model_validator
from typing_extensions import Self
from typing import Optional

# class ResetPassword(BaseModel):
#     password: str
#     password_repeat: str

#     @model_validator(mode='after')
#     def check_passwords_match(self) -> Self:
#         if self.password != self.password_repeat:
#             raise ValueError('Passwords do not match')
#         return self

class Subscription(BaseModel):
    subscription_id: str
    subscription_type: Optional[str] = None
    email: str
    is_active: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    subscription_id: str
    subscription_type: Optional[str] = None
    email: Optional[str] = None
    is_active: bool

class CreateSubscription(BaseModel):
    subscription_type: str
    email: str
