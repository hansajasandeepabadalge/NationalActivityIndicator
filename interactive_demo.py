import sys
import os
import json
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.layer3.services.operational_service import OperationalService

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("="*60)
    print("   NATIONAL ACTIVITY INDICATOR - LAYER 3 ENGINE (DEMO)   ")
    print("="*60)
    print("This demo runs on the Mock Data Layer and Core Logic.")
    print("No external database or API server required.")
    print("-" * 60)

def main():
    service = OperationalService()
    
    while True:
        clear_screen()
        print_header()
        
        print("\nAvailable Mock Companies:")
        companies = service.get_all_companies()
        for i, c in enumerate(companies):
            print(f" [{i+1}] {c['company_name']} (ID: {c['company_id']}) - {c['industry'].title()}")
        
        print("\nOptions:")
        print(" [Q] Quit")
        
        choice = input("\nEnter selection (Number or ID): ").strip()
        
        if choice.lower() == 'q':
            print("\nExiting...")
            break
            
        selected_company_id = None
        
        # Handle number selection
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(companies):
                selected_company_id = companies[idx]['company_id']
        
        # Handle ID selection
        else:
            for c in companies:
                if c['company_id'] == choice:
                    selected_company_id = choice
                    break
        
        if selected_company_id:
            run_calculation(service, selected_company_id)
        else:
            print("\nInvalid selection. Press Enter to try again.")
            input()

def run_calculation(service, company_id):
    print(f"\nRunning calculation for {company_id}...")
    time.sleep(0.5) # Fake processing time
    
    try:
        result = service.calculate_indicators_for_company(company_id)
        
        print("\n" + "-"*30)
        print(f" RESULTS FOR: {company_id}")
        print("-" * 30)
        
        print("\n[UNIVERSAL INDICATORS]")
        for k, v in result['universal_indicators'].items():
            print(f"  {k.replace('_', ' ').title():<25}: {v:.2f}")
            
        print("\n[INDUSTRY SPECIFIC]")
        for k, v in result['industry_specific_indicators'].items():
            if isinstance(v, dict):
                val = v.get('value', 0)
                print(f"  {k.replace('_', ' ').title():<25}: {val:.2f}%")
            else:
                print(f"  {k.replace('_', ' ').title():<25}: {v:.2f}")
                
        print("\n[IMPACT TRANSLATION (Sample)]")
        impacts = result['translation_impacts']
        if impacts:
            for impact in impacts[:3]: # Show first 3
                print(f"  Rule: {impact['rule_type'].upper()} -> Val: {impact['value']:.2f} (Conf: {impact['confidence']})")
        else:
            print("  No direct translation rules triggered.")
            
        print("\n" + "="*60)
        input("\nPress Enter to return to menu...")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
