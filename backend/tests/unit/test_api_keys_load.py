"""Test API key loading and rotation."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("API Key Loading Test")
print("=" * 60)

# Check raw environment variables
groq_api_keys = os.getenv("GROQ_API_KEYS", "")
groq_api_key = os.getenv("GROQ_API_KEY", "")

print(f"\n1. Environment Variables:")
print(f"   GROQ_API_KEYS: {'SET' if groq_api_keys else 'NOT SET'}")
print(f"   GROQ_API_KEY:  {'SET' if groq_api_key else 'NOT SET'}")

if groq_api_keys:
    keys = [k.strip() for k in groq_api_keys.split(",") if k.strip()]
    print(f"\n2. Parsed Keys from GROQ_API_KEYS: {len(keys)}")
    for i, key in enumerate(keys, 1):
        print(f"   Key {i}: ...{key[-12:]}")

# Test APIKeyManager
print(f"\n3. Testing APIKeyManager:")
try:
    from app.layer2.services.llm_base import APIKeyManager, api_key_manager
    
    print(f"   Keys loaded: {len(api_key_manager._keys)}")
    
    # Get stats
    stats = api_key_manager.get_stats()
    print(f"   Manager stats: {stats}")
    
    # Test getting next key
    next_key = api_key_manager.get_next_available_key()
    if next_key:
        print(f"\n   Next available key: ...{next_key[-12:]}")
    else:
        print(f"\n   ERROR: No available key returned!")
        
    # Test that all 3 keys can be accessed
    print(f"\n4. Testing Key Rotation:")
    current_index = api_key_manager._current_index
    for i in range(len(api_key_manager._keys)):
        key = api_key_manager._keys[(current_index + i) % len(api_key_manager._keys)]
        key_id = api_key_manager._get_key_id(key)
        print(f"   Key {i+1}: {key_id}")
        
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
