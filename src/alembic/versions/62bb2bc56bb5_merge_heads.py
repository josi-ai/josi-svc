"""merge_heads

Revision ID: 62bb2bc56bb5
Revises: 001, add_user_auth_ai
Create Date: 2025-07-15 14:03:05.323061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62bb2bc56bb5'
down_revision: Union[str, None] = ('001', 'add_user_auth_ai')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass