"""Initial migration with table_id primary keys

Revision ID: 001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organization table
    op.create_table('organization',
        sa.Column('organization_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('api_key', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('plan_type', sa.String(), nullable=False),
        sa.Column('monthly_api_limit', sa.Integer(), nullable=False),
        sa.Column('current_month_usage', sa.Integer(), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_name', sa.String(), nullable=True),
        sa.Column('contact_phone', sa.String(), nullable=True),
        sa.Column('address_line1', sa.String(), nullable=True),
        sa.Column('address_line2', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('organization_id')
    )
    op.create_index(op.f('ix_organization_api_key'), 'organization', ['api_key'], unique=True)
    op.create_index(op.f('ix_organization_slug'), 'organization', ['slug'], unique=True)

    # Create person table
    op.create_table('person',
        sa.Column('person_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('time_of_birth', sa.DateTime(), nullable=False),
        sa.Column('place_of_birth', sa.String(), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('timezone', sa.String(), nullable=False),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('birth_certificate_id', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('source_system', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.organization_id'], ),
        sa.PrimaryKeyConstraint('person_id')
    )
    op.create_index(op.f('ix_person_email'), 'person', ['email'], unique=False)
    op.create_index(op.f('ix_person_external_id'), 'person', ['external_id'], unique=False)
    op.create_index(op.f('ix_person_organization_id'), 'person', ['organization_id'], unique=False)

    # Create astrology_chart table
    op.create_table('astrology_chart',
        sa.Column('chart_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('person_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('chart_type', sa.String(), nullable=False),
        sa.Column('house_system', sa.String(), nullable=True),
        sa.Column('ayanamsa', sa.String(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('calculation_version', sa.String(), nullable=False),
        sa.Column('chart_data', sa.JSON(), nullable=True),
        sa.Column('planet_positions', sa.JSON(), nullable=True),
        sa.Column('house_cusps', sa.JSON(), nullable=True),
        sa.Column('aspects', sa.JSON(), nullable=True),
        sa.Column('divisional_chart_type', sa.Integer(), nullable=True),
        sa.Column('progression_type', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.organization_id'], ),
        sa.ForeignKeyConstraint(['person_id'], ['person.person_id'], ),
        sa.PrimaryKeyConstraint('chart_id')
    )
    op.create_index(op.f('ix_astrology_chart_chart_type'), 'astrology_chart', ['chart_type'], unique=False)
    op.create_index(op.f('ix_astrology_chart_organization_id'), 'astrology_chart', ['organization_id'], unique=False)
    op.create_index(op.f('ix_astrology_chart_person_id'), 'astrology_chart', ['person_id'], unique=False)

    # Create planet_position table
    op.create_table('planet_position',
        sa.Column('planet_position_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('chart_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('planet_name', sa.String(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('sign', sa.String(), nullable=False),
        sa.Column('sign_degree', sa.Float(), nullable=False),
        sa.Column('house', sa.Integer(), nullable=False),
        sa.Column('house_degree', sa.Float(), nullable=True),
        sa.Column('nakshatra', sa.String(), nullable=True),
        sa.Column('nakshatra_pada', sa.Integer(), nullable=True),
        sa.Column('dignity', sa.String(), nullable=True),
        sa.Column('is_retrograde', sa.Boolean(), nullable=False),
        sa.Column('is_combust', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chart_id'], ['astrology_chart.chart_id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.organization_id'], ),
        sa.PrimaryKeyConstraint('planet_position_id')
    )
    op.create_index(op.f('ix_planet_position_chart_id'), 'planet_position', ['chart_id'], unique=False)
    op.create_index(op.f('ix_planet_position_organization_id'), 'planet_position', ['organization_id'], unique=False)

    # Create chart_interpretation table
    op.create_table('chart_interpretation',
        sa.Column('chart_interpretation_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('chart_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('interpretation_type', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('detailed_text', sa.JSON(), nullable=True),
        sa.Column('interpreter_version', sa.String(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chart_id'], ['astrology_chart.chart_id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.organization_id'], ),
        sa.PrimaryKeyConstraint('chart_interpretation_id')
    )
    op.create_index(op.f('ix_chart_interpretation_chart_id'), 'chart_interpretation', ['chart_id'], unique=False)
    op.create_index(op.f('ix_chart_interpretation_organization_id'), 'chart_interpretation', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chart_interpretation_organization_id'), table_name='chart_interpretation')
    op.drop_index(op.f('ix_chart_interpretation_chart_id'), table_name='chart_interpretation')
    op.drop_table('chart_interpretation')
    op.drop_index(op.f('ix_planet_position_organization_id'), table_name='planet_position')
    op.drop_index(op.f('ix_planet_position_chart_id'), table_name='planet_position')
    op.drop_table('planet_position')
    op.drop_index(op.f('ix_astrology_chart_person_id'), table_name='astrology_chart')
    op.drop_index(op.f('ix_astrology_chart_organization_id'), table_name='astrology_chart')
    op.drop_index(op.f('ix_astrology_chart_chart_type'), table_name='astrology_chart')
    op.drop_table('astrology_chart')
    op.drop_index(op.f('ix_person_organization_id'), table_name='person')
    op.drop_index(op.f('ix_person_external_id'), table_name='person')
    op.drop_index(op.f('ix_person_email'), table_name='person')
    op.drop_table('person')
    op.drop_index(op.f('ix_organization_slug'), table_name='organization')
    op.drop_index(op.f('ix_organization_api_key'), table_name='organization')
    op.drop_table('organization')