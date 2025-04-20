from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas


class UserService:

    def __init__(self, user_repository: interface_UserRepository):
        self.user_repository = user_repository

    async def get_table(self):
        try:
            return await self.user_repository.get_table()
        except Exception as e:
            raise Exception(f"Error getting table: {str(e)}")
    
    async def get_user(self, email: str):
        try:
            return await self.user_repository.get_user(email)
        except Exception as e:
            raise Exception(f"Error getting user: {str(e)}")
        
    async def create_user(self, user_instance: UserSchemas.User):
        try:
            # Validate the user instance
            if user_instance.hashed_password or user_instance.salt or user_instance.is_active:
                raise Exception("These fields are not allowed to be set manually.")
            
            user_instance.hashed_password = "dummy_hashed_password"  # Placeholder for actual hashing logic
            user_instance.salt = "dummy_salt"  # Placeholder for actual salt generation logic
            user_instance.is_active = True  # Default value for is_active
            
            # Create the user
            return await self.user_repository.create_user(user_instance)
        
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")
    
    async def update_user(self, user_instance: UserSchemas.User):
        try:
            return await self.user_repository.update_user(user_instance)
        except Exception as e:
            raise Exception(f"Error updating user: {str(e)}")
        
    