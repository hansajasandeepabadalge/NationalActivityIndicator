"""add_ai_agent_tables

Revision ID: ai_agent_001
Revises: 
Create Date: 2025-12-07

Adds database tables for the AI Agent System:
- agent_decisions: Log all agent decisions
- scraping_schedule: Dynamic scraping frequencies
- urgency_classifications: Content urgency tracking
- quality_validations: Quality check results
- agent_metrics: Performance metrics
- source_configs: Source configuration
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ai_agent_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agent Decisions table
    op.create_table(
        'agent_decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('decision_type', sa.String(50), nullable=False),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_decision', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('llm_provider', sa.String(50), nullable=True),
        sa.Column('llm_model', sa.String(100), nullable=True),
        sa.Column('tokens_used', sa.Integer(), default=0),
        sa.Column('latency_ms', sa.Integer(), default=0),
        sa.Column('cost_usd', sa.Float(), default=0.0),
        sa.Column('success', sa.Boolean(), default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_decisions_agent_name', 'agent_decisions', ['agent_name'])
    op.create_index('ix_agent_decisions_decision_type', 'agent_decisions', ['decision_type'])
    op.create_index('ix_agent_decisions_created_at', 'agent_decisions', ['created_at'])

    # Scraping Schedule table
    op.create_table(
        'scraping_schedule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(100), nullable=False, unique=True),
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
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scraping_schedule_source_name', 'scraping_schedule', ['source_name'])

    # Urgency Classifications table
    op.create_table(
        'urgency_classifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.String(100), nullable=False),
        sa.Column('urgency_level', sa.String(20), nullable=False),
        sa.Column('urgency_score', sa.Float(), default=0.5),
        sa.Column('detected_signals', postgresql.ARRAY(sa.String()), default=[]),
        sa.Column('classification_reasoning', sa.Text(), nullable=True),
        sa.Column('processing_priority', sa.Integer(), default=100),
        sa.Column('fast_tracked', sa.Boolean(), default=False),
        sa.Column('notification_sent', sa.Boolean(), default=False),
        sa.Column('human_confirmed', sa.Boolean(), nullable=True),
        sa.Column('human_feedback', sa.Text(), nullable=True),
        sa.Column('classified_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_urgency_classifications_content_id', 'urgency_classifications', ['content_id'])
    op.create_index('ix_urgency_classifications_urgency_level', 'urgency_classifications', ['urgency_level'])
    op.create_index('ix_urgency_classifications_classified_at', 'urgency_classifications', ['classified_at'])

    # Quality Validations table
    op.create_table(
        'quality_validations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.String(100), nullable=False),
        sa.Column('is_valid', sa.Boolean(), default=True),
        sa.Column('quality_score', sa.Float(), default=0.0),
        sa.Column('validation_issues', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('auto_corrections', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('requires_review', sa.Boolean(), default=False),
        sa.Column('reviewed_by', sa.String(100), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('cross_validated', sa.Boolean(), default=False),
        sa.Column('matching_sources', sa.Integer(), default=0),
        sa.Column('validated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_quality_validations_content_id', 'quality_validations', ['content_id'])
    op.create_index('ix_quality_validations_validated_at', 'quality_validations', ['validated_at'])

    # Agent Metrics table
    op.create_table(
        'agent_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('decisions_made', sa.Integer(), default=0),
        sa.Column('successful_decisions', sa.Integer(), default=0),
        sa.Column('failed_decisions', sa.Integer(), default=0),
        sa.Column('avg_latency_ms', sa.Integer(), default=0),
        sa.Column('max_latency_ms', sa.Integer(), default=0),
        sa.Column('total_tokens_used', sa.Integer(), default=0),
        sa.Column('cost_usd', sa.Float(), default=0.0),
        sa.Column('groq_requests', sa.Integer(), default=0),
        sa.Column('together_requests', sa.Integer(), default=0),
        sa.Column('openai_requests', sa.Integer(), default=0),
        sa.Column('accuracy_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_metrics_agent_name', 'agent_metrics', ['agent_name'])
    op.create_index('ix_agent_metrics_date', 'agent_metrics', ['date'])

    # Source Configs table
    op.create_table(
        'source_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('display_name', sa.String(200), nullable=True),
        sa.Column('base_url', sa.String(500), nullable=False),
        sa.Column('source_type', sa.String(50), default='news'),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('priority_level', sa.String(20), default='medium'),
        sa.Column('scraper_class', sa.String(100), nullable=True),
        sa.Column('scraper_config', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('default_frequency_minutes', sa.Integer(), default=60),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('requires_auth', sa.Boolean(), default=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_source_configs_name', 'source_configs', ['name'])

    # Insert initial source configuration for Ada Derana
    op.execute("""
        INSERT INTO source_configs (name, display_name, base_url, source_type, language, category, priority_level, scraper_class, default_frequency_minutes)
        VALUES ('ada_derana', 'Ada Derana', 'https://www.adaderana.lk', 'news', 'en', 'general', 'high', 'AdaDeranaScraper', 15)
        ON CONFLICT (name) DO NOTHING;
    """)
    
    # Insert initial scraping schedule for Ada Derana
    op.execute("""
        INSERT INTO scraping_schedule (source_name, source_url, frequency_minutes, priority_level, is_active)
        VALUES ('ada_derana', 'https://www.adaderana.lk', 15, 'high', true)
        ON CONFLICT (source_name) DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_table('source_configs')
    op.drop_table('agent_metrics')
    op.drop_table('quality_validations')
    op.drop_table('urgency_classifications')
    op.drop_table('scraping_schedule')
    op.drop_table('agent_decisions')
