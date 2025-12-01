# LAYER 4: BUSINESS INSIGHTS ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan - PART 2

---

## TABLE OF CONTENTS - PART 2

1. [Risk Detection Methods](#risk-detection-methods)
2. [Opportunity Detection Methods](#opportunity-detection)
3. [Scoring & Prioritization](#scoring-prioritization)
4. [Recommendation Engine](#recommendation-engine)
5. [Contextual Intelligence](#contextual-intelligence)
6. [Mock Data Strategy](#mock-data)
7. [ML Integration](#ml-integration)
8. [Feedback & Learning System](#feedback-learning)
9. [Iteration 1 Implementation Checklist](#iteration-1)
10. [Iteration 2 Advanced Features](#iteration-2)
11. [Integration & Testing](#integration-testing)

---

## RISK DETECTION METHODS {#risk-detection-methods}

### 4.1 THREE-TIER DETECTION SYSTEM

```
Tier 1: Rule-Based Detection (Fast, Deterministic)
    ↓
Tier 2: Pattern Recognition (Historical Patterns)
    ↓
Tier 3: ML-Based Prediction (Advanced, Learning)
```

#### Tier 1: Rule-Based Risk Detection

**Purpose**: Fast, reliable detection of known risk patterns

**Implementation:**

```python
class RuleBasedRiskDetector:
    
    def __init__(self):
        self.risk_rules = self._load_risk_rules()
    
    def detect_risks(self, operational_indicators, company_profile):
        """
        Evaluate all rule-based risk conditions
        """
        
        detected_risks = []
        
        for risk_def in self.risk_rules:
            # Evaluate trigger conditions
            is_triggered = self._evaluate_conditions(
                risk_def['trigger_logic'],
                operational_indicators,
                company_profile
            )
            
            if is_triggered:
                # Calculate risk score
                risk = self._generate_risk(risk_def, operational_indicators, company_profile)
                detected_risks.append(risk)
        
        return detected_risks
    
    def _evaluate_conditions(self, trigger_logic, indicators, profile):
        """
        Evaluate trigger conditions using boolean logic
        
        Example trigger_logic:
        {
            "conditions": [
                {"indicator": "OPS_SUPPLY_CHAIN", "operator": "<", "threshold": 60},
                {"indicator": "OPS_TRANSPORT_AVAIL", "operator": "<", "threshold": 50}
            ],
            "logic": "AND"  # or "OR"
        }
        """
        
        condition_results = []
        
        for condition in trigger_logic['conditions']:
            indicator_code = condition['indicator']
            operator = condition['operator']
            threshold = condition['threshold']
            
            # Get current indicator value
            current_value = self._get_indicator_value(indicator_code, indicators)
            
            # Evaluate condition
            if operator == 'less_than' or operator == '<':
                result = current_value < threshold
            elif operator == 'greater_than' or operator == '>':
                result = current_value > threshold
            elif operator == 'equals' or operator == '==':
                result = current_value == threshold
            elif operator == 'between':
                result = condition['min'] <= current_value <= condition['max']
            else:
                result = False
            
            # Apply weight if specified
            weight = condition.get('weight', 1.0)
            condition_results.append((result, weight))
        
        # Combine results based on logic
        logic = trigger_logic.get('logic', 'AND')
        
        if logic == 'AND':
            # All conditions must be true
            return all(result for result, weight in condition_results)
        
        elif logic == 'OR':
            # At least one condition must be true
            return any(result for result, weight in condition_results)
        
        elif logic == 'WEIGHTED':
            # Weighted combination
            total_weight = sum(weight for result, weight in condition_results)
            triggered_weight = sum(weight for result, weight in condition_results if result)
            threshold = trigger_logic.get('threshold', 0.6)
            return (triggered_weight / total_weight) >= threshold
        
        return False
    
    def _generate_risk(self, risk_def, indicators, profile):
        """
        Generate risk object with initial scoring
        """
        
        return {
            'definition_id': risk_def['definition_id'],
            'code': risk_def['code'],
            'name': risk_def['name'],
            'category': risk_def['category'],
            'type': 'risk',
            'triggering_indicators': self._get_triggering_values(risk_def, indicators),
            'detection_method': 'rule_based',
            'confidence': 0.8  # High confidence for rule-based
        }
```

**Example Risk Rules:**

```yaml
# Supply Chain Disruption Risk
code: "RISK_SUPPLY_CHAIN_DISRUPTION"
name: "Supply Chain Disruption Risk"
category: "operational"

trigger_logic:
  conditions:
    - indicator: "OPS_SUPPLY_CHAIN"
      operator: "less_than"
      threshold: 60
      weight: 0.4
    
    - indicator: "OPS_TRANSPORT_AVAIL"
      operator: "less_than"
      threshold: 50
      weight: 0.3
    
    - indicator: "ECON_FUEL_AVAIL"
      operator: "less_than"
      threshold: 40
      weight: 0.3
  
  logic: "WEIGHTED"
  threshold: 0.6  # 60% of weighted conditions must trigger

applicable_industries:
  - "retail"
  - "manufacturing"
  - "logistics"

# Revenue Loss Risk
code: "RISK_REVENUE_DECLINE"
name: "Revenue Decline Risk"
category: "financial"

trigger_logic:
  conditions:
    - indicator: "OPS_FOOTFALL_IMPACT"
      operator: "less_than"
      threshold: -25  # 25% decline
    
    - indicator: "ECON_CONSUMER_CONF"
      operator: "less_than"
      threshold: 40
  
  logic: "OR"  # Either condition triggers

applicable_industries:
  - "retail"
  - "hospitality"

# Cost Escalation Risk
code: "RISK_COST_ESCALATION"
name: "Operating Cost Escalation Risk"
category: "financial"

trigger_logic:
  conditions:
    - indicator: "OPS_COST_PRESSURE"
      operator: "greater_than"
      threshold: 70
    
    - indicator: "ECON_INFLATION_PRESSURE"
      operator: "greater_than"
      threshold: 60
  
  logic: "AND"

# Workforce Disruption Risk
code: "RISK_WORKFORCE_DISRUPTION"
name: "Workforce Availability Risk"
category: "operational"

trigger_logic:
  conditions:
    - indicator: "OPS_WORKFORCE_AVAIL"
      operator: "less_than"
      threshold: 70
    
    - indicator: "POL_STRIKE_ACTIVITY"
      operator: "greater_than"
      threshold: 70
  
  logic: "OR"
```

#### Tier 2: Pattern Recognition

**Purpose**: Detect risks based on historical patterns

**Implementation:**

```python
class PatternBasedRiskDetector:
    
    def __init__(self):
        self.historical_patterns = self._load_historical_patterns()
    
    def detect_risks(self, operational_indicators, company_profile, historical_data):
        """
        Detect risks by comparing current situation to historical patterns
        """
        
        detected_risks = []
        
        # Get current indicator profile
        current_profile = self._create_indicator_profile(operational_indicators)
        
        # Compare against known risk patterns
        for pattern in self.historical_patterns:
            similarity = self._calculate_similarity(current_profile, pattern['indicator_profile'])
            
            if similarity > 0.75:  # High similarity threshold
                # This situation resembles a past risk event
                risk = {
                    'code': f"RISK_PATTERN_{pattern['risk_type']}",
                    'name': f"Pattern-Detected: {pattern['risk_name']}",
                    'category': pattern['category'],
                    'type': 'risk',
                    'detection_method': 'pattern_recognition',
                    'confidence': similarity,
                    'historical_context': {
                        'similar_event': pattern['event_date'],
                        'outcome': pattern['outcome'],
                        'duration': pattern['duration_days'],
                        'impact': pattern['business_impact']
                    }
                }
                detected_risks.append(risk)
        
        return detected_risks
    
    def _calculate_similarity(self, current_profile, historical_profile):
        """
        Calculate cosine similarity between indicator profiles
        """
        import numpy as np
        
        # Convert to vectors
        current_vec = np.array([current_profile.get(k, 0) for k in historical_profile.keys()])
        historical_vec = np.array(list(historical_profile.values()))
        
        # Cosine similarity
        dot_product = np.dot(current_vec, historical_vec)
        magnitude = np.linalg.norm(current_vec) * np.linalg.norm(historical_vec)
        
        if magnitude == 0:
            return 0
        
        return dot_product / magnitude
```

**Historical Pattern Storage:**

```json
{
    "pattern_id": "pattern_001",
    "risk_type": "FUEL_CRISIS",
    "risk_name": "Fuel Shortage Crisis",
    "category": "operational",
    
    "event_date": "2022-05-15",
    "duration_days": 12,
    "severity": "high",
    
    "indicator_profile": {
        "ECON_FUEL_AVAIL": 35,
        "OPS_TRANSPORT_AVAIL": 40,
        "OPS_SUPPLY_CHAIN": 50,
        "POL_UNREST": 75
    },
    
    "outcome": "Widespread delivery delays, 30% revenue impact for retail",
    "business_impact": {
        "retail": {"revenue_impact": -0.30, "duration_days": 12},
        "logistics": {"revenue_impact": -0.45, "duration_days": 12},
        "manufacturing": {"revenue_impact": -0.20, "duration_days": 8}
    },
    
    "leading_indicators": [
        "Government fuel distribution problems mentioned 5 days prior",
        "Queue length reports increasing 3 days prior"
    ]
}
```

#### Tier 3: ML-Based Risk Prediction

**Purpose**: Predict risks using machine learning models

**Model Architecture:**

```
Input Features (from operational indicators):
├── Current indicator values (normalized)
├── Indicator trends (7-day, 30-day)
├── Rate of change
├── Volatility measures
├── Company characteristics
└── Industry factors

↓

Feature Engineering
├── Lag features (yesterday, 3 days ago, 7 days ago)
├── Rolling statistics (mean, std, min, max)
├── Interaction features (indicator combinations)
└── Temporal features (day of week, seasonality)

↓

ML Model (Random Forest or XGBoost)
├── Binary classification: Risk present/absent
├── Multi-class: Risk category
└── Regression: Risk severity score

↓

Output:
├── Risk probability (0-1)
├── Risk category
├── Feature importance (explainability)
└── Confidence score
```

**Implementation:**

```python
class MLRiskPredictor:
    
    def __init__(self, model_path='models/risk_predictor.pkl'):
        self.model = self._load_model(model_path)
        self.feature_engineer = FeatureEngineer()
    
    def predict_risks(self, operational_indicators, company_profile, historical_data):
        """
        Predict risks using trained ML model
        """
        
        # Prepare features
        features = self.feature_engineer.create_features(
            operational_indicators,
            company_profile,
            historical_data
        )
        
        # Predict
        predictions = self.model.predict_proba(features)
        
        # Convert predictions to risk objects
        detected_risks = []
        
        for risk_class, probability in enumerate(predictions[0]):
            if probability > 0.5:  # Threshold for detection
                risk_info = self._get_risk_info(risk_class)
                
                risk = {
                    'code': risk_info['code'],
                    'name': risk_info['name'],
                    'category': risk_info['category'],
                    'type': 'risk',
                    'detection_method': 'ml_prediction',
                    'confidence': probability,
                    'ml_explanation': self._explain_prediction(features, risk_class)
                }
                detected_risks.append(risk)
        
        return detected_risks
    
    def _explain_prediction(self, features, risk_class):
        """
        Use SHAP or feature importance to explain prediction
        """
        import shap
        
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(features)
        
        # Get top contributing features
        feature_contributions = sorted(
            zip(features.columns, shap_values[risk_class][0]),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return {
            'top_factors': [
                {'feature': name, 'contribution': float(contrib)}
                for name, contrib in feature_contributions[:5]
            ]
        }
```

**Training Data Schema:**

```sql
CREATE TABLE ml_training_data (
    training_id SERIAL PRIMARY KEY,
    
    -- Input features
    feature_vector JSONB NOT NULL,
    /* Structure:
    {
        "OPS_SUPPLY_CHAIN": 55,
        "OPS_TRANSPORT_AVAIL": 45,
        "ECON_FUEL_AVAIL": 40,
        "trend_7day_supply_chain": -15,
        "volatility_transport": 12.5,
        "company_import_dependency": 0.6,
        ...
    }
    */
    
    -- Labels (outcomes)
    risk_materialized BOOLEAN,
    risk_category VARCHAR(50),
    risk_severity VARCHAR(20),
    actual_impact DECIMAL(10,2),
    
    -- Temporal
    feature_date DATE NOT NULL,
    outcome_date DATE,
    
    -- Metadata
    company_id VARCHAR(50),
    industry VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## OPPORTUNITY DETECTION METHODS {#opportunity-detection}

### 4.2 OPPORTUNITY DETECTION STRATEGIES

#### Strategy 1: Gap Analysis

**Purpose**: Identify market gaps and unmet needs

```python
class GapAnalyzer:
    
    def detect_opportunities(self, operational_indicators, national_indicators, competitive_intel):
        """
        Detect opportunities through gap analysis
        """
        
        opportunities = []
        
        # Gap 1: Competitor weakness while you're strong
        if self._detect_competitive_advantage_gap(operational_indicators, competitive_intel):
            opportunities.append(self._create_market_capture_opportunity())
        
        # Gap 2: Rising demand with constrained supply
        if self._detect_supply_demand_gap(national_indicators):
            opportunities.append(self._create_supply_gap_opportunity())
        
        # Gap 3: Cost advantage window
        if self._detect_cost_advantage_gap(operational_indicators, national_indicators):
            opportunities.append(self._create_cost_opportunity())
        
        return opportunities
    
    def _detect_competitive_advantage_gap(self, your_indicators, competitive_intel):
        """
        Detect if competitors are weaker than you in current conditions
        """
        
        your_supply_chain = your_indicators.get('OPS_SUPPLY_CHAIN', 50)
        
        # Check competitive intelligence
        for intel in competitive_intel:
            if intel['intel_type'] == 'weakness':
                if 'supply chain' in intel['description'].lower():
                    # Competitor has supply chain issues, you don't
                    if your_supply_chain > 70:
                        return True
        
        return False
    
    def _detect_supply_demand_gap(self, national_indicators):
        """
        Detect if demand is rising but supply is constrained
        """
        
        consumer_confidence = national_indicators.get('ECON_CONSUMER_CONF', 50)
        supply_chain_health = national_indicators.get('ECON_SUPPLY_CHAIN', 50)
        
        # High demand, low supply = opportunity
        if consumer_confidence > 60 and supply_chain_health < 50:
            return True
        
        return False
```

#### Strategy 2: Positive Trend Detection

**Purpose**: Identify favorable trends early

```python
class TrendOpportunityDetector:
    
    def detect_opportunities(self, indicators, historical_data):
        """
        Detect opportunities from positive trends
        """
        
        opportunities = []
        
        for indicator_code, current_value in indicators.items():
            # Analyze trend
            trend = self._analyze_trend(indicator_code, historical_data)
            
            # Positive momentum opportunities
            if self._is_positive_trend(indicator_code, trend):
                opportunity = self._create_trend_opportunity(indicator_code, trend)
                opportunities.append(opportunity)
        
        return opportunities
    
    def _is_positive_trend(self, indicator_code, trend):
        """
        Determine if trend represents an opportunity
        """
        
        # Example: Rising consumer confidence
        if 'CONSUMER_CONF' in indicator_code:
            if trend['direction'] == 'rising' and trend['strength'] > 0.7:
                return True
        
        # Example: Improving infrastructure
        if 'INFRASTRUCTURE' in indicator_code:
            if trend['direction'] == 'rising' and trend['rate_of_change'] > 5:
                return True
        
        # Example: Declining competitor advantage
        if 'COMPETITOR' in indicator_code:
            if trend['direction'] == 'falling':
                return True
        
        return False
```

#### Strategy 3: Event-Triggered Opportunities

**Purpose**: Detect opportunities from specific events

```python
class EventOpportunityDetector:
    
    def __init__(self):
        self.opportunity_triggers = self._load_opportunity_triggers()
    
    def detect_opportunities(self, indicators, events, company_profile):
        """
        Detect opportunities triggered by specific events
        """
        
        opportunities = []
        
        for trigger in self.opportunity_triggers:
            if self._is_triggered(trigger, indicators, events, company_profile):
                opportunity = self._generate_opportunity(trigger, indicators, company_profile)
                opportunities.append(opportunity)
        
        return opportunities
    
    def _is_triggered(self, trigger, indicators, events, profile):
        """
        Check if opportunity trigger conditions are met
        """
        
        # Example trigger: New policy announcement favoring industry
        if trigger['type'] == 'policy_benefit':
            for event in events:
                if 'policy' in event['description'].lower():
                    if profile['industry'] in trigger['beneficiary_industries']:
                        return True
        
        # Example trigger: Currency depreciation (good for exporters)
        if trigger['type'] == 'currency_advantage':
            currency_indicator = indicators.get('ECON_CURRENCY_STAB', 50)
            if currency_indicator < 40:  # Weak currency
                if profile.get('export_percentage', 0) > 0.3:  # Exporter
                    return True
        
        return False
```

**Opportunity Trigger Definitions:**

```yaml
# Market Capture Opportunity
code: "OPP_MARKET_CAPTURE"
name: "Market Share Capture Opportunity"
category: "market"

trigger_logic:
  conditions:
    - type: "competitive_weakness"
      description: "Competitor experiencing operational issues"
    
    - type: "your_strength"
      indicator: "OPS_SUPPLY_CHAIN"
      operator: "greater_than"
      threshold: 70
  
  logic: "AND"

potential_value: "high"
feasibility_requirements:
  - "Marketing budget available"
  - "Capacity to handle increased demand"

# Cost Reduction Opportunity
code: "OPP_COST_REDUCTION"
name: "Input Cost Reduction Opportunity"
category: "cost"

trigger_logic:
  conditions:
    - type: "favorable_indicator"
      indicator: "ECON_CURRENCY_STAB"
      operator: "greater_than"
      threshold: 60
    
    - type: "company_characteristic"
      field: "import_dependency"
      operator: "greater_than"
      threshold: 0.5
  
  logic: "AND"

# Strategic Partnership Opportunity
code: "OPP_PARTNERSHIP"
name: "Strategic Partnership Opportunity"
category: "strategic"

trigger_logic:
  conditions:
    - type: "competitive_intel"
      intel_type: "distressed_competitor"
    
    - type: "company_strength"
      indicator: "financial_health"
      operator: "greater_than"
      threshold: 70
  
  logic: "AND"
```

---

## SCORING & PRIORITIZATION {#scoring-prioritization}

### 4.3 RISK SCORING ALGORITHM

**Risk Score Formula:**

```
Risk_Score = Probability × Impact × Urgency × Confidence

Where:
- Probability: 0.0 to 1.0 (likelihood of occurrence)
- Impact: 0 to 10 (severity if it occurs)
- Urgency: 1 to 5 (time sensitivity)
- Confidence: 0.0 to 1.0 (certainty of prediction)

Final Score: 0 to 50
```

**Implementation:**

```python
class RiskScorer:
    
    def calculate_risk_score(self, risk, operational_indicators, company_profile):
        """
        Calculate comprehensive risk score
        """
        
        # Calculate each component
        probability = self._calculate_probability(risk, operational_indicators)
        impact = self._calculate_impact(risk, company_profile)
        urgency = self._calculate_urgency(risk, operational_indicators)
        confidence = self._calculate_confidence(risk)
        
        # Final score
        final_score = probability * impact * urgency * confidence
        
        # Classify severity
        severity = self._classify_severity(final_score)
        
        return {
            'probability': probability,
            'impact': impact,
            'urgency': urgency,
            'confidence': confidence,
            'final_score': final_score,
            'severity': severity,
            'breakdown': {
                'probability_reasoning': self._explain_probability(risk, operational_indicators),
                'impact_reasoning': self._explain_impact(risk, company_profile),
                'urgency_reasoning': self._explain_urgency(risk)
            }
        }
    
    def _calculate_probability(self, risk, indicators):
        """
        Estimate likelihood of risk materializing
        
        Factors:
        - How far indicators are from thresholds
        - Trend direction (getting worse?)
        - Historical frequency
        """
        
        base_probability = 0.5  # Start neutral
        
        # Adjust based on indicator deviation
        triggering_indicators = risk.get('triggering_indicators', [])
        
        for trig_ind in triggering_indicators:
            current_value = trig_ind['value']
            threshold = trig_ind['threshold']
            
            # How far past threshold?
            if current_value < threshold:
                deviation = (threshold - current_value) / threshold
                base_probability += deviation * 0.3
        
        # Adjust based on trend
        if self._has_worsening_trend(risk, indicators):
            base_probability += 0.15
        
        # Adjust based on detection method confidence
        if risk.get('detection_method') == 'rule_based':
            # Rule-based is high confidence
            base_probability *= 1.1
        elif risk.get('detection_method') == 'ml_prediction':
            # ML confidence from model
            ml_confidence = risk.get('confidence', 0.7)
            base_probability *= ml_confidence
        
        # Cap at 1.0
        return min(base_probability, 1.0)
    
    def _calculate_impact(self, risk, company_profile):
        """
        Estimate severity if risk occurs
        
        Factors:
        - Risk category base impact
        - Company size (bigger = bigger impact)
        - Company vulnerability (dependencies)
        - Industry typical impact
        """
        
        # Base impact by category
        category_impacts = {
            'operational': 7.0,
            'financial': 8.0,
            'competitive': 6.0,
            'reputational': 7.5,
            'compliance': 8.5,
            'strategic': 6.5
        }
        
        base_impact = category_impacts.get(risk['category'], 5.0)
        
        # Adjust for company size
        size = company_profile.get('business_scale', {}).get('size', 'medium')
        size_multipliers = {
            'small': 1.2,      # Small companies more vulnerable
            'medium': 1.0,
            'large': 0.9,      # Large companies more resilient
            'enterprise': 0.8
        }
        base_impact *= size_multipliers.get(size, 1.0)
        
        # Adjust for company vulnerabilities
        if risk['category'] == 'operational':
            # Check supply chain dependency
            import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
            base_impact *= (0.8 + import_dep * 0.4)  # Range: 0.8 to 1.2
        
        # Cap at 10.0
        return min(base_impact, 10.0)
    
    def _calculate_urgency(self, risk, indicators):
        """
        Determine time sensitivity
        
        Score 1-5:
        5 = Immediate (< 24 hours)
        4 = Very soon (1-3 days)
        3 = Soon (3-7 days)
        2 = Upcoming (1-2 weeks)
        1 = Future (> 2 weeks)
        """
        
        # Analyze trend velocity
        trend_strength = self._get_trend_strength(risk, indicators)
        
        if trend_strength > 0.8:
            # Rapidly deteriorating
            return 5
        elif trend_strength > 0.6:
            return 4
        elif trend_strength > 0.4:
            return 3
        elif trend_strength > 0.2:
            return 2
        else:
            return 1
    
    def _calculate_confidence(self, risk):
        """
        How confident are we in this risk assessment?
        
        Factors:
        - Detection method reliability
        - Data quality
        - Historical validation
        """
        
        base_confidence = 0.7
        
        # Detection method confidence
        method = risk.get('detection_method')
        if method == 'rule_based':
            base_confidence = 0.85
        elif method == 'pattern_recognition':
            base_confidence = 0.75
        elif method == 'ml_prediction':
            base_confidence = risk.get('confidence', 0.7)
        
        # Adjust for data quality
        data_quality = self._assess_data_quality(risk)
        base_confidence *= data_quality
        
        return min(base_confidence, 1.0)
    
    def _classify_severity(self, score):
        """
        Map numeric score to severity level
        """
        
        if score >= 40:
            return 'critical'
        elif score >= 30:
            return 'high'
        elif score >= 15:
            return 'medium'
        else:
            return 'low'
```

### 4.4 OPPORTUNITY SCORING ALGORITHM

**Opportunity Score Formula:**

```
Opportunity_Score = Potential_Value × Feasibility × Timing × Strategic_Fit

Where:
- Potential_Value: 0 to 10 (benefit magnitude)
- Feasibility: 0.0 to 1.0 (can we execute?)
- Timing: 0.0 to 1.0 (window size)
- Strategic_Fit: 0.0 to 1.0 (alignment)

Final Score: 0 to 10
```

**Implementation:**

```python
class OpportunityScorer:
    
    def calculate_opportunity_score(self, opportunity, company_profile, market_data):
        """
        Calculate comprehensive opportunity score
        """
        
        potential_value = self._calculate_potential_value(opportunity, company_profile)
        feasibility = self._calculate_feasibility(opportunity, company_profile)
        timing = self._calculate_timing(opportunity, market_data)
        strategic_fit = self._calculate_strategic_fit(opportunity, company_profile)
        
        final_score = potential_value * feasibility * timing * strategic_fit
        
        priority = self._classify_priority(final_score)
        
        return {
            'potential_value': potential_value,
            'feasibility': feasibility,
            'timing': timing,
            'strategic_fit': strategic_fit,
            'final_score': final_score,
            'priority': priority
        }
    
    def _calculate_potential_value(self, opportunity, profile):
        """
        Estimate benefit magnitude
        
        Factors:
        - Market size
        - Revenue potential
        - Cost savings
        - Strategic value
        """
        
        category = opportunity['category']
        
        # Base value by category
        category_values = {
            'market': 8.0,      # High revenue potential
            'cost': 7.0,        # Direct savings
            'strategic': 6.5,   # Long-term value
            'talent': 5.5,      # Enabling value
            'financial': 7.5,   # Capital access
            'innovation': 6.0   # Future positioning
        }
        
        base_value = category_values.get(category, 5.0)
        
        # Adjust for company size (bigger company = bigger opportunity value)
        size = profile.get('business_scale', {}).get('size', 'medium')
        size_multipliers = {
            'small': 0.7,
            'medium': 1.0,
            'large': 1.3,
            'enterprise': 1.5
        }
        
        final_value = base_value * size_multipliers.get(size, 1.0)
        
        return min(final_value, 10.0)
    
    def _calculate_feasibility(self, opportunity, profile):
        """
        Can we actually execute on this?
        
        Factors:
        - Required resources available?
        - Capabilities present?
        - Competitive position
        """
        
        feasibility_score = 0.7  # Start with moderate feasibility
        
        # Check resource requirements
        required = opportunity.get('requirements', {})
        
        # Financial feasibility
        if 'budget_required' in required:
            available_cash = profile.get('financial', {}).get('cash_reserves', 0)
            if available_cash >= required['budget_required']:
                feasibility_score += 0.15
            else:
                feasibility_score -= 0.2
        
        # Capability feasibility
        if 'capabilities' in required:
            has_capabilities = self._check_capabilities(required['capabilities'], profile)
            if has_capabilities:
                feasibility_score += 0.15
            else:
                feasibility_score -= 0.15
        
        return max(0, min(feasibility_score, 1.0))
    
    def _calculate_timing(self, opportunity, market_data):
        """
        How good is the timing?
        
        Factors:
        - Window of opportunity size
        - First-mover advantage
        - Market readiness
        """
        
        # Check if opportunity is time-sensitive
        if opportunity.get('time_sensitive', False):
            # Narrow window
            return 0.9
        
        # Check market trends
        if self._is_trend_accelerating(opportunity, market_data):
            return 0.85
        
        # Stable opportunity
        return 0.7
    
    def _calculate_strategic_fit(self, opportunity, profile):
        """
        How well does this align with strategy?
        
        Factors:
        - Core business alignment
        - Strategic goals match
        - Risk appetite compatibility
        """
        
        fit_score = 0.5
        
        # Industry alignment
        if opportunity.get('industry_match', False):
            fit_score += 0.2
        
        # Strategic goals alignment
        strategic_goals = profile.get('strategic_goals', [])
        opportunity_goals = opportunity.get('supports_goals', [])
        
        goal_overlap = len(set(strategic_goals) & set(opportunity_goals))
        if goal_overlap > 0:
            fit_score += 0.2
        
        # Risk appetite
        risk_appetite = profile.get('risk_appetite', 'moderate')
        opportunity_risk = opportunity.get('risk_level', 'moderate')
        
        if risk_appetite == opportunity_risk:
            fit_score += 0.1
        
        return min(fit_score, 1.0)
```

### 4.5 PRIORITIZATION ENGINE

**Purpose**: Rank insights by importance

```python
class InsightPrioritizer:
    
    def prioritize(self, risks, opportunities, company_profile):
        """
        Rank all insights by priority
        
        Output: Single prioritized list of actions
        """
        
        all_insights = []
        
        # Add risks with priority scores
        for risk in risks:
            priority_score = self._calculate_priority_score(risk, 'risk', company_profile)
            all_insights.append({
                'type': 'risk',
                'insight': risk,
                'priority_score': priority_score
            })
        
        # Add opportunities with priority scores
        for opp in opportunities:
            priority_score = self._calculate_priority_score(opp, 'opportunity', company_profile)
            all_insights.append({
                'type': 'opportunity',
                'insight': opp,
                'priority_score': priority_score
            })
        
        # Sort by priority
        prioritized = sorted(all_insights, key=lambda x: x['priority_score'], reverse=True)
        
        # Assign ranks
        for rank, item in enumerate(prioritized, 1):
            item['priority_rank'] = rank
        
        return prioritized
    
    def _calculate_priority_score(self, insight, insight_type, profile):
        """
        Universal priority scoring
        
        Factors:
        - Severity/Value (from risk/opportunity score)
        - Urgency/Timing
        - Actionability
        - Strategic importance
        """
        
        if insight_type == 'risk':
            base_score = insight['final_score']
            urgency_weight = 0.3
            actionability = self._assess_risk_actionability(insight)
        else:  # opportunity
            base_score = insight['final_score'] * 10  # Scale to match risk scores
            urgency_weight = 0.2  # Opportunities less urgent
            actionability = self._assess_opportunity_actionability(insight)
        
        # Adjust for urgency
        urgency = insight.get('urgency', 3)
        urgency_factor = urgency / 5.0
        
        # Adjust for actionability
        actionability_factor = actionability
        
        # Strategic importance
        strategic_importance = self._assess_strategic_importance(insight, profile)
        
        # Weighted combination
        priority_score = (
            base_score * 0.5 +
            (urgency_factor * 50) * urgency_weight +
            (actionability_factor * 30) * 0.2 +
            (strategic_importance * 20) * 0.1
        )
        
        return priority_score
    
    def _assess_risk_actionability(self, risk):
        """
        Can we do something about this risk?
        
        Score 0-1:
        1.0 = Highly actionable (we can mitigate)
        0.5 = Somewhat actionable
        0.0 = Not actionable (external factors only)
        """
        
        category = risk['category']
        
        # Operational risks are usually actionable
        if category == 'operational':
            return 0.9
        
        # Financial risks somewhat actionable
        elif category == 'financial':
            return 0.7
        
        # Competitive risks less actionable
        elif category == 'competitive':
            return 0.5
        
        # External factors
        elif category == 'compliance' or category == 'strategic':
            return 0.6
        
        return 0.5
```

---

This completes the core detection and scoring systems. Would you like me to continue with Part 3 covering the Recommendation Engine, Contextual Intelligence, Mock Data, ML Integration, and Implementation Checklist?

