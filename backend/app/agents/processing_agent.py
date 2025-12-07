"""
Processing Agent (Agent 2)

Intelligently processes different content types:
- Detects content type (news, PDF, API data)
- Routes to appropriate processor
- Handles translation if needed
- Checks for duplicates

Uses Groq Llama 3.1 8B (FREE) for fast classification.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.agents.base_agent import BaseAgent
from app.agents.config import TaskComplexity
from app.agents.tools.processor_tools import (
    get_processor_tools,
    detect_content_type,
    detect_language,
    process_news_article,
    clean_content,
    calculate_quality_score,
    calculate_content_hash,
    check_duplicate
)

logger = logging.getLogger(__name__)


PROCESSING_AGENT_PROMPT = """You are a Content Processing Agent for a business intelligence platform.

ROLE: Process scraped content by detecting type, cleaning, translating if needed, and quality checking.

PROCESSING PIPELINE:
1. Detect content type (news article, PDF, API data, social media)
2. Check for duplicates (skip if already processed)
3. Clean and normalize content
4. Detect language (English, Sinhala, Tamil)
5. Translate to English if needed
6. Calculate quality score
7. Extract metadata (keywords, entities)

QUALITY THRESHOLDS:
- Score >= 80: High quality, process immediately
- Score 60-79: Acceptable, process with minor flags
- Score 40-59: Low quality, flag for review
- Score < 40: Reject, likely spam or error

CONTENT TYPE HANDLING:
- news_article: Clean HTML, extract text, validate structure
- pdf: Extract text, may need OCR for scanned docs
- structured_data: Parse JSON/API response, validate schema
- social_media: Handle short form, extract hashtags/mentions

INPUT: Content to process with metadata
OUTPUT: Processed content with quality assessment

Respond with valid JSON only:
{
  "action": "process|skip|reject",
  "content_type": "news_article|pdf|structured_data",
  "language": "en|si|ta|mixed",
  "needs_translation": true/false,
  "quality_score": 0-100,
  "issues": [],
  "recommendation": "Brief processing recommendation"
}
"""


class ProcessingAgent(BaseAgent):
    """
    Agent 2: Content Processing
    
    Routes content through appropriate processing pipelines
    based on content type and quality requirements.
    """
    
    agent_name = "processing"
    agent_description = "Processes and routes content through pipelines"
    task_complexity = TaskComplexity.SIMPLE  # Use fast 8B model
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for content processing."""
        return PROCESSING_AGENT_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get tools for content processing."""
        return get_processor_tools()
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content processing.
        
        Args:
            input_data: Dict with 'content', 'title', 'source', etc.
            
        Returns:
            Dict with processed content and quality assessment
        """
        content = input_data.get("content", "")
        title = input_data.get("title", "")
        source = input_data.get("source", "unknown")
        
        if not content and not title:
            return {
                "action": "reject",
                "reason": "No content provided",
                "quality_score": 0
            }
        
        # Step 1: Detect content type
        type_result = detect_content_type(content)
        content_type = type_result.get("type", "news_article")
        
        # Step 2: Check for duplicates
        content_hash = calculate_content_hash(title + " " + content[:500])
        duplicate_check = check_duplicate(content_hash)
        
        if duplicate_check.get("is_duplicate"):
            return {
                "action": "skip",
                "reason": "Duplicate content detected",
                "content_hash": content_hash,
                "matching_id": duplicate_check.get("matching_article_id")
            }
        
        # Step 3: Detect language
        lang_result = detect_language(content)
        language = lang_result.get("language", "en")
        needs_translation = language != "en" and language != "unknown"
        
        # Step 4: Process based on content type
        if content_type == "news_article":
            processed = process_news_article({
                "title": title,
                "body": content,
                "url": input_data.get("url"),
                "publish_date": input_data.get("publish_date"),
                "source": source
            })
        else:
            # For other types, do basic cleaning
            cleaned = clean_content(content)
            quality = calculate_quality_score({"title": title, "body": content})
            processed = {
                "success": True,
                "processed_content": {
                    "title": title,
                    "body": cleaned.get("cleaned_text", content),
                    "language": language
                },
                "quality": quality
            }
        
        # Extract results
        quality_score = processed.get("quality", {}).get("quality_score", 50)
        issues = processed.get("quality", {}).get("issues", [])
        
        # Determine action based on quality
        if quality_score >= 60:
            action = "process"
        elif quality_score >= 40:
            action = "review"
        else:
            action = "reject"
        
        return {
            "action": action,
            "content_type": content_type,
            "language": language,
            "needs_translation": needs_translation,
            "quality_score": quality_score,
            "issues": issues,
            "processed_content": processed.get("processed_content", {}),
            "content_hash": content_hash,
            "processing_time_ms": processed.get("processing_time_ms", 0),
            "recommendation": self._get_recommendation(quality_score, issues),
            "decision_method": "rule_based"  # Can enhance with LLM later
        }
    
    def _get_recommendation(self, score: int, issues: List[str]) -> str:
        """Generate recommendation based on quality assessment."""
        if score >= 80:
            return "High quality content, ready for storage"
        elif score >= 60:
            if issues:
                return f"Acceptable quality with minor issues: {', '.join(issues[:2])}"
            return "Acceptable quality, proceed with processing"
        elif score >= 40:
            return f"Low quality, needs review: {', '.join(issues[:3])}"
        else:
            return f"Very low quality, recommend rejection: {', '.join(issues)}"
    
    async def process_batch(
        self, 
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process a batch of articles.
        
        Args:
            articles: List of article dicts
            
        Returns:
            Dict with batch processing results
        """
        results = {
            "processed": [],
            "skipped": [],
            "rejected": [],
            "total": len(articles)
        }
        
        for article in articles:
            try:
                result = await self.execute(article)
                
                if result["action"] == "process":
                    results["processed"].append({
                        "article_id": article.get("article_id"),
                        "quality_score": result["quality_score"],
                        "content": result.get("processed_content")
                    })
                elif result["action"] == "skip":
                    results["skipped"].append({
                        "article_id": article.get("article_id"),
                        "reason": result.get("reason")
                    })
                else:
                    results["rejected"].append({
                        "article_id": article.get("article_id"),
                        "reason": result.get("recommendation"),
                        "score": result["quality_score"]
                    })
                    
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                results["rejected"].append({
                    "article_id": article.get("article_id"),
                    "reason": f"Processing error: {str(e)}"
                })
        
        results["summary"] = {
            "processed_count": len(results["processed"]),
            "skipped_count": len(results["skipped"]),
            "rejected_count": len(results["rejected"]),
            "success_rate": len(results["processed"]) / max(len(articles), 1) * 100
        }
        
        return results
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection for testing.
        
        Detects Sinhala, Tamil, or English based on character ranges.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('si', 'ta', 'en', or 'unknown')
        """
        if not text or len(text.strip()) == 0:
            return "unknown"
        
        # Count characters in different scripts
        sinhala_count = 0
        tamil_count = 0
        latin_count = 0
        total = 0
        
        for char in text:
            code = ord(char)
            if char.isalpha():
                total += 1
                # Sinhala Unicode range: U+0D80 to U+0DFF
                if 0x0D80 <= code <= 0x0DFF:
                    sinhala_count += 1
                # Tamil Unicode range: U+0B80 to U+0BFF
                elif 0x0B80 <= code <= 0x0BFF:
                    tamil_count += 1
                # Latin characters
                elif code < 128 and char.isalpha():
                    latin_count += 1
        
        if total == 0:
            return "unknown"
        
        # Determine language based on dominant script
        if sinhala_count / total > 0.3:
            return "si"
        elif tamil_count / total > 0.3:
            return "ta"
        elif latin_count / total > 0.5:
            return "en"
        else:
            return "unknown"
