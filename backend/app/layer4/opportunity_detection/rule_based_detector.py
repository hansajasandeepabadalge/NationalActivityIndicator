"""
Layer 4: Rule-Based Opportunity Detector

Detects business opportunities based on operational indicators using predefined rules.
Implements 10+ opportunity types across market, cost, strategic, and growth categories.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal

from app.layer4.schemas.opportunity_schemas import DetectedOpportunity
from app.layer4.mock_data.layer3_mock_generator import OperationalIndicators

logger = logging.getLogger(__name__)


class OpportunityRule:
    """Defines a single opportunity detection rule"""
    
    def __init__(
        self,
        code: str,
        name: str,
        category: str,
        subcategory: str,
        description_template: str,
        conditions: List[Dict[str, Any]],
        applicable_industries: Optional[List[str]] = None,
        applicable_scales: Optional[List[str]] = None,
        base_value: float = 5.0,
        base_feasibility: float = 0.7,
        window_days: int = 30
    ):
        self.code = code
        self.name = name
        self.category = category
        self.subcategory = subcategory
        self.description_template = description_template
        self.conditions = conditions
        self.applicable_industries = applicable_industries
        self.applicable_scales = applicable_scales
        self.base_value = base_value
        self.base_feasibility = base_feasibility
        self.window_days = window_days
    
    def is_applicable(self, industry: str, scale: str = "medium") -> bool:
        """Check if this rule applies to the given industry/scale"""
        if self.applicable_industries and industry not in self.applicable_industries:
            return False
        if self.applicable_scales and scale not in self.applicable_scales:
            return False
        return True


class RuleBasedOpportunityDetector:
    """
    Detects business opportunities using rule-based logic.
    
    Opportunity Categories:
    1. Market Opportunities (market share, expansion, pricing)
    2. Cost Opportunities (input costs, efficiency, labor)
    3. Strategic Opportunities (partnerships, acquisitions, diversification)
    4. Growth Opportunities (demand surge, export, innovation)
    """
    
    def __init__(self):
        self.rules = self._initialize_rules()
        logger.info(f"Initialized RuleBasedOpportunityDetector with {len(self.rules)} rules")
    
    def _initialize_rules(self) -> List[OpportunityRule]:
        """Initialize all opportunity detection rules"""
        
        rules = []
        
        # =======================================================================
        # MARKET OPPORTUNITIES
        # =======================================================================
        
        # 1. Market Share Capture Opportunity
        rules.append(OpportunityRule(
            code="OPP_MARKET_CAPTURE",
            name="Market Share Capture Opportunity",
            category="market",
            subcategory="competition",
            description_template=(
                "Competitor weaknesses detected while your supply chain and productivity "
                "remain strong. This creates a window to capture market share by "
                "emphasizing reliability and service quality."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 70,
                    "weight": 0.4
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_PRODUCTIVITY",
                    "threshold": 65,
                    "weight": 0.3
                },
                {
                    "type": "trend_positive",
                    "indicator": "OPS_DEMAND_LEVEL",
                    "weight": 0.3
                }
            ],
            base_value=7.5,
            base_feasibility=0.75,
            window_days=45
        ))
        
        # 2. Pricing Power Opportunity
        rules.append(OpportunityRule(
            code="OPP_PRICING_POWER",
            name="Premium Pricing Opportunity",
            category="market",
            subcategory="pricing",
            description_template=(
                "Strong demand with constrained market supply creates pricing power. "
                "Consider selective price increases or premium product positioning."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_DEMAND_LEVEL",
                    "threshold": 75,
                    "weight": 0.4
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_PRICING_POWER",
                    "threshold": 70,
                    "weight": 0.4
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 60,
                    "weight": 0.2
                }
            ],
            base_value=6.5,
            base_feasibility=0.8,
            window_days=30
        ))
        
        # 3. Market Expansion Opportunity
        rules.append(OpportunityRule(
            code="OPP_MARKET_EXPANSION",
            name="Geographic/Segment Expansion",
            category="market",
            subcategory="expansion",
            description_template=(
                "Strong operational capacity with good logistics support suggests "
                "readiness to expand into new geographic areas or customer segments."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 75,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_TRANSPORT_AVAIL",
                    "threshold": 70,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 65,
                    "weight": 0.2
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_WORKFORCE_AVAIL",
                    "threshold": 60,
                    "weight": 0.2
                }
            ],
            applicable_industries=["retail", "manufacturing", "logistics", "services"],
            base_value=8.0,
            base_feasibility=0.65,
            window_days=90
        ))
        
        # =======================================================================
        # COST OPPORTUNITIES
        # =======================================================================
        
        # 4. Input Cost Reduction Opportunity
        rules.append(OpportunityRule(
            code="OPP_COST_REDUCTION",
            name="Input Cost Reduction Window",
            category="cost",
            subcategory="procurement",
            description_template=(
                "Favorable conditions for reducing input costs through bulk purchasing, "
                "supplier renegotiation, or alternative sourcing. Raw material and "
                "energy costs are currently advantageous."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_RAW_MATERIAL_COST",
                    "threshold": 60,
                    "weight": 0.4
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_ENERGY_COST",
                    "threshold": 55,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 65,
                    "weight": 0.3
                }
            ],
            applicable_industries=["manufacturing", "construction", "food_processing"],
            base_value=6.0,
            base_feasibility=0.85,
            window_days=60
        ))
        
        # 5. Efficiency Improvement Opportunity
        rules.append(OpportunityRule(
            code="OPP_EFFICIENCY_GAIN",
            name="Operational Efficiency Improvement",
            category="cost",
            subcategory="operations",
            description_template=(
                "Current operational stability provides an ideal window for implementing "
                "efficiency improvements, automation, or process optimization without "
                "disrupting ongoing operations."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_POWER_RELIABILITY",
                    "threshold": 75,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_INTERNET_CONNECTIVITY",
                    "threshold": 70,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_WORKFORCE_AVAIL",
                    "threshold": 65,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 60,
                    "weight": 0.25
                }
            ],
            base_value=7.0,
            base_feasibility=0.70,
            window_days=120
        ))
        
        # 6. Labor Cost Optimization
        rules.append(OpportunityRule(
            code="OPP_LABOR_OPTIMIZATION",
            name="Workforce Optimization Opportunity",
            category="cost",
            subcategory="labor",
            description_template=(
                "Favorable labor market conditions enable workforce restructuring, "
                "training investments, or strategic hiring to improve productivity "
                "and reduce long-term labor costs."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_WORKFORCE_AVAIL",
                    "threshold": 70,
                    "weight": 0.4
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_LABOR_COST",
                    "threshold": 55,
                    "weight": 0.35
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 60,
                    "weight": 0.25
                }
            ],
            base_value=5.5,
            base_feasibility=0.75,
            window_days=90
        ))
        
        # =======================================================================
        # STRATEGIC OPPORTUNITIES
        # =======================================================================
        
        # 7. Partnership/Alliance Opportunity
        rules.append(OpportunityRule(
            code="OPP_STRATEGIC_PARTNER",
            name="Strategic Partnership Window",
            category="strategic",
            subcategory="partnership",
            description_template=(
                "Market conditions favor forming strategic partnerships or alliances. "
                "Consider collaborations that can strengthen supply chain, expand "
                "market reach, or share operational risks."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 60,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_DEMAND_LEVEL",
                    "threshold": 60,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CREDIT_AVAIL",
                    "threshold": 55,
                    "weight": 0.2
                },
                {
                    "type": "indicator_moderate",
                    "indicator": "OPS_COST_PRESSURE",
                    "min": 40,
                    "max": 70,
                    "weight": 0.2
                }
            ],
            base_value=7.5,
            base_feasibility=0.60,
            window_days=60
        ))
        
        # 8. Technology/Digital Transformation
        rules.append(OpportunityRule(
            code="OPP_DIGITAL_TRANSFORM",
            name="Digital Transformation Window",
            category="strategic",
            subcategory="technology",
            description_template=(
                "Infrastructure stability and workforce availability create an ideal "
                "opportunity for technology upgrades, digital transformation initiatives, "
                "or automation investments."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_INTERNET_CONNECTIVITY",
                    "threshold": 75,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_POWER_RELIABILITY",
                    "threshold": 80,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_WORKFORCE_AVAIL",
                    "threshold": 60,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 65,
                    "weight": 0.2
                }
            ],
            base_value=8.5,
            base_feasibility=0.55,
            window_days=180
        ))
        
        # =======================================================================
        # GROWTH OPPORTUNITIES
        # =======================================================================
        
        # 9. Demand Surge Capture
        rules.append(OpportunityRule(
            code="OPP_DEMAND_SURGE",
            name="Demand Surge Capture",
            category="growth",
            subcategory="demand",
            description_template=(
                "Significant increase in demand detected with operational capacity "
                "to handle it. Consider increasing production, extending hours, or "
                "temporary capacity expansion."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_DEMAND_LEVEL",
                    "threshold": 80,
                    "weight": 0.4
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 65,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_WORKFORCE_AVAIL",
                    "threshold": 60,
                    "weight": 0.2
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_POWER_RELIABILITY",
                    "threshold": 65,
                    "weight": 0.15
                }
            ],
            applicable_industries=["retail", "manufacturing", "hospitality", "services"],
            base_value=8.0,
            base_feasibility=0.80,
            window_days=30
        ))
        
        # 10. Export Opportunity
        rules.append(OpportunityRule(
            code="OPP_EXPORT_EXPANSION",
            name="Export Market Expansion",
            category="growth",
            subcategory="export",
            description_template=(
                "Favorable currency conditions combined with strong logistics make "
                "this an optimal time to expand export activities or enter new "
                "international markets."
            ),
            conditions=[
                {
                    "type": "indicator_above",  # Strong supply chain for exports
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 75,
                    "weight": 0.35
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_LOGISTICS_COST",
                    "threshold": 55,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_IMPORT_FLOW",
                    "threshold": 60,
                    "weight": 0.25
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_PRODUCTIVITY",
                    "threshold": 65,
                    "weight": 0.15
                }
            ],
            applicable_industries=["manufacturing", "agriculture", "textiles", "it_services"],
            base_value=7.5,
            base_feasibility=0.60,
            window_days=90
        ))
        
        # 11. Talent Acquisition Opportunity
        rules.append(OpportunityRule(
            code="OPP_TALENT_ACQUISITION",
            name="Strategic Talent Acquisition",
            category="growth",
            subcategory="talent",
            description_template=(
                "Strong workforce availability in the market presents an opportunity "
                "to acquire key talent, build teams for new initiatives, or upgrade "
                "workforce capabilities."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_WORKFORCE_AVAIL",
                    "threshold": 75,
                    "weight": 0.5
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 60,
                    "weight": 0.3
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_LABOR_COST",
                    "threshold": 50,
                    "weight": 0.2
                }
            ],
            base_value=6.5,
            base_feasibility=0.85,
            window_days=60
        ))
        
        # 12. Inventory/Stock Building Opportunity
        rules.append(OpportunityRule(
            code="OPP_INVENTORY_BUILD",
            name="Strategic Inventory Building",
            category="growth",
            subcategory="inventory",
            description_template=(
                "Current favorable supply conditions and pricing present an opportunity "
                "to build strategic inventory reserves at advantageous costs, protecting "
                "against future supply disruptions or price increases."
            ),
            conditions=[
                {
                    "type": "indicator_above",
                    "indicator": "OPS_SUPPLY_CHAIN",
                    "threshold": 80,
                    "weight": 0.35
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_RAW_MATERIAL_COST",
                    "threshold": 65,
                    "weight": 0.35
                },
                {
                    "type": "indicator_above",
                    "indicator": "OPS_CASH_FLOW",
                    "threshold": 70,
                    "weight": 0.3
                }
            ],
            applicable_industries=["retail", "manufacturing", "wholesale"],
            base_value=6.0,
            base_feasibility=0.90,
            window_days=45
        ))
        
        return rules
    
    def detect_opportunities(
        self,
        company_id: str,
        industry: str,
        indicators: OperationalIndicators,
        business_scale: str = "medium"
    ) -> List[DetectedOpportunity]:
        """
        Detect opportunities for a company based on their operational indicators.
        
        Args:
            company_id: Unique company identifier
            industry: Company's industry sector
            indicators: Current operational indicators
            business_scale: Company size (small, medium, large)
            
        Returns:
            List of detected opportunities
        """
        opportunities = []
        indicator_dict = indicators.model_dump()
        
        for rule in self.rules:
            # Check industry/scale applicability
            if not rule.is_applicable(industry, business_scale):
                continue
            
            # Evaluate rule conditions
            evaluation = self._evaluate_conditions(rule, indicator_dict)
            
            if evaluation['triggered']:
                opportunity = self._create_opportunity(
                    rule=rule,
                    company_id=company_id,
                    evaluation=evaluation,
                    indicators=indicator_dict
                )
                opportunities.append(opportunity)
        
        # Sort by final score (highest first)
        opportunities.sort(key=lambda x: x.final_score, reverse=True)
        
        logger.info(
            f"Detected {len(opportunities)} opportunities for company {company_id} "
            f"in industry {industry}"
        )
        
        return opportunities
    
    def _evaluate_conditions(
        self,
        rule: OpportunityRule,
        indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate if rule conditions are met"""
        
        total_weight = 0.0
        weighted_score = 0.0
        triggered_conditions = []
        all_required_met = True
        
        for condition in rule.conditions:
            cond_type = condition['type']
            indicator_name = condition.get('indicator')
            weight = condition.get('weight', 1.0)
            
            if indicator_name and indicator_name not in indicators:
                logger.warning(f"Indicator {indicator_name} not found for rule {rule.code}")
                continue
            
            indicator_value = indicators.get(indicator_name, 50) if indicator_name else 50
            condition_met = False
            condition_score = 0.0
            
            if cond_type == 'indicator_above':
                threshold = condition['threshold']
                if indicator_value >= threshold:
                    condition_met = True
                    # Score based on how much above threshold
                    condition_score = min(1.0, (indicator_value - threshold) / 30 + 0.5)
                    triggered_conditions.append({
                        'indicator': indicator_name,
                        'value': indicator_value,
                        'threshold': threshold,
                        'type': 'above'
                    })
            
            elif cond_type == 'indicator_below':
                threshold = condition['threshold']
                if indicator_value <= threshold:
                    condition_met = True
                    condition_score = min(1.0, (threshold - indicator_value) / 30 + 0.5)
                    triggered_conditions.append({
                        'indicator': indicator_name,
                        'value': indicator_value,
                        'threshold': threshold,
                        'type': 'below'
                    })
            
            elif cond_type == 'indicator_moderate':
                min_val = condition['min']
                max_val = condition['max']
                if min_val <= indicator_value <= max_val:
                    condition_met = True
                    # Score highest at middle of range
                    mid = (min_val + max_val) / 2
                    distance_from_mid = abs(indicator_value - mid)
                    max_distance = (max_val - min_val) / 2
                    condition_score = 1.0 - (distance_from_mid / max_distance) * 0.5
                    triggered_conditions.append({
                        'indicator': indicator_name,
                        'value': indicator_value,
                        'range': [min_val, max_val],
                        'type': 'moderate'
                    })
            
            elif cond_type == 'trend_positive':
                # Check if the indicator has a positive trend
                trend = indicators.get('trends', {}).get(indicator_name, 'stable')
                if trend == 'rising':
                    condition_met = True
                    condition_score = 0.8
                    triggered_conditions.append({
                        'indicator': indicator_name,
                        'trend': trend,
                        'type': 'trend'
                    })
            
            if condition_met:
                weighted_score += weight * condition_score
            else:
                all_required_met = False
            
            total_weight += weight
        
        # Normalize score
        final_score = (weighted_score / total_weight) if total_weight > 0 else 0
        
        # Require at least 60% of weighted conditions met to trigger
        triggered = final_score >= 0.6 and len(triggered_conditions) >= len(rule.conditions) // 2
        
        return {
            'triggered': triggered,
            'score': final_score,
            'triggered_conditions': triggered_conditions,
            'condition_count': len(triggered_conditions),
            'total_conditions': len(rule.conditions)
        }
    
    def _create_opportunity(
        self,
        rule: OpportunityRule,
        company_id: str,
        evaluation: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> DetectedOpportunity:
        """Create a DetectedOpportunity from a triggered rule"""
        
        now = datetime.utcnow()
        
        # Calculate potential value (0-10)
        base_value = Decimal(str(rule.base_value))
        value_modifier = Decimal(str(evaluation['score']))
        potential_value = min(Decimal('10.0'), base_value * value_modifier)
        
        # Calculate feasibility (0-1)
        base_feasibility = Decimal(str(rule.base_feasibility))
        # Adjust feasibility based on cash flow and operational stability
        cash_flow = indicators.get('OPS_CASH_FLOW', 50)
        feasibility_adj = Decimal(str(1.0 + (cash_flow - 50) / 200))
        feasibility = min(Decimal('1.0'), base_feasibility * feasibility_adj)
        
        # Calculate timing score (0-1)
        # Better timing when conditions strongly met
        timing_score = Decimal(str(min(1.0, evaluation['score'] * 1.2)))
        
        # Strategic fit (0-1) - base on overall operational health
        avg_ops = sum(
            v for k, v in indicators.items() 
            if isinstance(v, (int, float)) and k.startswith('OPS_')
        ) / max(1, len([k for k in indicators if k.startswith('OPS_')]))
        strategic_fit = Decimal(str(min(1.0, avg_ops / 100 * 1.3)))
        
        # Final score calculation
        final_score = (
            potential_value * Decimal('0.4') +
            feasibility * Decimal('10') * Decimal('0.25') +
            timing_score * Decimal('10') * Decimal('0.2') +
            strategic_fit * Decimal('10') * Decimal('0.15')
        )
        final_score = min(Decimal('10.0'), final_score)
        
        # Determine priority
        if final_score >= 7:
            priority = 'high'
        elif final_score >= 4:
            priority = 'medium'
        else:
            priority = 'low'
        
        # Build triggering indicators
        triggering_indicators = {
            cond['indicator']: {
                'value': cond.get('value'),
                'threshold': cond.get('threshold'),
                'type': cond['type']
            }
            for cond in evaluation['triggered_conditions']
            if 'indicator' in cond
        }
        
        # Generate reasoning
        reasoning = self._generate_reasoning(rule, evaluation, indicators)
        
        return DetectedOpportunity(
            opportunity_code=rule.code,
            company_id=company_id,
            title=rule.name,
            description=rule.description_template,
            category=rule.category,
            potential_value=potential_value,
            feasibility=feasibility,
            timing_score=timing_score,
            strategic_fit=strategic_fit,
            final_score=final_score,
            priority_level=priority,
            triggering_indicators=triggering_indicators,
            detection_method="rule_based",
            reasoning=reasoning,
            window_start=now,
            window_end=now + timedelta(days=rule.window_days),
            window_duration_days=rule.window_days
        )
    
    def _generate_reasoning(
        self,
        rule: OpportunityRule,
        evaluation: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for the opportunity"""
        
        conditions_text = []
        for cond in evaluation['triggered_conditions']:
            if 'value' in cond:
                if cond['type'] == 'above':
                    conditions_text.append(
                        f"{cond['indicator']}: {cond['value']:.1f} (above {cond['threshold']} threshold)"
                    )
                elif cond['type'] == 'below':
                    conditions_text.append(
                        f"{cond['indicator']}: {cond['value']:.1f} (below {cond['threshold']} threshold)"
                    )
                elif cond['type'] == 'moderate':
                    conditions_text.append(
                        f"{cond['indicator']}: {cond['value']:.1f} (in optimal range {cond['range']})"
                    )
            elif 'trend' in cond:
                conditions_text.append(
                    f"{cond['indicator']}: trending {cond['trend']}"
                )
        
        return (
            f"Opportunity detected based on {evaluation['condition_count']} favorable conditions: "
            + "; ".join(conditions_text)
            + f". Overall confidence score: {evaluation['score']:.2f}"
        )
    
    def get_opportunity_categories(self) -> Dict[str, List[str]]:
        """Get all opportunity categories and their codes"""
        categories = {}
        for rule in self.rules:
            if rule.category not in categories:
                categories[rule.category] = []
            categories[rule.category].append(rule.code)
        return categories
    
    def get_rules_count(self) -> int:
        """Get total number of opportunity rules"""
        return len(self.rules)


# Export for easy importing
__all__ = ['RuleBasedOpportunityDetector', 'OpportunityRule']
