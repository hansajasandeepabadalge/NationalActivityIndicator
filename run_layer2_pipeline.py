"""
Layer 2 Pipeline Runner Script

Runs the Layer 2 pipeline to:
1. Fetch unprocessed articles from MongoDB
2. Run through classification, sentiment, entity extraction
3. Calculate all 105 indicators
4. Store results to PostgreSQL and MongoDB
"""

import asyncio
import sys
import os
from datetime import datetime

# SET API KEYS BEFORE ANY IMPORTS (critical for Groq LLM to work)
os.environ["GROQ_API_KEYS"] = "YOUR_GROQ_API_KEYS_HERE"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def run_layer2_pipeline():
    """Run the Layer 2 pipeline with proper configuration."""
    print("\n" + "="*60)
    print("LAYER 2 PIPELINE EXECUTION")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import the pipeline orchestrator
        from app.layer2.pipeline_orchestrator import Layer2PipelineOrchestrator
        
        # Initialize with correct database config
        orchestrator = Layer2PipelineOrchestrator(
            mongo_url="mongodb://admin:mongo_secure_2024@localhost:27017/",
            mongo_db="national_indicator",
            pg_config={
                'host': '127.0.0.1',
                'port': 15432,
                'database': 'national_indicator',
                'user': 'postgres',
                'password': 'postgres_secure_2024'
            }
        )
        
        print("\n✅ Pipeline orchestrator initialized")
        print("\n[1/2] Running pipeline with up to 50 articles...")
        
        # Run the pipeline
        result = await orchestrator.run_full_pipeline(
            article_limit=50,
            time_window_hours=168,  # Last 7 days
            store_results=True
        )
        
        print("\n" + "-"*60)
        print("PIPELINE RESULTS")
        print("-"*60)
        
        if result:
            print(f"✅ Pipeline completed successfully!")
            print(f"\n📊 Summary:")
            print(f"  - Articles processed: {result.articles_processed}")
            print(f"  - Indicators calculated: {result.indicators_calculated}")
            print(f"  - Processing time: {result.total_duration_ms/1000:.2f}s")
            print(f"  - Success: {result.success}")
            
            if hasattr(result, 'stages') and result.stages:
                print(f"\n📋 Stage Results:")
                for stage in result.stages:
                    status = "✅" if stage.success else "❌"
                    print(f"  {status} {stage.stage_name}: {stage.item_count} items in {stage.duration_ms/1000:.2f}s")
            
            if hasattr(result, 'errors') and result.errors:
                print(f"\n⚠️ Errors: {len(result.errors)}")
                for err in result.errors[:5]:
                    print(f"  - {err}")
        else:
            print("❌ Pipeline returned no result")
            
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nTrying alternative import...")
        
        try:
            # Try direct import
            from backend.app.layer2.pipeline_orchestrator import Layer2PipelineOrchestrator
            print("✅ Alternative import successful")
        except ImportError as e2:
            print(f"❌ Alternative import also failed: {e2}")
            return False
            
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True


def main():
    """Main entry point."""
    success = asyncio.run(run_layer2_pipeline())
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
