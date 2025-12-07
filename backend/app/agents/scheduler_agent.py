"""
Scheduler Agent (Agent 5)

Dynamically optimizes scraping frequencies based on:
- Historical scraping patterns
- Source update behavior
- System resource usage
- Efficiency metrics

Uses Groq Llama 3.1 70B (FREE) for strategic optimization.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent
from app.agents.config import TaskComplexity
from app.agents.tools.database_tools import (
    get_all_source_schedules,
    update_scraping_schedule,
    get_source_reliability
)

logger = logging.getLogger(__name__)


SCHEDULER_PROMPT = """You are a Scheduler Agent for optimizing data collection frequency.

ROLE: Analyze source performance and optimize scraping schedules to maximize efficiency while ensuring timely data collection.

OPTIMIZATION GOALS:
1. Minimize wasted scrapes (scrapes with 0 new articles)
2. Maximize article capture (don't miss updates)
3. Balance resource usage across sources
4. Adapt to changing source behavior

ANALYSIS APPROACH:
For each source, consider:
- Average articles per scrape: Low (<1) suggests decrease frequency
- Update patterns: Some sources peak at certain hours
- Reliability: Frequent failures suggest different handling
- Priority level: Critical sources need higher frequency

FREQUENCY CONSTRAINTS:
- CRITICAL priority: 5-15 minutes (never slower)
- HIGH priority: 15-60 minutes
- MEDIUM priority: 1-4 hours
- LOW priority: 4-24 hours

OPTIMIZATION RULES:
1. If avg_articles_per_scrape < 0.5: DECREASE frequency by 50%
2. If avg_articles_per_scrape > 5: INCREASE frequency by 25%
3. If consecutive_failures > 2: Use exponential backoff
4. If reliability_score < 0.5: Flag for investigation

INPUT: Historical performance data for all sources
OUTPUT: Optimized schedule recommendations

Respond with valid JSON:
{
  "recommendations": [
    {
      "source_name": "source1",
      "current_frequency": 60,
      "recommended_frequency": 30,
      "reason": "High article volume justifies increase",
      "priority_change": null
    }
  ],
  "overall_efficiency": 0.0-1.0,
  "resource_savings": "Description of expected savings",
  "monitoring_alerts": ["Any concerns"]
}
"""


class SchedulerAgent(BaseAgent):
    """
    Agent 5: Adaptive Scheduler
    
    Optimizes scraping frequencies based on source behavior
    patterns and system resources.
    """
    
    agent_name = "scheduler"
    agent_description = "Optimizes scraping schedules for efficiency"
    task_complexity = TaskComplexity.MEDIUM
    
    # Frequency limits by priority
    FREQUENCY_LIMITS = {
        "critical": {"min": 5, "max": 15},
        "high": {"min": 15, "max": 60},
        "medium": {"min": 60, "max": 240},
        "low": {"min": 240, "max": 1440}
    }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for scheduling optimization."""
        return SCHEDULER_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get tools for scheduling."""
        return []  # Uses rule-based optimization
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute schedule optimization.
        
        Args:
            input_data: Optional historical data override
            
        Returns:
            Dict with optimization recommendations
        """
        # Get current schedules
        schedules = get_all_source_schedules()
        
        if not schedules:
            return {
                "recommendations": [],
                "overall_efficiency": 0.0,
                "resource_savings": "No sources configured",
                "monitoring_alerts": ["No source schedules found in database"]
            }
        
        recommendations = []
        alerts = []
        total_current_frequency = 0
        total_recommended_frequency = 0
        
        for schedule in schedules:
            source_name = schedule["source_name"]
            
            # Get reliability info
            reliability = get_source_reliability(source_name)
            
            # Calculate recommendation
            recommendation = self._optimize_source(schedule, reliability)
            
            if recommendation["change_recommended"]:
                recommendations.append(recommendation)
            
            # Track totals for efficiency calculation
            total_current_frequency += 1440 / schedule["frequency_minutes"]  # Scrapes per day
            total_recommended_frequency += 1440 / recommendation["recommended_frequency"]
            
            # Check for alerts
            if schedule.get("consecutive_failures", 0) >= 3:
                alerts.append(f"{source_name}: Multiple consecutive failures")
            
            if reliability.get("reliability_score", 1.0) < 0.5:
                alerts.append(f"{source_name}: Low reliability score")
        
        # Calculate efficiency
        if total_current_frequency > 0:
            efficiency_ratio = total_recommended_frequency / total_current_frequency
        else:
            efficiency_ratio = 1.0
        
        # Calculate resource savings
        savings = self._calculate_savings(
            total_current_frequency, 
            total_recommended_frequency
        )
        
        return {
            "recommendations": recommendations,
            "overall_efficiency": round(efficiency_ratio, 2),
            "resource_savings": savings,
            "monitoring_alerts": alerts,
            "sources_analyzed": len(schedules),
            "changes_recommended": len(recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _optimize_source(
        self, 
        schedule: Dict[str, Any],
        reliability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate optimization recommendation for a single source.
        
        Args:
            schedule: Current schedule data
            reliability: Reliability metrics
            
        Returns:
            Recommendation dict
        """
        source_name = schedule["source_name"]
        current_freq = schedule["frequency_minutes"]
        priority = schedule.get("priority_level", "medium")
        avg_articles = reliability.get("avg_articles_per_scrape", 1.0)
        failures = schedule.get("consecutive_failures", 0)
        reliability_score = reliability.get("reliability_score", 1.0)
        
        limits = self.FREQUENCY_LIMITS.get(priority, self.FREQUENCY_LIMITS["medium"])
        
        # Start with current frequency
        recommended_freq = current_freq
        reasons = []
        
        # Rule 1: Adjust based on article volume
        if avg_articles < 0.5 and current_freq < limits["max"]:
            # Too few articles, decrease frequency
            recommended_freq = min(int(current_freq * 1.5), limits["max"])
            reasons.append(f"Low article yield ({avg_articles:.1f}/scrape)")
        elif avg_articles > 5 and current_freq > limits["min"]:
            # High article volume, increase frequency
            recommended_freq = max(int(current_freq * 0.75), limits["min"])
            reasons.append(f"High article yield ({avg_articles:.1f}/scrape)")
        
        # Rule 2: Handle failures
        if failures >= 3:
            # Apply exponential backoff
            backoff_freq = min(current_freq * (2 ** (failures - 2)), limits["max"])
            if backoff_freq > recommended_freq:
                recommended_freq = int(backoff_freq)
                reasons.append(f"Exponential backoff due to {failures} failures")
        
        # Rule 3: Reliability issues
        if reliability_score < 0.5:
            # Source is unreliable, reduce frequency
            recommended_freq = min(int(recommended_freq * 1.5), limits["max"])
            reasons.append(f"Low reliability ({reliability_score:.1%})")
        
        # Ensure within limits
        recommended_freq = max(limits["min"], min(limits["max"], recommended_freq))
        
        # Determine if change is recommended
        change_recommended = abs(recommended_freq - current_freq) >= 5
        
        return {
            "source_name": source_name,
            "current_frequency": current_freq,
            "recommended_frequency": recommended_freq,
            "change_recommended": change_recommended,
            "reason": "; ".join(reasons) if reasons else "No change needed",
            "priority_level": priority,
            "metrics": {
                "avg_articles": avg_articles,
                "failures": failures,
                "reliability": reliability_score
            }
        }
    
    def _calculate_savings(
        self, 
        current_daily: float, 
        recommended_daily: float
    ) -> str:
        """Calculate and describe resource savings."""
        if current_daily == 0:
            return "No current scraping activity"
        
        reduction = current_daily - recommended_daily
        reduction_percent = (reduction / current_daily) * 100
        
        if reduction > 0:
            return (
                f"Recommended changes would reduce daily scrapes by "
                f"{reduction:.0f} ({reduction_percent:.1f}% reduction), "
                f"saving API calls and system resources"
            )
        elif reduction < 0:
            return (
                f"Recommended changes would increase daily scrapes by "
                f"{abs(reduction):.0f} ({abs(reduction_percent):.1f}% increase) "
                f"to improve data coverage"
            )
        else:
            return "Current schedule is optimal"
    
    async def apply_recommendations(
        self, 
        recommendations: List[Dict[str, Any]],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Apply schedule recommendations to the database.
        
        Args:
            recommendations: List of recommendations to apply
            dry_run: If True, only simulate changes
            
        Returns:
            Dict with results of applying changes
        """
        applied = []
        failed = []
        
        for rec in recommendations:
            if not rec.get("change_recommended"):
                continue
            
            source_name = rec["source_name"]
            new_freq = rec["recommended_frequency"]
            reason = rec["reason"]
            
            if dry_run:
                applied.append({
                    "source_name": source_name,
                    "new_frequency": new_freq,
                    "status": "simulated",
                    "reason": reason
                })
            else:
                try:
                    result = update_scraping_schedule(
                        source_name=source_name,
                        frequency_minutes=new_freq,
                        reason=f"Scheduler optimization: {reason}"
                    )
                    
                    if result.get("success"):
                        applied.append({
                            "source_name": source_name,
                            "new_frequency": new_freq,
                            "status": "applied",
                            "reason": reason
                        })
                    else:
                        failed.append({
                            "source_name": source_name,
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    failed.append({
                        "source_name": source_name,
                        "error": str(e)
                    })
        
        return {
            "dry_run": dry_run,
            "applied_count": len(applied),
            "failed_count": len(failed),
            "applied": applied,
            "failed": failed,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def run_daily_optimization(self) -> Dict[str, Any]:
        """
        Run the full daily optimization cycle.
        
        This should be scheduled to run once daily (e.g., at 2 AM).
        
        Returns:
            Complete optimization report
        """
        logger.info("Starting daily schedule optimization")
        
        # Generate recommendations
        analysis = await self.execute({})
        
        # Apply recommendations if there are changes
        if analysis["recommendations"]:
            # Dry run first
            dry_run_result = await self.apply_recommendations(
                analysis["recommendations"],
                dry_run=True
            )
            
            # Log what would change
            logger.info(f"Dry run: Would apply {dry_run_result['applied_count']} changes")
            
            # Actually apply changes
            apply_result = await self.apply_recommendations(
                analysis["recommendations"],
                dry_run=False
            )
            
            analysis["apply_result"] = apply_result
        
        return analysis
