"""
Test: Run Full Pipeline and Store Results in Database

This script:
1. Runs the L2->L3->L4 pipeline
2. Stores results in the database using Layer4PersistenceService
3. Verifies data is accessible via Layer 5 dashboard service
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def run_pipeline_and_store():
    print('='*70)
    print('RUN PIPELINE AND STORE RESULTS')
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
    print(f'   ✅ Layer 2: {len(l2_output.indicators)} indicators')
    
    # Step 2: Run Integration Pipeline (L2->L3->L4)
    print('\n[2] Running Integration Pipeline...')
    from app.integration.pipeline import IntegrationPipeline
    
    pipeline = IntegrationPipeline()
    
    # Test company profiles
    companies = [
        {
            'company_id': 'retail_001',
            'company_name': 'ABC Retail Chain',
            'industry': 'retail',
            'size': 'large',
            'region': 'Western Province'
        },
        {
            'company_id': 'mfg_001',
            'company_name': 'XYZ Manufacturing',
            'industry': 'manufacturing',
            'size': 'medium',
            'region': 'Central Province'
        },
        {
            'company_id': 'tech_001',
            'company_name': 'TechStar Solutions',
            'industry': 'technology',
            'size': 'small',
            'region': 'Western Province'
        }
    ]
    
    # Step 3: Store results in database
    print('\n[3] Storing results in database...')
    from app.db.session import SessionLocal
    from app.layer4.storage.persistence_service import Layer4PersistenceService
    
    db = SessionLocal()
    persistence = Layer4PersistenceService(db)
    
    total_stored = {
        "risks": 0,
        "opportunities": 0,
        "recommendations": 0
    }
    
    try:
        for company in companies:
            print(f'\n   Processing: {company["company_name"]}...')
            
            # Run pipeline for this company
            result = await pipeline.run_full_pipeline(
                company_profile=company,
                layer2_input=l2_output.model_dump()
            )
            
            if not result.get('success'):
                print(f'   ❌ Pipeline failed for {company["company_id"]}')
                continue
            
            l4_output = result.get('layer4_output', {})
            
            # Store results
            stats = persistence.store_pipeline_results(
                company_id=company['company_id'],
                layer4_output=l4_output
            )
            
            print(f'   ✅ Stored: {stats["risks_stored"]} risks, '
                  f'{stats["opportunities_stored"]} opportunities, '
                  f'{stats["recommendations_stored"]} recommendations')
            
            total_stored["risks"] += stats["risks_stored"]
            total_stored["opportunities"] += stats["opportunities_stored"]
            total_stored["recommendations"] += stats["recommendations_stored"]
        
        db.commit()
        
    except Exception as e:
        print(f'   ❌ Error: {e}')
        db.rollback()
        raise
    finally:
        db.close()
    
    # Step 4: Verify stored data
    print('\n[4] Verifying stored data...')
    db = SessionLocal()
    
    try:
        from app.models.business_insight_models import BusinessInsight
        
        # Count by type
        risks = db.query(BusinessInsight).filter(
            BusinessInsight.insight_type == 'risk',
            BusinessInsight.status == 'active'
        ).count()
        
        opportunities = db.query(BusinessInsight).filter(
            BusinessInsight.insight_type == 'opportunity',
            BusinessInsight.status == 'active'
        ).count()
        
        recommendations = db.query(BusinessInsight).filter(
            BusinessInsight.insight_type == 'recommendation',
            BusinessInsight.status == 'active'
        ).count()
        
        print(f'   Database counts:')
        print(f'   - Risks: {risks}')
        print(f'   - Opportunities: {opportunities}')
        print(f'   - Recommendations: {recommendations}')
        
        # Show sample insights
        print('\n   Sample stored insights:')
        samples = db.query(BusinessInsight).filter(
            BusinessInsight.status == 'active'
        ).limit(5).all()
        
        for s in samples:
            print(f'   - [{s.insight_type.upper()}] {s.title[:50]}... ({s.company_id})')
        
    finally:
        db.close()
    
    print('\n' + '='*70)
    print('✅ PIPELINE RUN AND STORAGE COMPLETE!')
    print('='*70)
    print(f'\nTotal stored:')
    print(f'  Risks: {total_stored["risks"]}')
    print(f'  Opportunities: {total_stored["opportunities"]}')
    print(f'  Recommendations: {total_stored["recommendations"]}')
    print(f'\nData is now accessible via Layer 5 dashboard API!')


if __name__ == '__main__':
    asyncio.run(run_pipeline_and_store())
