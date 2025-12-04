"""
Layer 4: Tier 1 - Rule-Based Risk Detection

Fast, deterministic risk detection using predefined rules
Confidence: 80%+ for rule-based detections
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import logging

from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.mock_data.layer3_mock_generator import OperationalIndicators

logger = logging.getLogger(__name__)


class RiskDefinitionRule:
    """Single risk definition with trigger logic"""

    def __init__(
        self,
        risk_id: str,
        risk_name: str,
        category: str,
        trigger_logic: Dict[str, Any],
        default_probability: float = 0.75,
        default_impact: float = 7.0,
        default_urgency: int = 3,
        applicable_industries: Optional[List[str]] = None,
        description_template: str = "",
    ):
        self.risk_id = risk_id
        self.risk_name = risk_name
        self.category = category
        self.trigger_logic = trigger_logic
        self.default_probability = default_probability
        self.default_impact = default_impact
        self.default_urgency = default_urgency
        self.applicable_industries = applicable_industries or []
        self.description_template = description_template


class RuleBasedRiskDetector:
    """
    Tier 1: Rule-Based Risk Detection

    Uses predefined rules with boolean logic to detect risks
    Fast, deterministic, high confidence (80%+)
    """

    def __init__(self):
        self.risk_rules = self._load_risk_rules()
        logger.info(f"Loaded {len(self.risk_rules)} risk detection rules")

    def _load_risk_rules(self) -> List[RiskDefinitionRule]:
        """Load 10+ risk definition rules"""

        rules = [
            # Risk 1: Supply Chain Disruption
            RiskDefinitionRule(
                risk_id="RISK_SUPPLY_CHAIN",
                risk_name="Supply Chain Disruption",
                category="operational",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_SUPPLY_CHAIN", "operator": "<", "threshold": 60},
                        {"indicator": "OPS_TRANSPORT_AVAIL", "operator": "<", "threshold": 50}
                    ],
                    "confidence_threshold": 0.80
                },
                default_probability=0.75,
                default_impact=8.0,
                default_urgency=4,
                applicable_industries=["retail", "manufacturing", "logistics"],
                description_template="Critical supply chain disruption detected. Supply chain integrity at {OPS_SUPPLY_CHAIN}% and transport availability at {OPS_TRANSPORT_AVAIL}%. Expect delivery delays and potential stockouts."
            ),

            # Risk 2: Revenue Decline Risk
            RiskDefinitionRule(
                risk_id="RISK_REVENUE_DECLINE",
                risk_name="Revenue Decline Risk",
                category="financial",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_DEMAND_LEVEL", "operator": "<", "threshold": 55},
                        {"indicator": "OPS_PRICING_POWER", "operator": "<", "threshold": 50}
                    ],
                    "confidence_threshold": 0.75
                },
                default_probability=0.70,
                default_impact=7.5,
                default_urgency=3,
                applicable_industries=["retail", "hospitality", "manufacturing"],
                description_template="Revenue decline risk identified. Demand level at {OPS_DEMAND_LEVEL}% with pricing power at {OPS_PRICING_POWER}%. Market conditions unfavorable for revenue growth."
            ),

            # Risk 3: Cost Escalation Risk
            RiskDefinitionRule(
                risk_id="RISK_COST_ESCALATION",
                risk_name="Cost Escalation Risk",
                category="financial",
                trigger_logic={
                    "type": "WEIGHTED",
                    "conditions": [
                        {"indicator": "OPS_COST_PRESSURE", "operator": "<", "threshold": 45, "weight": 0.4},
                        {"indicator": "OPS_RAW_MATERIAL_COST", "operator": "<", "threshold": 50, "weight": 0.3},
                        {"indicator": "OPS_ENERGY_COST", "operator": "<", "threshold": 50, "weight": 0.3}
                    ],
                    "confidence_threshold": 0.75,
                    "weighted_threshold": 0.65
                },
                default_probability=0.72,
                default_impact=7.0,
                default_urgency=3,
                applicable_industries=["manufacturing", "logistics", "retail"],
                description_template="Significant cost escalation risk. Overall cost pressure at {OPS_COST_PRESSURE}%, raw materials at {OPS_RAW_MATERIAL_COST}%, energy at {OPS_ENERGY_COST}%. Margin compression likely."
            ),

            # Risk 4: Workforce Disruption Risk
            RiskDefinitionRule(
                risk_id="RISK_WORKFORCE_DISRUPTION",
                risk_name="Workforce Disruption Risk",
                category="operational",
                trigger_logic={
                    "type": "OR",
                    "conditions": [
                        {"indicator": "OPS_WORKFORCE_AVAIL", "operator": "<", "threshold": 50},
                        {"indicator": "OPS_LABOR_COST", "operator": "<", "threshold": 40}
                    ],
                    "confidence_threshold": 0.80
                },
                default_probability=0.68,
                default_impact=6.5,
                default_urgency=4,
                applicable_industries=["manufacturing", "hospitality", "retail", "logistics"],
                description_template="Workforce disruption risk detected. Workforce availability at {OPS_WORKFORCE_AVAIL}% and labor cost pressure at {OPS_LABOR_COST}%. Operations may be impacted."
            ),

            # Risk 5: Power Outage Risk
            RiskDefinitionRule(
                risk_id="RISK_POWER_OUTAGE",
                risk_name="Power Infrastructure Risk",
                category="operational",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_POWER_RELIABILITY", "operator": "<", "threshold": 50},
                        {"indicator": "OPS_PRODUCTIVITY", "operator": "<", "threshold": 60}
                    ],
                    "confidence_threshold": 0.85
                },
                default_probability=0.78,
                default_impact=7.5,
                default_urgency=5,
                applicable_industries=["manufacturing", "hospitality", "retail", "technology"],
                description_template="Power infrastructure risk critical. Power reliability at {OPS_POWER_RELIABILITY}% causing productivity decline to {OPS_PRODUCTIVITY}%. Operations severely impacted."
            ),

            # Risk 6: Transport Disruption Risk
            RiskDefinitionRule(
                risk_id="RISK_TRANSPORT_DISRUPTION",
                risk_name="Transport Disruption Risk",
                category="operational",
                trigger_logic={
                    "type": "WEIGHTED",
                    "conditions": [
                        {"indicator": "OPS_TRANSPORT_AVAIL", "operator": "<", "threshold": 55, "weight": 0.5},
                        {"indicator": "OPS_FUEL_AVAIL", "operator": "<", "threshold": 50, "weight": 0.3},
                        {"indicator": "OPS_LOGISTICS_COST", "operator": "<", "threshold": 45, "weight": 0.2}
                    ],
                    "confidence_threshold": 0.80,
                    "weighted_threshold": 0.70
                },
                default_probability=0.75,
                default_impact=7.0,
                default_urgency=4,
                applicable_industries=["logistics", "retail", "manufacturing"],
                description_template="Transport disruption risk identified. Transport availability at {OPS_TRANSPORT_AVAIL}%, fuel availability at {OPS_FUEL_AVAIL}%. Delivery delays expected."
            ),

            # Risk 7: Currency Impact Risk
            RiskDefinitionRule(
                risk_id="RISK_CURRENCY_IMPACT",
                risk_name="Currency Impact Risk",
                category="financial",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_IMPORT_FLOW", "operator": "<", "threshold": 55},
                        {"indicator": "OPS_RAW_MATERIAL_COST", "operator": "<", "threshold": 45}
                    ],
                    "confidence_threshold": 0.75
                },
                default_probability=0.70,
                default_impact=6.5,
                default_urgency=3,
                applicable_industries=["manufacturing", "retail"],
                description_template="Currency impact risk detected. Import flow at {OPS_IMPORT_FLOW}% with raw material costs at {OPS_RAW_MATERIAL_COST}%. Currency volatility affecting costs."
            ),

            # Risk 8: Cash Flow Pressure Risk
            RiskDefinitionRule(
                risk_id="RISK_CASH_FLOW_PRESSURE",
                risk_name="Cash Flow Pressure Risk",
                category="financial",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_CASH_FLOW", "operator": "<", "threshold": 55},
                        {"indicator": "OPS_PAYMENT_DELAYS", "operator": "<", "threshold": 60}
                    ],
                    "confidence_threshold": 0.80
                },
                default_probability=0.72,
                default_impact=8.0,
                default_urgency=5,
                applicable_industries=["retail", "manufacturing", "hospitality", "logistics"],
                description_template="Cash flow pressure risk critical. Cash flow health at {OPS_CASH_FLOW}% with payment delays at {OPS_PAYMENT_DELAYS}%. Liquidity concerns rising."
            ),

            # Risk 9: Competitive Pressure Risk
            RiskDefinitionRule(
                risk_id="RISK_COMPETITIVE_PRESSURE",
                risk_name="Competitive Pressure Risk",
                category="competitive",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_COMPETITION_INTENSITY", "operator": ">", "threshold": 75},
                        {"indicator": "OPS_PRICING_POWER", "operator": "<", "threshold": 55}
                    ],
                    "confidence_threshold": 0.75
                },
                default_probability=0.68,
                default_impact=6.0,
                default_urgency=2,
                applicable_industries=["retail", "hospitality", "technology"],
                description_template="Competitive pressure risk. Competition intensity at {OPS_COMPETITION_INTENSITY}% while pricing power only {OPS_PRICING_POWER}%. Market share at risk."
            ),

            # Risk 10: Compliance Cost Risk
            RiskDefinitionRule(
                risk_id="RISK_COMPLIANCE_BURDEN",
                risk_name="Compliance Cost Burden",
                category="compliance",
                trigger_logic={
                    "type": "AND",
                    "conditions": [
                        {"indicator": "OPS_REGULATORY_BURDEN", "operator": "<", "threshold": 50},
                        {"indicator": "OPS_COMPLIANCE_COST", "operator": "<", "threshold": 55}
                    ],
                    "confidence_threshold": 0.75
                },
                default_probability=0.65,
                default_impact=5.5,
                default_urgency=2,
                applicable_industries=["manufacturing", "hospitality", "retail"],
                description_template="Compliance cost burden risk. Regulatory burden at {OPS_REGULATORY_BURDEN}% with compliance costs at {OPS_COMPLIANCE_COST}%. Additional costs expected."
            ),
        ]

        return rules

    def _evaluate_operator(self, value: float, operator: str, threshold: float) -> bool:
        """Evaluate a single condition operator"""
        operators = {
            "<": lambda v, t: v < t,
            ">": lambda v, t: v > t,
            "<=": lambda v, t: v <= t,
            ">=": lambda v, t: v >= t,
            "==": lambda v, t: v == t,
            "!=": lambda v, t: v != t,
        }

        if operator not in operators:
            logger.warning(f"Unknown operator: {operator}")
            return False

        return operators[operator](value, threshold)

    def _evaluate_conditions(
        self,
        trigger_logic: Dict[str, Any],
        indicators: OperationalIndicators
    ) -> tuple[bool, float, Dict[str, Any]]:
        """
        Evaluate trigger conditions

        Returns:
            (is_triggered, confidence, context)
        """
        logic_type = trigger_logic.get("type", "AND")
        conditions = trigger_logic.get("conditions", [])
        confidence_threshold = trigger_logic.get("confidence_threshold", 0.75)

        if not conditions:
            return False, 0.0, {}

        # Get indicator values as dict
        indicator_dict = indicators.dict()

        # Track which conditions passed
        passed_conditions = []
        failed_conditions = []
        contributing_indicators = {}

        for condition in conditions:
            indicator_name = condition.get("indicator")
            operator = condition.get("operator")
            threshold = condition.get("threshold")
            weight = condition.get("weight", 1.0)

            if indicator_name not in indicator_dict:
                logger.warning(f"Indicator {indicator_name} not found")
                failed_conditions.append(condition)
                continue

            indicator_value = indicator_dict[indicator_name]
            passed = self._evaluate_operator(indicator_value, operator, threshold)

            if passed:
                passed_conditions.append(condition)
                contributing_indicators[indicator_name] = {
                    "value": indicator_value,
                    "threshold": threshold,
                    "operator": operator,
                    "weight": weight
                }
            else:
                failed_conditions.append(condition)

        # Evaluate based on logic type
        if logic_type == "AND":
            triggered = len(passed_conditions) == len(conditions)
            confidence = 0.85 if triggered else 0.0

        elif logic_type == "OR":
            triggered = len(passed_conditions) > 0
            # Confidence based on percentage of conditions met
            confidence = 0.80 * (len(passed_conditions) / len(conditions)) if triggered else 0.0

        elif logic_type == "WEIGHTED":
            # Calculate weighted score
            total_weight = sum(c.get("weight", 1.0) for c in passed_conditions)
            max_weight = sum(c.get("weight", 1.0) for c in conditions)
            weighted_score = total_weight / max_weight if max_weight > 0 else 0.0

            weighted_threshold = trigger_logic.get("weighted_threshold", 0.65)
            triggered = weighted_score >= weighted_threshold
            confidence = 0.82 if triggered else 0.0

        else:
            logger.warning(f"Unknown logic type: {logic_type}")
            triggered = False
            confidence = 0.0

        # Only return triggered if confidence meets threshold
        if triggered and confidence < confidence_threshold:
            triggered = False

        context = {
            "logic_type": logic_type,
            "total_conditions": len(conditions),
            "passed_conditions": len(passed_conditions),
            "failed_conditions": len(failed_conditions),
            "contributing_indicators": contributing_indicators
        }

        return triggered, confidence, context

    def detect_risks(
        self,
        company_id: str,
        industry: str,
        indicators: OperationalIndicators,
        company_profile: Optional[Dict[str, Any]] = None
    ) -> List[DetectedRisk]:
        """
        Detect risks for a company based on operational indicators

        Args:
            company_id: Company identifier
            industry: Company industry
            indicators: Operational indicators from Layer 3
            company_profile: Optional company profile for context

        Returns:
            List of detected risks
        """
        detected_risks = []

        for rule in self.risk_rules:
            # Check industry applicability
            if rule.applicable_industries and industry not in rule.applicable_industries:
                continue

            # Evaluate trigger conditions
            is_triggered, confidence, context = self._evaluate_conditions(
                rule.trigger_logic,
                indicators
            )

            if not is_triggered:
                continue

            # Generate risk description
            description = self._generate_description(rule, indicators, context)

            # Calculate severity
            final_score = rule.default_probability * rule.default_impact * rule.default_urgency * confidence
            severity = self._classify_severity(final_score)

            # Create detected risk
            risk = DetectedRisk(
                risk_code=rule.risk_id,
                company_id=company_id,
                title=rule.risk_name,
                description=description,
                category=rule.category,
                probability=Decimal(str(rule.default_probability)),
                impact=Decimal(str(rule.default_impact)),
                urgency=rule.default_urgency,
                confidence=Decimal(str(confidence)),
                final_score=Decimal(str(round(final_score, 2))),
                severity_level=severity,
                triggering_indicators=context["contributing_indicators"],
                detection_method="rule_based",
                reasoning=self._generate_reasoning(rule, context),
                is_urgent=rule.default_urgency >= 4,
                requires_immediate_action=severity in ["critical", "high"] and rule.default_urgency >= 4
            )

            detected_risks.append(risk)
            logger.info(f"Detected risk: {rule.risk_id} for company {company_id} (confidence: {confidence:.2f})")

        return detected_risks

    def _generate_description(
        self,
        rule: RiskDefinitionRule,
        indicators: OperationalIndicators,
        context: Dict[str, Any]
    ) -> str:
        """Generate risk description from template"""
        template = rule.description_template
        indicator_dict = indicators.dict()

        # Replace placeholders with actual values
        for indicator_name, indicator_value in indicator_dict.items():
            placeholder = f"{{{indicator_name}}}"
            if placeholder in template:
                template = template.replace(placeholder, f"{indicator_value:.1f}")

        return template

    def _generate_reasoning(self, rule: RiskDefinitionRule, context: Dict[str, Any]) -> str:
        """Generate explanation of why risk was detected"""
        contributing = context["contributing_indicators"]
        logic_type = context["logic_type"]

        reasoning_parts = [
            f"Risk detected using {logic_type} logic with {context['passed_conditions']}/{context['total_conditions']} conditions met."
        ]

        reasoning_parts.append("Contributing factors:")
        for indicator, details in contributing.items():
            reasoning_parts.append(
                f"  - {indicator}: {details['value']:.1f} {details['operator']} {details['threshold']:.1f}"
            )

        return " ".join(reasoning_parts)

    def _classify_severity(self, score: float) -> str:
        """Classify risk severity based on score"""
        if score >= 40:
            return "critical"
        elif score >= 30:
            return "high"
        elif score >= 15:
            return "medium"
        else:
            return "low"
