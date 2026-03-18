import stripe
from fastapi import HTTPException, status

from app.api.finance.dependencies import invalidate_premium_cache
from app.api.finance.s3_repository import S3YieldRepository
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


def set_premium(sub: str, value: bool) -> None:
    """Write is_premium into the user's settings.json."""
    repo = S3YieldRepository(user_key=sub)
    user_settings = repo.read_settings()
    user_settings["is_premium"] = value
    repo.write_settings(user_settings)
    invalidate_premium_cache(sub)


def create_checkout_url(plan: str, email: str, sub: str) -> str:
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
        client_reference_id=sub,
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
        sub = data.get("client_reference_id")
        if sub:
            set_premium(sub, True)
            # Store sub on the Stripe customer so we can find it on cancellation
            stripe.Customer.modify(data["customer"], metadata={"sub": sub})
            logger.info("premium_granted", user=sub, event_id=event["id"])
        else:
            logger.warning("checkout_completed_no_sub", event_id=event["id"])

    elif event_type in (
        "customer.subscription.deleted",
        "customer.subscription.paused",
    ):
        customer = stripe.Customer.retrieve(data["customer"])
        sub = customer.get("metadata", {}).get("sub")
        if sub:
            set_premium(sub, False)
            logger.info(
                "premium_revoked",
                user=sub,
                event_type=event_type,
                event_id=event["id"],
            )
        else:
            logger.warning(
                "subscription_event_no_sub",
                event_type=event_type,
                event_id=event["id"],
            )

    elif event_type == "invoice.payment_failed":
        logger.info(
            "invoice_payment_failed",
            customer=data.get("customer"),
            event_id=event["id"],
        )
