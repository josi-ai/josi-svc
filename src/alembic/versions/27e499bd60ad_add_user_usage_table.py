"""add user_usage table

Revision ID: 27e499bd60ad
Revises: caec70e249db
Create Date: 2026-03-08 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '27e499bd60ad'
down_revision: Union[str, None] = 'caec70e249db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_usage',
        sa.Column('usage_id', UUID(), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('period', sa.String(), nullable=False),
        sa.Column('charts_calculated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ai_interpretations_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('consultations_booked', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('saved_charts_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('usage_id'),
    )
    op.create_index(op.f('ix_user_usage_user_id'), 'user_usage', ['user_id'])
    op.create_index(op.f('ix_user_usage_period'), 'user_usage', ['period'])


def downgrade() -> None:
    op.drop_index(op.f('ix_user_usage_period'), table_name='user_usage')
    op.drop_index(op.f('ix_user_usage_user_id'), table_name='user_usage')
    op.drop_table('user_usage')
