from datetime import datetime, timezone
from typing import Optional
from pymongo import DESCENDING

from app.models.company import Company
from app.models.insight import BusinessInsight
from app.models.Indicator import NationalIndicator, OperationalIndicatorValue
from app.models.access_log import DashboardAccessLog
from app.schemas.dashboard import (
    UserDashboardHome,
    AdminDashboardHome,
    AlertItem,
    UserAlertsResponse,
    DashboardStats
)
from app.schemas.Insight import InsightListItem
from app.services.IndicatorService import IndicatorService
from app.services.InsightService import InsightService
from app.services.companyService import CompanyService


class DashboardService:

    @staticmethod
    async def get_user_dashboard_home(company_id: str) -> UserDashboardHome:
        # Get company
        company = await Company.get(company_id)
        if not company:
            raise ValueError("Company not found")

        # Get health score and indicators
        health_data = await IndicatorService.get_company_health_score(company_id)

        # Get insights summary
        insights_summary = await InsightService.get_company_insights_summary(company_id)

        return UserDashboardHome(
            health_score=health_data.health_score,
            health_trend=health_data.trend,
            health_trend_change=health_data.trend_change,
            indicators=health_data.indicators,
            recent_insights=insights_summary.recent_insights,
            alert_count=insights_summary.total_risks + insights_summary.total_opportunities,
            critical_risks=insights_summary.critical_risks,
            high_opportunities=insights_summary.high_value_opportunities,
            company_name=company.company_name,
            last_updated=health_data.last_updated
        )

    @staticmethod
    async def get_admin_dashboard_home() -> AdminDashboardHome:
        # Get total companies
        total_companies = await Company.find_all().count()

        # Get companies at risk
        all_companies = await Company.find_all().to_list()
        companies_at_risk = sum(
            1 for c in all_companies
            if c.health_score and c.health_score < 50
        )

        # Calculate average health score
        health_scores = [c.health_score for c in all_companies if c.health_score]
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 0

        # Get national indicators summary
        national_indicators = await IndicatorService.get_national_indicators_grouped()

        # Summarize by category
        national_summary = {}
        for category in ["political", "economic", "social", "infrastructure"]:
            indicators = getattr(national_indicators, category)
            if indicators:
                avg_value = sum(i.value for i in indicators) / len(indicators)
                critical_count = sum(1 for i in indicators if i.status == "critical")
                national_summary[category] = {
                    "avg_value": round(avg_value, 1),
                    "critical_count": critical_count,
                    "indicator_count": len(indicators)
                }

        # Get critical alerts count
        critical_alerts = await BusinessInsight.find(
            BusinessInsight.type == "risk",
            BusinessInsight.severity == "critical",
            BusinessInsight.active == True
        ).count()

        # Get recent critical insights using dict query for $in operator
        recent_critical = await BusinessInsight.find({
            "type": "risk",
            "severity": {"$in": ["critical", "high"]},
            "active": True
        }).sort([("created_at", DESCENDING)]).limit(5).to_list()

        recent_critical_insights = [
            InsightListItem(
                id=str(ins.id),
                company_id=ins.company_id,
                type=ins.type,
                severity=ins.severity,
                title=ins.title,
                summary=ins.summary,
                impact_score=getattr(ins, 'impact_score', None),
                probability=getattr(ins, 'probability', None),
                category=ins.category,
                active=getattr(ins, 'active', True),
                created_at=ins.created_at
            )
            for ins in recent_critical
        ]

        # Get industries overview
        industries = await CompanyService.get_all_industries()
        industries_overview = []

        for industry in industries[:5]:  # Top 5 industries
            agg = await CompanyService.get_industry_aggregation(industry)
            industries_overview.append({
                "industry": industry,
                "company_count": agg.company_count,
                "avg_health_score": agg.avg_health_score,
                "companies_at_risk": agg.companies_at_risk
            })

        # System health (placeholder)
        system_health = {
            "database": "healthy",
            "cache": "healthy",
            "api": "healthy",
            "last_data_update": datetime.now(timezone.utc).isoformat()
        }

        return AdminDashboardHome(
            total_companies=total_companies,
            companies_at_risk=companies_at_risk,
            avg_health_score=round(avg_health_score, 1),
            national_indicators_summary=national_summary,
            critical_alerts_count=critical_alerts,
            recent_critical_insights=recent_critical_insights,
            industries_overview=industries_overview,
            system_health=system_health
        )

    @staticmethod
    async def get_user_alerts(
            company_id: str,
            limit: int = 20
    ) -> UserAlertsResponse:
        # Get recent insights as alerts
        insights = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.active == True
        ).sort([("created_at", DESCENDING)]).limit(limit).to_list()

        alerts = []
        for ins in insights:
            alerts.append(AlertItem(
                id=str(ins.id),
                type=ins.type,
                severity=ins.severity,
                title=ins.title,
                created_at=ins.created_at,
                source="insight"
            ))

        # Get unacknowledged count
        unread_count = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.active == True,
            BusinessInsight.acknowledged == False
        ).count()

        total_count = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.active == True
        ).count()

        return UserAlertsResponse(
            alerts=alerts,
            unread_count=unread_count,
            total_count=total_count
        )

    @staticmethod
    async def get_dashboard_stats(company_id: Optional[str] = None) -> DashboardStats:
        if company_id:
            # User-specific stats
            indicators = await OperationalIndicatorValue.find(
                OperationalIndicatorValue.company_id == company_id
            ).to_list()

            total_indicators = len(indicators)
            indicators_improving = sum(1 for i in indicators if i.trend == "up")
            indicators_declining = sum(1 for i in indicators if i.trend == "down")

            total_insights = await BusinessInsight.find(
                BusinessInsight.company_id == company_id
            ).count()

            active_risks = await BusinessInsight.find(
                BusinessInsight.company_id == company_id,
                BusinessInsight.type == "risk",
                BusinessInsight.active == True
            ).count()

            active_opportunities = await BusinessInsight.find(
                BusinessInsight.company_id == company_id,
                BusinessInsight.type == "opportunity",
                BusinessInsight.active == True
            ).count()
        else:
            # System-wide stats
            total_indicators = await NationalIndicator.find_all().count()

            indicators = await NationalIndicator.find_all().to_list()
            indicators_improving = sum(1 for i in indicators if i.trend == "up")
            indicators_declining = sum(1 for i in indicators if i.trend == "down")

            total_insights = await BusinessInsight.find_all().count()

            active_risks = await BusinessInsight.find(
                BusinessInsight.type == "risk",
                BusinessInsight.active == True
            ).count()

            active_opportunities = await BusinessInsight.find(
                BusinessInsight.type == "opportunity",
                BusinessInsight.active == True
            ).count()

        return DashboardStats(
            total_indicators=total_indicators,
            indicators_improving=indicators_improving,
            indicators_declining=indicators_declining,
            total_insights=total_insights,
            active_risks=active_risks,
            active_opportunities=active_opportunities
        )

    @staticmethod
    async def log_access(
            user_id: str,
            action: str,
            resource_type: Optional[str] = None,
            resource_id: Optional[str] = None,
            ip_address: Optional[str] = None,
            user_agent: Optional[str] = None
    ):
        log_entry = DashboardAccessLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await log_entry.insert()

