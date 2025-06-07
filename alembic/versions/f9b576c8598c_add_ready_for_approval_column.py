"""add_ready_for_approval_column

Revision ID: f9b576c8598c
Revises: cffacc7812c5
Create Date: 2025-06-07 14:15:12.459192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9b576c8598c'
down_revision: Union[str, None] = 'cffacc7812c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the ready_for_approval column as nullable first
    op.add_column('training_forms', sa.Column('ready_for_approval', sa.Boolean(), nullable=True))
    
    # Update existing forms based on content
    connection = op.get_bind()
    
    # Set default value for all existing records to True first
    connection.execute(sa.text("UPDATE training_forms SET ready_for_approval = 1"))
    
    # Define the pattern values that indicate form is not ready for approval
    flagged_patterns = ['NA', 'N/A', 'na', '1111']
    
    # Build the update query to check all relevant text and string fields
    update_query = """
    UPDATE training_forms 
    SET ready_for_approval = 0 
    WHERE training_name IN ({patterns})
        OR trainer_name IN ({patterns})
        OR supplier_name IN ({patterns})
        OR location_details IN ({patterns})
        OR training_description IN ({patterns})
        OR notes IN ({patterns})
        OR invoice_number IN ({patterns})
        OR concur_claim IN ({patterns})
        OR ida_class IN ({patterns})
    """.format(patterns="'" + "','".join(flagged_patterns) + "'")
    
    connection.execute(sa.text(update_query))
    
    # Now make the column NOT NULL (SQLite doesn't support this directly, so we'll leave it nullable)
    # In production with other databases, you could add: op.alter_column('training_forms', 'ready_for_approval', nullable=False)


def downgrade() -> None:
    # Remove the ready_for_approval column
    op.drop_column('training_forms', 'ready_for_approval')
