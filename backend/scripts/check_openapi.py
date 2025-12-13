"""
Check OpenAPI schema to see which endpoints are registered
"""
import requests
import json

print("Fetching OpenAPI schema...")
try:
    response = requests.get("http://localhost:8080/api/v1/openapi.json")
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get('paths', {})
        
        print(f"\n✅ Found {len(paths)} endpoints:")
        
        # Check for user operations endpoints
        user_ops_endpoints = [path for path in paths if '/user/operations' in path or '/user/test' in path]
        
        if user_ops_endpoints:
            print(f"\n📊 User operations endpoints found:")
            for path in user_ops_endpoints:
                print(f"   - {path}")
        else:
            print(f"\n❌ No user operations endpoints found!")
            
        # List all /user endpoints
        user_endpoints = [path for path in paths if path.startswith('/user')]
        print(f"\n📋 All /user endpoints ({len(user_endpoints)}):")
        for path in sorted(user_endpoints):
            methods = list(paths[path].keys())
            print(f"   - {path} [{', '.join(methods)}]")
            
    else:
        print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
