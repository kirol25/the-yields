"""add subscription_plan column to users

Revision ID: c3e1f7a29b4d
Revises: b4f812c9d1e2
Create Date: 2026-03-22 12:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3e1f7a29b4d"
down_revision: str | None = "b4f812c9d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "subscription_plan",
            sa.String(20),
            nullable=True,
            comment="Active plan: 'monthly' or 'yearly'. NULL when not premium.",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "subscription_plan")
