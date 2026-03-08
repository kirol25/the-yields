import boto3
import stripe
from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app import settings
from app.api.auth import invalidate_premium_cache
from app.api.finance.dependencies import AuthContextDep

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

STRIPE_ENABLED = bool(settings.STRIPE_SECRET_KEY)

if STRIPE_ENABLED:
    stripe.api_key = settings.STRIPE_SECRET_KEY

_PLAN_TO_PRICE = {
    "monthly": settings.STRIPE_PRICE_ID_MONTHLY,
    "yearly": settings.STRIPE_PRICE_ID_YEARLY,
}


def _set_premium(user_email: str, value: bool) -> None:
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
    except ClientError:
        # Non-fatal — log in production; don't break the webhook response
        pass


class CheckoutRequest(BaseModel):
    plan: str  # "monthly" | "yearly"


# ── routes ────────────────────────────────────────────────────────────────────


@router.post(
    "/checkout",
    status_code=status.HTTP_200_OK,
    summary="Create Stripe Checkout session",
    description="Creates a Stripe Checkout session for the given plan and returns "
    "the hosted checkout URL. Requires STRIPE_SECRET_KEY to be configured.",
)
def create_checkout_session(
    body: CheckoutRequest,
    ctx: AuthContextDep,
) -> dict[str, str]:
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )
    price_id = _PLAN_TO_PRICE.get(body.plan)
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown plan: {body.plan!r}. Use 'monthly' or 'yearly'.",
        )

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=ctx["email"],
        client_reference_id=ctx["email"],
        success_url=f"{settings.APP_URL}/subscription/success",
        cancel_url=f"{settings.APP_URL}/subscriptions",
    )
    return {"url": session.url}


@router.post(
    "/portal",
    status_code=status.HTTP_200_OK,
    summary="Create Stripe Customer Portal session",
    description="Returns a Stripe Billing Portal URL so the user can manage or "
    "cancel their subscription.",
)
def create_portal_session(ctx: AuthContextDep) -> dict[str, str]:
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )

    # Look up the Stripe customer by email
    customers = stripe.Customer.list(email=ctx["email"], limit=1)
    if not customers.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Stripe customer found for this account",
        )

    session = stripe.billing_portal.Session.create(
        customer=customers.data[0].id,
        return_url=f"{settings.APP_URL}/subscriptions",
    )
    return {"url": session.url}


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Stripe webhook receiver",
    description="Receives and verifies Stripe webhook events. "
    "Updates Cognito custom:is_premium on checkout completion or cancellation.",  # noqa: E501
)
async def stripe_webhook(request: Request) -> dict[str, str]:
    if not STRIPE_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

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

    if event_type == "checkout.session.completed":
        email = data.get("client_reference_id") or data.get("customer_email")
        if email:
            _set_premium(email, True)
            invalidate_premium_cache(email)

    elif event_type in (
        "customer.subscription.deleted",
        "customer.subscription.paused",
    ):
        # Retrieve the customer to get their email
        customer = stripe.Customer.retrieve(data["customer"])
        email = customer.get("email")
        if email:
            _set_premium(email, False)
            invalidate_premium_cache(email)

    elif event_type == "invoice.payment_failed":
        # Optionally revoke premium after repeated failures
        # (Stripe retries — only act on subscription deletion above)
        pass

    return {"status": "ok"}
