"""add_receive_emails_to_admins

Revision ID: 7654429db461
Revises: 871cb1a270e3
Create Date: 2025-06-05 11:53:57.015096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7654429db461'
down_revision: Union[str, None] = '871cb1a270e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add receive_emails column to admins table
    # Default to True so existing admins will receive emails by default
    op.add_column('admins', sa.Column('receive_emails', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Remove receive_emails column from admins table
    op.drop_column('admins', 'receive_emails')
