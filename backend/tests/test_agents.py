"""
Tests for AI Agent System

Tests the basic functionality of all AI agents without requiring
actual LLM API keys (uses mocked responses).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Import agents
from app.agents.config import AgentConfig, get_agent_config
from app.agents.source_monitor_agent import SourceMonitorAgent
from app.agents.processing_agent import ProcessingAgent
from app.agents.priority_agent import PriorityDetectionAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.scheduler_agent import SchedulerAgent


class TestAgentConfig:
    """Tests for agent configuration."""
    
    def test_get_agent_config(self):
        """Test that config loads correctly."""
        config = get_agent_config()
        
        assert config is not None
        assert hasattr(config, 'sources')
        assert hasattr(config, 'llm_config')
        assert len(config.sources) > 0
    
    def test_source_priorities(self):
        """Test that all sources have valid priorities."""
        config = get_agent_config()
        valid_priorities = ["critical", "high", "medium", "low"]
        
        for source in config.sources:
            assert source.priority_level in valid_priorities


class TestSourceMonitorAgent:
    """Tests for SourceMonitorAgent."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = SourceMonitorAgent()
        
        assert agent.agent_name == "source_monitor"
        assert agent.get_system_prompt() is not None
    
    @pytest.mark.asyncio
    async def test_rule_based_check(self):
        """Test rule-based source checking."""
        agent = SourceMonitorAgent()
        
        # Mock a source that needs scraping
        test_source = {
            "source_name": "test_source",
            "last_scraped": None,  # Never scraped
            "frequency_minutes": 60,
            "priority_level": "high"
        }
        
        # The agent should decide to scrape sources without recent data
        result = agent._needs_scraping_rule_based(test_source)
        assert result is True


class TestProcessingAgent:
    """Tests for ProcessingAgent."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = ProcessingAgent()
        
        assert agent.agent_name == "processing"
        assert agent.get_system_prompt() is not None
    
    def test_language_detection(self):
        """Test basic language detection."""
        agent = ProcessingAgent()
        
        # Test with Sinhala content
        sinhala_text = "මෙය සිංහල පාඨයකි"
        result = agent._detect_language(sinhala_text)
        assert result in ["si", "unknown"]
        
        # Test with English content  
        english_text = "This is English text"
        result = agent._detect_language(english_text)
        assert result in ["en", "unknown"]


class TestPriorityAgent:
    """Tests for PriorityDetectionAgent."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = PriorityDetectionAgent()
        
        assert agent.agent_name == "priority_detection"
        assert agent.get_system_prompt() is not None
    
    def test_keyword_classification_critical(self):
        """Test critical content detection."""
        agent = PriorityDetectionAgent()
        
        critical_text = "breaking: major earthquake hits capital devastating the region"
        
        result = agent._keyword_classification(critical_text, "news")
        assert result is not None
        assert result["urgency_level"] in ["critical", "high"]
    
    def test_keyword_classification_normal(self):
        """Test normal content detection."""
        agent = PriorityDetectionAgent()
        
        normal_text = "local festival celebrations continue with traditional events"
        
        result = agent._keyword_classification(normal_text, "news")
        # Should be low or medium priority
        assert result["urgency_level"] in ["low", "medium"]


class TestValidationAgent:
    """Tests for ValidationAgent."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = ValidationAgent()
        
        assert agent.agent_name == "validation"
        assert agent.get_system_prompt() is not None
    
    @pytest.mark.asyncio
    async def test_basic_validation_pass(self):
        """Test validation of valid content."""
        agent = ValidationAgent()
        
        valid_content = {
            "title": "Valid Article Title Here That Is Long Enough",
            "content": "This is valid article content with enough text to pass validation checks. " * 20,
            "url": "https://example.com/article/123",
            "publish_date": "2024-01-15"
        }
        
        result = await agent.execute(valid_content)
        assert result["is_valid"] is True
        assert result["quality_score"] >= 60
    
    @pytest.mark.asyncio
    async def test_basic_validation_fail(self):
        """Test validation of invalid content."""
        agent = ValidationAgent()
        
        invalid_content = {
            "title": "",  # Empty title
            "content": "Short",  # Too short
            "url": ""  # Missing URL
        }
        
        result = await agent.execute(invalid_content)
        assert result["is_valid"] is False
        assert len(result["validation_issues"]) > 0


class TestSchedulerAgent:
    """Tests for SchedulerAgent."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = SchedulerAgent()
        
        assert agent.agent_name == "scheduler"
        assert agent.get_system_prompt() is not None
    
    def test_frequency_limits(self):
        """Test that frequency limits are properly defined."""
        agent = SchedulerAgent()
        
        assert "critical" in agent.FREQUENCY_LIMITS
        assert "high" in agent.FREQUENCY_LIMITS
        assert "medium" in agent.FREQUENCY_LIMITS
        assert "low" in agent.FREQUENCY_LIMITS
        
        # Critical should have lowest limits
        assert agent.FREQUENCY_LIMITS["critical"]["min"] < agent.FREQUENCY_LIMITS["low"]["min"]
    
    def test_optimize_source_high_volume(self):
        """Test optimization for high-volume source."""
        agent = SchedulerAgent()
        
        schedule = {
            "source_name": "test_source",
            "frequency_minutes": 60,
            "priority_level": "high",
            "consecutive_failures": 0
        }
        
        reliability = {
            "avg_articles_per_scrape": 10,  # High volume
            "reliability_score": 0.95
        }
        
        result = agent._optimize_source(schedule, reliability)
        
        # Should recommend increasing frequency (lower minutes)
        assert result["recommended_frequency"] <= schedule["frequency_minutes"]
    
    def test_optimize_source_low_volume(self):
        """Test optimization for low-volume source."""
        agent = SchedulerAgent()
        
        schedule = {
            "source_name": "test_source",
            "frequency_minutes": 30,
            "priority_level": "medium",
            "consecutive_failures": 0
        }
        
        reliability = {
            "avg_articles_per_scrape": 0.2,  # Low volume
            "reliability_score": 0.95
        }
        
        result = agent._optimize_source(schedule, reliability)
        
        # Should recommend decreasing frequency (higher minutes)
        assert result["recommended_frequency"] >= schedule["frequency_minutes"]


class TestLLMManager:
    """Tests for LLM Manager."""
    
    def test_manager_initialization(self):
        """Test that LLM manager initializes."""
        from app.agents.llm_manager import LLMManager
        
        manager = LLMManager()
        assert manager is not None
        assert hasattr(manager, 'invoke')
    
    def test_daily_stats(self):
        """Test that stats tracking works."""
        from app.agents.llm_manager import get_llm_manager
        
        manager = get_llm_manager()
        stats = manager.get_daily_stats()
        
        assert "groq" in stats
        assert "together" in stats
        assert "openai" in stats


# Integration test - requires mocking
class TestOrchestratorMocked:
    """Tests for MasterOrchestrator with mocked components."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test that orchestrator initializes."""
        from app.orchestrator import create_orchestrator
        
        orchestrator = create_orchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'run_cycle')
        assert hasattr(orchestrator, 'get_status')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
