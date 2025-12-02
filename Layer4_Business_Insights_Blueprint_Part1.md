# LAYER 4: BUSINESS INSIGHTS ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan - PART 1

---

## TABLE OF CONTENTS - PART 1

1. [Phase 0: Strategic Analysis & Design Philosophy](#phase-0)
2. [Architectural Overview](#architectural-overview)
3. [Risk & Opportunity Framework](#risk-opportunity-framework)
4. [Database Architecture for Layer 4](#database-architecture)
5. [Mock Data Strategy](#mock-data)
6. [Risk Identification Engine](#risk-identification)
7. [Risk Scoring & Classification](#risk-scoring)
8. [Risk Detection Methods](#risk-detection-methods)

---

## PHASE 0: STRATEGIC ANALYSIS & DESIGN PHILOSOPHY {#phase-0}

### System Design Philosophy

**Core Purpose:**
Transform operational indicators into actionable business intelligence - answering the critical question: "So what should I DO about it?"

**The Intelligence Pyramid:**

```
Layer 1: "WHAT happened?" (Data Collection)
Layer 2: "HOW IS the nation?" (National Indicators)
Layer 3: "HOW DOES IT AFFECT ME?" (Operational Impact)
Layer 4: "WHAT SHOULD I DO?" (Business Insights) ← YOU ARE HERE
```

**The Critical Transformation:**

```
Operational Indicator          Business Insight
─────────────────────    →    ──────────────────────
"Supply Chain Risk: 75"       "HIGH RISK ALERT:
                               - Delivery delays: 80% probability
                               - Revenue impact: -20%
                               - Action required: 24 hours
                               
                               RECOMMENDED ACTIONS:
                               1. Secure backup logistics (today)
                               2. Communicate with customers
                               3. Review contingency plans
                               
                               OPPORTUNITY:
                               Competitors also affected -
                               differentiate with reliability"
```

**Key Design Principles:**

1. **Actionable Over Informational**: Every insight must lead to a decision or action
2. **Context-Aware**: Same indicator → Different insights for different businesses
3. **Prioritized**: Focus attention on what matters most (top 5 priorities)
4. **Time-Sensitive**: Urgent vs. can wait - different action timelines
5. **Evidence-Based**: Always show WHY and HOW CONFIDENT we are
6. **Learning System**: Improve accuracy through feedback loops

**The Two Intelligence Streams:**

```
DEFENSIVE INTELLIGENCE (Risk Management)
├── Identify threats before they materialize
├── Assess severity and probability
├── Recommend mitigation actions
└── Monitor for escalation

OFFENSIVE INTELLIGENCE (Opportunity Capture)
├── Spot favorable conditions
├── Assess value and feasibility
├── Recommend capture actions
└── Track success rate
```

### Conceptual Framework

**The Insight Generation Pipeline:**

```
Operational Indicators (from Layer 3)
        ↓
Context Integration (Company profile, industry, history)
        ↓
Pattern Recognition (ML + Rules)
        ↓
    ┌───┴───┐
    ↓       ↓
RISKS    OPPORTUNITIES
    ↓       ↓
Scoring & Classification
    ↓
Prioritization
    ↓
Recommendation Generation
    ↓
Action Planning
    ↓
Delivery to User
```

**Intelligence Types:**

```
1. DIAGNOSTIC INSIGHTS
   "Why is this happening?"
   Example: "Supply chain risk elevated due to port congestion +
            fuel shortage + weather conditions"

2. PREDICTIVE INSIGHTS
   "What will happen next?"
   Example: "Based on current trajectory, delivery delays will
            worsen in next 48 hours"

3. PRESCRIPTIVE INSIGHTS
   "What should be done?"
   Example: "Secure backup logistics today, notify customers,
            increase buffer stock"

4. COMPARATIVE INSIGHTS
   "How does this compare?"
   Example: "Your supply chain risk is 25% higher than
            industry average"

5. CONTEXTUAL INSIGHTS
   "What else is relevant?"
   Example: "Similar situation in May 2022 lasted 5 days,
            resulted in 30% revenue drop for logistics sector"
```

---

## ARCHITECTURAL OVERVIEW {#architectural-overview}

### The Complete Layer 4 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 4: BUSINESS INSIGHTS ENGINE                   │
└─────────────────────────────────────────────────────────────────┘

INPUT (From Layer 3):                OUTPUT (To Dashboard/User):
├── Operational indicators           ├── Prioritized risk alerts
├── Company profile                  ├── Opportunity recommendations
├── Industry benchmarks              ├── Action plans
├── Historical context               ├── Scenario forecasts
└── Real-time updates                └── Executive summaries

┌──────────────────────────────────────────────────────────────┐
│                     PROCESSING FLOW                           │
└──────────────────────────────────────────────────────────────┘

Layer 3 Operational Indicators
        ↓
┌────────────────────┐
│  Context Enricher  │ ← Company Profile
│  "Add business     │   Industry Templates
│   context"         │   Historical Data
└────────────────────┘
        ↓
    ┌───┴───┐
    ↓       ↓
┌─────────────┐  ┌─────────────┐
│Risk         │  │Opportunity  │
│Detector     │  │Detector     │
└─────────────┘  └─────────────┘
    ↓               ↓
┌─────────────┐  ┌─────────────┐
│Risk         │  │Opportunity  │
│Scorer       │  │Scorer       │
└─────────────┘  └─────────────┘
    ↓               ↓
    └───┬───────────┘
        ↓
┌────────────────────┐
│  Prioritizer       │
│  "What matters     │
│   most?"           │
└────────────────────┘
        ↓
┌────────────────────┐
│  Recommendation    │
│  Generator         │
│  "What to do?"     │
└────────────────────┘
        ↓
┌────────────────────┐
│  Narrative         │
│  Generator         │
│  "Explain it"      │
└────────────────────┘
        ↓
┌────────────────────┐
│  Alert Manager     │
│  "Notify user"     │
└────────────────────┘
        ↓
    Final Output
```

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
└─────────────────────────────────────────────────────────┘

Layer 3 Database (Operational Indicators)
    ↓
Indicator Pull Service (every 15 min)
    ↓
┌─────────────────────────────────┐
│  Real-Time Processing Queue     │
│  (Redis-based)                  │
└─────────────────────────────────┘
    ↓
Parallel Processors
    ↓
├─→ Risk Detection Engine
│   ├── Rule-Based Detector
│   ├── ML-Based Predictor
│   └── Pattern Recognizer
│       ↓
│   Risk Candidates
│
├─→ Opportunity Detection Engine
│   ├── Gap Analyzer
│   ├── Trend Spotter
│   └── Competitive Intel
│       ↓
│   Opportunity Candidates
│
└─→ Context Enricher
    ├── Historical Comparisons
    ├── Industry Benchmarks
    └── Company Specifics
        ↓
    Enriched Context
        ↓
    Scoring & Prioritization
        ↓
    Recommendation Generation
        ↓
    ├─→ PostgreSQL (Insights, recommendations, audit trail)
    ├─→ TimescaleDB (Insight time-series, tracking)
    ├─→ MongoDB (Detailed reasoning, narratives)
    └─→ Redis (Current alerts cache, priority queue)
        ↓
    API Layer
        ↓
    Dashboard / Notifications / Integrations
```

---

## RISK & OPPORTUNITY FRAMEWORK {#risk-opportunity-framework}

### 3.1 RISK TAXONOMY

**Complete Risk Category Structure:**

```
1. OPERATIONAL RISKS
   ├── Supply Chain Disruption
   │   ├── Import delays
   │   ├── Supplier failures
   │   ├── Logistics breakdowns
   │   └── Inventory shortages
   │
   ├── Workforce Disruption
   │   ├── Strike action
   │   ├── High absenteeism
   │   ├── Skill shortages
   │   └── Labor disputes
   │
   ├── Infrastructure Failure
   │   ├── Power outages
   │   ├── Internet disruptions
   │   ├── Water supply issues
   │   └── Transport infrastructure damage
   │
   ├── Service Quality Degradation
   │   ├── Capacity constraints
   │   ├── Process breakdowns
   │   └── Customer service failures
   │
   └── Security & Safety
       ├── Physical security threats
       ├── Workplace safety issues
       └── Natural disaster impacts

2. FINANCIAL RISKS
   ├── Revenue Risks
   │   ├── Demand decline
   │   ├── Customer loss
   │   ├── Price pressure
   │   └── Market contraction
   │
   ├── Cost Escalation
   │   ├── Input cost inflation
   │   ├── Currency impacts
   │   ├── Wage inflation
   │   └── Utility cost spikes
   │
   ├── Cash Flow Risks
   │   ├── Payment delays
   │   ├── Credit squeeze
   │   ├── Working capital pressure
   │   └── Collection issues
   │
   ├── Margin Compression
   │   ├── Cost-price squeeze
   │   ├── Competitive pricing
   │   └── Volume decline
   │
   └── Financial Market Risks
       ├── Currency volatility
       ├── Interest rate changes
       └── Credit availability

3. COMPETITIVE RISKS
   ├── Market Share Loss
   │   ├── Competitor gains
   │   ├── New entrants
   │   └── Substitute products
   │
   ├── Competitive Disadvantage
   │   ├── Technology gap
   │   ├── Cost disadvantage
   │   ├── Quality perception
   │   └── Brand weakness
   │
   └── Disruption Threats
       ├── Business model innovation
       ├── Technology disruption
       └── Regulatory advantages (for competitors)

4. REPUTATIONAL RISKS
   ├── Brand Damage
   │   ├── Negative publicity
   │   ├── Product failures
   │   ├── Service failures
   │   └── Ethical issues
   │
   ├── Customer Trust Erosion
   │   ├── Data breaches
   │   ├── Privacy concerns
   │   └── Broken promises
   │
   └── Social Media Backlash
       ├── Viral negative content
       └── Influencer criticism

5. COMPLIANCE & LEGAL RISKS
   ├── Regulatory Non-Compliance
   │   ├── New regulations
   │   ├── Policy violations
   │   └── Licensing issues
   │
   ├── Legal Liabilities
   │   ├── Contract disputes
   │   ├── Labor law issues
   │   └── Consumer protection
   │
   └── Tax & Accounting Risks
       ├── Tax policy changes
       └── Audit risks

6. STRATEGIC RISKS
   ├── Market Timing Risks
   │   ├── Expansion timing
   │   ├── Exit timing
   │   └── Investment timing
   │
   ├── Portfolio Risks
   │   ├── Product mix issues
   │   ├── Geographic concentration
   │   └── Customer concentration
   │
   └── Transformation Risks
       ├── Digital transformation failures
       ├── Organizational change resistance
       └── Strategic pivot challenges
```

### 3.2 OPPORTUNITY TAXONOMY

**Complete Opportunity Category Structure:**

```
1. MARKET OPPORTUNITIES
   ├── Demand Surge
   │   ├── Seasonal increases
   │   ├── Trend-driven demand
   │   ├── Recovery signals
   │   └── Unmet needs
   │
   ├── Competitor Weakness
   │   ├── Service disruptions
   │   ├── Quality issues
   │   ├── Financial troubles
   │   └── Management changes
   │
   ├── Market Gaps
   │   ├── Underserved segments
   │   ├── Product gaps
   │   ├── Geographic gaps
   │   └── Import substitution
   │
   ├── Customer Base Expansion
   │   ├── New customer segments
   │   ├── Cross-selling opportunities
   │   └── Geographic expansion
   │
   └── Pricing Power
       ├── Supply constraints (for competitors)
       ├── Quality differentiation
       └── Brand strength

2. COST OPTIMIZATION OPPORTUNITIES
   ├── Input Cost Reduction
   │   ├── Commodity price drops
   │   ├── Currency advantages
   │   ├── Supplier competition
   │   └── Bulk purchase opportunities
   │
   ├── Efficiency Gains
   │   ├── Process improvements
   │   ├── Technology adoption
   │   ├── Automation opportunities
   │   └── Waste reduction
   │
   ├── Negotiation Leverage
   │   ├── Supplier distress
   │   ├── Market oversupply
   │   └── Volume consolidation
   │
   └── Alternative Sourcing
       ├── Local alternatives
       ├── New suppliers
       └── Vertical integration

3. STRATEGIC OPPORTUNITIES
   ├── Partnerships & Alliances
   │   ├── Complementary businesses
   │   ├── Distribution partnerships
   │   ├── Technology partnerships
   │   └── Joint ventures
   │
   ├── Mergers & Acquisitions
   │   ├── Distressed assets
   │   ├── Consolidation plays
   │   ├── Vertical integration
   │   └── Market entry acquisitions
   │
   ├── Policy & Regulatory Benefits
   │   ├── Incentive programs
   │   ├── Tax benefits
   │   ├── Special economic zones
   │   └── Government support programs
   │
   ├── Innovation Windows
   │   ├── Regulatory sandboxes
   │   ├── Technology breakthroughs
   │   ├── Patent opportunities
   │   └── R&D collaboration
   │
   └── Brand Building
       ├── Positive sentiment waves
       ├── Cultural moments
       ├── CSR opportunities
       └── Thought leadership

4. TALENT OPPORTUNITIES
   ├── Skilled Labor Availability
   │   ├── Industry layoffs
   │   ├── Returning diaspora
   │   ├── University graduates
   │   └── Competitor turnover
   │
   ├── Training & Development
   │   ├── Government programs
   │   ├── International partnerships
   │   └── Skill gap filling
   │
   └── Culture & Retention
       ├── Employer brand building
       └── Competitive advantage

5. FINANCIAL OPPORTUNITIES
   ├── Funding Availability
   │   ├── New credit facilities
   │   ├── Investor interest
   │   ├── Grants & subsidies
   │   └── Venture capital
   │
   ├── Capital Structure Optimization
   │   ├── Refinancing opportunities
   │   ├── Interest rate advantages
   │   └── Debt restructuring
   │
   └── Currency Advantages
       ├── Export opportunities
       ├── Import savings
       └── Hedging opportunities

6. INNOVATION OPPORTUNITIES
   ├── Product Innovation
   │   ├── New product gaps
   │   ├── Feature enhancements
   │   └── Service bundling
   │
   ├── Process Innovation
   │   ├── Digital transformation
   │   ├── Automation
   │   └── Business model evolution
   │
   └── Technology Adoption
       ├── AI/ML applications
       ├── Cloud migration
       └── IoT integration
```

---

## DATABASE ARCHITECTURE FOR LAYER 4 {#database-architecture}

### 3.3 MULTI-DATABASE STRATEGY

**Database Responsibility Matrix:**

```
PostgreSQL:       Risk/opportunity definitions, insights metadata, 
                  action plans, user feedback
TimescaleDB:      Insight time-series, tracking over time,
                  historical patterns
MongoDB:          Detailed reasoning, narratives, calculation details,
                  recommendation logic
Redis:            Current active alerts, priority queues, 
                  real-time scoring cache
```

#### PostgreSQL Schema

**Table 1: `risk_opportunity_definitions`**
```sql
/*
Purpose: Define all possible risk and opportunity types
Responsibility: Master catalog of business insights
*/

CREATE TABLE risk_opportunity_definitions (
    definition_id SERIAL PRIMARY KEY,
    
    -- Identification
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    display_name VARCHAR(200),
    
    -- Classification
    type VARCHAR(20) NOT NULL,              -- 'risk' or 'opportunity'
    category VARCHAR(50) NOT NULL,
    -- For risks: 'operational', 'financial', 'competitive', 'reputational', 'compliance', 'strategic'
    -- For opportunities: 'market', 'cost', 'strategic', 'talent', 'financial', 'innovation'
    
    subcategory VARCHAR(100),
    
    -- Trigger conditions
    trigger_logic JSONB NOT NULL,
    /* Structure:
    {
        "conditions": [
            {
                "operational_indicator": "OPS_SUPPLY_CHAIN",
                "operator": "less_than",
                "threshold": 60,
                "weight": 0.4
            },
            {
                "operational_indicator": "OPS_TRANSPORT_AVAIL",
                "operator": "less_than",
                "threshold": 50,
                "weight": 0.3
            }
        ],
        "logic": "AND",  // or "OR"
        "confidence_threshold": 0.6
    }
    */
    
    -- Scoring configuration
    impact_formula TEXT,
    probability_formula TEXT,
    urgency_formula TEXT,
    
    -- Default values
    default_impact DECIMAL(4,2),
    default_probability DECIMAL(3,2),
    default_urgency INTEGER,
    
    -- Applicability
    applicable_industries TEXT[],
    applicable_business_scales TEXT[],
    
    -- Content
    description_template TEXT,
    explanation_template TEXT,
    
    -- Recommendations
    immediate_actions JSONB,
    short_term_actions JSONB,
    medium_term_actions JSONB,
    
    -- Metadata
    severity_mapping JSONB,
    /* Structure:
    {
        "critical": {"min_score": 40, "max_score": 50, "color": "red"},
        "high": {"min_score": 30, "max_score": 39, "color": "orange"},
        "medium": {"min_score": 15, "max_score": 29, "color": "yellow"},
        "low": {"min_score": 0, "max_score": 14, "color": "green"}
    }
    */
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Indexes
CREATE INDEX idx_risk_opp_type ON risk_opportunity_definitions(type);
CREATE INDEX idx_risk_opp_category ON risk_opportunity_definitions(category);
CREATE INDEX idx_risk_opp_active ON risk_opportunity_definitions(is_active);
```

**Table 2: `business_insights`**
```sql
/*
Purpose: Store generated business insights (risks and opportunities)
Responsibility: Current and historical insights for each company
*/

CREATE TABLE business_insights (
    insight_id SERIAL PRIMARY KEY,
    
    -- Reference
    definition_id INTEGER REFERENCES risk_opportunity_definitions(definition_id),
    company_id VARCHAR(50) NOT NULL,
    
    -- Classification
    insight_type VARCHAR(20) NOT NULL,      -- 'risk' or 'opportunity'
    category VARCHAR(50) NOT NULL,
    
    -- Identification
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Scoring
    probability DECIMAL(3,2),               -- 0.00 to 1.00
    impact DECIMAL(4,2),                    -- 0 to 10
    urgency INTEGER,                        -- 1 to 5
    confidence DECIMAL(3,2),                -- 0.00 to 1.00
    
    final_score DECIMAL(6,2),
    severity_level VARCHAR(20),             -- 'critical', 'high', 'medium', 'low'
    
    -- Temporal
    detected_at TIMESTAMP NOT NULL,
    expected_impact_time TIMESTAMP,
    expected_duration_hours INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',
    -- 'active', 'acknowledged', 'in_progress', 'resolved', 'expired'
    
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    
    -- Impact tracking
    actual_impact TEXT,
    actual_outcome TEXT,
    lessons_learned TEXT,
    
    -- Related data
    triggering_indicators JSONB,
    /* Structure:
    [
        {
            "indicator_code": "OPS_SUPPLY_CHAIN",
            "value": 55,
            "threshold": 60,
            "contribution": 0.4
        }
    ]
    */
    
    related_insights INTEGER[],
    affected_operations TEXT[],
    
    -- Priority
    priority_rank INTEGER,
    is_urgent BOOLEAN DEFAULT FALSE,
    requires_immediate_action BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_insights_company ON business_insights(company_id, detected_at DESC);
CREATE INDEX idx_insights_type ON business_insights(insight_type, severity_level);
CREATE INDEX idx_insights_status ON business_insights(status, detected_at DESC);
CREATE INDEX idx_insights_priority ON business_insights(priority_rank, detected_at DESC) WHERE status = 'active';
CREATE INDEX idx_insights_urgent ON business_insights(is_urgent, detected_at DESC) WHERE is_urgent = TRUE;
```

**Table 3: `insight_recommendations`**
```sql
/*
Purpose: Store specific action recommendations for insights
Responsibility: Actionable guidance for each insight
*/

CREATE TABLE insight_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    insight_id INTEGER REFERENCES business_insights(insight_id),
    
    -- Recommendation details
    category VARCHAR(50),                   -- 'immediate', 'short_term', 'medium_term', 'long_term'
    priority INTEGER,                       -- 1 = highest
    
    action_title VARCHAR(200) NOT NULL,
    action_description TEXT,
    
    -- Implementation details
    responsible_role VARCHAR(100),          -- 'CEO', 'Operations Manager', 'Finance', etc.
    estimated_effort VARCHAR(50),          -- 'Low', 'Medium', 'High'
    estimated_cost VARCHAR(50),
    estimated_timeframe VARCHAR(100),       -- '24 hours', 'This week', 'This month'
    
    -- Expected outcomes
    expected_benefit TEXT,
    success_metrics TEXT[],
    
    -- Resources needed
    required_resources JSONB,
    /* Structure:
    {
        "budget": 50000,
        "personnel": ["Operations Manager", "2 logistics staff"],
        "tools": ["Backup generator", "Fuel reserve"],
        "time": "2 days"
    }
    */
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending',
    -- 'pending', 'in_progress', 'completed', 'dismissed'
    
    assigned_to VARCHAR(100),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Outcomes
    implementation_notes TEXT,
    outcome_achieved BOOLEAN,
    actual_benefit TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recommendations_insight ON insight_recommendations(insight_id);
CREATE INDEX idx_recommendations_status ON insight_recommendations(status, priority);
```

**Table 4: `insight_feedback`**
```sql
/*
Purpose: Capture user feedback on insights for learning
Responsibility: Enable system improvement through feedback loops
*/

CREATE TABLE insight_feedback (
    feedback_id SERIAL PRIMARY KEY,
    insight_id INTEGER REFERENCES business_insights(insight_id),
    company_id VARCHAR(50) NOT NULL,
    
    -- Feedback type
    feedback_type VARCHAR(50),
    -- 'accuracy', 'relevance', 'usefulness', 'outcome'
    
    -- Ratings (1-5 scale)
    accuracy_rating INTEGER,                -- Was prediction accurate?
    relevance_rating INTEGER,               -- Was it relevant to business?
    usefulness_rating INTEGER,              -- Was it helpful?
    timeliness_rating INTEGER,              -- Was it timely?
    
    -- Qualitative feedback
    comments TEXT,
    
    -- Outcome verification
    did_risk_materialize BOOLEAN,
    did_opportunity_exist BOOLEAN,
    was_action_taken BOOLEAN,
    action_effectiveness VARCHAR(50),       -- 'very_effective', 'somewhat', 'not_effective'
    
    -- Impact assessment
    actual_business_impact TEXT,
    financial_impact_estimate DECIMAL(15,2),
    
    -- Improvement suggestions
    what_was_wrong TEXT,
    what_was_missing TEXT,
    suggestions TEXT,
    
    -- Metadata
    provided_by VARCHAR(100),
    provided_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_insight ON insight_feedback(insight_id);
CREATE INDEX idx_feedback_company ON insight_feedback(company_id, provided_at DESC);
```

**Table 5: `scenario_simulations`**
```sql
/*
Purpose: Store "what-if" scenario analyses
Responsibility: Scenario planning and contingency analysis
*/

CREATE TABLE scenario_simulations (
    simulation_id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) NOT NULL,
    
    -- Scenario details
    scenario_name VARCHAR(200) NOT NULL,
    scenario_description TEXT,
    
    -- Input assumptions
    assumptions JSONB NOT NULL,
    /* Structure:
    {
        "duration": "2 weeks",
        "severity": "high",
        "affected_indicators": {
            "ECON_FUEL_AVAIL": 20,
            "OPS_TRANSPORT_AVAIL": 30
        }
    }
    */
    
    -- Simulation results
    predicted_risks JSONB,
    predicted_opportunities JSONB,
    estimated_impact JSONB,
    /* Structure:
    {
        "revenue_impact": -250000,
        "cost_impact": +75000,
        "operational_disruption_days": 10,
        "market_share_impact": -2.5
    }
    */
    
    -- Recommendations
    recommended_contingencies JSONB,
    preparation_actions JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft',
    -- 'draft', 'active', 'archived'
    
    -- Metadata
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scenarios_company ON scenario_simulations(company_id, created_at DESC);
CREATE INDEX idx_scenarios_status ON scenario_simulations(status);
```

**Table 6: `competitive_intelligence`**
```sql
/*
Purpose: Track competitor-related insights
Responsibility: Competitive advantage opportunities
*/

CREATE TABLE competitive_intelligence (
    intel_id SERIAL PRIMARY KEY,
    company_id VARCHAR(50) NOT NULL,
    
    -- Competitor information
    competitor_name VARCHAR(200),
    competitor_industry VARCHAR(100),
    
    -- Intelligence type
    intel_type VARCHAR(50),
    -- 'weakness', 'strength', 'movement', 'vulnerability'
    
    -- Details
    description TEXT,
    source VARCHAR(200),                    -- Where this intel came from
    confidence_level DECIMAL(3,2),
    
    -- Impact on your business
    relevance_score DECIMAL(3,2),
    potential_opportunity TEXT,
    suggested_response TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'new',
    -- 'new', 'monitoring', 'acted_on', 'expired'
    
    -- Temporal
    detected_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_competitive_intel_company ON competitive_intelligence(company_id, detected_at DESC);
CREATE INDEX idx_competitive_intel_status ON competitive_intelligence(status);
```

#### TimescaleDB Schema

**Hypertable 1: `insight_tracking`**
```sql
/*
Purpose: Track insights over time for trend analysis
Responsibility: Historical insight patterns
*/

CREATE TABLE insight_tracking (
    time TIMESTAMPTZ NOT NULL,
    company_id VARCHAR(50) NOT NULL,
    
    -- Daily snapshot
    total_active_risks INTEGER,
    total_active_opportunities INTEGER,
    
    -- By severity
    critical_risks INTEGER,
    high_risks INTEGER,
    medium_risks INTEGER,
    low_risks INTEGER,
    
    -- By category
    operational_risks INTEGER,
    financial_risks INTEGER,
    competitive_risks INTEGER,
    reputational_risks INTEGER,
    compliance_risks INTEGER,
    strategic_risks INTEGER,
    
    -- Opportunities
    market_opportunities INTEGER,
    cost_opportunities INTEGER,
    strategic_opportunities INTEGER,
    
    -- Actions
    recommendations_generated INTEGER,
    actions_taken INTEGER,
    actions_completed INTEGER,
    
    -- Outcomes
    risks_materialized INTEGER,
    risks_avoided INTEGER,
    opportunities_captured INTEGER,
    opportunities_missed INTEGER,
    
    PRIMARY KEY (time, company_id)
);

SELECT create_hypertable('insight_tracking', 'time');

CREATE INDEX idx_insight_tracking_company ON insight_tracking(company_id, time DESC);
```

**Hypertable 2: `insight_score_history`**
```sql
/*
Purpose: Track how insight scores change over time
Responsibility: Monitor risk/opportunity evolution
*/

CREATE TABLE insight_score_history (
    time TIMESTAMPTZ NOT NULL,
    insight_id INTEGER NOT NULL,
    
    -- Score components
    probability DECIMAL(3,2),
    impact DECIMAL(4,2),
    urgency INTEGER,
    confidence DECIMAL(3,2),
    
    final_score DECIMAL(6,2),
    severity_level VARCHAR(20),
    
    -- Contributing factors
    triggering_indicators JSONB,
    
    PRIMARY KEY (time, insight_id)
);

SELECT create_hypertable('insight_score_history', 'time');

CREATE INDEX idx_score_history_insight ON insight_score_history(insight_id, time DESC);
```

#### MongoDB Schema

**Collection 1: `insight_reasoning`**
```javascript
/*
Purpose: Store detailed reasoning behind each insight
Use: Explainability, debugging, audit trail
*/

{
    _id: ObjectId("..."),
    insight_id: 123,
    company_id: "abc_retail_001",
    generated_at: ISODate("2025-12-01T10:00:00Z"),
    
    reasoning: {
        trigger_analysis: {
            primary_trigger: {
                indicator: "OPS_SUPPLY_CHAIN",
                value: 55,
                threshold: 60,
                deviation: -5,
                weight: 0.40
            },
            
            secondary_triggers: [
                {
                    indicator: "OPS_TRANSPORT_AVAIL",
                    value: 45,
                    threshold: 50,
                    deviation: -5,
                    weight: 0.30
                },
                {
                    indicator: "ECON_FUEL_AVAIL",
                    value: 40,
                    threshold: 50,
                    deviation: -10,
                    weight: 0.30
                }
            ],
            
            combined_signal_strength: 0.85
        },
        
        scoring_breakdown: {
            probability: {
                base_probability: 0.70,
                adjustments: [
                    {factor: "historical_pattern", adjustment: +0.10},
                    {factor: "trend_strength", adjustment: +0.05}
                ],
                final_probability: 0.85
            },
            
            impact: {
                base_impact: 7.0,
                adjustments: [
                    {factor: "company_dependency", multiplier: 1.2},
                    {factor: "business_scale", multiplier: 1.1}
                ],
                final_impact: 9.24
            },
            
            urgency: {
                time_to_impact_hours: 48,
                urgency_score: 4,
                reasoning: "Expected within 48 hours"
            },
            
            confidence: {
                data_quality: 0.85,
                source_reliability: 0.90,
                pattern_match_strength: 0.80,
                final_confidence: 0.85
            }
        },
        
        final_calculation: {
            formula: "Probability × Impact × Urgency × Confidence",
            computation: "0.85 × 9.24 × 4 × 0.85",
            raw_score: 26.77,
            normalized_score: 26.77,
            severity: "high"
        },
        
        contextual_factors: {
            historical_comparison: {
                similar_event: "2022-05-15 Fuel Crisis",
                similarity_score: 0.78,
                outcome: "Delivery delays lasted 5 days, 30% revenue impact"
            },
            
            industry_context: {
                industry_avg_risk_score: 18.5,
                your_score_deviation: +8.27,
                interpretation: "Significantly higher risk than industry"
            },
            
            company_specifics: {
                import_dependency: 0.60,
                fleet_dependency: "high",
                buffer_stock_days: 3,
                vulnerability_assessment: "High exposure due to low inventory buffer"
            }
        }
    },
    
    narrative: {
        headline: "Critical Supply Chain Disruption Risk",
        
        summary: "High probability (85%) of significant supply chain disruptions within the next 48 hours. Multiple indicators show deteriorating conditions: supply chain integrity at 55, transport availability at 45, and fuel availability at 40.",
        
        explanation: "Your business is at elevated risk due to 60% import dependency and only 3 days of buffer stock. Similar conditions in May 2022 resulted in 5-day delivery delays and 30% revenue impact for retail sector.",
        
        impact_statement: "Expected impacts: Delivery delays, potential stock-outs of imported goods, customer dissatisfaction, estimated 20-25% revenue impact if prolonged beyond 3 days."
    }
}

// Indexes
db.insight_reasoning.createIndex({"insight_id": 1})
db.insight_reasoning.createIndex({"company_id": 1, "generated_at": -1})
```

**Collection 2: `recommendation_details`**
```javascript
/*
Purpose: Detailed recommendation logic and implementation guidance
Use: Action planning, execution support
*/

{
    _id: ObjectId("..."),
    insight_id: 123,
    recommendation_id: 456,
    
    recommendation: {
        category: "immediate",
        priority: 1,
        
        action: {
            title: "Secure Emergency Logistics",
            description: "Contact backup logistics partners and secure delivery capacity for next 7 days",
            
            rationale: "Primary logistics partner likely to face severe fuel shortage. Backup capacity needed to maintain customer commitments.",
            
            steps: [
                {
                    step: 1,
                    action: "Call XYZ Backup Logistics",
                    details: "Request availability for urgent deliveries",
                    responsible: "Operations Manager",
                    deadline: "Today 3pm",
                    estimated_time: "30 minutes"
                },
                {
                    step: 2,
                    action: "Secure fuel allocation",
                    details: "Pre-purchase fuel for company fleet - minimum 2 week supply",
                    responsible: "Procurement",
                    deadline: "Today 5pm",
                    estimated_time: "2 hours",
                    estimated_cost: "LKR 500,000"
                },
                {
                    step: 3,
                    action: "Customer communication",
                    details: "Prepare and send proactive email to key customers about potential delays",
                    responsible: "Customer Service Manager",
                    deadline: "Today 6pm",
                    estimated_time: "1 hour"
                }
            ]
        },
        
        resources: {
            financial: {
                immediate_cost: 500000,
                currency: "LKR",
                breakdown: [
                    {item: "Fuel pre-purchase", amount: 400000},
                    {item: "Backup logistics premium", amount: 100000}
                ]
            },
            
            personnel: [
                {role: "Operations Manager", time: "4 hours"},
                {role: "Procurement Officer", time: "3 hours"},
                {role: "Customer Service Manager", time: "2 hours"}
            ],
            
            tools: [
                "Backup logistics contact list",
                "Customer communication template",
                "Emergency procurement approval"
            ]
        },
        
        expected_outcomes: {
            primary: "Maintain delivery commitments despite supply chain disruption",
            
            metrics: [
                {
                    metric: "On-time delivery rate",
                    current: "95%",
                    target: "Maintain >90%",
                    measurement: "Daily tracking"
                },
                {
                    metric: "Customer satisfaction",
                    current: "4.2/5",
                    target: "Maintain >4.0",
                    measurement: "Survey responses"
                }
            ],
            
            risk_reduction: "Reduces delivery delay probability from 80% to 30%"
        },
        
        alternatives: [
            {
                option: "Delay all non-critical deliveries",
                pros: ["Lower immediate cost", "Less complex"],
                cons: ["Customer dissatisfaction", "Revenue loss"],
                recommendation: "Not recommended - reputational damage"
            }
        ],
        
        dependencies: [
            "Backup logistics partner availability",
            "Fuel supply availability",
            "Management approval for emergency spending"
        ],
        
        risk_factors: [
            "Backup partner may also face fuel issues",
            "Cost may exceed estimate if premium prices charged",
            "Customer communication may not prevent all complaints"
        ]
    },
    
    implementation_guidance: {
        do: [
            "Act quickly - situation deteriorating",
            "Over-communicate with customers",
            "Document all costs for analysis"
        ],
        
        dont: [
            "Wait for confirmation - be proactive",
            "Promise specific delivery dates",
            "Exhaust all fuel reserves"
        ],
        
        watch_for: [
            "Fuel prices spiking suddenly",
            "Backup logistics partner reliability",
            "Customer sentiment on social media"
        ]
    }
}

// Indexes
db.recommendation_details.createIndex({"insight_id": 1})
db.recommendation_details.createIndex({"recommendation_id": 1})
```

#### Redis Schema

**Key Patterns:**

```
Purpose: Fast access to current active insights

Key Patterns:
├── company:insights:{company_id}
│   └── Hash: Current active insights summary
│       {
│         "critical_risks": "3",
│         "high_risks": "7",
│         "active_opportunities": "4",
│         "urgent_actions": "5",
│         "last_updated": "2025-12-01T10:00:00Z"
│       }
│
├── insight:current:{insight_id}
│   └── Hash: Current insight state
│       {
│         "score": "26.77",
│         "severity": "high",
│         "status": "active",
│         "priority_rank": "2"
│       }
│
├── priority:queue:{company_id}
│   └── Sorted Set: Insights ranked by priority
│       [
│         {"insight_id": 123, "score": 26.77},
│         {"insight_id": 124, "score": 23.50}
│       ]
│
├── alert:pending:{company_id}
│   └── List: Pending alert deliveries
│       [
│         {"insight_id": 123, "alert_type": "email", "scheduled_at": "..."}
│       ]
│
└── calculation:cache:{cache_key}
    └── Hash: Cached calculation results
        TTL: 15 minutes
```

---

This completes Part 1 of the Layer 4 blueprint. Part 2 will continue with Risk Detection Methods, Opportunity Detection, Scoring Algorithms, Recommendation Engine, and Implementation Checklist.

