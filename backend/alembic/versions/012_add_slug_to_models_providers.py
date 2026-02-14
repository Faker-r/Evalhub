"""Add slug columns to models and providers

Revision ID: 012_add_slug_to_models_providers
Revises: 011_add_models_providers
Create Date: 2026-01-28
"""

# pylint: disable=no-member

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012_add_slug_to_models_providers"
down_revision: str | None = "011_add_models_providers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("providers", sa.Column("slug", sa.String(), nullable=True))
    op.add_column("models", sa.Column("slug", sa.String(), nullable=True))

    op.execute("UPDATE providers SET slug = name WHERE slug IS NULL")
    op.execute("UPDATE models SET slug = display_name WHERE slug IS NULL")


def downgrade() -> None:
    op.drop_column("models", "slug")
    op.drop_column("providers", "slug")
