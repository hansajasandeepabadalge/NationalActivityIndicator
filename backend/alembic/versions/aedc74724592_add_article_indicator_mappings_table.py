"""add article indicator mappings table

Revision ID: aedc74724592
Revises: 001
Create Date: 2025-12-02 17:31:50.467568

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'aedc74724592'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create article_indicator_mappings table
    op.create_table(
        'article_indicator_mappings',
        sa.Column('mapping_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('article_id', sa.String(100), nullable=False, index=True),
        sa.Column('indicator_id', sa.String(50), sa.ForeignKey('indicator_definitions.indicator_id', ondelete='CASCADE'), nullable=False),
        sa.Column('match_confidence', sa.Float(), nullable=False),
        sa.Column('classification_method', sa.String(50), default='rule_based'),
        sa.Column('matched_keywords', postgresql.ARRAY(sa.String(200))),
        sa.Column('keyword_match_count', sa.Integer(), default=0),
        sa.Column('article_category', sa.String(50)),
        sa.Column('article_published_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('extra_metadata', postgresql.JSONB)
    )

    # Create indexes for performance
    op.create_index('idx_article_mappings_article', 'article_indicator_mappings', ['article_id'])
    op.create_index('idx_article_mappings_indicator', 'article_indicator_mappings', ['indicator_id'])
    op.create_index('idx_article_mappings_confidence', 'article_indicator_mappings', ['match_confidence'])
    op.create_index('idx_article_mappings_method', 'article_indicator_mappings', ['classification_method'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_article_mappings_method', 'article_indicator_mappings')
    op.drop_index('idx_article_mappings_confidence', 'article_indicator_mappings')
    op.drop_index('idx_article_mappings_indicator', 'article_indicator_mappings')
    op.drop_index('idx_article_mappings_article', 'article_indicator_mappings')

    # Drop table
    op.drop_table('article_indicator_mappings')
