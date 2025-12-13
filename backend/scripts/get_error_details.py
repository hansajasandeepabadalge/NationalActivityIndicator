"""
Get detailed error response from the endpoint
"""
import requests

# Login
login_response = requests.post("http://localhost:8080/api/v1/auth/login", json={
    "email": "admin@example.com",
    "password": "admin123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    
    # Call operations endpoint
    print("Calling /api/v1/user/operations-data...")
    response = requests.get(
        "http://localhost:8080/api/v1/user/operations-data?limit=20",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"\nResponse headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nResponse body:")
    print(response.text)
