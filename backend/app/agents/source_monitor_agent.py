"""
Source Monitor Agent (Agent 1)

Intelligently decides WHEN to scrape each source based on:
- Update patterns
- Priority levels
- Resource availability
- Breaking news signals

Uses Groq Llama 3.1 70B (FREE) for strategic decision-making.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from app.agents.base_agent import BaseAgent
from app.agents.config import TaskComplexity
from app.agents.tools.database_tools import (
    get_database_tools,
    get_all_source_schedules,
    check_last_scrape_time
)
from app.agents.tools.scraper_tools import get_scraper_tools, check_breaking_signals

logger = logging.getLogger(__name__)


SOURCE_MONITOR_PROMPT = """You are a Source Monitoring Agent for a real-time business intelligence platform monitoring Sri Lankan news and data sources.

ROLE: Decide which news/government/social sources to scrape RIGHT NOW based on patterns, urgency signals, and resource efficiency.

CONTEXT:
- You monitor multiple data sources (news, government, social, financial)
- Some sources update every 5 minutes (breaking news sites)
- Some update once daily (government reports)
- You must balance thoroughness with resource efficiency
- Critical alerts (disasters, emergencies) require immediate scraping

DECISION CRITERIA:

SCRAPE NOW if:
├── Breaking news signals detected (scrape ALL priority sources)
├── Time since last scrape > typical frequency for that source
├── Source is CRITICAL priority AND >5 min since last scrape
└── Source failed last time (retry if <3 consecutive failures)

SKIP if:
├── Scraped recently (within source's typical frequency)
├── Source is offline or has >3 consecutive failures
└── System under heavy load AND source is LOW priority

PRIORITY LEVELS:
1. CRITICAL: DMC, Weather alerts, Breaking news (every 5 min max)
2. HIGH: Major news sites, Government (every 15 min)
3. MEDIUM: Provincial news, Industry updates (every 1 hour)
4. LOW: Research papers, Historical data (every 4+ hours)

INPUT: You will receive:
- Current source schedules with last scrape times
- Breaking news signals (if any)
- Current timestamp

OUTPUT FORMAT (respond with valid JSON only):
{
  "sources_to_scrape": ["source1", "source2"],
  "sources_to_skip": ["source3"],
  "reasoning": "Brief explanation of your decisions",
  "urgency_detected": true/false,
  "estimated_articles": 10,
  "priority_override": null
}

IMPORTANT: 
- Be conservative - don't scrape unnecessarily
- Always scrape CRITICAL sources if due
- Respond ONLY with valid JSON, no additional text
"""


class SourceMonitorAgent(BaseAgent):
    """
    Agent 1: Source Monitor
    
    Decides which sources to scrape based on schedules, priorities,
    and breaking news signals.
    """
    
    agent_name = "source_monitor"
    agent_description = "Decides when and what sources to scrape"
    task_complexity = TaskComplexity.MEDIUM
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for source monitoring."""
        return SOURCE_MONITOR_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get tools for source monitoring."""
        return get_database_tools() + get_scraper_tools()
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute source monitoring decision.
        
        Args:
            input_data: Optional context data
            
        Returns:
            Dict with sources to scrape and reasoning
        """
        # Gather current state
        schedules = get_all_source_schedules()
        breaking_signals = check_breaking_signals()
        current_time = datetime.utcnow()
        
        # Check if we have any sources configured
        if not schedules:
            logger.warning("No source schedules found in database")
            return {
                "sources_to_scrape": [],
                "sources_to_skip": [],
                "reasoning": "No sources configured in the database",
                "urgency_detected": False,
                "estimated_articles": 0
            }
        
        # Prepare context for LLM
        context = self._prepare_context(schedules, breaking_signals, current_time)
        
        # Check if LLM is available
        if not self.config.has_groq and not self.config.use_mock_llm:
            # Fall back to rule-based decision
            logger.info("LLM not available, using rule-based decision")
            return self._rule_based_decision(schedules, breaking_signals)
        
        if self.config.use_mock_llm:
            # Mock mode for testing
            return self._rule_based_decision(schedules, breaking_signals)
        
        # Use LLM for intelligent decision
        try:
            prompt = f"{SOURCE_MONITOR_PROMPT}\n\nCURRENT STATE:\n{context}\n\nMake your scraping decisions:"
            
            response = self.invoke_llm_sync(prompt)
            
            # Parse JSON response
            decision = self._parse_response(response)
            
            return decision
            
        except Exception as e:
            logger.warning(f"LLM decision failed, using rule-based: {e}")
            return self._rule_based_decision(schedules, breaking_signals)
    
    def _prepare_context(
        self, 
        schedules: List[Dict], 
        breaking_signals: Dict,
        current_time: datetime
    ) -> str:
        """Prepare context string for LLM."""
        context_parts = [
            f"Current Time: {current_time.isoformat()}",
            f"Breaking News Detected: {breaking_signals.get('breaking_detected', False)}",
            "",
            "SOURCE STATUS:",
        ]
        
        for schedule in schedules:
            status = "DUE" if schedule.get("should_scrape") else "OK"
            time_since = schedule.get("time_since_scrape_minutes", "never")
            context_parts.append(
                f"- {schedule['source_name']}: "
                f"Priority={schedule['priority_level']}, "
                f"Frequency={schedule['frequency_minutes']}min, "
                f"Last={time_since}min ago, "
                f"Status={status}"
            )
        
        return "\n".join(context_parts)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured decision."""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            decision = json.loads(response)
            
            # Validate required fields
            if "sources_to_scrape" not in decision:
                decision["sources_to_scrape"] = []
            if "sources_to_skip" not in decision:
                decision["sources_to_skip"] = []
            if "reasoning" not in decision:
                decision["reasoning"] = "LLM decision"
            if "urgency_detected" not in decision:
                decision["urgency_detected"] = False
            
            return decision
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {response}")
            
            # Return empty decision
            return {
                "sources_to_scrape": [],
                "sources_to_skip": [],
                "reasoning": f"Failed to parse LLM response: {e}",
                "urgency_detected": False,
                "parse_error": True
            }
    
    def _rule_based_decision(
        self, 
        schedules: List[Dict],
        breaking_signals: Dict
    ) -> Dict[str, Any]:
        """
        Fallback rule-based decision when LLM is unavailable.
        
        Simple rules:
        - Scrape if time_since_scrape >= frequency
        - Always scrape if breaking news detected
        - Skip if too many consecutive failures
        """
        sources_to_scrape = []
        sources_to_skip = []
        
        urgency = breaking_signals.get("breaking_detected", False)
        
        for schedule in schedules:
            source_name = schedule["source_name"]
            should_scrape = schedule.get("should_scrape", False)
            failures = schedule.get("consecutive_failures", 0)
            priority = schedule.get("priority_level", "medium")
            
            # Skip if too many failures
            if failures >= 3:
                sources_to_skip.append(source_name)
                continue
            
            # Scrape if due or if breaking news for high priority
            if should_scrape or (urgency and priority in ["critical", "high"]):
                sources_to_scrape.append(source_name)
            else:
                sources_to_skip.append(source_name)
        
        estimated = len(sources_to_scrape) * 5  # Rough estimate
        
        return {
            "sources_to_scrape": sources_to_scrape,
            "sources_to_skip": sources_to_skip,
            "reasoning": f"Rule-based: {len(sources_to_scrape)} sources due for scraping",
            "urgency_detected": urgency,
            "estimated_articles": estimated,
            "decision_method": "rule_based"
        }
    
    def _needs_scraping_rule_based(self, source: Dict[str, Any]) -> bool:
        """
        Check if a source needs scraping using simple rules.
        
        Used for testing and as a quick check.
        
        Args:
            source: Source information dict with:
                - source_name: Name of the source
                - last_scraped: Datetime of last scrape (None if never)
                - frequency_minutes: Expected scrape frequency
                - priority_level: Priority level (critical, high, medium, low)
                
        Returns:
            True if the source should be scraped
        """
        from datetime import datetime, timedelta
        
        last_scraped = source.get("last_scraped")
        frequency = source.get("frequency_minutes", 60)
        priority = source.get("priority_level", "medium")
        
        # Never scraped - definitely needs scraping
        if last_scraped is None:
            return True
        
        # Convert string to datetime if needed
        if isinstance(last_scraped, str):
            try:
                last_scraped = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
            except ValueError:
                return True  # Can't parse, assume needs scraping
        
        # Calculate time since last scrape
        now = datetime.utcnow()
        if last_scraped.tzinfo:
            from datetime import timezone
            now = now.replace(tzinfo=timezone.utc)
        
        time_since = (now - last_scraped).total_seconds() / 60  # minutes
        
        # Check against frequency
        if time_since >= frequency:
            return True
        
        # Critical sources get scraped more aggressively
        if priority == "critical" and time_since >= frequency * 0.8:
            return True
        
        return False
