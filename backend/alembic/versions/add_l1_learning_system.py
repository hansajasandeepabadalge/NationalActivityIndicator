"""Add Layer 1 Adaptive Learning System tables

Revision ID: add_l1_learning_system
Revises: add_layer5_dashboard
Create Date: 2024-01-15

Tables created:
- l1_learning_metrics: Stores performance metrics for sources, scrapers, validators
- l1_feedback_signals: Stores downstream feedback signals
- l1_performance_profiles: Stores learned performance profiles
- l1_quality_issues: Stores detected quality issues
- l1_quality_patterns: Stores recurring quality patterns
- l1_tuning_history: Stores parameter adjustment history
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'add_l1_learning_system'
down_revision = 'add_layer5_dashboard'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # Learning Metrics Table
    # ==========================================================================
    op.create_table(
        'l1_learning_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.String(255), nullable=False),  # source_id, scraper_type, etc.
        sa.Column('entity_type', sa.String(50), nullable=False),  # source, scraper, validator
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('sample_count', sa.Integer(), default=1),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(
        'ix_l1_learning_metrics_entity',
        'l1_learning_metrics',
        ['entity_id', 'entity_type', 'recorded_at']
    )
    op.create_index(
        'ix_l1_learning_metrics_type',
        'l1_learning_metrics',
        ['metric_type', 'recorded_at']
    )
    
    # ==========================================================================
    # Feedback Signals Table
    # ==========================================================================
    op.create_table(
        'l1_feedback_signals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('article_id', sa.String(255), nullable=True),
        sa.Column('source_id', sa.String(255), nullable=True),
        sa.Column('feedback_type', sa.String(50), nullable=False),
        sa.Column('quality_rating', sa.Float(), nullable=True),
        sa.Column('downstream_layer', sa.String(50), nullable=True),  # L2, L3, L4, L5
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.Column('applied_to_reputation', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(
        'ix_l1_feedback_source',
        'l1_feedback_signals',
        ['source_id', 'created_at']
    )
    op.create_index(
        'ix_l1_feedback_unprocessed',
        'l1_feedback_signals',
        ['processed', 'created_at'],
        postgresql_where=sa.text('processed = false')
    )
    
    # ==========================================================================
    # Performance Profiles Table
    # ==========================================================================
    op.create_table(
        'l1_performance_profiles',
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        
        # Timing metrics
        sa.Column('avg_response_time_ms', sa.Float(), default=0.0),
        sa.Column('p95_response_time_ms', sa.Float(), default=0.0),
        sa.Column('p99_response_time_ms', sa.Float(), default=0.0),
        
        # Success metrics
        sa.Column('success_rate', sa.Float(), default=1.0),
        sa.Column('retry_success_rate', sa.Float(), default=0.0),
        
        # Failure rates
        sa.Column('timeout_rate', sa.Float(), default=0.0),
        sa.Column('rate_limit_rate', sa.Float(), default=0.0),
        sa.Column('server_error_rate', sa.Float(), default=0.0),
        
        # Learned optimal settings
        sa.Column('optimal_timeout_ms', sa.Integer(), default=30000),
        sa.Column('optimal_retry_count', sa.Integer(), default=3),
        sa.Column('optimal_concurrency', sa.Integer(), default=5),
        sa.Column('optimal_batch_size', sa.Integer(), default=10),
        
        # Timing patterns (JSON array of best/worst hours)
        sa.Column('timing_patterns', postgresql.JSONB(), nullable=True),
        
        sa.Column('sample_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), 
                  onupdate=sa.func.now(), nullable=False),
        
        sa.PrimaryKeyConstraint('entity_id')
    )
    
    # ==========================================================================
    # Quality Issues Table
    # ==========================================================================
    op.create_table(
        'l1_quality_issues',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('issue_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('source_id', sa.String(255), nullable=True),
        sa.Column('article_id', sa.String(255), nullable=True),
        sa.Column('field_name', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('raw_value', sa.Text(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('resolved', sa.Boolean(), default=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(
        'ix_l1_quality_issues_source',
        'l1_quality_issues',
        ['source_id', 'detected_at']
    )
    op.create_index(
        'ix_l1_quality_issues_type',
        'l1_quality_issues',
        ['issue_type', 'severity', 'detected_at']
    )
    op.create_index(
        'ix_l1_quality_issues_unresolved',
        'l1_quality_issues',
        ['resolved', 'severity'],
        postgresql_where=sa.text('resolved = false')
    )
    
    # ==========================================================================
    # Quality Patterns Table
    # ==========================================================================
    op.create_table(
        'l1_quality_patterns',
        sa.Column('pattern_id', sa.String(255), nullable=False),
        sa.Column('issue_types', postgresql.JSONB(), nullable=False),  # Array of issue types
        sa.Column('affected_sources', postgresql.JSONB(), nullable=False),  # Array of source IDs
        sa.Column('affected_fields', postgresql.JSONB(), nullable=True),
        sa.Column('occurrence_count', sa.Integer(), default=0),
        sa.Column('first_seen', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.Column('suggested_fix', sa.Text(), nullable=True),
        sa.Column('auto_fixable', sa.Boolean(), default=False),
        sa.Column('priority_score', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(),
                  onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('pattern_id')
    )
    
    op.create_index(
        'ix_l1_quality_patterns_priority',
        'l1_quality_patterns',
        ['priority_score', 'last_seen'],
        postgresql_ops={'priority_score': 'DESC'}
    )
    
    # ==========================================================================
    # Tuning History Table (for rollback capability)
    # ==========================================================================
    op.create_table(
        'l1_tuning_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('parameter_name', sa.String(100), nullable=False),
        sa.Column('old_value', sa.Float(), nullable=True),
        sa.Column('new_value', sa.Float(), nullable=False),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('change_type', sa.String(50), nullable=False),  # auto, manual, rollback
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('applied', sa.Boolean(), default=True),
        sa.Column('rolled_back', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('rolled_back_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index(
        'ix_l1_tuning_history_entity',
        'l1_tuning_history',
        ['entity_id', 'created_at']
    )
    op.create_index(
        'ix_l1_tuning_history_rollback',
        'l1_tuning_history',
        ['applied', 'rolled_back'],
        postgresql_where=sa.text('applied = true AND rolled_back = false')
    )
    
    # ==========================================================================
    # Aggregated Metrics View (for dashboard queries)
    # ==========================================================================
    op.execute("""
        CREATE OR REPLACE VIEW l1_learning_dashboard AS
        SELECT 
            DATE_TRUNC('hour', recorded_at) as time_bucket,
            entity_type,
            COUNT(*) as metric_count,
            AVG(metric_value) as avg_value,
            MIN(metric_value) as min_value,
            MAX(metric_value) as max_value
        FROM l1_learning_metrics
        WHERE recorded_at > NOW() - INTERVAL '7 days'
        GROUP BY DATE_TRUNC('hour', recorded_at), entity_type
        ORDER BY time_bucket DESC
    """)


def downgrade() -> None:
    # Drop view first
    op.execute("DROP VIEW IF EXISTS l1_learning_dashboard")
    
    # Drop tables in reverse order
    op.drop_table('l1_tuning_history')
    op.drop_table('l1_quality_patterns')
    op.drop_table('l1_quality_issues')
    op.drop_table('l1_performance_profiles')
    op.drop_table('l1_feedback_signals')
    op.drop_table('l1_learning_metrics')
