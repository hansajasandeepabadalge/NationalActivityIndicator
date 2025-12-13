"""
Layer 5: Operational Indicators API - PLAN B: Different Path

Creating endpoint at /api/v1/ops/indicators to avoid any conflicts.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pymongo import MongoClient
from typing import Optional
import traceback

from app.db.session import get_db
from app.layer5.api.auth_routes import get_current_user
from app.layer5.services.dashboard_service import DashboardService
from app.layer5.schemas.auth import UserResponse
from app.core.config import settings

# NEW ROUTER with different prefix to avoid conflicts
router = APIRouter(prefix="/ops", tags=["operations", "layer3"])


@router.get("/indicators")
def get_operational_indicators_clean(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get operational indicators for user's company (Layer 3 data).
    
    CLEAN ENDPOINT at /api/v1/ops/indicators
    
    - Admins see all companies' indicators
    - Regular users see only their company's indicators
    """
    try:
        print(f"🎯 CLEAN OPS ENDPOINT called by: {current_user.email}")
        
        # Determine company_id
        if current_user.role == "admin":
            company_id = None
            print(f"   Admin - fetching all")
        else:
            if not current_user.company_id:
                raise HTTPException(status_code=400, detail="User not linked to company")
            company_id = current_user.company_id
            print(f"   User - fetching company: {company_id}")
        
        # Connect to MongoDB
        print(f"   Connecting to MongoDB...")
        mongo_client = MongoClient(settings.MONGODB_URL)
        
        try:
            dashboard_service = DashboardService(
                db=db,
                mongo_client=mongo_client,
                mongo_db_name=settings.MONGODB_DB_NAME
            )
            
            print(f"   Fetching indicators (limit={limit})...")
            result = dashboard_service.get_operational_indicators(
                company_id=company_id,
                limit=limit
            )
            
            print(f"   ✅ Got {result.total} indicators")
            
            # Manual dict conversion
            indicators_list = []
            for ind in result.indicators:
                indicators_list.append({
                    "indicator_id": ind.indicator_id,
                    "indicator_name": ind.indicator_name,
                    "category": ind.category,
                    "current_value": float(ind.current_value) if ind.current_value is not None else None,
                    "baseline_value": float(ind.baseline_value) if ind.baseline_value is not None else None,
                    "deviation": float(ind.deviation) if ind.deviation is not None else None,
                    "impact_score": float(ind.impact_score) if ind.impact_score is not None else None,
                    "trend": str(ind.trend.value) if ind.trend else "stable",
                    "is_above_threshold": bool(ind.is_above_threshold),
                    "is_below_threshold": bool(ind.is_below_threshold),
                    "company_id": str(ind.company_id) if ind.company_id else None,
                    "calculated_at": ind.calculated_at.isoformat() if ind.calculated_at else None
                })
            
            response = {
                "company_id": str(result.company_id),
                "total": int(result.total),
                "critical_count": int(result.critical_count),
                "warning_count": int(result.warning_count),
                "indicators": indicators_list
            }
            
            print(f"   ✅ Returning {len(indicators_list)} indicators")
            return response
            
        finally:
            mongo_client.close()
            print(f"   MongoDB closed")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR:")
        print(f"   {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@router.get("/test")
def test_ops_endpoint():
    """Test endpoint"""
    return {"status": "ok", "message": "Clean ops endpoint working!", "path": "/api/v1/ops/indicators"}
