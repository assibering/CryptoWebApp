from abc import ABC, abstractmethod
from ...schemas import UserSchemas

class UserRepository(ABC):

    @abstractmethod
    async def get_user(self, email: str) -> UserSchemas.User:
        pass

    @abstractmethod
    async def create_user(self, User_instance: UserSchemas.User):
        pass

    @abstractmethod
    async def update_user(self, User_instance: UserSchemas.User):
        pass