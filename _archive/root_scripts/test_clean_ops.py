"""
Test the CLEAN operational indicators endpoint at /api/v1/ops/indicators
"""
import requests

def test_clean_endpoint():
    """Test the new /api/v1/ops/indicators endpoint"""
    
    print("="*70)
    print("TESTING CLEAN /api/v1/ops/indicators ENDPOINT")
    print("="*70)
    
    # Login
    print("\n[1] Logging in...")
    login_response = requests.post("http://localhost:8080/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed")
        return
    
    token = login_response.json()["access_token"]
    print(f"   ✅ Logged in")
    
    # Test simple endpoint
    print("\n[2] Testing /api/v1/ops/test...")
    test_response = requests.get(
        "http://localhost:8080/api/v1/ops/test",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"   Status: {test_response.status_code}")
    if test_response.status_code == 200:
        print(f"   ✅ {test_response.json()}")
    
    # Test indicators endpoint
    print("\n[3] Testing /api/v1/ops/indicators...")
    ops_response = requests.get(
        "http://localhost:8080/api/v1/ops/indicators?limit=20",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"   Status: {ops_response.status_code}")
    
    if ops_response.status_code == 200:
        data = ops_response.json()
        print(f"   🎉 SUCCESS!")
        print(f"   Total: {data.get('total')}")
        print(f"   Indicators: {len(data.get('indicators', []))}")
        
        if data.get('indicators'):
            print(f"\n   First 3:")
            for i, ind in enumerate(data['indicators'][:3], 1):
                print(f"      {i}. {ind.get('indicator_name')}: {ind.get('current_value')}")
    else:
        print(f"   ❌ Failed: {ops_response.text}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_clean_endpoint()
