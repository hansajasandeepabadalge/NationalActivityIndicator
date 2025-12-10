"""
Feedback Collection System

Collects and manages user feedback on insights, recommendations, and predictions.
Supports multiple feedback types and rating scales.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    USEFULNESS = "usefulness"  # Was this insight useful?
    ACCURACY = "accuracy"  # Was the prediction accurate?
    TIMELINESS = "timeliness"  # Was this alert timely?
    ACTIONABILITY = "actionability"  # Could you act on this?
    RELEVANCE = "relevance"  # Was this relevant to your business?
    OVERALL = "overall"  # Overall satisfaction


class FeedbackRating(Enum):
    """Standard rating scale for feedback."""
    VERY_POOR = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5
    
    # Quick ratings
    THUMBS_DOWN = -1
    THUMBS_UP = 1
    
    @classmethod
    def from_thumbs(cls, thumbs_up: bool) -> "FeedbackRating":
        """Convert thumbs up/down to rating."""
        return cls.THUMBS_UP if thumbs_up else cls.THUMBS_DOWN
    
    @classmethod
    def from_score(cls, score: int) -> "FeedbackRating":
        """Convert numeric score (1-5) to rating."""
        mapping = {
            1: cls.VERY_POOR,
            2: cls.POOR,
            3: cls.NEUTRAL,
            4: cls.GOOD,
            5: cls.EXCELLENT,
        }
        return mapping.get(score, cls.NEUTRAL)


@dataclass
class InsightFeedback:
    """Represents feedback on a specific insight."""
    feedback_id: str
    insight_id: str
    user_id: str
    company_id: str
    
    # Feedback content
    feedback_type: FeedbackType
    rating: FeedbackRating
    comment: Optional[str] = None
    
    # Context
    insight_type: str = ""  # "risk", "opportunity", "recommendation"
    insight_category: str = ""  # e.g., "SUPPLY_CHAIN", "WORKFORCE"
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    time_to_feedback: Optional[timedelta] = None  # Time from insight to feedback
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "feedback_id": self.feedback_id,
            "insight_id": self.insight_id,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating.value,
            "comment": self.comment,
            "insight_type": self.insight_type,
            "insight_category": self.insight_category,
            "created_at": self.created_at.isoformat(),
            "time_to_feedback": self.time_to_feedback.total_seconds() if self.time_to_feedback else None,
            "metadata": self.metadata,
        }


@dataclass
class FeedbackSummary:
    """Summary statistics for feedback on insights."""
    total_feedback_count: int
    average_rating: float
    rating_distribution: Dict[int, int]
    feedback_by_type: Dict[str, int]
    feedback_by_category: Dict[str, float]  # Average rating per category
    recent_trend: str  # "improving", "declining", "stable"
    top_issues: List[str]  # Most common negative feedback themes
    period_start: datetime
    period_end: datetime


class FeedbackCollector:
    """
    Collects and manages user feedback on insights.
    
    Supports:
    - Multiple feedback types (usefulness, accuracy, timeliness, etc.)
    - Rating scales (1-5, thumbs up/down)
    - Comments and detailed feedback
    - Aggregation and analysis
    """
    
    def __init__(self):
        """Initialize feedback collector."""
        # In-memory storage (would be database in production)
        self._feedback_store: Dict[str, InsightFeedback] = {}
        self._feedback_by_insight: Dict[str, List[str]] = defaultdict(list)
        self._feedback_by_user: Dict[str, List[str]] = defaultdict(list)
        self._feedback_by_company: Dict[str, List[str]] = defaultdict(list)
        self._feedback_counter = 0
    
    def _generate_feedback_id(self) -> str:
        """Generate unique feedback ID."""
        self._feedback_counter += 1
        return f"FB_{self._feedback_counter:06d}"
    
    def collect_feedback(
        self,
        insight_id: str,
        user_id: str,
        company_id: str,
        feedback_type: FeedbackType,
        rating: FeedbackRating,
        comment: Optional[str] = None,
        insight_type: str = "",
        insight_category: str = "",
        insight_created_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> InsightFeedback:
        """
        Collect feedback on an insight.
        
        Args:
            insight_id: ID of the insight being rated
            user_id: ID of the user providing feedback
            company_id: ID of the company
            feedback_type: Type of feedback (usefulness, accuracy, etc.)
            rating: Rating value
            comment: Optional text comment
            insight_type: Type of insight (risk, opportunity, recommendation)
            insight_category: Category of the insight
            insight_created_at: When the insight was created (for timing analysis)
            metadata: Additional metadata
        
        Returns:
            InsightFeedback object
        """
        feedback_id = self._generate_feedback_id()
        
        # Calculate time to feedback if insight creation time provided
        time_to_feedback = None
        if insight_created_at:
            time_to_feedback = datetime.now() - insight_created_at
        
        feedback = InsightFeedback(
            feedback_id=feedback_id,
            insight_id=insight_id,
            user_id=user_id,
            company_id=company_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            insight_type=insight_type,
            insight_category=insight_category,
            time_to_feedback=time_to_feedback,
            metadata=metadata or {},
        )
        
        # Store feedback
        self._feedback_store[feedback_id] = feedback
        self._feedback_by_insight[insight_id].append(feedback_id)
        self._feedback_by_user[user_id].append(feedback_id)
        self._feedback_by_company[company_id].append(feedback_id)
        
        return feedback
    
    def collect_quick_feedback(
        self,
        insight_id: str,
        user_id: str,
        company_id: str,
        thumbs_up: bool,
        insight_type: str = "",
        insight_category: str = "",
    ) -> InsightFeedback:
        """
        Collect quick thumbs up/down feedback.
        
        Args:
            insight_id: ID of the insight
            user_id: ID of the user
            company_id: ID of the company
            thumbs_up: True for positive, False for negative
            insight_type: Type of insight
            insight_category: Category of insight
        
        Returns:
            InsightFeedback object
        """
        return self.collect_feedback(
            insight_id=insight_id,
            user_id=user_id,
            company_id=company_id,
            feedback_type=FeedbackType.OVERALL,
            rating=FeedbackRating.from_thumbs(thumbs_up),
            insight_type=insight_type,
            insight_category=insight_category,
        )
    
    def get_feedback(self, feedback_id: str) -> Optional[InsightFeedback]:
        """Get feedback by ID."""
        return self._feedback_store.get(feedback_id)
    
    def get_feedback_for_insight(self, insight_id: str) -> List[InsightFeedback]:
        """Get all feedback for a specific insight."""
        feedback_ids = self._feedback_by_insight.get(insight_id, [])
        return [self._feedback_store[fid] for fid in feedback_ids if fid in self._feedback_store]
    
    def get_feedback_for_user(self, user_id: str) -> List[InsightFeedback]:
        """Get all feedback from a specific user."""
        feedback_ids = self._feedback_by_user.get(user_id, [])
        return [self._feedback_store[fid] for fid in feedback_ids if fid in self._feedback_store]
    
    def get_feedback_for_company(self, company_id: str) -> List[InsightFeedback]:
        """Get all feedback from a specific company."""
        feedback_ids = self._feedback_by_company.get(company_id, [])
        return [self._feedback_store[fid] for fid in feedback_ids if fid in self._feedback_store]
    
    def get_recent_feedback(
        self,
        days: int = 7,
        feedback_type: Optional[FeedbackType] = None,
        insight_type: Optional[str] = None,
    ) -> List[InsightFeedback]:
        """
        Get feedback from the last N days.
        
        Args:
            days: Number of days to look back
            feedback_type: Filter by feedback type
            insight_type: Filter by insight type
        
        Returns:
            List of matching feedback
        """
        cutoff = datetime.now() - timedelta(days=days)
        results = []
        
        for feedback in self._feedback_store.values():
            if feedback.created_at < cutoff:
                continue
            if feedback_type and feedback.feedback_type != feedback_type:
                continue
            if insight_type and feedback.insight_type != insight_type:
                continue
            results.append(feedback)
        
        return sorted(results, key=lambda f: f.created_at, reverse=True)
    
    def calculate_average_rating(
        self,
        feedback_list: List[InsightFeedback],
        feedback_type: Optional[FeedbackType] = None,
    ) -> float:
        """
        Calculate average rating from feedback list.
        
        Args:
            feedback_list: List of feedback to analyze
            feedback_type: Filter by type before calculating
        
        Returns:
            Average rating (1-5 scale)
        """
        if feedback_type:
            feedback_list = [f for f in feedback_list if f.feedback_type == feedback_type]
        
        if not feedback_list:
            return 0.0
        
        # Convert ratings to numeric values
        ratings = []
        for fb in feedback_list:
            if fb.rating == FeedbackRating.THUMBS_UP:
                ratings.append(4.0)  # Map to "Good"
            elif fb.rating == FeedbackRating.THUMBS_DOWN:
                ratings.append(2.0)  # Map to "Poor"
            else:
                ratings.append(float(fb.rating.value))
        
        return statistics.mean(ratings) if ratings else 0.0
    
    def get_rating_distribution(
        self,
        feedback_list: List[InsightFeedback],
    ) -> Dict[int, int]:
        """
        Get distribution of ratings.
        
        Args:
            feedback_list: List of feedback to analyze
        
        Returns:
            Dict mapping rating values to counts
        """
        distribution = defaultdict(int)
        
        for fb in feedback_list:
            if fb.rating == FeedbackRating.THUMBS_UP:
                distribution[4] += 1
            elif fb.rating == FeedbackRating.THUMBS_DOWN:
                distribution[2] += 1
            else:
                distribution[fb.rating.value] += 1
        
        return dict(distribution)
    
    def get_feedback_summary(
        self,
        company_id: Optional[str] = None,
        days: int = 30,
    ) -> FeedbackSummary:
        """
        Get summary statistics for feedback.
        
        Args:
            company_id: Filter by company (None for all)
            days: Number of days to analyze
        
        Returns:
            FeedbackSummary with statistics
        """
        # Get relevant feedback
        if company_id:
            all_feedback = self.get_feedback_for_company(company_id)
        else:
            all_feedback = list(self._feedback_store.values())
        
        # Filter by time
        cutoff = datetime.now() - timedelta(days=days)
        feedback_list = [f for f in all_feedback if f.created_at >= cutoff]
        
        if not feedback_list:
            return FeedbackSummary(
                total_feedback_count=0,
                average_rating=0.0,
                rating_distribution={},
                feedback_by_type={},
                feedback_by_category={},
                recent_trend="stable",
                top_issues=[],
                period_start=cutoff,
                period_end=datetime.now(),
            )
        
        # Calculate statistics
        avg_rating = self.calculate_average_rating(feedback_list)
        rating_dist = self.get_rating_distribution(feedback_list)
        
        # Feedback by type
        by_type: Dict[str, int] = defaultdict(int)
        for fb in feedback_list:
            by_type[fb.feedback_type.value] += 1
        
        # Average rating by category
        by_category: Dict[str, List[float]] = defaultdict(list)
        for fb in feedback_list:
            if fb.insight_category:
                if fb.rating == FeedbackRating.THUMBS_UP:
                    by_category[fb.insight_category].append(4.0)
                elif fb.rating == FeedbackRating.THUMBS_DOWN:
                    by_category[fb.insight_category].append(2.0)
                else:
                    by_category[fb.insight_category].append(float(fb.rating.value))
        
        category_averages = {
            cat: statistics.mean(ratings) for cat, ratings in by_category.items()
        }
        
        # Determine trend (compare recent vs older)
        mid_point = cutoff + timedelta(days=days // 2)
        recent = [f for f in feedback_list if f.created_at >= mid_point]
        older = [f for f in feedback_list if f.created_at < mid_point]
        
        recent_avg = self.calculate_average_rating(recent) if recent else 0
        older_avg = self.calculate_average_rating(older) if older else 0
        
        if recent_avg > older_avg + 0.3:
            trend = "improving"
        elif recent_avg < older_avg - 0.3:
            trend = "declining"
        else:
            trend = "stable"
        
        # Find top issues from negative feedback comments
        negative_comments = [
            fb.comment for fb in feedback_list
            if fb.comment and fb.rating.value <= 2
        ]
        
        return FeedbackSummary(
            total_feedback_count=len(feedback_list),
            average_rating=avg_rating,
            rating_distribution=rating_dist,
            feedback_by_type=dict(by_type),
            feedback_by_category=category_averages,
            recent_trend=trend,
            top_issues=negative_comments[:5],  # Top 5 issues
            period_start=cutoff,
            period_end=datetime.now(),
        )
    
    def get_insight_accuracy_rate(
        self,
        insight_type: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 30,
    ) -> float:
        """
        Calculate accuracy rate based on feedback.
        
        Args:
            insight_type: Filter by insight type
            category: Filter by category
            days: Number of days to analyze
        
        Returns:
            Accuracy rate (0-1)
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        accuracy_feedback = [
            fb for fb in self._feedback_store.values()
            if fb.feedback_type == FeedbackType.ACCURACY
            and fb.created_at >= cutoff
        ]
        
        if insight_type:
            accuracy_feedback = [fb for fb in accuracy_feedback if fb.insight_type == insight_type]
        if category:
            accuracy_feedback = [fb for fb in accuracy_feedback if fb.insight_category == category]
        
        if not accuracy_feedback:
            return 0.0
        
        # Count positive accuracy ratings (4 or 5, or thumbs up)
        positive = sum(
            1 for fb in accuracy_feedback
            if fb.rating.value >= 4 or fb.rating == FeedbackRating.THUMBS_UP
        )
        
        return positive / len(accuracy_feedback)
    
    def get_actionability_score(
        self,
        company_id: Optional[str] = None,
        days: int = 30,
    ) -> float:
        """
        Calculate how actionable insights are perceived.
        
        Args:
            company_id: Filter by company
            days: Number of days to analyze
        
        Returns:
            Actionability score (0-1)
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        if company_id:
            all_feedback = self.get_feedback_for_company(company_id)
        else:
            all_feedback = list(self._feedback_store.values())
        
        action_feedback = [
            fb for fb in all_feedback
            if fb.feedback_type == FeedbackType.ACTIONABILITY
            and fb.created_at >= cutoff
        ]
        
        if not action_feedback:
            return 0.0
        
        avg_rating = self.calculate_average_rating(action_feedback)
        return avg_rating / 5.0  # Normalize to 0-1
    
    def export_feedback_data(
        self,
        company_id: Optional[str] = None,
        days: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Export feedback data for analysis or training.
        
        Args:
            company_id: Filter by company
            days: Filter by time period
        
        Returns:
            List of feedback dictionaries
        """
        if company_id:
            feedback_list = self.get_feedback_for_company(company_id)
        else:
            feedback_list = list(self._feedback_store.values())
        
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            feedback_list = [f for f in feedback_list if f.created_at >= cutoff]
        
        return [fb.to_dict() for fb in feedback_list]
    
    def clear_old_feedback(self, days: int = 365) -> int:
        """
        Clear feedback older than specified days.
        
        Args:
            days: Age threshold in days
        
        Returns:
            Number of feedback items cleared
        """
        cutoff = datetime.now() - timedelta(days=days)
        old_ids = [
            fid for fid, fb in self._feedback_store.items()
            if fb.created_at < cutoff
        ]
        
        for fid in old_ids:
            fb = self._feedback_store.pop(fid)
            # Clean up indexes
            if fb.insight_id in self._feedback_by_insight:
                self._feedback_by_insight[fb.insight_id] = [
                    f for f in self._feedback_by_insight[fb.insight_id] if f != fid
                ]
            if fb.user_id in self._feedback_by_user:
                self._feedback_by_user[fb.user_id] = [
                    f for f in self._feedback_by_user[fb.user_id] if f != fid
                ]
            if fb.company_id in self._feedback_by_company:
                self._feedback_by_company[fb.company_id] = [
                    f for f in self._feedback_by_company[fb.company_id] if f != fid
                ]
        
        return len(old_ids)
