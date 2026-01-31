"""Remove slug column from models

Revision ID: 013_remove_slug_from_models
Revises: 012_add_slug_to_models_providers
Create Date: 2026-01-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "013_remove_slug_from_models"
down_revision: str | None = "012_add_slug_to_models_providers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("models", "slug")


def downgrade() -> None:
    op.add_column("models", sa.Column("slug", sa.String(), nullable=True))
