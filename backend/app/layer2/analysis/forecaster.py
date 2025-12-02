from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import timedelta

class Forecaster:
    """
    Predicts future indicator values.
    """

    def forecast(self, history: List[Dict[str, Any]], days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Forecast values for the next N days.
        
        Args:
            history: List of dicts with 'time' and 'value' keys.
            days_ahead: Number of days to forecast.
            
        Returns:
            List of forecasted values with 'time' and 'value'.
        """
        if not history or len(history) < 5:
            return []
            
        # Simple Linear Regression Forecast
        # In a real scenario, we would use Prophet or ARIMA here
        
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
            
            # Clamp value to 0-100 range (assuming index)
            future_value = max(0.0, min(100.0, future_value))
            
            forecasts.append({
                "time": (last_time + timedelta(days=i)).isoformat(),
                "value": float(future_value),
                "type": "forecast"
            })
            
        return forecasts
    
    def forecast_prophet(self, history: List[Dict[str, Any]], days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Placeholder for Prophet forecasting.
        """
        # from prophet import Prophet
        # df = pd.DataFrame(history)
        # df.columns = ['ds', 'y']
        # m = Prophet()
        # m.fit(df)
        # future = m.make_future_dataframe(periods=days_ahead)
        # forecast = m.predict(future)
        # return forecast.tail(days_ahead).to_dict('records')
        pass
