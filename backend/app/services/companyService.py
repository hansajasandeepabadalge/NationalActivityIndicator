from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from loguru import logger
from beanie import PydanticObjectId

from app.models.company import Company, OperationalProfile, RiskSensitivity
from app.models.user import User
from app.models.insight import BusinessInsight
from app.schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyListItem,
    IndustryAggregation
)


class CompanyService:

    @staticmethod
    async def create_company(user_id: str, company_data: CompanyCreate) -> Company:
        # Check if user already has a company
        existing = await Company.find_one(Company.user_id == user_id)
        if existing:
            raise ValueError("User already has a company profile")

        # Create company
        company = Company(
            user_id=user_id,
            company_name=company_data.company_name,
            industry=company_data.industry,
            business_scale=company_data.business_scale,
            location_province=company_data.location_province,
            location_city=company_data.location_city,
            num_employees=company_data.num_employees,
            year_established=company_data.year_established,
            annual_revenue_range=company_data.annual_revenue_range,
            profile_data=company_data.profile_data or {}
        )

        # Set operational profile if provided
        if company_data.operational_profile:
            company.operational_profile = OperationalProfile(
                **company_data.operational_profile.model_dump()
            )

        # Set risk sensitivity if provided
        if company_data.risk_sensitivity:
            company.risk_sensitivity = RiskSensitivity(
                **company_data.risk_sensitivity.model_dump()
            )

        await company.insert()

        # Update user with company_id
        user = await User.get(user_id)
        if user:
            user.company_id = str(company.id)
            await user.save()

        logger.info(f"Company created: {company.company_name} for user {user_id}")
        return company

    @staticmethod
    async def get_company_by_user(user_id: str) -> Optional[Company]:
        return await Company.find_one(Company.user_id == user_id)

    @staticmethod
    async def get_company_by_id(company_id: str) -> Optional[Company]:
        try:
            return await Company.get(company_id)
        except Exception:
            return None

    @staticmethod
    async def update_company(
            company: Company,
            update_data: CompanyUpdate
    ) -> Company:
        update_dict = update_data.model_dump(exclude_unset=True)

        # Handle nested objects
        if "operational_profile" in update_dict and update_dict["operational_profile"]:
            company.operational_profile = OperationalProfile(
                **update_dict.pop("operational_profile")
            )

        if "risk_sensitivity" in update_dict and update_dict["risk_sensitivity"]:
            company.risk_sensitivity = RiskSensitivity(
                **update_dict.pop("risk_sensitivity")
            )

        # Update remaining fields
        for field, value in update_dict.items():
            if hasattr(company, field):
                setattr(company, field, value)

        company.update_timestamp()
        await company.save()

        logger.info(f"Company updated: {company.company_name}")
        return company

    @staticmethod
    async def get_all_companies(
            industry: Optional[str] = None,
            page: int = 1,
            page_size: int = 20
    ) -> tuple[List[Company], int]:
        query = Company.find()

        if industry:
            query = query.find(Company.industry == industry)

        total = await query.count()

        companies = await query.skip((page - 1) * page_size).limit(page_size).to_list()

        return companies, total

    @staticmethod
    async def get_company_list_with_risks() -> List[CompanyListItem]:

        companies = await Company.find_all().to_list()
        result = []

        for company in companies:
            # Count risks for this company
            risk_count = await BusinessInsight.find(
                BusinessInsight.company_id == str(company.id),
                BusinessInsight.type == "risk",
                BusinessInsight.active == True
            ).count()

            critical_risks = await BusinessInsight.find(
                BusinessInsight.company_id == str(company.id),
                BusinessInsight.type == "risk",
                BusinessInsight.severity == "critical",
                BusinessInsight.active == True
            ).count()

            result.append(CompanyListItem(
                id=str(company.id),
                company_name=company.company_name,
                industry=company.industry,
                business_scale=company.business_scale,
                location_province=company.location_province,
                health_score=company.health_score,
                risk_count=risk_count,
                critical_risks=critical_risks
            ))

        return result

    @staticmethod
    async def get_industry_aggregation(industry: str) -> IndustryAggregation:
        companies = await Company.find(Company.industry == industry).to_list()

        if not companies:
            return IndustryAggregation(
                industry=industry,
                company_count=0
            )

        # Calculate averages
        health_scores = [c.health_score for c in companies if c.health_score is not None]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else None

        # Count companies at risk vs healthy
        companies_at_risk = sum(1 for c in companies if c.health_score and c.health_score < 50)
        companies_healthy = sum(1 for c in companies if c.health_score and c.health_score >= 70)

        return IndustryAggregation(
            industry=industry,
            company_count=len(companies),
            avg_health_score=avg_health,
            companies_at_risk=companies_at_risk,
            companies_healthy=companies_healthy
        )

    @staticmethod
    async def get_all_industries() -> List[str]:
        pipeline = [
            {"$group": {"_id": "$industry"}},
            {"$sort": {"_id": 1}}
        ]

        # Use the collection directly for aggregation
        collection = Company.get_pymongo_collection()
        cursor = collection.aggregate(pipeline)
        result = []
        async for doc in cursor:
            if doc.get("_id"):
                result.append(doc["_id"])
        return result

    @staticmethod
    def company_to_response(company: Company) -> CompanyResponse:
        return CompanyResponse(
            id=str(company.id),
            user_id=company.user_id,
            company_name=company.company_name,
            industry=company.industry,
            business_scale=company.business_scale,
            location_province=company.location_province,
            location_city=company.location_city,
            num_employees=company.num_employees,
            year_established=company.year_established,
            annual_revenue_range=company.annual_revenue_range,
            operational_profile=company.operational_profile.model_dump(),
            risk_sensitivity=company.risk_sensitivity.model_dump(),
            profile_data=company.profile_data,
            health_score=company.health_score,
            created_at=company.created_at,
            updated_at=company.updated_at
        )