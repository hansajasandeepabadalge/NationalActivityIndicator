from typing import List, Dict, Any
from datetime import datetime, timedelta
import math

class WeightingSystem:
    """
    Calculates weights for articles based on various factors.
    """
    
    @staticmethod
    def calculate_article_weight(article: Dict[str, Any]) -> float:
        """
        Calculate composite weight for an article.
        """
        recency_weight = WeightingSystem._calculate_recency_weight(article)
        credibility_weight = WeightingSystem._calculate_credibility_weight(article)
        
        return recency_weight * credibility_weight

    @staticmethod
    def _calculate_recency_weight(article: Dict[str, Any]) -> float:
        """
        Newer articles get higher weight.
        Decay function: 1 / (1 + days_old)
        """
        try:
            publish_str = article.get("metadata", {}).get("publish_timestamp")
            if not publish_str:
                return 1.0
                
            publish_date = datetime.fromisoformat(publish_str.replace("Z", "+00:00"))
            # Naive approach for now, assuming UTC
            if publish_date.tzinfo is None:
                now = datetime.now()
            else:
                now = datetime.now(publish_date.tzinfo)
                
            age = now - publish_date
            days_old = max(0, age.days)
            
            # Decay factor
            return 1.0 / (1.0 + (days_old * 0.2)) # Slow decay
        except Exception:
            return 1.0

    @staticmethod
    def _calculate_credibility_weight(article: Dict[str, Any]) -> float:
        """
        Use source credibility score.
        """
        return article.get("metadata", {}).get("source_credibility", 1.0)
