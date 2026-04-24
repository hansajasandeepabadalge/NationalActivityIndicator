"""
Test if the API is accessible and check docs
"""
import requests

# Test health endpoint
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:8080/api/v1/health")
    print(f"Health endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test API docs
print("\nChecking if API docs are accessible...")
try:
    response = requests.get("http://localhost:8080/api/v1/docs")
    print(f"API docs: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test operations test endpoint
print("\nTesting /user/test-simple endpoint...")
try:
    response = requests.get("http://localhost:8080/api/v1/user/test-simple")
    print(f"Test endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
