"""update_ready_for_approval_not_sure_ida_class

Revision ID: 31a71c4d1ca3
Revises: f9b576c8598c
Create Date: 2025-06-07 15:44:23.017595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31a71c4d1ca3'
down_revision: Union[str, None] = 'f9b576c8598c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update existing forms where ida_class is 'Not sure' to set ready_for_approval = 0
    connection = op.get_bind()
    
    # Update forms with 'Not sure' ida_class to not be ready for approval
    connection.execute(sa.text(
        "UPDATE training_forms SET ready_for_approval = 0 WHERE ida_class = 'Not sure'"
    ))


def downgrade() -> None:
    # Reverse the change by setting ready_for_approval back to 1 for 'Not sure' ida_class
    connection = op.get_bind()
    
    # Set ready_for_approval back to 1 for forms with 'Not sure' ida_class
    connection.execute(sa.text(
        "UPDATE training_forms SET ready_for_approval = 1 WHERE ida_class = 'Not sure'"
    ))
