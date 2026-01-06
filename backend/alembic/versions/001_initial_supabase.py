"""Initial Supabase-compatible migration

Revision ID: 001_initial_supabase
Revises: 
Create Date: 2025-12-04

This migration creates all tables for the evalhub application.
User authentication is handled by Supabase Auth, so no users table is needed.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_supabase"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create datasets table
    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_datasets_name", "datasets", ["name"], unique=True)

    # Create guidelines table
    op.create_table(
        "guidelines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_guidelines_name", "guidelines", ["name"], unique=True)

    # Create traces table
    # user_id is a String to store Supabase UUID (no FK to a local users table)
    op.create_table(
        "traces",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),  # Supabase UUID
        sa.Column("dataset_name", sa.String(), nullable=False),
        sa.Column("guideline_names", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("completion_model", sa.String(), nullable=False),
        sa.Column("model_provider", sa.String(), nullable=False),
        sa.Column("judge_model", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_traces_user_id", "traces", ["user_id"])

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
    op.create_index("ix_trace_events_trace_id", "trace_events", ["trace_id"])
    op.create_index("ix_trace_events_event_type", "trace_events", ["event_type"])


def downgrade() -> None:
    # Drop indexes and tables in reverse order
    op.drop_index("ix_trace_events_event_type", table_name="trace_events")
    op.drop_index("ix_trace_events_trace_id", table_name="trace_events")
    op.drop_table("trace_events")

    op.drop_index("ix_traces_user_id", table_name="traces")
    op.drop_table("traces")

    op.drop_index("ix_guidelines_name", table_name="guidelines")
    op.drop_table("guidelines")

    op.drop_index("ix_datasets_name", table_name="datasets")
    op.drop_table("datasets")

