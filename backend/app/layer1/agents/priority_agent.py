"""
Priority Detection Agent (Agent 3)

Rapidly identifies urgent/critical content requiring immediate attention:
- Disaster alerts
- Breaking news
- Policy changes
- Economic shocks

Uses Groq Llama 3.1 70B (FREE) for accurate urgency assessment.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Set

from app.agents.base_agent import BaseAgent
from app.agents.config import TaskComplexity

logger = logging.getLogger(__name__)


# Urgency keyword dictionaries
CRITICAL_KEYWORDS: Set[str] = {
    # Disasters
    "tsunami", "earthquake", "flood", "cyclone", "landslide", "storm",
    "disaster", "emergency", "evacuation", "casualty", "casualties",
    "death toll", "missing persons", "rescue", "relief",
    # Critical events
    "curfew", "state of emergency", "martial law", "terrorism", "attack",
    "explosion", "crash", "accident", "collapse",
    # Economic shocks
    "currency crash", "bank collapse", "market crash", "default",
    # DMC alerts
    "dmc", "disaster management", "warning", "red alert"
}

HIGH_KEYWORDS: Set[str] = {
    # Political
    "parliament", "president", "prime minister", "cabinet", "minister",
    "election", "vote", "resignation", "impeachment", "protest",
    # Economic
    "interest rate", "inflation", "gdp", "central bank", "imf",
    "budget", "tax", "fuel price", "utility price",
    # Major events
    "strike", "shutdown", "blockade", "demonstration", "rally"
}

MEDIUM_KEYWORDS: Set[str] = {
    # Government
    "circular", "gazette", "regulation", "policy", "announcement",
    "tender", "contract", "procurement",
    # Business
    "quarterly results", "annual report", "merger", "acquisition",
    "investment", "expansion", "layoff"
}


PRIORITY_AGENT_PROMPT = """You are a Priority Detection Agent for urgent news classification.

ROLE: Rapidly assess content urgency to ensure critical information is processed immediately.

URGENCY LEVELS:

CRITICAL (process in <1 minute):
├── Disaster alerts (floods, earthquakes, tsunamis)
├── Severe weather warnings from DMC
├── National emergencies, attacks, major accidents
├── Major economic shocks (currency crash, bank failure)
└── Official government emergency announcements

HIGH (process in <5 minutes):
├── Breaking political news (major policy changes)
├── Large-scale protests or strikes affecting economy
├── Significant market movements
├── Major policy announcements
└── Infrastructure failures affecting businesses

MEDIUM (process in <15 minutes):
├── Important government circulars
├── Economic indicators and data releases
├── Industry-specific news
└── Regulatory changes

LOW (normal queue):
├── Routine announcements
├── Historical data and reports
├── Non-urgent updates
└── General information

ASSESSMENT CRITERIA:
1. Source authority (official government > major news > other)
2. Content keywords and signals
3. Potential business impact
4. Time sensitivity
5. Geographic scope (national > regional > local)

INPUT: Article content with metadata
OUTPUT: Urgency classification with reasoning

Respond with valid JSON:
{
  "urgency_level": "critical|high|medium|low",
  "urgency_score": 0.0-1.0,
  "detected_signals": ["signal1", "signal2"],
  "fast_track": true/false,
  "notification_required": true/false,
  "reasoning": "Brief explanation",
  "affected_sectors": ["sector1", "sector2"]
}
"""


class PriorityDetectionAgent(BaseAgent):
    """
    Agent 3: Priority Detection
    
    Classifies content urgency and routes critical items
    for fast-track processing.
    """
    
    agent_name = "priority_detection"
    agent_description = "Detects urgent content requiring immediate attention"
    task_complexity = TaskComplexity.MEDIUM  # Accuracy critical
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for priority detection."""
        return PRIORITY_AGENT_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get tools for priority detection."""
        return []  # Uses direct LLM for fast classification
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute urgency classification.
        
        Args:
            input_data: Dict with 'title', 'content', 'source'
            
        Returns:
            Dict with urgency classification
        """
        title = input_data.get("title", "")
        content = input_data.get("content", "")
        source = input_data.get("source", "unknown")
        
        # Combine for analysis
        full_text = f"{title} {content}".lower()
        
        # Quick keyword-based classification (always runs, very fast)
        keyword_result = self._keyword_classification(full_text, source)
        
        # If keywords indicate critical/high, trust that
        if keyword_result["urgency_level"] in ["critical", "high"]:
            return keyword_result
        
        # For medium/low, can optionally use LLM for refinement
        # But for speed, we use rule-based approach
        return keyword_result
    
    def _keyword_classification(
        self, 
        text: str,
        source: str
    ) -> Dict[str, Any]:
        """
        Fast keyword-based urgency classification.
        
        Args:
            text: Combined title and content (lowercase)
            source: Source name
            
        Returns:
            Urgency classification dict
        """
        detected_signals = []
        
        # Check critical keywords
        critical_matches = [kw for kw in CRITICAL_KEYWORDS if kw in text]
        if critical_matches:
            detected_signals.extend([f"critical:{kw}" for kw in critical_matches])
        
        # Check high keywords
        high_matches = [kw for kw in HIGH_KEYWORDS if kw in text]
        if high_matches:
            detected_signals.extend([f"high:{kw}" for kw in high_matches])
        
        # Check medium keywords
        medium_matches = [kw for kw in MEDIUM_KEYWORDS if kw in text]
        if medium_matches:
            detected_signals.extend([f"medium:{kw}" for kw in medium_matches[:3]])
        
        # Calculate urgency level
        if critical_matches:
            urgency_level = "critical"
            urgency_score = min(0.7 + len(critical_matches) * 0.1, 1.0)
        elif high_matches and len(high_matches) >= 2:
            urgency_level = "high"
            urgency_score = min(0.5 + len(high_matches) * 0.1, 0.8)
        elif high_matches or medium_matches:
            urgency_level = "medium" if high_matches else "low"
            urgency_score = 0.3 + len(high_matches + medium_matches) * 0.05
        else:
            urgency_level = "low"
            urgency_score = 0.1
        
        # Source authority boost
        official_sources = ["dmc", "government", "central_bank", "president", "pm"]
        if any(src in source.lower() for src in official_sources):
            urgency_score = min(urgency_score + 0.15, 1.0)
            detected_signals.append("official_source")
        
        # Determine actions
        fast_track = urgency_level in ["critical", "high"]
        notify = urgency_level == "critical"
        
        # Infer affected sectors
        sectors = self._infer_sectors(text)
        
        return {
            "urgency_level": urgency_level,
            "urgency_score": round(urgency_score, 2),
            "detected_signals": detected_signals[:10],  # Limit signals
            "fast_track": fast_track,
            "notification_required": notify,
            "reasoning": self._generate_reasoning(
                urgency_level, 
                critical_matches, 
                high_matches,
                medium_matches
            ),
            "affected_sectors": sectors,
            "processing_priority": self._get_priority_number(urgency_level),
            "decision_method": "keyword_based"
        }
    
    def _infer_sectors(self, text: str) -> List[str]:
        """Infer affected business sectors from content."""
        sectors = []
        
        sector_keywords = {
            "tourism": ["tourist", "tourism", "hotel", "travel", "airline"],
            "finance": ["bank", "finance", "loan", "interest", "investment"],
            "retail": ["retail", "shop", "consumer", "price", "market"],
            "manufacturing": ["factory", "manufacturing", "production", "export"],
            "agriculture": ["farmer", "agriculture", "crop", "harvest", "paddy"],
            "transport": ["transport", "logistics", "shipping", "port", "road"],
            "energy": ["power", "electricity", "fuel", "gas", "energy"],
            "healthcare": ["hospital", "health", "medical", "covid", "disease"]
        }
        
        for sector, keywords in sector_keywords.items():
            if any(kw in text for kw in keywords):
                sectors.append(sector)
        
        return sectors[:5]  # Limit to top 5
    
    def _generate_reasoning(
        self,
        level: str,
        critical: List[str],
        high: List[str],
        medium: List[str]
    ) -> str:
        """Generate human-readable reasoning."""
        if level == "critical":
            return f"CRITICAL: Detected {len(critical)} critical signals: {', '.join(critical[:3])}"
        elif level == "high":
            signals = critical + high
            return f"HIGH priority: {len(signals)} urgent signals detected"
        elif level == "medium":
            return f"Medium priority: {len(high + medium)} relevant signals"
        else:
            return "Low priority: No urgent signals detected"
    
    def _get_priority_number(self, level: str) -> int:
        """Convert urgency level to priority number (lower = higher priority)."""
        mapping = {
            "critical": 1,
            "high": 10,
            "medium": 50,
            "low": 100
        }
        return mapping.get(level, 100)
    
    async def classify_batch(
        self, 
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Classify urgency for a batch of articles.
        
        Args:
            articles: List of articles to classify
            
        Returns:
            Dict with classified articles by urgency level
        """
        results = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "total": len(articles)
        }
        
        for article in articles:
            classification = await self.execute(article)
            level = classification["urgency_level"]
            
            results[level].append({
                "article_id": article.get("article_id"),
                "title": article.get("title", "")[:100],
                "classification": classification
            })
        
        # Sort by priority within each level
        for level in ["critical", "high", "medium", "low"]:
            results[level].sort(
                key=lambda x: x["classification"]["urgency_score"],
                reverse=True
            )
        
        results["summary"] = {
            "critical_count": len(results["critical"]),
            "high_count": len(results["high"]),
            "medium_count": len(results["medium"]),
            "low_count": len(results["low"]),
            "fast_track_count": len(results["critical"]) + len(results["high"])
        }
        
        return results
