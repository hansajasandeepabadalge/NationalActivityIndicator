"""
Integration Pipeline REST API

Provides endpoints to run the Layer 2 → Layer 3 → Layer 4 pipeline.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

from app.integration import (
    create_pipeline,
    MockDataGenerator,
    validate_layer2_output,
    validate_layer3_output,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class EconomicScenario(str, Enum):
    """Available economic scenarios for mock data generation"""
    NORMAL = "normal"
    CRISIS = "crisis"
    GROWTH = "growth"
    RECESSION = "recession"


class IndustryType(str, Enum):
    """Supported industry types"""
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    LOGISTICS = "logistics"
    HOSPITALITY = "hospitality"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"


class CompanyProfileRequest(BaseModel):
    """Company profile for pipeline context"""
    company_id: str = Field(..., description="Unique company identifier")
    company_name: str = Field(..., description="Company name")
    industry: IndustryType = Field(..., description="Industry type")
    size: str = Field(default="medium", description="Company size: small, medium, large")
    region: str = Field(default="Southeast Asia", description="Operating region")
    annual_revenue: Optional[float] = Field(default=None, description="Annual revenue in USD")
    employee_count: Optional[int] = Field(default=None, description="Number of employees")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance: low, moderate, high")


class PipelineRunRequest(BaseModel):
    """Request to run the full pipeline"""
    company_profile: CompanyProfileRequest
    scenario: EconomicScenario = Field(
        default=EconomicScenario.NORMAL,
        description="Economic scenario for mock data generation"
    )
    use_mock_data: bool = Field(
        default=True,
        description="Use mock data (True) or expect real Layer 2 input (False)"
    )
    layer2_input: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional: Provide real Layer 2 output instead of mock"
    )


class Layer3OnlyRequest(BaseModel):
    """Request to run Layer 2 → Layer 3 only"""
    company_profile: CompanyProfileRequest
    scenario: EconomicScenario = Field(default=EconomicScenario.NORMAL)
    layer2_input: Optional[Dict[str, Any]] = None


class Layer4OnlyRequest(BaseModel):
    """Request to run Layer 3 → Layer 4 only"""
    company_profile: CompanyProfileRequest
    layer3_input: Dict[str, Any] = Field(..., description="Layer 3 output data")


class RiskSummary(BaseModel):
    """Summary of a detected risk"""
    risk_code: str
    title: str
    severity: str
    category: str


class OpportunitySummary(BaseModel):
    """Summary of a detected opportunity"""
    opportunity_code: str
    title: str
    potential_value: str
    category: str


class PipelineSummaryResponse(BaseModel):
    """Summarized pipeline response"""
    success: bool
    company_id: str
    company_name: str
    industry: str
    timestamp: datetime
    
    # Layer 2 summary
    layer2_summary: Dict[str, Any]
    
    # Layer 3 summary
    layer3_summary: Dict[str, Any]
    
    # Layer 4 summary
    layer4_summary: Dict[str, Any]
    
    # Performance
    total_time_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "company_id": "COMP001",
                "company_name": "Test Manufacturing Co",
                "industry": "manufacturing",
                "timestamp": "2025-12-05T10:30:00",
                "layer2_summary": {
                    "overall_sentiment": 0.1,
                    "activity_level": 60.0,
                    "indicator_count": 8
                },
                "layer3_summary": {
                    "overall_health": 72.3,
                    "supply_chain": 91.9,
                    "workforce": 50.4,
                    "critical_issues": 0
                },
                "layer4_summary": {
                    "risk_count": 1,
                    "opportunity_count": 6,
                    "recommendation_count": 33,
                    "risk_level": "medium"
                },
                "total_time_seconds": 0.45
            }
        }


class PipelineFullResponse(BaseModel):
    """Full pipeline response with all details"""
    success: bool
    error: Optional[str] = None
    layer2_output: Optional[Dict[str, Any]] = None
    layer3_output: Optional[Dict[str, Any]] = None
    layer4_output: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any]


# =============================================================================
# API Endpoints
# =============================================================================

@router.post(
    "/run",
    response_model=PipelineSummaryResponse,
    summary="Run Full Pipeline",
    description="Execute the complete Layer 2 → Layer 3 → Layer 4 pipeline"
)
async def run_full_pipeline(request: PipelineRunRequest):
    """
    Run the complete integration pipeline.
    
    This endpoint:
    1. Takes company profile and optional Layer 2 input
    2. Generates mock Layer 2 data if not provided
    3. Transforms through Layer 3 (operational indicators)
    4. Runs Layer 4 engines (risks, opportunities, recommendations)
    5. Returns summarized results
    """
    try:
        pipeline = create_pipeline()
        
        # Prepare company profile
        company_profile = request.company_profile.model_dump()
        
        # Get Layer 2 input
        if request.use_mock_data or request.layer2_input is None:
            mock_gen = MockDataGenerator(seed=42)
            layer2_input = mock_gen.generate_layer2_output(request.scenario.value)
        else:
            layer2_input = request.layer2_input
        
        # Run pipeline
        result = await pipeline.run_full_pipeline(
            company_profile=company_profile,
            layer2_input=layer2_input
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Pipeline execution failed: {result.get('error', 'Unknown error')}"
            )
        
        # Build summary response
        l2 = result["layer2_output"]
        l3 = result["layer3_output"]
        l4 = result["layer4_output"]
        
        return PipelineSummaryResponse(
            success=True,
            company_id=company_profile["company_id"],
            company_name=company_profile["company_name"],
            industry=company_profile["industry"],
            timestamp=datetime.now(),
            layer2_summary={
                "overall_sentiment": l2.get("overall_sentiment", 0),
                "activity_level": l2.get("activity_level", 0),
                "indicator_count": len(l2.get("indicators", {})),
                "data_quality": l2.get("data_quality_score", 0)
            },
            layer3_summary={
                "overall_health": l3.get("overall_operational_health", 0),
                "supply_chain": l3.get("supply_chain_health", 0),
                "workforce": l3.get("workforce_health", 0),
                "infrastructure": l3.get("infrastructure_health", 0),
                "cost_pressure": l3.get("cost_pressure", 0),
                "critical_issues": len(l3.get("critical_issues", []))
            },
            layer4_summary=l4.get("summary", {
                "risk_count": len(l4.get("risks", [])),
                "opportunity_count": len(l4.get("opportunities", [])),
                "recommendation_count": len(l4.get("recommendations", [])),
                "risk_level": "unknown"
            }),
            total_time_seconds=result["metrics"]["total_time_seconds"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/run/full",
    response_model=PipelineFullResponse,
    summary="Run Full Pipeline (Detailed)",
    description="Execute pipeline and return complete output from all layers"
)
async def run_full_pipeline_detailed(request: PipelineRunRequest):
    """
    Run the complete pipeline and return full details.
    
    Returns complete output from Layer 2, Layer 3, and Layer 4
    including all indicators, risks, opportunities, and recommendations.
    """
    try:
        pipeline = create_pipeline()
        company_profile = request.company_profile.model_dump()
        
        if request.use_mock_data or request.layer2_input is None:
            mock_gen = MockDataGenerator(seed=42)
            layer2_input = mock_gen.generate_layer2_output(request.scenario.value)
        else:
            layer2_input = request.layer2_input
        
        result = await pipeline.run_full_pipeline(
            company_profile=company_profile,
            layer2_input=layer2_input
        )
        
        return PipelineFullResponse(**result)
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return PipelineFullResponse(
            success=False,
            error=str(e),
            metrics={"error": str(e)}
        )


@router.post(
    "/run/layer2-to-layer3",
    summary="Run Layer 2 → Layer 3 Only",
    description="Transform national indicators to operational indicators"
)
async def run_layer2_to_layer3(request: Layer3OnlyRequest):
    """
    Run only the Layer 2 to Layer 3 transformation.
    
    Useful when you only need operational indicators without
    full Layer 4 business insights.
    """
    try:
        pipeline = create_pipeline()
        company_profile = request.company_profile.model_dump()
        
        if request.layer2_input is None:
            mock_gen = MockDataGenerator(seed=42)
            layer2_input = mock_gen.generate_layer2_output(request.scenario.value)
        else:
            layer2_input = request.layer2_input
        
        result = await pipeline.run_layer2_to_layer3(layer2_input, company_profile)
        
        return {
            "success": True,
            "company_id": company_profile["company_id"],
            "layer3_output": result
        }
        
    except Exception as e:
        logger.error(f"Layer 2→3 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/run/layer3-to-layer4",
    summary="Run Layer 3 → Layer 4 Only",
    description="Generate business insights from operational indicators"
)
async def run_layer3_to_layer4(request: Layer4OnlyRequest):
    """
    Run only the Layer 3 to Layer 4 transformation.
    
    Provide Layer 3 operational indicators and get
    risks, opportunities, and recommendations.
    """
    try:
        pipeline = create_pipeline()
        company_profile = request.company_profile.model_dump()
        
        result = await pipeline.run_layer3_to_layer4(
            request.layer3_input,
            company_profile
        )
        
        return {
            "success": True,
            "company_id": company_profile["company_id"],
            "layer4_output": result
        }
        
    except Exception as e:
        logger.error(f"Layer 3→4 error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/scenarios",
    summary="List Available Scenarios",
    description="Get list of available economic scenarios"
)
async def list_scenarios():
    """List available economic scenarios for mock data generation"""
    return {
        "scenarios": [
            {
                "id": "normal",
                "name": "Normal Economy",
                "description": "Moderate growth, stable conditions"
            },
            {
                "id": "crisis",
                "name": "Economic Crisis",
                "description": "High volatility, negative sentiment, supply disruptions"
            },
            {
                "id": "growth",
                "name": "Growth Period",
                "description": "Strong growth, positive sentiment, opportunities"
            },
            {
                "id": "recession",
                "name": "Recession",
                "description": "Declining activity, cost pressures, demand drop"
            }
        ]
    }


@router.get(
    "/industries",
    summary="List Supported Industries",
    description="Get list of supported industry types"
)
async def list_industries():
    """List supported industries with sensitivity profiles"""
    return {
        "industries": [
            {
                "id": "retail",
                "name": "Retail",
                "key_sensitivities": ["market_conditions", "supply_chain"]
            },
            {
                "id": "manufacturing",
                "name": "Manufacturing",
                "key_sensitivities": ["supply_chain", "infrastructure", "cost_pressure"]
            },
            {
                "id": "logistics",
                "name": "Logistics",
                "key_sensitivities": ["supply_chain", "infrastructure"]
            },
            {
                "id": "hospitality",
                "name": "Hospitality",
                "key_sensitivities": ["workforce", "market_conditions"]
            },
            {
                "id": "technology",
                "name": "Technology",
                "key_sensitivities": ["infrastructure", "workforce"]
            },
            {
                "id": "healthcare",
                "name": "Healthcare",
                "key_sensitivities": ["workforce", "regulatory"]
            },
            {
                "id": "finance",
                "name": "Finance",
                "key_sensitivities": ["financial", "regulatory"]
            }
        ]
    }


@router.get(
    "/demo",
    summary="Demo Pipeline Run",
    description="Quick demo with default parameters"
)
async def demo_pipeline(
    industry: IndustryType = Query(default=IndustryType.MANUFACTURING),
    scenario: EconomicScenario = Query(default=EconomicScenario.NORMAL)
):
    """
    Quick demo endpoint - runs pipeline with minimal input.
    
    Just provide industry and scenario to see sample results.
    """
    request = PipelineRunRequest(
        company_profile=CompanyProfileRequest(
            company_id="DEMO001",
            company_name=f"Demo {industry.value.title()} Company",
            industry=industry
        ),
        scenario=scenario,
        use_mock_data=True
    )
    
    return await run_full_pipeline(request)


@router.get(
    "/health",
    summary="Pipeline Health Check",
    description="Check if pipeline components are available"
)
async def pipeline_health():
    """Check pipeline component availability"""
    try:
        # Try importing all components
        from app.integration import create_pipeline, MockDataGenerator
        from app.layer4.risk_detection import RuleBasedRiskDetector
        from app.layer4.opportunity_detection import RuleBasedOpportunityDetector
        from app.layer4.recommendation import RecommendationEngine
        
        return {
            "status": "healthy",
            "components": {
                "integration_pipeline": True,
                "mock_data_generator": True,
                "risk_detector": True,
                "opportunity_detector": True,
                "recommendation_engine": True
            }
        }
    except ImportError as e:
        return {
            "status": "degraded",
            "error": str(e)
        }
