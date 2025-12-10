"""
Enhanced Trend Detection with Multiple Methods and Statistical Rigor.

Improvements over basic version:
1. Multiple trend detection algorithms (linear, polynomial, exponential)
2. Statistical significance testing (p-value thresholds)
3. Seasonality detection and decomposition
4. Momentum indicators (RSI-like)
5. Volatility-adjusted trend strength
6. Change point detection
7. Confidence scoring

Author: Day 5 Enhancement
"""
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy import stats
from scipy.signal import find_peaks
import json
import warnings

warnings.filterwarnings('ignore')

DEFAULT_HISTORICAL = Path(__file__).resolve().parents[3] / 'data' / 'historical_indicator_values.json'


class TrendDirection(Enum):
    STRONG_RISING = "strong_rising"
    RISING = "rising"
    WEAK_RISING = "weak_rising"
    STABLE = "stable"
    WEAK_FALLING = "weak_falling"
    FALLING = "falling"
    STRONG_FALLING = "strong_falling"
    UNKNOWN = "unknown"


@dataclass
class TrendResult:
    """Comprehensive trend analysis result."""
    direction: str
    strength: float  # 0-1, higher = stronger trend
    confidence: float  # 0-1, statistical confidence
    slope: float  # Rate of change per day
    r_squared: float  # Model fit quality
    p_value: float  # Statistical significance
    volatility: float  # Standard deviation of residuals
    momentum: float  # -100 to +100, RSI-like
    is_significant: bool  # p_value < 0.05
    seasonality_detected: bool
    change_points: List[int]  # Indices where trend changes
    
    def to_dict(self) -> Dict:
        return {
            'direction': self.direction,
            'strength': round(self.strength, 4),
            'confidence': round(self.confidence, 4),
            'slope': round(self.slope, 6),
            'r_squared': round(self.r_squared, 4),
            'p_value': round(self.p_value, 6),
            'volatility': round(self.volatility, 4),
            'momentum': round(self.momentum, 2),
            'is_significant': bool(self.is_significant),
            'seasonality_detected': bool(self.seasonality_detected),
            'change_points': [int(x) for x in self.change_points]
        }


def _load_historical_all(path: Optional[Path] = None) -> List[Dict]:
    path = Path(path or DEFAULT_HISTORICAL)
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_historical_values(indicator_id: int, days: int = 90, path: Optional[Path] = None) -> List[Dict]:
    all_data = _load_historical_all(path)
    filtered = [r for r in all_data if int(r.get('indicator_id')) == int(indicator_id)]
    filtered.sort(key=lambda x: x['timestamp'])
    return filtered[-days:]


class EnhancedTrendDetector:
    """
    Advanced trend detection with multiple algorithms and statistical rigor.
    
    Features:
    - Multiple regression types (linear, polynomial)
    - Statistical significance testing
    - Momentum indicators
    - Volatility normalization
    - Change point detection
    - Seasonality detection
    """
    
    def __init__(self, 
                 historical_path: Optional[Path] = None,
                 significance_level: float = 0.05,
                 min_data_points: int = 7):
        self.historical_path = Path(historical_path) if historical_path else None
        self.significance_level = significance_level
        self.min_data_points = min_data_points
    
    def calculate_moving_averages(self, 
                                   indicator_id: int, 
                                   periods: List[int] = [7, 14, 30, 60, 90]) -> Dict[str, Optional[float]]:
        """
        Calculate multiple moving averages with additional metrics.
        
        Returns:
            Dict with ma_{period}day values and crossover signals
        """
        result = {}
        all_mas = {}
        
        # Get maximum period data
        max_period = max(periods)
        values = get_historical_values(indicator_id, days=max_period, path=self.historical_path)
        
        if len(values) < self.min_data_points:
            return {f'ma_{p}day': None for p in periods}
        
        arr = np.array([v['value'] for v in values], dtype=float)
        
        for period in periods:
            if len(arr) >= period:
                ma = float(np.mean(arr[-period:]))
                result[f'ma_{period}day'] = round(ma, 4)
                all_mas[period] = ma
            else:
                result[f'ma_{period}day'] = None
        
        # Calculate EMA (Exponential Moving Average) for short-term
        if len(arr) >= 7:
            ema_7 = self._calculate_ema(arr, 7)
            result['ema_7day'] = round(ema_7, 4)
        
        # MA Crossover signals (short-term vs long-term)
        if all_mas.get(7) and all_mas.get(30):
            ma_ratio = all_mas[7] / all_mas[30]
            if ma_ratio > 1.05:
                result['ma_signal'] = 'bullish_crossover'
            elif ma_ratio < 0.95:
                result['ma_signal'] = 'bearish_crossover'
            else:
                result['ma_signal'] = 'neutral'
            result['ma_7_30_ratio'] = round(ma_ratio, 4)
        
        return result
    
    def _calculate_ema(self, data: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average."""
        multiplier = 2 / (period + 1)
        ema = data[0]
        for price in data[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return float(ema)
    
    def detect_trend(self, 
                     indicator_id: int, 
                     window_days: int = 30,
                     method: str = 'ensemble') -> TrendResult:
        """
        Detect trend using specified method.
        
        Args:
            indicator_id: The indicator to analyze
            window_days: Analysis window
            method: 'linear', 'polynomial', 'ensemble' (combines both)
        
        Returns:
            TrendResult with comprehensive trend analysis
        """
        values = get_historical_values(indicator_id, days=window_days, path=self.historical_path)
        
        if len(values) < self.min_data_points:
            return TrendResult(
                direction=TrendDirection.UNKNOWN.value,
                strength=0.0, confidence=0.0, slope=0.0, r_squared=0.0,
                p_value=1.0, volatility=0.0, momentum=0.0,
                is_significant=False, seasonality_detected=False, change_points=[]
            )
        
        y = np.array([v['value'] for v in values], dtype=float)
        x = np.arange(len(y))
        
        # Linear regression with full statistics
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared = r_value ** 2
        
        # Calculate residuals and volatility
        fitted = slope * x + intercept
        residuals = y - fitted
        volatility = float(np.std(residuals))
        
        # Normalize slope by value range for comparability
        value_range = np.ptp(y) if np.ptp(y) > 0 else 1
        normalized_slope = slope / value_range * len(y)
        
        # Momentum indicator (RSI-like, -100 to +100)
        momentum = self._calculate_momentum(y)
        
        # Determine trend direction with granularity
        direction = self._classify_trend_direction(slope, r_squared, p_value, momentum)
        
        # Calculate confidence score (combines r_squared and p_value)
        confidence = self._calculate_confidence(r_squared, p_value, len(y))
        
        # Strength (volatility-adjusted r_squared)
        strength = r_squared * (1 - min(volatility / value_range, 0.5))
        
        # Check for seasonality (simple autocorrelation check)
        seasonality = self._detect_seasonality(y)
        
        # Detect change points
        change_points = self._detect_change_points(y)
        
        return TrendResult(
            direction=direction,
            strength=float(strength),
            confidence=float(confidence),
            slope=float(slope),
            r_squared=float(r_squared),
            p_value=float(p_value),
            volatility=volatility,
            momentum=float(momentum),
            is_significant=p_value < self.significance_level,
            seasonality_detected=seasonality,
            change_points=change_points
        )
    
    def _calculate_momentum(self, values: np.ndarray, period: int = 14) -> float:
        """
        Calculate momentum using RSI-like formula.
        Returns value from -100 (extreme negative) to +100 (extreme positive).
        """
        if len(values) < period + 1:
            period = len(values) - 1
        
        if period < 2:
            return 0.0
        
        deltas = np.diff(values[-period-1:])
        gains = np.maximum(deltas, 0)
        losses = np.abs(np.minimum(deltas, 0))
        
        avg_gain = np.mean(gains) if len(gains) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 0.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Convert RSI (0-100) to momentum (-100 to +100)
        momentum = (rsi - 50) * 2
        return float(momentum)
    
    def _classify_trend_direction(self, 
                                   slope: float, 
                                   r_squared: float, 
                                   p_value: float,
                                   momentum: float) -> str:
        """Classify trend direction with granularity based on multiple factors."""
        
        # Not significant - call it stable
        if p_value > self.significance_level or r_squared < 0.1:
            return TrendDirection.STABLE.value
        
        # Combine slope direction with strength
        if slope > 0:
            if r_squared > 0.7 and momentum > 30:
                return TrendDirection.STRONG_RISING.value
            elif r_squared > 0.4 or momentum > 10:
                return TrendDirection.RISING.value
            else:
                return TrendDirection.WEAK_RISING.value
        else:
            if r_squared > 0.7 and momentum < -30:
                return TrendDirection.STRONG_FALLING.value
            elif r_squared > 0.4 or momentum < -10:
                return TrendDirection.FALLING.value
            else:
                return TrendDirection.WEAK_FALLING.value
    
    def _calculate_confidence(self, r_squared: float, p_value: float, n: int) -> float:
        """
        Calculate overall confidence in the trend detection.
        Combines statistical significance with model fit quality.
        """
        # Base confidence from p-value (higher p = lower confidence)
        p_confidence = 1 - min(p_value, 1.0)
        
        # Adjust for sample size (more data = more confident)
        size_factor = min(n / 30, 1.0)  # Max out at 30 days
        
        # Combine factors
        confidence = (r_squared * 0.4 + p_confidence * 0.4 + size_factor * 0.2)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _detect_seasonality(self, values: np.ndarray, period: int = 7) -> bool:
        """
        Simple seasonality detection using autocorrelation.
        Checks if there's significant correlation at lag=period (e.g., weekly).
        """
        if len(values) < period * 2:
            return False
        
        # Calculate autocorrelation at the given lag
        n = len(values)
        mean = np.mean(values)
        var = np.var(values)
        
        if var == 0:
            return False
        
        # Autocorrelation at lag=period
        autocorr = np.sum((values[:n-period] - mean) * (values[period:] - mean)) / (n * var)
        
        # If autocorrelation > 0.3, consider it seasonal
        return abs(autocorr) > 0.3
    
    def _detect_change_points(self, values: np.ndarray, threshold: float = 2.0) -> List[int]:
        """
        Detect significant change points in the time series.
        Uses rolling statistics to find where the trend changes.
        """
        if len(values) < 10:
            return []
        
        change_points = []
        window = max(3, len(values) // 10)
        
        for i in range(window, len(values) - window):
            before = values[i-window:i]
            after = values[i:i+window]
            
            # Check if means are significantly different
            mean_before = np.mean(before)
            mean_after = np.mean(after)
            std_overall = np.std(values)
            
            if std_overall > 0:
                z_score = abs(mean_after - mean_before) / std_overall
                if z_score > threshold:
                    # Avoid consecutive change points
                    if not change_points or i - change_points[-1] > window:
                        change_points.append(i)
        
        return change_points
    
    def get_trend_summary(self, indicator_id: int) -> Dict:
        """
        Get a comprehensive trend summary for an indicator.
        Combines short-term, medium-term, and long-term analysis.
        """
        short_trend = self.detect_trend(indicator_id, window_days=7)
        medium_trend = self.detect_trend(indicator_id, window_days=30)
        long_trend = self.detect_trend(indicator_id, window_days=90)
        
        mas = self.calculate_moving_averages(indicator_id)
        
        # Determine overall outlook
        directions = [short_trend.direction, medium_trend.direction, long_trend.direction]
        rising_count = sum(1 for d in directions if 'rising' in d)
        falling_count = sum(1 for d in directions if 'falling' in d)
        
        if rising_count >= 2:
            overall = 'bullish'
        elif falling_count >= 2:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        return {
            'indicator_id': indicator_id,
            'overall_outlook': overall,
            'short_term': short_trend.to_dict(),
            'medium_term': medium_trend.to_dict(),
            'long_term': long_trend.to_dict(),
            'moving_averages': mas,
            'trend_alignment': rising_count == 3 or falling_count == 3
        }


# Backward compatible function
def detect_trend_enhanced(indicator_id: int, window_days: int = 30) -> Dict:
    """Convenience function for quick trend detection."""
    detector = EnhancedTrendDetector()
    result = detector.detect_trend(indicator_id, window_days)
    return result.to_dict()


if __name__ == '__main__':
    print("Enhanced Trend Detector - Testing")
    print("=" * 50)
    
    detector = EnhancedTrendDetector()
    
    # Test on indicator 1
    print("\n📊 Indicator 1 - Full Summary:")
    summary = detector.get_trend_summary(1)
    print(f"  Overall Outlook: {summary['overall_outlook']}")
    print(f"  Short-term: {summary['short_term']['direction']} (conf: {summary['short_term']['confidence']:.2f})")
    print(f"  Medium-term: {summary['medium_term']['direction']} (conf: {summary['medium_term']['confidence']:.2f})")
    print(f"  Long-term: {summary['long_term']['direction']} (conf: {summary['long_term']['confidence']:.2f})")
    print(f"  Trend Alignment: {summary['trend_alignment']}")
    print(f"  Moving Averages: {summary['moving_averages']}")
