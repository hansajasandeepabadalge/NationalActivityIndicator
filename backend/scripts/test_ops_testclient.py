"""
Check backend logs for the 500 error
Run the endpoint and capture the error
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_operations_endpoint():
    """Test the operations endpoint with TestClient"""
    
    print("="*70)
    print("TESTING OPERATIONS ENDPOINT WITH TEST CLIENT")
    print("="*70)
    
    # Login first
    print("\n[1] Logging in...")
    login_response = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.json()}")
        return
    
    token = login_response.json()["access_token"]
    print(f"   ✅ Logged in successfully")
    
    # Test operations endpoint
    print("\n[2] Testing /api/v1/user/operations-data...")
    try:
        response = client.get(
            "/api/v1/user/operations-data?limit=20",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            print(f"   Total: {data.get('total')}")
            print(f"   Indicators: {len(data.get('indicators', []))}")
        else:
            print(f"   ❌ Error response:")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception occurred:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_operations_endpoint()
