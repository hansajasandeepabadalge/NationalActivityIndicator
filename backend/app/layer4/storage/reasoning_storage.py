"""
Layer 4: MongoDB Storage Service for Detailed Reasoning

Handles persistence of:
- Detection reasoning and explanations
- Generated narratives
- Score breakdowns
- Contextual information
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import logging

from app.layer4.schemas.risk_schemas import DetectedRisk, RiskScoreBreakdown
from app.layer4.schemas.opportunity_schemas import DetectedOpportunity

logger = logging.getLogger(__name__)


class ReasoningStorageService:
    """
    MongoDB storage for detailed reasoning and narratives

    Collections:
    - insight_reasoning: Detection logic and score breakdowns
    - narratives: Human-readable narratives
    - recommendation_details: Implementation guidance
    """

    def __init__(self, mongo_client: MongoClient, db_name: str = "national_indicator"):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        self.insight_reasoning = self.db['insight_reasoning']
        self.narratives = self.db['narratives']
        self.recommendation_details = self.db['recommendation_details']

        # Create indexes
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes for efficient querying"""
        # insight_reasoning indexes
        self.insight_reasoning.create_index([("insight_id", 1)])
        self.insight_reasoning.create_index([("timestamp", DESCENDING)])
        self.insight_reasoning.create_index([("risk_code", 1)])

        # narratives indexes
        self.narratives.create_index([("insight_id", 1)])
        self.narratives.create_index([("company_id", 1), ("timestamp", DESCENDING)])

        # recommendation_details indexes
        self.recommendation_details.create_index([("insight_id", 1)])

        logger.debug("MongoDB indexes ensured for Layer 4 collections")

    def store_detection_reasoning(
        self,
        insight_id: int,
        risk: DetectedRisk,
        score_breakdown: RiskScoreBreakdown
    ) -> str:
        """
        Store detailed reasoning for risk detection

        Args:
            insight_id: PostgreSQL insight_id
            risk: Detected risk
            score_breakdown: Detailed score breakdown

        Returns:
            MongoDB document ID
        """
        document = {
            "insight_id": insight_id,
            "timestamp": datetime.now(),
            "detection_method": risk.detection_method,
            "risk_code": risk.risk_code,
            "reasoning": risk.reasoning,
            "score_breakdown": {
                "probability": float(score_breakdown.probability),
                "probability_reasoning": score_breakdown.probability_reasoning,
                "impact": float(score_breakdown.impact),
                "impact_reasoning": score_breakdown.impact_reasoning,
                "urgency": score_breakdown.urgency,
                "urgency_reasoning": score_breakdown.urgency_reasoning,
                "confidence": float(score_breakdown.confidence),
                "confidence_source": score_breakdown.confidence_source,
                "final_score": float(score_breakdown.final_score),
                "severity": score_breakdown.severity
            },
            "triggering_indicators": risk.triggering_indicators if isinstance(risk.triggering_indicators, dict) else {},
            "metadata": {
                "category": risk.category,
                "severity_level": risk.severity_level,
                "is_urgent": risk.is_urgent,
                "requires_immediate_action": risk.requires_immediate_action
            }
        }

        result = self.insight_reasoning.insert_one(document)

        logger.info(f"Stored reasoning for insight {insight_id}, MongoDB ID: {result.inserted_id}")

        return str(result.inserted_id)

    def store_opportunity_reasoning(
        self,
        insight_id: int,
        opportunity: DetectedOpportunity
    ) -> str:
        """
        Store detailed reasoning for opportunity detection

        Args:
            insight_id: PostgreSQL insight_id
            opportunity: Detected opportunity

        Returns:
            MongoDB document ID
        """
        document = {
            "insight_id": insight_id,
            "timestamp": datetime.now(),
            "detection_method": opportunity.detection_method,
            "opportunity_code": opportunity.opportunity_code,
            "reasoning": opportunity.reasoning,
            "score_breakdown": {
                "potential_value": float(opportunity.potential_value),
                "feasibility": float(opportunity.feasibility),
                "timing_score": opportunity.timing_score,
                "strategic_fit": float(opportunity.strategic_fit),
                "final_score": float(opportunity.final_score),
                "priority": opportunity.priority
            },
            "triggering_factors": opportunity.triggering_factors if isinstance(opportunity.triggering_factors, dict) else {},
            "metadata": {
                "category": opportunity.category,
                "window_days": opportunity.window_days,
                "estimated_roi": float(opportunity.estimated_roi) if opportunity.estimated_roi else None,
                "implementation_complexity": opportunity.implementation_complexity
            }
        }

        result = self.insight_reasoning.insert_one(document)

        logger.info(f"Stored opportunity reasoning for insight {insight_id}, MongoDB ID: {result.inserted_id}")

        return str(result.inserted_id)

    def store_narrative(
        self,
        insight_id: int,
        company_id: str,
        narrative: Dict[str, str]
    ) -> str:
        """
        Store generated narrative

        Args:
            insight_id: PostgreSQL insight_id
            company_id: Company identifier
            narrative: Dictionary with narrative components

        Returns:
            MongoDB document ID
        """
        document = {
            "insight_id": insight_id,
            "company_id": company_id,
            "timestamp": datetime.now(),
            **narrative  # emoji, headline, summary, detailed_explanation, etc.
        }

        result = self.narratives.insert_one(document)

        logger.info(f"Stored narrative for insight {insight_id}, MongoDB ID: {result.inserted_id}")

        return str(result.inserted_id)

    def store_recommendation_details(
        self,
        insight_id: int,
        recommendation_id: int,
        details: Dict[str, Any]
    ) -> str:
        """
        Store detailed implementation guidance for recommendation

        Args:
            insight_id: PostgreSQL insight_id
            recommendation_id: PostgreSQL recommendation_id
            details: Implementation details

        Returns:
            MongoDB document ID
        """
        document = {
            "insight_id": insight_id,
            "recommendation_id": recommendation_id,
            "timestamp": datetime.now(),
            **details
        }

        result = self.recommendation_details.insert_one(document)

        logger.info(f"Stored recommendation details for recommendation {recommendation_id}, MongoDB ID: {result.inserted_id}")

        return str(result.inserted_id)

    def get_reasoning(self, insight_id: int) -> Optional[Dict]:
        """
        Retrieve reasoning for an insight

        Args:
            insight_id: PostgreSQL insight_id

        Returns:
            Reasoning document or None
        """
        result = self.insight_reasoning.find_one(
            {"insight_id": insight_id},
            sort=[("timestamp", DESCENDING)]
        )

        if result:
            # Convert ObjectId to string for JSON serialization
            result['_id'] = str(result['_id'])
            logger.debug(f"Retrieved reasoning for insight {insight_id}")
        else:
            logger.debug(f"No reasoning found for insight {insight_id}")

        return result

    def get_narrative(self, insight_id: int) -> Optional[Dict]:
        """
        Retrieve narrative for an insight

        Args:
            insight_id: PostgreSQL insight_id

        Returns:
            Narrative document or None
        """
        result = self.narratives.find_one(
            {"insight_id": insight_id},
            sort=[("timestamp", DESCENDING)]
        )

        if result:
            # Convert ObjectId to string for JSON serialization
            result['_id'] = str(result['_id'])
            logger.debug(f"Retrieved narrative for insight {insight_id}")
        else:
            logger.debug(f"No narrative found for insight {insight_id}")

        return result

    def get_recommendation_details(self, recommendation_id: int) -> Optional[Dict]:
        """
        Retrieve detailed implementation guidance for recommendation

        Args:
            recommendation_id: PostgreSQL recommendation_id

        Returns:
            Recommendation details or None
        """
        result = self.recommendation_details.find_one(
            {"recommendation_id": recommendation_id},
            sort=[("timestamp", DESCENDING)]
        )

        if result:
            # Convert ObjectId to string for JSON serialization
            result['_id'] = str(result['_id'])
            logger.debug(f"Retrieved details for recommendation {recommendation_id}")
        else:
            logger.debug(f"No details found for recommendation {recommendation_id}")

        return result

    def get_company_narratives(
        self,
        company_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve recent narratives for a company

        Args:
            company_id: Company identifier
            limit: Maximum number of narratives to return

        Returns:
            List of narrative documents
        """
        cursor = self.narratives.find(
            {"company_id": company_id}
        ).sort("timestamp", DESCENDING).limit(limit)

        results = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            results.append(doc)

        logger.debug(f"Retrieved {len(results)} narratives for company {company_id}")

        return results

    def get_reasoning_by_risk_code(
        self,
        risk_code: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve historical reasoning for a specific risk type

        Args:
            risk_code: Risk code to search for
            limit: Maximum number of documents to return

        Returns:
            List of reasoning documents
        """
        cursor = self.insight_reasoning.find(
            {"risk_code": risk_code}
        ).sort("timestamp", DESCENDING).limit(limit)

        results = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            results.append(doc)

        logger.debug(f"Retrieved {len(results)} reasoning documents for risk code {risk_code}")

        return results

    def update_narrative(
        self,
        insight_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update existing narrative

        Args:
            insight_id: PostgreSQL insight_id
            updates: Fields to update

        Returns:
            True if successful
        """
        result = self.narratives.update_one(
            {"insight_id": insight_id},
            {
                "$set": {
                    **updates,
                    "updated_at": datetime.now()
                }
            },
            upsert=False
        )

        if result.modified_count > 0:
            logger.info(f"Updated narrative for insight {insight_id}")
            return True
        else:
            logger.warning(f"No narrative found to update for insight {insight_id}")
            return False

    def delete_reasoning(self, insight_id: int) -> bool:
        """
        Delete reasoning for an insight

        Args:
            insight_id: PostgreSQL insight_id

        Returns:
            True if successful
        """
        result = self.insight_reasoning.delete_many({"insight_id": insight_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted {result.deleted_count} reasoning document(s) for insight {insight_id}")
            return True
        else:
            logger.debug(f"No reasoning documents found to delete for insight {insight_id}")
            return False

    def delete_narrative(self, insight_id: int) -> bool:
        """
        Delete narrative for an insight

        Args:
            insight_id: PostgreSQL insight_id

        Returns:
            True if successful
        """
        result = self.narratives.delete_many({"insight_id": insight_id})

        if result.deleted_count > 0:
            logger.info(f"Deleted {result.deleted_count} narrative(s) for insight {insight_id}")
            return True
        else:
            logger.debug(f"No narratives found to delete for insight {insight_id}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """
        Get collection statistics

        Returns:
            Dictionary with document counts
        """
        return {
            "total_reasoning_documents": self.insight_reasoning.count_documents({}),
            "total_narratives": self.narratives.count_documents({}),
            "total_recommendation_details": self.recommendation_details.count_documents({})
        }
