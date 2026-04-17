"""Add missing category column to guidelines

Revision ID: 002_add_missing_columns
Revises: 001_initial_supabase
Create Date: 2025-12-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_missing_columns"
down_revision: str | None = "001_initial_supabase"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add missing category column to guidelines table
    op.add_column("guidelines", sa.Column("category", sa.String(), nullable=True))

    # Update existing rows to have a default category (if any exist)
    op.execute("UPDATE guidelines SET category = 'general' WHERE category IS NULL")

    # Make the column non-nullable after setting defaults
    op.alter_column("guidelines", "category", nullable=False)


def downgrade() -> None:
    op.drop_column("guidelines", "category")
