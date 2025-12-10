"""
Quality Scoring Service for Processed Articles

This module provides comprehensive quality scoring for processed articles.
It evaluates multiple dimensions to produce a 0-100 quality score:
- Classification quality (25%)
- Sentiment analysis quality (20%)
- Entity extraction quality (20%)
- Cross-source validation (20%)
- Completeness (15%)

Quality bands: Excellent (90+), Good (75-89), Fair (50-74), Poor (25-49), Unreliable (<25)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# ============================================================================
# Quality Models
# ============================================================================

class QualityBand(str, Enum):
    """Quality band classification."""
    EXCELLENT = "excellent"   # 90-100
    GOOD = "good"             # 75-89
    FAIR = "fair"             # 50-74
    POOR = "poor"             # 25-49
    UNRELIABLE = "unreliable" # 0-24


class QualityDimension(str, Enum):
    """Quality scoring dimensions."""
    CLASSIFICATION = "classification"
    SENTIMENT = "sentiment"
    ENTITY = "entity"
    VALIDATION = "validation"
    COMPLETENESS = "completeness"


# Default weights for quality dimensions
DEFAULT_WEIGHTS = {
    QualityDimension.CLASSIFICATION: 0.25,
    QualityDimension.SENTIMENT: 0.20,
    QualityDimension.ENTITY: 0.20,
    QualityDimension.VALIDATION: 0.20,
    QualityDimension.COMPLETENESS: 0.15
}


# ============================================================================
# Quality Result Dataclasses
# ============================================================================

@dataclass
class DimensionScore:
    """
    Score for a single quality dimension.
    """
    dimension: QualityDimension
    score: float  # 0-100
    weight: float  # 0-1
    weighted_score: float  # score * weight
    
    # Breakdown of sub-components
    components: Dict[str, float] = field(default_factory=dict)
    
    # Issues found
    issues: List[str] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 2),
            "weight": self.weight,
            "weighted_score": round(self.weighted_score, 2),
            "components": {k: round(v, 2) for k, v in self.components.items()},
            "issues": self.issues,
            "recommendations": self.recommendations
        }


@dataclass
class QualityScore:
    """
    Complete quality score result for an article.
    """
    # Overall score
    overall_score: float  # 0-100
    quality_band: QualityBand
    
    # Dimension scores
    dimension_scores: Dict[QualityDimension, DimensionScore] = field(default_factory=dict)
    
    # Summary
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    processing_source: str = "enhanced"  # "enhanced" or "basic"
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "overall_score": round(self.overall_score, 2),
            "quality_band": self.quality_band.value,
            "dimensions": {
                dim.value: score.to_dict()
                for dim, score in self.dimension_scores.items()
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "processing_source": self.processing_source,
            "confidence": self.confidence
        }
    
    def is_acceptable(self, threshold: float = 50.0) -> bool:
        """Check if quality meets threshold."""
        return self.overall_score >= threshold
    
    def get_lowest_dimension(self) -> Optional[QualityDimension]:
        """Get the dimension with lowest score."""
        if not self.dimension_scores:
            return None
        return min(
            self.dimension_scores.keys(),
            key=lambda d: self.dimension_scores[d].score
        )


def score_to_band(score: float) -> QualityBand:
    """Convert numeric score to quality band."""
    if score >= 90:
        return QualityBand.EXCELLENT
    elif score >= 75:
        return QualityBand.GOOD
    elif score >= 50:
        return QualityBand.FAIR
    elif score >= 25:
        return QualityBand.POOR
    else:
        return QualityBand.UNRELIABLE


# ============================================================================
# Quality Scorer Service
# ============================================================================

class QualityScorer:
    """
    Comprehensive quality scoring for processed articles.
    
    Evaluates multiple dimensions and produces a 0-100 quality score
    with detailed breakdown and recommendations.
    
    Usage:
        scorer = QualityScorer()
        quality = scorer.score(
            classification_result=classification,
            sentiment_result=sentiment,
            entity_result=entities,
            validation_result=validation,
            article_metadata=metadata
        )
    """
    
    def __init__(
        self,
        weights: Optional[Dict[QualityDimension, float]] = None,
        min_acceptable_score: float = 50.0
    ):
        """
        Initialize Quality Scorer.
        
        Args:
            weights: Custom dimension weights (must sum to 1.0)
            min_acceptable_score: Minimum score for acceptable quality
        """
        self.weights = weights or DEFAULT_WEIGHTS
        self.min_acceptable_score = min_acceptable_score
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            logger.warning(f"Weights sum to {weight_sum}, normalizing...")
            self.weights = {k: v / weight_sum for k, v in self.weights.items()}
        
        # Statistics
        self._total_scored = 0
        self._score_distribution = {band: 0 for band in QualityBand}
    
    def score(
        self,
        classification_result: Optional[Dict[str, Any]] = None,
        sentiment_result: Optional[Dict[str, Any]] = None,
        entity_result: Optional[Dict[str, Any]] = None,
        validation_result: Optional[Dict[str, Any]] = None,
        article_metadata: Optional[Dict[str, Any]] = None
    ) -> QualityScore:
        """
        Calculate comprehensive quality score.
        
        Args:
            classification_result: Result from LLMClassifier
            sentiment_result: Result from AdvancedSentimentAnalyzer
            entity_result: Result from SmartEntityExtractor
            validation_result: Result from cross-source validation
            article_metadata: Article metadata (title, text, source, etc.)
        
        Returns:
            QualityScore with full breakdown
        """
        self._total_scored += 1
        
        dimension_scores = {}
        
        # Score each dimension
        dimension_scores[QualityDimension.CLASSIFICATION] = self._score_classification(
            classification_result
        )
        dimension_scores[QualityDimension.SENTIMENT] = self._score_sentiment(
            sentiment_result
        )
        dimension_scores[QualityDimension.ENTITY] = self._score_entity(
            entity_result
        )
        dimension_scores[QualityDimension.VALIDATION] = self._score_validation(
            validation_result
        )
        dimension_scores[QualityDimension.COMPLETENESS] = self._score_completeness(
            article_metadata,
            classification_result,
            sentiment_result,
            entity_result
        )
        
        # Calculate overall score
        overall_score = sum(
            score.weighted_score for score in dimension_scores.values()
        )
        
        # Determine quality band
        quality_band = score_to_band(overall_score)
        self._score_distribution[quality_band] += 1
        
        # Generate summary
        strengths, weaknesses, recommendations = self._generate_summary(
            dimension_scores, overall_score
        )
        
        return QualityScore(
            overall_score=overall_score,
            quality_band=quality_band,
            dimension_scores=dimension_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            processing_source="enhanced",
            confidence=self._calculate_confidence(dimension_scores)
        )
    
    def _score_classification(
        self,
        result: Optional[Dict[str, Any]]
    ) -> DimensionScore:
        """Score classification quality."""
        weight = self.weights[QualityDimension.CLASSIFICATION]
        issues = []
        recommendations = []
        components = {}
        
        if not result:
            return DimensionScore(
                dimension=QualityDimension.CLASSIFICATION,
                score=0,
                weight=weight,
                weighted_score=0,
                issues=["No classification result available"],
                recommendations=["Ensure classification is performed"]
            )
        
        score = 0
        
        # Confidence component (40%)
        confidence = result.get("primary_confidence", result.get("confidence", 0))
        confidence_score = confidence * 100
        components["confidence"] = confidence_score
        score += confidence_score * 0.4
        
        if confidence < 0.6:
            issues.append(f"Low classification confidence: {confidence:.2f}")
            recommendations.append("Review classification for ambiguous content")
        
        # Multi-category coverage (20%)
        all_categories = result.get("all_categories", {})
        category_count = len([c for c, conf in all_categories.items() if conf > 0.2])
        category_score = min(100, category_count * 25)  # Up to 4 categories = 100
        components["category_coverage"] = category_score
        score += category_score * 0.2
        
        # Sub-theme identification (20%)
        sub_themes = result.get("sub_themes", {})
        has_sub_themes = any(len(themes) > 0 for themes in sub_themes.values())
        sub_theme_score = 100 if has_sub_themes else 50
        components["sub_themes"] = sub_theme_score
        score += sub_theme_score * 0.2
        
        if not has_sub_themes:
            issues.append("No sub-themes identified")
            recommendations.append("Consider more detailed topic analysis")
        
        # Source quality (20%)
        source = result.get("classification_source", "unknown")
        source_scores = {"llm": 100, "hybrid": 80, "rule_fallback": 50, "unknown": 30}
        source_score = source_scores.get(source, 30)
        components["source_quality"] = source_score
        score += source_score * 0.2
        
        if source == "rule_fallback":
            issues.append("Classification used rule-based fallback")
            recommendations.append("LLM classification recommended for better accuracy")
        
        return DimensionScore(
            dimension=QualityDimension.CLASSIFICATION,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            components=components,
            issues=issues,
            recommendations=recommendations
        )
    
    def _score_sentiment(
        self,
        result: Optional[Dict[str, Any]]
    ) -> DimensionScore:
        """Score sentiment analysis quality."""
        weight = self.weights[QualityDimension.SENTIMENT]
        issues = []
        recommendations = []
        components = {}
        
        if not result:
            return DimensionScore(
                dimension=QualityDimension.SENTIMENT,
                score=0,
                weight=weight,
                weighted_score=0,
                issues=["No sentiment result available"],
                recommendations=["Ensure sentiment analysis is performed"]
            )
        
        score = 0
        
        # Overall confidence (30%)
        overall = result.get("overall", {})
        confidence = overall.get("confidence", 0.5)
        confidence_score = confidence * 100
        components["confidence"] = confidence_score
        score += confidence_score * 0.3
        
        # Multi-dimensional coverage (30%)
        dimensions = result.get("dimensions", {})
        dimension_count = len(dimensions)
        dim_score = min(100, dimension_count * 33)  # 3+ dimensions = 100
        components["dimensional_coverage"] = dim_score
        score += dim_score * 0.3
        
        if dimension_count < 3:
            issues.append(f"Only {dimension_count} sentiment dimensions analyzed")
            recommendations.append("Use advanced sentiment for multi-dimensional analysis")
        
        # Driver identification (20%)
        drivers = result.get("drivers", {})
        has_drivers = len(drivers.get("positive", [])) + len(drivers.get("negative", [])) > 0
        driver_score = 100 if has_drivers else 40
        components["driver_identification"] = driver_score
        score += driver_score * 0.2
        
        if not has_drivers:
            issues.append("No sentiment drivers identified")
        
        # Source quality (20%)
        source = result.get("analysis_source", "unknown")
        source_scores = {"llm": 100, "basic_fallback": 60, "keyword_fallback": 40, "quick_check": 50}
        source_score = source_scores.get(source, 40)
        components["source_quality"] = source_score
        score += source_score * 0.2
        
        return DimensionScore(
            dimension=QualityDimension.SENTIMENT,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            components=components,
            issues=issues,
            recommendations=recommendations
        )
    
    def _score_entity(
        self,
        result: Optional[Dict[str, Any]]
    ) -> DimensionScore:
        """Score entity extraction quality."""
        weight = self.weights[QualityDimension.ENTITY]
        issues = []
        recommendations = []
        components = {}
        
        if not result:
            return DimensionScore(
                dimension=QualityDimension.ENTITY,
                score=0,
                weight=weight,
                weighted_score=0,
                issues=["No entity result available"],
                recommendations=["Ensure entity extraction is performed"]
            )
        
        score = 0
        
        # Entity count (30%)
        entity_count = result.get("entity_count", 0)
        # Reasonable range: 3-15 entities for most articles
        if entity_count >= 5:
            count_score = 100
        elif entity_count >= 3:
            count_score = 80
        elif entity_count >= 1:
            count_score = 50
        else:
            count_score = 20
            issues.append("Very few entities extracted")
        components["entity_count"] = count_score
        score += count_score * 0.3
        
        # Entity diversity (25%)
        entities_by_type = result.get("entities_by_type", {})
        type_count = len(entities_by_type)
        diversity_score = min(100, type_count * 20)  # 5+ types = 100
        components["entity_diversity"] = diversity_score
        score += diversity_score * 0.25
        
        if type_count < 3:
            issues.append(f"Limited entity type diversity: {type_count} types")
        
        # Relationship extraction (25%)
        relationship_count = result.get("relationship_count", 0)
        if relationship_count >= 3:
            rel_score = 100
        elif relationship_count >= 1:
            rel_score = 70
        else:
            rel_score = 40
            issues.append("No entity relationships extracted")
        components["relationships"] = rel_score
        score += rel_score * 0.25
        
        # Source quality (20%)
        source = result.get("extraction_source", "unknown")
        source_scores = {"llm": 100, "basic_fallback": 60, "regex_fallback": 40}
        source_score = source_scores.get(source, 40)
        components["source_quality"] = source_score
        score += source_score * 0.2
        
        return DimensionScore(
            dimension=QualityDimension.ENTITY,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            components=components,
            issues=issues,
            recommendations=recommendations
        )
    
    def _score_validation(
        self,
        result: Optional[Dict[str, Any]]
    ) -> DimensionScore:
        """Score cross-source validation quality."""
        weight = self.weights[QualityDimension.VALIDATION]
        issues = []
        recommendations = []
        components = {}
        
        if not result:
            # Validation is optional, give neutral score
            return DimensionScore(
                dimension=QualityDimension.VALIDATION,
                score=50,
                weight=weight,
                weighted_score=50 * weight,
                issues=["Cross-source validation not performed"],
                recommendations=["Consider enabling validation for higher confidence"],
                components={"default": 50}
            )
        
        score = 0
        
        # Trust score (40%)
        trust_score = result.get("trust_score", 0.5) * 100
        components["trust_score"] = trust_score
        score += trust_score * 0.4
        
        if trust_score < 50:
            issues.append(f"Low trust score: {trust_score:.0f}%")
            recommendations.append("Verify claims with additional sources")
        
        # Source count (25%)
        source_count = result.get("source_count", 1)
        if source_count >= 3:
            source_score = 100
        elif source_count == 2:
            source_score = 75
        else:
            source_score = 50
            issues.append("Single source - cannot corroborate")
        components["source_count"] = source_score
        score += source_score * 0.25
        
        # Corroboration rate (35%)
        corroboration_rate = result.get("corroboration_rate", 0.5) * 100
        components["corroboration"] = corroboration_rate
        score += corroboration_rate * 0.35
        
        if corroboration_rate < 50:
            issues.append("Low corroboration from other sources")
            recommendations.append("Cross-reference with additional sources")
        
        return DimensionScore(
            dimension=QualityDimension.VALIDATION,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            components=components,
            issues=issues,
            recommendations=recommendations
        )
    
    def _score_completeness(
        self,
        metadata: Optional[Dict[str, Any]],
        classification: Optional[Dict[str, Any]],
        sentiment: Optional[Dict[str, Any]],
        entity: Optional[Dict[str, Any]]
    ) -> DimensionScore:
        """Score article processing completeness."""
        weight = self.weights[QualityDimension.COMPLETENESS]
        issues = []
        recommendations = []
        components = {}
        
        score = 0
        
        # Metadata completeness (30%)
        if metadata:
            required_fields = ["title", "text", "source", "published_at"]
            present_fields = sum(1 for f in required_fields if metadata.get(f))
            metadata_score = (present_fields / len(required_fields)) * 100
            
            missing = [f for f in required_fields if not metadata.get(f)]
            if missing:
                issues.append(f"Missing metadata: {', '.join(missing)}")
        else:
            metadata_score = 20
            issues.append("No article metadata provided")
        components["metadata"] = metadata_score
        score += metadata_score * 0.3
        
        # Text quality (25%)
        if metadata and metadata.get("text"):
            text = metadata["text"]
            text_length = len(text)
            if text_length >= 500:
                text_score = 100
            elif text_length >= 200:
                text_score = 75
            elif text_length >= 50:
                text_score = 50
            else:
                text_score = 25
                issues.append("Very short article text")
        else:
            text_score = 0
            issues.append("No article text available")
        components["text_quality"] = text_score
        score += text_score * 0.25
        
        # Processing completeness (45%)
        processing_count = sum([
            1 if classification else 0,
            1 if sentiment else 0,
            1 if entity else 0
        ])
        processing_score = (processing_count / 3) * 100
        
        if processing_count < 3:
            missing_processing = []
            if not classification:
                missing_processing.append("classification")
            if not sentiment:
                missing_processing.append("sentiment")
            if not entity:
                missing_processing.append("entity extraction")
            issues.append(f"Incomplete processing: missing {', '.join(missing_processing)}")
        
        components["processing_completeness"] = processing_score
        score += processing_score * 0.45
        
        return DimensionScore(
            dimension=QualityDimension.COMPLETENESS,
            score=score,
            weight=weight,
            weighted_score=score * weight,
            components=components,
            issues=issues,
            recommendations=recommendations
        )
    
    def _generate_summary(
        self,
        dimension_scores: Dict[QualityDimension, DimensionScore],
        overall_score: float
    ) -> tuple:
        """Generate summary of strengths, weaknesses, and recommendations."""
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Identify strengths (scores >= 80)
        for dim, score in dimension_scores.items():
            if score.score >= 80:
                strengths.append(f"Strong {dim.value} quality ({score.score:.0f}%)")
            elif score.score < 50:
                weaknesses.append(f"Weak {dim.value} quality ({score.score:.0f}%)")
        
        # Aggregate recommendations
        for score in dimension_scores.values():
            recommendations.extend(score.recommendations)
        
        # Remove duplicates
        recommendations = list(set(recommendations))[:5]
        
        # Add overall assessment
        if overall_score >= 90:
            strengths.insert(0, "Excellent overall quality - highly reliable")
        elif overall_score >= 75:
            strengths.insert(0, "Good overall quality - reliable for analysis")
        elif overall_score < 50:
            weaknesses.insert(0, "Overall quality below acceptable threshold")
            recommendations.insert(0, "Review and re-process article for better results")
        
        return strengths[:5], weaknesses[:5], recommendations[:5]
    
    def _calculate_confidence(
        self,
        dimension_scores: Dict[QualityDimension, DimensionScore]
    ) -> float:
        """Calculate confidence in the quality score itself."""
        # Based on consistency of dimension scores
        scores = [s.score for s in dimension_scores.values()]
        if not scores:
            return 0.5
        
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Lower variance = higher confidence
        # Max std_dev would be ~50 (scores ranging 0-100)
        confidence = max(0.5, 1.0 - (std_dev / 50))
        return min(1.0, confidence)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get quality scoring statistics."""
        total = self._total_scored
        return {
            "total_scored": total,
            "score_distribution": {
                band.value: {
                    "count": count,
                    "percentage": (count / total * 100) if total > 0 else 0
                }
                for band, count in self._score_distribution.items()
            }
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_quality_scorer(
    weights: Optional[Dict[str, float]] = None,
    min_acceptable_score: float = 50.0
) -> QualityScorer:
    """
    Factory function to create a QualityScorer instance.
    
    Args:
        weights: Custom dimension weights (classification, sentiment, entity, validation, completeness)
        min_acceptable_score: Minimum score for acceptable quality
    
    Returns:
        Configured QualityScorer instance
    """
    if weights:
        # Convert string keys to QualityDimension
        typed_weights = {}
        for key, value in weights.items():
            try:
                dim = QualityDimension(key)
                typed_weights[dim] = value
            except ValueError:
                logger.warning(f"Unknown quality dimension: {key}")
        weights = typed_weights if typed_weights else None
    
    return QualityScorer(
        weights=weights,
        min_acceptable_score=min_acceptable_score
    )
