"""Tests for the /api/me endpoint."""

from app.core import settings


class TestGetMe:
    def test_free_user_response_shape(self, free_client):
        resp = free_client.get("/api/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
        assert data["is_premium"] is False
        assert data["free_tier_limit"] == settings.FREE_TIER_LIMIT

    def test_premium_user_is_flagged(self, premium_client):
        resp = premium_client.get("/api/me")
        assert resp.status_code == 200
        assert resp.json()["is_premium"] is True

    def test_free_tier_limit_matches_config(self, free_client):
        resp = free_client.get("/api/me")
        assert resp.json()["free_tier_limit"] == settings.FREE_TIER_LIMIT
