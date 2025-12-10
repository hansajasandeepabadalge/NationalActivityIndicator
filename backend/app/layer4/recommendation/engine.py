"""
Layer 4: Recommendation Engine

Generates actionable recommendations based on detected risks and opportunities.
Provides templates for common business situations and prioritization logic.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal

from app.layer4.schemas.recommendation_schemas import (
    Recommendation,
    RecommendationCreate,
    ActionPlan,
    ActionPlanStep,
    RecommendationTemplate,
    NarrativeContent
)
from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity

logger = logging.getLogger(__name__)


class RecommendationTemplate:
    """Template for generating recommendations"""
    
    def __init__(
        self,
        code: str,
        name: str,
        applicable_to: List[str],
        immediate_actions: List[Dict[str, Any]],
        short_term_actions: List[Dict[str, Any]],
        medium_term_actions: Optional[List[Dict[str, Any]]] = None,
        default_effort: str = "Medium",
        success_metrics: Optional[List[str]] = None
    ):
        self.code = code
        self.name = name
        self.applicable_to = applicable_to
        self.immediate_actions = immediate_actions
        self.short_term_actions = short_term_actions
        self.medium_term_actions = medium_term_actions or []
        self.default_effort = default_effort
        self.success_metrics = success_metrics or []


class RecommendationEngine:
    """
    Generates recommendations for detected risks and opportunities.
    
    Features:
    - Template-based recommendation generation
    - Prioritization based on severity and business impact
    - Action plan creation with steps and dependencies
    - Narrative content generation for executive communication
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        logger.info(f"Initialized RecommendationEngine with {len(self.templates)} templates")
    
    def _initialize_templates(self) -> Dict[str, RecommendationTemplate]:
        """Initialize recommendation templates"""
        
        templates = {}
        
        # ==================================================================
        # RISK MITIGATION TEMPLATES
        # ==================================================================
        
        # Supply Chain Risk Template
        templates["RISK_SUPPLY_CHAIN"] = RecommendationTemplate(
            code="RISK_SUPPLY_CHAIN",
            name="Supply Chain Risk Mitigation",
            applicable_to=["RISK_SUPPLY_CHAIN", "RISK_IMPORT"],
            immediate_actions=[
                {
                    "action": "Contact primary suppliers to assess delivery status",
                    "responsible": "Procurement Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Review current inventory levels and identify critical items",
                    "responsible": "Inventory Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Activate backup supplier list for critical materials",
                    "responsible": "Procurement Manager",
                    "timeframe": "24 hours",
                    "effort": "Medium"
                }
            ],
            short_term_actions=[
                {
                    "action": "Negotiate expedited shipping for critical items",
                    "responsible": "Procurement Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Review and adjust production schedule based on available materials",
                    "responsible": "Operations Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Communicate potential delays to key customers",
                    "responsible": "Sales Manager",
                    "timeframe": "48 hours",
                    "effort": "Low"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Diversify supplier base to reduce single-point dependencies",
                    "responsible": "Procurement Director",
                    "timeframe": "This month",
                    "effort": "High"
                },
                {
                    "action": "Increase safety stock levels for critical items",
                    "responsible": "Inventory Manager",
                    "timeframe": "This month",
                    "effort": "Medium"
                }
            ],
            success_metrics=["Delivery delays < 5%", "No production stoppages", "Customer satisfaction maintained"]
        )
        
        # Revenue Decline Risk Template
        templates["RISK_REVENUE_DECLINE"] = RecommendationTemplate(
            code="RISK_REVENUE_DECLINE",
            name="Revenue Decline Response",
            applicable_to=["RISK_REVENUE_DECLINE", "RISK_DEMAND"],
            immediate_actions=[
                {
                    "action": "Analyze sales data to identify declining segments",
                    "responsible": "Sales Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Review pricing competitiveness versus market",
                    "responsible": "Marketing Manager",
                    "timeframe": "24 hours",
                    "effort": "Medium"
                }
            ],
            short_term_actions=[
                {
                    "action": "Launch targeted promotional campaign for underperforming products",
                    "responsible": "Marketing Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Re-engage dormant customers with special offers",
                    "responsible": "Sales Team",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Review and optimize sales team territories",
                    "responsible": "Sales Director",
                    "timeframe": "2 weeks",
                    "effort": "Medium"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Conduct customer satisfaction survey",
                    "responsible": "Marketing Manager",
                    "timeframe": "This month",
                    "effort": "Medium"
                },
                {
                    "action": "Explore new market segments or distribution channels",
                    "responsible": "Business Development",
                    "timeframe": "This quarter",
                    "effort": "High"
                }
            ],
            success_metrics=["Revenue decline halted", "Customer retention > 90%", "Market share maintained"]
        )
        
        # Cost Escalation Risk Template
        templates["RISK_COST_ESCALATION"] = RecommendationTemplate(
            code="RISK_COST_ESCALATION",
            name="Cost Control Measures",
            applicable_to=["RISK_COST_ESCALATION", "RISK_COST"],
            immediate_actions=[
                {
                    "action": "Review all discretionary spending and defer non-essential purchases",
                    "responsible": "Finance Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Identify top 5 cost drivers and assess reduction options",
                    "responsible": "Operations Manager",
                    "timeframe": "Today",
                    "effort": "Medium"
                }
            ],
            short_term_actions=[
                {
                    "action": "Renegotiate contracts with major suppliers",
                    "responsible": "Procurement Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Implement energy-saving measures",
                    "responsible": "Facilities Manager",
                    "timeframe": "This week",
                    "effort": "Low"
                },
                {
                    "action": "Review and optimize overtime usage",
                    "responsible": "HR Manager",
                    "timeframe": "This week",
                    "effort": "Low"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Conduct comprehensive cost audit",
                    "responsible": "Finance Director",
                    "timeframe": "This month",
                    "effort": "High"
                },
                {
                    "action": "Evaluate process automation opportunities",
                    "responsible": "Operations Director",
                    "timeframe": "This quarter",
                    "effort": "High"
                }
            ],
            success_metrics=["Cost reduction of 10%", "Margin improvement", "No quality impact"]
        )
        
        # Workforce Risk Template
        templates["RISK_WORKFORCE"] = RecommendationTemplate(
            code="RISK_WORKFORCE",
            name="Workforce Risk Mitigation",
            applicable_to=["RISK_WORKFORCE", "RISK_LABOR"],
            immediate_actions=[
                {
                    "action": "Identify critical roles and single points of failure",
                    "responsible": "HR Manager",
                    "timeframe": "Today",
                    "effort": "Medium"
                },
                {
                    "action": "Review and accelerate pending hiring processes",
                    "responsible": "HR Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                }
            ],
            short_term_actions=[
                {
                    "action": "Develop cross-training program for critical functions",
                    "responsible": "Operations Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Review compensation competitiveness for key roles",
                    "responsible": "HR Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Engage temporary staffing agency for backup",
                    "responsible": "HR Manager",
                    "timeframe": "48 hours",
                    "effort": "Low"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Implement employee retention program",
                    "responsible": "HR Director",
                    "timeframe": "This month",
                    "effort": "High"
                },
                {
                    "action": "Build talent pipeline through internship programs",
                    "responsible": "HR Director",
                    "timeframe": "This quarter",
                    "effort": "Medium"
                }
            ],
            success_metrics=["Staff turnover < 10%", "Critical roles covered", "Productivity maintained"]
        )
        
        # Power/Infrastructure Risk Template
        templates["RISK_POWER"] = RecommendationTemplate(
            code="RISK_POWER",
            name="Infrastructure Continuity Plan",
            applicable_to=["RISK_POWER", "RISK_INFRASTRUCTURE"],
            immediate_actions=[
                {
                    "action": "Verify backup power systems are operational",
                    "responsible": "Facilities Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Identify critical systems and priority order for power allocation",
                    "responsible": "IT Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                }
            ],
            short_term_actions=[
                {
                    "action": "Procure additional fuel for backup generators",
                    "responsible": "Facilities Manager",
                    "timeframe": "24 hours",
                    "effort": "Low"
                },
                {
                    "action": "Establish load-shedding schedule if needed",
                    "responsible": "Operations Manager",
                    "timeframe": "Today",
                    "effort": "Medium"
                },
                {
                    "action": "Enable remote work capabilities for non-essential staff",
                    "responsible": "IT Manager",
                    "timeframe": "48 hours",
                    "effort": "Medium"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Evaluate solar/alternative power options",
                    "responsible": "Facilities Director",
                    "timeframe": "This month",
                    "effort": "High"
                },
                {
                    "action": "Upgrade UPS systems for critical equipment",
                    "responsible": "IT Director",
                    "timeframe": "This quarter",
                    "effort": "High"
                }
            ],
            success_metrics=["Zero data loss", "Critical ops maintained", "< 2 hours unplanned downtime"]
        )
        
        # ==================================================================
        # OPPORTUNITY CAPTURE TEMPLATES
        # ==================================================================
        
        # Market Capture Opportunity Template
        templates["OPP_MARKET_CAPTURE"] = RecommendationTemplate(
            code="OPP_MARKET_CAPTURE",
            name="Market Share Capture Strategy",
            applicable_to=["OPP_MARKET_CAPTURE", "OPP_COMPETITIVE"],
            immediate_actions=[
                {
                    "action": "Identify competitor vulnerabilities and affected customers",
                    "responsible": "Sales Manager",
                    "timeframe": "Today",
                    "effort": "Medium"
                },
                {
                    "action": "Prepare competitive differentiation messaging",
                    "responsible": "Marketing Manager",
                    "timeframe": "24 hours",
                    "effort": "Medium"
                }
            ],
            short_term_actions=[
                {
                    "action": "Launch targeted outreach to competitor's customers",
                    "responsible": "Sales Team",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Offer special switching incentives",
                    "responsible": "Sales Director",
                    "timeframe": "This week",
                    "effort": "Low"
                },
                {
                    "action": "Increase advertising in competitor's stronghold markets",
                    "responsible": "Marketing Manager",
                    "timeframe": "2 weeks",
                    "effort": "High"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Develop case studies from new customer wins",
                    "responsible": "Marketing Manager",
                    "timeframe": "This month",
                    "effort": "Medium"
                }
            ],
            success_metrics=["Market share +2%", "10+ new customer wins", "Revenue increase 15%"]
        )
        
        # Pricing Power Opportunity Template
        templates["OPP_PRICING_POWER"] = RecommendationTemplate(
            code="OPP_PRICING_POWER",
            name="Premium Pricing Strategy",
            applicable_to=["OPP_PRICING_POWER", "OPP_PRICING"],
            immediate_actions=[
                {
                    "action": "Analyze price elasticity for key products",
                    "responsible": "Finance Manager",
                    "timeframe": "Today",
                    "effort": "Medium"
                },
                {
                    "action": "Identify products with highest pricing potential",
                    "responsible": "Product Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                }
            ],
            short_term_actions=[
                {
                    "action": "Implement selective price increases on high-demand items",
                    "responsible": "Sales Director",
                    "timeframe": "This week",
                    "effort": "Low"
                },
                {
                    "action": "Enhance value proposition messaging to justify premium",
                    "responsible": "Marketing Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Train sales team on value-based selling",
                    "responsible": "Sales Director",
                    "timeframe": "2 weeks",
                    "effort": "Medium"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Launch premium product tier",
                    "responsible": "Product Manager",
                    "timeframe": "This quarter",
                    "effort": "High"
                }
            ],
            success_metrics=["Margin improvement 5%", "Price increase without volume loss", "Premium segment growth"]
        )
        
        # Demand Surge Opportunity Template
        templates["OPP_DEMAND_SURGE"] = RecommendationTemplate(
            code="OPP_DEMAND_SURGE",
            name="Demand Surge Capture",
            applicable_to=["OPP_DEMAND_SURGE", "OPP_DEMAND"],
            immediate_actions=[
                {
                    "action": "Assess current capacity and inventory levels",
                    "responsible": "Operations Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Identify potential capacity expansion options",
                    "responsible": "Operations Manager",
                    "timeframe": "Today",
                    "effort": "Medium"
                }
            ],
            short_term_actions=[
                {
                    "action": "Authorize overtime and additional shifts",
                    "responsible": "Operations Director",
                    "timeframe": "24 hours",
                    "effort": "Low"
                },
                {
                    "action": "Accelerate raw material procurement",
                    "responsible": "Procurement Manager",
                    "timeframe": "48 hours",
                    "effort": "Medium"
                },
                {
                    "action": "Engage contract manufacturing if needed",
                    "responsible": "Operations Director",
                    "timeframe": "This week",
                    "effort": "High"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Evaluate permanent capacity expansion",
                    "responsible": "Operations Director",
                    "timeframe": "This month",
                    "effort": "High"
                }
            ],
            success_metrics=["Demand fulfilled 95%+", "No stockouts", "Revenue capture maximized"]
        )
        
        # Digital Transformation Opportunity Template
        templates["OPP_DIGITAL_TRANSFORM"] = RecommendationTemplate(
            code="OPP_DIGITAL_TRANSFORM",
            name="Digital Transformation Initiative",
            applicable_to=["OPP_DIGITAL_TRANSFORM", "OPP_TECHNOLOGY"],
            immediate_actions=[
                {
                    "action": "Identify quick-win automation opportunities",
                    "responsible": "IT Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Assess current technology gaps",
                    "responsible": "IT Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                }
            ],
            short_term_actions=[
                {
                    "action": "Implement cloud-based productivity tools",
                    "responsible": "IT Manager",
                    "timeframe": "2 weeks",
                    "effort": "Medium"
                },
                {
                    "action": "Launch pilot automation project",
                    "responsible": "Operations Manager",
                    "timeframe": "This month",
                    "effort": "High"
                },
                {
                    "action": "Train staff on new digital tools",
                    "responsible": "HR Manager",
                    "timeframe": "This month",
                    "effort": "Medium"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Develop comprehensive digital roadmap",
                    "responsible": "IT Director",
                    "timeframe": "This quarter",
                    "effort": "High"
                },
                {
                    "action": "Implement ERP/CRM upgrade",
                    "responsible": "IT Director",
                    "timeframe": "This year",
                    "effort": "High"
                }
            ],
            success_metrics=["Productivity +20%", "Process automation 50%", "Digital skills improvement"]
        )
        
        # Talent Acquisition Opportunity Template
        templates["OPP_TALENT_ACQUISITION"] = RecommendationTemplate(
            code="OPP_TALENT_ACQUISITION",
            name="Strategic Talent Acquisition",
            applicable_to=["OPP_TALENT_ACQUISITION", "OPP_TALENT"],
            immediate_actions=[
                {
                    "action": "Identify critical skill gaps and priorities",
                    "responsible": "HR Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                },
                {
                    "action": "Review pending recruitment and fast-track key positions",
                    "responsible": "HR Manager",
                    "timeframe": "Today",
                    "effort": "Low"
                }
            ],
            short_term_actions=[
                {
                    "action": "Launch targeted recruitment campaign",
                    "responsible": "HR Manager",
                    "timeframe": "This week",
                    "effort": "Medium"
                },
                {
                    "action": "Attend industry job fairs and networking events",
                    "responsible": "HR Team",
                    "timeframe": "This month",
                    "effort": "Medium"
                },
                {
                    "action": "Offer competitive signing bonuses for key hires",
                    "responsible": "HR Director",
                    "timeframe": "This week",
                    "effort": "Low"
                }
            ],
            medium_term_actions=[
                {
                    "action": "Build employer brand and employee value proposition",
                    "responsible": "HR Director",
                    "timeframe": "This quarter",
                    "effort": "High"
                }
            ],
            success_metrics=["Key positions filled", "Time to hire < 30 days", "Quality of hire high"]
        )
        
        return templates
    
    def generate_recommendations(
        self,
        insight: Union[DetectedRisk, DetectedOpportunity],
        company_profile: Optional[Dict[str, Any]] = None
    ) -> List[RecommendationCreate]:
        """
        Generate recommendations for a detected risk or opportunity.
        
        Args:
            insight: Detected risk or opportunity
            company_profile: Optional company context for customization
            
        Returns:
            List of recommendation objects
        """
        recommendations = []
        
        # Determine the insight code
        if hasattr(insight, 'risk_code'):
            insight_code = insight.risk_code
            insight_type = "risk"
        else:
            insight_code = insight.opportunity_code
            insight_type = "opportunity"
        
        # Find applicable template
        template = self._find_template(insight_code)
        
        if not template:
            # Generate generic recommendations
            template = self._generate_generic_template(insight_type, insight_code)
        
        # Generate recommendations from template
        priority = 1
        
        # Immediate actions
        for action in template.immediate_actions:
            rec = RecommendationCreate(
                insight_id=0,  # Will be set when persisted
                category="immediate",
                priority=priority,
                action_title=action["action"][:200],
                action_description=action["action"],
                responsible_role=action.get("responsible"),
                estimated_effort=action.get("effort", template.default_effort),
                estimated_timeframe=action.get("timeframe", "Today"),
                expected_benefit=self._get_expected_benefit(insight_type),
                success_metrics=template.success_metrics
            )
            recommendations.append(rec)
            priority += 1
        
        # Short-term actions
        for action in template.short_term_actions:
            rec = RecommendationCreate(
                insight_id=0,
                category="short_term",
                priority=priority,
                action_title=action["action"][:200],
                action_description=action["action"],
                responsible_role=action.get("responsible"),
                estimated_effort=action.get("effort", template.default_effort),
                estimated_timeframe=action.get("timeframe", "This week"),
                expected_benefit=self._get_expected_benefit(insight_type),
                success_metrics=template.success_metrics
            )
            recommendations.append(rec)
            priority += 1
        
        # Medium-term actions
        for action in template.medium_term_actions:
            rec = RecommendationCreate(
                insight_id=0,
                category="medium_term",
                priority=priority,
                action_title=action["action"][:200],
                action_description=action["action"],
                responsible_role=action.get("responsible"),
                estimated_effort=action.get("effort", "High"),
                estimated_timeframe=action.get("timeframe", "This month"),
                expected_benefit=self._get_expected_benefit(insight_type),
                success_metrics=template.success_metrics
            )
            recommendations.append(rec)
            priority += 1
        
        return recommendations
    
    def _find_template(self, insight_code: str) -> Optional[RecommendationTemplate]:
        """Find the best matching template for an insight"""
        
        # Direct match
        if insight_code in self.templates:
            return self.templates[insight_code]
        
        # Partial match
        for template_code, template in self.templates.items():
            if insight_code in template.applicable_to:
                return template
            # Match by prefix (e.g., RISK_SUPPLY matches RISK_SUPPLY_CHAIN)
            if insight_code.startswith(template_code.rsplit('_', 1)[0]):
                return template
        
        return None
    
    def _generate_generic_template(self, insight_type: str, code: str) -> RecommendationTemplate:
        """Generate a generic template for unmatched insights"""
        
        if insight_type == "risk":
            return RecommendationTemplate(
                code=f"GENERIC_{code}",
                name=f"Generic Risk Response",
                applicable_to=[code],
                immediate_actions=[
                    {
                        "action": "Assess the situation and gather more information",
                        "responsible": "Manager",
                        "timeframe": "Today",
                        "effort": "Low"
                    },
                    {
                        "action": "Identify potential impacts on operations",
                        "responsible": "Operations",
                        "timeframe": "Today",
                        "effort": "Medium"
                    }
                ],
                short_term_actions=[
                    {
                        "action": "Develop mitigation plan",
                        "responsible": "Management",
                        "timeframe": "This week",
                        "effort": "Medium"
                    },
                    {
                        "action": "Communicate with stakeholders",
                        "responsible": "Management",
                        "timeframe": "This week",
                        "effort": "Low"
                    }
                ],
                success_metrics=["Risk mitigated", "Operations stable"]
            )
        else:
            return RecommendationTemplate(
                code=f"GENERIC_{code}",
                name=f"Generic Opportunity Capture",
                applicable_to=[code],
                immediate_actions=[
                    {
                        "action": "Assess the opportunity and gather data",
                        "responsible": "Manager",
                        "timeframe": "Today",
                        "effort": "Low"
                    },
                    {
                        "action": "Identify resources needed to capture opportunity",
                        "responsible": "Management",
                        "timeframe": "Today",
                        "effort": "Medium"
                    }
                ],
                short_term_actions=[
                    {
                        "action": "Develop action plan to capture opportunity",
                        "responsible": "Management",
                        "timeframe": "This week",
                        "effort": "Medium"
                    },
                    {
                        "action": "Allocate resources and begin execution",
                        "responsible": "Operations",
                        "timeframe": "This week",
                        "effort": "Medium"
                    }
                ],
                success_metrics=["Opportunity captured", "Value realized"]
            )
    
    def _get_expected_benefit(self, insight_type: str) -> str:
        """Get expected benefit text based on insight type"""
        if insight_type == "risk":
            return "Risk mitigation and operational continuity"
        else:
            return "Value capture and competitive advantage"
    
    def create_action_plan(
        self,
        insight: Union[DetectedRisk, DetectedOpportunity],
        recommendations: List[RecommendationCreate]
    ) -> ActionPlan:
        """
        Create a comprehensive action plan from recommendations.
        
        Args:
            insight: The risk or opportunity being addressed
            recommendations: List of generated recommendations
            
        Returns:
            Complete ActionPlan object
        """
        action_items = []
        step_num = 1
        
        for rec in recommendations:
            step = ActionPlanStep(
                step_number=step_num,
                action=rec.action_description,
                category=rec.category,
                timeframe=rec.estimated_timeframe or "TBD",
                responsible=rec.responsible_role or "Manager",
                resources={},
                success_metric=rec.success_metrics[0] if rec.success_metrics else "Complete action",
                dependencies=None if step_num == 1 else [step_num - 1] if rec.category != "immediate" else None
            )
            action_items.append(step)
            step_num += 1
        
        # Determine title
        if hasattr(insight, 'risk_code'):
            insight_title = insight.description
            plan_title = f"Risk Mitigation: {insight.title}"
        else:
            insight_title = insight.description
            plan_title = f"Opportunity Capture: {insight.title}"
        
        return ActionPlan(
            insight_id=0,  # Will be set when persisted
            insight_title=insight_title[:200] if len(insight_title) > 200 else insight_title,
            plan_title=plan_title[:200] if len(plan_title) > 200 else plan_title,
            action_items=action_items,
            risk_factors=["Resource availability", "Timeline constraints"],
            success_criteria=["All actions completed", "Outcome achieved"],
            created_at=datetime.utcnow()
        )
    
    def generate_narrative(
        self,
        insight: Union[DetectedRisk, DetectedOpportunity],
        recommendations: List[RecommendationCreate]
    ) -> NarrativeContent:
        """
        Generate narrative content for executive communication.
        
        Args:
            insight: The risk or opportunity
            recommendations: Associated recommendations
            
        Returns:
            NarrativeContent for display
        """
        is_risk = hasattr(insight, 'risk_code')
        
        if is_risk:
            emoji = self._get_risk_emoji(insight.severity_level)
            insight_type = "risk"
            urgency = self._get_urgency(insight.severity_level)
            headline = f"Alert: {insight.title}"
            why_it_matters = (
                f"This {insight.severity_level} severity risk affects {insight.category} operations "
                f"with a confidence level of {float(insight.confidence) * 100:.0f}%."
            )
        else:
            emoji = "🎯" if insight.priority_level == "high" else "💡"
            insight_type = "opportunity"
            urgency = "THIS WEEK" if insight.priority_level == "high" else "THIS MONTH"
            headline = f"Opportunity: {insight.title}"
            why_it_matters = (
                f"This {insight.priority_level} priority opportunity in {insight.category} "
                f"has a potential value score of {float(insight.potential_value):.1f}/10."
            )
        
        # Build what to do summary
        immediate_actions = [r.action_title for r in recommendations if r.category == "immediate"][:2]
        what_to_do = ". ".join(immediate_actions) if immediate_actions else "Review and assess the situation."
        
        return NarrativeContent(
            insight_id=0,
            insight_type=insight_type,
            emoji=emoji,
            headline=headline,
            summary=insight.description[:200] if len(insight.description) > 200 else insight.description,
            situation=insight.description,
            why_it_matters=why_it_matters,
            what_to_do=what_to_do,
            urgency_indicator=urgency,
            confidence_statement=f"Based on analysis of operational indicators",
            generated_at=datetime.utcnow()
        )
    
    def _get_risk_emoji(self, severity: str) -> str:
        """Get emoji based on risk severity"""
        emoji_map = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        return emoji_map.get(severity, "⚠️")
    
    def _get_urgency(self, severity: str) -> str:
        """Get urgency indicator based on severity"""
        urgency_map = {
            "critical": "NOW",
            "high": "TODAY",
            "medium": "THIS WEEK",
            "low": "THIS MONTH"
        }
        return urgency_map.get(severity, "THIS WEEK")
    
    def get_templates_count(self) -> int:
        """Get total number of recommendation templates"""
        return len(self.templates)


# Export for easy importing
__all__ = ['RecommendationEngine', 'RecommendationTemplate']
