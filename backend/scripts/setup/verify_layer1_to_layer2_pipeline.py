"""
Full Layer 1 → Layer 2 Pipeline Verification

This script verifies:
1. Raw articles exist in MongoDB
2. Cleaning/preprocessing pipeline works
3. Processed articles are stored correctly
4. Data is properly structured for Layer 2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Load environment
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


async def verify_full_pipeline():
    """Verify the complete raw → processed → Layer 2 pipeline."""
    
    print_header("LAYER 1 → LAYER 2 PIPELINE VERIFICATION")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "mongodb_connection": False,
        "raw_articles_exist": False,
        "cleaner_works": False,
        "processed_articles_stored": False,
        "layer2_data_format": False
    }
    
    # =============================================
    # Step 1: Connect to MongoDB
    # =============================================
    print_section("1. MongoDB Connection")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # MongoDB connection with authentication
        mongo_url = "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin"
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        db = client.national_indicator
        
        print_success("Connected to MongoDB")
        results["mongodb_connection"] = True
        
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        return results
    
    # =============================================
    # Step 2: Check Raw Articles
    # =============================================
    print_section("2. Raw Articles in MongoDB")
    
    try:
        raw_count = await db.raw_articles.count_documents({})
        print(f"   📊 raw_articles collection: {raw_count} documents")
        
        if raw_count > 0:
            # Get sample raw articles
            sample_raw = await db.raw_articles.find().limit(3).to_list(length=3)
            print(f"   Sample raw articles:")
            for doc in sample_raw:
                title = doc.get("title", doc.get("raw_content", {}).get("title", "No title"))
                if isinstance(title, str):
                    title = title[:50]
                source = doc.get("source", doc.get("source_name", "Unknown"))
                if isinstance(source, dict):
                    source = source.get("name", "Unknown")
                print(f"      • {source}: {title}...")
            
            results["raw_articles_exist"] = True
            print_success(f"Found {raw_count} raw articles")
        else:
            print_warning("No raw articles found - need to run scraping first")
            
    except Exception as e:
        print_error(f"Error checking raw articles: {e}")
    
    # =============================================
    # Step 3: Test Data Cleaner
    # =============================================
    print_section("3. Data Cleaning Pipeline")
    
    try:
        from app.cleaning.cleaner import DataCleaner
        from app.models.raw_article import RawArticle
        from app.models.processed_article import ProcessedArticle
        
        cleaner = DataCleaner()
        
        # Create a test raw article
        test_raw = {
            "article_id": "test_cleaning_001",
            "source": {
                "source_id": 1,
                "name": "Test Source",
                "url": "https://test.com/article1"
            },
            "scrape_metadata": {
                "scraped_at": datetime.utcnow()
            },
            "raw_content": {
                "title": "  Test Article   Title  with   Extra   Spaces  ",
                "body": "<p>This is a <b>test</b> article with <script>alert('xss')</script> HTML content.</p>",
                "author": "Test Author",
                "publish_date": datetime.utcnow()
            },
            "validation": {
                "is_valid": True,
                "word_count": 10
            }
        }
        
        raw_article = RawArticle(**test_raw)
        processed = cleaner.process_article(raw_article)
        
        print(f"   Input title:  '{test_raw['raw_content']['title']}'")
        print(f"   Output title: '{processed.content.title_original}'")
        print(f"   Stages completed: {processed.processing_pipeline.stages_completed}")
        
        # Verify cleaning worked
        assert processed.content.title_original == "Test Article Title with Extra Spaces"
        assert "<script>" not in processed.content.body_original
        assert processed.processing_pipeline.stages_completed == ["cleaning"]
        
        results["cleaner_works"] = True
        print_success("DataCleaner working correctly")
        
    except Exception as e:
        print_error(f"DataCleaner failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 4: Check/Create Processed Articles
    # =============================================
    print_section("4. Processed Articles Collection")
    
    try:
        processed_count = await db.processed_articles.count_documents({})
        print(f"   📊 processed_articles collection: {processed_count} documents")
        
        if processed_count == 0 and raw_count > 0:
            print("   Running cleaning pipeline on raw articles...")
            
            # Process some raw articles
            raw_docs = await db.raw_articles.find().limit(10).to_list(length=10)
            processed_docs = 0
            
            for doc in raw_docs:
                try:
                    # Handle different raw article formats
                    if "raw_content" in doc:
                        raw_article = RawArticle(**doc)
                    else:
                        # Convert flat format to nested format
                        converted = {
                            "article_id": doc.get("article_id", str(doc.get("_id"))),
                            "source": {
                                "source_id": doc.get("source_id", 0),
                                "name": doc.get("source_name", doc.get("source", "Unknown")),
                                "url": doc.get("url", "")
                            },
                            "scrape_metadata": {
                                "scraped_at": doc.get("scraped_at", datetime.utcnow())
                            },
                            "raw_content": {
                                "title": doc.get("title", ""),
                                "body": doc.get("content", doc.get("body", "")),
                                "author": doc.get("author"),
                                "publish_date": doc.get("publish_date", doc.get("published_at"))
                            },
                            "validation": {
                                "is_valid": True,
                                "word_count": len(doc.get("content", doc.get("body", "")).split())
                            }
                        }
                        raw_article = RawArticle(**converted)
                    
                    processed = cleaner.process_article(raw_article)
                    
                    # Store in MongoDB
                    processed_dict = processed.model_dump(mode='json')
                    await db.processed_articles.update_one(
                        {"article_id": processed.article_id},
                        {"$set": processed_dict},
                        upsert=True
                    )
                    processed_docs += 1
                    
                except Exception as e:
                    print_warning(f"Failed to process article: {e}")
            
            print_success(f"Processed and stored {processed_docs} articles")
            processed_count = processed_docs
        
        if processed_count > 0:
            results["processed_articles_stored"] = True
            
            # Show sample processed articles
            sample_processed = await db.processed_articles.find().limit(3).to_list(length=3)
            print(f"\n   Sample processed articles:")
            for doc in sample_processed:
                title = doc.get("content", {}).get("title_original", "No title")[:50]
                stages = doc.get("processing_pipeline", {}).get("stages_completed", [])
                print(f"      • {title}... (stages: {stages})")
                
    except Exception as e:
        print_error(f"Error with processed articles: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 5: Verify Layer 2 Data Format
    # =============================================
    print_section("5. Layer 2 Data Format Verification")
    
    try:
        # Check if processed articles have required fields for Layer 2
        sample = await db.processed_articles.find_one({})
        
        if sample:
            required_fields = [
                ("article_id", sample.get("article_id")),
                ("content.title_original", sample.get("content", {}).get("title_original")),
                ("content.body_original", sample.get("content", {}).get("body_original")),
                ("extraction", sample.get("extraction")),
                ("quality", sample.get("quality")),
            ]
            
            missing_fields = []
            for field_name, value in required_fields:
                if value is None or value == "":
                    missing_fields.append(field_name)
                else:
                    print_success(f"{field_name}: ✓")
            
            if missing_fields:
                print_warning(f"Missing fields: {missing_fields}")
            else:
                results["layer2_data_format"] = True
                print_success("All required fields present for Layer 2")
            
            # Test Layer 2 can consume this data
            print("\n   Testing Layer 2 ingestion format...")
            try:
                from app.layer2.data_ingestion.schemas import Article
                
                # Convert processed article to Layer 2 format
                layer2_article = Article(
                    article_id=sample.get("article_id"),
                    title=sample.get("content", {}).get("title_original", ""),
                    body=sample.get("content", {}).get("body_original", ""),
                    source=sample.get("source_name", "unknown"),
                    url=sample.get("source_url", ""),
                    published_at=sample.get("extraction", {}).get("publish_timestamp")
                )
                print_success(f"Layer 2 Article schema validated: {layer2_article.article_id}")
                results["layer2_data_format"] = True
                
            except ImportError:
                print_warning("Layer 2 schemas not available - checking basic format only")
            except Exception as e:
                print_warning(f"Layer 2 format validation: {e}")
        else:
            print_warning("No processed articles to verify format")
            
    except Exception as e:
        print_error(f"Layer 2 format verification failed: {e}")
    
    # Close MongoDB connection
    client.close()
    
    # =============================================
    # Summary
    # =============================================
    print_header("PIPELINE VERIFICATION SUMMARY")
    
    print("\n📊 RESULTS:")
    print(f"   {'Component':<35} {'Status'}")
    print("-" * 55)
    
    status_icons = {True: "✅ PASS", False: "❌ FAIL"}
    for component, status in results.items():
        component_name = component.replace("_", " ").title()
        print(f"   {component_name:<35} {status_icons[status]}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n   Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Full pipeline is working correctly!")
        print("   Raw articles → Cleaning → Processed articles → Layer 2 ready")
    elif passed >= 3:
        print("\n⚠️ Pipeline mostly working, some issues to address")
    else:
        print("\n❌ Pipeline has significant issues")
    
    return results


async def main():
    try:
        results = await verify_full_pipeline()
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
