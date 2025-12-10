"""
Test Layer 2 -> Layer 3 Integration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


async def test_l2_to_l3():
    print('='*70)
    print('TESTING LAYER 2 -> LAYER 3 INTEGRATION')
    print('='*70)
    
    # Step 1: Get Layer 2 Output
    print('\n[1] Getting Layer 2 Output...')
    from app.layer2.pipeline_orchestrator import Layer2PipelineOrchestrator
    
    l2_orchestrator = Layer2PipelineOrchestrator()
    l2_result = await l2_orchestrator.run_full_pipeline(article_limit=50, store_results=False)
    
    if not l2_result.success or not l2_result.layer2_output:
        print('   ERROR: Layer 2 failed')
        return
    
    l2_output = l2_result.layer2_output
    print(f'   Layer 2 Output: {len(l2_output.indicators)} indicators')
    print(f'   Activity Level: {l2_output.activity_level:.1f}')
    print(f'   Sentiment: {l2_output.overall_sentiment:.3f}')
    
    # Step 2: Transform to Layer 3
    print('\n[2] Transforming to Layer 3 format...')
    from app.integration.pipeline import IntegrationPipeline
    from app.integration.contracts import validate_layer2_output
    
    pipeline = IntegrationPipeline()
    
    # Test company profile
    company_profile = {
        'company_id': 'test_retail_001',
        'company_name': 'Test Retail Co',
        'industry': 'retail',
        'size': 'medium'
    }
    
    # Validate L2 output first
    l2_validated = validate_layer2_output(l2_output.model_dump())
    print('   L2 validated successfully')
    
    # Step 3: Simulate Layer 3 processing
    print('\n[3] Running Layer 3 simulation...')
    l3_result = pipeline._simulate_layer3(l2_validated, company_profile)
    
    print('   Layer 3 Result:')
    print(f'   - Company: {l3_result.get("company_name")}')
    print(f'   - Industry: {l3_result.get("industry")}')
    print(f'   - Overall Health: {l3_result.get("overall_operational_health", 0):.1f}')
    print(f'   - Supply Chain Health: {l3_result.get("supply_chain_health", 0):.1f}')
    print(f'   - Workforce Health: {l3_result.get("workforce_health", 0):.1f}')
    print(f'   - Infrastructure Health: {l3_result.get("infrastructure_health", 0):.1f}')
    print(f'   - Cost Pressure: {l3_result.get("cost_pressure", 0):.1f}')
    print(f'   - Critical Issues: {l3_result.get("critical_issues", [])}')
    
    # Step 4: Show operational indicators
    print('\n[4] Operational Indicators:')
    for code, ind in l3_result.get('indicators', {}).items():
        print(f'   {code}: {ind["value"]:.1f} ({ind["trend"]})')
    
    # Step 5: Test with different industries
    print('\n[5] Testing across different industries...')
    industries = ['retail', 'manufacturing', 'logistics', 'technology', 'healthcare']
    
    for industry in industries:
        profile = {
            'company_id': f'test_{industry}_001',
            'company_name': f'Test {industry.title()} Co',
            'industry': industry,
            'size': 'medium'
        }
        
        l3 = pipeline._simulate_layer3(l2_validated, profile)
        print(f'   {industry.title():15} -> Overall Health: {l3.get("overall_operational_health", 0):.1f}')
    
    print('\n' + '='*70)
    print('L2 -> L3 INTEGRATION SUCCESSFUL!')
    print('='*70)


if __name__ == "__main__":
    asyncio.run(test_l2_to_l3())
