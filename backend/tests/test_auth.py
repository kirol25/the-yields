"""Tests for the get_auth_context dependency and the config.py .env loading."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.finance.dependencies import get_auth_context
from app.core.config import BACKEND_ROOT
from app.main import app

# ---------------------------------------------------------------------------
# Config / .env loading
# ---------------------------------------------------------------------------


def test_backend_root_points_to_backend_dir():
    """BACKEND_ROOT must resolve to the `backend/` directory, not `backend/app/`."""
    assert BACKEND_ROOT.name == "backend"


# ---------------------------------------------------------------------------
# get_auth_context — dev mode (ALLOW_INSECURE_DEV_AUTH=True)
# ---------------------------------------------------------------------------


def _build_dev_settings(allow_insecure: bool = True, cognito_user_pool_id: str = ""):
    s = MagicMock()
    s.ALLOW_INSECURE_DEV_AUTH = allow_insecure
    s.COGNITO_USER_POOL_ID = cognito_user_pool_id
    return s


def _call_auth(authorization=None, x_user_email=None, settings_obj=None):
    """Call get_auth_context with the given header values and patched settings."""
    with patch("app.api.finance.dependencies.settings", settings_obj):
        return get_auth_context(
            authorization=authorization,
            x_user_email=x_user_email,
        )


class TestDevMode:
    """get_auth_context behaviour when ALLOW_INSECURE_DEV_AUTH=True."""

    def _settings(self):
        return _build_dev_settings(allow_insecure=True, cognito_user_pool_id="")

    def test_valid_email_returns_ctx(self):
        ctx = _call_auth(x_user_email="user@example.com", settings_obj=self._settings())
        assert ctx == {"email": "user@example.com", "sub": "", "is_premium": False}

    def test_missing_email_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(x_user_email=None, settings_obj=self._settings())
        assert exc.value.status_code == 401

    def test_invalid_email_raises_400(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(x_user_email="not-an-email", settings_obj=self._settings())
        assert exc.value.status_code == 400

    def test_is_premium_always_false_in_dev(self):
        ctx = _call_auth(x_user_email="user@example.com", settings_obj=self._settings())
        assert ctx["is_premium"] is False

    def test_sub_is_empty_string_in_dev(self):
        ctx = _call_auth(x_user_email="user@example.com", settings_obj=self._settings())
        assert ctx["sub"] == ""


class TestProdMode:
    """get_auth_context behaviour when ALLOW_INSECURE_DEV_AUTH=False."""

    def _settings(self):
        return _build_dev_settings(
            allow_insecure=False, cognito_user_pool_id="eu-central-1"
        )

    def test_missing_bearer_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(authorization=None, settings_obj=self._settings())
        assert exc.value.status_code == 401

    def test_malformed_bearer_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            _call_auth(authorization="Token abc", settings_obj=self._settings())
        assert exc.value.status_code == 401

    def test_valid_bearer_calls_verify_and_fetches_premium(self):
        mock_verify = MagicMock(
            return_value={"email": "u@example.com", "sub": "test-sub-uuid"}
        )
        mock_get_premium = MagicMock(return_value=True)
        with (
            patch("app.api.finance.dependencies.verify_token", mock_verify),
            patch("app.api.finance.dependencies._get_is_premium", mock_get_premium),
        ):
            ctx = _call_auth(
                authorization="Bearer fake.jwt.token",
                settings_obj=self._settings(),
            )
        mock_verify.assert_called_once_with("fake.jwt.token")
        mock_get_premium.assert_called_once_with("test-sub-uuid")
        assert ctx["email"] == "u@example.com"
        assert ctx["sub"] == "test-sub-uuid"
        assert ctx["is_premium"] is True


class TestUnconfiguredMode:
    """No Cognito and ALLOW_INSECURE_DEV_AUTH=False → 503."""

    def test_raises_503(self):
        s = _build_dev_settings(allow_insecure=False, cognito_user_pool_id="")
        with pytest.raises(HTTPException) as exc:
            _call_auth(x_user_email="user@example.com", settings_obj=s)
        assert exc.value.status_code == 503


# ---------------------------------------------------------------------------
# End-to-end: dev mode client rejects bad headers
# ---------------------------------------------------------------------------


class TestDevModeEndToEnd:
    """Integration: ensure the /api/me endpoint enforces X-User-Email in dev."""

    def _dev_settings(self):
        return _build_dev_settings(allow_insecure=True, cognito_user_pool_id="")

    def test_missing_email_header_returns_401(self):
        app.dependency_overrides.clear()
        client = TestClient(app, raise_server_exceptions=False)
        with patch("app.api.finance.dependencies.settings", self._dev_settings()):
            resp = client.get("/api/me")
        assert resp.status_code == 401

    def test_valid_email_header_returns_200(self):
        app.dependency_overrides.clear()
        client = TestClient(app, raise_server_exceptions=False)
        with patch("app.api.finance.dependencies.settings", self._dev_settings()):
            resp = client.get("/api/me", headers={"X-User-Email": "user@example.com"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "user@example.com"
