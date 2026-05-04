"""Test national indicators endpoint"""
import sys
import os
import json
from pathlib import Path

# Resolve backend root dynamically — works regardless of machine or CWD
_backend_root = str(Path(__file__).resolve().parent.parent.parent)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/v1")

# Test credentials — read from env so they never live in source code
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "")


def test_national_indicators():
    print("Testing national indicators endpoint...")

    if not ADMIN_PASSWORD:
        print("SKIP: TEST_ADMIN_PASSWORD env var not set — cannot authenticate")
        return

    # Login
    print(f"Logging in as {ADMIN_EMAIL}...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10,
    )

    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return

    token = login_response.json()["access_token"]
    print("Login successful, got token")

    # Test national indicators endpoint
    print("\nTesting /admin/indicators/national endpoint...")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/admin/indicators/national",
        headers=headers,
        params={"limit": 5},
        timeout=10,
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nFull response structure:")
        print(f"Keys: {list(data.keys())}")
        print(f"Total count: {data.get('total_count', 0)}")

        indicators = data.get("indicators", [])
        print(f"Number of indicators: {len(indicators)}")

        if indicators:
            print("\nFirst indicator:")
            print(json.dumps(indicators[0], indent=2))
        else:
            print("No indicators in response")
    else:
        print(f"Error response:")
        print(response.text)


if __name__ == "__main__":
    test_national_indicators()
