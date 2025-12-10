"""
Populate Indicator Dependencies in Database.

Defines relationships between indicators for cascade effect prediction.
Run: python scripts/populate_dependencies.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models import IndicatorDependency

# Indicator dependency definitions
DEPENDENCIES = [
    # Economic chain effects
    {
        "parent_indicator_id": "ECON_FUEL_01",
        "child_indicator_id": "TECH_TRANSPORT_01",
        "relationship_type": "causes",
        "weight": 0.85
    },
    {
        "parent_indicator_id": "ECON_FUEL_01",
        "child_indicator_id": "ECON_INFLATION_01",
        "relationship_type": "causes",
        "weight": 0.70
    },
    {
        "parent_indicator_id": "ECON_CURRENCY_01",
        "child_indicator_id": "ECON_INFLATION_01",
        "relationship_type": "causes",
        "weight": 0.75
    },
    {
        "parent_indicator_id": "ECON_INFLATION_01",
        "child_indicator_id": "ECON_CONFIDENCE_01",
        "relationship_type": "causes",
        "weight": -0.65
    },
    {
        "parent_indicator_id": "ECON_CONFIDENCE_01",
        "child_indicator_id": "ECON_BIZ_SENTIMENT_01",
        "relationship_type": "correlates",
        "weight": 0.60
    },
    
    # Political chain effects
    {
        "parent_indicator_id": "POL_UNREST_01",
        "child_indicator_id": "ECON_CURRENCY_01",
        "relationship_type": "influences",
        "weight": -0.55
    },
    {
        "parent_indicator_id": "POL_UNREST_01",
        "child_indicator_id": "ECON_TOURISM_01",
        "relationship_type": "causes",
        "weight": -0.70
    },
    {
        "parent_indicator_id": "POL_POLICY_01",
        "child_indicator_id": "ECON_BIZ_SENTIMENT_01",
        "relationship_type": "influences",
        "weight": 0.45
    },
    
    # Environmental chain effects
    {
        "parent_indicator_id": "ENV_WEATHER_01",
        "child_indicator_id": "ENV_FLOOD_01",
        "relationship_type": "causes",
        "weight": 0.80
    },
    {
        "parent_indicator_id": "ENV_FLOOD_01",
        "child_indicator_id": "TECH_TRANSPORT_01",
        "relationship_type": "causes",
        "weight": -0.75
    },
    {
        "parent_indicator_id": "ENV_DROUGHT_01",
        "child_indicator_id": "ECON_INFLATION_01",
        "relationship_type": "influences",
        "weight": 0.40
    },
    
    # Social chain effects
    {
        "parent_indicator_id": "SOC_COST_LIVING_01",
        "child_indicator_id": "SOC_SENTIMENT_01",
        "relationship_type": "causes",
        "weight": -0.70
    },
    {
        "parent_indicator_id": "TECH_POWER_01",
        "child_indicator_id": "ECON_BIZ_SENTIMENT_01",
        "relationship_type": "causes",
        "weight": -0.55
    },
]


def populate_dependencies():
    """Insert dependencies into database"""
    session = SessionLocal()
    
    try:
        added = 0
        skipped = 0
        
        for dep_data in DEPENDENCIES:
            # Check if exists
            existing = session.query(IndicatorDependency).filter_by(
                parent_indicator_id=dep_data["parent_indicator_id"],
                child_indicator_id=dep_data["child_indicator_id"]
            ).first()
            
            if existing:
                print(f"  SKIP: {dep_data['parent_indicator_id']} -> {dep_data['child_indicator_id']}")
                skipped += 1
                continue
            
            dep = IndicatorDependency(**dep_data)
            session.add(dep)
            print(f"  ADD:  {dep_data['parent_indicator_id']} -> {dep_data['child_indicator_id']}")
            added += 1
        
        session.commit()
        print(f"\nDone! Added: {added}, Skipped: {skipped}")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    print("Populating Indicator Dependencies...")
    print("-" * 40)
    populate_dependencies()
