"""
Outcome Tracking System

Tracks predicted outcomes vs actual outcomes to measure accuracy
and improve future predictions.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics


class OutcomeStatus(Enum):
    """Status of an outcome prediction."""
    PENDING = "pending"  # Waiting for outcome
    CONFIRMED = "confirmed"  # Prediction was correct
    PARTIALLY_CONFIRMED = "partially_confirmed"  # Partially correct
    INCORRECT = "incorrect"  # Prediction was wrong
    EXPIRED = "expired"  # Time window passed, no data
    CANCELLED = "cancelled"  # Event didn't occur


class ImpactLevel(Enum):
    """Predicted/actual impact level."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    @classmethod
    def from_score(cls, score: float) -> "ImpactLevel":
        """Convert score (0-1) to impact level."""
        if score < 0.2:
            return cls.NONE
        elif score < 0.4:
            return cls.LOW
        elif score < 0.6:
            return cls.MEDIUM
        elif score < 0.8:
            return cls.HIGH
        else:
            return cls.CRITICAL


@dataclass
class PredictedOutcome:
    """A predicted outcome from the system."""
    prediction_id: str
    insight_id: str
    company_id: str
    
    # What was predicted
    predicted_event: str  # e.g., "supply_chain_disruption"
    predicted_impact: ImpactLevel
    predicted_impact_score: float  # 0-1
    predicted_timeframe: timedelta  # Expected time to occurrence
    
    # Prediction details
    predicted_indicators: List[str]  # Indicators that would be affected
    predicted_magnitude: Dict[str, float]  # Expected change per indicator
    confidence_level: float  # 0-1
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expected_by: Optional[datetime] = None
    
    # Tracking
    status: OutcomeStatus = OutcomeStatus.PENDING
    
    def __post_init__(self):
        if self.expected_by is None:
            self.expected_by = self.created_at + self.predicted_timeframe


@dataclass
class ActualOutcome:
    """Actual outcome observed after a prediction."""
    outcome_id: str
    prediction_id: str
    company_id: str
    
    # What actually happened
    actual_event: str
    actual_impact: ImpactLevel
    actual_impact_score: float  # 0-1
    occurred_at: datetime
    
    # Actual effects
    actual_indicators: Dict[str, float]  # Actual indicator changes
    
    # Notes
    notes: str = ""
    reported_by: str = ""  # User who confirmed outcome
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OutcomeComparison:
    """Comparison between predicted and actual outcomes."""
    prediction_id: str
    outcome_id: str
    
    # Accuracy metrics
    event_match: bool  # Did the predicted event occur?
    impact_accuracy: float  # How close was impact prediction (0-1)
    timing_accuracy: float  # How close was timing (0-1)
    indicator_accuracy: Dict[str, float]  # Per-indicator accuracy
    
    # Overall score
    overall_accuracy: float  # Weighted combination
    
    # Analysis
    underestimated: bool  # Did we predict lower than actual?
    overestimated: bool  # Did we predict higher than actual?
    timing_error_days: float  # Days off from prediction
    
    # Recommendations
    suggested_adjustments: List[str]


@dataclass
class AccuracyMetrics:
    """Aggregated accuracy metrics over a time period."""
    period_start: datetime
    period_end: datetime
    
    # Counts
    total_predictions: int
    confirmed_predictions: int
    partially_confirmed: int
    incorrect_predictions: int
    pending_predictions: int
    
    # Rates
    accuracy_rate: float  # Confirmed / total resolved
    partial_accuracy_rate: float  # (Confirmed + Partial) / total
    
    # Impact accuracy
    mean_impact_error: float  # Average error in impact prediction
    impact_accuracy_by_level: Dict[str, float]
    
    # Timing accuracy
    mean_timing_error_days: float
    timing_accuracy_rate: float  # Within predicted window
    
    # Category breakdown
    accuracy_by_category: Dict[str, float]
    accuracy_by_insight_type: Dict[str, float]
    
    # Trends
    accuracy_trend: str  # "improving", "declining", "stable"


class OutcomeTracker:
    """
    Tracks predicted outcomes vs actual outcomes.
    
    Provides:
    - Prediction registration
    - Outcome recording
    - Accuracy calculation
    - Performance analytics
    """
    
    def __init__(self):
        """Initialize outcome tracker."""
        self._predictions: Dict[str, PredictedOutcome] = {}
        self._outcomes: Dict[str, ActualOutcome] = {}
        self._comparisons: Dict[str, OutcomeComparison] = {}
        
        # Indexes
        self._predictions_by_company: Dict[str, List[str]] = defaultdict(list)
        self._predictions_by_insight: Dict[str, List[str]] = defaultdict(list)
        self._outcomes_by_prediction: Dict[str, str] = {}
        
        self._prediction_counter = 0
        self._outcome_counter = 0
    
    def _generate_prediction_id(self) -> str:
        """Generate unique prediction ID."""
        self._prediction_counter += 1
        return f"PRED_{self._prediction_counter:06d}"
    
    def _generate_outcome_id(self) -> str:
        """Generate unique outcome ID."""
        self._outcome_counter += 1
        return f"OUT_{self._outcome_counter:06d}"
    
    def register_prediction(
        self,
        insight_id: str,
        company_id: str,
        predicted_event: str,
        predicted_impact: ImpactLevel,
        predicted_impact_score: float,
        predicted_timeframe: timedelta,
        predicted_indicators: List[str],
        predicted_magnitude: Optional[Dict[str, float]] = None,
        confidence_level: float = 0.5,
    ) -> PredictedOutcome:
        """
        Register a prediction to track.
        
        Args:
            insight_id: ID of the source insight
            company_id: Company this prediction applies to
            predicted_event: What event is predicted
            predicted_impact: Expected impact level
            predicted_impact_score: Impact score (0-1)
            predicted_timeframe: When we expect this to occur
            predicted_indicators: Indicators expected to be affected
            predicted_magnitude: Expected change per indicator
            confidence_level: How confident we are (0-1)
        
        Returns:
            PredictedOutcome object
        """
        prediction_id = self._generate_prediction_id()
        
        prediction = PredictedOutcome(
            prediction_id=prediction_id,
            insight_id=insight_id,
            company_id=company_id,
            predicted_event=predicted_event,
            predicted_impact=predicted_impact,
            predicted_impact_score=predicted_impact_score,
            predicted_timeframe=predicted_timeframe,
            predicted_indicators=predicted_indicators,
            predicted_magnitude=predicted_magnitude or {},
            confidence_level=confidence_level,
        )
        
        self._predictions[prediction_id] = prediction
        self._predictions_by_company[company_id].append(prediction_id)
        self._predictions_by_insight[insight_id].append(prediction_id)
        
        return prediction
    
    def record_outcome(
        self,
        prediction_id: str,
        actual_event: str,
        actual_impact: ImpactLevel,
        actual_impact_score: float,
        occurred_at: datetime,
        actual_indicators: Dict[str, float],
        notes: str = "",
        reported_by: str = "",
    ) -> Tuple[ActualOutcome, OutcomeComparison]:
        """
        Record an actual outcome for a prediction.
        
        Args:
            prediction_id: ID of the prediction this outcome is for
            actual_event: What actually happened
            actual_impact: Actual impact level
            actual_impact_score: Actual impact score (0-1)
            occurred_at: When it occurred
            actual_indicators: Actual indicator changes
            notes: Additional notes
            reported_by: User reporting the outcome
        
        Returns:
            Tuple of (ActualOutcome, OutcomeComparison)
        """
        prediction = self._predictions.get(prediction_id)
        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")
        
        outcome_id = self._generate_outcome_id()
        
        outcome = ActualOutcome(
            outcome_id=outcome_id,
            prediction_id=prediction_id,
            company_id=prediction.company_id,
            actual_event=actual_event,
            actual_impact=actual_impact,
            actual_impact_score=actual_impact_score,
            occurred_at=occurred_at,
            actual_indicators=actual_indicators,
            notes=notes,
            reported_by=reported_by,
        )
        
        self._outcomes[outcome_id] = outcome
        self._outcomes_by_prediction[prediction_id] = outcome_id
        
        # Generate comparison
        comparison = self._compare_outcome(prediction, outcome)
        self._comparisons[prediction_id] = comparison
        
        # Update prediction status
        if comparison.overall_accuracy >= 0.8:
            prediction.status = OutcomeStatus.CONFIRMED
        elif comparison.overall_accuracy >= 0.5:
            prediction.status = OutcomeStatus.PARTIALLY_CONFIRMED
        else:
            prediction.status = OutcomeStatus.INCORRECT
        
        return outcome, comparison
    
    def _compare_outcome(
        self,
        prediction: PredictedOutcome,
        outcome: ActualOutcome,
    ) -> OutcomeComparison:
        """Compare a prediction with its actual outcome."""
        # Event match (simple string comparison for now)
        event_match = (
            prediction.predicted_event.lower() == outcome.actual_event.lower()
        )
        
        # Impact accuracy (how close was the impact score)
        impact_diff = abs(prediction.predicted_impact_score - outcome.actual_impact_score)
        impact_accuracy = max(0, 1 - impact_diff)
        
        # Timing accuracy
        timing_diff = abs((outcome.occurred_at - prediction.expected_by).total_seconds())
        expected_window = prediction.predicted_timeframe.total_seconds()
        
        if expected_window > 0:
            timing_accuracy = max(0, 1 - (timing_diff / expected_window))
        else:
            timing_accuracy = 1.0 if timing_diff < 86400 else 0.0  # Within a day
        
        timing_error_days = timing_diff / 86400
        
        # Indicator accuracy
        indicator_accuracy = {}
        for indicator in prediction.predicted_indicators:
            if indicator in prediction.predicted_magnitude and indicator in outcome.actual_indicators:
                pred_change = prediction.predicted_magnitude[indicator]
                actual_change = outcome.actual_indicators[indicator]
                diff = abs(pred_change - actual_change)
                indicator_accuracy[indicator] = max(0, 1 - diff)
            elif indicator in outcome.actual_indicators:
                indicator_accuracy[indicator] = 0.5  # Indicator affected but magnitude not predicted
            else:
                indicator_accuracy[indicator] = 0.0  # Indicator not affected
        
        # Overall accuracy (weighted)
        overall_accuracy = (
            0.3 * (1.0 if event_match else 0.0) +
            0.4 * impact_accuracy +
            0.2 * timing_accuracy +
            0.1 * (statistics.mean(indicator_accuracy.values()) if indicator_accuracy else 0.5)
        )
        
        # Under/over estimation
        underestimated = outcome.actual_impact_score > prediction.predicted_impact_score + 0.1
        overestimated = outcome.actual_impact_score < prediction.predicted_impact_score - 0.1
        
        # Suggested adjustments
        adjustments = []
        if underestimated:
            adjustments.append("Increase sensitivity for this event type")
        if overestimated:
            adjustments.append("Decrease sensitivity for this event type")
        if timing_error_days > 3:
            adjustments.append("Adjust timing predictions for this category")
        if not event_match:
            adjustments.append("Review event classification rules")
        
        return OutcomeComparison(
            prediction_id=prediction.prediction_id,
            outcome_id=outcome.outcome_id,
            event_match=event_match,
            impact_accuracy=impact_accuracy,
            timing_accuracy=timing_accuracy,
            indicator_accuracy=indicator_accuracy,
            overall_accuracy=overall_accuracy,
            underestimated=underestimated,
            overestimated=overestimated,
            timing_error_days=timing_error_days,
            suggested_adjustments=adjustments,
        )
    
    def get_prediction(self, prediction_id: str) -> Optional[PredictedOutcome]:
        """Get a prediction by ID."""
        return self._predictions.get(prediction_id)
    
    def get_outcome(self, outcome_id: str) -> Optional[ActualOutcome]:
        """Get an outcome by ID."""
        return self._outcomes.get(outcome_id)
    
    def get_comparison(self, prediction_id: str) -> Optional[OutcomeComparison]:
        """Get comparison for a prediction."""
        return self._comparisons.get(prediction_id)
    
    def get_pending_predictions(
        self,
        company_id: Optional[str] = None,
        days_old: int = 30,
    ) -> List[PredictedOutcome]:
        """
        Get pending predictions that need outcome tracking.
        
        Args:
            company_id: Filter by company
            days_old: Max age of predictions to return
        
        Returns:
            List of pending predictions
        """
        cutoff = datetime.now() - timedelta(days=days_old)
        
        if company_id:
            pred_ids = self._predictions_by_company.get(company_id, [])
            predictions = [self._predictions[pid] for pid in pred_ids]
        else:
            predictions = list(self._predictions.values())
        
        return [
            p for p in predictions
            if p.status == OutcomeStatus.PENDING
            and p.created_at >= cutoff
        ]
    
    def mark_expired(self, prediction_id: str) -> None:
        """Mark a prediction as expired (time window passed)."""
        prediction = self._predictions.get(prediction_id)
        if prediction:
            prediction.status = OutcomeStatus.EXPIRED
    
    def mark_cancelled(self, prediction_id: str) -> None:
        """Mark a prediction as cancelled (event didn't occur)."""
        prediction = self._predictions.get(prediction_id)
        if prediction:
            prediction.status = OutcomeStatus.CANCELLED
    
    def check_and_expire_old_predictions(self, grace_days: int = 7) -> int:
        """
        Check for predictions past their window and mark expired.
        
        Args:
            grace_days: Extra days after expected_by before expiring
        
        Returns:
            Number of predictions expired
        """
        now = datetime.now()
        expired_count = 0
        
        for prediction in self._predictions.values():
            if prediction.status != OutcomeStatus.PENDING:
                continue
            
            expiry_date = prediction.expected_by + timedelta(days=grace_days)
            if now > expiry_date:
                prediction.status = OutcomeStatus.EXPIRED
                expired_count += 1
        
        return expired_count
    
    def calculate_accuracy_metrics(
        self,
        company_id: Optional[str] = None,
        days: int = 30,
    ) -> AccuracyMetrics:
        """
        Calculate accuracy metrics over a time period.
        
        Args:
            company_id: Filter by company
            days: Number of days to analyze
        
        Returns:
            AccuracyMetrics object
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Get relevant predictions
        if company_id:
            pred_ids = self._predictions_by_company.get(company_id, [])
            predictions = [self._predictions[pid] for pid in pred_ids]
        else:
            predictions = list(self._predictions.values())
        
        predictions = [p for p in predictions if p.created_at >= cutoff]
        
        # Count by status
        total = len(predictions)
        confirmed = sum(1 for p in predictions if p.status == OutcomeStatus.CONFIRMED)
        partial = sum(1 for p in predictions if p.status == OutcomeStatus.PARTIALLY_CONFIRMED)
        incorrect = sum(1 for p in predictions if p.status == OutcomeStatus.INCORRECT)
        pending = sum(1 for p in predictions if p.status == OutcomeStatus.PENDING)
        
        resolved = confirmed + partial + incorrect
        
        # Calculate rates
        accuracy_rate = confirmed / resolved if resolved > 0 else 0
        partial_rate = (confirmed + partial) / resolved if resolved > 0 else 0
        
        # Get comparisons for detailed metrics
        comparisons = [
            self._comparisons[p.prediction_id]
            for p in predictions
            if p.prediction_id in self._comparisons
        ]
        
        # Impact accuracy
        if comparisons:
            mean_impact_error = statistics.mean(
                1 - c.impact_accuracy for c in comparisons
            )
            mean_timing_error = statistics.mean(c.timing_error_days for c in comparisons)
            timing_accuracy_rate = sum(
                1 for c in comparisons if c.timing_accuracy >= 0.5
            ) / len(comparisons)
        else:
            mean_impact_error = 0
            mean_timing_error = 0
            timing_accuracy_rate = 0
        
        # Accuracy by impact level
        accuracy_by_level: Dict[str, List[float]] = defaultdict(list)
        for pred in predictions:
            if pred.prediction_id in self._comparisons:
                comp = self._comparisons[pred.prediction_id]
                accuracy_by_level[pred.predicted_impact.name].append(comp.overall_accuracy)
        
        level_averages = {
            level: statistics.mean(accs) if accs else 0
            for level, accs in accuracy_by_level.items()
        }
        
        # Accuracy by category (using predicted_event as proxy)
        accuracy_by_category: Dict[str, List[float]] = defaultdict(list)
        for pred in predictions:
            if pred.prediction_id in self._comparisons:
                comp = self._comparisons[pred.prediction_id]
                category = pred.predicted_event.split("_")[0]  # First part as category
                accuracy_by_category[category].append(comp.overall_accuracy)
        
        category_averages = {
            cat: statistics.mean(accs) if accs else 0
            for cat, accs in accuracy_by_category.items()
        }
        
        # Calculate trend (compare first half vs second half)
        mid_point = cutoff + timedelta(days=days // 2)
        recent_preds = [p for p in predictions if p.created_at >= mid_point]
        older_preds = [p for p in predictions if p.created_at < mid_point]
        
        recent_resolved = [
            p for p in recent_preds
            if p.status in [OutcomeStatus.CONFIRMED, OutcomeStatus.PARTIALLY_CONFIRMED, OutcomeStatus.INCORRECT]
        ]
        older_resolved = [
            p for p in older_preds
            if p.status in [OutcomeStatus.CONFIRMED, OutcomeStatus.PARTIALLY_CONFIRMED, OutcomeStatus.INCORRECT]
        ]
        
        if recent_resolved and older_resolved:
            recent_acc = sum(
                1 for p in recent_resolved if p.status == OutcomeStatus.CONFIRMED
            ) / len(recent_resolved)
            older_acc = sum(
                1 for p in older_resolved if p.status == OutcomeStatus.CONFIRMED
            ) / len(older_resolved)
            
            if recent_acc > older_acc + 0.1:
                trend = "improving"
            elif recent_acc < older_acc - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return AccuracyMetrics(
            period_start=cutoff,
            period_end=datetime.now(),
            total_predictions=total,
            confirmed_predictions=confirmed,
            partially_confirmed=partial,
            incorrect_predictions=incorrect,
            pending_predictions=pending,
            accuracy_rate=accuracy_rate,
            partial_accuracy_rate=partial_rate,
            mean_impact_error=mean_impact_error,
            impact_accuracy_by_level=level_averages,
            mean_timing_error_days=mean_timing_error,
            timing_accuracy_rate=timing_accuracy_rate,
            accuracy_by_category=category_averages,
            accuracy_by_insight_type={},  # Would need insight type tracking
            accuracy_trend=trend,
        )
    
    def get_improvement_suggestions(
        self,
        company_id: Optional[str] = None,
        days: int = 30,
    ) -> List[str]:
        """
        Get suggestions for improving predictions.
        
        Args:
            company_id: Filter by company
            days: Analysis period
        
        Returns:
            List of improvement suggestions
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        if company_id:
            pred_ids = self._predictions_by_company.get(company_id, [])
        else:
            pred_ids = list(self._predictions.keys())
        
        suggestions = []
        underestimate_count = 0
        overestimate_count = 0
        timing_issues = 0
        
        for pred_id in pred_ids:
            if pred_id not in self._comparisons:
                continue
            
            pred = self._predictions[pred_id]
            if pred.created_at < cutoff:
                continue
            
            comp = self._comparisons[pred_id]
            
            if comp.underestimated:
                underestimate_count += 1
            if comp.overestimated:
                overestimate_count += 1
            if comp.timing_error_days > 3:
                timing_issues += 1
        
        total_compared = len([
            p for p in pred_ids
            if p in self._comparisons and self._predictions[p].created_at >= cutoff
        ])
        
        if total_compared > 0:
            if underestimate_count / total_compared > 0.3:
                suggestions.append(
                    "System tends to underestimate impact - consider increasing base impact scores"
                )
            if overestimate_count / total_compared > 0.3:
                suggestions.append(
                    "System tends to overestimate impact - consider decreasing sensitivity"
                )
            if timing_issues / total_compared > 0.3:
                suggestions.append(
                    "Timing predictions often off - review timeframe estimation logic"
                )
        
        return suggestions
    
    def export_training_data(
        self,
        company_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Export prediction/outcome pairs for model training.
        
        Args:
            company_id: Filter by company
        
        Returns:
            List of training data dictionaries
        """
        training_data = []
        
        for pred_id, comparison in self._comparisons.items():
            prediction = self._predictions.get(pred_id)
            outcome_id = self._outcomes_by_prediction.get(pred_id)
            outcome = self._outcomes.get(outcome_id) if outcome_id else None
            
            if not prediction or not outcome:
                continue
            
            if company_id and prediction.company_id != company_id:
                continue
            
            training_data.append({
                "prediction": {
                    "event": prediction.predicted_event,
                    "impact_score": prediction.predicted_impact_score,
                    "impact_level": prediction.predicted_impact.name,
                    "timeframe_hours": prediction.predicted_timeframe.total_seconds() / 3600,
                    "confidence": prediction.confidence_level,
                    "indicators": prediction.predicted_indicators,
                    "magnitude": prediction.predicted_magnitude,
                },
                "outcome": {
                    "event": outcome.actual_event,
                    "impact_score": outcome.actual_impact_score,
                    "impact_level": outcome.actual_impact.name,
                    "indicators": outcome.actual_indicators,
                },
                "comparison": {
                    "event_match": comparison.event_match,
                    "impact_accuracy": comparison.impact_accuracy,
                    "timing_accuracy": comparison.timing_accuracy,
                    "overall_accuracy": comparison.overall_accuracy,
                    "timing_error_days": comparison.timing_error_days,
                },
            })
        
        return training_data
