from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    Depot,
    DividendEntry,
    DividendMonth,
    Ticker,
    User,
    YearGoal,
    YieldEntry,
    YieldMonth,
)


class DBYieldRepository:
    """Reads and writes all user data via the relational database.

    Scoped to a single user (identified by Cognito sub + email).
    All data lives under the user's "Default" depot unless the depot API
    is used directly in the future.
    """

    def __init__(self, sub: str, email: str, session: Session) -> None:
        self._sub = sub
        self._email = email
        self._db = session

    # ── private helpers ───────────────────────────────────────────────────────

    def _get_or_create_user(self) -> User:
        user = self._db.query(User).filter_by(sub=self._sub).first()
        if not user:
            user = User(sub=self._sub, email=self._email)
            self._db.add(user)
            self._db.flush()
        return user

    def _get_or_create_default_depot(self) -> Depot:
        user = self._get_or_create_user()
        depot = self._db.query(Depot).filter_by(user_id=user.id, name="Default").first()
        if not depot:
            depot = Depot(user_id=user.id, name="Default")
            self._db.add(depot)
            self._db.flush()
        return depot

    # ── public interface ──────────────────────────────────────────────────────

    def list_years(self) -> list[int]:
        """Return all years that have at least one dividend or yield entry."""
        depot = self._get_or_create_default_depot()
        div_years = {
            y
            for (y,) in self._db.query(DividendEntry.year)
            .filter_by(depot_id=depot.id)
            .distinct()
        }
        yld_years = {
            y
            for (y,) in self._db.query(YieldEntry.year)
            .filter_by(depot_id=depot.id)
            .distinct()
        }
        return sorted(div_years | yld_years)

    def read_year(self, year: int) -> dict[str, Any]:
        """Return the full dividend + yield payload for *year*.

        Returns an empty scaffold ``{"dividends": {}, "yields": {}}`` when no
        data exists yet, matching the legacy file-based behaviour.
        Display name resolves as: entry.name → ticker_ref.name → ticker symbol.
        """
        depot = self._get_or_create_default_depot()

        div_entries = (
            self._db.query(DividendEntry)
            .options(
                selectinload(DividendEntry.months),
                selectinload(DividendEntry.ticker_ref),
            )
            .filter_by(depot_id=depot.id, year=year)
            .all()
        )
        yld_entries = (
            self._db.query(YieldEntry)
            .options(selectinload(YieldEntry.months))
            .filter_by(depot_id=depot.id, year=year)
            .all()
        )

        return {
            "dividends": {
                e.ticker: {
                    "name": e.name or (e.ticker_ref.name if e.ticker_ref else e.ticker),
                    "months": {f"{m.month:02d}": float(m.amount) for m in e.months},
                }
                for e in div_entries
            },
            "yields": {
                e.account_key: {
                    "months": {f"{m.month:02d}": float(m.amount) for m in e.months},
                }
                for e in yld_entries
            },
        }

    def write_year(self, year: int, data: dict[str, Any]) -> None:
        """Atomically replace the full dividend + yield data for *year*.

        Existing entries for the year are deleted (months cascade via FK) and
        the incoming payload is re-inserted in full.
        """
        depot = self._get_or_create_default_depot()

        # Full replacement — remove existing rows first; months are removed by
        # PostgreSQL's ON DELETE CASCADE on the FK.
        self._db.query(DividendEntry).filter_by(depot_id=depot.id, year=year).delete(
            synchronize_session="fetch"
        )
        self._db.query(YieldEntry).filter_by(depot_id=depot.id, year=year).delete(
            synchronize_session="fetch"
        )
        self._db.flush()

        # Fetch known ticker symbols once to avoid N+1 queries
        known_symbols: set[str] = {
            row[0] for row in self._db.query(Ticker.symbol).all()
        }

        for ticker, entry_data in data.get("dividends", {}).items():
            entry = DividendEntry(
                depot_id=depot.id,
                year=year,
                ticker=ticker,
                name=entry_data.get("name"),
                ticker_symbol=ticker if ticker in known_symbols else None,
            )
            self._db.add(entry)
            self._db.flush()
            for month_str, amount in entry_data.get("months", {}).items():
                self._db.add(
                    DividendMonth(
                        entry_id=entry.id,
                        month=int(month_str),
                        amount=Decimal(str(amount)),
                    )
                )

        for account_key, entry_data in data.get("yields", {}).items():
            entry = YieldEntry(depot_id=depot.id, year=year, account_key=account_key)
            self._db.add(entry)
            self._db.flush()
            for month_str, amount in entry_data.get("months", {}).items():
                self._db.add(
                    YieldMonth(
                        entry_id=entry.id,
                        month=int(month_str),
                        amount=Decimal(str(amount)),
                    )
                )

        self._db.flush()

    def delete_entry(self, year: int, section: str, key: str) -> bool:
        """Remove one ticker (dividends) or account (yields) from *year*.

        Returns ``True`` if the entry existed and was removed, ``False`` if not found.
        """
        depot = self._get_or_create_default_depot()
        if section == "dividends":
            deleted = (
                self._db.query(DividendEntry)
                .filter_by(depot_id=depot.id, year=year, ticker=key)
                .delete(synchronize_session="fetch")
            )
        else:
            deleted = (
                self._db.query(YieldEntry)
                .filter_by(depot_id=depot.id, year=year, account_key=key)
                .delete(synchronize_session="fetch")
            )
        self._db.flush()
        return bool(deleted)

    def delete_all_data(self) -> None:
        """Permanently delete all depots (and all cascaded data) for this user."""
        user = self._get_or_create_user()
        self._db.query(Depot).filter_by(user_id=user.id).delete(
            synchronize_session="fetch"
        )
        self._db.flush()

    def read_settings(self) -> dict[str, Any]:
        """Return goals and steuerfreibetrag, keyed by year string.

        Also includes ``is_premium`` from the User row so callers have a
        single source of truth.
        """
        user = self._get_or_create_user()
        goals = self._db.query(YearGoal).filter_by(user_id=user.id).all()

        dividend_goal: dict[str, int] = {}
        yield_goal: dict[str, int] = {}
        steuerfreibetrag: dict[str, int] = {}

        for goal in goals:
            y = str(goal.year)
            if goal.dividend_goal is not None:
                dividend_goal[y] = int(goal.dividend_goal)
            if goal.yield_goal is not None:
                yield_goal[y] = int(goal.yield_goal)
            if goal.steuerfreibetrag is not None:
                steuerfreibetrag[y] = int(goal.steuerfreibetrag)

        result: dict[str, Any] = {"is_premium": user.is_premium}
        if dividend_goal:
            result["dividendGoal"] = dividend_goal
        if yield_goal:
            result["yieldGoal"] = yield_goal
        if steuerfreibetrag:
            result["steuerfreibetrag"] = steuerfreibetrag
        return result

    def write_settings(self, data: dict[str, Any]) -> None:
        """Upsert year goals from *data*.

        ``is_premium`` is intentionally ignored here — it is managed exclusively
        by the Stripe webhook via the User row.
        """
        user = self._get_or_create_user()

        years_touched: set[int] = set()
        for field in ("dividendGoal", "yieldGoal", "steuerfreibetrag"):
            for year_str in data.get(field, {}):
                years_touched.add(int(year_str))

        for year in years_touched:
            y = str(year)
            goal = (
                self._db.query(YearGoal).filter_by(user_id=user.id, year=year).first()
            )
            if not goal:
                goal = YearGoal(user_id=user.id, year=year)
                self._db.add(goal)

            if "dividendGoal" in data and y in data["dividendGoal"]:
                goal.dividend_goal = int(data["dividendGoal"][y])
            if "yieldGoal" in data and y in data["yieldGoal"]:
                goal.yield_goal = int(data["yieldGoal"][y])
            if "steuerfreibetrag" in data and y in data["steuerfreibetrag"]:
                goal.steuerfreibetrag = int(data["steuerfreibetrag"][y])

        self._db.flush()
