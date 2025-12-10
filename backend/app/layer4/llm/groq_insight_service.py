"""
Layer 4: Groq-Based Insight Generation Service

Uses the same multi-API key rotation system from Layer 2 to generate
LLM-powered risk analysis, opportunity identification, and recommendations.

Cost: $0 (Groq free tier with 3 rotating API keys)
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GroqInsightService:
    """
    LLM-powered insight generation using Groq Llama 3.1 70B.
    
    Reuses the Layer 2 multi-API key rotation system for:
    - Risk analysis with context-aware reasoning
    - Opportunity identification from operational data
    - Actionable recommendation generation
    
    Falls back to rule-based when LLM is unavailable.
    """
    
    def __init__(self):
        self._llm = None
        self._api_key_manager = None
        self._current_api_key = None
        self._init_llm()
        
        # Statistics
        self._stats = {
            "total_calls": 0,
            "llm_calls": 0,
            "fallback_calls": 0,
            "errors": 0,
            "key_rotations": 0
        }
    
    def _init_llm(self, api_key: Optional[str] = None):
        """Initialize Groq LLM using Layer 2's API key manager."""
        try:
            # Import Layer 2's API key manager
            from app.layer2.services.llm_base import api_key_manager, APIKeyManager
            
            self._api_key_manager = api_key_manager
            
            if not self._api_key_manager.has_keys:
                logger.warning("No Groq API keys available for Layer 4")
                return
            
            from langchain_groq import ChatGroq
            
            # Get API key
            if api_key is None:
                api_key = self._api_key_manager.get_next_available_key()
            
            if not api_key:
                logger.warning("All API keys rate limited")
                return
            
            self._current_api_key = api_key
            self._llm = ChatGroq(
                model="llama-3.3-70b-versatile",  # Updated from decommissioned 3.1
                temperature=0.3,
                max_tokens=2000,
                api_key=api_key
            )
            
            key_id = self._api_key_manager._get_key_id(api_key)
            logger.info(f"Layer 4 Groq LLM initialized with key {key_id}")
            
        except ImportError as e:
            logger.warning(f"Could not import Groq dependencies: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq LLM: {e}")
    
    def _rotate_api_key(self) -> bool:
        """Rotate to next available API key."""
        if not self._api_key_manager:
            return False
            
        if self._current_api_key:
            self._api_key_manager.mark_rate_limited(self._current_api_key, retry_after_seconds=60)
        
        next_key = self._api_key_manager.get_next_available_key()
        if next_key and next_key != self._current_api_key:
            self._init_llm(next_key)
            self._stats["key_rotations"] += 1
            return self._llm is not None
        return False
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self._llm is not None
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call LLM with automatic retry and key rotation."""
        if not self.is_available:
            return None
        
        self._stats["total_calls"] += 1
        
        for attempt in range(3):
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                
                self._stats["llm_calls"] += 1
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]
                
                response = self._llm.invoke(messages)
                content = response.content
                
                # Parse JSON response
                try:
                    json_content = content
                    if "```json" in content:
                        json_content = content.split("```json")[1].split("```")[0]
                    elif "```" in content:
                        json_content = content.split("```")[1].split("```")[0]
                    
                    result = json.loads(json_content.strip())
                    
                    # Record success
                    if self._current_api_key and self._api_key_manager:
                        self._api_key_manager.record_success(self._current_api_key)
                    
                    return result
                    
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse LLM response as JSON: {content[:200]}")
                    return {"raw_response": content}
                
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit = any(phrase in error_str for phrase in [
                    "rate limit", "429", "too many requests", "quota"
                ])
                
                if is_rate_limit:
                    logger.warning(f"Rate limit hit, rotating API key...")
                    if self._rotate_api_key():
                        continue
                    else:
                        break
                
                logger.error(f"LLM call failed (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))
        
        self._stats["errors"] += 1
        return None
    
    def generate_risk_analysis(
        self,
        operational_indicators: Dict[str, Any],
        company_profile: Dict[str, Any],
        detected_risks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate LLM-enhanced risk analysis.
        
        Takes rule-based detected risks and enhances them with:
        - Contextual reasoning
        - Interconnection analysis
        - Severity refinement
        - Mitigation priorities
        """
        system_prompt = """You are an expert business risk analyst. Analyze the operational indicators 
and detected risks for this company. Provide enhanced analysis with:
1. Risk severity assessment (critical/high/medium/low)
2. Root cause analysis
3. Interconnections between risks
4. Potential cascading effects
5. Immediate vs long-term concerns

Respond in JSON format:
{
    "enhanced_risks": [
        {
            "risk_code": "string",
            "severity": "critical|high|medium|low",
            "reasoning": "detailed explanation",
            "root_causes": ["cause1", "cause2"],
            "connected_risks": ["other_risk_codes"],
            "cascading_effects": ["effect1", "effect2"],
            "urgency": "immediate|short_term|medium_term",
            "confidence": 0.0-1.0
        }
    ],
    "overall_risk_level": "critical|high|medium|low",
    "key_concern": "main risk summary",
    "recommended_focus": "where to prioritize attention"
}"""

        user_prompt = f"""Company Profile:
- Industry: {company_profile.get('industry', 'unknown')}
- Size: {company_profile.get('size', 'unknown')}
- Region: {company_profile.get('region', 'unknown')}

Key Operational Indicators:
{self._format_indicators(operational_indicators)}

Rule-Based Detected Risks:
{json.dumps(detected_risks, indent=2, default=str)}

Analyze these risks and provide enhanced insights."""

        result = self._call_llm(system_prompt, user_prompt)
        
        if result and "enhanced_risks" in result:
            return result
        
        # Fallback: return original risks with minimal enhancement
        self._stats["fallback_calls"] += 1
        return {
            "enhanced_risks": detected_risks,
            "overall_risk_level": "medium" if detected_risks else "low",
            "key_concern": detected_risks[0].get("description", "No major concerns") if detected_risks else "No risks detected",
            "source": "fallback"
        }
    
    def generate_opportunity_analysis(
        self,
        operational_indicators: Dict[str, Any],
        company_profile: Dict[str, Any],
        detected_opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate LLM-enhanced opportunity analysis.
        """
        system_prompt = """You are a strategic business advisor. Analyze the operational indicators
and detected opportunities for this company. Provide enhanced analysis with:
1. Opportunity prioritization
2. Feasibility assessment
3. Resource requirements
4. Timing recommendations
5. Potential synergies

Respond in JSON format:
{
    "enhanced_opportunities": [
        {
            "opportunity_code": "string",
            "priority": "high|medium|low",
            "potential_impact": "description of business impact",
            "feasibility": 0.0-1.0,
            "resource_level": "low|medium|high",
            "timing": "immediate|short_term|medium_term",
            "synergies": ["related opportunities"],
            "key_success_factors": ["factor1", "factor2"]
        }
    ],
    "top_opportunity": "best opportunity to pursue",
    "quick_wins": ["opportunities with fast ROI"],
    "strategic_opportunities": ["longer-term high-value opportunities"]
}"""

        user_prompt = f"""Company Profile:
- Industry: {company_profile.get('industry', 'unknown')}
- Size: {company_profile.get('size', 'unknown')}

Key Operational Indicators:
{self._format_indicators(operational_indicators)}

Detected Opportunities:
{json.dumps(detected_opportunities, indent=2, default=str)}

Analyze and prioritize these opportunities."""

        result = self._call_llm(system_prompt, user_prompt)
        
        if result and "enhanced_opportunities" in result:
            return result
        
        self._stats["fallback_calls"] += 1
        return {
            "enhanced_opportunities": detected_opportunities,
            "top_opportunity": detected_opportunities[0].get("description", "No opportunities") if detected_opportunities else "No opportunities",
            "source": "fallback"
        }
    
    def generate_recommendations(
        self,
        risks: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        company_profile: Dict[str, Any],
        operational_health: float
    ) -> List[Dict[str, Any]]:
        """
        Generate LLM-powered actionable recommendations.
        """
        system_prompt = """You are a senior business consultant. Generate specific, actionable 
recommendations based on the company's risks, opportunities, and operational health.

For each recommendation provide:
1. Clear action title (what to do)
2. Detailed steps
3. Expected outcome
4. Priority level
5. Timeline
6. Resource requirements

Respond in JSON format:
{
    "recommendations": [
        {
            "title": "clear action title",
            "category": "risk_mitigation|opportunity_capture|operational_improvement",
            "priority": 1-5 (1=highest),
            "description": "detailed explanation",
            "action_steps": ["step1", "step2", "step3"],
            "expected_outcome": "what success looks like",
            "timeline": "immediate|this_week|this_month|this_quarter",
            "resources_needed": "low|medium|high",
            "success_metrics": ["metric1", "metric2"],
            "related_risks": ["risk_codes if applicable"],
            "related_opportunities": ["opp_codes if applicable"]
        }
    ],
    "top_priority_action": "single most important action",
    "quick_wins": ["fast low-effort actions"],
    "strategic_initiatives": ["longer-term high-impact actions"]
}"""

        user_prompt = f"""Company: {company_profile.get('company_name', 'Company')}
Industry: {company_profile.get('industry', 'unknown')}
Overall Operational Health: {operational_health:.1f}/100

Identified Risks ({len(risks)}):
{json.dumps(risks[:5], indent=2, default=str)}

Identified Opportunities ({len(opportunities)}):
{json.dumps(opportunities[:5], indent=2, default=str)}

Generate prioritized, actionable recommendations for this company."""

        result = self._call_llm(system_prompt, user_prompt)
        
        if result and "recommendations" in result:
            # Format recommendations to match expected schema
            formatted_recs = []
            for i, rec in enumerate(result.get("recommendations", [])[:10]):
                formatted_recs.append({
                    "action_title": rec.get("title", f"Recommendation {i+1}"),
                    "action_description": rec.get("description", ""),
                    "category": rec.get("category", "operational_improvement"),
                    "priority": rec.get("priority", 3),
                    "estimated_timeframe": rec.get("timeline", "this_week"),
                    "estimated_effort": rec.get("resources_needed", "medium"),
                    "expected_benefit": rec.get("expected_outcome", ""),
                    "success_metrics": rec.get("success_metrics", []),
                    "action_steps": rec.get("action_steps", []),
                    "source": "llm_generated"
                })
            return formatted_recs
        
        self._stats["fallback_calls"] += 1
        return []
    
    def _format_indicators(self, indicators: Dict[str, Any]) -> str:
        """Format indicators for prompt."""
        lines = []
        for key, value in indicators.items():
            if isinstance(value, (int, float)) and not key.startswith("_"):
                status = "⚠️ LOW" if value < 40 else "✅ OK" if value > 70 else "➡️ MODERATE"
                lines.append(f"- {key}: {value:.1f} {status}")
        return "\n".join(lines[:15])  # Limit to top 15 indicators
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        stats = dict(self._stats)
        if self._api_key_manager:
            stats["api_key_status"] = self._api_key_manager.get_stats()
        return stats


# Global instance
groq_insight_service = GroqInsightService()
