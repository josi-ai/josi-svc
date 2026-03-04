"""sync model drift

Revision ID: 69133c8c07c3
Revises: 6aa21d239323
Create Date: 2026-03-04 17:46:41.937135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '69133c8c07c3'
down_revision: Union[str, None] = '6aa21d239323'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('astrology_chart', 'chart_data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('astrology_chart', 'planet_positions',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('astrology_chart', 'house_cusps',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('astrology_chart', 'aspects',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('chart_interpretation', 'detailed_text',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('chart_interpretation', 'keywords',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)


def downgrade() -> None:
    op.alter_column('chart_interpretation', 'keywords',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('chart_interpretation', 'detailed_text',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('astrology_chart', 'aspects',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('astrology_chart', 'house_cusps',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('astrology_chart', 'planet_positions',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('astrology_chart', 'chart_data',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
