from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from .utils import saltAndHashedPW
from src.exceptions import BaseAppException, ResourceNotFoundException, ResourceAlreadyExistsException, ValidationException
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class UserService:

    def __init__(self, user_repository: interface_UserRepository):
        self.user_repository = user_repository
    
    async def get_user(self, email: str) -> UserSchemas.UserResponse:
        try:
            user = await self.user_repository.get_user(email)
            return UserSchemas.UserResponse(
                email=user.email,
                is_active=user.is_active
            )
        except ResourceNotFoundException:
            raise #Re-raise from repository layer
        except Exception as e:
            logger.exception(f"Error getting user: {str(e)}")
            raise BaseAppException(f"Error getting user: {str(e)}") from e
        
    async def create_user(
            self,
            User_instance: UserSchemas.User,
            eventtype_prefix: str,
            payload_add: Dict[str, Any] = None
        ) -> None:
        try:
            
            # Create the user
            await self.user_repository.create_user(

                User_instance = User_instance,

                Outbox_instance = UserSchemas.Outbox(
                    aggregatetype = "user",
                    aggregateid = User_instance.email,
                    eventtype_prefix = eventtype_prefix,
                    payload = {
                        "email": User_instance.email,
                        "is_active": True if User_instance.is_active else False,
                        **(payload_add or {})
                    }
                )
            )

        except ResourceAlreadyExistsException:
            raise
        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")
            raise BaseAppException(f"Error creating user: {str(e)}") from e
    
    async def reset_password(
            self,
            email: str,
            reset_password: UserSchemas.ResetPassword
        ) -> UserSchemas.UserResponse:

        hashed_pw = await saltAndHashedPW(reset_password.password)
        try:
            await self.user_repository.update_user(
                UserSchemas.User(
                    email=email,
                    hashed_password=hashed_pw,
                    is_active=True
                )
            )

            return UserSchemas.UserResponse(
                email=email
            )
        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error updating user: {str(e)}")
            raise BaseAppException(f"Error updating user: {str(e)}") from e
    
    async def deactivate_user(self, email: str) -> UserSchemas.UserResponse:
        try:
            user = await self.user_repository.update_user(
                UserSchemas.User(
                    email=email,
                    is_active=False
                )
            )
            return UserSchemas.UserResponse(
                email=user.email,
                is_active=user.is_active
            )
        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error deactivating user: {str(e)}")
            raise BaseAppException(f"Error deactivating user: {str(e)}") from e
    
    async def delete_user(self, email: str) -> None:
        try:
            await self.user_repository.delete_user(
                email = email
            )

        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error deactivating user: {str(e)}")
            raise BaseAppException(f"Error deactivating user: {str(e)}") from e