"""
User API routes for business user dashboard.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from loguru import logger

from app.models.user import User
from app.api.deps import get_current_user, get_current_business_user
from app.services.companyService import CompanyService
from app.services.IndicatorService import IndicatorService
from app.services.InsightService import InsightService
from app.services.dashboardService import DashboardService
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse
)
from app.schemas.Indicator import (
    OperationalIndicatorResponse,
    OperationalIndicatorWithHistory,
    HealthScoreResponse,
    IndicatorHistoryResponse
)
from app.schemas.Insight import (
    InsightResponse,
    InsightListItem,
    InsightsSummary
)
from app.schemas.dashboard import (
    UserDashboardHome,
    UserAlertsResponse,
    DashboardStats
)
from app.schemas.common import MessageResponse, PaginatedResponse


router = APIRouter(prefix="/user", tags=["User Dashboard"])


# ==================== Company Profile ====================

@router.post(
    "/company/profile",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create company profile"
)
async def create_company_profile(
        company_data: CompanyCreate,
        current_user: User = Depends(get_current_user)
):
    try:
        company = await CompanyService.create_company(
            user_id=str(current_user.id),
            company_data=company_data
        )

        # Seed initial indicators and insights for demo
        await IndicatorService.seed_company_indicators(str(company.id))
        await InsightService.seed_company_insights(str(company.id))

        return CompanyService.company_to_response(company)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/company/profile",
    response_model=CompanyResponse,
    summary="Get company profile"
)
async def get_company_profile(
        current_user: User = Depends(get_current_user)
):
    company = await CompanyService.get_company_by_user(str(current_user.id))

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please create one first."
        )

    return CompanyService.company_to_response(company)


@router.put(
    "/company/profile",
    response_model=CompanyResponse,
    summary="Update company profile"
)
async def update_company_profile(
        update_data: CompanyUpdate,
        current_user: User = Depends(get_current_user)
):
    company = await CompanyService.get_company_by_user(str(current_user.id))

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )

    updated_company = await CompanyService.update_company(company, update_data)
    return CompanyService.company_to_response(updated_company)


# ==================== Dashboard Home ====================

@router.get(
    "/dashboard/home",
    response_model=UserDashboardHome,
    summary="Get dashboard home data"
)
async def get_dashboard_home(
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    try:
        return await DashboardService.get_user_dashboard_home(current_user.company_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/dashboard/stats",
    response_model=DashboardStats,
    summary="Get dashboard statistics"
)
async def get_dashboard_stats(
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await DashboardService.get_dashboard_stats(current_user.company_id)


@router.get(
    "/alerts",
    response_model=UserAlertsResponse,
    summary="Get alerts"
)
async def get_alerts(
        limit: int = Query(default=20, ge=1, le=100),
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await DashboardService.get_user_alerts(
        current_user.company_id,
        limit=limit
    )


# ==================== Indicators ====================

@router.get(
    "/indicators",
    response_model=list[OperationalIndicatorResponse],
    summary="Get operational indicators"
)
async def get_indicators(
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await IndicatorService.get_company_indicators(current_user.company_id)


@router.get(
    "/indicators/health",
    response_model=HealthScoreResponse,
    summary="Get health score"
)
async def get_health_score(
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await IndicatorService.get_company_health_score(current_user.company_id)


@router.get(
    "/indicators/history/{indicator_name}",
    response_model=IndicatorHistoryResponse,
    summary="Get indicator history"
)
async def get_indicator_history(
        indicator_name: str,
        days: int = Query(default=30, ge=1, le=365),
        current_user: User = Depends(get_current_user)
):
    # This would need to be implemented for operational indicators
    # For now, return empty history
    return IndicatorHistoryResponse(
        indicator_name=indicator_name,
        data_points=[]
    )


# ==================== Risks ====================

@router.get(
    "/risks",
    response_model=list[InsightListItem],
    summary="Get risks"
)
async def get_risks(
        severity: Optional[str] = Query(default=None, regex="^(critical|high|medium|low)$"),
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await InsightService.get_company_risks(
        current_user.company_id,
        severity=severity
    )


@router.get(
    "/risks/{risk_id}",
    response_model=InsightResponse,
    summary="Get risk details"
)
async def get_risk_details(
        risk_id: str,
        current_user: User = Depends(get_current_user)
):
    insight = await InsightService.get_insight_by_id(risk_id)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )

    # Verify ownership
    if insight.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return insight


@router.post(
    "/risks/{risk_id}/acknowledge",
    response_model=MessageResponse,
    summary="Acknowledge risk"
)
async def acknowledge_risk(
        risk_id: str,
        current_user: User = Depends(get_current_user)
):
    # Verify ownership first
    insight = await InsightService.get_insight_by_id(risk_id)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found"
        )

    if insight.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    success = await InsightService.acknowledge_insight(risk_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge risk"
        )

    return MessageResponse(message="Risk acknowledged")


# ==================== Opportunities ====================

@router.get(
    "/opportunities",
    response_model=list[InsightListItem],
    summary="Get opportunities"
)
async def get_opportunities(
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await InsightService.get_company_opportunities(current_user.company_id)


@router.get(
    "/opportunities/{opportunity_id}",
    response_model=InsightResponse,
    summary="Get opportunity details"
)
async def get_opportunity_details(
        opportunity_id: str,
        current_user: User = Depends(get_current_user)
):
    insight = await InsightService.get_insight_by_id(opportunity_id)

    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    # Verify ownership
    if insight.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return insight


# ==================== Insights Summary ====================

@router.get(
    "/insights/summary",
    response_model=InsightsSummary,
    summary="Get insights summary"
)
async def get_insights_summary(
        current_user: User = Depends(get_current_user)
):
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a company profile first"
        )

    return await InsightService.get_company_insights_summary(current_user.company_id)