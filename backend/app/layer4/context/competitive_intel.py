"""
Layer 4: Competitive Intelligence

Tracks competitor moves and market positioning.
Provides strategic context for business decisions.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class CompetitorMoveType(Enum):
    """Types of competitor moves"""
    EXPANSION = "expansion"
    CONTRACTION = "contraction"
    PRICING = "pricing"
    PRODUCT = "product"
    MARKETING = "marketing"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    RESTRUCTURING = "restructuring"


class ThreatLevel(Enum):
    """Competitive threat level"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class OpportunityLevel(Enum):
    """Competitive opportunity level"""
    MARGINAL = "marginal"
    NOTABLE = "notable"
    SIGNIFICANT = "significant"
    MAJOR = "major"


@dataclass
class CompetitorProfile:
    """Profile of a competitor"""
    competitor_id: str
    name: str
    industry: str
    
    # Market position
    market_share: float  # Estimated market share (0-1)
    market_position: str  # 'leader', 'challenger', 'follower', 'niche'
    
    # Strengths and weaknesses
    strengths: List[str]
    weaknesses: List[str]
    
    # Recent performance indicators
    performance_trend: str  # 'growing', 'stable', 'declining'
    estimated_revenue_growth: Optional[float]
    
    # Coverage overlap
    geographic_overlap: float  # 0-1, how much geographic coverage overlaps
    product_overlap: float  # 0-1, how much product/service overlap
    customer_overlap: float  # 0-1, how much customer base overlap
    
    # Monitoring priority
    monitoring_priority: str  # 'high', 'medium', 'low'


@dataclass
class CompetitorMove:
    """A specific move by a competitor"""
    move_id: str
    competitor_id: str
    competitor_name: str
    
    move_type: CompetitorMoveType
    description: str
    
    # Timing
    detected_date: datetime
    effective_date: Optional[datetime]
    
    # Impact assessment
    threat_level: ThreatLevel
    opportunity_level: OpportunityLevel
    
    # Affected areas
    affected_segments: List[str]
    affected_regions: List[str]
    
    # Strategic implications
    implications: List[str]
    
    # Recommended responses
    recommended_responses: List[str]
    
    # Confidence in assessment
    confidence: float


@dataclass
class MarketPositionAnalysis:
    """Analysis of company's market position relative to competitors"""
    company_id: str
    industry: str
    analysis_date: datetime
    
    # Overall position
    market_rank: int
    market_share_estimate: float
    position_category: str  # 'leader', 'challenger', 'follower', 'niche'
    
    # Competitive gap analysis
    gaps: List[Dict[str, Any]]
    
    # Competitive advantages
    advantages: List[Dict[str, Any]]
    
    # Threat landscape
    primary_threats: List[str]
    emerging_threats: List[str]
    
    # Opportunity landscape
    opportunities: List[str]
    
    # Strategic recommendations
    recommendations: List[str]


class CompetitiveIntelligenceAnalyzer:
    """
    Analyzes competitive landscape and competitor moves.
    
    Features:
    - Competitor tracking
    - Market positioning analysis
    - Competitive threat assessment
    - Strategic opportunity identification
    """
    
    def __init__(self):
        self._competitor_profiles = self._load_competitor_profiles()
        self._recent_moves = self._load_recent_competitor_moves()
        self._market_data = self._load_market_data()
        
        logger.info(f"Initialized CompetitiveIntelligenceAnalyzer with {len(self._competitor_profiles)} competitors tracked")
    
    def get_competitor_activity(
        self,
        industry: str,
        lookback_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get recent competitor activity in an industry.
        
        Args:
            industry: Industry to analyze
            lookback_days: How far back to look
            
        Returns:
            Summary of competitor activity
        """
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        # Filter moves by industry and date
        relevant_moves = [
            m for m in self._recent_moves
            if self._is_industry_relevant(m.competitor_id, industry)
            and m.detected_date >= cutoff_date
        ]
        
        # Summarize by move type
        move_summary = defaultdict(list)
        for move in relevant_moves:
            move_summary[move.move_type.value].append({
                "competitor": move.competitor_name,
                "description": move.description,
                "threat_level": move.threat_level.value,
                "date": move.detected_date.strftime("%Y-%m-%d"),
            })
        
        # Calculate threat level
        threat_counts = defaultdict(int)
        for move in relevant_moves:
            threat_counts[move.threat_level.value] += 1
        
        overall_threat = "low"
        if threat_counts.get("critical", 0) > 0:
            overall_threat = "critical"
        elif threat_counts.get("high", 0) >= 2:
            overall_threat = "high"
        elif threat_counts.get("moderate", 0) >= 2:
            overall_threat = "moderate"
        
        return {
            "industry": industry,
            "period_days": lookback_days,
            "total_moves_detected": len(relevant_moves),
            "moves_by_type": dict(move_summary),
            "threat_level_distribution": dict(threat_counts),
            "overall_threat_level": overall_threat,
            "key_developments": self._extract_key_developments(relevant_moves),
            "requires_immediate_attention": any(
                m.threat_level in (ThreatLevel.CRITICAL, ThreatLevel.HIGH)
                for m in relevant_moves
            ),
        }
    
    def analyze_market_position(
        self,
        company_id: str,
        industry: str,
        company_indicators: Optional[Dict[str, float]] = None,
    ) -> MarketPositionAnalysis:
        """
        Analyze company's market position.
        
        Args:
            company_id: Company to analyze
            industry: Industry context
            company_indicators: Optional company performance indicators
            
        Returns:
            Market position analysis
        """
        # Get competitor profiles for industry
        competitors = [
            p for p in self._competitor_profiles
            if p.industry == industry
        ]
        
        # Estimate market rank (simplified)
        market_rank = len([c for c in competitors if c.market_share > 0.15]) + 1
        
        # Estimate market share (placeholder - would use real data)
        estimated_share = 0.12  # Default estimate
        if company_indicators:
            # Adjust based on indicators
            avg_performance = sum(company_indicators.values()) / len(company_indicators) if company_indicators else 0.5
            estimated_share = 0.08 + (avg_performance * 0.12)
        
        # Determine position category
        if estimated_share >= 0.25:
            position = "leader"
        elif estimated_share >= 0.15:
            position = "challenger"
        elif estimated_share >= 0.05:
            position = "follower"
        else:
            position = "niche"
        
        # Gap analysis
        gaps = self._identify_gaps(company_indicators, competitors)
        
        # Advantage analysis
        advantages = self._identify_advantages(company_indicators, competitors)
        
        # Threat analysis
        threats = self._identify_threats(industry, competitors)
        
        # Opportunity analysis
        opportunities = self._identify_opportunities(industry, competitors)
        
        # Strategic recommendations
        recommendations = self._generate_recommendations(
            position, gaps, advantages, threats, opportunities
        )
        
        return MarketPositionAnalysis(
            company_id=company_id,
            industry=industry,
            analysis_date=datetime.now(),
            market_rank=market_rank,
            market_share_estimate=estimated_share,
            position_category=position,
            gaps=gaps,
            advantages=advantages,
            primary_threats=threats[:3],
            emerging_threats=threats[3:] if len(threats) > 3 else [],
            opportunities=opportunities,
            recommendations=recommendations,
        )
    
    def assess_competitive_threat(
        self,
        company_id: str,
        industry: str,
        event_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assess competitive threats in current context.
        
        Args:
            company_id: Company to assess threats for
            industry: Industry context
            event_context: Optional current events/indicators
            
        Returns:
            Threat assessment
        """
        # Get competitor profiles
        competitors = [
            p for p in self._competitor_profiles
            if p.industry == industry
        ]
        
        # Get recent competitor moves
        recent_moves = [
            m for m in self._recent_moves
            if self._is_industry_relevant(m.competitor_id, industry)
            and m.detected_date >= datetime.now() - timedelta(days=30)
        ]
        
        threats = []
        
        for competitor in competitors:
            competitor_moves = [
                m for m in recent_moves
                if m.competitor_id == competitor.competitor_id
            ]
            
            threat_score = self._calculate_threat_score(
                competitor, competitor_moves, event_context
            )
            
            if threat_score > 0.3:  # Threshold
                threats.append({
                    "competitor": competitor.name,
                    "threat_score": round(threat_score, 2),
                    "threat_level": self._score_to_threat_level(threat_score),
                    "recent_moves": len(competitor_moves),
                    "overlap_risk": round((
                        competitor.geographic_overlap * 0.3 +
                        competitor.product_overlap * 0.4 +
                        competitor.customer_overlap * 0.3
                    ), 2),
                    "key_concerns": self._get_key_concerns(competitor, competitor_moves),
                })
        
        # Sort by threat score
        threats.sort(key=lambda t: t["threat_score"], reverse=True)
        
        # Calculate overall threat level
        if threats:
            max_score = max(t["threat_score"] for t in threats)
            overall_level = self._score_to_threat_level(max_score)
        else:
            overall_level = "low"
        
        return {
            "company_id": company_id,
            "industry": industry,
            "assessment_date": datetime.now().isoformat(),
            "overall_threat_level": overall_level,
            "competitor_count_tracked": len(competitors),
            "threats": threats[:5],
            "recommended_actions": self._get_threat_response_actions(threats[:3]),
            "monitoring_recommendations": self._get_monitoring_recommendations(threats),
        }
    
    def identify_competitive_opportunities(
        self,
        company_id: str,
        industry: str,
        company_strengths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Identify competitive opportunities.
        
        Args:
            company_id: Company to find opportunities for
            industry: Industry context
            company_strengths: Optional list of company strengths
            
        Returns:
            Opportunity analysis
        """
        competitors = [
            p for p in self._competitor_profiles
            if p.industry == industry
        ]
        
        opportunities = []
        
        # Identify opportunities from competitor weaknesses
        for competitor in competitors:
            for weakness in competitor.weaknesses:
                # Check if company strength can exploit this
                if company_strengths:
                    matching_strength = next(
                        (s for s in company_strengths 
                         if self._is_complementary(s, weakness)),
                        None
                    )
                else:
                    matching_strength = None
                
                opportunities.append({
                    "type": "competitor_weakness",
                    "competitor": competitor.name,
                    "weakness": weakness,
                    "your_advantage": matching_strength,
                    "opportunity_level": "significant" if matching_strength else "notable",
                    "action": f"Target {competitor.name}'s weakness in {weakness}",
                })
        
        # Identify market gaps
        market_gaps = self._identify_market_gaps(industry, competitors)
        for gap in market_gaps:
            opportunities.append({
                "type": "market_gap",
                "gap": gap["description"],
                "potential_value": gap["value"],
                "opportunity_level": gap["level"],
                "action": gap["recommended_action"],
            })
        
        # Identify timing opportunities from recent moves
        recent_moves = [
            m for m in self._recent_moves
            if self._is_industry_relevant(m.competitor_id, industry)
            and m.opportunity_level in (OpportunityLevel.SIGNIFICANT, OpportunityLevel.MAJOR)
        ]
        
        for move in recent_moves:
            opportunities.append({
                "type": "competitor_move",
                "competitor": move.competitor_name,
                "move": move.description,
                "opportunity_level": move.opportunity_level.value,
                "action": move.recommended_responses[0] if move.recommended_responses else "Monitor and prepare response",
            })
        
        # Sort by opportunity level
        level_order = {"major": 4, "significant": 3, "notable": 2, "marginal": 1}
        opportunities.sort(
            key=lambda o: level_order.get(o.get("opportunity_level", "marginal"), 0),
            reverse=True
        )
        
        return {
            "company_id": company_id,
            "industry": industry,
            "analysis_date": datetime.now().isoformat(),
            "total_opportunities": len(opportunities),
            "top_opportunities": opportunities[:5],
            "by_type": {
                "competitor_weakness": [o for o in opportunities if o["type"] == "competitor_weakness"][:3],
                "market_gap": [o for o in opportunities if o["type"] == "market_gap"][:3],
                "timing": [o for o in opportunities if o["type"] == "competitor_move"][:3],
            },
            "immediate_actions": [
                o["action"] for o in opportunities[:3]
            ],
        }
    
    def get_competitor_comparison(
        self,
        company_id: str,
        competitor_ids: List[str],
        metrics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Compare company against specific competitors.
        
        Args:
            company_id: Company to compare
            competitor_ids: Competitors to compare against
            metrics: Optional specific metrics to compare
            
        Returns:
            Comparison analysis
        """
        competitors = [
            p for p in self._competitor_profiles
            if p.competitor_id in competitor_ids
        ]
        
        if not competitors:
            return {
                "company_id": company_id,
                "error": "No matching competitors found",
            }
        
        default_metrics = ["market_share", "strengths_count", "performance_trend"]
        metrics_to_compare = metrics or default_metrics
        
        comparison = {
            "company_id": company_id,
            "comparison_date": datetime.now().isoformat(),
            "competitors_compared": len(competitors),
            "comparisons": [],
        }
        
        for competitor in competitors:
            comp_data = {
                "competitor_id": competitor.competitor_id,
                "competitor_name": competitor.name,
                "market_position": competitor.market_position,
                "performance_trend": competitor.performance_trend,
                "overlap_scores": {
                    "geographic": competitor.geographic_overlap,
                    "product": competitor.product_overlap,
                    "customer": competitor.customer_overlap,
                    "total": round((
                        competitor.geographic_overlap * 0.3 +
                        competitor.product_overlap * 0.4 +
                        competitor.customer_overlap * 0.3
                    ), 2),
                },
                "strengths": competitor.strengths[:3],
                "weaknesses": competitor.weaknesses[:3],
                "threat_assessment": self._assess_single_competitor_threat(competitor),
            }
            comparison["comparisons"].append(comp_data)
        
        # Summary
        avg_overlap = sum(
            c["overlap_scores"]["total"] for c in comparison["comparisons"]
        ) / len(comparison["comparisons"])
        
        comparison["summary"] = {
            "average_overlap": round(avg_overlap, 2),
            "highest_threat": max(
                comparison["comparisons"],
                key=lambda c: c["threat_assessment"]["score"]
            )["competitor_name"],
            "competitive_environment": self._assess_environment(comparison["comparisons"]),
        }
        
        return comparison
    
    def _is_industry_relevant(self, competitor_id: str, industry: str) -> bool:
        """Check if competitor is relevant to industry."""
        competitor = next(
            (p for p in self._competitor_profiles if p.competitor_id == competitor_id),
            None
        )
        return competitor is not None and competitor.industry == industry
    
    def _extract_key_developments(self, moves: List[CompetitorMove]) -> List[str]:
        """Extract key developments from moves."""
        # Prioritize high-threat moves
        high_priority = [
            m for m in moves
            if m.threat_level in (ThreatLevel.CRITICAL, ThreatLevel.HIGH)
        ]
        
        developments = []
        for move in high_priority[:3]:
            developments.append(f"{move.competitor_name}: {move.description}")
        
        return developments
    
    def _identify_gaps(
        self,
        company_indicators: Optional[Dict[str, float]],
        competitors: List[CompetitorProfile],
    ) -> List[Dict[str, Any]]:
        """Identify gaps relative to competitors."""
        gaps = []
        
        # Analyze based on competitor strengths
        strength_counts = defaultdict(int)
        for comp in competitors:
            for strength in comp.strengths:
                strength_counts[strength] += 1
        
        # Common strengths that company might lack
        for strength, count in strength_counts.items():
            if count >= 2:  # Multiple competitors have this
                gaps.append({
                    "area": strength,
                    "gap_level": "significant" if count >= 3 else "moderate",
                    "competitors_with_strength": count,
                    "recommended_action": f"Develop capabilities in {strength}",
                })
        
        return gaps[:5]
    
    def _identify_advantages(
        self,
        company_indicators: Optional[Dict[str, float]],
        competitors: List[CompetitorProfile],
    ) -> List[Dict[str, Any]]:
        """Identify advantages relative to competitors."""
        advantages = []
        
        # Analyze competitor weaknesses
        weakness_counts = defaultdict(int)
        for comp in competitors:
            for weakness in comp.weaknesses:
                weakness_counts[weakness] += 1
        
        for weakness, count in weakness_counts.items():
            if count >= 2:
                advantages.append({
                    "area": weakness,
                    "advantage_level": "significant" if count >= 3 else "moderate",
                    "competitors_affected": count,
                    "recommended_action": f"Capitalize on competitors' weakness in {weakness}",
                })
        
        return advantages[:5]
    
    def _identify_threats(
        self,
        industry: str,
        competitors: List[CompetitorProfile],
    ) -> List[str]:
        """Identify competitive threats."""
        threats = []
        
        for comp in competitors:
            if comp.performance_trend == "growing":
                threats.append(f"{comp.name} showing strong growth")
            if comp.market_position == "leader":
                threats.append(f"{comp.name} maintains market leadership")
        
        return threats
    
    def _identify_opportunities(
        self,
        industry: str,
        competitors: List[CompetitorProfile],
    ) -> List[str]:
        """Identify competitive opportunities."""
        opportunities = []
        
        for comp in competitors:
            if comp.performance_trend == "declining":
                opportunities.append(f"Capture market share from declining {comp.name}")
            for weakness in comp.weaknesses[:1]:
                opportunities.append(f"Exploit {comp.name}'s weakness: {weakness}")
        
        return opportunities[:5]
    
    def _generate_recommendations(
        self,
        position: str,
        gaps: List[Dict[str, Any]],
        advantages: List[Dict[str, Any]],
        threats: List[str],
        opportunities: List[str],
    ) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        
        if position == "leader":
            recommendations.append("Defend market position through innovation")
        elif position == "challenger":
            recommendations.append("Focus on differentiation to gain market share")
        elif position == "follower":
            recommendations.append("Identify niche segments for focused growth")
        else:
            recommendations.append("Build specialized expertise in chosen niche")
        
        if advantages:
            recommendations.append(f"Leverage advantage in {advantages[0]['area']}")
        
        if gaps:
            recommendations.append(f"Address gap in {gaps[0]['area']}")
        
        return recommendations[:5]
    
    def _calculate_threat_score(
        self,
        competitor: CompetitorProfile,
        recent_moves: List[CompetitorMove],
        event_context: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate threat score for a competitor."""
        base_score = 0.0
        
        # Market position factor
        position_scores = {"leader": 0.3, "challenger": 0.25, "follower": 0.15, "niche": 0.1}
        base_score += position_scores.get(competitor.market_position, 0.1)
        
        # Performance trend factor
        if competitor.performance_trend == "growing":
            base_score += 0.2
        elif competitor.performance_trend == "stable":
            base_score += 0.1
        
        # Overlap factor
        overlap = (
            competitor.geographic_overlap * 0.3 +
            competitor.product_overlap * 0.4 +
            competitor.customer_overlap * 0.3
        )
        base_score += overlap * 0.3
        
        # Recent moves factor
        for move in recent_moves:
            if move.threat_level == ThreatLevel.CRITICAL:
                base_score += 0.15
            elif move.threat_level == ThreatLevel.HIGH:
                base_score += 0.1
            elif move.threat_level == ThreatLevel.MODERATE:
                base_score += 0.05
        
        return min(1.0, base_score)
    
    def _score_to_threat_level(self, score: float) -> str:
        """Convert score to threat level."""
        if score >= 0.7:
            return "critical"
        elif score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "moderate"
        else:
            return "low"
    
    def _get_key_concerns(
        self,
        competitor: CompetitorProfile,
        moves: List[CompetitorMove],
    ) -> List[str]:
        """Get key concerns about a competitor."""
        concerns = []
        
        if competitor.performance_trend == "growing":
            concerns.append("Showing strong growth trajectory")
        
        for move in moves[:2]:
            if move.threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
                concerns.append(move.description)
        
        for strength in competitor.strengths[:1]:
            concerns.append(f"Strong in {strength}")
        
        return concerns[:3]
    
    def _get_threat_response_actions(
        self,
        threats: List[Dict[str, Any]],
    ) -> List[str]:
        """Get recommended actions to respond to threats."""
        actions = []
        
        for threat in threats:
            if threat.get("threat_level") in ("critical", "high"):
                actions.append(f"Monitor {threat['competitor']} closely and prepare competitive response")
        
        if not actions:
            actions.append("Continue regular competitive monitoring")
        
        return actions[:3]
    
    def _get_monitoring_recommendations(
        self,
        threats: List[Dict[str, Any]],
    ) -> List[str]:
        """Get monitoring recommendations."""
        if not threats:
            return ["Maintain regular competitive scanning"]
        
        high_threats = [t for t in threats if t.get("threat_level") in ("critical", "high")]
        
        if high_threats:
            return [
                f"Increase monitoring frequency for {t['competitor']}"
                for t in high_threats[:2]
            ]
        
        return ["Continue standard monitoring schedule"]
    
    def _is_complementary(self, strength: str, weakness: str) -> bool:
        """Check if a strength complements a weakness."""
        # Simple keyword matching
        strength_lower = strength.lower()
        weakness_lower = weakness.lower()
        
        # Check for direct matches or related terms
        return any(
            term in strength_lower and term in weakness_lower
            for term in ["service", "price", "quality", "speed", "innovation", "coverage"]
        )
    
    def _identify_market_gaps(
        self,
        industry: str,
        competitors: List[CompetitorProfile],
    ) -> List[Dict[str, Any]]:
        """Identify gaps in the market."""
        return [
            {
                "description": "Underserved segments",
                "value": "moderate",
                "level": "notable",
                "recommended_action": "Research underserved customer segments",
            }
        ]
    
    def _assess_single_competitor_threat(
        self,
        competitor: CompetitorProfile,
    ) -> Dict[str, Any]:
        """Assess threat from single competitor."""
        overlap = (
            competitor.geographic_overlap * 0.3 +
            competitor.product_overlap * 0.4 +
            competitor.customer_overlap * 0.3
        )
        
        trend_factor = 0.2 if competitor.performance_trend == "growing" else 0.0
        position_factor = 0.2 if competitor.market_position == "leader" else 0.1
        
        score = overlap * 0.6 + trend_factor + position_factor
        
        return {
            "score": round(score, 2),
            "level": self._score_to_threat_level(score),
        }
    
    def _assess_environment(self, comparisons: List[Dict[str, Any]]) -> str:
        """Assess overall competitive environment."""
        high_threats = sum(
            1 for c in comparisons
            if c.get("threat_assessment", {}).get("level") in ("high", "critical")
        )
        
        if high_threats >= 2:
            return "highly_competitive"
        elif high_threats >= 1:
            return "competitive"
        else:
            return "moderate"
    
    def _load_competitor_profiles(self) -> List[CompetitorProfile]:
        """Load competitor profiles."""
        return [
            # Retail industry
            CompetitorProfile(
                competitor_id="comp_retail_1",
                name="MegaMart",
                industry="retail",
                market_share=0.25,
                market_position="leader",
                strengths=["Wide distribution", "Strong brand", "Economies of scale"],
                weaknesses=["Slow to innovate", "Customer service", "Premium positioning"],
                performance_trend="stable",
                estimated_revenue_growth=0.02,
                geographic_overlap=0.8,
                product_overlap=0.7,
                customer_overlap=0.6,
                monitoring_priority="high",
            ),
            CompetitorProfile(
                competitor_id="comp_retail_2",
                name="QuickShop",
                industry="retail",
                market_share=0.15,
                market_position="challenger",
                strengths=["Convenience focus", "Extended hours", "Urban presence"],
                weaknesses=["Limited range", "Higher prices", "Supply chain"],
                performance_trend="growing",
                estimated_revenue_growth=0.08,
                geographic_overlap=0.6,
                product_overlap=0.5,
                customer_overlap=0.7,
                monitoring_priority="high",
            ),
            
            # Manufacturing industry
            CompetitorProfile(
                competitor_id="comp_mfg_1",
                name="IndoProd",
                industry="manufacturing",
                market_share=0.30,
                market_position="leader",
                strengths=["Production capacity", "Technical expertise", "Export relations"],
                weaknesses=["Labor costs", "Energy dependency", "Flexibility"],
                performance_trend="stable",
                estimated_revenue_growth=0.03,
                geographic_overlap=0.5,
                product_overlap=0.6,
                customer_overlap=0.4,
                monitoring_priority="medium",
            ),
            
            # Hospitality industry
            CompetitorProfile(
                competitor_id="comp_hosp_1",
                name="LuxuryStay",
                industry="hospitality",
                market_share=0.20,
                market_position="challenger",
                strengths=["Premium positioning", "Service quality", "Loyalty program"],
                weaknesses=["High costs", "Limited locations", "Seasonal dependency"],
                performance_trend="growing",
                estimated_revenue_growth=0.12,
                geographic_overlap=0.4,
                product_overlap=0.5,
                customer_overlap=0.3,
                monitoring_priority="medium",
            ),
            
            # Logistics industry
            CompetitorProfile(
                competitor_id="comp_log_1",
                name="SwiftDeliver",
                industry="logistics",
                market_share=0.35,
                market_position="leader",
                strengths=["Fleet size", "Technology", "Coverage"],
                weaknesses=["Fuel dependency", "Labor issues", "Urban congestion"],
                performance_trend="growing",
                estimated_revenue_growth=0.10,
                geographic_overlap=0.9,
                product_overlap=0.8,
                customer_overlap=0.7,
                monitoring_priority="high",
            ),
        ]
    
    def _load_recent_competitor_moves(self) -> List[CompetitorMove]:
        """Load recent competitor moves."""
        return [
            CompetitorMove(
                move_id="move_1",
                competitor_id="comp_retail_2",
                competitor_name="QuickShop",
                move_type=CompetitorMoveType.EXPANSION,
                description="Opening 15 new urban locations",
                detected_date=datetime.now() - timedelta(days=5),
                effective_date=datetime.now() + timedelta(days=60),
                threat_level=ThreatLevel.HIGH,
                opportunity_level=OpportunityLevel.MARGINAL,
                affected_segments=["urban_retail", "convenience"],
                affected_regions=["metro_area"],
                implications=["Increased competition in urban areas", "Price pressure possible"],
                recommended_responses=["Review urban strategy", "Strengthen convenience offering"],
                confidence=0.85,
            ),
            CompetitorMove(
                move_id="move_2",
                competitor_id="comp_log_1",
                competitor_name="SwiftDeliver",
                move_type=CompetitorMoveType.PRICING,
                description="Launching aggressive pricing for bulk contracts",
                detected_date=datetime.now() - timedelta(days=10),
                effective_date=datetime.now() - timedelta(days=5),
                threat_level=ThreatLevel.MODERATE,
                opportunity_level=OpportunityLevel.NOTABLE,
                affected_segments=["bulk_logistics", "b2b"],
                affected_regions=["national"],
                implications=["Margin pressure", "Customer retention risk"],
                recommended_responses=["Review pricing structure", "Focus on service differentiation"],
                confidence=0.9,
            ),
            CompetitorMove(
                move_id="move_3",
                competitor_id="comp_hosp_1",
                competitor_name="LuxuryStay",
                move_type=CompetitorMoveType.PRODUCT,
                description="Launching extended stay product line",
                detected_date=datetime.now() - timedelta(days=15),
                effective_date=datetime.now() + timedelta(days=30),
                threat_level=ThreatLevel.MODERATE,
                opportunity_level=OpportunityLevel.SIGNIFICANT,
                affected_segments=["extended_stay", "business_travel"],
                affected_regions=["major_cities"],
                implications=["New segment entry", "Potential demand shift"],
                recommended_responses=["Evaluate extended stay opportunity", "Monitor market response"],
                confidence=0.75,
            ),
        ]
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Load market data."""
        return {
            "retail": {"total_market_size": 1000000000, "growth_rate": 0.03},
            "manufacturing": {"total_market_size": 800000000, "growth_rate": 0.02},
            "hospitality": {"total_market_size": 500000000, "growth_rate": 0.08},
            "logistics": {"total_market_size": 600000000, "growth_rate": 0.05},
        }


# Export for easy importing
__all__ = [
    "CompetitiveIntelligenceAnalyzer",
    "CompetitorProfile",
    "CompetitorMove",
    "MarketPositionAnalysis",
    "CompetitorMoveType",
    "ThreatLevel",
    "OpportunityLevel",
]
