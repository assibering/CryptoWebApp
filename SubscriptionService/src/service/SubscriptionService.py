from src.repository.interfaces import interface_SubscriptionRepository
from src.schemas import SubscriptionSchemas
from src.exceptions import BaseAppException, ResourceNotFoundException, ValidationException, ResourceAlreadyExistsException
import logging
from src.service.utils import *

logger = logging.getLogger(__name__)

class SubscriptionService:

    def __init__(self, subscription_repository: interface_SubscriptionRepository):
        self.subscription_repository = subscription_repository
    
    async def get_subscription(self, subscription_id: str) -> SubscriptionSchemas.SubscriptionResponse:
        try:
            subscription = await self.subscription_repository.get_subscription(subscription_id)
            return SubscriptionSchemas.SubscriptionResponse(
                subscription_id=subscription.subscription_id,
                subscription_type=subscription.subscription_type,
                email=subscription.email,
                is_active=subscription.is_active
            )
        except ResourceNotFoundException:
            raise #Re-raise from repository layer
        except Exception as e:
            logger.exception(f"Error getting user: {str(e)}")
            raise BaseAppException(f"Error getting user: {str(e)}") from e
    
    async def create_subscription(
            self,
            subscription_create: SubscriptionSchemas.CreateSubscription
        ) -> SubscriptionSchemas.SubscriptionResponse:
        subscription_id = generate_unique_id()
        try:
            # Create the subscription
            subscription = await self.subscription_repository.create_subscription(
                SubscriptionSchemas.Subscription(
                    subscription_id=subscription_id,
                    subscription_type=subscription_create.subscription_type,
                    email=subscription_create.email,
                    is_active=subscription_create.is_active
                )
            )

            # Return the subscription response
            return SubscriptionSchemas.SubscriptionResponse(
                subscription_id=subscription.subscription_id,
                subscription_type=subscription.subscription_type,
                email=subscription.email,
                is_active=subscription.is_active
            )
        except ResourceAlreadyExistsException:
            raise
        except Exception as e:
            logger.exception(f"Error creating user: {str(e)}")
            raise BaseAppException(f"Error creating user: {str(e)}") from e