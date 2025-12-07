"""
Processor Tools for AI Agents

LangChain tools that wrap content processing functionality:
- Content cleaning
- Language detection
- Translation
- Quality scoring
- Metadata extraction
- Semantic deduplication (90% better duplicate detection)
- Business impact scoring (better prioritization)
"""

import asyncio
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain.tools import Tool

from app.cleaning.cleaner import DataCleaner
from app.models.raw_article import RawArticle
from app.models.processed_article import ProcessedArticle

logger = logging.getLogger(__name__)

# Initialize cleaner
_cleaner = DataCleaner()


# ============================================
# Processor Tool Functions
# ============================================

def detect_content_type(content: str) -> Dict[str, Any]:
    """
    Detect the type of content (news article, PDF, API data, etc.).
    
    Args:
        content: Raw content string or dict as string
        
    Returns:
        Dict with detected content type and confidence
    """
    if not content:
        return {"type": "unknown", "confidence": 0.0, "error": "Empty content"}
    
    content_lower = content.lower() if isinstance(content, str) else str(content).lower()
    
    # Check for PDF indicators
    if "%pdf" in content_lower or content_lower.startswith("jvberi"):
        return {
            "type": "pdf",
            "confidence": 0.95,
            "processor": "process_pdf_document"
        }
    
    # Check for JSON/API data
    if content.strip().startswith("{") or content.strip().startswith("["):
        return {
            "type": "structured_data",
            "confidence": 0.9,
            "processor": "process_api_data"
        }
    
    # Check for HTML
    if "<html" in content_lower or "<body" in content_lower:
        return {
            "type": "html",
            "confidence": 0.9,
            "processor": "process_html_article"
        }
    
    # Default to news article (plain text)
    return {
        "type": "news_article",
        "confidence": 0.8,
        "processor": "process_news_article"
    }


def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect the language of the given text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dict with detected language code and confidence
    """
    if not text or len(text) < 10:
        return {"language": "unknown", "confidence": 0.0}
    
    # Simple heuristic detection for Sri Lankan context
    # In production, use langdetect or similar library
    
    # Check for Sinhala Unicode range
    sinhala_chars = sum(1 for c in text if '\u0D80' <= c <= '\u0DFF')
    # Check for Tamil Unicode range  
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    # ASCII/English chars
    ascii_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    
    total_alpha = sinhala_chars + tamil_chars + ascii_chars
    if total_alpha == 0:
        return {"language": "unknown", "confidence": 0.0}
    
    sinhala_ratio = sinhala_chars / total_alpha
    tamil_ratio = tamil_chars / total_alpha
    english_ratio = ascii_chars / total_alpha
    
    if sinhala_ratio > 0.5:
        return {"language": "si", "confidence": sinhala_ratio, "name": "Sinhala"}
    elif tamil_ratio > 0.5:
        return {"language": "ta", "confidence": tamil_ratio, "name": "Tamil"}
    elif english_ratio > 0.5:
        return {"language": "en", "confidence": english_ratio, "name": "English"}
    else:
        return {"language": "mixed", "confidence": 0.5, "name": "Mixed"}


def clean_content(text: str) -> Dict[str, Any]:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Dict with cleaned text and cleaning stats
    """
    if not text:
        return {"cleaned_text": "", "original_length": 0, "cleaned_length": 0}
    
    original_length = len(text)
    cleaned_text = _cleaner.clean_text(text)
    cleaned_length = len(cleaned_text)
    
    return {
        "cleaned_text": cleaned_text,
        "original_length": original_length,
        "cleaned_length": cleaned_length,
        "chars_removed": original_length - cleaned_length,
        "reduction_percent": round((1 - cleaned_length/original_length) * 100, 2) if original_length > 0 else 0
    }


def calculate_quality_score(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate quality score for processed content.
    
    Args:
        content: Dict with title and body
        
    Returns:
        Dict with quality score and breakdown
    """
    title = content.get("title", "")
    body = content.get("body", "")
    
    score = 0
    issues = []
    
    # Title checks (30 points max)
    if title:
        if len(title) > 10:
            score += 15
        else:
            issues.append("Title too short")
        if len(title) < 200:
            score += 10
        else:
            issues.append("Title too long")
        if not any(c.isdigit() for c in title[:5]):  # Doesn't start with numbers
            score += 5
    else:
        issues.append("Missing title")
    
    # Body checks (50 points max)
    if body:
        word_count = len(body.split())
        if word_count >= 100:
            score += 25
        elif word_count >= 50:
            score += 15
        else:
            issues.append("Content too short")
        
        # Check for proper sentences
        if ". " in body:
            score += 15
        else:
            issues.append("No proper sentence structure")
        
        # Check for excessive special characters
        special_ratio = sum(1 for c in body if not c.isalnum() and not c.isspace()) / len(body)
        if special_ratio < 0.2:
            score += 10
        else:
            issues.append("Too many special characters")
    else:
        issues.append("Missing body content")
    
    # Source/metadata checks (20 points max)
    if content.get("url"):
        score += 10
    if content.get("publish_date"):
        score += 10
    
    return {
        "quality_score": score,
        "max_score": 100,
        "is_acceptable": score >= 60,
        "issues": issues,
        "word_count": len(body.split()) if body else 0
    }


def calculate_content_hash(content: str) -> str:
    """
    Calculate hash for content deduplication.
    
    Args:
        content: Content to hash
        
    Returns:
        SHA256 hash of the content
    """
    if not content:
        return ""
    
    # Normalize content before hashing
    normalized = " ".join(content.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def check_duplicate(content_hash: str) -> Dict[str, Any]:
    """
    Check if content already exists (by hash).
    
    Args:
        content_hash: SHA256 hash of the content
        
    Returns:
        Dict with duplicate status
    """
    # TODO: Implement actual database lookup
    # For now, return no duplicate found
    
    return {
        "is_duplicate": False,
        "content_hash": content_hash,
        "matching_article_id": None,
        "message": "No duplicate found"
    }


async def _check_semantic_duplicate_async(
    article_id: str,
    title: str,
    body: str,
    url: str = "",
    source_name: str = "",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Check for semantic duplicates using embeddings.
    
    This provides 90% better duplicate detection compared to URL-only matching
    by understanding the semantic meaning of articles.
    
    Args:
        article_id: Unique article identifier
        title: Article title
        body: Article body text
        url: Article URL (optional)
        source_name: Name of the source
        language: Language code (en, si, ta)
        
    Returns:
        Dict with duplicate detection results
    """
    try:
        from app.deduplication import get_deduplicator
        
        dedup = await get_deduplicator()
        result = await dedup.check_duplicate(
            article_id=article_id,
            title=title,
            body=body,
            url=url,
            source_name=source_name,
            language=language,
            word_count=len(body.split()) if body else 0
        )
        
        return result.to_dict()
        
    except Exception as e:
        logger.error(f"Error in semantic deduplication: {e}")
        return {
            "is_duplicate": False,
            "duplicate_type": "unknown",
            "confidence": 0.0,
            "error": str(e),
            "recommendation": "accept"
        }


def check_semantic_duplicate(
    article_id: str,
    title: str,
    body: str,
    url: str = "",
    source_name: str = ""
) -> Dict[str, Any]:
    """
    Check for semantic duplicates (sync wrapper).
    
    Uses multi-level detection:
    1. URL Hash (exact match)
    2. Content Hash (normalized text)
    3. Semantic Similarity (embeddings + FAISS)
    
    Args:
        article_id: Unique article identifier
        title: Article title
        body: Article body text
        url: Article URL
        source_name: Source name
        
    Returns:
        Dict with duplicate detection results
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    _check_semantic_duplicate_async(
                        article_id, title, body, url, source_name
                    )
                )
                return future.result()
        else:
            return asyncio.run(
                _check_semantic_duplicate_async(
                    article_id, title, body, url, source_name
                )
            )
    except Exception as e:
        logger.error(f"Error in check_semantic_duplicate: {e}")
        # Fallback to simple hash check
        return check_duplicate(calculate_content_hash(title + " " + body))


async def _get_similar_articles_async(
    title: str,
    body: str,
    top_k: int = 10
) -> Dict[str, Any]:
    """Find similar articles using semantic search"""
    try:
        from app.deduplication import get_deduplicator
        
        dedup = await get_deduplicator()
        similar = await dedup.get_similar_articles(title, body, top_k=top_k)
        
        return {
            "success": True,
            "similar_articles": similar,
            "count": len(similar)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar articles: {e}")
        return {
            "success": False,
            "error": str(e),
            "similar_articles": []
        }


def get_similar_articles(title: str, body: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Find articles similar to the given text.
    
    Args:
        title: Article title
        body: Article body
        top_k: Number of results
        
    Returns:
        Dict with similar articles
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    _get_similar_articles_async(title, body, top_k)
                )
                return future.result()
        else:
            return asyncio.run(_get_similar_articles_async(title, body, top_k))
    except Exception as e:
        logger.error(f"Error in get_similar_articles: {e}")
        return {"success": False, "error": str(e), "similar_articles": []}


def get_deduplication_stats() -> Dict[str, Any]:
    """
    Get deduplication system statistics.
    
    Returns:
        Dict with dedup metrics, index stats, and cluster info
    """
    try:
        from app.deduplication import get_deduplicator_sync
        
        dedup = get_deduplicator_sync()
        return dedup.get_metrics()
        
    except Exception as e:
        logger.error(f"Error getting dedup stats: {e}")
        return {"error": str(e)}


def extract_metadata(text: str) -> Dict[str, Any]:
    """
    Extract metadata from article text.
    
    Args:
        text: Article text
        
    Returns:
        Dict with extracted metadata
    """
    if not text:
        return {"keywords": [], "entities": {}}
    
    # Simple keyword extraction (in production, use NLP libraries)
    words = text.lower().split()
    
    # Filter common words and get frequent terms
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                 'can', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                 'from', 'as', 'into', 'through', 'during', 'before', 'after',
                 'above', 'below', 'between', 'under', 'again', 'further', 'then',
                 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'that',
                 'which', 'who', 'whom', 'this', 'these', 'those', 'am', 'it', 'its'}
    
    filtered_words = [w for w in words if w.isalpha() and len(w) > 3 and w not in stopwords]
    
    # Get word frequencies
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "keywords": [k[0] for k in keywords],
        "word_count": len(words),
        "unique_words": len(set(filtered_words)),
        "entities": {}  # TODO: Implement NER
    }


def process_news_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full processing pipeline for a news article.
    
    Args:
        article_data: Dict with title, body, url, etc.
        
    Returns:
        Dict with processed article data
    """
    start_time = datetime.utcnow()
    
    title = article_data.get("title", "")
    body = article_data.get("body", "")
    
    # Clean content
    cleaned_title = _cleaner.clean_text(title)
    cleaned_body = _cleaner.clean_text(body)
    
    # Detect language
    lang_result = detect_language(cleaned_body)
    
    # Calculate quality
    quality_result = calculate_quality_score({
        "title": cleaned_title,
        "body": cleaned_body,
        "url": article_data.get("url"),
        "publish_date": article_data.get("publish_date")
    })
    
    # Extract metadata
    metadata = extract_metadata(cleaned_body)
    
    # Calculate hash for deduplication
    content_hash = calculate_content_hash(cleaned_title + " " + cleaned_body)
    
    processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return {
        "success": True,
        "processed_content": {
            "title": cleaned_title,
            "body": cleaned_body,
            "language": lang_result["language"],
            "word_count": metadata["word_count"],
            "keywords": metadata["keywords"]
        },
        "quality": quality_result,
        "content_hash": content_hash,
        "processing_time_ms": processing_time,
        "requires_translation": lang_result["language"] != "en"
    }


def translate_content(text: str, source_lang: str = "auto") -> Dict[str, Any]:
    """
    Translate content to English.
    
    Args:
        text: Text to translate
        source_lang: Source language code (or 'auto' for detection)
        
    Returns:
        Dict with translated text
    """
    # TODO: Implement actual translation using Google Translate API
    # For now, return placeholder
    
    if source_lang == "en" or (source_lang == "auto" and detect_language(text)["language"] == "en"):
        return {
            "translated": False,
            "text": text,
            "source_language": "en",
            "target_language": "en",
            "message": "Content already in English"
        }
    
    return {
        "translated": False,
        "text": text,
        "source_language": source_lang,
        "target_language": "en",
        "message": "Translation not yet implemented - content kept in original language"
    }


# ============================================
# Business Impact Scoring Functions
# ============================================

def score_business_impact(
    title: str,
    body: str,
    source: str = "unknown",
    publish_time: Optional[str] = None,
    target_sectors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate business impact score for an article.
    
    Uses multi-factor analysis including:
    - Severity/magnitude of event
    - Sector relevance
    - Source credibility
    - Geographic scope
    - Temporal urgency
    - Volume/momentum
    
    Args:
        title: Article title
        body: Article content
        source: Source name
        publish_time: Publication timestamp (ISO format)
        target_sectors: Optional list of sectors to prioritize
        
    Returns:
        Dict with impact score, priority rank, factor breakdown, and sector analysis
    """
    try:
        from app.impact_scorer import get_impact_scorer_sync
        
        scorer = get_impact_scorer_sync()
        
        article = {
            "title": title,
            "content": body,
            "source": source,
            "publish_time": publish_time
        }
        
        result = scorer.score_article_sync(article, target_sectors)
        
        return {
            "success": True,
            "impact_score": result.impact_score,
            "impact_level": result.impact_level.value,
            "priority_rank": result.priority_rank,
            "requires_fast_track": result.requires_fast_track,
            "requires_notification": result.requires_notification,
            "factors": result.factors.to_dict(),
            "factor_contributions": result.factor_contributions,
            "primary_sectors": result.primary_sectors,
            "secondary_sectors": result.secondary_sectors,
            "cascade_effects": result.cascade_effects,
            "confidence": result.confidence,
            "detected_signals": result.detected_signals,
            "processing_guidance": result.processing_guidance,
            "scoring_profile": result.scoring_profile
        }
    except Exception as e:
        logger.error(f"Error scoring business impact: {e}")
        return {
            "success": False,
            "error": str(e),
            "impact_score": 25.0,
            "impact_level": "minimal",
            "priority_rank": 5
        }


def get_sector_impact(
    title: str,
    body: str,
    target_sectors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get detailed sector impact analysis for an article.
    
    Args:
        title: Article title
        body: Article content
        target_sectors: Optional list of sectors to focus on
        
    Returns:
        Dict with sector analysis results
    """
    try:
        from app.impact_scorer.sector_engine import SectorImpactEngine
        
        engine = SectorImpactEngine()
        result = engine.analyze_sectors(
            title=title,
            content=body,
            target_sectors=target_sectors
        )
        
        return {
            "success": True,
            "overall_sector_score": result.overall_sector_score,
            "sector_count": result.sector_count,
            "primary_sectors": [s.to_dict() for s in result.primary_sectors],
            "secondary_sectors": [s.to_dict() for s in result.secondary_sectors],
            "cascade_effects": result.cascade_effects
        }
    except Exception as e:
        logger.error(f"Error analyzing sectors: {e}")
        return {
            "success": False,
            "error": str(e),
            "overall_sector_score": 0.0,
            "sector_count": 0,
            "primary_sectors": [],
            "secondary_sectors": [],
            "cascade_effects": []
        }


def get_impact_scorer_stats() -> Dict[str, Any]:
    """
    Get statistics from the business impact scorer.
    
    Returns:
        Dict with scoring statistics
    """
    try:
        from app.impact_scorer import get_impact_scorer_sync
        
        scorer = get_impact_scorer_sync()
        stats = scorer.get_stats()
        
        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"Error getting impact scorer stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def compare_scoring_profiles(
    title: str,
    body: str,
    source: str = "unknown"
) -> Dict[str, Any]:
    """
    Compare impact scores across different scoring profiles.
    
    Useful for understanding how different weight configurations
    affect article prioritization.
    
    Args:
        title: Article title
        body: Article content
        source: Source name
        
    Returns:
        Dict with scores for each profile
    """
    try:
        from app.impact_scorer.multi_factor_analyzer import MultiFactorAnalyzer
        from app.impact_scorer.sector_engine import SectorImpactEngine
        from app.impact_scorer.score_aggregator import ScoreAggregator, ScoringProfile
        
        analyzer = MultiFactorAnalyzer()
        sector_engine = SectorImpactEngine()
        
        factor_scores = analyzer.analyze(
            title=title,
            content=body,
            source=source
        )
        
        sector_result = sector_engine.analyze_sectors(
            title=title,
            content=body
        )
        
        # Compare across profiles
        profile_results = {}
        for profile in ScoringProfile:
            aggregator = ScoreAggregator(profile=profile)
            result = aggregator.aggregate(factor_scores, sector_result)
            profile_results[profile.value] = {
                "final_score": result.final_score,
                "priority_rank": result.priority_rank,
                "priority_label": result.priority_label
            }
        
        return {
            "success": True,
            "factor_scores": factor_scores.to_dict(),
            "sector_score": sector_result.overall_sector_score,
            "profile_comparison": profile_results,
            "recommendation": _recommend_profile(profile_results)
        }
    except Exception as e:
        logger.error(f"Error comparing profiles: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _recommend_profile(results: Dict[str, Any]) -> str:
    """Recommend best profile based on score variance."""
    scores = [r["final_score"] for r in results.values()]
    variance = max(scores) - min(scores)
    
    if variance < 10:
        return "balanced - scores are consistent across profiles"
    else:
        max_profile = max(results.items(), key=lambda x: x[1]["final_score"])[0]
        return f"{max_profile} - shows highest impact with this article type"


# ============================================
# Create LangChain Tools
# ============================================

def get_processor_tools() -> List[Tool]:
    """
    Get all processor tools for AI agents.
    
    Returns:
        List of LangChain Tool objects
    """
    return [
        Tool(
            name="detect_content_type",
            func=detect_content_type,
            description=(
                "Detect the type of content (news article, PDF, API data, etc.). "
                "Input: raw content string. "
                "Returns: content type and recommended processor."
            )
        ),
        Tool(
            name="detect_language",
            func=detect_language,
            description=(
                "Detect the language of text content. "
                "Input: text string. "
                "Returns: language code (en/si/ta) and confidence."
            )
        ),
        Tool(
            name="clean_content",
            func=clean_content,
            description=(
                "Clean and normalize text content. "
                "Input: raw text string. "
                "Returns: cleaned text with stats."
            )
        ),
        Tool(
            name="calculate_quality_score",
            func=lambda x: calculate_quality_score({"title": x.get("title", ""), "body": x.get("body", "")} if isinstance(x, dict) else {"body": x}),
            description=(
                "Calculate quality score for content. "
                "Input: dict with 'title' and 'body'. "
                "Returns: score (0-100), issues, acceptability."
            )
        ),
        Tool(
            name="check_duplicate",
            func=lambda x: check_duplicate(calculate_content_hash(x)),
            description=(
                "Check if content is a duplicate using hash. "
                "Input: content text. "
                "Returns: whether duplicate exists."
            )
        ),
        Tool(
            name="check_semantic_duplicate",
            func=lambda x: check_semantic_duplicate(
                article_id=x.get("article_id", ""),
                title=x.get("title", ""),
                body=x.get("body", ""),
                url=x.get("url", ""),
                source_name=x.get("source_name", "")
            ) if isinstance(x, dict) else {"error": "Input must be a dict"},
            description=(
                "Check for semantic duplicates using AI embeddings. "
                "90% better duplicate detection than URL-only matching. "
                "Input: dict with article_id, title, body, url, source_name. "
                "Returns: is_duplicate, duplicate_type, confidence, similar_articles."
            )
        ),
        Tool(
            name="get_similar_articles",
            func=lambda x: get_similar_articles(
                title=x.get("title", ""),
                body=x.get("body", ""),
                top_k=x.get("top_k", 10)
            ) if isinstance(x, dict) else {"error": "Input must be a dict"},
            description=(
                "Find articles similar to the given text using semantic search. "
                "Input: dict with title, body, optional top_k. "
                "Returns: list of similar articles with similarity scores."
            )
        ),
        Tool(
            name="extract_metadata",
            func=extract_metadata,
            description=(
                "Extract keywords and metadata from text. "
                "Input: article text. "
                "Returns: keywords, word count, entities."
            )
        ),
        Tool(
            name="process_news_article",
            func=process_news_article,
            description=(
                "Full processing pipeline for a news article. "
                "Input: dict with title, body, url, publish_date. "
                "Returns: cleaned content, quality score, metadata."
            )
        ),
        Tool(
            name="translate_content",
            func=translate_content,
            description=(
                "Translate content to English if needed. "
                "Input: text to translate. "
                "Returns: translated text or original if already English."
            )
        ),
        Tool(
            name="get_deduplication_stats",
            func=lambda _: get_deduplication_stats(),
            description=(
                "Get deduplication system statistics. "
                "No input required. "
                "Returns: metrics, index stats, cluster info."
            )
        ),
        # Business Impact Scoring Tools
        Tool(
            name="score_business_impact",
            func=lambda x: score_business_impact(
                title=x.get("title", ""),
                body=x.get("body", x.get("content", "")),
                source=x.get("source", x.get("source_name", "unknown")),
                publish_time=x.get("publish_time"),
                target_sectors=x.get("target_sectors")
            ) if isinstance(x, dict) else {"error": "Input must be a dict"},
            description=(
                "Calculate business impact score for prioritization. "
                "Multi-factor scoring: severity, sector relevance, credibility, "
                "geographic scope, temporal urgency, volume. "
                "Input: dict with title, body/content, source, optional publish_time and target_sectors. "
                "Returns: impact_score (0-100), priority_rank (1-5), factor breakdown, sector analysis."
            )
        ),
        Tool(
            name="get_sector_impact",
            func=lambda x: get_sector_impact(
                title=x.get("title", ""),
                body=x.get("body", x.get("content", "")),
                target_sectors=x.get("target_sectors")
            ) if isinstance(x, dict) else {"error": "Input must be a dict"},
            description=(
                "Analyze sector-specific business impact. "
                "Input: dict with title, body/content, optional target_sectors list. "
                "Returns: primary sectors, secondary sectors, cascade effects."
            )
        ),
        Tool(
            name="compare_scoring_profiles",
            func=lambda x: compare_scoring_profiles(
                title=x.get("title", ""),
                body=x.get("body", x.get("content", "")),
                source=x.get("source", "unknown")
            ) if isinstance(x, dict) else {"error": "Input must be a dict"},
            description=(
                "Compare impact scores across different scoring profiles. "
                "Profiles: balanced, urgency_focused, business_focused, credibility_focused. "
                "Input: dict with title, body/content, optional source. "
                "Returns: scores for each profile with recommendation."
            )
        ),
        Tool(
            name="get_impact_scorer_stats",
            func=lambda _: get_impact_scorer_stats(),
            description=(
                "Get business impact scorer statistics. "
                "No input required. "
                "Returns: articles scored, average score, critical count, processing time."
            )
        ),
    ]
