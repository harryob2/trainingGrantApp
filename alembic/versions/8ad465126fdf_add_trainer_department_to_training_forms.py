"""add_trainer_department_to_training_forms

Revision ID: 8ad465126fdf
Revises: 20083c585b8b
Create Date: 2025-06-04 15:26:50.471213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ad465126fdf'
down_revision: Union[str, None] = '20083c585b8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add trainer_department column to training_forms table
    op.add_column('training_forms', sa.Column('trainer_department', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove trainer_department column from training_forms table
    op.drop_column('training_forms', 'trainer_department')
