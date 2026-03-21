"""Integration tests for the depot HTTP API.

Tests run against a real PostgreSQL database using the SAVEPOINT-based
transaction isolation from the shared ``db_session`` fixture (all changes
are rolled back after each test).
"""

import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

CURRENT_YEAR = datetime.now(UTC).year


# ---------------------------------------------------------------------------
# list depots
# ---------------------------------------------------------------------------


class TestListDepots:
    def test_returns_empty_for_new_user(self, free_db_client: TestClient):
        resp = free_db_client.get("/api/depots")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_created_depot(self, free_db_client: TestClient):
        free_db_client.post("/api/depots", json={"name": "Default"})
        resp = free_db_client.get("/api/depots")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Default"
        assert "id" in data[0]
        assert "created_at" in data[0]


# ---------------------------------------------------------------------------
# create depot
# ---------------------------------------------------------------------------


class TestCreateDepot:
    def test_create_succeeds_for_free_user_with_no_existing_depot(
        self, free_db_client: TestClient
    ):
        resp = free_db_client.post("/api/depots", json={"name": "Default"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Default"

    def test_free_user_cannot_create_second_depot(self, free_db_client: TestClient):
        free_db_client.post("/api/depots", json={"name": "Default"})
        resp = free_db_client.post("/api/depots", json={"name": "Broker B"})
        assert resp.status_code == 403

    def test_premium_user_can_create_multiple_depots(
        self, premium_db_client: TestClient
    ):
        r1 = premium_db_client.post("/api/depots", json={"name": "Depot A"})
        r2 = premium_db_client.post("/api/depots", json={"name": "Depot B"})
        r3 = premium_db_client.post("/api/depots", json={"name": "Depot C"})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r3.status_code == 201

    def test_duplicate_name_rejected(self, premium_db_client: TestClient):
        premium_db_client.post("/api/depots", json={"name": "Default"})
        resp = premium_db_client.post("/api/depots", json={"name": "Default"})
        assert resp.status_code == 409

    def test_empty_name_rejected(self, free_db_client: TestClient):
        resp = free_db_client.post("/api/depots", json={"name": ""})
        assert resp.status_code == 422

    def test_created_depot_has_uuid(self, free_db_client: TestClient):
        resp = free_db_client.post("/api/depots", json={"name": "MyDepot"})
        assert resp.status_code == 201
        data = resp.json()
        # Validate that id is a valid UUID
        uuid.UUID(data["id"])


# ---------------------------------------------------------------------------
# rename depot
# ---------------------------------------------------------------------------


class TestRenameDepot:
    def test_rename_succeeds(self, premium_db_client: TestClient):
        created = premium_db_client.post("/api/depots", json={"name": "Old"}).json()
        depot_id = created["id"]

        resp = premium_db_client.patch(f"/api/depots/{depot_id}", json={"name": "New"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New"

    def test_rename_to_same_name_is_idempotent(self, free_db_client: TestClient):
        created = free_db_client.post("/api/depots", json={"name": "Default"}).json()
        resp = free_db_client.patch(
            f"/api/depots/{created['id']}", json={"name": "Default"}
        )
        assert resp.status_code == 200

    def test_rename_to_existing_name_rejected(self, premium_db_client: TestClient):
        premium_db_client.post("/api/depots", json={"name": "Depot A"})
        b = premium_db_client.post("/api/depots", json={"name": "Depot B"}).json()
        resp = premium_db_client.patch(
            f"/api/depots/{b['id']}", json={"name": "Depot A"}
        )
        assert resp.status_code == 409

    def test_rename_unknown_depot_returns_404(self, free_db_client: TestClient):
        resp = free_db_client.patch(f"/api/depots/{uuid.uuid4()}", json={"name": "X"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# delete depot
# ---------------------------------------------------------------------------


class TestDeleteDepot:
    def test_delete_succeeds_when_multiple_depots(self, premium_db_client: TestClient):
        premium_db_client.post("/api/depots", json={"name": "Depot A"})
        b = premium_db_client.post("/api/depots", json={"name": "Depot B"}).json()

        resp = premium_db_client.delete(f"/api/depots/{b['id']}")
        assert resp.status_code == 204

        remaining = premium_db_client.get("/api/depots").json()
        names = [d["name"] for d in remaining]
        assert "Depot B" not in names
        assert "Depot A" in names

    def test_cannot_delete_only_depot(self, free_db_client: TestClient):
        created = free_db_client.post("/api/depots", json={"name": "Only"}).json()
        resp = free_db_client.delete(f"/api/depots/{created['id']}")
        assert resp.status_code == 400

    def test_delete_unknown_depot_returns_404(self, free_db_client: TestClient):
        resp = free_db_client.delete(f"/api/depots/{uuid.uuid4()}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# finance sub-routes scoped to depot
# ---------------------------------------------------------------------------


class TestDepotFinanceRoutes:
    SAMPLE_DATA = {
        "dividends": {"AAPL": {"name": "Apple Inc.", "months": {"01": 10.0}}},
        "yields": {"Savings": {"months": {"01": 5.0}}},
    }

    def test_years_empty_for_new_depot(self, free_db_client: TestClient):
        depot = free_db_client.post("/api/depots", json={"name": "Default"}).json()
        resp = free_db_client.get(f"/api/depots/{depot['id']}/years")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_put_and_get_data_roundtrip(self, free_db_client: TestClient):
        depot = free_db_client.post("/api/depots", json={"name": "Default"}).json()
        depot_id = depot["id"]

        put_resp = free_db_client.put(
            f"/api/depots/{depot_id}/data/{CURRENT_YEAR}", json=self.SAMPLE_DATA
        )
        assert put_resp.status_code == 200

        get_resp = free_db_client.get(f"/api/depots/{depot_id}/data/{CURRENT_YEAR}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert "AAPL" in data["dividends"]
        assert data["dividends"]["AAPL"]["months"]["01"] == 10.0

    def test_years_returns_written_year(self, free_db_client: TestClient):
        depot = free_db_client.post("/api/depots", json={"name": "Default"}).json()
        free_db_client.put(
            f"/api/depots/{depot['id']}/data/{CURRENT_YEAR}", json=self.SAMPLE_DATA
        )
        resp = free_db_client.get(f"/api/depots/{depot['id']}/years")
        assert CURRENT_YEAR in resp.json()

    def test_depot_data_isolated_from_another_depot(
        self, premium_db_client: TestClient
    ):
        a = premium_db_client.post("/api/depots", json={"name": "Depot A"}).json()
        b = premium_db_client.post("/api/depots", json={"name": "Depot B"}).json()

        premium_db_client.put(
            f"/api/depots/{a['id']}/data/{CURRENT_YEAR}", json=self.SAMPLE_DATA
        )

        resp = premium_db_client.get(f"/api/depots/{b['id']}/data/{CURRENT_YEAR}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["dividends"] == {}
        assert data["yields"] == {}

    def test_delete_entry_removes_only_target(self, free_db_client: TestClient):
        depot = free_db_client.post("/api/depots", json={"name": "Default"}).json()
        depot_id = depot["id"]
        free_db_client.put(
            f"/api/depots/{depot_id}/data/{CURRENT_YEAR}", json=self.SAMPLE_DATA
        )

        resp = free_db_client.delete(
            f"/api/depots/{depot_id}/data/{CURRENT_YEAR}/dividends/AAPL"
        )
        assert resp.status_code == 202

        data = free_db_client.get(f"/api/depots/{depot_id}/data/{CURRENT_YEAR}").json()
        assert "AAPL" not in data["dividends"]
        assert "Savings" in data["yields"]
