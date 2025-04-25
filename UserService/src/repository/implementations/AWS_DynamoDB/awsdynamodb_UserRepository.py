from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from src.exceptions import ResourceNotFoundException, BaseAppException, ResourceAlreadyExistsException
import logging
from typing import Any

logger = logging.getLogger(__name__)

class UserRepository(interface_UserRepository.UserRepository):

    def __init__(self, db: Any):
        self.db = db

    async def get_user(self, email: str) -> UserSchemas.User:
        try:
            return
            
        except ResourceNotFoundException:
            raise

        except Exception as e:
            logger.exception(f"Error getting user: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def create_user(self, User_instance: UserSchemas.User) -> UserSchemas.User:
        try:
            return
        
        except ResourceAlreadyExistsException:
            raise

        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def update_user(self, User_instance: UserSchemas.User) -> UserSchemas.User:
        try:
            return
            
        except ResourceNotFoundException:
            raise
        
        except Exception as e:
            logger.exception(f"Error updating user: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e