"""Add user authentication and AI features

Revision ID: add_user_auth_ai
Revises: [previous_revision]
Create Date: 2025-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_auth_ai'
down_revision = None  # Update this with the actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user authentication tables."""
    
    # Create users table
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=True),
        sa.Column('birth_location', sa.JSON(), nullable=True),
        sa.Column('subscription_tier', sa.String(), nullable=False),
        sa.Column('subscription_end_date', sa.DateTime(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=False),
        sa.Column('notification_settings', sa.JSON(), nullable=False),
        sa.Column('oauth_providers', sa.JSON(), nullable=False),
        sa.Column('google_id', sa.String(), nullable=True),
        sa.Column('github_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # Create indexes for users table
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=False)
    op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=False)
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=False)
    op.create_index(op.f('ix_users_github_id'), 'users', ['github_id'], unique=False)


def downgrade() -> None:
    """Drop user authentication tables."""
    
    # Drop indexes
    op.drop_index(op.f('ix_users_github_id'), table_name='users')
    op.drop_index(op.f('ix_users_google_id'), table_name='users')
    op.drop_index(op.f('ix_users_stripe_customer_id'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    
    # Drop tables
    op.drop_table('users')