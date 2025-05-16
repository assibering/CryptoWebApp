from abc import ABC, abstractmethod
from ...schemas import SubscriptionSchemas

class SubscriptionRepository(ABC):

    @abstractmethod
    async def get_subscription(
            self,
            subscription_id: str
        ) -> SubscriptionSchemas.Subscription:
        
        pass
    

    @abstractmethod
    async def create_subscription(
            self,
            Subscription_instance: SubscriptionSchemas.Subscription,
            Outbox_instance: SubscriptionSchemas.Outbox
        ) -> None:
        
        pass