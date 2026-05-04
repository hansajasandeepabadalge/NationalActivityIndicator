"""
Test Layer 1 → Layer 2 Pipeline with MongoDB Loader

This script tests the complete flow:
1. Fetch processed articles from MongoDB (Layer 1 output)
2. Transform to Layer 2 format
3. Process through Layer 2 enhanced pipeline
4. Store results back in MongoDB
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
load_dotenv()


def print_header(text: str):
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_section(text: str):
    print(f"\n--- {text} ---")


def print_success(text: str):
    print(f"   ✅ {text}")


def print_warning(text: str):
    print(f"   ⚠️ {text}")


def print_error(text: str):
    print(f"   ❌ {text}")


async def test_mongodb_loader():
    """Test the MongoDB article loader for Layer 2."""
    
    print_header("TESTING MONGODB LOADER FOR LAYER 2")
    
    results = {
        "loader_init": False,
        "connection": False,
        "fetch_articles": False,
        "transform_format": False,
        "layer2_processing": False
    }
    
    # =============================================
    # Step 1: Initialize Loader
    # =============================================
    print_section("1. Initialize MongoDB Loader")
    
    try:
        from app.layer2.data_ingestion.mongodb_loader import (
            MongoDBArticleLoader,
            Layer2Article,
            fetch_articles_for_layer2
        )
        
        loader = MongoDBArticleLoader()
        print_success("MongoDBArticleLoader imported and instantiated")
        results["loader_init"] = True
        
    except Exception as e:
        print_error(f"Failed to initialize loader: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    # =============================================
    # Step 2: Connect to MongoDB
    # =============================================
    print_section("2. Connect to MongoDB")
    
    try:
        connected = await loader.connect()
        if connected:
            print_success("Connected to MongoDB")
            results["connection"] = True
        else:
            print_error("Failed to connect to MongoDB")
            return results
            
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return results
    
    # =============================================
    # Step 3: Fetch Articles
    # =============================================
    print_section("3. Fetch Processed Articles from MongoDB")
    
    try:
        # Count total processed articles
        total_count = await loader.count_all_processed()
        print(f"   📊 Total processed articles: {total_count}")
        
        # Count unprocessed by Layer 2
        unprocessed_count = await loader.count_unprocessed()
        print(f"   📊 Unprocessed by Layer 2: {unprocessed_count}")
        
        # Fetch articles
        articles = await loader.get_all_articles(limit=5)
        print(f"   📊 Fetched {len(articles)} articles for testing")
        
        if articles:
            results["fetch_articles"] = True
            print_success(f"Successfully fetched {len(articles)} articles")
        else:
            print_warning("No articles found to process")
            
    except Exception as e:
        print_error(f"Failed to fetch articles: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    # =============================================
    # Step 4: Verify Transform Format
    # =============================================
    print_section("4. Verify Layer 2 Article Format")
    
    if articles:
        try:
            print("\n   Sample articles in Layer 2 format:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n   [{i}] Article: {article.article_id}")
                print(f"       Title: {article.title[:60]}..." if len(article.title) > 60 else f"       Title: {article.title}")
                print(f"       Source: {article.source}")
                print(f"       Language: {article.language}")
                print(f"       Text length: {len(article.text)} chars")
                print(f"       L1 Quality Score: {article.layer1_quality_score}")
                print(f"       L1 Stages: {article.layer1_stages_completed}")
            
            # Verify all required fields are present
            sample = articles[0]
            required_fields = ['article_id', 'text', 'title']
            all_present = all(getattr(sample, f, None) for f in required_fields)
            
            if all_present:
                results["transform_format"] = True
                print_success("Article format is correct for Layer 2")
            else:
                print_warning("Some required fields are missing")
                
        except Exception as e:
            print_error(f"Format verification failed: {e}")
    
    # =============================================
    # Step 5: Test Layer 2 Processing
    # =============================================
    print_section("5. Test Layer 2 Enhanced Processing")
    
    if articles:
        try:
            # Import enhanced pipeline
            from app.layer2.services import get_enhanced_pipeline
            
            pipeline = get_enhanced_pipeline()
            
            # Initialize pipeline
            print("   Initializing enhanced pipeline...")
            await pipeline.initialize()
            
            # Process first article
            test_article = articles[0]
            print(f"   Processing article: {test_article.article_id}")
            
            result = await pipeline.process(
                text=test_article.text,
                title=test_article.title,
                article_id=test_article.article_id
            )
            
            print("\n   Layer 2 Processing Result:")
            if result.classification:
                print(f"      Classification: {result.classification.primary_category}")
                print(f"      Confidence: {result.classification.primary_confidence:.2f}")
            if result.sentiment:
                print(f"      Sentiment: {result.sentiment.overall.label}")
                print(f"      Score: {result.sentiment.overall.score:.2f}")
            if result.quality:
                print(f"      Quality Score: {result.quality.overall_score:.1f}")
            
            print(f"      Processing Time: {result.processing_time_ms:.0f}ms")
            
            # Mark as processed
            marked = await loader.mark_as_layer2_processed(
                article_id=test_article.article_id,
                layer2_result={
                    "classification": result.classification.primary_category if result.classification else None,
                    "sentiment": result.sentiment.overall.label if result.sentiment else None,
                    "quality_score": result.quality.overall_score if result.quality else None,
                    "processed_at": datetime.utcnow().isoformat()
                }
            )
            
            if marked:
                print_success("Article marked as Layer 2 processed")
            
            results["layer2_processing"] = True
            print_success("Layer 2 processing completed successfully")
            
        except Exception as e:
            print_error(f"Layer 2 processing failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Close connection
    await loader.disconnect()
    
    # =============================================
    # Summary
    # =============================================
    print_header("LAYER 1 → LAYER 2 PIPELINE TEST SUMMARY")
    
    print("\n📊 RESULTS:")
    print(f"   {'Component':<30} {'Status'}")
    print("-" * 50)
    
    status_icons = {True: "✅ PASS", False: "❌ FAIL"}
    for component, status in results.items():
        component_name = component.replace("_", " ").title()
        print(f"   {component_name:<30} {status_icons[status]}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n   Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Layer 1 → Layer 2 pipeline is fully functional!")
        print("   Articles can flow from MongoDB processed_articles to Layer 2 enhanced processing")
    elif passed >= 3:
        print("\n⚠️ Pipeline mostly working, some components need attention")
    else:
        print("\n❌ Pipeline has significant issues")
    
    return results


async def main():
    try:
        results = await test_mongodb_loader()
        success = all(results.values())
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
