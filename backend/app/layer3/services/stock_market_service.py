"""
Stock Market Service - Layer 3
Fetches data from Colombo Stock Exchange API
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# CSE API base URL
CSE_BASE_URL = "https://www.cse.lk/api"

# Cache for CSE data
_cse_cache: Dict[str, Dict[str, Any]] = {}
CACHE_DURATION = timedelta(minutes=5)


class StockMarketService:
    """Service for fetching stock market data from CSE"""

    @staticmethod
    async def get_market_summary() -> Dict[str, Any]:
        """
        Fetch market summary from CSE API
        Returns comprehensive market data including indices, top movers, etc.
        """
        # Check cache first
        cache_key = "market_summary"
        if cache_key in _cse_cache:
            cached_data = _cse_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < CACHE_DURATION:
                logger.info("Returning cached CSE market data")
                return cached_data["data"]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch trade summary
                response = await client.get(f"{CSE_BASE_URL}/tradeSummary")
                response.raise_for_status()
                trade_data = response.json()

                # Transform to our format
                market_data = StockMarketService._transform_cse_data(trade_data)

                # Cache the result
                _cse_cache[cache_key] = {
                    "data": market_data,
                    "timestamp": datetime.now()
                }

                logger.info("Successfully fetched CSE market data")
                return market_data

        except Exception as e:
            logger.error(f"Failed to fetch CSE data: {str(e)}")
            # Return mock data as fallback
            return StockMarketService._get_mock_data()

    @staticmethod
    def _transform_cse_data(api_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform CSE /tradeSummary response into our standard format.

        The CSE tradeSummary endpoint returns a list of per-symbol
        objects (symbol, name, price, change, volume, turnover, trades).
        We compute aggregate stats and pick top movers/most-active from it.

        If the response shape is unrecognised, we fall back to mock data
        rather than returning a half-built payload.
        """
        # CSE tradeSummary returns either {"reqTradeSummery": [...]} or a bare list
        if isinstance(api_data, dict):
            rows = (
                api_data.get("reqTradeSummery")
                or api_data.get("tradeSummary")
                or api_data.get("data")
                or []
            )
        elif isinstance(api_data, list):
            rows = api_data
        else:
            rows = []

        if not rows:
            logger.warning("CSE response empty/unrecognised — returning mock data")
            return StockMarketService._get_mock_data()

        def _f(v, default=0.0):
            try:
                return float(v) if v is not None else default
            except (TypeError, ValueError):
                return default

        def _i(v, default=0):
            try:
                return int(v) if v is not None else default
            except (TypeError, ValueError):
                return default

        normalised = []
        advancers = decliners = unchanged = 0
        total_turnover = 0.0
        total_volume = 0
        total_trades = 0

        for r in rows:
            change = _f(r.get("change") or r.get("priceChange"))
            price = _f(r.get("price") or r.get("lastTradedPrice"))
            volume = _i(r.get("tradeVolume") or r.get("volume"))
            turnover = _f(r.get("turnover"))
            trades = _i(r.get("trades") or r.get("tradeCount"))

            if change > 0:
                advancers += 1
            elif change < 0:
                decliners += 1
            else:
                unchanged += 1

            total_turnover += turnover
            total_volume += volume
            total_trades += trades

            normalised.append({
                "symbol": r.get("symbol") or r.get("name") or "?",
                "name": r.get("name") or r.get("companyName") or "",
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": round(_f(r.get("changePercentage") or r.get("percentageChange")), 2),
                "volume": volume,
                "turnover": int(turnover),
                "trades": trades,
            })

        top_gainers = sorted(normalised, key=lambda x: x["changePercent"], reverse=True)[:5]
        top_losers = sorted(normalised, key=lambda x: x["changePercent"])[:5]
        most_active = sorted(normalised, key=lambda x: x["volume"], reverse=True)[:5]

        return {
            "indices": [],  # tradeSummary doesn't include index values
            "marketSummary": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "totalTurnover": int(total_turnover),
                "totalVolume": int(total_volume),
                "totalTrades": int(total_trades),
                "advancers": advancers,
                "decliners": decliners,
                "unchanged": unchanged,
                "marketCap": None,
            },
            "topGainers": top_gainers,
            "topLosers": top_losers,
            "mostActive": most_active,
            "lastUpdate": int(datetime.now().timestamp() * 1000),
            "source": "cse_live",
        }

    @staticmethod
    def _get_mock_data() -> Dict[str, Any]:
        """
        Generate realistic mock CSE data
        """
        import random

        base_aspi = 11245.67
        base_sp20 = 3456.89

        return {
            "indices": [
                {
                    "name": "All Share Price Index",
                    "code": "ASPI",
                    "value": round(base_aspi + random.uniform(-50, 50), 2),
                    "change": round(random.uniform(-30, 30), 2),
                    "changePercent": round(random.uniform(-1.5, 1.5), 2),
                    "high": round(base_aspi + random.uniform(20, 80), 2),
                    "low": round(base_aspi - random.uniform(20, 80), 2),
                    "timestamp": int(datetime.now().timestamp() * 1000)
                },
                {
                    "name": "S&P Sri Lanka 20",
                    "code": "S&P SL20",
                    "value": round(base_sp20 + random.uniform(-20, 20), 2),
                    "change": round(random.uniform(-15, 15), 2),
                    "changePercent": round(random.uniform(-0.8, 0.8), 2),
                    "high": round(base_sp20 + random.uniform(10, 40), 2),
                    "low": round(base_sp20 - random.uniform(10, 40), 2),
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
            ],
            "marketSummary": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "totalTurnover": int(2450000000 * random.uniform(0.8, 1.2)),
                "totalVolume": int(45678900 * random.uniform(0.8, 1.2)),
                "totalTrades": int(5678 * random.uniform(0.8, 1.2)),
                "advancers": random.randint(75, 105),
                "decliners": random.randint(55, 85),
                "unchanged": random.randint(35, 55),
                "marketCap": 3250
            },
            "topGainers": [
                {
                    "symbol": "JKH",
                    "name": "John Keells Holdings PLC",
                    "price": round(145.50 + random.uniform(-5, 5), 2),
                    "change": round(random.uniform(5, 10), 2),
                    "changePercent": round(random.uniform(4, 7), 2),
                    "volume": int(1234500 * random.uniform(0.8, 1.2)),
                    "turnover": int(179621250 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(400, 500)
                },
                {
                    "symbol": "COMB",
                    "name": "Commercial Bank of Ceylon PLC",
                    "price": round(98.75 + random.uniform(-3, 3), 2),
                    "change": round(random.uniform(4, 6), 2),
                    "changePercent": round(random.uniform(4.5, 6.5), 2),
                    "volume": int(987600 * random.uniform(0.8, 1.2)),
                    "turnover": int(97525500 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(200, 250)
                },
                {
                    "symbol": "DIAL",
                    "name": "Dialog Axiata PLC",
                    "price": round(12.30 + random.uniform(-0.5, 0.5), 2),
                    "change": round(random.uniform(0.4, 0.8), 2),
                    "changePercent": round(random.uniform(4, 6), 2),
                    "volume": int(5678900 * random.uniform(0.8, 1.2)),
                    "turnover": int(69850470 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(700, 850)
                }
            ],
            "topLosers": [
                {
                    "symbol": "SAMP",
                    "name": "Sampath Bank PLC",
                    "price": round(87.25 + random.uniform(-3, 3), 2),
                    "change": round(random.uniform(-6, -3), 2),
                    "changePercent": round(random.uniform(-6, -4), 2),
                    "volume": int(567800 * random.uniform(0.8, 1.2)),
                    "turnover": int(49550550 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(100, 150)
                },
                {
                    "symbol": "HNB",
                    "name": "Hatton National Bank PLC",
                    "price": round(156.00 + random.uniform(-5, 5), 2),
                    "change": round(random.uniform(-8, -5), 2),
                    "changePercent": round(random.uniform(-5, -3.5), 2),
                    "volume": int(345600 * random.uniform(0.8, 1.2)),
                    "turnover": int(53913600 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(80, 120)
                }
            ],
            "mostActive": [
                {
                    "symbol": "DIAL",
                    "name": "Dialog Axiata PLC",
                    "price": round(12.30 + random.uniform(-0.5, 0.5), 2),
                    "change": round(random.uniform(0.4, 0.8), 2),
                    "changePercent": round(random.uniform(4, 6), 2),
                    "volume": int(5678900 * random.uniform(0.8, 1.2)),
                    "turnover": int(69850470 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(700, 850)
                },
                {
                    "symbol": "JKH",
                    "name": "John Keells Holdings PLC",
                    "price": round(145.50 + random.uniform(-5, 5), 2),
                    "change": round(random.uniform(5, 10), 2),
                    "changePercent": round(random.uniform(4, 7), 2),
                    "volume": int(1234500 * random.uniform(0.8, 1.2)),
                    "turnover": int(179621250 * random.uniform(0.8, 1.2)),
                    "trades": random.randint(400, 500)
                }
            ],
            "lastUpdate": int(datetime.now().timestamp() * 1000)
        }

    @staticmethod
    def clear_cache():
        """Clear the CSE data cache"""
        global _cse_cache
        _cse_cache = {}
        logger.info("CSE cache cleared")
