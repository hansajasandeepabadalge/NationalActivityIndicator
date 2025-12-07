"""
Smart Entity Recognition and Linking Service

This module provides advanced Named Entity Recognition using Groq's Llama 3.1 70B.
It extends the existing EntityExtractor with:
- Enhanced entity extraction with context
- Entity relationship detection
- Entity linking to master tables
- Importance scoring for entities
- Disambiguation and normalization

Falls back to spaCy-based EntityExtractor if LLM is unavailable.
"""

import asyncio
import logging
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from pydantic import BaseModel, Field

from .llm_base import GroqLLMClient, LLMConfig, CacheConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Entity Models
# ============================================================================

class EntityType(str, Enum):
    """Entity type classification."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    GOVERNMENT = "government"
    COMPANY = "company"
    POLITICAL_PARTY = "political_party"
    INSTITUTION = "institution"
    EVENT = "event"
    DATE = "date"
    MONEY = "money"
    PERCENTAGE = "percentage"
    ECONOMIC_INDICATOR = "economic_indicator"
    POLICY = "policy"
    LEGISLATION = "legislation"
    OTHER = "other"


class EntityRole(str, Enum):
    """Role of entity in the article context."""
    SUBJECT = "subject"        # Main subject of discussion
    ACTOR = "actor"            # Entity taking action
    TARGET = "target"          # Entity being affected
    SOURCE = "source"          # Information source
    REFERENCE = "reference"    # Referenced entity
    CONTEXT = "context"        # Contextual mention


class RelationType(str, Enum):
    """Relationship types between entities."""
    LEADS = "leads"
    MEMBER_OF = "member_of"
    LOCATED_IN = "located_in"
    SUBSIDIARY_OF = "subsidiary_of"
    PARTNER_OF = "partner_of"
    REGULATES = "regulates"
    IMPACTS = "impacts"
    ANNOUNCES = "announces"
    CRITICIZES = "criticizes"
    SUPPORTS = "supports"
    OPPOSES = "opposes"
    RELATED_TO = "related_to"


# Pydantic models for structured LLM output
class ExtractedEntity(BaseModel):
    """Single extracted entity."""
    text: str = Field(description="Entity text as it appears")
    normalized: str = Field(description="Normalized/canonical form")
    type: str = Field(description="Entity type")
    role: str = Field(default="reference", description="Entity role in context")
    importance: float = Field(ge=0.0, le=1.0, default=0.5, description="Importance score")
    context: str = Field(default="", description="Brief context description")


class EntityRelation(BaseModel):
    """Relationship between two entities."""
    source_entity: str = Field(description="Source entity text")
    target_entity: str = Field(description="Target entity text")
    relation_type: str = Field(description="Type of relationship")
    description: str = Field(default="", description="Relationship description")
    confidence: float = Field(ge=0.0, le=1.0, default=0.7, description="Confidence")


class LLMEntityResult(BaseModel):
    """Complete LLM entity extraction response."""
    entities: List[ExtractedEntity] = Field(default_factory=list)
    relationships: List[EntityRelation] = Field(default_factory=list)
    primary_entities: List[str] = Field(default_factory=list, description="Most important entities")
    summary: str = Field(default="", description="Brief entity summary")


# ============================================================================
# Entity Result Dataclasses
# ============================================================================

@dataclass
class Entity:
    """
    Enhanced entity with full metadata.
    """
    text: str                          # Original text
    normalized: str                    # Normalized form
    entity_type: EntityType
    role: EntityRole
    importance: float = 0.5            # 0-1 importance score
    context: str = ""                  # Context description
    
    # Linking information
    master_id: Optional[str] = None    # ID in master entity table
    confidence: float = 0.8            # Extraction confidence
    
    # Position in text
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "normalized": self.normalized,
            "type": self.entity_type.value,
            "role": self.role.value,
            "importance": self.importance,
            "context": self.context,
            "master_id": self.master_id,
            "confidence": self.confidence
        }


@dataclass
class Relationship:
    """
    Relationship between two entities.
    """
    source: Entity
    target: Entity
    relation_type: RelationType
    description: str = ""
    confidence: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source.text,
            "target": self.target.text,
            "relation_type": self.relation_type.value,
            "description": self.description,
            "confidence": self.confidence
        }


@dataclass
class SmartEntityResult:
    """
    Complete entity extraction result with relationships.
    """
    # All entities
    entities: List[Entity] = field(default_factory=list)
    
    # Primary entities (most important)
    primary_entities: List[Entity] = field(default_factory=list)
    
    # Relationships
    relationships: List[Relationship] = field(default_factory=list)
    
    # Grouped by type
    entities_by_type: Dict[str, List[Entity]] = field(default_factory=dict)
    
    # Metadata
    entity_count: int = 0
    relationship_count: int = 0
    extraction_source: str = "llm"
    processing_time_ms: float = 0.0
    cached: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "entities": [e.to_dict() for e in self.entities],
            "primary_entities": [e.to_dict() for e in self.primary_entities],
            "relationships": [r.to_dict() for r in self.relationships],
            "entities_by_type": {
                k: [e.to_dict() for e in v] 
                for k, v in self.entities_by_type.items()
            },
            "entity_count": self.entity_count,
            "relationship_count": self.relationship_count,
            "extraction_source": self.extraction_source,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached
        }
    
    def to_legacy_format(self) -> Dict[str, List[str]]:
        """
        Convert to legacy EntityExtractor format for backward compatibility.
        """
        result = {}
        for entity_type, entities in self.entities_by_type.items():
            result[entity_type] = [e.text for e in entities]
        return result
    
    def get_entities_of_type(self, entity_type: EntityType) -> List[Entity]:
        """Get entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]
    
    def get_high_importance_entities(self, threshold: float = 0.7) -> List[Entity]:
        """Get entities above importance threshold."""
        return [e for e in self.entities if e.importance >= threshold]


# ============================================================================
# Master Entity Table (In-Memory for now, would be database in production)
# ============================================================================

class MasterEntityTable:
    """
    Master entity table for entity linking.
    
    In production, this would be backed by a database.
    For now, uses in-memory storage with common entities.
    """
    
    def __init__(self):
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._aliases: Dict[str, str] = {}  # alias -> master_id
        self._initialize_common_entities()
    
    def _initialize_common_entities(self):
        """Initialize with common entities."""
        # Government entities
        common_entities = [
            # Government
            {"id": "GOV_CENTRAL", "name": "Central Government", "type": "government", 
             "aliases": ["government", "federal government", "central govt"]},
            {"id": "GOV_TREASURY", "name": "Treasury", "type": "government",
             "aliases": ["treasury", "ministry of finance", "finance ministry"]},
            {"id": "GOV_CENTRAL_BANK", "name": "Central Bank", "type": "institution",
             "aliases": ["central bank", "reserve bank", "monetary authority"]},
            
            # Economic entities
            {"id": "ECON_GDP", "name": "Gross Domestic Product", "type": "economic_indicator",
             "aliases": ["gdp", "gross domestic product"]},
            {"id": "ECON_CPI", "name": "Consumer Price Index", "type": "economic_indicator",
             "aliases": ["cpi", "consumer price index", "inflation rate"]},
            {"id": "ECON_UNEMPLOYMENT", "name": "Unemployment Rate", "type": "economic_indicator",
             "aliases": ["unemployment", "jobless rate", "unemployment rate"]},
            
            # International organizations
            {"id": "ORG_IMF", "name": "International Monetary Fund", "type": "organization",
             "aliases": ["imf", "international monetary fund"]},
            {"id": "ORG_WORLD_BANK", "name": "World Bank", "type": "organization",
             "aliases": ["world bank", "wb", "ibrd"]},
            {"id": "ORG_UN", "name": "United Nations", "type": "organization",
             "aliases": ["un", "united nations"]},
        ]
        
        for entity in common_entities:
            self._entities[entity["id"]] = {
                "name": entity["name"],
                "type": entity["type"]
            }
            # Add aliases
            for alias in entity.get("aliases", []):
                self._aliases[alias.lower()] = entity["id"]
    
    def lookup(self, text: str) -> Optional[str]:
        """
        Look up entity in master table.
        
        Returns master_id if found, None otherwise.
        """
        text_lower = text.lower().strip()
        
        # Direct alias lookup
        if text_lower in self._aliases:
            return self._aliases[text_lower]
        
        # Fuzzy matching could be added here
        return None
    
    def add_entity(self, master_id: str, name: str, entity_type: str, aliases: List[str] = None):
        """Add new entity to master table."""
        self._entities[master_id] = {"name": name, "type": entity_type}
        if aliases:
            for alias in aliases:
                self._aliases[alias.lower()] = master_id
    
    def get_entity(self, master_id: str) -> Optional[Dict[str, Any]]:
        """Get entity details by master ID."""
        return self._entities.get(master_id)


# Global master table instance
_master_entity_table: Optional[MasterEntityTable] = None

def get_master_entity_table() -> MasterEntityTable:
    """Get or create master entity table."""
    global _master_entity_table
    if _master_entity_table is None:
        _master_entity_table = MasterEntityTable()
    return _master_entity_table


# ============================================================================
# Smart Entity Extractor Service
# ============================================================================

class SmartEntityExtractor:
    """
    LLM-powered entity extraction with relationship detection.
    
    Features:
    - Enhanced NER with context understanding
    - Entity relationship extraction
    - Entity linking to master table
    - Importance scoring
    - Fallback to spaCy when needed
    
    Usage:
        extractor = SmartEntityExtractor()
        result = await extractor.extract("Article text here...")
    """
    
    EXTRACTION_PROMPT = """Extract entities and their relationships from this article.

ARTICLE:
{article_text}

INSTRUCTIONS:
1. Extract ALL significant entities including:
   - People (officials, executives, experts)
   - Organizations (companies, institutions, agencies)
   - Locations (countries, cities, regions)
   - Government bodies and political parties
   - Economic indicators (GDP, inflation, etc.)
   - Policies, laws, and legislation
   - Events (summits, elections, announcements)
   - Monetary values and percentages

2. For each entity, provide:
   - Text as it appears in the article
   - Normalized/canonical form
   - Entity type
   - Role in the article (subject, actor, target, source, reference, context)
   - Importance score (0-1) based on centrality to the article

3. Identify relationships between entities:
   - leads, member_of, located_in, subsidiary_of, partner_of
   - regulates, impacts, announces, criticizes, supports, opposes
   - Provide confidence score for each relationship

4. Identify the 3-5 most important/primary entities

Entity Types: person, organization, location, government, company, political_party, institution, event, date, money, percentage, economic_indicator, policy, legislation, other

Roles: subject, actor, target, source, reference, context"""

    SYSTEM_PROMPT = """You are an expert entity extraction system specializing in economic and political news.
Extract entities accurately with their full context.
Normalize entity names to their canonical forms (e.g., "Fed" -> "Federal Reserve").
Identify meaningful relationships between entities.
Be precise with importance scores - primary subjects should score highest."""

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        cache_config: Optional[CacheConfig] = None,
        fallback_extractor: Optional[Any] = None,
        master_table: Optional[MasterEntityTable] = None,
        min_text_length: int = 50
    ):
        """
        Initialize Smart Entity Extractor.
        
        Args:
            llm_config: LLM configuration
            cache_config: Cache configuration
            fallback_extractor: Instance of basic EntityExtractor for fallback
            master_table: Master entity table for linking
            min_text_length: Minimum text length to process
        """
        self.llm_config = llm_config or LLMConfig()
        self.cache_config = cache_config or CacheConfig(prefix="entity_extractor")
        self.llm_client = GroqLLMClient(self.llm_config, self.cache_config)
        self.fallback_extractor = fallback_extractor
        self.master_table = master_table or get_master_entity_table()
        self.min_text_length = min_text_length
        
        # Statistics
        self._total_extractions = 0
        self._llm_extractions = 0
        self._fallback_extractions = 0
        self._entities_extracted = 0
        self._relationships_extracted = 0
        self._errors = 0
    
    async def extract(
        self,
        text: str,
        title: str = "",
        extract_relationships: bool = True,
        link_entities: bool = True
    ) -> SmartEntityResult:
        """
        Extract entities and relationships from text.
        
        Args:
            text: Article text content
            title: Article title (optional)
            extract_relationships: Whether to extract relationships
            link_entities: Whether to link to master entity table
        
        Returns:
            SmartEntityResult with entities and relationships
        """
        import time
        start_time = time.time()
        
        self._total_extractions += 1
        
        # Combine title and text
        full_text = f"{title}\n\n{text}" if title else text
        
        # Skip very short texts
        if len(full_text) < self.min_text_length:
            return SmartEntityResult(
                extraction_source="skipped",
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        try:
            # Truncate very long texts
            max_length = 3500
            if len(full_text) > max_length:
                full_text = full_text[:max_length] + "..."
            
            # Build prompt
            prompt = self.EXTRACTION_PROMPT.format(article_text=full_text)
            
            # Get LLM extraction
            response = await self.llm_client.generate_structured(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                response_model=LLMEntityResult
            )
            
            # Parse result
            result = self._parse_llm_response(response, link_entities)
            result.processing_time_ms = (time.time() - start_time) * 1000
            
            self._llm_extractions += 1
            self._entities_extracted += result.entity_count
            self._relationships_extracted += result.relationship_count
            
            logger.info(
                f"LLM extracted: {result.entity_count} entities, "
                f"{result.relationship_count} relationships"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"LLM entity extraction failed: {e}")
            self._errors += 1
            return await self._fallback_extract(full_text, start_time)
    
    async def extract_batch(
        self,
        texts: List[Dict[str, str]],
        concurrency: int = 5
    ) -> List[SmartEntityResult]:
        """
        Extract entities from multiple texts concurrently.
        
        Args:
            texts: List of dicts with 'text', optional 'title'
            concurrency: Max concurrent extractions
        
        Returns:
            List of SmartEntityResult objects
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def extract_with_limit(item: Dict[str, str]) -> SmartEntityResult:
            async with semaphore:
                return await self.extract(
                    text=item.get("text", ""),
                    title=item.get("title", "")
                )
        
        tasks = [extract_with_limit(item) for item in texts]
        return await asyncio.gather(*tasks)
    
    def _parse_llm_response(
        self,
        response: LLMEntityResult,
        link_entities: bool
    ) -> SmartEntityResult:
        """
        Parse LLM response into SmartEntityResult.
        """
        entities: List[Entity] = []
        entity_lookup: Dict[str, Entity] = {}  # text -> entity
        
        # Parse entities
        for ext_entity in response.entities:
            try:
                entity_type = EntityType(ext_entity.type.lower())
            except ValueError:
                entity_type = EntityType.OTHER
            
            try:
                role = EntityRole(ext_entity.role.lower())
            except ValueError:
                role = EntityRole.REFERENCE
            
            entity = Entity(
                text=ext_entity.text,
                normalized=ext_entity.normalized or ext_entity.text,
                entity_type=entity_type,
                role=role,
                importance=ext_entity.importance,
                context=ext_entity.context[:200] if ext_entity.context else ""
            )
            
            # Link to master table
            if link_entities:
                master_id = self.master_table.lookup(entity.normalized)
                if master_id:
                    entity.master_id = master_id
            
            entities.append(entity)
            entity_lookup[ext_entity.text.lower()] = entity
        
        # Parse relationships
        relationships: List[Relationship] = []
        for rel in response.relationships:
            source_entity = entity_lookup.get(rel.source_entity.lower())
            target_entity = entity_lookup.get(rel.target_entity.lower())
            
            if source_entity and target_entity:
                try:
                    relation_type = RelationType(rel.relation_type.lower())
                except ValueError:
                    relation_type = RelationType.RELATED_TO
                
                relationship = Relationship(
                    source=source_entity,
                    target=target_entity,
                    relation_type=relation_type,
                    description=rel.description[:200] if rel.description else "",
                    confidence=rel.confidence
                )
                relationships.append(relationship)
        
        # Identify primary entities
        primary_entities = sorted(
            entities,
            key=lambda e: e.importance,
            reverse=True
        )[:5]
        
        # Group by type
        entities_by_type: Dict[str, List[Entity]] = {}
        for entity in entities:
            type_key = entity.entity_type.value
            if type_key not in entities_by_type:
                entities_by_type[type_key] = []
            entities_by_type[type_key].append(entity)
        
        return SmartEntityResult(
            entities=entities,
            primary_entities=primary_entities,
            relationships=relationships,
            entities_by_type=entities_by_type,
            entity_count=len(entities),
            relationship_count=len(relationships),
            extraction_source="llm"
        )
    
    async def _fallback_extract(
        self,
        text: str,
        start_time: float
    ) -> SmartEntityResult:
        """
        Fall back to basic entity extraction.
        """
        import time
        
        self._fallback_extractions += 1
        
        if self.fallback_extractor:
            try:
                # Use existing EntityExtractor
                result = await self._run_basic_extractor(text)
                result.extraction_source = "basic_fallback"
                result.processing_time_ms = (time.time() - start_time) * 1000
                return result
            except Exception as e:
                logger.error(f"Fallback extractor also failed: {e}")
        
        # Ultimate fallback - regex based
        result = self._regex_based_extraction(text)
        result.processing_time_ms = (time.time() - start_time) * 1000
        result.extraction_source = "regex_fallback"
        return result
    
    async def _run_basic_extractor(self, text: str) -> SmartEntityResult:
        """
        Run the existing basic EntityExtractor.
        """
        # Integration with existing EntityExtractor would go here
        return self._regex_based_extraction(text)
    
    def _regex_based_extraction(self, text: str) -> SmartEntityResult:
        """
        Simple regex-based entity extraction as fallback.
        """
        import re
        
        entities: List[Entity] = []
        
        # Extract percentages
        percentages = re.findall(r'\b\d+(?:\.\d+)?%', text)
        for pct in percentages[:5]:
            entities.append(Entity(
                text=pct,
                normalized=pct,
                entity_type=EntityType.PERCENTAGE,
                role=EntityRole.REFERENCE,
                importance=0.4
            ))
        
        # Extract money amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?\s*(?:billion|million|trillion)?|\b[\d,]+\s*(?:billion|million|trillion)\s*(?:dollars|USD)?'
        money_matches = re.findall(money_pattern, text, re.IGNORECASE)
        for money in money_matches[:5]:
            entities.append(Entity(
                text=money.strip(),
                normalized=money.strip(),
                entity_type=EntityType.MONEY,
                role=EntityRole.REFERENCE,
                importance=0.5
            ))
        
        # Extract capitalized phrases (potential names/organizations)
        cap_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b'
        cap_matches = re.findall(cap_pattern, text)
        seen: Set[str] = set()
        for match in cap_matches[:10]:
            if match.lower() not in seen and len(match) > 3:
                seen.add(match.lower())
                # Guess type based on keywords
                if any(w in match.lower() for w in ["minister", "president", "ceo", "director"]):
                    entity_type = EntityType.PERSON
                elif any(w in match.lower() for w in ["bank", "company", "corporation", "ministry", "department"]):
                    entity_type = EntityType.ORGANIZATION
                else:
                    entity_type = EntityType.OTHER
                
                entities.append(Entity(
                    text=match,
                    normalized=match,
                    entity_type=entity_type,
                    role=EntityRole.REFERENCE,
                    importance=0.5
                ))
        
        # Group by type
        entities_by_type: Dict[str, List[Entity]] = {}
        for entity in entities:
            type_key = entity.entity_type.value
            if type_key not in entities_by_type:
                entities_by_type[type_key] = []
            entities_by_type[type_key].append(entity)
        
        return SmartEntityResult(
            entities=entities,
            primary_entities=entities[:3],
            relationships=[],
            entities_by_type=entities_by_type,
            entity_count=len(entities),
            relationship_count=0
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        llm_stats = self.llm_client.get_stats()
        return {
            "total_extractions": self._total_extractions,
            "llm_extractions": self._llm_extractions,
            "fallback_extractions": self._fallback_extractions,
            "entities_extracted": self._entities_extracted,
            "relationships_extracted": self._relationships_extracted,
            "errors": self._errors,
            "llm_usage_rate": (
                self._llm_extractions / self._total_extractions
                if self._total_extractions > 0 else 0
            ),
            "llm_client_stats": llm_stats
        }


# ============================================================================
# Factory Function
# ============================================================================

def create_smart_entity_extractor(
    api_key: Optional[str] = None,
    cache_enabled: bool = True,
    fallback_extractor: Optional[Any] = None,
    master_table: Optional[MasterEntityTable] = None
) -> SmartEntityExtractor:
    """
    Factory function to create a SmartEntityExtractor instance.
    
    Args:
        api_key: Groq API key (uses env var if not provided)
        cache_enabled: Whether to enable response caching
        fallback_extractor: Basic EntityExtractor instance for fallback
        master_table: Master entity table for linking
    
    Returns:
        Configured SmartEntityExtractor instance
    """
    llm_config = LLMConfig(
        model="llama-3.1-70b-versatile",
        temperature=0.1,  # Low temperature for precise extraction
        max_tokens=2000
    )
    
    cache_config = CacheConfig(
        enabled=cache_enabled,
        ttl_hours=48,  # Longer cache for entity extraction
        prefix="entity_extractor"
    )
    
    return SmartEntityExtractor(
        llm_config=llm_config,
        cache_config=cache_config,
        fallback_extractor=fallback_extractor,
        master_table=master_table
    )
