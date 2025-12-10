"""Test Groq LLM integration in Layer 4"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

async def test():
    print('='*60)
    print('Testing Groq LLM in Layer 4')
    print('='*60)
    
    from app.layer4.llm.groq_insight_service import groq_insight_service
    
    print(f'\nLLM Available: {groq_insight_service.is_available}')
    
    stats = groq_insight_service.get_stats()
    print(f'API Keys: {stats.get("api_key_status", {}).get("total_keys", 0)}')
    print(f'Available Keys: {stats.get("api_key_status", {}).get("available_keys", "?")}')
    
    if groq_insight_service.is_available:
        print('\nGenerating LLM recommendations...')
        
        recs = groq_insight_service.generate_recommendations(
            risks=[
                {'description': 'Regulatory burden at 23.5%', 'severity_level': 'low', 'risk_code': 'RISK_COMPLIANCE'}
            ],
            opportunities=[
                {'description': 'Strong market demand at 100%', 'priority_level': 'high', 'opportunity_code': 'OPP_DEMAND'},
                {'description': 'Pricing power opportunity', 'priority_level': 'high', 'opportunity_code': 'OPP_PRICING'}
            ],
            company_profile={
                'industry': 'retail',
                'company_name': 'ABC Retail Chain',
                'size': 'large'
            },
            operational_health=86.3
        )
        
        print(f'\n✅ Generated {len(recs)} LLM recommendations:\n')
        for i, r in enumerate(recs[:5], 1):
            title = r.get('action_title', 'No title')
            priority = r.get('priority', 3)
            category = r.get('category', 'unknown')
            print(f'{i}. [{priority}] {title}')
            print(f'   Category: {category}')
            if r.get('action_steps'):
                print(f'   Steps: {r["action_steps"][:2]}...')
            print()
        
        print(f'Stats after call: {groq_insight_service.get_stats()}')
    else:
        print('\n❌ LLM not available - check API keys')

if __name__ == '__main__':
    asyncio.run(test())
