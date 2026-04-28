import sys
import os
import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

# ---------------------------------------------------------------------------
# Lightweight stand-in for IndicatorDefinition (avoids SQLAlchemy ORM + DB)
# The real ORM model lives in app.models.indicator_models but requires a live
# DB session; for simulation purposes a simple dataclass is sufficient.
# ---------------------------------------------------------------------------
@dataclass
class IndicatorDefinition:
    indicator_id: str
    indicator_code: str
    indicator_name: str
    calculation_type: str
    min_value: float = 0.0
    max_value: float = 100.0
    is_active: bool = True


from app.layer2.indicators.registry import IndicatorRegistry
from app.layer2.indicators.frequency_calculator import FrequencyCalculator, KeywordDensityCalculator
from app.layer2.indicators.sentiment_calculator import SentimentCalculator
from app.layer2.analysis.trend_analyzer import TrendAnalyzer
from app.layer2.analysis.forecaster import Forecaster
from app.layer2.analysis.anomaly_detector import AnomalyDetector


def load_mock_data():
    # Resolve to backend/data/mock/mock_articles.json regardless of CWD
    mock_file = os.path.join(
        os.path.dirname(__file__), "../../data/mock/mock_articles.json"
    )
    mock_file = os.path.normpath(mock_file)

    if not os.path.exists(mock_file):
        raise FileNotFoundError(
            f"Mock data not found at {mock_file}. "
            "Run the mock data generation script first."
        )

    with open(mock_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Support both {"articles": [...]} wrapper and bare list
    if isinstance(data, dict):
        return data.get("articles", [])
    return data


def create_mock_indicators():
    return [
        IndicatorDefinition(
            indicator_id="POL_UNREST_01",
            indicator_code="POL_UNREST_01",
            indicator_name="Protest Frequency",
            calculation_type="frequency_count",
            min_value=0,
            max_value=50,
        ),
        IndicatorDefinition(
            indicator_id="ECON_SENTIMENT_01",
            indicator_code="ECON_SENTIMENT_01",
            indicator_name="Economic Sentiment",
            calculation_type="sentiment_analysis",
            min_value=0,
            max_value=100,
        ),
        IndicatorDefinition(
            indicator_id="ENV_FLOOD_01",
            indicator_code="ENV_FLOOD_01",
            indicator_name="Flood Risk",
            calculation_type="keyword_density",
            min_value=0,
            max_value=100,
        ),
    ]


def simulate_pipeline():
    print("Starting Pipeline Simulation...")

    # 1. Load Data
    print("\nLoading Mock Data...")
    all_articles = load_mock_data()
    print(f"   Loaded {len(all_articles)} articles.")

    # 2. Setup Indicators
    indicators = create_mock_indicators()

    # 3. Simulation Loop (Simulate 30 days of history)
    print("\nSimulating 30 days of history...")

    history = {ind.indicator_code: [] for ind in indicators}
    start_date = datetime.now() - timedelta(days=30)

    trend_analyzer = TrendAnalyzer()
    forecaster = Forecaster()
    anomaly_detector = AnomalyDetector()

    for i in range(31):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.isoformat()

        # Filter articles for this "day" (mock: random subset)
        sample_size = min(random.randint(5, 20), len(all_articles))
        daily_articles = random.sample(all_articles, k=sample_size)

        for ind in indicators:
            try:
                calculator = IndicatorRegistry.get_calculator(ind.calculation_type)
                value = calculator.calculate(daily_articles, ind)
            except ValueError:
                # Calculator not registered (e.g. sentiment_analysis) — use random fallback
                value = random.uniform(ind.min_value, ind.max_value)

            if ind.calculation_type == "sentiment_analysis":
                value += random.uniform(-5, 5)
                value = max(ind.min_value, min(ind.max_value, value))

            history[ind.indicator_code].append({"time": date_str, "value": value})

    # 4. Analysis & Reporting
    print("\nAnalysis Results:")

    for ind in indicators:
        code = ind.indicator_code
        ind_history = history[code]
        last_value = ind_history[-1]["value"]

        print(f"\n  Indicator: {ind.indicator_name} ({code})")
        print(f"   Current Value: {last_value:.2f}")

        trend = trend_analyzer.analyze_trend(ind_history)
        print(f"   Trend: {trend['direction'].upper()} (Strength: {trend['strength']:.2f})")
        ma_7d = trend.get("ma_7d")
        print(f"   MA(7d): {ma_7d:.2f}" if ma_7d is not None else "   MA(7d): N/A")

        forecast = forecaster.forecast(ind_history, days_ahead=3)
        if forecast:
            print(f"   Forecast (Next 3 days): {[round(f['value'], 2) for f in forecast]}")

        anomalies = anomaly_detector.detect_anomalies(ind_history)
        if anomalies:
            print(f"   Anomalies Detected: {len(anomalies)}")
            for a in anomalies:
                print(
                    f"      - {a['time'][:10]}: {a['type']} "
                    f"(Value: {a['value']:.2f}, Z: {a['z_score']:.2f})"
                )
        else:
            print("   No Anomalies Detected")

    print("\nPipeline Simulation Complete!")


if __name__ == "__main__":
    simulate_pipeline()
