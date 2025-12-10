"""
Layer 4: Industry Context Provider

Provides industry benchmarking, competitor comparisons, and sector-level insights.
Enables contextual understanding of how a company compares to its industry.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class IndustryCategory(str, Enum):
    """Industry categories for benchmarking"""
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    HOSPITALITY = "hospitality"
    LOGISTICS = "logistics"
    AGRICULTURE = "agriculture"
    TECHNOLOGY = "technology"
    FINANCIAL_SERVICES = "financial_services"
    HEALTHCARE = "healthcare"
    CONSTRUCTION = "construction"
    TOURISM = "tourism"
    EXPORT = "export"
    IMPORT = "import"


@dataclass
class IndustryBenchmark:
    """Industry-level benchmark data"""
    industry: str
    indicator_code: str
    indicator_name: str
    industry_average: float
    industry_median: float
    top_quartile: float  # 75th percentile
    bottom_quartile: float  # 25th percentile
    sample_size: int
    as_of: datetime
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0-1


@dataclass
class CompanyBenchmarkResult:
    """Result of comparing a company to industry benchmarks"""
    company_id: str
    industry: str
    indicator_code: str
    company_value: float
    industry_average: float
    percentile_rank: int  # 0-100
    position: str  # 'above_average', 'average', 'below_average'
    gap_to_average: float
    gap_to_top_quartile: float
    comparison_narrative: str


@dataclass
class IndustrySentiment:
    """Industry-level sentiment and outlook"""
    industry: str
    overall_sentiment: str  # 'positive', 'neutral', 'negative'
    sentiment_score: float  # -1 to 1
    key_themes: List[str]
    outlook: str  # 'improving', 'stable', 'declining'
    confidence: float
    as_of: datetime


class IndustryContextProvider:
    """
    Provides industry-level context for business insights.
    
    Features:
    - Industry benchmarking against key indicators
    - Sector sentiment analysis
    - Competitor performance context
    - Industry trend identification
    """
    
    def __init__(self):
        # Industry benchmark data (in production, from database)
        self._benchmarks = self._load_industry_benchmarks()
        self._industry_profiles = self._load_industry_profiles()
        self._sensitivity_matrix = self._build_sensitivity_matrix()
        
        logger.info("Initialized IndustryContextProvider")
    
    def get_industry_benchmark(
        self,
        industry: str,
        indicator_code: str,
    ) -> Optional[IndustryBenchmark]:
        """
        Get benchmark data for a specific industry and indicator.
        
        Args:
            industry: Industry category
            indicator_code: Operational indicator code
            
        Returns:
            IndustryBenchmark with industry statistics
        """
        key = f"{industry}:{indicator_code}"
        return self._benchmarks.get(key)
    
    def compare_to_industry(
        self,
        company_id: str,
        industry: str,
        indicator_code: str,
        company_value: float,
    ) -> CompanyBenchmarkResult:
        """
        Compare a company's indicator value to industry benchmarks.
        
        Args:
            company_id: Company identifier
            industry: Industry category
            indicator_code: Operational indicator code
            company_value: Company's current indicator value
            
        Returns:
            CompanyBenchmarkResult with comparison details
        """
        benchmark = self.get_industry_benchmark(industry, indicator_code)
        
        if not benchmark:
            # Return default if no benchmark exists
            return CompanyBenchmarkResult(
                company_id=company_id,
                industry=industry,
                indicator_code=indicator_code,
                company_value=company_value,
                industry_average=0.5,  # Assume neutral
                percentile_rank=50,
                position="average",
                gap_to_average=0.0,
                gap_to_top_quartile=0.0,
                comparison_narrative="No industry benchmark data available",
            )
        
        # Calculate percentile rank
        percentile = self._calculate_percentile(
            company_value,
            benchmark.bottom_quartile,
            benchmark.industry_median,
            benchmark.top_quartile,
        )
        
        # Determine position
        if company_value >= benchmark.top_quartile:
            position = "top_performer"
        elif company_value >= benchmark.industry_average:
            position = "above_average"
        elif company_value >= benchmark.bottom_quartile:
            position = "below_average"
        else:
            position = "needs_improvement"
        
        # Calculate gaps
        gap_to_average = company_value - benchmark.industry_average
        gap_to_top = benchmark.top_quartile - company_value
        
        # Generate narrative
        narrative = self._generate_benchmark_narrative(
            indicator_code,
            company_value,
            benchmark,
            position,
        )
        
        return CompanyBenchmarkResult(
            company_id=company_id,
            industry=industry,
            indicator_code=indicator_code,
            company_value=company_value,
            industry_average=benchmark.industry_average,
            percentile_rank=percentile,
            position=position,
            gap_to_average=gap_to_average,
            gap_to_top_quartile=gap_to_top,
            comparison_narrative=narrative,
        )
    
    def get_full_benchmark_comparison(
        self,
        company_id: str,
        industry: str,
        company_indicators: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Compare all company indicators to industry benchmarks.
        
        Args:
            company_id: Company identifier
            industry: Industry category
            company_indicators: Dict of indicator_code -> value
            
        Returns:
            Comprehensive benchmark comparison
        """
        comparisons = []
        strengths = []
        weaknesses = []
        
        for indicator_code, value in company_indicators.items():
            result = self.compare_to_industry(
                company_id, industry, indicator_code, value
            )
            comparisons.append(result)
            
            if result.position in ["top_performer", "above_average"]:
                strengths.append({
                    "indicator": indicator_code,
                    "percentile": result.percentile_rank,
                    "gap": result.gap_to_average,
                })
            elif result.position in ["below_average", "needs_improvement"]:
                weaknesses.append({
                    "indicator": indicator_code,
                    "percentile": result.percentile_rank,
                    "gap_to_close": -result.gap_to_average,
                })
        
        # Calculate overall position
        avg_percentile = sum(c.percentile_rank for c in comparisons) / len(comparisons) if comparisons else 50
        
        return {
            "company_id": company_id,
            "industry": industry,
            "as_of": datetime.now(),
            "overall_percentile": round(avg_percentile),
            "overall_position": self._classify_overall_position(avg_percentile),
            "comparisons": [
                {
                    "indicator": c.indicator_code,
                    "company_value": c.company_value,
                    "industry_average": c.industry_average,
                    "percentile": c.percentile_rank,
                    "position": c.position,
                    "narrative": c.comparison_narrative,
                }
                for c in comparisons
            ],
            "strengths": sorted(strengths, key=lambda x: x["percentile"], reverse=True)[:5],
            "weaknesses": sorted(weaknesses, key=lambda x: x["percentile"])[:5],
            "summary": self._generate_overall_summary(industry, avg_percentile, strengths, weaknesses),
        }
    
    def get_industry_sentiment(self, industry: str) -> IndustrySentiment:
        """
        Get current sentiment and outlook for an industry.
        
        Args:
            industry: Industry category
            
        Returns:
            IndustrySentiment with sentiment analysis
        """
        # In production, this would aggregate from news, reports, indicators
        sentiment_data = self._calculate_industry_sentiment(industry)
        return sentiment_data
    
    def get_industry_sensitivities(self, industry: str) -> Dict[str, float]:
        """
        Get industry sensitivity to various indicator categories.
        
        Returns dict of indicator_category -> sensitivity_score (0-1)
        where higher scores mean more sensitive.
        """
        return self._sensitivity_matrix.get(industry, {})
    
    def get_peer_comparison(
        self,
        company_id: str,
        industry: str,
        company_indicators: Dict[str, float],
        num_peers: int = 5,
    ) -> Dict[str, Any]:
        """
        Compare company to simulated peer companies.
        
        Args:
            company_id: Company identifier
            industry: Industry category
            company_indicators: Company's indicator values
            num_peers: Number of peers to compare against
            
        Returns:
            Peer comparison analysis
        """
        # Generate simulated peer data based on industry benchmarks
        peers = self._generate_peer_data(industry, num_peers)
        
        # Calculate company ranking among peers
        company_score = sum(company_indicators.values()) / len(company_indicators) if company_indicators else 0
        
        peer_scores = []
        for peer in peers:
            peer_avg = sum(peer["indicators"].values()) / len(peer["indicators"])
            peer_scores.append({
                "peer_id": peer["peer_id"],
                "score": peer_avg,
            })
        
        # Add company to ranking
        all_scores = peer_scores + [{"peer_id": company_id, "score": company_score}]
        all_scores.sort(key=lambda x: x["score"], reverse=True)
        
        company_rank = next(
            (i + 1 for i, s in enumerate(all_scores) if s["peer_id"] == company_id),
            len(all_scores)
        )
        
        return {
            "company_id": company_id,
            "industry": industry,
            "company_rank": company_rank,
            "total_peers": num_peers + 1,
            "company_score": round(company_score, 2),
            "peer_average": round(sum(s["score"] for s in peer_scores) / len(peer_scores), 2),
            "position_narrative": self._generate_peer_narrative(company_rank, num_peers + 1),
            "peers": peers,
        }
    
    def _load_industry_benchmarks(self) -> Dict[str, IndustryBenchmark]:
        """Load industry benchmark data."""
        benchmarks = {}
        
        # Define benchmarks for each industry and key indicators
        industry_data = {
            "retail": {
                "OPS_SUPPLY_CHAIN": (0.72, 0.70, 0.85, 0.55, "stable"),
                "OPS_POWER_RELIABILITY": (0.80, 0.82, 0.92, 0.68, "stable"),
                "OPS_TRANSPORT_AVAIL": (0.68, 0.65, 0.80, 0.50, "declining"),
                "OPS_LABOR_AVAIL": (0.75, 0.73, 0.88, 0.60, "stable"),
                "OPS_DEMAND_LEVEL": (0.65, 0.62, 0.78, 0.48, "improving"),
            },
            "manufacturing": {
                "OPS_SUPPLY_CHAIN": (0.68, 0.65, 0.82, 0.50, "declining"),
                "OPS_POWER_RELIABILITY": (0.75, 0.73, 0.88, 0.60, "stable"),
                "OPS_EQUIPMENT_STATUS": (0.78, 0.76, 0.90, 0.62, "improving"),
                "OPS_PRODUCTION_CAP": (0.70, 0.68, 0.85, 0.52, "stable"),
                "OPS_QUALITY_CONTROL": (0.82, 0.80, 0.92, 0.68, "improving"),
            },
            "hospitality": {
                "OPS_DEMAND_LEVEL": (0.58, 0.55, 0.72, 0.40, "improving"),
                "OPS_LABOR_AVAIL": (0.65, 0.62, 0.78, 0.48, "declining"),
                "OPS_POWER_RELIABILITY": (0.82, 0.80, 0.92, 0.70, "stable"),
                "OPS_WATER_SUPPLY": (0.78, 0.76, 0.88, 0.62, "stable"),
            },
            "logistics": {
                "OPS_TRANSPORT_AVAIL": (0.62, 0.60, 0.78, 0.45, "declining"),
                "OPS_SUPPLY_CHAIN": (0.65, 0.63, 0.80, 0.48, "declining"),
                "OPS_DEMAND_LEVEL": (0.70, 0.68, 0.82, 0.55, "stable"),
            },
        }
        
        for industry, indicators in industry_data.items():
            for indicator_code, (avg, median, top_q, bottom_q, trend) in indicators.items():
                key = f"{industry}:{indicator_code}"
                benchmarks[key] = IndustryBenchmark(
                    industry=industry,
                    indicator_code=indicator_code,
                    indicator_name=indicator_code.replace("OPS_", "").replace("_", " ").title(),
                    industry_average=avg,
                    industry_median=median,
                    top_quartile=top_q,
                    bottom_quartile=bottom_q,
                    sample_size=50,  # Simulated
                    as_of=datetime.now(),
                    trend_direction=trend,
                    trend_strength=0.6,
                )
        
        return benchmarks
    
    def _load_industry_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load industry profile data."""
        return {
            "retail": {
                "key_indicators": ["OPS_SUPPLY_CHAIN", "OPS_DEMAND_LEVEL", "OPS_TRANSPORT_AVAIL"],
                "typical_margins": (0.15, 0.35),
                "labor_intensity": "high",
                "capital_intensity": "medium",
                "seasonality": "high",
                "import_dependency": 0.6,
            },
            "manufacturing": {
                "key_indicators": ["OPS_SUPPLY_CHAIN", "OPS_POWER_RELIABILITY", "OPS_PRODUCTION_CAP"],
                "typical_margins": (0.08, 0.25),
                "labor_intensity": "medium",
                "capital_intensity": "high",
                "seasonality": "medium",
                "import_dependency": 0.7,
            },
            "hospitality": {
                "key_indicators": ["OPS_DEMAND_LEVEL", "OPS_LABOR_AVAIL", "OPS_POWER_RELIABILITY"],
                "typical_margins": (0.10, 0.30),
                "labor_intensity": "very_high",
                "capital_intensity": "medium",
                "seasonality": "very_high",
                "import_dependency": 0.3,
            },
            "logistics": {
                "key_indicators": ["OPS_TRANSPORT_AVAIL", "OPS_SUPPLY_CHAIN"],
                "typical_margins": (0.05, 0.15),
                "labor_intensity": "medium",
                "capital_intensity": "high",
                "seasonality": "low",
                "import_dependency": 0.4,
            },
        }
    
    def _build_sensitivity_matrix(self) -> Dict[str, Dict[str, float]]:
        """Build industry sensitivity matrix."""
        return {
            "retail": {
                "supply_chain": 0.9,
                "transport": 0.8,
                "power": 0.7,
                "labor": 0.6,
                "currency": 0.7,
                "consumer_sentiment": 0.9,
            },
            "manufacturing": {
                "supply_chain": 0.95,
                "transport": 0.7,
                "power": 0.9,
                "labor": 0.7,
                "currency": 0.8,
                "consumer_sentiment": 0.5,
            },
            "hospitality": {
                "supply_chain": 0.5,
                "transport": 0.6,
                "power": 0.8,
                "labor": 0.9,
                "currency": 0.7,
                "consumer_sentiment": 0.95,
            },
            "logistics": {
                "supply_chain": 0.8,
                "transport": 0.95,
                "power": 0.5,
                "labor": 0.7,
                "currency": 0.6,
                "consumer_sentiment": 0.4,
            },
        }
    
    def _calculate_percentile(
        self,
        value: float,
        bottom_q: float,
        median: float,
        top_q: float,
    ) -> int:
        """Calculate approximate percentile rank."""
        if value <= bottom_q:
            # Below 25th percentile
            return max(1, int(25 * (value / bottom_q))) if bottom_q > 0 else 1
        elif value <= median:
            # Between 25th and 50th percentile
            range_size = median - bottom_q
            position = (value - bottom_q) / range_size if range_size > 0 else 0.5
            return int(25 + 25 * position)
        elif value <= top_q:
            # Between 50th and 75th percentile
            range_size = top_q - median
            position = (value - median) / range_size if range_size > 0 else 0.5
            return int(50 + 25 * position)
        else:
            # Above 75th percentile
            extra = (value - top_q) / (1 - top_q) if top_q < 1 else 0
            return min(99, int(75 + 24 * extra))
    
    def _generate_benchmark_narrative(
        self,
        indicator_code: str,
        company_value: float,
        benchmark: IndustryBenchmark,
        position: str,
    ) -> str:
        """Generate a narrative describing the benchmark comparison."""
        indicator_name = indicator_code.replace("OPS_", "").replace("_", " ").lower()
        
        if position == "top_performer":
            return f"Your {indicator_name} performance ({company_value:.0%}) is among the top 25% in your industry."
        elif position == "above_average":
            return f"Your {indicator_name} ({company_value:.0%}) exceeds the industry average of {benchmark.industry_average:.0%}."
        elif position == "below_average":
            gap = benchmark.industry_average - company_value
            return f"Your {indicator_name} ({company_value:.0%}) is {gap:.0%} below the industry average."
        else:
            return f"Your {indicator_name} ({company_value:.0%}) needs improvement to match industry standards."
    
    def _classify_overall_position(self, avg_percentile: float) -> str:
        """Classify overall industry position."""
        if avg_percentile >= 75:
            return "industry_leader"
        elif avg_percentile >= 50:
            return "competitive"
        elif avg_percentile >= 25:
            return "lagging"
        else:
            return "at_risk"
    
    def _generate_overall_summary(
        self,
        industry: str,
        avg_percentile: float,
        strengths: List[Dict],
        weaknesses: List[Dict],
    ) -> str:
        """Generate overall benchmark summary."""
        position = self._classify_overall_position(avg_percentile)
        
        if position == "industry_leader":
            base = f"You are performing in the top quartile of the {industry} industry."
        elif position == "competitive":
            base = f"You are performing above average in the {industry} industry."
        elif position == "lagging":
            base = f"You are performing below the {industry} industry average."
        else:
            base = f"Significant improvement needed to be competitive in {industry}."
        
        # Add strength/weakness highlights
        if strengths:
            top_strength = strengths[0]["indicator"].replace("OPS_", "").replace("_", " ").lower()
            base += f" Your strongest area is {top_strength}."
        
        if weaknesses:
            top_weakness = weaknesses[0]["indicator"].replace("OPS_", "").replace("_", " ").lower()
            base += f" Focus on improving {top_weakness}."
        
        return base
    
    def _calculate_industry_sentiment(self, industry: str) -> IndustrySentiment:
        """Calculate industry sentiment from available data."""
        # Simulated sentiment calculation
        # In production, would aggregate from news, indicators, reports
        
        sentiment_data = {
            "retail": (0.2, "cautiously_optimistic", ["supply chain recovery", "consumer spending", "digital transformation"]),
            "manufacturing": (-0.1, "cautious", ["input costs", "export demand", "automation"]),
            "hospitality": (0.4, "optimistic", ["tourism recovery", "domestic travel", "events resuming"]),
            "logistics": (-0.2, "concerned", ["fuel costs", "driver shortage", "infrastructure"]),
        }
        
        data = sentiment_data.get(industry, (0.0, "neutral", ["general economic conditions"]))
        
        return IndustrySentiment(
            industry=industry,
            overall_sentiment="positive" if data[0] > 0.2 else ("negative" if data[0] < -0.2 else "neutral"),
            sentiment_score=data[0],
            key_themes=data[2],
            outlook=data[1],
            confidence=0.75,
            as_of=datetime.now(),
        )
    
    def _generate_peer_data(self, industry: str, num_peers: int) -> List[Dict[str, Any]]:
        """Generate simulated peer company data."""
        import random
        
        peers = []
        benchmarks_for_industry = {
            k.split(":")[1]: v 
            for k, v in self._benchmarks.items() 
            if k.startswith(f"{industry}:")
        }
        
        for i in range(num_peers):
            peer_indicators = {}
            for indicator_code, benchmark in benchmarks_for_industry.items():
                # Generate value around industry average with some variance
                value = random.gauss(benchmark.industry_average, 0.1)
                peer_indicators[indicator_code] = max(0, min(1, value))
            
            peers.append({
                "peer_id": f"PEER_{industry.upper()}_{i+1:03d}",
                "indicators": peer_indicators,
            })
        
        return peers
    
    def _generate_peer_narrative(self, rank: int, total: int) -> str:
        """Generate narrative about peer ranking."""
        if rank == 1:
            return "You are the top performer among your peers."
        elif rank <= total // 4:
            return f"You rank #{rank} out of {total}, placing you in the top quartile."
        elif rank <= total // 2:
            return f"You rank #{rank} out of {total}, above the peer average."
        elif rank <= 3 * total // 4:
            return f"You rank #{rank} out of {total}, below the peer average."
        else:
            return f"You rank #{rank} out of {total}, indicating room for improvement."


# Export for easy importing
__all__ = [
    "IndustryContextProvider",
    "IndustryBenchmark",
    "CompanyBenchmarkResult",
    "IndustrySentiment",
    "IndustryCategory",
]
