"""add tickers reference table, soft FK on dividend_entries, goals as integer

Revision ID: b4f812c9d1e2
Revises: 938beee1a35d
Create Date: 2026-03-20 21:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.core.tickers import DEFAULT_TICKERS

revision: str = "b4f812c9d1e2"
down_revision: str | None = "938beee1a35d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tickers",
        sa.Column("symbol", sa.String(20), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sector", sa.String(100), nullable=True),
        sa.Column("exchange", sa.String(20), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
    )

    tickers_table = sa.table(
        "tickers",
        sa.column("symbol", sa.String),
        sa.column("name", sa.String),
        sa.column("sector", sa.String),
        sa.column("exchange", sa.String),
        sa.column("currency", sa.String),
    )
    op.bulk_insert(tickers_table, DEFAULT_TICKERS)

    # Soft FK from dividend_entries to tickers (nullable — allows custom symbols)
    op.add_column(
        "dividend_entries",
        sa.Column(
            "ticker_symbol",
            sa.String(20),
            sa.ForeignKey("tickers.symbol", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_dividend_entries_ticker_symbol",
        "dividend_entries",
        ["ticker_symbol"],
    )

    # Make dividend_entries.name nullable (display name override,
    # falls back to tickers.name)
    op.alter_column("dividend_entries", "name", nullable=True)

    # Change year_goals goal columns from NUMERIC(12,4) to INTEGER
    op.alter_column(
        "year_goals",
        "dividend_goal",
        type_=sa.Integer(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
        postgresql_using="dividend_goal::integer",
    )
    op.alter_column(
        "year_goals",
        "yield_goal",
        type_=sa.Integer(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
        postgresql_using="yield_goal::integer",
    )
    op.alter_column(
        "year_goals",
        "steuerfreibetrag",
        type_=sa.Integer(),
        existing_type=sa.Numeric(12, 4),
        existing_nullable=True,
        postgresql_using="steuerfreibetrag::integer",
    )


def downgrade() -> None:
    op.alter_column(
        "year_goals",
        "steuerfreibetrag",
        type_=sa.Numeric(12, 4),
        existing_type=sa.Integer(),
        existing_nullable=True,
        postgresql_using="steuerfreibetrag::numeric",
    )
    op.alter_column(
        "year_goals",
        "yield_goal",
        type_=sa.Numeric(12, 4),
        existing_type=sa.Integer(),
        existing_nullable=True,
        postgresql_using="yield_goal::numeric",
    )
    op.alter_column(
        "year_goals",
        "dividend_goal",
        type_=sa.Numeric(12, 4),
        existing_type=sa.Integer(),
        existing_nullable=True,
        postgresql_using="dividend_goal::numeric",
    )
    op.alter_column("dividend_entries", "name", nullable=False)
    op.drop_index("ix_dividend_entries_ticker_symbol", table_name="dividend_entries")
    op.drop_column("dividend_entries", "ticker_symbol")
    op.drop_table("tickers")
