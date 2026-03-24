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


def _get_active_subscription(email: str):
    """Return (customer_id, subscription) for the user's active subscription.

    Raises 404 if no customer or no active subscription exists.
    """
    customers = stripe.Customer.list(email=email, limit=1)
    if not customers.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Stripe customer found for this account",
        )
    subscriptions = stripe.Subscription.list(
        customer=customers.data[0].id,
        status="active",
        limit=1,
    )
    if not subscriptions.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    return subscriptions.data[0]


def get_subscription_status(email: str) -> dict:
    """Return current subscription state from Stripe.

    Returns ``cancel_at_period_end`` and ``ends_at`` so the frontend can
    show the appropriate action (cancel vs. reactivate).
    """
    _require_stripe()
    try:
        sub = _get_active_subscription(email)
    except HTTPException:
        return {"active": False, "cancel_at_period_end": False, "ends_at": None}
    except stripe.StripeError as exc:
        logger.error("stripe_status_failed", user=email, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve subscription status",
        ) from exc
    cancel_at_period_end = getattr(sub, "cancel_at_period_end", False)
    cancel_at = getattr(sub, "cancel_at", None) or getattr(
        sub, "current_period_end", None
    )

    # Interval comes from the first subscription item's price
    interval: str | None = None
    try:
        interval = sub.items.data[0].price.recurring.interval
    except Exception:
        pass

    return {
        "active": True,
        "cancel_at_period_end": cancel_at_period_end,
        "ends_at": cancel_at if cancel_at_period_end else None,
        "started_at": getattr(sub, "start_date", None),
        "current_period_start": getattr(sub, "current_period_start", None),
        "current_period_end": getattr(sub, "current_period_end", None),
        "interval": interval,
    }


def reactivate_subscription(email: str) -> dict:
    """Remove a pending cancellation so the subscription continues as normal."""
    _require_stripe()
    try:
        sub = _get_active_subscription(email)
        stripe.Subscription.modify(sub.id, cancel_at_period_end=False)
    except HTTPException:
        raise
    except stripe.StripeError as exc:
        logger.error("stripe_reactivate_failed", user=email, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reactivate subscription",
        ) from exc
    logger.info("subscription_reactivated", user=email)
    return {"status": "reactivated"}


def cancel_subscription(email: str) -> dict:
    """Cancel the user's active Stripe subscription at the end of the current period.

    Returns a dict with ``ends_at`` (Unix timestamp) so the frontend can
    display when access expires.  Raises 404 if no active subscription is found.
    """
    _require_stripe()
    try:
        existing = _get_active_subscription(email)
        sub = stripe.Subscription.modify(existing.id, cancel_at_period_end=True)
    except HTTPException:
        raise
    except stripe.StripeError as exc:
        logger.error("stripe_cancel_failed", user=email, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to cancel subscription",
        ) from exc
    logger.info("subscription_cancel_scheduled", user=email)
    # cancel_at is set to current_period_end when cancel_at_period_end=True;
    # fall back to current_period_end for older API shapes.
    ends_at = getattr(sub, "cancel_at", None) or getattr(
        sub, "current_period_end", None
    )
    return {"ends_at": ends_at}


def handle_webhook(payload: bytes, sig_header: str, db: Session) -> None:
    """Verify and process an incoming Stripe webhook event."""
    _require_stripe()
    from app.api.subscription.webhook import StripeWebhookHandler

    StripeWebhookHandler(db).handle(payload, sig_header)
