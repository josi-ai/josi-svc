"""rename descope_id to clerk_id

Revision ID: 180733c4c4fc
Revises: 2dc9d889793e
Create Date: 2026-03-07 23:38:47.190676

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '180733c4c4fc'
down_revision: Union[str, None] = '2dc9d889793e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_users_descope_id'), table_name='users')
    op.alter_column('users', 'descope_id', new_column_name='clerk_id')
    op.create_index(op.f('ix_users_clerk_id'), 'users', ['clerk_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_clerk_id'), table_name='users')
    op.alter_column('users', 'clerk_id', new_column_name='descope_id')
    op.create_index(op.f('ix_users_descope_id'), 'users', ['descope_id'], unique=True)
