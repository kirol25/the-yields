"""Tests for the /api/me endpoint."""


class TestGetMe:
    def test_user_response_shape(self, free_client):
        resp = free_client.get("/api/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"
