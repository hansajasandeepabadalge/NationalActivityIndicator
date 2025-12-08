"""
Dashboard access log model for tracking user activity.
"""
from datetime import datetime, timezone
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field


class DashboardAccessLog(Document):
    """
    Dashboard access log document model.
    Tracks user activity and access patterns.
    """

    user_id: Indexed(str)  # type: ignore
    company_id: Optional[str] = None

    # Access details
    action: str  # e.g., "view_dashboard", "view_insight", "update_profile"
    resource_type: Optional[str] = None  # e.g., "dashboard", "insight", "indicator"
    resource_id: Optional[str] = None

    # Request info
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None

    # Additional data
    metadata: dict = Field(default_factory=dict)

    # Timestamps
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "dashboard_access_logs"
        use_state_management = True

