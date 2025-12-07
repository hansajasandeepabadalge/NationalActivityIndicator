"""
llm_service.py - High-level LLM operations
"""

from typing import Dict, List, Any, Optional
import json
import logging
import asyncio
from datetime import datetime

from app.layer4.llm.llm_client import openai_client, anthropic_client, UnifiedLLMClient
from app.layer4.llm.prompts import PromptTemplateManager
from app.layer4.cache.manager import CacheManager
from app.layer4.data.aggregator import DataAggregator

logger = logging.getLogger(__name__)


class LLMInsightService:
    """
    High-level service for generating business insights via LLM
    """

    def __init__(self):
        # Default to OpenAI, fallback to Anthropic if configured, or None
        self.llm = openai_client if openai_client else anthropic_client
        self.prompts = PromptTemplateManager()
        self.cache = CacheManager()
        self.aggregator = DataAggregator()

        if not self.llm:
            logger.warning("No LLM client available. LLM features will fail.")

    async def generate_risk_analysis(
        self,
        company_id: str,
        context_package: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate risk analysis using LLM
        """
        if not self.llm:
            raise RuntimeError("LLM client not configured")

        # Prepare context if not provided
        if not context_package:
            context_package = await self.aggregator.prepare_context_package(company_id)

        # Check cache
        cache_key = self.cache.generate_key('risks', context_package)
        cached = await self.cache.get(cache_key)
        if cached:
            logger.info(f"Risk analysis cache hit: {company_id}")
            return cached

        # Build prompt
        prompt = self.prompts.build_risk_analysis_prompt(context_package)

        # Call LLM
        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse response
            risks_data = self._parse_json_response(response['content'])

            # Add metadata
            result = {
                'risks': risks_data.get('risks', []),
                'risk_count': len(risks_data.get('risks', [])),
                'overall_risk_level': risks_data.get('overall_risk_level', 'unknown'),
                'summary': risks_data.get('summary', ''),
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'model': response['model'],
                    'tokens_used': response['usage']['total_tokens'],
                    'latency_ms': response['latency_ms']
                }
            }

            # Cache result
            await self.cache.set(cache_key, result, ttl=3600)

            return result

        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            raise

    async def generate_opportunity_analysis(
        self,
        company_id: str,
        context_package: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate opportunity analysis
        """
        if not self.llm:
            raise RuntimeError("LLM client not configured")

        if not context_package:
            context_package = await self.aggregator.prepare_context_package(company_id)

        cache_key = self.cache.generate_key('opportunities', context_package)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        prompt = self.prompts.build_opportunity_prompt(context_package)

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.4,
                max_tokens=1500
            )

            data = self._parse_json_response(response['content'])

            result = {
                'opportunities': data.get('opportunities', []),
                'opportunity_count': len(data.get('opportunities', [])),
                'summary': data.get('summary', ''),
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'model': response['model'],
                    'tokens_used': response['usage']['total_tokens']
                }
            }

            await self.cache.set(cache_key, result, ttl=7200)
            return result

        except Exception as e:
            logger.error(f"Opportunity analysis failed: {e}")
            raise

    async def generate_recommendations(
        self,
        insight: Dict[str, Any],
        company_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a specific insight
        """
        if not self.llm:
            raise RuntimeError("LLM client not configured")

        # Need company profile
        company_profile = await self.aggregator.layer3.fetch_company_profile(company_id)

        prompt = self.prompts.build_recommendation_prompt(insight, company_profile)

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000
            )

            recs = self._parse_json_response(response['content'])
            return recs

        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise

    async def generate_complete_insights(
        self,
        company_id: str
    ) -> Dict[str, Any]:
        """
        Generate complete insight package
        """
        # Prepare context once
        context_package = await self.aggregator.prepare_context_package(company_id)

        # Run analyses in parallel
        risks_task = self.generate_risk_analysis(company_id, context_package)
        opps_task = self.generate_opportunity_analysis(company_id, context_package)

        risks_result, opps_result = await asyncio.gather(
            risks_task, opps_task, return_exceptions=True
        )

        # Handle exceptions
        final_risks = risks_result if not isinstance(risks_result, Exception) else {"error": str(risks_result)}
        final_opps = opps_result if not isinstance(opps_result, Exception) else {"error": str(opps_result)}

        return {
            "company_id": company_id,
            "timestamp": datetime.now().isoformat(),
            "risks_analysis": final_risks,
            "opportunities_analysis": final_opps
        }

    def _parse_json_response(self, content: str) -> Any:
        """Helper to parse JSON from LLM response"""
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        return json.loads(content.strip())


# Singleton instance
_llm_service: Optional[LLMInsightService] = None


def get_llm_insight_service() -> LLMInsightService:
    """Get the singleton LLM insight service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMInsightService()
    return _llm_service
