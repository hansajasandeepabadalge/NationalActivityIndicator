"""
prompts.py - Prompt Template Manager
"""

from typing import Dict, List, Any
import json

class PromptTemplateManager:
    """
    Manages all LLM prompt templates
    """
    
    def __init__(self):
        # In a real system, these might be loaded from a file or DB
        pass
    
    def _format_indicators_for_prompt(self, indicators: List[Dict[str, Any]]) -> str:
        """Format indicators list for prompt"""
        lines = []
        for ind in indicators:
            lines.append(f"- {ind['name']} ({ind['code']}): {ind['value']} - {ind.get('interpretation', '')}")
        return "\n".join(lines)
        
    def _format_concerns(self, concerns: List[str]) -> str:
        """Format concerns list"""
        if not concerns:
            return "None identified."
        return "\n".join([f"- {c}" for c in concerns])

    def build_risk_analysis_prompt(
        self, 
        context_package: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive risk analysis prompt
        """
        
        company = context_package['company']
        current_state = context_package['current_state']
        trends = context_package['trends']
        
        prompt = f"""You are an expert business risk analyst specializing in {company['industry']} in Sri Lanka.

COMPANY CONTEXT:
- Name: {company['name']}
- Industry: {company['industry']}
- Size: {company['size']} ({company.get('characteristics', {}).get('employees', 'N/A')} employees)
- Key Dependencies: {', '.join(company.get('characteristics', {}).get('critical_dependencies', []))}
- Import Dependency: {company.get('characteristics', {}).get('import_dependency', 0)*100}%

CURRENT OPERATIONAL INDICATORS (0-100 scale, higher is better):
{self._format_indicators_for_prompt(current_state['indicators'])}

TRENDS (Last 7 days):
- Improving: {', '.join(trends['improving']) if trends['improving'] else 'None'}
- Deteriorating: {', '.join(trends['deteriorating']) if trends['deteriorating'] else 'None'}

AREAS OF CONCERN:
{self._format_concerns(current_state['areas_of_concern'])}

TASK: Identify and analyze the TOP 3 MOST SIGNIFICANT RISKS facing this business right now.

For each risk, provide:
1. **Risk Name**: Clear, specific title
2. **Category**: One of [operational, financial, competitive, reputational, compliance, strategic]
3. **Probability**: 0-100% (likelihood of occurring)
4. **Impact**: One of [low, medium, high, critical]
5. **Time Horizon**: When it might occur (e.g., "24-48 hours", "this week", "this month")
6. **Root Cause**: Which indicators/factors are driving this risk (2-3 sentences)
7. **Confidence**: 0-100% (how confident are you in this assessment)
8. **Reasoning**: Why is this a significant risk for THIS specific company? (3-4 sentences)

IMPORTANT GUIDELINES:
- Be specific to {company['industry']} industry context
- Consider the company's size and dependencies
- Focus on ACTIONABLE risks (things the business can respond to)
- Provide realistic probability estimates
- Explain your reasoning clearly
- Consider Sri Lankan market context

OUTPUT FORMAT: Valid JSON matching this exact schema:
{{
  "risks": [
    {{
      "name": "string",
      "category": "operational|financial|competitive|reputational|compliance|strategic",
      "probability": 85,
      "impact": "low|medium|high|critical",
      "time_horizon": "string",
      "root_cause": "string",
      "confidence": 85,
      "reasoning": "string",
      "affected_operations": ["list", "of", "affected", "areas"]
    }}
  ],
  "overall_risk_level": "low|medium|high|critical",
  "summary": "2-3 sentence overview of overall risk landscape"
}}

Generate the risk analysis now:"""
        return prompt

    def build_opportunity_prompt(
        self,
        context_package: Dict[str, Any]
    ) -> str:
        """
        Build opportunity detection prompt
        """
        company = context_package['company']
        current_state = context_package['current_state']
        trends = context_package['trends']
        
        prompt = f"""You are a strategic business consultant for the {company['industry']} industry in Sri Lanka.

COMPANY CONTEXT:
- Name: {company['name']}
- Size: {company['size']}
- Strong Areas: {', '.join(trends['improving'])}

CURRENT STATE:
{self._format_indicators_for_prompt(current_state['indicators'])}

TASK: Identify TOP 3 BUSINESS OPPORTUNITIES based on the current indicators and trends.

For each opportunity:
1. Title
2. Description
3. Potential Value (1-10)
4. Feasibility (0-100%)
5. Priority (low/medium/high)
6. Strategy to execute

OUTPUT FORMAT: Valid JSON:
{{
  "opportunities": [
    {{
      "title": "string",
      "description": "string",
      "potential_value": 8,
      "feasibility": 75,
      "priority": "high",
      "strategy": "string",
      "category": "efficiency|market|product|partnership"
    }}
  ],
  "summary": "Overview string"
}}
"""
        return prompt

    def build_recommendation_prompt(
        self,
        insight: Dict[str, Any],
        company_profile: Dict[str, Any]
    ) -> str:
        """
        Build recommendation generation prompt
        """
        prompt = f"""Generate actionable recommendations for the following business insight:

INSIGHT:
Type: {insight.get('category', 'General')}
Title: {insight.get('name', insight.get('title', 'Unknown'))}
Description: {insight.get('reasoning', insight.get('description', ''))}
Impact/Value: {insight.get('impact', insight.get('potential_value', 'Unknown'))}

COMPANY:
Name: {company_profile['name']}
Industry: {company_profile['industry']}

TASK: Provide 3 concrete, actionable steps the company should take to address this.

OUTPUT FORMAT: Valid JSON array of objects:
[
  {{
    "action_title": "string",
    "action_description": "string",
    "responsible_role": "string",
    "priority": "high|medium|low",
    "estimated_effort": "low|medium|high",
    "estimated_cost": "low|medium|high",
    "estimated_timeframe": "string (e.g. 2 days)",
    "expected_benefit": "string",
    "success_metrics": ["metric1", "metric2"],
    "required_resources": ["res1", "res2"],
    "category": "process|technology|personnel|financial"
  }}
]
"""
        return prompt
