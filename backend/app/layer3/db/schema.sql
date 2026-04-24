-- Layer 3 Database Schema Setup
-- Run this to create all necessary tables for Layer 3

-- ============================================================================
-- COMPANY PROFILES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_profiles (
    company_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    industry_id VARCHAR(50),
    sub_industry VARCHAR(100),
    
    -- Business characteristics
    business_scale JSONB,
    /* Structure:
    {
        "size": "large",
        "employees": 450,
        "annual_revenue_lkr": 5000000000,
        "locations_count": 8
    }
    */
    
    -- Operational profile
    supply_chain_config JSONB,
    /* Structure:
    {
        "import_dependency": 0.60,
        "local_sourcing": 0.40,
        "critical_suppliers": [...]
    }
    */
    
    critical_dependencies JSONB,
    /* Structure:
    {
        "fuel": "high",
        "power": "high",
        "internet": "medium",
        "transport_access": "high"
    }
    */
    
    customer_profile JSONB,
    risk_profile JSONB,
    
    -- Custom settings
    custom_weights JSONB,
    alert_thresholds JSONB,
    /* Structure:
    {
        "supply_chain_risk": {"high": 70, "critical": 85},
        "foot_traffic_impact": {"high": -25, "critical": -40}
    }
    */
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_company_industry ON company_profiles(industry_id);
CREATE INDEX idx_company_active ON company_profiles(is_active);

-- ============================================================================
-- COMPANY LOCATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS company_locations (
    location_id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES company_profiles(company_id) ON DELETE CASCADE,
    
    -- Location details
    location_name VARCHAR(200) NOT NULL,
    location_type VARCHAR(50),  -- 'headquarters', 'branch', 'warehouse', 'factory'
    
    -- Geographic data
    city VARCHAR(100),
    district VARCHAR(100),
    province VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Location characteristics
    size_category VARCHAR(50),  -- 'flagship', 'standard', 'small'
    daily_capacity INTEGER,
    employee_count INTEGER,
    
    -- Operational settings
    operating_hours JSONB,
    critical_services TEXT[],
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_location_company ON company_locations(company_id);
CREATE INDEX idx_location_geography ON company_locations(province, district, city);
CREATE INDEX idx_location_coords ON company_locations(latitude, longitude);

-- ============================================================================
-- OPERATIONAL INDICATOR VALUES (TimescaleDB Hypertable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS operational_indicator_values (
    company_id VARCHAR(50) NOT NULL,
    indicator_code VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    value DECIMAL(10,2),
    confidence DECIMAL(5,4),
    
    -- Additional metadata
    calculation_method VARCHAR(50),
    source_indicators TEXT[],
    metadata JSONB,
    
    PRIMARY KEY (company_id, indicator_code, timestamp)
);

-- Convert to TimescaleDB hypertable (if TimescaleDB extension is available)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
    ) THEN
        PERFORM create_hypertable(
            'operational_indicator_values',
            'timestamp',
            if_not_exists => TRUE,
            migrate_data => TRUE
        );
    END IF;
END $$;

CREATE INDEX idx_operational_company_time ON operational_indicator_values(company_id, timestamp DESC);
CREATE INDEX idx_operational_indicator ON operational_indicator_values(indicator_code, timestamp DESC);

-- ============================================================================
-- INDUSTRY TEMPLATES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS industry_templates (
    industry_id VARCHAR(50) PRIMARY KEY,
    industry_name VARCHAR(200) NOT NULL,
    display_name VARCHAR(200),
    parent_industry VARCHAR(50),
    
    -- Sensitivity configuration
    sensitivity_config JSONB NOT NULL,
    /* Structure:
    {
        "national_indicators": {
            "indicator_code": {
                "relevance": 0.95,
                "impact_multiplier": 1.5
            }
        },
        "operational_priorities": [...]
    }
    */
    
    -- Impact lag configuration
    impact_lags JSONB,
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- ============================================================================
-- SAMPLE DATA: Industry Templates
-- ============================================================================

INSERT INTO industry_templates (industry_id, industry_name, display_name, sensitivity_config, impact_lags)
VALUES 
(
    'retail',
    'Retail & Consumer Goods',
    'Retail',
    '{
        "national_indicators": {
            "ECON_CONSUMER_CONF": {"relevance": 0.95, "impact_multiplier": 1.4},
            "ECON_INFLATION_PRESSURE": {"relevance": 0.90, "impact_multiplier": 1.3},
            "ENV_WEATHER_SEV": {"relevance": 0.80, "impact_multiplier": 1.2},
            "POL_UNREST_01": {"relevance": 0.90, "impact_multiplier": 1.5}
        },
        "operational_priorities": [
            {"name": "Expected Foot Traffic", "weight": 0.35},
            {"name": "Supply Chain Integrity", "weight": 0.25},
            {"name": "Consumer Purchasing Power", "weight": 0.20}
        ]
    }',
    '{"weather_change": 2, "transport_disruption": 6, "consumer_sentiment_shift": 48}'
),
(
    'logistics',
    'Logistics & Transportation',
    'Logistics',
    '{
        "national_indicators": {
            "ECON_FUEL_AVAIL": {"relevance": 1.00, "impact_multiplier": 2.0},
            "ECON_FUEL_PRICES": {"relevance": 0.95, "impact_multiplier": 1.8},
            "ENV_WEATHER_SEV": {"relevance": 0.90, "impact_multiplier": 1.5},
            "ENV_ROAD_STATUS": {"relevance": 0.95, "impact_multiplier": 1.6},
            "POL_UNREST_01": {"relevance": 0.90, "impact_multiplier": 1.5}
        },
        "operational_priorities": [
            {"name": "Fleet Availability", "weight": 0.30},
            {"name": "Route Viability", "weight": 0.30},
            {"name": "Operating Cost", "weight": 0.25}
        ]
    }',
    '{"fuel_shortage": 12, "weather_alert": 6, "road_closure": 2}'
),
(
    'manufacturing',
    'Manufacturing',
    'Manufacturing',
    '{
        "national_indicators": {
            "ECON_CURRENCY_STAB": {"relevance": 0.95, "impact_multiplier": 1.5},
            "ECON_INFLATION_PRESSURE": {"relevance": 0.85, "impact_multiplier": 1.2},
            "ENV_POWER_RELIABILITY": {"relevance": 0.95, "impact_multiplier": 1.6},
            "POL_STRIKE_ACTIVITY": {"relevance": 0.80, "impact_multiplier": 1.3}
        },
        "operational_priorities": [
            {"name": "Raw Material Availability", "weight": 0.30},
            {"name": "Energy Supply Reliability", "weight": 0.25},
            {"name": "Workforce Availability", "weight": 0.20}
        ]
    }',
    '{"currency_change": 24, "strike_announcement": 48, "power_outage": 0}'
)
ON CONFLICT (industry_id) DO NOTHING;

-- ============================================================================
-- SAMPLE DATA: Test Company Profiles
-- ============================================================================

INSERT INTO company_profiles (
    company_id,
    company_name,
    industry_id,
    sub_industry,
    business_scale,
    supply_chain_config,
    critical_dependencies,
    alert_thresholds,
    is_active
)
VALUES 
(
    'test_retail_001',
    'ABC Supermarkets (Test)',
    'retail',
    'grocery_supermarkets',
    '{"size": "large", "employees": 450, "annual_revenue_lkr": 5000000000, "locations_count": 8}',
    '{"import_dependency": 0.60, "local_sourcing": 0.40}',
    '{"fuel": "high", "power": "high", "internet": "medium", "transport_access": "high", "labor": "high"}',
    '{"supply_chain_risk": {"high": 70, "critical": 85}, "foot_traffic_impact": {"high": -25, "critical": -40}}',
    TRUE
),
(
    'test_logistics_001',
    'XYZ Logistics (Test)',
    'logistics',
    'freight_cargo',
    '{"size": "medium", "employees": 150, "fleet_size": 45}',
    '{"import_dependency": 0.30, "local_sourcing": 0.70}',
    '{"fuel": "critical", "road_access": "critical", "port_operations": "high"}',
    '{"fleet_availability": {"high": 70, "critical": 50}, "fuel_cost": {"high": 30, "critical": 50}}',
    TRUE
),
(
    'test_manufacturing_001',
    'DEF Manufacturing (Test)',
    'manufacturing',
    'food_beverage',
    '{"size": "large", "employees": 600, "production_capacity": 10000}',
    '{"import_dependency": 0.75, "local_sourcing": 0.25}',
    '{"fuel": "high", "power": "critical", "raw_materials": "critical", "labor": "high"}',
    '{"production_capacity": {"high": 70, "critical": 50}, "cost_pressure": {"high": 30, "critical": 50}}',
    TRUE
)
ON CONFLICT (company_id) DO NOTHING;

-- ============================================================================
-- SAMPLE DATA: Company Locations
-- ============================================================================

INSERT INTO company_locations (
    location_id,
    company_id,
    location_name,
    location_type,
    city,
    district,
    province,
    latitude,
    longitude,
    size_category,
    daily_capacity,
    employee_count,
    is_active
)
VALUES 
(
    'loc_retail_col_001',
    'test_retail_001',
    'Colombo Main Branch',
    'flagship',
    'Colombo',
    'Colombo',
    'Western',
    6.9271,
    79.8612,
    'flagship',
    2500,
    80,
    TRUE
),
(
    'loc_retail_kan_001',
    'test_retail_001',
    'Kandy Branch',
    'branch',
    'Kandy',
    'Kandy',
    'Central',
    7.2906,
    80.6337,
    'standard',
    1200,
    40,
    TRUE
),
(
    'loc_logistics_col_001',
    'test_logistics_001',
    'Colombo Warehouse',
    'warehouse',
    'Colombo',
    'Colombo',
    'Western',
    6.9500,
    79.8500,
    'large',
    50,
    60,
    TRUE
)
ON CONFLICT (location_id) DO NOTHING;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check tables created
SELECT 
    tablename,
    schemaname
FROM pg_tables 
WHERE tablename IN (
    'company_profiles',
    'company_locations',
    'operational_indicator_values',
    'industry_templates'
)
ORDER BY tablename;

-- Check sample data
SELECT company_id, company_name, industry_id FROM company_profiles;
SELECT industry_id, industry_name FROM industry_templates;
SELECT COUNT(*) as location_count FROM company_locations;

-- Check TimescaleDB hypertable (if available)
SELECT 
    hypertable_name,
    num_dimensions
FROM timescaledb_information.hypertables 
WHERE hypertable_name = 'operational_indicator_values';
