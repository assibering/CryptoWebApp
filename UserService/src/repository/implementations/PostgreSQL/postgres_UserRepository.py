from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from sqlalchemy.orm import Session
from src.repository.implementations.PostgreSQL.models.ORM_User import UserORM

class UserRepository(interface_UserRepository.UserRepository):

    def __init__(self, db: Session):
        self.db = db

    async def get_user(self, email: str) -> UserSchemas.User:
        user = self.db.query(UserORM).filter(UserORM.email == email).first()
        if user:    
            return UserSchemas.User(
                email=user.email,
                is_active=user.is_active
            )
        else:
            raise Exception("User not found")

    async def create_user(self, User_instance: UserSchemas.User):
        try:
            db_user = UserORM(
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
        db_user = self.db.query(UserORM).filter(UserORM.email == User_instance.email).first()
        if not db_user:
            raise Exception("User not found")
        
        update_fields = User_instance.dict(exclude_unset=True)

        for field, value in update_fields.items():
            setattr(db_user, field, value)  # dynamically update each field
        
        self.db.commit()
        self.db.refresh(db_user)

        print("update_user method called with User_instance:", User_instance)
        return True