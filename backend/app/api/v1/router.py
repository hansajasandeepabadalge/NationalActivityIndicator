"""API v1 router - Integrated"""

from fastapi import APIRouter

# Import endpoint routers (Developer A)
try:
    from app.api.v1.endpoints import indicators
    HAS_INDICATORS = True
except ImportError:
    HAS_INDICATORS = False

# Import Layer 4 insights endpoints
try:
    from app.api.v1.endpoints import insights
    HAS_INSIGHTS = True
except ImportError:
    HAS_INSIGHTS = False

api_router = APIRouter()


# Health check endpoint (Developer B)
@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "layer": "Layer4-BusinessInsights"}


# Include indicator endpoints if available (Developer A)
if HAS_INDICATORS:
    api_router.include_router(
        indicators.router,
        prefix="/indicators",
        tags=["indicators"]
    )

# Include Layer 4 insights endpoints
if HAS_INSIGHTS:
    api_router.include_router(
        insights.router,
        prefix="/insights",
        tags=["insights", "layer4"]
    )
