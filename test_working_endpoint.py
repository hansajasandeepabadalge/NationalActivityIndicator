"""
Test the WORKING test-debug endpoint
"""
import requests

print("="*70)
print("TESTING WORKING /api/v1/user/test-debug ENDPOINT")
print("="*70)

# Login
print("\n[1] Logging in...")
login_response = requests.post("http://localhost:8080/api/v1/auth/login", json={
    "email": "admin@example.com",
    "password": "admin123"
})

if login_response.status_code != 200:
    print(f"   ❌ Login failed")
    exit(1)

token = login_response.json()["access_token"]
print(f"   ✅ Logged in")

# Test the working endpoint
print("\n[2] Testing /api/v1/user/test-debug...")
response = requests.get(
    "http://localhost:8080/api/v1/user/test-debug?limit=20",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"   Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   🎉 SUCCESS!")
    print(f"   Total: {data.get('total')}")
    print(f"   Indicators: {len(data.get('indicators', []))}")
    
    if data.get('indicators'):
        print(f"\n   First 5 indicators:")
        for i, ind in enumerate(data['indicators'][:5], 1):
            print(f"      {i}. {ind.get('indicator_name')}: {ind.get('current_value')}")
else:
    print(f"   ❌ Failed: {response.text}")

print("\n" + "="*70)
