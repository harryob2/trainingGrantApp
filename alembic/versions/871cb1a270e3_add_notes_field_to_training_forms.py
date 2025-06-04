"""add_notes_field_to_training_forms

Revision ID: 871cb1a270e3
Revises: 8ad465126fdf
Create Date: 2025-06-04 16:22:56.039489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '871cb1a270e3'
down_revision: Union[str, None] = '8ad465126fdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notes column to training_forms table
    op.add_column('training_forms', sa.Column('notes', sa.Text, nullable=True))


def downgrade() -> None:
    # Remove notes column from training_forms table
    op.drop_column('training_forms', 'notes')
