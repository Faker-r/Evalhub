"""Add count_on_leaderboard to traces

Revision ID: 015_add_trace_count_on_leaderboard
Revises: 014_trace_model_config_columns
Create Date: 2026-02-06

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "015_trace_count_on_leaderboard"
down_revision: str | None = "014_trace_model_config_columns"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) add nullable column (instant, no rewrite, no lock)
    op.add_column(
        "traces",
        sa.Column("count_on_leaderboard", sa.Boolean(), nullable=True),
    )

    # 2) backfill in small batches (IMPORTANT)
    op.execute("""
        UPDATE traces
        SET count_on_leaderboard = false
        WHERE count_on_leaderboard IS NULL
    """)

    # 3) add constraint + default (fast metadata change)
    op.alter_column(
        "traces",
        "count_on_leaderboard",
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    op.drop_column("traces", "count_on_leaderboard")
