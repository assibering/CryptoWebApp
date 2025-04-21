from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.repository.implementations.PostgreSQL.models.ORM_User import UserORM

class UserRepository(interface_UserRepository.UserRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, email: str) -> UserSchemas.User:
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if db_user:    
            return UserSchemas.User(
                email=db_user.email,
                is_active=db_user.is_active
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
            await self.db.commit()
            await self.db.refresh(db_user)
            print("create_user method called with User_instance:", User_instance)
            return True
        except Exception as e:
            print("Error creating user:", str(e))
            return False

    async def update_user(self, User_instance: UserSchemas.User):
        stmt = select(UserORM).where(UserORM.email == User_instance.email)
        result = await self.db.execute(stmt)
        db_user = result.scalar_one_or_none()
        if not db_user:
            raise Exception("User not found")
        
        update_fields = User_instance.dict(exclude_unset=True)

        for field, value in update_fields.items():
            setattr(db_user, field, value)  # dynamically update each field
        
        await self.db.commit()
        await self.db.refresh(db_user)

        print("update_user method called with User_instance:", User_instance)
        return True