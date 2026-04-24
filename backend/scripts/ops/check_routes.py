"""Check all registered routes in the FastAPI app"""
import sys
sys.path.insert(0, 'C:\\Users\\user\\Desktop\\National_Indicator\\NationalActivityIndicator_MAIN\\backend')

from app.main import app

print("=== All Routes ===")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        if 'history' in route.path.lower():
            print(f"{list(route.methods)} {route.path}")

print("\n=== Admin Routes with 'history' ===")
from app.layer5.api import admin_router
for route in admin_router.routes:
    if hasattr(route, 'path') and 'history' in route.path.lower():
        methods = list(route.methods) if hasattr(route, 'methods') else ['N/A']
        print(f"{methods} {route.path}")
