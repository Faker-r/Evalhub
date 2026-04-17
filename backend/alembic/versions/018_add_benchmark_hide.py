"""Add hide flag to benchmarks table

Revision ID: 018_add_benchmark_hide
Revises: 017_add_visibility
Create Date: 2026-03-16
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "018_add_benchmark_hide"
down_revision: str | None = "017_add_visibility"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "benchmarks",
        sa.Column(
            "hide", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )


def downgrade() -> None:
    op.drop_column("benchmarks", "hide")
