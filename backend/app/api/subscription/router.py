from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.finance.dependencies import AuthContextDep
from app.api.subscription import service
from app.api.subscription.schemas import CheckoutRequest
from app.core.limiter import limiter
from app.db.session import get_db

router = APIRouter(prefix="/api/subscription", tags=["subscription"])


@router.post(
    "/checkout",
    status_code=status.HTTP_200_OK,
    summary="Create Stripe Checkout session",
    description="Creates a Stripe Checkout session for the given plan and returns "
    "the hosted checkout URL. Requires STRIPE_SECRET_KEY to be configured.",
)
@limiter.limit("10/minute")
def create_checkout_session(
    request: Request,
    body: CheckoutRequest,
    ctx: AuthContextDep,
) -> dict[str, str]:
    return {"url": service.create_checkout_url(body.plan, ctx["email"], ctx["sub"])}


@router.post(
    "/portal",
    status_code=status.HTTP_200_OK,
    summary="Create Stripe Customer Portal session",
    description="Returns a Stripe Billing Portal URL so the user can manage or "
    "cancel their subscription.",
)
@limiter.limit("10/minute")
def create_portal_session(request: Request, ctx: AuthContextDep) -> dict[str, str]:
    return {"url": service.create_portal_url(ctx["email"])}


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Stripe webhook receiver",
    description="Receives and verifies Stripe webhook events. "
    "Updates is_premium on the User row on checkout completion or cancellation.",
)
async def stripe_webhook(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    service.handle_webhook(payload, sig_header, db)
    return {"status": "ok"}
