# LAYER 2: NATIONAL ACTIVITY INDICATOR ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan - PART 1

---

## TABLE OF CONTENTS - PART 1

1. [Phase 0: Strategic Analysis & Design Philosophy](#phase-0)
2. [Architectural Overview](#architectural-overview)
3. [Indicator Taxonomy & Framework](#indicator-taxonomy)
4. [Database Architecture for Layer 2](#database-architecture)
5. [Data Ingestion & Mock Data Strategy](#data-ingestion)
6. [Indicator Generation Framework](#indicator-generation)
7. [ML Classification Pipeline](#ml-classification)
8. [Sentiment Analysis Engine](#sentiment-analysis)

---

## PHASE 0: STRATEGIC ANALYSIS & DESIGN PHILOSOPHY {#phase-0}

### System Design Philosophy

**Core Purpose:**
Transform unstructured textual content (news articles) into structured, quantifiable indicators that represent the national activity state across multiple dimensions.

**Key Design Principles:**

1. **Quantification Over Qualification**: Every indicator must be a measurable number, not just a description
2. **Temporal Awareness**: All indicators tracked over time, enabling trend detection
3. **Multi-Dimensional Analysis**: PESTEL framework ensures comprehensive coverage
4. **Confidence-Driven**: Every metric includes a confidence score
5. **Interpretability**: System must explain WHY an indicator has a certain value

**The Social Science Foundation**

**What are Indicators?**
- **Proxies for Complex Phenomena**: A single number representing hundreds of data points
- **Decision-Making Tools**: Enable quantitative comparison ("Is today worse than yesterday?")
- **Early Warning Signals**: Detect changes before official statistics are available

**Example:**
```
Traditional Approach:
"There are protests happening in Colombo"

Indicator Approach:
Political_Unrest_Index: 78 (↑ 23 points from yesterday)
├── Based on 15 news articles
├── 3 social media trending topics
├── Confidence: 85%
└── Interpretation: "Significantly elevated civil unrest"
```

**Why PESTEL Framework?**

**PESTEL = Standard Business Environment Analysis Tool**

```
Political:       Government actions, stability, policies
Economic:        Financial health, markets, trade
Social:          Public mood, demographics, culture
Technological:   Infrastructure, innovation, digital adoption
Environmental:   Weather, disasters, climate impacts
Legal:           Regulations, compliance, judicial activity
```

**Benefits:**
- **Comprehensive**: Covers all major external factors affecting businesses
- **Standardized**: Widely recognized in business/academic circles
- **Actionable**: Each dimension maps to specific business decisions

---

## ARCHITECTURAL OVERVIEW {#architectural-overview}

### The Complete Layer 2 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 2: NATIONAL ACTIVITY INDICATORS               │
└─────────────────────────────────────────────────────────────────┘

INPUT (From Layer 1):                    OUTPUT (To Layer 3):
├── Processed articles (English)         ├── PESTEL Indicators
├── Source metadata                      ├── Trend analysis
├── Credibility scores                   ├── Anomaly alerts
├── Entity extractions                   ├── Geographic patterns
└── Timestamps                           └── Confidence scores

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ARTICLE    │───▶│   INITIAL    │───▶│  INDICATOR   │
│   INGESTION  │    │ CLASSIFICATION│    │  ASSIGNMENT  │
└──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
                    ┌────────────────────────────────────┐
                    │     INDICATOR PROCESSORS           │
                    │  ┌──────────────────────────────┐  │
                    │  │ Frequency Counters           │  │
                    │  │ Sentiment Aggregators        │  │
                    │  │ Entity Extractors            │  │
                    │  │ Numeric Value Extractors     │  │
                    │  └──────────────────────────────┘  │
                    └────────────────────────────────────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  INDICATOR   │◀───│ CALCULATION  │◀───│  WEIGHTING   │
│   VALUES     │    │   ENGINE     │    │   SYSTEM     │
└──────────────┘    └──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   TREND      │    │   ANOMALY    │    │  DEPENDENCY  │
│  ANALYSIS    │    │  DETECTION   │    │   MAPPING    │
└──────────────┘    └──────────────┘    └──────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    INDICATOR STORAGE    │
              │  ┌────────────────────┐ │
              │  │ TimescaleDB:       │ │
              │  │ Time-series data   │ │
              │  ├────────────────────┤ │
              │  │ PostgreSQL:        │ │
              │  │ Indicator metadata │ │
              │  ├────────────────────┤ │
              │  │ MongoDB:           │ │
              │  │ Supporting docs    │ │
              │  └────────────────────┘ │
              └─────────────────────────┘
```

---

## INDICATOR TAXONOMY & FRAMEWORK {#indicator-taxonomy}

### 2.1 COMPLETE PESTEL INDICATOR HIERARCHY

#### POLITICAL INDICATORS

```
POLITICAL DOMAIN
│
├── Government Stability
│   ├── Cabinet_Changes_Frequency
│   │   └── Count of ministerial appointments/resignations per month
│   ├── Policy_Reversal_Index
│   │   └── Number of announced policies that are reversed/modified
│   ├── Coalition_Cohesion_Score
│   │   └── Sentiment analysis of inter-party relations
│   └── Leadership_Approval_Proxy
│       └── Public sentiment toward government/president
│
├── Civil Unrest
│   ├── Protest_Frequency_Index
│   │   └── Count of protest events per week
│   ├── Strike_Activity_Score
│   │   ├── Active strikes count
│   │   ├── Sectors affected
│   │   └── Participation estimates
│   ├── Public_Dissatisfaction_Index
│   │   └── Aggregate negative sentiment toward governance
│   └── Violence_Escalation_Indicator
│       └── Mentions of violence/clashes in protests
│
├── International Relations
│   ├── Diplomatic_Activity_Index
│   │   └── High-level visits, agreements signed
│   ├── Trade_Partnership_Momentum
│   │   └── New deals, partnership announcements
│   ├── Geopolitical_Tension_Score
│   │   └── Negative mentions of foreign relations
│   └── Regional_Cooperation_Index
│       └── SAARC/BIMSTEC engagement
│
├── Election Activity (When Applicable)
│   ├── Campaign_Intensity_Score
│   ├── Voter_Sentiment_Tracker
│   └── Electoral_Volatility_Index
│
└── Security Situation
    ├── Law_Order_Incidents
    ├── Border_Security_Mentions
    └── Internal_Conflict_Signals
```

#### ECONOMIC INDICATORS

```
ECONOMIC DOMAIN
│
├── Macroeconomic Health
│   ├── GDP_Growth_Sentiment
│   │   └── Positive/negative mentions of economic growth
│   ├── Inflation_Pressure_Index
│   │   ├── Price increase mentions
│   │   ├── "Expensive" keyword frequency
│   │   └── Cost of living complaints
│   ├── Currency_Stability_Indicator
│   │   ├── LKR volatility mentions
│   │   ├── Exchange rate concern frequency
│   │   └── Black market rate discussions
│   ├── Debt_Concern_Level
│   │   └── Mentions of debt crisis, IMF, restructuring
│   └── Fiscal_Policy_Direction
│       └── Tax changes, government spending news
│
├── Financial Markets
│   ├── Stock_Market_Sentiment
│   │   └── CSE performance mentions + sentiment
│   ├── Investment_Climate_Score
│   │   ├── FDI announcements
│   │   ├── Business expansion news
│   │   └── Investor confidence indicators
│   ├── Banking_Sector_Health
│   │   └── Bank stability, liquidity mentions
│   └── Interest_Rate_Trend
│       └── Central Bank policy discussions
│
├── Trade & Commerce
│   ├── Export_Performance_Index
│   │   └── Export growth/decline mentions
│   ├── Import_Dependency_Risk
│   │   └── Import restrictions, shortage concerns
│   ├── Port_Activity_Indicator
│   │   └── Colombo port operations, congestion
│   ├── Trade_Balance_Sentiment
│   │   └── Deficit/surplus discussions
│   └── Remittance_Flow_Indicator
│       └── Worker remittance trends
│
├── Sectoral Performance
│   ├── Tourism_Activity_Index
│   │   ├── Arrival numbers mentions
│   │   ├── Hotel occupancy indicators
│   │   └── Tourism sentiment
│   ├── Manufacturing_Health
│   │   └── Production, factory activity news
│   ├── Agriculture_Status
│   │   ├── Harvest reports
│   │   ├── Crop prices
│   │   └── Farmer concerns
│   ├── Services_Sector_Momentum
│   │   └── IT, BPO, professional services news
│   └── Construction_Activity
│       └── Infrastructure projects, real estate
│
├── Employment Situation
│   ├── Job_Market_Health
│   │   ├── Hiring announcements
│   │   ├── Layoff reports
│   │   └── Job availability sentiment
│   ├── Wage_Pressure_Index
│   │   └── Salary demands, minimum wage discussions
│   └── Skills_Gap_Indicator
│       └── Employer complaints about talent shortage
│
└── Consumer Behavior
    ├── Consumer_Confidence_Proxy
    │   ├── Shopping sentiment
    │   ├── Spending willingness
    │   └── Purchase postponement signals
    ├── Retail_Activity_Indicator
    │   └── Sales reports, shopping traffic
    └── Savings_vs_Spending_Ratio
        └── Sentiment about saving vs consumption
```

#### SOCIAL INDICATORS

```
SOCIAL DOMAIN
│
├── Public Mood & Sentiment
│   ├── Overall_Public_Sentiment
│   │   └── Aggregate sentiment across all articles
│   ├── Anxiety_Level_Index
│   │   └── Frequency of worry/fear/concern keywords
│   ├── Optimism_Indicator
│   │   └── Hope/improvement/positive future mentions
│   └── Social_Media_Mood
│       └── Trending topics sentiment
│
├── Quality of Life
│   ├── Cost_of_Living_Burden
│   │   └── Affordability concerns, poverty mentions
│   ├── Healthcare_Access_Index
│   │   ├── Hospital capacity mentions
│   │   ├── Medicine shortage reports
│   │   └── Treatment affordability
│   ├── Education_Disruption_Level
│   │   ├── School closures
│   │   ├── Exam postponements
│   │   └── Teacher strikes
│   └── Housing_Affordability
│       └── Rent/property price discussions
│
├── Public Safety
│   ├── Crime_Rate_Perception
│   │   └── Crime reports, safety concerns
│   ├── Traffic_Safety_Index
│   │   └── Accident reports, road safety
│   └── Public_Space_Safety
│       └── Evening/night safety concerns
│
├── Community Cohesion
│   ├── Inter_Community_Relations
│   │   └── Ethnic/religious harmony indicators
│   ├── Civic_Engagement_Level
│   │   └── Volunteer activities, community initiatives
│   └── Social_Support_Systems
│       └── Charity, aid programs mentions
│
└── Demographics & Migration
    ├── Migration_Intention_Index
    │   └── Brain drain, emigration discussions
    ├── Urbanization_Trends
    │   └── Rural-urban movement indicators
    └── Population_Mobility
        └── Internal displacement, relocation
```

#### TECHNOLOGICAL INDICATORS

```
TECHNOLOGICAL DOMAIN
│
├── Digital Infrastructure
│   ├── Internet_Connectivity_Status
│   │   ├── Outage reports
│   │   ├── Speed complaints
│   │   └── Coverage gaps
│   ├── Telecom_Service_Quality
│   │   └── Mobile network issues
│   ├── Power_Infrastructure_Health
│   │   ├── Load shedding frequency
│   │   ├── Power cut duration
│   │   └── Electricity reliability
│   └── Transport_Infrastructure
│       ├── Road conditions
│       ├── Rail service quality
│       └── Airport operations
│
├── Innovation & Adoption
│   ├── Startup_Ecosystem_Health
│   │   ├── Funding announcements
│   │   ├── New company launches
│   │   └── Incubator activities
│   ├── Digital_Payment_Adoption
│   │   └── Fintech, mobile money usage
│   ├── E_Commerce_Growth
│   │   └── Online shopping trends
│   ├── Tech_Investment_Flow
│   │   └── Tech sector investments
│   └── Digital_Literacy_Progress
│       └── Education tech, digital skills
│
├── Cybersecurity & Data
│   ├── Cyber_Threat_Level
│   │   └── Hacking, data breach reports
│   ├── Privacy_Concerns
│   │   └── Data protection discussions
│   └── Digital_Rights_Issues
│       └── Internet censorship, access rights
│
└── Research & Development
    ├── Innovation_Output
    │   └── Patents, research publications
    └── Tech_Collaboration
        └── International tech partnerships
```

#### ENVIRONMENTAL INDICATORS

```
ENVIRONMENTAL DOMAIN
│
├── Weather & Climate
│   ├── Weather_Severity_Index
│   │   ├── Extreme temperature events
│   │   ├── Rainfall intensity
│   │   └── Seasonal anomalies
│   ├── Flood_Risk_Level
│   │   ├── Flood warnings
│   │   ├── Affected areas count
│   │   └── Damage reports
│   ├── Drought_Concern_Index
│   │   ├── Water shortage mentions
│   │   ├── Agricultural impact
│   │   └── Reservoir levels
│   └── Storm_Activity_Indicator
│       └── Cyclone, storm warnings
│
├── Natural Disasters
│   ├── Disaster_Frequency
│   │   └── Landslides, earthquakes, floods
│   ├── Disaster_Impact_Severity
│   │   ├── Casualties
│   │   ├── Displacement
│   │   └── Economic damage
│   └── Recovery_Progress_Index
│       └── Rehabilitation efforts
│
├── Environmental Quality
│   ├── Pollution_Concern_Level
│   │   ├── Air quality mentions
│   │   ├── Water contamination
│   │   └── Waste management issues
│   ├── Deforestation_Activity
│   │   └── Forest loss, illegal logging
│   └── Wildlife_Conservation_Status
│       └── Habitat loss, species threats
│
├── Agriculture & Land
│   ├── Crop_Health_Indicator
│   │   └── Harvest expectations, pest issues
│   ├── Agricultural_Productivity
│   │   └── Yield reports, farming conditions
│   └── Land_Use_Changes
│       └── Urban expansion, farmland conversion
│
└── Climate Action
    ├── Sustainability_Initiatives
    │   └── Green projects, renewable energy
    ├── Climate_Policy_Activity
    │   └── Environmental regulations
    └── Carbon_Reduction_Efforts
        └── Emissions reduction programs
```

#### LEGAL & REGULATORY INDICATORS

```
LEGAL DOMAIN
│
├── Legislative Activity
│   ├── New_Laws_Frequency
│   │   └── Bills passed, amendments
│   ├── Regulatory_Changes_Rate
│   │   └── Rule modifications across sectors
│   ├── Court_Decision_Impact
│   │   └── Major rulings affecting businesses
│   └── Legal_Reform_Momentum
│       └── Justice system improvements
│
├── Business Regulation
│   ├── Business_Ease_Index
│   │   ├── Licensing changes
│   │   ├── Permit processes
│   │   └── Registration requirements
│   ├── Tax_Policy_Direction
│   │   ├── Tax rate changes
│   │   ├── New tax introductions
│   │   └── Tax relief measures
│   ├── Labor_Law_Changes
│   │   └── Employment regulations
│   └── Trade_Regulations
│       └── Import/export rules
│
├── Compliance & Enforcement
│   ├── Regulatory_Strictness_Index
│   │   └── Enforcement action frequency
│   ├── Penalty_Severity_Trend
│   │   └── Fine amounts, sanctions
│   └── Compliance_Burden_Score
│       └── Reporting requirements
│
├── Intellectual Property
│   ├── IP_Protection_Strength
│   │   └── Patent, trademark enforcement
│   └── IP_Dispute_Frequency
│       └── Infringement cases
│
└── Contract & Commercial Law
    ├── Contract_Enforcement_Quality
    │   └── Dispute resolution efficiency
    └── Bankruptcy_Activity
        └── Insolvency filings
```

---

## DATABASE ARCHITECTURE FOR LAYER 2 {#database-architecture}

### 2.2 MULTI-DATABASE STRATEGY FOR INDICATORS

**Database Responsibility Matrix:**

```
PostgreSQL:       Indicator definitions, relationships, metadata
TimescaleDB:      Time-series indicator values (primary storage)
MongoDB:          Supporting documents, article-indicator mappings
Redis:            Real-time calculations cache, temporary aggregations
```

#### PostgreSQL Schema (Indicator Configuration & Relationships)

**Table 1: `indicator_definitions`**
```sql
/*
Purpose: Master registry of all indicators
Responsibility: Define what each indicator is and how it's calculated
*/

CREATE TABLE indicator_definitions (
    indicator_id SERIAL PRIMARY KEY,
    
    -- Identification
    indicator_code VARCHAR(100) NOT NULL UNIQUE,  -- e.g., "POL_GOV_STAB_01"
    indicator_name VARCHAR(200) NOT NULL,          -- e.g., "Cabinet Changes Frequency"
    display_name VARCHAR(200) NOT NULL,            -- User-friendly name
    
    -- Classification
    pestel_category VARCHAR(20) NOT NULL,          -- 'Political', 'Economic', etc.
    subcategory VARCHAR(100),                      -- 'Government Stability'
    sub_subcategory VARCHAR(100),                  -- Further nesting if needed
    
    -- Calculation methodology
    calculation_type VARCHAR(50) NOT NULL,
    -- 'frequency_count', 'sentiment_aggregate', 'numeric_extraction', 
    -- 'composite', 'ratio', 'weighted_average'
    
    calculation_formula TEXT,                      -- Formula or logic description
    data_sources JSONB,                            -- Which types of articles feed this
    
    -- Value specifications
    value_type VARCHAR(20) NOT NULL,               -- 'integer', 'float', 'percentage', 'index'
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    default_value DECIMAL(10,2),
    
    -- Temporal settings
    aggregation_window VARCHAR(20),                -- 'hourly', 'daily', 'weekly'
    historical_lookback_days INTEGER DEFAULT 30,
    
    -- Weighting & priority
    base_weight DECIMAL(3,2) DEFAULT 1.00,
    priority_level INTEGER DEFAULT 5,              -- 1=critical, 10=low
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_composite BOOLEAN DEFAULT FALSE,            -- Calculated from other indicators
    
    -- Documentation
    description TEXT,
    interpretation_guide TEXT,                     -- How to read the values
    business_relevance TEXT,                       -- Why this matters
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Indexes
CREATE INDEX idx_indicators_category ON indicator_definitions(pestel_category);
CREATE INDEX idx_indicators_active ON indicator_definitions(is_active);
CREATE INDEX idx_indicators_type ON indicator_definitions(calculation_type);
```

**Table 2: `indicator_dependencies`**
```sql
/*
Purpose: Define relationships between indicators
Responsibility: Enable composite indicators and dependency tracking
*/

CREATE TABLE indicator_dependencies (
    dependency_id SERIAL PRIMARY KEY,
    
    parent_indicator_id INTEGER REFERENCES indicator_definitions(indicator_id),
    child_indicator_id INTEGER REFERENCES indicator_definitions(indicator_id),
    
    -- Relationship type
    relationship_type VARCHAR(50),
    -- 'component' (child is part of parent calculation)
    -- 'correlate' (changes together)
    -- 'leads' (child predicts parent)
    -- 'causes' (child influences parent)
    
    -- For composite indicators
    weight_in_parent DECIMAL(3,2),                -- If parent is composite
    
    -- For causal relationships
    time_lag_hours INTEGER,                       -- How long before effect appears
    correlation_strength DECIMAL(3,2),            -- -1.00 to 1.00
    
    -- Evidence
    confidence_level DECIMAL(3,2),               -- How confident are we in this relationship
    evidence_base TEXT,                          -- Historical data supporting this
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_dependencies_parent ON indicator_dependencies(parent_indicator_id);
CREATE INDEX idx_dependencies_child ON indicator_dependencies(child_indicator_id);
```

**Table 3: `indicator_keywords`**
```sql
/*
Purpose: Keyword mappings for rule-based classification
Responsibility: Fast article → indicator routing
*/

CREATE TABLE indicator_keywords (
    keyword_id SERIAL PRIMARY KEY,
    indicator_id INTEGER REFERENCES indicator_definitions(indicator_id),
    
    -- Keyword specification
    keyword VARCHAR(200) NOT NULL,
    keyword_type VARCHAR(20),                    -- 'exact', 'partial', 'regex', 'semantic'
    language VARCHAR(10) DEFAULT 'en',
    
    -- Weighting
    relevance_weight DECIMAL(3,2) DEFAULT 1.00,  -- How strongly this keyword signals indicator
    
    -- Context requirements
    requires_context BOOLEAN DEFAULT FALSE,       -- Must appear with other keywords
    context_keywords TEXT[],                      -- Required co-occurring keywords
    
    -- Exclusions
    exclude_if_present TEXT[],                    -- Don't match if these words also present
    
    -- Performance tracking
    match_count INTEGER DEFAULT 0,
    false_positive_rate DECIMAL(3,2),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_keywords_indicator ON indicator_keywords(indicator_id);
CREATE INDEX idx_keywords_keyword ON indicator_keywords(keyword);
```

**Table 4: `article_indicator_mappings`**
```sql
/*
Purpose: Track which articles contribute to which indicators
Responsibility: Audit trail and recalculation support
*/

CREATE TABLE article_indicator_mappings (
    mapping_id SERIAL PRIMARY KEY,
    
    article_id VARCHAR(50) NOT NULL,              -- From Layer 1
    indicator_id INTEGER REFERENCES indicator_definitions(indicator_id),
    
    -- Match details
    match_method VARCHAR(50),                     -- 'keyword', 'ml_classification', 'manual'
    match_confidence DECIMAL(3,2),
    
    -- Contribution
    contribution_value DECIMAL(10,4),             -- How much this article affects indicator
    sentiment_score DECIMAL(4,3),                 -- If sentiment-based
    extracted_numeric_value DECIMAL(15,2),        -- If numeric extraction
    
    -- Temporal
    article_published_at TIMESTAMP,
    processed_at TIMESTAMP DEFAULT NOW(),
    
    -- Quality
    article_credibility DECIMAL(3,2),
    weight_applied DECIMAL(3,2)
);

CREATE INDEX idx_mapping_article ON article_indicator_mappings(article_id);
CREATE INDEX idx_mapping_indicator ON article_indicator_mappings(indicator_id);
CREATE INDEX idx_mapping_published ON article_indicator_mappings(article_published_at DESC);
```

**Table 5: `indicator_thresholds`**
```sql
/*
Purpose: Define alert thresholds and interpretation levels
Responsibility: Enable automated alerting and interpretation
*/

CREATE TABLE indicator_thresholds (
    threshold_id SERIAL PRIMARY KEY,
    indicator_id INTEGER REFERENCES indicator_definitions(indicator_id),
    
    -- Threshold levels
    level_name VARCHAR(50),                      -- 'Critical', 'High', 'Elevated', 'Normal', 'Low'
    level_order INTEGER,                         -- For sorting
    
    -- Value ranges
    min_value DECIMAL(10,2),
    max_value DECIMAL(10,2),
    
    -- Interpretation
    interpretation TEXT,                         -- What this level means
    color_code VARCHAR(20),                      -- For UI (red, orange, yellow, green)
    
    -- Actions
    should_alert BOOLEAN DEFAULT FALSE,
    alert_message_template TEXT,
    recommended_actions TEXT[],
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_thresholds_indicator ON indicator_thresholds(indicator_id);
```

#### TimescaleDB Schema (Time-Series Indicator Values)

**Hypertable 1: `indicator_values`**
```sql
/*
Purpose: Store all indicator values over time
Responsibility: Primary time-series storage for all indicators
*/

CREATE TABLE indicator_values (
    time TIMESTAMPTZ NOT NULL,
    indicator_id INTEGER NOT NULL,
    
    -- Value data
    value DECIMAL(15,4) NOT NULL,
    normalized_value DECIMAL(5,4),               -- Normalized to 0-1 or 0-100
    
    -- Calculation metadata
    calculation_method VARCHAR(50),
    contributing_articles_count INTEGER,
    data_points_used INTEGER,
    
    -- Quality & confidence
    confidence_score DECIMAL(3,2),
    quality_flags TEXT[],                        -- ['low_volume', 'high_variance', etc.]
    
    -- Comparative metrics
    previous_period_value DECIMAL(15,4),
    change_absolute DECIMAL(15,4),
    change_percentage DECIMAL(6,2),
    
    -- Statistical measures
    std_deviation DECIMAL(10,4),
    min_value DECIMAL(15,4),
    max_value DECIMAL(15,4),
    median_value DECIMAL(15,4),
    
    PRIMARY KEY (time, indicator_id)
);

-- Convert to hypertable
SELECT create_hypertable('indicator_values', 'time');

-- Indexes
CREATE INDEX idx_indicator_values_indicator ON indicator_values(indicator_id, time DESC);
CREATE INDEX idx_indicator_values_time ON indicator_values(time DESC);

-- Continuous aggregates for performance
CREATE MATERIALIZED VIEW indicator_values_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    indicator_id,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value,
    COUNT(*) AS data_points
FROM indicator_values
GROUP BY hour, indicator_id;

CREATE MATERIALIZED VIEW indicator_values_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS day,
    indicator_id,
    AVG(value) AS avg_value,
    MAX(value) AS max_value,
    MIN(value) AS min_value,
    STDDEV(value) AS std_dev,
    COUNT(*) AS data_points
FROM indicator_values
GROUP BY day, indicator_id;
```

**Hypertable 2: `indicator_events`**
```sql
/*
Purpose: Log significant indicator events (anomalies, threshold breaches)
Responsibility: Alert and notification system
*/

CREATE TABLE indicator_events (
    time TIMESTAMPTZ NOT NULL,
    indicator_id INTEGER NOT NULL,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL,
    -- 'threshold_breach', 'anomaly_detected', 'rapid_change', 
    -- 'correlation_break', 'data_quality_issue'
    
    event_severity VARCHAR(20),                  -- 'critical', 'high', 'medium', 'low'
    
    -- Values
    current_value DECIMAL(15,4),
    expected_value DECIMAL(15,4),
    deviation_magnitude DECIMAL(6,2),
    
    -- Context
    description TEXT,
    affected_indicators INTEGER[],               -- Related indicators also affected
    
    -- Response
    notification_sent BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    
    PRIMARY KEY (time, indicator_id, event_type)
);

SELECT create_hypertable('indicator_events', 'time');
```

**Hypertable 3: `indicator_trends`**
```sql
/*
Purpose: Store trend analysis results
Responsibility: Enable fast trend queries
*/

CREATE TABLE indicator_trends (
    time TIMESTAMPTZ NOT NULL,
    indicator_id INTEGER NOT NULL,
    
    -- Trend data
    trend_direction VARCHAR(20),                 -- 'rising', 'falling', 'stable', 'volatile'
    trend_strength DECIMAL(3,2),                 -- 0.00 (weak) to 1.00 (strong)
    
    -- Moving averages
    ma_7day DECIMAL(15,4),
    ma_30day DECIMAL(15,4),
    ma_90day DECIMAL(15,4),
    
    -- Momentum indicators
    rate_of_change DECIMAL(6,2),                -- % change per day
    momentum_score DECIMAL(4,2),                -- -10 to +10
    
    -- Volatility
    volatility_index DECIMAL(6,2),
    
    -- Forecasting
    forecast_1day DECIMAL(15,4),
    forecast_3day DECIMAL(15,4),
    forecast_7day DECIMAL(15,4),
    forecast_confidence DECIMAL(3,2),
    
    PRIMARY KEY (time, indicator_id)
);

SELECT create_hypertable('indicator_trends', 'time');
```

#### MongoDB Schema (Supporting Documents)

**Collection 1: `indicator_calculations`**
```javascript
/*
Purpose: Store detailed calculation breakdowns
Retention: Audit trail for indicator values
*/

{
    _id: ObjectId("..."),
    indicator_id: 1,
    indicator_code: "POL_UNREST_01",
    
    calculation_timestamp: ISODate("2025-11-30T10:00:00Z"),
    time_window: {
        start: ISODate("2025-11-29T10:00:00Z"),
        end: ISODate("2025-11-30T10:00:00Z"),
        duration_hours: 24
    },
    
    // Detailed breakdown
    calculation_details: {
        method: "frequency_count",
        formula: "COUNT(articles WHERE keywords MATCH)",
        
        input_articles: [
            {
                article_id: "ada_derana_001234",
                contribution: 1.0,
                weight_applied: 0.9,
                credibility: 0.85,
                relevance_score: 0.95
            },
            // ... more articles
        ],
        
        intermediate_values: {
            raw_count: 15,
            weighted_count: 12.8,
            normalized_score: 78.5
        },
        
        adjustments_applied: [
            {type: "recency_weight", factor: 1.2},
            {type: "credibility_adjustment", factor: 0.95}
        ]
    },
    
    result: {
        final_value: 78.5,
        confidence: 0.85,
        quality_flags: [],
        data_points: 15
    },
    
    comparative_context: {
        historical_average: 45.2,
        deviation: +33.3,
        percentile: 92
    }
}

// Indexes
db.indicator_calculations.createIndex({"indicator_id": 1, "calculation_timestamp": -1})
db.indicator_calculations.createIndex({"calculation_timestamp": -1})
```

**Collection 2: `indicator_narratives`**
```javascript
/*
Purpose: Auto-generated explanations for indicator values
Use: User-facing explanations
*/

{
    _id: ObjectId("..."),
    indicator_id: 1,
    timestamp: ISODate("2025-11-30T10:00:00Z"),
    
    narrative: {
        headline: "Political Unrest Index Elevated",
        
        summary: "The Political Unrest Index increased 35% today to 78.5, indicating significantly elevated civil unrest. This is based on 15 news articles reporting protests and strikes.",
        
        key_factors: [
            "15 articles about protests in Colombo (↑ 200% from yesterday)",
            "3 major strikes announced in transportation sector",
            "Social media trending: #ProtestSL (5,420 mentions)"
        ],
        
        comparison: "This is the highest level in 30 days and 73% above the monthly average.",
        
        implications: [
            "Transportation disruptions likely in Colombo region",
            "Business operations may face delays",
            "Elevated political risk for next 48-72 hours"
        ],
        
        confidence_explanation: "High confidence (85%) based on multiple credible sources including government statements and major news outlets."
    },
    
    generated_by: "narrative_engine_v1",
    language: "en"
}

// Indexes
db.indicator_narratives.createIndex({"indicator_id": 1, "timestamp": -1})
```

#### Redis Schema (Real-Time Cache)

**Key Patterns:**

```
Purpose: Fast access to current indicator states

Key Patterns:
├── indicator:current:{indicator_id}
│   └── Hash: {value, confidence, last_updated, trend}
│
├── indicator:processing:{indicator_id}
│   └── Lock key for concurrent processing prevention
│
├── indicator:articles:{indicator_id}:{window}
│   └── Set: Article IDs contributing to current calculation
│
├── calculation:queue
│   └── List: Indicator IDs pending calculation
│
└── indicator:cache:{indicator_id}:{timerange}
    └── Cached query results, TTL 5 minutes
```

---

## DATA INGESTION & MOCK DATA STRATEGY {#data-ingestion}

### 2.3 HANDLING LAYER 1 → LAYER 2 DATA FLOW

#### Input Interface Design

**What Layer 2 Expects from Layer 1:**

```python
# Expected data structure
ProcessedArticle = {
    "article_id": str,
    "content": {
        "title": str,
        "body": str,
        "summary": str (optional)
    },
    "metadata": {
        "source": str,
        "source_credibility": float,  # 0.00-1.00
        "publish_timestamp": datetime,
        "language_original": str,
        "translation_confidence": float
    },
    "initial_classification": {
        "source_category": str (optional),
        "keywords": List[str],
        "detected_language": str
    },
    "quality": {
        "credibility_score": float,
        "word_count": int,
        "is_duplicate": bool,
        "related_articles": List[str]
    },
    "entities": {  # Optional, enhanced if available
        "locations": List[str],
        "organizations": List[str],
        "persons": List[str],
        "dates": List[str],
        "amounts": List[dict]
    }
}
```

#### Mock Data Generation Strategy

**Phase 1: Static Mock Data (Initial Development)**

**Purpose**: Enable Layer 2 development before Layer 1 is complete

**Approach:**
```
Create realistic mock data files:
├── /mock_data/articles_political.json
├── /mock_data/articles_economic.json
├── /mock_data/articles_social.json
├── /mock_data/articles_environmental.json
└── /mock_data/articles_mixed.json

Each file contains 50-100 pre-crafted articles covering:
- Various indicator scenarios
- Different time periods (last 30 days)
- Multiple sources (varying credibility)
- Diverse keywords and entities
```

**Mock Data Generator Script:**
```
MockDataGenerator:
├── Template-based article generation
├── Realistic timestamp distribution
├── Credibility score variation
├── Keyword injection based on indicator
└── Export to JSON format compatible with Layer 2 ingestion
```

**Example Mock Article:**
```json
{
    "article_id": "mock_pol_001",
    "content": {
        "title": "Transport workers announce nationwide strike",
        "body": "The Ceylon Transport Board employees union announced a 48-hour nationwide strike starting next Monday, demanding better working conditions and wage increases. The strike is expected to affect bus services across all provinces, potentially disrupting daily commutes for thousands of workers...",
        "summary": "Transport workers to strike for 48 hours demanding better conditions"
    },
    "metadata": {
        "source": "Daily Mirror",
        "source_credibility": 0.85,
        "publish_timestamp": "2025-11-28T14:30:00Z",
        "language_original": "en",
        "translation_confidence": 1.0
    },
    "initial_classification": {
        "source_category": "Labor",
        "keywords": ["strike", "transport", "workers", "union", "nationwide"],
        "detected_language": "en"
    },
    "quality": {
        "credibility_score": 0.85,
        "word_count": 156,
        "is_duplicate": false,
        "related_articles": []
    },
    "entities": {
        "locations": ["nationwide", "all provinces"],
        "organizations": ["Ceylon Transport Board", "employees union"],
        "persons": [],
        "dates": ["next Monday", "48-hour"],
        "amounts": []
    }
}
```

**Phase 2: Dynamic Mock Data (Testing & Simulation)**

**Purpose**: Simulate real-time data flow

**Mock Data Simulator:**
```
Features:
├── Time-based article generation (new articles every 15 min)
├── Scenario simulation:
│   ├── Crisis scenario (fuel shortage)
│   ├── Positive trend (tourism recovery)
│   ├── Mixed signals (election uncertainty)
│   └── Normal operations baseline
├── Realistic volume patterns:
│   ├── Higher activity during business hours
│   ├── Breaking news spikes
│   └── Weekend lulls
└── Event sequences:
    └── Related articles over time (story evolution)
```

**Phase 3: Integration with Real Layer 1**

**Hybrid Approach:**
```
Data Source Priority:
1. Real Layer 1 data (when available)
2. Mock data fallback (if Layer 1 down or insufficient volume)
3. Historical replay (past real data for testing)

Configuration:
├── data_source_mode: "mock" | "real" | "hybrid"
├── mock_data_ratio: 0.0 - 1.0 (percentage of mock in hybrid)
└── fallback_enabled: true/false
```

#### Data Ingestion Module Architecture

**Ingestion Pipeline:**

```
┌─────────────────────────────────────────┐
│      ARTICLE INGESTION LAYER            │
└─────────────────────────────────────────┘

Layer 1 Output / Mock Data Source
            ↓
    ┌───────────────┐
    │  Data Fetcher │
    │  - Pull from Layer 1 DB
    │  - Load mock files
    │  - Stream new articles
    └───────────────┘
            ↓
    ┌───────────────┐
    │  Validator    │
    │  - Schema check
    │  - Required fields
    │  - Data quality
    └───────────────┘
            ↓
    ┌───────────────┐
    │  Preprocessor │
    │  - Text cleanup
    │  - Entity extraction
    │  - Keyword normalization
    └───────────────┘
            ↓
    ┌───────────────┐
    │  Queue Manager│
    │  - Redis queue
    │  - Priority sorting
    │  - Batch formation
    └───────────────┘
            ↓
    Indicator Assignment Pipeline
```

**Implementation Pseudo-Logic:**

```
class ArticleIngestionService:
    
    def __init__(self, mode='hybrid'):
        self.mode = mode
        self.mock_loader = MockDataLoader()
        self.layer1_connector = Layer1DatabaseConnector()
        self.queue = RedisQueue('articles_for_processing')
    
    def fetch_articles(self, time_window):
        """Fetch articles from configured sources"""
        
        if self.mode == 'mock':
            return self.mock_loader.get_articles(time_window)
        
        elif self.mode == 'real':
            return self.layer1_connector.fetch_processed_articles(time_window)
        
        elif self.mode == 'hybrid':
            real_articles = self.layer1_connector.fetch_processed_articles(time_window)
            if len(real_articles) < MIN_THRESHOLD:
                mock_articles = self.mock_loader.get_articles(time_window)
                return real_articles + mock_articles[:SUPPLEMENT_COUNT]
            return real_articles
    
    def validate_article(self, article):
        """Ensure article has required structure"""
        required_fields = ['article_id', 'content', 'metadata', 'quality']
        
        for field in required_fields:
            if field not in article:
                raise ValidationError(f"Missing required field: {field}")
        
        # Check content quality
        if article['quality']['credibility_score'] < MIN_CREDIBILITY:
            return False  # Skip low quality
        
        if article['quality']['is_duplicate']:
            return False  # Skip duplicates
        
        return True
    
    def preprocess_article(self, article):
        """Additional processing before indicator assignment"""
        
        # Extract additional keywords if not present
        if not article['initial_classification'].get('keywords'):
            article['initial_classification']['keywords'] = \
                self.keyword_extractor.extract(article['content']['body'])
        
        # Extract entities if not present
        if not article.get('entities'):
            article['entities'] = self.entity_extractor.extract(
                article['content']['body']
            )
        
        # Normalize text
        article['content']['body_normalized'] = \
            self.text_normalizer.normalize(article['content']['body'])
        
        return article
    
    def ingest_batch(self, batch_size=50):
        """Main ingestion loop"""
        
        # Fetch new articles
        articles = self.fetch_articles(last_hours=1)
        
        processed_count = 0
        for article in articles:
            try:
                # Validate
                if not self.validate_article(article):
                    continue
                
                # Preprocess
                article = self.preprocess_article(article)
                
                # Add to processing queue
                self.queue.add(article, priority=self._calculate_priority(article))
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error ingesting article {article.get('article_id')}: {e}")
        
        logger.info(f"Ingested {processed_count} articles")
        return processed_count
    
    def _calculate_priority(self, article):
        """Determine processing priority"""
        
        # Breaking news = high priority
        age_hours = (datetime.now() - article['metadata']['publish_timestamp']).hours
        if age_hours < 2:
            return 1  # High priority
        
        # High credibility = medium priority
        if article['quality']['credibility_score'] > 0.8:
            return 3
        
        # Default priority
        return 5
```

---

## INDICATOR GENERATION FRAMEWORK {#indicator-generation}

### 2.4 CORE INDICATOR PROCESSING ARCHITECTURE

#### Classification Strategy: Hybrid Approach

**The Three-Pass System:**

```
┌─────────────────────────────────────────────────────────────┐
│           INDICATOR ASSIGNMENT PIPELINE                      │
└─────────────────────────────────────────────────────────────┘

Article Input
      ↓
┌─────────────────┐
│  PASS 1:        │
│  Rule-Based     │ ← Fast keyword matching
│  Filtering      │   Eliminates obvious non-matches
└─────────────────┘   Assigns primary categories
      ↓
┌─────────────────┐
│  PASS 2:        │
│  ML             │ ← Multi-label classification
│  Classification │   Assigns specific indicators
└─────────────────┘   Provides confidence scores
      ↓
┌─────────────────┐
│  PASS 3:        │
│  Entity         │ ← Extract numeric values
│  Extraction     │   Extract locations, dates
└─────────────────┘   Extract organizations
      ↓
Article-Indicator Mappings
```

#### Pass 1: Rule-Based Filtering

**Purpose**: Fast elimination and obvious assignments

**Implementation Strategy:**

```
RuleBasedClassifier:
    
    Input: Article with keywords
    Output: List of candidate indicators with confidence
    
    Process:
    1. Load keyword mappings from indicator_keywords table
    2. Check article keywords against each indicator's keyword list
    3. Score matches based on:
       - Keyword frequency in article
       - Keyword relevance weight
       - Context keyword presence
       - Exclusion keyword absence
    4. Return top candidates (threshold: 0.3 confidence)
```

**Keyword Matching Logic:**

```python
class RuleBasedIndicatorAssigner:
    
    def __init__(self):
        self.keyword_mappings = self._load_keyword_mappings()
        # Structure: {indicator_id: {keywords, weights, context, exclusions}}
    
    def assign_indicators(self, article):
        """Assign indicators using keyword matching"""
        
        article_text = article['content']['title'] + " " + article['content']['body']
        article_keywords = set(article['initial_classification']['keywords'])
        
        candidate_indicators = []
        
        for indicator_id, rules in self.keyword_mappings.items():
            score = self._calculate_match_score(
                article_text,
                article_keywords,
                rules
            )
            
            if score >= RULE_BASED_THRESHOLD:
                candidate_indicators.append({
                    'indicator_id': indicator_id,
                    'confidence': score,
                    'method': 'rule_based',
                    'matched_keywords': self._get_matched_keywords(article_keywords, rules)
                })
        
        return sorted(candidate_indicators, key=lambda x: x['confidence'], reverse=True)
    
    def _calculate_match_score(self, text, keywords, rules):
        """Calculate how well article matches indicator rules"""
        
        score = 0.0
        
        # Check primary keywords
        for keyword in rules['keywords']:
            if keyword.lower() in text.lower():
                weight = rules['weights'].get(keyword, 1.0)
                score += weight
        
        # Bonus for context keywords (AND logic)
        if rules.get('requires_context'):
            context_met = all(
                ctx.lower() in text.lower() 
                for ctx in rules['context_keywords']
            )
            if context_met:
                score *= 1.5
            else:
                score *= 0.5  # Penalize if context missing
        
        # Check exclusions (NOT logic)
        for exclusion in rules.get('exclusions', []):
            if exclusion.lower() in text.lower():
                score *= 0.1  # Heavy penalty
        
        # Normalize to 0-1
        return min(score / rules['max_possible_score'], 1.0)
    
    def _get_matched_keywords(self, article_keywords, rules):
        """Return which keywords actually matched"""
        return list(set(article_keywords) & set(rules['keywords']))
```

**Example Rule Configuration:**

```yaml
# Stored in indicator_keywords table
Political_Unrest_Index:
  keywords:
    - protest
    - strike
    - demonstration
    - hartal
    - walkout
    - civil unrest
    - public gathering
  weights:
    protest: 1.0
    strike: 1.2
    hartal: 1.5
  context_keywords:
    - [] # No required context
  exclusions:
    - sports
    - entertainment
    - cultural
  max_possible_score: 10.0

Economic_Inflation_Index:
  keywords:
    - inflation
    - price increase
    - expensive
    - cost of living
    - rising prices
    - costly
  weights:
    inflation: 1.5
    price increase: 1.2
    expensive: 0.8
  context_keywords:
    - [food, fuel, commodity, goods]  # At least one must be present
  exclusions:
    - luxury
    - premium product
  max_possible_score: 8.0
```

---

This completes Part 1 of the Layer 2 blueprint. Part 2 will continue with ML Classification, Sentiment Analysis, Indicator Calculation, and advanced features.

