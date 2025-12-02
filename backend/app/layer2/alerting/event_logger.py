from sqlalchemy.orm import Session
from app.models.indicator_value import IndicatorEvent
from datetime import datetime

class EventLogger:
    """
    Logs significant events related to indicators.
    """
    
    def log_event(self, db: Session, indicator_id: int, event_type: str, description: str, severity: float, start_time: datetime = None):
        """
        Log an event to the database.
        """
        if start_time is None:
            start_time = datetime.utcnow()
            
        event = IndicatorEvent(
            indicator_id=indicator_id,
            event_type=event_type,
            description=description,
            severity=severity,
            start_time=start_time
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        
        return event
