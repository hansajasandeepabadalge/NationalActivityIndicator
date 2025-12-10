"""
NLP Processing Module for National Activity Indicator System.

Components:
- SentimentAnalyzer: Unified sentiment analysis with VADER and Transformers backends
- SentimentResult: Structured sentiment analysis result
- SentimentLabel: Categorical sentiment labels
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

__all__ = [
    'SentimentAnalyzer',
    'SentimentResult', 
    'SentimentLabel',
    'analyze_sentiment',
    'analyze_sentiment_batch',
    'VaderBackend',
    'TransformersBackend'
]
