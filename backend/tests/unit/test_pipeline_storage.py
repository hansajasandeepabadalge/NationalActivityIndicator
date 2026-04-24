"""
Test: Run Pipeline and Store Results to Database

This script:
1. Runs the L2→L3→L4 pipeline
2. Stores results to PostgreSQL using the persistence service
3. Verifies the data can be retrieved
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def test_pipeline_and_store():
    print('='*70)
    print('TESTING: Pipeline Run + Database Storage')
    print('='*70)
    
    # Step 1: Run Layer 2 Pipeline
    print('\n[1] Running Layer 2 Pipeline...')
    from app.layer2.pipeline_orchestrator import Layer2PipelineOrchestrator
    
    l2_orchestrator = Layer2PipelineOrchestrator()
    l2_result = await l2_orchestrator.run_full_pipeline(article_limit=50, store_results=False)
    
    if not l2_result.success or not l2_result.layer2_output:
        print('   ERROR: Layer 2 failed')
        return
    
    l2_output = l2_result.layer2_output
    print(f'   ✅ Layer 2: {len(l2_output.indicators)} indicators, NAI: {l2_output.activity_level:.1f}')
    
    # Step 2: Run Integration Pipeline (L2→L3→L4)
    print('\n[2] Running Integration Pipeline...')
    from app.integration.pipeline import IntegrationPipeline
    
    pipeline = IntegrationPipeline()
    
    # Test company
    company_profile = {
        'company_id': 'dashboard_test_001',
        'company_name': 'Dashboard Test Company',
        'industry': 'retail',
        'size': 'large',
        'region': 'Western Province'
    }
    
    result = await pipeline.run_full_pipeline(
        company_profile=company_profile,
        layer2_input=l2_output.model_dump()
    )
    
    if not result.get('success'):
        print(f'   ERROR: Pipeline failed - {result.get("error")}')
        return
    
    l4_output = result.get('layer4_output', {})
    print(f'   ✅ Layer 4: {len(l4_output.get("risks", []))} risks, '
          f'{len(l4_output.get("opportunities", []))} opportunities, '
          f'{len(l4_output.get("recommendations", []))} recommendations')
    
    # Step 3: Store to Database
    print('\n[3] Storing results to PostgreSQL...')
    from app.db.session import SessionLocal
    from app.layer4.storage.persistence_service import Layer4PersistenceService
    
    db = SessionLocal()
    try:
        persistence = Layer4PersistenceService(db)
        
        # Clear old insights for this test company
        persistence.clear_old_insights('dashboard_test_001')
        
        # Store new results
        stats = persistence.store_pipeline_results(
            company_id='dashboard_test_001',
            layer4_output=l4_output
        )
        
        print(f'   ✅ Stored:')
        print(f'      - Risks: {stats["risks_stored"]}')
        print(f'      - Opportunities: {stats["opportunities_stored"]}')
        print(f'      - Recommendations: {stats["recommendations_stored"]}')
        if stats["errors"] > 0:
            print(f'      ⚠️  Errors: {stats["errors"]}')
        
        # Step 4: Verify retrieval
        print('\n[4] Verifying stored data...')
        risks = persistence.get_stored_insights('dashboard_test_001', 'risk')
        opps = persistence.get_stored_insights('dashboard_test_001', 'opportunity')
        recs = persistence.get_stored_insights('dashboard_test_001', 'recommendation')
        
        print(f'   Retrieved from DB:')
        print(f'   - Risks: {len(risks)}')
        for r in risks[:3]:
            print(f'     • [{r.severity_level}] {r.title[:50]}')
        
        print(f'   - Opportunities: {len(opps)}')
        for o in opps[:3]:
            print(f'     • [{o.severity_level}] {o.title[:50]}')
        
        print(f'   - Recommendations: {len(recs)}')
        for rec in recs[:3]:
            print(f'     • [{rec.severity_level}] {rec.title[:50]}')
        
        # Step 5: Test L5 Dashboard Service
        print('\n[5] Testing L5 Dashboard Service...')
        from app.layer5.services.dashboard_service import DashboardService
        
        dashboard_service = DashboardService(db)
        
        # Get business insights for this company
        insights = dashboard_service.get_business_insights(
            company_id='dashboard_test_001',
            limit=20
        )
        
        print(f'   Dashboard service retrieved: {insights.total} insights')
        for insight in insights.insights[:5]:
            print(f'   • [{insight.insight_type}] {insight.title[:40]}...')
        
        print('\n' + '='*70)
        print('✅ PIPELINE + STORAGE TEST COMPLETE!')
        print('='*70)
        print('\nData is now available in the dashboard via:')
        print('  GET /api/v1/admin/insights')
        print('  GET /api/v1/user/insights')
        
    finally:
        db.close()


if __name__ == '__main__':
    asyncio.run(test_pipeline_and_store())
