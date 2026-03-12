import boto3
import stripe
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from app.api.auth import invalidate_premium_cache
from app.core import settings
from app.core.logging_config import logger

STRIPE_ENABLED = bool(settings.STRIPE_SECRET_KEY)

if STRIPE_ENABLED:
    stripe.api_key = settings.STRIPE_SECRET_KEY

_PLAN_TO_PRICE = {
    "monthly": settings.STRIPE_PRICE_ID_MONTHLY,
    "yearly": settings.STRIPE_PRICE_ID_YEARLY,
}


def _require_stripe() -> None:
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )


def set_premium(user_email: str, value: bool) -> None:
    """Update custom:is_premium on the Cognito user."""
    if not settings.COGNITO_REGION or not settings.COGNITO_USER_POOL_ID:
        return
    client = boto3.client("cognito-idp", region_name=settings.COGNITO_REGION)
    try:
        client.admin_update_user_attributes(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Username=user_email,
            UserAttributes=[
                {"Name": "custom:is_premium", "Value": "true" if value else "false"}
            ],
        )
    except ClientError as exc:
        logger.error("set_premium_failed", user=user_email, value=value, error=str(exc))


def create_checkout_url(plan: str, email: str) -> str:
    """Create a Stripe Checkout session and return the hosted URL."""
    _require_stripe()
    price_id = _PLAN_TO_PRICE.get(plan)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown plan: {plan!r}. Use 'monthly' or 'yearly'.",
        )
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=email,
        client_reference_id=email,
        success_url=f"{settings.APP_URL}/subscription/success",
        cancel_url=f"{settings.APP_URL}/subscriptions",
    )
    return session.url


def create_portal_url(email: str) -> str:
    """Create a Stripe Billing Portal session and return the URL."""
    _require_stripe()
    customers = stripe.Customer.list(email=email, limit=1)
    if not customers.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Stripe customer found for this account",
        )
    session = stripe.billing_portal.Session.create(
        customer=customers.data[0].id,
        return_url=f"{settings.APP_URL}/subscriptions",
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str) -> None:
    """Verify and process an incoming Stripe webhook event."""
    _require_stripe()
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    event_type = event["type"]
    data = event["data"]["object"]

    logger.info("stripe_webhook_received", event_type=event_type, event_id=event["id"])

    if event_type == "checkout.session.completed":
        email = data.get("client_reference_id") or data.get("customer_email")
        if email:
            set_premium(email, True)
            invalidate_premium_cache(email)
            logger.info("premium_granted", user=email, event_id=event["id"])
        else:
            logger.warning("checkout_completed_no_email", event_id=event["id"])

    elif event_type in (
        "customer.subscription.deleted",
        "customer.subscription.paused",
    ):
        customer = stripe.Customer.retrieve(data["customer"])
        email = customer.get("email")
        if email:
            set_premium(email, False)
            invalidate_premium_cache(email)
            logger.info(
                "premium_revoked",
                user=email,
                event_type=event_type,
                event_id=event["id"],
            )
        else:
            logger.warning(
                "subscription_event_no_email",
                event_type=event_type,
                event_id=event["id"],
            )

    elif event_type == "invoice.payment_failed":
        logger.info(
            "invoice_payment_failed",
            customer=data.get("customer"),
            event_id=event["id"],
        )
