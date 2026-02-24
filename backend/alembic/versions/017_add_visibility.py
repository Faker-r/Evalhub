"""Add visibility and user ownership to datasets and guidelines

Revision ID: 017_add_visibility
Revises: 016_models_providers_id_string
Create Date: 2026-02-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "017_add_visibility"
down_revision: str | None = "016_models_providers_id_string"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add visibility and user_id to datasets
    op.add_column("datasets", sa.Column("visibility", sa.String(), nullable=False, server_default="public"))
    op.add_column("datasets", sa.Column("user_id", sa.String(), nullable=True))
    op.create_index("ix_datasets_visibility", "datasets", ["visibility"])
    op.create_index("ix_datasets_user_id", "datasets", ["user_id"])

    # Add visibility and user_id to guidelines
    op.add_column("guidelines", sa.Column("visibility", sa.String(), nullable=False, server_default="public"))
    op.add_column("guidelines", sa.Column("user_id", sa.String(), nullable=True))
    op.create_index("ix_guidelines_visibility", "guidelines", ["visibility"])
    op.create_index("ix_guidelines_user_id", "guidelines", ["user_id"])


def downgrade() -> None:
    # Remove from guidelines
    op.drop_index("ix_guidelines_user_id", table_name="guidelines")
    op.drop_index("ix_guidelines_visibility", table_name="guidelines")
    op.drop_column("guidelines", "user_id")
    op.drop_column("guidelines", "visibility")

    # Remove from datasets
    op.drop_index("ix_datasets_user_id", table_name="datasets")
    op.drop_index("ix_datasets_visibility", table_name="datasets")
    op.drop_column("datasets", "user_id")
    op.drop_column("datasets", "visibility")
