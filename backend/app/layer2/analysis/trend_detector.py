"""
Trend detection utilities.
Uses historical data saved as JSON by default: `backend/data/historical_indicator_values.json`.

Provides:
- TrendDetector.calculate_moving_averages(indicator_id, periods)
- TrendDetector.detect_trend(indicator_id, window_days)

The detector avoids external DB dependencies and reads from a JSON file so it's runnable in local dev.
"""
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
from scipy import stats
import json

DEFAULT_HISTORICAL = Path(__file__).resolve().parents[3] / 'data' / 'historical_indicator_values.json'


def _load_historical_all(path: Optional[Path] = None) -> List[Dict]:
    path = Path(path or DEFAULT_HISTORICAL)
    if not path.exists():
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_historical_values(indicator_id: int, days: int = 90, path: Optional[Path] = None) -> List[Dict]:
    """Return list of records for indicator_id ordered by timestamp ascending.

    Each record: {'timestamp': ISO, 'indicator_id': int, 'value': float}
    """
    all_data = _load_historical_all(path)
    # Filter
    filtered = [r for r in all_data if int(r.get('indicator_id')) == int(indicator_id)]
    # Keep only last `days` entries (assuming daily data)
    if len(filtered) == 0:
        return []
    # If timestamps are ISO strings, assume sorted; otherwise sort
    try:
        filtered.sort(key=lambda x: x['timestamp'])
    except Exception:
        pass
    return filtered[-days:]


class TrendDetector:
    def __init__(self, historical_path: Optional[Path] = None):
        self.historical_path = Path(historical_path) if historical_path else None

    def calculate_moving_averages(self, indicator_id: int, periods: List[int] = [7, 30, 90]) -> Dict[str, float]:
        """Calculate moving averages for requested periods. Returns dict ma_{period}day -> value"""
        mas = {}
        for period in periods:
            values = get_historical_values(indicator_id, days=period, path=self.historical_path)
            if len(values) >= 1:
                arr = np.array([v['value'] for v in values[-period:]])
                mas[f'ma_{period}day'] = float(np.mean(arr))
            else:
                mas[f'ma_{period}day'] = None
        return mas

    def detect_trend(self, indicator_id: int, window_days: int = 30) -> Dict:
        """Detect trend direction and strength over last `window_days` days.

        Returns:
            {
                'direction': 'rising'|'falling'|'stable'|'unknown',
                'strength': r_squared (0-1),
                'slope': slope,
                'r_squared': r_squared,
                'rate_of_change': (last - first)/window_days
            }
        """
        values = get_historical_values(indicator_id, days=window_days, path=self.historical_path)
        if len(values) < 5:
            return {'direction': 'unknown', 'strength': 0.0, 'slope': 0.0, 'r_squared': 0.0, 'rate_of_change': 0.0}

        y = np.array([v['value'] for v in values], dtype=float)
        x = np.arange(len(y))

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r_squared = float(r_value**2)

        if slope > 0.25:
            direction = 'rising'
        elif slope < -0.25:
            direction = 'falling'
        else:
            direction = 'stable'

        rate_of_change = float((y[-1] - y[0]) / max(len(y), 1))

        return {
            'direction': direction,
            'strength': r_squared,
            'slope': float(slope),
            'r_squared': r_squared,
            'rate_of_change': rate_of_change
        }


if __name__ == '__main__':
    # Quick smoke test when run directly
    td = TrendDetector()
    # Attempt to detect trend for indicator 1
    print('Detecting trend for indicator 1...')
    res = td.detect_trend(1)
    print(res)
