from fastapi import APIRouter, Depends
from src.schemas import SubscriptionSchemas
from src.dependencies import get_subscription_service
from src.service.SubscriptionService import SubscriptionService

router = APIRouter(
    prefix="/subscriptions"
)

@router.get("", status_code=200)
async def get_subscription(
    subscription_id: str,
    subscription_service: SubscriptionService = Depends(get_subscription_service)):
    return await subscription_service.get_subscription(subscription_id=subscription_id)

@router.post("/create-subscription", status_code=201)
async def create_subscription(
    subscription_create: SubscriptionSchemas.CreateSubscription,
    subscription_service: SubscriptionService = Depends(get_subscription_service)):
    return await subscription_service.create_subscription(CreateSubscription_instance=subscription_create)