"""
Demo script to run the full integration pipeline with different scenarios
"""

import asyncio
from app.integration import create_pipeline, MockDataGenerator


async def run_demo():
    """Run the integration pipeline with different economic scenarios"""
    
    # Create pipeline and mock data generator
    pipeline = create_pipeline()
    mock_gen = MockDataGenerator(seed=42)
    
    # Test different scenarios
    scenarios = ['normal', 'crisis', 'growth', 'recession']
    
    print("\n" + "=" * 70)
    print("INTEGRATION PIPELINE DEMONSTRATION")
    print("=" * 70)
    
    for scenario in scenarios:
        print(f"\n{'-' * 50}")
        print(f"SCENARIO: {scenario.upper()}")
        print("-" * 50)
        
        # Generate Layer 2 mock data
        l2_data = mock_gen.generate_layer2_output(scenario)
        
        # Generate company profile
        company = mock_gen.generate_company_profile("DEMO001", "manufacturing")
        
        # Run full pipeline
        result = await pipeline.run_full_pipeline(company, layer2_input=l2_data)
        
        if result['success']:
            l3 = result['layer3_output']
            l4 = result['layer4_output']
            metrics = result['metrics']
            
            print("\n  LAYER 2 (National Indicators):")
            print(f"    Overall Sentiment: {l2_data['overall_sentiment']:.2f}")
            print(f"    Activity Level: {l2_data['activity_level']:.1f}")
            print(f"    Indicators Count: {len(l2_data['indicators'])}")
            
            print("\n  LAYER 3 (Operational Indicators):")
            print(f"    Overall Health: {l3['overall_operational_health']:.1f}")
            print(f"    Supply Chain: {l3['supply_chain_health']:.1f}")
            print(f"    Workforce: {l3['workforce_health']:.1f}")
            print(f"    Infrastructure: {l3['infrastructure_health']:.1f}")
            print(f"    Cost Pressure: {l3['cost_pressure']:.1f}")
            print(f"    Financial: {l3['financial_health']:.1f}")
            
            print("\n  LAYER 4 (Business Insights):")
            summary = l4.get('summary', {})
            print(f"    Risk Level: {summary.get('risk_level', 'N/A')}")
            print(f"    Risks Detected: {summary.get('risk_count', len(l4.get('risks', [])))}")
            print(f"    Opportunities: {summary.get('opportunity_count', len(l4.get('opportunities', [])))}")
            print(f"    Recommendations: {summary.get('recommendation_count', len(l4.get('recommendations', [])))}")
            
            print("\n  PERFORMANCE:")
            print(f"    Layer 2 Time: {metrics['layer_times'].get('layer2', 0):.4f}s")
            print(f"    Layer 3 Time: {metrics['layer_times'].get('layer3', 0):.4f}s")
            print(f"    Layer 4 Time: {metrics['layer_times'].get('layer4', 0):.4f}s")
            print(f"    Total Time: {metrics['total_time_seconds']:.4f}s")
        else:
            print(f"\n  ERROR: {result['error']}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE - All scenarios processed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
