"""
Claim Extractor

Extracts and normalizes key claims from article content for cross-source validation.

Features:
- Entity extraction (who, what, when, where)
- Numeric claim extraction (percentages, amounts, counts)
- Event claim extraction
- Claim normalization and fingerprinting
"""

import logging
import re
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Types of extractable claims."""
    NUMERIC = "numeric"           # Numbers, percentages, amounts
    EVENT = "event"               # Events, actions, happenings
    STATEMENT = "statement"       # Quotes, announcements
    PREDICTION = "prediction"     # Forecasts, predictions
    FACTUAL = "factual"          # Facts, statistics
    ATTRIBUTION = "attribution"   # Claims attributed to someone


class EntityType(Enum):
    """Types of entities in claims."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"
    QUANTITY = "quantity"


@dataclass
class ExtractedEntity:
    """An extracted entity from text."""
    text: str
    entity_type: EntityType
    normalized: str
    start_pos: int = 0
    end_pos: int = 0
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "type": self.entity_type.value,
            "normalized": self.normalized,
            "confidence": round(self.confidence, 2)
        }


@dataclass
class ExtractedClaim:
    """A claim extracted from an article."""
    claim_id: str
    claim_type: ClaimType
    text: str                      # Original claim text
    normalized: str                # Normalized claim text
    fingerprint: str               # Hash for matching
    
    # Entities involved
    entities: List[ExtractedEntity] = field(default_factory=list)
    
    # Context
    source_article_id: str = ""
    source_name: str = ""
    extracted_at: datetime = field(default_factory=datetime.utcnow)
    
    # Claim specifics
    subject: str = ""              # Who/what the claim is about
    predicate: str = ""            # What is claimed
    object: str = ""               # Target of the claim
    
    # Numeric claims
    numeric_value: Optional[float] = None
    numeric_unit: str = ""
    numeric_context: str = ""      # e.g., "increased by", "reached"
    
    # Confidence
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "type": self.claim_type.value,
            "text": self.text,
            "normalized": self.normalized,
            "fingerprint": self.fingerprint,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "entities": [e.to_dict() for e in self.entities],
            "numeric_value": self.numeric_value,
            "numeric_unit": self.numeric_unit,
            "confidence": round(self.confidence, 2),
            "source": self.source_name
        }


class ClaimExtractor:
    """
    Extracts claims from article content.
    
    Uses pattern matching and NLP-like heuristics to identify:
    - Numeric claims (X increased/decreased by Y%)
    - Event claims (X happened at Y)
    - Statement claims (X said Y)
    - Factual claims (X is Y)
    """
    
    # Patterns for numeric extraction
    NUMERIC_PATTERNS = [
        # Percentages
        (r'(\d+(?:\.\d+)?)\s*(?:percent|%)', 'percentage'),
        # Currency amounts
        (r'(?:Rs\.?|LKR|USD|\$)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion)?', 'money'),
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion)?\s*(?:rupees|dollars)', 'money'),
        # General numbers with units
        (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(people|persons|deaths|cases|vehicles|units|tons|kg|km)', 'quantity'),
    ]
    
    # Patterns for claim context
    INCREASE_PATTERNS = [
        r'increas(?:ed?|ing)',
        r'rose?|risen|rising',
        r'grew|growing|growth',
        r'jump(?:ed)?|jumped',
        r'surge(?:d)?|surging',
        r'climb(?:ed)?|climbing',
    ]
    
    DECREASE_PATTERNS = [
        r'decreas(?:ed?|ing)',
        r'fell|fallen|falling',
        r'drop(?:ped)?|dropping',
        r'declin(?:ed?|ing)',
        r'shr(?:a|u)nk|shrinking',
        r'plung(?:ed)?|plunging',
    ]
    
    # Statement attribution patterns
    ATTRIBUTION_PATTERNS = [
        r'(?P<speaker>[A-Z][a-z]+ [A-Z][a-z]+)\s+said\s+(?:that\s+)?["\']?(?P<statement>.+?)["\']?(?:\.|$)',
        r'according to\s+(?P<speaker>[A-Z][^,]+),?\s+(?P<statement>.+?)(?:\.|$)',
        r'(?P<speaker>[A-Z][a-z]+ [A-Z][a-z]+)\s+announced\s+(?:that\s+)?(?P<statement>.+?)(?:\.|$)',
        r'(?P<speaker>[A-Z][a-z]+ [A-Z][a-z]+)\s+stated\s+(?:that\s+)?["\']?(?P<statement>.+?)["\']?(?:\.|$)',
    ]
    
    # Event patterns
    EVENT_PATTERNS = [
        r'(?P<event>flood(?:s|ing)?|earthquake|storm|cyclone|drought)\s+(?:hit|struck|affected)\s+(?P<location>[A-Z][a-z]+)',
        r'(?P<event>protest(?:s)?|strike(?:s)?|demonstration(?:s)?)\s+(?:in|at|near)\s+(?P<location>[A-Z][a-z]+)',
        r'(?P<event>accident|crash|collision)\s+(?:on|at|near)\s+(?P<location>.+?)(?:,|\.|$)',
    ]
    
    # Organization patterns
    ORG_PATTERNS = [
        r'\b(Central Bank|CBSL|IMF|World Bank|Government|Ministry of [A-Z][a-z]+)\b',
        r'\b([A-Z]{2,})\b',  # Acronyms
    ]
    
    def __init__(self):
        """Initialize the claim extractor."""
        self._compile_patterns()
        logger.info("ClaimExtractor initialized")
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency."""
        self._numeric_compiled = [
            (re.compile(pattern, re.IGNORECASE), unit_type)
            for pattern, unit_type in self.NUMERIC_PATTERNS
        ]
        
        self._increase_compiled = re.compile(
            '|'.join(self.INCREASE_PATTERNS), 
            re.IGNORECASE
        )
        
        self._decrease_compiled = re.compile(
            '|'.join(self.DECREASE_PATTERNS),
            re.IGNORECASE
        )
        
        self._attribution_compiled = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.ATTRIBUTION_PATTERNS
        ]
        
        self._event_compiled = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.EVENT_PATTERNS
        ]
    
    def extract_claims(
        self,
        content: str,
        title: str = "",
        article_id: str = "",
        source_name: str = ""
    ) -> List[ExtractedClaim]:
        """
        Extract all claims from article content.
        
        Args:
            content: Article body text
            title: Article title
            article_id: Article identifier
            source_name: Source name
            
        Returns:
            List of extracted claims
        """
        claims = []
        
        # Combine title and content for extraction
        full_text = f"{title}. {content}" if title else content
        
        # Extract different claim types
        numeric_claims = self._extract_numeric_claims(
            full_text, article_id, source_name
        )
        claims.extend(numeric_claims)
        
        attribution_claims = self._extract_attribution_claims(
            full_text, article_id, source_name
        )
        claims.extend(attribution_claims)
        
        event_claims = self._extract_event_claims(
            full_text, article_id, source_name
        )
        claims.extend(event_claims)
        
        logger.debug(f"Extracted {len(claims)} claims from article {article_id}")
        
        return claims
    
    def _extract_numeric_claims(
        self,
        text: str,
        article_id: str,
        source_name: str
    ) -> List[ExtractedClaim]:
        """Extract numeric claims from text."""
        claims = []
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            for pattern, unit_type in self._numeric_compiled:
                matches = pattern.finditer(sentence)
                
                for match in matches:
                    # Extract the numeric value
                    value_str = match.group(1).replace(',', '')
                    try:
                        value = float(value_str)
                    except ValueError:
                        continue
                    
                    # Check for multiplier
                    multiplier = 1
                    if match.lastindex >= 2 and match.group(2):
                        mult_str = match.group(2).lower()
                        if mult_str == 'million':
                            multiplier = 1_000_000
                        elif mult_str == 'billion':
                            multiplier = 1_000_000_000
                        elif mult_str == 'trillion':
                            multiplier = 1_000_000_000_000
                    
                    value *= multiplier
                    
                    # Determine context (increase/decrease)
                    context = "stated"
                    if self._increase_compiled.search(sentence):
                        context = "increased"
                    elif self._decrease_compiled.search(sentence):
                        context = "decreased"
                    
                    # Create claim
                    claim_text = sentence.strip()
                    normalized = self._normalize_claim(claim_text)
                    fingerprint = self._generate_fingerprint(normalized)
                    
                    claim = ExtractedClaim(
                        claim_id=f"{article_id}_{fingerprint[:8]}",
                        claim_type=ClaimType.NUMERIC,
                        text=claim_text,
                        normalized=normalized,
                        fingerprint=fingerprint,
                        source_article_id=article_id,
                        source_name=source_name,
                        numeric_value=value,
                        numeric_unit=unit_type,
                        numeric_context=context,
                        confidence=0.85
                    )
                    
                    # Extract entities
                    claim.entities = self._extract_entities(sentence)
                    
                    claims.append(claim)
        
        return claims
    
    def _extract_attribution_claims(
        self,
        text: str,
        article_id: str,
        source_name: str
    ) -> List[ExtractedClaim]:
        """Extract statement attribution claims."""
        claims = []
        
        for pattern in self._attribution_compiled:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    speaker = match.group('speaker')
                    statement = match.group('statement')
                except IndexError:
                    continue
                
                claim_text = match.group(0).strip()
                normalized = self._normalize_claim(statement)
                fingerprint = self._generate_fingerprint(normalized)
                
                claim = ExtractedClaim(
                    claim_id=f"{article_id}_{fingerprint[:8]}",
                    claim_type=ClaimType.ATTRIBUTION,
                    text=claim_text,
                    normalized=normalized,
                    fingerprint=fingerprint,
                    source_article_id=article_id,
                    source_name=source_name,
                    subject=speaker,
                    predicate="said",
                    object=statement[:100] if len(statement) > 100 else statement,
                    confidence=0.9
                )
                
                # Add speaker as entity
                claim.entities.append(ExtractedEntity(
                    text=speaker,
                    entity_type=EntityType.PERSON,
                    normalized=speaker.lower(),
                    confidence=0.9
                ))
                
                claims.append(claim)
        
        return claims
    
    def _extract_event_claims(
        self,
        text: str,
        article_id: str,
        source_name: str
    ) -> List[ExtractedClaim]:
        """Extract event claims."""
        claims = []
        
        for pattern in self._event_compiled:
            matches = pattern.finditer(text)
            
            for match in matches:
                try:
                    event = match.group('event')
                    location = match.group('location')
                except IndexError:
                    continue
                
                claim_text = match.group(0).strip()
                normalized = self._normalize_claim(claim_text)
                fingerprint = self._generate_fingerprint(normalized)
                
                claim = ExtractedClaim(
                    claim_id=f"{article_id}_{fingerprint[:8]}",
                    claim_type=ClaimType.EVENT,
                    text=claim_text,
                    normalized=normalized,
                    fingerprint=fingerprint,
                    source_article_id=article_id,
                    source_name=source_name,
                    subject=event,
                    predicate="occurred at",
                    object=location,
                    confidence=0.85
                )
                
                # Add entities
                claim.entities.append(ExtractedEntity(
                    text=location,
                    entity_type=EntityType.LOCATION,
                    normalized=location.lower(),
                    confidence=0.85
                ))
                
                claims.append(claim)
        
        return claims
    
    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities from text."""
        entities = []
        
        # Extract organizations
        org_pattern = re.compile(
            r'\b(Central Bank|CBSL|IMF|World Bank|Government|Ministry of [A-Z][a-z]+|[A-Z]{2,5})\b'
        )
        for match in org_pattern.finditer(text):
            entities.append(ExtractedEntity(
                text=match.group(1),
                entity_type=EntityType.ORGANIZATION,
                normalized=match.group(1).lower(),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.8
            ))
        
        # Extract money
        money_pattern = re.compile(
            r'(?:Rs\.?|LKR|USD|\$)\s*(\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|trillion))?)',
            re.IGNORECASE
        )
        for match in money_pattern.finditer(text):
            entities.append(ExtractedEntity(
                text=match.group(0),
                entity_type=EntityType.MONEY,
                normalized=match.group(0).lower(),
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.9
            ))
        
        # Extract percentages
        pct_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(?:percent|%)')
        for match in pct_pattern.finditer(text):
            entities.append(ExtractedEntity(
                text=match.group(0),
                entity_type=EntityType.PERCENTAGE,
                normalized=match.group(1) + "%",
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=0.95
            ))
        
        # Extract locations (basic heuristic: capitalized words after location prepositions)
        loc_pattern = re.compile(r'\b(?:in|at|near|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b')
        for match in loc_pattern.finditer(text):
            entities.append(ExtractedEntity(
                text=match.group(1),
                entity_type=EntityType.LOCATION,
                normalized=match.group(1).lower(),
                start_pos=match.start(1),
                end_pos=match.end(1),
                confidence=0.7
            ))
        
        return entities
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _normalize_claim(self, claim_text: str) -> str:
        """Normalize claim text for comparison."""
        # Lowercase
        normalized = claim_text.lower()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove punctuation except numbers and %
        normalized = re.sub(r'[^\w\s%.]', '', normalized)
        
        # Normalize numbers (remove commas)
        normalized = re.sub(r'(\d),(\d)', r'\1\2', normalized)
        
        return normalized
    
    def _generate_fingerprint(self, normalized_text: str) -> str:
        """Generate a fingerprint hash for a claim."""
        # Extract key tokens (remove stopwords)
        stopwords = {'the', 'a', 'an', 'is', 'was', 'were', 'are', 'been', 'be',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', 'shall', 'can',
                     'that', 'this', 'these', 'those', 'it', 'its', 'to', 'of',
                     'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                     'through', 'during', 'before', 'after', 'above', 'below',
                     'between', 'and', 'but', 'or', 'nor', 'so', 'yet'}
        
        tokens = normalized_text.split()
        key_tokens = [t for t in tokens if t not in stopwords]
        
        # Sort tokens for order-independent matching
        key_tokens.sort()
        
        # Generate hash
        fingerprint_text = ' '.join(key_tokens)
        return hashlib.md5(fingerprint_text.encode()).hexdigest()
    
    def find_matching_claims(
        self,
        claim: ExtractedClaim,
        other_claims: List[ExtractedClaim],
        threshold: float = 0.8
    ) -> List[Tuple[ExtractedClaim, float]]:
        """
        Find claims that match a given claim.
        
        Args:
            claim: Claim to match
            other_claims: Claims to search
            threshold: Minimum similarity threshold
            
        Returns:
            List of (claim, similarity) tuples
        """
        matches = []
        
        for other in other_claims:
            # Skip same article
            if other.source_article_id == claim.source_article_id:
                continue
            
            # Check fingerprint match (exact)
            if claim.fingerprint == other.fingerprint:
                matches.append((other, 1.0))
                continue
            
            # Check type match
            if claim.claim_type != other.claim_type:
                continue
            
            # For numeric claims, compare values
            if claim.claim_type == ClaimType.NUMERIC:
                if claim.numeric_value and other.numeric_value:
                    # Calculate relative difference
                    max_val = max(abs(claim.numeric_value), abs(other.numeric_value))
                    if max_val > 0:
                        diff = abs(claim.numeric_value - other.numeric_value) / max_val
                        similarity = 1 - min(diff, 1)
                        if similarity >= threshold:
                            matches.append((other, similarity))
            
            # For other claims, compare normalized text
            else:
                similarity = self._calculate_text_similarity(
                    claim.normalized, other.normalized
                )
                if similarity >= threshold:
                    matches.append((other, similarity))
        
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
