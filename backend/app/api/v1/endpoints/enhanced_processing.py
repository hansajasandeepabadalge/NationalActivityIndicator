"""
Layer 2 Enhanced Processing API Endpoints

Provides REST API endpoints for the enhanced LLM-powered processing services:
- Enhanced article processing
- LLM classification
- Advanced sentiment analysis
- Smart entity extraction
- Topic modeling
- Quality scoring
- Service statistics
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

# Services
from app.layer2.services import (
    get_llm_classifier,
    get_advanced_sentiment,
    get_smart_entity_extractor,
    get_topic_modeler,
    get_quality_scorer,
    get_enhanced_pipeline,
    LLM_CLASSIFICATION_ENABLED,
    ADVANCED_SENTIMENT_ENABLED,
    SMART_NER_ENABLED,
    TOPIC_MODELING_ENABLED,
    QUALITY_SCORING_ENABLED
)

router = APIRouter(prefix="/enhanced", tags=["Layer 2 Enhanced Processing"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ArticleInput(BaseModel):
    """Input model for article processing."""
    text: str = Field(..., min_length=10, description="Article text content")
    title: str = Field(default="", description="Article title")
    source: str = Field(default="", description="Article source")
    article_id: str = Field(default="", description="Unique article identifier")
    published_at: Optional[datetime] = Field(default=None, description="Publication timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "The Federal Reserve announced a 0.25% interest rate hike today, citing concerns about persistent inflation...",
                "title": "Fed Raises Interest Rates Amid Inflation Concerns",
                "source": "Reuters",
                "article_id": "art_12345"
            }
        }


class BatchArticleInput(BaseModel):
    """Input model for batch article processing."""
    articles: List[ArticleInput]
    concurrency: int = Field(default=5, ge=1, le=10, description="Max concurrent processing")


class ClassificationResponse(BaseModel):
    """Classification result response."""
    primary_indicator_id: str
    primary_category: str
    primary_confidence: float
    all_categories: Dict[str, float]
    sub_themes: Dict[str, List[str]]
    urgency: str
    business_relevance: str
    key_entities: List[str]
    summary: str
    classification_source: str
    processing_time_ms: float


class SentimentResponse(BaseModel):
    """Sentiment analysis result response."""
    overall: Dict[str, Any]
    dimensions: Dict[str, Any]
    emotions: Dict[str, Any]
    tone: str
    drivers: Dict[str, List[Any]]
    summary: str
    analysis_source: str
    processing_time_ms: float


class EntityResponse(BaseModel):
    """Entity extraction result response."""
    entities: List[Dict[str, Any]]
    primary_entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    entities_by_type: Dict[str, List[Any]]
    entity_count: int
    relationship_count: int
    extraction_source: str
    processing_time_ms: float


class QualityResponse(BaseModel):
    """Quality score result response."""
    overall_score: float
    quality_band: str
    dimensions: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


class EnhancedProcessingResponse(BaseModel):
    """Complete enhanced processing result."""
    article_id: str
    success: bool
    classification: Optional[Dict[str, Any]]
    sentiment: Optional[Dict[str, Any]]
    entities: Optional[Dict[str, Any]]
    topic_match: Optional[Dict[str, Any]]
    quality: Optional[Dict[str, Any]]
    stages_completed: List[str]
    stages_failed: List[str]
    fallbacks_used: List[str]
    processing_time_ms: float


class ServiceStatsResponse(BaseModel):
    """Service statistics response."""
    service: str
    stats: Dict[str, Any]


class FeatureFlagsResponse(BaseModel):
    """Current feature flags status."""
    llm_classification: bool
    advanced_sentiment: bool
    smart_ner: bool
    topic_modeling: bool
    quality_scoring: bool


# ============================================================================
# Complete Processing Endpoints
# ============================================================================

@router.post(
    "/process",
    response_model=EnhancedProcessingResponse,
    summary="Process article through enhanced pipeline",
    description="Run article through complete enhanced processing pipeline with LLM classification, advanced sentiment, smart NER, and quality scoring."
)
async def process_article(article: ArticleInput):
    """
    Process a single article through the enhanced pipeline.
    
    Returns comprehensive processing results including:
    - PESTEL classification with confidence scores
    - Multi-dimensional sentiment analysis
    - Entity extraction with relationships
    - Topic matching
    - Quality score
    """
    try:
        pipeline = get_enhanced_pipeline()
        await pipeline.initialize()
        
        result = await pipeline.process(
            article_id=article.article_id or f"api_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            text=article.text,
            title=article.title,
            source=article.source,
            published_at=article.published_at
        )
        
        return EnhancedProcessingResponse(
            article_id=result.article_id,
            success=result.success,
            classification=result.classification.to_dict() if result.classification else None,
            sentiment=result.sentiment.to_dict() if result.sentiment else None,
            entities=result.entities.to_dict() if result.entities else None,
            topic_match=result.topic_match.to_dict() if result.topic_match else None,
            quality=result.quality.to_dict() if result.quality else None,
            stages_completed=result.stages_completed,
            stages_failed=result.stages_failed,
            fallbacks_used=result.fallbacks_used,
            processing_time_ms=result.processing_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post(
    "/process/batch",
    response_model=List[EnhancedProcessingResponse],
    summary="Process multiple articles",
    description="Process multiple articles concurrently through the enhanced pipeline."
)
async def process_articles_batch(batch: BatchArticleInput):
    """Process multiple articles concurrently."""
    try:
        pipeline = get_enhanced_pipeline()
        await pipeline.initialize()
        
        articles = [
            {
                "id": art.article_id or f"batch_{i}",
                "text": art.text,
                "title": art.title,
                "source": art.source,
                "published_at": art.published_at
            }
            for i, art in enumerate(batch.articles)
        ]
        
        results = await pipeline.process_batch(articles, concurrency=batch.concurrency)
        
        return [
            EnhancedProcessingResponse(
                article_id=r.article_id,
                success=r.success,
                classification=r.classification.to_dict() if r.classification else None,
                sentiment=r.sentiment.to_dict() if r.sentiment else None,
                entities=r.entities.to_dict() if r.entities else None,
                topic_match=r.topic_match.to_dict() if r.topic_match else None,
                quality=r.quality.to_dict() if r.quality else None,
                stages_completed=r.stages_completed,
                stages_failed=r.stages_failed,
                fallbacks_used=r.fallbacks_used,
                processing_time_ms=r.processing_time_ms
            )
            for r in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


# ============================================================================
# Individual Service Endpoints
# ============================================================================

@router.post(
    "/classify",
    response_model=ClassificationResponse,
    summary="LLM-powered PESTEL classification",
    description="Classify article using Groq Llama 3.1 70B with multi-label PESTEL categories, sub-themes, and urgency assessment."
)
async def classify_article(article: ArticleInput):
    """Classify article using LLM-powered classifier."""
    if not LLM_CLASSIFICATION_ENABLED:
        raise HTTPException(status_code=503, detail="LLM classification is disabled")
    
    try:
        classifier = get_llm_classifier()
        result = await classifier.classify(
            text=article.text,
            title=article.title,
            source=article.source
        )
        
        return ClassificationResponse(
            primary_indicator_id=result.primary_indicator_id,
            primary_category=result.primary_category.value,
            primary_confidence=result.primary_confidence,
            all_categories=result.all_categories,
            sub_themes=result.sub_themes,
            urgency=result.urgency.value,
            business_relevance=result.business_relevance.value,
            key_entities=result.key_entities,
            summary=result.summary,
            classification_source=result.classification_source,
            processing_time_ms=result.processing_time_ms
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


@router.post(
    "/sentiment",
    response_model=SentimentResponse,
    summary="Multi-dimensional sentiment analysis",
    description="Analyze sentiment across 4 dimensions: overall, business confidence, public mood, and economic outlook."
)
async def analyze_sentiment(article: ArticleInput):
    """Analyze article sentiment using advanced analyzer."""
    if not ADVANCED_SENTIMENT_ENABLED:
        raise HTTPException(status_code=503, detail="Advanced sentiment is disabled")
    
    try:
        analyzer = get_advanced_sentiment()
        result = await analyzer.analyze(
            text=article.text,
            title=article.title
        )
        
        response_dict = result.to_dict()
        return SentimentResponse(
            overall=response_dict["overall"],
            dimensions=response_dict["dimensions"],
            emotions=response_dict["emotions"],
            tone=response_dict["tone"],
            drivers=response_dict["drivers"],
            summary=response_dict["summary"],
            analysis_source=response_dict["analysis_source"],
            processing_time_ms=response_dict["processing_time_ms"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")


@router.post(
    "/entities",
    response_model=EntityResponse,
    summary="Smart entity extraction",
    description="Extract entities with relationships and importance scoring using LLM-powered NER."
)
async def extract_entities(article: ArticleInput):
    """Extract entities using smart extractor."""
    if not SMART_NER_ENABLED:
        raise HTTPException(status_code=503, detail="Smart NER is disabled")
    
    try:
        extractor = get_smart_entity_extractor()
        result = await extractor.extract(
            text=article.text,
            title=article.title
        )
        
        response_dict = result.to_dict()
        return EntityResponse(
            entities=response_dict["entities"],
            primary_entities=response_dict["primary_entities"],
            relationships=response_dict["relationships"],
            entities_by_type=response_dict["entities_by_type"],
            entity_count=response_dict["entity_count"],
            relationship_count=response_dict["relationship_count"],
            extraction_source=response_dict["extraction_source"],
            processing_time_ms=response_dict["processing_time_ms"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")


@router.post(
    "/quality",
    response_model=QualityResponse,
    summary="Calculate quality score",
    description="Calculate comprehensive quality score (0-100) based on classification, sentiment, entities, and completeness."
)
async def calculate_quality(
    article: ArticleInput,
    include_processing: bool = Query(True, description="Process article first if True")
):
    """Calculate quality score for article."""
    if not QUALITY_SCORING_ENABLED:
        raise HTTPException(status_code=503, detail="Quality scoring is disabled")
    
    try:
        scorer = get_quality_scorer()
        
        if include_processing:
            # Run through enhanced pipeline first
            pipeline = get_enhanced_pipeline()
            await pipeline.initialize()
            
            result = await pipeline.process(
                article_id="quality_check",
                text=article.text,
                title=article.title,
                source=article.source
            )
            
            if result.quality:
                quality_dict = result.quality.to_dict()
                return QualityResponse(
                    overall_score=quality_dict["overall_score"],
                    quality_band=quality_dict["quality_band"],
                    dimensions=quality_dict["dimensions"],
                    strengths=quality_dict["strengths"],
                    weaknesses=quality_dict["weaknesses"],
                    recommendations=quality_dict["recommendations"]
                )
        
        # Just score metadata without processing
        quality = scorer.score(
            article_metadata={
                "text": article.text,
                "title": article.title,
                "source": article.source
            }
        )
        
        quality_dict = quality.to_dict()
        return QualityResponse(
            overall_score=quality_dict["overall_score"],
            quality_band=quality_dict["quality_band"],
            dimensions=quality_dict["dimensions"],
            strengths=quality_dict["strengths"],
            weaknesses=quality_dict["weaknesses"],
            recommendations=quality_dict["recommendations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality scoring failed: {str(e)}")


# ============================================================================
# Topic Modeling Endpoints
# ============================================================================

@router.get(
    "/topics/trending",
    summary="Get trending topics",
    description="Get current trending, emerging, and declining topics from the article corpus."
)
async def get_trending_topics(
    limit: int = Query(10, ge=1, le=50, description="Max topics per category")
):
    """Get trending topics from topic modeler."""
    if not TOPIC_MODELING_ENABLED:
        raise HTTPException(status_code=503, detail="Topic modeling is disabled")
    
    try:
        modeler = get_topic_modeler()
        await modeler.initialize()
        
        result = await modeler.get_trending_topics(limit=limit)
        return result.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")


@router.get(
    "/topics/{topic_id}",
    summary="Get topic details",
    description="Get detailed information about a specific topic."
)
async def get_topic(topic_id: str):
    """Get topic details by ID."""
    if not TOPIC_MODELING_ENABLED:
        raise HTTPException(status_code=503, detail="Topic modeling is disabled")
    
    try:
        modeler = get_topic_modeler()
        topic = modeler.get_topic(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
        
        return topic.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topic: {str(e)}")


# ============================================================================
# Status and Statistics Endpoints
# ============================================================================

@router.get(
    "/status",
    response_model=FeatureFlagsResponse,
    summary="Get feature flags status",
    description="Get current status of all enhanced processing feature flags."
)
async def get_feature_flags():
    """Get current feature flag status."""
    return FeatureFlagsResponse(
        llm_classification=LLM_CLASSIFICATION_ENABLED,
        advanced_sentiment=ADVANCED_SENTIMENT_ENABLED,
        smart_ner=SMART_NER_ENABLED,
        topic_modeling=TOPIC_MODELING_ENABLED,
        quality_scoring=QUALITY_SCORING_ENABLED
    )


@router.get(
    "/stats",
    summary="Get all service statistics",
    description="Get comprehensive statistics from all enhanced processing services."
)
async def get_all_stats():
    """Get statistics from all services."""
    try:
        pipeline = get_enhanced_pipeline()
        return pipeline.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get(
    "/stats/{service}",
    response_model=ServiceStatsResponse,
    summary="Get service statistics",
    description="Get statistics for a specific service."
)
async def get_service_stats(
    service: str = Query(..., description="Service name: classifier, sentiment, entities, topics, quality, pipeline")
):
    """Get statistics for a specific service."""
    try:
        if service == "classifier":
            stats = get_llm_classifier().get_stats()
        elif service == "sentiment":
            stats = get_advanced_sentiment().get_stats()
        elif service == "entities":
            stats = get_smart_entity_extractor().get_stats()
        elif service == "topics":
            stats = get_topic_modeler().get_stats()
        elif service == "quality":
            stats = get_quality_scorer().get_stats()
        elif service == "pipeline":
            stats = get_enhanced_pipeline().get_stats()
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown service: {service}. Valid options: classifier, sentiment, entities, topics, quality, pipeline"
            )
        
        return ServiceStatsResponse(service=service, stats=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats for {service}: {str(e)}")


@router.get(
    "/health",
    summary="Health check",
    description="Check health status of enhanced processing services."
)
async def health_check():
    """Health check for enhanced services."""
    health = {
        "status": "healthy",
        "services": {},
        "features_enabled": {
            "llm_classification": LLM_CLASSIFICATION_ENABLED,
            "advanced_sentiment": ADVANCED_SENTIMENT_ENABLED,
            "smart_ner": SMART_NER_ENABLED,
            "topic_modeling": TOPIC_MODELING_ENABLED,
            "quality_scoring": QUALITY_SCORING_ENABLED
        }
    }
    
    # Check each service
    try:
        if LLM_CLASSIFICATION_ENABLED:
            classifier = get_llm_classifier()
            health["services"]["classifier"] = "available"
    except Exception as e:
        health["services"]["classifier"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    try:
        if ADVANCED_SENTIMENT_ENABLED:
            sentiment = get_advanced_sentiment()
            health["services"]["sentiment"] = "available"
    except Exception as e:
        health["services"]["sentiment"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    try:
        if SMART_NER_ENABLED:
            entities = get_smart_entity_extractor()
            health["services"]["entities"] = "available"
    except Exception as e:
        health["services"]["entities"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    try:
        if TOPIC_MODELING_ENABLED:
            topics = get_topic_modeler()
            health["services"]["topics"] = "available"
    except Exception as e:
        health["services"]["topics"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    try:
        if QUALITY_SCORING_ENABLED:
            quality = get_quality_scorer()
            health["services"]["quality"] = "available"
    except Exception as e:
        health["services"]["quality"] = f"error: {str(e)}"
        health["status"] = "degraded"
    
    return health
