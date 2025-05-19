from src.repository.interfaces import interface_SubscriptionRepository
from src.schemas import SubscriptionSchemas
from src.exceptions import BaseAppException, ResourceNotFoundException, ValidationException, ResourceAlreadyExistsException
import logging
from src.service.utils import *
from typing import Dict, Any

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
            logger.exception(f"Error getting subscription: {str(e)}")
            raise BaseAppException(f"Error getting subscription: {str(e)}") from e
    
    async def create_subscription(
            self,
            CreateSubscription_instance: SubscriptionSchemas.CreateSubscription,
            eventtype_prefix: str,
            payload_add: Dict[str, Any] = None
        ) -> SubscriptionSchemas.SubscriptionResponse:
        subscription_id = generate_unique_id()
        try:
            # Create the subscription
            await self.subscription_repository.create_subscription(

                Subscription_instance = SubscriptionSchemas.Subscription(
                    subscription_id=subscription_id,
                    subscription_type=CreateSubscription_instance.subscription_type,
                    email=CreateSubscription_instance.email,
                    is_active=True # Default to True on creation
                ),

                Outbox_instance = SubscriptionSchemas.Outbox(
                    aggregatetype = "subscription",
                    aggregateid = subscription_id,
                    eventtype_prefix = eventtype_prefix,
                    payload = {
                        "subscription_id": subscription_id,
                        "email": CreateSubscription_instance.email,
                        **(payload_add or {})
                    }
                )
                
            )

            # Return the subscription response
            return SubscriptionSchemas.SubscriptionResponse(
                subscription_id=subscription_id
            )
        
        except ResourceAlreadyExistsException:
            raise
        except Exception as e:
            logger.exception(f"Error creating subscription: {str(e)}")
            raise BaseAppException(f"Error creating subscription: {str(e)}") from e
    

    async def delete_subscription(
            self,
            subscription_id: str,
            payload_add: Dict[str, Any] = {}
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
            await self.subscription_repository.delete_subscription(

                subscription_id = subscription_id,

                Outbox_instance = SubscriptionSchemas.Outbox(
                    aggregatetype = "subscription",
                    aggregateid = subscription_id,
                    eventtype_prefix = "subscription_deleted",
                    payload = {
                        "subscription_id": subscription_id
                    }.update(payload_add)
                )
            )

        except ResourceNotFoundException:
            raise
        except Exception as e:
            logger.exception(f"Error deleting subscription: {str(e)}")
            raise BaseAppException(f"Error deleting subscription: {str(e)}") from e