"""
Correlation Analysis Module.

Provides cross-indicator relationship analysis including:
- Correlation matrix calculation
- Lead/lag relationship detection
- Causal inference
- Indicator clustering
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math


class CorrelationType(Enum):
    """Types of correlations."""
    STRONG_POSITIVE = "strong_positive"  # >= 0.7
    MODERATE_POSITIVE = "moderate_positive"  # >= 0.4
    WEAK_POSITIVE = "weak_positive"  # >= 0.2
    NONE = "none"  # -0.2 to 0.2
    WEAK_NEGATIVE = "weak_negative"  # <= -0.2
    MODERATE_NEGATIVE = "moderate_negative"  # <= -0.4
    STRONG_NEGATIVE = "strong_negative"  # <= -0.7


class CausalDirection(Enum):
    """Direction of causal relationship."""
    A_CAUSES_B = "a_causes_b"
    B_CAUSES_A = "b_causes_a"
    BIDIRECTIONAL = "bidirectional"
    NO_CAUSATION = "no_causation"
    UNKNOWN = "unknown"


@dataclass
class CorrelationPair:
    """Correlation between two indicators."""
    indicator_a: str
    indicator_b: str
    correlation: float
    correlation_type: CorrelationType
    
    # Statistical significance
    p_value: float = 0.0
    is_significant: bool = True
    
    # Sample info
    sample_size: int = 0
    
    # Time period
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


@dataclass
class CorrelationMatrix:
    """Full correlation matrix for indicators."""
    matrix_id: str
    calculated_at: datetime
    
    # Matrix data (indicator -> indicator -> correlation)
    correlations: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Correlation pairs for easy access
    pairs: List[CorrelationPair] = field(default_factory=list)
    
    # Statistics
    strongest_positive: Optional[CorrelationPair] = None
    strongest_negative: Optional[CorrelationPair] = None
    average_correlation: float = 0.0
    
    # Indicators included
    indicators: List[str] = field(default_factory=list)
    sample_size: int = 0


@dataclass
class LeadLagRelation:
    """Lead/lag relationship between indicators."""
    leading_indicator: str
    lagging_indicator: str
    
    # Relationship parameters
    lag_days: int = 0
    correlation_at_lag: float = 0.0
    correlation_type: CorrelationType = CorrelationType.NONE
    
    # Confidence
    confidence: float = 0.0
    
    # Predictive power
    predictive_power: float = 0.0  # R-squared for lagged prediction


@dataclass
class CausalLink:
    """Inferred causal relationship."""
    indicator_a: str
    indicator_b: str
    
    # Causality
    direction: CausalDirection
    causal_strength: float = 0.0
    
    # Evidence
    granger_statistic: float = 0.0
    p_value: float = 0.0
    
    # Interpretation
    explanation: str = ""
    confidence: str = "low"  # low, medium, high


@dataclass
class IndicatorRelationship:
    """Comprehensive relationship between two indicators."""
    indicator_a: str
    indicator_b: str
    
    # Correlation
    correlation: CorrelationPair = field(default_factory=lambda: CorrelationPair(
        indicator_a="", indicator_b="", correlation=0.0, correlation_type=CorrelationType.NONE
    ))
    
    # Lead/lag
    lead_lag: Optional[LeadLagRelation] = None
    
    # Causality
    causal_link: Optional[CausalLink] = None
    
    # Clustering
    same_cluster: bool = False
    cluster_id: Optional[str] = None
    
    # Summary
    relationship_strength: str = "none"  # none, weak, moderate, strong
    relationship_summary: str = ""


@dataclass
class IndicatorCluster:
    """Cluster of related indicators."""
    cluster_id: str
    name: str
    
    # Indicators in cluster
    indicators: List[str] = field(default_factory=list)
    
    # Cluster properties
    average_internal_correlation: float = 0.0
    centroid_indicator: str = ""
    
    # Description
    description: str = ""


class CorrelationAnalyzer:
    """
    Correlation analysis engine for indicator relationships.
    
    Provides correlation matrix calculation, lead/lag detection,
    and causal inference capabilities.
    """
    
    def __init__(self):
        """Initialize the correlation analyzer."""
        self._historical_data: Dict[str, List[Tuple[datetime, Dict[str, float]]]] = {}
        self._correlation_matrices: Dict[str, CorrelationMatrix] = {}
        self._relationships: Dict[str, IndicatorRelationship] = {}
        self._clusters: Dict[str, IndicatorCluster] = {}
        self._matrix_counter = 0
        self._cluster_counter = 0
    
    def add_data_point(
        self,
        company_id: str,
        timestamp: datetime,
        indicators: Dict[str, float],
    ) -> None:
        """Add a data point for correlation analysis."""
        if company_id not in self._historical_data:
            self._historical_data[company_id] = []
        
        self._historical_data[company_id].append((timestamp, indicators.copy()))
        
        # Sort by timestamp
        self._historical_data[company_id].sort(key=lambda x: x[0])
        
        # Keep only last 365 days
        cutoff = datetime.now() - timedelta(days=365)
        self._historical_data[company_id] = [
            dp for dp in self._historical_data[company_id]
            if dp[0] > cutoff
        ]
    
    def add_historical_data(
        self,
        company_id: str,
        data: List[Tuple[datetime, Dict[str, float]]],
    ) -> None:
        """Add batch historical data."""
        for timestamp, indicators in data:
            self.add_data_point(company_id, timestamp, indicators)
    
    def calculate_correlation_matrix(
        self,
        company_id: str,
        indicators: Optional[List[str]] = None,
    ) -> CorrelationMatrix:
        """
        Calculate correlation matrix for a company.
        
        Args:
            company_id: Company to analyze
            indicators: Specific indicators to include (all if None)
            
        Returns:
            CorrelationMatrix with all correlations
        """
        data = self._historical_data.get(company_id, [])
        if len(data) < 2:
            raise ValueError(f"Insufficient data for company {company_id}")
        
        self._matrix_counter += 1
        matrix_id = f"matrix_{self._matrix_counter}"
        
        # Get indicator list
        all_indicators = set()
        for _, ind_values in data:
            all_indicators.update(ind_values.keys())
        
        if indicators:
            all_indicators = all_indicators.intersection(set(indicators))
        
        indicator_list = sorted(list(all_indicators))
        
        # Build time series for each indicator
        time_series: Dict[str, List[float]] = {ind: [] for ind in indicator_list}
        
        for _, ind_values in data:
            for ind in indicator_list:
                time_series[ind].append(ind_values.get(ind, 0.0))
        
        # Calculate correlations
        correlations: Dict[str, Dict[str, float]] = {}
        pairs: List[CorrelationPair] = []
        
        for i, ind_a in enumerate(indicator_list):
            correlations[ind_a] = {}
            for j, ind_b in enumerate(indicator_list):
                if i == j:
                    correlations[ind_a][ind_b] = 1.0
                elif j < i:
                    # Already calculated
                    correlations[ind_a][ind_b] = correlations[ind_b][ind_a]
                else:
                    corr = self._pearson_correlation(
                        time_series[ind_a],
                        time_series[ind_b],
                    )
                    correlations[ind_a][ind_b] = corr
                    
                    pair = CorrelationPair(
                        indicator_a=ind_a,
                        indicator_b=ind_b,
                        correlation=corr,
                        correlation_type=self._get_correlation_type(corr),
                        sample_size=len(data),
                        period_start=data[0][0],
                        period_end=data[-1][0],
                    )
                    pairs.append(pair)
        
        # Find strongest correlations
        positive_pairs = [p for p in pairs if p.correlation > 0]
        negative_pairs = [p for p in pairs if p.correlation < 0]
        
        strongest_positive = max(positive_pairs, key=lambda x: x.correlation) if positive_pairs else None
        strongest_negative = min(negative_pairs, key=lambda x: x.correlation) if negative_pairs else None
        
        # Calculate average
        avg_corr = sum(p.correlation for p in pairs) / len(pairs) if pairs else 0.0
        
        matrix = CorrelationMatrix(
            matrix_id=matrix_id,
            calculated_at=datetime.now(),
            correlations=correlations,
            pairs=pairs,
            strongest_positive=strongest_positive,
            strongest_negative=strongest_negative,
            average_correlation=avg_corr,
            indicators=indicator_list,
            sample_size=len(data),
        )
        
        self._correlation_matrices[matrix_id] = matrix
        return matrix
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        
        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _get_correlation_type(self, corr: float) -> CorrelationType:
        """Convert correlation value to type."""
        if corr >= 0.7:
            return CorrelationType.STRONG_POSITIVE
        elif corr >= 0.4:
            return CorrelationType.MODERATE_POSITIVE
        elif corr >= 0.2:
            return CorrelationType.WEAK_POSITIVE
        elif corr > -0.2:
            return CorrelationType.NONE
        elif corr > -0.4:
            return CorrelationType.WEAK_NEGATIVE
        elif corr > -0.7:
            return CorrelationType.MODERATE_NEGATIVE
        else:
            return CorrelationType.STRONG_NEGATIVE
    
    def detect_lead_lag(
        self,
        company_id: str,
        indicator_a: str,
        indicator_b: str,
        max_lag_days: int = 30,
    ) -> LeadLagRelation:
        """
        Detect lead/lag relationship between two indicators.
        
        Args:
            company_id: Company to analyze
            indicator_a: First indicator
            indicator_b: Second indicator
            max_lag_days: Maximum lag to test
            
        Returns:
            LeadLagRelation with detected relationship
        """
        data = self._historical_data.get(company_id, [])
        if len(data) < max_lag_days + 5:
            raise ValueError("Insufficient data for lead/lag detection")
        
        # Build time series
        series_a = [d[1].get(indicator_a, 0.0) for d in data]
        series_b = [d[1].get(indicator_b, 0.0) for d in data]
        
        best_lag = 0
        best_correlation = 0.0
        
        # Test different lags
        for lag in range(-max_lag_days, max_lag_days + 1):
            if lag == 0:
                lagged_a = series_a
                lagged_b = series_b
            elif lag > 0:
                # A leads B by 'lag' days
                lagged_a = series_a[:-lag]
                lagged_b = series_b[lag:]
            else:
                # B leads A by 'abs(lag)' days
                lagged_a = series_a[abs(lag):]
                lagged_b = series_b[:lag]
            
            if len(lagged_a) >= 2:
                corr = abs(self._pearson_correlation(lagged_a, lagged_b))
                if corr > best_correlation:
                    best_correlation = corr
                    best_lag = lag
        
        # Determine leading indicator
        if best_lag > 0:
            leading = indicator_a
            lagging = indicator_b
            lag_days = best_lag
        elif best_lag < 0:
            leading = indicator_b
            lagging = indicator_a
            lag_days = abs(best_lag)
        else:
            leading = indicator_a
            lagging = indicator_b
            lag_days = 0
        
        # Get actual correlation value (with sign)
        if lag_days > 0:
            if best_lag > 0:
                lagged_a = series_a[:-lag_days]
                lagged_b = series_b[lag_days:]
            else:
                lagged_a = series_a[lag_days:]
                lagged_b = series_b[:-lag_days]
            actual_corr = self._pearson_correlation(lagged_a, lagged_b)
        else:
            actual_corr = self._pearson_correlation(series_a, series_b)
        
        return LeadLagRelation(
            leading_indicator=leading,
            lagging_indicator=lagging,
            lag_days=lag_days,
            correlation_at_lag=actual_corr,
            correlation_type=self._get_correlation_type(actual_corr),
            confidence=best_correlation,
            predictive_power=best_correlation ** 2,
        )
    
    def infer_causality(
        self,
        company_id: str,
        indicator_a: str,
        indicator_b: str,
        lag_order: int = 5,
    ) -> CausalLink:
        """
        Infer causal relationship using Granger-like test.
        
        Args:
            company_id: Company to analyze
            indicator_a: First indicator
            indicator_b: Second indicator
            lag_order: Number of lags to include
            
        Returns:
            CausalLink with inferred causality
        """
        data = self._historical_data.get(company_id, [])
        if len(data) < lag_order + 10:
            raise ValueError("Insufficient data for causal inference")
        
        series_a = [d[1].get(indicator_a, 0.0) for d in data]
        series_b = [d[1].get(indicator_b, 0.0) for d in data]
        
        # Simple Granger-like test: compare predictive power
        # Does A help predict B?
        a_predicts_b = self._test_predictive_power(series_a, series_b, lag_order)
        
        # Does B help predict A?
        b_predicts_a = self._test_predictive_power(series_b, series_a, lag_order)
        
        # Determine direction
        threshold = 0.1  # Minimum improvement to consider causal
        
        if a_predicts_b > threshold and b_predicts_a > threshold:
            direction = CausalDirection.BIDIRECTIONAL
            strength = (a_predicts_b + b_predicts_a) / 2
        elif a_predicts_b > threshold:
            direction = CausalDirection.A_CAUSES_B
            strength = a_predicts_b
        elif b_predicts_a > threshold:
            direction = CausalDirection.B_CAUSES_A
            strength = b_predicts_a
        else:
            direction = CausalDirection.NO_CAUSATION
            strength = 0.0
        
        # Determine confidence
        if strength >= 0.3:
            confidence = "high"
        elif strength >= 0.15:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Generate explanation
        if direction == CausalDirection.A_CAUSES_B:
            explanation = (
                f"Changes in {indicator_a} appear to predict changes in {indicator_b}"
            )
        elif direction == CausalDirection.B_CAUSES_A:
            explanation = (
                f"Changes in {indicator_b} appear to predict changes in {indicator_a}"
            )
        elif direction == CausalDirection.BIDIRECTIONAL:
            explanation = (
                f"{indicator_a} and {indicator_b} appear to mutually influence each other"
            )
        else:
            explanation = (
                f"No clear causal relationship detected between {indicator_a} and {indicator_b}"
            )
        
        return CausalLink(
            indicator_a=indicator_a,
            indicator_b=indicator_b,
            direction=direction,
            causal_strength=strength,
            granger_statistic=max(a_predicts_b, b_predicts_a),
            p_value=0.05 if strength > threshold else 0.5,
            explanation=explanation,
            confidence=confidence,
        )
    
    def _test_predictive_power(
        self,
        predictor: List[float],
        target: List[float],
        lag_order: int,
    ) -> float:
        """
        Test how well predictor series helps predict target series.
        
        Returns improvement in prediction (R-squared improvement).
        """
        if len(predictor) != len(target) or len(predictor) < lag_order + 5:
            return 0.0
        
        # Create lagged versions
        n = len(target) - lag_order
        
        # Baseline: predict target from its own lags
        baseline_predictions = []
        for i in range(lag_order, len(target)):
            # Simple average of past values
            baseline_predictions.append(sum(target[i-lag_order:i]) / lag_order)
        
        actual = target[lag_order:]
        
        baseline_error = sum(
            (a - p) ** 2 for a, p in zip(actual, baseline_predictions)
        ) / len(actual)
        
        # With predictor: add lagged predictor
        enhanced_predictions = []
        for i in range(lag_order, len(target)):
            # Average of own lags + predictor lags
            own_avg = sum(target[i-lag_order:i]) / lag_order
            pred_avg = sum(predictor[i-lag_order:i]) / lag_order
            enhanced_predictions.append((own_avg + pred_avg) / 2)
        
        enhanced_error = sum(
            (a - p) ** 2 for a, p in zip(actual, enhanced_predictions)
        ) / len(actual)
        
        # Improvement
        if baseline_error > 0:
            improvement = (baseline_error - enhanced_error) / baseline_error
            return max(0.0, improvement)
        
        return 0.0
    
    def analyze_relationship(
        self,
        company_id: str,
        indicator_a: str,
        indicator_b: str,
    ) -> IndicatorRelationship:
        """
        Comprehensive relationship analysis between two indicators.
        
        Args:
            company_id: Company to analyze
            indicator_a: First indicator
            indicator_b: Second indicator
            
        Returns:
            IndicatorRelationship with all analysis
        """
        # Calculate correlation
        matrix = self.calculate_correlation_matrix(
            company_id, [indicator_a, indicator_b]
        )
        
        correlation_pair = None
        for pair in matrix.pairs:
            if (pair.indicator_a == indicator_a and pair.indicator_b == indicator_b) or \
               (pair.indicator_a == indicator_b and pair.indicator_b == indicator_a):
                correlation_pair = pair
                break
        
        if not correlation_pair:
            correlation_pair = CorrelationPair(
                indicator_a=indicator_a,
                indicator_b=indicator_b,
                correlation=0.0,
                correlation_type=CorrelationType.NONE,
            )
        
        # Detect lead/lag
        try:
            lead_lag = self.detect_lead_lag(company_id, indicator_a, indicator_b)
        except ValueError:
            lead_lag = None
        
        # Infer causality
        try:
            causal = self.infer_causality(company_id, indicator_a, indicator_b)
        except ValueError:
            causal = None
        
        # Determine overall strength
        abs_corr = abs(correlation_pair.correlation)
        if abs_corr >= 0.7:
            strength = "strong"
        elif abs_corr >= 0.4:
            strength = "moderate"
        elif abs_corr >= 0.2:
            strength = "weak"
        else:
            strength = "none"
        
        # Generate summary
        summary_parts = []
        
        if correlation_pair.correlation_type != CorrelationType.NONE:
            summary_parts.append(
                f"{correlation_pair.correlation_type.value} correlation ({correlation_pair.correlation:.2f})"
            )
        
        if lead_lag and lead_lag.lag_days > 0:
            summary_parts.append(
                f"{lead_lag.leading_indicator} leads by {lead_lag.lag_days} days"
            )
        
        if causal and causal.direction != CausalDirection.NO_CAUSATION:
            summary_parts.append(causal.explanation)
        
        summary = "; ".join(summary_parts) if summary_parts else "No significant relationship detected"
        
        relationship = IndicatorRelationship(
            indicator_a=indicator_a,
            indicator_b=indicator_b,
            correlation=correlation_pair,
            lead_lag=lead_lag,
            causal_link=causal,
            relationship_strength=strength,
            relationship_summary=summary,
        )
        
        key = f"{indicator_a}_{indicator_b}"
        self._relationships[key] = relationship
        
        return relationship
    
    def cluster_indicators(
        self,
        company_id: str,
        num_clusters: int = 3,
    ) -> List[IndicatorCluster]:
        """
        Cluster indicators based on correlation patterns.
        
        Args:
            company_id: Company to analyze
            num_clusters: Number of clusters to create
            
        Returns:
            List of IndicatorCluster
        """
        matrix = self.calculate_correlation_matrix(company_id)
        
        if not matrix.indicators:
            return []
        
        # Simple hierarchical clustering based on correlation distance
        indicators = matrix.indicators.copy()
        clusters: List[List[str]] = [[ind] for ind in indicators]
        
        while len(clusters) > num_clusters:
            # Find most similar pair of clusters
            best_pair = (0, 1)
            best_sim = -2.0
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    sim = self._cluster_similarity(
                        clusters[i], clusters[j], matrix
                    )
                    if sim > best_sim:
                        best_sim = sim
                        best_pair = (i, j)
            
            # Merge clusters
            i, j = best_pair
            clusters[i].extend(clusters[j])
            clusters.pop(j)
        
        # Create cluster objects
        result = []
        for idx, cluster_indicators in enumerate(clusters):
            self._cluster_counter += 1
            cluster_id = f"cluster_{self._cluster_counter}"
            
            # Calculate internal correlation
            internal_corrs = []
            for i in range(len(cluster_indicators)):
                for j in range(i + 1, len(cluster_indicators)):
                    corr = matrix.correlations.get(
                        cluster_indicators[i], {}
                    ).get(cluster_indicators[j], 0.0)
                    internal_corrs.append(corr)
            
            avg_internal = sum(internal_corrs) / len(internal_corrs) if internal_corrs else 0.0
            
            # Find centroid (most connected indicator)
            connectedness = {}
            for ind in cluster_indicators:
                total_corr = sum(
                    abs(matrix.correlations.get(ind, {}).get(other, 0.0))
                    for other in cluster_indicators
                    if other != ind
                )
                connectedness[ind] = total_corr
            
            centroid = max(connectedness.keys(), key=lambda x: connectedness[x])
            
            cluster = IndicatorCluster(
                cluster_id=cluster_id,
                name=f"Cluster {idx + 1}",
                indicators=cluster_indicators,
                average_internal_correlation=avg_internal,
                centroid_indicator=centroid,
                description=f"Cluster of {len(cluster_indicators)} related indicators",
            )
            
            self._clusters[cluster_id] = cluster
            result.append(cluster)
        
        return result
    
    def _cluster_similarity(
        self,
        cluster_a: List[str],
        cluster_b: List[str],
        matrix: CorrelationMatrix,
    ) -> float:
        """Calculate average correlation between two clusters."""
        correlations = []
        
        for ind_a in cluster_a:
            for ind_b in cluster_b:
                corr = matrix.correlations.get(ind_a, {}).get(ind_b, 0.0)
                correlations.append(corr)
        
        return sum(correlations) / len(correlations) if correlations else 0.0
    
    def get_top_correlations(
        self,
        company_id: str,
        n: int = 10,
        positive_only: bool = False,
    ) -> List[CorrelationPair]:
        """Get top N correlations for a company."""
        matrix = self.calculate_correlation_matrix(company_id)
        
        pairs = matrix.pairs
        if positive_only:
            pairs = [p for p in pairs if p.correlation > 0]
        
        # Sort by absolute correlation
        pairs.sort(key=lambda x: abs(x.correlation), reverse=True)
        
        return pairs[:n]
    
    def get_data_summary(self, company_id: str) -> Dict[str, Any]:
        """Get summary of available data for a company."""
        data = self._historical_data.get(company_id, [])
        
        if not data:
            return {"company_id": company_id, "data_points": 0}
        
        all_indicators = set()
        for _, ind_values in data:
            all_indicators.update(ind_values.keys())
        
        return {
            "company_id": company_id,
            "data_points": len(data),
            "date_range": {
                "start": data[0][0].isoformat(),
                "end": data[-1][0].isoformat(),
            },
            "indicators": list(all_indicators),
            "indicator_count": len(all_indicators),
        }
    
    def clear_data(self, company_id: Optional[str] = None) -> None:
        """Clear historical data."""
        if company_id:
            if company_id in self._historical_data:
                del self._historical_data[company_id]
        else:
            self._historical_data.clear()
