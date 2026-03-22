import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.finance.dependencies import invalidate_premium_cache
from app.core import settings
from app.core.enums import SubscriptionPlan
from app.core.logging_config import logger
from app.db.models import User

STRIPE_ENABLED = bool(settings.STRIPE_SECRET_KEY)

if STRIPE_ENABLED:
    stripe.api_key = settings.STRIPE_SECRET_KEY

_PLAN_TO_PRICE = {
    SubscriptionPlan.monthly: settings.STRIPE_PRICE_ID_MONTHLY,
    SubscriptionPlan.yearly: settings.STRIPE_PRICE_ID_YEARLY,
}


def _require_stripe() -> None:
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )


def set_premium(
    sub: str, value: bool, db: Session, plan: SubscriptionPlan | None = None
) -> None:
    """Set is_premium and subscription_plan on the User row and bust the cache."""
    user = db.query(User).filter_by(sub=sub).first()
    if not user:
        logger.warning("set_premium_user_not_found", user=sub)
        return
    user.is_premium = value
    user.subscription_plan = plan.value if plan else None
    db.flush()
    invalidate_premium_cache(sub)


def create_checkout_url(plan: SubscriptionPlan, email: str, sub: str) -> str:
    """Create a Stripe Checkout session and return the hosted URL."""
    _require_stripe()
    price_id = _PLAN_TO_PRICE.get(plan)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown plan: {plan!r}. Use 'monthly' or 'yearly'.",
        )
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            customer_email=email,
            client_reference_id=sub,
            metadata={"plan": plan.value},
            success_url=f"{settings.APP_URL}/subscription/success",
            cancel_url=f"{settings.APP_URL}/subscriptions",
        )
    except stripe.StripeError as exc:
        logger.error("stripe_checkout_failed", plan=plan, user=sub, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to create checkout session",
        ) from exc
    logger.info("stripe_checkout_created", plan=plan, user=sub)
    return session.url


def create_portal_url(email: str) -> str:
    """Create a Stripe Billing Portal session and return the URL."""
    _require_stripe()
    try:
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
    except HTTPException:
        raise
    except stripe.StripeError as exc:
        logger.error("stripe_portal_failed", user=email, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to create billing portal session",
        ) from exc
    logger.info("stripe_portal_created", user=email)
    return session.url


def handle_webhook(payload: bytes, sig_header: str, db: Session) -> None:
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
            raw_plan = data.get("metadata", {}).get("plan")
            try:
                plan: SubscriptionPlan | None = SubscriptionPlan(raw_plan)
            except (ValueError, KeyError):
                plan = None
            set_premium(sub, True, db, plan=plan)
            # Store sub on the Stripe customer so we can find it on cancellation
            try:
                stripe.Customer.modify(data["customer"], metadata={"sub": sub})
            except stripe.StripeError as exc:
                logger.error(
                    "stripe_customer_modify_failed",
                    user=sub,
                    event_id=event["id"],
                    error=str(exc),
                )
            logger.info("premium_granted", user=sub, plan=plan, event_id=event["id"])
        else:
            logger.warning("checkout_completed_no_sub", event_id=event["id"])

    elif event_type in (
        "customer.subscription.deleted",
        "customer.subscription.paused",
    ):
        try:
            customer = stripe.Customer.retrieve(data["customer"])
        except stripe.StripeError as exc:
            logger.error(
                "stripe_customer_retrieve_failed",
                event_type=event_type,
                event_id=event["id"],
                error=str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to retrieve Stripe customer",
            ) from exc
        sub = customer.get("metadata", {}).get("sub")
        if sub:
            set_premium(sub, False, db, plan=None)
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
