"""
Test Full Pipeline: Layer 2 -> Layer 3 -> Layer 4
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


async def test_full_pipeline():
    print('='*70)
    print('TESTING FULL PIPELINE: L2 -> L3 -> L4')
    print('='*70)
    
    # Step 1: Get Layer 2 Output
    print('\n[1] Running Layer 2 Pipeline (100 articles)...')
    from app.layer2.pipeline_orchestrator import Layer2PipelineOrchestrator
    
    l2_orchestrator = Layer2PipelineOrchestrator()
    l2_result = await l2_orchestrator.run_full_pipeline(article_limit=100, store_results=False)
    
    if not l2_result.success or not l2_result.layer2_output:
        print('   ERROR: Layer 2 failed')
        return
    
    l2_output = l2_result.layer2_output
    print(f'   ✅ Layer 2 Complete:')
    print(f'      - Indicators: {len(l2_output.indicators)}')
    print(f'      - Activity Level: {l2_output.activity_level:.1f}')
    print(f'      - Sentiment: {l2_output.overall_sentiment:.3f}')
    
    # Step 2: Run through Integration Pipeline
    print('\n[2] Running Integration Pipeline (L2->L3->L4)...')
    from app.integration.pipeline import IntegrationPipeline
    
    pipeline = IntegrationPipeline()
    
    # Test company profile
    company_profile = {
        'company_id': 'test_retail_001',
        'company_name': 'ABC Retail Chain',
        'industry': 'retail',
        'size': 'large',
        'region': 'Western Province',
        'supply_chain': {
            'import_dependency': 0.6,
            'local_sourcing': 0.4
        },
        'critical_dependencies': {
            'fuel': 'high',
            'power': 'high',
            'transport_access': 'high'
        }
    }
    
    result = await pipeline.run_full_pipeline(
        company_profile=company_profile,
        layer2_input=l2_output.model_dump()
    )
    
    if not result.get('success'):
        print(f'   ERROR: Pipeline failed - {result.get("error")}')
        return
    
    # Step 3: Analyze Layer 3 Output
    print('\n[3] Layer 3 Operational Indicators:')
    l3_output = result.get('layer3_output', {})
    
    print(f'   Company: {l3_output.get("company_name")}')
    print(f'   Industry: {l3_output.get("industry")}')
    print(f'   Overall Health: {l3_output.get("overall_operational_health", 0):.1f}/100')
    
    print('\n   Category Health Scores:')
    categories = [
        ('supply_chain_health', 'Supply Chain'),
        ('workforce_health', 'Workforce'),
        ('infrastructure_health', 'Infrastructure'),
        ('cost_pressure', 'Cost Pressure'),
        ('market_conditions', 'Market Conditions'),
        ('financial_health', 'Financial'),
        ('regulatory_burden', 'Regulatory Burden')
    ]
    
    for key, name in categories:
        value = l3_output.get(key, 50)
        bar = '█' * int(value / 5) + '░' * (20 - int(value / 5))
        print(f'   {name:20} [{bar}] {value:.1f}')
    
    critical = l3_output.get('critical_issues', [])
    if critical:
        print(f'\n   ⚠️  Critical Issues: {critical}')
    else:
        print(f'\n   ✅ No critical issues detected')
    
    # Step 4: Analyze Layer 4 Output
    print('\n[4] Layer 4 Business Insights:')
    l4_output = result.get('layer4_output', {})
    
    if l4_output:
        # Check if LLM enhanced
        summary = l4_output.get('summary', {})
        llm_enhanced = summary.get('llm_enhanced', False)
        source = l4_output.get('source', 'unknown')
        if llm_enhanced or 'llm' in source:
            print('   🤖 LLM-Enhanced Insights (Groq Llama 3.3 70B)')
        else:
            print('   📋 Rule-Based Insights')
        
        # Risks
        risks = l4_output.get('risks', [])
        print(f'\n   Detected Risks: {len(risks)}')
        for risk in risks[:5]:
            severity = risk.get('severity_level', risk.get('severity', 'unknown'))
            desc = risk.get('description', risk.get('title', risk.get('risk_type', 'Unknown risk')))[:60]
            print(f'   - [{severity.upper()}] {desc}')
        
        # Opportunities  
        opportunities = l4_output.get('opportunities', [])
        print(f'\n   Detected Opportunities: {len(opportunities)}')
        for opp in opportunities[:5]:
            priority = opp.get('priority_level', opp.get('impact_level', opp.get('impact', 'medium')))
            desc = opp.get('description', opp.get('title', opp.get('opportunity_type', 'Unknown')))[:60]
            print(f'   - [{str(priority).upper()}] {desc}')
        
        # Recommendations
        recommendations = l4_output.get('recommendations', [])
        print(f'\n   Recommendations: {len(recommendations)}')
        for rec in recommendations[:5]:
            priority = rec.get('priority', 'medium')
            if isinstance(priority, int):
                priority_labels = {1: 'HIGH', 2: 'HIGH', 3: 'MEDIUM', 4: 'MEDIUM', 5: 'LOW'}
                priority_str = priority_labels.get(priority, 'MEDIUM')
            else:
                priority_str = str(priority).upper()
            # Try different field names for the action text
            action = rec.get('action_title') or rec.get('action') or rec.get('action_description') or rec.get('recommendation', 'No action')
            if action:
                action = str(action)[:60]
            else:
                action = 'No action'
            print(f'   - [{priority_str}] {action}')
    else:
        print('   No Layer 4 output available')
    
    # Step 5: Pipeline Metrics
    print('\n[5] Pipeline Metrics:')
    metrics = result.get('metrics', {})
    print(f'   Total Time: {metrics.get("total_time_seconds", 0):.2f}s')
    
    layer_times = metrics.get('layer_times', {})
    for layer, time in layer_times.items():
        print(f'   {layer}: {time:.2f}s')
    
    errors = metrics.get('validation_errors', [])
    if errors:
        print(f'\n   ⚠️  Validation Errors: {errors}')
    
    # Step 6: Test different industries
    print('\n[6] Testing across industries...')
    industries = [
        ('retail', 'ABC Retail'),
        ('manufacturing', 'XYZ Manufacturing'),
        ('logistics', 'FastTrack Logistics'),
        ('technology', 'TechStar Solutions'),
        ('healthcare', 'MediCare Plus')
    ]
    
    for industry, name in industries:
        profile = {
            'company_id': f'test_{industry}_001',
            'company_name': name,
            'industry': industry,
            'size': 'medium'
        }
        
        r = await pipeline.run_full_pipeline(
            company_profile=profile,
            layer2_input=l2_output.model_dump()
        )
        
        if r.get('success'):
            l3 = r.get('layer3_output', {})
            health = l3.get('overall_operational_health', 0)
            risks_count = len(r.get('layer4_output', {}).get('risks', []))
            opps_count = len(r.get('layer4_output', {}).get('opportunities', []))
            print(f'   {name:25} Health: {health:.1f}  Risks: {risks_count}  Opportunities: {opps_count}')
    
    print('\n' + '='*70)
    print('✅ FULL PIPELINE TEST COMPLETE!')
    print('='*70)
    print('\nSummary:')
    print(f'  Layer 1 -> Layer 2: {l2_result.articles_processed} articles -> {len(l2_output.indicators)} indicators')
    print(f'  Layer 2 -> Layer 3: National indicators -> Operational health scores')
    print(f'  Layer 3 -> Layer 4: Operational data -> Risks, Opportunities, Recommendations')


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
