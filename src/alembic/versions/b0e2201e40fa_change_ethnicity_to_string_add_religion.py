"""change_ethnicity_to_string_add_religion

Revision ID: b0e2201e40fa
Revises: da050cce91a7
Create Date: 2026-04-18 21:39:32.011896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b0e2201e40fa'
down_revision: Union[str, None] = 'da050cce91a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add religion column
    op.add_column('users', sa.Column('religion', sa.String(), nullable=True))

    # Convert ethnicity from JSON array to plain string in one step
    # The USING clause extracts the first element of the JSON array during type conversion
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN ethnicity TYPE VARCHAR
        USING (ethnicity::json->>0)
    """)


def downgrade() -> None:
    # Convert ethnicity back to JSON array
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN ethnicity TYPE JSON
        USING (CASE WHEN ethnicity IS NOT NULL THEN json_build_array(ethnicity) ELSE NULL END)
    """)
    op.drop_column('users', 'religion')