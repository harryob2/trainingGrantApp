"""Add concur_claim_number to travel_expenses and material_expenses

Revision ID: add_concur_claim_number
Revises: 20083c585b8b
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_concur_claim_number'
down_revision: Union[str, None] = '20083c585b8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add concur_claim_number column to travel_expenses table
    op.add_column('travel_expenses', sa.Column('concur_claim_number', sa.String(255), nullable=True))
    
    # Add concur_claim_number column to material_expenses table
    op.add_column('material_expenses', sa.Column('concur_claim_number', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove concur_claim_number column from material_expenses table
    op.drop_column('material_expenses', 'concur_claim_number')
    
    # Remove concur_claim_number column from travel_expenses table
    op.drop_column('travel_expenses', 'concur_claim_number') 