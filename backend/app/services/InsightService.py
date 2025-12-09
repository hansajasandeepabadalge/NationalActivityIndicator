from typing import Optional, List, Literal
from loguru import logger
from pymongo import DESCENDING

from app.models.insight import BusinessInsight, Recommendation
from app.models.company import Company
from app.schemas.Insight import (
    InsightResponse,
    InsightListItem,
    InsightListWithCompany,
    InsightsSummary,
    AdminInsightsSummary
)


class InsightService:

    @staticmethod
    async def get_company_insights(
            company_id: str,
            insight_type: Optional[Literal["risk", "opportunity"]] = None,
            severity: Optional[str] = None,
            active_only: bool = True,
            page: int = 1,
            page_size: int = 20
    ) -> tuple[List[InsightListItem], int]:
        query_filters = {"company_id": company_id}

        if insight_type:
            query_filters["type"] = insight_type

        if severity:
            query_filters["severity"] = severity

        if active_only:
            query_filters["active"] = True

        query = BusinessInsight.find(query_filters)
        total = await query.count()

        insights = await query.sort(
            [("severity", DESCENDING), ("created_at", DESCENDING)]
        ).skip((page - 1) * page_size).limit(page_size).to_list()

        result = [
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
            for ins in insights
        ]

        return result, total

    @staticmethod
    async def get_insight_by_id(insight_id: str) -> Optional[InsightResponse]:
        try:
            insight = await BusinessInsight.get(insight_id)
            if not insight:
                return None

            return InsightResponse(
                id=str(insight.id),
                company_id=insight.company_id,
                type=insight.type,
                severity=insight.severity,
                title=insight.title,
                description=insight.description,
                summary=insight.summary,
                impact_score=insight.impact_score,
                probability=insight.probability,
                risk_score=insight.risk_score,
                potential_value=insight.potential_value,
                feasibility=insight.feasibility,
                category=insight.category,
                tags=insight.tags,
                recommendations=[r.model_dump() for r in insight.recommendations],
                time_horizon=insight.time_horizon,
                active=insight.active,
                acknowledged=insight.acknowledged,
                resolved=insight.resolved,
                created_at=insight.created_at
            )
        except Exception:
            return None

    @staticmethod
    async def get_company_risks(
            company_id: str,
            severity: Optional[str] = None
    ) -> List[InsightListItem]:
        insights, _ = await InsightService.get_company_insights(
            company_id=company_id,
            insight_type="risk",
            severity=severity,
            page_size=100
        )
        return insights

    @staticmethod
    async def get_company_opportunities(company_id: str) -> List[InsightListItem]:
        insights, _ = await InsightService.get_company_insights(
            company_id=company_id,
            insight_type="opportunity",
            page_size=100
        )
        return insights

    @staticmethod
    async def get_company_insights_summary(company_id: str) -> InsightsSummary:
        # Get counts
        total_risks = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.type == "risk",
            BusinessInsight.active == True
        ).count()

        critical_risks = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.type == "risk",
            BusinessInsight.severity == "critical",
            BusinessInsight.active == True
        ).count()

        high_risks = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.type == "risk",
            BusinessInsight.severity == "high",
            BusinessInsight.active == True
        ).count()

        total_opportunities = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.type == "opportunity",
            BusinessInsight.active == True
        ).count()

        # Query for high value opportunities (critical or high severity)
        high_value_opportunities = await BusinessInsight.find({
            "company_id": company_id,
            "type": "opportunity",
            "severity": {"$in": ["critical", "high"]},
            "active": True
        }).count()

        # Get recent insights
        recent = await BusinessInsight.find(
            BusinessInsight.company_id == company_id,
            BusinessInsight.active == True
        ).sort([("created_at", DESCENDING)]).limit(5).to_list()

        recent_insights = [
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
            for ins in recent
        ]

        return InsightsSummary(
            total_risks=total_risks,
            critical_risks=critical_risks,
            high_risks=high_risks,
            total_opportunities=total_opportunities,
            high_value_opportunities=high_value_opportunities,
            recent_insights=recent_insights
        )

    @staticmethod
    async def acknowledge_insight(insight_id: str, user_id: str = "system") -> bool:
        try:
            insight = await BusinessInsight.get(insight_id)
            if not insight:
                return False

            insight.acknowledge(user_id)
            await insight.save()
            return True
        except Exception:
            return False

    @staticmethod
    async def resolve_insight(insight_id: str) -> bool:
        try:
            insight = await BusinessInsight.get(insight_id)
            if not insight:
                return False

            insight.resolve()
            await insight.save()
            return True
        except Exception:
            return False

    @staticmethod
    async def get_all_insights_admin(
            industry: Optional[str] = None,
            insight_type: Optional[str] = None,
            severity: Optional[str] = None,
            page: int = 1,
            page_size: int = 20
    ) -> tuple[List[InsightListWithCompany], int]:
        # Build query
        query_filters = {"active": True}

        if insight_type:
            query_filters["type"] = insight_type

        if severity:
            query_filters["severity"] = severity

        # If filtering by industry, get company IDs first
        if industry:
            companies = await Company.find(Company.industry == industry).to_list()
            company_ids = [str(c.id) for c in companies]
            query_filters["company_id"] = {"$in": company_ids}

        query = BusinessInsight.find(query_filters)
        total = await query.count()

        insights = await query.sort(
            [("severity", DESCENDING), ("created_at", DESCENDING)]
        ).skip((page - 1) * page_size).limit(page_size).to_list()

        # Get company info for each insight
        result = []
        for ins in insights:
            company = await Company.get(ins.company_id)
            result.append(InsightListWithCompany(
                id=str(ins.id),
                company_id=ins.company_id,
                type=ins.type,
                severity=ins.severity,
                title=ins.title,
                summary=ins.summary,
                impact_score=ins.impact_score,
                probability=ins.probability,
                category=ins.category,
                active=ins.active,
                created_at=ins.created_at,
                company_name=company.company_name if company else "Unknown",
                industry=company.industry if company else "Unknown"
            ))

        return result, total

    @staticmethod
    async def get_admin_insights_summary() -> AdminInsightsSummary:
        # Total companies
        total_companies = await Company.find_all().count()

        # Companies with critical risks
        critical_insights = await BusinessInsight.find(
            BusinessInsight.type == "risk",
            BusinessInsight.severity == "critical",
            BusinessInsight.active == True
        ).to_list()

        companies_with_critical = len(set(ins.company_id for ins in critical_insights))

        # Total counts
        total_risks = await BusinessInsight.find(
            BusinessInsight.type == "risk",
            BusinessInsight.active == True
        ).count()

        total_opportunities = await BusinessInsight.find(
            BusinessInsight.type == "opportunity",
            BusinessInsight.active == True
        ).count()

        # Risks by severity
        risks_by_severity = {}
        for sev in ["critical", "high", "medium", "low"]:
            count = await BusinessInsight.find(
                BusinessInsight.type == "risk",
                BusinessInsight.severity == sev,
                BusinessInsight.active == True
            ).count()
            risks_by_severity[sev] = count

        # Risks by category
        pipeline = [
            {"$match": {"type": "risk", "active": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        collection = BusinessInsight.get_pymongo_collection()
        cursor = collection.aggregate(pipeline)
        risks_by_category = {}
        async for r in cursor:
            if r.get("_id"):
                risks_by_category[r["_id"]] = r["count"]

        # Industries at risk (with critical/high risks)
        high_risk_insights = await BusinessInsight.find({
            "type": "risk",
            "severity": {"$in": ["critical", "high"]},
            "active": True
        }).to_list()

        company_ids_at_risk = set(ins.company_id for ins in high_risk_insights)
        companies_at_risk = await Company.find(
            {"_id": {"$in": list(company_ids_at_risk)}}
        ).to_list()
        industries_at_risk = list(set(c.industry for c in companies_at_risk))

        return AdminInsightsSummary(
            total_companies=total_companies,
            companies_with_critical_risks=companies_with_critical,
            total_risks=total_risks,
            total_opportunities=total_opportunities,
            risks_by_severity=risks_by_severity,
            risks_by_category=risks_by_category,
            industries_at_risk=industries_at_risk
        )

    @staticmethod
    async def seed_company_insights(company_id: str):
        # Sample risks
        sample_risks = [
            {
                "title": "Supply Chain Disruption Risk",
                "description": "Fuel shortage expected in Western Province may affect deliveries and increase operational costs.",
                "severity": "high",
                "category": "supply_chain",
                "impact_score": 7,
                "probability": 8
            },
            {
                "title": "Currency Depreciation Impact",
                "description": "Continued currency depreciation may increase import costs by 15-20%.",
                "severity": "medium",
                "category": "financial",
                "impact_score": 6,
                "probability": 7
            },
            {
                "title": "Labor Market Tightening",
                "description": "Skilled labor shortage in the region may affect production capacity.",
                "severity": "medium",
                "category": "workforce",
                "impact_score": 5,
                "probability": 6
            }
        ]

        # Sample opportunities
        sample_opportunities = [
            {
                "title": "Export Tax Incentive Available",
                "description": "New government tax breaks for exporters could reduce tax burden by up to 30%.",
                "severity": "high",
                "category": "financial",
                "impact_score": 8,
                "probability": 9,
                "potential_value": 8.5,
                "feasibility": 7
            },
            {
                "title": "Digital Transformation Grant",
                "description": "Government grants available for SME digital transformation initiatives.",
                "severity": "medium",
                "category": "technology",
                "impact_score": 6,
                "probability": 8,
                "potential_value": 6.0,
                "feasibility": 8
            }
        ]

        for risk_data in sample_risks:
            existing = await BusinessInsight.find_one(
                BusinessInsight.company_id == company_id,
                BusinessInsight.title == risk_data["title"]
            )

            if not existing:
                insight = BusinessInsight(
                    company_id=company_id,
                    type="risk",
                    **risk_data,
                    summary=risk_data["description"][:100] + "...",
                    recommendations=[
                        Recommendation(
                            title="Monitor situation",
                            description="Keep track of developments and prepare contingency plans.",
                            priority="high"
                        )
                    ]
                )
                await insight.insert()

        for opp_data in sample_opportunities:
            existing = await BusinessInsight.find_one(
                BusinessInsight.company_id == company_id,
                BusinessInsight.title == opp_data["title"]
            )

            if not existing:
                insight = BusinessInsight(
                    company_id=company_id,
                    type="opportunity",
                    **opp_data,
                    summary=opp_data["description"][:100] + "...",
                    recommendations=[
                        Recommendation(
                            title="Evaluate eligibility",
                            description="Review requirements and assess eligibility criteria.",
                            priority="medium"
                        )
                    ]
                )
                await insight.insert()

        logger.info(f"Business insights seeded for company {company_id}")

