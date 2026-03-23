"""Integration tests for the GET /api/init bootstrap endpoint."""

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

CURRENT_YEAR = datetime.now(UTC).year


class TestGetInit:
    def test_returns_200(self, free_db_client: TestClient):
        resp = free_db_client.get("/api/init")
        assert resp.status_code == 200

    def test_response_contains_all_required_fields(self, free_db_client: TestClient):
        data = free_db_client.get("/api/init").json()
        assert "me" in data
        assert "settings" in data
        assert "depots" in data
        assert "years" in data
        assert "year_data" in data
        assert "current_year" in data
        assert "depot_id" in data

    def test_creates_default_depot_for_new_user(self, free_db_client: TestClient):
        data = free_db_client.get("/api/init").json()
        assert len(data["depots"]) == 1
        assert data["depots"][0]["name"] == "Default"

    def test_depot_id_matches_returned_depot(self, free_db_client: TestClient):
        data = free_db_client.get("/api/init").json()
        assert data["depot_id"] == data["depots"][0]["id"]

    def test_me_contains_expected_fields(self, free_db_client: TestClient):
        me = free_db_client.get("/api/init").json()["me"]
        assert "is_premium" in me
        assert "free_tier_limit" in me
        assert "email" in me

    def test_free_user_is_not_premium(self, free_db_client: TestClient):
        me = free_db_client.get("/api/init").json()["me"]
        assert me["is_premium"] is False

    def test_premium_user_is_premium(self, premium_db_client: TestClient):
        me = premium_db_client.get("/api/init").json()["me"]
        assert me["is_premium"] is True

    def test_year_data_is_empty_scaffold_for_new_depot(
        self, free_db_client: TestClient
    ):
        data = free_db_client.get("/api/init").json()
        assert data["year_data"] == {"dividends": {}, "yields": {}}

    def test_current_year_defaults_to_this_year(self, free_db_client: TestClient):
        data = free_db_client.get("/api/init").json()
        assert data["current_year"] == CURRENT_YEAR

    def test_year_param_is_respected(self, free_db_client: TestClient):
        data = free_db_client.get("/api/init", params={"year": 2022}).json()
        # No data for 2022 — server should still return a valid response
        assert data["current_year"] == 2022

    def test_stale_depot_id_falls_back_gracefully(self, free_db_client: TestClient):
        stale = str(uuid.uuid4())
        resp = free_db_client.get("/api/init", params={"depot_id": stale})
        assert resp.status_code == 200
        data = resp.json()
        # Falls back to default depot, not the stale id
        assert data["depot_id"] != stale

    def test_valid_depot_id_is_used(self, free_db_client: TestClient):
        # First call provisions the default depot and returns its id
        first = free_db_client.get("/api/init").json()
        depot_id = first["depot_id"]

        # Second call with that id should return the same depot
        second = free_db_client.get("/api/init", params={"depot_id": depot_id}).json()
        assert second["depot_id"] == depot_id

    def test_idempotent_repeated_calls(self, free_db_client: TestClient):
        # Calling init twice should not create duplicate depots
        free_db_client.get("/api/init")
        data = free_db_client.get("/api/init").json()
        assert len(data["depots"]) == 1
