"""
Layer 5: User Operational Indicators Route

Separate file to avoid caching issues.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pymongo import MongoClient
import traceback

from app.db.session import get_db
from app.layer5.api.auth_routes import get_current_user
from app.layer5.services.dashboard_service import DashboardService
from app.layer5.schemas.auth import UserResponse
from app.layer5.schemas.dashboard import OperationalIndicatorListResponse
from app.core.config import settings

router = APIRouter(prefix="/user", tags=["user", "layer5", "operations"])


@router.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "ok", "message": "Database connection works"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/test-simple")
def test_simple():
    """Simplest possible test"""
    return {"status": "ok", "message": "Simple endpoint works"}


@router.get("/test-auth")
def test_auth(current_user: UserResponse = Depends(get_current_user)):
    """Test auth dependency"""
    return {"status": "ok", "user": current_user.email, "role": current_user.role}


def _get_user_company_id(user: UserResponse) -> str:
    """Get company ID for user, raise error if not linked to a company"""
    if not user.company_id:
        raise HTTPException(
            status_code=400,
            detail="User is not linked to a company. Please contact admin to link your account."
        )
    return user.company_id


@router.get("/operations-data")  # , response_model=OperationalIndicatorListResponse)
def get_operational_indicators(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get operational indicators for user's company (Layer 3 data).
    Admins can see aggregated indicators from all companies.
    """
<<<<<<< Updated upstream
    import traceback
    from fastapi import HTTPException

    try:
=======
    try:
        print(f"🔍 Operations endpoint called by: {current_user.email}, role: {current_user.role}")
        
>>>>>>> Stashed changes
        # Admin users: show all companies' operational indicators
        # Regular users: show only their company's indicators
        if current_user.role == "admin":
            company_id = None  # None = fetch from all companies
<<<<<<< Updated upstream
        else:
            company_id = _get_user_company_id(current_user)

        # Initialize MongoDB connection for Layer 3 data
        mongo_client = MongoClient(settings.MONGODB_URL)
        dashboard_service = DashboardService(db, mongo_client=mongo_client)

        try:
=======
            print(f"   Admin user - fetching all companies")
        else:
            company_id = _get_user_company_id(current_user)
            print(f"   Regular user - fetching company: {company_id}")

        # Initialize MongoDB connection for Layer 3 data
        print(f"   Connecting to MongoDB: {settings.MONGODB_URL}")
        mongo_client = MongoClient(settings.MONGODB_URL)
        dashboard_service = DashboardService(
            db, 
            mongo_client=mongo_client, 
            mongo_db_name=settings.MONGODB_DB_NAME
        )

        try:
            print(f"   Calling dashboard_service.get_operational_indicators(company_id={company_id}, limit={limit})")
>>>>>>> Stashed changes
            result = dashboard_service.get_operational_indicators(
                company_id=company_id,
                limit=limit
            )
<<<<<<< Updated upstream
            return result
        finally:
            mongo_client.close()
    except Exception as e:
        error_msg = f"!!! ERROR in get_operational_indicators endpoint: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("C:/temp/endpoint_error.txt", "w") as f:
            f.write(error_msg)
        raise HTTPException(status_code=500, detail=f"Error fetching operational indicators: {str(e)}")
=======
            print(f"   ✅ Success! Returning {result.total} indicators")
            return result
        finally:
            mongo_client.close()
            print(f"   MongoDB connection closed")
            
    except Exception as e:
        print(f"❌ ERROR in get_operational_indicators endpoint:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching operational indicators: {str(e)}"
        )

>>>>>>> Stashed changes
