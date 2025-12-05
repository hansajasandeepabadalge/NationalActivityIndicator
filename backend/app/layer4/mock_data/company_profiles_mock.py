"""
Mock Company Profiles Generator

Creates realistic company profiles for testing Layer 4
"""
from typing import List, Dict, Any
from decimal import Decimal


class MockCompanyGenerator:
    """Generate mock company profiles across various industries"""

    def __init__(self):
        self.companies = self._create_companies()

    def _create_companies(self) -> List[Dict[str, Any]]:
        """Create 10+ mock companies across different industries"""

        companies = [
            # 1. Retail - Large supermarket chain
            {
                'company_id': 'retail_001',
                'company_name': 'Ceylon SuperMart Holdings',
                'display_name': 'Ceylon SuperMart',
                'industry': 'retail',
                'sub_industry': 'supermarkets',
                'business_scale': 'large',
                'description': 'Leading supermarket chain with 50+ outlets nationwide',
                'business_model': 'B2C',
                'annual_revenue': Decimal('5500000000'),  # LKR 5.5B
                'revenue_currency': 'LKR',
                'cash_reserves': Decimal('850000000'),  # LKR 850M
                'debt_level': 'moderate',
                'employee_count': 2500,
                'locations': ['Colombo', 'Kandy', 'Galle', 'Jaffna', 'Kurunegala'],
                'primary_location': 'Colombo',
                'supply_chain_profile': {
                    'import_dependency': 0.6,
                    'key_suppliers': ['Global Foods Ltd', 'Lanka Distributors', 'Import Corp'],
                    'supplier_concentration': 'medium',
                    'average_lead_time_days': 21
                },
                'operational_dependencies': {
                    'power_dependency': 'critical',
                    'transport_dependency': 'high',
                    'workforce_dependency': 'high',
                    'digital_dependency': 'medium'
                },
                'market_position': 'challenger',
                'market_share_percentage': Decimal('18.5'),
                'key_competitors': ['Metro Foods', 'Lanka Retail Chain', 'QuickMart'],
                'geographic_exposure': {
                    'regions': ['Western', 'Central', 'Southern', 'Northern'],
                    'concentration': 'diversified',
                    'export_percentage': 0.0
                },
                'risk_tolerance': 'moderate',
                'vulnerability_factors': {
                    'currency_exposure': 'high',
                    'regulatory_exposure': 'medium',
                    'commodity_price_sensitivity': 'high',
                    'seasonality_impact': 'low'
                },
                'strategic_priorities': ['market_expansion', 'cost_reduction', 'digital_transformation'],
                'growth_stage': 'growth',
                'primary_contact_name': 'Rohan Perera',
                'primary_contact_email': 'rohan.perera@ceylonsupermart.lk',
                'ownership_type': 'public',
                'alert_preferences': {
                    'critical_threshold': 40.0,
                    'notification_channels': ['email', 'dashboard', 'sms'],
                    'quiet_hours': {'start': '20:00', 'end': '06:00'},
                    'categories_to_watch': ['operational', 'financial', 'competitive']
                },
                'is_active': True,
                'onboarding_completed': True
            },

            # 2. Manufacturing - Garment exporter
            {
                'company_id': 'manufacturing_001',
                'company_name': 'Lanka Garment Industries Ltd',
                'display_name': 'LGI Apparel',
                'industry': 'manufacturing',
                'sub_industry': 'textiles_garments',
                'business_scale': 'large',
                'description': 'Export-oriented garment manufacturer serving international brands',
                'business_model': 'B2B',
                'annual_revenue': Decimal('8200000000'),  # LKR 8.2B
                'revenue_currency': 'LKR',
                'cash_reserves': Decimal('950000000'),
                'debt_level': 'high',
                'employee_count': 4200,
                'locations': ['Katunayake', 'Biyagama', 'Koggala'],
                'primary_location': 'Katunayake',
                'supply_chain_profile': {
                    'import_dependency': 0.85,
                    'key_suppliers': ['China Textiles', 'India Cotton Export', 'Bangladesh Fabrics'],
                    'supplier_concentration': 'high',
                    'average_lead_time_days': 45
                },
                'operational_dependencies': {
                    'power_dependency': 'critical',
                    'transport_dependency': 'critical',
                    'workforce_dependency': 'critical',
                    'digital_dependency': 'medium'
                },
                'market_position': 'follower',
                'market_share_percentage': Decimal('12.0'),
                'key_competitors': ['Brandix', 'MAS Holdings', 'Hirdaramani'],
                'geographic_exposure': {
                    'regions': ['Western'],
                    'concentration': 'concentrated',
                    'export_percentage': 0.95
                },
                'risk_tolerance': 'conservative',
                'vulnerability_factors': {
                    'currency_exposure': 'critical',
                    'regulatory_exposure': 'high',
                    'commodity_price_sensitivity': 'high',
                    'seasonality_impact': 'medium'
                },
                'strategic_priorities': ['cost_reduction', 'quality_improvement', 'client_retention'],
                'growth_stage': 'mature',
                'ownership_type': 'private',
                'is_active': True,
                'onboarding_completed': True
            },

            # 3. Logistics - Transport company
            {
                'company_id': 'logistics_001',
                'company_name': 'Swift Logistics Lanka',
                'display_name': 'Swift Logistics',
                'industry': 'logistics',
                'sub_industry': 'freight_transport',
                'business_scale': 'medium',
                'description': 'Nationwide logistics and freight forwarding services',
                'business_model': 'B2B',
                'annual_revenue': Decimal('1800000000'),
                'revenue_currency': 'LKR',
                'cash_reserves': Decimal('220000000'),
                'debt_level': 'moderate',
                'employee_count': 450,
                'locations': ['Colombo', 'Galle', 'Jaffna', 'Trincomalee'],
                'primary_location': 'Colombo',
                'supply_chain_profile': {
                    'import_dependency': 0.15,
                    'key_suppliers': ['Fuel Corp', 'Vehicle Parts Ltd'],
                    'supplier_concentration': 'low',
                    'average_lead_time_days': 7
                },
                'operational_dependencies': {
                    'power_dependency': 'low',
                    'transport_dependency': 'critical',
                    'workforce_dependency': 'high',
                    'digital_dependency': 'high'
                },
                'market_position': 'challenger',
                'market_share_percentage': Decimal('8.5'),
                'key_competitors': ['Hayleys', 'Expolanka', 'John Keells Logistics'],
                'geographic_exposure': {
                    'regions': ['Western', 'Southern', 'Northern', 'Eastern'],
                    'concentration': 'diversified',
                    'export_percentage': 0.0
                },
                'risk_tolerance': 'moderate',
                'vulnerability_factors': {
                    'currency_exposure': 'medium',
                    'regulatory_exposure': 'medium',
                    'commodity_price_sensitivity': 'critical',  # Fuel prices
                    'seasonality_impact': 'low'
                },
                'strategic_priorities': ['route_optimization', 'fleet_expansion', 'technology_adoption'],
                'growth_stage': 'growth',
                'ownership_type': 'private',
                'is_active': True,
                'onboarding_completed': True
            },

            # 4. Hospitality - Beach resort
            {
                'company_id': 'hospitality_001',
                'company_name': 'Paradise Beach Resorts',
                'display_name': 'Paradise Resorts',
                'industry': 'hospitality',
                'sub_industry': 'hotels_resorts',
                'business_scale': 'medium',
                'description': '4-star beach resort with 120 rooms in Bentota',
                'business_model': 'B2C',
                'annual_revenue': Decimal('950000000'),
                'revenue_currency': 'LKR',
                'cash_reserves': Decimal('85000000'),
                'debt_level': 'high',
                'employee_count': 180,
                'locations': ['Bentota'],
                'primary_location': 'Bentota',
                'supply_chain_profile': {
                    'import_dependency': 0.3,
                    'key_suppliers': ['Local Food Suppliers', 'Beverage Distributors', 'Linen Services'],
                    'supplier_concentration': 'low',
                    'average_lead_time_days': 3
                },
                'operational_dependencies': {
                    'power_dependency': 'critical',
                    'transport_dependency': 'medium',
                    'workforce_dependency': 'high',
                    'digital_dependency': 'medium'
                },
                'market_position': 'niche',
                'market_share_percentage': Decimal('2.5'),
                'key_competitors': ['Cinnamon Hotels', 'Jetwing', 'Aitken Spence Hotels'],
                'geographic_exposure': {
                    'regions': ['Southern'],
                    'concentration': 'concentrated',
                    'export_percentage': 0.0  # Foreign revenue but not "export"
                },
                'risk_tolerance': 'aggressive',
                'vulnerability_factors': {
                    'currency_exposure': 'medium',  # Foreign tourists
                    'regulatory_exposure': 'medium',
                    'commodity_price_sensitivity': 'medium',
                    'seasonality_impact': 'critical'  # Tourism seasonality
                },
                'strategic_priorities': ['occupancy_improvement', 'brand_building', 'service_excellence'],
                'growth_stage': 'mature',
                'ownership_type': 'family_business',
                'is_active': True,
                'onboarding_completed': True
            },

            # 5. Technology - Software company
            {
                'company_id': 'technology_001',
                'company_name': 'CodeCraft Solutions',
                'display_name': 'CodeCraft',
                'industry': 'technology',
                'sub_industry': 'software_development',
                'business_scale': 'small',
                'description': 'Software development and IT consulting for international clients',
                'business_model': 'B2B',
                'annual_revenue': Decimal('380000000'),
                'revenue_currency': 'LKR',
                'cash_reserves': Decimal('65000000'),
                'debt_level': 'low',
                'employee_count': 65,
                'locations': ['Colombo'],
                'primary_location': 'Colombo',
                'supply_chain_profile': {
                    'import_dependency': 0.05,
                    'key_suppliers': ['Cloud Providers', 'Software Licenses'],
                    'supplier_concentration': 'low',
                    'average_lead_time_days': 1
                },
                'operational_dependencies': {
                    'power_dependency': 'high',
                    'transport_dependency': 'low',
                    'workforce_dependency': 'critical',
                    'digital_dependency': 'critical'
                },
                'market_position': 'niche',
                'market_share_percentage': Decimal('0.8'),
                'key_competitors': ['99X Technology', 'Virtusa', 'WSO2'],
                'geographic_exposure': {
                    'regions': ['Western'],
                    'concentration': 'concentrated',
                    'export_percentage': 0.90  # Service exports
                },
                'risk_tolerance': 'aggressive',
                'vulnerability_factors': {
                    'currency_exposure': 'low',  # Earns foreign currency
                    'regulatory_exposure': 'low',
                    'commodity_price_sensitivity': 'low',
                    'seasonality_impact': 'low'
                },
                'strategic_priorities': ['talent_acquisition', 'innovation', 'client_diversification'],
                'growth_stage': 'growth',
                'ownership_type': 'private',
                'is_active': True,
                'onboarding_completed': True
            },

            # 6. Agriculture - Tea plantation
            {
                'company_id': 'agriculture_001',
                'company_name': 'Highland Tea Estates',
                'display_name': 'Highland Tea',
                'industry': 'agriculture',
                'sub_industry': 'tea_cultivation',
                'business_scale': 'medium',
                'description': 'Tea cultivation and processing for export markets',
                'business_model': 'B2B',
                'annual_revenue': Decimal('1250000000'),
                'revenue_currency': 'LKR',
                'cash_reserves': Decimal('155000000'),
                'debt_level': 'moderate',
                'employee_count': 850,
                'locations': ['Nuwara Eliya', 'Badulla'],
                'primary_location': 'Nuwara Eliya',
                'supply_chain_profile': {
                    'import_dependency': 0.25,
                    'key_suppliers': ['Fertilizer Imports', 'Machinery Parts'],
                    'supplier_concentration': 'medium',
                    'average_lead_time_days': 30
                },
                'operational_dependencies': {
                    'power_dependency': 'medium',
                    'transport_dependency': 'high',
                    'workforce_dependency': 'critical',
                    'digital_dependency': 'low'
                },
                'market_position': 'follower',
                'market_share_percentage': Decimal('5.2'),
                'key_competitors': ['Dilmah', 'Watawala Plantations', 'Bogawantalawa'],
                'geographic_exposure': {
                    'regions': ['Central'],
                    'concentration': 'concentrated',
                    'export_percentage': 0.75
                },
                'risk_tolerance': 'conservative',
                'vulnerability_factors': {
                    'currency_exposure': 'medium',
                    'regulatory_exposure': 'high',
                    'commodity_price_sensitivity': 'high',
                    'seasonality_impact': 'critical'  # Weather dependent
                },
                'strategic_priorities': ['yield_improvement', 'sustainability', 'brand_development'],
                'growth_stage': 'mature',
                'ownership_type': 'public',
                'is_active': True,
                'onboarding_completed': True
            },

            # 7-10: Add more companies...
            # (Continuing with smaller examples for brevity)

            {
                'company_id': 'retail_002',
                'company_name': 'Fashion Hub Lanka',
                'industry': 'retail',
                'sub_industry': 'apparel_retail',
                'business_scale': 'small',
                'annual_revenue': Decimal('285000000'),
                'employee_count': 35,
                'locations': ['Colombo'],
                'primary_location': 'Colombo',
                'is_active': True,
                'onboarding_completed': True
            },

            {
                'company_id': 'manufacturing_002',
                'company_name': 'Ceylon Ceramics Ltd',
                'industry': 'manufacturing',
                'sub_industry': 'ceramics',
                'business_scale': 'medium',
                'annual_revenue': Decimal('1650000000'),
                'employee_count': 520,
                'locations': ['Piliyandala', 'Ratnapura'],
                'primary_location': 'Piliyandala',
                'is_active': True,
                'onboarding_completed': True
            },

            {
                'company_id': 'hospitality_002',
                'company_name': 'City Business Hotel',
                'industry': 'hospitality',
                'sub_industry': 'business_hotels',
                'business_scale': 'small',
                'annual_revenue': Decimal('420000000'),
                'employee_count': 55,
                'locations': ['Colombo'],
                'primary_location': 'Colombo',
                'is_active': True,
                'onboarding_completed': True
            },

            {
                'company_id': 'technology_002',
                'company_name': 'DataTech Analytics',
                'industry': 'technology',
                'sub_industry': 'data_analytics',
                'business_scale': 'small',
                'annual_revenue': Decimal('195000000'),
                'employee_count': 28,
                'locations': ['Colombo'],
                'primary_location': 'Colombo',
                'is_active': True,
                'onboarding_completed': True
            },
        ]

        return companies

    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all mock companies"""
        return self.companies

    def get_company_by_id(self, company_id: str) -> Dict[str, Any]:
        """Get a specific company by ID"""
        for company in self.companies:
            if company['company_id'] == company_id:
                return company
        raise ValueError(f"Company {company_id} not found")

    def get_companies_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get all companies in an industry"""
        return [c for c in self.companies if c['industry'] == industry]

    def get_companies_by_scale(self, business_scale: str) -> List[Dict[str, Any]]:
        """Get all companies of a certain scale"""
        return [c for c in self.companies if c.get('business_scale') == business_scale]
