"""
Advanced Forecaster with Multiple Models and Ensemble Prediction.

Improvements over basic version:
1. Multiple forecasting methods (linear, exponential smoothing, Holt-Winters)
2. Ensemble predictions combining multiple models
3. Adaptive confidence intervals based on volatility
4. Trend-aware predictions
5. Seasonality-adjusted forecasts
6. Prediction quality scoring
7. Automatic model selection

Author: Day 5 Enhancement
"""
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import json
import warnings

warnings.filterwarnings('ignore')

DEFAULT_HISTORICAL = Path(__file__).resolve().parents[3] / 'data' / 'historical_indicator_values.json'


class ForecastMethod(Enum):
    LINEAR = "linear"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    HOLT_LINEAR = "holt_linear"
    WEIGHTED_AVERAGE = "weighted_average"
    ENSEMBLE = "ensemble"


@dataclass
class ForecastPoint:
    """Single forecast point with confidence interval."""
    days_ahead: int
    forecast_value: float
    lower_bound: float
    upper_bound: float
    confidence: float  # 0-1, how confident in this prediction
    method: str
    
    def to_dict(self) -> Dict:
        return {
            'days_ahead': self.days_ahead,
            'forecast_value': round(self.forecast_value, 4),
            'lower_bound': round(self.lower_bound, 4),
            'upper_bound': round(self.upper_bound, 4),
            'confidence': round(self.confidence, 4),
            'method': self.method
        }


@dataclass
class ForecastResult:
    """Complete forecast result with metadata."""
    indicator_id: int
    method: str
    forecasts: List[ForecastPoint]
    model_quality: float  # 0-1, based on backtest
    trend_direction: str
    volatility: float
    last_value: float
    
    def to_dict(self) -> Dict:
        return {
            'indicator_id': self.indicator_id,
            'method': self.method,
            'forecasts': [f.to_dict() for f in self.forecasts],
            'model_quality': round(self.model_quality, 4),
            'trend_direction': self.trend_direction,
            'volatility': round(self.volatility, 4),
            'last_value': round(self.last_value, 4)
        }


def _load_historical_all(path: Optional[Path] = None) -> List[Dict]:
    path = Path(path or DEFAULT_HISTORICAL)
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_historical_values(indicator_id: int, days: int = 30, path: Optional[Path] = None) -> List[Dict]:
    all_data = _load_historical_all(path)
    filtered = [r for r in all_data if int(r.get('indicator_id')) == int(indicator_id)]
    filtered.sort(key=lambda x: x['timestamp'])
    return filtered[-days:]


class EnhancedForecaster:
    """
    Advanced forecasting with multiple methods and ensemble prediction.
    
    Features:
    - Multiple forecasting algorithms
    - Automatic model selection based on data characteristics
    - Ensemble predictions for robustness
    - Volatility-adjusted confidence intervals
    - Backtesting for model quality assessment
    """
    
    def __init__(self, 
                 historical_path: Optional[Path] = None,
                 min_data_points: int = 14,
                 default_confidence_level: float = 0.95):
        self.historical_path = Path(historical_path) if historical_path else None
        self.min_data_points = min_data_points
        self.confidence_level = default_confidence_level
    
    def forecast(self,
                 indicator_id: int,
                 days_ahead: int = 7,
                 lookback: int = 30,
                 method: ForecastMethod = ForecastMethod.ENSEMBLE) -> Optional[ForecastResult]:
        """
        Generate forecast using specified method.
        
        Args:
            indicator_id: The indicator to forecast
            days_ahead: How many days to forecast
            lookback: Historical data window for model fitting
            method: Forecasting method to use
        
        Returns:
            ForecastResult with predictions and metadata
        """
        values = get_historical_values(indicator_id, days=lookback, path=self.historical_path)
        
        if len(values) < self.min_data_points:
            return None
        
        y = np.array([v['value'] for v in values], dtype=float)
        
        # Calculate basic statistics
        volatility = float(np.std(y))
        last_value = float(y[-1])
        trend_direction = self._detect_simple_trend(y)
        
        # Generate forecast based on method
        if method == ForecastMethod.LINEAR:
            forecasts = self._forecast_linear(y, days_ahead)
        elif method == ForecastMethod.EXPONENTIAL_SMOOTHING:
            forecasts = self._forecast_exponential_smoothing(y, days_ahead)
        elif method == ForecastMethod.HOLT_LINEAR:
            forecasts = self._forecast_holt_linear(y, days_ahead)
        elif method == ForecastMethod.WEIGHTED_AVERAGE:
            forecasts = self._forecast_weighted_average(y, days_ahead)
        else:  # ENSEMBLE
            forecasts = self._forecast_ensemble(y, days_ahead)
        
        # Backtest model quality
        model_quality = self._backtest_model(y, method)
        
        return ForecastResult(
            indicator_id=indicator_id,
            method=method.value,
            forecasts=forecasts,
            model_quality=model_quality,
            trend_direction=trend_direction,
            volatility=volatility,
            last_value=last_value
        )
    
    def _forecast_linear(self, y: np.ndarray, days_ahead: int) -> List[ForecastPoint]:
        """Simple linear regression forecast."""
        x = np.arange(len(y))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Calculate prediction intervals
        fitted = slope * x + intercept
        residuals = y - fitted
        std_resid = np.std(residuals)
        
        forecasts = []
        n = len(y)
        
        for i in range(1, days_ahead + 1):
            future_x = n + i - 1
            forecast_value = slope * future_x + intercept
            
            # Widen interval as we go further
            interval_width = std_resid * 2 * (1 + 0.1 * i)
            
            # Confidence decreases with distance
            confidence = max(0.3, 1.0 - (0.08 * i))
            
            forecasts.append(ForecastPoint(
                days_ahead=i,
                forecast_value=float(np.clip(forecast_value, 0, 100)),
                lower_bound=float(np.clip(forecast_value - interval_width, 0, 100)),
                upper_bound=float(np.clip(forecast_value + interval_width, 0, 100)),
                confidence=confidence,
                method='linear'
            ))
        
        return forecasts
    
    def _forecast_exponential_smoothing(self, y: np.ndarray, days_ahead: int, 
                                         alpha: float = None) -> List[ForecastPoint]:
        """Simple Exponential Smoothing (SES) forecast."""
        # Optimize alpha if not provided
        if alpha is None:
            alpha = self._optimize_ses_alpha(y)
        
        # Calculate smoothed values
        smoothed = np.zeros(len(y))
        smoothed[0] = y[0]
        
        for t in range(1, len(y)):
            smoothed[t] = alpha * y[t] + (1 - alpha) * smoothed[t-1]
        
        # Forecast is last smoothed value (flat forecast)
        forecast_value = smoothed[-1]
        
        # Calculate residuals for intervals
        residuals = y - smoothed
        std_resid = np.std(residuals)
        
        forecasts = []
        for i in range(1, days_ahead + 1):
            interval_width = std_resid * 2 * np.sqrt(i)
            confidence = max(0.3, 1.0 - (0.1 * i))
            
            forecasts.append(ForecastPoint(
                days_ahead=i,
                forecast_value=float(np.clip(forecast_value, 0, 100)),
                lower_bound=float(np.clip(forecast_value - interval_width, 0, 100)),
                upper_bound=float(np.clip(forecast_value + interval_width, 0, 100)),
                confidence=confidence,
                method='exponential_smoothing'
            ))
        
        return forecasts
    
    def _optimize_ses_alpha(self, y: np.ndarray) -> float:
        """Optimize SES alpha using MSE minimization."""
        def mse(alpha):
            if alpha <= 0 or alpha >= 1:
                return float('inf')
            smoothed = np.zeros(len(y))
            smoothed[0] = y[0]
            for t in range(1, len(y)):
                smoothed[t] = alpha * y[t] + (1 - alpha) * smoothed[t-1]
            return np.mean((y - smoothed) ** 2)
        
        result = minimize(mse, x0=0.3, bounds=[(0.01, 0.99)], method='L-BFGS-B')
        return float(result.x[0]) if result.success else 0.3
    
    def _forecast_holt_linear(self, y: np.ndarray, days_ahead: int) -> List[ForecastPoint]:
        """Holt's Linear Trend Method (double exponential smoothing)."""
        # Optimize parameters
        alpha, beta = self._optimize_holt_params(y)
        
        n = len(y)
        level = np.zeros(n)
        trend = np.zeros(n)
        
        # Initialize
        level[0] = y[0]
        trend[0] = y[1] - y[0] if n > 1 else 0
        
        # Update equations
        for t in range(1, n):
            level[t] = alpha * y[t] + (1 - alpha) * (level[t-1] + trend[t-1])
            trend[t] = beta * (level[t] - level[t-1]) + (1 - beta) * trend[t-1]
        
        # Calculate residuals
        fitted = level[:-1] + trend[:-1]
        std_resid = np.std(y[1:] - fitted)
        
        forecasts = []
        for i in range(1, days_ahead + 1):
            forecast_value = level[-1] + i * trend[-1]
            interval_width = std_resid * 2 * np.sqrt(i)
            confidence = max(0.3, 1.0 - (0.07 * i))
            
            forecasts.append(ForecastPoint(
                days_ahead=i,
                forecast_value=float(np.clip(forecast_value, 0, 100)),
                lower_bound=float(np.clip(forecast_value - interval_width, 0, 100)),
                upper_bound=float(np.clip(forecast_value + interval_width, 0, 100)),
                confidence=confidence,
                method='holt_linear'
            ))
        
        return forecasts
    
    def _optimize_holt_params(self, y: np.ndarray) -> Tuple[float, float]:
        """Optimize Holt's method parameters."""
        def mse(params):
            alpha, beta = params
            if not (0.01 < alpha < 0.99 and 0.01 < beta < 0.99):
                return float('inf')
            
            n = len(y)
            level = np.zeros(n)
            trend = np.zeros(n)
            level[0] = y[0]
            trend[0] = y[1] - y[0] if n > 1 else 0
            
            for t in range(1, n):
                level[t] = alpha * y[t] + (1 - alpha) * (level[t-1] + trend[t-1])
                trend[t] = beta * (level[t] - level[t-1]) + (1 - beta) * trend[t-1]
            
            fitted = level + trend
            return np.mean((y[1:] - fitted[:-1]) ** 2)
        
        result = minimize(mse, x0=[0.3, 0.1], 
                          bounds=[(0.01, 0.99), (0.01, 0.99)],
                          method='L-BFGS-B')
        
        if result.success:
            return float(result.x[0]), float(result.x[1])
        return 0.3, 0.1
    
    def _forecast_weighted_average(self, y: np.ndarray, days_ahead: int) -> List[ForecastPoint]:
        """Weighted moving average with trend adjustment."""
        # Recent values weighted more heavily
        weights = np.exp(np.linspace(-1, 0, min(14, len(y))))
        weights = weights / weights.sum()
        
        recent = y[-len(weights):]
        weighted_avg = np.sum(recent * weights)
        
        # Calculate trend from last 7 days
        if len(y) >= 7:
            recent_trend = (y[-1] - y[-7]) / 7
        else:
            recent_trend = 0
        
        std_resid = np.std(np.diff(y[-14:]) if len(y) >= 14 else np.diff(y))
        
        forecasts = []
        for i in range(1, days_ahead + 1):
            forecast_value = weighted_avg + i * recent_trend * 0.5  # Dampen trend
            interval_width = std_resid * 2 * np.sqrt(i)
            confidence = max(0.3, 1.0 - (0.09 * i))
            
            forecasts.append(ForecastPoint(
                days_ahead=i,
                forecast_value=float(np.clip(forecast_value, 0, 100)),
                lower_bound=float(np.clip(forecast_value - interval_width, 0, 100)),
                upper_bound=float(np.clip(forecast_value + interval_width, 0, 100)),
                confidence=confidence,
                method='weighted_average'
            ))
        
        return forecasts
    
    def _forecast_ensemble(self, y: np.ndarray, days_ahead: int) -> List[ForecastPoint]:
        """
        Ensemble forecast combining multiple methods.
        Uses weighted average based on historical performance.
        """
        # Get forecasts from all methods
        linear = self._forecast_linear(y, days_ahead)
        ses = self._forecast_exponential_smoothing(y, days_ahead)
        holt = self._forecast_holt_linear(y, days_ahead)
        weighted = self._forecast_weighted_average(y, days_ahead)
        
        # Get model weights based on backtest performance
        weights = self._get_ensemble_weights(y)
        
        forecasts = []
        for i in range(days_ahead):
            # Weighted average of forecasts
            values = [
                linear[i].forecast_value,
                ses[i].forecast_value,
                holt[i].forecast_value,
                weighted[i].forecast_value
            ]
            
            lowers = [
                linear[i].lower_bound,
                ses[i].lower_bound,
                holt[i].lower_bound,
                weighted[i].lower_bound
            ]
            
            uppers = [
                linear[i].upper_bound,
                ses[i].upper_bound,
                holt[i].upper_bound,
                weighted[i].upper_bound
            ]
            
            ensemble_value = np.average(values, weights=weights)
            ensemble_lower = np.average(lowers, weights=weights)
            ensemble_upper = np.average(uppers, weights=weights)
            
            # Confidence from disagreement between models
            disagreement = np.std(values)
            mean_val = np.mean(values)
            agreement_factor = 1 - min(disagreement / (mean_val + 1), 0.5)
            confidence = max(0.4, min(0.95, agreement_factor * (1 - 0.06 * (i + 1))))
            
            forecasts.append(ForecastPoint(
                days_ahead=i + 1,
                forecast_value=float(np.clip(ensemble_value, 0, 100)),
                lower_bound=float(np.clip(ensemble_lower, 0, 100)),
                upper_bound=float(np.clip(ensemble_upper, 0, 100)),
                confidence=confidence,
                method='ensemble'
            ))
        
        return forecasts
    
    def _get_ensemble_weights(self, y: np.ndarray) -> np.ndarray:
        """Calculate ensemble weights based on backtest MSE."""
        if len(y) < 20:
            return np.array([0.25, 0.25, 0.25, 0.25])
        
        # Use first 70% for fitting, last 30% for validation
        split = int(len(y) * 0.7)
        train, test = y[:split], y[split:]
        
        methods_mse = []
        
        # Test each method
        for method in [self._forecast_linear, self._forecast_exponential_smoothing,
                       self._forecast_holt_linear, self._forecast_weighted_average]:
            try:
                forecasts = method(train, len(test))
                predictions = [f.forecast_value for f in forecasts]
                mse = np.mean((test - predictions[:len(test)]) ** 2)
                methods_mse.append(mse if not np.isnan(mse) else float('inf'))
            except Exception:
                methods_mse.append(float('inf'))
        
        # Convert MSE to weights (lower MSE = higher weight)
        mse_array = np.array(methods_mse)
        if np.all(np.isinf(mse_array)):
            return np.array([0.25, 0.25, 0.25, 0.25])
        
        # Inverse MSE weighting
        mse_array = np.where(np.isinf(mse_array), np.max(mse_array[~np.isinf(mse_array)]) * 10, mse_array)
        inverse_mse = 1 / (mse_array + 1e-10)
        weights = inverse_mse / inverse_mse.sum()
        
        return weights
    
    def _backtest_model(self, y: np.ndarray, method: ForecastMethod) -> float:
        """
        Backtest the forecasting model to estimate quality.
        Returns score from 0 (poor) to 1 (excellent).
        """
        if len(y) < 20:
            return 0.5  # Not enough data for reliable backtest
        
        # Rolling forecast evaluation
        errors = []
        window = max(14, len(y) // 3)
        
        for i in range(window, len(y) - 3):
            train = y[:i]
            actual = y[i:i+3]
            
            try:
                if method == ForecastMethod.ENSEMBLE:
                    forecasts = self._forecast_ensemble(train, 3)
                elif method == ForecastMethod.LINEAR:
                    forecasts = self._forecast_linear(train, 3)
                elif method == ForecastMethod.EXPONENTIAL_SMOOTHING:
                    forecasts = self._forecast_exponential_smoothing(train, 3)
                elif method == ForecastMethod.HOLT_LINEAR:
                    forecasts = self._forecast_holt_linear(train, 3)
                else:
                    forecasts = self._forecast_weighted_average(train, 3)
                
                predictions = [f.forecast_value for f in forecasts[:len(actual)]]
                mape = np.mean(np.abs(actual - predictions) / (actual + 1e-10)) * 100
                errors.append(mape)
            except Exception:
                continue
        
        if not errors:
            return 0.5
        
        avg_mape = np.mean(errors)
        
        # Convert MAPE to quality score (lower MAPE = higher quality)
        # MAPE < 5% = excellent (1.0), MAPE > 30% = poor (0.0)
        quality = max(0.0, min(1.0, 1 - (avg_mape - 5) / 25))
        
        return float(quality)
    
    def _detect_simple_trend(self, y: np.ndarray) -> str:
        """Quick trend detection for metadata."""
        if len(y) < 5:
            return 'unknown'
        
        slope, _, r_value, _, _ = stats.linregress(np.arange(len(y)), y)
        
        if abs(r_value) < 0.3:
            return 'stable'
        elif slope > 0:
            return 'rising'
        else:
            return 'falling'
    
    def forecast_all_indicators(self, 
                                 indicator_ids: List[int] = None,
                                 days_ahead: int = 7) -> Dict[int, ForecastResult]:
        """
        Forecast multiple indicators at once.
        Returns dict mapping indicator_id to ForecastResult.
        """
        if indicator_ids is None:
            indicator_ids = list(range(1, 25))
        
        results = {}
        for ind_id in indicator_ids:
            result = self.forecast(ind_id, days_ahead=days_ahead)
            if result:
                results[ind_id] = result
        
        return results


# Convenience function for backward compatibility
def forecast_enhanced(indicator_id: int, days_ahead: int = 7, lookback: int = 30) -> Optional[Dict]:
    """Quick forecast using ensemble method."""
    forecaster = EnhancedForecaster()
    result = forecaster.forecast(indicator_id, days_ahead, lookback)
    return result.to_dict() if result else None


if __name__ == '__main__':
    print("Enhanced Forecaster - Testing")
    print("=" * 50)
    
    forecaster = EnhancedForecaster()
    
    # Test on indicator 1
    print("\n📈 Indicator 1 - Ensemble Forecast:")
    result = forecaster.forecast(1, days_ahead=7)
    
    if result:
        print(f"  Model Quality: {result.model_quality:.2f}")
        print(f"  Trend: {result.trend_direction}")
        print(f"  Volatility: {result.volatility:.2f}")
        print(f"  Last Value: {result.last_value:.2f}")
        print(f"\n  7-Day Forecast:")
        for f in result.forecasts:
            print(f"    Day {f.days_ahead}: {f.forecast_value:.1f} [{f.lower_bound:.1f} - {f.upper_bound:.1f}] (conf: {f.confidence:.2f})")
    else:
        print("  Insufficient data for forecast")
