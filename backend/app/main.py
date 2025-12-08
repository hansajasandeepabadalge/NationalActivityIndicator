"""
Layer5 Dashboard API - Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import RedisCache
from app.api.routes.AuthRoutes import router as auth_router
from app.api.routes.userRoutes import router as user_router
from app.api.routes.adminRoutes import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Starting up application...")
    await connect_to_mongo()
    await RedisCache.connect()
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_mongo_connection()
    await RedisCache.disconnect()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(user_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)



@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
