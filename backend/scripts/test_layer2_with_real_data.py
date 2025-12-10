"""
Test Layer 2 Processing with Real Scraped Data from Layer 1

This script tests all Layer 2 components using actual articles
that were scraped and processed through Layer 1.

Layer 2 Components:
1. LLM Classification (PESTEL categories)
2. Advanced Sentiment Analysis
3. Smart Entity Extraction
4. Topic Modeling
5. Quality Scoring
6. Enhanced Pipeline (orchestrates all above)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List

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


async def fetch_real_articles(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetch real processed articles from MongoDB."""
    from motor.motor_asyncio import AsyncIOMotorClient
    
    mongo_url = "mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin"
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    
    try:
        await client.admin.command('ping')
        db = client.national_indicator
        
        # Get articles with actual content
        cursor = db.processed_articles.find({
            "content.body_original": {"$ne": "", "$exists": True}
        }).limit(limit)
        
        articles = await cursor.to_list(length=limit)
        
        # If not enough from processed, try raw
        if len(articles) < limit:
            raw_cursor = db.raw_articles.find({
                "$or": [
                    {"content": {"$ne": "", "$exists": True}},
                    {"body": {"$ne": "", "$exists": True}}
                ]
            }).limit(limit - len(articles))
            raw_articles = await raw_cursor.to_list(length=limit - len(articles))
            
            # Transform raw to simple format
            for raw in raw_articles:
                articles.append({
                    "article_id": raw.get("article_id", str(raw.get("_id"))),
                    "content": {
                        "title_original": raw.get("title", ""),
                        "body_original": raw.get("content", raw.get("body", ""))
                    },
                    "source_name": raw.get("source_name", raw.get("source", "Unknown"))
                })
        
        return articles
        
    finally:
        client.close()


async def test_layer2_components():
    """Test all Layer 2 components with real data."""
    
    print_header("LAYER 2 TESTING WITH REAL SCRAPED DATA")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "data_fetch": False,
        "llm_classification": False,
        "sentiment_analysis": False,
        "entity_extraction": False,
        "quality_scoring": False,
        "topic_modeling": False,
        "enhanced_pipeline": False
    }
    
    # =============================================
    # Step 1: Fetch Real Articles
    # =============================================
    print_section("1. Fetching Real Articles from Layer 1")
    
    try:
        articles = await fetch_real_articles(limit=5)
        print(f"   📊 Fetched {len(articles)} articles")
        
        if not articles:
            print_error("No articles found! Run Layer 1 scraping first.")
            return results
        
        # Prepare test data
        test_articles = []
        for doc in articles:
            content = doc.get("content", {})
            title = content.get("title_original", "") or doc.get("title", "")
            body = content.get("body_original", "") or doc.get("content", "") or doc.get("body", "")
            
            if body and len(body) > 50:  # Ensure meaningful content
                test_articles.append({
                    "article_id": doc.get("article_id", "unknown"),
                    "title": title,
                    "text": f"{title}\n\n{body}".strip(),
                    "source": doc.get("source_name", "Unknown")
                })
        
        print(f"   📊 Prepared {len(test_articles)} articles with meaningful content")
        
        for i, art in enumerate(test_articles[:3], 1):
            print(f"\n   [{i}] {art['source']}: {art['title'][:50]}...")
            print(f"       Content length: {len(art['text'])} chars")
        
        if test_articles:
            results["data_fetch"] = True
            print_success(f"Real articles ready for Layer 2 testing")
        else:
            print_error("No articles with meaningful content found")
            return results
            
    except Exception as e:
        print_error(f"Failed to fetch articles: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    # Use the first article with good content for testing
    test_article = max(test_articles, key=lambda x: len(x['text']))
    print(f"\n   Using test article: {test_article['article_id']}")
    print(f"   Content preview: {test_article['text'][:200]}...")
    
    # =============================================
    # Step 2: Test LLM Classification
    # =============================================
    print_section("2. LLM Classification (PESTEL Categories)")
    
    try:
        from app.layer2.services import get_llm_classifier, LLM_CLASSIFICATION_ENABLED
        
        print(f"   Feature enabled: {LLM_CLASSIFICATION_ENABLED}")
        
        classifier = get_llm_classifier()
        
        result = await classifier.classify(
            text=test_article['text'],
            title=test_article['title']
        )
        
        print(f"\n   Classification Results:")
        print(f"      Primary Category: {result.primary_category}")
        print(f"      Confidence: {result.primary_confidence:.2%}")
        print(f"      Urgency: {result.urgency}")
        print(f"      Business Relevance: {result.business_relevance}")
        print(f"      Source: {result.classification_source}")
        
        if result.all_categories:
            print(f"      All Categories: {dict(list(result.all_categories.items())[:3])}")
        
        results["llm_classification"] = True
        print_success("LLM Classification working with real data")
        
    except Exception as e:
        print_error(f"LLM Classification failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 3: Test Sentiment Analysis
    # =============================================
    print_section("3. Advanced Sentiment Analysis")
    
    try:
        from app.layer2.services import get_advanced_sentiment, ADVANCED_SENTIMENT_ENABLED
        
        print(f"   Feature enabled: {ADVANCED_SENTIMENT_ENABLED}")
        
        analyzer = get_advanced_sentiment()
        
        result = await analyzer.analyze(
            text=test_article['text'],
            title=test_article['title']
        )
        
        print(f"\n   Sentiment Results:")
        # Handle both attribute formats
        if hasattr(result, 'overall'):
            print(f"      Overall: {result.overall.label} ({result.overall.score:.2f})")
        else:
            print(f"      Overall: {result.overall_level.value} ({result.overall_score:.2f})")
        print(f"      Tone: {result.tone.value if hasattr(result.tone, 'value') else result.tone}")
        print(f"      Source: {result.analysis_source}")
        
        if hasattr(result, 'primary_emotion'):
            print(f"      Primary Emotion: {result.primary_emotion.value if hasattr(result.primary_emotion, 'value') else result.primary_emotion}")
        
        results["sentiment_analysis"] = True
        print_success("Sentiment Analysis working with real data")
        
    except Exception as e:
        print_error(f"Sentiment Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 4: Test Entity Extraction
    # =============================================
    print_section("4. Smart Entity Extraction")
    
    try:
        from app.layer2.services import get_smart_entity_extractor, SMART_NER_ENABLED
        
        print(f"   Feature enabled: {SMART_NER_ENABLED}")
        
        extractor = get_smart_entity_extractor()
        
        result = await extractor.extract(
            text=test_article['text'],
            title=test_article['title']
        )
        
        print(f"\n   Entity Extraction Results:")
        print(f"      Total Entities: {result.entity_count}")
        print(f"      Source: {result.extraction_source}")
        
        if result.primary_entities:
            print(f"      Primary Entities:")
            for ent in result.primary_entities[:5]:
                ent_type = ent.entity_type.value if hasattr(ent.entity_type, 'value') else str(ent.entity_type)
                print(f"         • {ent.text} ({ent_type}) - Importance: {ent.importance:.2f}")
        
        if result.entities_by_type:
            print(f"      By Type: {dict((k, len(v)) for k, v in result.entities_by_type.items())}")
        
        if result.relationships:
            print(f"      Relationships found: {len(result.relationships)}")
        
        results["entity_extraction"] = True
        print_success("Entity Extraction working with real data")
        
    except Exception as e:
        print_error(f"Entity Extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 5: Test Quality Scoring
    # =============================================
    print_section("5. Quality Scoring")
    
    try:
        from app.layer2.services import get_quality_scorer, QUALITY_SCORING_ENABLED
        
        print(f"   Feature enabled: {QUALITY_SCORING_ENABLED}")
        
        scorer = get_quality_scorer()
        
        # QualityScorer.score() expects results from other services, not raw text
        # Pass article_metadata instead
        result = scorer.score(
            article_metadata={
                "title": test_article['title'],
                "text": test_article['text'],
                "source": test_article.get('source', 'unknown'),
                "word_count": len(test_article['text'].split())
            }
        )
        
        print(f"\n   Quality Score Results:")
        print(f"      Overall Score: {result.overall_score:.1f}/100")
        print(f"      Band: {result.quality_band.value}")
        
        if result.dimension_scores:
            print(f"      Dimension Scores:")
            for dim, dim_score in result.dimension_scores.items():
                print(f"         • {dim.value}: {dim_score.score:.1f}")
        
        if result.weaknesses:
            print(f"      Weaknesses: {result.weaknesses[:3]}")
        
        if result.recommendations:
            print(f"      Recommendations: {result.recommendations[:2]}")
        
        results["quality_scoring"] = True
        print_success("Quality Scoring working with real data")
        
    except Exception as e:
        print_error(f"Quality Scoring failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 6: Test Topic Modeling
    # =============================================
    print_section("6. Topic Modeling")
    
    try:
        from app.layer2.services import get_topic_modeler, TOPIC_MODELING_ENABLED
        
        print(f"   Feature enabled: {TOPIC_MODELING_ENABLED}")
        
        modeler = get_topic_modeler()
        
        # Initialize the modeler
        init_result = await modeler.initialize()
        print(f"   Modeler initialized: {init_result}")
        
        # Add article and get topic match
        result = await modeler.add_article(
            article_id=test_article['article_id'],
            text=test_article['text'],
            title=test_article['title']
        )
        
        print(f"\n   Topic Modeling Results:")
        if result:
            # Handle different attribute names
            topic_id = getattr(result, 'topic_id', getattr(result, 'matched_topic_id', 'N/A'))
            topic_name = getattr(result, 'topic_name', getattr(result, 'matched_topic_name', 'N/A'))
            similarity = getattr(result, 'similarity_score', getattr(result, 'confidence', 0))
            is_emerging = getattr(result, 'is_emerging', getattr(result, 'emerging', False))
            
            print(f"      Topic ID: {topic_id}")
            print(f"      Topic Name: {topic_name}")
            print(f"      Similarity: {similarity:.2%}" if isinstance(similarity, float) else f"      Similarity: {similarity}")
            print(f"      Is Emerging: {is_emerging}")
        else:
            print(f"      No strong topic match found (new topic)")
        
        results["topic_modeling"] = True
        print_success("Topic Modeling working with real data")
        
    except Exception as e:
        print_error(f"Topic Modeling failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Step 7: Test Enhanced Pipeline (Full)
    # =============================================
    print_section("7. Enhanced Pipeline (Full Processing)")
    
    try:
        from app.layer2.services import get_enhanced_pipeline
        
        pipeline = get_enhanced_pipeline()
        
        # Initialize
        print("   Initializing enhanced pipeline...")
        await pipeline.initialize()
        
        # Process multiple articles
        print(f"   Processing {len(test_articles)} articles through full pipeline...")
        
        processed_count = 0
        for art in test_articles[:3]:
            result = await pipeline.process(
                text=art['text'],
                title=art['title'],
                article_id=art['article_id']
            )
            
            print(f"\n   Article: {art['article_id']}")
            
            if result.classification:
                print(f"      Category: {result.classification.primary_category} ({result.classification.primary_confidence:.0%})")
            
            if result.sentiment:
                if hasattr(result.sentiment, 'overall'):
                    print(f"      Sentiment: {result.sentiment.overall.label} ({result.sentiment.overall.score:.2f})")
                else:
                    print(f"      Sentiment: {result.sentiment.overall_level.value} ({result.sentiment.overall_score:.2f})")
            
            if result.entities:
                print(f"      Entities: {result.entities.entity_count} found")
            
            if result.quality:
                band = getattr(result.quality, 'quality_band', getattr(result.quality, 'grade', 'N/A'))
                band_value = band.value if hasattr(band, 'value') else str(band)
                print(f"      Quality: {result.quality.overall_score:.0f}/100 ({band_value})")
            
            print(f"      Processing Time: {result.processing_time_ms:.0f}ms")
            
            processed_count += 1
        
        print(f"\n   Successfully processed {processed_count}/{len(test_articles[:3])} articles")
        
        results["enhanced_pipeline"] = True
        print_success("Enhanced Pipeline working with real data")
        
    except Exception as e:
        print_error(f"Enhanced Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
    
    # =============================================
    # Summary
    # =============================================
    print_header("LAYER 2 TESTING SUMMARY")
    
    print("\n📊 COMPONENT RESULTS:")
    print(f"   {'Component':<30} {'Status'}")
    print("-" * 50)
    
    status_icons = {True: "✅ PASS", False: "❌ FAIL"}
    for component, status in results.items():
        component_name = component.replace("_", " ").title()
        print(f"   {component_name:<30} {status_icons[status]}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n   Overall: {passed}/{total} components passed")
    
    if passed == total:
        print("\n🎉 ALL Layer 2 components working with real scraped data!")
        print("   The full NLP pipeline is operational:")
        print("   - PESTEL Classification ✓")
        print("   - Sentiment Analysis ✓")
        print("   - Entity Extraction ✓")
        print("   - Quality Scoring ✓")
        print("   - Topic Modeling ✓")
        print("   - Full Pipeline ✓")
    elif passed >= 5:
        print("\n⚠️ Most Layer 2 components working, minor issues to address")
    else:
        print("\n❌ Layer 2 has significant issues")
    
    return results


async def main():
    try:
        results = await test_layer2_components()
        passed = sum(results.values())
        return 0 if passed >= 5 else 1
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
