"""
Test Multi-API Key Support for Groq

This script tests the API key rotation mechanism.
Run with: python -m scripts.test_multi_api_keys

You can set multiple API keys using:
- GROQ_API_KEY: Single key (existing behavior)
- GROQ_API_KEYS: Comma-separated list of keys (new feature)

Example:
set GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3
python -m scripts.test_multi_api_keys
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_key_manager():
    """Test the API key manager functionality."""
    from app.layer2.services.llm_base import api_key_manager, APIKeyManager
    
    print("\n" + "="*60)
    print("TESTING API KEY MANAGER")
    print("="*60)
    
    # Get stats
    stats = api_key_manager.get_stats()
    print(f"\n✓ Total API keys loaded: {stats['total_keys']}")
    print(f"✓ Available keys: {stats['available_keys']}")
    print(f"✓ Current key: {stats['current_key']}")
    
    if stats['total_keys'] > 0:
        print("\nKey Status:")
        for key_id, status in stats['key_status'].items():
            print(f"  - {key_id}: available={status['available']}, calls={status['total_calls']}")
    else:
        print("\n⚠ No API keys found!")
        print("Set GROQ_API_KEY or GROQ_API_KEYS environment variable")
    
    return stats['total_keys'] > 0


def test_llm_with_rotation():
    """Test LLM call with key rotation."""
    from app.layer2.services.llm_classifier import LLMClassifier
    
    print("\n" + "="*60)
    print("TESTING LLM CLASSIFIER WITH KEY ROTATION")
    print("="*60)
    
    classifier = LLMClassifier()
    
    # Get initial stats
    stats = classifier.get_stats()
    print(f"\n✓ LLM Available: {stats.get('llm_available')}")
    print(f"✓ Current API Key: {stats.get('current_api_key')}")
    
    if stats.get('api_keys_stats'):
        print(f"✓ Total Keys: {stats['api_keys_stats'].get('total_keys')}")
        print(f"✓ Available Keys: {stats['api_keys_stats'].get('available_keys')}")
    
    # Test classification
    test_text = """
    The central bank announced a 0.5% interest rate hike today, 
    citing concerns about rising inflation. The economy is showing 
    signs of slowing growth, with GDP projections revised downward.
    """
    
    print("\n📝 Testing classification...")
    result = classifier.classify(test_text)
    
    if result:
        print(f"✓ Classification successful!")
        print(f"  Source: {result.get('source', 'unknown')}")
        print(f"  Primary Category: {result.get('primary_category', 'unknown')}")
        print(f"  Secondary Categories: {result.get('secondary_categories', [])}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
    else:
        print("✗ Classification failed (returned None)")
    
    # Get updated stats
    stats = classifier.get_stats()
    print(f"\n📊 Updated Stats:")
    print(f"  Total Calls: {stats.get('total_calls')}")
    print(f"  LLM Calls: {stats.get('llm_calls')}")
    print(f"  Cache Hits: {stats.get('cache_hits')}")
    print(f"  Key Rotations: {stats.get('key_rotations', 0)}")
    print(f"  Errors: {stats.get('errors')}")
    
    return result is not None


def show_usage_instructions():
    """Show instructions for setting up multiple API keys."""
    print("\n" + "="*60)
    print("HOW TO USE MULTIPLE API KEYS")
    print("="*60)
    
    print("""
To use multiple API keys for rate limit handling:

1. Generate additional Groq API keys from: https://console.groq.com

2. Set environment variable with comma-separated keys:

   Windows (PowerShell):
   $env:GROQ_API_KEYS = "gsk_key1,gsk_key2,gsk_key3"

   Windows (CMD):
   set GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3

   Linux/Mac:
   export GROQ_API_KEYS="gsk_key1,gsk_key2,gsk_key3"

3. Or add to .env file:
   GROQ_API_KEYS=gsk_key1,gsk_key2,gsk_key3

The system will automatically:
- Use the first available key
- Rotate to next key when rate limit is hit
- Track usage stats per key
- Reset rate-limited keys after cooldown period
""")


def main():
    """Main test function."""
    print("\n" + "="*60)
    print("MULTI-API KEY SUPPORT TEST")
    print("="*60)
    
    # Check current environment
    single_key = os.getenv("GROQ_API_KEY", "")
    multi_keys = os.getenv("GROQ_API_KEYS", "")
    
    print(f"\n📋 Environment Check:")
    print(f"  GROQ_API_KEY: {'Set (' + single_key[-4:] + '...)' if single_key else 'Not set'}")
    print(f"  GROQ_API_KEYS: {'Set (' + str(len(multi_keys.split(','))) + ' keys)' if multi_keys else 'Not set'}")
    
    # Test API key manager
    has_keys = test_api_key_manager()
    
    if has_keys:
        # Test LLM with rotation
        success = test_llm_with_rotation()
        
        if success:
            print("\n" + "="*60)
            print("✅ MULTI-API KEY SUPPORT WORKING!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠ LLM call failed - check rate limits or API key validity")
            print("="*60)
    else:
        show_usage_instructions()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
