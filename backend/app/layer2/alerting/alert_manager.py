"""
Alert Manager - Centralized alert generation and management.

Handles:
- Threshold breach detection
- Anomaly alerts
- Rapid change alerts
- Alert aggregation and deduplication
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts"""
    THRESHOLD_BREACH = "threshold_breach"
    ANOMALY_DETECTED = "anomaly_detected"
    RAPID_CHANGE = "rapid_change"
    TREND_REVERSAL = "trend_reversal"
    CORRELATION_BREAK = "correlation_break"


@dataclass
class Alert:
    """Represents a system alert"""
    alert_id: str
    indicator_id: str
    indicator_name: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    current_value: float
    threshold_value: Optional[float] = None
    change_percent: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "indicator_id": self.indicator_id,
            "indicator_name": self.indicator_name,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "change_percent": self.change_percent,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
            "metadata": self.metadata
        }


@dataclass
class ThresholdConfig:
    """Threshold configuration for an indicator"""
    indicator_id: str
    warning_high: float = 80.0
    critical_high: float = 90.0
    warning_low: float = 20.0
    critical_low: float = 10.0
    rapid_change_threshold: float = 20.0  # % change in 24h


class AlertManager:
    """
    Centralized alert management system.
    
    Generates alerts based on:
    - Threshold breaches
    - Anomaly detection
    - Rapid changes
    - Trend reversals
    """
    
    # Default thresholds
    DEFAULT_THRESHOLDS = {
        "warning_high": 75.0,
        "critical_high": 90.0,
        "warning_low": 25.0,
        "critical_low": 10.0,
        "rapid_change": 25.0  # 25% change triggers alert
    }
    
    def __init__(self):
        self._alerts: List[Alert] = []
        self._thresholds: Dict[str, ThresholdConfig] = {}
        self._alert_counter = 0
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        self._alert_counter += 1
        return f"ALT-{datetime.utcnow().strftime('%Y%m%d')}-{self._alert_counter:05d}"
    
    def set_threshold(self, config: ThresholdConfig):
        """Set custom threshold for an indicator"""
        self._thresholds[config.indicator_id] = config
    
    def get_threshold(self, indicator_id: str) -> ThresholdConfig:
        """Get threshold config for indicator"""
        if indicator_id in self._thresholds:
            return self._thresholds[indicator_id]
        return ThresholdConfig(
            indicator_id=indicator_id,
            warning_high=self.DEFAULT_THRESHOLDS["warning_high"],
            critical_high=self.DEFAULT_THRESHOLDS["critical_high"],
            warning_low=self.DEFAULT_THRESHOLDS["warning_low"],
            critical_low=self.DEFAULT_THRESHOLDS["critical_low"],
            rapid_change_threshold=self.DEFAULT_THRESHOLDS["rapid_change"]
        )
    
    def check_threshold(self, indicator_id: str, indicator_name: str,
                        current_value: float) -> Optional[Alert]:
        """
        Check if value breaches thresholds.
        
        Returns:
            Alert if threshold breached, None otherwise
        """
        threshold = self.get_threshold(indicator_id)
        
        severity = None
        direction = None
        
        if current_value >= threshold.critical_high:
            severity = AlertSeverity.CRITICAL
            direction = "high"
        elif current_value >= threshold.warning_high:
            severity = AlertSeverity.HIGH
            direction = "high"
        elif current_value <= threshold.critical_low:
            severity = AlertSeverity.CRITICAL
            direction = "low"
        elif current_value <= threshold.warning_low:
            severity = AlertSeverity.HIGH
            direction = "low"
        
        if severity:
            threshold_val = (threshold.critical_high if direction == "high" and severity == AlertSeverity.CRITICAL
                           else threshold.warning_high if direction == "high"
                           else threshold.critical_low if severity == AlertSeverity.CRITICAL
                           else threshold.warning_low)
            
            alert = Alert(
                alert_id=self._generate_alert_id(),
                indicator_id=indicator_id,
                indicator_name=indicator_name,
                alert_type=AlertType.THRESHOLD_BREACH,
                severity=severity,
                title=f"{indicator_name} at {severity.value} level",
                message=f"{indicator_name} has reached {current_value:.1f}, "
                        f"{'exceeding' if direction == 'high' else 'below'} "
                        f"the {severity.value} threshold of {threshold_val:.1f}",
                current_value=current_value,
                threshold_value=threshold_val
            )
            self._alerts.append(alert)
            return alert
        
        return None
    
    def check_rapid_change(self, indicator_id: str, indicator_name: str,
                           current_value: float, previous_value: float,
                           hours: int = 24) -> Optional[Alert]:
        """
        Check for rapid changes.
        
        Returns:
            Alert if rapid change detected, None otherwise
        """
        if previous_value == 0:
            return None
        
        change_percent = ((current_value - previous_value) / abs(previous_value)) * 100
        threshold = self.get_threshold(indicator_id)
        
        if abs(change_percent) >= threshold.rapid_change_threshold:
            direction = "increased" if change_percent > 0 else "decreased"
            severity = AlertSeverity.HIGH if abs(change_percent) >= 50 else AlertSeverity.MEDIUM
            
            alert = Alert(
                alert_id=self._generate_alert_id(),
                indicator_id=indicator_id,
                indicator_name=indicator_name,
                alert_type=AlertType.RAPID_CHANGE,
                severity=severity,
                title=f"{indicator_name} rapid {direction[:-1]}",
                message=f"{indicator_name} has {direction} by {abs(change_percent):.1f}% "
                        f"in the last {hours} hours (from {previous_value:.1f} to {current_value:.1f})",
                current_value=current_value,
                change_percent=change_percent,
                metadata={"previous_value": previous_value, "hours": hours}
            )
            self._alerts.append(alert)
            return alert
        
        return None
    
    def check_anomaly(self, indicator_id: str, indicator_name: str,
                      current_value: float, z_score: float,
                      expected_value: float) -> Optional[Alert]:
        """
        Create alert for detected anomaly.
        
        Args:
            z_score: How many standard deviations from mean
        """
        if abs(z_score) < 2:
            return None
        
        if abs(z_score) >= 3:
            severity = AlertSeverity.CRITICAL
            anomaly_type = "extreme"
        else:
            severity = AlertSeverity.HIGH
            anomaly_type = "significant"
        
        direction = "above" if z_score > 0 else "below"
        deviation = abs(current_value - expected_value)
        
        alert = Alert(
            alert_id=self._generate_alert_id(),
            indicator_id=indicator_id,
            indicator_name=indicator_name,
            alert_type=AlertType.ANOMALY_DETECTED,
            severity=severity,
            title=f"{indicator_name} anomaly detected",
            message=f"{anomaly_type.capitalize()} anomaly: {indicator_name} is {deviation:.1f} points "
                    f"{direction} expected value of {expected_value:.1f} (z-score: {z_score:.2f})",
            current_value=current_value,
            metadata={"z_score": z_score, "expected_value": expected_value, "anomaly_type": anomaly_type}
        )
        self._alerts.append(alert)
        return alert
    
    def generate_all_alerts(self, indicators: List[Dict[str, Any]]) -> List[Alert]:
        """
        Check all indicators and generate alerts.
        
        Args:
            indicators: List of indicator dicts with:
                - indicator_id, indicator_name, current_value
                - Optional: previous_value, z_score, expected_value
        
        Returns:
            List of generated alerts
        """
        new_alerts = []
        
        for ind in indicators:
            ind_id = ind.get("indicator_id")
            ind_name = ind.get("indicator_name", ind_id)
            current = ind.get("current_value")
            
            if current is None:
                continue
            
            # Check threshold
            alert = self.check_threshold(ind_id, ind_name, current)
            if alert:
                new_alerts.append(alert)
            
            # Check rapid change
            previous = ind.get("previous_value")
            if previous is not None:
                alert = self.check_rapid_change(ind_id, ind_name, current, previous)
                if alert:
                    new_alerts.append(alert)
            
            # Check anomaly
            z_score = ind.get("z_score")
            expected = ind.get("expected_value")
            if z_score is not None and expected is not None:
                alert = self.check_anomaly(ind_id, ind_name, current, z_score, expected)
                if alert:
                    new_alerts.append(alert)
        
        return new_alerts
    
    def get_active_alerts(self, hours: int = 24, 
                          severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get recent unacknowledged alerts"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = [a for a in self._alerts 
                  if not a.acknowledged and a.created_at >= cutoff]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda x: x.created_at, reverse=True)
    
    def get_alerts_by_indicator(self, indicator_id: str) -> List[Alert]:
        """Get all alerts for a specific indicator"""
        return [a for a in self._alerts if a.indicator_id == indicator_id]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                return True
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alert status"""
        active = self.get_active_alerts()
        
        by_severity = {}
        for sev in AlertSeverity:
            by_severity[sev.value] = len([a for a in active if a.severity == sev])
        
        by_type = {}
        for at in AlertType:
            by_type[at.value] = len([a for a in active if a.alert_type == at])
        
        return {
            "total_active": len(active),
            "by_severity": by_severity,
            "by_type": by_type,
            "critical_count": by_severity.get("critical", 0),
            "high_count": by_severity.get("high", 0)
        }
    
    def clear_old_alerts(self, days: int = 7):
        """Remove alerts older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        self._alerts = [a for a in self._alerts if a.created_at >= cutoff]


# Singleton instance
_alert_manager: Optional[AlertManager] = None

def get_alert_manager() -> AlertManager:
    """Get or create the alert manager instance"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
