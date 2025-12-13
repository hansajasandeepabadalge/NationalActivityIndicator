"""
Layer 3: Indicator History Service

Manages historical time-series data for operational indicators.
Stores daily snapshots and provides trend analysis.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pydantic import BaseModel


class IndicatorSnapshot(BaseModel):
    """Single point-in-time snapshot of an indicator"""
    indicator_id: str
    company_id: Optional[str] = None
    timestamp: datetime
    value: float
    baseline_value: Optional[float] = None
    deviation: Optional[float] = None
    impact_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class IndicatorHistoryService:
    """Service for managing indicator historical data"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "national_indicator"):
        self.mongo_client = mongo_client
        self.db: Database = mongo_client[db_name]
        self.collection = self.db["indicator_history"]
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for efficient querying"""
        # Compound index for querying by indicator and time
        self.collection.create_index([
            ("indicator_id", ASCENDING),
            ("company_id", ASCENDING),
            ("timestamp", DESCENDING)
        ])
        
        # Index for time-based queries
        self.collection.create_index([("timestamp", DESCENDING)])
    
    def save_snapshot(
        self,
        indicator_id: str,
        value: float,
        company_id: Optional[str] = None,
        baseline_value: Optional[float] = None,
        deviation: Optional[float] = None,
        impact_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Save a snapshot of an indicator's current state.
        
        Args:
            indicator_id: Unique identifier for the indicator
            value: Current value of the indicator
            company_id: Optional company ID (None for national indicators)
            baseline_value: Baseline/reference value
            deviation: Deviation from baseline
            impact_score: Impact score (0-10)
            metadata: Additional metadata
            timestamp: Snapshot timestamp (defaults to now)
        
        Returns:
            Inserted document ID
        """
        snapshot = {
            "indicator_id": indicator_id,
            "company_id": company_id,
            "timestamp": timestamp or datetime.utcnow(),
            "value": value,
            "baseline_value": baseline_value,
            "deviation": deviation,
            "impact_score": impact_score,
            "metadata": metadata or {}
        }
        
        result = self.collection.insert_one(snapshot)
        return str(result.inserted_id)
    
    def get_history(
        self,
        indicator_id: str,
        company_id: Optional[str] = None,
        days: int = 7,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical data for an indicator.
        
        Args:
            indicator_id: Indicator to fetch history for
            company_id: Optional company filter
            days: Number of days of history to fetch
            limit: Optional limit on number of data points
        
        Returns:
            List of historical snapshots, ordered by timestamp (newest first)
        """
        # Calculate start date
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = {
            "indicator_id": indicator_id,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }
        
        if company_id is not None:
            query["company_id"] = company_id
        
        # Execute query
        cursor = self.collection.find(query).sort("timestamp", DESCENDING)
        
        if limit:
            cursor = cursor.limit(limit)
        
        # Convert to list and format
        history = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            history.append(doc)
        
        return history
    
    def get_trend_summary(
        self,
        indicator_id: str,
        company_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get trend summary for an indicator.
        
        Returns:
            Dictionary with trend direction, change percentage, and statistics
        """
        history = self.get_history(indicator_id, company_id, days)
        
        if len(history) < 2:
            return {
                "trend": "insufficient_data",
                "change_percent": 0.0,
                "data_points": len(history)
            }
        
        # Sort by timestamp ascending for trend calculation
        history_sorted = sorted(history, key=lambda x: x["timestamp"])
        
        # Get first and last values
        first_value = history_sorted[0]["value"]
        last_value = history_sorted[-1]["value"]
        
        # Calculate change
        change = last_value - first_value
        change_percent = (change / first_value * 100) if first_value != 0 else 0.0
        
        # Determine trend direction
        if abs(change_percent) < 1.0:
            trend = "stable"
        elif change_percent > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Calculate statistics
        values = [h["value"] for h in history_sorted]
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "change_absolute": round(change, 2),
            "current_value": last_value,
            "previous_value": first_value,
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": round(sum(values) / len(values), 2),
            "data_points": len(history),
            "period_days": days
        }
    
    def bulk_save_snapshots(self, snapshots: List[IndicatorSnapshot]) -> int:
        """
        Save multiple snapshots at once.
        
        Args:
            snapshots: List of IndicatorSnapshot objects
        
        Returns:
            Number of documents inserted
        """
        if not snapshots:
            return 0
        
        documents = [s.model_dump() for s in snapshots]
        result = self.collection.insert_many(documents)
        return len(result.inserted_ids)
    
    def delete_old_snapshots(self, days_to_keep: int = 365) -> int:
        """
        Delete snapshots older than specified days.
        
        Args:
            days_to_keep: Number of days of history to retain
        
        Returns:
            Number of documents deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        result = self.collection.delete_many({"timestamp": {"$lt": cutoff_date}})
        return result.deleted_count
