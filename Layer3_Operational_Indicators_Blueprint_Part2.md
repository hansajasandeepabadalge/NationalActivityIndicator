# LAYER 3: OPERATIONAL ENVIRONMENT INDICATOR ENGINE
## Comprehensive Architectural Blueprint & Implementation Plan - PART 2

---

## TABLE OF CONTENTS - PART 2

1. [Mock Data Strategy for Parallel Development](#mock-data)
2. [Impact Translation Engine](#impact-translation)
3. [Universal Operational Indicators](#universal-indicators)
4. [Industry-Specific Indicators](#industry-specific)
5. [Calculation Methodologies](#calculation-methods)
6. [Forecasting & Prediction](#forecasting)
7. [Recommendation Engine](#recommendations)
8. [Geographic Intelligence](#geographic)
9. [Scenario Simulation](#scenarios)
10. [Iteration 1 Implementation Checklist](#iteration-1-checklist)
11. [Iteration 2 Advanced Features](#iteration-2)
12. [Integration & Testing](#integration-testing)

---

## MOCK DATA STRATEGY FOR PARALLEL DEVELOPMENT {#mock-data}

### 3.5 MOCK DATA ARCHITECTURE

**Purpose**: Enable Layer 3 development independently of Layer 2 completion

**Mock Data Components:**

```
Mock Data Stack:
├── Mock Company Profiles (5-10 diverse businesses)
├── Mock National Indicators (from Layer 2)
├── Mock Translation Results
├── Mock Time-Series Data (30 days history)
└── Mock Scenario Datasets
```

#### Mock Company Profiles

**File: `mock_data/companies/abc_retail.json`**
```json
{
    "company_id": "mock_retail_001",
    "company_name": "ABC Supermarkets (Mock)",
    "industry": "retail",
    "sub_industry": "grocery_supermarkets",
    
    "business_scale": {
        "size": "large",
        "employees": 450,
        "annual_revenue_lkr": 5000000000,
        "locations_count": 8
    },
    
    "locations": [
        {
            "location_id": "mock_loc_col_001",
            "name": "Colombo Main Branch",
            "city": "Colombo",
            "district": "Colombo",
            "coordinates": {"lat": 6.9271, "lon": 79.8612},
            "daily_footfall_avg": 2500
        },
        {
            "location_id": "mock_loc_kan_001",
            "name": "Kandy Branch",
            "city": "Kandy",
            "district": "Kandy",
            "coordinates": {"lat": 7.2906, "lon": 80.6337},
            "daily_footfall_avg": 1200
        }
    ],
    
    "supply_chain": {
        "import_dependency": 0.60,
        "local_sourcing": 0.40
    },
    
    "critical_dependencies": {
        "fuel": "high",
        "power": "high",
        "transport_access": "high"
    },
    
    "alert_thresholds": {
        "supply_chain_risk": {"high": 70, "critical": 85},
        "foot_traffic_impact": {"high": -25, "critical": -40}
    }
}
```

**File: `mock_data/companies/xyz_logistics.json`**
```json
{
    "company_id": "mock_logistics_001",
    "company_name": "XYZ Logistics (Mock)",
    "industry": "logistics",
    "sub_industry": "freight_cargo",
    
    "business_scale": {
        "size": "medium",
        "employees": 150,
        "fleet_size": 45
    },
    
    "critical_dependencies": {
        "fuel": "critical",
        "road_access": "critical",
        "port_operations": "high"
    }
}
```

#### Mock National Indicators (Layer 2 Output)

**File: `mock_data/national_indicators/current_state.json`**
```json
{
    "timestamp": "2025-12-01T10:00:00Z",
    "indicators": [
        {
            "indicator_code": "POL_UNREST_01",
            "indicator_name": "Political Unrest Index",
            "pestel_category": "Political",
            "current_value": 78.5,
            "normalized_value": 0.785,
            "trend": {"direction": "rising", "strength": 0.82},
            "geographic_distribution": {
                "Colombo": 12,
                "Kandy": 2,
                "Galle": 1
            }
        },
        {
            "indicator_code": "ECON_FUEL_AVAIL",
            "indicator_name": "Fuel Availability Index",
            "pestel_category": "Economic",
            "current_value": 42.0,
            "normalized_value": 0.42,
            "trend": {"direction": "falling", "strength": 0.75},
            "severity": "high"
        },
        {
            "indicator_code": "ENV_WEATHER_SEV",
            "indicator_name": "Weather Severity Index",
            "pestel_category": "Environmental",
            "current_value": 65.0,
            "normalized_value": 0.65,
            "geographic_distribution": {
                "Colombo": 8,
                "Kandy": 3
            }
        },
        {
            "indicator_code": "ECON_CONSUMER_CONF",
            "indicator_name": "Consumer Confidence Proxy",
            "pestel_category": "Economic",
            "current_value": 48.0,
            "normalized_value": 0.48,
            "trend": {"direction": "falling", "strength": 0.60}
        },
        {
            "indicator_code": "ECON_PORT_OPS",
            "indicator_name": "Port Operations Status",
            "pestel_category": "Economic",
            "current_value": 65.0,
            "normalized_value": 0.65
        },
        {
            "indicator_code": "ENV_ROAD_STATUS",
            "indicator_name": "Road Network Status",
            "pestel_category": "Environmental",
            "current_value": 72.0,
            "normalized_value": 0.72
        }
    ]
}
```

#### Mock Historical Time-Series

**File: `mock_data/timeseries/fuel_availability_30days.json`**
```json
{
    "indicator_code": "ECON_FUEL_AVAIL",
    "time_series": [
        {"date": "2025-11-01", "value": 85.0},
        {"date": "2025-11-02", "value": 83.0},
        {"date": "2025-11-03", "value": 80.0},
        "...",
        {"date": "2025-11-28", "value": 48.0},
        {"date": "2025-11-29", "value": 45.0},
        {"date": "2025-11-30", "value": 42.0}
    ],
    "trend_summary": {
        "overall_direction": "declining",
        "rate_of_change": -1.43,
        "volatility": "high"
    }
}
```

#### Mock Data Loader

```python
class MockDataLoader:
    """
    Loads mock data for Layer 3 development
    """
    
    def __init__(self, mock_data_dir="mock_data/"):
        self.mock_data_dir = mock_data_dir
        self.companies = self._load_companies()
        self.national_indicators = self._load_national_indicators()
        self.historical_data = self._load_historical_data()
    
    def _load_companies(self):
        """Load mock company profiles"""
        companies = {}
        company_dir = os.path.join(self.mock_data_dir, "companies")
        
        for filename in os.listdir(company_dir):
            if filename.endswith('.json'):
                with open(os.path.join(company_dir, filename)) as f:
                    company = json.load(f)
                    companies[company['company_id']] = company
        
        return companies
    
    def _load_national_indicators(self):
        """Load mock national indicators"""
        with open(os.path.join(self.mock_data_dir, "national_indicators/current_state.json")) as f:
            return json.load(f)
    
    def _load_historical_data(self):
        """Load time-series mock data"""
        historical = {}
        ts_dir = os.path.join(self.mock_data_dir, "timeseries")
        
        for filename in os.listdir(ts_dir):
            if filename.endswith('.json'):
                with open(os.path.join(ts_dir, filename)) as f:
                    data = json.load(f)
                    historical[data['indicator_code']] = data['time_series']
        
        return historical
    
    def get_company(self, company_id):
        """Get mock company profile"""
        return self.companies.get(company_id)
    
    def get_national_indicator(self, indicator_code):
        """Get current value of national indicator"""
        indicators = self.national_indicators.get('indicators', [])
        for ind in indicators:
            if ind['indicator_code'] == indicator_code:
                return ind
        return None
    
    def get_historical_values(self, indicator_code, days=30):
        """Get historical values for indicator"""
        return self.historical_data.get(indicator_code, [])[-days:]
    
    def simulate_real_time_update(self):
        """
        Simulate new data arriving (for testing)
        Randomly adjust indicator values slightly
        """
        import random
        
        for indicator in self.national_indicators['indicators']:
            # Small random change
            change = random.uniform(-5, 5)
            new_value = max(0, min(100, indicator['current_value'] + change))
            indicator['current_value'] = new_value
            indicator['normalized_value'] = new_value / 100
        
        # Update timestamp
        self.national_indicators['timestamp'] = datetime.now().isoformat()
        
        return self.national_indicators
```

#### Integration Points

**Phase 1: Mock Data Only**
```python
# Development mode
data_source_mode = "mock"

if data_source_mode == "mock":
    data_loader = MockDataLoader()
    national_indicators = data_loader.get_national_indicators()
```

**Phase 2: Real Layer 2 Integration**
```python
# Production mode
data_source_mode = "real"

if data_source_mode == "real":
    data_loader = Layer2Connector()
    national_indicators = data_loader.fetch_current_indicators()
elif data_source_mode == "mock":
    data_loader = MockDataLoader()
    national_indicators = data_loader.get_national_indicators()
```

**Phase 3: Hybrid (Testing)**
```python
# Hybrid mode for testing
data_source_mode = "hybrid"

real_loader = Layer2Connector()
mock_loader = MockDataLoader()

# Use real data if available, mock as fallback
try:
    national_indicators = real_loader.fetch_current_indicators()
    if len(national_indicators) < MIN_THRESHOLD:
        # Supplement with mock
        mock_data = mock_loader.get_national_indicators()
        national_indicators.extend(mock_data['indicators'])
except Exception as e:
    logger.warning(f"Layer 2 unavailable, using mock data: {e}")
    national_indicators = mock_loader.get_national_indicators()
```

---

## IMPACT TRANSLATION ENGINE {#impact-translation}

### 3.6 TRANSLATING NATIONAL TO OPERATIONAL

**Core Translation Concept:**

```
National Indicator Value
    ↓
Filter by Business Profile (Is this relevant to me?)
    ↓
Apply Industry Sensitivity (How much does this affect my industry?)
    ↓
Apply Company-Specific Factors (What's unique about my business?)
    ↓
Calculate Operational Impact
    ↓
Operational Indicator Value
```

#### Translation Rule Types

**Type 1: Direct Linear Mapping**

```python
def translate_linear(national_value, industry_sensitivity, company_factor):
    """
    Simple proportional translation
    
    Example:
    National fuel shortage: 85
    Industry sensitivity (logistics): 2.0 (very high)
    Company dependency: 1.2 (fleet-heavy)
    
    Operational impact = 85 * 2.0 * 1.2 = 204 → capped at 100
    """
    
    operational_impact = national_value * industry_sensitivity * company_factor
    
    # Cap at 0-100 scale
    operational_impact = max(0, min(100, operational_impact))
    
    return operational_impact
```

**Type 2: Threshold-Based Translation**

```python
def translate_threshold(national_value, thresholds):
    """
    Different operational impacts at different thresholds
    
    Example:
    Political unrest national level → Store closure decision
    
    0-30: No impact (0)
    30-60: Minor impact (20)
    60-80: Moderate impact (60)
    80-100: High impact (95)
    """
    
    for threshold in thresholds:
        if threshold['min'] <= national_value < threshold['max']:
            return threshold['operational_impact']
    
    return 0  # Default
```

**Type 3: Formula-Based Translation**

```python
def translate_formula(national_value, company_profile, formula):
    """
    Complex formula using multiple factors
    
    Example formula for footfall impact:
    footfall_impact = 
        (weather_severity * -0.3) +
        (transport_disruption * -0.4) +
        (consumer_confidence * 0.5) +
        (safety_perception * 0.2)
    """
    
    # Parse formula and evaluate
    # This is pseudocode - actual implementation would use safe eval or expression parser
    
    variables = {
        'national_value': national_value,
        'import_dependency': company_profile['supply_chain']['import_dependency'],
        'location_count': len(company_profile['locations']),
        # ... more variables
    }
    
    # Safe evaluation
    result = evaluate_expression(formula, variables)
    
    return result
```

**Type 4: Lookup Table Translation**

```python
def translate_lookup(national_value, industry, lookup_table):
    """
    Pre-defined mappings for specific combinations
    
    Example:
    (Fuel shortage 85, Logistics) → Fleet availability -40%
    (Fuel shortage 85, IT Services) → Minimal impact -5%
    """
    
    # Round to nearest 10 for lookup
    bucket = round(national_value / 10) * 10
    
    key = f"{industry}_{bucket}"
    
    return lookup_table.get(key, {
        'impact_percentage': 0,
        'severity': 'low'
    })
```

#### Impact Translation Matrix Implementation

```python
class ImpactTranslator:
    
    def __init__(self):
        self.translation_rules = self._load_translation_rules()
        self.industry_templates = self._load_industry_templates()
    
    def translate_to_operational(self, national_indicator, company_profile):
        """
        Main translation function
        
        Args:
            national_indicator: dict with indicator data from Layer 2
            company_profile: dict with company configuration
        
        Returns:
            dict with operational impacts
        """
        
        national_code = national_indicator['indicator_code']
        national_value = national_indicator['current_value']
        industry = company_profile['industry']
        
        # Step 1: Check relevance
        is_relevant = self._check_relevance(national_code, industry, company_profile)
        
        if not is_relevant:
            return None  # This national indicator doesn't affect this business
        
        # Step 2: Get industry sensitivity
        sensitivity = self._get_industry_sensitivity(national_code, industry)
        
        # Step 3: Get company-specific factors
        company_factor = self._get_company_factor(national_code, company_profile)
        
        # Step 4: Find applicable translation rules
        rules = self._find_translation_rules(national_code, industry)
        
        # Step 5: Apply translation
        operational_impacts = []
        
        for rule in rules:
            impact = self._apply_translation_rule(
                rule,
                national_value,
                sensitivity,
                company_factor
            )
            
            operational_impacts.append(impact)
        
        return operational_impacts
    
    def _check_relevance(self, national_code, industry, company_profile):
        """
        Determine if this national indicator is relevant to this business
        """
        
        # Get industry template
        template = self.industry_templates.get(industry)
        
        if not template:
            return False
        
        # Check if national indicator is in sensitivity config
        sensitivities = template['sensitivity_config']['national_indicators']
        
        if national_code not in sensitivities:
            return False
        
        # Check relevance score
        relevance = sensitivities[national_code].get('relevance', 0)
        
        # Threshold: Only relevant if score > 0.3
        return relevance > 0.3
    
    def _get_industry_sensitivity(self, national_code, industry):
        """
        Get how sensitive this industry is to this national indicator
        """
        
        template = self.industry_templates.get(industry, {})
        sensitivities = template.get('sensitivity_config', {}).get('national_indicators', {})
        
        indicator_sensitivity = sensitivities.get(national_code, {})
        
        return {
            'relevance': indicator_sensitivity.get('relevance', 0.5),
            'impact_multiplier': indicator_sensitivity.get('impact_multiplier', 1.0)
        }
    
    def _get_company_factor(self, national_code, company_profile):
        """
        Calculate company-specific adjustment factor
        """
        
        # Example: Fuel shortage impact depends on fuel dependency
        if 'FUEL' in national_code:
            dependency = company_profile['critical_dependencies'].get('fuel', 'medium')
            
            dependency_multipliers = {
                'critical': 1.5,
                'high': 1.2,
                'medium': 1.0,
                'low': 0.7
            }
            
            return dependency_multipliers.get(dependency, 1.0)
        
        # Example: Import-related indicators depend on import dependency
        if 'IMPORT' in national_code or 'CURRENCY' in national_code:
            import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
            
            # Higher import dependency = higher impact
            return 0.5 + (import_dep * 1.0)  # Range: 0.5 to 1.5
        
        # Default: No company-specific adjustment
        return 1.0
    
    def _find_translation_rules(self, national_code, industry):
        """
        Find applicable translation rules
        """
        
        applicable_rules = []
        
        for rule in self.translation_rules:
            if rule['national_indicator_code'] == national_code:
                # Check if rule applies to this industry
                if (rule['applicable_industries'] is None or
                    industry in rule['applicable_industries']):
                    applicable_rules.append(rule)
        
        return applicable_rules
    
    def _apply_translation_rule(self, rule, national_value, sensitivity, company_factor):
        """
        Apply specific translation rule
        """
        
        rule_type = rule['rule_config']['type']
        
        if rule_type == 'linear':
            base_impact = national_value * sensitivity['impact_multiplier'] * company_factor
            operational_value = max(0, min(100, base_impact))
        
        elif rule_type == 'threshold':
            thresholds = rule['rule_config']['thresholds']
            operational_value = self._apply_threshold_rule(national_value, thresholds)
        
        elif rule_type == 'formula':
            expression = rule['rule_config']['expression']
            operational_value = self._evaluate_formula(expression, national_value, sensitivity, company_factor)
        
        else:
            operational_value = national_value  # Pass-through
        
        return {
            'operational_indicator_code': rule['operational_indicator_code'],
            'value': operational_value,
            'rule_type': rule_type,
            'confidence': rule.get('confidence_level', 0.8),
            'impact_lag_hours': rule.get('impact_lag_hours', 0)
        }
    
    def _apply_threshold_rule(self, value, thresholds):
        """Apply threshold-based translation"""
        for threshold in thresholds:
            if threshold['min'] <= value < threshold['max']:
                return threshold['output']
        return 0
    
    def _evaluate_formula(self, expression, national_value, sensitivity, company_factor):
        """Safely evaluate formula expression"""
        # In production, use a safe expression evaluator
        # This is simplified pseudocode
        
        variables = {
            'national_value': national_value,
            'sensitivity': sensitivity['impact_multiplier'],
            'company_factor': company_factor
        }
        
        # Safe evaluation (use libraries like simpleeval in production)
        result = eval(expression, {"__builtins__": {}}, variables)
        
        return max(0, min(100, result))
```

#### Geographic-Specific Translation

```python
def translate_with_geography(national_indicator, company_profile):
    """
    Apply geographic filtering for location-specific impacts
    
    Example:
    National indicator: "Colombo has severe weather"
    Company has locations in: Colombo, Kandy, Galle
    
    Result: Only Colombo location affected
    """
    
    geographic_dist = national_indicator.get('geographic_distribution', {})
    
    if not geographic_dist:
        # No geographic data, apply to all locations
        return apply_to_all_locations(national_indicator, company_profile)
    
    location_impacts = []
    
    for location in company_profile['locations']:
        location_city = location['city']
        
        # Check if this location is mentioned in geographic distribution
        if location_city in geographic_dist:
            intensity = geographic_dist[location_city]
            
            # Translate with location-specific intensity
            impact = translate_for_location(
                national_indicator,
                location,
                intensity
            )
            
            location_impacts.append(impact)
    
    return location_impacts
```

---

## UNIVERSAL OPERATIONAL INDICATORS {#universal-indicators}

### 3.7 INDICATORS APPLICABLE TO ALL BUSINESSES

**Universal Indicator 1: Transportation Availability**

```python
def calculate_transportation_availability(national_indicators, company_profile):
    """
    How easily can people/goods move?
    
    Inputs:
    - Road network status
    - Public transport disruptions
    - Fuel availability
    - Weather conditions
    - Civil unrest (blocked roads)
    
    Output: 0-100 score (100 = fully available)
    """
    
    # Gather relevant national indicators
    road_status = get_indicator_value('ENV_ROAD_STATUS', national_indicators)
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    weather = get_indicator_value('ENV_WEATHER_SEV', national_indicators)
    unrest = get_indicator_value('POL_UNREST_01', national_indicators)
    
    # Calculate base score (inverse of problems)
    base_score = 100
    
    # Road issues reduce availability
    if road_status < 70:
        base_score -= (70 - road_status) * 0.5
    
    # Fuel shortage reduces availability
    if fuel_avail < 50:
        base_score -= (50 - fuel_avail) * 0.8
    
    # Severe weather reduces availability
    if weather > 60:
        base_score -= (weather - 60) * 0.6
    
    # Civil unrest blocks roads
    if unrest > 70:
        base_score -= (unrest - 70) * 1.0
    
    # Company-specific adjustment
    # If company is in multiple cities, average across locations
    if len(company_profile['locations']) > 1:
        location_scores = []
        for location in company_profile['locations']:
            loc_score = adjust_for_location(base_score, location, national_indicators)
            location_scores.append(loc_score)
        
        final_score = sum(location_scores) / len(location_scores)
    else:
        final_score = base_score
    
    return max(0, min(100, final_score))
```

**Universal Indicator 2: Workforce Availability**

```python
def calculate_workforce_availability(national_indicators, company_profile):
    """
    Can employees reach workplace and perform their duties?
    
    Inputs:
    - Transportation availability
    - Health alerts (epidemics)
    - Strike activity (in related sectors)
    - Safety concerns
    
    Output: 0-100 score (100 = full workforce available)
    """
    
    transport_avail = calculate_transportation_availability(national_indicators, company_profile)
    health_alerts = get_indicator_value('SOCIAL_HEALTH_ALERTS', national_indicators)
    strike_activity = get_indicator_value('POL_STRIKE_ACTIVITY', national_indicators)
    safety = get_indicator_value('SOCIAL_SAFETY_PERCEPTION', national_indicators)
    
    # Base score
    base_score = 100
    
    # Transport issues prevent employees from reaching work
    transport_impact = (100 - transport_avail) * 0.4
    base_score -= transport_impact
    
    # Health alerts cause sick leave / absenteeism
    if health_alerts > 50:
        health_impact = (health_alerts - 50) * 0.3
        base_score -= health_impact
    
    # Strikes in related sectors (transport, fuel) affect commute
    if strike_activity > 60:
        strike_impact = (strike_activity - 60) * 0.4
        base_score -= strike_impact
    
    # Safety concerns keep people home
    if safety < 50:
        safety_impact = (50 - safety) * 0.3
        base_score -= safety_impact
    
    return max(0, min(100, base_score))
```

**Universal Indicator 3: Supply Chain Integrity**

```python
def calculate_supply_chain_integrity(national_indicators, company_profile):
    """
    Can supplies reach the business?
    
    Inputs:
    - Port operations (for imports)
    - Road network
    - Fuel availability
    - Import policy stability
    - Currency stability (affects import costs)
    
    Output: 0-100 score (100 = supply chain fully intact)
    """
    
    port_ops = get_indicator_value('ECON_PORT_OPS', national_indicators)
    road_status = get_indicator_value('ENV_ROAD_STATUS', national_indicators)
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    import_policy = get_indicator_value('LEGAL_IMPORT_POLICY', national_indicators)
    currency = get_indicator_value('ECON_CURRENCY_STAB', national_indicators)
    
    # Company's import dependency determines port/currency weight
    import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
    
    # Calculate weighted score
    supply_chain_score = (
        port_ops * 0.30 * import_dep +          # Port matters more if you import
        road_status * 0.25 +
        fuel_avail * 0.25 +
        import_policy * 0.10 * import_dep +
        currency * 0.10 * import_dep
    )
    
    # Adjust for local sourcing (less vulnerable)
    local_sourcing = 1 - import_dep
    resilience_bonus = local_sourcing * 10  # Up to 10 points bonus
    
    final_score = supply_chain_score + resilience_bonus
    
    return max(0, min(100, final_score))
```

**Universal Indicator 4: Operational Cost Pressure**

```python
def calculate_operational_cost_pressure(national_indicators, company_profile):
    """
    Are operating costs increasing?
    
    Inputs:
    - Fuel prices
    - Inflation pressure
    - Currency depreciation (for importers)
    - Utility costs
    - Wage pressure
    
    Output: 0-100 score (100 = extreme cost pressure, 0 = stable)
    """
    
    fuel_prices = get_indicator_value('ECON_FUEL_PRICES', national_indicators)
    inflation = get_indicator_value('ECON_INFLATION_PRESSURE', national_indicators)
    currency = get_indicator_value('ECON_CURRENCY_STAB', national_indicators)
    wage_pressure = get_indicator_value('SOCIAL_WAGE_PRESSURE', national_indicators)
    
    # Base cost pressure
    cost_pressure = 0
    
    # Fuel cost impact (varies by dependency)
    fuel_dependency = company_profile['critical_dependencies'].get('fuel', 'medium')
    fuel_weight = {'critical': 0.40, 'high': 0.30, 'medium': 0.20, 'low': 0.10}
    
    if fuel_prices > 50:  # Assume 50 is baseline
        cost_pressure += (fuel_prices - 50) * fuel_weight.get(fuel_dependency, 0.20)
    
    # Inflation affects all costs
    if inflation > 50:
        cost_pressure += (inflation - 50) * 0.30
    
    # Currency depreciation affects importers
    import_dep = company_profile.get('supply_chain', {}).get('import_dependency', 0.5)
    if currency < 50:  # Lower score = weaker currency
        cost_pressure += (50 - currency) * 0.20 * import_dep
    
    # Wage pressure
    if wage_pressure > 50:
        cost_pressure += (wage_pressure - 50) * 0.15
    
    return max(0, min(100, cost_pressure))
```

**Universal Indicator 5: Regulatory Compliance Status**

```python
def calculate_regulatory_compliance_status(national_indicators, company_profile):
    """
    Are there new compliance requirements or changes?
    
    Inputs:
    - New laws/regulations announced
    - Tax policy changes
    - Industry-specific regulations
    
    Output: 0-100 score (100 = high burden/many changes, 0 = stable)
    """
    
    legal_changes = get_indicator_value('LEGAL_REGULATORY_CHANGES', national_indicators)
    tax_changes = get_indicator_value('LEGAL_TAX_POLICY', national_indicators)
    
    # Frequency of changes indicates burden
    compliance_burden = (
        legal_changes * 0.60 +
        tax_changes * 0.40
    )
    
    return max(0, min(100, compliance_burden))
```

---

## INDUSTRY-SPECIFIC INDICATORS {#industry-specific}

### 3.8 RETAIL SECTOR INDICATORS

**Indicator: Expected Foot Traffic Impact**

```python
def calculate_retail_footfall_impact(national_indicators, company_profile):
    """
    For retail businesses: How will store foot traffic be affected?
    
    Formula:
    Base Footfall * Adjustment Factors
    
    Factors:
    - Weather (rain/heat reduces traffic)
    - Transportation availability (can customers reach store?)
    - Consumer confidence (willing to spend?)
    - Safety perception (is it safe to go out?)
    - Events/holidays
    """
    
    # Get base historical average
    base_footfall = company_profile.get('avg_daily_footfall', 1000)
    
    # Adjustment factors (multiplicative)
    adjustment = 1.0
    
    # Weather impact
    weather = get_indicator_value('ENV_WEATHER_SEV', national_indicators)
    if weather > 60:  # Severe weather
        weather_factor = 1 - ((weather - 60) / 40 * 0.30)  # Up to -30%
        adjustment *= weather_factor
    
    # Transportation
    transport_avail = calculate_transportation_availability(national_indicators, company_profile)
    transport_factor = transport_avail / 100
    adjustment *= (0.7 + transport_factor * 0.3)  # Transport affects 30% of traffic
    
    # Consumer confidence
    consumer_conf = get_indicator_value('ECON_CONSUMER_CONF', national_indicators)
    confidence_factor = consumer_conf / 100
    adjustment *= (0.8 + confidence_factor * 0.2)  # Confidence affects 20%
    
    # Safety perception
    safety = get_indicator_value('SOCIAL_SAFETY_PERCEPTION', national_indicators)
    safety_factor = safety / 100
    adjustment *= (0.75 + safety_factor * 0.25)  # Safety affects 25%
    
    # Civil unrest (people stay home)
    unrest = get_indicator_value('POL_UNREST_01', national_indicators)
    if unrest > 70:
        unrest_factor = 1 - ((unrest - 70) / 30 * 0.40)  # Up to -40%
        adjustment *= unrest_factor
    
    # Calculate impact as percentage change
    adjusted_footfall = base_footfall * adjustment
    impact_percentage = ((adjusted_footfall - base_footfall) / base_footfall) * 100
    
    return {
        'base_footfall': base_footfall,
        'expected_footfall': adjusted_footfall,
        'impact_percentage': impact_percentage,
        'confidence': 0.75
    }
```

### 3.9 MANUFACTURING SECTOR INDICATORS

**Indicator: Production Capacity Utilization**

```python
def calculate_manufacturing_capacity(national_indicators, company_profile):
    """
    For manufacturers: What % of production capacity can be utilized?
    
    Factors:
    - Power supply reliability (can machines run?)
    - Raw material availability
    - Workforce availability
    - Fuel for generators/transport
    """
    
    # Start with 100% capacity
    capacity = 100.0
    
    # Power outages reduce capacity
    power_reliability = get_indicator_value('ENV_POWER_RELIABILITY', national_indicators)
    if power_reliability < 100:
        # If power is 70% reliable, capacity drops proportionally
        capacity *= (power_reliability / 100)
    
    # Raw material availability
    supply_chain = calculate_supply_chain_integrity(national_indicators, company_profile)
    # If supply chain is 60%, may have material shortages
    if supply_chain < 80:
        material_factor = supply_chain / 100
        capacity *= (0.5 + material_factor * 0.5)  # Partial impact
    
    # Workforce
    workforce_avail = calculate_workforce_availability(national_indicators, company_profile)
    workforce_factor = workforce_avail / 100
    capacity *= workforce_factor
    
    # Fuel (for generators, logistics within factory)
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    if fuel_avail < 50:
        fuel_factor = 0.7 + (fuel_avail / 100 * 0.3)
        capacity *= fuel_factor
    
    return max(0, min(100, capacity))
```

### 3.10 LOGISTICS SECTOR INDICATORS

**Indicator: Fleet Availability**

```python
def calculate_logistics_fleet_availability(national_indicators, company_profile):
    """
    For logistics companies: What % of fleet can operate?
    
    Critical factors:
    - Fuel availability (can't run without fuel)
    - Route viability (blocked roads)
    - Driver availability
    - Vehicle maintenance (parts availability)
    """
    
    # Base fleet size
    total_fleet = company_profile.get('fleet_size', 50)
    available_fleet = total_fleet
    
    # Fuel is CRITICAL - direct proportional impact
    fuel_avail = get_indicator_value('ECON_FUEL_AVAIL', national_indicators)
    fuel_factor = fuel_avail / 100
    available_fleet *= fuel_factor
    
    # Route viability
    road_status = get_indicator_value('ENV_ROAD_STATUS', national_indicators)
    unrest = get_indicator_value('POL_UNREST_01', national_indicators)
    
    if road_status < 70 or unrest > 70:
        route_factor = min(road_status, 100 - unrest) / 100
        available_fleet *= (0.6 + route_factor * 0.4)  # Routes affect 40% of fleet
    
    # Driver availability
    workforce_avail = calculate_workforce_availability(national_indicators, company_profile)
    driver_factor = workforce_avail / 100
    available_fleet *= driver_factor
    
    # Express as percentage
    fleet_availability_pct = (available_fleet / total_fleet) * 100
    
    return {
        'total_fleet': total_fleet,
        'available_vehicles': int(available_fleet),
        'availability_percentage': fleet_availability_pct
    }
```

---

This completes Part 2 of the Layer 3 blueprint. The document provides comprehensive coverage of mock data strategy, impact translation, universal and industry-specific indicators, and detailed calculation methodologies.

The implementation can proceed with:
1. Mock data for independent development
2. Clear translation rules from national to operational
3. Pre-built calculation functions for common indicators
4. Industry-specific customizations

Would you like me to continue with the remaining sections (Forecasting, Recommendations, Scenarios, Implementation Checklist) or would you prefer to review what we have so far?

