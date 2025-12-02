from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
