from sqlalchemy.orm import Session
from app.models import IndicatorEvent  # Import from unified models package
from datetime import datetime

class EventLogger:
    """
    Logs significant events related to indicators.
    """
    
    def log_event(self, db: Session, indicator_id: str, event_type: str, description: str, severity: str = "medium", timestamp: datetime = None):
        """
        Log an event to the database.
        
        Args:
            db: Database session
            indicator_id: The indicator ID (string)
            event_type: Type of event (threshold_breach, anomaly_detected, etc.)
            description: Event description
            severity: Severity level (low, medium, high, critical)
            timestamp: Event time (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        event = IndicatorEvent(
            indicator_id=indicator_id,
            event_type=event_type,
            description=description,
            severity=severity,
            timestamp=timestamp
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return event
