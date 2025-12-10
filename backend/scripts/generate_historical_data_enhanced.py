"""
Enhanced Historical Data Generator with Realistic Patterns.

Improvements over basic version:
1. Realistic temporal patterns (seasonality, weekly cycles)
2. Indicator correlations (related indicators move together)
3. Event-based spikes (simulate real-world events)
4. Economic cycle simulation
5. Trend persistence (trends don't randomly change)
6. Noise calibrated to real-world data
7. Domain-specific patterns per indicator type

Author: Day 5 Enhancement
"""
import json
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import numpy as np

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "historical_indicator_values.json"


class IndicatorCategory(Enum):
    POLITICAL = "political"
    ECONOMIC = "economic"
    SOCIAL = "social"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    LEGAL = "legal"


class TrendType(Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    CYCLICAL = "cyclical"
    VOLATILE = "volatile"
    RECOVERING = "recovering"  # Was falling, now rising
    DECLINING = "declining"   # Was rising, now falling


@dataclass
class IndicatorConfig:
    """Configuration for each indicator's data generation."""
    indicator_id: int
    name: str
    category: IndicatorCategory
    base_value: float  # Typical center value (0-100)
    volatility: float  # How much it fluctuates (std dev)
    trend_type: TrendType
    trend_strength: float  # How strong the trend is
    weekly_seasonality: float  # Weekend effect (-1 to 1)
    correlated_with: List[int]  # IDs of correlated indicators
    correlation_strength: float  # How strongly correlated
    event_sensitivity: float  # How sensitive to events (0-1)


# Define realistic indicator configurations
INDICATOR_CONFIGS = {
    # Political (IDs 1-5)
    1: IndicatorConfig(1, "Cabinet Changes Frequency", IndicatorCategory.POLITICAL,
                       30, 8, TrendType.VOLATILE, 0.1, 0.0, [], 0.0, 0.9),
    2: IndicatorConfig(2, "Protest Frequency Index", IndicatorCategory.POLITICAL,
                       45, 12, TrendType.CYCLICAL, 0.3, 0.2, [3, 5], 0.6, 0.95),
    3: IndicatorConfig(3, "Strike Activity Score", IndicatorCategory.POLITICAL,
                       35, 10, TrendType.STABLE, 0.1, 0.3, [2, 15], 0.7, 0.85),
    4: IndicatorConfig(4, "Public Dissatisfaction Index", IndicatorCategory.POLITICAL,
                       50, 8, TrendType.RISING, 0.2, 0.1, [5, 10], 0.5, 0.7),
    5: IndicatorConfig(5, "Governance Risk Score", IndicatorCategory.POLITICAL,
                       40, 6, TrendType.STABLE, 0.05, 0.0, [1, 4], 0.4, 0.6),
    
    # Economic (IDs 6-13)
    6: IndicatorConfig(6, "Consumer Confidence Proxy", IndicatorCategory.ECONOMIC,
                       55, 7, TrendType.CYCLICAL, 0.15, 0.1, [7, 11], 0.6, 0.5),
    7: IndicatorConfig(7, "Inflation Pressure Index", IndicatorCategory.ECONOMIC,
                       60, 5, TrendType.RISING, 0.25, 0.0, [6, 8], -0.4, 0.4),
    8: IndicatorConfig(8, "Currency Stability Indicator", IndicatorCategory.ECONOMIC,
                       50, 8, TrendType.FALLING, 0.2, 0.0, [7], -0.5, 0.6),
    9: IndicatorConfig(9, "Business Activity Index", IndicatorCategory.ECONOMIC,
                       52, 6, TrendType.RECOVERING, 0.15, 0.15, [6, 11], 0.5, 0.45),
    10: IndicatorConfig(10, "Supply Chain Health", IndicatorCategory.ECONOMIC,
                        48, 10, TrendType.STABLE, 0.1, 0.05, [3, 15], 0.4, 0.7),
    11: IndicatorConfig(11, "Tourism Activity Index", IndicatorCategory.ECONOMIC,
                        45, 15, TrendType.RECOVERING, 0.3, 0.3, [6, 9], 0.5, 0.8),
    12: IndicatorConfig(12, "Stock Market Sentiment", IndicatorCategory.ECONOMIC,
                        50, 12, TrendType.VOLATILE, 0.2, 0.1, [6, 8], 0.6, 0.9),
    13: IndicatorConfig(13, "Export Performance Index", IndicatorCategory.ECONOMIC,
                        42, 8, TrendType.DECLINING, 0.15, 0.1, [8, 10], 0.5, 0.5),
    
    # Social (IDs 14-17)
    14: IndicatorConfig(14, "Overall Public Sentiment", IndicatorCategory.SOCIAL,
                        48, 6, TrendType.STABLE, 0.1, 0.1, [4, 6], 0.7, 0.6),
    15: IndicatorConfig(15, "Cost of Living Burden", IndicatorCategory.SOCIAL,
                        65, 5, TrendType.RISING, 0.2, 0.0, [7], 0.5, 0.3),
    16: IndicatorConfig(16, "Healthcare Access Index", IndicatorCategory.SOCIAL,
                        55, 4, TrendType.STABLE, 0.05, 0.1, [], 0.0, 0.4),
    17: IndicatorConfig(17, "Education Disruption Level", IndicatorCategory.SOCIAL,
                        30, 8, TrendType.FALLING, 0.15, 0.2, [3], 0.3, 0.6),
    
    # Technological (IDs 18-19)
    18: IndicatorConfig(18, "Internet Connectivity Status", IndicatorCategory.TECHNOLOGICAL,
                        75, 5, TrendType.RISING, 0.1, 0.0, [], 0.0, 0.3),
    19: IndicatorConfig(19, "Power Infrastructure Health", IndicatorCategory.TECHNOLOGICAL,
                        60, 8, TrendType.STABLE, 0.05, 0.1, [], 0.0, 0.7),
    
    # Environmental (IDs 20-22)
    20: IndicatorConfig(20, "Weather Severity Index", IndicatorCategory.ENVIRONMENTAL,
                        40, 15, TrendType.CYCLICAL, 0.3, 0.0, [21, 22], 0.7, 0.95),
    21: IndicatorConfig(21, "Flood Risk Level", IndicatorCategory.ENVIRONMENTAL,
                        35, 20, TrendType.CYCLICAL, 0.4, 0.0, [20], 0.8, 0.9),
    22: IndicatorConfig(22, "Drought Concern Index", IndicatorCategory.ENVIRONMENTAL,
                        30, 12, TrendType.STABLE, 0.1, 0.0, [20], 0.5, 0.7),
    
    # Legal (IDs 23-24)
    23: IndicatorConfig(23, "New Laws Frequency", IndicatorCategory.LEGAL,
                        25, 6, TrendType.STABLE, 0.05, 0.2, [], 0.0, 0.2),
    24: IndicatorConfig(24, "Regulatory Change Rate", IndicatorCategory.LEGAL,
                        30, 5, TrendType.RISING, 0.1, 0.15, [23], 0.4, 0.3),
}


class RealisticDataGenerator:
    """
    Generate realistic historical indicator data with:
    - Temporal patterns
    - Inter-indicator correlations
    - Event-based anomalies
    - Domain-specific behaviors
    """
    
    def __init__(self, seed: int = None):
        if seed is not None:
            np.random.seed(seed)
        
        self.configs = INDICATOR_CONFIGS
        self.generated_data: Dict[int, np.ndarray] = {}
        self.events: List[Dict] = []
    
    def generate_events(self, days: int) -> List[Dict]:
        """Generate random events that affect multiple indicators."""
        events = []
        
        # Economic crisis event (affects economy, politics)
        if np.random.random() < 0.3:
            start_day = np.random.randint(days // 4, days // 2)
            events.append({
                'type': 'economic_crisis',
                'start_day': start_day,
                'duration': np.random.randint(7, 21),
                'intensity': np.random.uniform(0.3, 0.7),
                'affected_categories': [IndicatorCategory.ECONOMIC, IndicatorCategory.POLITICAL, IndicatorCategory.SOCIAL]
            })
        
        # Political unrest event
        if np.random.random() < 0.4:
            start_day = np.random.randint(0, days - 14)
            events.append({
                'type': 'political_unrest',
                'start_day': start_day,
                'duration': np.random.randint(3, 10),
                'intensity': np.random.uniform(0.4, 0.8),
                'affected_categories': [IndicatorCategory.POLITICAL]
            })
        
        # Weather event (monsoon, flood)
        if np.random.random() < 0.5:
            start_day = np.random.randint(days // 3, 2 * days // 3)
            events.append({
                'type': 'weather_event',
                'start_day': start_day,
                'duration': np.random.randint(5, 15),
                'intensity': np.random.uniform(0.5, 0.9),
                'affected_categories': [IndicatorCategory.ENVIRONMENTAL]
            })
        
        self.events = events
        return events
    
    def _apply_trend(self, base: float, day: int, days: int, config: IndicatorConfig) -> float:
        """Apply trend based on trend type."""
        progress = day / days  # 0 to 1
        trend_effect = 0
        
        if config.trend_type == TrendType.RISING:
            trend_effect = config.trend_strength * progress * 30
        elif config.trend_type == TrendType.FALLING:
            trend_effect = -config.trend_strength * progress * 30
        elif config.trend_type == TrendType.CYCLICAL:
            # Sine wave with period of ~30 days
            cycle = np.sin(2 * np.pi * day / 30)
            trend_effect = config.trend_strength * cycle * 15
        elif config.trend_type == TrendType.RECOVERING:
            # V-shape: falling then rising
            if progress < 0.4:
                trend_effect = -config.trend_strength * (progress / 0.4) * 20
            else:
                trend_effect = config.trend_strength * ((progress - 0.4) / 0.6) * 25 - 20
        elif config.trend_type == TrendType.DECLINING:
            # Inverted V: rising then falling
            if progress < 0.5:
                trend_effect = config.trend_strength * (progress / 0.5) * 15
            else:
                trend_effect = 15 - config.trend_strength * ((progress - 0.5) / 0.5) * 20
        
        return base + trend_effect
    
    def _apply_weekly_seasonality(self, value: float, day: int, config: IndicatorConfig) -> float:
        """Apply weekly seasonality (weekend effect)."""
        if config.weekly_seasonality == 0:
            return value
        
        # Day of week (0 = Monday, 6 = Sunday)
        dow = day % 7
        
        # Weekend effect
        if dow >= 5:  # Weekend
            return value * (1 - config.weekly_seasonality * 0.1)
        else:
            return value
    
    def _apply_event_effects(self, value: float, day: int, config: IndicatorConfig) -> float:
        """Apply effects of events."""
        for event in self.events:
            if event['start_day'] <= day <= event['start_day'] + event['duration']:
                if config.category in event['affected_categories']:
                    # Calculate event intensity based on distance from peak
                    event_progress = (day - event['start_day']) / event['duration']
                    # Peak intensity in the middle
                    intensity_curve = np.sin(np.pi * event_progress)
                    
                    effect = event['intensity'] * intensity_curve * config.event_sensitivity
                    
                    # Events generally push indicators higher (crisis = more activity)
                    if event['type'] == 'economic_crisis':
                        if config.category == IndicatorCategory.ECONOMIC:
                            value *= (1 - effect * 0.3)  # Economic indicators drop
                        else:
                            value *= (1 + effect * 0.2)  # Others rise (unrest, etc.)
                    elif event['type'] == 'political_unrest':
                        value *= (1 + effect * 0.4)  # Political indicators spike
                    elif event['type'] == 'weather_event':
                        value *= (1 + effect * 0.5)  # Weather indicators spike
        
        return value
    
    def _apply_correlations(self, values_today: Dict[int, float], config: IndicatorConfig) -> float:
        """Apply correlation effects from related indicators."""
        if not config.correlated_with or config.correlation_strength == 0:
            return 0
        
        correlation_effect = 0
        for corr_id in config.correlated_with:
            if corr_id in values_today:
                corr_config = self.configs.get(corr_id)
                if corr_config:
                    # How much the correlated indicator deviates from its base
                    corr_deviation = (values_today[corr_id] - corr_config.base_value) / 100
                    correlation_effect += corr_deviation * config.correlation_strength * 10
        
        return correlation_effect / max(len(config.correlated_with), 1)
    
    def generate_indicator_series(self, 
                                   indicator_id: int, 
                                   days: int,
                                   existing_data: Dict[int, np.ndarray] = None) -> np.ndarray:
        """Generate time series for a single indicator."""
        config = self.configs.get(indicator_id)
        if not config:
            # Fallback for unknown indicators
            config = IndicatorConfig(
                indicator_id, f"Indicator {indicator_id}", 
                IndicatorCategory.ECONOMIC, 50, 8, TrendType.STABLE,
                0.1, 0.0, [], 0.0, 0.5
            )
        
        values = np.zeros(days)
        
        for day in range(days):
            # Start with base value
            value = config.base_value
            
            # Apply trend
            value = self._apply_trend(value, day, days, config)
            
            # Apply weekly seasonality
            value = self._apply_weekly_seasonality(value, day, config)
            
            # Apply random noise (calibrated to volatility)
            noise = np.random.normal(0, config.volatility)
            value += noise
            
            # Apply event effects
            value = self._apply_event_effects(value, day, config)
            
            # Apply correlation effects (if we have other indicators' data)
            if existing_data and day > 0:
                values_today = {iid: data[day-1] for iid, data in existing_data.items() if day-1 < len(data)}
                correlation_effect = self._apply_correlations(values_today, config)
                value += correlation_effect
            
            # Momentum: today's value influenced by yesterday's
            if day > 0:
                momentum = (values[day-1] - config.base_value) * 0.3
                value += momentum
            
            # Clip to valid range
            values[day] = float(np.clip(value, 0, 100))
        
        return values
    
    def generate_all(self, days: int = 90) -> List[Dict]:
        """Generate data for all indicators with correlations."""
        # First, generate events
        self.generate_events(days)
        
        # Generate in order (so correlations can reference earlier indicators)
        indicator_ids = sorted(self.configs.keys())
        
        # First pass: generate base data
        for ind_id in indicator_ids:
            self.generated_data[ind_id] = self.generate_indicator_series(
                ind_id, days, self.generated_data
            )
        
        # Second pass: apply correlations more accurately
        for ind_id in indicator_ids:
            config = self.configs.get(ind_id)
            if config and config.correlated_with:
                for day in range(1, days):
                    values_today = {iid: self.generated_data[iid][day-1] 
                                    for iid in config.correlated_with 
                                    if iid in self.generated_data}
                    if values_today:
                        corr_effect = self._apply_correlations(values_today, config) * 0.5
                        self.generated_data[ind_id][day] = float(
                            np.clip(self.generated_data[ind_id][day] + corr_effect, 0, 100)
                        )
        
        # Convert to output format
        output = []
        base_time = datetime.now(timezone.utc)
        
        for ind_id in indicator_ids:
            for day in range(days):
                timestamp = base_time - timedelta(days=(days - day - 1))
                output.append({
                    'timestamp': timestamp.isoformat().replace('+00:00', 'Z'),
                    'indicator_id': ind_id,
                    'value': round(self.generated_data[ind_id][day], 4)
                })
        
        # Sort by indicator then timestamp
        output.sort(key=lambda x: (x['indicator_id'], x['timestamp']))
        
        return output
    
    def get_statistics(self) -> Dict:
        """Get statistics about generated data."""
        stats = {}
        for ind_id, data in self.generated_data.items():
            config = self.configs.get(ind_id)
            stats[ind_id] = {
                'name': config.name if config else f'Indicator {ind_id}',
                'mean': round(float(np.mean(data)), 2),
                'std': round(float(np.std(data)), 2),
                'min': round(float(np.min(data)), 2),
                'max': round(float(np.max(data)), 2),
                'trend': self._detect_trend(data)
            }
        return stats
    
    def _detect_trend(self, data: np.ndarray) -> str:
        """Detect trend in generated data."""
        if len(data) < 5:
            return 'unknown'
        
        from scipy import stats as sp_stats
        slope, _, r_value, _, _ = sp_stats.linregress(np.arange(len(data)), data)
        
        if r_value ** 2 < 0.1:
            return 'stable'
        elif slope > 0.1:
            return 'rising'
        elif slope < -0.1:
            return 'falling'
        else:
            return 'stable'


def save_json(data: List[Dict], path: Path):
    """Save data to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} records to {path}")


def main():
    parser = argparse.ArgumentParser(description='Generate realistic historical indicator values')
    parser.add_argument('--days', type=int, default=90, help='Number of days to generate')
    parser.add_argument('--out', type=str, default=str(DEFAULT_OUTPUT), help='Output JSON file path')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--stats', action='store_true', help='Print statistics after generation')
    args = parser.parse_args()
    
    print(f"Generating {args.days} days of realistic historical data...")
    
    generator = RealisticDataGenerator(seed=args.seed)
    data = generator.generate_all(days=args.days)
    save_json(data, Path(args.out))
    
    if args.stats:
        print("\n📊 Generation Statistics:")
        stats = generator.get_statistics()
        for ind_id, stat in list(stats.items())[:5]:  # Show first 5
            print(f"  Indicator {ind_id} ({stat['name']}): "
                  f"mean={stat['mean']}, std={stat['std']}, trend={stat['trend']}")
        print(f"  ... and {len(stats) - 5} more indicators")
    
    if generator.events:
        print(f"\n🎭 Simulated Events:")
        for event in generator.events:
            print(f"  - {event['type']}: day {event['start_day']}-{event['start_day']+event['duration']}, "
                  f"intensity={event['intensity']:.2f}")


if __name__ == '__main__':
    main()
