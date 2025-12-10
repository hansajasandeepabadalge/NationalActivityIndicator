"""Narrative generator for indicators"""

from typing import Dict
from app.layer2.nlp_processing.entity_schemas import ExtractedEntities
from app.layer2.narrative.schemas import NarrativeText


class NarrativeGenerator:
    """Generate human-readable narratives for indicators"""

    # Emoji mappings
    EMOJI_MAP = {
        "rising": "📈",
        "falling": "📉",
        "stable": "➡️",
        "alert": "⚠️",
        "critical": "🔥",
        "positive": "✅",
        "negative": "❌"
    }

    # Headline templates
    HEADLINE_TEMPLATES = {
        "ECO_CURRENCY_STABILITY": {
            "rising": "{emoji} Currency Stability Strengthening",
            "falling": "{emoji} Currency Volatility Detected",
            "stable": "{emoji} Currency Markets Steady"
        },
        "POL_GEOGRAPHIC_SCOPE": {
            "rising": "{emoji} Geographic Reach Expanding",
            "falling": "{emoji} Focus Narrowing to Local Issues",
            "stable": "{emoji} Geographic Coverage Stable"
        }
    }

    def generate_narrative(
        self,
        article_id: str,
        indicator_id: str,
        confidence: float,
        entities: ExtractedEntities,
        trend: str = "stable"
    ) -> NarrativeText:
        """Generate narrative for an indicator calculation"""

        # Select emoji based on trend and confidence
        emoji = self._select_emoji(trend, confidence)

        # Generate headline
        headline = self._generate_headline(indicator_id, trend, emoji)

        # Generate summary
        summary = self._generate_summary(indicator_id, confidence, entities, trend)

        return NarrativeText(
            article_id=article_id,
            indicator_id=indicator_id,
            headline=headline,
            summary=summary,
            emoji=emoji,
            confidence=confidence
        )

    def _select_emoji(self, trend: str, confidence: float) -> str:
        """Select appropriate emoji"""
        if confidence > 0.8:
            return self.EMOJI_MAP["critical"]
        elif trend == "rising":
            return self.EMOJI_MAP["rising"]
        elif trend == "falling":
            return self.EMOJI_MAP["falling"]
        else:
            return self.EMOJI_MAP["stable"]

    def _generate_headline(self, indicator_id: str, trend: str, emoji: str) -> str:
        """Generate headline from template"""
        templates = self.HEADLINE_TEMPLATES.get(indicator_id, {})
        template = templates.get(trend, f"{emoji} {indicator_id.replace('_', ' ').title()}")
        return template.format(emoji=emoji)

    def _generate_summary(
        self,
        indicator_id: str,
        confidence: float,
        entities: ExtractedEntities,
        trend: str
    ) -> str:
        """Generate 2-3 sentence summary"""

        if indicator_id == "ECO_CURRENCY_STABILITY":
            return self._generate_currency_summary(confidence, entities, trend)
        elif indicator_id == "POL_GEOGRAPHIC_SCOPE":
            return self._generate_geographic_summary(confidence, entities, trend)
        else:
            return f"Indicator {indicator_id} detected with {confidence:.1%} confidence."

    def _generate_currency_summary(
        self,
        confidence: float,
        entities: ExtractedEntities,
        trend: str
    ) -> str:
        """Generate currency stability narrative"""
        parts = []

        # Mention currency amounts
        if entities.amounts:
            currencies = set(amt.currency for amt in entities.amounts)
            if len(currencies) > 1:
                parts.append(f"Multiple currencies mentioned ({', '.join(currencies)})")
            else:
                parts.append(f"{list(currencies)[0]} currency activity detected")

            large_amounts = [amt for amt in entities.amounts if amt.amount > 1_000_000_000]
            if large_amounts:
                parts.append("with large transaction amounts exceeding Rs. 1 billion")

        # Mention percentages
        if entities.percentages:
            parts.append(f"including {len(entities.percentages)} percentage indicators")

        # Add trend context
        if trend == "rising":
            parts.append("Economic indicators show positive momentum")
        elif trend == "falling":
            parts.append("Economic indicators show declining stability")
        else:
            parts.append("Economic indicators remain stable")

        summary = ". ".join(parts)
        if not summary.endswith("."):
            summary += "."
        return summary

    def _generate_geographic_summary(
        self,
        confidence: float,
        entities: ExtractedEntities,
        trend: str
    ) -> str:
        """Generate geographic scope narrative"""
        parts = []

        if entities.locations:
            location_names = [loc.text for loc in entities.locations[:3]]
            parts.append(f"Article mentions {len(entities.locations)} locations including {', '.join(location_names)}")

        if entities.organizations:
            parts.append(f"Coverage includes {len(entities.organizations)} organizations")

        if trend == "rising":
            parts.append("indicating broad national or international scope")
        elif trend == "falling":
            parts.append("indicating narrowed focus on local issues")
        else:
            parts.append("maintaining consistent geographic scope")

        summary = ". ".join(parts)
        if not summary.endswith("."):
            summary += "."
        return summary
