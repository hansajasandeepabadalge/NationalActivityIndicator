from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

app = create_app()
