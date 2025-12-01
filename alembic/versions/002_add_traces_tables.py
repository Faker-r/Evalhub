"""add traces and trace_events tables

Revision ID: 002_add_traces
Revises: 001_add_datasets_guidelines
Create Date: 2025-12-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_traces"
down_revision: str | None = "001_add_datasets_guidelines"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create traces table
    op.create_table(
        "traces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("dataset_name", sa.String(), nullable=False),
        sa.Column("guideline_names", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("completion_model", sa.String(), nullable=False),
        sa.Column("model_provider", sa.String(), nullable=False),
        sa.Column("judge_model", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create trace_events table
    op.create_table(
        "trace_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trace_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("sample_id", sa.String(), nullable=True),
        sa.Column("guideline_name", sa.String(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["trace_id"], ["traces.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for common queries
    op.create_index("ix_traces_user_id", "traces", ["user_id"])
    op.create_index("ix_trace_events_trace_id", "trace_events", ["trace_id"])
    op.create_index("ix_trace_events_event_type", "trace_events", ["event_type"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_trace_events_event_type", table_name="trace_events")
    op.drop_index("ix_trace_events_trace_id", table_name="trace_events")
    op.drop_index("ix_traces_user_id", table_name="traces")

    # Drop tables
    op.drop_table("trace_events")
    op.drop_table("traces")

