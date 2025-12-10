"""Indicator API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from app.api.v1.endpoints.schemas import (
    IndicatorBasic, IndicatorDetail, IndicatorHistoryResponse,
    TrendInfo, AnomalyInfo, AlertInfo, CompositeMetric, IndicatorHistory
)
from app.db.mongodb_entities import MongoDBEntityStorage
from app.layer2.analysis.trend_detector import TrendDetector
from app.core.config import settings

router = APIRouter()
mongo = MongoDBEntityStorage()
trend_detector = TrendDetector()

# Load historical data (cached at module level)
HISTORICAL_DATA_PATH = Path("backend/data/historical_indicator_values.json")
HISTORICAL_DATA = json.loads(HISTORICAL_DATA_PATH.read_text()) if HISTORICAL_DATA_PATH.exists() else {}


@router.get("/", response_model=List[IndicatorBasic])
async def list_indicators():
    """List all available indicators"""
    indicators = [
        IndicatorBasic(
            indicator_id="ECO_CURRENCY_STABILITY",
            name="Currency Stability",
            category="ECO",
            description="Tracks currency mentions and stability signals"
        ),
        IndicatorBasic(
            indicator_id="POL_GEOGRAPHIC_SCOPE",
            name="Geographic Scope",
            category="POL",
            description="Measures geographic diversity of coverage"
        )
    ]
    return indicators


@router.get("/{indicator_id}", response_model=IndicatorDetail)
async def get_indicator_details(indicator_id: str):
    """Get detailed information for a specific indicator"""

    # Get latest calculation from MongoDB
    latest = mongo.indicator_calculations.find_one(
        {"indicator_id": indicator_id},
        sort=[("calculation_timestamp", -1)]
    )

    if not latest:
        raise HTTPException(status_code=404, detail="Indicator not found")

    # Get narrative
    narrative_doc = mongo.narratives.find_one({
        "indicator_id": indicator_id
    }, sort=[("generated_at", -1)])

    narrative_text = None
    if narrative_doc:
        narrative_text = narrative_doc.get("summary")

    return IndicatorDetail(
        indicator_id=indicator_id,
        name=indicator_id.replace("_", " ").title(),
        category=indicator_id.split("_")[0],
        description=f"Indicator {indicator_id}",
        latest_value=latest.get("confidence"),
        latest_confidence=latest.get("confidence"),
        last_updated=latest.get("calculation_timestamp"),
        narrative=narrative_text
    )


@router.get("/{indicator_id}/history", response_model=IndicatorHistoryResponse)
async def get_indicator_history(
    indicator_id: str,
    days: int = Query(30, ge=1, le=90, description="Number of days of history")
):
    """Get time series history for an indicator"""

    # Load from JSON historical data
    indicator_data = HISTORICAL_DATA.get(indicator_id, [])

    if not indicator_data:
        raise HTTPException(status_code=404, detail="No historical data found")

    # Filter to requested days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    filtered_data = [
        IndicatorHistory(
            date=datetime.fromisoformat(item["date"]),
            value=item["value"],
            confidence=item.get("confidence", item["value"])
        )
        for item in indicator_data
        if datetime.fromisoformat(item["date"]) >= cutoff_date
    ]

    if not filtered_data:
        raise HTTPException(status_code=404, detail="No data in requested time range")

    return IndicatorHistoryResponse(
        indicator_id=indicator_id,
        time_series=filtered_data,
        period_start=filtered_data[0].date,
        period_end=filtered_data[-1].date
    )


@router.get("/trends/", response_model=List[TrendInfo])
async def get_trends(min_strength: float = Query(0.5, ge=0, le=1)):
    """Get indicators with strong trends"""

    trends = []

    for indicator_id in HISTORICAL_DATA.keys():
        data = HISTORICAL_DATA[indicator_id]
        values = [item["value"] for item in data[-30:]]  # Last 30 days

        if len(values) < 7:
            continue

        # Detect trend
        trend_result = trend_detector.detect_trend(values)

        if abs(trend_result["strength"]) >= min_strength:
            trends.append(TrendInfo(
                indicator_id=indicator_id,
                trend=trend_result["direction"],
                strength=abs(trend_result["strength"]),
                change_percent=trend_result["change_percent"]
            ))

    # Sort by strength descending
    trends.sort(key=lambda x: x.strength, reverse=True)
    return trends


@router.get("/anomalies/", response_model=List[AnomalyInfo])
async def detect_anomalies(threshold: float = Query(2.0, ge=1.0, le=5.0)):
    """Detect anomalies in indicator values"""

    anomalies = []

    for indicator_id in HISTORICAL_DATA.keys():
        data = HISTORICAL_DATA[indicator_id]
        values = [item["value"] for item in data]

        if len(values) < 10:
            continue

        # Simple anomaly detection: values beyond threshold standard deviations
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        for i, item in enumerate(data[-7:]):  # Last sanity days only
            value = item["value"]
            z_score = abs(value - mean) / std_dev if std_dev > 0 else 0

            if z_score > threshold:
                severity = "high" if z_score > 3 else "medium" if z_score > 2 else "low"
                anomalies.append(AnomalyInfo(
                    indicator_id=indicator_id,
                    date=datetime.fromisoformat(item["date"]),
                    value=value,
                    expected_range=(mean - threshold * std_dev, mean + threshold * std_dev),
                    severity=severity
                ))

    return anomalies


@router.get("/alerts/", response_model=List[AlertInfo])
async def get_recent_alerts(hours: int = Query(24, ge=1, le=168)):
    """Get recent alerts for significant changes"""

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    alerts = []

    # Query MongoDB for recent high-confidence indicators
    recent_calculations = mongo.indicator_calculations.find({
        "calculation_timestamp": {"$gte": cutoff_time},
        "confidence": {"$gte": 0.7}
    }).sort("calculation_timestamp", -1).limit(20)

    for calc in recent_calculations:
        # Check if this is a spike compared to historical average
        indicator_id = calc["indicator_id"]
        current_value = calc["confidence"]

        historical = HISTORICAL_DATA.get(indicator_id, [])
        if historical:
            recent_values = [item["value"] for item in historical[-30:]]
            if recent_values:
                avg = sum(recent_values) / len(recent_values)

                if current_value > avg * 1.5:
                    alerts.append(AlertInfo(
                        indicator_id=indicator_id,
                        alert_type="spike",
                        message=f"{indicator_id} increased significantly to {current_value:.2f} (avg: {avg:.2f})",
                        triggered_at=calc["calculation_timestamp"],
                        severity="high" if current_value > avg * 2 else "medium"
                    ))

    return alerts


@router.get("/composite/", response_model=List[CompositeMetric])
async def get_composite_metrics():
    """Get composite indicators (economic health, national stability)"""

    # Economic Health: Average of all ECO_ indicators
    eco_indicators = [k for k in HISTORICAL_DATA.keys() if k.startswith("ECO_")]
    eco_values = {}
    eco_sum = 0

    for ind_id in eco_indicators:
        if HISTORICAL_DATA[ind_id]:
            latest_value = HISTORICAL_DATA[ind_id][-1]["value"]
            eco_values[ind_id] = latest_value
            eco_sum += latest_value

    eco_health = eco_sum / len(eco_indicators) if eco_indicators else 0

    # Political Stability: Average of all POL_ indicators
    pol_indicators = [k for k in HISTORICAL_DATA.keys() if k.startswith("POL_")]
    pol_values = {}
    pol_sum = 0

    for ind_id in pol_indicators:
        if HISTORICAL_DATA[ind_id]:
            latest_value = HISTORICAL_DATA[ind_id][-1]["value"]
            pol_values[ind_id] = latest_value
            pol_sum += latest_value

    pol_stability = pol_sum / len(pol_indicators) if pol_indicators else 0

    return [
        CompositeMetric(
            metric_id="ECONOMIC_HEALTH",
            name="Economic Health Index",
            value=eco_health,
            components=eco_values,
            last_updated=datetime.utcnow()
        ),
        CompositeMetric(
            metric_id="NATIONAL_STABILITY",
            name="National Stability Index",
            value=pol_stability,
            components=pol_values,
            last_updated=datetime.utcnow()
        )
    ]
