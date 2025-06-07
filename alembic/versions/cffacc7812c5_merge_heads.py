"""merge_heads

Revision ID: cffacc7812c5
Revises: 2927b5fcd043, add_concur_claim_number
Create Date: 2025-06-07 14:14:59.208399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cffacc7812c5'
down_revision: Union[str, None] = ('2927b5fcd043', 'add_concur_claim_number')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
