"""API v1 router - Integrated"""

from fastapi import APIRouter

# Import endpoint routers (Developer A)
try:
    from app.api.v1.endpoints import indicators
    HAS_INDICATORS = True
except ImportError:
    HAS_INDICATORS = False

api_router = APIRouter()


# Health check endpoint (Developer B)
@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "layer": "Layer2-Integrated"}


# Include indicator endpoints if available (Developer A)
if HAS_INDICATORS:
    api_router.include_router(
        indicators.router,
        prefix="/indicators",
        tags=["indicators"]
    )
