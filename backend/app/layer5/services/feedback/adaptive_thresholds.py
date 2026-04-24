"""
Adaptive Threshold Management

Self-adjusting thresholds for risk/opportunity detection based on
feedback, outcomes, and company-specific patterns.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import statistics
import math


class ThresholdCategory(Enum):
    """Categories of thresholds."""
    RISK_SEVERITY = "risk_severity"
    OPPORTUNITY_SCORE = "opportunity_score"
    ALERT_TRIGGER = "alert_trigger"
    INDICATOR_CRITICAL = "indicator_critical"
    INDICATOR_WARNING = "indicator_warning"


class AdjustmentReason(Enum):
    """Reasons for threshold adjustment."""
    HIGH_FALSE_POSITIVE = "high_false_positive"  # Too many false alerts
    HIGH_FALSE_NEGATIVE = "high_false_negative"  # Missing real events
    USER_PREFERENCE = "user_preference"  # User requested adjustment
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    SEASONAL_ADJUSTMENT = "seasonal_adjustment"
    COMPANY_CALIBRATION = "company_calibration"


@dataclass
class ThresholdConfig:
    """Configuration for a threshold."""
    threshold_id: str
    category: ThresholdCategory
    name: str
    
    # Values
    current_value: float
    min_value: float
    max_value: float
    default_value: float
    
    # Adjustment settings
    auto_adjust: bool = True
    adjustment_rate: float = 0.05  # Max change per adjustment
    cooldown_hours: int = 24  # Hours between adjustments
    
    # Scope
    company_id: Optional[str] = None  # None = global
    industry: Optional[str] = None
    
    # Tracking
    last_adjusted: Optional[datetime] = None
    adjustment_count: int = 0
    
    def can_adjust(self) -> bool:
        """Check if threshold can be adjusted (cooldown passed)."""
        if not self.auto_adjust:
            return False
        if self.last_adjusted is None:
            return True
        
        cooldown = timedelta(hours=self.cooldown_hours)
        return datetime.now() >= self.last_adjusted + cooldown


@dataclass
class ThresholdAdjustment:
    """Record of a threshold adjustment."""
    adjustment_id: str
    threshold_id: str
    
    # Change
    old_value: float
    new_value: float
    reason: AdjustmentReason
    
    # Context
    supporting_metrics: Dict[str, float]
    confidence: float
    
    # Timing
    adjusted_at: datetime = field(default_factory=datetime.now)
    adjusted_by: str = "system"  # "system" or user ID


@dataclass
class ThresholdHistory:
    """Historical record of threshold values."""
    threshold_id: str
    values: List[Tuple[datetime, float]]
    adjustments: List[ThresholdAdjustment]
    
    def get_trend(self, days: int = 30) -> str:
        """Get trend direction over time period."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [v for t, v in self.values if t >= cutoff]
        
        if len(recent) < 2:
            return "stable"
        
        first_half = recent[:len(recent)//2]
        second_half = recent[len(recent)//2:]
        
        avg_first = statistics.mean(first_half) if first_half else 0
        avg_second = statistics.mean(second_half) if second_half else 0
        
        if avg_second > avg_first + 0.02:
            return "increasing"
        elif avg_second < avg_first - 0.02:
            return "decreasing"
        return "stable"


class AdaptiveThresholdManager:
    """
    Manages adaptive thresholds that self-adjust based on performance.
    
    Features:
    - Automatic threshold adjustment based on false positive/negative rates
    - Company-specific threshold customization
    - Seasonal adjustment support
    - Manual override capability
    - Threshold history and auditing
    """
    
    def __init__(self):
        """Initialize adaptive threshold manager."""
        # Counters must be initialized first
        self._threshold_counter = 0
        self._adjustment_counter = 0
        
        # Default thresholds
        self._thresholds: Dict[str, ThresholdConfig] = {}
        self._histories: Dict[str, ThresholdHistory] = {}
        
        # Company-specific overrides
        self._company_thresholds: Dict[str, Dict[str, ThresholdConfig]] = defaultdict(dict)
        
        # Initialize default thresholds
        self._initialize_defaults()
    
    def _generate_threshold_id(self) -> str:
        """Generate unique threshold ID."""
        self._threshold_counter += 1
        return f"THRESH_{self._threshold_counter:06d}"
    
    def _generate_adjustment_id(self) -> str:
        """Generate unique adjustment ID."""
        self._adjustment_counter += 1
        return f"ADJ_{self._adjustment_counter:06d}"
    
    def _initialize_defaults(self) -> None:
        """Initialize default threshold configurations."""
        defaults = [
            # Risk severity thresholds
            ("critical_risk", ThresholdCategory.RISK_SEVERITY, 0.8, 0.6, 0.95),
            ("high_risk", ThresholdCategory.RISK_SEVERITY, 0.6, 0.4, 0.8),
            ("medium_risk", ThresholdCategory.RISK_SEVERITY, 0.4, 0.2, 0.6),
            ("low_risk", ThresholdCategory.RISK_SEVERITY, 0.2, 0.05, 0.4),
            
            # Opportunity thresholds
            ("high_opportunity", ThresholdCategory.OPPORTUNITY_SCORE, 0.7, 0.5, 0.9),
            ("medium_opportunity", ThresholdCategory.OPPORTUNITY_SCORE, 0.5, 0.3, 0.7),
            
            # Alert triggers
            ("immediate_alert", ThresholdCategory.ALERT_TRIGGER, 0.85, 0.7, 0.95),
            ("daily_digest", ThresholdCategory.ALERT_TRIGGER, 0.5, 0.3, 0.7),
            
            # Indicator thresholds
            ("supply_chain_critical", ThresholdCategory.INDICATOR_CRITICAL, 0.3, 0.1, 0.5),
            ("power_critical", ThresholdCategory.INDICATOR_CRITICAL, 0.2, 0.1, 0.4),
            ("workforce_warning", ThresholdCategory.INDICATOR_WARNING, 0.5, 0.3, 0.7),
            ("cash_flow_warning", ThresholdCategory.INDICATOR_WARNING, 0.4, 0.2, 0.6),
        ]
        
        for name, category, default, min_val, max_val in defaults:
            threshold_id = self._generate_threshold_id()
            config = ThresholdConfig(
                threshold_id=threshold_id,
                category=category,
                name=name,
                current_value=default,
                min_value=min_val,
                max_value=max_val,
                default_value=default,
            )
            self._thresholds[name] = config
            self._histories[name] = ThresholdHistory(
                threshold_id=threshold_id,
                values=[(datetime.now(), default)],
                adjustments=[],
            )
    
    def get_threshold(
        self,
        name: str,
        company_id: Optional[str] = None,
    ) -> float:
        """
        Get threshold value.
        
        Args:
            name: Threshold name
            company_id: Company for company-specific threshold
        
        Returns:
            Threshold value
        """
        # Check company-specific first
        if company_id and company_id in self._company_thresholds:
            company_thresh = self._company_thresholds[company_id].get(name)
            if company_thresh:
                return company_thresh.current_value
        
        # Fall back to global
        if name in self._thresholds:
            return self._thresholds[name].current_value
        
        return 0.5  # Default fallback
    
    def get_threshold_config(
        self,
        name: str,
        company_id: Optional[str] = None,
    ) -> Optional[ThresholdConfig]:
        """Get threshold configuration."""
        if company_id and company_id in self._company_thresholds:
            company_thresh = self._company_thresholds[company_id].get(name)
            if company_thresh:
                return company_thresh
        
        return self._thresholds.get(name)
    
    def set_threshold(
        self,
        name: str,
        value: float,
        company_id: Optional[str] = None,
        reason: AdjustmentReason = AdjustmentReason.USER_PREFERENCE,
        adjusted_by: str = "system",
    ) -> ThresholdAdjustment:
        """
        Manually set a threshold value.
        
        Args:
            name: Threshold name
            value: New value
            company_id: Company for company-specific threshold
            reason: Reason for adjustment
            adjusted_by: Who made the change
        
        Returns:
            ThresholdAdjustment record
        """
        config = self.get_threshold_config(name, company_id)
        
        if config is None:
            # Create new company-specific threshold
            if company_id:
                global_config = self._thresholds.get(name)
                if global_config:
                    config = ThresholdConfig(
                        threshold_id=self._generate_threshold_id(),
                        category=global_config.category,
                        name=name,
                        current_value=global_config.current_value,
                        min_value=global_config.min_value,
                        max_value=global_config.max_value,
                        default_value=global_config.default_value,
                        company_id=company_id,
                    )
                    self._company_thresholds[company_id][name] = config
                else:
                    raise ValueError(f"Unknown threshold: {name}")
            else:
                raise ValueError(f"Unknown threshold: {name}")
        
        # Clamp value to valid range
        value = max(config.min_value, min(config.max_value, value))
        
        old_value = config.current_value
        
        # Create adjustment record
        adjustment = ThresholdAdjustment(
            adjustment_id=self._generate_adjustment_id(),
            threshold_id=config.threshold_id,
            old_value=old_value,
            new_value=value,
            reason=reason,
            supporting_metrics={},
            confidence=1.0,  # Manual = full confidence
            adjusted_by=adjusted_by,
        )
        
        # Apply change
        config.current_value = value
        config.last_adjusted = datetime.now()
        config.adjustment_count += 1
        
        # Record in history
        history_key = f"{company_id}_{name}" if company_id else name
        if history_key not in self._histories:
            self._histories[history_key] = ThresholdHistory(
                threshold_id=config.threshold_id,
                values=[],
                adjustments=[],
            )
        
        self._histories[history_key].values.append((datetime.now(), value))
        self._histories[history_key].adjustments.append(adjustment)
        
        return adjustment
    
    def auto_adjust_threshold(
        self,
        name: str,
        false_positive_rate: float,
        false_negative_rate: float,
        company_id: Optional[str] = None,
    ) -> Optional[ThresholdAdjustment]:
        """
        Automatically adjust threshold based on performance metrics.
        
        Args:
            name: Threshold name
            false_positive_rate: Rate of false positives (0-1)
            false_negative_rate: Rate of false negatives (0-1)
            company_id: Company for company-specific threshold
        
        Returns:
            ThresholdAdjustment if adjustment made, None otherwise
        """
        config = self.get_threshold_config(name, company_id)
        
        if config is None or not config.can_adjust():
            return None
        
        old_value = config.current_value
        new_value = old_value
        reason = None
        
        # Adjust based on false positive/negative rates
        if false_positive_rate > 0.3:
            # Too many false alerts - raise threshold
            adjustment = min(config.adjustment_rate, false_positive_rate * 0.1)
            new_value = min(config.max_value, old_value + adjustment)
            reason = AdjustmentReason.HIGH_FALSE_POSITIVE
        elif false_negative_rate > 0.3:
            # Missing too many events - lower threshold
            adjustment = min(config.adjustment_rate, false_negative_rate * 0.1)
            new_value = max(config.min_value, old_value - adjustment)
            reason = AdjustmentReason.HIGH_FALSE_NEGATIVE
        
        if reason is None or abs(new_value - old_value) < 0.01:
            return None
        
        # Calculate confidence based on sample size (would need more context)
        confidence = min(1.0, (false_positive_rate + false_negative_rate) * 2)
        
        # Create adjustment
        adjustment = ThresholdAdjustment(
            adjustment_id=self._generate_adjustment_id(),
            threshold_id=config.threshold_id,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            supporting_metrics={
                "false_positive_rate": false_positive_rate,
                "false_negative_rate": false_negative_rate,
            },
            confidence=confidence,
        )
        
        # Apply if company-specific or global
        if company_id:
            if company_id not in self._company_thresholds:
                self._company_thresholds[company_id] = {}
            
            if name not in self._company_thresholds[company_id]:
                # Create company-specific copy
                self._company_thresholds[company_id][name] = ThresholdConfig(
                    threshold_id=self._generate_threshold_id(),
                    category=config.category,
                    name=name,
                    current_value=old_value,
                    min_value=config.min_value,
                    max_value=config.max_value,
                    default_value=config.default_value,
                    company_id=company_id,
                )
            
            target_config = self._company_thresholds[company_id][name]
        else:
            target_config = config
        
        target_config.current_value = new_value
        target_config.last_adjusted = datetime.now()
        target_config.adjustment_count += 1
        
        # Record in history
        history_key = f"{company_id}_{name}" if company_id else name
        if history_key not in self._histories:
            self._histories[history_key] = ThresholdHistory(
                threshold_id=target_config.threshold_id,
                values=[],
                adjustments=[],
            )
        
        self._histories[history_key].values.append((datetime.now(), new_value))
        self._histories[history_key].adjustments.append(adjustment)
        
        return adjustment
    
    def batch_adjust(
        self,
        performance_data: Dict[str, Dict[str, float]],
        company_id: Optional[str] = None,
    ) -> List[ThresholdAdjustment]:
        """
        Adjust multiple thresholds based on performance data.
        
        Args:
            performance_data: Dict mapping threshold names to {fp_rate, fn_rate}
            company_id: Company for company-specific thresholds
        
        Returns:
            List of adjustments made
        """
        adjustments = []
        
        for name, metrics in performance_data.items():
            fp_rate = metrics.get("false_positive_rate", 0)
            fn_rate = metrics.get("false_negative_rate", 0)
            
            adjustment = self.auto_adjust_threshold(
                name=name,
                false_positive_rate=fp_rate,
                false_negative_rate=fn_rate,
                company_id=company_id,
            )
            
            if adjustment:
                adjustments.append(adjustment)
        
        return adjustments
    
    def reset_to_default(
        self,
        name: str,
        company_id: Optional[str] = None,
    ) -> ThresholdAdjustment:
        """
        Reset a threshold to its default value.
        
        Args:
            name: Threshold name
            company_id: Company for company-specific threshold
        
        Returns:
            ThresholdAdjustment record
        """
        config = self.get_threshold_config(name, company_id)
        
        if config is None:
            raise ValueError(f"Unknown threshold: {name}")
        
        return self.set_threshold(
            name=name,
            value=config.default_value,
            company_id=company_id,
            reason=AdjustmentReason.USER_PREFERENCE,
            adjusted_by="system_reset",
        )
    
    def get_all_thresholds(
        self,
        company_id: Optional[str] = None,
        category: Optional[ThresholdCategory] = None,
    ) -> List[ThresholdConfig]:
        """
        Get all threshold configurations.
        
        Args:
            company_id: Company for company-specific thresholds
            category: Filter by category
        
        Returns:
            List of threshold configurations
        """
        results = []
        
        # Start with global thresholds
        for name, config in self._thresholds.items():
            if category and config.category != category:
                continue
            
            # Check for company override
            if company_id and company_id in self._company_thresholds:
                company_config = self._company_thresholds[company_id].get(name)
                if company_config:
                    results.append(company_config)
                    continue
            
            results.append(config)
        
        return results
    
    def get_threshold_history(
        self,
        name: str,
        company_id: Optional[str] = None,
        days: int = 30,
    ) -> ThresholdHistory:
        """
        Get history of threshold changes.
        
        Args:
            name: Threshold name
            company_id: Company for company-specific threshold
            days: Number of days of history
        
        Returns:
            ThresholdHistory object
        """
        history_key = f"{company_id}_{name}" if company_id else name
        
        if history_key not in self._histories:
            # Return empty history
            config = self.get_threshold_config(name, company_id)
            return ThresholdHistory(
                threshold_id=config.threshold_id if config else "unknown",
                values=[],
                adjustments=[],
            )
        
        history = self._histories[history_key]
        
        # Filter by time
        cutoff = datetime.now() - timedelta(days=days)
        
        return ThresholdHistory(
            threshold_id=history.threshold_id,
            values=[(t, v) for t, v in history.values if t >= cutoff],
            adjustments=[a for a in history.adjustments if a.adjusted_at >= cutoff],
        )
    
    def get_adjustment_recommendations(
        self,
        feedback_summary: Dict[str, Any],
        accuracy_metrics: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations for threshold adjustments.
        
        Args:
            feedback_summary: Summary from FeedbackCollector
            accuracy_metrics: Metrics from OutcomeTracker
        
        Returns:
            List of recommended adjustments
        """
        recommendations = []
        
        # Analyze false positive/negative patterns
        accuracy_rate = accuracy_metrics.get("accuracy_rate", 0.7)
        
        if accuracy_rate < 0.5:
            # Low accuracy - recommend threshold adjustments
            recommendations.append({
                "threshold": "critical_risk",
                "current": self.get_threshold("critical_risk"),
                "recommended": self.get_threshold("critical_risk") + 0.05,
                "reason": f"Low accuracy rate ({accuracy_rate:.1%}) suggests too many false positives",
                "confidence": 0.7,
            })
        
        # Check feedback patterns
        avg_rating = feedback_summary.get("average_rating", 3.0)
        
        if avg_rating < 2.5:
            # Low satisfaction - might be too noisy
            recommendations.append({
                "threshold": "daily_digest",
                "current": self.get_threshold("daily_digest"),
                "recommended": self.get_threshold("daily_digest") + 0.1,
                "reason": f"Low user satisfaction ({avg_rating:.1f}/5.0) - reduce alert noise",
                "confidence": 0.6,
            })
        
        return recommendations
    
    def apply_seasonal_adjustment(
        self,
        season: str,
        adjustments: Dict[str, float],
    ) -> List[ThresholdAdjustment]:
        """
        Apply seasonal adjustments to thresholds.
        
        Args:
            season: Season name (e.g., "monsoon", "holiday", "election")
            adjustments: Dict mapping threshold names to adjustment factors
        
        Returns:
            List of adjustments made
        """
        results = []
        
        for name, factor in adjustments.items():
            config = self.get_threshold_config(name)
            if config is None:
                continue
            
            new_value = config.current_value * factor
            new_value = max(config.min_value, min(config.max_value, new_value))
            
            adjustment = ThresholdAdjustment(
                adjustment_id=self._generate_adjustment_id(),
                threshold_id=config.threshold_id,
                old_value=config.current_value,
                new_value=new_value,
                reason=AdjustmentReason.SEASONAL_ADJUSTMENT,
                supporting_metrics={"season": season, "factor": factor},
                confidence=0.8,
            )
            
            config.current_value = new_value
            config.last_adjusted = datetime.now()
            config.adjustment_count += 1
            
            if name in self._histories:
                self._histories[name].values.append((datetime.now(), new_value))
                self._histories[name].adjustments.append(adjustment)
            
            results.append(adjustment)
        
        return results
    
    def export_thresholds(
        self,
        company_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Export threshold configurations for backup."""
        thresholds = self.get_all_thresholds(company_id)
        
        return {
            "company_id": company_id,
            "exported_at": datetime.now().isoformat(),
            "thresholds": [
                {
                    "name": t.name,
                    "category": t.category.value,
                    "current_value": t.current_value,
                    "default_value": t.default_value,
                    "min_value": t.min_value,
                    "max_value": t.max_value,
                    "adjustment_count": t.adjustment_count,
                }
                for t in thresholds
            ],
        }
    
    def import_thresholds(
        self,
        data: Dict[str, Any],
        company_id: Optional[str] = None,
    ) -> int:
        """
        Import threshold configurations.
        
        Args:
            data: Exported threshold data
            company_id: Company to import for
        
        Returns:
            Number of thresholds imported
        """
        count = 0
        
        for thresh_data in data.get("thresholds", []):
            name = thresh_data.get("name")
            value = thresh_data.get("current_value")
            
            if name and value is not None:
                try:
                    self.set_threshold(
                        name=name,
                        value=value,
                        company_id=company_id,
                        reason=AdjustmentReason.USER_PREFERENCE,
                        adjusted_by="import",
                    )
                    count += 1
                except ValueError:
                    continue
        
        return count
