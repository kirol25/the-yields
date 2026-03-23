"""Tests for get_auth_context and config loading."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException  # noqa: F401

from app.api.finance.dependencies import get_auth_context
from app.core.config import BACKEND_ROOT

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def test_backend_root_points_to_backend_dir():
    """BACKEND_ROOT must resolve to the `backend/` directory."""
    assert BACKEND_ROOT.name == "backend"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _settings(cognito_user_pool_id: str = "eu-central-1_TestPool"):
    s = MagicMock()
    s.COGNITO_USER_POOL_ID = cognito_user_pool_id
    return s


def _call_auth(authorization=None, settings_obj=None):
    with patch("app.api.finance.dependencies.settings", settings_obj):
        return get_auth_context(authorization=authorization)


# ---------------------------------------------------------------------------
# Cognito not configured → 503
# ---------------------------------------------------------------------------


class TestUnconfigured:
    def test_raises_503_when_cognito_not_set(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(settings_obj=_settings(cognito_user_pool_id=""))
        assert exc.value.status_code == 503


# ---------------------------------------------------------------------------
# Cognito configured - token checks
# ---------------------------------------------------------------------------


class TestAuth:
    def test_missing_authorization_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(authorization=None, settings_obj=_settings())
        assert exc.value.status_code == 401

    def test_non_bearer_scheme_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(authorization="Token abc123", settings_obj=_settings())
        assert exc.value.status_code == 401

    def test_valid_token_returns_full_context(self):
        mock_verify = MagicMock(
            return_value={"email": "u@example.com", "sub": "sub-uuid"}
        )
        mock_subscription = MagicMock(return_value=(False, None))
        with (
            patch("app.api.finance.dependencies.verify_token", mock_verify),
            patch(
                "app.api.finance.dependencies._get_user_subscription", mock_subscription
            ),
        ):
            ctx = _call_auth(
                authorization="Bearer valid.jwt.token",
                settings_obj=_settings(),
            )
        mock_verify.assert_called_once_with("valid.jwt.token")
        mock_subscription.assert_called_once_with("sub-uuid", None)
        assert ctx == {
            "email": "u@example.com",
            "sub": "sub-uuid",
            "is_premium": False,
            "subscription_plan": None,
        }

    def test_premium_user_gets_is_premium_true(self):
        mock_verify = MagicMock(
            return_value={"email": "u@example.com", "sub": "sub-uuid"}
        )
        mock_subscription = MagicMock(return_value=(True, "monthly"))
        with (
            patch("app.api.finance.dependencies.verify_token", mock_verify),
            patch(
                "app.api.finance.dependencies._get_user_subscription", mock_subscription
            ),
        ):
            ctx = _call_auth(
                authorization="Bearer valid.jwt.token",
                settings_obj=_settings(),
            )
        assert ctx["is_premium"] is True

    def test_verify_token_exception_propagates(self):
        mock_verify = MagicMock(
            side_effect=HTTPException(status_code=401, detail="Token expired")
        )
        with patch("app.api.finance.dependencies.verify_token", mock_verify):
            with pytest.raises(HTTPException) as exc:
                _call_auth(
                    authorization="Bearer expired.token",
                    settings_obj=_settings(),
                )
        assert exc.value.status_code == 401
