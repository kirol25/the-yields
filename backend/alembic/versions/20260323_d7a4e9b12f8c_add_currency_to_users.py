"""add currency column to users

Revision ID: d7a4e9b12f8c
Revises: b4f812c9d1e2
Create Date: 2026-03-23 12:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d7a4e9b12f8c"
down_revision: str | None = "b4f812c9d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "currency",
            sa.String(3),
            nullable=False,
            server_default="EUR",
            comment="ISO 4217 display currency preference, e.g. 'EUR'",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "currency")
