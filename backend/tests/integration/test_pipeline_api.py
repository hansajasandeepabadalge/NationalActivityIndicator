"""
Tests for Integration Pipeline API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

# Import the app
from app.main import app

client = TestClient(app)


# =============================================================================
# Health Check Tests
# =============================================================================

class TestPipelineHealth:
    """Test pipeline health endpoints"""
    
    def test_pipeline_health_check(self):
        """Test pipeline health endpoint"""
        response = client.get("/api/v1/pipeline/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data


# =============================================================================
# Scenario & Industry List Tests
# =============================================================================

class TestPipelineMetadata:
    """Test pipeline metadata endpoints"""
    
    def test_list_scenarios(self):
        """Test listing available scenarios"""
        response = client.get("/api/v1/pipeline/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        scenarios = data["scenarios"]
        assert len(scenarios) == 4
        scenario_ids = [s["id"] for s in scenarios]
        assert "normal" in scenario_ids
        assert "crisis" in scenario_ids
        assert "growth" in scenario_ids
        assert "recession" in scenario_ids
    
    def test_list_industries(self):
        """Test listing supported industries"""
        response = client.get("/api/v1/pipeline/industries")
        assert response.status_code == 200
        data = response.json()
        assert "industries" in data
        industries = data["industries"]
        assert len(industries) >= 5
        industry_ids = [i["id"] for i in industries]
        assert "manufacturing" in industry_ids
        assert "retail" in industry_ids


# =============================================================================
# Demo Endpoint Tests
# =============================================================================

class TestPipelineDemo:
    """Test demo endpoint"""
    
    def test_demo_default(self):
        """Test demo with default parameters"""
        response = client.get("/api/v1/pipeline/demo")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "company_id" in data
        assert "layer2_summary" in data
        assert "layer3_summary" in data
        assert "layer4_summary" in data
    
    def test_demo_with_industry(self):
        """Test demo with specific industry"""
        response = client.get("/api/v1/pipeline/demo?industry=retail")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["industry"] == "retail"
    
    def test_demo_with_scenario(self):
        """Test demo with specific scenario"""
        response = client.get("/api/v1/pipeline/demo?scenario=crisis")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Crisis should show more risks
        assert data["layer4_summary"]["risk_count"] >= 1


# =============================================================================
# Full Pipeline Tests
# =============================================================================

class TestFullPipeline:
    """Test full pipeline execution"""
    
    def test_run_full_pipeline_normal(self):
        """Test running full pipeline with normal scenario"""
        request_data = {
            "company_profile": {
                "company_id": "TEST001",
                "company_name": "Test Company",
                "industry": "manufacturing"
            },
            "scenario": "normal",
            "use_mock_data": True
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["company_id"] == "TEST001"
        assert data["company_name"] == "Test Company"
        assert data["industry"] == "manufacturing"
        
        # Check layer summaries
        assert "layer2_summary" in data
        assert "layer3_summary" in data
        assert "layer4_summary" in data
        
        # Check Layer 2 summary
        l2 = data["layer2_summary"]
        assert "overall_sentiment" in l2
        assert "activity_level" in l2
        
        # Check Layer 3 summary
        l3 = data["layer3_summary"]
        assert "overall_health" in l3
        assert "supply_chain" in l3
        
        # Check Layer 4 summary
        l4 = data["layer4_summary"]
        assert "risk_count" in l4
        assert "opportunity_count" in l4
    
    def test_run_full_pipeline_crisis(self):
        """Test running full pipeline with crisis scenario"""
        request_data = {
            "company_profile": {
                "company_id": "CRISIS001",
                "company_name": "Crisis Test Co",
                "industry": "retail"
            },
            "scenario": "crisis",
            "use_mock_data": True
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Crisis should have lower health
        assert data["layer3_summary"]["overall_health"] < 60
    
    def test_run_full_pipeline_growth(self):
        """Test running full pipeline with growth scenario"""
        request_data = {
            "company_profile": {
                "company_id": "GROWTH001",
                "company_name": "Growth Test Co",
                "industry": "technology"
            },
            "scenario": "growth",
            "use_mock_data": True
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        # Growth should have opportunities
        assert data["layer4_summary"]["opportunity_count"] >= 1
    
    def test_run_full_pipeline_detailed(self):
        """Test detailed pipeline output"""
        request_data = {
            "company_profile": {
                "company_id": "DETAIL001",
                "company_name": "Detail Test Co",
                "industry": "manufacturing"
            },
            "scenario": "normal",
            "use_mock_data": True
        }
        
        response = client.post("/api/v1/pipeline/run/full", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "layer2_output" in data
        assert "layer3_output" in data
        assert "layer4_output" in data
        assert "metrics" in data


# =============================================================================
# Layer-Specific Pipeline Tests
# =============================================================================

class TestLayerSpecificPipeline:
    """Test layer-specific pipeline endpoints"""
    
    def test_layer2_to_layer3(self):
        """Test Layer 2 → Layer 3 transformation"""
        request_data = {
            "company_profile": {
                "company_id": "L2L3001",
                "company_name": "L2L3 Test Co",
                "industry": "logistics"
            },
            "scenario": "normal"
        }
        
        response = client.post("/api/v1/pipeline/run/layer2-to-layer3", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "layer3_output" in data
        
        l3 = data["layer3_output"]
        assert "supply_chain_health" in l3
        assert "workforce_health" in l3
        assert "overall_operational_health" in l3
    
    def test_layer3_to_layer4(self):
        """Test Layer 3 → Layer 4 transformation"""
        # First get Layer 3 output
        l2l3_request = {
            "company_profile": {
                "company_id": "L3L4001",
                "company_name": "L3L4 Test Co",
                "industry": "hospitality"
            },
            "scenario": "normal"
        }
        
        l2l3_response = client.post("/api/v1/pipeline/run/layer2-to-layer3", json=l2l3_request)
        l3_output = l2l3_response.json()["layer3_output"]
        
        # Now run Layer 3 → Layer 4
        request_data = {
            "company_profile": {
                "company_id": "L3L4001",
                "company_name": "L3L4 Test Co",
                "industry": "hospitality"
            },
            "layer3_input": l3_output
        }
        
        response = client.post("/api/v1/pipeline/run/layer3-to-layer4", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "layer4_output" in data


# =============================================================================
# Different Industry Tests
# =============================================================================

class TestDifferentIndustries:
    """Test pipeline with different industries"""
    
    @pytest.mark.parametrize("industry", [
        "retail",
        "manufacturing",
        "logistics",
        "hospitality",
        "technology",
        "healthcare",
        "finance"
    ])
    def test_all_industries(self, industry):
        """Test pipeline works for all industries"""
        request_data = {
            "company_profile": {
                "company_id": f"{industry.upper()}001",
                "company_name": f"Test {industry.title()} Co",
                "industry": industry
            },
            "scenario": "normal",
            "use_mock_data": True
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["industry"] == industry


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_industry(self):
        """Test invalid industry returns error"""
        request_data = {
            "company_profile": {
                "company_id": "ERR001",
                "company_name": "Error Test Co",
                "industry": "invalid_industry"  # Invalid!
            },
            "scenario": "normal"
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_invalid_scenario(self):
        """Test invalid scenario returns error"""
        request_data = {
            "company_profile": {
                "company_id": "ERR002",
                "company_name": "Error Test Co",
                "industry": "manufacturing"
            },
            "scenario": "invalid_scenario"  # Invalid!
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_missing_company_id(self):
        """Test missing required field returns error"""
        request_data = {
            "company_profile": {
                "company_name": "Error Test Co",
                "industry": "manufacturing"
                # Missing company_id!
            },
            "scenario": "normal"
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 422  # Validation error


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_pipeline_execution_time(self):
        """Test pipeline completes in reasonable time"""
        request_data = {
            "company_profile": {
                "company_id": "PERF001",
                "company_name": "Performance Test Co",
                "industry": "manufacturing"
            },
            "scenario": "normal",
            "use_mock_data": True
        }
        
        response = client.post("/api/v1/pipeline/run", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should complete in under 5 seconds
        assert data["total_time_seconds"] < 5.0
