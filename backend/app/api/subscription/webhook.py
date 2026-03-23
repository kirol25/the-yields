"""Stripe webhook event handling."""

import stripe
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.subscription.service import set_premium
from app.core import settings
from app.core.enums import SubscriptionPlan
from app.core.logging_config import logger


class StripeWebhookHandler:
    """Dispatches Stripe webhook events to dedicated handler methods."""

    _HANDLERS: dict[str, str] = {
        "checkout.session.completed": "_on_checkout_completed",
        "customer.subscription.deleted": "_on_subscription_ended",
        "customer.subscription.paused": "_on_subscription_ended",
        "invoice.payment_failed": "_on_payment_failed",
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def handle(self, payload: bytes, sig_header: str) -> None:
        event = self._verify_signature(payload, sig_header)
        event_type = event["type"]
        event_id = event["id"]
        data = event["data"]["object"]

        logger.info("stripe_webhook_received", event_type=event_type, event_id=event_id)

        handler_name = self._HANDLERS.get(event_type)
        if handler_name:
            getattr(self, handler_name)(event_id, event_type, data)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _verify_signature(self, payload: bytes, sig_header: str) -> stripe.Event:
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature",
            )

    def _resolve_plan(self, raw_plan: str | None) -> SubscriptionPlan | None:
        try:
            return SubscriptionPlan(raw_plan)
        except (ValueError, KeyError):
            return None

    def _tag_customer_with_sub(self, customer_id: str, sub: str, event_id: str) -> None:
        """Store the internal user `sub` on the Stripe Customer for later lookups."""
        try:
            stripe.Customer.modify(customer_id, metadata={"sub": sub})
        except stripe.StripeError as exc:
            logger.error(
                "stripe_customer_modify_failed",
                user=sub,
                event_id=event_id,
                error=str(exc),
            )

    def _retrieve_customer(
        self, customer_id: str, event_type: str, event_id: str
    ) -> stripe.Customer:
        try:
            return stripe.Customer.retrieve(customer_id)
        except stripe.StripeError as exc:
            logger.error(
                "stripe_customer_retrieve_failed",
                event_type=event_type,
                event_id=event_id,
                error=str(exc),
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to retrieve Stripe customer",
            ) from exc

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_checkout_completed(
        self, event_id: str, _event_type: str, data: dict
    ) -> None:
        sub = data.get("client_reference_id")
        if not sub:
            logger.warning("checkout_completed_no_sub", event_id=event_id)
            return

        plan = self._resolve_plan(data.get("metadata", {}).get("plan"))
        set_premium(sub, True, self.db, plan=plan)
        self._tag_customer_with_sub(data["customer"], sub, event_id)
        logger.info("premium_granted", user=sub, plan=plan, event_id=event_id)

    def _on_subscription_ended(
        self, event_id: str, event_type: str, data: dict
    ) -> None:
        customer = self._retrieve_customer(data["customer"], event_type, event_id)
        sub = customer.get("metadata", {}).get("sub")
        if not sub:
            logger.warning(
                "subscription_event_no_sub",
                event_type=event_type,
                event_id=event_id,
            )
            return

        set_premium(sub, False, self.db, plan=None)
        logger.info(
            "premium_revoked", user=sub, event_type=event_type, event_id=event_id
        )

    def _on_payment_failed(self, event_id: str, _event_type: str, data: dict) -> None:
        logger.info(
            "invoice_payment_failed",
            customer=data.get("customer"),
            event_id=event_id,
        )
