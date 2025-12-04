"""
Layer 4: Tier 2 - Pattern-Based Risk Detection

Detects risks by matching current situation to historical patterns
Uses cosine similarity for pattern matching
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import logging
from math import sqrt

from app.layer4.schemas.risk_schemas import DetectedRisk
from app.layer4.mock_data.layer3_mock_generator import OperationalIndicators
from app.layer4.mock_data.historical_patterns_mock import MockHistoricalPatterns

logger = logging.getLogger(__name__)


class PatternBasedRiskDetector:
    """
    Tier 2: Pattern-Based Risk Detection

    Identifies risks by comparing current indicators to historical patterns
    Confidence based on similarity score (threshold: 0.75)
    """

    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold
        self.historical_patterns = MockHistoricalPatterns()
        logger.info(f"Loaded {len(self.historical_patterns.get_all_patterns())} historical patterns")

    def calculate_similarity(
        self,
        current_indicators: Dict[str, float],
        pattern_profile: Dict[str, float]
    ) -> float:
        """
        Calculate cosine similarity between current indicators and pattern

        Args:
            current_indicators: Current operational indicators
            pattern_profile: Historical pattern indicator profile

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Get common indicators
        common_indicators = set(current_indicators.keys()) & set(pattern_profile.keys())

        if not common_indicators:
            return 0.0

        # Calculate dot product
        dot_product = sum(
            current_indicators[ind] * pattern_profile[ind]
            for ind in common_indicators
        )

        # Calculate magnitudes
        current_magnitude = sqrt(sum(
            current_indicators[ind] ** 2
            for ind in common_indicators
        ))

        pattern_magnitude = sqrt(sum(
            pattern_profile[ind] ** 2
            for ind in common_indicators
        ))

        if current_magnitude == 0 or pattern_magnitude == 0:
            return 0.0

        # Cosine similarity
        similarity = dot_product / (current_magnitude * pattern_magnitude)

        # Normalize to 0-1 range (cosine can be -1 to 1, but indicators are all positive)
        similarity = max(0.0, min(1.0, similarity))

        return similarity

    def _generate_risk_from_pattern(
        self,
        company_id: str,
        industry: str,
        pattern: Dict[str, Any],
        similarity: float,
        current_indicators: OperationalIndicators
    ) -> Optional[DetectedRisk]:
        """Generate a risk from a matched pattern"""

        # Only create risk for negative patterns (not opportunities)
        if pattern.get('severity') == 'positive':
            return None

        # Get outcome data for industry
        outcomes = pattern.get('outcomes', {})
        industry_outcome = outcomes.get(industry, {})

        if not industry_outcome:
            # Use average outcome if industry-specific not available
            if outcomes:
                industry_outcome = list(outcomes.values())[0]
            else:
                return None

        # Calculate impact based on historical outcome
        revenue_impact = abs(industry_outcome.get('revenue_impact', -0.20))
        cost_increase = industry_outcome.get('cost_increase', 0.15)
        duration_days = industry_outcome.get('duration_days', 30)

        # Map to impact score (0-10)
        impact_score = min(10.0, (revenue_impact + cost_increase) * 10)

        # Probability is the similarity score
        probability = similarity

        # Urgency based on severity
        severity_map = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2
        }
        urgency = severity_map.get(pattern.get('severity', 'medium'), 3)

        # Confidence is the similarity score
        confidence = similarity

        # Calculate final score
        final_score = probability * impact_score * urgency * confidence

        # Classify severity
        if final_score >= 40:
            severity_level = "critical"
        elif final_score >= 30:
            severity_level = "high"
        elif final_score >= 15:
            severity_level = "medium"
        else:
            severity_level = "low"

        # Generate description
        description = self._generate_pattern_description(
            pattern, industry_outcome, similarity, current_indicators
        )

        # Get lessons learned
        lessons_learned = pattern.get('lessons_learned', [])
        lessons_text = " | ".join(lessons_learned[:3]) if lessons_learned else "No historical lessons available"

        # Create detected risk
        risk = DetectedRisk(
            risk_code=f"PATTERN_{pattern['pattern_id'].upper()}",
            company_id=company_id,
            title=f"Pattern Match: {pattern['pattern_name']}",
            description=description,
            category="operational",  # Default category
            probability=Decimal(str(round(probability, 2))),
            impact=Decimal(str(round(impact_score, 2))),
            urgency=urgency,
            confidence=Decimal(str(round(confidence, 2))),
            final_score=Decimal(str(round(final_score, 2))),
            severity_level=severity_level,
            triggering_indicators={
                "pattern_id": pattern['pattern_id'],
                "similarity_score": similarity,
                "historical_date": pattern['event_date'].isoformat(),
                "matched_indicators": pattern.get('indicator_profile', {}),
                "lessons_learned": lessons_text
            },
            detection_method="pattern",
            reasoning=self._generate_pattern_reasoning(pattern, similarity, industry_outcome),
            expected_duration_hours=duration_days * 24,
            is_urgent=urgency >= 4,
            requires_immediate_action=severity_level in ["critical", "high"]
        )

        return risk

    def _generate_pattern_description(
        self,
        pattern: Dict[str, Any],
        industry_outcome: Dict[str, Any],
        similarity: float,
        current_indicators: OperationalIndicators
    ) -> str:
        """Generate descriptive text for pattern-matched risk"""

        revenue_impact = industry_outcome.get('revenue_impact', -0.20)
        cost_increase = industry_outcome.get('cost_increase', 0.15)
        duration_days = industry_outcome.get('duration_days', 30)

        description = (
            f"Current situation shows {similarity*100:.0f}% similarity to '{pattern['pattern_name']}' "
            f"which occurred on {pattern['event_date'].strftime('%B %Y')}. "
            f"\n\nHistorical Impact: Revenue {revenue_impact:+.1%}, Costs {cost_increase:+.1%}, "
            f"Duration: {duration_days} days. "
            f"\n\n{pattern.get('description', '')}"
        )

        return description

    def _generate_pattern_reasoning(
        self,
        pattern: Dict[str, Any],
        similarity: float,
        industry_outcome: Dict[str, Any]
    ) -> str:
        """Generate reasoning for pattern detection"""

        reasoning = (
            f"Pattern-based detection with {similarity:.2%} similarity to historical event. "
            f"Matched {len(pattern.get('indicator_profile', {}))} operational indicators. "
            f"Historical precedent suggests {abs(industry_outcome.get('revenue_impact', 0.20)):.0%} impact over "
            f"{industry_outcome.get('duration_days', 30)} days."
        )

        return reasoning

    def detect_risks(
        self,
        company_id: str,
        industry: str,
        indicators: OperationalIndicators,
        company_profile: Optional[Dict[str, Any]] = None
    ) -> List[DetectedRisk]:
        """
        Detect risks by matching to historical patterns

        Args:
            company_id: Company identifier
            industry: Company industry
            indicators: Current operational indicators
            company_profile: Optional company profile

        Returns:
            List of detected risks from pattern matching
        """
        detected_risks = []

        # Convert indicators to dict
        current_indicators = indicators.dict()

        # Get patterns relevant to industry
        relevant_patterns = self.historical_patterns.get_patterns_by_industry(industry)

        logger.info(f"Checking {len(relevant_patterns)} patterns for industry {industry}")

        for pattern in relevant_patterns:
            # Skip if no indicator profile
            if 'indicator_profile' not in pattern:
                continue

            # Calculate similarity
            similarity = self.calculate_similarity(
                current_indicators,
                pattern['indicator_profile']
            )

            logger.debug(f"Pattern {pattern['pattern_id']}: similarity = {similarity:.3f}")

            # Check if similarity meets threshold
            if similarity < self.similarity_threshold:
                continue

            # Generate risk from pattern
            risk = self._generate_risk_from_pattern(
                company_id=company_id,
                industry=industry,
                pattern=pattern,
                similarity=similarity,
                current_indicators=indicators
            )

            if risk:
                detected_risks.append(risk)
                logger.info(
                    f"Detected pattern-based risk: {pattern['pattern_id']} "
                    f"for company {company_id} (similarity: {similarity:.2f})"
                )

        return detected_risks

    def find_similar_historical_events(
        self,
        indicators: OperationalIndicators,
        industry: str,
        top_n: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find top N most similar historical events

        Args:
            indicators: Current operational indicators
            industry: Company industry
            top_n: Number of top matches to return

        Returns:
            List of (pattern, similarity_score) tuples
        """
        current_indicators = indicators.dict()
        relevant_patterns = self.historical_patterns.get_patterns_by_industry(industry)

        matches = []

        for pattern in relevant_patterns:
            if 'indicator_profile' not in pattern:
                continue

            similarity = self.calculate_similarity(
                current_indicators,
                pattern['indicator_profile']
            )

            matches.append((pattern, similarity))

        # Sort by similarity (descending)
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches[:top_n]

    def enrich_risk_with_context(
        self,
        risk: DetectedRisk,
        indicators: OperationalIndicators
    ) -> DetectedRisk:
        """
        Enrich a risk with historical context

        Args:
            risk: Detected risk to enrich
            indicators: Current indicators

        Returns:
            Enriched risk with historical context
        """
        # Find similar historical events
        similar_events = self.find_similar_historical_events(
            indicators=indicators,
            industry=risk.category,  # Using category as proxy for industry
            top_n=2
        )

        if not similar_events:
            return risk

        # Add historical context to reasoning
        context_text = "\n\nHistorical Context: "
        for pattern, similarity in similar_events:
            context_text += (
                f"\n- {pattern['pattern_name']} ({pattern['event_date'].strftime('%Y')}) "
                f"had {similarity:.0%} similarity. {pattern.get('description', '')[:100]}..."
            )

        if risk.reasoning:
            risk.reasoning += context_text
        else:
            risk.reasoning = context_text.strip()

        return risk
