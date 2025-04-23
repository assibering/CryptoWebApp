from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from .utils import saltAndHashedPW
from src.exceptions import BaseAppException, ResourceNotFoundException, ValidationException, ResourceAlreadyExistsException
import logging

logger = logging.getLogger(__name__)

class UserService:

    def __init__(self, user_repository: interface_UserRepository):
        self.user_repository = user_repository
    
    async def get_user(self, email: str) -> UserSchemas.User:
        try:
            return await self.user_repository.get_user(email)
        except ResourceNotFoundException:
            raise #Re-raise from repository layer
        except BaseAppException:
            raise 
        except Exception as e:
            logger.exception(f"Error getting user: {str(e)}")
            raise BaseAppException(f"Error getting user: {str(e)}") from e
        
    async def create_user(self, user_instance: UserSchemas.User):
        try:
            # Validate the user instance
            if user_instance.hashed_password is not None or user_instance.is_active is not None:
                logger.warning("User instance should not contain hashed_password or is_active fields")
                raise ValidationException("User instance should not contain hashed_password or is_active fields")
            
            # Create the user
            return await self.user_repository.create_user(user_instance)
        except ResourceAlreadyExistsException:
            raise
        except BaseAppException:
            raise
        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")
            raise BaseAppException(f"Error creating user: {str(e)}") from e
    
    async def reset_password(self, email: str, reset_password: UserSchemas.ResetPassword):
        hashed_pw = await saltAndHashedPW(reset_password.password)
        try:
            return await self.user_repository.update_user(
                UserSchemas.User(
                    email=email,
                    hashed_password=hashed_pw,
                    is_active=True
                )
            )
        except ResourceNotFoundException:
            raise
        except BaseAppException:
            raise
        except Exception as e:
            logger.exception(f"Error updating user: {str(e)}")
            raise BaseAppException(f"Error updating user: {str(e)}") from e
    
    async def deactivate_user(self, email: str):
        try:
            return await self.user_repository.update_user(
                UserSchemas.User(
                    email=email,
                    is_active=False
                )
            )
        except ResourceNotFoundException:
            raise
        except BaseAppException:
            raise
        except Exception as e:
            logger.exception(f"Error deactivating user: {str(e)}")
            raise BaseAppException(f"Error deactivating user: {str(e)}") from e
        
    