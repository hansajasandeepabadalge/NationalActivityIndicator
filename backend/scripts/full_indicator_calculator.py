"""
Full Layer 2 Indicator Calculation System.

This module provides a comprehensive indicator calculation service that:
1. Loads all 105 indicator definitions from PostgreSQL
2. Matches articles to indicators based on keywords
3. Calculates indicator values using appropriate calculation types
4. Generates composite PESTEL scores
5. Calculates the National Activity Index (NAI)
"""

import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extras import RealDictCursor


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


class FullIndicatorCalculator:
    """
    Comprehensive indicator calculator that uses all 105 indicators.
    """
    
    def __init__(self, pg_config: Optional[Dict[str, Any]] = None):
        """Initialize with PostgreSQL connection."""
        self.pg_config = pg_config or {
            'host': 'localhost',
            'port': 15432,
            'dbname': 'national_indicator',
            'user': 'postgres',
            'password': 'postgres_secure_2024'
        }
        self.indicators: List[IndicatorDefinition] = []
        self._load_indicators()
        
    def _load_indicators(self):
        """Load all indicator definitions from PostgreSQL."""
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
        
        print(f"Loaded {len(self.indicators)} indicator definitions")
        
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
        # More articles = higher value
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
            if isinstance(sentiment, dict):
                score = sentiment.get('score', 0.5)
                # Convert -1 to 1 scale to 0-100
                if score >= -1 and score <= 1:
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
        
        # Filter indicators if needed
        indicators = self.indicators
        if category_filter:
            indicators = [i for i in indicators if i.pestel_category == category_filter]
            
        print(f"\nCalculating {len(indicators)} indicators from {len(articles)} articles...")
        
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
                matching_articles=[a.get('article_id', 'unknown') for a in matching[:5]],
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


def main():
    """Test the full indicator calculation system."""
    from pymongo import MongoClient
    from dotenv import load_dotenv
    
    load_dotenv()
    
    print("=" * 70)
    print(" FULL LAYER 2 INDICATOR CALCULATION TEST")
    print("=" * 70)
    
    # Fetch articles from MongoDB
    print("\n1. Fetching articles from MongoDB...")
    client = MongoClient("mongodb://admin:mongo_secure_2024@localhost:27017/")
    db = client["national_indicator"]
    
    articles = list(db.processed_articles.find().limit(100))
    
    # Transform to required format
    processed_articles = []
    for article in articles:
        content = article.get("content", {})
        body = content.get("body_translated", "") or content.get("body_original", "")
        title = content.get("title_translated", "") or content.get("title_original", "")
        
        if body or title:
            processed_articles.append({
                "article_id": article.get("article_id", str(article.get("_id"))),
                "title": title,
                "body": body,
                "sentiment": article.get("nlp_features", {}).get("sentiment", {})
            })
    
    client.close()
    print(f"   Loaded {len(processed_articles)} articles with content")
    
    # Initialize calculator
    print("\n2. Initializing Full Indicator Calculator...")
    calculator = FullIndicatorCalculator()
    
    # Calculate all indicators
    print("\n3. Calculating indicators...")
    indicator_values = calculator.calculate_all_indicators(processed_articles)
    
    # Calculate composites
    print("\n4. Calculating composite scores...")
    composites = calculator.calculate_composite_scores(indicator_values)
    
    # Generate report
    print("\n5. Generating summary report...")
    report = calculator.generate_summary_report(indicator_values, composites)
    
    # Print results
    print("\n" + "=" * 70)
    print(" RESULTS")
    print("=" * 70)
    
    # NAI
    nai = report['national_activity_index']
    print(f"\n🏆 NATIONAL ACTIVITY INDEX: {nai.get('value', 'N/A')}/100")
    print(f"   {nai.get('interpretation', '')}")
    print(f"   Total indicators: {nai.get('total_indicators', 0)}")
    print(f"   With data: {nai.get('indicators_with_data', 0)}")
    
    # Category composites
    print("\n📊 CATEGORY COMPOSITE SCORES:")
    for cat, data in report['category_composites'].items():
        score = data.get('composite_score', 50)
        active = data.get('active_indicators', 0)
        total = data.get('total_indicators', 0)
        articles = data.get('total_articles', 0)
        print(f"   {cat}: {score:.1f}/100 ({active}/{total} active, {articles} articles)")
    
    # Top indicators
    print("\n📈 TOP 10 INDICATORS:")
    for i, ind in enumerate(report['top_indicators'][:10], 1):
        print(f"   {i}. {ind['name']} ({ind['category']}): {ind['value']:.1f} ({ind['articles']} articles)")
    
    # Concerning indicators
    if report['concerning_indicators']:
        print("\n⚠️ CONCERNING INDICATORS (value < 40):")
        for ind in report['concerning_indicators'][:5]:
            print(f"   - {ind['name']} ({ind['category']}): {ind['value']:.1f}")
    
    # Summary
    stats = report['summary_stats']
    print(f"\n📋 SUMMARY:")
    print(f"   Total indicators defined: {stats['total_indicators']}")
    print(f"   Indicators with data: {stats['indicators_with_data']}")
    print(f"   Average confidence: {stats['avg_confidence']}")
    print(f"   Total article matches: {stats['total_article_matches']}")
    
    # Save report
    report_path = os.path.join(os.path.dirname(__file__), 'indicator_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n💾 Full report saved to: {report_path}")
    
    print("\n" + "=" * 70)
    print(" TEST COMPLETE")
    print("=" * 70)
    
    return report


if __name__ == "__main__":
    main()
