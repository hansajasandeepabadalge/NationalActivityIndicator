from typing import List, Dict, Any
import numpy as np
import pandas as pd

class AnomalyDetector:
    """
    Detects anomalies in indicator values using statistical methods.
    """

    def detect_anomalies(self, history: List[Dict[str, Any]], threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies using Z-score.
        
        Args:
            history: List of dicts with 'time' and 'value'.
            threshold: Z-score threshold (default 2.0 for 95% confidence).
            
        Returns:
            List of anomalies detected.
        """
        if not history or len(history) < 5:
            return []
            
        df = pd.DataFrame(history)
        df['value'] = pd.to_numeric(df['value'])
        
        # Calculate Z-score
        mean = df['value'].mean()
        std = df['value'].std()
        
        if std == 0:
            return []
            
        df['z_score'] = (df['value'] - mean) / std
        
        # Filter anomalies
        anomalies_df = df[abs(df['z_score']) > threshold].copy()
        
        anomalies = []
        for _, row in anomalies_df.iterrows():
            anomalies.append({
                "time": row['time'],
                "value": row['value'],
                "z_score": row['z_score'],
                "type": "spike" if row['z_score'] > 0 else "drop",
                "severity": abs(row['z_score'])
            })
            
        return anomalies
