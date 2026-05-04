"""
Model Retraining Pipeline

Updates model weights and parameters based on feedback and outcome data.
Implements continuous learning for improved predictions.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
import statistics
import math


class RetrainingStrategy(Enum):
    """Strategy for retraining models."""
    FULL = "full"  # Complete retraining
    INCREMENTAL = "incremental"  # Update existing weights
    ADAPTIVE = "adaptive"  # Small continuous adjustments


class WeightType(Enum):
    """Types of weights that can be adjusted."""
    RISK_SEVERITY = "risk_severity"
    OPPORTUNITY_SCORE = "opportunity_score"
    INDICATOR_IMPORTANCE = "indicator_importance"
    CATEGORY_PRIORITY = "category_priority"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    THRESHOLD = "threshold"


@dataclass
class WeightUpdate:
    """A proposed weight update."""
    weight_type: WeightType
    weight_name: str
    old_value: float
    new_value: float
    reason: str
    confidence: float  # 0-1, how confident we are in this update
    supporting_data_points: int


@dataclass
class RetrainingConfig:
    """Configuration for retraining."""
    strategy: RetrainingStrategy = RetrainingStrategy.INCREMENTAL
    min_data_points: int = 10  # Minimum feedback points before retraining
    learning_rate: float = 0.1  # How much to adjust weights
    max_adjustment: float = 0.2  # Maximum change per retraining
    require_approval: bool = True  # Require human approval for changes
    auto_apply_threshold: float = 0.9  # Auto-apply if confidence above this


@dataclass
class RetrainingResult:
    """Result of a retraining run."""
    retraining_id: str
    strategy: RetrainingStrategy
    started_at: datetime
    completed_at: datetime
    
    # Data used
    feedback_count: int
    outcome_count: int
    data_period_days: int
    
    # Results
    weight_updates: List[WeightUpdate]
    applied_updates: List[str]  # IDs of updates that were applied
    pending_updates: List[str]  # IDs awaiting approval
    rejected_updates: List[str]  # IDs that were rejected
    
    # Metrics
    expected_improvement: float  # Expected accuracy improvement
    previous_accuracy: float
    projected_accuracy: float
    
    # Status
    status: str  # "completed", "pending_approval", "failed"
    error_message: Optional[str] = None


class ModelRetrainer:
    """
    Retrains and updates model weights based on feedback.
    
    Supports:
    - Multiple retraining strategies
    - Weight adjustment for various model components
    - A/B testing of new weights
    - Rollback capability
    """
    
    def __init__(self, config: Optional[RetrainingConfig] = None):
        """Initialize model retrainer."""
        self.config = config or RetrainingConfig()
        
        # Current weights (would be loaded from storage in production)
        self._weights: Dict[str, Dict[str, float]] = {
            "risk_severity": {
                "SUPPLY_CHAIN": 0.8,
                "WORKFORCE": 0.7,
                "INFRASTRUCTURE": 0.75,
                "FINANCIAL": 0.85,
                "MARKET": 0.7,
                "REGULATORY": 0.65,
            },
            "opportunity_score": {
                "MARKET_CAPTURE": 0.8,
                "PRICING_POWER": 0.75,
                "COST_REDUCTION": 0.7,
                "INNOVATION": 0.65,
            },
            "indicator_importance": {
                "OPS_SUPPLY_CHAIN": 0.85,
                "OPS_DEMAND_LEVEL": 0.8,
                "OPS_POWER_RELIABILITY": 0.75,
                "OPS_WORKFORCE_AVAIL": 0.7,
                "OPS_CASH_FLOW": 0.8,
            },
            "category_priority": {
                "SUPPLY_CHAIN": 0.9,
                "FINANCIAL": 0.85,
                "WORKFORCE": 0.7,
                "INFRASTRUCTURE": 0.75,
                "MARKET": 0.7,
            },
            "confidence_calibration": {
                "risk": 1.0,  # Multiplier for risk confidence
                "opportunity": 1.0,
                "timing": 0.9,
            },
            "thresholds": {
                "critical_risk": 0.8,
                "high_risk": 0.6,
                "medium_risk": 0.4,
                "low_risk": 0.2,
                "high_opportunity": 0.7,
                "medium_opportunity": 0.5,
            },
        }
        
        # History of weight changes
        self._weight_history: List[Dict[str, Any]] = []
        
        # Pending updates
        self._pending_updates: Dict[str, WeightUpdate] = {}
        
        # Retraining history
        self._retraining_history: List[RetrainingResult] = []
        
        self._retraining_counter = 0
        self._update_counter = 0
    
    def _generate_retraining_id(self) -> str:
        """Generate unique retraining ID."""
        self._retraining_counter += 1
        return f"RETRAIN_{self._retraining_counter:06d}"
    
    def _generate_update_id(self) -> str:
        """Generate unique update ID."""
        self._update_counter += 1
        return f"UPD_{self._update_counter:06d}"
    
    def get_current_weights(
        self,
        weight_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get current weight values.
        
        Args:
            weight_type: Specific weight type to get (None for all)
        
        Returns:
            Current weights
        """
        if weight_type:
            return self._weights.get(weight_type, {})
        return self._weights.copy()
    
    def get_weight(self, weight_type: str, weight_name: str) -> float:
        """Get a specific weight value."""
        return self._weights.get(weight_type, {}).get(weight_name, 0.5)
    
    def calculate_weight_adjustments(
        self,
        feedback_data: List[Dict[str, Any]],
        outcome_data: List[Dict[str, Any]],
    ) -> List[WeightUpdate]:
        """
        Calculate weight adjustments based on feedback and outcomes.
        
        Args:
            feedback_data: Feedback from FeedbackCollector
            outcome_data: Outcomes from OutcomeTracker
        
        Returns:
            List of proposed weight updates
        """
        updates = []
        
        # Analyze feedback patterns
        feedback_by_category = self._analyze_feedback_by_category(feedback_data)
        
        # Analyze outcome accuracy
        accuracy_by_category = self._analyze_outcome_accuracy(outcome_data)
        
        # Generate updates for categories with poor performance
        for category, avg_rating in feedback_by_category.items():
            if avg_rating < 3.0:  # Below neutral
                current = self.get_weight("category_priority", category)
                adjustment = self._calculate_adjustment(avg_rating, 3.0, 5.0)
                new_value = max(0.1, min(1.0, current + adjustment))
                
                if abs(new_value - current) > 0.01:
                    updates.append(WeightUpdate(
                        weight_type=WeightType.CATEGORY_PRIORITY,
                        weight_name=category,
                        old_value=current,
                        new_value=new_value,
                        reason=f"Low user satisfaction ({avg_rating:.1f}/5.0)",
                        confidence=min(1.0, len(feedback_data) / 50),
                        supporting_data_points=len([
                            f for f in feedback_data
                            if f.get("insight_category") == category
                        ]),
                    ))
        
        # Adjust based on outcome accuracy
        for category, accuracy in accuracy_by_category.items():
            if accuracy < 0.5:  # Less than 50% accurate
                # Adjust confidence calibration
                current = self.get_weight("confidence_calibration", "risk")
                adjustment = (0.5 - accuracy) * self.config.learning_rate
                new_value = max(0.5, min(1.5, current - adjustment))
                
                updates.append(WeightUpdate(
                    weight_type=WeightType.CONFIDENCE_CALIBRATION,
                    weight_name="risk",
                    old_value=current,
                    new_value=new_value,
                    reason=f"Low prediction accuracy for {category} ({accuracy:.1%})",
                    confidence=0.7,
                    supporting_data_points=len([
                        o for o in outcome_data
                        if o.get("prediction", {}).get("event", "").startswith(category)
                    ]),
                ))
        
        # Analyze indicator importance from outcomes
        indicator_accuracy = self._analyze_indicator_accuracy(outcome_data)
        for indicator, accuracy in indicator_accuracy.items():
            current = self.get_weight("indicator_importance", indicator)
            
            if accuracy > 0.8:  # Very accurate predictions
                # Increase importance
                adjustment = (accuracy - 0.8) * self.config.learning_rate
                new_value = min(1.0, current + adjustment)
            elif accuracy < 0.5:  # Poor predictions
                # Decrease importance
                adjustment = (0.5 - accuracy) * self.config.learning_rate
                new_value = max(0.1, current - adjustment)
            else:
                continue
            
            if abs(new_value - current) > 0.01:
                updates.append(WeightUpdate(
                    weight_type=WeightType.INDICATOR_IMPORTANCE,
                    weight_name=indicator,
                    old_value=current,
                    new_value=new_value,
                    reason=f"Indicator prediction accuracy: {accuracy:.1%}",
                    confidence=0.6,
                    supporting_data_points=len([
                        o for o in outcome_data
                        if indicator in o.get("prediction", {}).get("indicators", [])
                    ]),
                ))
        
        # Limit adjustments to max configured value
        for update in updates:
            max_change = self.config.max_adjustment
            change = update.new_value - update.old_value
            if abs(change) > max_change:
                update.new_value = update.old_value + (max_change if change > 0 else -max_change)
        
        return updates
    
    def _analyze_feedback_by_category(
        self,
        feedback_data: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Analyze average feedback rating by category."""
        ratings_by_category: Dict[str, List[float]] = defaultdict(list)
        
        for fb in feedback_data:
            category = fb.get("insight_category", "")
            rating = fb.get("rating", 3)
            if category and isinstance(rating, (int, float)):
                ratings_by_category[category].append(float(rating))
        
        return {
            cat: statistics.mean(ratings) if ratings else 3.0
            for cat, ratings in ratings_by_category.items()
        }
    
    def _analyze_outcome_accuracy(
        self,
        outcome_data: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Analyze prediction accuracy by category."""
        accuracy_by_category: Dict[str, List[float]] = defaultdict(list)
        
        for outcome in outcome_data:
            comparison = outcome.get("comparison", {})
            prediction = outcome.get("prediction", {})
            
            event = prediction.get("event", "")
            accuracy = comparison.get("overall_accuracy", 0)
            
            if event:
                category = event.split("_")[0].upper()
                accuracy_by_category[category].append(accuracy)
        
        return {
            cat: statistics.mean(accs) if accs else 0.5
            for cat, accs in accuracy_by_category.items()
        }
    
    def _analyze_indicator_accuracy(
        self,
        outcome_data: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Analyze accuracy per indicator."""
        accuracy_by_indicator: Dict[str, List[float]] = defaultdict(list)
        
        for outcome in outcome_data:
            comparison = outcome.get("comparison", {})
            indicator_acc = comparison.get("indicator_accuracy", {})
            
            for indicator, acc in indicator_acc.items():
                accuracy_by_indicator[indicator].append(acc)
        
        return {
            ind: statistics.mean(accs) if accs else 0.5
            for ind, accs in accuracy_by_indicator.items()
        }
    
    def _calculate_adjustment(
        self,
        actual: float,
        target_min: float,
        target_max: float,
    ) -> float:
        """Calculate weight adjustment based on deviation from target."""
        # Normalize to 0-1 scale
        normalized = (actual - target_min) / (target_max - target_min)
        normalized = max(0, min(1, normalized))
        
        # Calculate adjustment (negative if below target)
        adjustment = (normalized - 0.5) * 2 * self.config.learning_rate
        
        return adjustment
    
    def run_retraining(
        self,
        feedback_data: List[Dict[str, Any]],
        outcome_data: List[Dict[str, Any]],
        auto_apply: bool = False,
    ) -> RetrainingResult:
        """
        Run a retraining cycle.
        
        Args:
            feedback_data: Feedback from FeedbackCollector
            outcome_data: Outcomes from OutcomeTracker
            auto_apply: Whether to auto-apply high-confidence updates
        
        Returns:
            RetrainingResult with details
        """
        started_at = datetime.now()
        retraining_id = self._generate_retraining_id()
        
        # Check minimum data requirements
        if len(feedback_data) < self.config.min_data_points:
            return RetrainingResult(
                retraining_id=retraining_id,
                strategy=self.config.strategy,
                started_at=started_at,
                completed_at=datetime.now(),
                feedback_count=len(feedback_data),
                outcome_count=len(outcome_data),
                data_period_days=30,
                weight_updates=[],
                applied_updates=[],
                pending_updates=[],
                rejected_updates=[],
                expected_improvement=0,
                previous_accuracy=0,
                projected_accuracy=0,
                status="failed",
                error_message=f"Insufficient data: {len(feedback_data)} < {self.config.min_data_points}",
            )
        
        # Calculate weight adjustments
        updates = self.calculate_weight_adjustments(feedback_data, outcome_data)
        
        applied = []
        pending = []
        rejected = []
        
        for update in updates:
            update_id = self._generate_update_id()
            
            # Apply based on confidence and config
            should_apply = (
                auto_apply and
                update.confidence >= self.config.auto_apply_threshold and
                not self.config.require_approval
            )
            
            if should_apply:
                self._apply_update(update)
                applied.append(update_id)
            elif update.confidence < 0.3:
                # Too uncertain, reject
                rejected.append(update_id)
            else:
                # Pending approval
                self._pending_updates[update_id] = update
                pending.append(update_id)
        
        # Calculate expected improvement
        expected_improvement = self._estimate_improvement(updates)
        
        result = RetrainingResult(
            retraining_id=retraining_id,
            strategy=self.config.strategy,
            started_at=started_at,
            completed_at=datetime.now(),
            feedback_count=len(feedback_data),
            outcome_count=len(outcome_data),
            data_period_days=30,
            weight_updates=updates,
            applied_updates=applied,
            pending_updates=pending,
            rejected_updates=rejected,
            expected_improvement=expected_improvement,
            previous_accuracy=0.7,  # Would come from metrics
            projected_accuracy=0.7 + expected_improvement,
            status="completed" if not pending else "pending_approval",
        )
        
        self._retraining_history.append(result)
        return result
    
    def _apply_update(self, update: WeightUpdate) -> None:
        """Apply a weight update."""
        weight_type = update.weight_type.value
        
        if weight_type not in self._weights:
            self._weights[weight_type] = {}
        
        # Record history
        self._weight_history.append({
            "timestamp": datetime.now().isoformat(),
            "weight_type": weight_type,
            "weight_name": update.weight_name,
            "old_value": update.old_value,
            "new_value": update.new_value,
            "reason": update.reason,
        })
        
        # Apply update
        self._weights[weight_type][update.weight_name] = update.new_value
    
    def approve_update(self, update_id: str) -> bool:
        """Approve and apply a pending update."""
        if update_id not in self._pending_updates:
            return False
        
        update = self._pending_updates.pop(update_id)
        self._apply_update(update)
        return True
    
    def reject_update(self, update_id: str) -> bool:
        """Reject a pending update."""
        if update_id not in self._pending_updates:
            return False
        
        self._pending_updates.pop(update_id)
        return True
    
    def get_pending_updates(self) -> List[Dict[str, Any]]:
        """Get all pending updates awaiting approval."""
        return [
            {
                "update_id": uid,
                "weight_type": update.weight_type.value,
                "weight_name": update.weight_name,
                "old_value": update.old_value,
                "new_value": update.new_value,
                "reason": update.reason,
                "confidence": update.confidence,
                "data_points": update.supporting_data_points,
            }
            for uid, update in self._pending_updates.items()
        ]
    
    def _estimate_improvement(self, updates: List[WeightUpdate]) -> float:
        """Estimate accuracy improvement from updates."""
        if not updates:
            return 0.0
        
        # Simple heuristic: weighted average of expected improvements
        total_impact = 0
        total_confidence = 0
        
        for update in updates:
            change = abs(update.new_value - update.old_value)
            # Estimate impact based on change magnitude and confidence
            impact = change * update.confidence * 0.1  # Max 10% improvement
            total_impact += impact
            total_confidence += update.confidence
        
        if total_confidence == 0:
            return 0.0
        
        return min(0.15, total_impact / len(updates))  # Cap at 15%
    
    def rollback_last_change(self) -> bool:
        """Rollback the most recent weight change."""
        if not self._weight_history:
            return False
        
        last_change = self._weight_history.pop()
        weight_type = last_change["weight_type"]
        weight_name = last_change["weight_name"]
        old_value = last_change["old_value"]
        
        if weight_type in self._weights:
            self._weights[weight_type][weight_name] = old_value
        
        return True
    
    def get_retraining_history(
        self,
        limit: int = 10,
    ) -> List[RetrainingResult]:
        """Get recent retraining history."""
        return self._retraining_history[-limit:]
    
    def get_weight_history(
        self,
        weight_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get weight change history."""
        history = self._weight_history
        
        if weight_type:
            history = [h for h in history if h["weight_type"] == weight_type]
        
        return history[-limit:]
    
    def export_weights(self) -> Dict[str, Any]:
        """Export all current weights for backup/restore."""
        return {
            "weights": self._weights.copy(),
            "exported_at": datetime.now().isoformat(),
            "version": len(self._weight_history),
        }
    
    def import_weights(self, weights_data: Dict[str, Any]) -> bool:
        """Import weights from backup."""
        if "weights" not in weights_data:
            return False
        
        self._weights = weights_data["weights"].copy()
        self._weight_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "import",
            "source_version": weights_data.get("version", "unknown"),
        })
        
        return True
