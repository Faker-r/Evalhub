"""Update guidelines scoring system

Revision ID: 006_update_guidelines_scoring
Revises: 005_add_related_tasks
Create Date: 2026-01-09

This migration updates the guidelines table to support different scoring scales:
- Adds scoring_scale column (string)
- Adds scoring_scale_config column (JSON)
- Removes max_score column
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "006_update_guidelines_scoring"
down_revision: str | None = "005_add_related_tasks"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add new columns
    op.add_column(
        "guidelines",
        sa.Column("scoring_scale", sa.String(), nullable=True),
    )
    op.add_column(
        "guidelines",
        sa.Column(
            "scoring_scale_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    # Migrate existing data: convert max_score to numeric scale
    op.execute(
        """
        UPDATE guidelines 
        SET 
            scoring_scale = 'numeric',
            scoring_scale_config = jsonb_build_object(
                'min_value', 0,
                'max_value', max_score
            )
        WHERE max_score IS NOT NULL
    """
    )

    # Make new columns non-nullable
    op.alter_column("guidelines", "scoring_scale", nullable=False)
    op.alter_column("guidelines", "scoring_scale_config", nullable=False)

    # Drop old max_score column
    op.drop_column("guidelines", "max_score")


def downgrade() -> None:
    # Add back max_score column
    op.add_column(
        "guidelines",
        sa.Column("max_score", sa.Integer(), nullable=True),
    )

    # Migrate data back: extract max_value from numeric scale configs
    op.execute(
        """
        UPDATE guidelines 
        SET max_score = CAST(scoring_scale_config->>'max_value' AS INTEGER)
        WHERE scoring_scale = 'numeric'
    """
    )

    # Set default value for non-numeric scales
    op.execute(
        """
        UPDATE guidelines 
        SET max_score = 1
        WHERE max_score IS NULL
    """
    )

    # Make max_score non-nullable
    op.alter_column("guidelines", "max_score", nullable=False)

    # Drop new columns
    op.drop_column("guidelines", "scoring_scale_config")
    op.drop_column("guidelines", "scoring_scale")
