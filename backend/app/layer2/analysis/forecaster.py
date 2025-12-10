"""
Integrated Forecaster - Combines Developer A and Developer B approaches.

Developer A: JSON-based historical data with file loading
Developer B: DataFrame-based with Prophet placeholder
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import timedelta
import numpy as np

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

DEFAULT_HISTORICAL = Path(__file__).resolve().parents[3] / 'data' / 'historical_indicator_values.json'


def _load_historical_all(path: Optional[Path] = None) -> List[Dict]:
    """Load historical data from JSON file (Developer A)."""
    import json
    path = Path(path or DEFAULT_HISTORICAL)
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_historical_values(indicator_id: int, days: int = 30, path: Optional[Path] = None) -> List[Dict]:
    """Get historical values for an indicator (Developer A)."""
    all_data = _load_historical_all(path)
    filtered = [r for r in all_data if int(r.get('indicator_id')) == int(indicator_id)]
    filtered.sort(key=lambda x: x['timestamp'])
    return filtered[-days:]


class Forecaster:
    """
    Unified Forecaster combining both developers' approaches.
    
    - forecast_linear: Developer A's JSON-based linear regression
    - forecast: Developer B's DataFrame-based approach
    - forecast_prophet: Placeholder for advanced forecasting
    """
    
    def __init__(self, historical_path: Optional[Path] = None):
        self.historical_path = Path(historical_path) if historical_path else None

    # ===== Developer A's Method =====
    def forecast_linear(self, indicator_id: int, days_ahead: int = 7, lookback: int = 30) -> Optional[List[Dict]]:
        """
        Simple linear forecast using last `lookback` points.
        Loads from JSON historical data file.

        Returns list of dicts: days_ahead, forecast_value, lower_bound, upper_bound
        """
        values = get_historical_values(indicator_id, days=lookback, path=self.historical_path)
        if len(values) < 10:
            return None

        y = np.array([v['value'] for v in values], dtype=float)
        x = np.arange(len(y))

        # Fit linear model
        coef = np.polyfit(x, y, 1)
        slope, intercept = float(coef[0]), float(coef[1])

        # Residuals for simple std error
        fitted = slope * x + intercept
        residuals = y - fitted
        std_error = float(np.std(residuals))

        forecasts = []
        n = len(y)
        for i in range(1, days_ahead + 1):
            future_x = n + i - 1
            forecast_value = slope * future_x + intercept
            lower = forecast_value - 2 * std_error
            upper = forecast_value + 2 * std_error
            forecasts.append({
                'days_ahead': i,
                'forecast_value': float(np.clip(forecast_value, 0, 100)),
                'lower_bound': float(np.clip(lower, 0, 100)),
                'upper_bound': float(np.clip(upper, 0, 100))
            })

        return forecasts

    # ===== Developer B's Method =====
    def forecast(self, history: List[Dict[str, Any]], days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Forecast values for the next N days using DataFrame approach.
        
        Args:
            history: List of dicts with 'time' and 'value' keys.
            days_ahead: Number of days to forecast.
            
        Returns:
            List of forecasted values with 'time' and 'value'.
        """
        if not history or len(history) < 5:
            return []
        
        if not HAS_PANDAS:
            # Fallback to simple numpy-based approach
            return self._forecast_simple(history, days_ahead)
            
        # DataFrame-based approach
        df = pd.DataFrame(history)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # Use numeric representation of time for regression
        df['time_num'] = (df['time'] - df['time'].min()) / pd.Timedelta(days=1)
        
        x = df['time_num'].values
        y = df['value'].values
        
        # Fit line
        slope, intercept = np.polyfit(x, y, 1)
        
        last_time = df['time'].max()
        last_time_num = df['time_num'].max()
        
        forecasts = []
        for i in range(1, days_ahead + 1):
            future_time_num = last_time_num + i
            future_value = slope * future_time_num + intercept
            
            # Clamp value to 0-100 range
            future_value = max(0.0, min(100.0, future_value))
            
            forecasts.append({
                "time": (last_time + timedelta(days=i)).isoformat(),
                "value": float(future_value),
                "type": "forecast"
            })
            
        return forecasts
    
    def _forecast_simple(self, history: List[Dict], days_ahead: int) -> List[Dict]:
        """Simple forecast without pandas."""
        values = [h['value'] for h in history]
        x = np.arange(len(values))
        y = np.array(values)
        
        slope, intercept = np.polyfit(x, y, 1)
        
        forecasts = []
        for i in range(1, days_ahead + 1):
            future_value = slope * (len(values) + i) + intercept
            future_value = max(0.0, min(100.0, future_value))
            forecasts.append({
                "days_ahead": i,
                "value": float(future_value),
                "type": "forecast"
            })
        return forecasts
    
    def forecast_prophet(self, history: List[Dict[str, Any]], days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Placeholder for Prophet forecasting (requires prophet package).
        """
        # from prophet import Prophet
        # df = pd.DataFrame(history)
        # df.columns = ['ds', 'y']
        # m = Prophet()
        # m.fit(df)
        # future = m.make_future_dataframe(periods=days_ahead)
        # forecast = m.predict(future)
        # return forecast.tail(days_ahead).to_dict('records')
        return []  # Return empty until Prophet is set up


if __name__ == '__main__':
    # Smoke test
    f = Forecaster()
    res = f.forecast_linear(1, days_ahead=7)
    print('Forecast result for indicator 1:')
    print(res)
