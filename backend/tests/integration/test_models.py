"""Tests for all SQLAlchemy ORM models.

Each test class maps to one model. Every test runs inside a transaction that
is rolled back on teardown, so tests are fully isolated and leave no data.

Coverage:
- Field defaults and basic CRUD
- Unique constraints (via IntegrityError)
- Foreign-key cascade deletes
- Relationship back-populates
- Numeric precision for financial amounts
- Multi-depot support (same ticker, different depots)
"""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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

# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class TestUser:
    def test_create_with_defaults(self, db_session: Session):
        user = User(sub="sub-001", email="u001@example.com")
        db_session.add(user)
        db_session.flush()

        fetched = db_session.get(User, user.id)
        assert fetched is not None
        assert fetched.email == "u001@example.com"
        assert fetched.sub == "sub-001"
        assert fetched.created_at is not None
        assert fetched.updated_at is not None

    def test_sub_unique_constraint(self, db_session: Session):
        db_session.add(User(sub="dup-sub", email="a@example.com"))
        db_session.flush()

        db_session.add(User(sub="dup-sub", email="b@example.com"))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_email_unique_constraint(self, db_session: Session):
        db_session.add(User(sub="sub-a", email="dup@example.com"))
        db_session.flush()

        db_session.add(User(sub="sub-b", email="dup@example.com"))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_relationships_start_empty(self, db_session: Session, user: User):
        db_session.refresh(user)
        assert user.depots == []
        assert user.year_goals == []


# ---------------------------------------------------------------------------
# Depot
# ---------------------------------------------------------------------------


class TestDepot:
    def test_create(self, db_session: Session, user: User):
        depot = Depot(user_id=user.id, name="TradeRepublic")
        db_session.add(depot)
        db_session.flush()

        fetched = db_session.get(Depot, depot.id)
        assert fetched.name == "TradeRepublic"
        assert fetched.user_id == user.id
        assert fetched.created_at is not None

    def test_user_name_unique_constraint(self, db_session: Session, user: User):
        db_session.add(Depot(user_id=user.id, name="Duplicate"))
        db_session.flush()

        db_session.add(Depot(user_id=user.id, name="Duplicate"))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_same_name_allowed_for_different_users(self, db_session: Session):
        u1 = User(sub="sub-x1", email="x1@example.com")
        u2 = User(sub="sub-x2", email="x2@example.com")
        db_session.add_all([u1, u2])
        db_session.flush()

        db_session.add(Depot(user_id=u1.id, name="TradeRepublic"))
        db_session.add(Depot(user_id=u2.id, name="TradeRepublic"))
        db_session.flush()  # must not raise

    def test_cascade_delete_from_user(self, db_session: Session):
        user = User(sub="cascade-depot", email="cascade-depot@example.com")
        db_session.add(user)
        db_session.flush()

        depot = Depot(user_id=user.id, name="Default")
        db_session.add(depot)
        db_session.flush()
        depot_id = depot.id

        db_session.delete(user)
        db_session.flush()

        assert db_session.get(Depot, depot_id) is None

    def test_back_populates_user(self, db_session: Session, user: User):
        d1 = Depot(user_id=user.id, name="Depot A")
        d2 = Depot(user_id=user.id, name="Depot B")
        db_session.add_all([d1, d2])
        db_session.flush()
        db_session.refresh(user)

        assert {d.name for d in user.depots} == {"Depot A", "Depot B"}


# ---------------------------------------------------------------------------
# DividendEntry
# ---------------------------------------------------------------------------


class TestDividendEntry:
    def test_create(self, db_session: Session, depot: Depot):
        entry = DividendEntry(
            depot_id=depot.id, year=2024, ticker="AAPL", name="Apple Inc."
        )
        db_session.add(entry)
        db_session.flush()

        fetched = db_session.get(DividendEntry, entry.id)
        assert fetched.ticker == "AAPL"
        assert fetched.name == "Apple Inc."
        assert fetched.year == 2024

    def test_depot_year_ticker_unique(self, db_session: Session, depot: Depot):
        db_session.add(
            DividendEntry(depot_id=depot.id, year=2024, ticker="AAPL", name="Apple")
        )
        db_session.flush()

        db_session.add(
            DividendEntry(depot_id=depot.id, year=2024, ticker="AAPL", name="Apple")
        )
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_same_ticker_allowed_in_different_years(
        self, db_session: Session, depot: Depot
    ):
        db_session.add(
            DividendEntry(depot_id=depot.id, year=2023, ticker="AAPL", name="Apple")
        )
        db_session.add(
            DividendEntry(depot_id=depot.id, year=2024, ticker="AAPL", name="Apple")
        )
        db_session.flush()  # must not raise

    def test_same_ticker_allowed_in_different_depots(
        self, db_session: Session, user: User
    ):
        """Core multi-depot requirement: AAPL at TradeRepublic and IB independently."""
        tr = Depot(user_id=user.id, name="TradeRepublic")
        ib = Depot(user_id=user.id, name="Interactive Brokers")
        db_session.add_all([tr, ib])
        db_session.flush()

        db_session.add(
            DividendEntry(depot_id=tr.id, year=2024, ticker="AAPL", name="Apple")
        )
        db_session.add(
            DividendEntry(depot_id=ib.id, year=2024, ticker="AAPL", name="Apple")
        )
        db_session.flush()  # must not raise

    def test_cascade_delete_from_depot(self, db_session: Session, depot: Depot):
        entry = DividendEntry(
            depot_id=depot.id, year=2024, ticker="DEL", name="Delete Me"
        )
        db_session.add(entry)
        db_session.flush()
        entry_id = entry.id

        db_session.delete(depot)
        db_session.flush()

        assert db_session.get(DividendEntry, entry_id) is None

    def test_back_populates_depot(self, db_session: Session, depot: Depot):
        db_session.add(
            DividendEntry(depot_id=depot.id, year=2024, ticker="MSFT", name="Microsoft")
        )
        db_session.flush()
        db_session.refresh(depot)

        assert len(depot.dividend_entries) == 1
        assert depot.dividend_entries[0].ticker == "MSFT"


# ---------------------------------------------------------------------------
# DividendMonth
# ---------------------------------------------------------------------------


class TestDividendMonth:
    def test_create_monthly_amounts(
        self, db_session: Session, dividend_entry: DividendEntry
    ):
        months_data = {1: "100.00", 6: "110.50", 12: "125.75"}
        for month, amount in months_data.items():
            db_session.add(
                DividendMonth(
                    entry_id=dividend_entry.id, month=month, amount=Decimal(amount)
                )
            )
        db_session.flush()
        db_session.refresh(dividend_entry)

        assert len(dividend_entry.months) == 3
        by_month = {m.month: m.amount for m in dividend_entry.months}
        assert by_month[1] == Decimal("100.00")
        assert by_month[6] == Decimal("110.50")
        assert by_month[12] == Decimal("125.75")

    def test_entry_month_unique(
        self, db_session: Session, dividend_entry: DividendEntry
    ):
        db_session.add(
            DividendMonth(entry_id=dividend_entry.id, month=3, amount=Decimal("50"))
        )
        db_session.flush()

        db_session.add(
            DividendMonth(entry_id=dividend_entry.id, month=3, amount=Decimal("60"))
        )
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_numeric_precision(
        self, db_session: Session, dividend_entry: DividendEntry
    ):
        db_session.add(
            DividendMonth(
                entry_id=dividend_entry.id, month=1, amount=Decimal("1234.5678")
            )
        )
        db_session.flush()
        db_session.expire_all()

        row = (
            db_session.query(DividendMonth)
            .filter_by(entry_id=dividend_entry.id, month=1)
            .one()
        )
        assert row.amount == Decimal("1234.5678")

    def test_cascade_delete_from_entry(
        self, db_session: Session, dividend_entry: DividendEntry
    ):
        month = DividendMonth(
            entry_id=dividend_entry.id, month=7, amount=Decimal("42.00")
        )
        db_session.add(month)
        db_session.flush()
        month_id = month.id

        db_session.delete(dividend_entry)
        db_session.flush()

        assert db_session.get(DividendMonth, month_id) is None


# ---------------------------------------------------------------------------
# YieldEntry
# ---------------------------------------------------------------------------


class TestYieldEntry:
    def test_create(self, db_session: Session, depot: Depot):
        entry = YieldEntry(
            depot_id=depot.id, year=2024, account_key="TradeRepublic Cash"
        )
        db_session.add(entry)
        db_session.flush()

        fetched = db_session.get(YieldEntry, entry.id)
        assert fetched.account_key == "TradeRepublic Cash"
        assert fetched.year == 2024

    def test_depot_year_account_unique(self, db_session: Session, depot: Depot):
        db_session.add(YieldEntry(depot_id=depot.id, year=2024, account_key="Savings"))
        db_session.flush()

        db_session.add(YieldEntry(depot_id=depot.id, year=2024, account_key="Savings"))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_same_account_allowed_in_different_depots(
        self, db_session: Session, user: User
    ):
        d1 = Depot(user_id=user.id, name="D1")
        d2 = Depot(user_id=user.id, name="D2")
        db_session.add_all([d1, d2])
        db_session.flush()

        db_session.add(YieldEntry(depot_id=d1.id, year=2024, account_key="Cash"))
        db_session.add(YieldEntry(depot_id=d2.id, year=2024, account_key="Cash"))
        db_session.flush()  # must not raise

    def test_with_monthly_amounts(self, db_session: Session, depot: Depot):
        entry = YieldEntry(depot_id=depot.id, year=2024, account_key="DKB Tagesgeld")
        db_session.add(entry)
        db_session.flush()

        for month, amount in [(1, "25.00"), (3, "26.50"), (12, "30.00")]:
            db_session.add(
                YieldMonth(entry_id=entry.id, month=month, amount=Decimal(amount))
            )
        db_session.flush()
        db_session.refresh(entry)

        assert len(entry.months) == 3
        total = sum(m.amount for m in entry.months)
        assert total == Decimal("81.50")

    def test_cascade_delete_from_depot(self, db_session: Session, depot: Depot):
        entry = YieldEntry(depot_id=depot.id, year=2024, account_key="DeleteMe")
        db_session.add(entry)
        db_session.flush()

        month = YieldMonth(entry_id=entry.id, month=1, amount=Decimal("5.00"))
        db_session.add(month)
        db_session.flush()
        month_id = month.id

        db_session.delete(depot)
        db_session.flush()

        assert db_session.get(YieldEntry, entry.id) is None
        assert db_session.get(YieldMonth, month_id) is None

    def test_back_populates_depot(self, db_session: Session, depot: Depot):
        db_session.add(YieldEntry(depot_id=depot.id, year=2024, account_key="Savings"))
        db_session.flush()
        db_session.refresh(depot)

        assert len(depot.yield_entries) == 1


# ---------------------------------------------------------------------------
# YieldMonth
# ---------------------------------------------------------------------------


class TestYieldMonth:
    def test_entry_month_unique(self, db_session: Session, depot: Depot):
        entry = YieldEntry(depot_id=depot.id, year=2024, account_key="UniqueTest")
        db_session.add(entry)
        db_session.flush()

        db_session.add(YieldMonth(entry_id=entry.id, month=5, amount=Decimal("10")))
        db_session.flush()

        db_session.add(YieldMonth(entry_id=entry.id, month=5, amount=Decimal("20")))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_numeric_precision(self, db_session: Session, depot: Depot):
        entry = YieldEntry(depot_id=depot.id, year=2024, account_key="PrecisionTest")
        db_session.add(entry)
        db_session.flush()

        db_session.add(
            YieldMonth(entry_id=entry.id, month=1, amount=Decimal("9999.9999"))
        )
        db_session.flush()
        db_session.expire_all()

        row = db_session.query(YieldMonth).filter_by(entry_id=entry.id, month=1).one()
        assert row.amount == Decimal("9999.9999")


# ---------------------------------------------------------------------------
# YearGoal
# ---------------------------------------------------------------------------


class TestYearGoal:
    def test_create_full(self, db_session: Session, user: User):
        goal = YearGoal(
            user_id=user.id,
            year=2024,
            dividend_goal=Decimal("1200.00"),
            yield_goal=Decimal("500.00"),
            steuerfreibetrag=Decimal("801.00"),
        )
        db_session.add(goal)
        db_session.flush()

        fetched = db_session.get(YearGoal, goal.id)
        assert fetched.dividend_goal == Decimal("1200.00")
        assert fetched.yield_goal == Decimal("500.00")
        assert fetched.steuerfreibetrag == Decimal("801.00")

    def test_all_goals_nullable(self, db_session: Session, user: User):
        goal = YearGoal(user_id=user.id, year=2030)
        db_session.add(goal)
        db_session.flush()

        fetched = db_session.get(YearGoal, goal.id)
        assert fetched.dividend_goal is None
        assert fetched.yield_goal is None
        assert fetched.steuerfreibetrag is None

    def test_user_year_unique(self, db_session: Session, user: User):
        db_session.add(YearGoal(user_id=user.id, year=2025))
        db_session.flush()

        db_session.add(YearGoal(user_id=user.id, year=2025))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_same_year_allowed_for_different_users(self, db_session: Session):
        u1 = User(sub="goal-u1", email="goal-u1@example.com")
        u2 = User(sub="goal-u2", email="goal-u2@example.com")
        db_session.add_all([u1, u2])
        db_session.flush()

        db_session.add(YearGoal(user_id=u1.id, year=2024))
        db_session.add(YearGoal(user_id=u2.id, year=2024))
        db_session.flush()  # must not raise

    def test_cascade_delete_from_user(self, db_session: Session):
        user = User(sub="goal-cascade", email="goal-cascade@example.com")
        db_session.add(user)
        db_session.flush()

        goal = YearGoal(user_id=user.id, year=2024)
        db_session.add(goal)
        db_session.flush()
        goal_id = goal.id

        db_session.delete(user)
        db_session.flush()

        assert db_session.get(YearGoal, goal_id) is None

    def test_back_populates_user(self, db_session: Session, user: User):
        db_session.add(YearGoal(user_id=user.id, year=2024))
        db_session.add(YearGoal(user_id=user.id, year=2025))
        db_session.flush()
        db_session.refresh(user)

        assert len(user.year_goals) == 2


# ---------------------------------------------------------------------------
# Full cascade chain: User → Depot → DividendEntry → DividendMonth
# ---------------------------------------------------------------------------


class TestFullCascadeChain:
    def test_delete_user_removes_entire_tree(self, db_session: Session):
        user = User(sub="tree-user", email="tree@example.com")
        db_session.add(user)
        db_session.flush()

        depot = Depot(user_id=user.id, name="Default")
        db_session.add(depot)
        db_session.flush()

        div_entry = DividendEntry(
            depot_id=depot.id, year=2024, ticker="AAPL", name="Apple"
        )
        yld_entry = YieldEntry(depot_id=depot.id, year=2024, account_key="Savings")
        db_session.add_all([div_entry, yld_entry])
        db_session.flush()

        div_month = DividendMonth(
            entry_id=div_entry.id, month=1, amount=Decimal("50.00")
        )
        yld_month = YieldMonth(entry_id=yld_entry.id, month=1, amount=Decimal("20.00"))
        db_session.add_all([div_month, yld_month])
        db_session.flush()

        ids = {
            "depot": depot.id,
            "div_entry": div_entry.id,
            "yld_entry": yld_entry.id,
            "div_month": div_month.id,
            "yld_month": yld_month.id,
        }

        db_session.delete(user)
        db_session.flush()

        assert db_session.get(Depot, ids["depot"]) is None
        assert db_session.get(DividendEntry, ids["div_entry"]) is None
        assert db_session.get(YieldEntry, ids["yld_entry"]) is None
        assert db_session.get(DividendMonth, ids["div_month"]) is None
        assert db_session.get(YieldMonth, ids["yld_month"]) is None


# ---------------------------------------------------------------------------
# Ticker
# ---------------------------------------------------------------------------


class TestTicker:
    def test_create_minimal(self, db_session: Session):
        t = Ticker(symbol="AAPL", name="Apple Inc.")
        db_session.add(t)
        db_session.flush()
        fetched = db_session.get(Ticker, "AAPL")
        assert fetched is not None
        assert fetched.name == "Apple Inc."
        assert fetched.sector is None
        assert fetched.exchange is None
        assert fetched.currency is None

    def test_create_full(self, db_session: Session):
        t = Ticker(
            symbol="SAP",
            name="SAP SE",
            sector="Technology",
            exchange="XETRA",
            currency="EUR",
        )
        db_session.add(t)
        db_session.flush()
        fetched = db_session.get(Ticker, "SAP")
        assert fetched.sector == "Technology"
        assert fetched.exchange == "XETRA"
        assert fetched.currency == "EUR"

    def test_symbol_is_primary_key(self, db_session: Session):
        db_session.add(Ticker(symbol="DUPE", name="First"))
        db_session.flush()
        db_session.add(Ticker(symbol="DUPE", name="Second"))
        with pytest.raises(IntegrityError):
            db_session.flush()
        db_session.rollback()

    def test_soft_fk_links_dividend_entry(self, db_session: Session, depot: Depot):
        db_session.add(Ticker(symbol="KO", name="Coca-Cola Co.", currency="USD"))
        db_session.flush()
        entry = DividendEntry(
            depot_id=depot.id, year=2024, ticker="KO", ticker_symbol="KO"
        )
        db_session.add(entry)
        db_session.flush()
        db_session.refresh(entry)
        assert entry.ticker_ref is not None
        assert entry.ticker_ref.name == "Coca-Cola Co."

    def test_null_ticker_symbol_allowed(self, db_session: Session, depot: Depot):
        # Custom / unlisted symbol — no entry in tickers table
        entry = DividendEntry(
            depot_id=depot.id, year=2024, ticker="CUSTOM", ticker_symbol=None
        )
        db_session.add(entry)
        db_session.flush()
        assert entry.ticker_symbol is None
        assert entry.ticker_ref is None

    def test_deleting_ticker_sets_null_on_entry(
        self, db_session: Session, depot: Depot
    ):
        db_session.add(Ticker(symbol="DEL", name="To Delete"))
        db_session.flush()
        entry = DividendEntry(
            depot_id=depot.id, year=2024, ticker="DEL", ticker_symbol="DEL"
        )
        db_session.add(entry)
        db_session.flush()

        t = db_session.get(Ticker, "DEL")
        db_session.delete(t)
        db_session.flush()
        db_session.refresh(entry)
        assert entry.ticker_symbol is None

    def test_back_populates_dividend_entries(self, db_session: Session, depot: Depot):
        db_session.add(Ticker(symbol="VZ", name="Verizon"))
        db_session.flush()
        db_session.add(
            DividendEntry(depot_id=depot.id, year=2024, ticker="VZ", ticker_symbol="VZ")
        )
        db_session.flush()
        t = db_session.get(Ticker, "VZ")
        db_session.refresh(t)
        assert len(t.dividend_entries) == 1
