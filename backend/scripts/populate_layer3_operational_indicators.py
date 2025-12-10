"""
Populate Layer 3 Operational Indicators in MongoDB

This script:
1. Runs Layer 2 pipeline to get national indicators
2. Transforms to Layer 3 operational indicators for test companies
3. Stores operational calculations in MongoDB
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.layer2.pipeline_orchestrator import Layer2PipelineOrchestrator
from app.integration.pipeline import IntegrationPipeline
from app.integration.contracts import validate_layer2_output


async def populate_operational_indicators():
    print('='*70)
    print('POPULATING LAYER 3 OPERATIONAL INDICATORS')
    print('='*70)

    # Connect to MongoDB
    client = MongoClient(settings.MONGODB_URL)
    db = client['national_indicator']

    # Clear existing data
    print('\n[1] Clearing existing operational calculations...')
    db.operational_calculations.delete_many({})
    db.operational_recommendations.delete_many({})
    print('   ✅ Cleared')

    # Run Layer 2 pipeline
    print('\n[2] Running Layer 2 pipeline...')
    l2_orchestrator = Layer2PipelineOrchestrator()
    l2_result = await l2_orchestrator.run_full_pipeline(article_limit=50, store_results=False)

    if not l2_result.success or not l2_result.layer2_output:
        print('   ❌ Layer 2 failed')
        return

    l2_output = l2_result.layer2_output
    print(f'   ✅ Generated {len(l2_output.indicators)} indicators')

    # Validate L2 output
    l2_validated = validate_layer2_output(l2_output.model_dump())

    # Integration pipeline
    pipeline = IntegrationPipeline()

    # Test companies
    test_companies = [
        {
            'company_id': 'retail_001',
            'company_name': 'ABC Retail Chain',
            'industry': 'retail',
            'size': 'large'
        },
        {
            'company_id': 'manufacturing_001',
            'company_name': 'XYZ Manufacturing',
            'industry': 'manufacturing',
            'size': 'medium'
        },
        {
            'company_id': 'tech_001',
            'company_name': 'TechStar Solutions',
            'industry': 'technology',
            'size': 'medium'
        },
        {
            'company_id': 'logistics_001',
            'company_name': 'FastMove Logistics',
            'industry': 'logistics',
            'size': 'small'
        }
    ]

    print('\n[3] Generating operational indicators for companies...')
    total_stored = 0

    for company in test_companies:
        print(f'\n   Processing: {company["company_name"]}')

        # Simulate Layer 3
        l3_result = pipeline._simulate_layer3(l2_validated, company)

        # Store operational indicators in MongoDB
        indicators = l3_result.get('indicators', {})

        for indicator_code, indicator_data in indicators.items():
            # Create operational calculation document
            calculation_doc = {
                'company_id': company['company_id'],
                'operational_indicator_code': indicator_code,
                'calculation_timestamp': datetime.utcnow(),
                'calculation_details': {
                    'method': 'layer2_transformation',
                    'inputs': indicator_data.get('contributing_factors', []),
                    'base_calculation': indicator_data['value'],
                    'adjustments': [],
                    'final_value': indicator_data['value'],
                    'rounded_value': round(indicator_data['value'], 2),
                    'confidence': indicator_data.get('confidence', 0.8)
                },
                'context': {
                    'industry_average': 50.0,
                    'deviation_from_average': indicator_data['value'] - 50.0,
                    'trend_direction': indicator_data.get('trend', 'stable'),
                    'compared_to_yesterday': 0.0
                },
                'interpretation': {
                    'level': 'normal' if 40 <= indicator_data['value'] <= 60 else 'high' if indicator_data['value'] > 60 else 'low',
                    'severity_score': abs(indicator_data['value'] - 50) / 5,
                    'status_label': 'healthy' if 40 <= indicator_data['value'] <= 60 else 'attention_needed',
                    'requires_attention': indicator_data['value'] < 30 or indicator_data['value'] > 70
                }
            }

            db.operational_calculations.insert_one(calculation_doc)
            total_stored += 1

        print(f'      ✅ Stored {len(indicators)} operational indicators')
        print(f'      Overall Health: {l3_result.get("overall_operational_health", 0):.1f}')

    # Verify storage
    print('\n[4] Verifying stored data...')
    count = db.operational_calculations.count_documents({})
    print(f'   Total operational calculations: {count}')

    companies_with_data = db.operational_calculations.distinct('company_id')
    print(f'   Companies with data: {companies_with_data}')

    # Sample data
    print('\n[5] Sample operational indicators:')
    for company_id in companies_with_data[:2]:
        indicators = list(db.operational_calculations.find({'company_id': company_id}).limit(3))
        print(f'\n   {company_id}:')
        for ind in indicators:
            code = ind['operational_indicator_code']
            value = ind['calculation_details']['final_value']
            print(f'      - {code}: {value:.1f}')

    client.close()

    print('\n' + '='*70)
    print(f'✅ SUCCESSFULLY STORED {total_stored} OPERATIONAL INDICATORS!')
    print('='*70)
    print('\nData is now accessible via:')
    print('  - /api/v1/user/operational-indicators')
    print('  - /api/v1/admin/indicators/operational/{company_id}')
    print('\nRefresh your dashboard to see the operational indicators!')


if __name__ == "__main__":
    asyncio.run(populate_operational_indicators())
