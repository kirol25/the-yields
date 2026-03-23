"""Unit tests for subscription service and webhook handler."""

from unittest.mock import MagicMock, patch

import pytest
import stripe
from fastapi import HTTPException

from app.api.subscription.service import (
    create_checkout_url,
    create_portal_url,
    handle_webhook,
    set_premium,
)
from app.api.subscription.webhook import StripeWebhookHandler
from app.core.enums import SubscriptionPlan

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_db(user=None):
    db = MagicMock()
    db.query.return_value.filter_by.return_value.first.return_value = user
    return db


def _make_user(sub="user-sub-123", is_premium=False, subscription_plan=None):
    user = MagicMock()
    user.sub = sub
    user.is_premium = is_premium
    user.subscription_plan = subscription_plan
    return user


# ---------------------------------------------------------------------------
# set_premium
# ---------------------------------------------------------------------------


class TestSetPremium:
    def test_sets_premium_true_with_plan(self):
        user = _make_user()
        db = _make_db(user=user)
        with patch(
            "app.api.subscription.service.invalidate_premium_cache"
        ) as mock_cache:
            set_premium("user-sub-123", True, db, plan=SubscriptionPlan.monthly)

        assert user.is_premium is True
        assert user.subscription_plan == "monthly"
        db.flush.assert_called_once()
        mock_cache.assert_called_once_with("user-sub-123")

    def test_sets_premium_false_clears_plan(self):
        user = _make_user(is_premium=True, subscription_plan="yearly")
        db = _make_db(user=user)
        with patch("app.api.subscription.service.invalidate_premium_cache"):
            set_premium("user-sub-123", False, db, plan=None)

        assert user.is_premium is False
        assert user.subscription_plan is None

    def test_noop_when_user_not_found(self):
        db = _make_db(user=None)
        with patch(
            "app.api.subscription.service.invalidate_premium_cache"
        ) as mock_cache:
            set_premium("ghost-sub", True, db)

        db.flush.assert_not_called()
        mock_cache.assert_not_called()


# ---------------------------------------------------------------------------
# _require_stripe / STRIPE_ENABLED gate
# ---------------------------------------------------------------------------


class TestStripeDisabled:
    def _patch_disabled(self):
        return patch("app.api.subscription.service.STRIPE_ENABLED", False)

    def test_create_checkout_raises_503(self):
        with self._patch_disabled():
            with pytest.raises(HTTPException) as exc:
                create_checkout_url(SubscriptionPlan.monthly, "a@b.com", "sub")
        assert exc.value.status_code == 503

    def test_create_portal_raises_503(self):
        with self._patch_disabled():
            with pytest.raises(HTTPException) as exc:
                create_portal_url("a@b.com")
        assert exc.value.status_code == 503

    def test_handle_webhook_raises_503(self):
        with self._patch_disabled():
            with pytest.raises(HTTPException) as exc:
                handle_webhook(b"payload", "sig", MagicMock())
        assert exc.value.status_code == 503


# ---------------------------------------------------------------------------
# create_checkout_url
# ---------------------------------------------------------------------------


class TestCreateCheckoutUrl:
    def _patch_enabled(self):
        return patch("app.api.subscription.service.STRIPE_ENABLED", True)

    def test_returns_session_url(self):
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"

        with (
            self._patch_enabled(),
            patch(
                "app.api.subscription.service._PLAN_TO_PRICE",
                {SubscriptionPlan.monthly: "price_monthly"},
            ),
            patch("stripe.checkout.Session.create", return_value=mock_session),
        ):
            url = create_checkout_url(
                SubscriptionPlan.monthly, "user@example.com", "sub-123"
            )

        assert url == "https://checkout.stripe.com/pay/cs_test_123"

    def test_unknown_plan_raises_400(self):
        # patch _PLAN_TO_PRICE to return empty so .get() returns None
        with (
            self._patch_enabled(),
            patch("app.api.subscription.service._PLAN_TO_PRICE", {}),
        ):
            with pytest.raises(HTTPException) as exc:
                create_checkout_url(
                    SubscriptionPlan.monthly, "user@example.com", "sub-123"
                )
        assert exc.value.status_code == 400

    def test_stripe_error_raises_502(self):
        with (
            self._patch_enabled(),
            patch(
                "app.api.subscription.service._PLAN_TO_PRICE",
                {SubscriptionPlan.monthly: "price_monthly"},
            ),
            patch(
                "stripe.checkout.Session.create", side_effect=stripe.StripeError("boom")
            ),
        ):
            with pytest.raises(HTTPException) as exc:
                create_checkout_url(
                    SubscriptionPlan.monthly, "user@example.com", "sub-123"
                )
        assert exc.value.status_code == 502


# ---------------------------------------------------------------------------
# create_portal_url
# ---------------------------------------------------------------------------


class TestCreatePortalUrl:
    def _patch_enabled(self):
        return patch("app.api.subscription.service.STRIPE_ENABLED", True)

    def test_returns_portal_url(self):
        mock_customer = MagicMock()
        mock_customer.id = "cus_123"
        mock_customers = MagicMock()
        mock_customers.data = [mock_customer]

        mock_portal = MagicMock()
        mock_portal.url = "https://billing.stripe.com/session/bps_123"

        with (
            self._patch_enabled(),
            patch("stripe.Customer.list", return_value=mock_customers),
            patch("stripe.billing_portal.Session.create", return_value=mock_portal),
        ):
            url = create_portal_url("user@example.com")

        assert url == "https://billing.stripe.com/session/bps_123"

    def test_no_customer_raises_404(self):
        mock_customers = MagicMock()
        mock_customers.data = []

        with (
            self._patch_enabled(),
            patch("stripe.Customer.list", return_value=mock_customers),
        ):
            with pytest.raises(HTTPException) as exc:
                create_portal_url("nobody@example.com")
        assert exc.value.status_code == 404

    def test_stripe_error_on_list_raises_502(self):
        with (
            self._patch_enabled(),
            patch(
                "stripe.Customer.list", side_effect=stripe.StripeError("network error")
            ),
        ):
            with pytest.raises(HTTPException) as exc:
                create_portal_url("user@example.com")
        assert exc.value.status_code == 502


# ---------------------------------------------------------------------------
# StripeWebhookHandler._verify_signature
# ---------------------------------------------------------------------------


class TestVerifySignature:
    def _handler(self):
        return StripeWebhookHandler(db=MagicMock())

    def test_returns_event_on_valid_signature(self):
        mock_event = {
            "type": "checkout.session.completed",
            "id": "evt_1",
            "data": {"object": {}},
        }
        with patch("stripe.Webhook.construct_event", return_value=mock_event):
            event = self._handler()._verify_signature(b"payload", "sig")
        assert event["type"] == "checkout.session.completed"

    def test_invalid_signature_raises_400(self):
        with patch(
            "stripe.Webhook.construct_event",
            side_effect=stripe.error.SignatureVerificationError("bad sig", "sig"),
        ):
            with pytest.raises(HTTPException) as exc:
                self._handler()._verify_signature(b"payload", "badsig")
        assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# StripeWebhookHandler._resolve_plan
# ---------------------------------------------------------------------------


class TestResolvePlan:
    def _handler(self):
        return StripeWebhookHandler(db=MagicMock())

    def test_resolves_monthly(self):
        assert self._handler()._resolve_plan("monthly") == SubscriptionPlan.monthly

    def test_resolves_yearly(self):
        assert self._handler()._resolve_plan("yearly") == SubscriptionPlan.yearly

    def test_unknown_plan_returns_none(self):
        assert self._handler()._resolve_plan("biweekly") is None

    def test_none_returns_none(self):
        assert self._handler()._resolve_plan(None) is None


# ---------------------------------------------------------------------------
# StripeWebhookHandler._on_checkout_completed
# ---------------------------------------------------------------------------


class TestOnCheckoutCompleted:
    def _handler(self, db=None):
        return StripeWebhookHandler(db=db or MagicMock())

    def test_grants_premium_and_tags_customer(self):
        data = {
            "client_reference_id": "sub-abc",
            "customer": "cus_123",
            "metadata": {"plan": "monthly"},
        }
        with (
            patch("app.api.subscription.webhook.set_premium") as mock_set,
            patch.object(StripeWebhookHandler, "_tag_customer_with_sub") as mock_tag,
        ):
            self._handler()._on_checkout_completed(
                "evt_1", "checkout.session.completed", data
            )

        mock_set.assert_called_once()
        call_args = mock_set.call_args
        assert call_args.args[0] == "sub-abc"
        assert call_args.args[1] is True
        assert call_args.kwargs["plan"] == SubscriptionPlan.monthly
        mock_tag.assert_called_once_with("cus_123", "sub-abc", "evt_1")

    def test_no_sub_skips_premium_grant(self):
        data = {"customer": "cus_123", "metadata": {}}
        with patch("app.api.subscription.webhook.set_premium") as mock_set:
            self._handler()._on_checkout_completed(
                "evt_1", "checkout.session.completed", data
            )
        mock_set.assert_not_called()


# ---------------------------------------------------------------------------
# StripeWebhookHandler._on_subscription_ended
# ---------------------------------------------------------------------------


class TestOnSubscriptionEnded:
    def _handler(self, db=None):
        return StripeWebhookHandler(db=db or MagicMock())

    def test_revokes_premium(self):
        mock_customer = MagicMock()
        mock_customer.get.return_value = {"sub": "sub-abc"}

        data = {"customer": "cus_123"}
        with (
            patch.object(
                StripeWebhookHandler, "_retrieve_customer", return_value=mock_customer
            ),
            patch("app.api.subscription.webhook.set_premium") as mock_set,
        ):
            self._handler()._on_subscription_ended(
                "evt_1", "customer.subscription.deleted", data
            )

        mock_set.assert_called_once()
        call_args = mock_set.call_args
        assert call_args.args[1] is False
        assert call_args.kwargs["plan"] is None

    def test_no_sub_on_customer_skips_revoke(self):
        mock_customer = MagicMock()
        mock_customer.get.return_value = {}

        data = {"customer": "cus_123"}
        with (
            patch.object(
                StripeWebhookHandler, "_retrieve_customer", return_value=mock_customer
            ),
            patch("app.api.subscription.webhook.set_premium") as mock_set,
        ):
            self._handler()._on_subscription_ended(
                "evt_1", "customer.subscription.deleted", data
            )

        mock_set.assert_not_called()

    def test_stripe_error_on_retrieve_raises_502(self):
        data = {"customer": "cus_123"}
        with patch(
            "stripe.Customer.retrieve",
            side_effect=stripe.StripeError("network"),
        ):
            with pytest.raises(HTTPException) as exc:
                self._handler()._on_subscription_ended(
                    "evt_1", "customer.subscription.deleted", data
                )
        assert exc.value.status_code == 502


# ---------------------------------------------------------------------------
# StripeWebhookHandler.handle — dispatch
# ---------------------------------------------------------------------------


class TestWebhookDispatch:
    def _make_event(self, event_type, data=None):
        return {
            "type": event_type,
            "id": "evt_dispatch_test",
            "data": {"object": data or {}},
        }

    def test_dispatches_checkout_completed(self):
        event = self._make_event("checkout.session.completed")
        handler = StripeWebhookHandler(db=MagicMock())
        with (
            patch.object(handler, "_verify_signature", return_value=event),
            patch.object(handler, "_on_checkout_completed") as mock_h,
        ):
            handler.handle(b"payload", "sig")
        mock_h.assert_called_once()

    def test_dispatches_subscription_deleted(self):
        event = self._make_event("customer.subscription.deleted")
        handler = StripeWebhookHandler(db=MagicMock())
        with (
            patch.object(handler, "_verify_signature", return_value=event),
            patch.object(handler, "_on_subscription_ended") as mock_h,
        ):
            handler.handle(b"payload", "sig")
        mock_h.assert_called_once()

    def test_unknown_event_type_is_silently_ignored(self):
        event = self._make_event("some.unknown.event")
        handler = StripeWebhookHandler(db=MagicMock())
        with (
            patch.object(handler, "_verify_signature", return_value=event),
            patch.object(handler, "_on_checkout_completed") as mock_h,
        ):
            handler.handle(b"payload", "sig")
        mock_h.assert_not_called()
