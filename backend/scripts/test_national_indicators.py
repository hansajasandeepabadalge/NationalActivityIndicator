"""Test national indicators endpoint"""
import sys
sys.path.insert(0, 'C:\\Users\\user\\Desktop\\National_Indicator\\NationalActivityIndicator_MAIN\\backend')

import requests
from app.core.config import settings

BASE_URL = "http://localhost:8080/api/v1"

def test_national_indicators():
    print("Testing national indicators endpoint...")

    # First, login as admin
    print("Logging in as admin...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin123"
        }
    )

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return

    token = login_response.json()["access_token"]
    print(f"Login successful, got token")

    # Test national indicators endpoint
    print("\nTesting /admin/indicators/national endpoint...")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/admin/indicators/national",
        headers=headers,
        params={"limit": 5}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nFull response structure:")
        print(f"Keys: {data.keys()}")
        print(f"Total count: {data.get('total_count', 0)}")

        indicators = data.get('indicators', [])
        print(f"Number of indicators: {len(indicators)}")

        if indicators:
            print(f"\nFirst indicator:")
            import json
            print(json.dumps(indicators[0], indent=2))
        else:
            print("No indicators in response")
    else:
        print(f"Error response:")
        print(response.text)

if __name__ == "__main__":
    test_national_indicators()
