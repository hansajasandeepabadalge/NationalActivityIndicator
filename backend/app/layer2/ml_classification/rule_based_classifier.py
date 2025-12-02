"""Rule-based indicator classification using keyword matching"""

from typing import List, Dict, Tuple
import re

from .keyword_config import INDICATOR_KEYWORDS, KEYWORD_WEIGHTS


class RuleBasedClassifier:
    """Rule-based indicator assignment using keyword matching"""

    def __init__(self):
        """Initialize classifier with keyword configuration"""
        self.keyword_config = INDICATOR_KEYWORDS
        self.weights = KEYWORD_WEIGHTS

    def classify_article(self, article_text: str, article_title: str = "") -> List[Dict]:
        """
        Classify article and return indicator assignments with confidence

        Args:
            article_text: Main content of the article
            article_title: Title of the article (weighted 2x)

        Returns:
            List of dicts with indicator_id, confidence, matched_keywords
        """
        # Combine title and content (title has 2x weight for importance)
        full_text = f"{article_title} {article_title} {article_text}".lower()

        assignments = []

        for indicator_id, config in self.keyword_config.items():
            match_score, matched_keywords = self._calculate_match_score(
                full_text,
                config['keywords']
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

    def _calculate_match_score(self, text: str, keywords: Dict) -> Tuple[float, List[str]]:
        """
        Calculate weighted match score for keywords

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
