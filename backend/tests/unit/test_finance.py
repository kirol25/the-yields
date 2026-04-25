"""Tests for finance endpoints: /api/years, /api/data/{year}, /api/settings."""

from datetime import UTC, datetime

CURRENT_YEAR = datetime.now(UTC).year
PAST_YEAR = CURRENT_YEAR - 1

SAMPLE_PAYLOAD = {
    "dividends": {
        "AAPL": {"name": "Apple Inc.", "months": {"01": 1.50, "02": 1.50}},
    },
    "yields": {
        "TradeRepublic": {"months": {"01": 25.00}},
    },
}


# ---------------------------------------------------------------------------
# GET /api/years
# ---------------------------------------------------------------------------


class TestGetYears:
    def test_returns_empty_list_when_no_data(self, free_client):
        resp = free_client.get("/api/years")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_years(self, free_client):
        for year in [CURRENT_YEAR, PAST_YEAR]:
            free_client.put(f"/api/data/{year}", json=SAMPLE_PAYLOAD)

        resp = free_client.get("/api/years")
        assert resp.status_code == 200
        assert sorted(resp.json()) == sorted([CURRENT_YEAR, PAST_YEAR])


# ---------------------------------------------------------------------------
# GET /api/data/{year}
# ---------------------------------------------------------------------------


class TestGetData:
    def test_returns_empty_scaffold_for_missing_year(self, free_client):
        resp = free_client.get(f"/api/data/{CURRENT_YEAR}")
        assert resp.status_code == 200
        assert resp.json() == {"dividends": {}, "yields": {}}

    def test_returns_saved_data(self, free_client):
        free_client.put(f"/api/data/{CURRENT_YEAR}", json=SAMPLE_PAYLOAD)
        resp = free_client.get(f"/api/data/{CURRENT_YEAR}")
        assert resp.status_code == 200
        data = resp.json()
        assert "AAPL" in data["dividends"]
        assert "TradeRepublic" in data["yields"]

    def test_can_access_past_year(self, free_client):
        free_client.put(f"/api/data/{PAST_YEAR}", json=SAMPLE_PAYLOAD)
        resp = free_client.get(f"/api/data/{PAST_YEAR}")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# PUT /api/data/{year}
# ---------------------------------------------------------------------------


class TestPutData:
    def test_saves_and_retrieves_data(self, free_client):
        resp = free_client.put(f"/api/data/{CURRENT_YEAR}", json=SAMPLE_PAYLOAD)
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

        resp = free_client.get(f"/api/data/{CURRENT_YEAR}")
        assert resp.json()["dividends"]["AAPL"]["name"] == "Apple Inc."

    def test_can_save_past_year(self, free_client):
        resp = free_client.put(f"/api/data/{PAST_YEAR}", json=SAMPLE_PAYLOAD)
        assert resp.status_code == 200

    def test_can_save_many_tickers(self, free_client):
        big_payload = {
            "dividends": {
                f"TICK{i}": {"name": f"Ticker {i}", "months": {"01": 1.0}}
                for i in range(10)
            },
            "yields": {},
        }
        resp = free_client.put(f"/api/data/{CURRENT_YEAR}", json=big_payload)
        assert resp.status_code == 200

    def test_rejects_invalid_year(self, free_client):
        resp = free_client.put("/api/data/1999", json=SAMPLE_PAYLOAD)
        assert resp.status_code == 422

    def test_rejects_extra_fields(self, free_client):
        payload = {**SAMPLE_PAYLOAD, "extra": "field"}
        resp = free_client.put(f"/api/data/{CURRENT_YEAR}", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /api/data/{year}/{section}/{key}
# ---------------------------------------------------------------------------


class TestDeleteEntry:
    def test_deletes_existing_entry(self, free_client):
        free_client.put(f"/api/data/{CURRENT_YEAR}", json=SAMPLE_PAYLOAD)
        resp = free_client.delete(f"/api/data/{CURRENT_YEAR}/dividends/AAPL")
        assert resp.status_code == 202

        data = free_client.get(f"/api/data/{CURRENT_YEAR}").json()
        assert "AAPL" not in data["dividends"]

    def test_returns_404_for_missing_entry(self, free_client):
        resp = free_client.delete(f"/api/data/{CURRENT_YEAR}/dividends/MISSING")
        assert resp.status_code == 404

    def test_can_delete_from_past_year(self, free_client):
        free_client.put(f"/api/data/{PAST_YEAR}", json=SAMPLE_PAYLOAD)
        resp = free_client.delete(f"/api/data/{PAST_YEAR}/dividends/AAPL")
        assert resp.status_code == 202


# ---------------------------------------------------------------------------
# GET + PUT /api/settings
# ---------------------------------------------------------------------------


class TestSettings:
    def test_returns_default_settings_when_no_goals(self, free_client):
        resp = free_client.get("/api/settings")
        assert resp.status_code == 200
        data = resp.json()
        assert "currency" in data

    def test_saves_and_retrieves_settings(self, free_client):
        payload = {
            "dividendGoal": {"2024": 1200.0},
            "yieldGoal": {"2024": 500.0},
            "steuerfreibetrag": {"2024": 801.0},
        }
        resp = free_client.put("/api/settings", json=payload)
        assert resp.status_code == 200

        resp = free_client.get("/api/settings")
        data = resp.json()
        assert data["dividendGoal"]["2024"] == 1200.0
        assert data["steuerfreibetrag"]["2024"] == 801.0
