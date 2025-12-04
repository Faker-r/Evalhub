from typing import Optional, Sequence, Tuple, Union
"""add datasets and guidelines tables

Revision ID: 001_add_datasets_guidelines
Revises: ef2910566747
Create Date: 2025-12-01

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_add_datasets_guidelines"
down_revision: Optional[str] = "ef2910566747"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    # Create datasets table
    op.create_table(
        "datasets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("sample_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_datasets_id"), "datasets", ["id"], unique=False)
    op.create_index(op.f("ix_datasets_name"), "datasets", ["name"], unique=True)

    # Create guidelines table
    op.create_table(
        "guidelines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_guidelines_id"), "guidelines", ["id"], unique=False)
    op.create_index(op.f("ix_guidelines_name"), "guidelines", ["name"], unique=False)


def downgrade() -> None:
    # Drop guidelines table
    op.drop_index(op.f("ix_guidelines_name"), table_name="guidelines")
    op.drop_index(op.f("ix_guidelines_id"), table_name="guidelines")
    op.drop_table("guidelines")

    # Drop datasets table
    op.drop_index(op.f("ix_datasets_name"), table_name="datasets")
    op.drop_index(op.f("ix_datasets_id"), table_name="datasets")
    op.drop_table("datasets")
