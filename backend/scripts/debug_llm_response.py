"""Debug script to see what the LLM is actually returning."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Set up API key
os.environ.setdefault("GROQ_API_KEY", "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")


def test_llm_with_classifier_prompt():
    """Test raw LLM output with actual classifier prompt."""
    from app.layer2.services.llm_base import GroqLLMClient, LLMConfig, LLMProvider
    from app.layer2.services.llm_classifier import LLMClassifier
    
    # Create classifier
    classifier = LLMClassifier()
    
    # Use real article text
    test_text = """
    Sri Lanka's economy is showing signs of recovery with GDP growth reaching 2.5% 
    in Q3 2024. The Central Bank maintained interest rates while inflation dropped 
    to 4.5%. Technology sector investments increased by 30%. The government announced
    new fiscal policies to encourage foreign investment.
    """
    
    # Get the full prompt
    prompt = classifier.CLASSIFICATION_PROMPT.format(article_text=test_text)
    system_prompt = classifier.SYSTEM_PROMPT
    
    print("=" * 70)
    print("Testing With Actual Classifier Prompt")
    print("=" * 70)
    
    print(f"\n--- Prompt Preview (first 500 chars) ---")
    print(prompt[:500])
    
    # Get raw response from LLM client
    response = classifier.llm_client._call_llm(prompt, system_prompt, use_cache=False)
    
    print(f"\n--- Response Details ---")
    print(f"Success: {response.success}")
    print(f"Model: {response.model}")
    print(f"Processing time: {response.processing_time_ms:.2f}ms")
    
    print(f"\n--- Raw Content ---")
    print(f"Content:\n{response.content}")
    
    print(f"\n--- Parsed ---")
    print(f"Parsed: {response.parsed}")
    
    if response.parsed:
        print(f"\n--- Try to Create Pydantic Model ---")
        from app.layer2.services.llm_classifier import LLMClassificationResult
        try:
            result = LLMClassificationResult(**response.parsed)
            print(f"SUCCESS! Result: {result}")
        except Exception as e:
            print(f"FAILED: {e}")
    else:
        print("\n--- Attempting Manual Parse ---")
        import json
        import re
        content = response.content
        
        # Check for JSON markers
        if content:
            # Try to extract from markdown
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0]
                print(f"Extracted from markdown: {json_content[:300]}")
            else:
                # Find JSON object
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    json_content = match.group()
                    print(f"Regex extracted: {json_content[:300]}")
                else:
                    json_content = content
            
            try:
                parsed = json.loads(json_content.strip())
                print(f"Manual parse SUCCESS: {parsed}")
            except json.JSONDecodeError as e:
                print(f"Manual parse FAILED: {e}")
    
    return response


if __name__ == "__main__":
    test_llm_with_classifier_prompt()
