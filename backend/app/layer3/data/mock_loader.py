import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class MockDataLoader:
    """
    Loads mock data for Layer 3 development
    """
    
    def __init__(self, mock_data_dir: str = None):
        if mock_data_dir is None:
            # Default to relative path from this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.mock_data_dir = os.path.join(current_dir, "..", "mock_data")
        else:
            self.mock_data_dir = mock_data_dir
            
        self.companies = self._load_companies()
        self.national_indicators = self._load_national_indicators()
        self.historical_data = self._load_historical_data()
    
    def _load_companies(self) -> Dict[str, Any]:
        """Load mock company profiles"""
        companies = {}
        company_dir = os.path.join(self.mock_data_dir, "companies")
        
        if not os.path.exists(company_dir):
            return {}

        for filename in os.listdir(company_dir):
            if filename.endswith('.json'):
                with open(os.path.join(company_dir, filename), 'r') as f:
                    company = json.load(f)
                    companies[company['company_id']] = company
        
        return companies
    
    def _load_national_indicators(self) -> Dict[str, Any]:
        """Load mock national indicators"""
        path = os.path.join(self.mock_data_dir, "national_indicators", "current_state.json")
        if not os.path.exists(path):
            return {}
            
        with open(path, 'r') as f:
            return json.load(f)
    
    def _load_historical_data(self) -> Dict[str, List[Any]]:
        """Load time-series mock data"""
        historical = {}
        ts_dir = os.path.join(self.mock_data_dir, "timeseries")
        
        if not os.path.exists(ts_dir):
            return {}

        for filename in os.listdir(ts_dir):
            if filename.endswith('.json'):
                with open(os.path.join(ts_dir, filename), 'r') as f:
                    data = json.load(f)
                    historical[data['indicator_code']] = data['time_series']
        
        return historical
    
    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get mock company profile"""
        return self.companies.get(company_id)
    
    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all mock companies"""
        return list(self.companies.values())
    
    def get_national_indicators(self) -> Dict[str, Any]:
        """Get all national indicators"""
        return self.national_indicators
        
    def get_national_indicator(self, indicator_code: str) -> Optional[Dict[str, Any]]:
        """Get current value of national indicator"""
        indicators = self.national_indicators.get('indicators', [])
        for ind in indicators:
            if ind['indicator_code'] == indicator_code:
                return ind
        return None
    
    def get_historical_values(self, indicator_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical values for indicator"""
        return self.historical_data.get(indicator_code, [])[-days:]
