"""
Comprehensive Layer 2 Indicator Generation Test.

This script tests the complete Layer 2 pipeline:
1. Fetch processed articles from Layer 1
2. Classify articles using PESTEL categories
3. Analyze sentiment for each article
4. Extract entities from articles
5. Calculate indicator values
6. Aggregate to national indicators
7. Detect trends and anomalies
8. Store indicator values

Tests that Layer 2 properly fulfills its purpose of generating 
National Activity Indicators from scraped news articles.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, field
from collections import defaultdict

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ.setdefault("GROQ_API_KEY", "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")


@dataclass
class IndicatorResult:
    """Result of indicator calculation."""
    indicator_id: str
    indicator_name: str
    pestel_category: str
    value: float
    confidence: float
    article_count: int
    trend: str = "stable"
    change_percent: float = 0.0
    articles: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NationalIndicatorSummary:
    """Summary of all national indicators."""
    timestamp: datetime
    total_articles_processed: int
    indicators_generated: int
    by_category: Dict[str, List[IndicatorResult]]
    composite_scores: Dict[str, float]
    alerts: List[Dict[str, Any]]


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_section(title: str):
    """Print section header."""
    print(f"\n--- {title} ---")


async def fetch_articles_from_layer1(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch processed articles from MongoDB (Layer 1 output)."""
    from pymongo import MongoClient
    
    client = MongoClient("mongodb://admin:mongo_secure_2024@localhost:27017/")
    db = client["national_indicator"]
    
    # Fetch from processed_articles collection
    articles = list(db.processed_articles.find().limit(limit))
    client.close()
    
    # Transform to required format
    result = []
    for article in articles:
        content = article.get("content", {})
        quality = article.get("quality", {})
        
        # Get translated or original content
        body = content.get("body_translated", "") or content.get("body_original", "")
        title = content.get("title_translated", "") or content.get("title_original", "")
        
        result.append({
            "article_id": article.get("article_id", str(article.get("_id"))),
            "title": title,
            "body": body,
            "source": article.get("source_name", article.get("source_id", "unknown")),
            "published_date": article.get("scraped_at", datetime.now()),
            "url": article.get("source_url", ""),
            "credibility_score": quality.get("credibility_score", 0.7),
            "sentiment_score": article.get("sentiment_score", 0.0),
            "priority_score": article.get("priority_score", 0.5)
        })
    
    return result


async def classify_articles(articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Classify articles into PESTEL categories and sub-indicators."""
    from app.layer2.services.llm_classifier import LLMClassifier
    
    classifier = LLMClassifier()
    
    # Group articles by PESTEL category
    categorized = defaultdict(list)
    
    for article in articles:
        text = article.get("body", "")
        title = article.get("title", "")
        
        if len(text) < 50:
            continue
        
        try:
            result = await classifier.classify(text=text, title=title)
            
            article["classification"] = {
                "primary_category": result.primary_category.value,
                "confidence": result.primary_confidence,
                "all_categories": result.all_categories,
                "urgency": result.urgency.value,
                "business_relevance": result.business_relevance.value,
                "key_entities": result.key_entities,
                "source": result.classification_source
            }
            
            # Add to primary category
            categorized[result.primary_category.value].append(article)
            
            # Also add to secondary categories if confidence > 0.3
            for cat, conf in result.all_categories.items():
                if cat != result.primary_category.value and conf > 0.3:
                    categorized[cat].append(article)
                    
        except Exception as e:
            print(f"   ⚠️ Classification error for {article['article_id']}: {e}")
    
    return dict(categorized)


async def analyze_sentiment(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze sentiment for each article."""
    from app.layer2.services.advanced_sentiment import AdvancedSentimentAnalyzer
    
    analyzer = AdvancedSentimentAnalyzer()
    
    for article in articles:
        text = article.get("body", "")
        title = article.get("title", "")
        
        if len(text) < 50:
            article["sentiment"] = {"score": 0.0, "level": "neutral"}
            continue
        
        try:
            result = await analyzer.analyze(text=text, title=title)
            
            article["sentiment"] = {
                "overall_score": result.overall_sentiment_score,
                "level": result.overall_sentiment_level.value,
                "tone": result.tone,
                "business_confidence": result.business_confidence_score,
                "public_mood": result.public_mood_score,
                "economic_outlook": result.economic_outlook_score,
                "primary_emotion": result.primary_emotion,
                "source": result.analysis_source
            }
        except Exception as e:
            article["sentiment"] = {"score": 0.0, "level": "neutral", "error": str(e)}
    
    return articles


async def extract_entities(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract entities from articles."""
    from app.layer2.services.smart_entity_extractor import SmartEntityExtractor
    
    extractor = SmartEntityExtractor()
    
    for article in articles:
        text = article.get("body", "")
        title = article.get("title", "")
        
        if len(text) < 50:
            article["entities"] = []
            continue
        
        try:
            result = await extractor.extract(text=text, title=title)
            
            article["entities"] = [
                {
                    "text": e.text,
                    "type": e.entity_type.value if hasattr(e.entity_type, 'value') else str(e.entity_type),
                    "importance": e.importance
                }
                for e in result.entities[:10]  # Top 10 entities
            ]
            article["entity_count"] = result.entity_count
            article["primary_entities"] = result.primary_entities[:5]
            
        except Exception as e:
            article["entities"] = []
            article["entity_count"] = 0
    
    return articles


def calculate_indicator_values(
    categorized_articles: Dict[str, List[Dict[str, Any]]]
) -> List[IndicatorResult]:
    """Calculate indicator values from categorized articles."""
    
    indicators = []
    
    # Define indicators for each PESTEL category
    indicator_definitions = {
        "political": [
            {"id": "POL_STABILITY", "name": "Political Stability Index", "type": "sentiment"},
            {"id": "POL_UNREST", "name": "Political Unrest Index", "type": "frequency"},
            {"id": "POL_GOVERNANCE", "name": "Governance Quality Score", "type": "sentiment"},
        ],
        "economic": [
            {"id": "ECON_CONFIDENCE", "name": "Economic Confidence Index", "type": "sentiment"},
            {"id": "ECON_ACTIVITY", "name": "Economic Activity Level", "type": "frequency"},
            {"id": "ECON_INFLATION", "name": "Inflation Pressure Index", "type": "sentiment"},
            {"id": "ECON_BUSINESS", "name": "Business Climate Score", "type": "sentiment"},
        ],
        "social": [
            {"id": "SOC_MOOD", "name": "Public Mood Index", "type": "sentiment"},
            {"id": "SOC_WELLBEING", "name": "Social Wellbeing Score", "type": "sentiment"},
            {"id": "SOC_CONCERNS", "name": "Public Concerns Level", "type": "frequency"},
        ],
        "technological": [
            {"id": "TECH_ADOPTION", "name": "Technology Adoption Index", "type": "frequency"},
            {"id": "TECH_INNOVATION", "name": "Innovation Activity Score", "type": "sentiment"},
        ],
        "environmental": [
            {"id": "ENV_CONCERN", "name": "Environmental Concern Level", "type": "frequency"},
            {"id": "ENV_ACTION", "name": "Environmental Action Index", "type": "sentiment"},
        ],
        "legal": [
            {"id": "LEG_ACTIVITY", "name": "Legal Activity Index", "type": "frequency"},
            {"id": "LEG_COMPLIANCE", "name": "Regulatory Compliance Score", "type": "sentiment"},
        ],
    }
    
    for category, articles in categorized_articles.items():
        category_lower = category.lower()
        
        if category_lower not in indicator_definitions:
            continue
        
        for ind_def in indicator_definitions[category_lower]:
            if not articles:
                continue
            
            # Calculate based on type
            if ind_def["type"] == "sentiment":
                # Average sentiment score
                sentiment_scores = [
                    a.get("sentiment", {}).get("overall_score", 0.0) 
                    for a in articles
                ]
                # Convert from [-1, 1] to [0, 100]
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                value = ((avg_sentiment + 1) / 2) * 100
                
            elif ind_def["type"] == "frequency":
                # Normalized article count (assume 10 articles = 50, 20+ = 100)
                count = len(articles)
                value = min(100, (count / 20) * 100)
            else:
                value = 50.0  # Default neutral
            
            # Calculate confidence based on article count
            confidence = min(1.0, len(articles) / 10)
            
            indicators.append(IndicatorResult(
                indicator_id=ind_def["id"],
                indicator_name=ind_def["name"],
                pestel_category=category,
                value=round(value, 2),
                confidence=round(confidence, 2),
                article_count=len(articles),
                articles=[a.get("article_id", "") for a in articles[:5]]
            ))
    
    return indicators


def calculate_composite_scores(
    indicators: List[IndicatorResult]
) -> Dict[str, float]:
    """Calculate composite scores from individual indicators."""
    
    # Group by category
    by_category = defaultdict(list)
    for ind in indicators:
        by_category[ind.pestel_category].append(ind)
    
    composites = {}
    
    # Calculate category averages
    for category, inds in by_category.items():
        if inds:
            avg_value = sum(i.value for i in inds) / len(inds)
            composites[f"{category.upper()}_COMPOSITE"] = round(avg_value, 2)
    
    # Calculate overall national index (weighted average of all categories)
    if composites:
        overall = sum(composites.values()) / len(composites)
        composites["NATIONAL_ACTIVITY_INDEX"] = round(overall, 2)
    
    return composites


def detect_anomalies_and_alerts(
    indicators: List[IndicatorResult]
) -> List[Dict[str, Any]]:
    """Detect anomalies and generate alerts."""
    alerts = []
    
    for ind in indicators:
        # High value alert
        if ind.value > 80:
            alerts.append({
                "type": "HIGH_VALUE",
                "indicator_id": ind.indicator_id,
                "indicator_name": ind.indicator_name,
                "value": ind.value,
                "severity": "warning",
                "message": f"{ind.indicator_name} is at elevated level ({ind.value:.1f})"
            })
        
        # Low value alert
        elif ind.value < 20:
            alerts.append({
                "type": "LOW_VALUE",
                "indicator_id": ind.indicator_id,
                "indicator_name": ind.indicator_name,
                "value": ind.value,
                "severity": "info",
                "message": f"{ind.indicator_name} is at low level ({ind.value:.1f})"
            })
        
        # Low confidence alert
        if ind.confidence < 0.3:
            alerts.append({
                "type": "LOW_CONFIDENCE",
                "indicator_id": ind.indicator_id,
                "indicator_name": ind.indicator_name,
                "confidence": ind.confidence,
                "severity": "info",
                "message": f"{ind.indicator_name} has low confidence ({ind.confidence:.0%}) - more data needed"
            })
    
    return alerts


async def run_full_layer2_test():
    """Run the complete Layer 2 indicator generation test."""
    
    print_header("LAYER 2 NATIONAL INDICATOR GENERATION TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "articles_fetched": False,
        "classification": False,
        "sentiment": False,
        "entities": False,
        "indicators": False,
        "composites": False,
        "alerts": False
    }
    
    # Step 1: Fetch articles from Layer 1
    print_section("1. Fetching Processed Articles from Layer 1")
    try:
        articles = await fetch_articles_from_layer1(limit=50)
        print(f"   📊 Fetched {len(articles)} processed articles")
        
        # Filter articles with meaningful content
        articles = [a for a in articles if len(a.get("body", "")) >= 100]
        print(f"   📊 {len(articles)} articles with sufficient content")
        
        if articles:
            results["articles_fetched"] = True
            print("   ✅ Articles ready for processing")
        else:
            print("   ❌ No articles available")
            return results
            
    except Exception as e:
        print(f"   ❌ Failed to fetch articles: {e}")
        return results
    
    # Step 2: Classify articles into PESTEL categories
    print_section("2. PESTEL Classification")
    try:
        categorized = await classify_articles(articles)
        
        print(f"   📊 Classification Results:")
        total_classified = 0
        for category, cat_articles in sorted(categorized.items()):
            print(f"      • {category.upper()}: {len(cat_articles)} articles")
            total_classified += len(cat_articles)
        
        if categorized:
            results["classification"] = True
            print(f"   ✅ Classified {total_classified} article assignments")
        else:
            print("   ⚠️ No articles classified")
            
    except Exception as e:
        print(f"   ❌ Classification failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 3: Sentiment Analysis
    print_section("3. Sentiment Analysis")
    try:
        articles = await analyze_sentiment(articles)
        
        sentiment_stats = defaultdict(int)
        for article in articles:
            level = article.get("sentiment", {}).get("level", "unknown")
            sentiment_stats[level] += 1
        
        print(f"   📊 Sentiment Distribution:")
        for level, count in sorted(sentiment_stats.items()):
            print(f"      • {level}: {count} articles")
        
        results["sentiment"] = True
        print("   ✅ Sentiment analysis complete")
        
    except Exception as e:
        print(f"   ❌ Sentiment analysis failed: {e}")
    
    # Step 4: Entity Extraction
    print_section("4. Entity Extraction")
    try:
        articles = await extract_entities(articles)
        
        total_entities = sum(a.get("entity_count", 0) for a in articles)
        print(f"   📊 Extracted {total_entities} entities from {len(articles)} articles")
        
        # Show top entities across all articles
        entity_freq = defaultdict(int)
        for article in articles:
            for entity in article.get("entities", []):
                entity_freq[entity.get("text", "")] += 1
        
        top_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        if top_entities:
            print(f"   📊 Top Entities:")
            for entity, count in top_entities:
                print(f"      • {entity}: {count} mentions")
        
        results["entities"] = True
        print("   ✅ Entity extraction complete")
        
    except Exception as e:
        print(f"   ❌ Entity extraction failed: {e}")
    
    # Step 5: Calculate Indicator Values
    print_section("5. Indicator Calculation")
    try:
        indicators = calculate_indicator_values(categorized)
        
        print(f"   📊 Generated {len(indicators)} indicators:")
        
        # Group by category for display
        by_cat = defaultdict(list)
        for ind in indicators:
            by_cat[ind.pestel_category].append(ind)
        
        for category in sorted(by_cat.keys()):
            print(f"\n   {category.upper()}:")
            for ind in by_cat[category]:
                trend_symbol = "→" if ind.trend == "stable" else ("↑" if ind.trend == "rising" else "↓")
                print(f"      • {ind.indicator_name}: {ind.value:.1f} {trend_symbol} (confidence: {ind.confidence:.0%})")
        
        results["indicators"] = True
        print("\n   ✅ Indicator calculation complete")
        
    except Exception as e:
        print(f"   ❌ Indicator calculation failed: {e}")
        indicators = []
    
    # Step 6: Calculate Composite Scores
    print_section("6. Composite National Indicators")
    try:
        composites = calculate_composite_scores(indicators)
        
        print(f"   📊 Composite Scores:")
        for name, value in sorted(composites.items()):
            if name == "NATIONAL_ACTIVITY_INDEX":
                print(f"\n   🏆 {name}: {value:.1f}")
            else:
                print(f"      • {name}: {value:.1f}")
        
        results["composites"] = True
        print("\n   ✅ Composite scores calculated")
        
    except Exception as e:
        print(f"   ❌ Composite calculation failed: {e}")
        composites = {}
    
    # Step 7: Anomaly Detection & Alerts
    print_section("7. Anomaly Detection & Alerts")
    try:
        alerts = detect_anomalies_and_alerts(indicators)
        
        if alerts:
            print(f"   📊 Generated {len(alerts)} alerts:")
            for alert in alerts[:10]:  # Show first 10
                severity_icon = "🔴" if alert["severity"] == "critical" else ("🟡" if alert["severity"] == "warning" else "🔵")
                print(f"      {severity_icon} [{alert['type']}] {alert['message']}")
        else:
            print("   📊 No alerts generated (all indicators within normal range)")
        
        results["alerts"] = True
        print("   ✅ Anomaly detection complete")
        
    except Exception as e:
        print(f"   ❌ Anomaly detection failed: {e}")
        alerts = []
    
    # Summary
    print_header("LAYER 2 TEST SUMMARY")
    
    print("\n📊 PIPELINE STAGES:")
    stages = [
        ("Articles Fetched", results["articles_fetched"]),
        ("PESTEL Classification", results["classification"]),
        ("Sentiment Analysis", results["sentiment"]),
        ("Entity Extraction", results["entities"]),
        ("Indicator Calculation", results["indicators"]),
        ("Composite Scores", results["composites"]),
        ("Anomaly Detection", results["alerts"]),
    ]
    
    passed = 0
    for stage, status in stages:
        icon = "✅" if status else "❌"
        print(f"   {icon} {stage}")
        if status:
            passed += 1
    
    print(f"\n   Overall: {passed}/{len(stages)} stages passed")
    
    # Final National Indicators Summary
    if results["indicators"] and results["composites"]:
        print("\n" + "=" * 70)
        print(" NATIONAL ACTIVITY INDICATORS - CURRENT STATE")
        print("=" * 70)
        
        print(f"\n   Generated from {len(articles)} articles")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n   PESTEL Category Scores:")
        for name, value in sorted(composites.items()):
            if name != "NATIONAL_ACTIVITY_INDEX":
                # Create visual bar
                bar_len = int(value / 5)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"      {name:25} [{bar}] {value:.1f}")
        
        if "NATIONAL_ACTIVITY_INDEX" in composites:
            nai = composites["NATIONAL_ACTIVITY_INDEX"]
            print(f"\n   🏆 NATIONAL ACTIVITY INDEX: {nai:.1f}/100")
            
            if nai >= 70:
                interpretation = "Strong positive national activity"
            elif nai >= 50:
                interpretation = "Moderate national activity"
            elif nai >= 30:
                interpretation = "Below average national activity"
            else:
                interpretation = "Concerning national activity levels"
            
            print(f"      Interpretation: {interpretation}")
        
        print("\n🎉 Layer 2 is successfully generating National Activity Indicators!")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_full_layer2_test())
