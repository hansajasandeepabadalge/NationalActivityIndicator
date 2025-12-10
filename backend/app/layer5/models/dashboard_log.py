"""
Layer 5: Dashboard Access Log

Tracks user interactions with the dashboard for analytics.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.base_class import Base


class DashboardAccessLog(Base):
    """
    Logs user dashboard access for analytics and auditing.
    """
    __tablename__ = "l5_dashboard_access_log"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User reference
    user_id = Column(Integer, ForeignKey('l5_users.id'), nullable=False, index=True)
    
    # Access details
    endpoint = Column(String(200), nullable=False)
    action = Column(String(50))  # 'view', 'filter', 'export', 'acknowledge'
    
    # Additional context
    resource_type = Column(String(50))  # 'indicator', 'insight', 'company'
    resource_id = Column(String(100))
    
    # Request metadata
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Filter/query parameters used
    query_params = Column(JSONB)
    
    # Timestamp
    accessed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<DashboardAccessLog(user_id={self.user_id}, endpoint={self.endpoint})>"
