"""Change models and providers id columns from integer to string

Revision ID: 016_models_providers_id_string
Revises: 015_trace_count_on_leaderboard
Create Date: 2026-02-13

"""

from collections.abc import Sequence

from alembic import op

revision: str = "016_models_providers_id_string"
down_revision: str | None = "015_trace_count_on_leaderboard"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "model_provider_association_model_id_fkey",
        "model_provider_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        "model_provider_association_provider_id_fkey",
        "model_provider_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        "model_provider_association_pkey",
        "model_provider_association",
        type_="primary",
    )
    op.execute("ALTER TABLE providers ALTER COLUMN id TYPE VARCHAR(36) USING id::text")
    op.execute("ALTER TABLE models ALTER COLUMN id TYPE VARCHAR(36) USING id::text")
    op.execute(
        "ALTER TABLE model_provider_association ALTER COLUMN model_id TYPE VARCHAR(36) USING model_id::text"
    )
    op.execute(
        "ALTER TABLE model_provider_association ALTER COLUMN provider_id TYPE VARCHAR(36) USING provider_id::text"
    )
    op.create_primary_key(
        "model_provider_association_pkey",
        "model_provider_association",
        ["model_id", "provider_id"],
    )
    op.create_foreign_key(
        "model_provider_association_model_id_fkey",
        "model_provider_association",
        "models",
        ["model_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "model_provider_association_provider_id_fkey",
        "model_provider_association",
        "providers",
        ["provider_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "model_provider_association_model_id_fkey",
        "model_provider_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        "model_provider_association_provider_id_fkey",
        "model_provider_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        "model_provider_association_pkey",
        "model_provider_association",
        type_="primary",
    )
    op.execute(
        "ALTER TABLE model_provider_association ALTER COLUMN model_id TYPE INTEGER USING model_id::integer"
    )
    op.execute(
        "ALTER TABLE model_provider_association ALTER COLUMN provider_id TYPE INTEGER USING provider_id::integer"
    )
    op.execute("ALTER TABLE providers ALTER COLUMN id TYPE INTEGER USING id::integer")
    op.execute("ALTER TABLE models ALTER COLUMN id TYPE INTEGER USING id::integer")
    op.create_primary_key(
        "model_provider_association_pkey",
        "model_provider_association",
        ["model_id", "provider_id"],
    )
    op.create_foreign_key(
        "model_provider_association_model_id_fkey",
        "model_provider_association",
        "models",
        ["model_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "model_provider_association_provider_id_fkey",
        "model_provider_association",
        "providers",
        ["provider_id"],
        ["id"],
        ondelete="CASCADE",
    )
