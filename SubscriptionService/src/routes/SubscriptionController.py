from fastapi import APIRouter, Depends, Request
from src.schemas import SubscriptionSchemas
from src.dependencies import get_subscription_service
from src.service.SubscriptionService import SubscriptionService
from src.exceptions import BaseAppException
from src.config import get_settings
import stripe
from .utils import billing_anchor_friday_utc_unix_timestamp
import logging

logger = logging.getLogger(__name__)
stripe.api_key = get_settings().STRIPE_SECRET_KEY

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
    return await subscription_service.create_subscription(
        CreateSubscription_instance=subscription_create,
        eventtype_prefix="subscription_created"
    )

@router.get("/checkout-session", status_code=200)
async def get_checkout_session(
    subscription_service: SubscriptionService = Depends(get_subscription_service)
    ):
    try:
        session = stripe.checkout.Session.create(
            success_url=get_settings().STRIPE_SUCCESS_URL,
            cancel_url=get_settings().STRIPE_CANCEL_URL,
            line_items=[
                {
                    "price": "price_1T8XLQCZn3sXV588NngiVAzS",
                    "quantity": 1
                }
            ],
            mode="subscription",
            billing_address_collection="required",
            subscription_data={
                "billing_cycle_anchor": billing_anchor_friday_utc_unix_timestamp(),
                "proration_behavior": "create_prorations"
            }
        )

        return {"checkout_url": session.url}
        
    except Exception as e:
        logger.exception(f"Error creating checkout session: {str(e)}")
        raise BaseAppException(f"Error creating checkout session: {str(e)}") from e
    

    return await subscription_service.create_subscription(
        CreateSubscription_instance=subscription_create,
        eventtype_prefix="subscription_created"
    )

@router.post("/webhook", status_code=200)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = get_settings().STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise BaseAppException("Invalid signature", status_code=400)
    if event["type"] == "checkout.session.completed":
        logger.info("Checkout session completed event received")
        logger.info(f"Event data: {event}")
    return {"status": "success"}