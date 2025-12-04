from fastapi import FastAPI
from app.api.v1.endpoints import layer3

app = FastAPI(title="National Activity Indicator - Layer 3 Engine")

app.include_router(layer3.router, prefix="/api/v1/layer3", tags=["Layer 3"])

@app.get("/")
def root():
    return {"message": "Layer 3 Operational Indicator Engine is running"}
