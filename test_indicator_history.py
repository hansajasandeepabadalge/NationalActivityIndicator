"""
Test the indicator history API endpoint
"""
import requests

print("Testing Indicator History API Endpoint")
print("="*70)

# Login first
print("\n[1] Logging in...")
login_response = requests.post("http://localhost:8080/api/v1/auth/login", json={
    "email": "admin@example.com",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"   ❌ Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json()["access_token"]
print(f"   ✅ Logged in successfully")

# Test the history endpoint
print("\n[2] Testing /api/v1/indicators/supply_chain_health/history...")
history_response = requests.get(
    "http://localhost:8080/api/v1/indicators/supply_chain_health/history?days=7",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"   Status: {history_response.status_code}")

if history_response.status_code == 200:
    data = history_response.json()
    print(f"   🎉 SUCCESS!")
    print(f"   Indicator: {data.get('indicator_id')}")
    print(f"   Data points: {data.get('data_points')}")
    print(f"   Trend: {data.get('trend_summary', {}).get('trend')}")
    print(f"   Change: {data.get('trend_summary', {}).get('change_percent')}%")
else:
    print(f"   ❌ Failed: {history_response.text}")

print("\n" + "="*70)
