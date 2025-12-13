"""
Layer 5: Dashboard Service

Bridge service that reads data from Layers 2-4 and formats it for dashboard display.
This service ONLY READS from Layer 2-4 tables, never writes to them.
Uses synchronous SQLAlchemy sessions (same pattern as L1-L4).
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, and_, or_
from pymongo import MongoClient
from pymongo.database import Database

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

    PostgreSQL: Layer 2 indicators, Layer 4 insights
    MongoDB: Layer 3 operational indicators
    """

    def __init__(
        self,
        db: Session,
        mongo_client: Optional[MongoClient] = None,
        mongo_db_name: str = "national_indicator"
    ):
        self.db = db
        self.mongo_client = mongo_client
        self.mongo_db_name = mongo_db_name

        # Initialize MongoDB connection if provided
        if mongo_client:
            self.mongo_db: Database = mongo_client[mongo_db_name]
        else:
            self.mongo_db = None
    
    # ============== National Indicators (Layer 2) ==============
    
    def get_national_indicators(
        self,
        category: Optional[str] = None,
        limit: int = 20,
        sort_by: Optional[str] = None
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
        
        result = self.db.execute(query)
        definitions = list(result.scalars().all())
        
        indicators = []
        for defn in definitions:
            # Get latest value for this indicator
            latest_value = self._get_latest_indicator_value(defn.indicator_id)
            previous_value = self._get_previous_indicator_value(defn.indicator_id)
            
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
        
        # Sort indicators if requested
        if sort_by:
            if sort_by == "value":
                indicators.sort(key=lambda x: x.current_value or 0, reverse=True)
            elif sort_by == "confidence":
                indicators.sort(key=lambda x: x.confidence or 0, reverse=True)
            elif sort_by == "change":
                indicators.sort(key=lambda x: abs(x.change_percentage or 0), reverse=True)
            elif sort_by == "impact":
                # Calculate impact score = abs(deviation from midpoint) * confidence
                def get_impact_score(ind):
                    if ind.current_value is not None and ind.confidence is not None:
                        if ind.threshold_high and ind.threshold_low:
                            midpoint = (ind.threshold_high + ind.threshold_low) / 2
                            deviation = abs(ind.current_value - midpoint)
                            return deviation * ind.confidence
                        else:
                            return abs(ind.current_value) * (ind.confidence or 1.0)
                    return 0.0
                indicators.sort(key=get_impact_score, reverse=True)

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
    
    def _get_latest_indicator_value(self, indicator_id: str) -> Optional[IndicatorValue]:
        """Get the most recent value for an indicator"""
        result = self.db.execute(
            select(IndicatorValue)
            .where(IndicatorValue.indicator_id == indicator_id)
            .order_by(desc(IndicatorValue.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    def _get_previous_indicator_value(self, indicator_id: str) -> Optional[IndicatorValue]:
        """Get the second most recent value for trend calculation"""
        result = self.db.execute(
            select(IndicatorValue)
            .where(IndicatorValue.indicator_id == indicator_id)
            .order_by(desc(IndicatorValue.timestamp))
            .offset(1)
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ============== Operational Indicators (Layer 3) ==============

    def get_operational_indicators(
        self,
        company_id: Optional[str] = None,
        limit: int = 20
    ) -> OperationalIndicatorListResponse:
        """
        Get operational indicators for a company from Layer 3 (MongoDB).

        Args:
            company_id: Company identifier (None = fetch from all companies for admin)
            limit: Maximum number of indicators to return

        Returns:
            List of operational indicators with current values
        """
        if self.mongo_db is None:
            # Return empty response if MongoDB not connected
            return OperationalIndicatorListResponse(
                company_id=company_id or "all",
                indicators=[],
                total=0,
                critical_count=0,
                warning_count=0
            )

        try:
            # Build query filter
            query_filter = {}
            if company_id:
                query_filter["company_id"] = company_id

            # Fetch latest operational calculations from MongoDB
            calculations = list(
                self.mongo_db.operational_calculations.find(
                    query_filter
                ).sort("calculation_timestamp", -1).limit(limit)
            )

            # DEVELOPMENT: If no data in MongoDB, use mock data
            if not calculations:
                return self._get_mock_operational_indicators(company_id, limit)

            indicators = []
            critical_count = 0
            warning_count = 0

            for calc in calculations:
                # Extract values from calculation
                indicator_code = calc.get("operational_indicator_code", "")
                calc_details = calc.get("calculation_details", {})
                interpretation = calc.get("interpretation", {})
                context = calc.get("context", {})

                # Get current and baseline values
                current_value = calc_details.get("final_value") or calc_details.get("rounded_value")
                baseline = context.get("industry_average")

                # Calculate deviation
                deviation = None
                if current_value is not None and baseline is not None:
                    deviation = ((current_value - baseline) / baseline) * 100 if baseline != 0 else 0

                # Determine trend
                trend = TrendDirection.STABLE
                trend_dir = context.get("trend_direction", "").lower()
                if trend_dir == "up" or trend_dir == "increasing":
                    trend = TrendDirection.UP
                elif trend_dir == "down" or trend_dir == "decreasing":
                    trend = TrendDirection.DOWN

                # Check if critical or warning
                is_critical = interpretation.get("requires_attention", False)
                severity_level = interpretation.get("level", "").lower()

                if is_critical or severity_level in ["critical", "high"]:
                    critical_count += 1
                elif severity_level == "medium":
                    warning_count += 1

                # Map indicator code to human-readable name
                indicator_name = self._get_operational_indicator_name(indicator_code)
                category = self._get_operational_indicator_category(indicator_code)

                # Determine impact score (-1 to 1)
                impact_score = 0.0
                severity_score = interpretation.get("severity_score", 0)
                if severity_score:
                    # Convert severity (0-10) to impact (-1 to 1)
                    # Higher severity = more negative impact
                    impact_score = (severity_score - 5) / 5

                # Create response object
                indicators.append(OperationalIndicatorResponse(
                    indicator_id=indicator_code,
                    indicator_name=indicator_name,
                    category=category,
                    current_value=current_value,
                    baseline_value=baseline,
                    deviation=deviation,
                    impact_score=impact_score,
                    trend=trend,
                    is_above_threshold=interpretation.get("level", "").lower() in ["high", "critical"],
                    is_below_threshold=interpretation.get("level", "").lower() == "low",
                    company_id=calc.get("company_id", company_id),
                    calculated_at=calc.get("calculation_timestamp")
                ))

            return OperationalIndicatorListResponse(
                company_id=company_id or "all",
                indicators=indicators,
                total=len(indicators),
                critical_count=critical_count,
                warning_count=warning_count
            )

        except Exception as e:
            # Log error and return empty response
            print(f"Error fetching operational indicators: {e}")
            import traceback
            traceback.print_exc()
            return OperationalIndicatorListResponse(
                company_id=company_id or "all",
                indicators=[],
                total=0,
                critical_count=0,
                warning_count=0
            )

    def _get_operational_indicator_name(self, code: str) -> str:
        """Convert operational indicator code to human-readable name"""
        name_mapping = {
            "OPS_SUPPLY_CHAIN": "Supply Chain Health",
            "OPS_TRANSPORT_AVAIL": "Transportation Availability",
            "OPS_LOGISTICS_COST": "Logistics Cost Index",
            "OPS_IMPORT_FLOW": "Import Flow Status",
            "OPS_WORKFORCE_AVAIL": "Workforce Availability",
            "OPS_LABOR_COST": "Labor Cost Index",
            "OPS_PRODUCTIVITY": "Productivity Index",
            "OPS_POWER_RELIABILITY": "Power Reliability",
            "OPS_FUEL_AVAIL": "Fuel Availability",
            "OPS_WATER_SUPPLY": "Water Supply Status",
            "OPS_INTERNET_CONNECTIVITY": "Internet Connectivity",
            "OPS_COST_PRESSURE": "Cost Pressure Index",
            "OPS_RAW_MATERIAL_COST": "Raw Material Cost",
            "OPS_ENERGY_COST": "Energy Cost Index",
            "OPS_DEMAND_LEVEL": "Demand Level",
            "OPS_COMPETITION_INTENSITY": "Competition Intensity",
            "OPS_PRICING_POWER": "Pricing Power",
            "OPS_CASH_FLOW": "Cash Flow Health",
            "OPS_CREDIT_AVAIL": "Credit Availability",
            "OPS_PAYMENT_DELAYS": "Payment Delay Index",
            "OPS_REGULATORY_BURDEN": "Regulatory Burden",
            "OPS_COMPLIANCE_COST": "Compliance Cost"
        }
        return name_mapping.get(code, code.replace("_", " ").title())

    def _get_operational_indicator_category(self, code: str) -> str:
        """Get category for operational indicator"""
        if code.startswith("OPS_SUPPLY") or code.startswith("OPS_TRANSPORT") or code.startswith("OPS_LOGISTICS") or code.startswith("OPS_IMPORT"):
            return "Supply Chain & Logistics"
        elif code.startswith("OPS_WORKFORCE") or code.startswith("OPS_LABOR") or code.startswith("OPS_PRODUCTIVITY"):
            return "Workforce & Operations"
        elif code.startswith("OPS_POWER") or code.startswith("OPS_FUEL") or code.startswith("OPS_WATER") or code.startswith("OPS_INTERNET"):
            return "Infrastructure & Resources"
        elif code.startswith("OPS_COST") or code.startswith("OPS_RAW") or code.startswith("OPS_ENERGY"):
            return "Cost Pressures"
        elif code.startswith("OPS_DEMAND") or code.startswith("OPS_COMPETITION") or code.startswith("OPS_PRICING"):
            return "Market Conditions"
        elif code.startswith("OPS_CASH") or code.startswith("OPS_CREDIT") or code.startswith("OPS_PAYMENT"):
            return "Financial Operations"
        elif code.startswith("OPS_REGULATORY") or code.startswith("OPS_COMPLIANCE"):
            return "Regulatory & Compliance"
        else:
            return "Other"

    def _get_mock_operational_indicators(self, company_id: Optional[str], limit: int) -> OperationalIndicatorListResponse:
        """Return mock operational indicators for development"""
        from datetime import datetime
        import random

        mock_indicators = [
            ("OPS_SUPPLY_CHAIN", "Supply Chain Disruption", 72, 65, "Supply Chain & Logistics", 0.3),
            ("OPS_TRANSPORT_AVAIL", "Transportation Availability", 88, 90, "Supply Chain & Logistics", -0.1),
            ("OPS_WORKFORCE_AVAIL", "Workforce Availability", 76, 80, "Workforce & Operations", 0.2),
            ("OPS_LABOR_COST", "Labor Cost Index", 115, 100, "Cost Pressures", 0.6),
            ("OPS_POWER_RELIABILITY", "Power Reliability", 92, 95, "Infrastructure & Resources", -0.2),
            ("OPS_FUEL_AVAIL", "Fuel Availability", 68, 75, "Infrastructure & Resources", 0.4),
            ("OPS_COST_PRESSURE", "Cost Pressure Index", 118, 100, "Cost Pressures", 0.7),
            ("OPS_DEMAND_LEVEL", "Demand Level", 82, 85, "Market Conditions", -0.1),
            ("OPS_CASH_FLOW", "Cash Flow Health", 71, 80, "Financial Operations", 0.3),
            ("OPS_REGULATORY_BURDEN", "Regulatory Burden", 65, 60, "Regulatory & Compliance", 0.2),
        ]

        indicators = []
        critical_count = 0
        warning_count = 0

        for code, name, current, baseline, category, impact in random.sample(mock_indicators, min(limit, len(mock_indicators))):
            deviation = ((current - baseline) / baseline) * 100 if baseline != 0 else 0
            is_critical = abs(impact) > 0.5
            is_warning = 0.2 < abs(impact) <= 0.5

            if is_critical:
                critical_count += 1
            elif is_warning:
                warning_count += 1

            trend = TrendDirection.UP if current > baseline else TrendDirection.DOWN if current < baseline else TrendDirection.STABLE

            indicators.append(OperationalIndicatorResponse(
                indicator_id=code,
                indicator_name=name,
                category=category,
                current_value=float(current),
                baseline_value=float(baseline),
                deviation=deviation,
                impact_score=impact,
                trend=trend,
                is_above_threshold=current > baseline * 1.1,
                is_below_threshold=current < baseline * 0.9,
                company_id=company_id or "MOCK_COMPANY_001",
                calculated_at=datetime.now()
            ))

        return OperationalIndicatorListResponse(
            company_id=company_id or "all",
            indicators=indicators,
            total=len(indicators),
            critical_count=critical_count,
            warning_count=warning_count
        )

    # ============== Business Insights (Layer 4) ==============
    
    def get_business_insights(
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
        
        result = self.db.execute(query)
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
    
    def get_risks(
        self,
        company_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 20
    ) -> BusinessInsightListResponse:
        """Get only risks"""
        return self.get_business_insights(
            company_id=company_id,
            insight_type="risk",
            severity=severity,
            limit=limit
        )
    
    def get_opportunities(
        self,
        company_id: Optional[str] = None,
        limit: int = 20
    ) -> BusinessInsightListResponse:
        """Get only opportunities"""
        return self.get_business_insights(
            company_id=company_id,
            insight_type="opportunity",
            limit=limit
        )
    
    # ============== Dashboard Home ==============
    
    def get_dashboard_home(self, company_id: str) -> DashboardHomeResponse:
        """
        Get complete dashboard home data for a company.
        Used by USER role.
        """
        # Get company info
        company = self._get_company(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Get insights for this company
        insights = self.get_business_insights(company_id=company_id, limit=100)
        
        # Calculate health score
        health_score = self._calculate_health_score(company_id, insights)
        
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
        
        # Get operational indicators from Layer 3
        key_indicators = self.get_operational_indicators(company_id, limit=10).indicators

        return DashboardHomeResponse(
            company_id=company_id,
            company_name=company.company_name,
            health_score=health_score,
            risk_summary=risk_summary,
            opportunity_summary=opportunity_summary,
            key_indicators=key_indicators,
            last_updated=datetime.utcnow()
        )
    
    def _get_company(self, company_id: str) -> Optional[CompanyProfile]:
        """Get company by ID"""
        result = self.db.execute(
            select(CompanyProfile).where(CompanyProfile.company_id == company_id)
        )
        return result.scalar_one_or_none()
    
    def _calculate_health_score(
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
    
    def get_admin_dashboard(self) -> AdminDashboardResponse:
        """
        Get admin dashboard overview.
        Shows aggregate data across all companies.
        """
        # Count companies
        company_count = self.db.execute(
            select(func.count(CompanyProfile.company_id))
        )
        total_companies = company_count.scalar() or 0
        
        # Count active users (placeholder - would need user count)
        total_active_users = 0
        
        # Count total national indicators (Layer 2)
        indicator_count = self.db.execute(
            select(func.count(IndicatorDefinition.indicator_id))
            .where(IndicatorDefinition.is_active == True)
        )
        total_indicators = indicator_count.scalar() or 0
        
        # Get all insights
        all_insights = self.get_business_insights(limit=1000)
        total_insights = all_insights.total
        
        # Get industries
        industry_result = self.db.execute(
            select(CompanyProfile.industry).distinct()
        )
        industries = [row[0] for row in industry_result.fetchall() if row[0]]
        
        # Build industry overviews
        industry_overviews = []
        for industry in industries:
            overview = self._get_industry_overview(industry)
            if overview:
                industry_overviews.append(overview)
        
        return AdminDashboardResponse(
            total_companies=total_companies,
            total_active_users=total_active_users,
            total_indicators=total_indicators,
            total_insights=total_insights,
            total_active_risks=all_insights.risks_count,
            total_active_opportunities=all_insights.opportunities_count,
            critical_alerts=all_insights.critical_count,
            industries=industry_overviews,
            last_updated=datetime.utcnow()
        )
    
    def _get_industry_overview(self, industry: str) -> Optional[IndustryOverviewResponse]:
        """Get overview for a specific industry"""
        # Count companies in industry
        count_result = self.db.execute(
            select(func.count(CompanyProfile.company_id))
            .where(CompanyProfile.industry == industry)
        )
        company_count = count_result.scalar() or 0
        
        if company_count == 0:
            return None
        
        # Get company IDs in this industry
        companies_result = self.db.execute(
            select(CompanyProfile.company_id)
            .where(CompanyProfile.industry == industry)
        )
        company_ids = [row[0] for row in companies_result.fetchall()]
        
        # Count insights for these companies
        insights_result = self.db.execute(
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
    
    def get_indicator_history(
        self,
        indicator_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get historical values for an indicator"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        result = self.db.execute(
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

    def get_indicator_history_batch(
        self,
        indicator_ids: List[str],
        days: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """Get historical values for multiple indicators in a single query"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Batch query for all indicators
        result = self.db.execute(
            select(IndicatorValue, IndicatorDefinition)
            .join(IndicatorDefinition, IndicatorValue.indicator_id == IndicatorDefinition.indicator_id)
            .where(IndicatorValue.indicator_id.in_(indicator_ids))
            .where(IndicatorValue.timestamp >= cutoff)
            .order_by(IndicatorValue.indicator_id, IndicatorValue.timestamp)
        )

        # Group values by indicator_id
        grouped_data: Dict[str, Dict[str, Any]] = {}

        for value, definition in result:
            if value.indicator_id not in grouped_data:
                grouped_data[value.indicator_id] = {
                    "indicator_id": value.indicator_id,
                    "indicator_name": definition.indicator_name,
                    "days": days,
                    "history": []
                }

            grouped_data[value.indicator_id]["history"].append({
                "timestamp": value.timestamp.isoformat() if value.timestamp else None,
                "value": value.value,
                "confidence": value.confidence,
                "source_count": value.source_count
            })

        return grouped_data
