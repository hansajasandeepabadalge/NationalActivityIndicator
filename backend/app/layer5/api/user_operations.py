"""
Layer 5: User Operational Indicators Route

Separate file to avoid caching issues.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pymongo import MongoClient

from app.db.session import get_db
from app.layer5.api.auth_routes import get_current_user
from app.layer5.services.dashboard_service import DashboardService
from app.layer5.schemas.auth import UserResponse
from app.layer5.schemas.dashboard import OperationalIndicatorListResponse
from app.core.config import settings

router = APIRouter(prefix="/user", tags=["user", "layer5", "operations"])


def _get_user_company_id(user: UserResponse) -> str:
    """Get company ID for user, raise error if not linked to a company"""
    from fastapi import HTTPException
    if not user.company_id:
        raise HTTPException(
            status_code=400,
            detail="User is not linked to a company. Please contact admin to link your account."
        )
    return user.company_id


@router.get("/operations-data", response_model=OperationalIndicatorListResponse)
def get_operational_indicators(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get operational indicators for user's company (Layer 3 data).
    Admins can see aggregated indicators from all companies.
    """
    # Admin users: show all companies' operational indicators
    # Regular users: show only their company's indicators
    if current_user.role == "admin":
        company_id = None  # None = fetch from all companies
    else:
        company_id = _get_user_company_id(current_user)

    # Initialize MongoDB connection for Layer 3 data
    mongo_client = MongoClient(settings.MONGODB_URL)
    dashboard_service = DashboardService(db, mongo_client=mongo_client)

    try:
        return dashboard_service.get_operational_indicators(
            company_id=company_id,
            limit=limit
        )
    finally:
        mongo_client.close()
