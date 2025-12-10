"""Add selectors column to source_configs

Revision ID: add_selectors_column
Revises: layer1_ai_agent_tables
Create Date: 2025-12-09

This migration adds the 'selectors' JSONB column to source_configs table
to enable the Universal Configurable Scraper functionality.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'add_selectors_column'
down_revision = 'layer1_ai_agent_tables'  # Adjust if different
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add selectors and rate limiting columns to source_configs."""
    
    # Add selectors column for CSS selectors
    op.add_column(
        'source_configs',
        sa.Column('selectors', JSONB, nullable=True)
    )
    
    # Add rate limiting columns (if not already present)
    try:
        op.add_column(
            'source_configs',
            sa.Column('rate_limit_requests', sa.Integer(), default=10, nullable=True)
        )
    except Exception:
        pass  # Column may already exist from initial migration
    
    try:
        op.add_column(
            'source_configs',
            sa.Column('rate_limit_period', sa.Integer(), default=60, nullable=True)
        )
    except Exception:
        pass
    
    try:
        op.add_column(
            'source_configs',
            sa.Column('requires_javascript', sa.Boolean(), default=False, nullable=True)
        )
    except Exception:
        pass
    
    # Add display_name column if not present
    try:
        op.add_column(
            'source_configs',
            sa.Column('display_name', sa.String(200), nullable=True)
        )
    except Exception:
        pass


def downgrade() -> None:
    """Remove selectors column."""
    op.drop_column('source_configs', 'selectors')
    op.drop_column('source_configs', 'rate_limit_requests')
    op.drop_column('source_configs', 'rate_limit_period')
    op.drop_column('source_configs', 'requires_javascript')
    op.drop_column('source_configs', 'display_name')
