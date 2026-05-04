"""
Diagnose why only a few articles reached Layer 2
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def diagnose_article_flow():
    print("=" * 60)
    print(" ARTICLE FLOW DIAGNOSIS")
    print("=" * 60)
    
    mongo_url = 'mongodb://admin:mongo_secure_2024@127.0.0.1:27017/national_indicator?authSource=admin'
    client = AsyncIOMotorClient(mongo_url)
    db = client.national_indicator
    
    # 1. Count raw articles
    raw_count = await db.raw_articles.count_documents({})
    print(f"\n1. RAW ARTICLES: {raw_count}")
    
    # Sample raw articles
    raw_sample = await db.raw_articles.find().limit(3).to_list(3)
    print("   Sample structure:")
    for doc in raw_sample[:2]:
        print(f"   - ID: {doc.get('article_id', doc.get('_id'))}")
        print(f"     Title: {str(doc.get('title', 'N/A'))[:50]}")
        print(f"     Has content: {'content' in doc or 'body' in doc or 'raw_content' in doc}")
    
    # 2. Count processed articles
    processed_count = await db.processed_articles.count_documents({})
    print(f"\n2. PROCESSED ARTICLES: {processed_count}")
    
    if processed_count > 0:
        # Check stages
        cursor = db.processed_articles.find({}, {
            'article_id': 1, 
            'processing_pipeline.stages_completed': 1,
            'layer2_processed': 1
        })
        docs = await cursor.to_list(100)
        
        print("   Articles and their stages:")
        for doc in docs[:10]:
            article_id = doc.get('article_id', 'unknown')
            stages = doc.get('processing_pipeline', {}).get('stages_completed', [])
            l2 = doc.get('layer2_processed', False)
            print(f"   - {article_id}: stages={stages}, layer2={l2}")
    
    # 3. Why gap between raw (143) and processed (10)?
    print(f"\n3. GAP ANALYSIS:")
    print(f"   Raw articles: {raw_count}")
    print(f"   Processed articles: {processed_count}")
    print(f"   Gap: {raw_count - processed_count} articles not processed")
    
    # 4. Check if cleaning pipeline was run
    print(f"\n4. CLEANING PIPELINE STATUS:")
    
    # Check articles with 'cleaning' stage
    cleaning_done = await db.processed_articles.count_documents({
        'processing_pipeline.stages_completed': 'cleaning'
    })
    print(f"   Articles with 'cleaning' stage: {cleaning_done}")
    
    # 5. Layer 2 status
    l2_processed = await db.processed_articles.count_documents({'layer2_processed': True})
    l2_pending = await db.processed_articles.count_documents({
        '$or': [
            {'layer2_processed': {'$exists': False}},
            {'layer2_processed': False}
        ]
    })
    
    print(f"\n5. LAYER 2 STATUS:")
    print(f"   Already processed by L2: {l2_processed}")
    print(f"   Pending for L2: {l2_pending}")
    
    # 6. The test script only processed 3 - that's by design (limit in test)
    print(f"\n6. WHY ONLY 3 ARTICLES IN TEST?")
    print("   The test script has 'limit=5' and processes 'test_articles[:3]'")
    print("   This is a TEST LIMIT, not a pipeline issue!")
    
    # 7. Recommendation
    print(f"\n7. RECOMMENDATIONS:")
    if processed_count < raw_count:
        print(f"   ⚠️ Run cleaning pipeline to process all {raw_count} raw articles")
        print(f"      Command: python scripts/run_cleaning.py")
    
    print(f"\n   To process ALL articles through Layer 2:")
    print(f"   - Remove test limits in the processing scripts")
    print(f"   - Or run batch processing endpoint")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(diagnose_article_flow())
