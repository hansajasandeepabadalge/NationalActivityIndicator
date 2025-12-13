"""
Stock Market API Routes - Layer 5
Endpoints for Colombo Stock Exchange data
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.layer3.services.stock_market_service import StockMarketService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stock", tags=["Stock Market"])


@router.get("/market-summary")
async def get_market_summary() -> Dict[str, Any]:
    """
    Get Colombo Stock Exchange market summary
    
    Returns:
        - indices: ASPI and S&P SL20 index values
        - marketSummary: Trading statistics
        - topGainers: Top performing stocks
        - topLosers: Worst performing stocks
        - mostActive: Most traded stocks
    """
    try:
        market_data = await StockMarketService.get_market_summary()
        return market_data
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch market summary"
        )


@router.post("/clear-cache")
async def clear_cache():
    """
    Clear the stock market data cache
    Useful for forcing a fresh data fetch
    """
    try:
        StockMarketService.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )
