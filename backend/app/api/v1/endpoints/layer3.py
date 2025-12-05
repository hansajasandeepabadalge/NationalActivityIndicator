from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ...services.operational_service import OperationalService

router = APIRouter()

def get_service():
    return OperationalService()

@router.get("/companies", response_model=List[Dict[str, Any]])
def list_companies(service: OperationalService = Depends(get_service)):
    """List all available mock companies"""
    return service.get_all_companies()

@router.post("/calculate/{company_id}")
def calculate_indicators(company_id: str, service: OperationalService = Depends(get_service)):
    """Trigger calculation for a specific company"""
    try:
        result = service.calculate_indicators_for_company(company_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{company_id}")
def get_indicators(company_id: str, service: OperationalService = Depends(get_service)):
    """Get latest indicators for a company (Simulated by running calc)"""
    # In real app, this would fetch from DB. Here we re-calc for demo.
    return calculate_indicators(company_id, service)
