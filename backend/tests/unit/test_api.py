"""
Test the operational indicators API endpoint
"""
import requests
import json

def test_api():
    """Test the API endpoint"""
    try:
        # First, try without auth to see what happens
        url = "http://localhost:8080/api/v1/user/operations-data"
        
        print(f"Testing: {url}")
        print("=" * 60)
        
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
