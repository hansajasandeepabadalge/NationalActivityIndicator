"""
Test LLM Classification with Groq API

This script tests that the LLM classifier is actually calling Groq API.
Sets environment variables BEFORE importing any Layer 2 modules.
"""

import os
import asyncio
import sys

# SET API KEYS BEFORE ANY IMPORTS
os.environ["GROQ_API_KEYS"] = "YOUR_GROQ_API_KEYS_HERE"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# NOW import the modules (they will see the env vars)
from app.layer2.services.llm_classifier import create_llm_classifier, LLMClassifier
from app.layer2.services.llm_base import api_key_manager, APIKeyManager

async def test_llm_classification():
    """Test LLM classification with actual API call."""
    print("\n" + "="*60)
    print("LLM CLASSIFICATION TEST")
    print("="*60)
    
    # Check API key manager status
    print("\n[1/4] Checking API Key Manager...")
    
    # Force reload keys since singleton might have been initialized without them
    if not api_key_manager.has_keys:
        print("  ⚠️ Re-initializing API key manager...")
        APIKeyManager._initialized = False
        api_key_manager.__init__()
    
    print(f"  API keys loaded: {api_key_manager.has_keys}")
    print(f"  Available keys: {api_key_manager.available_keys_count}")
    
    if api_key_manager.current_key:
        key_preview = f"...{api_key_manager.current_key[-8:]}"
        print(f"  Current key: {key_preview}")
    else:
        print("  ❌ No API key available!")
        return False
    
    # Create classifier
    print("\n[2/4] Creating LLM Classifier...")
    classifier = create_llm_classifier()
    
    print(f"  LLM Client available: {classifier.llm_client.is_available}")
    
    if not classifier.llm_client.is_available:
        print("  ❌ LLM Client not available!")
        return False
    
    # Test classification
    print("\n[3/4] Running classification (force_llm=True)...")
    
    test_article = """
    The Central Bank of Sri Lanka has announced a 0.5% reduction in interest rates, 
    bringing the policy rate down to 8.5%. The decision was made in response to 
    declining inflation and aims to stimulate economic growth. Governor Dr. Nandalal 
    Weerasinghe stated that this move will help boost lending and investment activity.
    The IMF welcomed the decision as part of ongoing economic reforms.
    """
    
    try:
        result = await classifier.classify(
            text=test_article,
            title="Central Bank Cuts Interest Rates by 0.5%",
            force_llm=True  # Force LLM usage
        )
        
        print("\n  ✅ Classification successful!")
        print(f"\n  Primary Category: {result.primary_category.value}")
        print(f"  Confidence: {result.primary_confidence:.2f}")
        print(f"  Classification Source: {result.classification_source}")
        print(f"  Processing Time: {result.processing_time_ms:.0f}ms")
        
        if result.all_categories:
            print("\n  All Categories:")
            for cat, conf in result.all_categories.items():
                print(f"    - {cat}: {conf:.2f}")
        
        if result.summary:
            print(f"\n  Summary: {result.summary[:100]}...")
        
        if result.key_entities:
            print(f"  Key Entities: {', '.join(result.key_entities[:5])}")
        
        # Check if it was actually an LLM call or fallback
        if result.classification_source == "llm":
            print("\n  🎉 CONFIRMED: LLM API was used!")
        else:
            print(f"\n  ⚠️ Used fallback: {result.classification_source}")
            
    except Exception as e:
        print(f"\n  ❌ Classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Show stats
    print("\n[4/4] Classification Statistics...")
    stats = classifier.get_stats()
    print(f"  Total classifications: {stats['total_classifications']}")
    print(f"  LLM classifications: {stats['llm_classifications']}")
    print(f"  Fallback classifications: {stats['fallback_classifications']}")
    print(f"  LLM usage rate: {stats['llm_usage_rate']:.0%}")
    
    llm_stats = stats.get('llm_client_stats', {})
    print(f"  LLM calls made: {llm_stats.get('llm_calls', 0)}")
    
    return result.classification_source == "llm"


def main():
    print("\n" + "="*60)
    print(" GROQ API TEST - LLM CLASSIFICATION")
    print("="*60)
    
    # Show env var status
    api_keys = os.environ.get("GROQ_API_KEYS", "")
    if api_keys:
        keys = api_keys.split(",")
        print(f"\n✅ GROQ_API_KEYS set with {len(keys)} key(s)")
        for i, k in enumerate(keys, 1):
            print(f"   Key {i}: ...{k[-8:]}")
    else:
        print("\n❌ GROQ_API_KEYS not set!")
        return 1
    
    success = asyncio.run(test_llm_classification())
    
    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS: LLM API is working!")
    else:
        print("❌ FAILED: LLM API not being used")
    print("="*60)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
