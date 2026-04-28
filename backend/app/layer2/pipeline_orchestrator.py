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

# Analysis imports for new features
from app.layer2.analysis.anomaly_detector import AnomalyDetector
from app.layer2.narrative.generator import NarrativeGenerator

from app.core.schemas.layer1_to_layer2 import ProcessedArticleContract
from pydantic import ValidationError

from app.services.filters import create_quality_filter, FilterAction
from app.db.session import SessionLocal

# Integration contracts
from app.layer1.orchestrator.pipeline.contracts import (
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
        self._hybrid_classifier = None
        
    async def _init_components(self):
        """Initialize all pipeline components."""
        # Database session for Sync models
        if getattr(self, '_db_session', None) is None:
            self._db_session = SessionLocal()
            
        # Quality Filter
        if getattr(self, '_quality_filter', None) is None:
            self._quality_filter = create_quality_filter(self._db_session)
            
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
            
        # Full indicator calculator
        if not self._indicator_calculator:
            self._indicator_calculator = create_full_indicator_calculator(self.pg_config)

        # Hybrid classifier (Rule-based + ML, falls back to rule-only until ML is trained)
        # MUST initialize before enhanced_pipeline so we can wire it as the fallback.
        if self._hybrid_classifier is None:
            try:
                from app.layer2.ml_classification.hybrid_classifier import HybridClassifier
                self._hybrid_classifier = HybridClassifier()
                logger.info("HybridClassifier initialized (rule-based mode until ML model is trained)")
            except Exception as e:
                logger.warning(f"HybridClassifier unavailable: {e}")

        # Enhanced processing pipeline — wire up the real fallbacks so that
        # services/llm_classifier._run_hybrid_classifier and
        # services/smart_entity_extractor._run_basic_extractor have something
        # to fall back to when the LLM is rate-limited/unavailable.
        if not self._enhanced_pipeline:
            try:
                from app.layer2.services.enhanced_pipeline import create_enhanced_pipeline
                from app.layer2.nlp.entity_extractor import EntityExtractor
                from app.layer2.nlp.sentiment_analyzer import SentimentAnalyzer

                self._enhanced_pipeline = create_enhanced_pipeline(
                    PipelineConfig(),
                    fallback_classifier=self._hybrid_classifier,
                    fallback_sentiment=SentimentAnalyzer(backend='vader'),
                    fallback_entities=EntityExtractor(),
                )
            except Exception as e:
                logger.warning(f"Enhanced pipeline not available: {e}")
            
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
            hybrid_covered = sum(
                1 for a in classified_articles if a.get('hybrid_indicator_assignments')
            )
            stages.append(PipelineStageResult(
                stage_name="2_pestel_classification",
                success=len(classified_articles) > 0,
                item_count=len(classified_articles),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={
                    "method": "LLM + fallback (PESTEL) + HybridClassifier (indicators)",
                    "hybrid_articles_with_indicator_assignments": hybrid_covered
                }
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
            # STAGE 7: Calculate Real Trends from Historical Data
            # ================================================================
            stage_start = datetime.now()
            trends = self._calculate_real_trends(indicator_values)
            rising_count = sum(1 for t in trends.values() if t.direction == TrendDirection.RISING)
            falling_count = sum(1 for t in trends.values() if t.direction == TrendDirection.FALLING)
            stages.append(PipelineStageResult(
                stage_name="7_calculate_trends",
                success=len(trends) > 0,
                item_count=len(trends),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={
                    "rising": rising_count,
                    "falling": falling_count,
                    "stable": len(trends) - rising_count - falling_count
                }
            ))
            
            # ================================================================
            # STAGE 8: Detect Anomalies & Generate Events
            # ================================================================
            stage_start = datetime.now()
            events = self._stage_detect_anomalies_and_events(indicator_values, trends)
            critical_events = sum(1 for e in events if e.severity == SeverityLevel.CRITICAL)
            high_events = sum(1 for e in events if e.severity == SeverityLevel.HIGH)
            stages.append(PipelineStageResult(
                stage_name="8_detect_anomalies_events",
                success=True,
                item_count=len(events),
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={
                    "total_events": len(events),
                    "critical": critical_events,
                    "high": high_events,
                    "medium": sum(1 for e in events if e.severity == SeverityLevel.MEDIUM),
                    "low": sum(1 for e in events if e.severity == SeverityLevel.LOW)
                }
            ))
            
            # ================================================================
            # STAGE 9: Build Layer2Output Contract
            # ================================================================
            stage_start = datetime.now()
            layer2_output = self._build_layer2_output(
                indicator_values=indicator_values,
                composites=composites,
                articles=articles_with_entities,
                time_window_hours=time_window_hours,
                trends=trends,  # Pass calculated trends
                events=events   # Pass detected events
            )
            stages.append(PipelineStageResult(
                stage_name="9_build_layer2_output",
                success=layer2_output is not None,
                item_count=len(layer2_output.indicators) if layer2_output else 0,
                duration_ms=(datetime.now() - stage_start).total_seconds() * 1000,
                details={"output_ready_for_layer3": True}
            ))
            
            # ================================================================
            # STAGE 10: Store Results (Optional)
            # ================================================================
            if store_results:
                stage_start = datetime.now()
                stored_count = await self._stage_store_results(
                    articles=articles_with_entities,
                    indicator_values=indicator_values,
                    composites=composites
                )
                stages.append(PipelineStageResult(
                    stage_name="10_store_results",
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
            
            # Convert to dict format and VALIDATE AGAINST CONTRACT
            result = []
            ignored_count = 0
            
            for article in articles:
                raw_dict = {}
                if isinstance(article, Layer2Article):
                    raw_dict = {
                        'article_id': article.article_id,
                        'title': article.title,
                        'body': article.text,
                        'source': article.source,
                        'url': article.url,
                        'published_at': article.published_at,
                        'language': article.language,
                        'layer1_quality_score': getattr(article, "layer1_quality_score", 1.0),
                        'layer1_categories': getattr(article, "layer1_categories", []),
                        'layer1_entities': getattr(article, "layer1_entities", {})
                    }
                else:
                    raw_dict = article
                
                # Strict Boundary Validation
                try:
                    # Enforce the strict Pydantic contract
                    validated_article = ProcessedArticleContract.model_validate(raw_dict)
                    
                    # PRE-FILTER: Block blacklisted sources immediately
                    pre_result = await self._quality_filter.pre_filter(
                        article_id=validated_article.article_id,
                        source_name=validated_article.source
                    )
                    
                    if pre_result.action == FilterAction.REJECTED:
                        logger.warning(f"QualityFilter Pre-Rejected: {validated_article.article_id} from {validated_article.source}")
                        ignored_count += 1
                        continue
                        
                    dumped = validated_article.model_dump()
                    dumped['_weight_multiplier'] = pre_result.weight_multiplier
                    
                    # Convert strictly defined model back to dict for the rest of Layer 2
                    result.append(dumped)
                except ValidationError as e:
                    logger.warning(f"Contract Violation! Dropping article due to invalid Layer 1 output: {e}")
                    ignored_count += 1
                    
            logger.info(f"Fetched {len(result)} valid articles from Layer 1. (Dropped {ignored_count} invalid articles)")
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
                        classifier.classify(text[:2000], force_llm=True),  # Force LLM for better classification
                        timeout=30.0  # Increased timeout for LLM calls (Groq can be slow)
                    )
                    
                    if result and result.all_categories:
                        # all_categories is a dict of category -> confidence
                        article['pestel_categories'] = list(result.all_categories.keys())
                        article['pestel_confidence'] = list(result.all_categories.values())
                        article['primary_category'] = result.primary_category.value if result.primary_category else 'Economic'
                        logger.debug(f"LLM classified article: {result.classification_source}")
                    else:
                        logger.warning(f"LLM returned empty result, using fallback")
                        article['pestel_categories'] = self._fallback_classify(text)
                        article['pestel_confidence'] = [0.5]
                        
                except asyncio.TimeoutError:
                    logger.warning(f"LLM classification timeout (30s), using fallback")
                    article['pestel_categories'] = self._fallback_classify(
                        f"{article.get('title', '')} {article.get('body', '')}"
                    )
                    article['pestel_confidence'] = [0.5]
                except Exception as e:
                    logger.error(f"LLM classification error: {type(e).__name__}: {str(e)}")
                    article['pestel_categories'] = ['Economic']  # Default
                    article['pestel_confidence'] = [0.3]

        except ImportError:
            logger.warning("LLM classifier not available, using fallback")
            for article in articles:
                article['pestel_categories'] = self._fallback_classify(
                    f"{article.get('title', '')} {article.get('body', '')}"
                )
                article['pestel_confidence'] = [0.5]

        # Pass 2: Run HybridClassifier for indicator-level assignment on each article.
        # This is independent of PESTEL category assignment above — it assigns specific
        # indicator IDs (e.g. ECO_INFLATION) using rule-based + ML weights.
        if self._hybrid_classifier is not None:
            hybrid_hits = 0
            for article in articles:
                try:
                    assignments = self._hybrid_classifier.classify(
                        article_text=article.get('body', ''),
                        article_title=article.get('title', ''),
                        article_category=article.get('primary_category', ''),
                        min_confidence=0.3
                    )
                    article['hybrid_indicator_assignments'] = assignments
                    if assignments:
                        hybrid_hits += 1
                except Exception as e:
                    logger.debug(f"Hybrid classify error for {article.get('article_id', '?')}: {e}")
                    article['hybrid_indicator_assignments'] = []
            logger.info(f"HybridClassifier: {hybrid_hits}/{len(articles)} articles had indicator matches")

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
                    # Layer2Article uses 'text' (combined title+body), not 'body'
                    full_text = article.get('text', '') or f"{article.get('title', '')} {article.get('body', '')}"
                    result = analyzer.analyze(full_text)
                    
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
        """Stage 4: Extract named entities from articles via EntityExtractor."""
        logger.info(f"Extracting entities from {len(articles)} articles...")

        try:
            from app.layer2.nlp.entity_extractor import EntityExtractor
            extractor = EntityExtractor()  # singleton — spaCy model loaded once

            for article in articles:
                try:
                    # Layer2Article uses 'text' (combined), not 'body'
                    full_text = article.get('text', '') or f"{article.get('title', '')} {article.get('body', '')}"
                    title = article.get('title', '')
                    article_id = article.get('article_id', '')

                    extracted = extractor.extract_entities(article_id, title, full_text)

                    # Store structured result AND a flat list for backward-compat
                    article['extracted_entities'] = extracted  # ExtractedEntities model
                    article['entities'] = [
                        {'text': e.text, 'label': 'GPE', 'start': e.start_char, 'end': e.end_char}
                        for e in extracted.locations
                    ] + [
                        {'text': e.text, 'label': 'ORG', 'start': e.start_char, 'end': e.end_char}
                        for e in extracted.organizations
                    ] + [
                        {'text': e.text, 'label': 'PERSON', 'start': e.start_char, 'end': e.end_char}
                        for e in extracted.persons
                    ] + [
                        {'text': e.text, 'label': 'DATE', 'start': e.start_char, 'end': e.end_char}
                        for e in extracted.dates
                    ] + [
                        {'text': e.text, 'label': 'MONEY', 'start': e.start_char, 'end': e.end_char}
                        for e in extracted.amounts
                    ]

                except Exception as e:
                    logger.warning(f"Entity extraction error for {article.get('article_id')}: {e}")
                    article['extracted_entities'] = None
                    article['entities'] = []

        except Exception as e:
            logger.warning(f"EntityExtractor not available: {e}")
            for article in articles:
                article['extracted_entities'] = None
                article['entities'] = []

        return articles
    
    def _build_indicator_values_from_hybrid(
        self,
        articles: List[Dict[str, Any]]
    ) -> Dict[str, IndicatorValue]:
        """
        Build IndicatorValue objects from HybridClassifier per-article assignments.

        The hybrid classifier assigns specific indicator IDs (e.g. ECO_INFLATION) to
        articles with a confidence score. Here we aggregate across all articles to
        produce a frequency-based indicator value (0-100 scale), matching the same
        calculation logic as FullIndicatorCalculator._calculate_frequency_indicator.
        """
        from collections import defaultdict

        indicator_article_confs: Dict[str, List] = defaultdict(list)
        for article in articles:
            for assignment in article.get('hybrid_indicator_assignments', []):
                indicator_article_confs[assignment['indicator_id']].append(
                    (article, float(assignment['confidence']))
                )

        # Build lookup from FullIndicatorCalculator's loaded definitions
        indicator_meta = {
            ind.indicator_id: ind
            for ind in self._indicator_calculator.indicators
        }

        result: Dict[str, IndicatorValue] = {}
        for indicator_id, article_confs in indicator_article_confs.items():
            meta = indicator_meta.get(indicator_id)
            if not meta:
                continue

            count = len(article_confs)
            confidences = [c for _, c in article_confs]
            avg_conf = sum(confidences) / len(confidences)

            # Frequency-based 0-100 value (same formula as FullIndicatorCalculator)
            value = min(100.0, 50.0 + (count * 5)) if count >= 10 else 50.0 + (count * 5)

            result[indicator_id] = IndicatorValue(
                indicator_id=indicator_id,
                indicator_name=meta.indicator_name,
                pestel_category=meta.pestel_category,
                subcategory=meta.subcategory,
                value=round(value, 1),
                confidence=round(min(1.0, (count / 5) * avg_conf), 2),
                article_count=count,
                matching_articles=[a.get('article_id', '') for a, _ in article_confs[:5]],
                calculation_type='hybrid_classification'
            )

        return result

    def _stage_calculate_indicators(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[IndicatorValue]:
        """Stage 5: Calculate all 105 indicators.

        FullIndicatorCalculator covers all 105 via keyword matching.
        HybridClassifier covers the 10 blueprint-priority indicators with higher
        accuracy (rule-based + ML weights). Hybrid results override keyword-match
        results for those 10 indicators; the remaining 95 come from FullIndicatorCalculator.
        """
        logger.info(f"Calculating indicators from {len(articles)} articles...")

        full_results: List[IndicatorValue] = self._indicator_calculator.calculate_all_indicators(articles)

        hybrid_overrides = self._build_indicator_values_from_hybrid(articles)
        if not hybrid_overrides:
            return full_results

        merged = []
        override_count = 0
        for iv in full_results:
            if iv.indicator_id in hybrid_overrides:
                merged.append(hybrid_overrides[iv.indicator_id])
                override_count += 1
            else:
                merged.append(iv)

        logger.info(
            f"Indicator calc: {len(full_results)} total, "
            f"{override_count} overridden by HybridClassifier"
        )
        return merged
    
    def _calculate_real_trends(
        self,
        indicator_values: List[IndicatorValue]
    ) -> Dict[str, IndicatorTrendOutput]:
        """Calculate real trends from historical PostgreSQL data."""
        logger.info("Calculating real trends from historical data...")
        
        trends: Dict[str, IndicatorTrendOutput] = {}
        
        try:
            import numpy as np
            from scipy import stats
            
            # Connect to PostgreSQL
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Calculate trends for each indicator
            for iv in indicator_values:
                try:
                    # Query last 30 days of values
                    cursor.execute("""
                        SELECT timestamp, value
                        FROM indicator_values
                        WHERE indicator_id = %s
                          AND timestamp >= NOW() - INTERVAL '30 days'
                        ORDER BY timestamp ASC
                    """, (iv.indicator_id,))
                    
                    historical = cursor.fetchall()
                    
                    if len(historical) < 5:
                        # Not enough data - mark as stable
                        indicator_key = iv.indicator_name.replace(' ', '_').upper()
                        trends[indicator_key] = IndicatorTrendOutput(
                            indicator_id=iv.indicator_id,
                            direction=TrendDirection.STABLE,
                            change_percent=0.0,
                            period_days=7
                        )
                        continue
                    
                    # Extract values
                    values = np.array([float(row['value']) for row in historical])
                    x = np.arange(len(values))
                    
                    # Linear regression
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
                    
                    # Calculate percentage change
                    first_val = values[0]
                    last_val = values[-1]
                    if first_val != 0:
                        pct_change = ((last_val - first_val) / first_val) * 100
                    else:
                        pct_change = 0.0
                    
                    # Determine direction based on slope and percentage change
                    if slope > 0.5 and pct_change > 5:
                        direction = TrendDirection.RISING
                    elif slope < -0.5 and pct_change < -5:
                        direction = TrendDirection.FALLING
                    else:
                        direction = TrendDirection.STABLE
                    
                    indicator_key = iv.indicator_name.replace(' ', '_').upper()
                    trends[indicator_key] = IndicatorTrendOutput(
                        indicator_id=iv.indicator_id,
                        direction=direction,
                        change_percent=round(pct_change, 2),
                        period_days=len(historical)
                    )
                    
                except Exception as e:
                    logger.warning(f"Error calculating trend for {iv.indicator_id}: {e}")
                    # Fallback to stable
                    indicator_key = iv.indicator_name.replace(' ', '_').upper()
                    trends[indicator_key] = IndicatorTrendOutput(
                        indicator_id=iv.indicator_id,
                        direction=TrendDirection.STABLE,
                        change_percent=0.0,
                        period_days=7
                    )
            
            cursor.close()
            conn.close()
            
            logger.info(f"Calculated trends for {len(trends)} indicators")
            return trends
            
        except Exception as e:
            logger.error(f"Error in trend calculation: {e}")
            # Return empty trends on error
            return {}
    
    def _stage_detect_anomalies_and_events(
        self,
        indicator_values: List[IndicatorValue],
        trends: Dict[str, IndicatorTrendOutput]
    ) -> List[IndicatorEventOutput]:
        """Detect anomalies and generate events from indicator values."""
        logger.info("Detecting anomalies and generating events...")
        
        events: List[IndicatorEventOutput] = []
        event_id_counter = 1
        
        try:
            # Initialize anomaly detector
            anomaly_detector = AnomalyDetector()
            
            # Connect to PostgreSQL for historical data
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            for iv in indicator_values:
                try:
                    # Query historical values for anomaly detection
                    cursor.execute("""
                        SELECT timestamp, value
                        FROM indicator_values
                        WHERE indicator_id = %s
                          AND timestamp >= NOW() - INTERVAL '30 days'
                        ORDER BY timestamp ASC
                    """, (iv.indicator_id,))
                    
                    historical = cursor.fetchall()
                    
                    if len(historical) < 5:
                        continue  # Not enough data for anomaly detection
                    
                    # Prepare data for anomaly detector
                    history_data = [
                        {'time': row['timestamp'], 'value': float(row['value'])}
                        for row in historical
                    ]
                    
                    # Detect anomalies using Z-score (threshold=2.0 for 95% confidence)
                    anomalies = anomaly_detector.detect_anomalies(history_data, threshold=2.0)
                    
                    # Check if current value is an anomaly
                    current_is_anomaly = False
                    for anomaly in anomalies:
                        # Check if it's recent (within last day)
                        if isinstance(anomaly['time'], datetime):
                            time_diff = datetime.now() - anomaly['time']
                            if time_diff.total_seconds() < 86400:  # 24 hours
                                current_is_anomaly = True
                                break
                    
                    if current_is_anomaly or (anomalies and len(anomalies) > 0):
                        # Determine severity based on Z-score
                        latest_anomaly = anomalies[-1] if anomalies else None
                        if latest_anomaly:
                            z_score = abs(latest_anomaly.get('z_score', 0))
                            
                            if z_score > 3.0:
                                severity = SeverityLevel.CRITICAL
                            elif z_score > 2.5:
                                severity = SeverityLevel.HIGH
                            elif z_score > 2.0:
                                severity = SeverityLevel.MEDIUM
                            else:
                                severity = SeverityLevel.LOW
                            
                            # Get previous value
                            prev_value = historical[-2]['value'] if len(historical) > 1 else None
                            
                            # Create event
                            event = IndicatorEventOutput(
                                event_id=event_id_counter,
                                indicator_id=iv.indicator_id,
                                timestamp=datetime.now(),
                                event_type="anomaly_detected",
                                severity=severity,
                                value_before=float(prev_value) if prev_value else None,
                                value_after=float(iv.value),
                                description=f"{iv.indicator_name}: {latest_anomaly['type']} detected (Z-score: {z_score:.2f})"
                            )
                            events.append(event)
                            event_id_counter += 1
                    
                    # Check for threshold breaches (extreme values)
                    if iv.value > 90:
                        event = IndicatorEventOutput(
                            event_id=event_id_counter,
                            indicator_id=iv.indicator_id,
                            timestamp=datetime.now(),
                            event_type="threshold_breach_high",
                            severity=SeverityLevel.HIGH if iv.value > 95 else SeverityLevel.MEDIUM,
                            value_before=None,
                            value_after=float(iv.value),
                            description=f"{iv.indicator_name}: High threshold breach (value: {iv.value:.1f})"
                        )
                        events.append(event)
                        event_id_counter += 1
                    elif iv.value < 10:
                        event = IndicatorEventOutput(
                            event_id=event_id_counter,
                            indicator_id=iv.indicator_id,
                            timestamp=datetime.now(),
                            event_type="threshold_breach_low",
                            severity=SeverityLevel.HIGH if iv.value < 5 else SeverityLevel.MEDIUM,
                            value_before=None,
                            value_after=float(iv.value),
                            description=f"{iv.indicator_name}: Low threshold breach (value: {iv.value:.1f})"
                        )
                        events.append(event)
                        event_id_counter += 1
                    
                    # Check for significant trend changes
                    indicator_key = iv.indicator_name.replace(' ', '_').upper()
                    trend = trends.get(indicator_key)
                    if trend and abs(trend.change_percent) > 20:
                        # trend.direction is already a string value
                        direction_str = trend.direction if isinstance(trend.direction, str) else trend.direction.value
                        event = IndicatorEventOutput(
                            event_id=event_id_counter,
                            indicator_id=iv.indicator_id,
                            timestamp=datetime.now(),
                            event_type="significant_trend_change",
                            severity=SeverityLevel.MEDIUM if abs(trend.change_percent) < 30 else SeverityLevel.HIGH,
                            value_before=None,
                            value_after=float(iv.value),
                            description=f"{iv.indicator_name}: Significant {direction_str} trend ({trend.change_percent:+.1f}%)"
                        )
                        events.append(event)
                        event_id_counter += 1
                        
                except Exception as e:
                    logger.warning(f"Error detecting anomalies for {iv.indicator_id}: {e}")
                    continue
            
            cursor.close()
            conn.close()
            
            logger.info(f"Detected {len(events)} events/anomalies")
            return events
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return []
    
    
    def _build_layer2_output(
        self,
        indicator_values: List[IndicatorValue],
        composites: Dict[str, Any],
        articles: List[Dict[str, Any]],
        time_window_hours: int,
        trends: Optional[Dict[str, IndicatorTrendOutput]] = None,
        events: Optional[List[IndicatorEventOutput]] = None
    ) -> Optional[Layer2Output]:
        """Stage 8: Build the Layer2Output contract for Layer 3."""
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
            
            # Use provided trends or fallback to stable
            if trends is None or len(trends) == 0:
                logger.warning("No trends provided, using stable defaults")
                trends = {}
                for key, indicator in indicators_output.items():
                    trends[key] = IndicatorTrendOutput(
                        indicator_id=indicator.indicator_id,
                        direction=TrendDirection.STABLE,
                        change_percent=0.0,
                        period_days=7
                    )
            
            # Use provided events or empty list
            if events is None:
                events = []
                logger.info("No events detected")
            else:
                logger.info(f"Including {len(events)} events in output")
            
            
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
                events=events,  # Now using detected events!
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
            
            # Store indicator calculations to MongoDB
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
                
            # Store composite scores to MongoDB
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
            
            # ============================================================
            # STORE TO POSTGRESQL (for dashboard display)
            # ============================================================
            try:
                from app.layer2.storage.indicator_persistence import Layer2IndicatorPersistence
                
                # Convert IndicatorValue objects to dicts for storage
                pg_indicator_values = [
                    {
                        'indicator_id': iv.indicator_id,
                        'indicator_name': iv.indicator_name,
                        'value': iv.value,
                        'confidence': iv.confidence,
                        'article_count': iv.article_count,
                        'source_count': iv.article_count,
                        'calculation_type': iv.calculation_type,
                        'subcategory': iv.subcategory,
                        'matching_articles': iv.matching_articles[:10] if iv.matching_articles else []
                    }
                    for iv in indicator_values
                ]
                
                # Store to PostgreSQL
                persistence = Layer2IndicatorPersistence()
                pg_result = persistence.store_indicator_values(
                    indicator_values=pg_indicator_values,
                    timestamp=datetime.now()
                )
                
                pg_stored = pg_result.get('stored_count', 0)
                pg_updated = pg_result.get('updated_count', 0)
                logger.info(f"PostgreSQL: Stored {pg_stored} new, updated {pg_updated} indicator values")
                stored_count += pg_stored + pg_updated
                
            except Exception as pg_error:
                logger.error(f"PostgreSQL storage error: {pg_error}")
            
            # Mark articles as processed in MongoDB
            for article in articles:
                await self._mongodb_loader.mark_as_layer2_processed(
                    article.get('article_id', ''),
                    {'processed': True, 'timestamp': datetime.now().isoformat()}
                )
                
            logger.info(f"Stored {stored_count} documents total")
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
