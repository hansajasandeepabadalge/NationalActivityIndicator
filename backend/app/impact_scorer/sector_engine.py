"""
Sector Impact Engine

Calculates industry-specific impact scores based on:
- Sector keyword matching
- Industry dependency mapping
- Cross-sector cascade effects
- Business operation relevance

Supports 15+ industry sectors with Sri Lanka-specific context.
"""

import logging
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IndustrySector(Enum):
    """Business industry sectors."""
    TOURISM = "tourism"
    FINANCE = "finance"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    AGRICULTURE = "agriculture"
    TRANSPORT = "transport"
    ENERGY = "energy"
    HEALTHCARE = "healthcare"
    CONSTRUCTION = "construction"
    IT_SERVICES = "it_services"
    TELECOMMUNICATIONS = "telecommunications"
    APPAREL = "apparel"
    TEA_EXPORT = "tea_export"
    SEAFOOD = "seafood"
    REAL_ESTATE = "real_estate"
    EDUCATION = "education"
    GENERAL = "general"


@dataclass
class SectorImpact:
    """Impact assessment for a specific sector."""
    sector: IndustrySector
    impact_score: float          # 0-100
    relevance_score: float       # 0-100
    keywords_matched: List[str]
    impact_type: str             # "direct", "indirect", "cascading"
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sector": self.sector.value,
            "impact_score": self.impact_score,
            "relevance_score": self.relevance_score,
            "keywords_matched": self.keywords_matched,
            "impact_type": self.impact_type,
            "description": self.description
        }


@dataclass
class SectorAnalysisResult:
    """Complete sector analysis result."""
    primary_sectors: List[SectorImpact]
    secondary_sectors: List[SectorImpact]
    overall_sector_score: float
    sector_count: int
    cascade_effects: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_sectors": [s.to_dict() for s in self.primary_sectors],
            "secondary_sectors": [s.to_dict() for s in self.secondary_sectors],
            "overall_sector_score": self.overall_sector_score,
            "sector_count": self.sector_count,
            "cascade_effects": self.cascade_effects
        }


class SectorImpactEngine:
    """
    Engine for calculating sector-specific business impact.
    
    Features:
    - Multi-sector keyword matching
    - Industry dependency chains
    - Cascade effect prediction
    - Cross-sector correlation
    """
    
    # Sector-specific keywords
    SECTOR_KEYWORDS: Dict[IndustrySector, Set[str]] = {
        IndustrySector.TOURISM: {
            "tourist", "tourism", "hotel", "resort", "travel", "airline",
            "visitor", "vacation", "hospitality", "booking", "destination",
            "attraction", "safari", "beach", "heritage", "sigiriya", "kandy temple"
        },
        IndustrySector.FINANCE: {
            "bank", "banking", "finance", "loan", "interest rate", "investment",
            "stock", "share", "cse", "colombo stock", "credit", "deposit",
            "mortgage", "insurance", "leasing", "microfinance", "forex"
        },
        IndustrySector.RETAIL: {
            "retail", "shop", "store", "supermarket", "consumer", "shopping",
            "keells", "cargills", "arpico", "mall", "price", "goods", "fmcg"
        },
        IndustrySector.MANUFACTURING: {
            "factory", "manufacturing", "production", "industrial", "plant",
            "assembly", "machinery", "export", "boi", "zone", "katunayake"
        },
        IndustrySector.AGRICULTURE: {
            "farmer", "agriculture", "crop", "harvest", "paddy", "rice",
            "fertilizer", "irrigation", "farming", "yield", "cultivation",
            "plantation", "coconut", "rubber", "spices"
        },
        IndustrySector.TRANSPORT: {
            "transport", "logistics", "shipping", "port", "road", "highway",
            "bus", "rail", "railway", "trucking", "cargo", "colombo port",
            "hambantota", "freight", "container"
        },
        IndustrySector.ENERGY: {
            "power", "electricity", "fuel", "petrol", "diesel", "gas",
            "energy", "ceb", "cpc", "solar", "wind", "hydro", "lpg",
            "power cut", "load shedding"
        },
        IndustrySector.HEALTHCARE: {
            "hospital", "health", "medical", "pharma", "pharmaceutical",
            "clinic", "doctor", "patient", "medicine", "drug", "vaccine",
            "covid", "disease", "epidemic"
        },
        IndustrySector.CONSTRUCTION: {
            "construction", "building", "infrastructure", "project", "cement",
            "steel", "property", "development", "contractor", "highway project",
            "mega project"
        },
        IndustrySector.IT_SERVICES: {
            "it", "software", "technology", "tech", "digital", "startup",
            "bpo", "outsourcing", "data center", "cloud", "fintech",
            "e-commerce", "online"
        },
        IndustrySector.TELECOMMUNICATIONS: {
            "telecom", "mobile", "network", "dialog", "mobitel", "airtel",
            "hutch", "broadband", "5g", "4g", "internet", "fiber"
        },
        IndustrySector.APPAREL: {
            "garment", "apparel", "textile", "clothing", "fashion", "export",
            "brandix", "mas", "hirdaramani", "sewing", "factory"
        },
        IndustrySector.TEA_EXPORT: {
            "tea", "ceylon tea", "plantation", "tea export", "tea auction",
            "tea factory", "upcountry", "tea board"
        },
        IndustrySector.SEAFOOD: {
            "fish", "fishing", "seafood", "trawler", "fishery", "export",
            "negombo", "fish market", "crab", "prawn", "lobster"
        },
        IndustrySector.REAL_ESTATE: {
            "real estate", "property", "land", "apartment", "condo",
            "housing", "residential", "commercial property"
        },
        IndustrySector.EDUCATION: {
            "education", "school", "university", "student", "exam",
            "admission", "scholarship", "tuition", "college"
        }
    }
    
    # Sector dependencies (if A affected, B likely affected)
    SECTOR_DEPENDENCIES: Dict[IndustrySector, List[Tuple[IndustrySector, float]]] = {
        IndustrySector.ENERGY: [
            (IndustrySector.MANUFACTURING, 0.9),
            (IndustrySector.RETAIL, 0.7),
            (IndustrySector.IT_SERVICES, 0.8),
            (IndustrySector.TRANSPORT, 0.6)
        ],
        IndustrySector.TRANSPORT: [
            (IndustrySector.RETAIL, 0.8),
            (IndustrySector.MANUFACTURING, 0.7),
            (IndustrySector.AGRICULTURE, 0.6),
            (IndustrySector.TOURISM, 0.5)
        ],
        IndustrySector.FINANCE: [
            (IndustrySector.REAL_ESTATE, 0.8),
            (IndustrySector.CONSTRUCTION, 0.7),
            (IndustrySector.RETAIL, 0.6)
        ],
        IndustrySector.TOURISM: [
            (IndustrySector.TRANSPORT, 0.7),
            (IndustrySector.RETAIL, 0.6),
            (IndustrySector.HEALTHCARE, 0.3)
        ],
        IndustrySector.AGRICULTURE: [
            (IndustrySector.RETAIL, 0.7),
            (IndustrySector.MANUFACTURING, 0.5)
        ],
        IndustrySector.CONSTRUCTION: [
            (IndustrySector.REAL_ESTATE, 0.8),
            (IndustrySector.MANUFACTURING, 0.6)
        ],
        IndustrySector.TELECOMMUNICATIONS: [
            (IndustrySector.IT_SERVICES, 0.8),
            (IndustrySector.FINANCE, 0.5),
            (IndustrySector.RETAIL, 0.4)
        ]
    }
    
    # Impact multipliers for different event types
    EVENT_TYPE_MULTIPLIERS: Dict[str, Dict[IndustrySector, float]] = {
        "fuel_shortage": {
            IndustrySector.TRANSPORT: 1.5,
            IndustrySector.MANUFACTURING: 1.3,
            IndustrySector.AGRICULTURE: 1.2,
            IndustrySector.TOURISM: 1.2
        },
        "power_crisis": {
            IndustrySector.MANUFACTURING: 1.5,
            IndustrySector.IT_SERVICES: 1.4,
            IndustrySector.RETAIL: 1.2,
            IndustrySector.HEALTHCARE: 1.3
        },
        "currency_crisis": {
            IndustrySector.FINANCE: 1.5,
            IndustrySector.RETAIL: 1.3,
            IndustrySector.MANUFACTURING: 1.2,
            IndustrySector.APPAREL: 1.1  # Export benefit
        },
        "natural_disaster": {
            IndustrySector.AGRICULTURE: 1.5,
            IndustrySector.CONSTRUCTION: 1.3,
            IndustrySector.TOURISM: 1.4,
            IndustrySector.TRANSPORT: 1.2
        },
        "policy_change": {
            IndustrySector.FINANCE: 1.3,
            IndustrySector.RETAIL: 1.2,
            IndustrySector.MANUFACTURING: 1.2
        }
    }
    
    def __init__(self):
        """Initialize the sector impact engine."""
        logger.info("SectorImpactEngine initialized")
    
    def analyze_sectors(
        self,
        title: str,
        content: str,
        target_sectors: Optional[List[str]] = None,
        event_type: Optional[str] = None
    ) -> SectorAnalysisResult:
        """
        Analyze article for sector-specific impacts.
        
        Args:
            title: Article title
            content: Article content
            target_sectors: Optional list of sectors to focus on
            event_type: Optional event classification
            
        Returns:
            SectorAnalysisResult with all sector impacts
        """
        full_text = f"{title} {content}".lower()
        title_lower = title.lower()
        
        # Analyze direct sector impacts
        sector_impacts: List[SectorImpact] = []
        
        for sector, keywords in self.SECTOR_KEYWORDS.items():
            matched = [kw for kw in keywords if kw in full_text]
            
            if matched:
                # Calculate relevance based on keyword matches
                relevance = self._calculate_relevance(matched, keywords, title_lower)
                
                # Calculate impact score
                impact = self._calculate_sector_impact(
                    sector, relevance, matched, event_type
                )
                
                sector_impacts.append(SectorImpact(
                    sector=sector,
                    impact_score=impact,
                    relevance_score=relevance,
                    keywords_matched=matched[:5],
                    impact_type="direct",
                    description=self._generate_impact_description(sector, matched)
                ))
        
        # Sort by impact score
        sector_impacts.sort(key=lambda x: x.impact_score, reverse=True)
        
        # Separate primary (top 3) and secondary sectors
        primary = sector_impacts[:3]
        secondary = sector_impacts[3:6]
        
        # Calculate cascade effects
        cascade_effects = self._calculate_cascade_effects(primary)
        
        # Add cascade sectors as secondary if not already included
        cascade_sectors = self._get_cascade_sectors(primary, secondary)
        secondary.extend(cascade_sectors[:2])
        
        # Calculate overall sector score
        if primary:
            overall = sum(s.impact_score for s in primary) / len(primary)
        else:
            overall = 0.0
        
        return SectorAnalysisResult(
            primary_sectors=primary,
            secondary_sectors=secondary[:4],
            overall_sector_score=round(overall, 1),
            sector_count=len(sector_impacts),
            cascade_effects=cascade_effects
        )
    
    def _calculate_relevance(
        self,
        matched: List[str],
        all_keywords: Set[str],
        title: str
    ) -> float:
        """Calculate sector relevance score."""
        # Base relevance from match ratio
        match_ratio = len(matched) / min(len(all_keywords), 10)
        base_relevance = min(match_ratio * 100, 100)
        
        # Boost for title matches
        title_matches = sum(1 for kw in matched if kw in title)
        title_boost = title_matches * 15
        
        # Boost for multiple keyword matches
        multi_match_boost = min((len(matched) - 1) * 10, 30) if len(matched) > 1 else 0
        
        return min(base_relevance + title_boost + multi_match_boost, 100)
    
    def _calculate_sector_impact(
        self,
        sector: IndustrySector,
        relevance: float,
        matched: List[str],
        event_type: Optional[str]
    ) -> float:
        """Calculate sector-specific impact score."""
        # Start with relevance as base
        impact = relevance * 0.7
        
        # Apply event type multiplier if applicable
        if event_type and event_type in self.EVENT_TYPE_MULTIPLIERS:
            multipliers = self.EVENT_TYPE_MULTIPLIERS[event_type]
            if sector in multipliers:
                impact *= multipliers[sector]
        
        # Boost for highly specific keyword matches
        specific_keywords = {"crisis", "shortage", "closure", "strike", "collapse"}
        if any(kw in " ".join(matched) for kw in specific_keywords):
            impact *= 1.3
        
        return min(round(impact, 1), 100)
    
    def _calculate_cascade_effects(
        self,
        primary_sectors: List[SectorImpact]
    ) -> List[Dict[str, Any]]:
        """Calculate potential cascade effects to dependent sectors."""
        cascades = []
        
        for primary in primary_sectors:
            if primary.sector in self.SECTOR_DEPENDENCIES:
                for dep_sector, strength in self.SECTOR_DEPENDENCIES[primary.sector]:
                    cascade_impact = primary.impact_score * strength * 0.7
                    
                    if cascade_impact >= 20:  # Only significant cascades
                        cascades.append({
                            "from_sector": primary.sector.value,
                            "to_sector": dep_sector.value,
                            "cascade_strength": round(strength, 2),
                            "estimated_impact": round(cascade_impact, 1),
                            "description": f"Impact on {dep_sector.value} due to {primary.sector.value} disruption"
                        })
        
        # Sort by estimated impact
        cascades.sort(key=lambda x: x["estimated_impact"], reverse=True)
        return cascades[:5]
    
    def _get_cascade_sectors(
        self,
        primary: List[SectorImpact],
        existing_secondary: List[SectorImpact]
    ) -> List[SectorImpact]:
        """Get cascade-affected sectors not already in primary/secondary."""
        existing_sectors = {s.sector for s in primary + existing_secondary}
        cascade_sectors = []
        
        for primary_impact in primary:
            if primary_impact.sector in self.SECTOR_DEPENDENCIES:
                for dep_sector, strength in self.SECTOR_DEPENDENCIES[primary_impact.sector]:
                    if dep_sector not in existing_sectors:
                        cascade_impact = primary_impact.impact_score * strength * 0.6
                        if cascade_impact >= 25:
                            cascade_sectors.append(SectorImpact(
                                sector=dep_sector,
                                impact_score=round(cascade_impact, 1),
                                relevance_score=round(strength * 100, 1),
                                keywords_matched=[],
                                impact_type="cascading",
                                description=f"Cascading impact from {primary_impact.sector.value}"
                            ))
                            existing_sectors.add(dep_sector)
        
        return cascade_sectors
    
    def _generate_impact_description(
        self,
        sector: IndustrySector,
        matched_keywords: List[str]
    ) -> str:
        """Generate human-readable impact description."""
        keyword_str = ", ".join(matched_keywords[:3])
        
        descriptions = {
            IndustrySector.TOURISM: f"Tourism sector impact indicated by: {keyword_str}",
            IndustrySector.FINANCE: f"Financial services affected, signals: {keyword_str}",
            IndustrySector.RETAIL: f"Retail and consumer sector impact: {keyword_str}",
            IndustrySector.MANUFACTURING: f"Manufacturing operations affected: {keyword_str}",
            IndustrySector.AGRICULTURE: f"Agricultural sector impact: {keyword_str}",
            IndustrySector.TRANSPORT: f"Transport and logistics disruption: {keyword_str}",
            IndustrySector.ENERGY: f"Energy sector implications: {keyword_str}",
            IndustrySector.HEALTHCARE: f"Healthcare sector affected: {keyword_str}",
            IndustrySector.CONSTRUCTION: f"Construction industry impact: {keyword_str}",
            IndustrySector.IT_SERVICES: f"IT and digital services affected: {keyword_str}",
            IndustrySector.TELECOMMUNICATIONS: f"Telecom sector implications: {keyword_str}",
            IndustrySector.APPAREL: f"Apparel export sector impact: {keyword_str}",
            IndustrySector.TEA_EXPORT: f"Tea industry affected: {keyword_str}",
            IndustrySector.SEAFOOD: f"Fisheries and seafood impact: {keyword_str}",
            IndustrySector.REAL_ESTATE: f"Real estate market implications: {keyword_str}",
            IndustrySector.EDUCATION: f"Education sector affected: {keyword_str}",
            IndustrySector.GENERAL: f"General business impact: {keyword_str}"
        }
        
        return descriptions.get(sector, f"Sector impact detected: {keyword_str}")
    
    def get_sector_score_for_business(
        self,
        result: SectorAnalysisResult,
        business_sectors: List[str]
    ) -> float:
        """
        Calculate impact score for specific business sectors.
        
        Args:
            result: SectorAnalysisResult from analysis
            business_sectors: List of sector names relevant to business
            
        Returns:
            Weighted impact score for the business
        """
        if not business_sectors:
            return result.overall_sector_score
        
        relevant_scores = []
        all_impacts = result.primary_sectors + result.secondary_sectors
        
        for sector_name in business_sectors:
            try:
                sector = IndustrySector(sector_name.lower())
                for impact in all_impacts:
                    if impact.sector == sector:
                        relevant_scores.append(impact.impact_score)
                        break
            except ValueError:
                continue
        
        if relevant_scores:
            return sum(relevant_scores) / len(relevant_scores)
        
        return result.overall_sector_score * 0.5  # Discount if no direct match
