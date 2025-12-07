"""
Enhanced Processing Pipeline for Layer 2

This module provides the main orchestration pipeline that integrates all
enhanced services with graceful fallback to existing systems.

Pipeline stages:
1. LLM Classification (or HybridClassifier fallback)
2. Advanced Sentiment Analysis (or basic SentimentAnalyzer fallback)
3. Smart Entity Extraction (or spaCy-based fallback)
4. Topic Modeling (optional, ChromaDB-based)
5. Quality Scoring (always performed)

Features:
- Feature flag control for each enhancement
- Parallel processing where possible
- Graceful degradation on failures
- Comprehensive result aggregation
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from . import (
    LLM_CLASSIFICATION_ENABLED,
    ADVANCED_SENTIMENT_ENABLED,
    SMART_NER_ENABLED,
    TOPIC_MODELING_ENABLED,
    QUALITY_SCORING_ENABLED
)
from .llm_base import LLMConfig, CacheConfig
from .llm_classifier import LLMClassifier, ClassificationResult, create_llm_classifier
from .advanced_sentiment import AdvancedSentimentAnalyzer, AdvancedSentimentResult, create_advanced_sentiment_analyzer
from .smart_entity_extractor import SmartEntityExtractor, SmartEntityResult, create_smart_entity_extractor
from .topic_modeler import TopicModeler, TopicMatch, create_topic_modeler
from .quality_scorer import QualityScorer, QualityScore, create_quality_scorer

logger = logging.getLogger(__name__)


# ============================================================================
# Pipeline Configuration
# ============================================================================

@dataclass
class PipelineConfig:
    """
    Configuration for the enhanced processing pipeline.
    """
    # Feature toggles
    enable_llm_classification: bool = LLM_CLASSIFICATION_ENABLED
    enable_advanced_sentiment: bool = ADVANCED_SENTIMENT_ENABLED
    enable_smart_ner: bool = SMART_NER_ENABLED
    enable_topic_modeling: bool = TOPIC_MODELING_ENABLED
    enable_quality_scoring: bool = QUALITY_SCORING_ENABLED
    
    # Processing options
    parallel_processing: bool = True
    max_concurrency: int = 5
    timeout_seconds: int = 60
    
    # Quality thresholds
    min_quality_score: float = 50.0
    reprocess_on_low_quality: bool = False
    
    # Caching
    cache_enabled: bool = True
    cache_ttl_hours: int = 24
    
    # Fallback behavior
    use_fallbacks: bool = True
    log_fallback_usage: bool = True


# ============================================================================
# Pipeline Result
# ============================================================================

@dataclass
class EnhancedProcessingResult:
    """
    Complete result from enhanced pipeline processing.
    """
    # Article identification
    article_id: str
    
    # Individual results
    classification: Optional[ClassificationResult] = None
    sentiment: Optional[AdvancedSentimentResult] = None
    entities: Optional[SmartEntityResult] = None
    topic_match: Optional[TopicMatch] = None
    quality: Optional[QualityScore] = None
    
    # Processing metadata
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Status tracking
    stages_completed: List[str] = field(default_factory=list)
    stages_failed: List[str] = field(default_factory=list)
    fallbacks_used: List[str] = field(default_factory=list)
    
    # Overall status
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "article_id": self.article_id,
            "classification": self.classification.to_dict() if self.classification else None,
            "sentiment": self.sentiment.to_dict() if self.sentiment else None,
            "entities": self.entities.to_dict() if self.entities else None,
            "topic_match": self.topic_match.to_dict() if self.topic_match else None,
            "quality": self.quality.to_dict() if self.quality else None,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "timestamp": self.timestamp.isoformat(),
            "stages_completed": self.stages_completed,
            "stages_failed": self.stages_failed,
            "fallbacks_used": self.fallbacks_used,
            "success": self.success,
            "error_message": self.error_message
        }
    
    def to_legacy_format(self) -> Dict[str, Any]:
        """
        Convert to legacy format for backward compatibility with existing Layer 2.
        """
        result = {
            "article_id": self.article_id,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.classification:
            result["classification"] = self.classification.to_legacy_format()
        
        if self.sentiment:
            result["sentiment"] = self.sentiment.to_legacy_format()
        
        if self.entities:
            result["entities"] = self.entities.to_legacy_format()
        
        if self.quality:
            result["quality_score"] = self.quality.overall_score
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a brief summary of the processing result."""
        return {
            "article_id": self.article_id,
            "success": self.success,
            "quality_band": self.quality.quality_band.value if self.quality else None,
            "quality_score": round(self.quality.overall_score, 1) if self.quality else None,
            "primary_category": self.classification.primary_category.value if self.classification else None,
            "overall_sentiment": round(self.sentiment.overall_score, 2) if self.sentiment else None,
            "entity_count": self.entities.entity_count if self.entities else 0,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "stages_completed": len(self.stages_completed),
            "fallbacks_used": len(self.fallbacks_used)
        }


# ============================================================================
# Enhanced Pipeline Service
# ============================================================================

class EnhancedPipeline:
    """
    Main orchestration pipeline for enhanced Layer 2 processing.
    
    Integrates all enhanced services with intelligent fallback handling
    and parallel processing for optimal performance.
    
    Usage:
        pipeline = EnhancedPipeline()
        result = await pipeline.process(
            article_id="art_123",
            text="Article content...",
            title="Article Title"
        )
    """
    
    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
        llm_classifier: Optional[LLMClassifier] = None,
        sentiment_analyzer: Optional[AdvancedSentimentAnalyzer] = None,
        entity_extractor: Optional[SmartEntityExtractor] = None,
        topic_modeler: Optional[TopicModeler] = None,
        quality_scorer: Optional[QualityScorer] = None,
        fallback_classifier: Optional[Any] = None,
        fallback_sentiment: Optional[Any] = None,
        fallback_entities: Optional[Any] = None
    ):
        """
        Initialize Enhanced Pipeline.
        
        Args:
            config: Pipeline configuration
            llm_classifier: LLM classifier instance
            sentiment_analyzer: Sentiment analyzer instance
            entity_extractor: Entity extractor instance
            topic_modeler: Topic modeler instance
            quality_scorer: Quality scorer instance
            fallback_classifier: Fallback HybridClassifier
            fallback_sentiment: Fallback SentimentAnalyzer
            fallback_entities: Fallback EntityExtractor
        """
        self.config = config or PipelineConfig()
        
        # Initialize services (lazy if not provided)
        self._classifier = llm_classifier
        self._sentiment = sentiment_analyzer
        self._entities = entity_extractor
        self._topics = topic_modeler
        self._quality = quality_scorer
        
        # Fallback services
        self._fallback_classifier = fallback_classifier
        self._fallback_sentiment = fallback_sentiment
        self._fallback_entities = fallback_entities
        
        # Statistics
        self._total_processed = 0
        self._successful = 0
        self._failed = 0
        self._fallback_count = 0
        self._total_processing_time = 0.0
        
        # Initialization flag
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize all pipeline services.
        
        Returns:
            True if successfully initialized
        """
        try:
            # Initialize classifier
            if self.config.enable_llm_classification and not self._classifier:
                self._classifier = create_llm_classifier(
                    cache_enabled=self.config.cache_enabled,
                    fallback_classifier=self._fallback_classifier
                )
            
            # Initialize sentiment analyzer
            if self.config.enable_advanced_sentiment and not self._sentiment:
                self._sentiment = create_advanced_sentiment_analyzer(
                    cache_enabled=self.config.cache_enabled,
                    fallback_analyzer=self._fallback_sentiment
                )
            
            # Initialize entity extractor
            if self.config.enable_smart_ner and not self._entities:
                self._entities = create_smart_entity_extractor(
                    cache_enabled=self.config.cache_enabled,
                    fallback_extractor=self._fallback_entities
                )
            
            # Initialize topic modeler
            if self.config.enable_topic_modeling and not self._topics:
                self._topics = create_topic_modeler()
                await self._topics.initialize()
            
            # Initialize quality scorer
            if self.config.enable_quality_scoring and not self._quality:
                self._quality = create_quality_scorer(
                    min_acceptable_score=self.config.min_quality_score
                )
            
            self._initialized = True
            logger.info("Enhanced pipeline initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            self._initialized = False
            return False
    
    async def process(
        self,
        article_id: str,
        text: str,
        title: str = "",
        source: str = "",
        published_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EnhancedProcessingResult:
        """
        Process an article through the enhanced pipeline.
        
        Args:
            article_id: Unique article identifier
            text: Article text content
            title: Article title
            source: Article source
            published_at: Publication timestamp
            metadata: Additional article metadata
        
        Returns:
            EnhancedProcessingResult with all processing results
        """
        start_time = time.time()
        
        if not self._initialized:
            await self.initialize()
        
        self._total_processed += 1
        
        result = EnhancedProcessingResult(article_id=article_id)
        
        # Prepare metadata
        article_metadata = metadata or {}
        article_metadata.update({
            "title": title,
            "text": text,
            "source": source,
            "published_at": published_at.isoformat() if published_at else None
        })
        
        try:
            if self.config.parallel_processing:
                # Process in parallel where possible
                await self._process_parallel(
                    result, text, title, source, published_at
                )
            else:
                # Process sequentially
                await self._process_sequential(
                    result, text, title, source, published_at
                )
            
            # Quality scoring (always last, needs other results)
            if self.config.enable_quality_scoring and self._quality:
                try:
                    result.quality = self._quality.score(
                        classification_result=result.classification.to_dict() if result.classification else None,
                        sentiment_result=result.sentiment.to_dict() if result.sentiment else None,
                        entity_result=result.entities.to_dict() if result.entities else None,
                        validation_result=None,  # Cross-validation would come from Layer 1
                        article_metadata=article_metadata
                    )
                    result.stages_completed.append("quality_scoring")
                except Exception as e:
                    logger.error(f"Quality scoring failed: {e}")
                    result.stages_failed.append("quality_scoring")
            
            result.success = len(result.stages_failed) == 0
            self._successful += 1
            
        except Exception as e:
            logger.error(f"Pipeline processing failed for {article_id}: {e}")
            result.success = False
            result.error_message = str(e)
            self._failed += 1
        
        # Calculate processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        self._total_processing_time += result.processing_time_ms
        
        # Track fallback usage
        self._fallback_count += len(result.fallbacks_used)
        
        return result
    
    async def _process_parallel(
        self,
        result: EnhancedProcessingResult,
        text: str,
        title: str,
        source: str,
        published_at: Optional[datetime]
    ):
        """Process stages in parallel where possible."""
        tasks = []
        task_names = []
        
        # Classification task
        if self.config.enable_llm_classification and self._classifier:
            tasks.append(self._run_classification(text, title, source))
            task_names.append("classification")
        
        # Sentiment task
        if self.config.enable_advanced_sentiment and self._sentiment:
            tasks.append(self._run_sentiment(text, title))
            task_names.append("sentiment")
        
        # Entity extraction task
        if self.config.enable_smart_ner and self._entities:
            tasks.append(self._run_entity_extraction(text, title))
            task_names.append("entity_extraction")
        
        # Run all tasks concurrently
        if tasks:
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.config.timeout_seconds
                )
                
                # Process results
                for i, task_result in enumerate(results):
                    name = task_names[i]
                    if isinstance(task_result, Exception):
                        logger.error(f"Task {name} failed: {task_result}")
                        result.stages_failed.append(name)
                    else:
                        if name == "classification":
                            result.classification = task_result
                            if task_result and task_result.classification_source != "llm":
                                result.fallbacks_used.append("classification")
                        elif name == "sentiment":
                            result.sentiment = task_result
                            if task_result and task_result.analysis_source != "llm":
                                result.fallbacks_used.append("sentiment")
                        elif name == "entity_extraction":
                            result.entities = task_result
                            if task_result and task_result.extraction_source != "llm":
                                result.fallbacks_used.append("entity_extraction")
                        result.stages_completed.append(name)
                        
            except asyncio.TimeoutError:
                logger.error("Pipeline processing timed out")
                result.stages_failed.extend(task_names)
        
        # Topic modeling (runs after entity extraction for best results)
        if self.config.enable_topic_modeling and self._topics:
            try:
                result.topic_match = await self._topics.add_article(
                    article_id=result.article_id,
                    text=text,
                    title=title,
                    published_at=published_at
                )
                result.stages_completed.append("topic_modeling")
            except Exception as e:
                logger.error(f"Topic modeling failed: {e}")
                result.stages_failed.append("topic_modeling")
    
    async def _process_sequential(
        self,
        result: EnhancedProcessingResult,
        text: str,
        title: str,
        source: str,
        published_at: Optional[datetime]
    ):
        """Process stages sequentially."""
        # Classification
        if self.config.enable_llm_classification and self._classifier:
            try:
                result.classification = await self._run_classification(text, title, source)
                result.stages_completed.append("classification")
                if result.classification.classification_source != "llm":
                    result.fallbacks_used.append("classification")
            except Exception as e:
                logger.error(f"Classification failed: {e}")
                result.stages_failed.append("classification")
        
        # Sentiment
        if self.config.enable_advanced_sentiment and self._sentiment:
            try:
                result.sentiment = await self._run_sentiment(text, title)
                result.stages_completed.append("sentiment")
                if result.sentiment.analysis_source != "llm":
                    result.fallbacks_used.append("sentiment")
            except Exception as e:
                logger.error(f"Sentiment analysis failed: {e}")
                result.stages_failed.append("sentiment")
        
        # Entity extraction
        if self.config.enable_smart_ner and self._entities:
            try:
                result.entities = await self._run_entity_extraction(text, title)
                result.stages_completed.append("entity_extraction")
                if result.entities.extraction_source != "llm":
                    result.fallbacks_used.append("entity_extraction")
            except Exception as e:
                logger.error(f"Entity extraction failed: {e}")
                result.stages_failed.append("entity_extraction")
        
        # Topic modeling
        if self.config.enable_topic_modeling and self._topics:
            try:
                result.topic_match = await self._topics.add_article(
                    article_id=result.article_id,
                    text=text,
                    title=title,
                    published_at=published_at
                )
                result.stages_completed.append("topic_modeling")
            except Exception as e:
                logger.error(f"Topic modeling failed: {e}")
                result.stages_failed.append("topic_modeling")
    
    async def _run_classification(
        self,
        text: str,
        title: str,
        source: str
    ) -> ClassificationResult:
        """Run classification with timeout handling."""
        return await self._classifier.classify(
            text=text,
            title=title,
            source=source
        )
    
    async def _run_sentiment(
        self,
        text: str,
        title: str
    ) -> AdvancedSentimentResult:
        """Run sentiment analysis with timeout handling."""
        return await self._sentiment.analyze(
            text=text,
            title=title
        )
    
    async def _run_entity_extraction(
        self,
        text: str,
        title: str
    ) -> SmartEntityResult:
        """Run entity extraction with timeout handling."""
        return await self._entities.extract(
            text=text,
            title=title
        )
    
    async def process_batch(
        self,
        articles: List[Dict[str, Any]],
        concurrency: int = None
    ) -> List[EnhancedProcessingResult]:
        """
        Process multiple articles concurrently.
        
        Args:
            articles: List of article dicts with keys: id, text, title, source, published_at
            concurrency: Max concurrent processing (uses config default if not specified)
        
        Returns:
            List of EnhancedProcessingResult objects
        """
        concurrency = concurrency or self.config.max_concurrency
        semaphore = asyncio.Semaphore(concurrency)
        
        async def process_with_limit(article: Dict[str, Any]) -> EnhancedProcessingResult:
            async with semaphore:
                return await self.process(
                    article_id=article.get("id", ""),
                    text=article.get("text", ""),
                    title=article.get("title", ""),
                    source=article.get("source", ""),
                    published_at=article.get("published_at"),
                    metadata=article.get("metadata")
                )
        
        tasks = [process_with_limit(article) for article in articles]
        return await asyncio.gather(*tasks)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics."""
        stats = {
            "initialized": self._initialized,
            "total_processed": self._total_processed,
            "successful": self._successful,
            "failed": self._failed,
            "success_rate": (
                self._successful / self._total_processed * 100
                if self._total_processed > 0 else 0
            ),
            "fallback_count": self._fallback_count,
            "avg_processing_time_ms": (
                self._total_processing_time / self._total_processed
                if self._total_processed > 0 else 0
            ),
            "config": {
                "llm_classification": self.config.enable_llm_classification,
                "advanced_sentiment": self.config.enable_advanced_sentiment,
                "smart_ner": self.config.enable_smart_ner,
                "topic_modeling": self.config.enable_topic_modeling,
                "quality_scoring": self.config.enable_quality_scoring,
                "parallel_processing": self.config.parallel_processing
            }
        }
        
        # Add service-specific stats
        if self._classifier:
            stats["classifier_stats"] = self._classifier.get_stats()
        if self._sentiment:
            stats["sentiment_stats"] = self._sentiment.get_stats()
        if self._entities:
            stats["entity_stats"] = self._entities.get_stats()
        if self._topics:
            stats["topic_stats"] = self._topics.get_stats()
        if self._quality:
            stats["quality_stats"] = self._quality.get_stats()
        
        return stats
    
    def get_service(self, name: str) -> Optional[Any]:
        """
        Get a specific service instance.
        
        Args:
            name: Service name (classifier, sentiment, entities, topics, quality)
        
        Returns:
            Service instance or None
        """
        services = {
            "classifier": self._classifier,
            "sentiment": self._sentiment,
            "entities": self._entities,
            "topics": self._topics,
            "quality": self._quality
        }
        return services.get(name)


# ============================================================================
# Factory Function
# ============================================================================

def create_enhanced_pipeline(
    config: Optional[PipelineConfig] = None,
    fallback_classifier: Optional[Any] = None,
    fallback_sentiment: Optional[Any] = None,
    fallback_entities: Optional[Any] = None
) -> EnhancedPipeline:
    """
    Factory function to create an EnhancedPipeline instance.
    
    Args:
        config: Pipeline configuration
        fallback_classifier: HybridClassifier instance for fallback
        fallback_sentiment: SentimentAnalyzer instance for fallback
        fallback_entities: EntityExtractor instance for fallback
    
    Returns:
        Configured EnhancedPipeline instance
    """
    return EnhancedPipeline(
        config=config,
        fallback_classifier=fallback_classifier,
        fallback_sentiment=fallback_sentiment,
        fallback_entities=fallback_entities
    )


# ============================================================================
# Quick Processing Functions
# ============================================================================

async def process_article(
    article_id: str,
    text: str,
    title: str = "",
    source: str = "",
    published_at: Optional[datetime] = None
) -> EnhancedProcessingResult:
    """
    Quick function to process a single article.
    
    Creates a pipeline instance, processes the article, and returns the result.
    For batch processing, use EnhancedPipeline directly.
    
    Args:
        article_id: Unique article identifier
        text: Article text content
        title: Article title
        source: Article source
        published_at: Publication timestamp
    
    Returns:
        EnhancedProcessingResult
    """
    pipeline = create_enhanced_pipeline()
    return await pipeline.process(
        article_id=article_id,
        text=text,
        title=title,
        source=source,
        published_at=published_at
    )
