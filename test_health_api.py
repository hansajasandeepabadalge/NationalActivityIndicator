"""
Test script for System Health API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_health_endpoints():
    """Test all health monitoring endpoints"""
    
    endpoints = [
        "/health",
        "/health/status",
        "/health/metrics",
        "/health/database",
        "/health/errors",
        "/health/all",
    ]
    
    print("Testing System Health Endpoints")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"\nTesting: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}...")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error - Backend not running?")
        except requests.exceptions.Timeout:
            print("❌ Timeout - Backend too slow")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_health_endpoints()
