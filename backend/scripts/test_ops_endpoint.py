"""
Test if the operations-data endpoint is accessible
"""
import requests

def test_endpoint():
    """Test the operational indicators endpoint"""
    
    # First, login to get a token
    login_url = "http://localhost:8080/api/v1/auth/login"
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print("="*70)
    print("TESTING /api/v1/user/operations-data ENDPOINT")
    print("="*70)
    
    try:
        print("\n[1] Logging in...")
        login_response = requests.post(login_url, json=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        print(f"   ✅ Got access token: {access_token[:20]}...")
        
        # Now test the operations endpoint
        print("\n[2] Testing /api/v1/user/operations-data...")
        ops_url = "http://localhost:8080/api/v1/user/operations-data?limit=20"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        ops_response = requests.get(ops_url, headers=headers)
        print(f"   Status: {ops_response.status_code}")
        
        if ops_response.status_code == 200:
            data = ops_response.json()
            print(f"   ✅ Success!")
            print(f"   Company ID: {data.get('company_id')}")
            print(f"   Total indicators: {data.get('total')}")
            print(f"   Indicators count: {len(data.get('indicators', []))}")
            
            if data.get('indicators'):
                print(f"\n   First indicator:")
                first = data['indicators'][0]
                print(f"     - ID: {first.get('indicator_id')}")
                print(f"     - Name: {first.get('indicator_name')}")
                print(f"     - Value: {first.get('current_value')}")
        else:
            print(f"   ❌ Failed: {ops_response.text}")
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint()
