"""Add dataset_size column to benchmarks

Revision ID: 007_add_dataset_size
Revises: 006_update_guidelines_scoring
Create Date: 2026-01-26 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_dataset_size'
down_revision = '006_update_guidelines_scoring'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add dataset_size column to benchmarks table
    op.add_column('benchmarks', sa.Column('dataset_size', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove dataset_size column from benchmarks table
    op.drop_column('benchmarks', 'dataset_size')
