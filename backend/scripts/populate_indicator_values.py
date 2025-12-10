"""
Test Script: Populate Indicator Values for Dashboard

This script generates sample indicator values and stores them to PostgreSQL
so the dashboard can display them.
"""

import sys
import os
import random
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.indicator_models import IndicatorDefinition, IndicatorValue


def generate_indicator_values():
    """Generate sample indicator values for all defined indicators."""
    
    print("=" * 60)
    print("POPULATING INDICATOR VALUES FOR DASHBOARD")
    print("=" * 60)
    
    db: Session = SessionLocal()
    
    try:
        # Get all active indicator definitions
        indicators = db.query(IndicatorDefinition).filter(
            IndicatorDefinition.is_active == True
        ).all()
        
        print(f"\n[1] Found {len(indicators)} active indicator definitions")
        
        if not indicators:
            print("   ❌ No indicator definitions found!")
            print("   Run the indicator population script first.")
            return
        
        # Generate values for each indicator
        now = datetime.utcnow()
        values_created = 0
        values_updated = 0
        
        print(f"\n[2] Generating indicator values...")
        
        for indicator in indicators:
            # Generate a realistic value based on category
            base_value = random.uniform(30, 70)
            
            # Add some category-specific variation
            if indicator.pestel_category == 'Economic':
                base_value = random.uniform(40, 75)
            elif indicator.pestel_category == 'Political':
                base_value = random.uniform(35, 65)
            elif indicator.pestel_category == 'Social':
                base_value = random.uniform(45, 70)
            elif indicator.pestel_category == 'Technological':
                base_value = random.uniform(50, 80)
            elif indicator.pestel_category == 'Environmental':
                base_value = random.uniform(40, 65)
            elif indicator.pestel_category == 'Legal':
                base_value = random.uniform(45, 70)
            
            # Add some noise
            value = base_value + random.uniform(-10, 10)
            value = max(0, min(100, value))  # Clamp to 0-100
            
            confidence = random.uniform(0.7, 0.95)
            source_count = random.randint(3, 25)
            
            # Check if value already exists for this timestamp
            existing = db.query(IndicatorValue).filter(
                IndicatorValue.indicator_id == indicator.indicator_id,
                IndicatorValue.timestamp >= now - timedelta(hours=1)
            ).first()
            
            if existing:
                # Update existing
                existing.value = value
                existing.confidence = confidence
                existing.source_count = source_count
                values_updated += 1
            else:
                # Create new value
                new_value = IndicatorValue(
                    indicator_id=indicator.indicator_id,
                    timestamp=now,
                    value=value,
                    raw_count=source_count,
                    sentiment_score=random.uniform(-0.3, 0.5),
                    confidence=confidence,
                    source_count=source_count,
                    extra_metadata={
                        'generated': True,
                        'generation_time': now.isoformat()
                    }
                )
                db.add(new_value)
                values_created += 1
        
        db.commit()
        
        print(f"   ✅ Created: {values_created} new values")
        print(f"   ✅ Updated: {values_updated} existing values")
        
        # Also generate historical values (last 7 days)
        print(f"\n[3] Generating 7 days of historical data...")
        
        historical_count = 0
        for day_offset in range(1, 8):
            historical_time = now - timedelta(days=day_offset)
            
            for indicator in indicators[:20]:  # Just first 20 for history
                # Check if exists
                existing = db.query(IndicatorValue).filter(
                    IndicatorValue.indicator_id == indicator.indicator_id,
                    IndicatorValue.timestamp >= historical_time - timedelta(hours=1),
                    IndicatorValue.timestamp <= historical_time + timedelta(hours=1)
                ).first()
                
                if not existing:
                    historical_value = IndicatorValue(
                        indicator_id=indicator.indicator_id,
                        timestamp=historical_time,
                        value=random.uniform(30, 70),
                        raw_count=random.randint(2, 20),
                        confidence=random.uniform(0.6, 0.9),
                        source_count=random.randint(2, 20)
                    )
                    db.add(historical_value)
                    historical_count += 1
        
        db.commit()
        print(f"   ✅ Created: {historical_count} historical values")
        
        # Verify by reading back
        print(f"\n[4] Verifying stored data...")
        
        total_values = db.query(IndicatorValue).count()
        print(f"   Total indicator values in database: {total_values}")
        
        # Show sample values
        print(f"\n[5] Sample indicator values:")
        sample_values = db.query(
            IndicatorDefinition.indicator_name,
            IndicatorDefinition.pestel_category,
            IndicatorValue.value,
            IndicatorValue.confidence,
            IndicatorValue.timestamp
        ).join(
            IndicatorValue,
            IndicatorDefinition.indicator_id == IndicatorValue.indicator_id
        ).order_by(
            IndicatorValue.timestamp.desc()
        ).limit(10).all()
        
        for name, category, value, confidence, ts in sample_values:
            print(f"   • {name[:40]:<40} [{category:<12}] = {value:.1f} (conf: {confidence:.2f})")
        
        print("\n" + "=" * 60)
        print("✅ INDICATOR VALUES POPULATED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNow refresh the dashboard to see the indicator values.")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    generate_indicator_values()
