"""Add benchmarks table

Revision ID: 003_add_benchmarks
Revises: 002_add_missing_columns
Create Date: 2025-01-08

This migration creates the benchmarks table to store lighteval task information.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_add_benchmarks"
down_revision: str | None = "002_add_missing_columns"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create benchmarks table
    op.create_table(
        "benchmarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_name", sa.String(), nullable=False),
        sa.Column("dataset_name", sa.String(), nullable=False),
        sa.Column("hf_repo", sa.String(), nullable=False),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("downloads", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("estimated_input_tokens", sa.Integer(), nullable=True),
        sa.Column("repo_type", sa.String(), nullable=True),
        sa.Column("created_at_hf", sa.DateTime(), nullable=True),
        sa.Column("private", sa.Boolean(), nullable=True),
        sa.Column("gated", sa.Boolean(), nullable=True),
        sa.Column("files", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_benchmarks_task_name", "benchmarks", ["task_name"], unique=True)
    op.create_index("ix_benchmarks_hf_repo", "benchmarks", ["hf_repo"])
    op.create_index("ix_benchmarks_author", "benchmarks", ["author"])


def downgrade() -> None:
    op.drop_index("ix_benchmarks_author", table_name="benchmarks")
    op.drop_index("ix_benchmarks_hf_repo", table_name="benchmarks")
    op.drop_index("ix_benchmarks_task_name", table_name="benchmarks")
    op.drop_table("benchmarks")
