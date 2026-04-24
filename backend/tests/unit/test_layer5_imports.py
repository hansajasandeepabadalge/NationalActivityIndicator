"""
Test if Layer 5 imports work
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

print("Testing Layer 5 imports...")

try:
    from app.layer5.api import auth_router, admin_router, user_router, operations_router
    print("✅ Successfully imported all routers:")
    print(f"   - auth_router: {auth_router}")
    print(f"   - admin_router: {admin_router}")
    print(f"   - user_router: {user_router}")
    print(f"   - operations_router: {operations_router}")
except Exception as e:
    print(f"❌ Error importing routers: {e}")
    import traceback
    traceback.print_exc()
