from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from sqlalchemy.orm import Session
from src.repository.implementations.PostgreSQL.models import ORM_User

class UserRepository(interface_UserRepository.UserRepository):

    def __init__(self, db: Session):
        self.db = db

    async def get_table(self):
        print("get_table method called")
        return True

    async def get_user(self, email: str):
        print("get_user method called with email:", email)
        return True

    async def create_user(self, User_instance: UserSchemas.User):
        try:
            db_user = ORM_User.UserORM(
                email=User_instance.email,
                hashed_password=User_instance.hashed_password,
                salt=User_instance.salt,
                is_active=True if User_instance.is_active else False
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            print("create_user method called with User_instance:", User_instance)
            return True
        except Exception as e:
            print("Error creating user:", str(e))
            return False

    async def update_user(self, User_instance: UserSchemas.User):
        print("update_user method called with User_instance:", User_instance)
        return True