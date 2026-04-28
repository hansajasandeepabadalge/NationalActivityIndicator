"""
aggregator.py - Data Aggregator for Layer 4

Aggregates data from Layer 3 (Operational Indicators) to prepare
context packages for LLM-based insight generation.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class Layer3Connector:
    """
    Connects to Layer 3 to fetch operational indicators.

    Layer 3 `calculate_indicators_for_company()` returns:
      {
        'universal_indicators': {'transport_availability': float, ...},
        'industry_specific_indicators': {'footfall_impact': dict|float, ...},
        ...
      }

    This class adapts that output to the flat code-keyed format Layer 4 detectors use:
      { 'OPS_TRANSPORT_AVAIL': {'value': float, 'trend': str, 'confidence': float, 'name': str}, ... }
    """

    # Maps Layer 3 internal keys → Layer 4 indicator codes + human names
    _UNIV_CODE_MAP = {
        'transport_availability':  ('OPS_TRANSPORT_AVAIL',  'Transportation Availability'),
        'workforce_availability':  ('OPS_WORKFORCE_AVAIL',  'Workforce Availability'),
        'supply_chain_integrity':  ('OPS_SUPPLY_CHAIN',     'Supply Chain Integrity'),
        'cost_pressure':           ('OPS_COST_PRESSURE',    'Operational Cost Pressure'),
        'compliance_status':       ('OPS_COMPLIANCE',       'Regulatory Compliance Status'),
    }
    _IND_CODE_MAP = {
        'footfall_impact':         ('OPS_FOOTFALL_IMPACT',      'Expected Foot Traffic Impact'),
        'production_capacity':     ('OPS_PRODUCTION_CAPACITY',  'Production Capacity Utilization'),
        'fleet_availability':      ('OPS_FLEET_AVAIL',          'Fleet Availability'),
    }

    def __init__(self):
        self._op_service = None
        try:
            from app.layer3.services.operational_service import OperationalService
            self._op_service = OperationalService()
            logger.info("Layer3Connector using real OperationalService")
        except ImportError:
            logger.info("Layer3Connector using mock data (OperationalService not available)")

    def _adapt_layer3_output(self, layer3_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Layer 3 calculation output to the flat indicator dict Layer 4 expects.
        Each entry: { code: {'value': float, 'trend': 'stable', 'confidence': float, 'name': str} }
        """
        flat: Dict[str, Any] = {}

        univ = layer3_result.get('universal_indicators', {})
        for key, (code, name) in self._UNIV_CODE_MAP.items():
            raw = univ.get(key, 0.0)
            value = float(raw) if isinstance(raw, (int, float)) else 0.0
            flat[code] = {'value': value, 'trend': 'stable', 'confidence': 0.80, 'name': name}

        ind = layer3_result.get('industry_specific_indicators', {})
        for key, (code, name) in self._IND_CODE_MAP.items():
            raw = ind.get(key)
            if raw is None:
                continue
            if isinstance(raw, dict):
                value = float(raw.get('value', 0.0))
            else:
                value = float(raw)
            flat[code] = {'value': value, 'trend': 'stable', 'confidence': 0.80, 'name': name}

        return flat

    async def fetch_current_indicators(self, company_id: str) -> Dict[str, Any]:
        """Fetch latest operational indicators for a company."""
        if self._op_service:
            try:
                # calculate_indicators_for_company is sync — run in thread to stay non-blocking
                import asyncio
                result = await asyncio.to_thread(
                    self._op_service.calculate_indicators_for_company, company_id
                )
                return self._adapt_layer3_output(result)
            except Exception as e:
                logger.warning(f"Failed to fetch from Layer 3, using mock: {e}")

        # Mock fallback — codes match what Layer 4 rule detectors reference
        return {
            "OPS_SUPPLY_CHAIN":      {"value": 78, "trend": "stable",       "confidence": 0.88, "name": "Supply Chain Integrity"},
            "OPS_TRANSPORT_AVAIL":   {"value": 85, "trend": "improving",     "confidence": 0.92, "name": "Transportation Availability"},
            "OPS_WORKFORCE_AVAIL":   {"value": 65, "trend": "stable",        "confidence": 0.85, "name": "Workforce Availability"},
            "OPS_COST_PRESSURE":     {"value": 45, "trend": "deteriorating", "confidence": 0.80, "name": "Operational Cost Pressure"},
            "OPS_FOOTFALL_IMPACT":   {"value": 72, "trend": "improving",     "confidence": 0.87, "name": "Expected Foot Traffic Impact"},
        }

    async def fetch_company_profile(self, company_id: str) -> Dict[str, Any]:
        """
        Fetch company profile information
        """
        # In production, fetch from database
        # For now, return structured mock data
        return {
            "id": company_id,
            "name": f"Company {company_id}",
            "industry": "manufacturing",
            "size": "medium",
            "scale": "medium",
            "characteristics": {
                "employees": 250,
                "critical_dependencies": ["fuel", "raw_material_imports", "skilled_labor"],
                "import_dependency": 0.65,
                "export_percentage": 0.30,
                "primary_markets": ["domestic", "regional"]
            },
            "risk_tolerance": "moderate",
            "strategic_priorities": ["cost_reduction", "market_expansion"]
        }

    async def fetch_historical_context(
        self, 
        company_id: str, 
        days: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch historical indicator data for trend analysis
        """
        # Mock historical data
        base_date = datetime.now(timezone.utc)
        
        return {
            "OP_SUPPLY_001": [
                {"timestamp": (base_date.replace(day=max(1, base_date.day - i))).isoformat(), "value": 75 + i % 5}
                for i in range(min(days, 7))
            ],
            "OP_FUEL_002": [
                {"timestamp": (base_date.replace(day=max(1, base_date.day - i))).isoformat(), "value": 80 + i % 8}
                for i in range(min(days, 7))
            ],
            "OP_COST_004": [
                {"timestamp": (base_date.replace(day=max(1, base_date.day - i))).isoformat(), "value": 50 - i % 5}
                for i in range(min(days, 7))
            ]
        }

    async def fetch_industry_benchmarks(self, industry: str) -> Dict[str, Any]:
        """
        Fetch industry benchmark data for comparison
        """
        benchmarks = {
            "manufacturing": {
                "supply_chain_health": 75,
                "labor_availability": 70,
                "cost_efficiency": 65,
                "demand_index": 70
            },
            "retail": {
                "supply_chain_health": 80,
                "labor_availability": 75,
                "cost_efficiency": 60,
                "demand_index": 75
            },
            "technology": {
                "supply_chain_health": 85,
                "labor_availability": 65,
                "cost_efficiency": 70,
                "demand_index": 80
            }
        }
        return benchmarks.get(industry, benchmarks["manufacturing"])


class DataAggregator:
    """
    Aggregates all necessary data for LLM input.
    
    Collects data from Layer 3, processes trends, identifies concerns,
    and builds comprehensive context packages for LLM prompts.
    """

    def __init__(self):
        self.layer3 = Layer3Connector()

    async def prepare_context_package(self, company_id: str) -> Dict[str, Any]:
        """
        Prepare complete context package for LLM
        
        This is the main entry point that collects all necessary data
        and formats it for LLM consumption.
        """
        # Fetch all data
        current_indicators = await self.layer3.fetch_current_indicators(company_id)
        company_profile = await self.layer3.fetch_company_profile(company_id)
        historical_data = await self.layer3.fetch_historical_context(company_id)

        # Process and analyze
        trends = self._calculate_trends(current_indicators, historical_data)
        concerns = self._identify_concerns(current_indicators)
        strengths = self._identify_strengths(current_indicators)

        context_package = {
            'company': company_profile,
            'current_state': {
                'indicators': self._format_indicators(current_indicators),
                'areas_of_concern': concerns,
                'areas_of_strength': strengths
            },
            'trends': trends,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data_quality': self._assess_data_quality(current_indicators)
        }

        return context_package

    def _format_indicators(self, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format indicators for LLM consumption"""
        formatted = []
        for code, data in indicators.items():
            formatted.append({
                'code': code,
                'name': data.get('name', self._get_readable_name(code)),
                'value': data.get('value', 0),
                'trend': data.get('trend', 'stable'),
                'confidence': data.get('confidence', 0.5),
                'interpretation': self._interpret_value(data.get('value', 0), data.get('trend', 'stable'))
            })
        return formatted

    def _get_readable_name(self, code: str) -> str:
        """Map indicator codes to human-readable names"""
        mapping = {
            "OP_SUPPLY_001": "Supply Chain Health",
            "OP_FUEL_002": "Fuel Availability",
            "OP_LABOR_003": "Labor Availability",
            "OP_COST_004": "Cost Pressure Index",
            "OP_DEMAND_005": "Market Demand",
            "OP_AVAIL_001": "Resource Availability",
            "OP_EFF_002": "Production Efficiency",
            "OP_RISK_003": "Operational Risk Level"
        }
        return mapping.get(code, code.replace("_", " ").title())

    def _interpret_value(self, value: float, trend: str) -> str:
        """Generate interpretation text for an indicator value"""
        if value >= 80:
            level = "Excellent"
        elif value >= 60:
            level = "Good"
        elif value >= 40:
            level = "Moderate"
        elif value >= 20:
            level = "Poor"
        else:
            level = "Critical"
        
        trend_text = {
            "improving": "and improving",
            "deteriorating": "and declining",
            "stable": "and stable"
        }.get(trend, "")
        
        return f"{level} {trend_text}".strip()

    def _calculate_trends(
        self, 
        current: Dict[str, Any], 
        historical: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Calculate trends from current and historical data"""
        improving = []
        deteriorating = []
        stable = []

        for code, data in current.items():
            trend = data.get('trend', 'stable')
            name = data.get('name', self._get_readable_name(code))
            
            if trend == 'improving':
                improving.append(name)
            elif trend == 'deteriorating':
                deteriorating.append(name)
            else:
                stable.append(name)

        return {
            "improving": improving,
            "deteriorating": deteriorating,
            "stable": stable
        }

    def _identify_concerns(self, indicators: Dict[str, Any]) -> List[str]:
        """Identify areas of concern based on indicator values"""
        concerns = []
        for code, data in indicators.items():
            value = data.get('value', 0)
            trend = data.get('trend', 'stable')
            name = data.get('name', self._get_readable_name(code))
            
            if value < 50:
                concerns.append(f"Low {name} ({value}/100)")
            elif value < 60 and trend == 'deteriorating':
                concerns.append(f"Declining {name} ({value}/100, trending down)")
                
        return concerns

    def _identify_strengths(self, indicators: Dict[str, Any]) -> List[str]:
        """Identify areas of strength based on indicator values"""
        strengths = []
        for code, data in indicators.items():
            value = data.get('value', 0)
            trend = data.get('trend', 'stable')
            name = data.get('name', self._get_readable_name(code))
            
            if value >= 80:
                strengths.append(f"Strong {name} ({value}/100)")
            elif value >= 70 and trend == 'improving':
                strengths.append(f"Improving {name} ({value}/100, trending up)")
                
        return strengths

    def _assess_data_quality(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the input data"""
        confidences = [data.get('confidence', 0.5) for data in indicators.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        return {
            "indicator_count": len(indicators),
            "average_confidence": round(avg_confidence, 2),
            "data_freshness": "current",
            "completeness": "full" if len(indicators) >= 5 else "partial"
        }
