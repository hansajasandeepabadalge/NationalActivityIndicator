"""
Test AI Agents for Scraping Tasks

This script tests that our AI agents work correctly for scraping decisions:
1. Source Monitor Agent - Decides WHAT/WHEN to scrape
2. Scheduler Agent - Optimizes scraping frequencies
3. Processing Agent - Processes scraped content
4. Validation Agent - Validates article quality
5. Priority Agent - Classifies urgency

Uses Groq (FREE) as primary LLM.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_config_and_llm():
    """Test configuration and LLM manager."""
    print("\n" + "="*60)
    print("1️⃣ TESTING: Configuration & LLM Manager")
    print("="*60)
    
    try:
        from app.agents.config import get_agent_config
        from app.agents.llm_manager import LLMManager
        
        config = get_agent_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Primary Provider: {config.primary_provider.value}")
        print(f"   Groq API Key: {'SET' if config.groq_api_key else 'NOT SET'}")
        print(f"   DeepSeek API Key: {'SET' if config.deepseek_api_key else 'NOT SET'}")
        print(f"   Primary Model: {config.primary_model}")
        print(f"   Fast Model: {config.fast_model}")
        
        # Test LLM Manager
        llm_manager = LLMManager(config)
        print(f"\n✅ LLM Manager initialized")
        print(f"   Primary provider: {llm_manager.config.primary_provider.value}")
        
        return config, llm_manager
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def test_source_monitor_agent():
    """Test Source Monitor Agent - decides what to scrape."""
    print("\n" + "="*60)
    print("2️⃣ TESTING: Source Monitor Agent")
    print("="*60)
    
    try:
        from app.agents.source_monitor_agent import SourceMonitorAgent
        
        agent = SourceMonitorAgent()
        print(f"✅ Source Monitor Agent created")
        print(f"   Agent Name: {agent.agent_name}")
        print(f"   Description: {agent.agent_description}")
        print(f"   Task Complexity: {agent.task_complexity.value}")
        
        # Execute the agent
        print(f"\n📤 Executing agent to decide what to scrape...")
        result = await agent.execute({})
        
        print(f"\n📋 Agent Decision:")
        print(f"   Sources to scrape: {result.get('sources_to_scrape', [])}")
        print(f"   Sources to skip: {result.get('sources_to_skip', [])}")
        print(f"   Urgency detected: {result.get('urgency_detected', False)}")
        reasoning = result.get('reasoning', 'N/A')
        print(f"   Reasoning: {reasoning[:100] if reasoning else 'N/A'}...")
        
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_scheduler_agent():
    """Test Scheduler Agent - optimizes scraping frequencies."""
    print("\n" + "="*60)
    print("3️⃣ TESTING: Scheduler Agent")
    print("="*60)
    
    try:
        from app.agents.scheduler_agent import SchedulerAgent
        
        agent = SchedulerAgent()
        print(f"✅ Scheduler Agent created")
        print(f"   Agent Name: {agent.agent_name}")
        print(f"   Description: {agent.agent_description}")
        
        # Execute the agent
        print(f"\n📤 Executing agent to optimize schedules...")
        result = await agent.execute({})
        
        print(f"\n📋 Schedule Optimization Result:")
        recommendations = result.get('recommendations', [])
        print(f"   Recommendations: {len(recommendations)}")
        for rec in recommendations[:3]:
            print(f"      - {rec.get('source_name')}: {rec.get('current_frequency')}min -> {rec.get('recommended_frequency')}min")
            reason = rec.get('reason', 'N/A')
            print(f"        Reason: {reason[:60] if reason else 'N/A'}")
        
        print(f"   Overall Efficiency: {result.get('overall_efficiency', 0):.2%}")
        print(f"   Resource Savings: {result.get('resource_savings', 'N/A')}")
        
        alerts = result.get('monitoring_alerts', [])
        if alerts:
            print(f"   Alerts: {', '.join(str(a) for a in alerts[:3])}")
        
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_priority_agent():
    """Test Priority Agent - classifies article urgency."""
    print("\n" + "="*60)
    print("4️⃣ TESTING: Priority Detection Agent")
    print("="*60)
    
    try:
        from app.agents.priority_agent import PriorityDetectionAgent
        
        agent = PriorityDetectionAgent()
        print(f"✅ Priority Agent created")
        print(f"   Agent Name: {agent.agent_name}")
        
        # Test with sample articles
        sample_articles = [
            {
                "id": "test_001",
                "title": "Sri Lanka's death toll from Cyclone Ditwah rises to 638",
                "content": "The death toll from Cyclone Ditwah has risen to 638 as rescue operations continue across affected areas.",
                "source": "ada_derana"
            },
            {
                "id": "test_002",
                "title": "Stock market gains 439 points in trading session",
                "content": "The All Share Price Index (ASPI) gained 439 points during today's trading session.",
                "source": "daily_ft"
            }
        ]
        
        print(f"\n📤 Classifying urgency for {len(sample_articles)} articles...")
        result = await agent.execute({"articles": sample_articles})
        
        print(f"\n📋 Priority Classification Result:")
        classifications = result.get('classifications', [])
        for cls in classifications:
            title = cls.get('title', 'N/A')
            print(f"   Article: {title[:50]}...")
            print(f"      Priority: {cls.get('priority', 'N/A')}")
            print(f"      Urgency Score: {cls.get('urgency_score', 0):.2f}")
        
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_validation_agent():
    """Test Validation Agent - validates article quality."""
    print("\n" + "="*60)
    print("5️⃣ TESTING: Validation Agent")
    print("="*60)
    
    try:
        from app.agents.validation_agent import ValidationAgent
        
        agent = ValidationAgent()
        print(f"✅ Validation Agent created")
        print(f"   Agent Name: {agent.agent_name}")
        
        # Test with a sample article
        sample_article = {
            "id": "test_001",
            "title": "Sri Lanka Economic and Investment Summit focuses on recovery",
            "content": """The Sri Lanka Economic and Investment Summit 2025 brought together key stakeholders 
            to discuss the nation's economic recovery strategy. Finance Minister outlined plans for fiscal 
            consolidation and attracting foreign investment.""",
            "source": "daily_ft",
            "url": "https://www.ft.lk/example-article"
        }
        
        print(f"\n📤 Validating article quality...")
        result = await agent.execute({"article": sample_article})
        
        print(f"\n📋 Validation Result:")
        print(f"   Valid: {result.get('valid', False)}")
        print(f"   Quality Score: {result.get('quality_score', 0):.2f}")
        print(f"   Issues Found: {len(result.get('issues', []))}")
        
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_llm_call():
    """Test actual LLM call with Groq."""
    print("\n" + "="*60)
    print("6️⃣ TESTING: Actual LLM Call (Groq)")
    print("="*60)
    
    try:
        from app.agents.config import get_agent_config, TaskComplexity
        from app.agents.llm_manager import LLMManager
        
        config = get_agent_config()
        llm_manager = LLMManager(config)
        
        print(f"📤 Making test LLM call to Groq...")
        
        # Get LLM for simple task
        llm = llm_manager.get_llm(TaskComplexity.SIMPLE)
        
        # Simple test prompt
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = [
            SystemMessage(content="You are a helpful assistant. Respond briefly."),
            HumanMessage(content="What is 2+2? Respond with just the number.")
        ]
        
        response = await llm.ainvoke(messages)
        
        print(f"✅ LLM Response: {response.content}")
        print(f"   Model used: {llm.model_name}")
        print(f"   Provider: Groq (FREE)")
        
        return True
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all agent tests."""
    print("\n" + "="*70)
    print("🤖 AI AGENTS FOR SCRAPING TASKS - INTEGRATION TEST")
    print("="*70)
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    # Test 1: Config & LLM
    config, llm_manager = await test_config_and_llm()
    results["config_llm"] = config is not None
    
    if not config:
        print("\n❌ Cannot continue without configuration")
        return
    
    # Test 2: Source Monitor Agent
    source_result = await test_source_monitor_agent()
    results["source_monitor"] = source_result is not None
    
    # Test 3: Scheduler Agent
    scheduler_result = await test_scheduler_agent()
    results["scheduler"] = scheduler_result is not None
    
    # Test 4: Priority Agent
    priority_result = await test_priority_agent()
    results["priority"] = priority_result is not None
    
    # Test 5: Validation Agent
    validation_result = await test_validation_agent()
    results["validation"] = validation_result is not None
    
    # Test 6: Actual LLM Call
    llm_works = await test_llm_call()
    results["llm_call"] = llm_works
    
    # Summary
    print("\n" + "="*70)
    print("📋 AI AGENTS TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    agent_descriptions = {
        "config_llm": "Configuration & LLM Manager",
        "source_monitor": "Source Monitor Agent (decides WHAT to scrape)",
        "scheduler": "Scheduler Agent (optimizes scraping frequency)",
        "priority": "Priority Agent (classifies urgency)",
        "validation": "Validation Agent (validates quality)",
        "llm_call": "Actual Groq LLM Call"
    }
    
    for test_name, passed_test in results.items():
        icon = "✅" if passed_test else "❌"
        desc = agent_descriptions.get(test_name, test_name)
        print(f"   {icon} {desc}: {'PASSED' if passed_test else 'FAILED'}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL AI AGENTS ARE WORKING!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
    
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
