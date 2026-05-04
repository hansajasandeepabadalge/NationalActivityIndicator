"""
Mock Competitive Intelligence Generator

Creates mock competitive intelligence for opportunity detection
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from decimal import Decimal
import random


class MockCompetitiveIntelligence:
    """Generate mock competitive intelligence data"""

    def __init__(self):
        self.intel_items = self._create_intel()

    def _create_intel(self) -> List[Dict[str, Any]]:
        """Create mock competitive intelligence items"""

        base_date = datetime.now()

        intel = [
            # Retail sector intelligence
            {
                'intel_id': 'intel_001',
                'company_id': 'retail_001',  # Ceylon SuperMart
                'competitor_name': 'QuickMart Express',
                'competitor_industry': 'retail',
                'intel_type': 'weakness',
                'description': 'QuickMart experiencing supply chain issues, delayed deliveries to 15 outlets',
                'source': 'Industry contacts, social media monitoring',
                'confidence_level': Decimal('0.85'),
                'relevance_score': Decimal('0.90'),
                'potential_opportunity': 'Market share capture - customers switching due to stock shortages',
                'suggested_response': 'Increase stock levels, targeted marketing in QuickMart areas, offer delivery guarantee',
                'status': 'new',
                'detected_at': base_date - timedelta(days=2),
                'expires_at': base_date + timedelta(days=14)
            },

            {
                'intel_id': 'intel_002',
                'company_id': 'retail_001',
                'competitor_name': 'Metro Foods',
                'competitor_industry': 'retail',
                'intel_type': 'movement',
                'description': 'Metro Foods launching new loyalty program with aggressive cashback offers',
                'source': 'Public announcement, market research',
                'confidence_level': Decimal('0.95'),
                'relevance_score': Decimal('0.85'),
                'potential_opportunity': 'Counter with enhanced loyalty benefits, prevent customer migration',
                'suggested_response': 'Review loyalty program competitiveness, consider matching or exceeding benefits',
                'status': 'monitoring',
                'detected_at': base_date - timedelta(days=5),
                'expires_at': base_date + timedelta(days=30)
            },

            # Manufacturing sector intelligence
            {
                'intel_id': 'intel_003',
                'company_id': 'manufacturing_001',  # Lanka Garment
                'competitor_name': 'CompetitorGarments Ltd',
                'competitor_industry': 'manufacturing',
                'intel_type': 'vulnerability',
                'description': 'Major competitor lost 2 key clients due to quality issues',
                'source': 'Industry sources, buyer feedback',
                'confidence_level': Decimal('0.80'),
                'relevance_score': Decimal('0.95'),
                'potential_opportunity': 'Capture displaced orders, emphasize quality assurance',
                'suggested_response': 'Contact affected buyers immediately, showcase quality certifications, offer competitive pricing',
                'status': 'new',
                'detected_at': base_date - timedelta(days=1),
                'expires_at': base_date + timedelta(days=21)
            },

            {
                'intel_id': 'intel_004',
                'company_id': 'manufacturing_001',
                'competitor_name': 'Brandix Lanka',
                'competitor_industry': 'manufacturing',
                'intel_type': 'strength',
                'description': 'Brandix secured major sustainability certification, attracting eco-conscious brands',
                'source': 'Public announcement, buyer inquiries',
                'confidence_level': Decimal('0.90'),
                'relevance_score': Decimal('0.75'),
                'potential_opportunity': 'Invest in sustainability certifications to remain competitive',
                'suggested_response': 'Accelerate sustainability initiatives, pursue relevant certifications',
                'status': 'monitoring',
                'detected_at': base_date - timedelta(days=7),
                'expires_at': base_date + timedelta(days=60)
            },

            # Logistics sector intelligence
            {
                'intel_id': 'intel_005',
                'company_id': 'logistics_001',  # Swift Logistics
                'competitor_name': 'Expolanka Holdings',
                'competitor_industry': 'logistics',
                'intel_type': 'weakness',
                'description': 'Expolanka facing driver shortage, service delays on northern routes',
                'source': 'Client complaints, driver network',
                'confidence_level': Decimal('0.78'),
                'relevance_score': Decimal('0.88'),
                'potential_opportunity': 'Capture market share on northern routes, emphasize reliability',
                'suggested_response': 'Target Expolanka clients with reliability message, ensure northern route capacity',
                'status': 'new',
                'detected_at': base_date - timedelta(days=3),
                'expires_at': base_date + timedelta(days=20)
            },

            # Hospitality sector intelligence
            {
                'intel_id': 'intel_006',
                'company_id': 'hospitality_001',  # Paradise Resorts
                'competitor_name': 'Beachside Luxury Resort',
                'competitor_industry': 'hospitality',
                'intel_type': 'weakness',
                'description': 'Competitor resort closed for renovations for 6 weeks during peak season',
                'source': 'Public notification, travel agents',
                'confidence_level': Decimal('1.00'),
                'relevance_score': Decimal('0.95'),
                'potential_opportunity': 'Capture displaced bookings, intensive marketing to their customer base',
                'suggested_response': 'Aggressive booking promotions, contact travel agents, offer transition incentives',
                'status': 'acted_on',
                'detected_at': base_date - timedelta(days=10),
                'expires_at': base_date + timedelta(days=30)
            },

            {
                'intel_id': 'intel_007',
                'company_id': 'hospitality_001',
                'competitor_name': 'Cinnamon Hotels',
                'competitor_industry': 'hospitality',
                'intel_type': 'movement',
                'description': 'Cinnamon launching new all-inclusive package at aggressive pricing',
                'source': 'Marketing materials, booking platforms',
                'confidence_level': Decimal('0.92'),
                'relevance_score': Decimal('0.82'),
                'potential_opportunity': 'Differentiate with unique experiences vs price competition',
                'suggested_response': 'Emphasize boutique experience, personalized service, unique local experiences',
                'status': 'monitoring',
                'detected_at': base_date - timedelta(days=4),
                'expires_at': base_date + timedelta(days=45)
            },

            # Technology sector intelligence
            {
                'intel_id': 'intel_008',
                'company_id': 'technology_001',  # CodeCraft
                'competitor_name': '99X Technology',
                'competitor_industry': 'technology',
                'intel_type': 'vulnerability',
                'description': '99X lost senior developers to overseas opportunities, project delivery issues',
                'source': 'Professional networks, ex-employees',
                'confidence_level': Decimal('0.75'),
                'relevance_score': Decimal('0.88'),
                'potential_opportunity': 'Approach their clients with delivery assurance, recruit available talent',
                'suggested_response': 'Reach out to 99X clients, emphasize team stability, offer competitive talent packages',
                'status': 'new',
                'detected_at': base_date - timedelta(days=1),
                'expires_at': base_date + timedelta(days=25)
            },

            # Cross-industry intelligence
            {
                'intel_id': 'intel_009',
                'company_id': 'retail_001',
                'competitor_name': 'Regional Supermarket Chain',
                'competitor_industry': 'retail',
                'intel_type': 'movement',
                'description': 'Competitor expanding to online delivery, investing heavily in logistics',
                'source': 'Job postings, vendor discussions',
                'confidence_level': Decimal('0.88'),
                'relevance_score': Decimal('0.80'),
                'potential_opportunity': 'Accelerate own digital strategy or risk losing online market',
                'suggested_response': 'Evaluate digital capabilities, consider partnership or rapid development',
                'status': 'monitoring',
                'detected_at': base_date - timedelta(days=6),
                'expires_at': base_date + timedelta(days=90)
            },

            {
                'intel_id': 'intel_010',
                'company_id': 'manufacturing_001',
                'competitor_name': 'Foreign Garment Manufacturer',
                'competitor_industry': 'manufacturing',
                'intel_type': 'weakness',
                'description': 'Bangladesh competitor facing labor unrest, production disruptions',
                'source': 'Industry news, buyer communications',
                'confidence_level': Decimal('0.82'),
                'relevance_score': Decimal('0.85'),
                'potential_opportunity': 'Position as stable alternative, capture emergency orders',
                'suggested_response': 'Proactive outreach to buyers, highlight operational stability, offer quick turnaround',
                'status': 'new',
                'detected_at': base_date - timedelta(days=2),
                'expires_at': base_date + timedelta(days=30)
            },
        ]

        return intel

    def get_all_intelligence(self) -> List[Dict[str, Any]]:
        """Get all intelligence items"""
        return self.intel_items

    def get_intelligence_for_company(self, company_id: str) -> List[Dict[str, Any]]:
        """Get intelligence relevant to a specific company"""
        return [item for item in self.intel_items if item['company_id'] == company_id]

    def get_intelligence_by_type(self, intel_type: str) -> List[Dict[str, Any]]:
        """Get intelligence by type (weakness, strength, movement, vulnerability)"""
        return [item for item in self.intel_items if item['intel_type'] == intel_type]

    def get_active_intelligence(self) -> List[Dict[str, Any]]:
        """Get non-expired intelligence"""
        now = datetime.now()
        return [
            item for item in self.intel_items
            if item.get('expires_at') and item['expires_at'] > now
        ]

    def get_actionable_intelligence(self, company_id: str) -> List[Dict[str, Any]]:
        """Get high-relevance, active intelligence for a company"""
        now = datetime.now()
        return [
            item for item in self.intel_items
            if item['company_id'] == company_id
            and item.get('expires_at') and item['expires_at'] > now
            and item.get('relevance_score', 0) >= Decimal('0.75')
            and item.get('status') in ['new', 'monitoring']
        ]

    def generate_random_intel(
        self,
        company_id: str,
        competitor_name: str,
        industry: str
    ) -> Dict[str, Any]:
        """Generate random intelligence item"""

        intel_types = ['weakness', 'strength', 'movement', 'vulnerability']
        intel_type = random.choice(intel_types)

        descriptions = {
            'weakness': [
                f'{competitor_name} experiencing operational challenges',
                f'{competitor_name} facing customer service complaints',
                f'{competitor_name} reported supply issues',
            ],
            'strength': [
                f'{competitor_name} launched innovative product line',
                f'{competitor_name} secured major partnership',
                f'{competitor_name} expanded market presence',
            ],
            'movement': [
                f'{competitor_name} entering new market segment',
                f'{competitor_name} rebranding initiative underway',
                f'{competitor_name} pricing strategy change',
            ],
            'vulnerability': [
                f'{competitor_name} leadership transition creating uncertainty',
                f'{competitor_name} facing financial pressure',
                f'{competitor_name} losing key personnel',
            ]
        }

        return {
            'company_id': company_id,
            'competitor_name': competitor_name,
            'competitor_industry': industry,
            'intel_type': intel_type,
            'description': random.choice(descriptions[intel_type]),
            'source': 'Market intelligence',
            'confidence_level': Decimal(str(round(random.uniform(0.6, 0.95), 2))),
            'relevance_score': Decimal(str(round(random.uniform(0.5, 0.90), 2))),
            'status': 'new',
            'detected_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=random.randint(15, 60))
        }
