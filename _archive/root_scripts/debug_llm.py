"""
Debug LLM classification to see exactly what's happening
"""
import os
import asyncio
import sys

# SET API KEYS BEFORE ANY IMPORTS
os.environ["GROQ_API_KEYS"] = "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,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"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.layer2.services.llm_classifier import create_llm_classifier
from app.layer2.services.llm_base import api_key_manager

async def test():
    print("=== DEBUG LLM CLASSIFICATION ===\n")
    
    # Check API key status
    print(f"API keys loaded: {api_key_manager.has_keys}")
    print(f"Available keys: {api_key_manager.available_keys_count}")
    if api_key_manager.current_key:
        print(f"Current key: ...{api_key_manager.current_key[-8:]}")
    
    # Create classifier
    classifier = create_llm_classifier()
    
    print(f"\nLLM Client available: {classifier.llm_client.is_available}")
    print(f"Min text length: {classifier.min_text_length}")
    print(f"LLM threshold: {classifier.use_llm_threshold}")
    
    # Test with a real article
    test_text = """
    Sri Lanka's economy shows signs of recovery as inflation drops to 4.2% in November 2024,
    the lowest in three years. The Central Bank has maintained interest rates steady amid
    improving economic conditions. Foreign direct investment has increased by 15% compared
    to last year, with technology and manufacturing sectors leading the growth.
    """
    
    print(f"\nTest text length: {len(test_text)}")
    print(f"Should use LLM: {classifier._should_use_llm(test_text)}")
    print(f"LLM client should use LLM: {classifier.llm_client._should_use_llm(test_text, classifier.use_llm_threshold)}")
    
    # Run classification WITHOUT force_llm (as pipeline does)
    print("\n--- Classification WITHOUT force_llm ---")
    result1 = await classifier.classify(test_text)
    print(f"Source: {result1.classification_source}")
    print(f"Category: {result1.primary_category.value}")
    print(f"Confidence: {result1.primary_confidence:.2f}")
    
    # Run classification WITH force_llm 
    print("\n--- Classification WITH force_llm=True ---")
    result2 = await classifier.classify(test_text, force_llm=True)
    print(f"Source: {result2.classification_source}")
    print(f"Category: {result2.primary_category.value}")
    print(f"Confidence: {result2.primary_confidence:.2f}")
    
    # Check stats
    print("\n--- Stats ---")
    stats = classifier.get_stats()
    print(f"Total: {stats['total_classifications']}")
    print(f"LLM calls: {stats['llm_classifications']}")
    print(f"Fallback: {stats['fallback_classifications']}")
    
    llm_stats = stats.get('llm_client_stats', {})
    print(f"Actual LLM API calls: {llm_stats.get('llm_calls', 0)}")
    print(f"Cache hits: {llm_stats.get('cache_hits', 0)}")

asyncio.run(test())
