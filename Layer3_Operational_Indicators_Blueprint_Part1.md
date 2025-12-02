
# LAYER 3: OPERATIONAL ENVIRONMENT INDICATOR ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan - PART 1

---

## TABLE OF CONTENTS - PART 1

1. [Phase 0: Strategic Analysis & Design Philosophy](#phase-0)
2. [Architectural Overview](#architectural-overview)
3. [Industry Profile System](#industry-profiles)
4. [Database Architecture for Layer 3](#database-architecture)
5. [Mock Data Strategy](#mock-data)
6. [Impact Translation Framework](#impact-translation)
7. [Universal Operational Indicators](#universal-indicators)
8. [Industry-Specific Indicators](#industry-specific)

---

## PHASE 0: STRATEGIC ANALYSIS & DESIGN PHILOSOPHY {#phase-0}

### System Design Philosophy

**Core Purpose:**
Transform national-level indicators into actionable operational intelligence specific to each industry and business context.

**The Translation Challenge:**

```
Layer 2 Output: "Political Unrest Index = 78 (Elevated)"
                    ↓
Layer 3 Must Answer:
├── Retail Manager: "Should I close my store early today?"
├── Logistics Manager: "Can my trucks deliver safely?"
├── HR Manager: "Will employees make it to work?"
├── CFO: "What's the financial impact on operations?"
└── CEO: "Do I activate business continuity plans?"
```

**Key Design Principles:**

1. **Context-Driven**: Same national event → Different operational impacts per industry
2. **Actionable Intelligence**: Every indicator must answer "What should I do?"
3. **Customizable**: Business profiles determine relevance and weighting
4. **Predictive**: Forecast operational impacts, not just current state
5. **Scalable**: Support multiple industries, company sizes, locations

**The Paradigm Shift:**

```
Layer 1: "WHAT happened?" (News → Data)
Layer 2: "HOW IS the nation?" (Data → Indicators)
Layer 3: "HOW DOES IT AFFECT MY BUSINESS?" (Indicators → Decisions)
```

### Conceptual Framework

**The Translation Matrix:**

```
National Context × Business Profile = Operational Reality

Example:
("Fuel Shortage" × "Logistics Company") = "Critical Impact"
("Fuel Shortage" × "Software Company") = "Minimal Impact"

("Currency Depreciation" × "Import-Heavy Retail") = "Crisis"
("Currency Depreciation" × "Export Manufacturing") = "Opportunity"
```

**Intelligence Layers:**

```
Level 1: Universal Operational Factors (affect all businesses)
├── Transportation availability
├── Utility reliability
├── Workforce accessibility
├── Supply chain integrity
└── Regulatory compliance

Level 2: Industry-Specific Factors (vary by sector)
├── Manufacturing: Raw material availability, energy costs
├── Retail: Foot traffic, consumer sentiment
├── Logistics: Route disruptions, fuel costs
└── IT/Services: Talent availability, infrastructure

Level 3: Company-Specific Factors (unique to each business)
├── Your locations (Colombo vs. Kandy operations)
├── Your dependencies (60% imports vs. 40% local)
├── Your scale (SME vs. large enterprise)
└── Your business model (B2B vs. B2C)
```

---

## ARCHITECTURAL OVERVIEW {#architectural-overview}

### The Complete Layer 3 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│          LAYER 3: OPERATIONAL ENVIRONMENT INDICATORS             │
└─────────────────────────────────────────────────────────────────┘

INPUT (From Layer 2):                OUTPUT (To Dashboard/Users):
├── National indicators (50+)        ├── Operational risk scores
├── Trends & forecasts              ├── Industry-specific impacts
├── Anomaly alerts                  ├── Geographic intelligence
├── Geographic data                 ├── Actionable recommendations
└── Narrative summaries             └── Scenario forecasts

┌──────────────────────────────────────────────────────────────┐
│                     PROCESSING FLOW                           │
└──────────────────────────────────────────────────────────────┘

Layer 2 Indicators
        ↓
┌────────────────────┐
│  Relevance Filter  │ ← Business Profile
│  "Does this affect │   (Industry, Size,
│   my business?"    │    Locations, etc.)
└────────────────────┘
        ↓
┌────────────────────┐
│  Impact Translator │ ← Translation Rules
│  "How severely?"   │   (Impact matrices)
└────────────────────┘
        ↓
┌────────────────────┐
│  Aggregator        │ ← Weighting System
│  "Combined effect?"│
└────────────────────┘
        ↓
┌────────────────────┐
│  Operational       │
│  Indicators        │
│  Generated         │
└────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
Universal  Industry-Specific
Indicators  Indicators
    ↓           ↓
    └─────┬─────┘
          ↓
┌──────────────────┐
│  Recommendation  │
│  Engine          │
└──────────────────┘
          ↓
┌──────────────────┐
│  Forecasting     │
│  Engine          │
└──────────────────┘
          ↓
┌──────────────────┐
│  Scenario        │
│  Simulator       │
└──────────────────┘
          ↓
    Final Output
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
└─────────────────────────────────────────────────────────┘

Layer 2 Database
    ↓
Indicator Pull Service (every 15 min)
    ↓
    ├─→ Cache (Redis) ← Fast access for real-time queries
    └─→ Processing Queue
            ↓
    Parallel Processors (by business profile)
            ↓
    ├─→ Universal Indicators Calculator
    ├─→ Industry-Specific Calculator
    └─→ Company-Specific Calculator
            ↓
    Results Aggregator
            ↓
    ├─→ PostgreSQL (Operational indicator metadata)
    ├─→ TimescaleDB (Time-series operational values)
    └─→ MongoDB (Detailed calculations, recommendations)
            ↓
    API Layer (REST/GraphQL)
            ↓
    Dashboard / Mobile / Integrations
```

---

## INDUSTRY PROFILE SYSTEM {#industry-profiles}

### 3.1 INDUSTRY TAXONOMY

**Primary Industry Categories:**

```
1. MANUFACTURING
   ├── Food & Beverage
   ├── Textiles & Apparel
   ├── Pharmaceuticals
   ├── Chemicals & Plastics
   ├── Electronics & Machinery
   └── Construction Materials

2. RETAIL & CONSUMER GOODS
   ├── Grocery & Supermarkets
   ├── Fashion & Apparel
   ├── Electronics & Appliances
   ├── Automotive Retail
   └── Pharmacies & Healthcare Retail

3. LOGISTICS & TRANSPORTATION
   ├── Freight & Cargo
   ├── Courier Services
   ├── Warehousing
   ├── Fleet Management
   └── Last-Mile Delivery

4. TOURISM & HOSPITALITY
   ├── Hotels & Resorts
   ├── Restaurants & Cafes
   ├── Travel Agencies
   ├── Event Management
   └── Tour Operators

5. TECHNOLOGY & SERVICES
   ├── IT Services & BPO
   ├── Software Development
   ├── Telecommunications
   ├── Professional Services
   └── Education & Training

6. FINANCIAL SERVICES
   ├── Banking
   ├── Insurance
   ├── Investment Services
   ├── Microfinance
   └── Fintech

7. AGRICULTURE & FOOD PRODUCTION
   ├── Crop Farming
   ├── Livestock
   ├── Fisheries
   ├── Food Processing
   └── Agricultural Supply

8. CONSTRUCTION & REAL ESTATE
   ├── Residential Construction
   ├── Commercial Construction
   ├── Infrastructure Development
   ├── Property Management
   └── Real Estate Sales

9. HEALTHCARE
   ├── Hospitals & Clinics
   ├── Diagnostic Centers
   ├── Pharmaceutical Distribution
   └── Medical Equipment

10. ENERGY & UTILITIES
    ├── Power Generation
    ├── Water Supply
    ├── Renewable Energy
    └── Utility Services
```

### 3.2 INDUSTRY SENSITIVITY PROFILES

**Pre-Defined Sensitivity Matrices:**

**Manufacturing Sector Profile:**
```yaml
industry_id: "manufacturing"
display_name: "Manufacturing"

# Which national indicators matter most?
national_indicator_sensitivities:
  # Format: indicator_category: {relevance_score, impact_multiplier}
  
  ECONOMIC:
    currency_stability: {relevance: 0.95, impact: 1.5}
    # Currency affects import costs heavily
    
    inflation_pressure: {relevance: 0.85, impact: 1.2}
    # Affects input costs and wages
    
    supply_chain_health: {relevance: 0.90, impact: 1.4}
    # Critical for raw materials
  
  POLITICAL:
    labor_strikes: {relevance: 0.80, impact: 1.3}
    # Can halt production
    
    policy_changes: {relevance: 0.70, impact: 1.1}
    # Tax, tariffs affect costs
  
  ENVIRONMENTAL:
    power_outages: {relevance: 0.95, impact: 1.6}
    # Production停止
    
    weather_severity: {relevance: 0.60, impact: 0.8}
    # Some impact on logistics
  
  TECHNOLOGICAL:
    infrastructure_status: {relevance: 0.75, impact: 1.0}

# What operational factors are critical?
operational_priorities:
  - name: "Raw Material Availability"
    weight: 0.30
    dependencies: [supply_chain_health, currency_stability, port_operations]
  
  - name: "Energy Supply Reliability"
    weight: 0.25
    dependencies: [power_outages, fuel_availability]
  
  - name: "Workforce Availability"
    weight: 0.20
    dependencies: [labor_strikes, transport_disruptions, health_alerts]
  
  - name: "Production Cost Pressure"
    weight: 0.15
    dependencies: [inflation_pressure, currency_stability, energy_costs]
  
  - name: "Export Viability"
    weight: 0.10
    dependencies: [currency_stability, port_operations, trade_policies]

# Typical impact lag times
impact_lag_hours:
  currency_change: 24        # Immediate on costs
  strike_announcement: 48    # Time to prepare
  power_outage: 0           # Instant impact
  policy_change: 168        # Week to implement
```

**Retail Sector Profile:**
```yaml
industry_id: "retail"
display_name: "Retail & Consumer Goods"

national_indicator_sensitivities:
  ECONOMIC:
    consumer_confidence: {relevance: 0.95, impact: 1.4}
    # Direct correlation to sales
    
    inflation_pressure: {relevance: 0.90, impact: 1.3}
    # Affects purchasing power
    
    currency_stability: {relevance: 0.70, impact: 1.1}
    # If selling imported goods
  
  SOCIAL:
    public_mood: {relevance: 0.85, impact: 1.2}
    # Affects shopping behavior
    
    safety_perception: {relevance: 0.75, impact: 1.3}
    # People won't shop if unsafe
  
  ENVIRONMENTAL:
    weather_severity: {relevance: 0.80, impact: 1.2}
    # Rain reduces foot traffic
    
    transport_disruptions: {relevance: 0.85, impact: 1.4}
    # Can't reach stores
  
  POLITICAL:
    civil_unrest: {relevance: 0.90, impact: 1.5}
    # Stores close during protests

operational_priorities:
  - name: "Expected Foot Traffic"
    weight: 0.35
    dependencies: [transport_availability, weather, safety_perception, consumer_sentiment]
  
  - name: "Supply Chain Integrity"
    weight: 0.25
    dependencies: [port_operations, transport_disruptions, fuel_availability]
  
  - name: "Consumer Purchasing Power"
    weight: 0.20
    dependencies: [consumer_confidence, inflation_pressure, employment_situation]
  
  - name: "Operational Costs"
    weight: 0.15
    dependencies: [fuel_prices, utility_costs, wage_pressure]
  
  - name: "Competitive Landscape"
    weight: 0.05
    dependencies: [market_sentiment, new_entrants]

impact_lag_hours:
  weather_change: 2
  transport_disruption: 6
  consumer_sentiment_shift: 48
  supply_disruption: 72
```

**Logistics & Transportation Profile:**
```yaml
industry_id: "logistics"
display_name: "Logistics & Transportation"

national_indicator_sensitivities:
  ECONOMIC:
    fuel_availability: {relevance: 1.00, impact: 2.0}
    # Existential for operations
    
    fuel_prices: {relevance: 0.95, impact: 1.8}
    # Largest cost component
  
  ENVIRONMENTAL:
    weather_severity: {relevance: 0.90, impact: 1.5}
    # Roads impassable
    
    road_conditions: {relevance: 0.95, impact: 1.6}
  
  POLITICAL:
    strike_activity: {relevance: 0.85, impact: 1.4}
    # Own workforce + related sectors
    
    civil_unrest: {relevance: 0.90, impact: 1.5}
    # Routes blocked
  
  SOCIAL:
    port_operations: {relevance: 0.80, impact: 1.3}
    # For cargo logistics

operational_priorities:
  - name: "Fleet Availability"
    weight: 0.30
    dependencies: [fuel_availability, vehicle_maintenance, driver_availability]
  
  - name: "Route Viability"
    weight: 0.30
    dependencies: [road_conditions, weather, civil_unrest, road_closures]
  
  - name: "Operating Cost"
    weight: 0.25
    dependencies: [fuel_prices, maintenance_costs, toll_changes]
  
  - name: "Delivery Reliability"
    weight: 0.10
    dependencies: [traffic_conditions, weather, port_congestion]
  
  - name: "Customer Demand"
    weight: 0.05
    dependencies: [economic_activity, e-commerce_trends]

impact_lag_hours:
  fuel_shortage: 12
  weather_alert: 6
  road_closure: 2
  strike_announcement: 24
```

### 3.3 BUSINESS PROFILE SCHEMA

**Company-Specific Configuration:**

```yaml
# Example: ABC Retail Chain Profile

company_id: "abc_retail_001"
company_name: "ABC Supermarkets"
industry: "retail"
sub_industry: "grocery_supermarkets"

# Business characteristics
business_scale:
  size: "large"              # small, medium, large, enterprise
  employees: 450
  annual_revenue_lkr: 5000000000
  locations_count: 8

# Geographic footprint
locations:
  - location_id: "abc_col_001"
    name: "Colombo Main Branch"
    city: "Colombo"
    district: "Colombo"
    province: "Western"
    coordinates: {lat: 6.9271, lon: 79.8612}
    size: "flagship"
    daily_footfall_avg: 2500
    
  - location_id: "abc_kan_001"
    name: "Kandy Branch"
    city: "Kandy"
    district: "Kandy"
    province: "Central"
    coordinates: {lat: 7.2906, lon: 80.6337}
    size: "standard"
    daily_footfall_avg: 1200
  
  # ... more locations

# Supply chain profile
supply_chain:
  import_dependency: 0.60      # 60% of goods imported
  local_sourcing: 0.40
  
  critical_suppliers:
    - supplier_type: "food_imports"
      location: "international"
      criticality: "high"
      lead_time_days: 14
    
    - supplier_type: "local_produce"
      location: "upcountry"
      criticality: "medium"
      lead_time_days: 2
  
  logistics_partners:
    - name: "XYZ Logistics"
      service: "distribution"
      criticality: "high"

# Operational dependencies
critical_dependencies:
  fuel: "high"                 # For generators, transport
  power: "high"                # Refrigeration critical
  internet: "medium"           # POS, inventory systems
  water: "medium"
  transport_access: "high"     # Customer and supply access
  labor: "high"                # Service-intensive

# Customer profile
customer_base:
  type: "B2C"
  segment: "mass_market"
  geographic_spread: "multi_city"
  price_sensitivity: "high"

# Risk tolerance
risk_profile:
  operational_disruption_tolerance: "low"
  # Can't afford to close stores
  
  cost_volatility_tolerance: "medium"
  # Can adjust prices somewhat
  
  reputation_sensitivity: "high"
  # Bad service affects brand

# Custom alert thresholds
alert_thresholds:
  supply_chain_risk:
    low: 30
    medium: 50
    high: 70
    critical: 85
  
  foot_traffic_impact:
    low: -10    # -10% acceptable
    medium: -25
    high: -40
    critical: -60

# Operational hours
operating_schedule:
  weekdays: {open: "08:00", close: "21:00"}
  weekends: {open: "08:00", close: "22:00"}
  holidays: "variable"

# Business continuity
contingency_plans:
  power_outage: "generators"
  fuel_shortage: "2_week_reserve"
  staff_shortage: "cross_training"
  supply_disruption: "buffer_stock"
```

---

## DATABASE ARCHITECTURE FOR LAYER 3 {#database-architecture}

### 3.4 MULTI-DATABASE STRATEGY

**Database Responsibility Matrix:**

```
PostgreSQL:       Company profiles, industry templates, translation rules
TimescaleDB:      Operational indicator time-series values
MongoDB:          Detailed calculations, recommendations, scenarios
Redis:            Real-time cache, company-specific current states
```

#### PostgreSQL Schema

**Table 1: `industry_templates`**
```sql
/*
Purpose: Store pre-defined industry profiles
Responsibility: Define industry characteristics and sensitivities
*/

CREATE TABLE industry_templates (
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
        "operational_priorities": [
            {
                "name": "Raw Material Availability",
                "weight": 0.30,
                "dependencies": ["supply_chain_health", "currency"]
            }
        ]
    }
    */
    
    -- Impact lag configuration
    impact_lags JSONB,
    /* Structure:
    {
        "indicator_code": lag_hours
    }
    */
    
    -- Metadata
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Sample data
INSERT INTO industry_templates (industry_id, industry_name, sensitivity_config) VALUES
('manufacturing', 'Manufacturing', '{"national_indicators": {...}}'),
('retail', 'Retail & Consumer Goods', '{"national_indicators": {...}}'),
('logistics', 'Logistics & Transportation', '{"national_indicators": {...}}');
```

**Table 2: `company_profiles`**
```sql
/*
Purpose: Store individual company/business profiles
Responsibility: Company-specific configuration
*/

CREATE TABLE company_profiles (
    company_id VARCHAR(50) PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    
    -- Industry classification
    industry_id VARCHAR(50) REFERENCES industry_templates(industry_id),
    sub_industry VARCHAR(100),
    
    -- Business characteristics
    business_scale VARCHAR(20),          -- 'small', 'medium', 'large', 'enterprise'
    employee_count INTEGER,
    annual_revenue DECIMAL(15,2),
    
    -- Operational profile
    supply_chain_config JSONB,
    critical_dependencies JSONB,
    customer_profile JSONB,
    risk_profile JSONB,
    
    -- Custom settings
    custom_weights JSONB,                -- Override default industry weights
    alert_thresholds JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50),       -- If SaaS model
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_company_industry ON company_profiles(industry_id);
CREATE INDEX idx_company_active ON company_profiles(is_active);
```

**Table 3: `company_locations`**
```sql
/*
Purpose: Store company locations for geographic analysis
Responsibility: Enable location-specific operational indicators
*/

CREATE TABLE company_locations (
    location_id VARCHAR(50) PRIMARY KEY,
    company_id VARCHAR(50) REFERENCES company_profiles(company_id),
    
    -- Location details
    location_name VARCHAR(200) NOT NULL,
    location_type VARCHAR(50),           -- 'headquarters', 'branch', 'warehouse', 'factory'
    
    -- Geographic data
    city VARCHAR(100),
    district VARCHAR(100),
    province VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Location characteristics
    size_category VARCHAR(50),           -- 'flagship', 'standard', 'small'
    daily_capacity INTEGER,              -- footfall, production units, etc.
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
```

**Table 4: `operational_indicator_definitions`**
```sql
/*
Purpose: Define all operational indicators
Responsibility: Catalog of operational metrics
*/

CREATE TABLE operational_indicator_definitions (
    operational_indicator_id SERIAL PRIMARY KEY,
    
    -- Identification
    indicator_code VARCHAR(100) NOT NULL UNIQUE,
    indicator_name VARCHAR(200) NOT NULL,
    display_name VARCHAR(200),
    
    -- Classification
    indicator_type VARCHAR(50),
    -- 'universal', 'industry_specific', 'company_specific'
    
    applicable_industries TEXT[],
    -- NULL = applies to all, else specific industries
    
    -- Calculation specification
    calculation_method VARCHAR(50),
    -- 'direct_mapping', 'weighted_aggregation', 'rule_based', 'ml_model'
    
    calculation_formula TEXT,
    input_indicators JSONB,
    /* Structure:
    [
        {
            "national_indicator_code": "POL_UNREST_01",
            "weight": 0.4,
            "transformation": "inverse"  // optional
        }
    ]
    */
    
    -- Value specifications
    value_type VARCHAR(20),
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    unit VARCHAR(50),
    
    -- Interpretation
    interpretation_levels JSONB,
    /* Structure:
    {
        "critical": {"min": 80, "max": 100, "color": "red"},
        "high": {"min": 60, "max": 79, "color": "orange"},
        "medium": {"min": 40, "max": 59, "color": "yellow"},
        "low": {"min": 0, "max": 39, "color": "green"}
    }
    */
    
    -- Metadata
    description TEXT,
    business_relevance TEXT,
    recommended_actions JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Sample operational indicators
INSERT INTO operational_indicator_definitions 
(indicator_code, indicator_name, indicator_type, applicable_industries) VALUES
('OPS_TRANSPORT_AVAIL', 'Transportation Availability', 'universal', NULL),
('OPS_SUPPLY_CHAIN', 'Supply Chain Integrity Score', 'universal', NULL),
('OPS_WORKFORCE_AVAIL', 'Workforce Availability', 'universal', NULL),
('OPS_FOOTFALL_IMPACT', 'Expected Foot Traffic Impact', 'industry_specific', ARRAY['retail']),
('OPS_PRODUCTION_CAPACITY', 'Production Capacity Utilization', 'industry_specific', ARRAY['manufacturing']);
```

**Table 5: `translation_rules`**
```sql
/*
Purpose: Rules for translating national indicators to operational impacts
Responsibility: The "impact translation matrix"
*/

CREATE TABLE translation_rules (
    rule_id SERIAL PRIMARY KEY,
    
    -- Source
    national_indicator_code VARCHAR(100) NOT NULL,
    
    -- Target
    operational_indicator_code VARCHAR(100) REFERENCES operational_indicator_definitions(indicator_code),
    
    -- Applicability
    applicable_industries TEXT[],
    applicable_business_scales TEXT[],
    
    -- Translation logic
    rule_type VARCHAR(50),
    -- 'linear', 'threshold', 'formula', 'lookup_table', 'ml_model'
    
    rule_config JSONB NOT NULL,
    /* Examples:
    
    Linear:
    {
        "type": "linear",
        "slope": 0.8,
        "intercept": 10,
        "multiplier": industry_sensitivity
    }
    
    Threshold:
    {
        "type": "threshold",
        "thresholds": [
            {"min": 0, "max": 30, "output": 10},
            {"min": 30, "max": 60, "output": 40},
            {"min": 60, "max": 100, "output": 80}
        ]
    }
    
    Formula:
    {
        "type": "formula",
        "expression": "(national_value * 0.8) + (company_dependency * 20)"
    }
    */
    
    -- Impact characteristics
    impact_lag_hours INTEGER DEFAULT 0,
    impact_duration_hours INTEGER,
    confidence_level DECIMAL(3,2),
    
    -- Metadata
    description TEXT,
    validation_notes TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_translation_national ON translation_rules(national_indicator_code);
CREATE INDEX idx_translation_operational ON translation_rules(operational_indicator_code);
```

**Table 6: `recommendation_templates`**
```sql
/*
Purpose: Store actionable recommendations for different scenarios
Responsibility: "What should I do?" guidance
*/

CREATE TABLE recommendation_templates (
    template_id SERIAL PRIMARY KEY,
    
    -- Trigger conditions
    operational_indicator_code VARCHAR(100),
    severity_level VARCHAR(20),
    -- 'critical', 'high', 'medium', 'low'
    
    industry_id VARCHAR(50),
    
    -- Recommendation content
    recommendation_title VARCHAR(200),
    recommendation_text TEXT,
    
    action_items JSONB,
    /* Structure:
    [
        {
            "action": "Secure 2-week fuel supply",
            "priority": "urgent",
            "timeline": "within 24 hours",
            "responsible": "Operations Manager"
        }
    ]
    */
    
    -- Supporting information
    rationale TEXT,
    estimated_cost_impact VARCHAR(100),
    estimated_time_to_implement VARCHAR(100),
    
    -- References
    related_templates INTEGER[],
    external_resources TEXT[],
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### TimescaleDB Schema

**Hypertable 1: `operational_indicator_values`**
```sql
/*
Purpose: Store time-series operational indicator values
Responsibility: Historical operational metrics per company
*/

CREATE TABLE operational_indicator_values (
    time TIMESTAMPTZ NOT NULL,
    company_id VARCHAR(50) NOT NULL,
    operational_indicator_code VARCHAR(100) NOT NULL,
    location_id VARCHAR(50),                    -- NULL = company-wide
    
    -- Value data
    value DECIMAL(15,4) NOT NULL,
    normalized_value DECIMAL(5,4),              -- 0-1 or 0-100 scale
    
    -- Calculation metadata
    calculation_method VARCHAR(50),
    confidence_score DECIMAL(3,2),
    
    -- Contributing factors
    input_national_indicators JSONB,
    /* Structure:
    {
        "POL_UNREST_01": {"value": 78, "weight": 0.4},
        "ECON_FUEL_01": {"value": 85, "weight": 0.6}
    }
    */
    
    -- Comparative context
    previous_value DECIMAL(15,4),
    change_percentage DECIMAL(6,2),
    industry_average DECIMAL(15,4),
    deviation_from_average DECIMAL(6,2),
    
    -- Quality flags
    quality_flags TEXT[],
    
    PRIMARY KEY (time, company_id, operational_indicator_code, COALESCE(location_id, ''))
);

-- Convert to hypertable
SELECT create_hypertable('operational_indicator_values', 'time');

-- Indexes
CREATE INDEX idx_op_values_company ON operational_indicator_values(company_id, time DESC);
CREATE INDEX idx_op_values_indicator ON operational_indicator_values(operational_indicator_code, time DESC);
CREATE INDEX idx_op_values_location ON operational_indicator_values(location_id, time DESC) WHERE location_id IS NOT NULL;

-- Continuous aggregates for performance
CREATE MATERIALIZED VIEW operational_values_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    company_id,
    operational_indicator_code,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value,
    COUNT(*) AS data_points
FROM operational_indicator_values
GROUP BY hour, company_id, operational_indicator_code;

CREATE MATERIALIZED VIEW operational_values_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS day,
    company_id,
    operational_indicator_code,
    AVG(value) AS avg_value,
    STDDEV(value) AS std_dev,
    MAX(value) AS max_value,
    MIN(value) AS min_value
FROM operational_indicator_values
GROUP BY day, company_id, operational_indicator_code;
```

**Hypertable 2: `operational_alerts`**
```sql
/*
Purpose: Log operational alerts and threshold breaches
Responsibility: Alert history and notification tracking
*/

CREATE TABLE operational_alerts (
    time TIMESTAMPTZ NOT NULL,
    alert_id VARCHAR(50) NOT NULL,
    company_id VARCHAR(50) NOT NULL,
    
    -- Alert details
    operational_indicator_code VARCHAR(100),
    location_id VARCHAR(50),
    
    alert_type VARCHAR(50),
    -- 'threshold_breach', 'rapid_change', 'forecast_warning', 'cascade_alert'
    
    severity VARCHAR(20),
    -- 'critical', 'high', 'medium', 'low'
    
    -- Values
    current_value DECIMAL(15,4),
    threshold_value DECIMAL(15,4),
    previous_value DECIMAL(15,4),
    
    -- Context
    trigger_condition TEXT,
    affected_operations TEXT[],
    
    -- Response
    recommendations JSONB,
    notification_sent BOOLEAN DEFAULT FALSE,
    notification_channels TEXT[],
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    
    PRIMARY KEY (time, alert_id)
);

SELECT create_hypertable('operational_alerts', 'time');

CREATE INDEX idx_alerts_company ON operational_alerts(company_id, time DESC);
CREATE INDEX idx_alerts_severity ON operational_alerts(severity, time DESC);
CREATE INDEX idx_alerts_unacknowledged ON operational_alerts(acknowledged, time DESC) WHERE NOT acknowledged;
```

#### MongoDB Schema

**Collection 1: `operational_calculations`**
```javascript
/*
Purpose: Detailed calculation breakdown for operational indicators
Use: Audit trail, debugging, explanation
*/

{
    _id: ObjectId("..."),
    company_id: "abc_retail_001",
    operational_indicator_code: "OPS_SUPPLY_CHAIN",
    calculation_timestamp: ISODate("2025-12-01T10:00:00Z"),
    
    calculation_details: {
        method: "weighted_aggregation",
        
        inputs: [
            {
                national_indicator: "ECON_PORT_OPS",
                value: 65,
                weight: 0.30,
                weighted_contribution: 19.5,
                relevance_reason: "Port operations critical for imports"
            },
            {
                national_indicator: "ENV_ROAD_STATUS",
                value: 72,
                weight: 0.25,
                weighted_contribution: 18.0,
                relevance_reason: "Road conditions affect distribution"
            },
            {
                national_indicator: "ECON_FUEL_AVAIL",
                value: 58,
                weight: 0.25,
                weighted_contribution: 14.5,
                relevance_reason: "Fuel needed for logistics"
            },
            {
                national_indicator: "POL_IMPORT_POLICY",
                value: 80,
                weight: 0.20,
                weighted_contribution: 16.0,
                relevance_reason: "Import regulations stability"
            }
        ],
        
        base_calculation: 68.0,
        
        adjustments: [
            {
                type: "company_dependency",
                factor: "import_dependency_60%",
                multiplier: 0.95,
                adjusted_value: 64.6
            },
            {
                type: "industry_sensitivity",
                factor: "retail_supply_chain_critical",
                multiplier: 1.1,
                final_value: 71.06
            }
        ],
        
        final_value: 71.06,
        rounded_value: 71,
        confidence: 0.82
    },
    
    context: {
        industry_average: 68,
        deviation_from_average: +3.06,
        company_rank_percentile: 65,
        trend_direction: "improving",
        compared_to_yesterday: +2.5
    },
    
    interpretation: {
        level: "medium_risk",
        severity_score: 71,
        status_label: "Moderate Supply Chain Risk",
        requires_attention: true
    }
}

// Indexes
db.operational_calculations.createIndex({
    "company_id": 1,
    "calculation_timestamp": -1
})
db.operational_calculations.createIndex({
    "operational_indicator_code": 1,
    "calculation_timestamp": -1
})
```

**Collection 2: `operational_recommendations`**
```javascript
/*
Purpose: Generated recommendations for companies
Use: Decision support, action planning
*/

{
    _id: ObjectId("..."),
    company_id: "abc_retail_001",
    generated_at: ISODate("2025-12-01T10:00:00Z"),
    
    trigger: {
        operational_indicator: "OPS_FOOTFALL_IMPACT",
        value: -35,
        severity: "high",
        reason: "Transport disruption + weather + civil unrest"
    },
    
    recommendations: [
        {
            priority: "urgent",
            category: "operational_adjustment",
            title: "Consider Early Store Closure",
            
            description: "Expected foot traffic is 35% below normal due to transport disruptions and weather. Early closure may reduce operational costs without significant revenue loss.",
            
            actions: [
                {
                    action: "Review sales data from 6pm-9pm",
                    responsible: "Store Manager",
                    timeline: "Next 2 hours"
                },
                {
                    action: "If sales <20% of target, close at 7pm instead of 9pm",
                    responsible: "Regional Manager approval",
                    timeline: "Before 6pm today"
                },
                {
                    action: "Notify staff of potential early closure",
                    responsible: "HR",
                    timeline: "Immediate"
                }
            ],
            
            expected_impact: {
                cost_savings: "~LKR 50,000 per store",
                revenue_loss: "Minimal (<5% of evening sales)",
                staff_impact: "Early dismissal for 20 employees"
            },
            
            confidence: 0.78,
            
            related_indicators: [
                "OPS_TRANSPORT_AVAIL",
                "ENV_WEATHER_SEVERITY",
                "POL_CIVIL_UNREST"
            ]
        },
        
        {
            priority: "high",
            category: "supply_chain",
            title: "Expedite Critical Inventory Delivery",
            
            description: "Transport disruptions expected to worsen tomorrow. Move essential inventory today.",
            
            actions: [
                {
                    action: "Contact logistics partner for urgent deliveries",
                    responsible: "Supply Chain Manager",
                    timeline: "Within 3 hours"
                },
                {
                    action: "Prioritize: Milk, bread, perishables to all stores",
                    responsible: "Warehouse",
                    timeline: "Today before 5pm"
                }
            ],
            
            expected_impact: {
                cost_increase: "LKR 25,000 rush delivery fees",
                risk_mitigation: "Prevent stockouts during 2-day disruption"
            },
            
            confidence: 0.85
        }
    ],
    
    scenario_analysis: {
        if_conditions_worsen: {
            probability: 0.40,
            impact: "Full store closure may be necessary",
            prepare_for: ["Staff safety protocols", "Store security", "Perishable inventory management"]
        },
        
        if_conditions_improve: {
            probability: 0.30,
            impact: "Return to normal operations by tomorrow",
            monitor: ["Transport availability updates", "Weather forecasts"]
        }
    },
    
    validity_period: {
        start: ISODate("2025-12-01T10:00:00Z"),
        end: ISODate("2025-12-01T18:00:00Z"),
        reason: "Situation evolving rapidly, re-assess every 8 hours"
    }
}

// Indexes
db.operational_recommendations.createIndex({
    "company_id": 1,
    "generated_at": -1
})
db.operational_recommendations.createIndex({
    "validity_period.end": 1
})
```

#### Redis Schema

**Key Patterns:**

```
Purpose: Fast access to current operational state

Key Patterns:
├── company:current:{company_id}
│   └── Hash: Current operational indicator values
│       {
│         "OPS_SUPPLY_CHAIN": "71",
│         "OPS_FOOTFALL_IMPACT": "-35",
│         "OPS_WORKFORCE_AVAIL": "88",
│         "last_updated": "2025-12-01T10:00:00Z"
│       }
│
├── company:alerts:{company_id}
│   └── List: Active alerts (sorted by severity)
│       [
│         {"alert_id": "...", "severity": "critical", ...},
│         {"alert_id": "...", "severity": "high", ...}
│       ]
│
├── industry:avg:{industry_id}:{indicator_code}
│   └── String: Industry average for comparison
│       TTL: 1 hour
│
├── calculation:cache:{company_id}:{indicator_code}
│   └── Hash: Cached calculation results
│       TTL: 15 minutes
│
└── location:status:{location_id}
    └── Hash: Location-specific operational status
```

---

This completes Part 1 of the Layer 3 blueprint. Part 2 will continue with Impact Translation Framework, Universal Indicators, Industry-Specific Indicators, Calculation Methods, Forecasting, and Implementation Checklist.

