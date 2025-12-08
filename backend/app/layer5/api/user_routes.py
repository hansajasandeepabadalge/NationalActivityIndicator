"""
Layer 5: User API Routes

User dashboard endpoints for viewing company-specific data.
Users can only see their own company's insights and profile.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_async_session
from app.layer5.api.auth_routes import get_current_user
from app.layer5.services.dashboard_service import DashboardService
from app.layer5.services.company_service import CompanyService
from app.layer5.schemas.auth import UserResponse
from app.layer5.schemas.dashboard import (
    DashboardHomeResponse, BusinessInsightListResponse,
    OperationalIndicatorListResponse
)
from app.layer5.schemas.company import CompanyProfileResponse, CompanyProfileUpdate

router = APIRouter(prefix="/user", tags=["user", "layer5"])


def _get_user_company_id(user: UserResponse) -> str:
    """Get company ID for user, raise error if not linked to a company"""
    if not user.company_id:
        raise HTTPException(
            status_code=400,
            detail="User is not linked to a company. Please contact admin to link your account."
        )
    return user.company_id


# ============== Dashboard Home ==============

@router.get("/dashboard/home", response_model=DashboardHomeResponse)
async def get_dashboard_home(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get user's dashboard home page.
    Shows health score, risk/opportunity summaries, and key indicators.
    """
    company_id = _get_user_company_id(current_user)
    
    dashboard_service = DashboardService(db)
    
    try:
        return await dashboard_service.get_dashboard_home(company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============== Company Profile ==============

@router.get("/company", response_model=CompanyProfileResponse)
async def get_my_company(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get user's company profile.
    """
    company_id = _get_user_company_id(current_user)
    
    company_service = CompanyService(db)
    company = await company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")
    
    return CompanyProfileResponse.model_validate(company)


@router.put("/company", response_model=CompanyProfileResponse)
async def update_my_company(
    update_data: CompanyProfileUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update user's company profile.
    Only certain fields can be updated by users.
    """
    company_id = _get_user_company_id(current_user)
    
    company_service = CompanyService(db)
    company = await company_service.update_company(company_id, update_data)
    
    if not company:
        raise HTTPException(status_code=404, detail="Company profile not found")
    
    return CompanyProfileResponse.model_validate(company)


# ============== Business Insights ==============

@router.get("/insights", response_model=BusinessInsightListResponse)
async def get_my_insights(
    insight_type: Optional[str] = Query(None, description="Filter by 'risk' or 'opportunity'"),
    severity: Optional[str] = Query(None),
    status: str = Query("active"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get business insights for user's company.
    """
    company_id = _get_user_company_id(current_user)
    
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_business_insights(
        company_id=company_id,
        insight_type=insight_type,
        severity=severity,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/risks", response_model=BusinessInsightListResponse)
async def get_my_risks(
    severity: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get risks for user's company.
    """
    company_id = _get_user_company_id(current_user)
    
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_risks(
        company_id=company_id,
        severity=severity,
        limit=limit
    )


@router.get("/opportunities", response_model=BusinessInsightListResponse)
async def get_my_opportunities(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get opportunities for user's company.
    """
    company_id = _get_user_company_id(current_user)
    
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_opportunities(
        company_id=company_id,
        limit=limit
    )


# ============== Insight Actions ==============

@router.post("/insights/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Acknowledge a business insight.
    Marks it as seen/acknowledged by the user.
    """
    from datetime import datetime
    from sqlalchemy import update
    from app.models.business_insight_models import BusinessInsight
    
    company_id = _get_user_company_id(current_user)
    
    # Verify the insight belongs to user's company
    from sqlalchemy import select
    result = await db.execute(
        select(BusinessInsight).where(
            BusinessInsight.insight_id == insight_id,
            BusinessInsight.company_id == company_id
        )
    )
    insight = result.scalar_one_or_none()
    
    if not insight:
        raise HTTPException(
            status_code=404, 
            detail="Insight not found or does not belong to your company"
        )
    
    # Update status
    await db.execute(
        update(BusinessInsight)
        .where(BusinessInsight.insight_id == insight_id)
        .values(
            status='acknowledged',
            acknowledged_at=datetime.utcnow(),
            acknowledged_by=current_user.email
        )
    )
    await db.commit()
    
    return {"message": "Insight acknowledged", "insight_id": insight_id}


@router.post("/insights/{insight_id}/resolve")
async def resolve_insight(
    insight_id: int,
    resolution_notes: str = "",
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Mark a business insight as resolved.
    """
    from datetime import datetime
    from sqlalchemy import update, select
    from app.models.business_insight_models import BusinessInsight
    
    company_id = _get_user_company_id(current_user)
    
    # Verify the insight belongs to user's company
    result = await db.execute(
        select(BusinessInsight).where(
            BusinessInsight.insight_id == insight_id,
            BusinessInsight.company_id == company_id
        )
    )
    insight = result.scalar_one_or_none()
    
    if not insight:
        raise HTTPException(
            status_code=404,
            detail="Insight not found or does not belong to your company"
        )
    
    # Update status
    await db.execute(
        update(BusinessInsight)
        .where(BusinessInsight.insight_id == insight_id)
        .values(
            status='resolved',
            resolved_at=datetime.utcnow(),
            resolution_notes=resolution_notes
        )
    )
    await db.commit()
    
    return {"message": "Insight resolved", "insight_id": insight_id}
