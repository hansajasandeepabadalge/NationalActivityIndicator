"""Initial Layer 2 schema with TimescaleDB hypertables

Revision ID: 001
Revises:
Create Date: 2025-12-01

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create update_updated_at_column function for triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create ENUM types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE pestel_category_enum AS ENUM (
                'Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE calculation_type_enum AS ENUM (
                'frequency_count', 'sentiment_aggregate', 'numeric_extraction',
                'composite', 'ratio', 'weighted_average'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE event_type_enum AS ENUM (
                'threshold_breach', 'anomaly_detected', 'rapid_change',
                'correlation_break', 'data_quality_issue'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE trend_direction_enum AS ENUM (
                'rising', 'falling', 'stable', 'volatile'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create indicator_definitions table
    op.create_table(
        'indicator_definitions',
        sa.Column('indicator_id', sa.String(50), primary_key=True),
        sa.Column('indicator_name', sa.String(200), nullable=False),
        sa.Column('pestel_category', postgresql.ENUM(
            'Political', 'Economic', 'Social', 'Technological', 'Environmental', 'Legal',
            name='pestel_category_enum', create_type=False
        ), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('calculation_type', postgresql.ENUM(
            'frequency_count', 'sentiment_aggregate', 'numeric_extraction',
            'composite', 'ratio', 'weighted_average',
            name='calculation_type_enum', create_type=False
        ), nullable=False),
        sa.Column('base_weight', sa.Float, default=1.0),
        sa.Column('aggregation_window', sa.String(20), default='1 day'),
        sa.Column('threshold_high', sa.Float, nullable=True),
        sa.Column('threshold_low', sa.Float, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )

    # Create indicator_keywords table
    op.create_table(
        'indicator_keywords',
        sa.Column('keyword_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('indicator_id', sa.String(50), nullable=False),
        sa.Column('keyword_text', sa.String(200), nullable=False),
        sa.Column('keyword_type', sa.String(50), default='exact_match'),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['indicator_id'], ['indicator_definitions.indicator_id'], ondelete='CASCADE')
    )

    # Create indicator_values table (will be converted to hypertable)
    op.create_table(
        'indicator_values',
        sa.Column('indicator_id', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('raw_count', sa.Integer, default=0),
        sa.Column('sentiment_score', sa.Float, nullable=True),
        sa.Column('confidence', sa.Float, default=1.0),
        sa.Column('source_count', sa.Integer, default=1),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.PrimaryKeyConstraint('indicator_id', 'timestamp'),
        sa.ForeignKeyConstraint(['indicator_id'], ['indicator_definitions.indicator_id'], ondelete='CASCADE')
    )

    # Convert indicator_values to TimescaleDB hypertable
    op.execute("""
        SELECT create_hypertable(
            'indicator_values',
            'timestamp',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        );
    """)

    # Create indicator_events table (will be converted to hypertable)
    op.create_table(
        'indicator_events',
        sa.Column('event_id', sa.Integer, autoincrement=True),
        sa.Column('indicator_id', sa.String(50), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('event_id', 'timestamp'),
        sa.Column('event_type', postgresql.ENUM(
            'threshold_breach', 'anomaly_detected', 'rapid_change',
            'correlation_break', 'data_quality_issue',
            name='event_type_enum', create_type=False
        ), nullable=False),
        sa.Column('severity', sa.String(20), default='medium'),
        sa.Column('value_before', sa.Float, nullable=True),
        sa.Column('value_after', sa.Float, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('acknowledged', sa.Boolean, default=False),
        sa.Column('acknowledged_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['indicator_id'], ['indicator_definitions.indicator_id'], ondelete='CASCADE')
    )

    # Convert indicator_events to TimescaleDB hypertable
    op.execute("""
        SELECT create_hypertable(
            'indicator_events',
            'timestamp',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        );
    """)

    # Create indicator_correlations table
    op.create_table(
        'indicator_correlations',
        sa.Column('correlation_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('indicator_id_1', sa.String(50), nullable=False),
        sa.Column('indicator_id_2', sa.String(50), nullable=False),
        sa.Column('correlation_coefficient', sa.Float, nullable=False),
        sa.Column('p_value', sa.Float, nullable=True),
        sa.Column('lag_days', sa.Integer, default=0),
        sa.Column('calculation_date', sa.Date, nullable=False),
        sa.Column('sample_size', sa.Integer, nullable=False),
        sa.Column('confidence_interval', postgresql.JSONB, nullable=True),
        sa.Column('is_significant', sa.Boolean, default=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['indicator_id_1'], ['indicator_definitions.indicator_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['indicator_id_2'], ['indicator_definitions.indicator_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('indicator_id_1', 'indicator_id_2', 'calculation_date', 'lag_days')
    )

    # Create ml_classification_results table
    op.create_table(
        'ml_classification_results',
        sa.Column('result_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('article_id', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('predicted_indicators', postgresql.ARRAY(sa.String(50)), nullable=False),
        sa.Column('confidence_scores', postgresql.JSONB, nullable=False),
        sa.Column('classification_method', sa.String(50), default='hybrid'),
        sa.Column('processing_time_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )

    # Create trend_analysis table
    op.create_table(
        'trend_analysis',
        sa.Column('analysis_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('indicator_id', sa.String(50), nullable=False),
        sa.Column('analysis_date', sa.Date, nullable=False),
        sa.Column('window_days', sa.Integer, default=30),
        sa.Column('trend_direction', postgresql.ENUM(
            'rising', 'falling', 'stable', 'volatile',
            name='trend_direction_enum', create_type=False
        ), nullable=False),
        sa.Column('slope', sa.Float, nullable=True),
        sa.Column('r_squared', sa.Float, nullable=True),
        sa.Column('volatility', sa.Float, nullable=True),
        sa.Column('change_percentage', sa.Float, nullable=True),
        sa.Column('forecast_7d', sa.Float, nullable=True),
        sa.Column('forecast_30d', sa.Float, nullable=True),
        sa.Column('confidence', sa.Float, default=0.5),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.ForeignKeyConstraint(['indicator_id'], ['indicator_definitions.indicator_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('indicator_id', 'analysis_date', 'window_days')
    )

    # Create indexes for performance

    # Indicator definitions indexes
    op.create_index('idx_indicator_pestel', 'indicator_definitions', ['pestel_category'])
    op.create_index('idx_indicator_active', 'indicator_definitions', ['is_active'])

    # Indicator keywords indexes
    op.create_index('idx_keywords_indicator', 'indicator_keywords', ['indicator_id'])
    op.create_index('idx_keywords_text', 'indicator_keywords', ['keyword_text'])
    op.create_index('idx_keywords_active', 'indicator_keywords', ['is_active'])
    op.execute("CREATE INDEX idx_keywords_text_gin ON indicator_keywords USING gin(keyword_text gin_trgm_ops);")

    # Indicator values indexes
    op.create_index('idx_values_indicator_time', 'indicator_values', ['indicator_id', 'timestamp'])
    op.create_index('idx_values_timestamp', 'indicator_values', ['timestamp'])

    # Indicator events indexes
    op.create_index('idx_events_indicator_time', 'indicator_events', ['indicator_id', 'timestamp'])
    op.create_index('idx_events_type', 'indicator_events', ['event_type'])
    op.create_index('idx_events_severity', 'indicator_events', ['severity'])
    op.create_index('idx_events_acknowledged', 'indicator_events', ['acknowledged'])

    # Correlation indexes
    op.create_index('idx_correlation_indicators', 'indicator_correlations', ['indicator_id_1', 'indicator_id_2'])
    op.create_index('idx_correlation_date', 'indicator_correlations', ['calculation_date'])
    op.create_index('idx_correlation_significant', 'indicator_correlations', ['is_significant'])

    # ML results indexes
    op.create_index('idx_ml_article', 'ml_classification_results', ['article_id'])
    op.create_index('idx_ml_model', 'ml_classification_results', ['model_version'])
    op.create_index('idx_ml_created', 'ml_classification_results', ['created_at'])
    op.execute("CREATE INDEX idx_ml_indicators_gin ON ml_classification_results USING gin(predicted_indicators);")

    # Trend analysis indexes
    op.create_index('idx_trend_indicator_date', 'trend_analysis', ['indicator_id', 'analysis_date'])
    op.create_index('idx_trend_direction', 'trend_analysis', ['trend_direction'])

    # Create triggers for updated_at
    op.execute("""
        CREATE TRIGGER update_indicator_definitions_updated_at
        BEFORE UPDATE ON indicator_definitions
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)

    # Enable continuous aggregates for performance (TimescaleDB feature)
    op.execute("""
        CREATE MATERIALIZED VIEW indicator_hourly_agg
        WITH (timescaledb.continuous) AS
        SELECT
            indicator_id,
            time_bucket('1 hour', timestamp) AS bucket,
            AVG(value) AS avg_value,
            MAX(value) AS max_value,
            MIN(value) AS min_value,
            COUNT(*) AS count,
            STDDEV(value) AS stddev_value
        FROM indicator_values
        GROUP BY indicator_id, bucket
        WITH NO DATA;
    """)

    # Add refresh policy for continuous aggregate
    op.execute("""
        SELECT add_continuous_aggregate_policy('indicator_hourly_agg',
            start_offset => INTERVAL '3 hours',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '1 hour');
    """)


def downgrade() -> None:
    # Drop continuous aggregate policy and view
    op.execute("SELECT remove_continuous_aggregate_policy('indicator_hourly_agg', if_exists => true);")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS indicator_hourly_agg;")

    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_indicator_definitions_updated_at ON indicator_definitions;")

    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_trend_direction;")
    op.execute("DROP INDEX IF EXISTS idx_trend_indicator_date;")
    op.execute("DROP INDEX IF EXISTS idx_ml_indicators_gin;")
    op.execute("DROP INDEX IF EXISTS idx_ml_created;")
    op.execute("DROP INDEX IF EXISTS idx_ml_model;")
    op.execute("DROP INDEX IF EXISTS idx_ml_article;")
    op.execute("DROP INDEX IF EXISTS idx_correlation_significant;")
    op.execute("DROP INDEX IF EXISTS idx_correlation_date;")
    op.execute("DROP INDEX IF EXISTS idx_correlation_indicators;")
    op.execute("DROP INDEX IF EXISTS idx_events_acknowledged;")
    op.execute("DROP INDEX IF EXISTS idx_events_severity;")
    op.execute("DROP INDEX IF EXISTS idx_events_type;")
    op.execute("DROP INDEX IF EXISTS idx_events_indicator_time;")
    op.execute("DROP INDEX IF EXISTS idx_values_timestamp;")
    op.execute("DROP INDEX IF EXISTS idx_values_indicator_time;")
    op.execute("DROP INDEX IF EXISTS idx_keywords_text_gin;")
    op.execute("DROP INDEX IF EXISTS idx_keywords_active;")
    op.execute("DROP INDEX IF EXISTS idx_keywords_text;")
    op.execute("DROP INDEX IF EXISTS idx_keywords_indicator;")
    op.execute("DROP INDEX IF EXISTS idx_indicator_active;")
    op.execute("DROP INDEX IF EXISTS idx_indicator_pestel;")

    # Drop tables
    op.drop_table('trend_analysis')
    op.drop_table('ml_classification_results')
    op.drop_table('indicator_correlations')
    op.drop_table('indicator_events')
    op.drop_table('indicator_values')
    op.drop_table('indicator_keywords')
    op.drop_table('indicator_definitions')

    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS pestel_category_enum CASCADE;")
    op.execute("DROP TYPE IF EXISTS calculation_type_enum CASCADE;")
    op.execute("DROP TYPE IF EXISTS event_type_enum CASCADE;")
    op.execute("DROP TYPE IF EXISTS trend_direction_enum CASCADE;")
