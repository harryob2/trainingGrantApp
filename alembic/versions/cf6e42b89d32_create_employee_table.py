"""Create employee table

Revision ID: cf6e42b89d32
Revises: 31a71c4d1ca3
Create Date: 2025-06-07 23:34:00.126028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf6e42b89d32'
down_revision: Union[str, None] = '31a71c4d1ca3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the employees table
    op.create_table('employees',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Create index on email for fast lookups
    op.create_index('idx_employees_email', 'employees', ['email'])
    
    # Create index on department for filtering
    op.create_index('idx_employees_department', 'employees', ['department'])
    
    # Create index on last_name for sorting
    op.create_index('idx_employees_last_name', 'employees', ['last_name'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_employees_last_name', 'employees')
    op.drop_index('idx_employees_department', 'employees')
    op.drop_index('idx_employees_email', 'employees')
    
    # Drop the table
    op.drop_table('employees')
