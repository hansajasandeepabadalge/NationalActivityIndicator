"""
Test script for Layer 1 fixes.
Tests the new and modified components without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def print_pass(text):
    print(f"   ✅ {text}")

def print_fail(text):
    print(f"   ❌ {text}")

def test_configuration_loader():
    """Test the ConfigurationLoader and YAML configs."""
    print_header("Testing ConfigurationLoader")
    
    try:
        from app.scrapers.config_loader import ConfigurationLoader
        
        loader = ConfigurationLoader()
        configs = loader.load_all_sources()
        
        print_pass(f"Loaded {len(configs)} source configurations")
        
        # Check each source
        expected_sources = ["Ada Derana", "Daily FT", "Hiru News"]
        for source in expected_sources:
            if source in configs:
                config = configs[source]
                print_pass(f"{source}: type={config.metadata.source_type}, credibility={config.metadata.credibility_score}")
            else:
                print_fail(f"{source}: NOT FOUND")
        
        # Check stats
        stats = loader.get_stats()
        print_pass(f"Stats: {stats}")
        
        return len(configs) == 3
        
    except Exception as e:
        print_fail(f"Error: {e}")
        return False

def test_data_cleaner():
    """Test the DataCleaner with credibility scoring."""
    print_header("Testing DataCleaner")
    
    try:
        from app.cleaning.cleaner import DataCleaner, HAS_REPUTATION_TRACKER
        
        print_pass(f"HAS_REPUTATION_TRACKER: {HAS_REPUTATION_TRACKER}")
        
        cleaner = DataCleaner()
        
        # Test reputation tracker initialization
        if cleaner.reputation_tracker is not None:
            print_pass("SourceReputationTracker initialized")
        else:
            print_fail("SourceReputationTracker NOT available (but fallback works)")
        
        # Test content quality calculation
        quality = cleaner._calculate_content_quality_score(
            title="Test Article Title",
            body="This is a test article with enough content. " * 20,
            author="Test Author"
        )
        print_pass(f"Content quality score: {quality:.3f}")
        
        # Test credibility calculation
        credibility = cleaner._calculate_credibility_score("Ada Derana", quality)
        print_pass(f"Credibility score: {credibility:.3f}")
        
        return True
        
    except Exception as e:
        print_fail(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metrics_recorder():
    """Test the MetricsRecorder."""
    print_header("Testing MetricsRecorder")
    
    try:
        from app.services.metrics_recorder import (
            MetricsRecorder, 
            SourceHealthMetric,
            MentionMetric,
            get_metrics_recorder
        )
        
        # Test singleton
        recorder = get_metrics_recorder()
        print_pass(f"MetricsRecorder created (singleton)")
        
        # Test dataclasses
        health_metric = SourceHealthMetric(
            source_id=1,
            source_name="Ada Derana",
            scrape_duration_seconds=5,
            articles_collected=10,
            errors_count=0,
            success_rate=1.0
        )
        print_pass(f"SourceHealthMetric created: {health_metric.source_name}")
        
        mention_metric = MentionMetric(
            keyword="test",
            source_type="news",
            mention_count=5,
            unique_sources=2
        )
        print_pass(f"MentionMetric created: {mention_metric.keyword}")
        
        # Test buffer (since no DB)
        print_pass(f"Buffer size: {recorder.get_buffer_size()}")
        
        return True
        
    except Exception as e:
        print_fail(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_imports():
    """Test that MasterOrchestrator has the new imports."""
    print_header("Testing MasterOrchestrator Imports")
    
    try:
        # Import just the flags without initializing the full orchestrator
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "master_orchestrator", 
            "app/orchestrator/master_orchestrator.py"
        )
        
        # Read the file and check for our imports
        with open("app/orchestrator/master_orchestrator.py", "r") as f:
            content = f.read()
        
        checks = [
            ("SemanticDeduplicator import", "from app.deduplication import SemanticDeduplicator"),
            ("MetricsRecorder import", "from app.services.metrics_recorder import"),
            ("HAS_DEDUPLICATION flag", "HAS_DEDUPLICATION"),
            ("HAS_METRICS flag", "HAS_METRICS"),
            ("self.deduplicator init", "self.deduplicator"),
            ("self.metrics_recorder init", "self.metrics_recorder"),
            ("record_scrape_cycle call", "record_scrape_cycle")
        ]
        
        all_found = True
        for name, pattern in checks:
            if pattern in content:
                print_pass(f"{name}: Found")
            else:
                print_fail(f"{name}: NOT FOUND")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print_fail(f"Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print(" LAYER 1 FIXES VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    results["ConfigurationLoader"] = test_configuration_loader()
    results["DataCleaner"] = test_data_cleaner()
    results["MetricsRecorder"] = test_metrics_recorder()
    results["Orchestrator Imports"] = test_orchestrator_imports()
    
    # Summary
    print_header("SUMMARY")
    
    passed = 0
    total = len(results)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {component}: {'PASS' if status else 'FAIL'}")
        if status:
            passed += 1
    
    print(f"\n   Overall: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
