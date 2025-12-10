"""
Run trend detection and forecasting for all indicators and save results to JSON.
Writes to `backend/data/indicator_trends.json` by default.

Usage:
    python backend/scripts/calculate_all_trends_and_forecasts.py --out backend/data/indicator_trends.json
"""
import json
import argparse
from pathlib import Path
from app.layer2.analysis.trend_detector import TrendDetector
from app.layer2.analysis.forecaster import Forecaster

DEFAULT_OUT = Path(__file__).resolve().parents[1] / 'data' / 'indicator_trends.json'


def run_all(indicator_ids=None, out_path: Path = DEFAULT_OUT, lookback: int = 30, forecast_days: int = 7):
    indicator_ids = indicator_ids or list(range(1, 25))

    td = TrendDetector()
    fc = Forecaster()

    results = []

    for iid in indicator_ids:
        trend = td.detect_trend(iid, window_days=lookback)
        mas = td.calculate_moving_averages(iid, periods=[7, 30, 90])
        forecast = fc.forecast_linear(iid, days_ahead=forecast_days, lookback=lookback)

        results.append({
            'indicator_id': iid,
            'trend': trend,
            'moving_averages': mas,
            'forecast': forecast
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"Saved trends and forecasts for {len(results)} indicators to {out_path}")
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, default=str(DEFAULT_OUT))
    parser.add_argument('--lookback', type=int, default=30)
    parser.add_argument('--forecast_days', type=int, default=7)
    args = parser.parse_args()

    run_all(out_path=Path(args.out), lookback=args.lookback, forecast_days=args.forecast_days)
