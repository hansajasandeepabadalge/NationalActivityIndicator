from typing import Dict, Any, List
from datetime import datetime
from ..data.mock_loader import MockDataLoader
from ..engine.translator import ImpactTranslator
from ..engine import universal_indicators
from ..engine import industry_indicators

class OperationalService:
    
    def __init__(self):
        self.data_loader = MockDataLoader()
        self.translator = ImpactTranslator() # In real app, pass rules from DB
    
    def calculate_indicators_for_company(self, company_id: str) -> Dict[str, Any]:
        """
        Run full calculation pipeline for a company
        """
        # 1. Load Data
        company_profile = self.data_loader.get_company(company_id)
        if not company_profile:
            raise ValueError(f"Company {company_id} not found")
            
        national_indicators = self.data_loader.get_national_indicators()
        
        # 2. Calculate Universal Indicators
        universal_results = {
            'transport_availability': universal_indicators.calculate_transportation_availability(national_indicators, company_profile),
            'workforce_availability': universal_indicators.calculate_workforce_availability(national_indicators, company_profile),
            'supply_chain_integrity': universal_indicators.calculate_supply_chain_integrity(national_indicators, company_profile),
            'cost_pressure': universal_indicators.calculate_operational_cost_pressure(national_indicators, company_profile),
            'compliance_status': universal_indicators.calculate_regulatory_compliance_status(national_indicators, company_profile)
        }
        
        # 3. Calculate Industry-Specific Indicators
        industry_results = {}
        industry = company_profile.get('industry')
        
        if industry == 'retail':
            industry_results['footfall_impact'] = industry_indicators.calculate_retail_footfall_impact(national_indicators, company_profile)
        elif industry == 'manufacturing':
            industry_results['production_capacity'] = industry_indicators.calculate_manufacturing_capacity(national_indicators, company_profile)
        elif industry == 'logistics':
            industry_results['fleet_availability'] = industry_indicators.calculate_logistics_fleet_availability(national_indicators, company_profile)
            
        # 4. Translate National Indicators (Impact Translation)
        # This demonstrates the "Translation Matrix" concept
        translation_results = []
        for ind in national_indicators.get('indicators', []):
            impacts = self.translator.translate_to_operational(ind, company_profile)
            translation_results.extend(impacts)
            
        # 5. Aggregate Results
        final_output = {
            'company_id': company_id,
            'timestamp': datetime.utcnow().isoformat(),
            'universal_indicators': universal_results,
            'industry_specific_indicators': industry_results,
            'translation_impacts': translation_results,
            'status': 'success'
        }
        
        # In a real app, we would save to TimescaleDB and MongoDB here
        
        return final_output

    def get_all_companies(self):
        return self.data_loader.get_all_companies()
