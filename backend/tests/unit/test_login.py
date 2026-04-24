"""
Test login API endpoint directly
"""
import requests
import json

def test_login():
    """Test the login endpoint"""
    url = "http://localhost:8080/api/v1/auth/login"
    
    payload = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print(f"Testing login at: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Login successful!")
            token = response.json().get("access_token")
            if token:
                print(f"\n🔑 Access Token: {token[:50]}...")
                
                # Test the operations endpoint with this token
                print("\n" + "=" * 60)
                print("Testing operations endpoint with token...")
                ops_url = "http://localhost:8080/api/v1/user/operations-data"
                headers = {"Authorization": f"Bearer {token}"}
                
                ops_response = requests.get(ops_url, headers=headers)
                print(f"Status Code: {ops_response.status_code}")
                
                if ops_response.status_code == 200:
                    data = ops_response.json()
                    print(f"✅ Got {data.get('total', 0)} operational indicators")
                    if data.get('indicators'):
                        print(f"Sample: {data['indicators'][0].get('indicator_name', 'N/A')}")
                else:
                    print(f"Response: {ops_response.text}")
        else:
            print("\n❌ Login failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login()
