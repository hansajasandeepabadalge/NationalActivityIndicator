"""
Test if health service can be imported
"""

try:
    print("Testing health service import...")
    from app.services.system_health_service import SystemHealthService
    print("✓ SystemHealthService imported successfully")
    
    print("\nTesting health endpoints import...")
    from app.api.v1.endpoints import health
    print("✓ Health endpoints imported successfully")
    
    print("\nTesting basic functionality...")
    status = SystemHealthService.get_system_status()
    print(f"✓ System status: {status}")
    
    metrics = SystemHealthService.get_api_metrics()
    print(f"✓ API metrics: {metrics}")
    
    resources = SystemHealthService.get_resource_usage()
    print(f"✓ Resource usage: CPU={resources['cpu_percent']}%, Memory={resources['memory_percent']}%")
    
    print("\n✅ All imports and basic tests passed!")
    print("The health endpoints should work after backend restart.")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
