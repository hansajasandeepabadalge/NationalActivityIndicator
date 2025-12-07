"""
Database Tools for AI Agents

LangChain tools that wrap database operations for:
- Checking scraping status
- Storing articles
- Querying metrics
- Managing schedules
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from langchain.tools import Tool, StructuredTool
from langchain.pydantic_v1 import BaseModel, Field

from app.db.session import SessionLocal
from app.models.agent_models import (
    AgentDecision,
    ScrapingSchedule,
    UrgencyClassification,
    QualityValidation,
    SourceConfig
)

logger = logging.getLogger(__name__)


# ============================================
# Tool Input Schemas (Pydantic)
# ============================================

class CheckLastScrapeInput(BaseModel):
    """Input for checking last scrape time"""
    source_name: str = Field(description="Name of the source to check")


class UpdateScheduleInput(BaseModel):
    """Input for updating scraping schedule"""
    source_name: str = Field(description="Name of the source")
    frequency_minutes: int = Field(description="New frequency in minutes")
    reason: str = Field(default="", description="Reason for the update")


class LogDecisionInput(BaseModel):
    """Input for logging agent decisions"""
    agent_name: str = Field(description="Name of the agent making the decision")
    decision_type: str = Field(description="Type of decision")
    input_data: Dict[str, Any] = Field(default={}, description="Input data for the decision")
    output_decision: Dict[str, Any] = Field(default={}, description="The decision made")
    reasoning: str = Field(default="", description="Reasoning behind the decision")


# ============================================
# Database Tool Functions
# ============================================

def check_last_scrape_time(source_name: str) -> Dict[str, Any]:
    """
    Check when a source was last scraped.
    
    Args:
        source_name: Name of the source
        
    Returns:
        Dict with last_scraped, articles_count, and time_since_last_scrape
    """
    try:
        db = SessionLocal()
        schedule = db.query(ScrapingSchedule).filter(
            ScrapingSchedule.source_name == source_name
        ).first()
        db.close()
        
        if not schedule:
            return {
                "source_name": source_name,
                "found": False,
                "last_scraped": None,
                "articles_count": 0,
                "time_since_scrape_minutes": None,
                "message": f"Source '{source_name}' not found in schedule"
            }
        
        time_since = None
        if schedule.last_scraped:
            delta = datetime.utcnow() - schedule.last_scraped
            time_since = int(delta.total_seconds() / 60)
        
        return {
            "source_name": source_name,
            "found": True,
            "last_scraped": schedule.last_scraped.isoformat() if schedule.last_scraped else None,
            "articles_count": schedule.last_articles_count,
            "time_since_scrape_minutes": time_since,
            "frequency_minutes": schedule.frequency_minutes,
            "priority_level": schedule.priority_level,
            "is_active": schedule.is_active,
            "consecutive_failures": schedule.consecutive_failures
        }
    except Exception as e:
        logger.error(f"Error checking last scrape for {source_name}: {e}")
        return {"error": str(e), "source_name": source_name}


def get_all_source_schedules() -> List[Dict[str, Any]]:
    """
    Get scraping schedule for all active sources.
    
    Returns:
        List of source schedules with last scrape info
    """
    try:
        db = SessionLocal()
        schedules = db.query(ScrapingSchedule).filter(
            ScrapingSchedule.is_active == True
        ).all()
        db.close()
        
        result = []
        now = datetime.utcnow()
        
        for schedule in schedules:
            time_since = None
            should_scrape = True
            
            if schedule.last_scraped:
                delta = now - schedule.last_scraped
                time_since = int(delta.total_seconds() / 60)
                should_scrape = time_since >= schedule.frequency_minutes
            
            result.append({
                "source_name": schedule.source_name,
                "last_scraped": schedule.last_scraped.isoformat() if schedule.last_scraped else None,
                "time_since_scrape_minutes": time_since,
                "frequency_minutes": schedule.frequency_minutes,
                "priority_level": schedule.priority_level,
                "should_scrape": should_scrape,
                "articles_last_scrape": schedule.last_articles_count,
                "consecutive_failures": schedule.consecutive_failures
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting source schedules: {e}")
        return []


def update_scraping_schedule(
    source_name: str, 
    frequency_minutes: int,
    reason: str = ""
) -> Dict[str, Any]:
    """
    Update the scraping frequency for a source.
    
    Args:
        source_name: Name of the source
        frequency_minutes: New frequency in minutes
        reason: Reason for the update
        
    Returns:
        Updated schedule info
    """
    try:
        db = SessionLocal()
        schedule = db.query(ScrapingSchedule).filter(
            ScrapingSchedule.source_name == source_name
        ).first()
        
        if not schedule:
            db.close()
            return {"error": f"Source '{source_name}' not found", "success": False}
        
        old_frequency = schedule.frequency_minutes
        schedule.frequency_minutes = frequency_minutes
        schedule.updated_by = "scheduler_agent"
        schedule.updated_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        logger.info(f"Updated {source_name} frequency: {old_frequency} -> {frequency_minutes} min")
        
        return {
            "success": True,
            "source_name": source_name,
            "old_frequency": old_frequency,
            "new_frequency": frequency_minutes,
            "reason": reason
        }
    except Exception as e:
        logger.error(f"Error updating schedule for {source_name}: {e}")
        return {"error": str(e), "success": False}


def update_scrape_result(
    source_name: str,
    articles_count: int,
    success: bool = True
) -> Dict[str, Any]:
    """
    Update the result of a scrape operation.
    
    Args:
        source_name: Name of the source
        articles_count: Number of articles scraped
        success: Whether the scrape was successful
        
    Returns:
        Updated schedule info
    """
    try:
        db = SessionLocal()
        schedule = db.query(ScrapingSchedule).filter(
            ScrapingSchedule.source_name == source_name
        ).first()
        
        if not schedule:
            db.close()
            return {"error": f"Source '{source_name}' not found"}
        
        schedule.last_scraped = datetime.utcnow()
        schedule.last_articles_count = articles_count
        
        if success:
            schedule.consecutive_failures = 0
            schedule.total_articles_scraped += articles_count
            # Update rolling average
            if schedule.avg_articles_per_scrape == 0:
                schedule.avg_articles_per_scrape = articles_count
            else:
                schedule.avg_articles_per_scrape = (
                    schedule.avg_articles_per_scrape * 0.9 + articles_count * 0.1
                )
        else:
            schedule.consecutive_failures += 1
        
        db.commit()
        db.close()
        
        return {
            "success": True,
            "source_name": source_name,
            "articles_count": articles_count,
            "total_scraped": schedule.total_articles_scraped
        }
    except Exception as e:
        logger.error(f"Error updating scrape result for {source_name}: {e}")
        return {"error": str(e)}


def get_source_reliability(source_name: str) -> Dict[str, Any]:
    """
    Get reliability score and stats for a source.
    
    Args:
        source_name: Name of the source
        
    Returns:
        Source reliability information
    """
    try:
        db = SessionLocal()
        schedule = db.query(ScrapingSchedule).filter(
            ScrapingSchedule.source_name == source_name
        ).first()
        db.close()
        
        if not schedule:
            return {"error": f"Source '{source_name}' not found"}
        
        return {
            "source_name": source_name,
            "reliability_score": schedule.reliability_score,
            "avg_articles_per_scrape": schedule.avg_articles_per_scrape,
            "consecutive_failures": schedule.consecutive_failures,
            "total_articles_scraped": schedule.total_articles_scraped,
            "is_reliable": schedule.reliability_score >= 0.7 and schedule.consecutive_failures < 3
        }
    except Exception as e:
        logger.error(f"Error getting reliability for {source_name}: {e}")
        return {"error": str(e)}


def log_agent_decision(
    agent_name: str,
    decision_type: str,
    input_data: Dict[str, Any] = None,
    output_decision: Dict[str, Any] = None,
    reasoning: str = "",
    llm_provider: str = "groq",
    llm_model: str = "llama-3.1-70b-versatile",
    tokens_used: int = 0,
    latency_ms: int = 0,
    success: bool = True,
    error_message: str = None
) -> Dict[str, Any]:
    """
    Log an agent decision to the database.
    
    Args:
        agent_name: Name of the agent
        decision_type: Type of decision made
        input_data: Input data for the decision
        output_decision: The decision output
        reasoning: Reasoning for the decision
        llm_provider: LLM provider used
        llm_model: Model used
        tokens_used: Tokens consumed
        latency_ms: Response latency
        success: Whether the decision was successful
        error_message: Error message if failed
        
    Returns:
        Confirmation of logging
    """
    try:
        db = SessionLocal()
        
        decision = AgentDecision(
            agent_name=agent_name,
            decision_type=decision_type,
            input_data=input_data or {},
            output_decision=output_decision or {},
            reasoning=reasoning,
            llm_provider=llm_provider,
            llm_model=llm_model,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            cost_usd=0.0,  # Groq is FREE!
            success=success,
            error_message=error_message
        )
        
        db.add(decision)
        db.commit()
        decision_id = decision.id
        db.close()
        
        return {
            "success": True,
            "decision_id": decision_id,
            "agent_name": agent_name,
            "decision_type": decision_type
        }
    except Exception as e:
        logger.error(f"Error logging decision for {agent_name}: {e}")
        return {"error": str(e), "success": False}


def get_source_config(source_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific source.
    
    Args:
        source_name: Name of the source
        
    Returns:
        Source configuration
    """
    try:
        db = SessionLocal()
        config = db.query(SourceConfig).filter(
            SourceConfig.name == source_name
        ).first()
        db.close()
        
        if not config:
            return {"error": f"Source '{source_name}' not found"}
        
        return {
            "name": config.name,
            "display_name": config.display_name,
            "base_url": config.base_url,
            "source_type": config.source_type,
            "language": config.language,
            "category": config.category,
            "priority_level": config.priority_level,
            "scraper_class": config.scraper_class,
            "default_frequency_minutes": config.default_frequency_minutes,
            "is_active": config.is_active
        }
    except Exception as e:
        logger.error(f"Error getting config for {source_name}: {e}")
        return {"error": str(e)}


def get_all_active_sources() -> List[Dict[str, Any]]:
    """
    Get all active source configurations.
    
    Returns:
        List of active source configs
    """
    try:
        db = SessionLocal()
        configs = db.query(SourceConfig).filter(
            SourceConfig.is_active == True
        ).all()
        db.close()
        
        return [
            {
                "name": c.name,
                "display_name": c.display_name,
                "source_type": c.source_type,
                "priority_level": c.priority_level,
                "scraper_class": c.scraper_class
            }
            for c in configs
        ]
    except Exception as e:
        logger.error(f"Error getting active sources: {e}")
        return []


# ============================================
# Create LangChain Tools
# ============================================

def get_database_tools() -> List[Tool]:
    """
    Get all database tools for AI agents.
    
    Returns:
        List of LangChain Tool objects
    """
    return [
        Tool(
            name="check_last_scrape_time",
            func=check_last_scrape_time,
            description=(
                "Check when a specific source was last scraped. "
                "Input: source_name (string). "
                "Returns: last_scraped timestamp, articles_count, time since last scrape."
            )
        ),
        Tool(
            name="get_all_source_schedules",
            func=lambda _: get_all_source_schedules(),
            description=(
                "Get scraping schedules for ALL active sources. "
                "No input required. "
                "Returns: List of all sources with their scrape status and whether they should be scraped."
            )
        ),
        StructuredTool.from_function(
            func=update_scraping_schedule,
            name="update_scraping_schedule",
            description=(
                "Update the scraping frequency for a source. "
                "Use this to optimize scraping based on source behavior."
            ),
            args_schema=UpdateScheduleInput
        ),
        Tool(
            name="get_source_reliability",
            func=get_source_reliability,
            description=(
                "Get reliability score and statistics for a source. "
                "Input: source_name (string). "
                "Returns: reliability_score, avg_articles, failures, etc."
            )
        ),
        Tool(
            name="get_source_config",
            func=get_source_config,
            description=(
                "Get configuration for a specific source. "
                "Input: source_name (string). "
                "Returns: source type, URL, priority, scraper class, etc."
            )
        ),
        Tool(
            name="get_all_active_sources",
            func=lambda _: get_all_active_sources(),
            description=(
                "Get list of all active sources that can be scraped. "
                "No input required. "
                "Returns: List of source names with their types and priorities."
            )
        ),
    ]
