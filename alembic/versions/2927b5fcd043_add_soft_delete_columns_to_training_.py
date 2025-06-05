"""add_soft_delete_columns_to_training_forms

Revision ID: 2927b5fcd043
Revises: 0c660d79e6f1
Create Date: 2025-06-05 17:43:09.804498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2927b5fcd043'
down_revision: Union[str, None] = '0c660d79e6f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add soft delete columns to training_forms table
    op.add_column('training_forms', sa.Column('deleted', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('training_forms', sa.Column('deleted_datetimestamp', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove soft delete columns from training_forms table
    op.drop_column('training_forms', 'deleted_datetimestamp')
    op.drop_column('training_forms', 'deleted')
