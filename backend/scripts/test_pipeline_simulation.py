import sys
import os
import json
import random
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.models.indicator import IndicatorDefinition
from app.layer2.indicators.registry import IndicatorRegistry
from app.layer2.indicators.frequency_calculator import FrequencyCalculator, KeywordDensityCalculator
from app.layer2.indicators.sentiment_calculator import SentimentCalculator
from app.layer2.analysis.trend_analyzer import TrendAnalyzer
from app.layer2.analysis.forecaster import Forecaster
from app.layer2.analysis.anomaly_detector import AnomalyDetector

def load_mock_data():
    mock_dir = os.path.join(os.path.dirname(__file__), "../mock_data")
    articles = []
    for filename in os.listdir(mock_dir):
        if filename.endswith(".json"):
            with open(os.path.join(mock_dir, filename), 'r') as f:
                articles.extend(json.load(f))
    return articles

def create_mock_indicators():
    return [
        IndicatorDefinition(
            indicator_id=1,
            indicator_code="POL_UNREST_01",
            indicator_name="Protest Frequency",
            calculation_type="frequency_count",
            min_value=0,
            max_value=50
        ),
        IndicatorDefinition(
            indicator_id=2,
            indicator_code="ECON_SENTIMENT_01",
            indicator_name="Economic Sentiment",
            calculation_type="sentiment_analysis",
            min_value=0,
            max_value=100
        ),
        IndicatorDefinition(
            indicator_id=3,
            indicator_code="ENV_FLOOD_01",
            indicator_name="Flood Risk",
            calculation_type="keyword_density",
            min_value=0,
            max_value=100
        )
    ]

def simulate_pipeline():
    print("🚀 Starting Pipeline Simulation...")
    
    # 1. Load Data
    print("\n📥 Loading Mock Data...")
    all_articles = load_mock_data()
    print(f"   Loaded {len(all_articles)} articles.")
    
    # 2. Setup Indicators
    indicators = create_mock_indicators()
    
    # 3. Simulation Loop (Simulate 30 days of history)
    print("\n🔄 Simulating 30 days of history...")
    
    history = {ind.indicator_code: [] for ind in indicators}
    
    start_date = datetime.now() - timedelta(days=30)
    
    trend_analyzer = TrendAnalyzer()
    forecaster = Forecaster()
    anomaly_detector = AnomalyDetector()
    
    for i in range(31):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.isoformat()
        
        # Filter articles for this "day" (Mocking: just pick random subset)
        daily_articles = random.sample(all_articles, k=random.randint(5, 20))
        
        for ind in indicators:
            # Calculate
            calculator = IndicatorRegistry.get_calculator(ind.calculation_type)
            value = calculator.calculate(daily_articles, ind)
            
            # Add some random noise for realism
            if ind.calculation_type == "sentiment_analysis":
                value += random.uniform(-5, 5)
                value = max(0, min(100, value))
            
            # Store
            history[ind.indicator_code].append({
                "time": date_str,
                "value": value
            })
            
    # 4. Analysis & Reporting
    print("\n📊 Analysis Results:")
    
    for ind in indicators:
        code = ind.indicator_code
        ind_history = history[code]
        last_value = ind_history[-1]['value']
        
        print(f"\n🔹 Indicator: {ind.indicator_name} ({code})")
        print(f"   Current Value: {last_value:.2f}")
        
        # Trend
        trend = trend_analyzer.analyze_trend(ind_history)
        print(f"   Trend: {trend['direction'].upper()} (Strength: {trend['strength']:.2f})")
        print(f"   MA(7d): {trend['ma_7d']:.2f}")
        
        # Forecast
        forecast = forecaster.forecast(ind_history, days_ahead=3)
        if forecast:
            print(f"   Forecast (Next 3 days): {[round(f['value'], 2) for f in forecast]}")
            
        # Anomalies
        anomalies = anomaly_detector.detect_anomalies(ind_history)
        if anomalies:
            print(f"   ⚠️ Anomalies Detected: {len(anomalies)}")
            for a in anomalies:
                print(f"      - {a['time'][:10]}: {a['type']} (Value: {a['value']:.2f}, Z: {a['z_score']:.2f})")
        else:
            print("   ✅ No Anomalies Detected")

    print("\n🎉 Pipeline Simulation Complete!")

if __name__ == "__main__":
    simulate_pipeline()
