"""
Test if the new module can be imported
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("Testing imports...")

try:
    print("\n[1] Importing operational_indicators_v2...")
    from app.layer5.api import operational_indicators_v2
    print(f"   ✅ Success! Module: {operational_indicators_v2}")
    print(f"   Router: {operational_indicators_v2.router}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n[2] Importing ops_v2_router from __init__...")
    from app.layer5.api import ops_v2_router
    print(f"   ✅ Success! Router: {ops_v2_router}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
