"""Add Layer 1 AI Agent tables

Revision ID: layer1_ai_agent_tables
Revises: 94bc03e7215f
Create Date: 2024-12-07

This migration adds tables for the Layer 1 AI Agent System:
- agent_decisions: Stores all agent decisions for auditing
- scraping_schedule: Dynamic scraping schedule per source
- urgency_classifications: Urgency classification for content
- quality_validations: Quality validation results
- agent_metrics: Agent performance metrics
- source_configs: Source configuration storage
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers
revision = 'layer1_ai_agent_tables'
down_revision = '94bc03e7215f_add_layer4_business_insights_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create agent_decisions table
    op.create_table(
        'agent_decisions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('agent_name', sa.String(100), nullable=False, index=True),
        sa.Column('decision_type', sa.String(50), nullable=False, index=True),
        sa.Column('input_data', JSONB, nullable=True),
        sa.Column('output_decision', JSONB, nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('llm_provider', sa.String(50), nullable=True),
        sa.Column('llm_model', sa.String(100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), default=0),
        sa.Column('latency_ms', sa.Integer(), default=0),
        sa.Column('cost_usd', sa.Float(), default=0.0),
        sa.Column('success', sa.Boolean(), default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True),
    )

    # Create scraping_schedule table
    op.create_table(
        'scraping_schedule',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('source_name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('frequency_minutes', sa.Integer(), default=60),
        sa.Column('priority_level', sa.String(20), default='medium'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_scraped', sa.DateTime(), nullable=True),
        sa.Column('last_articles_count', sa.Integer(), default=0),
        sa.Column('consecutive_failures', sa.Integer(), default=0),
        sa.Column('total_articles_scraped', sa.Integer(), default=0),
        sa.Column('avg_articles_per_scrape', sa.Float(), default=0.0),
        sa.Column('reliability_score', sa.Float(), default=1.0),
        sa.Column('updated_by', sa.String(50), default='system'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create urgency_classifications table
    op.create_table(
        'urgency_classifications',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('content_id', sa.String(100), nullable=False, index=True),
        sa.Column('content_type', sa.String(50), default='article'),
        sa.Column('urgency_level', sa.String(20), nullable=False, index=True),
        sa.Column('urgency_score', sa.Float(), default=0.5),
        sa.Column('factors', JSONB, nullable=True),
        sa.Column('keywords_matched', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('entities_found', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('recommended_action', sa.String(100), nullable=True),
        sa.Column('classified_by', sa.String(50), default='priority_agent'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True),
    )

    # Create quality_validations table
    op.create_table(
        'quality_validations',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('content_id', sa.String(100), nullable=False, index=True),
        sa.Column('validation_type', sa.String(50), nullable=False),
        sa.Column('is_valid', sa.Boolean(), default=True, index=True),
        sa.Column('quality_score', sa.Float(), default=0.0),
        sa.Column('issues_found', JSONB, nullable=True),
        sa.Column('corrections_made', JSONB, nullable=True),
        sa.Column('original_content', sa.Text(), nullable=True),
        sa.Column('corrected_content', sa.Text(), nullable=True),
        sa.Column('validator', sa.String(50), default='validation_agent'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True),
    )

    # Create agent_metrics table
    op.create_table(
        'agent_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('agent_name', sa.String(100), nullable=False, index=True),
        sa.Column('metric_date', sa.Date(), nullable=False, index=True),
        sa.Column('total_tasks', sa.Integer(), default=0),
        sa.Column('successful_tasks', sa.Integer(), default=0),
        sa.Column('failed_tasks', sa.Integer(), default=0),
        sa.Column('avg_processing_time_ms', sa.Float(), default=0.0),
        sa.Column('total_tokens_used', sa.Integer(), default=0),
        sa.Column('total_cost_usd', sa.Float(), default=0.0),
        sa.Column('error_breakdown', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('agent_name', 'metric_date', name='uq_agent_metrics_name_date'),
    )

    # Create source_configs table
    op.create_table(
        'source_configs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('source_name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('source_type', sa.String(50), default='news'),
        sa.Column('base_url', sa.String(500), nullable=False),
        sa.Column('scraper_class', sa.String(100), nullable=True),
        sa.Column('selectors', JSONB, nullable=True),
        sa.Column('rate_limit_requests', sa.Integer(), default=10),
        sa.Column('rate_limit_period', sa.Integer(), default=60),
        sa.Column('requires_javascript', sa.Boolean(), default=False),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('country', sa.String(10), default='LK'),
        sa.Column('categories', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('reliability_tier', sa.String(20), default='standard'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for better query performance
    op.create_index('ix_agent_decisions_agent_created', 'agent_decisions', ['agent_name', 'created_at'])
    op.create_index('ix_urgency_class_level_created', 'urgency_classifications', ['urgency_level', 'created_at'])
    op.create_index('ix_quality_valid_type_created', 'quality_validations', ['validation_type', 'created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_quality_valid_type_created', table_name='quality_validations')
    op.drop_index('ix_urgency_class_level_created', table_name='urgency_classifications')
    op.drop_index('ix_agent_decisions_agent_created', table_name='agent_decisions')
    
    # Drop tables
    op.drop_table('source_configs')
    op.drop_table('agent_metrics')
    op.drop_table('quality_validations')
    op.drop_table('urgency_classifications')
    op.drop_table('scraping_schedule')
    op.drop_table('agent_decisions')
