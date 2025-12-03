"""API v1 router"""

from fastapi import APIRouter
from app.api.v1.endpoints import indicators

api_router = APIRouter()

# Include indicator endpoints
api_router.include_router(
    indicators.router,
    prefix="/indicators",
    tags=["indicators"]
)
