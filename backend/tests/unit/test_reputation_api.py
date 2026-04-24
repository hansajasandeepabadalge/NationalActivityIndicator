"""
Test Source Reputation API Endpoints

Quick test script to verify API endpoints work correctly.
Run this after starting the FastAPI server.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def test_get_sources():
    """Test GET /reputation/sources"""
    print_header("Test: GET /reputation/sources")
    
    try:
        response = requests.get(f"{BASE_URL}/reputation/sources", params={"limit": 5})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('sources', []))} sources")
            for source in data.get('sources', [])[:3]:
                print(f"   - {source.get('source_name')}: {source.get('reputation_score'):.3f} ({source.get('reputation_tier')})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


def test_get_summary():
    """Test GET /reputation/summary"""
    print_header("Test: GET /reputation/summary")
    
    try:
        response = requests.get(f"{BASE_URL}/reputation/summary")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reputation Summary:")
            print(f"   Total Sources: {data.get('total_sources')}")
            print(f"   Active Sources: {data.get('active_sources')}")
            print(f"   Average Reputation: {data.get('average_reputation', 0):.3f}")
            print(f"   Tier Distribution: {data.get('tier_distribution')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


def test_get_analytics():
    """Test GET /reputation/analytics"""
    print_header("Test: GET /reputation/analytics")
    
    try:
        response = requests.get(f"{BASE_URL}/reputation/analytics", params={"hours": 24})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filter Analytics (24h):")
            print(f"   Total Filtered: {data.get('total_filtered')}")
            print(f"   Acceptance Rate: {data.get('acceptance_rate', 0):.2%}")
            print(f"   Actions: {data.get('action_breakdown')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


def test_get_tiers():
    """Test GET /reputation/tiers"""
    print_header("Test: GET /reputation/tiers")
    
    try:
        for tier in ["gold", "silver", "bronze"]:
            response = requests.get(f"{BASE_URL}/reputation/tiers/{tier}")
            print(f"\n{tier.upper()} Tier (Status: {response.status_code}):")
            
            if response.status_code == 200:
                data = response.json()
                sources = data.get('sources', [])
                print(f"   Found {len(sources)} sources")
                for source in sources[:2]:
                    print(f"   - {source.get('source_name')}: {source.get('reputation_score'):.3f}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


def test_batch_filter():
    """Test POST /reputation/filter"""
    print_header("Test: POST /reputation/filter")
    
    try:
        payload = {
            "articles": [
                {"id": "test_art_1", "source_name": "Test News Source"},
                {"id": "test_art_2", "source_name": "Unknown Source"}
            ],
            "quality_scores": {
                "test_art_1": 75.0,
                "test_art_2": 35.0
            }
        }
        
        response = requests.post(f"{BASE_URL}/reputation/filter", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch Filter Results:")
            print(f"   Accepted: {data.get('accepted_count')}")
            print(f"   Rejected: {data.get('rejected_count')}")
            print(f"   Flagged: {data.get('flagged_count')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")


def main():
    print("\n🔍 Testing Source Reputation API Endpoints")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Time: {datetime.now()}")
    
    # Run tests
    test_get_sources()
    test_get_summary()
    test_get_analytics()
    test_get_tiers()
    test_batch_filter()
    
    print("\n" + "="*60)
    print(" Test Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
