"""Rule-based indicator classification using keyword matching (optimized)"""

from typing import List, Dict, Tuple
import re
from functools import lru_cache
import hashlib

from .keyword_config import INDICATOR_KEYWORDS, KEYWORD_WEIGHTS


class RuleBasedClassifier:
    """Rule-based indicator assignment using keyword matching with caching"""

    def __init__(self, enable_cache: bool = True):
        """Initialize classifier with keyword configuration
        
        Args:
            enable_cache: Enable LRU cache for repeated classifications (default: True)
        """
        self.keyword_config = INDICATOR_KEYWORDS
        self.weights = KEYWORD_WEIGHTS
        self.enable_cache = enable_cache
        
        # Precompile regex patterns for performance
        self._compiled_patterns = self._compile_keyword_patterns()
        
        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0

    def _compile_keyword_patterns(self) -> Dict:
        """Precompile all keyword regex patterns for faster matching"""
        compiled = {}
        
        for indicator_id, config in self.keyword_config.items():
            compiled[indicator_id] = {}
            
            for weight_category, keyword_list in config['keywords'].items():
                compiled[indicator_id][weight_category] = [
                    re.compile(r'\b' + re.escape(kw.lower()) + r'\b')
                    for kw in keyword_list
                ]
        
        return compiled

    def classify_article(self, article_text: str, article_title: str = "") -> List[Dict]:
        """
        Classify article and return indicator assignments with confidence (cached)

        Args:
            article_text: Main content of the article
            article_title: Title of the article (weighted 2x)

        Returns:
            List of dicts with indicator_id, confidence, matched_keywords
        """
        if not article_text or not article_text.strip():
            return []
        
        # Use caching if enabled
        if self.enable_cache:
            cache_key = self._generate_cache_key(article_text, article_title)
            result = self._classify_cached(cache_key, article_text, article_title)
            return result
        else:
            return self._classify_uncached(article_text, article_title)

    def _generate_cache_key(self, article_text: str, article_title: str) -> str:
        """Generate hash key for caching"""
        content = f"{article_title}||{article_text[:500]}"  # First 500 chars
        return hashlib.md5(content.encode()).hexdigest()

    @lru_cache(maxsize=1000)  # Cache up to 1000 articles
    def _classify_cached(self, cache_key: str, article_text: str, article_title: str) -> tuple:
        """Cached classification (returns tuple for hashability)"""
        self.cache_misses += 1
        results = self._classify_uncached(article_text, article_title)
        # Convert to tuple for caching
        return tuple(tuple(r.items()) for r in results)

    def _classify_uncached(self, article_text: str, article_title: str) -> List[Dict]:
        """Actual classification logic without caching"""
        # Combine title and content (title has 2x weight for importance)
        full_text = f"{article_title} {article_title} {article_text}".lower()

        assignments = []

        for indicator_id, config in self.keyword_config.items():
            match_score, matched_keywords = self._calculate_match_score_optimized(
                full_text,
                indicator_id
            )

            if match_score > 0.1:  # Minimum threshold
                confidence = self._normalize_confidence(match_score)
                assignments.append({
                    'indicator_id': indicator_id,
                    'indicator_name': config['name'],
                    'confidence': confidence,
                    'matched_keywords': matched_keywords,
                    'keyword_match_count': len(matched_keywords)
                })

        # Sort by confidence (highest first)
        assignments.sort(key=lambda x: x['confidence'], reverse=True)

        return assignments

    def _calculate_match_score_optimized(self, text: str, indicator_id: str) -> Tuple[float, List[str]]:
        """
        Calculate weighted match score using precompiled patterns (optimized)

        Args:
            text: Text to search in
            indicator_id: Indicator ID to get patterns for

        Returns:
            Tuple of (score, matched_keywords)
        """
        score = 0.0
        matched = []

        compiled_patterns = self._compiled_patterns.get(indicator_id, {})
        
        for weight_category, pattern_list in compiled_patterns.items():
            weight = self.weights[weight_category]

            for i, pattern in enumerate(pattern_list):
                # Use precompiled regex pattern
                matches = len(pattern.findall(text))

                if matches > 0:
                    # Get original keyword for reporting
                    original_keyword = self.keyword_config[indicator_id]['keywords'][weight_category][i]
                    matched.append(original_keyword)
                    # Diminishing returns for multiple matches (cap at 3)
                    score += weight * min(matches, 3)

        return score, matched

    def _calculate_match_score(self, text: str, keywords: Dict) -> Tuple[float, List[str]]:
        """
        Legacy method: Calculate weighted match score for keywords (fallback)

        Args:
            text: Text to search in
            keywords: Dict of weight_category -> list of keywords

        Returns:
            Tuple of (score, matched_keywords)
        """
        score = 0.0
        matched = []

        for weight_category, keyword_list in keywords.items():
            weight = self.weights[weight_category]

            for keyword in keyword_list:
                # Use word boundaries for exact matching
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, text))

                if matches > 0:
                    matched.append(keyword)
                    # Diminishing returns for multiple matches (cap at 3)
                    score += weight * min(matches, 3)

        return score, matched

    def _normalize_confidence(self, raw_score: float) -> float:
        """
        Normalize score to 0-1 confidence range

        Score thresholds:
        - 5+: High confidence (0.95)
        - 3-5: Good confidence (0.7-0.95)
        - 1-3: Medium confidence (0.4-0.7)
        - <1: Low confidence (0.2-0.4)

        Args:
            raw_score: Raw weighted keyword match score

        Returns:
            Normalized confidence score (0-1)
        """
        if raw_score >= 5:
            return 0.95
        elif raw_score >= 3:
            return 0.7 + (raw_score - 3) * 0.125  # 0.7 to 0.95
        elif raw_score >= 1:
            return 0.4 + (raw_score - 1) * 0.15  # 0.4 to 0.7
        else:
            return 0.2 + raw_score * 0.2  # 0.2 to 0.4

    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'cache_enabled': self.enable_cache,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total,
            'hit_rate_percent': round(hit_rate, 1),
            'cache_size': self._classify_cached.cache_info().currsize if self.enable_cache else 0,
            'cache_maxsize': self._classify_cached.cache_info().maxsize if self.enable_cache else 0
        }

    def clear_cache(self):
        """Clear the classification cache"""
        if self.enable_cache:
            self._classify_cached.cache_clear()
            self.cache_hits = 0
            self.cache_misses = 0
