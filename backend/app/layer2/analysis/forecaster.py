"""
Simple forecaster utilities.
Provides linear extrapolation forecasting with a basic confidence interval.
Uses historical JSON data by default (same as TrendDetector).
"""
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
import json

DEFAULT_HISTORICAL = Path(__file__).resolve().parents[3] / 'data' / 'historical_indicator_values.json'


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


class Forecaster:
    def __init__(self, historical_path: Optional[Path] = None):
        self.historical_path = Path(historical_path) if historical_path else None

    def forecast_linear(self, indicator_id: int, days_ahead: int = 7, lookback: int = 30) -> Optional[List[Dict]]:
        """Simple linear forecast using last `lookback` points.

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
                'forecast_value': float(forecast_value),
                'lower_bound': float(lower),
                'upper_bound': float(upper)
            })

        return forecasts


if __name__ == '__main__':
    # Smoke test
    f = Forecaster()
    res = f.forecast_linear(1, days_ahead=7)
    print('Forecast result for indicator 1:')
    print(res)
