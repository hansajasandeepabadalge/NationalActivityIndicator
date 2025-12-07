"""
prompts.py - Prompt Template Manager for Layer 4 LLM
"""

from typing import Dict, List, Any


class PromptTemplateManager:
    """
    Manages all LLM prompt templates for business insights generation
    """

    def __init__(self):
        # In a real system, these might be loaded from a file or DB
        pass

    def _format_indicators_for_prompt(self, indicators: List[Dict[str, Any]]) -> str:
        """Format indicators list for prompt"""
        if not indicators:
            return "No indicators available."
        lines = []
        for ind in indicators:
            interpretation = ind.get('interpretation', ind.get('trend', ''))
            lines.append(f"- {ind.get('name', ind.get('code', 'Unknown'))} ({ind.get('code', '')}): {ind.get('value', 'N/A')} - {interpretation}")
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

        company = context_package.get('company', {})
        current_state = context_package.get('current_state', {})
        trends = context_package.get('trends', {})

        industry = company.get('industry', 'general')
        company_name = company.get('name', 'Unknown Company')
        company_size = company.get('size', company.get('scale', 'medium'))
        characteristics = company.get('characteristics', {})
        
        critical_deps = characteristics.get('critical_dependencies', [])
        import_dep = characteristics.get('import_dependency', 0)
        employees = characteristics.get('employees', 'N/A')

        indicators = current_state.get('indicators', [])
        concerns = current_state.get('areas_of_concern', [])
        
        improving = trends.get('improving', [])
        deteriorating = trends.get('deteriorating', [])

        prompt = f"""You are an expert business risk analyst specializing in {industry} in Sri Lanka.

COMPANY CONTEXT:
- Name: {company_name}
- Industry: {industry}
- Size: {company_size} ({employees} employees)
- Key Dependencies: {', '.join(critical_deps) if critical_deps else 'Not specified'}
- Import Dependency: {import_dep * 100 if isinstance(import_dep, (int, float)) else import_dep}%

CURRENT OPERATIONAL INDICATORS (0-100 scale, higher is better):
{self._format_indicators_for_prompt(indicators)}

TRENDS (Last 7 days):
- Improving: {', '.join(improving) if improving else 'None'}
- Deteriorating: {', '.join(deteriorating) if deteriorating else 'None'}

AREAS OF CONCERN:
{self._format_concerns(concerns)}

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
- Be specific to {industry} industry context
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
        company = context_package.get('company', {})
        current_state = context_package.get('current_state', {})
        trends = context_package.get('trends', {})

        industry = company.get('industry', 'general')
        company_name = company.get('name', 'Unknown Company')
        company_size = company.get('size', company.get('scale', 'medium'))
        
        improving = trends.get('improving', [])
        indicators = current_state.get('indicators', [])

        prompt = f"""You are a strategic business consultant for the {industry} industry in Sri Lanka.

COMPANY CONTEXT:
- Name: {company_name}
- Size: {company_size}
- Strong Areas: {', '.join(improving) if improving else 'General operations'}

CURRENT STATE:
{self._format_indicators_for_prompt(indicators)}

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
        insight_category = insight.get('category', 'General')
        insight_name = insight.get('name', insight.get('title', 'Unknown'))
        insight_reasoning = insight.get('reasoning', insight.get('description', ''))
        insight_impact = insight.get('impact', insight.get('potential_value', 'Unknown'))
        
        company_name = company_profile.get('name', 'Unknown Company')
        company_industry = company_profile.get('industry', 'general')

        prompt = f"""Generate actionable recommendations for the following business insight:

INSIGHT:
Type: {insight_category}
Title: {insight_name}
Description: {insight_reasoning}
Impact/Value: {insight_impact}

COMPANY:
Name: {company_name}
Industry: {company_industry}

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

    def build_executive_summary_prompt(
        self,
        risks: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        company_profile: Dict[str, Any]
    ) -> str:
        """
        Build executive summary prompt combining risks and opportunities
        """
        company_name = company_profile.get('name', 'Unknown Company')
        industry = company_profile.get('industry', 'general')
        
        risk_summary = "\n".join([
            f"- {r.get('name', 'Unknown')}: {r.get('impact', 'unknown')} impact, {r.get('probability', 0)}% probability"
            for r in risks[:3]
        ]) if risks else "No significant risks identified."
        
        opp_summary = "\n".join([
            f"- {o.get('title', 'Unknown')}: {o.get('priority', 'medium')} priority, value {o.get('potential_value', 'N/A')}/10"
            for o in opportunities[:3]
        ]) if opportunities else "No significant opportunities identified."

        prompt = f"""Generate an executive summary for {company_name} ({industry}):

KEY RISKS:
{risk_summary}

KEY OPPORTUNITIES:
{opp_summary}

TASK: Write a 3-4 paragraph executive summary that:
1. Highlights the current business health status
2. Summarizes the top risks and their implications
3. Summarizes the top opportunities and potential gains
4. Provides strategic recommendations

OUTPUT FORMAT: Plain text, well-formatted with clear paragraphs.
"""
        return prompt
