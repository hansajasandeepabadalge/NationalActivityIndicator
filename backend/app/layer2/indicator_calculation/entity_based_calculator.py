from typing import Dict
from collections import Counter
from app.layer2.nlp_processing.entity_schemas import ExtractedEntities

class EntityBasedIndicatorCalculator:

    def calculate_currency_stability(self, entities: ExtractedEntities) -> float:
        """
        Calculate ECO_CURRENCY_STABILITY indicator

        Logic:
        - If article mentions currency amounts → 0.6-0.8 confidence
        - Multiple currencies mentioned → higher confidence (0.7-0.8)
        - Amounts > Rs. 1 billion → higher confidence (0.8+)
        - Percentage changes mentioned → add 0.1 confidence
        """
        if not entities.amounts:
            return 0.0

        confidence = 0.6

        currencies = set(amt.currency for amt in entities.amounts)
        if len(currencies) > 1:
            confidence += 0.1

        large_amounts = [amt for amt in entities.amounts if amt.amount > 1_000_000_000]
        if large_amounts:
            confidence += 0.1

        if entities.percentages:
            confidence += 0.1

        return min(confidence, 0.9)

    def calculate_geographic_scope(self, entities: ExtractedEntities) -> float:
        """
        Calculate POL_GEOGRAPHIC_SCOPE indicator

        Logic:
        - Use Herfindahl-Hirschman Index (HHI) for concentration
        - Many unique locations → high confidence (diverse scope)
        - Single location dominance → lower confidence (local scope)
        """
        if not entities.locations:
            return 0.0

        location_counts = Counter(loc.text.lower() for loc in entities.locations)
        total_mentions = sum(location_counts.values())

        hhi = sum((count / total_mentions) ** 2 for count in location_counts.values())

        diversity_score = 1 - hhi

        confidence = 0.4 + (diversity_score * 0.5)

        if len(location_counts) >= 3:
            confidence = min(confidence + 0.1, 0.9)

        return confidence

    def calculate_all_indicators(self, entities: ExtractedEntities) -> Dict[str, float]:
        """Calculate all entity-based indicators"""
        return {
            "ECO_CURRENCY_STABILITY": self.calculate_currency_stability(entities),
            "POL_GEOGRAPHIC_SCOPE": self.calculate_geographic_scope(entities)
        }
