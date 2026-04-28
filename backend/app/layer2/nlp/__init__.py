"""
NLP Processing Module for National Activity Indicator System.

Components:
- SentimentAnalyzer: Unified sentiment analysis with VADER and Transformers backends
- SentimentResult: Structured sentiment analysis result
- SentimentLabel: Categorical sentiment labels
- EntityExtractor: spaCy-based named entity + amount extraction
- ExtractedEntities: Pydantic schema for entity extraction results
"""

from app.layer2.nlp.sentiment_analyzer import (
    SentimentAnalyzer,
    SentimentResult,
    SentimentLabel,
    analyze_sentiment,
    analyze_sentiment_batch,
    VaderBackend,
    TransformersBackend
)
from app.layer2.nlp.entity_extractor import EntityExtractor
from app.layer2.nlp.entity_schemas import (
    ExtractedEntities,
    Location,
    Organization,
    Person,
    DateEntity,
    AmountEntity,
    PercentageEntity,
)

__all__ = [
    # Sentiment
    'SentimentAnalyzer',
    'SentimentResult',
    'SentimentLabel',
    'analyze_sentiment',
    'analyze_sentiment_batch',
    'VaderBackend',
    'TransformersBackend',
    # Entity extraction
    'EntityExtractor',
    'ExtractedEntities',
    'Location',
    'Organization',
    'Person',
    'DateEntity',
    'AmountEntity',
    'PercentageEntity',
]
