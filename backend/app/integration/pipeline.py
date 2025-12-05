"""
Integration Pipeline Orchestrator

Provides end-to-end data flow from Layer 2 through Layer 4.
This module replaces mock data with actual layer outputs.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import asyncio

from .contracts import (
    Layer2Output,
    Layer3Input,
    Layer3Output,
    Layer4Input,
    validate_layer2_output,
    validate_layer3_output,
)
from .adapters import Layer2ToLayer3Adapter, Layer3ToLayer4Adapter

logger = logging.getLogger(__name__)


class PipelineMetrics:
    """Tracks metrics for pipeline execution"""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.layer_times: Dict[str, float] = {}
        self.validation_errors: List[str] = []
        self.warnings: List[str] = []
        
    def start(self):
        self.start_time = datetime.now()
        
    def stop(self):
        self.end_time = datetime.now()
        
    def record_layer_time(self, layer: str, seconds: float):
        self.layer_times[layer] = seconds
        
    def add_error(self, error: str):
        self.validation_errors.append(error)
        
    def add_warning(self, warning: str):
        self.warnings.append(warning)
        
    @property
    def total_time_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_time_seconds": self.total_time_seconds,
            "layer_times": self.layer_times,
            "validation_errors": self.validation_errors,
            "warnings": self.warnings,
        }


class IntegrationPipeline:
    """
    End-to-end pipeline orchestrator for Layer 2 -> Layer 3 -> Layer 4
    
    This class:
    1. Accepts Layer 2 output (national indicators)
    2. Transforms and passes to Layer 3
    3. Transforms Layer 3 output for Layer 4
    4. Returns complete Layer 4 results
    """
    
    def __init__(self):
        self.l2_to_l3_adapter = Layer2ToLayer3Adapter()
        self.l3_to_l4_adapter = Layer3ToLayer4Adapter()
        self._layer2_processor = None
        self._layer3_processor = None
        self._layer4_processor = None
        
    def set_layer2_processor(self, processor):
        """Set the Layer 2 processor (indicator calculator)"""
        self._layer2_processor = processor
        
    def set_layer3_processor(self, processor):
        """Set the Layer 3 processor (operational service)"""
        self._layer3_processor = processor
        
    def set_layer4_processor(self, processor):
        """Set the Layer 4 processor (insights engine)"""
        self._layer4_processor = processor
    
    async def run_full_pipeline(
        self,
        company_profile: Dict[str, Any],
        layer2_input: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete pipeline from Layer 2 to Layer 4
        
        Args:
            company_profile: Company information for context
            layer2_input: Optional pre-computed Layer 2 data
            options: Pipeline options (e.g., skip_validation, cache)
            
        Returns:
            Dictionary with:
            - layer2_output: National indicators
            - layer3_output: Operational indicators
            - layer4_output: Business insights
            - metrics: Pipeline execution metrics
        """
        metrics = PipelineMetrics()
        metrics.start()
        options = options or {}
        
        try:
            # Step 1: Get or compute Layer 2 output
            layer2_start = datetime.now()
            if layer2_input:
                layer2_output = validate_layer2_output(layer2_input)
            elif self._layer2_processor:
                raw_l2 = await self._run_layer2()
                layer2_output = validate_layer2_output(raw_l2)
            else:
                raise ValueError("No Layer 2 input or processor provided")
            metrics.record_layer_time("layer2", (datetime.now() - layer2_start).total_seconds())
            
            # Step 2: Transform and run Layer 3
            layer3_start = datetime.now()
            layer3_input = self.l2_to_l3_adapter.adapt(
                layer2_output,
                company_profile,
                options.get("industry_config")
            )
            
            if self._layer3_processor:
                raw_l3 = await self._run_layer3(layer3_input)
            else:
                # Use adapter to create Layer 3 output from Layer 2
                raw_l3 = self._simulate_layer3(layer2_output, company_profile)
            
            layer3_output = validate_layer3_output(raw_l3)
            metrics.record_layer_time("layer3", (datetime.now() - layer3_start).total_seconds())
            
            # Step 3: Transform and run Layer 4
            layer4_start = datetime.now()
            layer4_input = self.l3_to_l4_adapter.adapt(
                layer3_output,
                company_profile,
                options.get("historical_context"),
                options.get("industry_benchmarks")
            )
            
            if self._layer4_processor:
                layer4_output = await self._run_layer4(layer4_input)
            else:
                # Use built-in Layer 4 components
                layer4_output = await self._run_layer4_builtin(layer3_output, company_profile)
            
            metrics.record_layer_time("layer4", (datetime.now() - layer4_start).total_seconds())
            
            metrics.stop()
            
            return {
                "success": True,
                "layer2_output": layer2_output.dict(),
                "layer3_output": layer3_output.dict(),
                "layer4_output": layer4_output,
                "metrics": metrics.to_dict(),
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            metrics.add_error(str(e))
            metrics.stop()
            return {
                "success": False,
                "error": str(e),
                "metrics": metrics.to_dict(),
            }
    
    async def run_layer2_to_layer3(
        self,
        layer2_output: Dict[str, Any],
        company_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run just the Layer 2 to Layer 3 transformation
        
        Args:
            layer2_output: Layer 2 national indicators
            company_profile: Company information
            
        Returns:
            Layer 3 operational indicators
        """
        l2_validated = validate_layer2_output(layer2_output)
        
        if self._layer3_processor:
            layer3_input = self.l2_to_l3_adapter.adapt(l2_validated, company_profile)
            raw_l3 = await self._run_layer3(layer3_input)
        else:
            raw_l3 = self._simulate_layer3(l2_validated, company_profile)
        
        return validate_layer3_output(raw_l3).dict()
    
    async def run_layer3_to_layer4(
        self,
        layer3_output: Dict[str, Any],
        company_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run just the Layer 3 to Layer 4 transformation
        
        Args:
            layer3_output: Layer 3 operational indicators
            company_profile: Company information
            
        Returns:
            Layer 4 business insights
        """
        l3_validated = validate_layer3_output(layer3_output)
        
        if self._layer4_processor:
            layer4_input = self.l3_to_l4_adapter.adapt(l3_validated, company_profile)
            return await self._run_layer4(layer4_input)
        else:
            return await self._run_layer4_builtin(l3_validated, company_profile)
    
    def _simulate_layer3(
        self,
        layer2_output: Layer2Output,
        company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate Layer 3 processing when no processor is available
        
        This creates a reasonable Layer 3 output from Layer 2 data
        using the adapter's transformation logic.
        """
        now = datetime.now()
        industry = company_profile.get("industry", "general")
        company_id = company_profile.get("company_id", "UNKNOWN")
        company_name = company_profile.get("company_name", "Unknown Company")
        
        # Get relevant indicators grouped by category
        categorized = self.l2_to_l3_adapter.get_relevant_indicators(layer2_output, industry)
        
        # Get industry sensitivity
        sensitivity = self.l2_to_l3_adapter.INDUSTRY_SENSITIVITY.get(
            industry.lower(), 
            self.l2_to_l3_adapter.default_sensitivity
        )
        
        # Calculate category health scores
        supply_chain = self.l2_to_l3_adapter.calculate_category_impact(
            categorized["supply_chain"], sensitivity.get("supply_chain", 1.0)
        )
        workforce = self.l2_to_l3_adapter.calculate_category_impact(
            categorized["workforce"], sensitivity.get("workforce", 1.0)
        )
        infrastructure = self.l2_to_l3_adapter.calculate_category_impact(
            categorized["infrastructure"], sensitivity.get("infrastructure", 1.0)
        )
        cost_pressure = 100 - self.l2_to_l3_adapter.calculate_category_impact(
            categorized["cost_pressure"], sensitivity.get("cost_pressure", 1.0)
        )  # Inverse - high cost pressure is bad
        market = self.l2_to_l3_adapter.calculate_category_impact(
            categorized["market_conditions"], sensitivity.get("market_conditions", 1.0)
        )
        financial = self.l2_to_l3_adapter.calculate_category_impact(
            categorized["financial"], sensitivity.get("financial", 1.0)
        )
        regulatory = 100 - self.l2_to_l3_adapter.calculate_category_impact(
            categorized["regulatory"], sensitivity.get("regulatory", 1.0)
        )  # Inverse - high regulatory burden is bad
        
        # Calculate overall health
        overall = (supply_chain + workforce + infrastructure + financial + market) / 5.0
        
        # Identify critical issues
        critical_issues = []
        if supply_chain < 30:
            critical_issues.append("Critical supply chain disruption")
        if workforce < 30:
            critical_issues.append("Severe workforce shortage")
        if infrastructure < 30:
            critical_issues.append("Major infrastructure issues")
        if cost_pressure > 80:
            critical_issues.append("Extreme cost pressure")
        if financial < 30:
            critical_issues.append("Financial stress detected")
        
        # Generate operational indicators
        indicators = {}
        ops_indicators = [
            ("OPS_SUPPLY_CHAIN", "Supply Chain Index", supply_chain),
            ("OPS_WORKFORCE_AVAIL", "Workforce Availability", workforce),
            ("OPS_INFRASTRUCTURE", "Infrastructure Health", infrastructure),
            ("OPS_COST_PRESSURE", "Cost Pressure Index", cost_pressure),
            ("OPS_MARKET_CONDITIONS", "Market Conditions", market),
            ("OPS_FINANCIAL_HEALTH", "Financial Health", financial),
            ("OPS_REGULATORY_BURDEN", "Regulatory Burden", regulatory),
        ]
        
        for code, name, value in ops_indicators:
            # Determine trend based on Layer 2 trends
            trend = "stable"
            for l2_code, l2_trend in layer2_output.trends.items():
                if l2_code in str(categorized):
                    trend = l2_trend.direction if hasattr(l2_trend, 'direction') else str(l2_trend)
                    break
            
            indicators[code] = {
                "indicator_code": code,
                "indicator_name": name,
                "value": value,
                "trend": trend,
                "impact_score": (value - 50) / 50,  # Convert to -1 to 1
                "contributing_national_indicators": list(layer2_output.indicators.keys())[:3],
                "confidence": 0.85,
            }
        
        return {
            "timestamp": now.isoformat(),
            "company_id": company_id,
            "company_name": company_name,
            "industry": industry,
            "indicators": indicators,
            "supply_chain_health": supply_chain,
            "workforce_health": workforce,
            "infrastructure_health": infrastructure,
            "cost_pressure": cost_pressure,
            "market_conditions": market,
            "financial_health": financial,
            "regulatory_burden": regulatory,
            "overall_operational_health": overall,
            "critical_issues": critical_issues,
            "trends": {code: ind["trend"] for code, ind in indicators.items()},
            "source_national_indicators": list(layer2_output.indicators.keys()),
        }
    
    async def _run_layer2(self) -> Dict[str, Any]:
        """Run Layer 2 processor"""
        if asyncio.iscoroutinefunction(self._layer2_processor.calculate):
            return await self._layer2_processor.calculate()
        return self._layer2_processor.calculate()
    
    async def _run_layer3(self, layer3_input: Layer3Input) -> Dict[str, Any]:
        """Run Layer 3 processor"""
        if asyncio.iscoroutinefunction(self._layer3_processor.process):
            return await self._layer3_processor.process(layer3_input.dict())
        return self._layer3_processor.process(layer3_input.dict())
    
    async def _run_layer4(self, layer4_input: Layer4Input) -> Dict[str, Any]:
        """Run Layer 4 processor"""
        if asyncio.iscoroutinefunction(self._layer4_processor.process):
            return await self._layer4_processor.process(layer4_input.dict())
        return self._layer4_processor.process(layer4_input.dict())
    
    async def _run_layer4_builtin(
        self,
        layer3_output: Layer3Output,
        company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run Layer 4 using built-in components
        
        This imports and uses the Layer 4 components directly.
        Falls back to minimal output if Layer 4 components require 
        database connections that aren't available.
        """
        try:
            # Try to import and use Layer 4 components
            from app.layer4.integration.layer4_orchestrator import Layer4Orchestrator
            
            # Convert Layer 3 output to Layer 4 format
            indicators_dict = self.l3_to_l4_adapter.to_layer4_indicators(layer3_output)
            trends_dict = self.l3_to_l4_adapter.to_layer4_trends(layer3_output)
            
            # Check if orchestrator requires database connections
            # If so, use the standalone components instead
            try:
                # Try using individual Layer 4 engines that don't need DB
                from app.layer4.risk_detection import RuleBasedRiskDetector
                from app.layer4.opportunity_detection import RuleBasedOpportunityDetector
                from app.layer4.recommendation import RecommendationEngine
                
                # Create mock operational data structure
                from app.layer4.mock_data.layer3_mock_generator import OperationalIndicators
                
                # Build operational indicators from Layer 3 output
                # Using the exact field names expected by OperationalIndicators schema
                ops_data = {
                    "timestamp": datetime.now(),
                    "company_id": layer3_output.company_id,
                    # Supply Chain & Logistics
                    "OPS_SUPPLY_CHAIN": layer3_output.supply_chain_health,
                    "OPS_TRANSPORT_AVAIL": layer3_output.supply_chain_health * 0.95,
                    "OPS_LOGISTICS_COST": 100 - layer3_output.cost_pressure,
                    "OPS_IMPORT_FLOW": layer3_output.supply_chain_health * 0.9,
                    # Workforce & Operations
                    "OPS_WORKFORCE_AVAIL": layer3_output.workforce_health,
                    "OPS_LABOR_COST": 100 - layer3_output.cost_pressure * 0.7,
                    "OPS_PRODUCTIVITY": layer3_output.workforce_health * 0.9,
                    # Infrastructure & Resources
                    "OPS_POWER_RELIABILITY": layer3_output.infrastructure_health,
                    "OPS_FUEL_AVAIL": layer3_output.infrastructure_health * 0.9,
                    "OPS_WATER_SUPPLY": layer3_output.infrastructure_health * 0.95,
                    "OPS_INTERNET_CONNECTIVITY": layer3_output.infrastructure_health * 0.85,
                    # Cost Pressures
                    "OPS_COST_PRESSURE": layer3_output.cost_pressure,
                    "OPS_RAW_MATERIAL_COST": 100 - layer3_output.cost_pressure,
                    "OPS_ENERGY_COST": 100 - layer3_output.cost_pressure * 0.8,
                    # Market Conditions
                    "OPS_DEMAND_LEVEL": layer3_output.market_conditions,
                    "OPS_COMPETITION_INTENSITY": 50.0,  # Neutral default
                    "OPS_PRICING_POWER": layer3_output.market_conditions * 0.85,
                    # Financial Operations
                    "OPS_CASH_FLOW": layer3_output.financial_health,
                    "OPS_CREDIT_AVAIL": layer3_output.financial_health * 0.9,
                    "OPS_PAYMENT_DELAYS": 100 - layer3_output.financial_health * 0.15,
                    # Regulatory & Compliance
                    "OPS_REGULATORY_BURDEN": layer3_output.regulatory_burden,
                    "OPS_COMPLIANCE_COST": layer3_output.regulatory_burden * 0.9,
                    # Trends
                    "trends": {k: v.value if hasattr(v, 'value') else str(v) 
                              for k, v in layer3_output.trends.items()},
                }
                
                operational_indicators = OperationalIndicators(**ops_data)
                
                # Run engines with required arguments
                company_id = layer3_output.company_id
                industry = layer3_output.industry
                
                risk_detector = RuleBasedRiskDetector()
                risks = risk_detector.detect_risks(
                    company_id=company_id,
                    industry=industry,
                    indicators=operational_indicators,
                    company_profile=company_profile
                )
                
                opp_identifier = RuleBasedOpportunityDetector()
                opportunities = opp_identifier.detect_opportunities(
                    company_id=company_id,
                    industry=industry,
                    indicators=operational_indicators
                )
                
                # Generate recommendations for each insight
                rec_engine = RecommendationEngine()
                recommendations = []
                
                # Generate recommendations for risks
                for risk in risks:
                    recs = rec_engine.generate_recommendations(risk, company_profile)
                    recommendations.extend(recs)
                    
                # Generate recommendations for opportunities
                for opp in opportunities:
                    recs = rec_engine.generate_recommendations(opp, company_profile)
                    recommendations.extend(recs)
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "company_id": layer3_output.company_id,
                    "company_name": layer3_output.company_name,
                    "industry": layer3_output.industry,
                    "summary": {
                        "overall_health": layer3_output.overall_operational_health,
                        "risk_level": "high" if len(risks) > 3 else "medium" if len(risks) > 0 else "low",
                        "risk_count": len(risks),
                        "opportunity_count": len(opportunities),
                        "recommendation_count": len(recommendations),
                    },
                    "risks": [r.model_dump() if hasattr(r, 'model_dump') else r.dict() for r in risks],
                    "opportunities": [o.model_dump() if hasattr(o, 'model_dump') else o.dict() for o in opportunities],
                    "recommendations": [r.model_dump() if hasattr(r, 'model_dump') else r.dict() for r in recommendations],
                    "source": "layer4_engines",
                }
                
            except Exception as engine_error:
                logger.warning(f"Could not use Layer 4 engines: {engine_error}")
                return self._minimal_layer4_output(layer3_output, company_profile)
            
        except ImportError as e:
            logger.warning(f"Could not import Layer 4 components: {e}")
            return self._minimal_layer4_output(layer3_output, company_profile)
        except Exception as e:
            logger.warning(f"Layer 4 execution failed, using minimal output: {e}")
            return self._minimal_layer4_output(layer3_output, company_profile)
    
    def _minimal_layer4_output(
        self,
        layer3_output: Layer3Output,
        company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate minimal Layer 4 output when full processing isn't available
        """
        critical = self.l3_to_l4_adapter.get_critical_indicators(layer3_output)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "company_id": layer3_output.company_id,
            "company_name": layer3_output.company_name,
            "summary": {
                "overall_health": layer3_output.overall_operational_health,
                "risk_level": "high" if critical else "medium",
                "critical_count": len(critical),
            },
            "risks": [
                {
                    "category": c["category"],
                    "severity": c["severity"],
                    "value": c["value"],
                }
                for c in critical
            ],
            "opportunities": [],
            "recommendations": [],
            "source": "minimal_layer4",
        }


class PipelineBuilder:
    """
    Builder pattern for creating configured pipelines
    """
    
    def __init__(self):
        self._pipeline = IntegrationPipeline()
        
    def with_layer2(self, processor) -> 'PipelineBuilder':
        """Add Layer 2 processor"""
        self._pipeline.set_layer2_processor(processor)
        return self
        
    def with_layer3(self, processor) -> 'PipelineBuilder':
        """Add Layer 3 processor"""
        self._pipeline.set_layer3_processor(processor)
        return self
        
    def with_layer4(self, processor) -> 'PipelineBuilder':
        """Add Layer 4 processor"""
        self._pipeline.set_layer4_processor(processor)
        return self
        
    def build(self) -> IntegrationPipeline:
        """Build the pipeline"""
        return self._pipeline


# Convenience function
def create_pipeline() -> IntegrationPipeline:
    """Create a new integration pipeline"""
    return IntegrationPipeline()
