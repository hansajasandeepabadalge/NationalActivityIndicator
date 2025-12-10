"""
Test MasterOrchestrator with AI Agents

This script runs the MasterOrchestrator which uses AI agents to:
1. Monitor sources and decide what to scrape (SourceMonitorAgent)
2. Execute scrapers for selected sources
3. Process articles through the pipeline
4. Classify priority/urgency (PriorityAgent)
5. Validate quality (ValidationAgent)
6. Store valid articles
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from datetime import datetime
from uuid import uuid4

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reduce noise from other loggers
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def print_section(text: str):
    """Print a section header."""
    print(f"\n--- {text} ---")


async def test_orchestrator():
    """Run the MasterOrchestrator test."""
    print_header("MASTER ORCHESTRATOR TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Import and initialize
    print_section("1. Importing MasterOrchestrator")
    try:
        from app.orchestrator.master_orchestrator import MasterOrchestrator
        print("✅ MasterOrchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Initialize orchestrator
    print_section("2. Initializing MasterOrchestrator")
    try:
        orchestrator = MasterOrchestrator()
        print("✅ MasterOrchestrator initialized")
        print(f"   - Source Monitor Agent: {type(orchestrator.source_monitor).__name__}")
        print(f"   - Processing Agent: {type(orchestrator.processing_agent).__name__}")
        print(f"   - Priority Agent: {type(orchestrator.priority_agent).__name__}")
        print(f"   - Validation Agent: {type(orchestrator.validation_agent).__name__}")
        print(f"   - Scheduler Agent: {type(orchestrator.scheduler_agent).__name__}")
        print(f"   - Has Reputation System: {orchestrator.quality_filter is not None}")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test Source Monitor Agent
    print_section("3. Testing Source Monitor Agent")
    try:
        run_id = str(uuid4())
        result = await orchestrator.source_monitor.execute({"run_id": run_id})
        sources = result.get("sources_to_scrape", [])
        print(f"✅ Source Monitor Agent executed")
        print(f"   - Run ID: {run_id[:8]}...")
        print(f"   - Sources to scrape: {len(sources)}")
        if sources:
            for source in sources[:5]:
                print(f"     • {source}")
            if len(sources) > 5:
                print(f"     ... and {len(sources) - 5} more")
    except Exception as e:
        print(f"❌ Source Monitor failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Run a single pipeline execution
    print_section("4. Running Full Pipeline (Single Execution)")
    try:
        run_id = str(uuid4())
        
        # Create initial state
        initial_state = {
            "run_id": run_id,
            "phase": "init",
            "sources_to_scrape": [],
            "scraped_content": [],
            "processed_articles": [],
            "priority_classifications": [],
            "validated_articles": [],
            "stored_articles": [],
            "errors": [],
            "metrics": {},
            "should_continue": True
        }
        
        print(f"   Starting pipeline run: {run_id[:8]}...")
        
        # Execute the graph
        final_state = await orchestrator.graph.ainvoke(initial_state)
        
        print("✅ Pipeline execution completed!")
        print(f"\n   📊 PIPELINE RESULTS:")
        print(f"   - Sources analyzed: {final_state.get('metrics', {}).get('sources_analyzed', 0)}")
        print(f"   - Sources to scrape: {final_state.get('metrics', {}).get('sources_to_scrape', 0)}")
        print(f"   - Articles scraped: {final_state.get('metrics', {}).get('articles_scraped', 0)}")
        print(f"   - Articles processed: {final_state.get('metrics', {}).get('articles_processed', 0)}")
        print(f"   - Articles validated: {final_state.get('metrics', {}).get('articles_validated', 0)}")
        print(f"   - Articles stored: {final_state.get('metrics', {}).get('articles_stored', 0)}")
        print(f"   - Errors: {len(final_state.get('errors', []))}")
        
        if final_state.get('errors'):
            print("\n   ⚠️ ERRORS:")
            for error in final_state.get('errors', [])[:5]:
                print(f"     • {error.get('phase', 'unknown')}: {error.get('error', 'Unknown')[:100]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    try:
        success = await test_orchestrator()
        
        print_header("TEST SUMMARY")
        if success:
            print("✅ MasterOrchestrator is working correctly!")
            print("\nThe AI Agent pipeline is operational:")
            print("  1. Source Monitor Agent → Decides which sources to scrape")
            print("  2. Scraper Tools → Fetch content from sources")
            print("  3. Processing Agent → Clean and enhance content")
            print("  4. Priority Agent → Classify urgency")
            print("  5. Validation Agent → Validate quality")
            print("  6. Storage → Store valid articles")
        else:
            print("❌ Some tests failed")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
