"""
Portfolio Analysis Module.

Provides multi-company portfolio risk analysis including:
- Portfolio risk aggregation
- Diversification analysis
- Concentration alerts
- Cross-company correlations
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import math


class RiskLevel(Enum):
    """Portfolio risk levels."""
    CRITICAL = "critical"
    HIGH = "high"
    ELEVATED = "elevated"
    MODERATE = "moderate"
    LOW = "low"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CompanyRiskProfile:
    """Risk profile for a single company."""
    company_id: str
    company_name: str
    sector: str
    region: str
    
    # Risk scores
    overall_risk: float = 0.0
    supply_chain_risk: float = 0.0
    operational_risk: float = 0.0
    financial_risk: float = 0.0
    market_risk: float = 0.0
    
    # Indicators
    key_indicators: Dict[str, float] = field(default_factory=dict)
    
    # Weight in portfolio
    portfolio_weight: float = 0.0
    
    # Last updated
    last_updated: Optional[datetime] = None


@dataclass
class DiversificationScore:
    """Diversification analysis result."""
    overall_score: float  # 0-1, higher is better
    
    # Component scores
    sector_diversification: float = 0.0
    regional_diversification: float = 0.0
    size_diversification: float = 0.0
    
    # Concentrations
    sector_concentration: Dict[str, float] = field(default_factory=dict)
    regional_concentration: Dict[str, float] = field(default_factory=dict)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ConcentrationAlert:
    """Alert for portfolio concentration risk."""
    alert_id: str
    alert_type: str  # "sector", "regional", "company", "risk_factor"
    severity: AlertSeverity
    
    # Details
    concentrated_element: str
    concentration_percentage: float
    threshold_exceeded: float
    
    # Impact
    potential_impact: str
    affected_companies: List[str] = field(default_factory=list)
    
    # Recommendation
    recommendation: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PortfolioRisk:
    """Overall portfolio risk assessment."""
    portfolio_id: str
    calculated_at: datetime
    
    # Aggregate risk scores
    overall_risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.MODERATE
    
    # Component risks
    weighted_supply_risk: float = 0.0
    weighted_operational_risk: float = 0.0
    weighted_financial_risk: float = 0.0
    weighted_market_risk: float = 0.0
    
    # Correlations
    average_correlation: float = 0.0
    max_correlation: float = 0.0
    correlation_risk_adjustment: float = 0.0
    
    # Value at Risk (simplified)
    var_95: float = 0.0  # 95% confidence
    var_99: float = 0.0  # 99% confidence
    
    # Risk contributors
    top_risk_contributors: List[str] = field(default_factory=list)
    risk_by_sector: Dict[str, float] = field(default_factory=dict)
    risk_by_region: Dict[str, float] = field(default_factory=dict)


@dataclass
class Portfolio:
    """Portfolio of companies."""
    portfolio_id: str
    name: str
    created_at: datetime
    
    # Companies
    companies: Dict[str, CompanyRiskProfile] = field(default_factory=dict)
    
    # Portfolio metadata
    total_companies: int = 0
    sectors: Set[str] = field(default_factory=set)
    regions: Set[str] = field(default_factory=set)
    
    # Risk assessment
    current_risk: Optional[PortfolioRisk] = None
    diversification: Optional[DiversificationScore] = None
    alerts: List[ConcentrationAlert] = field(default_factory=list)


class PortfolioAnalyzer:
    """
    Portfolio risk analyzer for multi-company analysis.
    
    Provides portfolio-level risk assessment, diversification
    analysis, and concentration alerts.
    """
    
    def __init__(self):
        """Initialize the portfolio analyzer."""
        self._portfolios: Dict[str, Portfolio] = {}
        self._correlations: Dict[str, Dict[str, float]] = {}
        self._alert_counter = 0
        
        # Configuration thresholds
        self._sector_concentration_threshold = 0.4  # 40%
        self._regional_concentration_threshold = 0.5  # 50%
        self._company_concentration_threshold = 0.25  # 25%
        self._correlation_threshold = 0.7
    
    def create_portfolio(
        self,
        portfolio_id: str,
        name: str,
    ) -> Portfolio:
        """Create a new portfolio."""
        portfolio = Portfolio(
            portfolio_id=portfolio_id,
            name=name,
            created_at=datetime.now(),
        )
        self._portfolios[portfolio_id] = portfolio
        return portfolio
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Portfolio]:
        """Get a portfolio by ID."""
        return self._portfolios.get(portfolio_id)
    
    def add_company(
        self,
        portfolio_id: str,
        company_id: str,
        company_name: str,
        sector: str,
        region: str,
        portfolio_weight: float = 0.0,
        risk_scores: Optional[Dict[str, float]] = None,
        indicators: Optional[Dict[str, float]] = None,
    ) -> CompanyRiskProfile:
        """Add a company to a portfolio."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        risk_scores = risk_scores or {}
        
        profile = CompanyRiskProfile(
            company_id=company_id,
            company_name=company_name,
            sector=sector,
            region=region,
            overall_risk=risk_scores.get("overall", 0.5),
            supply_chain_risk=risk_scores.get("supply_chain", 0.5),
            operational_risk=risk_scores.get("operational", 0.5),
            financial_risk=risk_scores.get("financial", 0.5),
            market_risk=risk_scores.get("market", 0.5),
            key_indicators=indicators or {},
            portfolio_weight=portfolio_weight,
            last_updated=datetime.now(),
        )
        
        portfolio.companies[company_id] = profile
        portfolio.total_companies = len(portfolio.companies)
        portfolio.sectors.add(sector)
        portfolio.regions.add(region)
        
        # Rebalance weights if needed
        if portfolio_weight == 0.0:
            self._rebalance_weights(portfolio)
        
        return profile
    
    def remove_company(self, portfolio_id: str, company_id: str) -> bool:
        """Remove a company from a portfolio."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            return False
        
        if company_id in portfolio.companies:
            del portfolio.companies[company_id]
            portfolio.total_companies = len(portfolio.companies)
            self._rebalance_weights(portfolio)
            return True
        
        return False
    
    def _rebalance_weights(self, portfolio: Portfolio) -> None:
        """Rebalance company weights to sum to 1.0."""
        if not portfolio.companies:
            return
        
        equal_weight = 1.0 / len(portfolio.companies)
        for profile in portfolio.companies.values():
            profile.portfolio_weight = equal_weight
    
    def update_company_risk(
        self,
        portfolio_id: str,
        company_id: str,
        risk_scores: Dict[str, float],
        indicators: Optional[Dict[str, float]] = None,
    ) -> Optional[CompanyRiskProfile]:
        """Update risk scores for a company."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio or company_id not in portfolio.companies:
            return None
        
        profile = portfolio.companies[company_id]
        
        profile.overall_risk = risk_scores.get("overall", profile.overall_risk)
        profile.supply_chain_risk = risk_scores.get(
            "supply_chain", profile.supply_chain_risk
        )
        profile.operational_risk = risk_scores.get(
            "operational", profile.operational_risk
        )
        profile.financial_risk = risk_scores.get(
            "financial", profile.financial_risk
        )
        profile.market_risk = risk_scores.get("market", profile.market_risk)
        
        if indicators:
            profile.key_indicators.update(indicators)
        
        profile.last_updated = datetime.now()
        
        return profile
    
    def calculate_portfolio_risk(
        self,
        portfolio_id: str,
        include_correlations: bool = True,
    ) -> PortfolioRisk:
        """Calculate overall portfolio risk."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        if not portfolio.companies:
            return PortfolioRisk(
                portfolio_id=portfolio_id,
                calculated_at=datetime.now(),
                risk_level=RiskLevel.LOW,
            )
        
        # Calculate weighted risks
        weighted_supply = 0.0
        weighted_operational = 0.0
        weighted_financial = 0.0
        weighted_market = 0.0
        
        risk_contributions = []
        
        for profile in portfolio.companies.values():
            weight = profile.portfolio_weight
            
            weighted_supply += profile.supply_chain_risk * weight
            weighted_operational += profile.operational_risk * weight
            weighted_financial += profile.financial_risk * weight
            weighted_market += profile.market_risk * weight
            
            risk_contributions.append(
                (profile.company_id, profile.overall_risk * weight)
            )
        
        # Sort by contribution
        risk_contributions.sort(key=lambda x: x[1], reverse=True)
        top_contributors = [c[0] for c in risk_contributions[:5]]
        
        # Calculate overall risk
        overall_risk = (
            weighted_supply * 0.3 +
            weighted_operational * 0.25 +
            weighted_financial * 0.25 +
            weighted_market * 0.2
        )
        
        # Correlation adjustment
        avg_corr = 0.0
        max_corr = 0.0
        correlation_adjustment = 0.0
        
        if include_correlations and len(portfolio.companies) > 1:
            correlations = self._calculate_company_correlations(portfolio)
            if correlations:
                avg_corr = sum(correlations) / len(correlations)
                max_corr = max(correlations)
                # Higher correlation increases risk
                correlation_adjustment = avg_corr * 0.1
                overall_risk += correlation_adjustment
        
        overall_risk = min(1.0, overall_risk)
        
        # Determine risk level
        risk_level = self._get_risk_level(overall_risk)
        
        # Calculate VaR (simplified)
        var_95 = overall_risk * 1.65  # 95% confidence
        var_99 = overall_risk * 2.33  # 99% confidence
        
        # Risk by sector
        risk_by_sector: Dict[str, float] = {}
        risk_by_region: Dict[str, float] = {}
        
        for profile in portfolio.companies.values():
            if profile.sector not in risk_by_sector:
                risk_by_sector[profile.sector] = 0.0
            risk_by_sector[profile.sector] += (
                profile.overall_risk * profile.portfolio_weight
            )
            
            if profile.region not in risk_by_region:
                risk_by_region[profile.region] = 0.0
            risk_by_region[profile.region] += (
                profile.overall_risk * profile.portfolio_weight
            )
        
        portfolio_risk = PortfolioRisk(
            portfolio_id=portfolio_id,
            calculated_at=datetime.now(),
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            weighted_supply_risk=weighted_supply,
            weighted_operational_risk=weighted_operational,
            weighted_financial_risk=weighted_financial,
            weighted_market_risk=weighted_market,
            average_correlation=avg_corr,
            max_correlation=max_corr,
            correlation_risk_adjustment=correlation_adjustment,
            var_95=var_95,
            var_99=var_99,
            top_risk_contributors=top_contributors,
            risk_by_sector=risk_by_sector,
            risk_by_region=risk_by_region,
        )
        
        portfolio.current_risk = portfolio_risk
        return portfolio_risk
    
    def _calculate_company_correlations(
        self,
        portfolio: Portfolio,
    ) -> List[float]:
        """Calculate correlations between companies in portfolio."""
        correlations = []
        
        companies = list(portfolio.companies.values())
        
        for i in range(len(companies)):
            for j in range(i + 1, len(companies)):
                # Simple correlation based on indicator similarity
                corr = self._calculate_indicator_correlation(
                    companies[i], companies[j]
                )
                correlations.append(corr)
        
        return correlations
    
    def _calculate_indicator_correlation(
        self,
        company1: CompanyRiskProfile,
        company2: CompanyRiskProfile,
    ) -> float:
        """Calculate correlation between two companies based on indicators."""
        # Find common indicators
        common_keys = set(company1.key_indicators.keys()) & set(
            company2.key_indicators.keys()
        )
        
        if not common_keys:
            # Same sector/region = assumed correlation
            corr = 0.0
            if company1.sector == company2.sector:
                corr += 0.3
            if company1.region == company2.region:
                corr += 0.2
            return corr
        
        # Calculate similarity
        differences = []
        for key in common_keys:
            diff = abs(
                company1.key_indicators[key] - company2.key_indicators[key]
            )
            differences.append(diff)
        
        avg_diff = sum(differences) / len(differences)
        
        # Convert difference to correlation (inverse relationship)
        correlation = max(0.0, 1.0 - avg_diff)
        
        return correlation
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to level."""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.ELEVATED
        elif risk_score >= 0.2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def analyze_diversification(
        self,
        portfolio_id: str,
    ) -> DiversificationScore:
        """Analyze portfolio diversification."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        if not portfolio.companies:
            return DiversificationScore(overall_score=0.0)
        
        # Calculate sector concentration
        sector_weights: Dict[str, float] = {}
        regional_weights: Dict[str, float] = {}
        
        for profile in portfolio.companies.values():
            if profile.sector not in sector_weights:
                sector_weights[profile.sector] = 0.0
            sector_weights[profile.sector] += profile.portfolio_weight
            
            if profile.region not in regional_weights:
                regional_weights[profile.region] = 0.0
            regional_weights[profile.region] += profile.portfolio_weight
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        sector_hhi = sum(w ** 2 for w in sector_weights.values())
        regional_hhi = sum(w ** 2 for w in regional_weights.values())
        
        # Convert HHI to diversification score (inverse)
        # HHI ranges from 1/n (perfect diversification) to 1 (full concentration)
        n_sectors = len(sector_weights)
        n_regions = len(regional_weights)
        
        min_sector_hhi = 1 / n_sectors if n_sectors > 0 else 1
        min_regional_hhi = 1 / n_regions if n_regions > 0 else 1
        
        sector_diversification = (
            (1 - sector_hhi) / (1 - min_sector_hhi)
            if min_sector_hhi < 1
            else 0.0
        )
        regional_diversification = (
            (1 - regional_hhi) / (1 - min_regional_hhi)
            if min_regional_hhi < 1
            else 0.0
        )
        
        # Size diversification (assume equal weight is ideal)
        weights = [p.portfolio_weight for p in portfolio.companies.values()]
        weight_variance = sum((w - 1/len(weights)) ** 2 for w in weights) / len(weights)
        size_diversification = max(0.0, 1.0 - weight_variance * 10)
        
        # Overall score
        overall_score = (
            sector_diversification * 0.4 +
            regional_diversification * 0.35 +
            size_diversification * 0.25
        )
        
        # Generate recommendations
        recommendations = []
        
        for sector, weight in sector_weights.items():
            if weight > self._sector_concentration_threshold:
                recommendations.append(
                    f"Reduce {sector} sector concentration from {weight:.1%}"
                )
        
        for region, weight in regional_weights.items():
            if weight > self._regional_concentration_threshold:
                recommendations.append(
                    f"Reduce {region} regional concentration from {weight:.1%}"
                )
        
        if overall_score < 0.5:
            recommendations.append(
                "Consider adding companies from different sectors/regions"
            )
        
        diversification = DiversificationScore(
            overall_score=overall_score,
            sector_diversification=sector_diversification,
            regional_diversification=regional_diversification,
            size_diversification=size_diversification,
            sector_concentration=sector_weights,
            regional_concentration=regional_weights,
            recommendations=recommendations,
        )
        
        portfolio.diversification = diversification
        return diversification
    
    def check_concentration_alerts(
        self,
        portfolio_id: str,
    ) -> List[ConcentrationAlert]:
        """Check for concentration risk alerts."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        alerts: List[ConcentrationAlert] = []
        
        if not portfolio.companies:
            return alerts
        
        # Check sector concentration
        sector_weights: Dict[str, List[str]] = {}
        for profile in portfolio.companies.values():
            if profile.sector not in sector_weights:
                sector_weights[profile.sector] = []
            sector_weights[profile.sector].append(profile.company_id)
        
        for sector, companies in sector_weights.items():
            concentration = len(companies) / len(portfolio.companies)
            if concentration > self._sector_concentration_threshold:
                self._alert_counter += 1
                alerts.append(
                    ConcentrationAlert(
                        alert_id=f"alert_{self._alert_counter}",
                        alert_type="sector",
                        severity=self._get_alert_severity(concentration),
                        concentrated_element=sector,
                        concentration_percentage=concentration,
                        threshold_exceeded=self._sector_concentration_threshold,
                        potential_impact=(
                            f"Sector-wide issues in {sector} could affect "
                            f"{concentration:.0%} of portfolio"
                        ),
                        affected_companies=companies,
                        recommendation=(
                            f"Consider reducing exposure to {sector} sector"
                        ),
                    )
                )
        
        # Check regional concentration
        regional_weights: Dict[str, List[str]] = {}
        for profile in portfolio.companies.values():
            if profile.region not in regional_weights:
                regional_weights[profile.region] = []
            regional_weights[profile.region].append(profile.company_id)
        
        for region, companies in regional_weights.items():
            concentration = len(companies) / len(portfolio.companies)
            if concentration > self._regional_concentration_threshold:
                self._alert_counter += 1
                alerts.append(
                    ConcentrationAlert(
                        alert_id=f"alert_{self._alert_counter}",
                        alert_type="regional",
                        severity=self._get_alert_severity(concentration),
                        concentrated_element=region,
                        concentration_percentage=concentration,
                        threshold_exceeded=self._regional_concentration_threshold,
                        potential_impact=(
                            f"Regional issues in {region} could affect "
                            f"{concentration:.0%} of portfolio"
                        ),
                        affected_companies=companies,
                        recommendation=(
                            f"Consider adding companies from other regions"
                        ),
                    )
                )
        
        # Check individual company concentration
        for profile in portfolio.companies.values():
            if profile.portfolio_weight > self._company_concentration_threshold:
                self._alert_counter += 1
                alerts.append(
                    ConcentrationAlert(
                        alert_id=f"alert_{self._alert_counter}",
                        alert_type="company",
                        severity=self._get_alert_severity(profile.portfolio_weight),
                        concentrated_element=profile.company_name,
                        concentration_percentage=profile.portfolio_weight,
                        threshold_exceeded=self._company_concentration_threshold,
                        potential_impact=(
                            f"Issues with {profile.company_name} could "
                            f"significantly impact portfolio"
                        ),
                        affected_companies=[profile.company_id],
                        recommendation=(
                            f"Consider reducing weight of {profile.company_name}"
                        ),
                    )
                )
        
        portfolio.alerts = alerts
        return alerts
    
    def _get_alert_severity(self, concentration: float) -> AlertSeverity:
        """Determine alert severity based on concentration level."""
        if concentration >= 0.7:
            return AlertSeverity.CRITICAL
        elif concentration >= 0.5:
            return AlertSeverity.HIGH
        elif concentration >= 0.35:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def get_stress_test_results(
        self,
        portfolio_id: str,
        stress_scenario: str = "market_crash",
    ) -> Dict[str, Any]:
        """Run stress test on portfolio."""
        portfolio = self._portfolios.get(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        # Define stress multipliers
        stress_multipliers = {
            "market_crash": {
                "supply_chain": 1.5,
                "operational": 1.3,
                "financial": 2.0,
                "market": 2.5,
            },
            "supply_disruption": {
                "supply_chain": 3.0,
                "operational": 1.8,
                "financial": 1.2,
                "market": 1.1,
            },
            "economic_recession": {
                "supply_chain": 1.2,
                "operational": 1.4,
                "financial": 1.8,
                "market": 1.5,
            },
        }
        
        multipliers = stress_multipliers.get(
            stress_scenario,
            stress_multipliers["market_crash"],
        )
        
        # Calculate stressed risks
        stressed_risks = {}
        for company_id, profile in portfolio.companies.items():
            stressed_overall = min(1.0, (
                profile.supply_chain_risk * multipliers["supply_chain"] * 0.25 +
                profile.operational_risk * multipliers["operational"] * 0.25 +
                profile.financial_risk * multipliers["financial"] * 0.25 +
                profile.market_risk * multipliers["market"] * 0.25
            ))
            stressed_risks[company_id] = stressed_overall
        
        # Calculate stressed portfolio risk
        stressed_portfolio_risk = sum(
            stressed_risks[cid] * profile.portfolio_weight
            for cid, profile in portfolio.companies.items()
        )
        
        return {
            "scenario": stress_scenario,
            "original_risk": portfolio.current_risk.overall_risk_score
            if portfolio.current_risk
            else 0.5,
            "stressed_risk": stressed_portfolio_risk,
            "risk_increase": stressed_portfolio_risk - (
                portfolio.current_risk.overall_risk_score
                if portfolio.current_risk
                else 0.5
            ),
            "company_stressed_risks": stressed_risks,
            "most_affected": max(stressed_risks, key=stressed_risks.get)
            if stressed_risks
            else None,
        }
    
    def list_portfolios(self) -> List[str]:
        """List all portfolio IDs."""
        return list(self._portfolios.keys())
    
    def delete_portfolio(self, portfolio_id: str) -> bool:
        """Delete a portfolio."""
        if portfolio_id in self._portfolios:
            del self._portfolios[portfolio_id]
            return True
        return False
