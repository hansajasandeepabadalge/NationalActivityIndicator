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
    # Create user_role enum type (if not exists)
    op.execute("DO $$ BEGIN CREATE TYPE user_role_enum AS ENUM ('admin', 'user'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Create l5_users table using raw SQL to avoid SQLAlchemy enum issues
    op.execute("""
        CREATE TABLE IF NOT EXISTS l5_users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(200),
            role user_role_enum NOT NULL DEFAULT 'user',
            company_id VARCHAR(50) REFERENCES company_profiles(company_id) ON DELETE SET NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_verified BOOLEAN NOT NULL DEFAULT false,
            refresh_token VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_login_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Create indexes for l5_users
    op.execute("CREATE INDEX IF NOT EXISTS ix_l5_users_email ON l5_users(email)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_l5_users_role ON l5_users(role)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_l5_users_is_active ON l5_users(is_active)")
    
    # Create l5_dashboard_access_log table
    op.execute("""
        CREATE TABLE IF NOT EXISTS l5_dashboard_access_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES l5_users(id) ON DELETE CASCADE,
            endpoint VARCHAR(200) NOT NULL,
            action VARCHAR(50),
            resource_type VARCHAR(50),
            resource_id VARCHAR(100),
            ip_address VARCHAR(50),
            user_agent TEXT,
            query_params JSONB,
            accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Create indexes for l5_dashboard_access_log
    op.execute("CREATE INDEX IF NOT EXISTS ix_l5_dashboard_access_log_user_id ON l5_dashboard_access_log(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_l5_dashboard_access_log_accessed_at ON l5_dashboard_access_log(accessed_at)")
    
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
        ON CONFLICT (email) DO NOTHING
    """)


def downgrade() -> None:
    # Drop tables
    op.drop_table('l5_dashboard_access_log')
    op.drop_table('l5_users')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS user_role_enum")
