"""
Layer Integration Adapters

Provides data transformation between layers:
- Layer2ToLayer3Adapter: Transforms national indicators to company-specific context
- Layer3ToLayer4Adapter: Transforms operational indicators to Layer 4 format
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .contracts import (
    Layer2Output,
    Layer3Input,
    Layer3Output,
    Layer4Input,
    IndicatorValueOutput,
    OperationalIndicatorOutput,
    TrendDirection,
    PESTELCategory,
)

logger = logging.getLogger(__name__)


class Layer2ToLayer3Adapter:
    """
    Adapts Layer 2 National Indicators output to Layer 3 Operational Indicators input
    
    This adapter:
    1. Maps national indicators to operational context
    2. Applies industry-specific translations
    3. Provides company-relevant filtering
    """
    
    # Mapping from PESTEL categories to operational categories
    # Layer 2 now outputs 105 real indicators with their PESTEL categories
    PESTEL_TO_OPERATIONAL = {
        "Political": {
            "supply_chain": 0.3,      # Political instability affects supply chains
            "workforce": 0.2,          # Strikes, unrest affect workforce
            "infrastructure": 0.1,
            "cost_pressure": 0.1,
            "market_conditions": 0.2,
            "financial": 0.1,
            "regulatory": 0.5,         # Political changes drive regulation
        },
        "Economic": {
            "supply_chain": 0.4,
            "workforce": 0.2,
            "infrastructure": 0.1,
            "cost_pressure": 0.5,      # Economic factors drive costs
            "market_conditions": 0.5,  # Economic factors drive market
            "financial": 0.5,          # Economic factors drive finance
            "regulatory": 0.1,
        },
        "Social": {
            "supply_chain": 0.1,
            "workforce": 0.5,          # Social factors heavily impact workforce
            "infrastructure": 0.1,
            "cost_pressure": 0.2,
            "market_conditions": 0.4,  # Consumer behavior
            "financial": 0.1,
            "regulatory": 0.1,
        },
        "Technological": {
            "supply_chain": 0.2,
            "workforce": 0.3,          # Tech affects skills/automation
            "infrastructure": 0.5,     # Tech is infrastructure
            "cost_pressure": 0.2,
            "market_conditions": 0.3,
            "financial": 0.2,
            "regulatory": 0.2,
        },
        "Environmental": {
            "supply_chain": 0.4,       # Weather, disasters affect supply
            "workforce": 0.2,
            "infrastructure": 0.4,     # Environmental affects infrastructure
            "cost_pressure": 0.3,
            "market_conditions": 0.2,
            "financial": 0.1,
            "regulatory": 0.3,
        },
        "Legal": {
            "supply_chain": 0.2,
            "workforce": 0.3,          # Labor laws
            "infrastructure": 0.1,
            "cost_pressure": 0.4,      # Compliance costs
            "market_conditions": 0.2,
            "financial": 0.3,
            "regulatory": 0.6,         # Legal directly affects regulation
        },
    }
    
    # Legacy mapping for backwards compatibility
    INDICATOR_MAPPING = {
        # Economic indicators -> Supply Chain, Cost, Financial
        "ECON_GDP_SENTIMENT": ["supply_chain", "market_conditions"],
        "ECON_INFLATION": ["cost_pressure", "financial"],
        "ECON_EMPLOYMENT": ["workforce", "market_conditions"],
        "ECON_TRADE_BALANCE": ["supply_chain", "cost_pressure"],
        "ECON_INTEREST_RATE": ["financial", "cost_pressure"],
        "ECON_CONSUMER_CONFIDENCE": ["market_conditions"],
        "ECON_BUSINESS_CONFIDENCE": ["market_conditions", "financial"],
        
        # Political indicators -> Regulatory, Supply Chain
        "POL_STABILITY": ["supply_chain", "regulatory"],
        "POL_POLICY_CHANGES": ["regulatory", "cost_pressure"],
        "POL_CORRUPTION": ["regulatory", "cost_pressure"],
        "POL_GOVERNMENT_SPENDING": ["market_conditions", "infrastructure"],
        
        # Social indicators -> Workforce, Market
        "SOC_EMPLOYMENT_TRENDS": ["workforce"],
        "SOC_CONSUMER_BEHAVIOR": ["market_conditions"],
        "SOC_EDUCATION": ["workforce"],
        "SOC_HEALTH_INDEX": ["workforce", "cost_pressure"],
        "SOC_MIGRATION": ["workforce", "market_conditions"],
        
        # Technological indicators -> Infrastructure, Cost
        "TECH_DIGITAL_ADOPTION": ["infrastructure"],
        "TECH_INNOVATION": ["market_conditions", "infrastructure"],
        "TECH_CONNECTIVITY": ["infrastructure"],
        "TECH_AUTOMATION": ["workforce", "cost_pressure"],
        
        # Environmental indicators -> Supply Chain, Cost, Infrastructure
        "ENV_CLIMATE_EVENTS": ["supply_chain", "infrastructure"],
        "ENV_RESOURCE_AVAILABILITY": ["supply_chain", "cost_pressure"],
        "ENV_POLLUTION": ["regulatory", "cost_pressure"],
        "ENV_SUSTAINABILITY": ["regulatory", "market_conditions"],
        
        # Legal indicators -> Regulatory, Cost
        "LEG_COMPLIANCE": ["regulatory", "cost_pressure"],
        "LEG_LABOR_LAWS": ["workforce", "regulatory"],
        "LEG_TAX_POLICY": ["financial", "cost_pressure"],
        "LEG_TRADE_REGULATIONS": ["supply_chain", "regulatory"],
    }
    
    # Industry sensitivity multipliers
    INDUSTRY_SENSITIVITY = {
        "retail": {
            "supply_chain": 1.2,
            "workforce": 0.9,
            "infrastructure": 0.8,
            "cost_pressure": 1.1,
            "market_conditions": 1.3,
            "financial": 1.0,
            "regulatory": 0.9,
        },
        "manufacturing": {
            "supply_chain": 1.4,
            "workforce": 1.1,
            "infrastructure": 1.3,
            "cost_pressure": 1.2,
            "market_conditions": 1.0,
            "financial": 1.0,
            "regulatory": 1.1,
        },
        "logistics": {
            "supply_chain": 1.5,
            "workforce": 1.0,
            "infrastructure": 1.4,
            "cost_pressure": 1.3,
            "market_conditions": 0.9,
            "financial": 0.9,
            "regulatory": 1.0,
        },
        "hospitality": {
            "supply_chain": 0.8,
            "workforce": 1.4,
            "infrastructure": 1.0,
            "cost_pressure": 1.1,
            "market_conditions": 1.4,
            "financial": 1.1,
            "regulatory": 1.0,
        },
        "technology": {
            "supply_chain": 0.7,
            "workforce": 1.3,
            "infrastructure": 1.5,
            "cost_pressure": 0.9,
            "market_conditions": 1.2,
            "financial": 1.1,
            "regulatory": 1.0,
        },
        "healthcare": {
            "supply_chain": 1.1,
            "workforce": 1.4,
            "infrastructure": 1.2,
            "cost_pressure": 1.0,
            "market_conditions": 0.8,
            "financial": 1.0,
            "regulatory": 1.5,
        },
        "finance": {
            "supply_chain": 0.5,
            "workforce": 1.1,
            "infrastructure": 1.3,
            "cost_pressure": 0.8,
            "market_conditions": 1.2,
            "financial": 1.5,
            "regulatory": 1.4,
        },
    }
    
    def __init__(self):
        self.default_sensitivity = {
            "supply_chain": 1.0,
            "workforce": 1.0,
            "infrastructure": 1.0,
            "cost_pressure": 1.0,
            "market_conditions": 1.0,
            "financial": 1.0,
            "regulatory": 1.0,
        }
    
    def adapt(
        self,
        layer2_output: Layer2Output,
        company_profile: Dict[str, Any],
        industry_config: Optional[Dict[str, Any]] = None
    ) -> Layer3Input:
        """
        Transform Layer 2 output to Layer 3 input format
        
        Args:
            layer2_output: Validated Layer 2 output
            company_profile: Company information
            industry_config: Optional industry-specific configuration
            
        Returns:
            Layer3Input ready for Layer 3 processing
        """
        logger.info(f"Adapting Layer 2 output for company: {company_profile.get('company_id')}")
        
        return Layer3Input(
            national_indicators=layer2_output,
            company_profile=company_profile,
            industry_config=industry_config
        )
    
    def get_relevant_indicators(
        self,
        layer2_output: Layer2Output,
        industry: str
    ) -> Dict[str, List[IndicatorValueOutput]]:
        """
        Filter and group indicators relevant to an industry
        
        Args:
            layer2_output: Layer 2 output
            industry: Industry type
            
        Returns:
            Dictionary grouped by operational category
        """
        industry_lower = industry.lower()
        sensitivity = self.INDUSTRY_SENSITIVITY.get(industry_lower, self.default_sensitivity)
        
        categorized = {
            "supply_chain": [],
            "workforce": [],
            "infrastructure": [],
            "cost_pressure": [],
            "market_conditions": [],
            "financial": [],
            "regulatory": [],
        }
        
        for indicator_id, indicator in layer2_output.indicators.items():
            # First try legacy mapping
            categories = self.INDICATOR_MAPPING.get(indicator_id, [])
            
            # If no legacy mapping, use PESTEL category-based mapping
            if not categories:
                pestel_cat = indicator.pestel_category
                if hasattr(pestel_cat, 'value'):
                    pestel_cat = pestel_cat.value
                
                # Get the operational category weights for this PESTEL category
                category_weights = self.PESTEL_TO_OPERATIONAL.get(pestel_cat, {})
                
                # Add to all operational categories with weight > 0.2
                for op_cat, weight in category_weights.items():
                    if weight >= 0.2 and op_cat in categorized:
                        if sensitivity.get(op_cat, 1.0) > 0.5:
                            categorized[op_cat].append(indicator)
            else:
                # Use legacy mapping
                for category in categories:
                    if category in categorized:
                        if sensitivity.get(category, 1.0) > 0.5:
                            categorized[category].append(indicator)
        
        return categorized
    
    def calculate_category_impact(
        self,
        indicators: List[IndicatorValueOutput],
        sensitivity: float = 1.0
    ) -> float:
        """
        Calculate weighted impact for a category
        
        Args:
            indicators: List of indicators in this category
            sensitivity: Industry sensitivity multiplier
            
        Returns:
            Weighted impact score 0-100
        """
        if not indicators:
            return 50.0  # Neutral if no data
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for ind in indicators:
            weight = ind.confidence
            value = ind.value * sensitivity
            weighted_sum += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50.0
        
        return min(100.0, max(0.0, weighted_sum / total_weight))


class Layer3ToLayer4Adapter:
    """
    Adapts Layer 3 Operational Indicators output to Layer 4 Business Insights input
    
    This adapter:
    1. Converts Layer3Output to OperationalIndicators for Layer 4
    2. Prepares company profile for Layer 4 processing
    3. Adds historical context and benchmarks
    """
    
    # Mapping from Layer 3 categories to Layer 4 operational indicators
    LAYER4_INDICATOR_MAPPING = {
        "supply_chain_health": ["OPS_SUPPLY_CHAIN", "OPS_TRANSPORT_AVAIL", "OPS_LOGISTICS_COST", "OPS_IMPORT_FLOW"],
        "workforce_health": ["OPS_WORKFORCE_AVAIL", "OPS_LABOR_COST", "OPS_PRODUCTIVITY"],
        "infrastructure_health": ["OPS_POWER_RELIABILITY", "OPS_FUEL_AVAIL", "OPS_WATER_SUPPLY", "OPS_INTERNET_CONNECTIVITY"],
        "cost_pressure": ["OPS_COST_PRESSURE", "OPS_RAW_MATERIAL_COST", "OPS_ENERGY_COST"],
        "market_conditions": ["OPS_DEMAND_LEVEL", "OPS_COMPETITION_INTENSITY", "OPS_PRICING_POWER"],
        "financial_health": ["OPS_CASH_FLOW", "OPS_CREDIT_AVAIL", "OPS_PAYMENT_DELAYS"],
        "regulatory_burden": ["OPS_REGULATORY_BURDEN", "OPS_COMPLIANCE_COST"],
    }
    
    def adapt(
        self,
        layer3_output: Layer3Output,
        company_profile: Dict[str, Any],
        historical_context: Optional[Dict[str, Any]] = None,
        industry_benchmarks: Optional[Dict[str, Any]] = None
    ) -> Layer4Input:
        """
        Transform Layer 3 output to Layer 4 input format
        
        Args:
            layer3_output: Validated Layer 3 output
            company_profile: Company information
            historical_context: Optional historical patterns
            industry_benchmarks: Optional industry benchmarks
            
        Returns:
            Layer4Input ready for Layer 4 processing
        """
        logger.info(f"Adapting Layer 3 output for company: {layer3_output.company_id}")
        
        return Layer4Input(
            operational_indicators=layer3_output,
            company_profile=company_profile,
            historical_context=historical_context,
            industry_benchmarks=industry_benchmarks
        )
    
    def to_layer4_indicators(
        self,
        layer3_output: Layer3Output
    ) -> Dict[str, float]:
        """
        Convert Layer 3 output to Layer 4 OperationalIndicators format
        
        This creates the indicator dictionary expected by Layer 4's
        RiskDetector and other components.
        
        Args:
            layer3_output: Layer 3 output
            
        Returns:
            Dictionary of indicator_code -> value (0-100)
        """
        indicators = {}
        
        # Map category health scores to individual indicators
        for category, indicator_codes in self.LAYER4_INDICATOR_MAPPING.items():
            category_value = getattr(layer3_output, category, 50.0)
            
            # Distribute category value with slight variation
            for i, code in enumerate(indicator_codes):
                # Add small variation to avoid all same values
                variation = (i - len(indicator_codes) / 2) * 2
                indicators[code] = min(100.0, max(0.0, category_value + variation))
        
        # Also include any explicit indicators from Layer 3
        for code, ind in layer3_output.indicators.items():
            # Use Layer3 indicator code directly if it starts with OPS_
            if code.startswith("OPS_"):
                indicators[code] = ind.value
        
        return indicators
    
    def to_layer4_trends(
        self,
        layer3_output: Layer3Output
    ) -> Dict[str, str]:
        """
        Convert Layer 3 trends to Layer 4 format
        
        Args:
            layer3_output: Layer 3 output
            
        Returns:
            Dictionary of indicator_code -> trend direction
        """
        trends = {}
        
        for code, direction in layer3_output.trends.items():
            if isinstance(direction, TrendDirection):
                trends[code] = direction.value
            else:
                trends[code] = str(direction)
        
        return trends
    
    def get_critical_indicators(
        self,
        layer3_output: Layer3Output,
        threshold: float = 30.0
    ) -> List[Dict[str, Any]]:
        """
        Identify indicators below critical threshold
        
        Args:
            layer3_output: Layer 3 output
            threshold: Value below which indicator is critical
            
        Returns:
            List of critical indicators with details
        """
        critical = []
        
        # Check category health scores
        categories = [
            ("supply_chain_health", "Supply Chain"),
            ("workforce_health", "Workforce"),
            ("infrastructure_health", "Infrastructure"),
            ("financial_health", "Financial"),
            ("market_conditions", "Market"),
        ]
        
        for attr, name in categories:
            value = getattr(layer3_output, attr, 50.0)
            if value < threshold:
                critical.append({
                    "category": name,
                    "value": value,
                    "severity": "critical" if value < 20 else "high",
                    "source": f"layer3.{attr}"
                })
        
        # Check cost pressure (inverse - high is bad)
        cost_pressure = layer3_output.cost_pressure
        if cost_pressure > (100 - threshold):
            critical.append({
                "category": "Cost Pressure",
                "value": cost_pressure,
                "severity": "critical" if cost_pressure > 80 else "high",
                "source": "layer3.cost_pressure"
            })
        
        # Check regulatory burden (inverse - high is bad)
        regulatory = layer3_output.regulatory_burden
        if regulatory > (100 - threshold):
            critical.append({
                "category": "Regulatory Burden",
                "value": regulatory,
                "severity": "high",
                "source": "layer3.regulatory_burden"
            })
        
        return critical


class MockDataGenerator:
    """
    Generates mock data for testing layer integration
    
    Replaces individual layer mock data with integrated mock data
    that flows properly through the pipeline.
    """
    
    def __init__(self, seed: Optional[int] = None):
        import random
        if seed:
            random.seed(seed)
        self._random = random
    
    def generate_layer2_output(
        self,
        scenario: str = "normal"
    ) -> Dict[str, Any]:
        """
        Generate realistic Layer 2 output
        
        Args:
            scenario: "normal", "crisis", "growth", "recession"
            
        Returns:
            Dictionary matching Layer2Output schema
        """
        now = datetime.now()
        
        # Base values by scenario
        scenarios = {
            "normal": {"base": 60, "variation": 15, "sentiment": 0.1},
            "crisis": {"base": 35, "variation": 20, "sentiment": -0.4},
            "growth": {"base": 75, "variation": 10, "sentiment": 0.5},
            "recession": {"base": 40, "variation": 15, "sentiment": -0.3},
        }
        
        config = scenarios.get(scenario, scenarios["normal"])
        
        indicators = {}
        trends = {}
        
        # Generate PESTEL indicators
        indicator_defs = [
            ("ECON_GDP_SENTIMENT", "GDP Sentiment", "Economic"),
            ("ECON_INFLATION", "Inflation Pressure", "Economic"),
            ("ECON_EMPLOYMENT", "Employment Level", "Economic"),
            ("POL_STABILITY", "Political Stability", "Political"),
            ("SOC_CONSUMER_BEHAVIOR", "Consumer Behavior", "Social"),
            ("TECH_DIGITAL_ADOPTION", "Digital Adoption", "Technological"),
            ("ENV_CLIMATE_EVENTS", "Climate Events", "Environmental"),
            ("LEG_COMPLIANCE", "Regulatory Compliance", "Legal"),
        ]
        
        for ind_id, ind_name, category in indicator_defs:
            value = config["base"] + self._random.uniform(-config["variation"], config["variation"])
            value = max(0, min(100, value))
            
            indicators[ind_id] = {
                "indicator_id": ind_id,
                "indicator_name": ind_name,
                "pestel_category": category,
                "timestamp": now.isoformat(),
                "value": value,
                "raw_count": self._random.randint(50, 200),
                "sentiment_score": config["sentiment"] + self._random.uniform(-0.2, 0.2),
                "confidence": 0.7 + self._random.uniform(0, 0.3),
                "source_count": self._random.randint(5, 20),
            }
            
            # Generate trend
            trend_options = ["rising", "falling", "stable"]
            if scenario == "crisis":
                trend_weights = [0.2, 0.6, 0.2]
            elif scenario == "growth":
                trend_weights = [0.6, 0.2, 0.2]
            else:
                trend_weights = [0.33, 0.33, 0.34]
            
            trends[ind_id] = {
                "indicator_id": ind_id,
                "direction": self._random.choices(trend_options, trend_weights)[0],
                "change_percent": self._random.uniform(-10, 10),
                "period_days": 7,
            }
        
        return {
            "timestamp": now.isoformat(),
            "calculation_window_hours": 24,
            "indicators": indicators,
            "trends": trends,
            "events": [],
            "overall_sentiment": config["sentiment"],
            "activity_level": config["base"],
            "article_count": self._random.randint(100, 500),
            "source_diversity": self._random.randint(10, 30),
            "data_quality_score": 0.8 + self._random.uniform(0, 0.2),
        }
    
    def generate_company_profile(
        self,
        company_id: str = "COMP001",
        industry: str = "retail"
    ) -> Dict[str, Any]:
        """
        Generate a company profile for testing
        
        Args:
            company_id: Company identifier
            industry: Industry type
            
        Returns:
            Company profile dictionary
        """
        return {
            "company_id": company_id,
            "company_name": f"Test Company {company_id}",
            "industry": industry,
            "size": "medium",
            "region": "Southeast Asia",
            "annual_revenue": 50000000,
            "employee_count": 500,
            "founded_year": 2010,
            "risk_tolerance": "moderate",
            "strategic_priorities": ["growth", "efficiency", "sustainability"],
        }
