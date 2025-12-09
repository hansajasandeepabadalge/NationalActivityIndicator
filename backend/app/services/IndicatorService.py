from datetime import datetime, timezone, timedelta
from typing import List, Dict
from loguru import logger

from app.models.Indicator import (
    NationalIndicator,
    OperationalIndicatorValue,
    NATIONAL_INDICATORS,
    OPERATIONAL_INDICATORS
)
from app.models.company import Company
from app.schemas.Indicator import (
    NationalIndicatorResponse,
    NationalIndicatorsGrouped,
    OperationalIndicatorResponse,
    IndicatorHistoryResponse,
    IndicatorHistoryPoint,
    HealthScoreResponse,
    IndustryIndicatorSummary
)
from app.db.redis import RedisCache, cache_key


class IndicatorService:

    # Cache keys
    NATIONAL_INDICATORS_CACHE = "national_indicators"
    OPERATIONAL_INDICATORS_CACHE = "operational_indicators"

    @staticmethod
    async def get_all_national_indicators() -> List[NationalIndicatorResponse]:
        # Try cache first
        cached = await RedisCache.get(IndicatorService.NATIONAL_INDICATORS_CACHE)
        if cached:
            return [NationalIndicatorResponse(**item) for item in cached]

        indicators = await NationalIndicator.find_all().to_list()

        result = []
        for ind in indicators:
            result.append(NationalIndicatorResponse(
                id=str(ind.id),
                indicator_name=ind.indicator_name,
                category=ind.category,
                value=ind.value,
                trend=ind.trend,
                trend_change=ind.trend_change,
                display_name=ind.display_name,
                description=ind.description,
                icon=ind.icon,
                status=ind.status,
                status_color=ind.status_color,
                calculated_at=ind.calculated_at
            ))

        # Cache results
        await RedisCache.set(
            IndicatorService.NATIONAL_INDICATORS_CACHE,
            [r.model_dump() for r in result],
            ttl=300  # 5 minutes
        )

        return result

    @staticmethod
    async def get_national_indicators_grouped() -> NationalIndicatorsGrouped:
        indicators = await IndicatorService.get_all_national_indicators()

        grouped = {
            "political": [],
            "economic": [],
            "social": [],
            "infrastructure": []
        }

        for ind in indicators:
            if ind.category in grouped:
                grouped[ind.category].append(ind)

        return NationalIndicatorsGrouped(**grouped)

    @staticmethod
    async def get_national_indicator_history(
            indicator_name: str,
            days: int = 30
    ) -> IndicatorHistoryResponse:
        indicator = await NationalIndicator.find_one(
            NationalIndicator.indicator_name == indicator_name
        )

        if not indicator:
            return IndicatorHistoryResponse(
                indicator_name=indicator_name,
                data_points=[]
            )

        # Filter history to requested days
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        history = [
            IndicatorHistoryPoint(value=h.value, recorded_at=h.recorded_at)
            for h in indicator.history
            if h.recorded_at >= cutoff
        ]

        return IndicatorHistoryResponse(
            indicator_name=indicator_name,
            data_points=history
        )

    @staticmethod
    async def get_company_indicators(
            company_id: str
    ) -> List[OperationalIndicatorResponse]:
        cache_key_str = cache_key(IndicatorService.OPERATIONAL_INDICATORS_CACHE, company_id)

        # Try cache
        cached = await RedisCache.get(cache_key_str)
        if cached:
            return [OperationalIndicatorResponse(**item) for item in cached]

        indicators = await OperationalIndicatorValue.find(
            OperationalIndicatorValue.company_id == company_id
        ).to_list()

        result = []
        for ind in indicators:
            result.append(OperationalIndicatorResponse(
                id=str(ind.id),
                company_id=ind.company_id,
                indicator_name=ind.indicator_name,
                value=ind.value,
                trend=ind.trend,
                trend_change=ind.trend_change,
                display_name=ind.display_name,
                status=ind.status,
                contributing_factors=ind.contributing_factors,
                calculated_at=ind.calculated_at
            ))

        # Cache results
        await RedisCache.set(cache_key_str, [r.model_dump() for r in result], ttl=300)

        return result

    @staticmethod
    async def get_company_health_score(company_id: str) -> HealthScoreResponse:
        indicators = await IndicatorService.get_company_indicators(company_id)

        if not indicators:
            return HealthScoreResponse(
                health_score=0,
                trend="stable",
                trend_change=None,
                indicators=[],
                last_updated=datetime.now(timezone.utc)
            )

        # Calculate health score as average of all indicators
        values = [ind.value for ind in indicators]
        health_score = sum(values) / len(values)

        # Determine trend from individual trends
        up_count = sum(1 for ind in indicators if ind.trend == "up")
        down_count = sum(1 for ind in indicators if ind.trend == "down")

        if up_count > down_count:
            trend = "up"
        elif down_count > up_count:
            trend = "down"
        else:
            trend = "stable"

        # Calculate trend change
        changes = [ind.trend_change for ind in indicators if ind.trend_change is not None]
        trend_change = sum(changes) / len(changes) if changes else None

        last_updated = max(ind.calculated_at for ind in indicators)

        return HealthScoreResponse(
            health_score=round(health_score, 1),
            trend=trend,
            trend_change=round(trend_change, 1) if trend_change else None,
            indicators=indicators,
            last_updated=last_updated
        )

    @staticmethod
    async def get_industry_indicators_summary(
            industry: str
    ) -> IndustryIndicatorSummary:
        # Get all companies in industry
        companies = await Company.find(Company.industry == industry).to_list()
        company_ids = [str(c.id) for c in companies]

        if not company_ids:
            return IndustryIndicatorSummary(
                industry=industry,
                company_count=0,
                avg_indicators={},
                indicator_distribution={}
            )

        # Get all indicators for these companies
        indicators = await OperationalIndicatorValue.find(
            {"company_id": {"$in": company_ids}}
        ).to_list()

        # Aggregate by indicator name
        indicator_values: Dict[str, List[float]] = {}
        indicator_statuses: Dict[str, Dict[str, int]] = {}

        for ind in indicators:
            name = ind.indicator_name

            if name not in indicator_values:
                indicator_values[name] = []
                indicator_statuses[name] = {"good": 0, "warning": 0, "critical": 0}

            indicator_values[name].append(ind.value)
            indicator_statuses[name][ind.status] += 1

        # Calculate averages
        avg_indicators = {
            name: round(sum(values) / len(values), 1)
            for name, values in indicator_values.items()
        }

        return IndustryIndicatorSummary(
            industry=industry,
            company_count=len(companies),
            avg_indicators=avg_indicators,
            indicator_distribution=indicator_statuses
        )

    @staticmethod
    async def seed_national_indicators():
        import random

        for category, indicators in NATIONAL_INDICATORS.items():
            for ind_data in indicators:
                existing = await NationalIndicator.find_one(
                    NationalIndicator.indicator_name == ind_data["name"]
                )

                if not existing:
                    value = random.uniform(40, 85)
                    indicator = NationalIndicator(
                        indicator_name=ind_data["name"],
                        category=category,
                        value=round(value, 1),
                        trend=random.choice(["up", "down", "stable"]),
                        trend_change=round(random.uniform(-5, 5), 1),
                        display_name=ind_data["display_name"],
                        description=f"Current {ind_data['display_name']} measurement"
                    )
                    await indicator.insert()

        logger.info("National indicators seeded")

    @staticmethod
    async def seed_company_indicators(company_id: str):
        import random

        for ind_data in OPERATIONAL_INDICATORS:
            existing = await OperationalIndicatorValue.find_one(
                OperationalIndicatorValue.company_id == company_id,
                OperationalIndicatorValue.indicator_name == ind_data["name"]
            )

            if not existing:
                value = random.uniform(50, 90)
                indicator = OperationalIndicatorValue(
                    company_id=company_id,
                    indicator_name=ind_data["name"],
                    value=round(value, 1),
                    trend=random.choice(["up", "down", "stable"]),
                    trend_change=round(random.uniform(-5, 5), 1),
                    display_name=ind_data["display_name"]
                )
                await indicator.insert()

        logger.info(f"Operational indicators seeded for company {company_id}")