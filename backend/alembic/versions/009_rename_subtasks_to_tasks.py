"""Rename benchmark_subtasks to benchmark_tasks

Revision ID: 009_rename_subtasks_to_tasks
Revises: 008_add_benchmark_subtasks
Create Date: 2026-01-27 13:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '009_rename_subtasks_to_tasks'
down_revision = '008_add_benchmark_subtasks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename the table
    op.rename_table('benchmark_subtasks', 'benchmark_tasks')
    # Rename the index
    op.drop_index('ix_benchmark_subtasks_benchmark_id', table_name='benchmark_tasks')
    op.create_index('ix_benchmark_tasks_benchmark_id', 'benchmark_tasks', ['benchmark_id'])


def downgrade() -> None:
    # Rename the index back
    op.drop_index('ix_benchmark_tasks_benchmark_id', table_name='benchmark_tasks')
    op.create_index('ix_benchmark_subtasks_benchmark_id', 'benchmark_tasks', ['benchmark_id'])
    # Rename the table back
    op.rename_table('benchmark_tasks', 'benchmark_subtasks')
