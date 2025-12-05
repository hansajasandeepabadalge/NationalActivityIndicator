"""
Trend Forecasting Module.

Provides time-series analysis and forecasting including:
- Trend detection and classification
- Seasonality analysis
- Forecast generation
- Trend anomaly detection
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math


class TrendDirection(Enum):
    """Direction of trend."""
    STRONG_UP = "strong_up"
    UP = "up"
    STABLE = "stable"
    DOWN = "down"
    STRONG_DOWN = "strong_down"


class TrendType(Enum):
    """Type of trend pattern."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    CYCLICAL = "cyclical"
    SEASONAL = "seasonal"
    RANDOM_WALK = "random_walk"
    MEAN_REVERTING = "mean_reverting"


class SeasonalPeriod(Enum):
    """Common seasonal periods."""
    WEEKLY = 7
    MONTHLY = 30
    QUARTERLY = 90
    YEARLY = 365


@dataclass
class Trend:
    """Detected trend in time series."""
    trend_id: str
    indicator: str
    company_id: str
    
    # Trend characteristics
    direction: TrendDirection
    trend_type: TrendType
    
    # Trend parameters
    slope: float = 0.0  # Rate of change per day
    intercept: float = 0.0
    r_squared: float = 0.0  # Goodness of fit
    
    # Significance
    is_significant: bool = True
    confidence: float = 0.0
    p_value: float = 0.0
    
    # Time period
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    data_points: int = 0
    
    # Additional info
    acceleration: float = 0.0  # Change in slope
    volatility: float = 0.0
    

@dataclass
class SeasonalPattern:
    """Detected seasonal pattern."""
    pattern_id: str
    indicator: str
    company_id: str
    
    # Pattern characteristics
    period: SeasonalPeriod
    period_days: int
    
    # Seasonal factors (day/week/month index -> factor)
    seasonal_factors: Dict[int, float] = field(default_factory=dict)
    
    # Pattern strength
    strength: float = 0.0  # 0-1
    explained_variance: float = 0.0
    
    # Peak and trough
    peak_index: int = 0
    trough_index: int = 0
    peak_factor: float = 1.0
    trough_factor: float = 1.0


@dataclass
class ForecastPoint:
    """Single forecast point."""
    date: datetime
    predicted_value: float
    
    # Confidence interval
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    confidence_level: float = 0.95
    
    # Components
    trend_component: float = 0.0
    seasonal_component: float = 0.0
    residual: float = 0.0


@dataclass
class Forecast:
    """Complete forecast for an indicator."""
    forecast_id: str
    indicator: str
    company_id: str
    generated_at: datetime
    
    # Forecast parameters
    horizon_days: int
    method: str = "ensemble"
    
    # Historical context
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)
    
    # Forecast values
    forecasted_values: List[ForecastPoint] = field(default_factory=list)
    
    # Trend and seasonality
    underlying_trend: Optional[Trend] = None
    seasonal_pattern: Optional[SeasonalPattern] = None
    
    # Accuracy metrics (from backtesting)
    mape: float = 0.0  # Mean Absolute Percentage Error
    rmse: float = 0.0  # Root Mean Squared Error
    
    # Summary
    expected_change: float = 0.0  # Expected change over horizon
    change_direction: str = "stable"


@dataclass
class TrendAnomaly:
    """Detected trend anomaly."""
    anomaly_id: str
    indicator: str
    company_id: str
    detected_at: datetime
    
    # Anomaly details
    anomaly_type: str  # "breakpoint", "outlier", "acceleration", "reversal"
    severity: str  # "low", "medium", "high"
    
    # Values
    expected_value: float
    actual_value: float
    deviation: float
    
    # Context
    previous_trend: Optional[TrendDirection] = None
    new_trend: Optional[TrendDirection] = None
    
    explanation: str = ""


class TrendForecaster:
    """
    Trend forecasting engine for time series analysis.
    
    Provides trend detection, seasonality analysis,
    and forecast generation.
    """
    
    def __init__(self):
        """Initialize the trend forecaster."""
        self._historical_data: Dict[str, Dict[str, List[Tuple[datetime, float]]]] = {}
        self._trends: Dict[str, Trend] = {}
        self._forecasts: Dict[str, Forecast] = {}
        self._seasonal_patterns: Dict[str, SeasonalPattern] = {}
        self._anomalies: List[TrendAnomaly] = []
        
        self._trend_counter = 0
        self._forecast_counter = 0
        self._pattern_counter = 0
        self._anomaly_counter = 0
    
    def add_data_point(
        self,
        company_id: str,
        indicator: str,
        timestamp: datetime,
        value: float,
    ) -> None:
        """Add a single data point."""
        if company_id not in self._historical_data:
            self._historical_data[company_id] = {}
        
        if indicator not in self._historical_data[company_id]:
            self._historical_data[company_id][indicator] = []
        
        self._historical_data[company_id][indicator].append((timestamp, value))
        
        # Sort by timestamp
        self._historical_data[company_id][indicator].sort(key=lambda x: x[0])
    
    def add_historical_data(
        self,
        company_id: str,
        indicator: str,
        data: List[Tuple[datetime, float]],
    ) -> None:
        """Add batch historical data."""
        for timestamp, value in data:
            self.add_data_point(company_id, indicator, timestamp, value)
    
    def detect_trend(
        self,
        company_id: str,
        indicator: str,
        lookback_days: Optional[int] = None,
    ) -> Trend:
        """
        Detect trend in indicator time series.
        
        Args:
            company_id: Company to analyze
            indicator: Indicator to analyze
            lookback_days: Days to look back (all if None)
            
        Returns:
            Detected Trend
        """
        data = self._get_indicator_data(company_id, indicator)
        if len(data) < 5:
            raise ValueError(f"Insufficient data for trend detection")
        
        # Filter by lookback
        if lookback_days:
            cutoff = datetime.now() - timedelta(days=lookback_days)
            data = [(t, v) for t, v in data if t > cutoff]
        
        if len(data) < 5:
            raise ValueError("Insufficient data after filtering")
        
        self._trend_counter += 1
        trend_id = f"trend_{self._trend_counter}"
        
        # Extract values
        timestamps = [(d[0] - data[0][0]).days for d in data]
        values = [d[1] for d in data]
        
        # Linear regression
        slope, intercept, r_squared = self._linear_regression(timestamps, values)
        
        # Determine direction
        direction = self._classify_direction(slope, values)
        
        # Determine trend type
        trend_type = self._classify_trend_type(timestamps, values, slope)
        
        # Calculate volatility
        volatility = self._calculate_volatility(values)
        
        # Calculate acceleration (change in slope)
        acceleration = self._calculate_acceleration(timestamps, values)
        
        # Confidence based on R-squared and data points
        confidence = min(0.95, r_squared * 0.7 + len(data) / 100 * 0.3)
        
        trend = Trend(
            trend_id=trend_id,
            indicator=indicator,
            company_id=company_id,
            direction=direction,
            trend_type=trend_type,
            slope=slope,
            intercept=intercept,
            r_squared=r_squared,
            is_significant=abs(slope) > 0.001 and r_squared > 0.1,
            confidence=confidence,
            period_start=data[0][0],
            period_end=data[-1][0],
            data_points=len(data),
            acceleration=acceleration,
            volatility=volatility,
        )
        
        self._trends[trend_id] = trend
        return trend
    
    def _get_indicator_data(
        self,
        company_id: str,
        indicator: str,
    ) -> List[Tuple[datetime, float]]:
        """Get time series data for an indicator."""
        if company_id not in self._historical_data:
            return []
        return self._historical_data[company_id].get(indicator, [])
    
    def _linear_regression(
        self,
        x: List[float],
        y: List[float],
    ) -> Tuple[float, float, float]:
        """Calculate linear regression parameters."""
        n = len(x)
        if n < 2:
            return 0.0, 0.0, 0.0
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Calculate slope and intercept
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = sum((xi - mean_x) ** 2 for xi in x)
        
        if denominator == 0:
            return 0.0, mean_y, 0.0
        
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x
        
        # Calculate R-squared
        predictions = [slope * xi + intercept for xi in x]
        ss_res = sum((yi - pi) ** 2 for yi, pi in zip(y, predictions))
        ss_tot = sum((yi - mean_y) ** 2 for yi in y)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        r_squared = max(0.0, r_squared)
        
        return slope, intercept, r_squared
    
    def _classify_direction(
        self,
        slope: float,
        values: List[float],
    ) -> TrendDirection:
        """Classify trend direction."""
        mean_value = sum(values) / len(values) if values else 1.0
        if mean_value == 0:
            mean_value = 1.0
        
        # Normalize slope by mean value
        normalized_slope = slope / abs(mean_value)
        
        if normalized_slope > 0.02:
            return TrendDirection.STRONG_UP
        elif normalized_slope > 0.005:
            return TrendDirection.UP
        elif normalized_slope < -0.02:
            return TrendDirection.STRONG_DOWN
        elif normalized_slope < -0.005:
            return TrendDirection.DOWN
        else:
            return TrendDirection.STABLE
    
    def _classify_trend_type(
        self,
        timestamps: List[float],
        values: List[float],
        linear_slope: float,
    ) -> TrendType:
        """Classify the type of trend."""
        if len(values) < 10:
            return TrendType.LINEAR
        
        # Check for mean reversion
        mean = sum(values) / len(values)
        crossings = sum(
            1 for i in range(1, len(values))
            if (values[i-1] - mean) * (values[i] - mean) < 0
        )
        
        if crossings > len(values) * 0.3:
            return TrendType.MEAN_REVERTING
        
        # Check for exponential trend
        if all(v > 0 for v in values):
            log_values = [math.log(v) for v in values]
            _, _, r_squared_log = self._linear_regression(timestamps, log_values)
            _, _, r_squared_linear = self._linear_regression(timestamps, values)
            
            if r_squared_log > r_squared_linear + 0.1:
                return TrendType.EXPONENTIAL
        
        # Check for cyclical pattern
        volatility = self._calculate_volatility(values)
        if volatility > 0.1 and abs(linear_slope) < 0.001:
            return TrendType.CYCLICAL
        
        return TrendType.LINEAR
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (normalized standard deviation)."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)
        
        # Normalize by mean
        if mean != 0:
            return std_dev / abs(mean)
        return std_dev
    
    def _calculate_acceleration(
        self,
        timestamps: List[float],
        values: List[float],
    ) -> float:
        """Calculate acceleration (change in slope over time)."""
        if len(values) < 10:
            return 0.0
        
        mid = len(values) // 2
        
        # First half slope
        slope1, _, _ = self._linear_regression(
            timestamps[:mid], values[:mid]
        )
        
        # Second half slope
        slope2, _, _ = self._linear_regression(
            timestamps[mid:], values[mid:]
        )
        
        return slope2 - slope1
    
    def detect_seasonality(
        self,
        company_id: str,
        indicator: str,
        period: SeasonalPeriod = SeasonalPeriod.WEEKLY,
    ) -> SeasonalPattern:
        """
        Detect seasonal pattern in indicator.
        
        Args:
            company_id: Company to analyze
            indicator: Indicator to analyze
            period: Seasonal period to test
            
        Returns:
            Detected SeasonalPattern
        """
        data = self._get_indicator_data(company_id, indicator)
        if len(data) < period.value * 2:
            raise ValueError(
                f"Need at least {period.value * 2} data points for seasonality"
            )
        
        self._pattern_counter += 1
        pattern_id = f"pattern_{self._pattern_counter}"
        
        period_days = period.value
        
        # Group values by position in period
        period_values: Dict[int, List[float]] = {}
        
        for timestamp, value in data:
            if period == SeasonalPeriod.WEEKLY:
                idx = timestamp.weekday()
            elif period == SeasonalPeriod.MONTHLY:
                idx = timestamp.day - 1
            elif period == SeasonalPeriod.QUARTERLY:
                idx = (timestamp.timetuple().tm_yday - 1) % 90
            else:  # YEARLY
                idx = timestamp.timetuple().tm_yday - 1
            
            if idx not in period_values:
                period_values[idx] = []
            period_values[idx].append(value)
        
        # Calculate average for each position
        overall_mean = sum(v for d, v in data) / len(data)
        
        seasonal_factors: Dict[int, float] = {}
        for idx, values in period_values.items():
            period_mean = sum(values) / len(values)
            if overall_mean != 0:
                seasonal_factors[idx] = period_mean / overall_mean
            else:
                seasonal_factors[idx] = 1.0
        
        # Calculate strength of seasonality
        factor_variance = sum(
            (f - 1.0) ** 2 for f in seasonal_factors.values()
        ) / len(seasonal_factors)
        strength = min(1.0, math.sqrt(factor_variance) * 5)
        
        # Find peak and trough
        if seasonal_factors:
            peak_idx = max(seasonal_factors.keys(), key=lambda x: seasonal_factors[x])
            trough_idx = min(seasonal_factors.keys(), key=lambda x: seasonal_factors[x])
        else:
            peak_idx = trough_idx = 0
        
        pattern = SeasonalPattern(
            pattern_id=pattern_id,
            indicator=indicator,
            company_id=company_id,
            period=period,
            period_days=period_days,
            seasonal_factors=seasonal_factors,
            strength=strength,
            explained_variance=strength ** 2,
            peak_index=peak_idx,
            trough_index=trough_idx,
            peak_factor=seasonal_factors.get(peak_idx, 1.0),
            trough_factor=seasonal_factors.get(trough_idx, 1.0),
        )
        
        self._seasonal_patterns[pattern_id] = pattern
        return pattern
    
    def generate_forecast(
        self,
        company_id: str,
        indicator: str,
        horizon_days: int = 30,
        include_seasonality: bool = True,
        confidence_level: float = 0.95,
    ) -> Forecast:
        """
        Generate forecast for an indicator.
        
        Args:
            company_id: Company to forecast for
            indicator: Indicator to forecast
            horizon_days: Number of days to forecast
            include_seasonality: Whether to include seasonal adjustment
            confidence_level: Confidence level for intervals
            
        Returns:
            Forecast with predicted values
        """
        data = self._get_indicator_data(company_id, indicator)
        if len(data) < 10:
            raise ValueError("Need at least 10 data points for forecasting")
        
        self._forecast_counter += 1
        forecast_id = f"forecast_{self._forecast_counter}"
        
        # Detect underlying trend
        trend = self.detect_trend(company_id, indicator)
        
        # Detect seasonality if requested
        seasonal_pattern = None
        if include_seasonality and len(data) >= 14:
            try:
                seasonal_pattern = self.detect_seasonality(
                    company_id, indicator, SeasonalPeriod.WEEKLY
                )
            except ValueError:
                pass
        
        # Generate forecasts
        last_date = data[-1][0]
        last_value = data[-1][1]
        values = [d[1] for d in data]
        
        # Calculate historical error for confidence intervals
        historical_error = self._calculate_volatility(values[-30:] if len(values) > 30 else values)
        
        forecasted_values: List[ForecastPoint] = []
        
        for day in range(1, horizon_days + 1):
            forecast_date = last_date + timedelta(days=day)
            
            # Trend component
            trend_value = trend.intercept + trend.slope * (
                (forecast_date - data[0][0]).days
            )
            
            # Seasonal component
            seasonal_factor = 1.0
            if seasonal_pattern and seasonal_pattern.strength > 0.1:
                if seasonal_pattern.period == SeasonalPeriod.WEEKLY:
                    idx = forecast_date.weekday()
                else:
                    idx = forecast_date.day - 1
                seasonal_factor = seasonal_pattern.seasonal_factors.get(idx, 1.0)
            
            predicted_value = trend_value * seasonal_factor
            
            # Confidence interval (widens with horizon)
            z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
            interval_width = historical_error * z_score * math.sqrt(day)
            
            forecasted_values.append(
                ForecastPoint(
                    date=forecast_date,
                    predicted_value=predicted_value,
                    lower_bound=predicted_value - interval_width * predicted_value,
                    upper_bound=predicted_value + interval_width * predicted_value,
                    confidence_level=confidence_level,
                    trend_component=trend_value,
                    seasonal_component=seasonal_factor - 1.0,
                )
            )
        
        # Calculate expected change
        if forecasted_values:
            expected_change = (
                forecasted_values[-1].predicted_value - last_value
            ) / last_value if last_value != 0 else 0.0
            
            if expected_change > 0.05:
                change_direction = "increasing"
            elif expected_change < -0.05:
                change_direction = "decreasing"
            else:
                change_direction = "stable"
        else:
            expected_change = 0.0
            change_direction = "stable"
        
        # Backtest for accuracy estimation
        mape, rmse = self._backtest_forecast(data, trend)
        
        forecast = Forecast(
            forecast_id=forecast_id,
            indicator=indicator,
            company_id=company_id,
            generated_at=datetime.now(),
            horizon_days=horizon_days,
            method="trend_seasonal" if seasonal_pattern else "trend",
            historical_values=data[-30:],  # Last 30 points
            forecasted_values=forecasted_values,
            underlying_trend=trend,
            seasonal_pattern=seasonal_pattern,
            mape=mape,
            rmse=rmse,
            expected_change=expected_change,
            change_direction=change_direction,
        )
        
        self._forecasts[forecast_id] = forecast
        return forecast
    
    def _backtest_forecast(
        self,
        data: List[Tuple[datetime, float]],
        trend: Trend,
        test_size: int = 10,
    ) -> Tuple[float, float]:
        """Backtest forecast accuracy."""
        if len(data) < test_size + 10:
            return 0.1, 0.1  # Default errors
        
        train_data = data[:-test_size]
        test_data = data[-test_size:]
        
        # Get last training date
        last_train_date = train_data[-1][0]
        
        errors = []
        squared_errors = []
        
        for test_date, actual in test_data:
            days_ahead = (test_date - data[0][0]).days
            predicted = trend.intercept + trend.slope * days_ahead
            
            error = abs(actual - predicted) / actual if actual != 0 else 0
            errors.append(error)
            squared_errors.append((actual - predicted) ** 2)
        
        mape = sum(errors) / len(errors) if errors else 0.0
        rmse = math.sqrt(sum(squared_errors) / len(squared_errors)) if squared_errors else 0.0
        
        return mape, rmse
    
    def detect_anomalies(
        self,
        company_id: str,
        indicator: str,
        sensitivity: float = 2.0,
    ) -> List[TrendAnomaly]:
        """
        Detect anomalies in trend behavior.
        
        Args:
            company_id: Company to analyze
            indicator: Indicator to analyze
            sensitivity: Standard deviations for anomaly threshold
            
        Returns:
            List of detected TrendAnomaly
        """
        data = self._get_indicator_data(company_id, indicator)
        if len(data) < 20:
            return []
        
        anomalies: List[TrendAnomaly] = []
        
        values = [d[1] for d in data]
        mean = sum(values) / len(values)
        std_dev = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
        
        threshold = sensitivity * std_dev
        
        for i, (timestamp, value) in enumerate(data):
            deviation = abs(value - mean)
            
            if deviation > threshold:
                self._anomaly_counter += 1
                
                # Determine type
                if i > 0 and i < len(data) - 1:
                    prev_value = data[i-1][1]
                    next_value = data[i+1][1]
                    
                    if abs(value - prev_value) > threshold and abs(next_value - prev_value) < std_dev:
                        anomaly_type = "outlier"
                    else:
                        anomaly_type = "level_shift"
                else:
                    anomaly_type = "outlier"
                
                # Determine severity
                if deviation > 3 * std_dev:
                    severity = "high"
                elif deviation > 2 * std_dev:
                    severity = "medium"
                else:
                    severity = "low"
                
                anomalies.append(
                    TrendAnomaly(
                        anomaly_id=f"anomaly_{self._anomaly_counter}",
                        indicator=indicator,
                        company_id=company_id,
                        detected_at=timestamp,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        expected_value=mean,
                        actual_value=value,
                        deviation=deviation / std_dev,  # In standard deviations
                        explanation=f"{anomaly_type.title()} detected: value is {deviation/std_dev:.1f} standard deviations from mean",
                    )
                )
        
        self._anomalies.extend(anomalies)
        return anomalies
    
    def detect_trend_changes(
        self,
        company_id: str,
        indicator: str,
        window_size: int = 14,
    ) -> List[TrendAnomaly]:
        """
        Detect changes in trend direction.
        
        Args:
            company_id: Company to analyze
            indicator: Indicator to analyze
            window_size: Window size for trend detection
            
        Returns:
            List of trend change anomalies
        """
        data = self._get_indicator_data(company_id, indicator)
        if len(data) < window_size * 3:
            return []
        
        anomalies: List[TrendAnomaly] = []
        
        values = [d[1] for d in data]
        timestamps = [d[0] for d in data]
        
        prev_direction = None
        
        for i in range(window_size, len(data) - window_size):
            # Calculate local trend
            local_x = list(range(window_size))
            local_y = values[i - window_size // 2:i + window_size // 2]
            
            if len(local_y) < window_size:
                continue
            
            slope, _, _ = self._linear_regression(local_x, local_y)
            direction = self._classify_direction(slope, local_y)
            
            if prev_direction is not None and direction != prev_direction:
                # Check if it's a significant change
                if self._is_significant_direction_change(prev_direction, direction):
                    self._anomaly_counter += 1
                    
                    anomalies.append(
                        TrendAnomaly(
                            anomaly_id=f"anomaly_{self._anomaly_counter}",
                            indicator=indicator,
                            company_id=company_id,
                            detected_at=timestamps[i],
                            anomaly_type="reversal",
                            severity="medium",
                            expected_value=values[i-1],
                            actual_value=values[i],
                            deviation=abs(slope) * 100,
                            previous_trend=prev_direction,
                            new_trend=direction,
                            explanation=f"Trend reversal from {prev_direction.value} to {direction.value}",
                        )
                    )
            
            prev_direction = direction
        
        self._anomalies.extend(anomalies)
        return anomalies
    
    def _is_significant_direction_change(
        self,
        prev: TrendDirection,
        current: TrendDirection,
    ) -> bool:
        """Check if direction change is significant."""
        up_directions = {TrendDirection.UP, TrendDirection.STRONG_UP}
        down_directions = {TrendDirection.DOWN, TrendDirection.STRONG_DOWN}
        
        return (prev in up_directions and current in down_directions) or \
               (prev in down_directions and current in up_directions)
    
    def compare_trends(
        self,
        company_id: str,
        indicators: List[str],
    ) -> Dict[str, Any]:
        """Compare trends across multiple indicators."""
        comparison = {
            "indicators": {},
            "correlations": {},
            "divergences": [],
        }
        
        trends = {}
        for indicator in indicators:
            try:
                trend = self.detect_trend(company_id, indicator)
                trends[indicator] = trend
                comparison["indicators"][indicator] = {
                    "direction": trend.direction.value,
                    "slope": trend.slope,
                    "r_squared": trend.r_squared,
                    "significant": trend.is_significant,
                }
            except ValueError:
                continue
        
        # Find divergences
        for i, ind1 in enumerate(indicators):
            for ind2 in indicators[i+1:]:
                if ind1 in trends and ind2 in trends:
                    dir1 = trends[ind1].direction
                    dir2 = trends[ind2].direction
                    
                    up = {TrendDirection.UP, TrendDirection.STRONG_UP}
                    down = {TrendDirection.DOWN, TrendDirection.STRONG_DOWN}
                    
                    if (dir1 in up and dir2 in down) or (dir1 in down and dir2 in up):
                        comparison["divergences"].append({
                            "indicator_1": ind1,
                            "indicator_2": ind2,
                            "direction_1": dir1.value,
                            "direction_2": dir2.value,
                        })
        
        return comparison
    
    def get_forecast(self, forecast_id: str) -> Optional[Forecast]:
        """Get a forecast by ID."""
        return self._forecasts.get(forecast_id)
    
    def get_trend(self, trend_id: str) -> Optional[Trend]:
        """Get a trend by ID."""
        return self._trends.get(trend_id)
    
    def get_data_summary(self, company_id: str) -> Dict[str, Any]:
        """Get summary of available data."""
        if company_id not in self._historical_data:
            return {"company_id": company_id, "indicators": {}}
        
        indicators = {}
        for ind, data in self._historical_data[company_id].items():
            if data:
                indicators[ind] = {
                    "data_points": len(data),
                    "start_date": data[0][0].isoformat(),
                    "end_date": data[-1][0].isoformat(),
                    "min_value": min(d[1] for d in data),
                    "max_value": max(d[1] for d in data),
                }
        
        return {
            "company_id": company_id,
            "indicators": indicators,
            "total_indicators": len(indicators),
        }
    
    def clear_data(self, company_id: Optional[str] = None) -> None:
        """Clear historical data."""
        if company_id:
            if company_id in self._historical_data:
                del self._historical_data[company_id]
        else:
            self._historical_data.clear()
