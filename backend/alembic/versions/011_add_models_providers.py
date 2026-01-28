"""Add models and providers tables

Revision ID: 011_add_models_providers
Revises: 010_remove_benchmark_size_tokens
Create Date: 2026-01-27

This migration creates the providers and models tables, and the association table
for the many-to-many relationship between them.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011_add_models_providers"
down_revision: str | None = "010_remove_benchmark_size_tokens"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create providers table
    op.create_table(
        "providers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_providers_name", "providers", ["name"], unique=True)

    # Create models table
    op.create_table(
        "models",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("developer", sa.String(), nullable=False),
        sa.Column("api_name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_models_api_name", "models", ["api_name"])

    # Create many-to-many association table
    op.create_table(
        "model_provider_association",
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["model_id"], ["models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_id"], ["providers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("model_id", "provider_id"),
    )


def downgrade() -> None:
    op.drop_table("model_provider_association")
    op.drop_index("ix_models_api_name", table_name="models")
    op.drop_table("models")
    op.drop_index("ix_providers_name", table_name="providers")
    op.drop_table("providers")
