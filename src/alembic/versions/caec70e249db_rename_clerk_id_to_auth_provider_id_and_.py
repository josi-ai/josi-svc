"""rename clerk_id to auth_provider_id and add auth_provider column

Revision ID: caec70e249db
Revises: 180733c4c4fc
Create Date: 2026-03-08 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'caec70e249db'
down_revision: Union[str, None] = '180733c4c4fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f('ix_users_clerk_id'), table_name='users')
    op.alter_column('users', 'clerk_id', new_column_name='auth_provider_id')
    op.create_index(op.f('ix_users_auth_provider_id'), 'users', ['auth_provider_id'], unique=True)
    op.add_column('users', sa.Column('auth_provider', sa.String(), nullable=False, server_default='clerk'))
    op.create_index(op.f('ix_users_auth_provider'), 'users', ['auth_provider'])


def downgrade() -> None:
    op.drop_index(op.f('ix_users_auth_provider'), table_name='users')
    op.drop_column('users', 'auth_provider')
    op.drop_index(op.f('ix_users_auth_provider_id'), table_name='users')
    op.alter_column('users', 'auth_provider_id', new_column_name='clerk_id')
    op.create_index(op.f('ix_users_clerk_id'), 'users', ['clerk_id'], unique=True)
