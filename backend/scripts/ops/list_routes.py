from app.main import app

print("All registered routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        if '/user/' in route.path:
            print(f"  {route.path} - {route.methods}")

print("\nOperational indicators route:")
op_routes = [r for r in app.routes if hasattr(r, 'path') and 'operational' in r.path]
if op_routes:
    for r in op_routes:
        print(f"  ✓ Found: {r.path} - {r.methods}")
else:
    print("  ✗ NOT FOUND")
