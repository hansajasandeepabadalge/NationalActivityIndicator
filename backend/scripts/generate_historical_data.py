"""
Generate realistic historical indicator values and save to JSON.
Writes to `backend/data/historical_indicator_values.json` by default.
Optional: attempt to insert into a database if configured (safe fallback to JSON file).

Usage:
    python backend/scripts/generate_historical_data.py --days 90 --out backend/data/historical_indicator_values.json

This script is intentionally self-contained and avoids assuming DB access.
"""
import json
import argparse
from datetime import datetime, timedelta, timezone
import numpy as np
from pathlib import Path
import random

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "historical_indicator_values.json"

INDICATOR_IDS = list(range(1, 25))  # 24 indicators by default


def generate_historical_indicator_values(indicator_id: int, days: int = 90):
    """Generate realistic time-series data for a single indicator.

    Returns a list of dicts with fields: timestamp (ISO), indicator_id, value (0-100)
    """
    patterns = ['rising', 'falling', 'stable', 'volatile']
    pattern = random.choice(patterns)

    values = []
    base_value = 50 + random.uniform(-10, 10)  # baseline per indicator

    for day in range(days):
        timestamp = datetime.now(timezone.utc) - timedelta(days=(days - day))

        if pattern == 'rising':
            trend = day * (random.uniform(0.1, 0.5))
            noise = np.random.normal(0, 2)
            value = base_value + trend + noise
        elif pattern == 'falling':
            trend = -day * (random.uniform(0.1, 0.5))
            noise = np.random.normal(0, 2)
            value = base_value + trend + noise
        elif pattern == 'volatile':
            value = base_value + np.random.normal(0, 8)
        else:  # stable
            value = base_value + np.random.normal(0, 2)

        # Clip to valid range
        value = float(np.clip(value, 0, 100))

        values.append({
            'timestamp': timestamp.isoformat() + 'Z',
            'indicator_id': int(indicator_id),
            'value': value
        })

    return values


def generate_all(indicator_ids=INDICATOR_IDS, days=90):
    output = []
    for iid in indicator_ids:
        output.extend(generate_historical_indicator_values(iid, days=days))
    # Sort by indicator then timestamp
    output.sort(key=lambda x: (x['indicator_id'], x['timestamp']))
    return output


def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} records to {path}")


def main():
    parser = argparse.ArgumentParser(description='Generate historical indicator values')
    parser.add_argument('--days', type=int, default=90, help='Number of days to generate per indicator')
    parser.add_argument('--out', type=str, default=str(DEFAULT_OUTPUT), help='Output JSON file path')
    args = parser.parse_args()

    data = generate_all(days=args.days)
    save_json(data, Path(args.out))


if __name__ == '__main__':
    main()
