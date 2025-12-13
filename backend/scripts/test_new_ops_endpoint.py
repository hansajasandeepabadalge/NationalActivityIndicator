"""
Test the NEW operational indicators endpoint
"""
import requests

def test_new_endpoint():
    """Test the new /user/operational-indicators endpoint"""
    
    # Login
    print("="*70)
    print("TESTING NEW /api/v1/user/operational-indicators ENDPOINT")
    print("="*70)
    
    print("\n[1] Logging in...")
    login_response = requests.post("http://localhost:8080/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"   ✅ Logged in successfully")
    
    # Test simple endpoint first
    print("\n[2] Testing /api/v1/user/test-ops-simple...")
    test_response = requests.get(
        "http://localhost:8080/api/v1/user/test-ops-simple",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"   Status: {test_response.status_code}")
    if test_response.status_code == 200:
        print(f"   Response: {test_response.json()}")
    else:
        print(f"   Error: {test_response.text}")
    
    # Test operational indicators endpoint
    print("\n[3] Testing /api/v1/user/operational-indicators...")
    ops_response = requests.get(
        "http://localhost:8080/api/v1/user/operational-indicators?limit=20",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {ops_response.status_code}")
    
    if ops_response.status_code == 200:
        data = ops_response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Company ID: {data.get('company_id')}")
        print(f"   Total: {data.get('total')}")
        print(f"   Critical: {data.get('critical_count')}")
        print(f"   Warning: {data.get('warning_count')}")
        print(f"   Indicators: {len(data.get('indicators', []))}")
        
        if data.get('indicators'):
            print(f"\n   First 3 indicators:")
            for i, ind in enumerate(data['indicators'][:3], 1):
                print(f"      {i}. {ind.get('indicator_name')}: {ind.get('current_value')}")
    else:
        print(f"   ❌ Failed: {ops_response.text}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_new_endpoint()
