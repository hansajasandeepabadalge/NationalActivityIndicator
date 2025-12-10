"""
test_llm_service.py - Tests for Layer 4 LLM Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.layer4.llm.llm_service import LLMInsightService
from app.layer4.llm.llm_client import UnifiedLLMClient

@pytest.mark.asyncio
async def test_generate_risk_analysis():
    # Mock dependencies
    with patch('app.layer4.llm.llm_service.UnifiedLLMClient') as MockClient:
        mock_llm = MockClient.return_value
        mock_llm.generate = AsyncMock(return_value={
            'content': '{"risks": [{"name": "Test Risk", "probability": 80}], "overall_risk_level": "high"}',
            'model': 'gpt-4',
            'usage': {'total_tokens': 100},
            'latency_ms': 500
        })

        service = LLMInsightService()
        service.llm = mock_llm  # Inject mock

        # Mock aggregator to return sample context attributes
        service.aggregator.prepare_context_package = AsyncMock(return_value={
            'company': {'name': 'Test Co', 'industry': 'Tech', 'size': 'Small'},
            'current_state': {'indicators': [], 'areas_of_concern': []},
            'trends': {'improving': [], 'deteriorating': []}
        })

        result = await service.generate_risk_analysis("company_123")

        assert result['risk_count'] == 1
        assert result['risks'][0]['name'] == 'Test Risk'
        assert result['metadata']['tokens_used'] == 100

@pytest.mark.asyncio
async def test_generate_opportunity_analysis():
    with patch('app.layer4.llm.llm_service.UnifiedLLMClient') as MockClient:
        mock_llm = MockClient.return_value
        mock_llm.generate = AsyncMock(return_value={
            'content': '{"opportunities": [{"title": "New Market"}], "summary": "Good opps"}',
            'model': 'gpt-4',
            'usage': {'total_tokens': 100}
        })

        service = LLMInsightService()
        service.llm = mock_llm

        service.aggregator.prepare_context_package = AsyncMock(return_value={
            'company': {'name': 'Test'},
            'current_state': {'indicators': []},
            'trends': {}
        })

        result = await service.generate_opportunity_analysis("company_123")

        assert result['opportunity_count'] == 1
        assert result['opportunities'][0]['title'] == "New Market"
