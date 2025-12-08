"""
Layer 5: Dashboard Service

Bridge service that reads data from Layers 2-4 and formats it for dashboard display.
This service ONLY READS from Layer 2-4 tables, never writes to them.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_

# Layer 2 models
from app.models.indicator_models import IndicatorDefinition, IndicatorValue

# Layer 4 models
from app.models.business_insight_models import BusinessInsight
from app.models.company_profile_models import CompanyProfile

# Layer 5 schemas
from app.layer5.schemas.dashboard import (
    NationalIndicatorResponse, NationalIndicatorListResponse,
    OperationalIndicatorResponse, OperationalIndicatorListResponse,
    BusinessInsightResponse, BusinessInsightListResponse,
    DashboardHomeResponse, HealthScore, RiskSummary, OpportunitySummary,
    TrendDirection, SeverityLevel, InsightType,
    IndustryOverviewResponse, AdminDashboardResponse
)


class DashboardService:
    """
    Service for dashboard data aggregation.
    Reads from Layers 2-4 and formats for dashboard display.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============== National Indicators (Layer 2) ==============
    
    async def get_national_indicators(
        self,
        category: Optional[str] = None,
        limit: int = 20
    ) -> NationalIndicatorListResponse:
        """
        Get national indicators (Layer 2 data).
        For ADMIN dashboard - shows all 20 national indicators.
        """
        # Build query for indicator definitions
        query = select(IndicatorDefinition).where(IndicatorDefinition.is_active == True)
        
        if category:
            query = query.where(IndicatorDefinition.pestel_category == category)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        definitions = list(result.scalars().all())
        
        indicators = []
        for defn in definitions:
            # Get latest value for this indicator
            latest_value = await self._get_latest_indicator_value(defn.indicator_id)
            previous_value = await self._get_previous_indicator_value(defn.indicator_id)
            
            # Calculate change and trend
            change = None
            trend = TrendDirection.STABLE
            if latest_value and previous_value and previous_value != 0:
                change = ((latest_value.value - previous_value.value) / abs(previous_value.value)) * 100
                if change > 1:
                    trend = TrendDirection.UP
                elif change < -1:
                    trend = TrendDirection.DOWN
            
            # Determine status based on thresholds
            status = "normal"
            if latest_value:
                if defn.threshold_high and latest_value.value >= defn.threshold_high:
                    status = "critical"
                elif defn.threshold_low and latest_value.value <= defn.threshold_low:
                    status = "warning"
            
            indicators.append(NationalIndicatorResponse(
                indicator_id=defn.indicator_id,
                indicator_name=defn.indicator_name,
                pestel_category=str(defn.pestel_category) if defn.pestel_category else "Unknown",
                description=defn.description,
                current_value=latest_value.value if latest_value else None,
                previous_value=previous_value.value if previous_value else None,
                change_percentage=change,
                trend=trend,
                threshold_high=defn.threshold_high,
                threshold_low=defn.threshold_low,
                status=status,
                last_updated=latest_value.timestamp if latest_value else None,
                confidence=latest_value.confidence if latest_value else None,
                source_count=latest_value.source_count if latest_value else None
            ))
        
        # Count by category
        category_counts = {}
        for ind in indicators:
            cat = ind.pestel_category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return NationalIndicatorListResponse(
            indicators=indicators,
            total=len(indicators),
            by_category=category_counts
        )
    
    async def _get_latest_indicator_value(self, indicator_id: str) -> Optional[IndicatorValue]:
        """Get the most recent value for an indicator"""
        result = await self.db.execute(
            select(IndicatorValue)
            .where(IndicatorValue.indicator_id == indicator_id)
            .order_by(desc(IndicatorValue.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def _get_previous_indicator_value(self, indicator_id: str) -> Optional[IndicatorValue]:
        """Get the second most recent value for trend calculation"""
        result = await self.db.execute(
            select(IndicatorValue)
            .where(IndicatorValue.indicator_id == indicator_id)
            .order_by(desc(IndicatorValue.timestamp))
            .offset(1)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    # ============== Business Insights (Layer 4) ==============
    
    async def get_business_insights(
        self,
        company_id: Optional[str] = None,
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: str = "active",
        limit: int = 20,
        offset: int = 0
    ) -> BusinessInsightListResponse:
        """
        Get business insights from Layer 4.
        If company_id is provided, filters to that company (USER role).
        If not, returns all insights (ADMIN role).
        """
        query = select(BusinessInsight)
        
        # Apply filters
        conditions = []
        if company_id:
            conditions.append(BusinessInsight.company_id == company_id)
        if insight_type:
            conditions.append(BusinessInsight.insight_type == insight_type)
        if severity:
            conditions.append(BusinessInsight.severity_level == severity)
        if status:
            conditions.append(BusinessInsight.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Order by urgency and detection time
        query = query.order_by(
            desc(BusinessInsight.is_urgent),
            desc(BusinessInsight.detected_at)
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        insights = list(result.scalars().all())
        
        # Convert to response schema
        insight_responses = [
            BusinessInsightResponse(
                insight_id=i.insight_id,
                company_id=i.company_id,
                insight_type=InsightType(i.insight_type) if i.insight_type else InsightType.RISK,
                category=i.category or "",
                title=i.title,
                description=i.description,
                probability=float(i.probability) if i.probability else None,
                impact=float(i.impact) if i.impact else None,
                urgency=i.urgency,
                final_score=float(i.final_score) if i.final_score else None,
                severity_level=SeverityLevel(i.severity_level) if i.severity_level else None,
                confidence=float(i.confidence) if i.confidence else None,
                detected_at=i.detected_at or datetime.utcnow(),
                expected_impact_time=i.expected_impact_time,
                expected_duration_hours=i.expected_duration_hours,
                status=i.status or "active",
                is_urgent=i.is_urgent or False,
                requires_immediate_action=i.requires_immediate_action or False,
                priority_rank=i.priority_rank,
                triggering_indicators=i.triggering_indicators,
                affected_operations=i.affected_operations
            )
            for i in insights
        ]
        
        # Calculate counts
        risks_count = sum(1 for i in insight_responses if i.insight_type == InsightType.RISK)
        opportunities_count = sum(1 for i in insight_responses if i.insight_type == InsightType.OPPORTUNITY)
        critical_count = sum(1 for i in insight_responses if i.severity_level == SeverityLevel.CRITICAL)
        
        # Count by category
        by_category = {}
        for i in insight_responses:
            cat = i.category
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return BusinessInsightListResponse(
            insights=insight_responses,
            total=len(insight_responses),
            risks_count=risks_count,
            opportunities_count=opportunities_count,
            critical_count=critical_count,
            by_category=by_category
        )
    
    async def get_risks(
        self,
        company_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 20
    ) -> BusinessInsightListResponse:
        """Get only risks"""
        return await self.get_business_insights(
            company_id=company_id,
            insight_type="risk",
            severity=severity,
            limit=limit
        )
    
    async def get_opportunities(
        self,
        company_id: Optional[str] = None,
        limit: int = 20
    ) -> BusinessInsightListResponse:
        """Get only opportunities"""
        return await self.get_business_insights(
            company_id=company_id,
            insight_type="opportunity",
            limit=limit
        )
    
    # ============== Dashboard Home ==============
    
    async def get_dashboard_home(self, company_id: str) -> DashboardHomeResponse:
        """
        Get complete dashboard home data for a company.
        Used by USER role.
        """
        # Get company info
        company = await self._get_company(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Get insights for this company
        insights = await self.get_business_insights(company_id=company_id, limit=100)
        
        # Calculate health score
        health_score = await self._calculate_health_score(company_id, insights)
        
        # Build risk summary
        risk_insights = [i for i in insights.insights if i.insight_type == InsightType.RISK]
        risk_summary = RiskSummary(
            total_active=len(risk_insights),
            critical=sum(1 for r in risk_insights if r.severity_level == SeverityLevel.CRITICAL),
            high=sum(1 for r in risk_insights if r.severity_level == SeverityLevel.HIGH),
            medium=sum(1 for r in risk_insights if r.severity_level == SeverityLevel.MEDIUM),
            low=sum(1 for r in risk_insights if r.severity_level == SeverityLevel.LOW),
            recent_risks=risk_insights[:5],
            trend=TrendDirection.STABLE  # TODO: Calculate from historical data
        )
        
        # Build opportunity summary
        opp_insights = [i for i in insights.insights if i.insight_type == InsightType.OPPORTUNITY]
        opportunity_summary = OpportunitySummary(
            total_active=len(opp_insights),
            high_potential=sum(1 for o in opp_insights if o.severity_level in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]),
            medium_potential=sum(1 for o in opp_insights if o.severity_level == SeverityLevel.MEDIUM),
            low_potential=sum(1 for o in opp_insights if o.severity_level == SeverityLevel.LOW),
            recent_opportunities=opp_insights[:5],
            trend=TrendDirection.STABLE
        )
        
        # Get key indicators (placeholder - would need Layer 3 operational indicators)
        key_indicators: List[OperationalIndicatorResponse] = []
        
        return DashboardHomeResponse(
            company_id=company_id,
            company_name=company.company_name,
            health_score=health_score,
            risk_summary=risk_summary,
            opportunity_summary=opportunity_summary,
            key_indicators=key_indicators,
            last_updated=datetime.utcnow()
        )
    
    async def _get_company(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company by ID"""
        result = await self.db.execute(
            select(CompanyProfile).where(CompanyProfile.company_id == company_id)
        )
        return result.scalar_one_or_none()
    
    async def _calculate_health_score(
        self, 
        company_id: str, 
        insights: BusinessInsightListResponse
    ) -> HealthScore:
        """
        Calculate company health score based on insights.
        Score is 0-100 where 100 is healthiest.
        """
        # Base score
        base_score = 100.0
        
        # Deduct for risks based on severity
        for insight in insights.insights:
            if insight.insight_type == InsightType.RISK:
                if insight.severity_level == SeverityLevel.CRITICAL:
                    base_score -= 15
                elif insight.severity_level == SeverityLevel.HIGH:
                    base_score -= 10
                elif insight.severity_level == SeverityLevel.MEDIUM:
                    base_score -= 5
                elif insight.severity_level == SeverityLevel.LOW:
                    base_score -= 2
        
        # Add for opportunities (max 20 bonus)
        opportunity_bonus = min(20, insights.opportunities_count * 3)
        
        # Final score (clamped to 0-100)
        final_score = max(0, min(100, base_score + opportunity_bonus))
        
        # Determine trend (placeholder)
        trend = TrendDirection.STABLE
        if final_score > 70:
            trend = TrendDirection.UP
        elif final_score < 40:
            trend = TrendDirection.DOWN
        
        return HealthScore(
            overall_score=final_score,
            trend=trend,
            components={
                "risk_score": max(0, base_score),
                "opportunity_score": opportunity_bonus,
            },
            last_calculated=datetime.utcnow()
        )
    
    # ============== Admin Dashboard ==============
    
    async def get_admin_dashboard(self) -> AdminDashboardResponse:
        """
        Get admin dashboard overview.
        Shows aggregate data across all companies.
        """
        # Count companies
        company_count = await self.db.execute(
            select(func.count(CompanyProfile.company_id))
        )
        total_companies = company_count.scalar() or 0
        
        # Count active users (placeholder - would need user count)
        total_active_users = 0
        
        # Get all insights
        all_insights = await self.get_business_insights(limit=1000)
        
        # Get industries
        industry_result = await self.db.execute(
            select(CompanyProfile.industry).distinct()
        )
        industries = [row[0] for row in industry_result.fetchall() if row[0]]
        
        # Build industry overviews
        industry_overviews = []
        for industry in industries:
            overview = await self._get_industry_overview(industry)
            if overview:
                industry_overviews.append(overview)
        
        return AdminDashboardResponse(
            total_companies=total_companies,
            total_active_users=total_active_users,
            total_active_risks=all_insights.risks_count,
            total_active_opportunities=all_insights.opportunities_count,
            critical_alerts=all_insights.critical_count,
            industries=industry_overviews,
            last_updated=datetime.utcnow()
        )
    
    async def _get_industry_overview(self, industry: str) -> Optional[IndustryOverviewResponse]:
        """Get overview for a specific industry"""
        # Count companies in industry
        count_result = await self.db.execute(
            select(func.count(CompanyProfile.company_id))
            .where(CompanyProfile.industry == industry)
        )
        company_count = count_result.scalar() or 0
        
        if company_count == 0:
            return None
        
        # Get company IDs in this industry
        companies_result = await self.db.execute(
            select(CompanyProfile.company_id)
            .where(CompanyProfile.industry == industry)
        )
        company_ids = [row[0] for row in companies_result.fetchall()]
        
        # Count insights for these companies
        insights_result = await self.db.execute(
            select(
                BusinessInsight.insight_type,
                BusinessInsight.severity_level,
                func.count(BusinessInsight.insight_id)
            )
            .where(BusinessInsight.company_id.in_(company_ids))
            .where(BusinessInsight.status == 'active')
            .group_by(BusinessInsight.insight_type, BusinessInsight.severity_level)
        )
        
        total_risks = 0
        total_opportunities = 0
        critical_risks = 0
        
        for row in insights_result.fetchall():
            insight_type, severity, count = row
            if insight_type == 'risk':
                total_risks += count
                if severity == 'critical':
                    critical_risks += count
            elif insight_type == 'opportunity':
                total_opportunities += count
        
        return IndustryOverviewResponse(
            industry=industry,
            company_count=company_count,
            average_health_score=75.0,  # Placeholder
            total_active_risks=total_risks,
            total_active_opportunities=total_opportunities,
            critical_risks=critical_risks,
            top_risk_indicators=[],  # Would need to aggregate
            top_opportunity_indicators=[]
        )
    
    # ============== Indicator Trends ==============
    
    async def get_indicator_history(
        self,
        indicator_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get historical values for an indicator"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(IndicatorValue)
            .where(IndicatorValue.indicator_id == indicator_id)
            .where(IndicatorValue.timestamp >= cutoff)
            .order_by(IndicatorValue.timestamp)
        )
        
        values = result.scalars().all()
        
        return [
            {
                "timestamp": v.timestamp.isoformat() if v.timestamp else None,
                "value": v.value,
                "confidence": v.confidence,
                "source_count": v.source_count
            }
            for v in values
        ]
