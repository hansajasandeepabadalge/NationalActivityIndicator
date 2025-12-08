"""
Layer 5: Admin API Routes

Admin dashboard endpoints for viewing all national indicators,
industry data, and all company insights.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.db.session import get_async_session
from app.layer5.api.auth_routes import require_admin, get_current_user
from app.layer5.services.dashboard_service import DashboardService
from app.layer5.services.company_service import CompanyService
from app.layer5.schemas.auth import UserResponse
from app.layer5.schemas.dashboard import (
    NationalIndicatorListResponse, BusinessInsightListResponse,
    AdminDashboardResponse, IndustryOverviewResponse
)
from app.layer5.schemas.company import CompanyProfileResponse

router = APIRouter(prefix="/admin", tags=["admin", "layer5"])


# ============== Admin Dashboard Overview ==============

@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get admin dashboard overview.
    Shows aggregate statistics across all companies.
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_admin_dashboard()


# ============== National Indicators (Layer 2) ==============

@router.get("/indicators/national", response_model=NationalIndicatorListResponse)
async def get_national_indicators(
    category: Optional[str] = Query(None, description="Filter by PESTEL category"),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all national indicators (Layer 2 data).
    Shows the 20 national-level economic indicators.
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_national_indicators(category=category, limit=limit)


@router.get("/indicators/national/{indicator_id}/history")
async def get_indicator_history(
    indicator_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get historical values for a specific indicator.
    """
    dashboard_service = DashboardService(db)
    history = await dashboard_service.get_indicator_history(indicator_id, days)
    return {"indicator_id": indicator_id, "days": days, "history": history}


# ============== Industry View ==============

@router.get("/industries")
async def list_industries(
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    List all industries with company counts.
    """
    company_service = CompanyService(db)
    industries = await company_service.get_industries()
    stats = await company_service.get_company_stats()
    
    return {
        "industries": industries,
        "by_industry": stats.get("by_industry", {})
    }


@router.get("/industries/{industry}/overview", response_model=IndustryOverviewResponse)
async def get_industry_overview(
    industry: str,
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get detailed overview for a specific industry.
    """
    dashboard_service = DashboardService(db)
    overview = await dashboard_service._get_industry_overview(industry)
    
    if not overview:
        raise HTTPException(status_code=404, detail=f"Industry '{industry}' not found")
    
    return overview


# ============== All Companies ==============

@router.get("/companies", response_model=List[CompanyProfileResponse])
async def list_companies(
    industry: Optional[str] = Query(None),
    business_scale: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    List all companies with optional filters.
    """
    company_service = CompanyService(db)
    companies = await company_service.list_companies(
        industry=industry,
        business_scale=business_scale,
        limit=limit,
        offset=offset
    )
    return [CompanyProfileResponse.model_validate(c) for c in companies]


@router.get("/companies/{company_id}", response_model=CompanyProfileResponse)
async def get_company(
    company_id: str,
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get detailed company profile.
    """
    company_service = CompanyService(db)
    company = await company_service.get_company(company_id)
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return CompanyProfileResponse.model_validate(company)


# ============== All Business Insights ==============

@router.get("/insights", response_model=BusinessInsightListResponse)
async def get_all_insights(
    insight_type: Optional[str] = Query(None, description="Filter by 'risk' or 'opportunity'"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    status: str = Query("active"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all business insights across all companies.
    """
    dashboard_service = DashboardService(db)
    
    # TODO: Add industry filter by joining with company_profiles
    
    return await dashboard_service.get_business_insights(
        insight_type=insight_type,
        severity=severity,
        status=status,
        limit=limit,
        offset=offset
    )


@router.get("/insights/risks", response_model=BusinessInsightListResponse)
async def get_all_risks(
    severity: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all risks across all companies.
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_risks(severity=severity, limit=limit)


@router.get("/insights/opportunities", response_model=BusinessInsightListResponse)
async def get_all_opportunities(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get all opportunities across all companies.
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_opportunities(limit=limit)


@router.get("/insights/company/{company_id}", response_model=BusinessInsightListResponse)
async def get_company_insights(
    company_id: str,
    insight_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get insights for a specific company (admin view).
    """
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_business_insights(
        company_id=company_id,
        insight_type=insight_type,
        limit=limit
    )
