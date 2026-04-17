"""Add description column to benchmarks

Revision ID: 004_add_benchmark_description
Revises: 003_add_benchmarks
Create Date: 2026-01-08 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_add_benchmark_description"
down_revision = "003_add_benchmarks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add description column to benchmarks table
    op.add_column("benchmarks", sa.Column("description", sa.String(), nullable=True))


def downgrade() -> None:
    # Remove description column from benchmarks table
    op.drop_column("benchmarks", "description")
