"""Add Layer 5 Dashboard tables

Revision ID: add_layer5_dashboard
Revises: add_source_reputation
Create Date: 2025-01-16

Layer 5 Dashboard Schema:
- l5_users: User accounts with authentication
- l5_dashboard_access_log: Analytics tracking
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_layer5_dashboard'
down_revision = 'add_source_reputation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_role enum type
    op.execute("CREATE TYPE user_role_enum AS ENUM ('admin', 'user')")
    
    # Create l5_users table
    op.create_table(
        'l5_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('role', sa.Enum('admin', 'user', name='user_role_enum', create_type=False), 
                  nullable=False, server_default='user'),
        sa.Column('company_id', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('refresh_token', sa.String(500), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['company_profiles.company_id'], ondelete='SET NULL'),
    )
    
    # Create indexes for l5_users
    op.create_index('ix_l5_users_email', 'l5_users', ['email'], unique=True)
    op.create_index('ix_l5_users_role', 'l5_users', ['role'])
    op.create_index('ix_l5_users_is_active', 'l5_users', ['is_active'])
    
    # Create l5_dashboard_access_log table
    op.create_table(
        'l5_dashboard_access_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(200), nullable=False),
        sa.Column('action', sa.String(50), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('query_params', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column('accessed_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['l5_users.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for l5_dashboard_access_log
    op.create_index('ix_l5_dashboard_access_log_user_id', 'l5_dashboard_access_log', ['user_id'])
    op.create_index('ix_l5_dashboard_access_log_accessed_at', 'l5_dashboard_access_log', ['accessed_at'])
    
    # Create default admin user (password: admin123 - CHANGE IN PRODUCTION!)
    # Hash is bcrypt with 12 rounds for 'admin123'
    op.execute("""
        INSERT INTO l5_users (email, password_hash, full_name, role, is_active, is_verified)
        VALUES (
            'admin@example.com',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4oaK0E0pN9cj0FWe',
            'System Admin',
            'admin',
            true,
            true
        )
    """)


def downgrade() -> None:
    # Drop tables
    op.drop_table('l5_dashboard_access_log')
    op.drop_table('l5_users')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS user_role_enum")
