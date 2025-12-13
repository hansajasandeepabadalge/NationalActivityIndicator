"""
Generate sample historical data for operational indicators.

Creates 30 days of historical snapshots with realistic trends.
"""
import sys
import os
from typing import List
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pymongo import MongoClient
from app.core.config import settings
from app.layer3.services.indicator_history_service import IndicatorHistoryService, IndicatorSnapshot


def generate_trend_values(
    start_value: float,
    days: int,
    trend_type: str = "stable",
    volatility: float = 0.05
) -> List[float]:
    """
    Generate realistic time-series values with trend.
    
    Args:
        start_value: Starting value
        days: Number of days
        trend_type: "increasing", "decreasing", or "stable"
        volatility: Random variation (0.0 to 1.0)
    
    Returns:
        List of values
    """
    values = [start_value]
    
    # Trend parameters
    if trend_type == "increasing":
        daily_change = start_value * 0.01  # 1% daily increase
    elif trend_type == "decreasing":
        daily_change = -start_value * 0.01  # 1% daily decrease
    else:
        daily_change = 0.0
    
    for _ in range(days - 1):
        # Apply trend
        new_value = values[-1] + daily_change
        
        # Add random volatility
        variation = new_value * volatility * (random.random() - 0.5) * 2
        new_value += variation
        
        # Ensure positive values
        new_value = max(0.1, new_value)
        
        values.append(new_value)
    
    return values


def main():
    print("="*70)
    print("GENERATING HISTORICAL INDICATOR DATA")
    print("="*70)
    
    # Connect to MongoDB
    print("\n[1] Connecting to MongoDB...")
    mongo_client = MongoClient(settings.MONGODB_URL)
    history_service = IndicatorHistoryService(
        mongo_client=mongo_client,
        db_name=settings.MONGODB_DB_NAME
    )
    print("   ✅ Connected")
    
    # Define indicators with their characteristics
    indicators = [
        {"id": "supply_chain_health", "start": 75.0, "trend": "increasing", "volatility": 0.08},
        {"id": "transportation_availability", "start": 80.0, "trend": "stable", "volatility": 0.05},
        {"id": "workforce_availability", "start": 70.0, "trend": "decreasing", "volatility": 0.10},
        {"id": "labor_cost_index", "start": 100.0, "trend": "increasing", "volatility": 0.06},
        {"id": "power_reliability", "start": 85.0, "trend": "increasing", "volatility": 0.07},
        {"id": "fuel_availability", "start": 75.0, "trend": "decreasing", "volatility": 0.09},
        {"id": "cost_pressure_index", "start": 100.0, "trend": "increasing", "volatility": 0.08},
        {"id": "demand_level", "start": 90.0, "trend": "increasing", "volatility": 0.06},
        {"id": "cash_flow_health", "start": 75.0, "trend": "decreasing", "volatility": 0.10},
        {"id": "regulatory_burden", "start": 60.0, "trend": "stable", "volatility": 0.04},
        {"id": "raw_material_availability", "start": 75.0, "trend": "stable", "volatility": 0.06},
        {"id": "production_capacity", "start": 80.0, "trend": "increasing", "volatility": 0.05},
        {"id": "inventory_turnover", "start": 7.0, "trend": "stable", "volatility": 0.08},
        {"id": "quality_compliance", "start": 90.0, "trend": "increasing", "volatility": 0.03},
        {"id": "customer_satisfaction", "start": 85.0, "trend": "increasing", "volatility": 0.04},
        {"id": "market_share", "start": 15.0, "trend": "increasing", "volatility": 0.05},
        {"id": "employee_retention", "start": 88.0, "trend": "stable", "volatility": 0.04},
        {"id": "technology_adoption", "start": 70.0, "trend": "increasing", "volatility": 0.06},
        {"id": "environmental_compliance", "start": 90.0, "trend": "stable", "volatility": 0.03},
        {"id": "safety_record", "start": 93.0, "trend": "increasing", "volatility": 0.02},
    ]
    
    # Generate 30 days of history
    days = 30
    print(f"\n[2] Generating {days} days of historical data for {len(indicators)} indicators...")
    
    all_snapshots = []
    end_date = datetime.utcnow()
    
    for indicator in indicators:
        print(f"   - {indicator['id']}: {indicator['trend']} trend")
        
        # Generate values
        values = generate_trend_values(
            start_value=indicator["start"],
            days=days,
            trend_type=indicator["trend"],
            volatility=indicator["volatility"]
        )
        
        # Create snapshots
        for day_offset, value in enumerate(values):
            timestamp = end_date - timedelta(days=days - day_offset - 1)
            
            snapshot = IndicatorSnapshot(
                indicator_id=indicator["id"],
                company_id=None,  # National indicator
                timestamp=timestamp,
                value=round(value, 2),
                baseline_value=indicator["start"],
                deviation=round(value - indicator["start"], 2),
                impact_score=round(random.uniform(5.0, 9.5), 1),
                metadata={
                    "trend_type": indicator["trend"],
                    "generated": True
                }
            )
            all_snapshots.append(snapshot)
    
    # Save to database
    print(f"\n[3] Saving {len(all_snapshots)} snapshots to MongoDB...")
    count = history_service.bulk_save_snapshots(all_snapshots)
    print(f"   ✅ Saved {count} snapshots")
    
    # Verify and show sample
    print("\n[4] Verifying data...")
    sample_indicator = indicators[0]["id"]
    history = history_service.get_history(sample_indicator, days=7)
    print(f"   Sample: {sample_indicator} has {len(history)} data points in last 7 days")
    
    # Get trend summary
    trend = history_service.get_trend_summary(sample_indicator, days=7)
    print(f"   Trend: {trend['trend']}, Change: {trend['change_percent']}%")
    
    print("\n" + "="*70)
    print("✅ HISTORICAL DATA GENERATION COMPLETE")
    print("="*70)
    print(f"\nGenerated {count} snapshots for {len(indicators)} indicators over {days} days")
    print("You can now use the historical chart features!")
    
    mongo_client.close()


if __name__ == "__main__":
    main()
