from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class TrendAnalyzer:
    """
    Analyzes trends in indicator values over time.
    """

    def analyze_trend(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trend based on historical values.
        
        Args:
            history: List of dicts with 'time' and 'value' keys.
            
        Returns:
            Dict containing trend direction, strength, and moving averages.
        """
        if not history or len(history) < 2:
            return {
                "direction": "stable",
                "strength": 0.0,
                "ma_7d": None,
                "ma_30d": None
            }
            
        # Convert to DataFrame
        df = pd.DataFrame(history)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        df.set_index('time', inplace=True)
        
        # Calculate Moving Averages
        ma_7d = df['value'].rolling(window=7, min_periods=1).mean().iloc[-1]
        ma_30d = df['value'].rolling(window=30, min_periods=1).mean().iloc[-1]
        
        # Determine Direction (Linear Regression Slope)
        # Use last 7 days for short-term trend
        recent_df = df.tail(7)
        
        if len(recent_df) > 1:
            x = np.arange(len(recent_df))
            y = recent_df['value'].values
            slope, _ = np.polyfit(x, y, 1)
            
            if slope > 0.5:
                direction = "rising"
            elif slope < -0.5:
                direction = "falling"
            else:
                direction = "stable"
                
            strength = abs(slope)
        else:
            direction = "stable"
            strength = 0.0
            
        return {
            "direction": direction,
            "strength": float(strength),
            "ma_7d": float(ma_7d),
            "ma_30d": float(ma_30d)
        }
