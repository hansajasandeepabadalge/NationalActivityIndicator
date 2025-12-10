"""
Full Layer 2 Indicator Calculation System.

This module provides a comprehensive indicator calculation service that:
1. Loads all 105 indicator definitions from PostgreSQL
2. Matches articles to indicators based on keywords
3. Calculates indicator values using appropriate calculation types
4. Generates composite PESTEL scores
5. Calculates the National Activity Index (NAI)
"""

import re
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


@dataclass
class IndicatorDefinition:
    """Indicator definition from database."""
    indicator_id: str
    indicator_name: str
    pestel_category: str
    subcategory: str
    description: str
    calculation_type: str
    keywords: List[str]
    base_weight: float
    threshold_high: float
    threshold_low: float


@dataclass
class IndicatorValue:
    """Calculated indicator value."""
    indicator_id: str
    indicator_name: str
    pestel_category: str
    subcategory: str
    value: float
    confidence: float
    article_count: int
    matching_articles: List[str]
    calculation_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'indicator_id': self.indicator_id,
            'indicator_name': self.indicator_name,
            'pestel_category': self.pestel_category,
            'subcategory': self.subcategory,
            'value': self.value,
            'confidence': self.confidence,
            'article_count': self.article_count,
            'matching_articles': self.matching_articles,
            'calculation_type': self.calculation_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class FullIndicatorCalculator:
    """
    Comprehensive indicator calculator that uses all 105 indicators.
    """
    
    def __init__(self, pg_config: Optional[Dict[str, Any]] = None):
        """Initialize with PostgreSQL connection."""
        self.pg_config = pg_config or {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '15432')),
            'dbname': os.getenv('POSTGRES_DB', 'national_indicator'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres_secure_2024')
        }
        self.indicators: List[IndicatorDefinition] = []
        self._load_indicators()
        
    def _load_indicators(self):
        """Load all indicator definitions from PostgreSQL."""
        try:
            conn = psycopg2.connect(**self.pg_config)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT 
                    indicator_id,
                    indicator_name,
                    pestel_category,
                    subcategory,
                    description,
                    calculation_type,
                    base_weight,
                    threshold_high,
                    threshold_low,
                    extra_metadata
                FROM indicator_definitions
                WHERE is_active = TRUE
                ORDER BY pestel_category, indicator_name
            """)
            
            for row in cur.fetchall():
                extra = row.get('extra_metadata') or {}
                keywords = extra.get('keywords', [])
                
                self.indicators.append(IndicatorDefinition(
                    indicator_id=row['indicator_id'],
                    indicator_name=row['indicator_name'],
                    pestel_category=str(row['pestel_category']),
                    subcategory=row['subcategory'] or '',
                    description=row['description'] or '',
                    calculation_type=str(row['calculation_type']),
                    keywords=keywords,
                    base_weight=row['base_weight'] or 1.0,
                    threshold_high=row['threshold_high'] or 70.0,
                    threshold_low=row['threshold_low'] or 30.0
                ))
            
            cur.close()
            conn.close()
            
            logger.info(f"Loaded {len(self.indicators)} indicator definitions")
        except Exception as e:
            logger.error(f"Failed to load indicator definitions: {e}")
            self.indicators = []
        
    def _match_article_to_indicator(
        self, 
        article: Dict[str, Any], 
        indicator: IndicatorDefinition
    ) -> float:
        """
        Calculate match score between article and indicator.
        
        Returns a score 0-1 indicating how well the article matches.
        """
        if not indicator.keywords:
            return 0.0
            
        # Get article text
        title = article.get('title', '') or ''
        body = article.get('body', '') or ''
        
        # Also check content nested structure
        content = article.get('content', {})
        if isinstance(content, dict):
            title = title or content.get('title_translated', '') or content.get('title_original', '')
            body = body or content.get('body_translated', '') or content.get('body_original', '')
        
        text = f"{title} {body}".lower()
        
        if not text.strip():
            return 0.0
            
        # Count keyword matches
        matches = 0
        for keyword in indicator.keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text):
                matches += 1
        
        if matches == 0:
            return 0.0
            
        # Calculate match score
        # At least 2 keywords = strong match
        # 1 keyword = weak match
        if matches >= 3:
            return 1.0
        elif matches >= 2:
            return 0.8
        else:
            return 0.4
            
    def _calculate_frequency_indicator(
        self,
        matching_articles: List[Dict[str, Any]],
        indicator: IndicatorDefinition
    ) -> float:
        """Calculate frequency-based indicator value."""
        count = len(matching_articles)
        
        # Normalize to 0-100 scale
        # Assume 10 articles/day is high activity
        if count == 0:
            return 50.0  # Neutral baseline
        elif count >= 10:
            return min(100.0, 50.0 + (count * 5))
        else:
            return 50.0 + (count * 5)
            
    def _calculate_sentiment_indicator(
        self,
        matching_articles: List[Dict[str, Any]],
        indicator: IndicatorDefinition
    ) -> float:
        """Calculate sentiment-based indicator value."""
        if not matching_articles:
            return 50.0
            
        # Average sentiment scores
        sentiments = []
        for article in matching_articles:
            sentiment = article.get('sentiment', {})
            
            # Check nested nlp_features
            if not sentiment:
                nlp = article.get('nlp_features', {})
                sentiment = nlp.get('sentiment', {})
                
            if isinstance(sentiment, dict):
                score = sentiment.get('score', sentiment.get('compound', 0.5))
                # Convert -1 to 1 scale to 0-100
                if -1 <= score <= 1:
                    score = (score + 1) * 50
                sentiments.append(score)
            elif isinstance(sentiment, (int, float)):
                sentiments.append(float(sentiment))
                
        if sentiments:
            return sum(sentiments) / len(sentiments)
        return 50.0
        
    def calculate_all_indicators(
        self,
        articles: List[Dict[str, Any]],
        category_filter: Optional[str] = None
    ) -> List[IndicatorValue]:
        """
        Calculate all indicators from a list of articles.
        
        Args:
            articles: List of processed articles
            category_filter: Optional PESTEL category to filter
            
        Returns:
            List of calculated indicator values
        """
        results = []
        
        if not self.indicators:
            logger.warning("No indicators loaded")
            return results
        
        # Filter indicators if needed
        indicators = self.indicators
        if category_filter:
            indicators = [i for i in indicators if i.pestel_category == category_filter]
            
        logger.info(f"Calculating {len(indicators)} indicators from {len(articles)} articles")
        
        for indicator in indicators:
            # Find matching articles
            matching = []
            scores = []
            
            for article in articles:
                score = self._match_article_to_indicator(article, indicator)
                if score > 0.3:  # Threshold for matching
                    matching.append(article)
                    scores.append(score)
                    
            # Calculate value based on calculation type
            if indicator.calculation_type == 'frequency_count':
                value = self._calculate_frequency_indicator(matching, indicator)
            elif indicator.calculation_type == 'sentiment_aggregate':
                value = self._calculate_sentiment_indicator(matching, indicator)
            else:
                # Default: frequency-based
                value = self._calculate_frequency_indicator(matching, indicator)
                
            # Calculate confidence based on article count and match quality
            if matching:
                avg_score = sum(scores) / len(scores)
                confidence = min(1.0, (len(matching) / 5) * avg_score)
            else:
                confidence = 0.0
                
            results.append(IndicatorValue(
                indicator_id=indicator.indicator_id,
                indicator_name=indicator.indicator_name,
                pestel_category=indicator.pestel_category,
                subcategory=indicator.subcategory,
                value=round(value, 1),
                confidence=round(confidence, 2),
                article_count=len(matching),
                matching_articles=[a.get('article_id', str(a.get('_id', 'unknown'))) for a in matching[:5]],
                calculation_type=indicator.calculation_type
            ))
            
        return results
        
    def calculate_composite_scores(
        self,
        indicator_values: List[IndicatorValue]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate composite scores for each PESTEL category.
        
        Returns:
            Dict with category composites and overall NAI
        """
        # Group by category
        by_category = defaultdict(list)
        for iv in indicator_values:
            by_category[iv.pestel_category].append(iv)
            
        composites = {}
        total_weighted_value = 0.0
        total_weight = 0.0
        
        # Category weights (from blueprint)
        category_weights = {
            'Political': 1.0,
            'Economic': 1.2,  # Economic has higher weight
            'Social': 1.0,
            'Technological': 0.8,
            'Environmental': 0.9,
            'Legal': 0.9
        }
        
        for category, values in by_category.items():
            if not values:
                continue
                
            # Weighted average by confidence
            weighted_sum = 0.0
            weight_sum = 0.0
            
            for iv in values:
                weight = iv.confidence if iv.confidence > 0 else 0.1
                weighted_sum += iv.value * weight
                weight_sum += weight
                
            if weight_sum > 0:
                composite_value = weighted_sum / weight_sum
            else:
                composite_value = 50.0
                
            # Count active indicators (with articles)
            active_count = sum(1 for iv in values if iv.article_count > 0)
            
            composites[category] = {
                'composite_score': round(composite_value, 1),
                'total_indicators': len(values),
                'active_indicators': active_count,
                'avg_confidence': round(sum(iv.confidence for iv in values) / len(values), 2) if values else 0,
                'total_articles': sum(iv.article_count for iv in values)
            }
            
            # Contribute to NAI
            cat_weight = category_weights.get(category, 1.0)
            total_weighted_value += composite_value * cat_weight
            total_weight += cat_weight
            
        # Calculate National Activity Index (NAI)
        nai = total_weighted_value / total_weight if total_weight > 0 else 50.0
        
        composites['NATIONAL_ACTIVITY_INDEX'] = {
            'value': round(nai, 1),
            'interpretation': self._interpret_nai(nai),
            'total_categories': len(by_category),
            'total_indicators': len(indicator_values),
            'indicators_with_data': sum(1 for iv in indicator_values if iv.article_count > 0)
        }
        
        return composites
        
    def _interpret_nai(self, nai: float) -> str:
        """Interpret the National Activity Index value."""
        if nai >= 80:
            return "Very High Activity - Strong positive indicators across all dimensions"
        elif nai >= 65:
            return "High Activity - Positive momentum in most areas"
        elif nai >= 55:
            return "Moderate Activity - Mixed signals, slightly positive"
        elif nai >= 45:
            return "Neutral Activity - Balanced positive and negative indicators"
        elif nai >= 35:
            return "Low Activity - Slight negative trend"
        elif nai >= 20:
            return "Declining Activity - Significant negative indicators"
        else:
            return "Critical - Major concerns across multiple dimensions"
            
    def generate_summary_report(
        self,
        indicator_values: List[IndicatorValue],
        composites: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        
        # Group indicators by category and subcategory
        by_category = defaultdict(lambda: defaultdict(list))
        for iv in indicator_values:
            by_category[iv.pestel_category][iv.subcategory].append({
                'name': iv.indicator_name,
                'value': iv.value,
                'confidence': iv.confidence,
                'articles': iv.article_count
            })
            
        # Find top indicators (highest values)
        sorted_indicators = sorted(indicator_values, key=lambda x: x.value, reverse=True)
        top_indicators = [
            {
                'name': iv.indicator_name,
                'category': iv.pestel_category,
                'value': iv.value,
                'articles': iv.article_count
            }
            for iv in sorted_indicators[:10]
        ]
        
        # Find concerning indicators (low values with data)
        concerning = [
            {
                'name': iv.indicator_name,
                'category': iv.pestel_category,
                'value': iv.value,
                'articles': iv.article_count
            }
            for iv in indicator_values
            if iv.article_count > 0 and iv.value < 40
        ][:10]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'national_activity_index': composites.get('NATIONAL_ACTIVITY_INDEX', {}),
            'category_composites': {k: v for k, v in composites.items() if k != 'NATIONAL_ACTIVITY_INDEX'},
            'indicators_by_category': {
                cat: {
                    'subcategories': dict(subcats),
                    'total_indicators': sum(len(inds) for inds in subcats.values()),
                    'composite_score': composites.get(cat, {}).get('composite_score', 50.0)
                }
                for cat, subcats in by_category.items()
            },
            'top_indicators': top_indicators,
            'concerning_indicators': concerning,
            'summary_stats': {
                'total_indicators': len(indicator_values),
                'indicators_with_data': sum(1 for iv in indicator_values if iv.article_count > 0),
                'avg_confidence': round(sum(iv.confidence for iv in indicator_values) / len(indicator_values), 2) if indicator_values else 0,
                'total_article_matches': sum(iv.article_count for iv in indicator_values)
            }
        }


# Factory function
def create_full_indicator_calculator(pg_config: Optional[Dict[str, Any]] = None) -> FullIndicatorCalculator:
    """Create and return a FullIndicatorCalculator instance."""
    return FullIndicatorCalculator(pg_config)
