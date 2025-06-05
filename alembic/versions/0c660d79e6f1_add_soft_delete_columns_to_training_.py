"""add_soft_delete_columns_to_training_forms

Revision ID: 0c660d79e6f1
Revises: 7654429db461
Create Date: 2025-06-05 17:42:47.468016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c660d79e6f1'
down_revision: Union[str, None] = '7654429db461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
