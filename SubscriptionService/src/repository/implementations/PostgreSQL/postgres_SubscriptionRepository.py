from src.repository.interfaces import interface_SubscriptionRepository
from src.schemas import SubscriptionSchemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.repository.implementations.PostgreSQL.models.ORM_Subscription import SubscriptionORM, SubscriptionsOutboxORM
from src.exceptions import ResourceNotFoundException, BaseAppException, ResourceAlreadyExistsException
import logging
from sqlalchemy.exc import IntegrityError
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SubscriptionRepository(interface_SubscriptionRepository.SubscriptionRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_subscription(self, subscription_id: str) -> SubscriptionSchemas.Subscription:
        try:
            stmt = select(SubscriptionORM).where(SubscriptionORM.subscription_id == subscription_id)
            result = await self.db.execute(stmt)
            db_subscription = result.scalar_one_or_none()
            if db_subscription:    
                return SubscriptionSchemas.Subscription(
                    subscription_id=str(db_subscription.subscription_id),
                    subscription_type=db_subscription.subscription_type,
                    email=db_subscription.email,
                    is_active=db_subscription.is_active
                )
            else:
                logger.warning(f"Subscription with subscription_id {subscription_id} not found")
                raise ResourceNotFoundException(f"Subscription with subscription_id {subscription_id} not found")
            
        except ResourceNotFoundException:
            raise

        except Exception as e:
            logger.exception(f"Error getting subscription: {str(e)}")
            raise BaseAppException(f"Internal database error: {str(e)}") from e
    
    async def create_subscription(
            self,
            Subscription_instance: SubscriptionSchemas.Subscription,
            Outbox_instance: SubscriptionSchemas.Outbox
        ) -> None:
        try:
            db_subscription = SubscriptionORM(
                subscription_id=Subscription_instance.subscription_id,
                subscription_type=Subscription_instance.subscription_type,
                email=Subscription_instance.email,
                is_active=False if Subscription_instance.is_active == False else True #default to True
            )

            outbox_event = SubscriptionsOutboxORM(
                aggregatetype = Outbox_instance.aggregatetype,
                aggregateid = Outbox_instance.aggregateid,
                eventtype = f"{Outbox_instance.eventtype_prefix}_success",
                payload = Outbox_instance.payload
            )

            # Start transaction
            async with self.db.begin():  # This ensures atomicity
                self.db.add(db_subscription)
                self.db.add(outbox_event)
            
            return SubscriptionSchemas.Subscription(
                subscription_id = str(db_subscription.subscription_id),
                subscription_type = db_subscription.subscription_type,
                email = db_subscription.email,
                is_active = db_subscription.is_active
            )
        
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                logger.warning(f"Subscription with subscription_id {Subscription_instance.subscription_id} already exists")

                fail_event = SubscriptionsOutboxORM(
                    aggregatetype = Outbox_instance.aggregatetype,
                    aggregateid = Outbox_instance.aggregateid,
                    eventtype = f"{Outbox_instance.eventtype_prefix}_failed",
                    payload = Outbox_instance.payload.update({
                        "exception": "ResourceAlreadyExistsException"
                    })
                )

                async with self.db.begin():
                    self.db.add(fail_event)

                raise ResourceAlreadyExistsException(f"Subscription with subscription_id {Subscription_instance.subscription_id} already exists")
            else:
                # Some other kind of IntegrityError (e.g., null value, foreign key constraint, etc)
                logger.exception(f"Error creating user: {str(e)}")

                fail_event = SubscriptionsOutboxORM(
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
            logger.exception(f"Error creating subscription: {str(e)}")

            fail_event = SubscriptionsOutboxORM(
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
    

    async def delete_subscription(
            self,
            subscription_id: str,
            Outbox_instance: SubscriptionSchemas.Outbox
        ) -> None:
        """
        Delete a subscription by subscription ID.
        
        Args:
            subscription_id: The subscription_id of the subscription to delete
            
        Raises:
            ResourceNotFoundException: If the subscription doesn't exist
            BaseAppException: For any other errors
        """
        try:
            # First check if the user exists
            stmt = select(SubscriptionORM).where(SubscriptionORM.subscription_id == subscription_id)
            result = await self.db.execute(stmt)
            db_subscription = result.scalar_one_or_none()
            
            if not db_subscription:
                logger.warning(f"Subscription with ID {subscription_id} not found for deletion")
                
                # Create a failed event
                fail_event = SubscriptionsOutboxORM(
                    aggregatetype = Outbox_instance.aggregatetype,
                    aggregateid = Outbox_instance.aggregateid,
                    eventtype = f"{Outbox_instance.eventtype_prefix}_failed",
                    payload = Outbox_instance.payload.update({
                        "exception": "ResourceNotFoundException"
                    })
                )
                
                async with self.db.begin():
                    self.db.add(fail_event)
                    
                raise ResourceNotFoundException(f"Subscription with ID {subscription_id} not found for deletion")
            
            # Create a success event
            success_event = SubscriptionsOutboxORM(
                aggregatetype = Outbox_instance.aggregatetype,
                aggregateid = Outbox_instance.aggregateid,
                eventtype = f"{Outbox_instance.eventtype_prefix}_success",
                payload = Outbox_instance.payload
            )
            
            # Start transaction for deletion and event
            async with self.db.begin():
                # Delete the user
                delete_stmt = delete(SubscriptionORM).where(SubscriptionORM.subscription_id == subscription_id)
                await self.db.execute(delete_stmt)
                
                # Add the outbox event
                self.db.add(success_event)
                
            logger.info(f"Subscription with ID {subscription_id} deleted successfully")
                
        except ResourceNotFoundException:
            raise
            
        except Exception as e:
            logger.exception(f"Error deleting user: {str(e)}")
            
            # Create a failed event
            fail_event = SubscriptionsOutboxORM(
                aggregatetype = Outbox_instance.aggregatetype,
                aggregateid = Outbox_instance.aggregateid,
                eventtype = f"{Outbox_instance.eventtype_prefix}_failed",
                payload = Outbox_instance.payload.update({
                    "exception": "BaseAppException"
                })
            )
            
            try:
                async with self.db.begin():
                    self.db.add(fail_event)
            except Exception as outbox_error:
                logger.exception(f"Error creating outbox event: {str(outbox_error)}")
                
            raise BaseAppException(f"Error deleting user: {str(e)}") from e