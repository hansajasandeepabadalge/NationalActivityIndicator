import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.layer3.services.operational_service import OperationalService

def verify_layer3():
    print("Initializing OperationalService...")
    service = OperationalService()
    
    print("\n--- Testing Mock Data Loading ---")
    companies = service.get_all_companies()
    print(f"Loaded {len(companies)} companies.")
    for c in companies:
        print(f" - {c['company_name']} ({c['industry']})")
        
    if not companies:
        print("ERROR: No companies loaded!")
        return
    
    target_company_id = "mock_retail_001"
    print(f"\n--- Running Calculation for {target_company_id} ---")
    
    try:
        result = service.calculate_indicators_for_company(target_company_id)
        
        print("Calculation Successful!")
        print("\nUniversal Indicators:")
        print(json.dumps(result['universal_indicators'], indent=2))
        
        print("\nIndustry Specific Indicators:")
        print(json.dumps(result['industry_specific_indicators'], indent=2))
        
        print(f"\nTranslation Impacts (First 3 of {len(result['translation_impacts'])}):")
        print(json.dumps(result['translation_impacts'][:3], indent=2))
        
        # Basic assertions
        assert result['status'] == 'success'
        assert 'transport_availability' in result['universal_indicators']
        assert 'footfall_impact' in result['industry_specific_indicators']
        
        print("\nVERIFICATION PASSED: Layer 3 Logic is working correctly.")
        
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_layer3()
