"""Optimized database queries for common operations"""

from typing import List, Dict
from datetime import datetime, timedelta
from app.db.mongodb_entities import MongoDBEntityStorage


class OptimizedQueries:
    """Optimized database queries for common operations"""

    def __init__(self):
        self.mongo = MongoDBEntityStorage()

    def get_recent_high_confidence_indicators(
        self,
        hours: int = 24,
        min_confidence: float = 0.7,
        limit: int = 20
    ) -> List[Dict]:
        """Get recent high-confidence indicators (optimized)"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Use projection to limit fields
        results = self.mongo.indicator_calculations.find(
            {
                "calculation_timestamp": {"$gte": cutoff},
                "confidence": {"$gte": min_confidence}
            },
            {
                "_id": 0,
                "article_id": 1,
                "indicator_id": 1,
                "confidence": 1,
                "calculation_timestamp": 1
            }
        ).sort("calculation_timestamp", -1).limit(limit)

        return list(results)

    def get_indicator_statistics(self, indicator_id: str, days: int = 30) -> Dict:
        """Get aggregated statistics for an indicator"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "indicator_id": indicator_id,
                    "calculation_timestamp": {"$gte": cutoff}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"},
                    "max_confidence": {"$max": "$confidence"},
                    "min_confidence": {"$min": "$confidence"}
                }
            }
        ]

        result = list(self.mongo.indicator_calculations.aggregate(pipeline))
        return result[0] if result else {}

    def get_indicators_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """Get all indicators for a specific category"""
        results = self.mongo.indicator_calculations.find(
            {"indicator_id": {"$regex": f"^{category}_"}},
            {"_id": 0, "indicator_id": 1, "confidence": 1, "calculation_timestamp": 1}
        ).sort("calculation_timestamp", -1).limit(limit)

        return list(results)

    def get_articles_by_indicator(
        self,
        indicator_id: str,
        min_confidence: float = 0.5,
        limit: int = 50
    ) -> List[str]:
        """Get article IDs that triggered a specific indicator"""
        results = self.mongo.indicator_calculations.find(
            {
                "indicator_id": indicator_id,
                "confidence": {"$gte": min_confidence}
            },
            {"_id": 0, "article_id": 1}
        ).limit(limit)

        return [doc["article_id"] for doc in results]
