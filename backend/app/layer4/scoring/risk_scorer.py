"""
Layer 4: Risk Scoring Engine

Comprehensive risk scoring: Risk_Score = Probability × Impact × Urgency × Confidence

Score Range: 0-50
- Critical: 40-50
- High: 30-39
- Medium: 15-29
- Low: 0-14
"""
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
import logging

from app.layer4.schemas.risk_schemas import DetectedRisk, RiskScoreBreakdown
from app.layer4.mock_data.layer3_mock_generator import OperationalIndicators

logger = logging.getLogger(__name__)


class RiskScorer:
    """
    Comprehensive Risk Scoring Engine

    Components:
    - Probability (0-1): How likely the risk will materialize
    - Impact (0-10): Severity if it occurs
    - Urgency (1-5): Time sensitivity
    - Confidence (0-1): How certain we are
    """

    def calculate_risk_score(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators,
        company_profile: Optional[Dict[str, Any]] = None
    ) -> RiskScoreBreakdown:
        """
        Calculate comprehensive risk score with breakdown

        Args:
            risk: Detected risk to score
            indicators: Current operational indicators
            company_profile: Optional company profile for context

        Returns:
            Risk score breakdown with reasoning
        """
        # Calculate each component
        probability = self._calculate_probability(risk, indicators)
        impact = self._calculate_impact(risk, company_profile)
        urgency = self._calculate_urgency(risk, indicators)
        confidence = self._calculate_confidence(risk)

        # Calculate final score
        final_score = float(probability) * float(impact) * float(urgency) * float(confidence)

        # Classify severity
        severity = self._classify_severity(final_score)

        # Generate reasoning for each component
        prob_reasoning = self._explain_probability(risk, indicators)
        impact_reasoning = self._explain_impact(risk, company_profile)
        urgency_reasoning = self._explain_urgency(risk, indicators)
        confidence_source = self._explain_confidence(risk)

        breakdown = RiskScoreBreakdown(
            probability=Decimal(str(round(probability, 2))),
            probability_reasoning=prob_reasoning,
            impact=Decimal(str(round(impact, 2))),
            impact_reasoning=impact_reasoning,
            urgency=int(urgency),
            urgency_reasoning=urgency_reasoning,
            confidence=Decimal(str(round(confidence, 2))),
            confidence_source=confidence_source,
            final_score=Decimal(str(round(final_score, 2))),
            severity=severity
        )

        logger.debug(
            f"Risk {risk.risk_code} scored: P={probability:.2f}, I={impact:.2f}, "
            f"U={urgency}, C={confidence:.2f}, Final={final_score:.2f} ({severity})"
        )

        return breakdown

    def _calculate_probability(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators
    ) -> float:
        """
        Calculate probability that risk will materialize (0-1)

        Factors:
        - Base probability from risk definition
        - Current indicator severity
        - Trend direction
        """
        # Start with base probability from detection
        base_probability = float(risk.probability)

        # Adjust based on indicator severity
        triggering = risk.triggering_indicators
        if isinstance(triggering, dict):
            # Count how severely indicators are breached
            severe_breaches = 0
            moderate_breaches = 0
            total_indicators = len(triggering)

            for indicator_name, details in triggering.items():
                if isinstance(details, dict):
                    value = details.get('value', 0)
                    threshold = details.get('threshold', 50)
                    operator = details.get('operator', '<')

                    # Calculate breach severity
                    if operator == '<':
                        if value < threshold * 0.8:  # Severe: 20%+ below threshold
                            severe_breaches += 1
                        elif value < threshold:  # Moderate
                            moderate_breaches += 1
                    elif operator == '>':
                        if value > threshold * 1.2:  # Severe: 20%+ above threshold
                            severe_breaches += 1
                        elif value > threshold:  # Moderate
                            moderate_breaches += 1

            # Adjust probability
            if total_indicators > 0:
                severity_adjustment = (severe_breaches * 0.10 + moderate_breaches * 0.05)
                base_probability += severity_adjustment

        # Check for negative trends
        indicator_dict = indicators.dict()
        trends = indicator_dict.get('trends', {})
        if isinstance(trends, dict):
            falling_trends = sum(1 for trend in trends.values() if trend == 'falling')
            if falling_trends > 3:  # Multiple falling indicators
                base_probability += 0.05

        # Cap at 1.0
        return min(1.0, base_probability)

    def _calculate_impact(
        self,
        risk: DetectedRisk,
        company_profile: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate severity if risk occurs (0-10)

        Factors:
        - Risk category base impact
        - Company size (smaller = more vulnerable)
        - Company dependencies
        - Cash reserves
        """
        # Category base impacts
        category_impacts = {
            'operational': 7.0,
            'financial': 8.0,
            'competitive': 6.0,
            'reputational': 6.5,
            'compliance': 5.5,
            'strategic': 7.5
        }

        base_impact = category_impacts.get(risk.category, float(risk.impact))

        if not company_profile:
            return base_impact

        # Adjust for company size
        business_scale = company_profile.get('business_scale', 'medium')
        scale_multipliers = {
            'small': 1.3,      # Small companies more vulnerable
            'medium': 1.0,
            'large': 0.9,      # Large companies more resilient
            'enterprise': 0.8
        }
        base_impact *= scale_multipliers.get(business_scale, 1.0)

        # Adjust for financial strength
        cash_reserves = company_profile.get('cash_reserves')
        debt_level = company_profile.get('debt_level', 'moderate')

        if debt_level == 'high':
            base_impact *= 1.15
        elif debt_level == 'low' and cash_reserves:
            base_impact *= 0.90

        # Category-specific adjustments
        if risk.category == 'operational':
            # Check operational dependencies
            dependencies = company_profile.get('operational_dependencies', {})
            if isinstance(dependencies, dict):
                critical_deps = sum(
                    1 for dep in dependencies.values()
                    if dep == 'critical'
                )
                if critical_deps >= 2:
                    base_impact *= 1.10

        elif risk.category == 'financial':
            # Cash flow risks more severe for cash-constrained companies
            if company_profile.get('debt_level') == 'high':
                base_impact *= 1.20

        # Cap at 10.0
        return min(10.0, base_impact)

    def _calculate_urgency(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators
    ) -> int:
        """
        Calculate time sensitivity (1-5)

        Factors:
        - Base urgency from risk
        - Rate of indicator deterioration
        - Expected impact time
        """
        # Start with base urgency
        base_urgency = risk.urgency

        # Check if indicators are rapidly deteriorating
        indicator_dict = indicators.dict()
        trends = indicator_dict.get('trends', {})

        if isinstance(trends, dict):
            rapid_decline = sum(
                1 for indicator_name, trend in trends.items()
                if trend == 'falling' and
                risk.triggering_indicators and
                indicator_name in risk.triggering_indicators
            )

            if rapid_decline >= 2:
                base_urgency = min(5, base_urgency + 1)

        # Check expected impact time
        if risk.expected_impact_time:
            # If impact expected soon, increase urgency
            # (In production, would calculate time delta)
            pass

        return max(1, min(5, base_urgency))

    def _calculate_confidence(self, risk: DetectedRisk) -> float:
        """
        Calculate confidence in detection (0-1)

        Factors:
        - Detection method
        - Number of confirming indicators
        - Data quality
        """
        # Base confidence from detection
        base_confidence = float(risk.confidence)

        # Detection method confidence
        method_confidence = {
            'rule_based': 0.85,     # High confidence in rules
            'pattern': 0.80,         # Good confidence in patterns
            'ml': 0.75,              # ML can have false positives
            'combined': 0.90         # Multiple methods agreeing
        }

        method = risk.detection_method
        if method in method_confidence:
            base_confidence = max(base_confidence, method_confidence[method])

        # Adjust based on number of indicators
        if risk.triggering_indicators:
            num_indicators = len(risk.triggering_indicators)
            if num_indicators >= 3:
                base_confidence += 0.05
            elif num_indicators == 1:
                base_confidence -= 0.05

        # Cap at 1.0
        return min(1.0, max(0.0, base_confidence))

    def _classify_severity(self, score: float) -> str:
        """Classify risk severity based on final score"""
        if score >= 40:
            return "critical"
        elif score >= 30:
            return "high"
        elif score >= 15:
            return "medium"
        else:
            return "low"

    def _explain_probability(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators
    ) -> str:
        """Generate explanation for probability score"""
        base_prob = float(risk.probability)

        explanation = f"Base probability {base_prob:.0%} from {risk.detection_method} detection. "

        # Check indicator severity
        if risk.triggering_indicators:
            num_indicators = len(risk.triggering_indicators)
            explanation += f"{num_indicators} indicators triggered. "

        # Check trends
        indicator_dict = indicators.dict()
        trends = indicator_dict.get('trends', {})
        if isinstance(trends, dict):
            falling = sum(1 for t in trends.values() if t == 'falling')
            if falling > 3:
                explanation += f"{falling} indicators show negative trends. "

        return explanation

    def _explain_impact(
        self,
        risk: DetectedRisk,
        company_profile: Optional[Dict[str, Any]]
    ) -> str:
        """Generate explanation for impact score"""
        explanation = f"{risk.category.capitalize()} risk with base impact {float(risk.impact):.1f}. "

        if company_profile:
            scale = company_profile.get('business_scale', 'medium')
            explanation += f"Company size ({scale}) "

            if scale == 'small':
                explanation += "increases vulnerability. "
            elif scale in ['large', 'enterprise']:
                explanation += "provides resilience. "

            debt = company_profile.get('debt_level')
            if debt == 'high':
                explanation += "High debt amplifies impact. "
            elif debt == 'low':
                explanation += "Strong financial position reduces impact. "

        return explanation

    def _explain_urgency(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators
    ) -> str:
        """Generate explanation for urgency score"""
        urgency = risk.urgency

        if urgency >= 4:
            explanation = "High urgency - immediate action required. "
        elif urgency == 3:
            explanation = "Moderate urgency - action needed within days. "
        else:
            explanation = "Lower urgency - monitoring and planning phase. "

        # Check trends
        indicator_dict = indicators.dict()
        trends = indicator_dict.get('trends', {})
        if isinstance(trends, dict):
            falling = sum(1 for t in trends.values() if t == 'falling')
            if falling >= 2:
                explanation += "Rapid deterioration increases urgency. "

        return explanation

    def _explain_confidence(self, risk: DetectedRisk) -> str:
        """Generate explanation for confidence score"""
        method = risk.detection_method
        confidence = float(risk.confidence)

        method_names = {
            'rule_based': 'rule-based detection',
            'pattern': 'historical pattern matching',
            'ml': 'machine learning prediction',
            'combined': 'multiple detection methods'
        }

        method_name = method_names.get(method, method)

        explanation = f"{confidence:.0%} confidence from {method_name}. "

        if risk.triggering_indicators:
            num_indicators = len(risk.triggering_indicators)
            explanation += f"Supported by {num_indicators} indicator(s). "

        return explanation

    def update_risk_score(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators,
        company_profile: Optional[Dict[str, Any]] = None
    ) -> DetectedRisk:
        """
        Recalculate and update risk score

        Args:
            risk: Existing risk to rescore
            indicators: Updated indicators
            company_profile: Optional company profile

        Returns:
            Risk with updated scores
        """
        breakdown = self.calculate_risk_score(risk, indicators, company_profile)

        # Update risk fields
        risk.probability = breakdown.probability
        risk.impact = breakdown.impact
        risk.urgency = breakdown.urgency
        risk.confidence = breakdown.confidence
        risk.final_score = breakdown.final_score
        risk.severity_level = breakdown.severity

        # Update urgency flags
        risk.is_urgent = breakdown.urgency >= 4
        risk.requires_immediate_action = (
            breakdown.severity in ["critical", "high"] and
            breakdown.urgency >= 4
        )

        return risk
