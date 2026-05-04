"""
Mock Historical Patterns Generator

Creates historical risk/opportunity patterns for pattern-based detection
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random


class MockHistoricalPatterns:
    """Generate historical patterns for pattern-based risk detection"""

    def __init__(self):
        self.patterns = self._create_patterns()

    def _create_patterns(self) -> List[Dict[str, Any]]:
        """Create 10+ historical patterns"""

        patterns = [
            # Pattern 1: Fuel Crisis 2022
            {
                'pattern_id': 'fuel_crisis_2022',
                'pattern_name': 'Fuel Crisis 2022',
                'event_date': datetime(2022, 5, 15),
                'duration_days': 45,
                'severity': 'critical',
                'description': 'Nationwide fuel shortage causing transport disruptions',

                'indicator_profile': {
                    'OPS_FUEL_AVAIL': 35,
                    'OPS_TRANSPORT_AVAIL': 42,
                    'OPS_LOGISTICS_COST': 28,
                    'OPS_ENERGY_COST': 25,
                    'OPS_COST_PRESSURE': 32,
                    'OPS_SUPPLY_CHAIN': 48,
                },

                'affected_industries': ['logistics', 'manufacturing', 'retail', 'hospitality'],

                'outcomes': {
                    'logistics': {
                        'revenue_impact': -0.35,  # -35%
                        'cost_increase': 0.45,  # +45%
                        'duration_days': 45,
                        'recovery_days': 20,
                        'bankruptcy_rate': 0.08
                    },
                    'manufacturing': {
                        'revenue_impact': -0.22,
                        'cost_increase': 0.30,
                        'duration_days': 40,
                        'recovery_days': 30,
                        'bankruptcy_rate': 0.03
                    },
                    'retail': {
                        'revenue_impact': -0.18,
                        'cost_increase': 0.25,
                        'duration_days': 35,
                        'recovery_days': 15,
                        'bankruptcy_rate': 0.02
                    },
                    'hospitality': {
                        'revenue_impact': -0.40,
                        'cost_increase': 0.35,
                        'duration_days': 50,
                        'recovery_days': 40,
                        'bankruptcy_rate': 0.12
                    }
                },

                'lessons_learned': [
                    'Companies with fuel reserves survived better',
                    'Alternative transport routes critical',
                    'Customer communication prevented panic',
                    'Price hedging protected margins'
                ]
            },

            # Pattern 2: Supply Chain Disruption 2021
            {
                'pattern_id': 'supply_chain_2021',
                'pattern_name': 'Import Restrictions 2021',
                'event_date': datetime(2021, 3, 10),
                'duration_days': 90,
                'severity': 'high',
                'description': 'Import restrictions causing raw material shortages',

                'indicator_profile': {
                    'OPS_SUPPLY_CHAIN': 45,
                    'OPS_IMPORT_FLOW': 38,
                    'OPS_RAW_MATERIAL_COST': 32,
                    'OPS_COST_PRESSURE': 40,
                    'OPS_PRODUCTION_CAPACITY': 52,
                },

                'affected_industries': ['manufacturing', 'retail'],

                'outcomes': {
                    'manufacturing': {
                        'revenue_impact': -0.30,
                        'cost_increase': 0.40,
                        'duration_days': 90,
                        'recovery_days': 60,
                        'bankruptcy_rate': 0.05
                    },
                    'retail': {
                        'revenue_impact': -0.25,
                        'cost_increase': 0.15,
                        'duration_days': 75,
                        'recovery_days': 30,
                        'bankruptcy_rate': 0.04
                    }
                },

                'lessons_learned': [
                    'Supplier diversification critical',
                    'Local sourcing alternatives valuable',
                    'Buffer stock investments paid off',
                    'Rapid product substitution helped'
                ]
            },

            # Pattern 3: Tourism Boom 2019
            {
                'pattern_id': 'tourism_boom_2019',
                'pattern_name': 'Tourism Record Year 2019',
                'event_date': datetime(2019, 1, 1),
                'duration_days': 120,
                'severity': 'positive',
                'description': 'Record tourist arrivals creating opportunities',

                'indicator_profile': {
                    'OPS_DEMAND_LEVEL': 88,
                    'OPS_PRICING_POWER': 82,
                    'OPS_CASH_FLOW': 85,
                    'OPS_CAPACITY_UTILIZATION': 92,
                },

                'affected_industries': ['hospitality', 'retail', 'logistics'],

                'outcomes': {
                    'hospitality': {
                        'revenue_impact': 0.45,  # +45%
                        'cost_increase': 0.12,
                        'duration_days': 120,
                        'market_share_gain': 0.05
                    },
                    'retail': {
                        'revenue_impact': 0.28,
                        'cost_increase': 0.08,
                        'duration_days': 100
                    },
                    'logistics': {
                        'revenue_impact': 0.22,
                        'cost_increase': 0.10,
                        'duration_days': 110
                    }
                },

                'lessons_learned': [
                    'Capacity expansion rewarded early movers',
                    'Premium pricing sustainable during peak',
                    'Staff training investments paid off',
                    'Marketing ROI exceptionally high'
                ]
            },

            # Pattern 4: Labor Shortage 2023
            {
                'pattern_id': 'labor_shortage_2023',
                'pattern_name': 'Skilled Labor Shortage 2023',
                'event_date': datetime(2023, 2, 1),
                'duration_days': 180,
                'severity': 'high',
                'description': 'Migration causing skilled worker shortage',

                'indicator_profile': {
                    'OPS_WORKFORCE_AVAIL': 45,
                    'OPS_LABOR_COST': 32,
                    'OPS_PRODUCTIVITY': 55,
                    'OPS_COST_PRESSURE': 42,
                },

                'affected_industries': ['manufacturing', 'hospitality', 'technology'],

                'outcomes': {
                    'manufacturing': {
                        'revenue_impact': -0.15,
                        'cost_increase': 0.25,
                        'duration_days': 180,
                        'productivity_drop': 0.18
                    },
                    'hospitality': {
                        'revenue_impact': -0.12,
                        'cost_increase': 0.20,
                        'duration_days': 150,
                        'service_quality_drop': 0.15
                    },
                    'technology': {
                        'revenue_impact': -0.08,
                        'cost_increase': 0.30,
                        'duration_days': 200,
                        'project_delays': 0.25
                    }
                },

                'lessons_learned': [
                    'Automation investments became critical',
                    'Remote work options retained talent',
                    'Training programs reduced impact',
                    'Wage increases necessary but manageable'
                ]
            },

            # Pattern 5: Power Outage Crisis 2023
            {
                'pattern_id': 'power_crisis_2023',
                'pattern_name': 'Rolling Power Cuts 2023',
                'event_date': datetime(2023, 7, 1),
                'duration_days': 60,
                'severity': 'critical',
                'description': 'Extended power cuts affecting operations',

                'indicator_profile': {
                    'OPS_POWER_RELIABILITY': 38,
                    'OPS_PRODUCTIVITY': 48,
                    'OPS_ENERGY_COST': 28,
                    'OPS_COST_PRESSURE': 35,
                },

                'affected_industries': ['manufacturing', 'hospitality', 'retail', 'technology'],

                'outcomes': {
                    'manufacturing': {
                        'revenue_impact': -0.28,
                        'cost_increase': 0.35,  # Generator costs
                        'duration_days': 60
                    },
                    'hospitality': {
                        'revenue_impact': -0.35,
                        'cost_increase': 0.40,
                        'duration_days': 60
                    },
                    'retail': {
                        'revenue_impact': -0.20,
                        'cost_increase': 0.25,
                        'duration_days': 55
                    },
                    'technology': {
                        'revenue_impact': -0.10,
                        'cost_increase': 0.15,
                        'duration_days': 50
                    }
                }
            },

            # Pattern 6: E-commerce Opportunity 2020
            {
                'pattern_id': 'ecommerce_surge_2020',
                'pattern_name': 'E-commerce Surge 2020',
                'event_date': datetime(2020, 4, 1),
                'duration_days': 365,
                'severity': 'positive',
                'description': 'Pandemic-driven digital transformation opportunity',

                'indicator_profile': {
                    'OPS_DEMAND_LEVEL': 85,
                    'OPS_DIGITAL_ENGAGEMENT': 92,
                    'OPS_PRICING_POWER': 75,
                },

                'affected_industries': ['retail', 'logistics', 'technology'],

                'outcomes': {
                    'retail': {
                        'revenue_impact': 0.40,
                        'market_share_gain': 0.08,
                        'duration_days': 365,
                        'customer_acquisition_cost': -0.20  # Decreased
                    },
                    'logistics': {
                        'revenue_impact': 0.55,
                        'market_share_gain': 0.12,
                        'duration_days': 365
                    },
                    'technology': {
                        'revenue_impact': 0.35,
                        'new_client_acquisition': 0.30,
                        'duration_days': 365
                    }
                }
            },

            # Pattern 7: Currency Devaluation 2022
            {
                'pattern_id': 'currency_crash_2022',
                'pattern_name': 'Currency Devaluation 2022',
                'event_date': datetime(2022, 3, 1),
                'duration_days': 120,
                'severity': 'critical',
                'description': 'Sharp currency devaluation impacting costs',

                'indicator_profile': {
                    'OPS_IMPORT_FLOW': 42,
                    'OPS_RAW_MATERIAL_COST': 25,
                    'OPS_COST_PRESSURE': 28,
                    'OPS_PRICING_POWER': 52,
                },

                'affected_industries': ['manufacturing', 'retail', 'hospitality'],

                'outcomes': {
                    'manufacturing': {
                        'revenue_impact': -0.25,
                        'cost_increase': 0.60,
                        'duration_days': 120,
                        'margin_compression': 0.45
                    }
                }
            },

            # Patterns 8-10: Additional patterns
            {
                'pattern_id': 'monsoon_disruption_2021',
                'pattern_name': 'Severe Monsoon Disruption 2021',
                'event_date': datetime(2021, 11, 1),
                'duration_days': 21,
                'severity': 'high',
                'affected_industries': ['agriculture', 'logistics', 'retail'],
            },

            {
                'pattern_id': 'competitor_exit_2020',
                'pattern_name': 'Major Competitor Exit 2020',
                'event_date': datetime(2020, 8, 1),
                'duration_days': 180,
                'severity': 'positive',
                'affected_industries': ['retail', 'hospitality'],
            },

            {
                'pattern_id': 'regulatory_change_2023',
                'pattern_name': 'New Compliance Requirements 2023',
                'event_date': datetime(2023, 1, 1),
                'duration_days': 90,
                'severity': 'medium',
                'affected_industries': ['manufacturing', 'retail', 'hospitality'],
            },
        ]

        return patterns

    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Get all historical patterns"""
        return self.patterns

    def get_pattern_by_id(self, pattern_id: str) -> Dict[str, Any]:
        """Get specific pattern by ID"""
        for pattern in self.patterns:
            if pattern['pattern_id'] == pattern_id:
                return pattern
        raise ValueError(f"Pattern {pattern_id} not found")

    def get_patterns_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get patterns relevant to an industry"""
        return [p for p in self.patterns if industry in p.get('affected_industries', [])]

    def find_similar_patterns(
        self,
        current_indicators: Dict[str, float],
        similarity_threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """Find historical patterns similar to current situation"""
        from math import sqrt

        similar_patterns = []

        for pattern in self.patterns:
            if 'indicator_profile' not in pattern:
                continue

            # Calculate cosine similarity
            pattern_profile = pattern['indicator_profile']

            # Get common indicators
            common_indicators = set(current_indicators.keys()) & set(pattern_profile.keys())

            if not common_indicators:
                continue

            # Calculate similarity
            dot_product = sum(
                current_indicators[ind] * pattern_profile[ind]
                for ind in common_indicators
            )

            current_magnitude = sqrt(sum(current_indicators[ind]**2 for ind in common_indicators))
            pattern_magnitude = sqrt(sum(pattern_profile[ind]**2 for ind in common_indicators))

            if current_magnitude == 0 or pattern_magnitude == 0:
                continue

            similarity = dot_product / (current_magnitude * pattern_magnitude)

            if similarity >= similarity_threshold:
                similar_patterns.append({
                    **pattern,
                    'similarity_score': similarity
                })

        # Sort by similarity
        similar_patterns.sort(key=lambda x: x['similarity_score'], reverse=True)

        return similar_patterns
