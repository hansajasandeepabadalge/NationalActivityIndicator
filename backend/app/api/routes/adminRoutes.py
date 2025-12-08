"""
Admin API routes for admin dashboard.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from loguru import logger

from app.models.user import User
from app.api.deps import get_current_admin
from app.services.companyService import CompanyService
from app.services.IndicatorService import IndicatorService
from app.services.InsightService import InsightService
from app.services.dashboardService import DashboardService
from app.schemas.company import (
    CompanyResponse,
    CompanyListItem,
    IndustryAggregation
)
from app.schemas.Indicator import (
    NationalIndicatorResponse,
    NationalIndicatorsGrouped,
    IndicatorHistoryResponse,
    IndustryIndicatorSummary
)
from app.schemas.Insight import (
    InsightResponse,
    InsightListWithCompany,
    AdminInsightsSummary
)
from app.schemas.dashboard import (
    AdminDashboardHome,
    DashboardStats
)
from app.schemas.common import PaginatedResponse


router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


# ==================== Dashboard Home ====================

@router.get(
    "/dashboard/home",
    response_model=AdminDashboardHome,
    summary="Get admin dashboard home"
)
async def get_admin_dashboard_home(
        current_user: User = Depends(get_current_admin)
):
    """
    Get all data for the admin dashboard home page.

    Includes:
    - System overview statistics
    - National indicators summary
    - Critical alerts
    - Industry overview
    """
    return await DashboardService.get_admin_dashboard_home()


@router.get(
    "/dashboard/stats",
    response_model=DashboardStats,
    summary="Get system statistics"
)
async def get_system_stats(
        current_user: User = Depends(get_current_admin)
):
    """Get system-wide dashboard statistics."""
    return await DashboardService.get_dashboard_stats()


# ==================== National Indicators ====================

@router.get(
    "/national-indicators",
    response_model=list[NationalIndicatorResponse],
    summary="Get all national indicators"
)
async def get_national_indicators(
        current_user: User = Depends(get_current_admin)
):
    """Get all 20 national indicators with current values."""
    return await IndicatorService.get_all_national_indicators()


@router.get(
    "/national-indicators/grouped",
    response_model=NationalIndicatorsGrouped,
    summary="Get national indicators grouped by category"
)
async def get_national_indicators_grouped(
        current_user: User = Depends(get_current_admin)
):
    """
    Get national indicators grouped by category.

    Categories: Political, Economic, Social, Infrastructure
    """
    return await IndicatorService.get_national_indicators_grouped()


@router.get(
    "/national-indicators/history/{indicator_name}",
    response_model=IndicatorHistoryResponse,
    summary="Get national indicator history"
)
async def get_national_indicator_history(
        indicator_name: str,
        days: int = Query(default=30, ge=1, le=365),
        current_user: User = Depends(get_current_admin)
):
    """Get historical data for a national indicator."""
    return await IndicatorService.get_national_indicator_history(
        indicator_name=indicator_name,
        days=days
    )


@router.post(
    "/national-indicators/seed",
    summary="Seed national indicators"
)
async def seed_national_indicators(
        current_user: User = Depends(get_current_admin)
):
    """Seed initial national indicators data for testing."""
    await IndicatorService.seed_national_indicators()
    return {"message": "National indicators seeded successfully"}


# ==================== Industry Indicators ====================

@router.get(
    "/industries",
    response_model=list[str],
    summary="Get all industries"
)
async def get_all_industries(
        current_user: User = Depends(get_current_admin)
):
    """Get list of all industries with registered companies."""
    return await CompanyService.get_all_industries()


@router.get(
    "/industry-indicators/{industry}",
    response_model=IndustryIndicatorSummary,
    summary="Get industry indicators summary"
)
async def get_industry_indicators(
        industry: str,
        current_user: User = Depends(get_current_admin)
):
    """
    Get aggregated operational indicators for an industry.

    Shows average values and distribution across companies.
    """
    return await IndicatorService.get_industry_indicators_summary(industry)


@router.get(
    "/industry-aggregation/{industry}",
    response_model=IndustryAggregation,
    summary="Get industry aggregation"
)
async def get_industry_aggregation(
        industry: str,
        current_user: User = Depends(get_current_admin)
):
    """Get aggregated company data for an industry."""
    return await CompanyService.get_industry_aggregation(industry)


# ==================== Companies ====================

@router.get(
    "/companies",
    response_model=list[CompanyListItem],
    summary="Get all companies"
)
async def get_all_companies(
        industry: Optional[str] = None,
        current_user: User = Depends(get_current_admin)
):
    """
    Get all companies with risk counts.

    Optionally filter by industry.
    """
    companies = await CompanyService.get_company_list_with_risks()

    if industry:
        companies = [c for c in companies if c.industry == industry]

    return companies


@router.get(
    "/companies/{company_id}",
    response_model=CompanyResponse,
    summary="Get company details"
)
async def get_company_details(
        company_id: str,
        current_user: User = Depends(get_current_admin)
):
    """Get detailed information for a specific company."""
    company = await CompanyService.get_company_by_id(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    return CompanyService.company_to_response(company)


@router.get(
    "/companies/{company_id}/indicators",
    summary="Get company indicators"
)
async def get_company_indicators(
        company_id: str,
        current_user: User = Depends(get_current_admin)
):
    """Get all operational indicators for a specific company."""
    company = await CompanyService.get_company_by_id(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    indicators = await IndicatorService.get_company_indicators(company_id)
    health = await IndicatorService.get_company_health_score(company_id)

    return {
        "company_id": company_id,
        "company_name": company.company_name,
        "health_score": health.health_score,
        "indicators": indicators
    }


@router.get(
    "/companies/{company_id}/insights",
    summary="Get company insights"
)
async def get_company_insights(
        company_id: str,
        insight_type: Optional[str] = Query(default=None, regex="^(risk|opportunity)$"),
        severity: Optional[str] = Query(default=None, regex="^(critical|high|medium|low)$"),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: User = Depends(get_current_admin)
):
    """Get all insights for a specific company."""
    company = await CompanyService.get_company_by_id(company_id)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )

    insights, total = await InsightService.get_company_insights(
        company_id=company_id,
        insight_type=insight_type,
        severity=severity,
        page=page,
        page_size=page_size
    )

    return {
        "company_id": company_id,
        "company_name": company.company_name,
        "insights": insights,
        "total": total,
        "page": page,
        "page_size": page_size
    }


# ==================== All Insights ====================

@router.get(
    "/insights",
    summary="Get all insights"
)
async def get_all_insights(
        industry: Optional[str] = None,
        insight_type: Optional[str] = Query(default=None, regex="^(risk|opportunity)$"),
        severity: Optional[str] = Query(default=None, regex="^(critical|high|medium|low)$"),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: User = Depends(get_current_admin)
):
    """
    Get all insights across all companies.

    Can filter by industry, type, and severity.
    """
    insights, total = await InsightService.get_all_insights_admin(
        industry=industry,
        insight_type=insight_type,
        severity=severity,
        page=page,
        page_size=page_size
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": insights,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


@router.get(
    "/insights/summary",
    response_model=AdminInsightsSummary,
    summary="Get insights summary"
)
async def get_insights_summary(
        current_user: User = Depends(get_current_admin)
):
    """Get aggregated insights summary across all companies."""
    return await InsightService.get_admin_insights_summary()


@router.get(
    "/insights/{insight_id}",
    response_model=InsightResponse,
    summary="Get insight details"
)
async def get_insight_details(
        insight_id: str,
        current_user: User = Depends(get_current_admin)
):
    """Get detailed information for a specific insight."""
    insight = await InsightService.get_insight_by_id(insight_id)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )

    return insight