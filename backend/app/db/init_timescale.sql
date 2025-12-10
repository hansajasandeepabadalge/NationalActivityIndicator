-- TimescaleDB Initialization Script
-- This runs automatically on first container startup

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create custom functions for performance
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create enum types
CREATE TYPE pestel_category_enum AS ENUM (
    'Political', 'Economic', 'Social',
    'Technological', 'Environmental', 'Legal'
);

CREATE TYPE calculation_type_enum AS ENUM (
    'frequency_count', 'sentiment_aggregate', 'numeric_extraction',
    'composite', 'ratio', 'weighted_average'
);

CREATE TYPE event_type_enum AS ENUM (
    'threshold_breach', 'anomaly_detected', 'rapid_change',
    'correlation_break', 'data_quality_issue'
);

CREATE TYPE trend_direction_enum AS ENUM (
    'rising', 'falling', 'stable', 'volatile'
);

-- Performance optimization settings
ALTER DATABASE national_indicator SET timezone TO 'UTC';
ALTER DATABASE national_indicator SET log_statement TO 'none';
ALTER DATABASE national_indicator SET log_min_duration_statement TO 1000;

-- Create extension for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

COMMENT ON DATABASE national_indicator IS 'National Activity Indicator System - Layer 2 Database';
