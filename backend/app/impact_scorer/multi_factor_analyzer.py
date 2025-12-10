"""
Multi-Factor Analyzer

Extracts and scores multiple impact factors from article content:
- Severity/Magnitude signals
- Source credibility assessment
- Geographic scope detection
- Temporal urgency analysis
- Volume/momentum indicators
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Event severity classification."""
    CRISIS = "crisis"          # National emergency, disaster
    HIGH = "high"              # Major policy change, significant event
    MEDIUM = "medium"          # Important but not critical
    LOW = "low"                # Routine, minor impact
    MINIMAL = "minimal"        # Informational only


class GeographicScope(Enum):
    """Geographic coverage scope."""
    NATIONAL = "national"      # Affects entire country
    REGIONAL = "regional"      # Multiple provinces/districts
    LOCAL = "local"            # Single district/city
    INTERNATIONAL = "international"  # Cross-border implications


@dataclass
class FactorScores:
    """Container for all extracted factor scores."""
    severity_score: float           # 0-100
    credibility_score: float        # 0-100
    geographic_score: float         # 0-100
    temporal_score: float           # 0-100
    volume_score: float             # 0-100
    
    severity_level: SeverityLevel
    geographic_scope: GeographicScope
    detected_signals: List[str]
    confidence: float               # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity_score": self.severity_score,
            "credibility_score": self.credibility_score,
            "geographic_score": self.geographic_score,
            "temporal_score": self.temporal_score,
            "volume_score": self.volume_score,
            "severity_level": self.severity_level.value,
            "geographic_scope": self.geographic_scope.value,
            "detected_signals": self.detected_signals,
            "confidence": self.confidence
        }


class MultiFactorAnalyzer:
    """
    Analyzes articles to extract multiple impact factors.
    
    Uses keyword matching, pattern detection, and heuristics
    to score each factor dimension.
    """
    
    # Severity keywords by level
    CRISIS_KEYWORDS: Set[str] = {
        # Natural disasters
        "tsunami", "earthquake", "flood", "cyclone", "landslide", "drought",
        "disaster", "catastrophe", "calamity",
        # Critical events
        "state of emergency", "martial law", "curfew", "evacuation",
        "death toll", "casualties", "fatalities", "missing",
        # Economic crisis
        "currency crash", "bank collapse", "default", "bankruptcy",
        "market crash", "hyperinflation", "economic crisis",
        # Security
        "terrorism", "attack", "explosion", "war", "conflict"
    }
    
    HIGH_SEVERITY_KEYWORDS: Set[str] = {
        # Political
        "impeachment", "resignation", "dissolution", "no confidence",
        "constitutional crisis", "political crisis",
        # Economic
        "recession", "layoffs", "factory closure", "strike",
        "fuel shortage", "power cut", "blackout",
        # Policy
        "major reform", "sweeping changes", "landmark decision",
        "historic", "unprecedented"
    }
    
    MEDIUM_SEVERITY_KEYWORDS: Set[str] = {
        # Government actions
        "new policy", "regulation", "circular", "gazette",
        "amendment", "revision", "tender", "procurement",
        # Business events
        "quarterly results", "merger", "acquisition", "expansion",
        "investment", "partnership", "contract"
    }
    
    # Source credibility mapping (normalized 0-100)
    SOURCE_CREDIBILITY: Dict[str, int] = {
        # Government sources (90-100)
        "government": 100,
        "dmc": 100,          # Disaster Management Centre
        "central_bank": 100,
        "cbsl": 100,
        "president": 95,
        "prime_minister": 95,
        "ministry": 90,
        
        # Official news (75-85)
        "reuters": 85,
        "afp": 85,
        "daily_mirror": 80,
        "daily_news": 80,
        "ada_derana": 80,
        "hiru_news": 75,
        "newsfirst": 75,
        "lankadeepa": 75,
        
        # Other news (60-70)
        "news_outlet": 65,
        "local_media": 60,
        
        # Social/unverified (20-40)
        "social_media": 40,
        "twitter": 35,
        "facebook": 30,
        "unverified": 20,
        "unknown": 30
    }
    
    # Geographic scope keywords
    NATIONAL_KEYWORDS: Set[str] = {
        "nationwide", "national", "country-wide", "across sri lanka",
        "all districts", "island-wide", "entire country"
    }
    
    REGIONAL_KEYWORDS: Set[str] = {
        "province", "provincial", "multiple districts", "region",
        "western province", "southern province", "central province",
        "northern province", "eastern province", "north western",
        "sabaragamuwa", "uva", "north central"
    }
    
    LOCAL_KEYWORDS: Set[str] = {
        "district", "divisional", "local", "municipality", "town",
        "village", "pradeshiya sabha", "urban council"
    }
    
    INTERNATIONAL_KEYWORDS: Set[str] = {
        "international", "global", "world", "imf", "world bank",
        "foreign", "export", "import", "bilateral", "multilateral"
    }
    
    def __init__(self):
        """Initialize the multi-factor analyzer."""
        self._compile_patterns()
        logger.info("MultiFactorAnalyzer initialized")
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        # Number extraction patterns
        self.number_pattern = re.compile(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|crore|lakh|%|percent)?\b', re.IGNORECASE)
        
        # Date patterns for temporal analysis
        self.date_pattern = re.compile(
            r'\b(today|yesterday|tomorrow|breaking|just now|hours? ago|'
            r'this morning|tonight|this week|next week|last week)\b',
            re.IGNORECASE
        )
        
        # District names for geographic analysis (Sri Lanka specific)
        self.districts = {
            "colombo", "gampaha", "kalutara", "kandy", "matale", "nuwara eliya",
            "galle", "matara", "hambantota", "jaffna", "kilinochchi", "mannar",
            "vavuniya", "mullaitivu", "batticaloa", "ampara", "trincomalee",
            "kurunegala", "puttalam", "anuradhapura", "polonnaruwa", "badulla",
            "monaragala", "ratnapura", "kegalle"
        }
    
    def analyze(
        self,
        title: str,
        content: str,
        source: str = "unknown",
        publish_time: Optional[datetime] = None,
        mention_count: int = 1
    ) -> FactorScores:
        """
        Analyze article and extract all factor scores.
        
        Args:
            title: Article title
            content: Article body content
            source: Source name/identifier
            publish_time: Publication timestamp
            mention_count: Number of mentions/references
            
        Returns:
            FactorScores with all dimensions scored
        """
        # Combine and normalize text
        full_text = f"{title} {content}".lower()
        title_lower = title.lower()
        
        detected_signals = []
        
        # 1. Analyze severity
        severity_score, severity_level, severity_signals = self._analyze_severity(
            full_text, title_lower
        )
        detected_signals.extend(severity_signals)
        
        # 2. Analyze source credibility
        credibility_score = self._analyze_credibility(source)
        if credibility_score >= 80:
            detected_signals.append(f"credible_source:{source}")
        
        # 3. Analyze geographic scope
        geographic_score, geographic_scope, geo_signals = self._analyze_geography(
            full_text
        )
        detected_signals.extend(geo_signals)
        
        # 4. Analyze temporal urgency
        temporal_score, temporal_signals = self._analyze_temporal(
            full_text, title_lower, publish_time
        )
        detected_signals.extend(temporal_signals)
        
        # 5. Analyze volume/momentum
        volume_score = self._analyze_volume(mention_count, full_text)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(
            severity_score, credibility_score, len(detected_signals)
        )
        
        return FactorScores(
            severity_score=severity_score,
            credibility_score=credibility_score,
            geographic_score=geographic_score,
            temporal_score=temporal_score,
            volume_score=volume_score,
            severity_level=severity_level,
            geographic_scope=geographic_scope,
            detected_signals=detected_signals[:15],  # Limit signals
            confidence=confidence
        )
    
    def _analyze_severity(
        self,
        text: str,
        title: str
    ) -> Tuple[float, SeverityLevel, List[str]]:
        """
        Analyze event severity from content.
        
        Returns:
            Tuple of (score 0-100, level, detected signals)
        """
        signals = []
        
        # Check crisis keywords
        crisis_matches = [kw for kw in self.CRISIS_KEYWORDS if kw in text]
        if crisis_matches:
            signals.extend([f"crisis:{kw}" for kw in crisis_matches[:3]])
        
        # Check high severity keywords
        high_matches = [kw for kw in self.HIGH_SEVERITY_KEYWORDS if kw in text]
        if high_matches:
            signals.extend([f"high:{kw}" for kw in high_matches[:3]])
        
        # Check medium severity keywords
        medium_matches = [kw for kw in self.MEDIUM_SEVERITY_KEYWORDS if kw in text]
        if medium_matches:
            signals.extend([f"medium:{kw}" for kw in medium_matches[:2]])
        
        # Title weight boost (keywords in title are more significant)
        title_crisis = any(kw in title for kw in self.CRISIS_KEYWORDS)
        title_high = any(kw in title for kw in self.HIGH_SEVERITY_KEYWORDS)
        
        # Calculate score
        if crisis_matches or title_crisis:
            base_score = 85
            level = SeverityLevel.CRISIS
            boost = min(len(crisis_matches) * 5, 15)
            score = min(base_score + boost, 100)
        elif high_matches or title_high:
            base_score = 65
            level = SeverityLevel.HIGH
            boost = min(len(high_matches) * 5, 15)
            score = min(base_score + boost, 80)
        elif medium_matches:
            base_score = 45
            level = SeverityLevel.MEDIUM
            boost = min(len(medium_matches) * 3, 10)
            score = min(base_score + boost, 60)
        else:
            # Check for any numeric indicators (large numbers suggest importance)
            numbers = self.number_pattern.findall(text)
            if numbers:
                score = 30
                level = SeverityLevel.LOW
            else:
                score = 15
                level = SeverityLevel.MINIMAL
        
        return score, level, signals
    
    def _analyze_credibility(self, source: str) -> float:
        """
        Analyze source credibility.
        
        Args:
            source: Source name/identifier
            
        Returns:
            Credibility score 0-100
        """
        source_lower = source.lower().replace(" ", "_").replace("-", "_")
        
        # Direct match
        if source_lower in self.SOURCE_CREDIBILITY:
            return float(self.SOURCE_CREDIBILITY[source_lower])
        
        # Partial match
        for known_source, score in self.SOURCE_CREDIBILITY.items():
            if known_source in source_lower or source_lower in known_source:
                return float(score)
        
        # Default for unknown sources
        return 30.0
    
    def _analyze_geography(
        self,
        text: str
    ) -> Tuple[float, GeographicScope, List[str]]:
        """
        Analyze geographic scope of the event.
        
        Returns:
            Tuple of (score 0-100, scope, signals)
        """
        signals = []
        
        # Check for national scope
        national_match = any(kw in text for kw in self.NATIONAL_KEYWORDS)
        
        # Check for international scope
        international_match = any(kw in text for kw in self.INTERNATIONAL_KEYWORDS)
        
        # Check for regional scope
        regional_match = any(kw in text for kw in self.REGIONAL_KEYWORDS)
        
        # Count district mentions
        districts_mentioned = [d for d in self.districts if d in text]
        
        if international_match:
            scope = GeographicScope.INTERNATIONAL
            score = 100
            signals.append("scope:international")
        elif national_match or len(districts_mentioned) >= 5:
            scope = GeographicScope.NATIONAL
            score = 90
            signals.append("scope:national")
        elif regional_match or len(districts_mentioned) >= 2:
            scope = GeographicScope.REGIONAL
            score = 60
            signals.append(f"scope:regional({len(districts_mentioned)} districts)")
        else:
            scope = GeographicScope.LOCAL
            score = 30
            if districts_mentioned:
                signals.append(f"scope:local:{districts_mentioned[0]}")
        
        return score, scope, signals
    
    def _analyze_temporal(
        self,
        text: str,
        title: str,
        publish_time: Optional[datetime]
    ) -> Tuple[float, List[str]]:
        """
        Analyze temporal urgency.
        
        Returns:
            Tuple of (score 0-100, signals)
        """
        signals = []
        score = 50  # Default for unknown timing
        
        # Breaking news indicators
        breaking_keywords = {"breaking", "just in", "developing", "urgent", "alert"}
        if any(kw in title for kw in breaking_keywords):
            score = 100
            signals.append("temporal:breaking")
            return score, signals
        
        # Recent time indicators
        recent_keywords = {"today", "tonight", "this morning", "hours ago", "just now"}
        if any(kw in text for kw in recent_keywords):
            score = 85
            signals.append("temporal:today")
        
        # Near-term indicators
        nearterm_keywords = {"yesterday", "tomorrow", "this week"}
        if any(kw in text for kw in nearterm_keywords) and score < 85:
            score = 70
            signals.append("temporal:near_term")
        
        # Use publish time if available
        if publish_time:
            age = datetime.utcnow() - publish_time
            if age < timedelta(hours=6):
                score = max(score, 95)
                signals.append("temporal:very_recent")
            elif age < timedelta(hours=24):
                score = max(score, 80)
                signals.append("temporal:last_24h")
            elif age < timedelta(days=3):
                score = max(score, 60)
                signals.append("temporal:last_3_days")
            elif age < timedelta(days=7):
                score = 45
                signals.append("temporal:last_week")
            else:
                score = min(score, 25)
                signals.append("temporal:old")
        
        return score, signals
    
    def _analyze_volume(self, mention_count: int, text: str) -> float:
        """
        Analyze volume/momentum indicators.
        
        Args:
            mention_count: Number of mentions across sources
            text: Article text
            
        Returns:
            Volume score 0-100
        """
        # Base score from mention count
        if mention_count >= 50:
            score = 100
        elif mention_count >= 20:
            score = 80
        elif mention_count >= 10:
            score = 60
        elif mention_count >= 5:
            score = 45
        elif mention_count >= 2:
            score = 30
        else:
            score = 20
        
        # Boost for viral indicators
        viral_keywords = {"trending", "viral", "widespread", "massive response"}
        if any(kw in text for kw in viral_keywords):
            score = min(score + 20, 100)
        
        return float(score)
    
    def _calculate_confidence(
        self,
        severity: float,
        credibility: float,
        signal_count: int
    ) -> float:
        """
        Calculate overall confidence in the analysis.
        
        Returns:
            Confidence score 0-1
        """
        # Higher confidence when:
        # - Source is credible
        # - Multiple signals detected
        # - Clear severity indicators
        
        credibility_factor = credibility / 100
        signal_factor = min(signal_count / 5, 1.0)  # Cap at 5 signals
        severity_factor = 0.5 + (severity / 200)  # 0.5 to 1.0 range
        
        confidence = (credibility_factor * 0.4 + 
                      signal_factor * 0.3 + 
                      severity_factor * 0.3)
        
        return round(min(confidence, 1.0), 2)
