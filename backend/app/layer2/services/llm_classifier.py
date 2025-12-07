"""
LLM-Powered PESTEL Classification Service

This module provides advanced classification using Groq's Llama 3.1 70B model.
It extends the existing HybridClassifier with:
- Multi-label PESTEL classification with confidence scores
- Sub-theme identification
- Urgency and business relevance scoring
- Rich classification explanations

Falls back to HybridClassifier if LLM is unavailable or for simple articles.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .llm_base import GroqLLMClient, LLMConfig, CacheConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Classification Models
# ============================================================================

class PESTELCategory(str, Enum):
    """PESTEL classification categories mapped to indicator IDs."""
    POLITICAL = "political"
    ECONOMIC = "economic"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"


class UrgencyLevel(str, Enum):
    """Article urgency classification."""
    BREAKING = "breaking"      # Immediate impact, < 24 hours
    URGENT = "urgent"          # Short-term impact, 1-7 days
    IMPORTANT = "important"    # Medium-term impact, 1-4 weeks
    STANDARD = "standard"      # Regular monitoring
    LOW = "low"                # Background information


class BusinessRelevance(str, Enum):
    """Business relevance classification."""
    CRITICAL = "critical"      # Direct business impact
    HIGH = "high"              # Significant market implications
    MEDIUM = "medium"          # Industry-wide relevance
    LOW = "low"                # General information
    MINIMAL = "minimal"        # Limited business relevance


# Pydantic models for structured LLM output
class CategoryClassification(BaseModel):
    """Single category classification result."""
    category: str = Field(description="PESTEL category (political, economic, social, technological, environmental, legal)")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    sub_themes: List[str] = Field(default_factory=list, description="Specific sub-themes within category")
    reasoning: str = Field(default="", description="Brief reasoning for this classification")


class LLMClassificationResult(BaseModel):
    """Complete LLM classification response structure."""
    categories: List[CategoryClassification] = Field(default_factory=list, description="All applicable PESTEL categories")
    primary_category: str = Field(description="The most relevant PESTEL category")
    urgency: str = Field(default="standard", description="Urgency level: breaking, urgent, important, standard, low")
    business_relevance: str = Field(default="medium", description="Business relevance: critical, high, medium, low, minimal")
    key_entities: List[str] = Field(default_factory=list, description="Key entities mentioned")
    summary: str = Field(default="", description="Brief one-sentence summary")


# ============================================================================
# Classification Result Dataclass
# ============================================================================

@dataclass
class ClassificationResult:
    """
    Enhanced classification result with full metadata.
    
    Compatible with existing HybridClassifier output but with additional fields.
    """
    # Primary classification
    primary_indicator_id: str
    primary_category: PESTELCategory
    primary_confidence: float
    
    # Multi-label classifications
    all_categories: Dict[str, float] = field(default_factory=dict)  # category -> confidence
    sub_themes: Dict[str, List[str]] = field(default_factory=dict)  # category -> sub-themes
    
    # Additional metadata
    urgency: UrgencyLevel = UrgencyLevel.STANDARD
    business_relevance: BusinessRelevance = BusinessRelevance.MEDIUM
    key_entities: List[str] = field(default_factory=list)
    summary: str = ""
    reasoning: str = ""
    
    # Processing metadata
    classification_source: str = "llm"  # "llm" or "hybrid_fallback"
    processing_time_ms: float = 0.0
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "primary_indicator_id": self.primary_indicator_id,
            "primary_category": self.primary_category.value,
            "primary_confidence": self.primary_confidence,
            "all_categories": self.all_categories,
            "sub_themes": self.sub_themes,
            "urgency": self.urgency.value,
            "business_relevance": self.business_relevance.value,
            "key_entities": self.key_entities,
            "summary": self.summary,
            "reasoning": self.reasoning,
            "classification_source": self.classification_source,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached
        }
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy HybridClassifier format for backward compatibility.
        
        Returns format matching existing HybridClassifier output.
        """
        return {
            "indicator_id": self.primary_indicator_id,
            "category": self.primary_category.value,
            "confidence": self.primary_confidence,
            "all_scores": self.all_categories
        }


# ============================================================================
# Category to Indicator Mapping
# ============================================================================

# Map PESTEL categories to specific indicator IDs
CATEGORY_TO_INDICATORS = {
    PESTELCategory.POLITICAL: [
        "POL_UNREST",
        "POL_STABILITY",
        "POL_POLICY",
        "POL_ELECTION",
        "POL_GOVERNANCE"
    ],
    PESTELCategory.ECONOMIC: [
        "ECO_INFLATION",
        "ECO_GROWTH",
        "ECO_EMPLOYMENT",
        "ECO_TRADE",
        "ECO_INVESTMENT",
        "ECO_FISCAL"
    ],
    PESTELCategory.SOCIAL: [
        "SOC_SENTIMENT",
        "SOC_DEMOGRAPHICS",
        "SOC_WELFARE",
        "SOC_EDUCATION",
        "SOC_HEALTH"
    ],
    PESTELCategory.TECHNOLOGICAL: [
        "TECH_INNOVATION",
        "TECH_DIGITAL",
        "TECH_INFRASTRUCTURE"
    ],
    PESTELCategory.ENVIRONMENTAL: [
        "ENV_CLIMATE",
        "ENV_RESOURCES",
        "ENV_SUSTAINABILITY"
    ],
    PESTELCategory.LEGAL: [
        "LEG_REGULATORY",
        "LEG_COMPLIANCE",
        "LEG_REFORM"
    ]
}

# Sub-theme to indicator refinement
SUB_THEME_INDICATORS = {
    "inflation": "ECO_INFLATION",
    "price": "ECO_INFLATION",
    "cost of living": "ECO_INFLATION",
    "interest rate": "ECO_FISCAL",
    "gdp": "ECO_GROWTH",
    "economic growth": "ECO_GROWTH",
    "unemployment": "ECO_EMPLOYMENT",
    "jobs": "ECO_EMPLOYMENT",
    "trade": "ECO_TRADE",
    "export": "ECO_TRADE",
    "import": "ECO_TRADE",
    "investment": "ECO_INVESTMENT",
    "protest": "POL_UNREST",
    "demonstration": "POL_UNREST",
    "election": "POL_ELECTION",
    "vote": "POL_ELECTION",
    "policy": "POL_POLICY",
    "regulation": "LEG_REGULATORY",
    "law": "LEG_REFORM",
    "climate": "ENV_CLIMATE",
    "pollution": "ENV_RESOURCES",
    "technology": "TECH_INNOVATION",
    "digital": "TECH_DIGITAL",
    "infrastructure": "TECH_INFRASTRUCTURE"
}


# ============================================================================
# LLM Classifier Service
# ============================================================================

class LLMClassifier:
    """
    LLM-powered article classifier using Groq's Llama 3.1 70B.
    
    Features:
    - Multi-label PESTEL classification
    - Confidence scoring for each category
    - Sub-theme identification
    - Urgency and business relevance assessment
    - Fallback to HybridClassifier when needed
    - Response caching for efficiency
    
    Usage:
        classifier = LLMClassifier()
        result = await classifier.classify("Article text here...")
    """
    
    # Classification prompt template
    CLASSIFICATION_PROMPT = """Analyze this article and classify it according to the PESTEL framework.

ARTICLE:
{article_text}

INSTRUCTIONS:
1. Identify ALL applicable PESTEL categories (can be multiple)
2. For each category, provide:
   - Confidence score (0.0 to 1.0)
   - Specific sub-themes within that category
   - Brief reasoning
3. Determine the PRIMARY category (most relevant)
4. Assess urgency based on time-sensitivity of the information
5. Assess business relevance for business decision-making

PESTEL Categories:
- political: Government actions, policies, political stability, elections, governance
- economic: Economy, inflation, employment, trade, investment, fiscal policy, markets
- social: Public sentiment, demographics, welfare, education, health, social issues
- technological: Innovation, digital transformation, infrastructure, tech adoption
- environmental: Climate, resources, sustainability, environmental regulations
- legal: Laws, regulations, compliance, legal reforms, court decisions

Urgency Levels:
- breaking: Immediate impact expected within 24 hours
- urgent: Short-term impact within 1-7 days
- important: Medium-term impact within 1-4 weeks
- standard: Regular monitoring importance
- low: Background information only

Business Relevance:
- critical: Direct and immediate business impact
- high: Significant market or industry implications
- medium: Industry-wide or sector relevance
- low: General informational value
- minimal: Limited business relevance

Respond with a structured analysis."""

    SYSTEM_PROMPT = """You are an expert PESTEL analyst specializing in news classification for national activity indicators. 
Your task is to accurately classify news articles and provide detailed analysis.
Be precise with confidence scores - only use high confidence (>0.8) when the classification is very clear.
Always consider multiple applicable categories when relevant.
Provide concise but informative reasoning."""

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        fallback_classifier: Optional[Any] = None,
        min_text_length: int = 100,
        use_llm_threshold: float = 0.6
    ):
        """
        Initialize LLM Classifier.
        
        Args:
            llm_config: LLM configuration (uses defaults if not provided)
            cache_config: Cache configuration (uses defaults if not provided)
            fallback_classifier: Instance of HybridClassifier for fallback
            min_text_length: Minimum text length to use LLM
            use_llm_threshold: Complexity threshold for LLM usage
        """
        self.llm_config = llm_config or LLMConfig()
        self.cache_config = cache_config or CacheConfig(prefix="llm_classifier")
        self.llm_client = GroqLLMClient(self.llm_config, self.cache_config)
        self.fallback_classifier = fallback_classifier
        self.min_text_length = min_text_length
        self.use_llm_threshold = use_llm_threshold
        
        # Statistics
        self._total_classifications = 0
        self._llm_classifications = 0
        self._fallback_classifications = 0
        self._errors = 0
    
    async def classify(
        self,
        text: str,
        title: str = "",
        source: str = "",
        force_llm: bool = False
    ) -> ClassificationResult:
        """
        Classify an article using LLM.
        
        Args:
            text: Article text content
            title: Article title (optional, enhances classification)
            source: Article source (optional)
            force_llm: Force LLM usage even for simple articles
        
        Returns:
            ClassificationResult with full classification details
        """
        import time
        start_time = time.time()
        
        self._total_classifications += 1
        
        # Combine title and text for classification
        full_text = f"{title}\n\n{text}" if title else text
        
        # Check if we should use LLM or fallback
        if not force_llm and not self._should_use_llm(full_text):
            return await self._fallback_classify(full_text, start_time)
        
        try:
            # Truncate very long texts
            max_length = 4000
            if len(full_text) > max_length:
                full_text = full_text[:max_length] + "..."
            
            # Build prompt
            prompt = self.CLASSIFICATION_PROMPT.format(article_text=full_text)
            
            # Get LLM classification
            response = await self.llm_client.generate_structured(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                response_model=LLMClassificationResult
            )
            
            # Convert to ClassificationResult
            result = self._parse_llm_response(response)
            result.processing_time_ms = (time.time() - start_time) * 1000
            
            self._llm_classifications += 1
            logger.info(
                f"LLM classified: {result.primary_category.value} "
                f"(confidence: {result.primary_confidence:.2f})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            self._errors += 1
            return await self._fallback_classify(full_text, start_time)
    
    async def classify_batch(
        self,
        articles: List[Dict[str, str]],
        concurrency: int = 5
    ) -> List[ClassificationResult]:
        """
        Classify multiple articles concurrently.
        
        Args:
            articles: List of dicts with 'text', optional 'title', 'source'
            concurrency: Max concurrent classifications
        
        Returns:
            List of ClassificationResult objects
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def classify_with_limit(article: Dict[str, str]) -> ClassificationResult:
            async with semaphore:
                return await self.classify(
                    text=article.get("text", ""),
                    title=article.get("title", ""),
                    source=article.get("source", "")
                )
        
        tasks = [classify_with_limit(article) for article in articles]
        return await asyncio.gather(*tasks)
    
    def _should_use_llm(self, text: str) -> bool:
        """
        Determine if LLM should be used for this text.
        
        Uses heuristics to decide:
        - Text length (too short = simple)
        - Presence of complex vocabulary
        - Multiple potential categories
        """
        # Too short - use fallback
        if len(text) < self.min_text_length:
            return False
        
        # Use LLM client's complexity check
        return self.llm_client._should_use_llm(text, self.use_llm_threshold)
    
    def _parse_llm_response(self, response: LLMClassificationResult) -> ClassificationResult:
        """
        Parse LLM response into ClassificationResult.
        
        Args:
            response: Structured LLM response
        
        Returns:
            ClassificationResult object
        """
        # Build category confidence dict
        all_categories = {}
        sub_themes = {}
        reasoning_parts = []
        
        for cat_result in response.categories:
            category_key = cat_result.category.lower()
            all_categories[category_key] = cat_result.confidence
            if cat_result.sub_themes:
                sub_themes[category_key] = cat_result.sub_themes
            if cat_result.reasoning:
                reasoning_parts.append(f"{category_key}: {cat_result.reasoning}")
        
        # Determine primary category
        primary_cat_str = response.primary_category.lower()
        try:
            primary_category = PESTELCategory(primary_cat_str)
        except ValueError:
            # Default to most confident if primary is invalid
            if all_categories:
                primary_cat_str = max(all_categories.keys(), key=lambda k: all_categories[k])
                primary_category = PESTELCategory(primary_cat_str)
            else:
                primary_category = PESTELCategory.ECONOMIC  # Default
        
        # Get primary confidence
        primary_confidence = all_categories.get(primary_cat_str, 0.5)
        
        # Determine indicator ID
        primary_indicator = self._get_indicator_id(
            primary_category,
            sub_themes.get(primary_cat_str, [])
        )
        
        # Parse urgency
        try:
            urgency = UrgencyLevel(response.urgency.lower())
        except ValueError:
            urgency = UrgencyLevel.STANDARD
        
        # Parse business relevance
        try:
            business_relevance = BusinessRelevance(response.business_relevance.lower())
        except ValueError:
            business_relevance = BusinessRelevance.MEDIUM
        
        return ClassificationResult(
            primary_indicator_id=primary_indicator,
            primary_category=primary_category,
            primary_confidence=primary_confidence,
            all_categories=all_categories,
            sub_themes=sub_themes,
            urgency=urgency,
            business_relevance=business_relevance,
            key_entities=response.key_entities[:10],  # Limit entities
            summary=response.summary[:500],  # Limit summary length
            reasoning="; ".join(reasoning_parts),
            classification_source="llm",
            cached=False  # Will be set by cache layer
        )
    
    def _get_indicator_id(
        self,
        category: PESTELCategory,
        sub_themes: List[str]
    ) -> str:
        """
        Determine specific indicator ID from category and sub-themes.
        
        Uses sub-themes to refine the indicator selection.
        """
        # Check sub-themes first for specific indicator
        for theme in sub_themes:
            theme_lower = theme.lower()
            for key, indicator in SUB_THEME_INDICATORS.items():
                if key in theme_lower:
                    return indicator
        
        # Fall back to first indicator for the category
        indicators = CATEGORY_TO_INDICATORS.get(category, [])
        return indicators[0] if indicators else f"{category.value.upper()[:3]}_GENERAL"
    
    async def _fallback_classify(
        self,
        text: str,
        start_time: float
    ) -> ClassificationResult:
        """
        Fall back to HybridClassifier when LLM is not suitable.
        """
        import time
        
        self._fallback_classifications += 1
        
        if self.fallback_classifier:
            try:
                # Use existing HybridClassifier
                result = await self._run_hybrid_classifier(text)
                return result
            except Exception as e:
                logger.error(f"Fallback classifier also failed: {e}")
        
        # Ultimate fallback - rule-based heuristics
        result = self._rule_based_classify(text)
        result.processing_time_ms = (time.time() - start_time) * 1000
        result.classification_source = "rule_fallback"
        return result
    
    async def _run_hybrid_classifier(self, text: str) -> ClassificationResult:
        """
        Run the existing HybridClassifier.
        """
        # This would integrate with existing HybridClassifier
        # For now, return rule-based as placeholder
        return self._rule_based_classify(text)
    
    def _rule_based_classify(self, text: str) -> ClassificationResult:
        """
        Simple rule-based classification as ultimate fallback.
        """
        text_lower = text.lower()
        
        # Keyword matching for categories
        category_scores = {
            PESTELCategory.POLITICAL: 0.0,
            PESTELCategory.ECONOMIC: 0.0,
            PESTELCategory.SOCIAL: 0.0,
            PESTELCategory.TECHNOLOGICAL: 0.0,
            PESTELCategory.ENVIRONMENTAL: 0.0,
            PESTELCategory.LEGAL: 0.0
        }
        
        # Political keywords
        political_keywords = [
            "government", "election", "vote", "parliament", "minister",
            "president", "political", "policy", "legislation", "opposition"
        ]
        category_scores[PESTELCategory.POLITICAL] = sum(
            1 for kw in political_keywords if kw in text_lower
        ) / len(political_keywords)
        
        # Economic keywords
        economic_keywords = [
            "economy", "economic", "inflation", "gdp", "growth", "market",
            "trade", "investment", "unemployment", "interest rate", "fiscal"
        ]
        category_scores[PESTELCategory.ECONOMIC] = sum(
            1 for kw in economic_keywords if kw in text_lower
        ) / len(economic_keywords)
        
        # Social keywords
        social_keywords = [
            "social", "public", "community", "education", "health",
            "welfare", "population", "demographic", "society", "culture"
        ]
        category_scores[PESTELCategory.SOCIAL] = sum(
            1 for kw in social_keywords if kw in text_lower
        ) / len(social_keywords)
        
        # Technological keywords
        tech_keywords = [
            "technology", "digital", "innovation", "tech", "software",
            "internet", "ai", "automation", "cyber", "infrastructure"
        ]
        category_scores[PESTELCategory.TECHNOLOGICAL] = sum(
            1 for kw in tech_keywords if kw in text_lower
        ) / len(tech_keywords)
        
        # Environmental keywords
        env_keywords = [
            "environment", "climate", "carbon", "pollution", "green",
            "sustainability", "renewable", "energy", "emission", "nature"
        ]
        category_scores[PESTELCategory.ENVIRONMENTAL] = sum(
            1 for kw in env_keywords if kw in text_lower
        ) / len(env_keywords)
        
        # Legal keywords
        legal_keywords = [
            "law", "legal", "court", "regulation", "compliance",
            "legislation", "judicial", "ruling", "lawsuit", "regulatory"
        ]
        category_scores[PESTELCategory.LEGAL] = sum(
            1 for kw in legal_keywords if kw in text_lower
        ) / len(legal_keywords)
        
        # Find primary category
        primary_category = max(category_scores.keys(), key=lambda k: category_scores[k])
        primary_confidence = min(category_scores[primary_category] * 2, 0.95)  # Scale up
        
        # Default to economic if no clear match
        if primary_confidence < 0.1:
            primary_category = PESTELCategory.ECONOMIC
            primary_confidence = 0.3
        
        # Get indicator
        indicators = CATEGORY_TO_INDICATORS.get(primary_category, [])
        primary_indicator = indicators[0] if indicators else "ECO_GENERAL"
        
        return ClassificationResult(
            primary_indicator_id=primary_indicator,
            primary_category=primary_category,
            primary_confidence=primary_confidence,
            all_categories={k.value: v for k, v in category_scores.items() if v > 0},
            sub_themes={},
            urgency=UrgencyLevel.STANDARD,
            business_relevance=BusinessRelevance.MEDIUM,
            key_entities=[],
            summary="",
            reasoning="Rule-based classification fallback",
            classification_source="rule_fallback"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        llm_stats = self.llm_client.get_stats()
        return {
            "total_classifications": self._total_classifications,
            "llm_classifications": self._llm_classifications,
            "fallback_classifications": self._fallback_classifications,
            "errors": self._errors,
            "llm_usage_rate": (
                self._llm_classifications / self._total_classifications
                if self._total_classifications > 0 else 0
            ),
            "llm_client_stats": llm_stats
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_llm_classifier(
    api_key: Optional[str] = None,
    cache_enabled: bool = True,
    fallback_classifier: Optional[Any] = None
) -> LLMClassifier:
    """
    Factory function to create an LLMClassifier instance.
    
    Args:
        api_key: Groq API key (uses env var if not provided)
        cache_enabled: Whether to enable response caching
        fallback_classifier: HybridClassifier instance for fallback
    
    Returns:
        Configured LLMClassifier instance
    """
    llm_config = LLMConfig(
        model="llama-3.1-70b-versatile",
        temperature=0.2,
        max_tokens=2000
    )
    
    cache_config = CacheConfig(
        enabled=cache_enabled,
        ttl_hours=24,
        prefix="llm_classifier"
    )
    
    return LLMClassifier(
        llm_config=llm_config,
        cache_config=cache_config,
        fallback_classifier=fallback_classifier
    )
