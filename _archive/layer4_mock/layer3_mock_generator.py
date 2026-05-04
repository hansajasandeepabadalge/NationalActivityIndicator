"""
Mock Layer 3 Operational Indicators Generator

Simulates operational indicators from Layer 3 for Layer 4 testing
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
from pydantic import BaseModel


class OperationalIndicators(BaseModel):
    """Mock operational indicators from Layer 3"""
    timestamp: datetime
    company_id: str

    # Supply Chain & Logistics (0-100 scale)
    OPS_SUPPLY_CHAIN: float  # Supply chain integrity
    OPS_TRANSPORT_AVAIL: float  # Transport availability
    OPS_LOGISTICS_COST: float  # Logistics cost pressure
    OPS_IMPORT_FLOW: float  # Import flow smoothness

    # Workforce & Operations
    OPS_WORKFORCE_AVAIL: float  # Workforce availability
    OPS_LABOR_COST: float  # Labor cost pressure
    OPS_PRODUCTIVITY: float  # Operational productivity

    # Infrastructure & Resources
    OPS_POWER_RELIABILITY: float  # Power infrastructure
    OPS_FUEL_AVAIL: float  # Fuel availability
    OPS_WATER_SUPPLY: float  # Water supply
    OPS_INTERNET_CONNECTIVITY: float  # Digital infrastructure

    # Cost Pressures
    OPS_COST_PRESSURE: float  # Overall cost pressure
    OPS_RAW_MATERIAL_COST: float  # Raw material costs
    OPS_ENERGY_COST: float  # Energy costs

    # Market Conditions
    OPS_DEMAND_LEVEL: float  # Customer demand
    OPS_COMPETITION_INTENSITY: float  # Competitive pressure
    OPS_PRICING_POWER: float  # Ability to raise prices

    # Financial Operations
    OPS_CASH_FLOW: float  # Cash flow health
    OPS_CREDIT_AVAIL: float  # Credit availability
    OPS_PAYMENT_DELAYS: float  # Customer payment delays

    # Regulatory & Compliance
    OPS_REGULATORY_BURDEN: float  # Regulatory complexity
    OPS_COMPLIANCE_COST: float  # Compliance costs

    # Trends (7-day change)
    trends: Dict[str, str]  # 'rising', 'falling', 'stable'


class MockLayer3Generator:
    """Generate mock Layer 3 operational indicators"""

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)

    def generate_baseline(self, company_id: str, industry: str, business_scale: str) -> Dict[str, float]:
        """Generate baseline indicator values based on company profile"""

        # Industry baselines
        industry_profiles = {
            'retail': {
                'OPS_SUPPLY_CHAIN': 70,
                'OPS_TRANSPORT_AVAIL': 75,
                'OPS_WORKFORCE_AVAIL': 65,
                'OPS_DEMAND_LEVEL': 70,
                'OPS_COMPETITION_INTENSITY': 80,
            },
            'manufacturing': {
                'OPS_SUPPLY_CHAIN': 65,
                'OPS_TRANSPORT_AVAIL': 70,
                'OPS_WORKFORCE_AVAIL': 70,
                'OPS_RAW_MATERIAL_COST': 60,
                'OPS_POWER_RELIABILITY': 65,
            },
            'logistics': {
                'OPS_TRANSPORT_AVAIL': 80,
                'OPS_FUEL_AVAIL': 70,
                'OPS_LOGISTICS_COST': 55,
                'OPS_DEMAND_LEVEL': 75,
            },
            'hospitality': {
                'OPS_WORKFORCE_AVAIL': 60,
                'OPS_DEMAND_LEVEL': 65,
                'OPS_POWER_RELIABILITY': 70,
                'OPS_WATER_SUPPLY': 75,
            },
            'technology': {
                'OPS_WORKFORCE_AVAIL': 80,
                'OPS_INTERNET_CONNECTIVITY': 85,
                'OPS_POWER_RELIABILITY': 75,
                'OPS_DEMAND_LEVEL': 80,
            },
            'agriculture': {
                'OPS_SUPPLY_CHAIN': 60,
                'OPS_TRANSPORT_AVAIL': 65,
                'OPS_FUEL_AVAIL': 65,
                'OPS_WATER_SUPPLY': 70,
                'OPS_RAW_MATERIAL_COST': 55,
            },
        }

        # Start with default values
        baseline = {
            'OPS_SUPPLY_CHAIN': 70,
            'OPS_TRANSPORT_AVAIL': 70,
            'OPS_LOGISTICS_COST': 60,
            'OPS_IMPORT_FLOW': 70,
            'OPS_WORKFORCE_AVAIL': 70,
            'OPS_LABOR_COST': 60,
            'OPS_PRODUCTIVITY': 70,
            'OPS_POWER_RELIABILITY': 70,
            'OPS_FUEL_AVAIL': 70,
            'OPS_WATER_SUPPLY': 75,
            'OPS_INTERNET_CONNECTIVITY': 75,
            'OPS_COST_PRESSURE': 60,
            'OPS_RAW_MATERIAL_COST': 65,
            'OPS_ENERGY_COST': 60,
            'OPS_DEMAND_LEVEL': 70,
            'OPS_COMPETITION_INTENSITY': 70,
            'OPS_PRICING_POWER': 60,
            'OPS_CASH_FLOW': 70,
            'OPS_CREDIT_AVAIL': 70,
            'OPS_PAYMENT_DELAYS': 70,
            'OPS_REGULATORY_BURDEN': 65,
            'OPS_COMPLIANCE_COST': 65,
        }

        # Apply industry-specific adjustments
        if industry in industry_profiles:
            for key, value in industry_profiles[industry].items():
                baseline[key] = value

        # Business scale adjustments
        scale_multipliers = {
            'small': {'OPS_CASH_FLOW': -10, 'OPS_COST_PRESSURE': 5, 'OPS_CREDIT_AVAIL': -5},
            'medium': {},  # Baseline
            'large': {'OPS_CASH_FLOW': 10, 'OPS_PRICING_POWER': 10, 'OPS_COST_PRESSURE': -5},
            'enterprise': {'OPS_CASH_FLOW': 15, 'OPS_PRICING_POWER': 15, 'OPS_SUPPLY_CHAIN': 10},
        }

        if business_scale in scale_multipliers:
            for key, adjustment in scale_multipliers[business_scale].items():
                if key in baseline:
                    baseline[key] = max(0, min(100, baseline[key] + adjustment))

        return baseline

    def apply_noise(self, value: float, volatility: float = 5.0) -> float:
        """Add random noise to indicator value"""
        noise = random.gauss(0, volatility)
        return max(0, min(100, value + noise))

    def apply_trend(self, value: float, trend: str, days_elapsed: int) -> float:
        """Apply trend over time"""
        if trend == 'rising':
            delta = random.uniform(0.5, 2.0) * days_elapsed
            return min(100, value + delta)
        elif trend == 'falling':
            delta = random.uniform(0.5, 2.0) * days_elapsed
            return max(0, value - delta)
        else:  # stable
            return value

    def generate_indicators(
        self,
        company_id: str,
        industry: str,
        business_scale: str,
        timestamp: datetime,
        scenario: Optional[str] = None
    ) -> OperationalIndicators:
        """Generate operational indicators for a company at a specific time"""

        baseline = self.generate_baseline(company_id, industry, business_scale)

        # Apply scenario modifications
        if scenario == 'fuel_crisis':
            baseline['OPS_FUEL_AVAIL'] = self.apply_noise(40, 5)
            baseline['OPS_TRANSPORT_AVAIL'] = self.apply_noise(45, 5)
            baseline['OPS_LOGISTICS_COST'] = self.apply_noise(35, 5)
            baseline['OPS_ENERGY_COST'] = self.apply_noise(30, 5)
            baseline['OPS_COST_PRESSURE'] = self.apply_noise(30, 5)

        elif scenario == 'supply_disruption':
            baseline['OPS_SUPPLY_CHAIN'] = self.apply_noise(45, 5)
            baseline['OPS_IMPORT_FLOW'] = self.apply_noise(50, 5)
            baseline['OPS_RAW_MATERIAL_COST'] = self.apply_noise(35, 5)
            baseline['OPS_COST_PRESSURE'] = self.apply_noise(40, 5)

        elif scenario == 'strong_demand':
            baseline['OPS_DEMAND_LEVEL'] = self.apply_noise(85, 3)
            baseline['OPS_PRICING_POWER'] = self.apply_noise(80, 3)
            baseline['OPS_CASH_FLOW'] = self.apply_noise(85, 3)
            baseline['OPS_PRODUCTIVITY'] = self.apply_noise(80, 3)

        elif scenario == 'labor_shortage':
            baseline['OPS_WORKFORCE_AVAIL'] = self.apply_noise(45, 5)
            baseline['OPS_LABOR_COST'] = self.apply_noise(35, 5)
            baseline['OPS_PRODUCTIVITY'] = self.apply_noise(55, 5)
            baseline['OPS_COST_PRESSURE'] = self.apply_noise(45, 5)

        else:
            # Normal scenario - add small random variations
            for key in baseline:
                baseline[key] = self.apply_noise(baseline[key], volatility=3.0)

        # Calculate trends (simplified)
        trends = {}
        for key in baseline:
            if baseline[key] > 70:
                trends[key] = random.choice(['stable', 'rising', 'rising'])
            elif baseline[key] < 50:
                trends[key] = random.choice(['stable', 'falling', 'falling'])
            else:
                trends[key] = random.choice(['stable', 'stable', 'rising', 'falling'])

        return OperationalIndicators(
            timestamp=timestamp,
            company_id=company_id,
            **baseline,
            trends=trends
        )

    def generate_time_series(
        self,
        company_id: str,
        industry: str,
        business_scale: str,
        start_date: datetime,
        days: int = 30,
        scenario_schedule: Optional[Dict[int, str]] = None
    ) -> List[OperationalIndicators]:
        """
        Generate time series of operational indicators

        Args:
            company_id: Company identifier
            industry: Industry type
            business_scale: Business size
            start_date: Starting date
            days: Number of days to generate
            scenario_schedule: Dict of {day_number: scenario_name}
        """
        series = []
        scenario_schedule = scenario_schedule or {}

        for day in range(days):
            current_date = start_date + timedelta(days=day)
            scenario = scenario_schedule.get(day, None)

            indicators = self.generate_indicators(
                company_id=company_id,
                industry=industry,
                business_scale=business_scale,
                timestamp=current_date,
                scenario=scenario
            )

            series.append(indicators)

        return series


# Convenience function
def generate_mock_operational_indicators(
    company_id: str,
    industry: str,
    business_scale: str,
    timestamp: Optional[datetime] = None
) -> OperationalIndicators:
    """Quick function to generate mock indicators"""
    generator = MockLayer3Generator()
    return generator.generate_indicators(
        company_id=company_id,
        industry=industry,
        business_scale=business_scale,
        timestamp=timestamp or datetime.now()
    )
