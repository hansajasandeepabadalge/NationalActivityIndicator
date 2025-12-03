"""
Enhanced Trend and Forecast Runner Script.

Uses the enhanced trend detector and forecaster for better quality predictions.
Generates comprehensive analysis for all indicators.

Usage:
    python backend/scripts/calculate_enhanced_trends_forecasts.py --out backend/data/enhanced_indicator_analysis.json

Author: Day 5 Enhancement
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.layer2.analysis.trend_detector_enhanced import EnhancedTrendDetector
from app.layer2.analysis.forecaster_enhanced import EnhancedForecaster, ForecastMethod

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "enhanced_indicator_analysis.json"
INDICATOR_IDS = list(range(1, 25))


def run_enhanced_analysis(indicator_ids: list = None, days_ahead: int = 7) -> dict:
    """
    Run enhanced trend detection and forecasting for all indicators.
    
    Returns comprehensive analysis with:
    - Multi-timeframe trend analysis
    - Ensemble forecasts
    - Model quality scores
    - Statistical significance
    """
    if indicator_ids is None:
        indicator_ids = INDICATOR_IDS
    
    trend_detector = EnhancedTrendDetector()
    forecaster = EnhancedForecaster()
    
    results = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'forecast_horizon': days_ahead,
        'indicators': {}
    }
    
    quality_scores = []
    
    for ind_id in indicator_ids:
        print(f"Analyzing indicator {ind_id}...", end=" ")
        
        # Get comprehensive trend summary
        trend_summary = trend_detector.get_trend_summary(ind_id)
        
        # Get ensemble forecast
        forecast_result = forecaster.forecast(
            ind_id, 
            days_ahead=days_ahead,
            method=ForecastMethod.ENSEMBLE
        )
        
        # Compile results
        indicator_analysis = {
            'indicator_id': ind_id,
            'trend_analysis': {
                'overall_outlook': trend_summary['overall_outlook'],
                'trend_alignment': trend_summary['trend_alignment'],
                'short_term': trend_summary['short_term'],
                'medium_term': trend_summary['medium_term'],
                'long_term': trend_summary['long_term'],
            },
            'moving_averages': trend_summary['moving_averages'],
        }
        
        if forecast_result:
            indicator_analysis['forecast'] = {
                'method': forecast_result.method,
                'model_quality': forecast_result.model_quality,
                'trend_direction': forecast_result.trend_direction,
                'volatility': forecast_result.volatility,
                'last_value': forecast_result.last_value,
                'predictions': [f.to_dict() for f in forecast_result.forecasts]
            }
            quality_scores.append(forecast_result.model_quality)
            print(f"✓ (quality: {forecast_result.model_quality:.2f})")
        else:
            indicator_analysis['forecast'] = None
            print("✓ (no forecast - insufficient data)")
        
        results['indicators'][str(ind_id)] = indicator_analysis
    
    # Add summary statistics
    if quality_scores:
        results['summary'] = {
            'total_indicators': len(indicator_ids),
            'forecasted_indicators': len(quality_scores),
            'average_model_quality': round(sum(quality_scores) / len(quality_scores), 3),
            'min_model_quality': round(min(quality_scores), 3),
            'max_model_quality': round(max(quality_scores), 3),
        }
        
        # Count outlook distributions
        outlooks = [results['indicators'][str(i)]['trend_analysis']['overall_outlook'] 
                    for i in indicator_ids]
        results['summary']['outlook_distribution'] = {
            'bullish': outlooks.count('bullish'),
            'bearish': outlooks.count('bearish'),
            'neutral': outlooks.count('neutral'),
        }
    
    return results


def save_results(results: dict, path: Path):
    """Save results to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved enhanced analysis to {path}")


def print_summary(results: dict):
    """Print analysis summary."""
    print("\n" + "=" * 60)
    print("ENHANCED INDICATOR ANALYSIS SUMMARY")
    print("=" * 60)
    
    if 'summary' in results:
        s = results['summary']
        print(f"\n📊 Overview:")
        print(f"   Total Indicators: {s['total_indicators']}")
        print(f"   Forecasted: {s['forecasted_indicators']}")
        print(f"   Average Model Quality: {s['average_model_quality']:.1%}")
        
        print(f"\n📈 Outlook Distribution:")
        od = s.get('outlook_distribution', {})
        print(f"   Bullish: {od.get('bullish', 0)}")
        print(f"   Bearish: {od.get('bearish', 0)}")
        print(f"   Neutral: {od.get('neutral', 0)}")
    
    print("\n📋 Top 5 Indicators by Model Quality:")
    indicators = results.get('indicators', {})
    
    sorted_indicators = sorted(
        [(ind_id, data) for ind_id, data in indicators.items() 
         if data.get('forecast') and data['forecast'].get('model_quality')],
        key=lambda x: x[1]['forecast']['model_quality'],
        reverse=True
    )
    
    for i, (ind_id, data) in enumerate(sorted_indicators[:5], 1):
        forecast = data['forecast']
        trend = data['trend_analysis']
        print(f"   {i}. Indicator {ind_id}: quality={forecast['model_quality']:.2f}, "
              f"outlook={trend['overall_outlook']}, "
              f"volatility={forecast['volatility']:.2f}")
    
    print("\n⚠️  Indicators with Low Model Quality (<0.5):")
    low_quality = [
        (ind_id, data) for ind_id, data in indicators.items()
        if data.get('forecast') and data['forecast'].get('model_quality', 1) < 0.5
    ]
    
    if low_quality:
        for ind_id, data in low_quality:
            print(f"   - Indicator {ind_id}: quality={data['forecast']['model_quality']:.2f}")
    else:
        print("   None - all models have acceptable quality!")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Run enhanced trend and forecast analysis')
    parser.add_argument('--out', type=str, default=str(DEFAULT_OUTPUT), help='Output JSON path')
    parser.add_argument('--days', type=int, default=7, help='Forecast horizon in days')
    parser.add_argument('--indicators', type=str, default=None, 
                        help='Comma-separated indicator IDs (default: all)')
    parser.add_argument('--quiet', action='store_true', help='Suppress detailed output')
    args = parser.parse_args()
    
    # Parse indicator IDs if provided
    indicator_ids = None
    if args.indicators:
        indicator_ids = [int(x.strip()) for x in args.indicators.split(',')]
    
    print(f"🔬 Running Enhanced Analysis (forecast horizon: {args.days} days)")
    print("-" * 60)
    
    results = run_enhanced_analysis(indicator_ids, days_ahead=args.days)
    save_results(results, Path(args.out))
    
    if not args.quiet:
        print_summary(results)


if __name__ == '__main__':
    main()
