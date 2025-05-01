from src.repository.interfaces import interface_SubscriptionRepository
from src.schemas import SubscriptionSchemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.repository.implementations.PostgreSQL.models.ORM_Subscription import SubscriptionORM, SubscriptionsOutboxORM
from src.exceptions import ResourceNotFoundException, BaseAppException, ResourceAlreadyExistsException
import logging
from sqlalchemy.exc import IntegrityError

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
                    subscription_id=db_subscription.subscription_id,
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
            transaction_id: str,
        ) -> SubscriptionSchemas.Subscription:
        try:
            db_subscription = SubscriptionORM(
                subscription_id=Subscription_instance.subscription_id,
                subscription_type=Subscription_instance.subscription_type,
                email=Subscription_instance.email,
                is_active=False if Subscription_instance.is_active == False else True #default to True
            )

            outbox_event = SubscriptionsOutboxORM(
                aggregatetype = "subscription",
                aggregateid = Subscription_instance.email,
                type = "subscription_created_success",
                payload = Subscription_instance.model_dump(),
                transaction_id = transaction_id
            )

            # Start transaction
            async with self.db.begin():  # This ensures atomicity
                self.db.add(db_subscription)
                self.db.add(outbox_event)
            
            return SubscriptionSchemas.Subscription(
                subscription_id = db_subscription.subscription_id,
                subscription_type = db_subscription.subscription_type,
                email = db_subscription.email,
                is_active = db_subscription.is_active
            )
        
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                logger.warning(f"Subscription with subscription_id {Subscription_instance.subscription_id} already exists")

                fail_event = SubscriptionsOutboxORM(
                    aggregatetype = "subscription",
                    aggregateid = Subscription_instance.email,
                    type = "subscription_created_failed",
                    payload = Subscription_instance.model_dump(),
                    transaction_id = transaction_id
                )

                async with self.db.begin():
                    self.db.add(fail_event)

                raise ResourceAlreadyExistsException(f"Subscription with subscription_id {Subscription_instance.subscription_id} already exists")
            else:
                # Some other kind of IntegrityError (e.g., null value, foreign key constraint, etc)
                logger.exception(f"Error creating user: {str(e)}")

                fail_event = SubscriptionsOutboxORM(
                    aggregatetype = "subscription",
                    aggregateid = Subscription_instance.email,
                    type = "subscription_created_failed",
                    payload = Subscription_instance.model_dump(),
                    transaction_id = transaction_id
                )

                async with self.db.begin():
                    self.db.add(fail_event)

                raise BaseAppException(f"Database integrity error: {str(e)}") from e
            
        except ResourceAlreadyExistsException:
            raise

        except Exception as e:
            logger.exception(f"Error creating subscription: {str(e)}")

            fail_event = SubscriptionsOutboxORM(
                aggregatetype = "subscription",
                aggregateid = Subscription_instance.email,
                type = "subscription_created_failed",
                payload = Subscription_instance.model_dump(),
                transaction_id = transaction_id
            )

            async with self.db.begin():
                self.db.add(fail_event)

            raise BaseAppException(f"Internal database error: {str(e)}") from e