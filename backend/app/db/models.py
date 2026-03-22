"""SQLAlchemy ORM models for the-yields.

Hierarchy:
    Ticker             (central reference table for known stock symbols)
    User
    ├── Depot              (one user → many depots, e.g. "TradeRepublic", "IB")
    │   ├── DividendEntry  (one depot+year → many tickers)
    │   │   └── DividendMonth  (one entry → up to 12 monthly amounts)
    │   └── YieldEntry     (one depot+year → many savings/interest accounts)
    │       └── YieldMonth     (one entry → up to 12 monthly amounts)
    └── YearGoal           (one user+year → dividend/yield goals + steuerfreibetrag)
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ticker(Base):
    """Central reference table of known stock / ETF symbols.

    Pre-seeded with common dividend stocks. Custom tickers entered by users
    that are not in this table are allowed — DividendEntry.ticker_symbol will
    simply be NULL for those rows.
    """

    __tablename__ = "tickers"

    symbol: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        comment="Exchange ticker symbol, e.g. 'AAPL'",
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Full company / fund name",
    )
    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="GICS sector, e.g. 'Technology'",
    )
    exchange: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Primary listing exchange, e.g. 'NASDAQ'",
    )
    currency: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
        comment="ISO 4217 trading currency, e.g. 'USD'",
    )

    # relationships
    dividend_entries: Mapped[list["DividendEntry"]] = relationship(
        "DividendEntry", back_populates="ticker_ref"
    )

    def __repr__(self) -> str:
        return f"<Ticker symbol={self.symbol!r} name={self.name!r}>"


class User(Base):
    """Authenticated user synced from Cognito on first sign-in."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sub: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="Cognito identity sub (stable unique identifier)",
    )
    email: Mapped[str] = mapped_column(
        String(254), unique=True, nullable=False, index=True
    )
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Set to True by Stripe webhook on active subscription",
    )
    subscription_plan: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="Active plan: 'monthly' or 'yearly'. NULL when not premium.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # relationships
    depots: Mapped[list["Depot"]] = relationship(
        "Depot", back_populates="user", cascade="all, delete-orphan"
    )
    year_goals: Mapped[list["YearGoal"]] = relationship(
        "YearGoal", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User email={self.email!r} premium={self.is_premium}>"


class Depot(Base):
    """A brokerage / provider account owned by a user.

    Every user gets at least one depot ("Default") for backwards compatibility.
    Additional depots allow tracking the same ticker independently across brokers.
    """

    __tablename__ = "depots"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_depot_user_name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment='Display name, e.g. "TradeRepublic" or "Interactive Brokers"',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="depots")
    dividend_entries: Mapped[list["DividendEntry"]] = relationship(
        "DividendEntry", back_populates="depot", cascade="all, delete-orphan"
    )
    yield_entries: Mapped[list["YieldEntry"]] = relationship(
        "YieldEntry", back_populates="depot", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Depot name={self.name!r}>"


class DividendEntry(Base):
    """One ticker's dividend data for a given depot and year.

    ``ticker`` is the unique key within the depot+year scope (e.g. "AAPL").
    ``name`` is a nullable override; falls back to tickers.name via ticker_ref.
    ``ticker_symbol`` is a soft FK to the tickers reference table; NULL when
    the symbol is not in the reference table (custom / unlisted instruments).
    Monthly amounts are stored in the related DividendMonth rows.
    """

    __tablename__ = "dividend_entries"
    __table_args__ = (
        UniqueConstraint(
            "depot_id", "year", "ticker", name="uq_dividend_depot_year_ticker"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    depot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    ticker: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="User-defined unique key within the depot+year,"
        "typically a ticker symbol",
    )
    name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Optional display name override; falls back to tickers.name when NULL",
    )
    ticker_symbol: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("tickers.symbol", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Soft FK to tickers.symbol; NULL for custom/unknown symbols",
    )

    # relationships
    depot: Mapped["Depot"] = relationship("Depot", back_populates="dividend_entries")
    ticker_ref: Mapped["Ticker | None"] = relationship(
        "Ticker", back_populates="dividend_entries"
    )
    months: Mapped[list["DividendMonth"]] = relationship(
        "DividendMonth", back_populates="entry", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DividendEntry ticker={self.ticker!r} year={self.year}>"


class DividendMonth(Base):
    """Monthly dividend amount for a single DividendEntry
    (sparse — only set months stored)."""

    __tablename__ = "dividend_months"
    __table_args__ = (
        UniqueConstraint("entry_id", "month", name="uq_dividend_entry_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dividend_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Calendar month 1–12"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="Dividend income in user's currency"
    )

    # relationships
    entry: Mapped["DividendEntry"] = relationship(
        "DividendEntry", back_populates="months"
    )

    def __repr__(self) -> str:
        return f"<DividendMonth month={self.month} amount={self.amount}>"


class YieldEntry(Base):
    """One savings/interest account's yield data for a given depot and year.

    ``account_key`` is both the unique key and the display label the user gave
    the account (e.g. "TradeRepublic Cash", "Tagesgeld DKB").
    Monthly amounts are stored in the related YieldMonth rows.
    """

    __tablename__ = "yield_entries"
    __table_args__ = (
        UniqueConstraint(
            "depot_id", "year", "account_key", name="uq_yield_depot_year_account"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    depot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("depots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    account_key: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="User-defined label, used as both key and display name",
    )

    # relationships
    depot: Mapped["Depot"] = relationship("Depot", back_populates="yield_entries")
    months: Mapped[list["YieldMonth"]] = relationship(
        "YieldMonth", back_populates="entry", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<YieldEntry account={self.account_key!r} year={self.year}>"


class YieldMonth(Base):
    """Monthly yield/interest amount for a single YieldEntry
    (sparse — only set months stored)."""

    __tablename__ = "yield_months"
    __table_args__ = (
        UniqueConstraint("entry_id", "month", name="uq_yield_entry_month"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("yield_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    month: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Calendar month 1–12"
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 4),
        nullable=False,
        comment="Yield/interest income in user's currency",
    )

    # relationships
    entry: Mapped["YieldEntry"] = relationship("YieldEntry", back_populates="months")

    def __repr__(self) -> str:
        return f"<YieldMonth month={self.month} amount={self.amount}>"


class YearGoal(Base):
    """Per-user, per-year financial goals and tax-free allowance (Steuerfreibetrag).

    A row is created (or upserted) whenever the user saves their settings.
    All goal fields are nullable — the user may set only some of them.
    Goals are stored as whole integers (euros/dollars — no cents needed for targets).
    """

    __tablename__ = "year_goals"
    __table_args__ = (
        UniqueConstraint("user_id", "year", name="uq_year_goal_user_year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    dividend_goal: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Target annual dividend income (whole currency units)",
    )
    yield_goal: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Target annual yield/interest income (whole currency units)",
    )
    steuerfreibetrag: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="German tax-free savings allowance for the year (whole euros)",
    )

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="year_goals")

    def __repr__(self) -> str:
        return f"<YearGoal user_id={self.user_id} year={self.year}>"
