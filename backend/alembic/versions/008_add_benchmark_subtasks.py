"""Add benchmark_subtasks table

Revision ID: 008_add_benchmark_subtasks
Revises: 007_add_dataset_size
Create Date: 2026-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '008_add_benchmark_subtasks'
down_revision = '007_add_dataset_size'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create benchmark_subtasks table
    op.create_table(
        'benchmark_subtasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('benchmark_id', sa.Integer(), sa.ForeignKey('benchmarks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_name', sa.String(), nullable=False),
        sa.Column('hf_subset', sa.String(), nullable=True),
        sa.Column('evaluation_splits', JSONB(), nullable=True),
        sa.Column('dataset_size', sa.Integer(), nullable=True),
        sa.Column('estimated_input_tokens', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    # Create index on benchmark_id for faster joins
    op.create_index('ix_benchmark_subtasks_benchmark_id', 'benchmark_subtasks', ['benchmark_id'])


def downgrade() -> None:
    op.drop_index('ix_benchmark_subtasks_benchmark_id', table_name='benchmark_subtasks')
    op.drop_table('benchmark_subtasks')
