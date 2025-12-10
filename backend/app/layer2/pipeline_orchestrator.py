"""
Layer 2 Complete Pipeline Orchestrator

This module provides end-to-end integration for Layer 2:
1. Fetch processed articles from Layer 1 (MongoDB)
2. Run PESTEL classification
3. Perform sentiment analysis
4. Extract entities
5. Calculate indicator values (all 105 indicators)
6. Generate composite scores and National Activity Index
7. Store results in MongoDB and PostgreSQL
8. Produce Layer2Output contract for Layer 3

This is the MAIN ENTRY POINT for Layer 2 processing.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import psycopg2
from psycopg2.extras import RealDictCursor

# Layer 2 imports
from app.layer2.data_ingestion.mongodb_loader import MongoDBArticleLoader, Layer2Article
from app.layer2.services.enhanced_pipeline import (
    EnhancedPipeline,
    PipelineConfig,
    EnhancedProcessingResult,
    create_enhanced_pipeline
)
from app.layer2.indicators.full_indicator_calculator import (
    FullIndicatorCalculator,
    IndicatorValue,
    create_full_indicator_calculator
)

# Integration contracts
from app.integration.contracts import (
    Layer2Output,
    IndicatorValueOutput,
    IndicatorTrendOutput,
    IndicatorEventOutput,
    PESTELCategory,
    TrendDirection,
    SeverityLevel
)

logger = logging.getLogger(__name__)


@dataclass
class PipelineStageResult:
    """Result from a pipeline stage."""
    stage_name: str
    success: bool
    item_count: int
    duration_ms: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Layer2PipelineResult:
    """Complete result from Layer 2 pipeline."""
    success: bool
    timestamp: datetime
    stages: List[PipelineStageResult]
    total_duration_ms: float
    articles_processed: int
    indicators_calculated: int
    layer2_output: Optional[Layer2Output] = None
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'timestamp': self.timestamp.isoformat(),
            'stages': [asdict(s) for s in self.stages],
            'total_duration_ms': self.total_duration_ms,
            'articles_processed': self.articles_processed,
            'indicators_calculated': self.indicators_calculated,
            'layer2_output': self.layer2_output.model_dump() if self.layer2_output else None,
            'errors': self.errors
        }


class Layer2PipelineOrchestrator:
    """
    Main orchestrator for Layer 2 processing pipeline.
    
    Coordinates all Layer 2 services to transform Layer 1 articles
    into National Activity Indicators for Layer 3.
    """
    
    def __init__(
        self,
        mongo_url: str = "mongodb://admin:mongo_secure_2024@localhost:27017/",
        mongo_db: str = "national_indicator",
        pg_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the pipeline orchestrator."""
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db
        self.pg_config = pg_config or {
            'host': 'localhost',
            'port': 15432,
            'dbname': 'national_indicator',
            'user': 'postgres',
            'password': 'postgres_secure_2024'
        }
        
        # Initialize components lazily
        self._mongodb_loader: Optional[MongoDBArticleLoader] = None
        self._enhanced_pipeline: Optional[EnhancedPipeline] = None
        self._indicator_calculator: Optional[FullIndicatorCalculator] = None
        self._mongo_client: Optional[MongoClient] = None
        
    async def _init_components(self):
        """Initialize all pipeline components."""
        # MongoDB Loader
        if not self._mongodb_loader:
            self._mongodb_loader = MongoDBArticleLoader(
                mongo_url=self.mongo_url,
                database_name=self.mongo_db
            )
            await self._mongodb_loader.connect()
            
        # Sync MongoDB client for storage
        if not self._mongo_client:
            self._mongo_client = MongoClient(self.mongo_url)
            
        # Enhanced processing pipeline
        if not self._enhanced_pipeline:
            try:
                from app.layer2.services.enhanced_pipeline import create_enhanced_pipeline
                self._enhanced_pipeline = create_enhanced_pipeline(PipelineConfig())
            except Exception as e:
                logger.warning(f"Enhanced pipeline not available: {e}")
                
        # Full indicator calculator
        if not self._indicator_calculator:
            self._indicator_calculator = create_full_indicator_calculator(self.pg_config)
            
    async def run_full_pipeline(
        self,
        article_limit: int = 100,
        time_window_hours: int = 24,
        store_results: bool = True
    ) -> Layer2PipelineResult:
        """
        Run the complete Layer 2 pipeline.
        
        Args:
            article_limit: Maximum articles to process
            time_window_hours: Time window for indicator calculation
            store_results: Whether to store results in databases
            
        Returns:
            Complete pipeline result with Layer2Output for Layer 3
        """
        start_time = datetime.now()
        stages: List[PipelineStageResult] = []
        errors: List[str] = []
        
        try:
            # Initialize components
            await self._init_components()
            
            # ================================================================
            # STAGE 1: Fetch Articles from Layer 1
            # ================================================================
            stage_start = datetime.now()
            articles = await self._stage_fetch_articles(article_limit)
            stages.append(PipelineStageResult(
                stage_name="1_fetch_articles",
                success=len(articles) > 0,
                item_count=len(articles),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={"source": "MongoDB processed_articles"}
            ))
            
            if not articles:
                return Layer2PipelineResult(
                    success=False,
                    timestamp=start_time,
                    stages=stages,
                    total_duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    articles_processed=0,
                    indicators_calculated=0,
                    errors=["No articles found for processing"]
                )
            
            # ================================================================
            # STAGE 2: PESTEL Classification
            # ================================================================
            stage_start = datetime.now()
            classified_articles = await self._stage_classify_articles(articles)
            stages.append(PipelineStageResult(
                stage_name="2_pestel_classification",
                success=len(classified_articles) > 0,
                item_count=len(classified_articles),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={"method": "LLM + fallback"}
            ))
            
            # ================================================================
            # STAGE 3: Sentiment Analysis
            # ================================================================
            stage_start = datetime.now()
            articles_with_sentiment = await self._stage_sentiment_analysis(classified_articles)
            stages.append(PipelineStageResult(
                stage_name="3_sentiment_analysis",
                success=True,
                item_count=len(articles_with_sentiment),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={"method": "VADER + fallback"}
            ))
            
            # ================================================================
            # STAGE 4: Entity Extraction
            # ================================================================
            stage_start = datetime.now()
            articles_with_entities = await self._stage_entity_extraction(articles_with_sentiment)
            entity_count = sum(len(a.get('entities', [])) for a in articles_with_entities)
            stages.append(PipelineStageResult(
                stage_name="4_entity_extraction",
                success=True,
                item_count=entity_count,
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={"method": "spaCy NER"}
            ))
            
            # ================================================================
            # STAGE 5: Indicator Calculation (All 105 Indicators)
            # ================================================================
            stage_start = datetime.now()
            indicator_values = self._stage_calculate_indicators(articles_with_entities)
            active_indicators = sum(1 for iv in indicator_values if iv.article_count > 0)
            stages.append(PipelineStageResult(
                stage_name="5_indicator_calculation",
                success=len(indicator_values) > 0,
                item_count=len(indicator_values),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={
                    "total_indicators": len(indicator_values),
                    "active_indicators": active_indicators
                }
            ))
            
            # ================================================================
            # STAGE 6: Composite Score Calculation
            # ================================================================
            stage_start = datetime.now()
            composites = self._indicator_calculator.calculate_composite_scores(indicator_values)
            nai = composites.get('NATIONAL_ACTIVITY_INDEX', {})
            stages.append(PipelineStageResult(
                stage_name="6_composite_scores",
                success=bool(composites),
                item_count=len(composites),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={
                    "national_activity_index": nai.get('value', 0),
                    "categories_calculated": len(composites) - 1
                }
            ))
            
            # ================================================================
            # STAGE 7: Build Layer2Output Contract
            # ================================================================
            stage_start = datetime.now()
            layer2_output = self._build_layer2_output(
                indicator_values=indicator_values,
                composites=composites,
                articles=articles_with_entities,
                time_window_hours=time_window_hours
            )
            stages.append(PipelineStageResult(
                stage_name="7_build_layer2_output",
                success=layer2_output is not None,
                item_count=len(layer2_output.indicators) if layer2_output else 0,
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={"output_ready_for_layer3": True}
            ))
            
            # ================================================================
            # STAGE 8: Store Results (Optional)
            # ================================================================
            if store_results:
                stage_start = datetime.now()
                stored_count = await self._stage_store_results(
                    articles=articles_with_entities,
                    indicator_values=indicator_values,
                    composites=composites
                )
                stages.append(PipelineStageResult(
                    stage_name="8_store_results",
                    success=stored_count > 0,
                    item_count=stored_count,
                    duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                    details={"storage": "MongoDB + PostgreSQL"}
                ))
            
            # Calculate total duration
            total_duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return Layer2PipelineResult(
                success=True,
                timestamp=start_time,
                stages=stages,
                total_duration_ms=total_duration,
                articles_processed=len(articles),
                indicators_calculated=len(indicator_values),
                layer2_output=layer2_output,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            errors.append(str(e))
            return Layer2PipelineResult(
                success=False,
                timestamp=start_time,
                stages=stages,
                total_duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                articles_processed=0,
                indicators_calculated=0,
                errors=errors
            )
    
    # ========================================================================
    # PIPELINE STAGES
    # ========================================================================
    
    async def _stage_fetch_articles(self, limit: int) -> List[Dict[str, Any]]:
        """Stage 1: Fetch articles from Layer 1."""
        logger.info(f"Fetching up to {limit} articles from Layer 1...")
        
        try:
            # Try to get unprocessed articles first
            articles = await self._mongodb_loader.get_unprocessed_articles(limit=limit)
            
            # If none found, get all available
            if not articles:
                logger.info("No unprocessed articles, fetching all available...")
                articles = await self._mongodb_loader.get_all_articles(limit=limit)
            
            # Convert to dict format
            result = []
            for article in articles:
                if isinstance(article, Layer2Article):
                    result.append({
                        'article_id': article.article_id,
                        'title': article.title,
                        'body': article.text,
                        'source': article.source,
                        'url': article.url,
                        'published_at': article.published_at,
                        'language': article.language,
                        'layer1_quality_score': article.layer1_quality_score,
                        'layer1_categories': article.layer1_categories,
                        'layer1_entities': article.layer1_entities
                    })
                else:
                    result.append(article)
                    
            logger.info(f"Fetched {len(result)} articles from Layer 1")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return []
    
    async def _stage_classify_articles(
        self, 
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Stage 2: Classify articles into PESTEL categories."""
        logger.info(f"Classifying {len(articles)} articles into PESTEL categories...")
        
        try:
            # Try LLM classifier first
            from app.layer2.services.llm_classifier import create_llm_classifier
            classifier = create_llm_classifier()
            
            for article in articles:
                try:
                    text = f"{article.get('title', '')} {article.get('body', '')}"
                    result = await asyncio.wait_for(
                        classifier.classify(text[:2000]),  # Limit text length
                        timeout=10.0
                    )
                    
                    if result and result.all_categories:
                        # all_categories is a dict of category -> confidence
                        article['pestel_categories'] = list(result.all_categories.keys())
                        article['pestel_confidence'] = list(result.all_categories.values())
                        article['primary_category'] = result.primary_category.value if result.primary_category else 'Economic'
                    else:
                        article['pestel_categories'] = self._fallback_classify(text)
                        article['pestel_confidence'] = [0.5]
                        
                except asyncio.TimeoutError:
                    article['pestel_categories'] = self._fallback_classify(
                        f"{article.get('title', '')} {article.get('body', '')}"
                    )
                    article['pestel_confidence'] = [0.5]
                except Exception as e:
                    logger.warning(f"Classification failed for article: {e}")
                    article['pestel_categories'] = ['Economic']  # Default
                    article['pestel_confidence'] = [0.3]
                    
        except ImportError:
            logger.warning("LLM classifier not available, using fallback")
            for article in articles:
                article['pestel_categories'] = self._fallback_classify(
                    f"{article.get('title', '')} {article.get('body', '')}"
                )
                article['pestel_confidence'] = [0.5]
                
        return articles
    
    def _fallback_classify(self, text: str) -> List[str]:
        """Fallback keyword-based classification."""
        text_lower = text.lower()
        categories = []
        
        keywords = {
            'Political': ['government', 'election', 'policy', 'minister', 'parliament', 'political'],
            'Economic': ['economy', 'gdp', 'inflation', 'market', 'trade', 'business', 'price'],
            'Social': ['people', 'community', 'health', 'education', 'society', 'public'],
            'Technological': ['technology', 'digital', 'internet', 'software', 'innovation'],
            'Environmental': ['environment', 'climate', 'weather', 'pollution', 'disaster'],
            'Legal': ['law', 'court', 'regulation', 'legal', 'justice', 'compliance']
        }
        
        for category, words in keywords.items():
            if any(word in text_lower for word in words):
                categories.append(category)
                
        return categories if categories else ['Economic']
    
    async def _stage_sentiment_analysis(
        self, 
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Stage 3: Analyze sentiment for each article."""
        logger.info(f"Analyzing sentiment for {len(articles)} articles...")
        
        try:
            from app.layer2.nlp.sentiment_analyzer import SentimentAnalyzer
            analyzer = SentimentAnalyzer(backend='vader')
            
            for article in articles:
                try:
                    text = f"{article.get('title', '')} {article.get('body', '')}"
                    result = analyzer.analyze(text)
                    
                    # SentimentResult has: score (-1 to 1), label, confidence, compound
                    article['sentiment'] = {
                        'score': result.score,  # -1 to 1
                        'compound': result.compound,
                        'label': result.label.value if hasattr(result.label, 'value') else str(result.label),
                        'confidence': result.confidence,
                        'positive': result.positive,
                        'negative': result.negative,
                        'neutral': result.neutral
                    }
                except Exception as e:
                    logger.warning(f"Sentiment analysis error: {e}")
                    article['sentiment'] = {'score': 0, 'label': 'neutral', 'confidence': 0.3}
                    
        except ImportError:
            logger.warning("Sentiment analyzer not available, using neutral defaults")
            for article in articles:
                article['sentiment'] = {'score': 0, 'label': 'neutral', 'confidence': 0.3}
                
        return articles
    
    async def _stage_entity_extraction(
        self, 
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Stage 4: Extract named entities from articles."""
        logger.info(f"Extracting entities from {len(articles)} articles...")
        
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            
            for article in articles:
                try:
                    text = f"{article.get('title', '')} {article.get('body', '')}"[:5000]
                    doc = nlp(text)
                    
                    entities = []
                    for ent in doc.ents:
                        entities.append({
                            'text': ent.text,
                            'label': ent.label_,
                            'start': ent.start_char,
                            'end': ent.end_char
                        })
                    article['entities'] = entities
                    
                except Exception as e:
                    article['entities'] = []
                    
        except Exception as e:
            logger.warning(f"Entity extraction not available: {e}")
            for article in articles:
                article['entities'] = []
                
        return articles
    
    def _stage_calculate_indicators(
        self, 
        articles: List[Dict[str, Any]]
    ) -> List[IndicatorValue]:
        """Stage 5: Calculate all 105 indicators."""
        logger.info(f"Calculating indicators from {len(articles)} articles...")
        
        return self._indicator_calculator.calculate_all_indicators(articles)
    
    def _build_layer2_output(
        self,
        indicator_values: List[IndicatorValue],
        composites: Dict[str, Any],
        articles: List[Dict[str, Any]],
        time_window_hours: int
    ) -> Optional[Layer2Output]:
        """Stage 7: Build the Layer2Output contract for Layer 3."""
        logger.info("Building Layer2Output contract...")
        
        try:
            # Build indicator outputs
            indicators_output: Dict[str, IndicatorValueOutput] = {}
            
            for iv in indicator_values:
                # Convert PESTEL category string to enum
                try:
                    pestel_enum = PESTELCategory(iv.pestel_category)
                except ValueError:
                    pestel_enum = PESTELCategory.ECONOMIC
                
                # Get sentiment from matching articles
                sentiment_score = 0.0
                if iv.article_count > 0:
                    # Find matching articles and average sentiment
                    matching_sentiments = []
                    for aid in iv.matching_articles:
                        for art in articles:
                            if art.get('article_id') == aid:
                                sent = art.get('sentiment', {})
                                if isinstance(sent, dict):
                                    matching_sentiments.append(sent.get('score', 0))
                    if matching_sentiments:
                        sentiment_score = sum(matching_sentiments) / len(matching_sentiments)
                
                indicator_key = iv.indicator_name.replace(' ', '_').upper()
                indicators_output[indicator_key] = IndicatorValueOutput(
                    indicator_id=iv.indicator_id,
                    indicator_name=iv.indicator_name,
                    pestel_category=pestel_enum,
                    timestamp=iv.timestamp,
                    value=iv.value,
                    raw_count=iv.article_count,
                    sentiment_score=max(-1, min(1, sentiment_score)),
                    confidence=iv.confidence,
                    source_count=max(1, iv.article_count)
                )
            
            # Build trends (simplified - showing stable for now)
            trends: Dict[str, IndicatorTrendOutput] = {}
            for key, indicator in indicators_output.items():
                trends[key] = IndicatorTrendOutput(
                    indicator_id=indicator.indicator_id,
                    direction=TrendDirection.STABLE,
                    change_percent=0.0,
                    period_days=7
                )
            
            # Calculate overall metrics
            nai = composites.get('NATIONAL_ACTIVITY_INDEX', {})
            activity_level = nai.get('value', 50.0)
            
            # Calculate overall sentiment from all articles
            all_sentiments = [
                a.get('sentiment', {}).get('score', 0) 
                for a in articles 
                if isinstance(a.get('sentiment'), dict)
            ]
            overall_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0.0
            
            # Count unique sources
            unique_sources = len(set(a.get('source', '') for a in articles if a.get('source')))
            
            # Data quality score based on confidence
            avg_confidence = sum(iv.confidence for iv in indicator_values) / len(indicator_values) if indicator_values else 0.5
            
            return Layer2Output(
                timestamp=datetime.now(),
                calculation_window_hours=time_window_hours,
                indicators=indicators_output,
                trends=trends,
                events=[],  # TODO: Implement event detection
                overall_sentiment=max(-1, min(1, overall_sentiment)),
                activity_level=activity_level,
                article_count=len(articles),
                source_diversity=unique_sources,
                data_quality_score=avg_confidence
            )
            
        except Exception as e:
            logger.error(f"Error building Layer2Output: {e}", exc_info=True)
            return None
    
    async def _stage_store_results(
        self,
        articles: List[Dict[str, Any]],
        indicator_values: List[IndicatorValue],
        composites: Dict[str, Any]
    ) -> int:
        """Stage 8: Store results to MongoDB and PostgreSQL."""
        logger.info("Storing results...")
        stored_count = 0
        
        try:
            db = self._mongo_client[self.mongo_db]
            
            # Store indicator calculations
            indicator_docs = []
            for iv in indicator_values:
                indicator_docs.append({
                    'indicator_id': iv.indicator_id,
                    'indicator_name': iv.indicator_name,
                    'pestel_category': iv.pestel_category,
                    'subcategory': iv.subcategory,
                    'value': iv.value,
                    'confidence': iv.confidence,
                    'article_count': iv.article_count,
                    'matching_articles': iv.matching_articles,
                    'calculation_type': iv.calculation_type,
                    'timestamp': iv.timestamp,
                    'created_at': datetime.now()
                })
            
            if indicator_docs:
                result = db.indicator_calculations.insert_many(indicator_docs)
                stored_count += len(result.inserted_ids)
                
            # Store composite scores
            nai = composites.get('NATIONAL_ACTIVITY_INDEX', {})
            composite_doc = {
                'type': 'daily_composite',
                'timestamp': datetime.now(),
                'national_activity_index': nai.get('value', 0),
                'interpretation': nai.get('interpretation', ''),
                'category_scores': {
                    k: v for k, v in composites.items() 
                    if k != 'NATIONAL_ACTIVITY_INDEX'
                },
                'total_articles': len(articles),
                'total_indicators': len(indicator_values)
            }
            db.composite_scores.insert_one(composite_doc)
            stored_count += 1
            
            # Mark articles as processed
            for article in articles:
                await self._mongodb_loader.mark_as_layer2_processed(
                    article.get('article_id', ''),
                    {'processed': True, 'timestamp': datetime.now().isoformat()}
                )
                
            logger.info(f"Stored {stored_count} documents")
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing results: {e}")
            return stored_count


# ============================================================================
# Factory Functions
# ============================================================================

def create_layer2_pipeline(
    mongo_url: str = "mongodb://admin:mongo_secure_2024@localhost:27017/",
    mongo_db: str = "national_indicator"
) -> Layer2PipelineOrchestrator:
    """Create a Layer 2 pipeline orchestrator instance."""
    return Layer2PipelineOrchestrator(mongo_url=mongo_url, mongo_db=mongo_db)


async def run_layer2_pipeline(
    article_limit: int = 100,
    store_results: bool = True
) -> Layer2PipelineResult:
    """
    Convenience function to run the full Layer 2 pipeline.
    
    Usage:
        result = await run_layer2_pipeline(article_limit=50)
        if result.success:
            layer2_output = result.layer2_output
            # Pass to Layer 3
    """
    pipeline = create_layer2_pipeline()
    return await pipeline.run_full_pipeline(
        article_limit=article_limit,
        store_results=store_results
    )


# ============================================================================
# CLI Entry Point
# ============================================================================

async def main():
    """Main entry point for testing."""
    import sys
    
    print("=" * 70)
    print(" LAYER 2 COMPLETE PIPELINE TEST")
    print("=" * 70)
    
    # Parse arguments
    article_limit = 50
    if len(sys.argv) > 1:
        try:
            article_limit = int(sys.argv[1])
        except ValueError:
            pass
    
    print(f"\nRunning pipeline with {article_limit} articles...")
    
    # Run pipeline
    result = await run_layer2_pipeline(
        article_limit=article_limit,
        store_results=True
    )
    
    # Print results
    print("\n" + "=" * 70)
    print(" PIPELINE RESULTS")
    print("=" * 70)
    
    print(f"\n✅ Success: {result.success}")
    print(f"⏱️  Duration: {result.total_duration_ms:.0f}ms")
    print(f"📄 Articles Processed: {result.articles_processed}")
    print(f"📊 Indicators Calculated: {result.indicators_calculated}")
    
    print("\n📋 STAGE SUMMARY:")
    for stage in result.stages:
        status = "✅" if stage.success else "❌"
        print(f"   {status} {stage.stage_name}: {stage.item_count} items ({stage.duration_ms:.0f}ms)")
    
    if result.layer2_output:
        print("\n🎯 LAYER 2 OUTPUT (for Layer 3):")
        print(f"   National Activity Index: {result.layer2_output.activity_level:.1f}")
        print(f"   Overall Sentiment: {result.layer2_output.overall_sentiment:.2f}")
        print(f"   Article Count: {result.layer2_output.article_count}")
        print(f"   Source Diversity: {result.layer2_output.source_diversity}")
        print(f"   Data Quality: {result.layer2_output.data_quality_score:.2f}")
        print(f"   Indicators: {len(result.layer2_output.indicators)}")
        
        # Category breakdown
        print("\n   📊 PESTEL Category Breakdown:")
        category_counts = {}
        for key, ind in result.layer2_output.indicators.items():
            cat = ind.pestel_category
            if cat not in category_counts:
                category_counts[cat] = {'count': 0, 'total_value': 0}
            category_counts[cat]['count'] += 1
            category_counts[cat]['total_value'] += ind.value
            
        for cat, data in category_counts.items():
            avg = data['total_value'] / data['count'] if data['count'] > 0 else 0
            print(f"      {cat}: {data['count']} indicators (avg: {avg:.1f})")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for error in result.errors:
            print(f"   - {error}")
    
    print("\n" + "=" * 70)
    print(" READY TO PASS TO LAYER 3")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
