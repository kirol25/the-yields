"""Integration tests for DBYieldRepository against a real PostgreSQL database.

Each test runs inside a rolled-back transaction (via the ``db_repo`` fixture),
so no data persists between tests.
"""

from datetime import UTC, datetime

import pytest

from app.api.finance.db_repository import DBYieldRepository
from app.db.models import User

CURRENT_YEAR = datetime.now(UTC).year
PAST_YEAR = CURRENT_YEAR - 1

SAMPLE_DATA = {
    "dividends": {
        "AAPL": {"name": "Apple Inc.", "months": {"01": 1.50, "06": 1.75}},
        "MSFT": {"name": "Microsoft", "months": {"03": 2.00}},
    },
    "yields": {
        "TradeRepublic": {"months": {"01": 25.00, "02": 26.50}},
    },
}


# ---------------------------------------------------------------------------
# Auto-provisioning: user + default depot are created on first access
# ---------------------------------------------------------------------------


class TestAutoProvisioning:
    def test_user_and_depot_created_on_list_years(self, db_repo: DBYieldRepository):
        db_repo.list_years()
        user = db_repo._db.query(User).filter_by(sub=db_repo._sub).first()
        assert user is not None
        assert user.email == db_repo._email
        assert len(user.depots) == 1
        assert user.depots[0].name == "Default"

    def test_user_created_only_once(self, db_repo: DBYieldRepository):
        db_repo.list_years()
        db_repo.list_years()
        count = db_repo._db.query(User).filter_by(sub=db_repo._sub).count()
        assert count == 1


# ---------------------------------------------------------------------------
# list_years
# ---------------------------------------------------------------------------


class TestListYears:
    def test_empty_when_no_data(self, db_repo: DBYieldRepository):
        assert db_repo.list_years() == []

    def test_returns_years_from_dividends(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        assert db_repo.list_years() == [CURRENT_YEAR]

    def test_returns_years_from_yields_only(self, db_repo: DBYieldRepository):
        db_repo.write_year(
            CURRENT_YEAR, {"dividends": {}, "yields": SAMPLE_DATA["yields"]}
        )
        assert db_repo.list_years() == [CURRENT_YEAR]

    def test_returns_multiple_years_sorted(self, db_repo: DBYieldRepository):
        db_repo.write_year(PAST_YEAR, SAMPLE_DATA)
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        assert db_repo.list_years() == [PAST_YEAR, CURRENT_YEAR]

    def test_no_duplicate_years(self, db_repo: DBYieldRepository):
        # Both dividends and yields in the same year — year appears once
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        assert db_repo.list_years().count(CURRENT_YEAR) == 1


# ---------------------------------------------------------------------------
# read_year
# ---------------------------------------------------------------------------


class TestReadYear:
    def test_empty_scaffold_when_no_data(self, db_repo: DBYieldRepository):
        result = db_repo.read_year(CURRENT_YEAR)
        assert result == {"dividends": {}, "yields": {}}

    def test_returns_saved_dividends(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        result = db_repo.read_year(CURRENT_YEAR)

        assert "AAPL" in result["dividends"]
        assert result["dividends"]["AAPL"]["name"] == "Apple Inc."
        assert result["dividends"]["AAPL"]["months"]["01"] == pytest.approx(1.50)
        assert result["dividends"]["AAPL"]["months"]["06"] == pytest.approx(1.75)

    def test_returns_saved_yields(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        result = db_repo.read_year(CURRENT_YEAR)

        assert "TradeRepublic" in result["yields"]
        assert result["yields"]["TradeRepublic"]["months"]["01"] == pytest.approx(25.00)

    def test_month_keys_are_zero_padded(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        months = db_repo.read_year(CURRENT_YEAR)["dividends"]["AAPL"]["months"]
        assert all(len(k) == 2 for k in months.keys())

    def test_years_are_isolated(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        result = db_repo.read_year(PAST_YEAR)
        assert result == {"dividends": {}, "yields": {}}


# ---------------------------------------------------------------------------
# write_year
# ---------------------------------------------------------------------------


class TestWriteYear:
    def test_full_replacement_removes_deleted_tickers(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)

        # Remove MSFT, keep AAPL
        updated = {
            "dividends": {"AAPL": SAMPLE_DATA["dividends"]["AAPL"]},
            "yields": SAMPLE_DATA["yields"],
        }
        db_repo.write_year(CURRENT_YEAR, updated)
        result = db_repo.read_year(CURRENT_YEAR)

        assert "AAPL" in result["dividends"]
        assert "MSFT" not in result["dividends"]

    def test_overwrites_existing_months(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)

        updated = {
            "dividends": {
                "AAPL": {"name": "Apple Inc.", "months": {"01": 9.99}},
            },
            "yields": {},
        }
        db_repo.write_year(CURRENT_YEAR, updated)
        result = db_repo.read_year(CURRENT_YEAR)

        assert result["dividends"]["AAPL"]["months"]["01"] == pytest.approx(9.99)
        assert "06" not in result["dividends"]["AAPL"]["months"]

    def test_write_empty_clears_year(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        db_repo.write_year(CURRENT_YEAR, {"dividends": {}, "yields": {}})
        result = db_repo.read_year(CURRENT_YEAR)
        assert result == {"dividends": {}, "yields": {}}

    def test_idempotent_on_repeat_write(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        result = db_repo.read_year(CURRENT_YEAR)
        assert list(result["dividends"].keys()) == ["AAPL", "MSFT"]


# ---------------------------------------------------------------------------
# delete_entry
# ---------------------------------------------------------------------------


class TestDeleteEntry:
    def test_delete_dividend_entry(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        removed = db_repo.delete_entry(CURRENT_YEAR, "dividends", "AAPL")
        assert removed is True

        result = db_repo.read_year(CURRENT_YEAR)
        assert "AAPL" not in result["dividends"]
        assert "MSFT" in result["dividends"]

    def test_delete_yield_entry(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        removed = db_repo.delete_entry(CURRENT_YEAR, "yields", "TradeRepublic")
        assert removed is True

        result = db_repo.read_year(CURRENT_YEAR)
        assert "TradeRepublic" not in result["yields"]

    def test_returns_false_for_missing_entry(self, db_repo: DBYieldRepository):
        removed = db_repo.delete_entry(CURRENT_YEAR, "dividends", "NONEXISTENT")
        assert removed is False

    def test_returns_false_for_wrong_year(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        removed = db_repo.delete_entry(PAST_YEAR, "dividends", "AAPL")
        assert removed is False


# ---------------------------------------------------------------------------
# delete_all_data
# ---------------------------------------------------------------------------


class TestDeleteAllData:
    def test_removes_all_years(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        db_repo.write_year(PAST_YEAR, SAMPLE_DATA)
        db_repo.delete_all_data()
        assert db_repo.list_years() == []

    def test_removes_depot(self, db_repo: DBYieldRepository):
        db_repo.write_year(CURRENT_YEAR, SAMPLE_DATA)
        db_repo.delete_all_data()

        user = db_repo._db.query(User).filter_by(sub=db_repo._sub).first()
        assert user is not None  # user row is kept
        assert user.depots == []  # but all depots (and their data) are gone

    def test_noop_when_no_data(self, db_repo: DBYieldRepository):
        db_repo.delete_all_data()  # must not raise
        assert db_repo.list_years() == []


# ---------------------------------------------------------------------------
# read_settings / write_settings
# ---------------------------------------------------------------------------


class TestSettings:
    def test_read_returns_is_premium_false_by_default(self, db_repo: DBYieldRepository):
        result = db_repo.read_settings()
        assert result["is_premium"] is False

    def test_read_empty_goals(self, db_repo: DBYieldRepository):
        result = db_repo.read_settings()
        assert "dividendGoal" not in result
        assert "yieldGoal" not in result
        assert "steuerfreibetrag" not in result

    def test_write_and_read_goals(self, db_repo: DBYieldRepository):
        payload = {
            "dividendGoal": {"2024": 1200.0, "2025": 1500.0},
            "yieldGoal": {"2024": 500.0},
            "steuerfreibetrag": {"2024": 801.0},
        }
        db_repo.write_settings(payload)
        result = db_repo.read_settings()

        assert result["dividendGoal"] == {
            "2024": pytest.approx(1200.0),
            "2025": pytest.approx(1500.0),
        }
        assert result["yieldGoal"]["2024"] == pytest.approx(500.0)
        assert result["steuerfreibetrag"]["2024"] == pytest.approx(801.0)

    def test_write_settings_upserts(self, db_repo: DBYieldRepository):
        db_repo.write_settings({"dividendGoal": {"2024": 1000.0}})
        db_repo.write_settings({"dividendGoal": {"2024": 2000.0}})
        result = db_repo.read_settings()
        assert result["dividendGoal"]["2024"] == pytest.approx(2000.0)

    def test_is_premium_ignored_by_write_settings(self, db_repo: DBYieldRepository):
        """is_premium must not be writable via write_settings -
        only the webhook sets it."""
        db_repo.write_settings({"is_premium": True})
        result = db_repo.read_settings()
        assert result["is_premium"] is False

    def test_partial_goals_only_updates_present_fields(
        self, db_repo: DBYieldRepository
    ):
        db_repo.write_settings(
            {"dividendGoal": {"2024": 500.0}, "yieldGoal": {"2024": 200.0}}
        )
        db_repo.write_settings({"dividendGoal": {"2024": 999.0}})
        result = db_repo.read_settings()
        assert result["dividendGoal"]["2024"] == pytest.approx(999.0)
        assert result["yieldGoal"]["2024"] == pytest.approx(200.0)  # unchanged
