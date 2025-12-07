"""
API v1 Router

Aggregates all API endpoints under the v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import agents
from app.api.v1.endpoints import users

api_router = APIRouter()

# Include all endpoint routers
# Note: agents.router already has prefix="/agents" defined internally
api_router.include_router(agents.router, tags=["AI Agents"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])