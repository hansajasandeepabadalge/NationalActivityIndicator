from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
from app.core.config import settings
from app.api.v1.router import api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Serve static files (dashboard)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Root endpoint - serve dashboard
    @app.get("/")
    async def root():
        return FileResponse("app/static/dashboard.html")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check for monitoring"""
        try:
            from app.db.mongodb_entities import MongoDBEntityStorage
            from app.api.v1.endpoints.cache import cache

            mongo = MongoDBEntityStorage()
            mongo.client.admin.command('ping')

            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected",
                "cache": "enabled" if cache.enabled else "disabled",
                "version": "1.0.0"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    return app

app = create_app()
