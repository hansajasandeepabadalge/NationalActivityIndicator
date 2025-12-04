"""
Layer 4: Business Insights API Endpoints

Provides risk detection, opportunity detection, and recommendation endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.layer4.schemas import (
    DetectedRisk,
    RiskWithScore,
    RiskScoreBreakdown,
    DetectedOpportunity,
    OpportunityWithScore,
    OpportunityScoreBreakdown,
    Recommendation,
    RecommendationCreate,
    ActionPlan,
    ActionPlanStep,
    NarrativeContent,
    InsightWithRecommendations,
    InsightPriority,
    TopPriorities,
)
from app.layer4.risk_detection import RuleBasedRiskDetector, PatternBasedRiskDetector
from app.layer4.opportunity_detection import RuleBasedOpportunityDetector
from app.layer4.recommendation import RecommendationEngine
from app.layer4.scoring import RiskScorer
from app.layer4.prioritization import InsightPrioritizer
from app.layer4.mock_data.layer3_mock_generator import OperationalIndicators

router = APIRouter()

# Initialize detectors and engines
risk_detector = RuleBasedRiskDetector()
pattern_detector = PatternBasedRiskDetector()
opportunity_detector = RuleBasedOpportunityDetector()
recommendation_engine = RecommendationEngine()
risk_scorer = RiskScorer()
insight_prioritizer = InsightPrioritizer()


# ==============================================================================
# Risk Detection Endpoints
# ==============================================================================

@router.post("/risks/detect", response_model=List[DetectedRisk])
async def detect_risks(
    company_id: str,
    industry: str = Query("manufacturing", description="Company industry"),
    layer3_data: Optional[Dict[str, Any]] = None,
):
    """
    Detect risks for a company based on operational indicators.
    
    If layer3_data is not provided, the latest Layer 3 data will be fetched.
    """
    try:
        # Use mock data if no Layer 3 data provided
        if layer3_data is None:
            layer3_data = _get_mock_layer3_data()
        
        # Convert to OperationalIndicators
        indicators = _create_operational_indicators(layer3_data)
        
        # Detect risks using rule-based detector
        risks = risk_detector.detect_risks(
            company_id=company_id,
            industry=industry,
            indicators=indicators,
        )
        
        return risks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk detection failed: {str(e)}")


@router.get("/risks", response_model=List[RiskWithScore])
async def list_risks(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    category: Optional[str] = Query(None, description="Filter by risk category"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List detected risks with optional filtering.
    """
    # In production, this would query the database
    # For now, return mock data
    risks = _get_mock_risks(company_id, category, severity)
    
    # Apply pagination
    return risks[offset:offset + limit]


@router.get("/risks/{risk_id}", response_model=RiskWithScore)
async def get_risk(risk_id: int):
    """
    Get detailed information about a specific risk.
    """
    # In production, this would query the database
    mock_risks = _get_mock_risks()
    
    for risk in mock_risks:
        if risk.insight_id == risk_id:
            return risk
    
    raise HTTPException(status_code=404, detail="Risk not found")


@router.get("/risks/{risk_id}/score-breakdown", response_model=RiskScoreBreakdown)
async def get_risk_score_breakdown(risk_id: int):
    """
    Get detailed score breakdown for a risk.
    """
    mock_risks = _get_mock_risks()
    
    for risk in mock_risks:
        if risk.insight_id == risk_id:
            return risk.score_breakdown
    
    raise HTTPException(status_code=404, detail="Risk not found")


@router.post("/risks/{risk_id}/acknowledge")
async def acknowledge_risk(
    risk_id: int,
    acknowledged_by: str,
    notes: Optional[str] = None,
):
    """
    Acknowledge a risk has been reviewed.
    """
    # In production, this would update the database
    return {
        "success": True,
        "risk_id": risk_id,
        "acknowledged_by": acknowledged_by,
        "acknowledged_at": datetime.now().isoformat(),
    }


@router.post("/risks/{risk_id}/resolve")
async def resolve_risk(
    risk_id: int,
    resolution_notes: str,
    actual_impact: Optional[str] = None,
    actual_outcome: Optional[str] = None,
):
    """
    Mark a risk as resolved.
    """
    # In production, this would update the database
    return {
        "success": True,
        "risk_id": risk_id,
        "status": "resolved",
        "resolved_at": datetime.now().isoformat(),
    }


# ==============================================================================
# Opportunity Detection Endpoints
# ==============================================================================

@router.post("/opportunities/detect", response_model=List[DetectedOpportunity])
async def detect_opportunities(
    company_id: str,
    industry: str = Query("manufacturing", description="Company industry"),
    layer3_data: Optional[Dict[str, Any]] = None,
):
    """
    Detect opportunities for a company based on operational indicators.
    
    If layer3_data is not provided, the latest Layer 3 data will be fetched.
    """
    try:
        # Use mock data if no Layer 3 data provided
        if layer3_data is None:
            layer3_data = _get_mock_layer3_data()
        
        # Convert to OperationalIndicators
        indicators = _create_operational_indicators(layer3_data)
        
        # Detect opportunities using rule-based detector
        opportunities = opportunity_detector.detect_opportunities(
            company_id=company_id,
            industry=industry,
            indicators=indicators,
        )
        
        return opportunities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Opportunity detection failed: {str(e)}")


@router.get("/opportunities", response_model=List[OpportunityWithScore])
async def list_opportunities(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    category: Optional[str] = Query(None, description="Filter by opportunity category"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List detected opportunities with optional filtering.
    """
    # In production, this would query the database
    opportunities = _get_mock_opportunities(company_id, category, priority)
    
    # Apply pagination
    return opportunities[offset:offset + limit]


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityWithScore)
async def get_opportunity(opportunity_id: int):
    """
    Get detailed information about a specific opportunity.
    """
    mock_opportunities = _get_mock_opportunities()
    
    for opp in mock_opportunities:
        if opp.insight_id == opportunity_id:
            return opp
    
    raise HTTPException(status_code=404, detail="Opportunity not found")


@router.post("/opportunities/{opportunity_id}/capture")
async def capture_opportunity(
    opportunity_id: int,
    captured_by: str,
    action_taken: str,
    expected_benefit: str,
):
    """
    Mark an opportunity as being acted upon.
    """
    return {
        "success": True,
        "opportunity_id": opportunity_id,
        "captured_by": captured_by,
        "captured_at": datetime.now().isoformat(),
    }


# ==============================================================================
# Recommendation Endpoints
# ==============================================================================

@router.post("/recommendations/generate", response_model=List[Recommendation])
async def generate_recommendations(
    insight_type: str = Query(..., description="'risk' or 'opportunity'"),
    insight_id: int = Query(..., description="ID of the risk or opportunity"),
):
    """
    Generate recommendations for a specific risk or opportunity.
    """
    try:
        if insight_type == "risk":
            # Get risk and generate recommendations
            mock_risks = _get_mock_risks()
            for risk in mock_risks:
                if risk.insight_id == insight_id:
                    detected_risk = _risk_with_score_to_detected_risk(risk)
                    rec_creates = recommendation_engine.generate_recommendations(detected_risk)
                    # Convert to Recommendation objects with IDs
                    recommendations = []
                    for i, rc in enumerate(rec_creates):
                        recommendations.append(Recommendation(
                            recommendation_id=i + 1,
                            insight_id=insight_id,
                            category=rc.category,
                            priority=rc.priority,
                            action_title=rc.action_title,
                            action_description=rc.action_description,
                            responsible_role=rc.responsible_role,
                            estimated_effort=rc.estimated_effort,
                            estimated_cost=rc.estimated_cost,
                            estimated_timeframe=rc.estimated_timeframe,
                            expected_benefit=rc.expected_benefit,
                            success_metrics=rc.success_metrics,
                            required_resources=rc.required_resources,
                            status="pending",
                            created_at=datetime.now(),
                        ))
                    return recommendations
            raise HTTPException(status_code=404, detail="Risk not found")
        
        elif insight_type == "opportunity":
            # Get opportunity and generate recommendations
            mock_opps = _get_mock_opportunities()
            for opp in mock_opps:
                if opp.insight_id == insight_id:
                    detected_opp = _opportunity_with_score_to_detected(opp)
                    rec_creates = recommendation_engine.generate_recommendations(detected_opp)
                    # Convert to Recommendation objects with IDs
                    recommendations = []
                    for i, rc in enumerate(rec_creates):
                        recommendations.append(Recommendation(
                            recommendation_id=i + 1,
                            insight_id=insight_id,
                            category=rc.category,
                            priority=rc.priority,
                            action_title=rc.action_title,
                            action_description=rc.action_description,
                            responsible_role=rc.responsible_role,
                            estimated_effort=rc.estimated_effort,
                            estimated_cost=rc.estimated_cost,
                            estimated_timeframe=rc.estimated_timeframe,
                            expected_benefit=rc.expected_benefit,
                            success_metrics=rc.success_metrics,
                            required_resources=rc.required_resources,
                            status="pending",
                            created_at=datetime.now(),
                        ))
                    return recommendations
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid insight_type. Use 'risk' or 'opportunity'")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@router.get("/recommendations", response_model=List[Recommendation])
async def list_recommendations(
    insight_id: Optional[int] = Query(None, description="Filter by insight ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List recommendations with optional filtering.
    """
    recommendations = _get_mock_recommendations(insight_id, status, category)
    return recommendations[offset:offset + limit]


@router.get("/recommendations/{recommendation_id}", response_model=Recommendation)
async def get_recommendation(recommendation_id: int):
    """
    Get a specific recommendation.
    """
    recommendations = _get_mock_recommendations()
    
    for rec in recommendations:
        if rec.recommendation_id == recommendation_id:
            return rec
    
    raise HTTPException(status_code=404, detail="Recommendation not found")


@router.post("/recommendations/{recommendation_id}/assign")
async def assign_recommendation(
    recommendation_id: int,
    assigned_to: str,
):
    """
    Assign a recommendation to someone.
    """
    return {
        "success": True,
        "recommendation_id": recommendation_id,
        "assigned_to": assigned_to,
        "assigned_at": datetime.now().isoformat(),
    }


@router.post("/recommendations/{recommendation_id}/complete")
async def complete_recommendation(
    recommendation_id: int,
    implementation_notes: str,
    outcome_achieved: bool,
    actual_benefit: Optional[str] = None,
):
    """
    Mark a recommendation as completed.
    """
    return {
        "success": True,
        "recommendation_id": recommendation_id,
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
    }


# ==============================================================================
# Action Plan Endpoints
# ==============================================================================

@router.post("/action-plans/generate", response_model=ActionPlan)
async def generate_action_plan(
    insight_type: str = Query(..., description="'risk' or 'opportunity'"),
    insight_id: int = Query(..., description="ID of the risk or opportunity"),
):
    """
    Generate a comprehensive action plan for an insight.
    """
    try:
        if insight_type == "risk":
            mock_risks = _get_mock_risks()
            for risk in mock_risks:
                if risk.insight_id == insight_id:
                    detected_risk = _risk_with_score_to_detected_risk(risk)
                    rec_creates = recommendation_engine.generate_recommendations(detected_risk)
                    action_plan = recommendation_engine.create_action_plan(detected_risk, rec_creates)
                    return action_plan
            raise HTTPException(status_code=404, detail="Risk not found")
        
        elif insight_type == "opportunity":
            mock_opps = _get_mock_opportunities()
            for opp in mock_opps:
                if opp.insight_id == insight_id:
                    detected_opp = _opportunity_with_score_to_detected(opp)
                    rec_creates = recommendation_engine.generate_recommendations(detected_opp)
                    action_plan = recommendation_engine.create_action_plan(detected_opp, rec_creates)
                    return action_plan
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid insight_type")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action plan generation failed: {str(e)}")


@router.get("/action-plans", response_model=List[ActionPlan])
async def list_action_plans(
    company_id: Optional[str] = Query(None, description="Filter by company ID"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
):
    """
    List generated action plans.
    """
    # In production, query from database
    return []


# ==============================================================================
# Prioritization Endpoints
# ==============================================================================

@router.get("/priorities/{company_id}", response_model=List[InsightPriority])
async def get_all_priorities(
    company_id: str,
    include_resolved: bool = Query(False, description="Include resolved insights"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Get all prioritized insights for a company.
    
    Returns all risks and opportunities ranked by priority score.
    Priority score combines urgency, actionability, severity, strategic importance,
    and time sensitivity with appropriate weights.
    """
    try:
        # Get risks and opportunities
        risks = _get_mock_detected_risks(company_id)
        opportunities = _get_mock_detected_opportunities(company_id)
        
        # Filter out resolved if requested
        if not include_resolved:
            risks = [r for r in risks if hasattr(r, 'status') and r.status != "resolved" or not hasattr(r, 'status')]
            opportunities = [o for o in opportunities if hasattr(o, 'status') and o.status != "captured" or not hasattr(o, 'status')]
        
        # Get company profile (in production, this would come from database)
        company_profile = _get_mock_company_profile(company_id)
        
        # Prioritize all insights
        all_priorities = insight_prioritizer.prioritize_all(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
        )
        
        # Apply pagination
        return all_priorities[offset:offset + limit]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prioritization failed: {str(e)}")


@router.get("/top-priorities/{company_id}", response_model=TopPriorities)
async def get_top_priorities(
    company_id: str,
    limit: int = Query(5, ge=1, le=10, description="Number of top priorities (max 10)"),
):
    """
    Get the top N priorities for a company.
    
    Returns a structured response with the most critical insights
    that require immediate attention, combining both risks and opportunities.
    
    The prioritization algorithm considers:
    - Urgency (30%): How soon action is needed
    - Actionability (25%): How easily the insight can be acted upon
    - Severity/Impact (25%): Potential business impact
    - Strategic Importance (15%): Alignment with company strategy
    - Time Sensitivity (5%): Escalation over time
    """
    try:
        # Get risks and opportunities
        risks = _get_mock_detected_risks(company_id)
        opportunities = _get_mock_detected_opportunities(company_id)
        
        # Get company profile
        company_profile = _get_mock_company_profile(company_id)
        
        # Get top priorities
        top_priorities = insight_prioritizer.get_top_priorities(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
            limit=limit,
        )
        
        return top_priorities
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Top priorities calculation failed: {str(e)}")


@router.get("/priorities/{company_id}/urgent", response_model=List[InsightPriority])
async def get_urgent_priorities(
    company_id: str,
):
    """
    Get only urgent priorities that require immediate action.
    
    Returns insights where is_urgent=True or requires_immediate_action=True.
    """
    try:
        # Get all priorities
        risks = _get_mock_detected_risks(company_id)
        opportunities = _get_mock_detected_opportunities(company_id)
        company_profile = _get_mock_company_profile(company_id)
        
        all_priorities = insight_prioritizer.prioritize_all(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
        )
        
        # Filter for urgent only
        urgent = [p for p in all_priorities if p.is_urgent or p.requires_immediate_action]
        
        return urgent
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Urgent priorities calculation failed: {str(e)}")


@router.get("/priorities/{company_id}/by-category")
async def get_priorities_by_category(
    company_id: str,
):
    """
    Get priorities grouped by category.
    
    Returns a dictionary with categories as keys and lists of priorities as values.
    """
    try:
        # Get all priorities
        risks = _get_mock_detected_risks(company_id)
        opportunities = _get_mock_detected_opportunities(company_id)
        company_profile = _get_mock_company_profile(company_id)
        
        all_priorities = insight_prioritizer.prioritize_all(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
        )
        
        # Group by category
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for priority in all_priorities:
            cat = priority.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(priority.model_dump())
        
        return {
            "company_id": company_id,
            "categories": by_category,
            "total_priorities": len(all_priorities),
            "category_count": len(by_category),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Priorities by category failed: {str(e)}")


@router.post("/priorities/{company_id}/recalculate", response_model=TopPriorities)
async def recalculate_priorities(
    company_id: str,
    urgency_weight: float = Query(0.30, ge=0, le=1),
    actionability_weight: float = Query(0.25, ge=0, le=1),
    severity_weight: float = Query(0.25, ge=0, le=1),
    strategic_weight: float = Query(0.15, ge=0, le=1),
    time_sensitivity_weight: float = Query(0.05, ge=0, le=1),
):
    """
    Recalculate priorities with custom weights.
    
    Allows adjusting the weight of different factors in priority calculation.
    Weights should sum to approximately 1.0.
    """
    try:
        # Create a custom prioritizer with adjusted weights
        custom_prioritizer = InsightPrioritizer()
        custom_prioritizer.urgency_weight = urgency_weight
        custom_prioritizer.actionability_weight = actionability_weight
        custom_prioritizer.severity_weight = severity_weight
        custom_prioritizer.strategic_weight = strategic_weight
        custom_prioritizer.time_sensitivity_weight = time_sensitivity_weight
        
        # Get risks and opportunities
        risks = _get_mock_detected_risks(company_id)
        opportunities = _get_mock_detected_opportunities(company_id)
        company_profile = _get_mock_company_profile(company_id)
        
        # Get top priorities with custom weights
        top_priorities = custom_prioritizer.get_top_priorities(
            risks=risks,
            opportunities=opportunities,
            company_profile=company_profile,
            limit=5,
        )
        
        return top_priorities
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Priority recalculation failed: {str(e)}")


# ==============================================================================
# Narrative Endpoints
# ==============================================================================

@router.post("/narratives/generate", response_model=NarrativeContent)
async def generate_narrative(
    insight_type: str = Query(..., description="'risk' or 'opportunity'"),
    insight_id: int = Query(..., description="ID of the insight"),
):
    """
    Generate an executive narrative for an insight.
    """
    try:
        if insight_type == "risk":
            mock_risks = _get_mock_risks()
            for risk in mock_risks:
                if risk.insight_id == insight_id:
                    detected_risk = _risk_with_score_to_detected_risk(risk)
                    rec_creates = recommendation_engine.generate_recommendations(detected_risk)
                    narrative = recommendation_engine.generate_narrative(detected_risk, rec_creates)
                    return narrative
            raise HTTPException(status_code=404, detail="Risk not found")
        
        elif insight_type == "opportunity":
            mock_opps = _get_mock_opportunities()
            for opp in mock_opps:
                if opp.insight_id == insight_id:
                    detected_opp = _opportunity_with_score_to_detected(opp)
                    rec_creates = recommendation_engine.generate_recommendations(detected_opp)
                    narrative = recommendation_engine.generate_narrative(detected_opp, rec_creates)
                    return narrative
            raise HTTPException(status_code=404, detail="Opportunity not found")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid insight_type")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Narrative generation failed: {str(e)}")


# ==============================================================================
# Combined Insights Endpoints
# ==============================================================================

@router.get("/dashboard/{company_id}")
async def get_insights_dashboard(
    company_id: str,
    include_recommendations: bool = Query(True),
):
    """
    Get a complete insights dashboard for a company.
    
    Includes top risks, opportunities, and recommendations.
    """
    risks = _get_mock_risks(company_id)[:5]
    opportunities = _get_mock_opportunities(company_id)[:5]
    
    return {
        "company_id": company_id,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_active_risks": len(risks),
            "critical_risks": sum(1 for r in risks if r.score_breakdown.severity == "critical"),
            "high_risks": sum(1 for r in risks if r.score_breakdown.severity == "high"),
            "total_opportunities": len(opportunities),
            "high_priority_opportunities": sum(1 for o in opportunities if o.score_breakdown.priority == "high"),
        },
        "top_risks": [risk.model_dump() for risk in risks[:3]],
        "top_opportunities": [opp.model_dump() for opp in opportunities[:3]],
        "urgent_actions": [],  # Would contain urgent recommendations
    }


@router.post("/full-analysis/{company_id}", response_model=InsightWithRecommendations)
async def run_full_analysis(
    company_id: str,
    industry: str = Query("manufacturing", description="Company industry"),
    layer3_data: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None,
):
    """
    Run a complete analysis for a company:
    1. Detect risks and opportunities
    2. Generate recommendations
    3. Create action plans
    4. Generate narratives
    
    Returns the highest priority insight with full recommendations.
    """
    try:
        if layer3_data is None:
            layer3_data = _get_mock_layer3_data()
        
        # Convert to OperationalIndicators
        indicators = _create_operational_indicators(layer3_data)
        
        # Detect risks
        risks = risk_detector.detect_risks(company_id, industry, indicators)
        
        # Detect opportunities
        opportunities = opportunity_detector.detect_opportunities(company_id, industry, indicators)
        
        # Get highest priority insight
        if risks:
            top_risk = max(risks, key=lambda r: float(r.final_score))
            rec_creates = recommendation_engine.generate_recommendations(top_risk)
            action_plan = recommendation_engine.create_action_plan(top_risk, rec_creates)
            narrative = recommendation_engine.generate_narrative(top_risk, rec_creates)
            
            # Convert to Recommendation objects
            recommendations = []
            for i, rc in enumerate(rec_creates):
                recommendations.append(Recommendation(
                    recommendation_id=i + 1,
                    insight_id=0,
                    category=rc.category,
                    priority=rc.priority,
                    action_title=rc.action_title,
                    action_description=rc.action_description,
                    responsible_role=rc.responsible_role,
                    estimated_effort=rc.estimated_effort,
                    estimated_cost=rc.estimated_cost,
                    estimated_timeframe=rc.estimated_timeframe,
                    expected_benefit=rc.expected_benefit,
                    success_metrics=rc.success_metrics,
                    required_resources=rc.required_resources,
                    status="pending",
                    created_at=datetime.now(),
                ))
            
            return InsightWithRecommendations(
                insight=top_risk.model_dump(),
                recommendations=recommendations,
                action_plan=action_plan,
                narrative=narrative,
            )
        
        elif opportunities:
            top_opp = max(opportunities, key=lambda o: float(o.final_score))
            rec_creates = recommendation_engine.generate_recommendations(top_opp)
            action_plan = recommendation_engine.create_action_plan(top_opp, rec_creates)
            narrative = recommendation_engine.generate_narrative(top_opp, rec_creates)
            
            # Convert to Recommendation objects
            recommendations = []
            for i, rc in enumerate(rec_creates):
                recommendations.append(Recommendation(
                    recommendation_id=i + 1,
                    insight_id=0,
                    category=rc.category,
                    priority=rc.priority,
                    action_title=rc.action_title,
                    action_description=rc.action_description,
                    responsible_role=rc.responsible_role,
                    estimated_effort=rc.estimated_effort,
                    estimated_cost=rc.estimated_cost,
                    estimated_timeframe=rc.estimated_timeframe,
                    expected_benefit=rc.expected_benefit,
                    success_metrics=rc.success_metrics,
                    required_resources=rc.required_resources,
                    status="pending",
                    created_at=datetime.now(),
                ))
            
            return InsightWithRecommendations(
                insight=top_opp.model_dump(),
                recommendations=recommendations,
                action_plan=action_plan,
                narrative=narrative,
            )
        
        else:
            return InsightWithRecommendations(
                insight={"message": "No significant insights detected"},
                recommendations=[],
                action_plan=None,
                narrative=None,
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full analysis failed: {str(e)}")


# ==============================================================================
# Helper Functions
# ==============================================================================

def _get_mock_layer3_data() -> Dict[str, Any]:
    """Get mock Layer 3 operational data for testing."""
    return {
        "company_id": "COMP001",
        "timestamp": datetime.now().isoformat(),
        "operational_indicators": {
            "OPS_POWER_RELIABILITY": 0.65,  # Low - should trigger risk
            "OPS_WATER_SUPPLY": 0.80,
            "OPS_LOGISTICS_EFFICIENCY": 0.55,  # Low
            "OPS_WORKFORCE_AVAILABILITY": 0.90,
            "OPS_SUPPLIER_RELIABILITY": 0.60,  # Low
            "OPS_EQUIPMENT_STATUS": 0.85,
            "OPS_REGULATORY_COMPLIANCE": 0.95,
            "OPS_MARKET_DEMAND": 0.70,
            "OPS_INPUT_COST": 0.80,  # High costs
            "OPS_PRODUCTION_CAPACITY": 0.75,
            "OPS_INVENTORY_TURNOVER": 0.85,
            "OPS_CASH_FLOW": 0.70,
        },
        "confidence_scores": {
            "OPS_POWER_RELIABILITY": 0.85,
            "OPS_WATER_SUPPLY": 0.90,
            "OPS_LOGISTICS_EFFICIENCY": 0.80,
        },
    }


def _create_operational_indicators(layer3_data: Dict[str, Any]) -> OperationalIndicators:
    """
    Create OperationalIndicators from raw Layer 3 data dict.
    
    Maps the Layer 3 API data format to the internal OperationalIndicators model.
    """
    indicators_dict = layer3_data.get("operational_indicators", {})
    
    # Map the common indicator names to OperationalIndicators fields
    # The field names need to match the OperationalIndicators model
    return OperationalIndicators(
        company_id=layer3_data.get("company_id", "UNKNOWN"),
        timestamp=datetime.fromisoformat(layer3_data.get("timestamp", datetime.now().isoformat())),
        OPS_POWER_RELIABILITY=indicators_dict.get("OPS_POWER_RELIABILITY", 0.75),
        OPS_WATER_SUPPLY=indicators_dict.get("OPS_WATER_SUPPLY", 0.75),
        OPS_TRANSPORT_AVAIL=indicators_dict.get("OPS_TRANSPORT_AVAIL", indicators_dict.get("OPS_LOGISTICS_EFFICIENCY", 0.75)),
        OPS_LABOR_AVAIL=indicators_dict.get("OPS_LABOR_AVAIL", indicators_dict.get("OPS_WORKFORCE_AVAILABILITY", 0.75)),
        OPS_SUPPLY_CHAIN=indicators_dict.get("OPS_SUPPLY_CHAIN", indicators_dict.get("OPS_SUPPLIER_RELIABILITY", 0.75)),
        OPS_DEMAND_LEVEL=indicators_dict.get("OPS_DEMAND_LEVEL", indicators_dict.get("OPS_MARKET_DEMAND", 0.70)),
        OPS_PRICING_POWER=indicators_dict.get("OPS_PRICING_POWER", 0.70),
        OPS_INPUT_COSTS=indicators_dict.get("OPS_INPUT_COSTS", indicators_dict.get("OPS_INPUT_COST", 0.50)),
        OPS_COMPETITOR_ACT=indicators_dict.get("OPS_COMPETITOR_ACT", 0.50),
        OPS_MARKET_ACCESS=indicators_dict.get("OPS_MARKET_ACCESS", 0.75),
        OPS_REG_COMPLIANCE=indicators_dict.get("OPS_REG_COMPLIANCE", indicators_dict.get("OPS_REGULATORY_COMPLIANCE", 0.80)),
        OPS_EXPORT_CAPACITY=indicators_dict.get("OPS_EXPORT_CAPACITY", 0.75),
        OPS_CREDIT_ACCESS=indicators_dict.get("OPS_CREDIT_ACCESS", 0.70),
        OPS_CURRENCY_RISK=indicators_dict.get("OPS_CURRENCY_RISK", 0.50),
        OPS_EQUIPMENT_STATUS=indicators_dict.get("OPS_EQUIPMENT_STATUS", 0.85),
        OPS_INVENTORY_LEVEL=indicators_dict.get("OPS_INVENTORY_LEVEL", indicators_dict.get("OPS_INVENTORY_TURNOVER", 0.80)),
        OPS_PRODUCTION_CAP=indicators_dict.get("OPS_PRODUCTION_CAP", indicators_dict.get("OPS_PRODUCTION_CAPACITY", 0.75)),
        OPS_QUALITY_CONTROL=indicators_dict.get("OPS_QUALITY_CONTROL", 0.85),
        OPS_TECH_ADOPTION=indicators_dict.get("OPS_TECH_ADOPTION", 0.65),
        OPS_INNOVATION_IDX=indicators_dict.get("OPS_INNOVATION_IDX", 0.60),
        OPS_DIGITAL_MATURITY=indicators_dict.get("OPS_DIGITAL_MATURITY", 0.55),
    )


def _get_mock_risks(
    company_id: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[RiskWithScore]:
    """Generate mock risks for testing."""
    now = datetime.now()
    
    risks = [
        RiskWithScore(
            insight_id=1,
            company_id="COMP001",
            title="Power Supply Reliability Risk",
            description="Power reliability has dropped below 70%, indicating potential operational disruptions.",
            category="infrastructure",
            score_breakdown=RiskScoreBreakdown(
                probability=Decimal("0.75"),
                probability_reasoning="Based on current power reliability metrics",
                impact=Decimal("8.0"),
                impact_reasoning="Significant impact on production capacity",
                urgency=4,
                urgency_reasoning="Requires attention within 24-48 hours",
                confidence=Decimal("0.85"),
                confidence_source="Layer 3 operational indicators",
                final_score=Decimal("7.2"),
                severity="high",
            ),
            detected_at=now,
            status="active",
            triggering_indicators={"OPS_POWER_RELIABILITY": 0.65},
            affected_operations=["production", "cold_storage", "machinery"],
        ),
        RiskWithScore(
            insight_id=2,
            company_id="COMP001",
            title="Logistics Efficiency Degradation",
            description="Transportation and logistics efficiency below acceptable threshold.",
            category="supply_chain",
            score_breakdown=RiskScoreBreakdown(
                probability=Decimal("0.60"),
                probability_reasoning="Current logistics metrics trending downward",
                impact=Decimal("6.5"),
                impact_reasoning="Moderate impact on delivery timelines",
                urgency=3,
                urgency_reasoning="Should be addressed this week",
                confidence=Decimal("0.80"),
                confidence_source="Layer 3 operational indicators",
                final_score=Decimal("5.8"),
                severity="medium",
            ),
            detected_at=now,
            status="active",
            triggering_indicators={"OPS_LOGISTICS_EFFICIENCY": 0.55},
            affected_operations=["delivery", "inventory_management"],
        ),
        RiskWithScore(
            insight_id=3,
            company_id="COMP001",
            title="Supplier Reliability Concerns",
            description="Key supplier reliability metrics showing decline.",
            category="supply_chain",
            score_breakdown=RiskScoreBreakdown(
                probability=Decimal("0.55"),
                probability_reasoning="Supplier metrics below threshold",
                impact=Decimal("7.0"),
                impact_reasoning="Could affect raw material availability",
                urgency=3,
                urgency_reasoning="Medium-term attention required",
                confidence=Decimal("0.75"),
                confidence_source="Supplier monitoring data",
                final_score=Decimal("5.5"),
                severity="medium",
            ),
            detected_at=now,
            status="active",
            triggering_indicators={"OPS_SUPPLIER_RELIABILITY": 0.60},
            affected_operations=["procurement", "production_planning"],
        ),
    ]
    
    # Apply filters
    if company_id:
        risks = [r for r in risks if r.company_id == company_id]
    if category:
        risks = [r for r in risks if r.category == category]
    if severity:
        risks = [r for r in risks if r.score_breakdown.severity == severity]
    
    return risks


def _get_mock_opportunities(
    company_id: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[OpportunityWithScore]:
    """Generate mock opportunities for testing."""
    now = datetime.now()
    
    opportunities = [
        OpportunityWithScore(
            insight_id=101,
            company_id="COMP001",
            title="Cost Optimization via Energy Efficiency",
            description="High energy costs present opportunity for efficiency improvements.",
            category="cost_reduction",
            score_breakdown=OpportunityScoreBreakdown(
                potential_value=Decimal("7.5"),
                value_reasoning="Significant potential cost savings",
                feasibility=Decimal("0.75"),
                feasibility_reasoning="Well-established solutions available",
                timing_score=Decimal("0.80"),
                timing_reasoning="Current conditions favor implementation",
                strategic_fit=Decimal("0.85"),
                fit_reasoning="Aligns with sustainability goals",
                final_score=Decimal("7.2"),
                priority="high",
            ),
            detected_at=now,
            status="identified",
            triggering_indicators={"OPS_INPUT_COST": 0.80, "OPS_POWER_RELIABILITY": 0.65},
            window_start=now,
            window_end=None,
        ),
        OpportunityWithScore(
            insight_id=102,
            company_id="COMP001",
            title="Market Expansion Opportunity",
            description="Strong market demand indicators suggest expansion potential.",
            category="market_expansion",
            score_breakdown=OpportunityScoreBreakdown(
                potential_value=Decimal("8.0"),
                value_reasoning="High market demand unmet",
                feasibility=Decimal("0.65"),
                feasibility_reasoning="Requires capacity expansion",
                timing_score=Decimal("0.70"),
                timing_reasoning="Market conditions favorable",
                strategic_fit=Decimal("0.80"),
                fit_reasoning="Aligns with growth strategy",
                final_score=Decimal("6.8"),
                priority="high",
            ),
            detected_at=now,
            status="identified",
            triggering_indicators={"OPS_MARKET_DEMAND": 0.70, "OPS_PRODUCTION_CAPACITY": 0.75},
            window_start=now,
            window_end=None,
        ),
    ]
    
    # Apply filters
    if company_id:
        opportunities = [o for o in opportunities if o.company_id == company_id]
    if category:
        opportunities = [o for o in opportunities if o.category == category]
    if priority:
        opportunities = [o for o in opportunities if o.score_breakdown.priority == priority]
    
    return opportunities


def _get_mock_recommendations(
    insight_id: Optional[int] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Recommendation]:
    """Generate mock recommendations for testing."""
    now = datetime.now()
    
    recommendations = [
        Recommendation(
            recommendation_id=1,
            insight_id=1,
            category="immediate",
            priority=1,
            action_title="Activate Backup Power Systems",
            action_description="Ensure backup generators are operational and ready for deployment.",
            responsible_role="Operations Manager",
            estimated_effort="Low",
            estimated_cost="Minimal - existing resources",
            estimated_timeframe="2-4 hours",
            expected_benefit="Ensure operational continuity during power issues",
            success_metrics=["Backup power tested", "Staff briefed on activation procedures"],
            required_resources={"personnel": 2, "equipment": ["backup_generators"]},
            status="pending",
            assigned_to=None,
            started_at=None,
            completed_at=None,
            implementation_notes=None,
            outcome_achieved=None,
            actual_benefit=None,
            created_at=now,
        ),
        Recommendation(
            recommendation_id=2,
            insight_id=1,
            category="short_term",
            priority=2,
            action_title="Contact Power Utility Provider",
            action_description="Coordinate with utility provider to understand outage timeline and mitigation.",
            responsible_role="Facilities Manager",
            estimated_effort="Low",
            estimated_cost="None",
            estimated_timeframe="24 hours",
            expected_benefit="Better planning and resource allocation",
            success_metrics=["Utility contact made", "Timeline received"],
            required_resources={"personnel": 1},
            status="pending",
            assigned_to=None,
            started_at=None,
            completed_at=None,
            implementation_notes=None,
            outcome_achieved=None,
            actual_benefit=None,
            created_at=now,
        ),
    ]
    
    # Apply filters
    if insight_id:
        recommendations = [r for r in recommendations if r.insight_id == insight_id]
    if status:
        recommendations = [r for r in recommendations if r.status == status]
    if category:
        recommendations = [r for r in recommendations if r.category == category]
    
    return recommendations


def _risk_with_score_to_detected_risk(risk: RiskWithScore) -> DetectedRisk:
    """Convert RiskWithScore to DetectedRisk for engine processing."""
    return DetectedRisk(
        risk_code=f"RISK_{risk.insight_id}",
        company_id=risk.company_id,
        title=risk.title,
        description=risk.description,
        category=risk.category,
        probability=risk.score_breakdown.probability,
        impact=risk.score_breakdown.impact,
        urgency=risk.score_breakdown.urgency,
        confidence=risk.score_breakdown.confidence,
        final_score=risk.score_breakdown.final_score,
        severity_level=risk.score_breakdown.severity,
        triggering_indicators=risk.triggering_indicators,
        detection_method="rule_based",
    )


def _opportunity_with_score_to_detected(opp: OpportunityWithScore) -> DetectedOpportunity:
    """Convert OpportunityWithScore to DetectedOpportunity for engine processing."""
    return DetectedOpportunity(
        opportunity_code=f"OPP_{opp.insight_id}",
        company_id=opp.company_id,
        title=opp.title,
        description=opp.description,
        category=opp.category,
        potential_value=opp.score_breakdown.potential_value,
        feasibility=opp.score_breakdown.feasibility,
        timing_score=opp.score_breakdown.timing_score,
        strategic_fit=opp.score_breakdown.strategic_fit,
        final_score=opp.score_breakdown.final_score,
        priority_level=opp.score_breakdown.priority,
        triggering_indicators=opp.triggering_indicators,
        detection_method="gap_analysis",
    )


def _get_mock_detected_risks(company_id: Optional[str] = None) -> List[DetectedRisk]:
    """Generate mock DetectedRisk objects for prioritization testing."""
    now = datetime.now()
    
    risks = [
        DetectedRisk(
            risk_code="RISK_POWER_001",
            company_id=company_id or "COMP001",
            title="Power Supply Reliability Risk",
            description="Power reliability has dropped below 70%, indicating potential operational disruptions.",
            category="infrastructure",
            probability=Decimal("0.75"),
            impact=Decimal("8.0"),
            urgency=4,  # High urgency
            confidence=Decimal("0.85"),
            final_score=Decimal("7.2"),
            severity_level="high",
            triggering_indicators={"OPS_POWER_RELIABILITY": 0.65},
            detection_method="rule_based",
        ),
        DetectedRisk(
            risk_code="RISK_LOGISTICS_001",
            company_id=company_id or "COMP001",
            title="Logistics Efficiency Degradation",
            description="Transportation and logistics efficiency below acceptable threshold.",
            category="operational",
            probability=Decimal("0.60"),
            impact=Decimal("6.5"),
            urgency=3,  # Medium urgency
            confidence=Decimal("0.80"),
            final_score=Decimal("5.8"),
            severity_level="medium",
            triggering_indicators={"OPS_LOGISTICS_EFFICIENCY": 0.55},
            detection_method="rule_based",
        ),
        DetectedRisk(
            risk_code="RISK_SUPPLIER_001",
            company_id=company_id or "COMP001",
            title="Supplier Reliability Concerns",
            description="Key supplier reliability metrics showing decline.",
            category="supply_chain",
            probability=Decimal("0.55"),
            impact=Decimal("7.0"),
            urgency=3,
            confidence=Decimal("0.75"),
            final_score=Decimal("5.5"),
            severity_level="medium",
            triggering_indicators={"OPS_SUPPLIER_RELIABILITY": 0.60},
            detection_method="rule_based",
        ),
        DetectedRisk(
            risk_code="RISK_CASH_001",
            company_id=company_id or "COMP001",
            title="Cash Flow Pressure",
            description="Working capital indicators showing strain.",
            category="financial",
            probability=Decimal("0.50"),
            impact=Decimal("8.5"),
            urgency=4,  # High urgency for financial
            confidence=Decimal("0.70"),
            final_score=Decimal("6.0"),
            severity_level="high",
            triggering_indicators={"OPS_CASH_FLOW": 0.45},
            detection_method="rule_based",
        ),
    ]
    
    return risks


def _get_mock_detected_opportunities(company_id: Optional[str] = None) -> List[DetectedOpportunity]:
    """Generate mock DetectedOpportunity objects for prioritization testing."""
    now = datetime.now()
    
    opportunities = [
        DetectedOpportunity(
            opportunity_code="OPP_ENERGY_001",
            company_id=company_id or "COMP001",
            title="Energy Efficiency Optimization",
            description="High energy costs present opportunity for efficiency improvements.",
            category="cost_reduction",
            potential_value=Decimal("7.5"),
            feasibility=Decimal("0.75"),
            timing_score=Decimal("0.80"),
            strategic_fit=Decimal("0.85"),
            final_score=Decimal("7.2"),
            priority_level="high",
            triggering_indicators={"OPS_INPUT_COST": 0.80, "OPS_POWER_RELIABILITY": 0.65},
            detection_method="gap_analysis",
        ),
        DetectedOpportunity(
            opportunity_code="OPP_MARKET_001",
            company_id=company_id or "COMP001",
            title="Market Expansion Opportunity",
            description="Strong market demand indicators suggest expansion potential.",
            category="market_expansion",
            potential_value=Decimal("8.0"),
            feasibility=Decimal("0.65"),
            timing_score=Decimal("0.70"),
            strategic_fit=Decimal("0.80"),
            final_score=Decimal("6.8"),
            priority_level="high",
            triggering_indicators={"OPS_MARKET_DEMAND": 0.70, "OPS_PRODUCTION_CAPACITY": 0.75},
            detection_method="gap_analysis",
        ),
        DetectedOpportunity(
            opportunity_code="OPP_DIGITAL_001",
            company_id=company_id or "COMP001",
            title="Digital Transformation Opportunity",
            description="Low digital maturity creates opportunity for technology investment.",
            category="technology",
            potential_value=Decimal("6.5"),
            feasibility=Decimal("0.60"),
            timing_score=Decimal("0.75"),
            strategic_fit=Decimal("0.70"),
            final_score=Decimal("5.9"),
            priority_level="medium",
            triggering_indicators={"OPS_DIGITAL_MATURITY": 0.55, "OPS_TECH_ADOPTION": 0.65},
            detection_method="gap_analysis",
        ),
    ]
    
    return opportunities


def _get_mock_company_profile(company_id: str) -> Dict[str, Any]:
    """Generate mock company profile for prioritization context."""
    return {
        "company_id": company_id,
        "name": f"Company {company_id}",
        "industry": "manufacturing",
        "size": "medium",
        "risk_tolerance": "moderate",
        "strategic_priorities": [
            "operational_efficiency",
            "cost_reduction",
            "market_expansion",
        ],
        "financial_health": "stable",
        "growth_stage": "mature",
        "regulatory_environment": "standard",
    }
