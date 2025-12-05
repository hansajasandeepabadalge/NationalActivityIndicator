"""Service for storing classification results in database"""

from sqlalchemy.orm import Session
from app.models.article_mapping import ArticleIndicatorMapping
from typing import List, Dict
from datetime import datetime


class ClassificationStorageService:
    """Store classification results in database"""

    def __init__(self, db: Session):
        """
        Initialize storage service

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def store_classifications(
        self,
        article_id: str,
        article_published_at: datetime,
        article_category: str,
        assignments: List[Dict],
        classification_method: str = "rule_based"
    ) -> int:
        """
        Store all indicator assignments for an article

        Args:
            article_id: Unique article identifier
            article_published_at: Article publication timestamp
            article_category: PESTEL category of article
            assignments: List of indicator assignments with confidence
            classification_method: Method used (rule_based, ml, hybrid)

        Returns:
            Number of mappings stored
        """
        stored_count = 0

        for assignment in assignments:
            mapping = ArticleIndicatorMapping(
                article_id=article_id,
                indicator_id=assignment['indicator_id'],
                match_confidence=assignment['confidence'],
                classification_method=classification_method,
                matched_keywords=assignment.get('matched_keywords', []),
                keyword_match_count=assignment.get('keyword_match_count', 0),
                article_category=article_category,
                article_published_at=article_published_at,
                extra_metadata={'indicator_name': assignment.get('indicator_name')}
            )

            self.db.add(mapping)
            stored_count += 1

        self.db.commit()
        return stored_count

    def get_article_indicators(self, article_id: str) -> List[ArticleIndicatorMapping]:
        """
        Retrieve all indicators for an article

        Args:
            article_id: Article identifier

        Returns:
            List of ArticleIndicatorMapping objects ordered by confidence
        """
        return self.db.query(ArticleIndicatorMapping).filter(
            ArticleIndicatorMapping.article_id == article_id
        ).order_by(ArticleIndicatorMapping.match_confidence.desc()).all()

    def get_indicator_articles(
        self,
        indicator_id: str,
        min_confidence: float = 0.3
    ) -> List[ArticleIndicatorMapping]:
        """
        Get all articles assigned to an indicator

        Args:
            indicator_id: Indicator identifier
            min_confidence: Minimum confidence threshold

        Returns:
            List of ArticleIndicatorMapping objects
        """
        return self.db.query(ArticleIndicatorMapping).filter(
            ArticleIndicatorMapping.indicator_id == indicator_id,
            ArticleIndicatorMapping.match_confidence >= min_confidence
        ).all()
