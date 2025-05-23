from src.repository.interfaces import interface_UserRepository
from src.schemas import UserSchemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.repository.implementations.PostgreSQL.models.ORM_User import UserORM, UsersOutboxORM
from src.exceptions import ResourceNotFoundException, BaseAppException, ResourceAlreadyExistsException, ValidationException
import logging
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any

logger = logging.getLogger(__name__)

class UserRepository(interface_UserRepository.UserRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(
            self,
            email: str
        ) -> UserSchemas.User:

        try:
            stmt = select(UserORM).where(UserORM.email == email)
            result = await self.db.execute(stmt)
            db_user = result.scalar_one_or_none()
            if db_user:    
                return UserSchemas.User(
                    email=db_user.email,
                    is_active=db_user.is_active
                )
            else:
                logger.warning(f"User with email {email} not found")
                raise ResourceNotFoundException(f"User with email {email} not found")
            
        except ResourceNotFoundException:
            raise

        except Exception as e:
            logger.exception(f"Error getting user: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def create_user(
            self,
            User_instance: UserSchemas.User,
            Outbox_instance: UserSchemas.Outbox
        ) -> None:

        try:
            db_user = UserORM(
                email=User_instance.email,
                hashed_password=User_instance.hashed_password,
                is_active=True if User_instance.is_active else False
            )

            outbox_event = UsersOutboxORM(
                aggregatetype = Outbox_instance.aggregatetype,
                aggregateid = Outbox_instance.aggregateid,
                eventtype = f"{Outbox_instance.eventtype_prefix}_success",
                payload = Outbox_instance.payload
            )

            # Start transaction
            async with self.db.begin():  # This ensures atomicity
                self.db.add(db_user)
                self.db.add(outbox_event)
        
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                logger.warning(f"User with email {User_instance.email} already exists")

                fail_event = UsersOutboxORM(
                    aggregatetype = Outbox_instance.aggregatetype,
                    aggregateid = Outbox_instance.aggregateid,
                    eventtype = f"{Outbox_instance.eventtype_prefix}_failed",
                    payload = Outbox_instance.payload.update({
                        "exception": "ResourceAlreadyExistsException"
                    })
                )

                async with self.db.begin():
                    self.db.add(fail_event)

                raise ResourceAlreadyExistsException(f"User with email {User_instance.email} already exists")
            else:
                # Some other kind of IntegrityError (e.g., null value, foreign key constraint, etc)
                logger.exception(f"Error creating user: {str(e)}")

                fail_event = UsersOutboxORM(
                    aggregatetype = Outbox_instance.aggregatetype,
                    aggregateid = Outbox_instance.aggregateid,
                    eventtype = f"{Outbox_instance.eventtype_prefix}_failed",
                    payload = Outbox_instance.payload.update({
                        "exception": "BaseAppException"
                    })
                )

                async with self.db.begin():
                    self.db.add(fail_event)

                raise BaseAppException(f"Database integrity error: {str(e)}") from e
            
        except ResourceAlreadyExistsException:
            raise

        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")

            fail_event = UsersOutboxORM(
                aggregatetype = Outbox_instance.aggregatetype,
                aggregateid = Outbox_instance.aggregateid,
                eventtype = f"{Outbox_instance.eventtype_prefix}_failed",
                payload = Outbox_instance.payload.update({
                    "exception": "BaseAppException"
                })
            )

            async with self.db.begin():
                self.db.add(fail_event)

            raise BaseAppException(f"Internal database error: {str(e)}") from e

    async def update_user(
            self,
            User_instance: UserSchemas.User
        ) -> None:

        try:
            stmt = select(UserORM).where(UserORM.email == User_instance.email)
            result = await self.db.execute(stmt)
            db_user = result.scalar_one_or_none()

            if db_user:
                update_fields = User_instance.model_dump(exclude_unset=True)

                for field, value in update_fields.items():
                    setattr(db_user, field, value)  # dynamically update each field
                
                await self.db.commit()
                await self.db.refresh(db_user)
                
            
            else:
                logger.warning(f"User with email {User_instance.email} not found")
                raise ResourceNotFoundException(f"User with email {User_instance.email} not found")
            
        except ResourceNotFoundException:
            raise
        
        except Exception as e:
            logger.exception(f"Error updating user: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e