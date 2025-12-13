"""
API endpoint for indicator historical data
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from pymongo import MongoClient
from typing import Optional
import traceback

from app.db.session import get_db
from app.layer5.api.auth_routes import get_current_user
from app.layer5.schemas.auth import UserResponse
from app.core.config import settings
from app.layer3.services.indicator_history_service import IndicatorHistoryService

router = APIRouter(prefix="/indicators", tags=["indicators", "history", "layer3"])


@router.get("/{indicator_id}/history")
def get_indicator_history(
    indicator_id: str = Path(..., description="Indicator ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days of history"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical time-series data for a specific indicator.
    
    Returns data points for the specified number of days, ordered by timestamp.
    Includes trend analysis and statistics.
    """
    try:
        print(f"📊 Fetching history for {indicator_id}, {days} days")
        
        # Determine company_id based on user role
        if current_user.role == "admin":
            company_id = None  # Admin sees national data
        else:
            company_id = current_user.company_id if hasattr(current_user, 'company_id') else None
        
        # Connect to MongoDB
        mongo_client = MongoClient(settings.MONGODB_URL)
        try:
            history_service = IndicatorHistoryService(
                mongo_client=mongo_client,
                db_name=settings.MONGODB_DB_NAME
            )
            
            # Get historical data
            history = history_service.get_history(
                indicator_id=indicator_id,
                company_id=company_id,
                days=days
            )
            
            # Get trend summary
            trend_summary = history_service.get_trend_summary(
                indicator_id=indicator_id,
                company_id=company_id,
                days=days
            )
            
            print(f"   ✅ Found {len(history)} data points, trend: {trend_summary['trend']}")
            
            return {
                "indicator_id": indicator_id,
                "company_id": company_id,
                "period_days": days,
                "data_points": len(history),
                "history": history,
                "trend_summary": trend_summary
            }
            
        finally:
            mongo_client.close()
            
    except Exception as e:
        print(f"❌ Error fetching indicator history: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching indicator history: {str(e)}"
        )


@router.get("/{indicator_id}/trend")
def get_indicator_trend(
    indicator_id: str = Path(..., description="Indicator ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days for trend calculation"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trend summary for a specific indicator.
    
    Returns trend direction, change percentage, and statistics.
    Lightweight endpoint for sparkline data.
    """
    try:
        # Determine company_id
        if current_user.role == "admin":
            company_id = None
        else:
            company_id = current_user.company_id if hasattr(current_user, 'company_id') else None
        
        # Connect to MongoDB
        mongo_client = MongoClient(settings.MONGODB_URL)
        try:
            history_service = IndicatorHistoryService(
                mongo_client=mongo_client,
                db_name=settings.MONGODB_DB_NAME
            )
            
            # Get trend summary only
            trend_summary = history_service.get_trend_summary(
                indicator_id=indicator_id,
                company_id=company_id,
                days=days
            )
            
            return {
                "indicator_id": indicator_id,
                "trend_summary": trend_summary
            }
            
        finally:
            mongo_client.close()
            
    except Exception as e:
        print(f"❌ Error fetching indicator trend: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching indicator trend: {str(e)}"
        )
