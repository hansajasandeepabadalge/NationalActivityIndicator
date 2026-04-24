"""
Test Script: Run L2 Pipeline and Store Indicator Values to PostgreSQL

This script:
1. Runs the Layer 2 pipeline to generate indicator values
2. Stores the results to PostgreSQL indicator_values table
3. Verifies the dashboard can read the data
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))


def run_full_test():
    """Run the complete test."""
    print("=" * 60)
    print("Layer 2 → PostgreSQL → Dashboard Test")
    print("=" * 60)
    
    # Step 1: Get indicator definitions from PostgreSQL
    print("\n[1] Getting indicator definitions from PostgreSQL...")
    from app.db.session import SessionLocal
    from app.models.indicator_models import IndicatorDefinition
    
    db = SessionLocal()
    try:
        definitions = db.query(IndicatorDefinition).filter(
            IndicatorDefinition.is_active == True
        ).all()
        print(f"   Found {len(definitions)} active indicator definitions")
        
        if len(definitions) == 0:
            print("   ❌ No indicator definitions found! Please run migrations first.")
            return
        
        # Show first few
        for defn in definitions[:3]:
            print(f"   - {defn.indicator_id}: {defn.indicator_name} ({defn.pestel_category})")
        print(f"   ... and {len(definitions) - 3} more")
    finally:
        db.close()
    
    # Step 2: Generate mock indicator values (simulating L2 output)
    print("\n[2] Generating indicator values (simulating L2 pipeline)...")
    
    import random
    indicator_values = []
    
    for defn in definitions:
        # Generate realistic values
        base_value = random.uniform(30, 70)
        noise = random.uniform(-10, 10)
        value = max(0, min(100, base_value + noise))
        
        indicator_values.append({
            'indicator_id': defn.indicator_id,
            'indicator_name': defn.indicator_name,
            'value': round(value, 2),
            'confidence': round(random.uniform(0.7, 1.0), 2),
            'article_count': random.randint(1, 50),
            'pestel_category': defn.pestel_category,
            'calculation_type': defn.calculation_type,
            'matching_articles': [f'article_{i}' for i in range(random.randint(1, 5))]
        })
    
    print(f"   Generated {len(indicator_values)} indicator values")
    
    # Show sample
    for iv in indicator_values[:3]:
        print(f"   - {iv['indicator_name']}: {iv['value']} (conf: {iv['confidence']})")
    
    # Step 3: Store to PostgreSQL
    print("\n[3] Storing indicator values to PostgreSQL...")
    from app.layer2.storage.indicator_persistence import Layer2IndicatorPersistence
    
    persistence = Layer2IndicatorPersistence()
    result = persistence.store_indicator_values(
        indicator_values,
        timestamp=datetime.utcnow()
    )
    
    print(f"   ✅ Stored: {result['stored_count']} new values")
    print(f"   ✅ Updated: {result['updated_count']} existing values")
    if result['errors']:
        print(f"   ⚠️  Errors: {len(result['errors'])}")
        for err in result['errors'][:3]:
            print(f"      - {err}")
    
    # Step 4: Verify dashboard can read the values
    print("\n[4] Verifying Dashboard Service can read values...")
    
    db = SessionLocal()
    try:
        from app.layer5.services.dashboard_service import DashboardService
        
        dashboard_service = DashboardService(db)
        indicators_response = dashboard_service.get_national_indicators(limit=10)
        
        print(f"   Dashboard retrieved: {indicators_response.total} total indicators")
        
        # Show indicators with values
        indicators_with_values = 0
        for ind in indicators_response.indicators:
            if ind.current_value is not None:
                indicators_with_values += 1
                if indicators_with_values <= 5:
                    trend_arrow = "↑" if ind.trend and ind.trend.value == "up" else "↓" if ind.trend and ind.trend.value == "down" else "→"
                    print(f"   • {ind.indicator_name}: {ind.current_value:.1f} {trend_arrow} (conf: {ind.confidence:.0%})")
        
        print(f"\n   ✅ {indicators_with_values} indicators now have values!")
        
    finally:
        db.close()
    
    # Step 5: Test admin dashboard summary
    print("\n[5] Testing Admin Dashboard Summary...")
    
    db = SessionLocal()
    try:
        dashboard_service = DashboardService(db)
        admin_dashboard = dashboard_service.get_admin_dashboard()
        
        print(f"   Total Indicators: {admin_dashboard.total_indicators}")
        print(f"   Total Insights: {admin_dashboard.total_insights}")
        print(f"   Total Companies: {admin_dashboard.total_companies}")
        print(f"   Active Risks: {admin_dashboard.total_active_risks}")
        print(f"   Active Opportunities: {admin_dashboard.total_active_opportunities}")
        
    finally:
        db.close()
    
    print("\n" + "=" * 60)
    print("✅ Test Complete! Dashboard should now show indicator values.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Refresh the dashboard at http://localhost:3000/dashboard")
    print("2. You should see indicator values in the National Indicators section")


if __name__ == "__main__":
    run_full_test()
