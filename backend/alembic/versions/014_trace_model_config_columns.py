"""Trace model config columns: completion_model_config, judge_model_config

Revision ID: 014_trace_model_config_columns
Revises: 013_remove_slug_from_models
Create Date: 2026-01-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014_trace_model_config_columns"
down_revision: str | None = "013_remove_slug_from_models"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "traces",
        sa.Column(
            "completion_model_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "traces",
        sa.Column(
            "judge_model_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE traces
        SET
        completion_model_config = jsonb_build_object(
            'api_source', 'standard',
            'api_name', completion_model,
            'provider_slug', model_provider
        ),
        judge_model_config = jsonb_build_object(
            'api_source', 'standard',
            'api_name', judge_model,
            'provider_slug', model_provider
        )
        WHERE completion_model_config IS NULL
        """
    )

    op.drop_column("traces", "completion_model")
    op.drop_column("traces", "model_provider")
    op.drop_column("traces", "judge_model")


def downgrade() -> None:
    op.execute(sa.text("SET LOCAL statement_timeout = '0'"))
    op.add_column("traces", sa.Column("completion_model", sa.String(), nullable=True))
    op.add_column("traces", sa.Column("model_provider", sa.String(), nullable=True))
    op.add_column("traces", sa.Column("judge_model", sa.String(), nullable=True))

    op.execute(
        """
        UPDATE traces
        SET
            completion_model = completion_model_config->>'api_name',
            model_provider = completion_model_config->>'provider_slug',
            judge_model = judge_model_config->>'api_name'
        """
    )

    op.alter_column("traces", "completion_model", nullable=False)
    op.alter_column("traces", "model_provider", nullable=False)
    op.alter_column("traces", "judge_model", nullable=False)

    op.drop_column("traces", "completion_model_config")
    op.drop_column("traces", "judge_model_config")
