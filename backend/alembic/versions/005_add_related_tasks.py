"""Refactor benchmarks to group by dataset

Revision ID: 005_add_related_tasks
Revises: 004_add_benchmark_description
Create Date: 2026-01-08

This migration refactors the benchmarks table to group tasks by dataset:
- Drops unique constraint on task_name
- Renames task_name to tasks (JSONB array)
- Tasks are now grouped by dataset_name instead of individual task names
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005_add_related_tasks"
down_revision: str | None = "004_add_benchmark_description"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop the unique index on task_name
    op.drop_index("ix_benchmarks_task_name", table_name="benchmarks")

    # Rename task_name column to tasks and change type to JSONB array
    # First, create new column
    op.add_column(
        "benchmarks",
        sa.Column("tasks", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    # Migrate existing data: convert task_name string to array with single element
    op.execute(
        """
        UPDATE benchmarks 
        SET tasks = jsonb_build_array(task_name)
        WHERE task_name IS NOT NULL
    """
    )

    # Drop old task_name column
    op.drop_column("benchmarks", "task_name")


def downgrade() -> None:
    # Add back task_name column
    op.add_column(
        "benchmarks",
        sa.Column("task_name", sa.String(), nullable=True),
    )

    # Migrate data back: take first element from tasks array
    op.execute(
        """
        UPDATE benchmarks 
        SET task_name = tasks->0
        WHERE tasks IS NOT NULL AND jsonb_array_length(tasks) > 0
    """
    )

    # Make task_name non-nullable
    op.alter_column("benchmarks", "task_name", nullable=False)

    # Drop tasks column
    op.drop_column("benchmarks", "tasks")

    # Recreate the unique index
    op.create_index("ix_benchmarks_task_name", "benchmarks", ["task_name"], unique=True)
