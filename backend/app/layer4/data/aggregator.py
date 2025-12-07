"""
aggregator.py - Data Aggregator for Layer 4
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
# In a real scenario, we would import Layer 3 services here
# from app.layer3.services.operational_service import OperationalService

logger = logging.getLogger(__name__)

class Layer3Connector:
    """
    Connects to Layer 3 to fetch operational indicators
    Simulated for now, but structured to use real services
    """
    
    def __init__(self):
        pass
        # self.op_service = OperationalService()
    
    async def fetch_current_indicators(self, company_id: str) -> Dict[str, Any]:
        """
        Fetch latest operational indicators for a company
        """
        # In production, this would call Layer 3 service
        # return await self.op_service.get_indicators(company_id)
        
        # For now, returning mock structure to match expectations
        return {
            "OP_AVAIL_001": {"value": 85, "trend": "stable", "confidence": 0.9},
            "OP_EFF_002": {"value": 72, "trend": "improving", "confidence": 0.85},
            "OP_RISK_003": {"value": 45, "trend": "deteriorating", "confidence": 0.8}
        }
    
    async def fetch_company_profile(self, company_id: str) -> Dict[str, Any]:
        """
        Fetch company profile
        """
        return {
            "id": company_id,
            "name": "Acme Manufacturing LK",
            "industry": "manufacturing",
            "scale": "medium",
            "characteristics": {
                "employees": 250,
                "critical_dependencies": ["fuel", "raw_material_imports"],
                "import_dependency": 0.65
            }
        }
        
    async def fetch_historical_context(self, company_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Fetch historical data
        """
        return {
            "OP_AVAIL_001": [{"timestamp": "2023-10-01", "value": 80}, {"timestamp": "2023-10-02", "value": 85}],
            "OP_EFF_002": [{"timestamp": "2023-10-01", "value": 70}, {"timestamp": "2023-10-02", "value": 72}]
        }

class DataAggregator:
    """
    Aggregates all necessary data for LLM input
    """
    
    def __init__(self):
        self.layer3 = Layer3Connector()
    
    async def prepare_context_package(self, company_id: str) -> Dict[str, Any]:
        """
        Prepare complete context package for LLM
        """
        
        # Fetch data
        current_indicators = await self.layer3.fetch_current_indicators(company_id)
        company_profile = await self.layer3.fetch_company_profile(company_id)
        historical_data = await self.layer3.fetch_historical_context(company_id)
        
        # Process trends
        trends = self._calculate_trends(historical_data)
        
        # Identify concerns
        concerns = self._identify_concerns(current_indicators)
        
        context_package = {
            'company': company_profile,
            'current_state': {
                'indicators': self._format_indicators(current_indicators),
                'areas_of_concern': concerns
            },
            'trends': trends,
            'timestamp': datetime.now().isoformat()
        }
        
        return context_package
    
    def _format_indicators(self, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format indicators for LLM"""
        formatted = []
        for code, data in indicators.items():
            formatted.append({
                'code': code,
                'name': self._get_readable_name(code),
                'value': data['value'],
                'trend': data['trend'],
                'confidence': data['confidence']
            })
        return formatted
    
    def _get_readable_name(self, code: str) -> str:
        """Map codes to names"""
        mapping = {
            "OP_AVAIL_001": "Fuel Availability",
            "OP_EFF_002": "Production Efficiency",
            "OP_RISK_003": "Supply Chain Risk"
        }
        return mapping.get(code, code)

    def _calculate_trends(self, historical_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Calculate trends"""
        return {
            "improving": ["Production Efficiency"],
            "deteriorating": ["Supply Chain Risk"],
            "stable": ["Fuel Availability"]
        }
        
    def _identify_concerns(self, indicators: Dict[str, Any]) -> List[str]:
        """Identify concerns"""
        concerns = []
        for code, data in indicators.items():
            if data['value'] < 50:
                concerns.append(f"Low {self._get_readable_name(code)} ({data['value']})")
        return concerns
