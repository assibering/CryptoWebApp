from pydantic import BaseModel, model_validator
from typing_extensions import Self
from typing import Optional

class ResetPassword(BaseModel):
    password: str
    password_repeat: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError('Passwords do not match')
        return self

class User(BaseModel):
    email: str
    hashed_password: Optional[str] = None
    salt: Optional[str] = None
    is_active: Optional[bool] = True

