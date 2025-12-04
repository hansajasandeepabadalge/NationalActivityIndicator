"""
Layer 4: Narrative Generator

Converts detected risks and opportunities into human-readable narratives
with context, emojis, and business impact explanations.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from decimal import Decimal

from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """
    Generates human-readable narratives for business insights

    Features:
    - Executive summaries
    - Contextual explanations
    - Business impact analysis
    - Urgency statements
    - Historical context
    """

    def generate_risk_narrative(
        self,
        risk: DetectedRisk,
        company_profile: Dict[str, Any],
        portfolio_context: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate comprehensive narrative for a risk

        Args:
            risk: Detected risk to narrativize
            company_profile: Company information for context
            portfolio_context: Optional portfolio metrics for context

        Returns:
            Dictionary with narrative components
        """
        return {
            "emoji": self._select_emoji(risk.severity_level),
            "headline": self._generate_headline(risk),
            "summary": self._generate_summary(risk, company_profile),
            "detailed_explanation": self._generate_explanation(risk, company_profile),
            "why_now": self._explain_timing(risk),
            "what_it_means": self._explain_business_impact(risk, company_profile),
            "historical_context": self._add_historical_context(risk),
            "urgency_statement": self._generate_urgency_statement(risk)
        }

    def generate_opportunity_narrative(
        self,
        opportunity: DetectedOpportunity,
        company_profile: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate comprehensive narrative for an opportunity

        Args:
            opportunity: Detected opportunity to narrativize
            company_profile: Company information for context

        Returns:
            Dictionary with narrative components
        """
        return {
            "emoji": self._select_opportunity_emoji(opportunity.priority),
            "headline": self._generate_opportunity_headline(opportunity),
            "summary": self._generate_opportunity_summary(opportunity, company_profile),
            "detailed_explanation": self._generate_opportunity_explanation(opportunity, company_profile),
            "why_now": self._explain_opportunity_timing(opportunity),
            "what_it_means": self._explain_opportunity_value(opportunity, company_profile),
            "urgency_statement": self._generate_opportunity_urgency(opportunity)
        }

    def _select_emoji(self, severity: str) -> str:
        """Select emoji for risk severity"""
        emoji_map = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "⚡",
            "low": "ℹ️"
        }
        return emoji_map.get(severity, "📊")

    def _select_opportunity_emoji(self, priority: str) -> str:
        """Select emoji for opportunity priority"""
        emoji_map = {
            "high": "🎯",
            "medium": "💡",
            "low": "🔍"
        }
        return emoji_map.get(priority, "✨")

    def _generate_headline(self, risk: DetectedRisk) -> str:
        """Create attention-grabbing headline"""
        severity_label = risk.severity_level.upper()
        return f"{severity_label} RISK: {risk.title}"

    def _generate_opportunity_headline(self, opportunity: DetectedOpportunity) -> str:
        """Create opportunity headline"""
        priority_label = opportunity.priority.upper()
        return f"{priority_label} PRIORITY OPPORTUNITY: {opportunity.title}"

    def _generate_summary(
        self,
        risk: DetectedRisk,
        company_profile: Dict
    ) -> str:
        """2-3 sentence executive summary"""
        company_name = company_profile.get('company_name', 'Your company')

        # Extract key indicator info
        triggering_info = ""
        if risk.triggering_indicators:
            if isinstance(risk.triggering_indicators, dict):
                indicator_count = len(risk.triggering_indicators)
                triggering_info = f"{indicator_count} key indicators have reached concerning levels."

        # Timeframe based on urgency
        timeframe_map = {
            5: "within 24-48 hours",
            4: "within this week",
            3: "within the next two weeks",
            2: "in the near term",
            1: "over the coming period"
        }
        timeframe = timeframe_map.get(risk.urgency, "in the foreseeable future")

        summary = (
            f"{company_name}'s {risk.category} operations show {risk.severity_level} signals. "
            f"{triggering_info} "
            f"{float(risk.probability):.0%} probability of impact {timeframe}."
        )

        return summary

    def _generate_opportunity_summary(
        self,
        opportunity: DetectedOpportunity,
        company_profile: Dict
    ) -> str:
        """2-3 sentence executive summary for opportunity"""
        company_name = company_profile.get('company_name', 'Your company')

        timeframe = f"{opportunity.window_days} days" if opportunity.window_days else "limited time"

        summary = (
            f"{company_name} has a {opportunity.priority} priority {opportunity.category} opportunity. "
            f"Potential value score: {opportunity.potential_value:.1f}/10, "
            f"feasibility: {opportunity.feasibility:.0%}. "
            f"Window of opportunity: {timeframe}."
        )

        return summary

    def _generate_explanation(
        self,
        risk: DetectedRisk,
        company_profile: Dict
    ) -> str:
        """Detailed explanation with indicators"""
        explanation_parts = []

        # Current situation
        explanation_parts.append(f"**Current Situation:**\n{risk.description}")

        # Triggering indicators
        if risk.triggering_indicators and isinstance(risk.triggering_indicators, dict):
            explanation_parts.append("\n**Key Indicators:**")
            for indicator, details in risk.triggering_indicators.items():
                if isinstance(details, dict) and 'value' in details:
                    value = details.get('value', 'N/A')
                    threshold = details.get('threshold', 'N/A')
                    explanation_parts.append(
                        f"- {indicator}: {value}/100 (threshold: {threshold})"
                    )

        # Detection method
        method_names = {
            'rule_based': 'Rule-Based Detection',
            'pattern': 'Historical Pattern Matching',
            'ml': 'Machine Learning Prediction',
            'combined': 'Multiple Detection Methods'
        }
        method_name = method_names.get(risk.detection_method, risk.detection_method.replace('_', ' ').title())
        explanation_parts.append(f"\n**Detection Method:** {method_name}")

        # Company context
        scale = company_profile.get('business_scale', 'N/A')
        industry = company_profile.get('industry', 'N/A')
        explanation_parts.append(f"\n**Company Context:** {scale.title()} {industry} business")

        return "\n".join(explanation_parts)

    def _generate_opportunity_explanation(
        self,
        opportunity: DetectedOpportunity,
        company_profile: Dict
    ) -> str:
        """Detailed explanation for opportunity"""
        explanation_parts = []

        # Opportunity description
        explanation_parts.append(f"**Opportunity Description:**\n{opportunity.description}")

        # Triggering factors
        if opportunity.triggering_factors and isinstance(opportunity.triggering_factors, dict):
            explanation_parts.append("\n**Triggering Factors:**")
            for factor, value in opportunity.triggering_factors.items():
                explanation_parts.append(f"- {factor}: {value}")

        # Company context
        scale = company_profile.get('business_scale', 'N/A')
        industry = company_profile.get('industry', 'N/A')
        explanation_parts.append(f"\n**Company Context:** {scale.title()} {industry} business")

        # Strategic fit
        explanation_parts.append(f"\n**Strategic Fit:** {opportunity.strategic_fit:.0%}")

        return "\n".join(explanation_parts)

    def _explain_timing(self, risk: DetectedRisk) -> str:
        """Explain why action is needed now"""
        urgency_map = {
            5: "IMMEDIATE ACTION REQUIRED - Impact expected within 24-48 hours",
            4: "URGENT - Address within this week to prevent escalation",
            3: "TIMELY - Action needed within 2 weeks to avoid deterioration",
            2: "MONITOR - Review situation and prepare response plan",
            1: "AWARENESS - Keep on radar for potential future impact"
        }
        return urgency_map.get(risk.urgency, "Monitor situation closely")

    def _explain_opportunity_timing(self, opportunity: DetectedOpportunity) -> str:
        """Explain opportunity window"""
        if opportunity.window_days:
            if opportunity.window_days <= 7:
                return f"ACT QUICKLY - Window closes in {opportunity.window_days} days"
            elif opportunity.window_days <= 30:
                return f"TIMELY ACTION NEEDED - {opportunity.window_days} day window"
            else:
                return f"PLAN AND EXECUTE - {opportunity.window_days} day window available"
        else:
            return "ASSESS TIMING - Evaluate window of opportunity"

    def _explain_business_impact(
        self,
        risk: DetectedRisk,
        company_profile: Dict
    ) -> str:
        """Explain business consequences"""
        impact_score = float(risk.impact)
        revenue = company_profile.get('annual_revenue', 0)
        currency = company_profile.get('revenue_currency', 'LKR')

        # Estimate financial impact
        impact_text_parts = [
            "**Potential Business Impact:**",
            f"- Severity: {risk.severity_level.upper()} ({risk.impact}/10)",
            f"- Probability: {float(risk.probability):.0%}",
            f"- Confidence: {float(risk.confidence):.0%}"
        ]

        if revenue > 0:
            # Estimate percentage impact based on severity
            estimated_impact_pct = (impact_score / 10) * 0.20  # Max 20% revenue impact
            estimated_amount = float(revenue) * estimated_impact_pct

            impact_text_parts.insert(
                2,
                f"- Estimated revenue impact: {estimated_impact_pct:.1%} (~{estimated_amount:,.0f} {currency})"
            )

        return "\n".join(impact_text_parts)

    def _explain_opportunity_value(
        self,
        opportunity: DetectedOpportunity,
        company_profile: Dict
    ) -> str:
        """Explain opportunity business value"""
        revenue = company_profile.get('annual_revenue', 0)
        currency = company_profile.get('revenue_currency', 'LKR')

        value_parts = [
            "**Potential Business Value:**",
            f"- Value Score: {opportunity.potential_value}/10",
            f"- Feasibility: {opportunity.feasibility:.0%}",
            f"- Strategic Fit: {opportunity.strategic_fit:.0%}"
        ]

        if revenue > 0 and opportunity.estimated_roi:
            estimated_gain = float(revenue) * float(opportunity.estimated_roi)
            value_parts.insert(
                2,
                f"- Estimated value: {opportunity.estimated_roi:.1%} ROI (~{estimated_gain:,.0f} {currency})"
            )

        return "\n".join(value_parts)

    def _add_historical_context(self, risk: DetectedRisk) -> str:
        """Add context from similar past events"""
        if risk.detection_method == "pattern":
            # Extract historical context from triggering_indicators
            if isinstance(risk.triggering_indicators, dict):
                if "lessons_learned" in risk.triggering_indicators:
                    return (
                        f"**Historical Precedent:**\n"
                        f"{risk.triggering_indicators['lessons_learned']}"
                    )
                if "historical_date" in risk.triggering_indicators:
                    return (
                        f"**Similar Historical Event:**\n"
                        f"Pattern matches event from {risk.triggering_indicators['historical_date']}"
                    )

        return ""

    def _generate_urgency_statement(self, risk: DetectedRisk) -> str:
        """Clear call-to-action based on urgency"""
        if risk.requires_immediate_action:
            return "⏰ **IMMEDIATE ACTION REQUIRED** - Review recommendations and implement response plan today."
        elif risk.urgency >= 3:
            return "📅 **ACTION NEEDED SOON** - Schedule response planning within the next few days."
        else:
            return "👁️ **MONITORING RECOMMENDED** - Track indicators and prepare contingency plans."

    def _generate_opportunity_urgency(self, opportunity: DetectedOpportunity) -> str:
        """Call-to-action for opportunity"""
        if opportunity.priority == "high" and opportunity.timing_score >= 4:
            return "🎯 **ACT NOW** - High-value opportunity with limited window. Begin implementation immediately."
        elif opportunity.timing_score >= 3:
            return "💡 **PLAN AND EXECUTE** - Develop implementation plan and allocate resources soon."
        else:
            return "🔍 **EVALUATE** - Assess feasibility and strategic alignment before committing resources."
