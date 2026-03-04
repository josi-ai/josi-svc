"""add pgvector extension and interpretation_embedding table

Revision ID: 6aa21d239323
Revises: 62bb2bc56bb5
Create Date: 2026-03-04 17:42:54.698056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy.vector

# revision identifiers, used by Alembic.
revision: str = '6aa21d239323'
down_revision: Union[str, None] = '62bb2bc56bb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table('interpretation_embedding',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(), nullable=True),
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('embedding_id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True),
    sa.Column('chart_features', sa.String(), nullable=False),
    sa.Column('question', sa.String(), nullable=False),
    sa.Column('interpretation', sa.Text(), nullable=False),
    sa.Column('chart_type', sa.String(), nullable=False),
    sa.Column('content_hash', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.organization_id'], ),
    sa.PrimaryKeyConstraint('embedding_id'),
    sa.UniqueConstraint('content_hash')
    )
    op.create_index(op.f('ix_interpretation_embedding_organization_id'), 'interpretation_embedding', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_interpretation_embedding_organization_id'), table_name='interpretation_embedding')
    op.drop_table('interpretation_embedding')
