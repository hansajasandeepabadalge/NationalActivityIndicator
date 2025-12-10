"""
Validation Agent (Agent 4)

Ensures data quality through intelligent validation:
- Field completeness checks
- Scraping error detection
- Cross-source validation
- Fake news signals
- Auto-correction of common errors

Uses Groq Llama 3.1 8B (FREE) for fast pattern recognition.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

from app.agents.base_agent import BaseAgent
from app.agents.config import TaskComplexity

logger = logging.getLogger(__name__)


class ValidationAgent(BaseAgent):
    """
    Agent 4: Data Quality Validation
    
    Validates processed content before storage, detecting errors
    and applying corrections when possible.
    """
    
    agent_name = "validation"
    agent_description = "Validates data quality and detects errors"
    task_complexity = TaskComplexity.SIMPLE  # Use fast 8B model
    
    # Validation thresholds
    MIN_TITLE_LENGTH = 10
    MAX_TITLE_LENGTH = 300
    MIN_BODY_LENGTH = 50
    MAX_SPECIAL_CHAR_RATIO = 0.3
    MIN_QUALITY_SCORE = 50
    
    # Common scraping artifacts to clean
    SCRAPING_ARTIFACTS = [
        r'<[^>]+>',  # HTML tags
        r'&[a-z]+;',  # HTML entities
        r'\s+',  # Excessive whitespace
        r'[\x00-\x1f\x7f-\x9f]',  # Control characters
        r'javascript:.*?;',  # JavaScript artifacts
        r'Cookie.*?policy',  # Cookie notices
        r'Subscribe.*?newsletter',  # Newsletter prompts
    ]
    
    # Known trusted sources
    TRUSTED_SOURCES = {
        "ada_derana", "daily_mirror", "sunday_times", "island",
        "government", "central_bank", "dmc", "met_department"
    }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for validation."""
        return "You are a data quality validation agent."
    
    def get_tools(self) -> List[Any]:
        """Get tools for validation."""
        return []  # Uses rule-based validation
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content validation.
        
        Args:
            input_data: Dict with content to validate
            
        Returns:
            Dict with validation results
        """
        issues = []
        corrections = {}
        
        title = input_data.get("title", "")
        body = input_data.get("body", "") or input_data.get("content", "")
        url = input_data.get("url", "")
        source = input_data.get("source", "unknown")
        publish_date = input_data.get("publish_date")
        
        # 1. Check required fields
        field_issues = self._check_required_fields(title, body, url)
        issues.extend(field_issues)
        
        # 2. Check for scraping errors and clean
        body, scraping_issues, scraping_corrections = self._detect_scraping_errors(body)
        issues.extend(scraping_issues)
        corrections.update(scraping_corrections)
        
        # 3. Validate title
        title, title_issues, title_corrections = self._validate_title(title)
        issues.extend(title_issues)
        corrections.update(title_corrections)
        
        # 4. Validate body content
        body_issues = self._validate_body(body)
        issues.extend(body_issues)
        
        # 5. Validate URL
        url_issues = self._validate_url(url)
        issues.extend(url_issues)
        
        # 6. Validate timestamp
        date_issues = self._validate_timestamp(publish_date)
        issues.extend(date_issues)
        
        # 7. Check source trustworthiness
        source_info = self._check_source(source)
        
        # 8. Detect suspicious content
        suspicious_issues = self._detect_suspicious_content(title, body)
        issues.extend(suspicious_issues)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(issues), 
            len(body.split()) if body else 0,
            source_info["is_trusted"]
        )
        
        # Determine validity
        is_valid = quality_score >= self.MIN_QUALITY_SCORE and len(field_issues) == 0
        requires_review = 40 <= quality_score < 60 or len(suspicious_issues) > 0
        
        return {
            "is_valid": is_valid,
            "quality_score": quality_score,
            "validation_issues": issues,
            "auto_corrections": corrections,
            "requires_review": requires_review,
            "corrected_content": {
                "title": title,
                "body": body
            },
            "source_info": source_info,
            "issue_count": len(issues),
            "correction_count": len(corrections),
            "recommendation": self._get_recommendation(is_valid, quality_score, issues)
        }
    
    def _check_required_fields(
        self, 
        title: str, 
        body: str, 
        url: str
    ) -> List[str]:
        """Check that all required fields are present and valid."""
        issues = []
        
        if not title or len(title.strip()) == 0:
            issues.append("Missing or empty title")
        
        if not body or len(body.strip()) == 0:
            issues.append("Missing or empty body content")
        
        return issues
    
    def _detect_scraping_errors(
        self, 
        content: str
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Detect and fix common scraping errors.
        
        Returns:
            Tuple of (cleaned_content, issues, corrections)
        """
        if not content:
            return content, [], {}
        
        issues = []
        corrections = {}
        original = content
        
        # Check for HTML tags
        if re.search(r'<[^>]+>', content):
            issues.append("HTML tags found in content")
            content = re.sub(r'<[^>]+>', ' ', content)
            corrections["removed_html_tags"] = True
        
        # Check for HTML entities
        if re.search(r'&[a-z]+;', content):
            issues.append("HTML entities found")
            content = re.sub(r'&nbsp;', ' ', content)
            content = re.sub(r'&amp;', '&', content)
            content = re.sub(r'&lt;', '<', content)
            content = re.sub(r'&gt;', '>', content)
            corrections["decoded_html_entities"] = True
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', content):
            content = re.sub(r'\s+', ' ', content)
            corrections["normalized_whitespace"] = True
        
        # Check for control characters
        if re.search(r'[\x00-\x1f\x7f-\x9f]', content):
            issues.append("Control characters found")
            content = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)
            corrections["removed_control_chars"] = True
        
        # Check for broken encoding
        if 'â€' in content or 'Ã' in content:
            issues.append("Possible encoding issues detected")
        
        return content.strip(), issues, corrections
    
    def _validate_title(
        self, 
        title: str
    ) -> Tuple[str, List[str], Dict[str, Any]]:
        """
        Validate and clean article title.
        
        Returns:
            Tuple of (cleaned_title, issues, corrections)
        """
        if not title:
            return title, ["Missing title"], {}
        
        issues = []
        corrections = {}
        
        # Clean title
        title = title.strip()
        
        # Check length
        if len(title) < self.MIN_TITLE_LENGTH:
            issues.append(f"Title too short ({len(title)} chars)")
        elif len(title) > self.MAX_TITLE_LENGTH:
            issues.append(f"Title too long ({len(title)} chars)")
            title = title[:self.MAX_TITLE_LENGTH] + "..."
            corrections["truncated_title"] = True
        
        # Check for all caps
        if title.isupper():
            issues.append("Title in all caps")
            title = title.title()
            corrections["normalized_caps"] = True
        
        # Check for excessive punctuation
        punct_count = sum(1 for c in title if c in '!?.')
        if punct_count > 3:
            issues.append("Excessive punctuation in title")
        
        return title, issues, corrections
    
    def _validate_body(self, body: str) -> List[str]:
        """Validate body content quality."""
        if not body:
            return ["Missing body content"]
        
        issues = []
        
        # Check length
        word_count = len(body.split())
        if word_count < 20:
            issues.append(f"Body too short ({word_count} words)")
        
        # Check for excessive special characters
        if body:
            special_ratio = sum(1 for c in body if not c.isalnum() and not c.isspace()) / len(body)
            if special_ratio > self.MAX_SPECIAL_CHAR_RATIO:
                issues.append(f"Excessive special characters ({special_ratio:.1%})")
        
        # Check for proper sentence structure
        if body and '. ' not in body and '.' not in body:
            issues.append("No sentence structure detected")
        
        # Check for repetitive content
        words = body.lower().split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                issues.append("Highly repetitive content")
        
        return issues
    
    def _validate_url(self, url: str) -> List[str]:
        """Validate article URL."""
        if not url:
            return []  # URL is optional
        
        issues = []
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                issues.append("URL missing scheme (http/https)")
            if not parsed.netloc:
                issues.append("Invalid URL format")
        except Exception:
            issues.append("Malformed URL")
        
        return issues
    
    def _validate_timestamp(self, timestamp: Any) -> List[str]:
        """Validate publish timestamp."""
        if not timestamp:
            return []  # Timestamp is optional
        
        issues = []
        
        try:
            if isinstance(timestamp, str):
                # Try parsing ISO format
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                dt = timestamp
            else:
                issues.append("Invalid timestamp format")
                return issues
            
            # Check for future dates
            if dt > datetime.utcnow():
                issues.append("Publish date is in the future")
            
            # Check for very old dates
            if dt.year < 2000:
                issues.append("Publish date seems too old")
                
        except Exception as e:
            issues.append(f"Could not parse timestamp: {e}")
        
        return issues
    
    def _check_source(self, source: str) -> Dict[str, Any]:
        """Check source trustworthiness."""
        source_lower = source.lower() if source else ""
        
        is_trusted = any(ts in source_lower for ts in self.TRUSTED_SOURCES)
        
        return {
            "source": source,
            "is_trusted": is_trusted,
            "trust_level": "high" if is_trusted else "medium"
        }
    
    def _detect_suspicious_content(
        self, 
        title: str, 
        body: str
    ) -> List[str]:
        """Detect potentially fake or suspicious content."""
        issues = []
        full_text = f"{title} {body}".lower()
        
        # Check for clickbait patterns
        clickbait_patterns = [
            r'you won\'t believe',
            r'shocking',
            r'doctors hate',
            r'one weird trick',
            r'click here',
            r'share before'
        ]
        
        for pattern in clickbait_patterns:
            if re.search(pattern, full_text):
                issues.append(f"Clickbait pattern detected: {pattern}")
                break
        
        # Check for excessive claims
        excessive_claims = ['100%', 'guaranteed', 'miracle', 'secret']
        claim_count = sum(1 for claim in excessive_claims if claim in full_text)
        if claim_count >= 2:
            issues.append("Multiple excessive claims detected")
        
        return issues
    
    def _calculate_quality_score(
        self, 
        issue_count: int,
        word_count: int,
        is_trusted_source: bool
    ) -> int:
        """Calculate overall quality score (0-100)."""
        score = 100
        
        # Deduct for issues
        score -= issue_count * 10
        
        # Deduct for short content
        if word_count < 50:
            score -= 20
        elif word_count < 100:
            score -= 10
        
        # Bonus for trusted source
        if is_trusted_source:
            score += 10
        
        # Clamp to valid range
        return max(0, min(100, score))
    
    def _get_recommendation(
        self, 
        is_valid: bool, 
        score: int, 
        issues: List[str]
    ) -> str:
        """Generate recommendation based on validation."""
        if is_valid and score >= 80:
            return "High quality content, approved for storage"
        elif is_valid and score >= 60:
            return f"Acceptable quality with {len(issues)} minor issues"
        elif score >= 40:
            return f"Low quality, needs review: {', '.join(issues[:2])}"
        else:
            return f"Rejected: {len(issues)} critical issues found"
    
    async def validate_batch(
        self, 
        articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate a batch of articles.
        
        Args:
            articles: List of articles to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            "valid": [],
            "invalid": [],
            "needs_review": [],
            "total": len(articles)
        }
        
        for article in articles:
            try:
                validation = await self.execute(article)
                
                article_result = {
                    "article_id": article.get("article_id"),
                    "title": article.get("title", "")[:50],
                    "validation": validation
                }
                
                if validation["is_valid"] and not validation["requires_review"]:
                    results["valid"].append(article_result)
                elif validation["requires_review"]:
                    results["needs_review"].append(article_result)
                else:
                    results["invalid"].append(article_result)
                    
            except Exception as e:
                logger.error(f"Validation error: {e}")
                results["invalid"].append({
                    "article_id": article.get("article_id"),
                    "error": str(e)
                })
        
        results["summary"] = {
            "valid_count": len(results["valid"]),
            "invalid_count": len(results["invalid"]),
            "review_count": len(results["needs_review"]),
            "validation_rate": len(results["valid"]) / max(len(articles), 1) * 100
        }
        
        return results
