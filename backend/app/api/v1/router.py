"""API v1 router - Integrated (Layers 1-5)"""

from fastapi import APIRouter

# Import Layer 1 AI Agent endpoints
try:
    from app.api.v1.endpoints import agents
    HAS_AGENTS = True
except ImportError:
    HAS_AGENTS = False

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

# Import Layer 4 advanced features endpoints
try:
    from app.api.v1 import advanced_features
    HAS_ADVANCED = True
except ImportError:
    HAS_ADVANCED = False

# Import Integration Pipeline endpoints
try:
    from app.api.v1 import pipeline
    HAS_PIPELINE = True
except ImportError:
    HAS_PIPELINE = False

# Import Layer 2 Enhanced Processing endpoints (LLM Services)
try:
    from app.api.v1.endpoints import enhanced_processing
    HAS_ENHANCED = True
except ImportError:
    HAS_ENHANCED = False

# Import Source Reputation System endpoints
try:
    from app.api.v1.endpoints import reputation
    HAS_REPUTATION = True
except ImportError:
    HAS_REPUTATION = False

# Import Layer 5 Dashboard endpoints
try:
    from app.layer5.api import auth_router, admin_router, user_router, operations_router
    HAS_LAYER5 = True
except ImportError:
    HAS_LAYER5 = False

# Import Layer 1 Admin Dashboard endpoints
try:
    from app.api.v1.endpoints import admin
    HAS_ADMIN = True
except ImportError:
    HAS_ADMIN = False

api_router = APIRouter()


# Health check endpoint (Developer B)
@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "layer": "Full-Stack-L12345"}


# Include Layer 1 AI Agent endpoints
if HAS_AGENTS:
    api_router.include_router(
        agents.router,
        prefix="/agents",
        tags=["agents", "layer1", "ai"]
    )

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

# Include Layer 4 advanced features endpoints
if HAS_ADVANCED:
    api_router.include_router(
        advanced_features.router,
        prefix="/advanced",
        tags=["advanced", "layer4"]
    )

# Include Integration Pipeline endpoints
if HAS_PIPELINE:
    api_router.include_router(
        pipeline.router,
        prefix="/pipeline",
        tags=["pipeline", "integration"]
    )

# Include Layer 2 Enhanced Processing endpoints (LLM Services)
if HAS_ENHANCED:
    api_router.include_router(
        enhanced_processing.router,
        prefix="/enhanced",
        tags=["enhanced", "layer2", "llm"]
    )

# Include Source Reputation System endpoints
if HAS_REPUTATION:
    api_router.include_router(
        reputation.router,
        tags=["reputation", "quality"]
    )

# Include Layer 5 Dashboard endpoints
if HAS_LAYER5:
    api_router.include_router(
        auth_router,
        tags=["auth", "layer5"]
    )
    api_router.include_router(
        admin_router,
        tags=["admin", "layer5"]
    )
    api_router.include_router(
        user_router,
        tags=["user", "layer5"]
    )
    api_router.include_router(
        operations_router,
        tags=["operations", "layer5"]
    )

# Include Layer 1 Admin Dashboard endpoints
if HAS_ADMIN:
    api_router.include_router(
        admin.router,
        prefix="/admin",
        tags=["admin", "layer1", "dashboard"]
    )
