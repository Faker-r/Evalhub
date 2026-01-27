"""Remove dataset_size and estimated_input_tokens from benchmarks table

These fields are now stored per-task in the benchmark_tasks table.

Revision ID: 010_remove_benchmark_size_tokens
Revises: 009_rename_subtasks_to_tasks
Create Date: 2026-01-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_remove_benchmark_size_tokens'
down_revision = '009_rename_subtasks_to_tasks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('benchmarks', 'dataset_size')
    op.drop_column('benchmarks', 'estimated_input_tokens')


def downgrade() -> None:
    op.add_column('benchmarks', sa.Column('estimated_input_tokens', sa.Integer(), nullable=True))
    op.add_column('benchmarks', sa.Column('dataset_size', sa.Integer(), nullable=True))
