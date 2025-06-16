"""add_is_draft_column_to_training_forms

Revision ID: b4a76550e4d5
Revises: cf6e42b89d32
Create Date: 2025-06-16 14:01:37.479900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4a76550e4d5'
down_revision: Union[str, None] = 'cf6e42b89d32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the is_draft column with default value False for existing records
    op.add_column('training_forms', sa.Column('is_draft', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove the is_draft column
    op.drop_column('training_forms', 'is_draft')
