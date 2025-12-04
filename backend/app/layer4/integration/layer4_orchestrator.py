"""
Layer 4: Business Insights Orchestrator

Complete pipeline coordinating:
1. Risk detection (Tier 1 + Tier 2)
2. Opportunity detection
3. Risk scoring
4. Narrative generation
5. Recommendation generation
6. Multi-database storage
7. Cache management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from pymongo import MongoClient
from redis import Redis

from app.layer4.risk_detection.rule_based_detector import RuleBasedRiskDetector
from app.layer4.risk_detection.pattern_detector import PatternBasedRiskDetector
from app.layer4.opportunity_detection.rule_based_detector import RuleBasedOpportunityDetector
from app.layer4.scoring.risk_scorer import RiskScorer
from app.layer4.narrative.generator import NarrativeGenerator
from app.layer4.recommendation.engine import RecommendationEngine
from app.layer4.storage.insight_storage import InsightStorageService
from app.layer4.storage.reasoning_storage import ReasoningStorageService
from app.layer4.storage.cache_manager import InsightCacheManager
from app.layer4.mock_data.layer3_mock_generator import MockLayer3Generator, OperationalIndicators
from app.layer4.schemas.risk_schemas import DetectedRisk, RiskScoreBreakdown

logger = logging.getLogger(__name__)


class Layer4Orchestrator:
    """
    Complete Layer 4 pipeline orchestrator

    Workflow:
    1. Detect risks (rule-based + pattern-based)
    2. Detect opportunities
    3. Score and aggregate
    4. Generate narratives
    5. Generate recommendations
    6. Store in PostgreSQL, MongoDB, Redis
    7. Calculate portfolio metrics
    8. Identify top priorities
    """

    def __init__(
        self,
        db_session: Session,
        mongo_client: MongoClient,
        redis_client: Redis,
        mongo_db_name: str = "national_indicator"
    ):
        """
        Initialize orchestrator with database connections

        Args:
            db_session: SQLAlchemy session
            mongo_client: MongoDB client
            redis_client: Redis client
            mongo_db_name: MongoDB database name
        """
        # Detection components
        self.rule_detector = RuleBasedRiskDetector()
        self.pattern_detector = PatternBasedRiskDetector()
        self.opportunity_detector = RuleBasedOpportunityDetector()

        # Scoring and generation
        self.scorer = RiskScorer()
        self.narrative_gen = NarrativeGenerator()
        self.recommendation_engine = RecommendationEngine()

        # Storage services
        self.insight_storage = InsightStorageService(db_session)
        self.reasoning_storage = ReasoningStorageService(mongo_client, mongo_db_name)
        self.cache_manager = InsightCacheManager(redis_client)

        # Mock data generator (for testing)
        self.mock_layer3 = MockLayer3Generator()

        logger.info("Layer4Orchestrator initialized successfully")

    def process_company(
        self,
        company_id: str,
        indicators: OperationalIndicators,
        company_profile: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Complete Layer 4 processing for a company

        Args:
            company_id: Company identifier
            indicators: Operational indicators from Layer 3
            company_profile: Company profile information
            use_cache: Whether to use cached results

        Returns:
            Dictionary with:
            - insights: List of stored insights with narratives
            - portfolio_metrics: Aggregated portfolio metrics
            - top_priorities: Top 5 priority actions
        """
        logger.info(f"Processing company {company_id} through Layer 4 pipeline")

        # Check cache first
        if use_cache:
            cached = self.cache_manager.get_cached_insights(company_id)
            if cached:
                logger.info(f"Returning cached insights for company {company_id}")
                return cached

        industry = company_profile.get('industry', 'general')

        # Step 1: Detect risks
        logger.debug("Step 1: Detecting risks...")
        rule_risks = self.rule_detector.detect_risks(
            company_id=company_id,
            industry=industry,
            indicators=indicators,
            company_profile=company_profile
        )

        pattern_risks = self.pattern_detector.detect_risks(
            company_id=company_id,
            industry=industry,
            indicators=indicators,
            company_profile=company_profile
        )

        # Combine and deduplicate risks
        all_risks = self._deduplicate_risks(rule_risks + pattern_risks)
        logger.info(f"Detected {len(all_risks)} unique risks")

        # Step 2: Detect opportunities
        logger.debug("Step 2: Detecting opportunities...")
        business_scale = company_profile.get('business_scale', 'medium')
        opportunities = self.opportunity_detector.detect_opportunities(
            company_id=company_id,
            industry=industry,
            indicators=indicators,
            business_scale=business_scale
        )
        logger.info(f"Detected {len(opportunities)} opportunities")

        # Step 3: Process each risk
        logger.debug("Step 3: Processing and storing risks...")
        risk_insights = []

        for risk in all_risks:
            # Score the risk
            score_breakdown = self.scorer.calculate_risk_score(
                risk, indicators, company_profile
            )

            # Update risk with scores
            risk.probability = score_breakdown.probability
            risk.impact = score_breakdown.impact
            risk.urgency = score_breakdown.urgency
            risk.confidence = score_breakdown.confidence
            risk.final_score = score_breakdown.final_score
            risk.severity_level = score_breakdown.severity

            # Generate narrative
            narrative = self.narrative_gen.generate_risk_narrative(
                risk, company_profile
            )

            # Generate recommendations
            recommendations = self.recommendation_engine.generate_recommendations(
                risk, company_profile
            )

            # Convert recommendations to dict format
            recs_dict = []
            for rec in recommendations:
                recs_dict.append({
                    "category": rec.category,
                    "priority": rec.priority,
                    "action_title": rec.action_title,
                    "action_description": rec.action_description,
                    "responsible_role": rec.responsible_role,
                    "estimated_effort": rec.estimated_effort,
                    "timeframe": rec.estimated_timeframe,
                    "expected_benefit": rec.expected_benefit
                })

            # Store in PostgreSQL
            insight_id = self.insight_storage.store_business_insight(
                risk, company_id
            )

            # Store recommendations
            self.insight_storage.store_recommendations(
                insight_id, recs_dict
            )

            # Store reasoning in MongoDB
            self.reasoning_storage.store_detection_reasoning(
                insight_id, risk, score_breakdown
            )

            # Store narrative in MongoDB
            self.reasoning_storage.store_narrative(
                insight_id, company_id, narrative
            )

            # Cache narrative
            self.cache_manager.cache_narrative(insight_id, narrative)

            risk_insights.append({
                "insight_id": insight_id,
                "risk": risk.dict(),
                "narrative": narrative,
                "recommendations": recs_dict,
                "score_breakdown": score_breakdown.dict()
            })

        # Step 4: Process opportunities
        logger.debug("Step 4: Processing and storing opportunities...")
        opportunity_insights = []

        for opp in opportunities:
            # Generate narrative
            narrative = self.narrative_gen.generate_opportunity_narrative(
                opp, company_profile
            )

            # Generate recommendations
            recommendations = self.recommendation_engine.generate_opportunity_recommendations(
                opp, company_profile
            )

            # Convert recommendations to dict format
            recs_dict = []
            for rec in recommendations:
                recs_dict.append({
                    "category": rec.category,
                    "priority": rec.priority,
                    "action_title": rec.action_title,
                    "action_description": rec.action_description,
                    "responsible_role": rec.responsible_role,
                    "estimated_effort": rec.estimated_effort,
                    "timeframe": rec.estimated_timeframe,
                    "expected_benefit": rec.expected_benefit
                })

            # Store in PostgreSQL
            insight_id = self.insight_storage.store_opportunity_insight(
                opp, company_id
            )

            # Store recommendations
            self.insight_storage.store_recommendations(
                insight_id, recs_dict
            )

            # Store reasoning in MongoDB
            self.reasoning_storage.store_opportunity_reasoning(
                insight_id, opp
            )

            # Store narrative in MongoDB
            self.reasoning_storage.store_narrative(
                insight_id, company_id, narrative
            )

            # Cache narrative
            self.cache_manager.cache_narrative(insight_id, narrative)

            opportunity_insights.append({
                "insight_id": insight_id,
                "opportunity": opp.dict(),
                "narrative": narrative,
                "recommendations": recs_dict
            })

        # Step 5: Calculate portfolio metrics
        logger.debug("Step 5: Calculating portfolio metrics...")
        portfolio_metrics = self._calculate_portfolio_metrics(
            all_risks, opportunities
        )

        # Step 6: Identify top priorities
        logger.debug("Step 6: Identifying top priorities...")
        top_priorities = self._identify_top_priorities(
            all_risks, opportunities
        )

        # Compile final output
        output = {
            "company_id": company_id,
            "timestamp": datetime.now().isoformat(),
            "risk_insights": risk_insights,
            "opportunity_insights": opportunity_insights,
            "portfolio_metrics": portfolio_metrics,
            "top_priorities": top_priorities,
            "summary": {
                "total_risks": len(all_risks),
                "total_opportunities": len(opportunities),
                "critical_risks": sum(1 for r in all_risks if r.severity_level == "critical"),
                "high_priority_opportunities": sum(1 for o in opportunities if o.priority == "high")
            }
        }

        # Cache the output
        self.cache_manager.cache_company_insights(company_id, [output])

        # Cache portfolio metrics
        self.cache_manager.cache_portfolio_metrics(company_id, portfolio_metrics)

        logger.info(f"Successfully processed company {company_id}: {len(all_risks)} risks, {len(opportunities)} opportunities")

        return output

    def _deduplicate_risks(self, risks: List[DetectedRisk]) -> List[DetectedRisk]:
        """
        Remove duplicate/overlapping risks

        Strategy:
        1. Group by risk_code
        2. Keep highest confidence detection
        3. Merge triggering_indicators
        4. Update reasoning to mention multiple detection methods
        """
        if not risks:
            return []

        # Group by risk code
        risk_groups = {}
        for risk in risks:
            code = risk.risk_code
            if code not in risk_groups:
                risk_groups[code] = []
            risk_groups[code].append(risk)

        # Deduplicate each group
        deduplicated = []
        for code, group in risk_groups.items():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Keep highest confidence
                best_risk = max(group, key=lambda r: float(r.confidence))

                # Merge reasoning
                methods = set(r.detection_method for r in group)
                if len(methods) > 1:
                    best_risk.detection_method = "combined"
                    best_risk.reasoning += f" Detected by multiple methods: {', '.join(methods)}."

                deduplicated.append(best_risk)
                logger.debug(f"Deduplicated {len(group)} detections of {code} into one")

        return deduplicated

    def _calculate_portfolio_metrics(
        self,
        risks: List[DetectedRisk],
        opportunities: List
    ) -> Dict[str, Any]:
        """Calculate company-level portfolio metrics"""

        # Count by severity
        severity_counts = {
            "critical": sum(1 for r in risks if r.severity_level == "critical"),
            "high": sum(1 for r in risks if r.severity_level == "high"),
            "medium": sum(1 for r in risks if r.severity_level == "medium"),
            "low": sum(1 for r in risks if r.severity_level == "low")
        }

        # Count by category
        category_counts = {}
        for risk in risks:
            cat = risk.category
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Calculate portfolio risk score (weighted average)
        if risks:
            severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            weighted_score = sum(
                float(r.final_score) * severity_weights.get(r.severity_level, 1)
                for r in risks
            )
            portfolio_risk_score = weighted_score / len(risks)
        else:
            portfolio_risk_score = 0.0

        # Opportunity metrics
        if opportunities:
            avg_opportunity_value = sum(float(o.potential_value) for o in opportunities) / len(opportunities)
            high_feasibility = sum(1 for o in opportunities if float(o.feasibility) >= 0.7)
        else:
            avg_opportunity_value = 0.0
            high_feasibility = 0

        return {
            "total_risks": len(risks),
            "total_opportunities": len(opportunities),
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "portfolio_risk_score": round(portfolio_risk_score, 2),
            "requires_immediate_action": [
                {
                    "risk_code": r.risk_code,
                    "title": r.title,
                    "severity": r.severity_level,
                    "score": float(r.final_score)
                }
                for r in risks if r.requires_immediate_action
            ],
            "average_opportunity_value": round(avg_opportunity_value, 2),
            "high_feasibility_opportunities": high_feasibility
        }

    def _identify_top_priorities(
        self,
        risks: List[DetectedRisk],
        opportunities: List
    ) -> List[Dict]:
        """
        Identify top 5 priority actions

        Priorities:
        1. Critical risks requiring immediate action
        2. High risks
        3. High-value, high-feasibility opportunities
        4. Medium risks with high urgency
        """
        priorities = []

        # Add critical/high risks
        for risk in risks:
            if risk.severity_level in ["critical", "high"]:
                priorities.append({
                    "type": "risk",
                    "rank": None,
                    "code": risk.risk_code,
                    "title": risk.title,
                    "severity": risk.severity_level,
                    "score": float(risk.final_score),
                    "urgency": risk.urgency,
                    "requires_immediate_action": risk.requires_immediate_action
                })

        # Add high-value opportunities
        for opp in opportunities:
            if opp.priority == "high" and float(opp.feasibility) >= 0.6:
                priorities.append({
                    "type": "opportunity",
                    "rank": None,
                    "code": opp.opportunity_code,
                    "title": opp.title,
                    "priority": opp.priority,
                    "value": float(opp.potential_value),
                    "feasibility": float(opp.feasibility),
                    "window_days": opp.window_days
                })

        # Sort by priority
        # Risks: immediate action first, then by score, then by urgency
        # Opportunities: by value * feasibility
        def priority_sort_key(item):
            if item["type"] == "risk":
                immediate = 1000 if item["requires_immediate_action"] else 0
                return -(immediate + item["score"] * 10 + item["urgency"])
            else:
                return -(item["value"] * item["feasibility"])

        priorities.sort(key=priority_sort_key)

        # Assign ranks and take top 5
        for i, item in enumerate(priorities[:5], 1):
            item["rank"] = i

        return priorities[:5]

    def get_company_insights_summary(
        self,
        company_id: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get summary of active insights for a company

        Args:
            company_id: Company identifier
            use_cache: Whether to check cache first

        Returns:
            Summary dictionary
        """
        # Check cache
        if use_cache:
            cached_metrics = self.cache_manager.get_cached_portfolio_metrics(company_id)
            if cached_metrics:
                logger.debug(f"Returning cached portfolio metrics for {company_id}")
                return cached_metrics

        # Fetch from database
        active_insights = self.insight_storage.get_active_insights(company_id)

        # Separate risks and opportunities
        risks = [i for i in active_insights if i.insight_type == 'risk']
        opportunities = [i for i in active_insights if i.insight_type == 'opportunity']

        # Calculate metrics
        severity_counts = {
            "critical": sum(1 for r in risks if r.severity_level == "critical"),
            "high": sum(1 for r in risks if r.severity_level == "high"),
            "medium": sum(1 for r in risks if r.severity_level == "medium"),
            "low": sum(1 for r in risks if r.severity_level == "low")
        }

        summary = {
            "company_id": company_id,
            "total_active_risks": len(risks),
            "total_active_opportunities": len(opportunities),
            "severity_breakdown": severity_counts,
            "urgent_risks": sum(1 for r in risks if r.is_urgent),
            "high_priority_opportunities": sum(
                1 for o in opportunities if o.severity_level == "high"  # Using severity_level for priority
            ),
            "timestamp": datetime.now().isoformat()
        }

        # Cache the result
        self.cache_manager.cache_portfolio_metrics(company_id, summary)

        return summary
