"""Test batch history endpoint"""
import sys
sys.path.insert(0, 'C:\\Users\\user\\Desktop\\National_Indicator\\NationalActivityIndicator_MAIN\\backend')

import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_batch_history():
    print("Testing batch history endpoint...")

    # Login as admin
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
        return

    token = login_response.json()["access_token"]
    print("Login successful")

    # Get some indicator IDs first
    print("\nGetting indicator IDs...")
    headers = {"Authorization": f"Bearer {token}"}
    indicators_response = requests.get(
        f"{BASE_URL}/admin/indicators/national",
        headers=headers,
        params={"limit": 3}
    )

    if indicators_response.status_code != 200:
        print(f"Failed to get indicators: {indicators_response.status_code}")
        return

    indicators = indicators_response.json()["indicators"]
    indicator_ids = [ind["indicator_id"] for ind in indicators]
    print(f"Got {len(indicator_ids)} indicator IDs: {indicator_ids}")

    # Test batch history endpoint
    print("\nTesting batch history endpoint...")
    batch_response = requests.post(
        f"{BASE_URL}/admin/indicators/national/history/batch",
        headers=headers,
        json={
            "indicator_ids": indicator_ids,
            "days": 30
        }
    )

    print(f"Status Code: {batch_response.status_code}")

    if batch_response.status_code == 200:
        data = batch_response.json()
        print(f"\nBatch history response:")
        print(f"Keys: {list(data.keys())}")
        for ind_id in indicator_ids[:2]:  # Show first 2
            history = data.get(ind_id, {})
            if isinstance(history, dict):
                history_list = history.get('history', [])
                print(f"\n{ind_id}: {len(history_list)} history points")
                if history_list:
                    print(f"  First point: {history_list[0]}")
            elif isinstance(history, list):
                print(f"\n{ind_id}: {len(history)} history points")
                if history:
                    print(f"  First point: {history[0]}")
    else:
        print(f"Error response:")
        print(batch_response.text)

if __name__ == "__main__":
    test_batch_history()
