"""
Scenario Simulation Module.

Provides what-if analysis capabilities including:
- Scenario definitions
- Impact propagation modeling
- Sensitivity analysis
- Monte Carlo simulation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import math
import random


class ScenarioType(Enum):
    """Types of scenarios."""
    SUPPLY_SHOCK = "supply_shock"
    DEMAND_SURGE = "demand_surge"
    COST_INCREASE = "cost_increase"
    MARKET_DISRUPTION = "market_disruption"
    REGULATORY_CHANGE = "regulatory_change"
    TECHNOLOGY_SHIFT = "technology_shift"
    CUSTOM = "custom"


class ImpactType(Enum):
    """Types of impact effects."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    CASCADING = "cascading"


@dataclass
class ScenarioParameter:
    """Parameter for a scenario."""
    name: str
    base_value: float
    modified_value: float
    unit: str = ""
    description: str = ""


@dataclass
class Scenario:
    """Scenario definition for simulation."""
    scenario_id: str
    name: str
    description: str
    scenario_type: ScenarioType
    
    # Parameters to modify
    parameters: List[ScenarioParameter] = field(default_factory=list)
    
    # Affected indicators
    affected_indicators: Dict[str, float] = field(default_factory=dict)
    
    # Time parameters
    duration_days: int = 30
    onset_days: int = 0  # Days until scenario starts
    recovery_days: int = 0  # Days to recover after scenario ends
    
    # Probability
    probability: float = 0.5  # 0-1
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class ImpactPropagation:
    """Impact propagation from one indicator to others."""
    source_indicator: str
    target_indicator: str
    impact_type: ImpactType
    
    # Propagation parameters
    propagation_factor: float = 0.5  # How much of source change propagates
    delay_days: int = 0  # Days before impact manifests
    decay_rate: float = 0.1  # How fast impact decays
    
    # Thresholds
    min_trigger: float = 0.1  # Minimum source change to trigger
    max_impact: float = 1.0  # Maximum impact on target


@dataclass
class SimulationResult:
    """Result from running a scenario simulation."""
    simulation_id: str
    scenario_id: str
    company_id: str
    run_at: datetime
    
    # Results
    baseline_indicators: Dict[str, float] = field(default_factory=dict)
    simulated_indicators: Dict[str, float] = field(default_factory=dict)
    indicator_changes: Dict[str, float] = field(default_factory=dict)
    
    # Impact assessment
    overall_impact: float = 0.0
    impact_direction: str = "neutral"
    severity: str = "low"
    
    # Time series (daily values over simulation period)
    daily_indicators: List[Dict[str, float]] = field(default_factory=list)
    
    # Propagation effects
    propagation_effects: Dict[str, List[str]] = field(default_factory=dict)
    
    # Statistics
    peak_impact: float = 0.0
    peak_day: int = 0
    recovery_time_days: int = 0


@dataclass
class SensitivityAnalysis:
    """Sensitivity analysis result."""
    analysis_id: str
    scenario_id: str
    company_id: str
    
    # Parameter sensitivities
    parameter_sensitivities: Dict[str, float] = field(default_factory=dict)
    
    # Most sensitive parameters
    top_sensitive_params: List[str] = field(default_factory=list)
    
    # Elasticity (% change in output / % change in input)
    elasticities: Dict[str, float] = field(default_factory=dict)
    
    # Critical thresholds
    critical_thresholds: Dict[str, float] = field(default_factory=dict)


class ScenarioSimulator:
    """
    Scenario simulation engine for what-if analysis.
    
    Supports scenario definition, impact propagation,
    and sensitivity analysis.
    """
    
    def __init__(self):
        """Initialize the scenario simulator."""
        self._scenarios: Dict[str, Scenario] = {}
        self._propagation_rules: List[ImpactPropagation] = []
        self._simulation_results: Dict[str, SimulationResult] = {}
        self._scenario_counter = 0
        self._simulation_counter = 0
        
        # Initialize default propagation rules
        self._initialize_propagation_rules()
    
    def _initialize_propagation_rules(self) -> None:
        """Initialize default impact propagation rules."""
        # Supply chain affects production
        self._propagation_rules.append(
            ImpactPropagation(
                source_indicator="OPS_SUPPLY_CHAIN",
                target_indicator="OPS_PRODUCTION",
                impact_type=ImpactType.DIRECT,
                propagation_factor=0.7,
                delay_days=3,
            )
        )
        
        # Production affects inventory
        self._propagation_rules.append(
            ImpactPropagation(
                source_indicator="OPS_PRODUCTION",
                target_indicator="OPS_INVENTORY",
                impact_type=ImpactType.DIRECT,
                propagation_factor=0.6,
                delay_days=1,
            )
        )
        
        # Demand affects revenue
        self._propagation_rules.append(
            ImpactPropagation(
                source_indicator="OPS_DEMAND",
                target_indicator="OPS_REVENUE",
                impact_type=ImpactType.DIRECT,
                propagation_factor=0.8,
                delay_days=0,
            )
        )
        
        # Cost affects profit margin
        self._propagation_rules.append(
            ImpactPropagation(
                source_indicator="OPS_COST",
                target_indicator="OPS_PROFIT_MARGIN",
                impact_type=ImpactType.DIRECT,
                propagation_factor=-0.5,  # Inverse relationship
                delay_days=0,
            )
        )
        
        # Revenue affects cash flow
        self._propagation_rules.append(
            ImpactPropagation(
                source_indicator="OPS_REVENUE",
                target_indicator="OPS_CASH_FLOW",
                impact_type=ImpactType.CASCADING,
                propagation_factor=0.6,
                delay_days=7,
            )
        )
    
    def create_scenario(
        self,
        name: str,
        description: str,
        scenario_type: ScenarioType,
        affected_indicators: Dict[str, float],
        duration_days: int = 30,
        probability: float = 0.5,
        parameters: Optional[List[ScenarioParameter]] = None,
    ) -> Scenario:
        """
        Create a new scenario.
        
        Args:
            name: Scenario name
            description: Description of the scenario
            scenario_type: Type of scenario
            affected_indicators: Dict of indicator -> change multiplier
            duration_days: How long the scenario lasts
            probability: Probability of scenario occurring
            parameters: Optional custom parameters
            
        Returns:
            Created Scenario
        """
        self._scenario_counter += 1
        scenario_id = f"scenario_{self._scenario_counter}"
        
        scenario = Scenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            scenario_type=scenario_type,
            parameters=parameters or [],
            affected_indicators=affected_indicators,
            duration_days=duration_days,
            probability=probability,
        )
        
        self._scenarios[scenario_id] = scenario
        return scenario
    
    def create_preset_scenario(
        self,
        preset: str,
        severity: str = "moderate",
    ) -> Scenario:
        """Create a scenario from presets."""
        severity_multipliers = {
            "mild": 0.5,
            "moderate": 1.0,
            "severe": 1.5,
            "extreme": 2.0,
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        
        presets = {
            "supply_disruption": {
                "name": "Supply Chain Disruption",
                "description": "Major supply chain disruption affecting inputs",
                "type": ScenarioType.SUPPLY_SHOCK,
                "indicators": {
                    "OPS_SUPPLY_CHAIN": -0.3 * multiplier,
                    "OPS_LOGISTICS": -0.2 * multiplier,
                    "OPS_COST": 0.2 * multiplier,
                },
                "duration": 45,
                "probability": 0.3,
            },
            "demand_surge": {
                "name": "Demand Surge",
                "description": "Sudden increase in market demand",
                "type": ScenarioType.DEMAND_SURGE,
                "indicators": {
                    "OPS_DEMAND": 0.4 * multiplier,
                    "OPS_REVENUE": 0.3 * multiplier,
                    "OPS_INVENTORY": -0.2 * multiplier,
                },
                "duration": 30,
                "probability": 0.4,
            },
            "cost_inflation": {
                "name": "Cost Inflation",
                "description": "Significant increase in operational costs",
                "type": ScenarioType.COST_INCREASE,
                "indicators": {
                    "OPS_COST": 0.3 * multiplier,
                    "OPS_PROFIT_MARGIN": -0.25 * multiplier,
                    "OPS_CASH_FLOW": -0.15 * multiplier,
                },
                "duration": 60,
                "probability": 0.5,
            },
            "market_crash": {
                "name": "Market Crash",
                "description": "Major market downturn",
                "type": ScenarioType.MARKET_DISRUPTION,
                "indicators": {
                    "OPS_DEMAND": -0.35 * multiplier,
                    "OPS_REVENUE": -0.4 * multiplier,
                    "OPS_MARKET_SHARE": -0.2 * multiplier,
                    "OPS_CASH_FLOW": -0.3 * multiplier,
                },
                "duration": 90,
                "probability": 0.15,
            },
        }
        
        preset_config = presets.get(preset)
        if not preset_config:
            raise ValueError(f"Unknown preset: {preset}")
        
        return self.create_scenario(
            name=preset_config["name"],
            description=preset_config["description"],
            scenario_type=preset_config["type"],
            affected_indicators=preset_config["indicators"],
            duration_days=preset_config["duration"],
            probability=preset_config["probability"],
        )
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID."""
        return self._scenarios.get(scenario_id)
    
    def list_scenarios(self) -> List[Scenario]:
        """List all scenarios."""
        return list(self._scenarios.values())
    
    def run_simulation(
        self,
        scenario_id: str,
        company_id: str,
        baseline_indicators: Dict[str, float],
        simulation_days: Optional[int] = None,
    ) -> SimulationResult:
        """
        Run a scenario simulation.
        
        Args:
            scenario_id: Scenario to simulate
            company_id: Company to simulate for
            baseline_indicators: Current indicator values
            simulation_days: Override scenario duration
            
        Returns:
            SimulationResult with outcomes
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        self._simulation_counter += 1
        simulation_id = f"sim_{self._simulation_counter}"
        
        duration = simulation_days or scenario.duration_days
        
        # Initialize simulation
        current_indicators = baseline_indicators.copy()
        daily_values: List[Dict[str, float]] = []
        propagation_effects: Dict[str, List[str]] = {}
        
        peak_impact = 0.0
        peak_day = 0
        
        # Run day-by-day simulation
        for day in range(duration):
            # Apply direct scenario effects
            day_indicators = current_indicators.copy()
            
            for indicator, change in scenario.affected_indicators.items():
                if indicator in day_indicators:
                    # Gradual onset and decay
                    effect_factor = self._calculate_effect_factor(
                        day, duration, scenario.onset_days, scenario.recovery_days
                    )
                    day_indicators[indicator] += change * effect_factor
                    day_indicators[indicator] = max(0.0, min(1.0, day_indicators[indicator]))
            
            # Apply propagation effects
            for rule in self._propagation_rules:
                if rule.source_indicator in scenario.affected_indicators:
                    if day >= rule.delay_days:
                        source_change = scenario.affected_indicators[rule.source_indicator]
                        
                        if abs(source_change) >= rule.min_trigger:
                            effect_factor = self._calculate_effect_factor(
                                day - rule.delay_days,
                                duration - rule.delay_days,
                                0,
                                0,
                            )
                            
                            propagated_change = (
                                source_change *
                                rule.propagation_factor *
                                effect_factor *
                                (1 - rule.decay_rate * (day - rule.delay_days) / duration)
                            )
                            
                            propagated_change = max(-rule.max_impact, min(rule.max_impact, propagated_change))
                            
                            if rule.target_indicator in day_indicators:
                                day_indicators[rule.target_indicator] += propagated_change
                                day_indicators[rule.target_indicator] = max(
                                    0.0, min(1.0, day_indicators[rule.target_indicator])
                                )
                                
                                # Track propagation
                                if rule.source_indicator not in propagation_effects:
                                    propagation_effects[rule.source_indicator] = []
                                if rule.target_indicator not in propagation_effects[rule.source_indicator]:
                                    propagation_effects[rule.source_indicator].append(
                                        rule.target_indicator
                                    )
            
            daily_values.append(day_indicators.copy())
            
            # Track peak impact
            day_impact = sum(
                abs(day_indicators.get(k, 0) - baseline_indicators.get(k, 0))
                for k in baseline_indicators.keys()
            ) / len(baseline_indicators)
            
            if day_impact > peak_impact:
                peak_impact = day_impact
                peak_day = day
            
            current_indicators = day_indicators
        
        # Calculate final changes
        final_indicators = daily_values[-1] if daily_values else baseline_indicators
        indicator_changes = {
            k: final_indicators.get(k, 0) - baseline_indicators.get(k, 0)
            for k in baseline_indicators.keys()
        }
        
        # Calculate overall impact
        overall_impact = sum(abs(v) for v in indicator_changes.values()) / len(indicator_changes)
        
        # Determine direction and severity
        avg_change = sum(indicator_changes.values()) / len(indicator_changes)
        if avg_change > 0.05:
            impact_direction = "positive"
        elif avg_change < -0.05:
            impact_direction = "negative"
        else:
            impact_direction = "neutral"
        
        if overall_impact >= 0.3:
            severity = "critical"
        elif overall_impact >= 0.2:
            severity = "high"
        elif overall_impact >= 0.1:
            severity = "medium"
        else:
            severity = "low"
        
        # Estimate recovery time
        recovery_time = self._estimate_recovery_time(
            baseline_indicators, final_indicators, scenario
        )
        
        result = SimulationResult(
            simulation_id=simulation_id,
            scenario_id=scenario_id,
            company_id=company_id,
            run_at=datetime.now(),
            baseline_indicators=baseline_indicators,
            simulated_indicators=final_indicators,
            indicator_changes=indicator_changes,
            overall_impact=overall_impact,
            impact_direction=impact_direction,
            severity=severity,
            daily_indicators=daily_values,
            propagation_effects=propagation_effects,
            peak_impact=peak_impact,
            peak_day=peak_day,
            recovery_time_days=recovery_time,
        )
        
        self._simulation_results[simulation_id] = result
        return result
    
    def _calculate_effect_factor(
        self,
        day: int,
        duration: int,
        onset_days: int,
        recovery_days: int,
    ) -> float:
        """Calculate effect factor for a given day."""
        if day < onset_days:
            # Gradual onset
            return day / onset_days if onset_days > 0 else 0.0
        elif day > duration - recovery_days:
            # Gradual recovery
            remaining = duration - day
            return remaining / recovery_days if recovery_days > 0 else 0.0
        else:
            # Full effect
            return 1.0
    
    def _estimate_recovery_time(
        self,
        baseline: Dict[str, float],
        final: Dict[str, float],
        scenario: Scenario,
    ) -> int:
        """Estimate time to recover from scenario effects."""
        total_change = sum(
            abs(final.get(k, 0) - baseline.get(k, 0))
            for k in baseline.keys()
        )
        
        # Assume 10% recovery per week
        recovery_rate = 0.1 / 7  # per day
        
        if recovery_rate > 0 and total_change > 0:
            recovery_days = int(total_change / recovery_rate)
            return min(recovery_days, 365)  # Cap at 1 year
        
        return 0
    
    def run_monte_carlo(
        self,
        scenario_id: str,
        company_id: str,
        baseline_indicators: Dict[str, float],
        num_simulations: int = 100,
        variance_factor: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for uncertainty analysis.
        
        Args:
            scenario_id: Scenario to simulate
            company_id: Company to simulate for
            baseline_indicators: Current indicator values
            num_simulations: Number of simulations to run
            variance_factor: Variance for random perturbation
            
        Returns:
            Statistical results from simulations
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        results: List[SimulationResult] = []
        
        for i in range(num_simulations):
            # Perturb scenario parameters
            perturbed_indicators = {}
            for indicator, change in scenario.affected_indicators.items():
                perturbation = random.gauss(0, variance_factor * abs(change))
                perturbed_indicators[indicator] = change + perturbation
            
            # Create temporary perturbed scenario
            temp_scenario = Scenario(
                scenario_id=f"temp_{i}",
                name=scenario.name,
                description=scenario.description,
                scenario_type=scenario.scenario_type,
                affected_indicators=perturbed_indicators,
                duration_days=scenario.duration_days,
                probability=scenario.probability,
            )
            
            self._scenarios[temp_scenario.scenario_id] = temp_scenario
            
            result = self.run_simulation(
                temp_scenario.scenario_id,
                company_id,
                baseline_indicators,
            )
            results.append(result)
            
            # Clean up temp scenario
            del self._scenarios[temp_scenario.scenario_id]
        
        # Calculate statistics
        impacts = [r.overall_impact for r in results]
        
        mean_impact = sum(impacts) / len(impacts)
        variance = sum((x - mean_impact) ** 2 for x in impacts) / len(impacts)
        std_dev = math.sqrt(variance)
        
        sorted_impacts = sorted(impacts)
        percentile_5 = sorted_impacts[int(len(sorted_impacts) * 0.05)]
        percentile_95 = sorted_impacts[int(len(sorted_impacts) * 0.95)]
        
        # Count severity distribution
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for r in results:
            severity_counts[r.severity] += 1
        
        return {
            "num_simulations": num_simulations,
            "mean_impact": mean_impact,
            "std_dev": std_dev,
            "min_impact": min(impacts),
            "max_impact": max(impacts),
            "percentile_5": percentile_5,
            "percentile_95": percentile_95,
            "severity_distribution": severity_counts,
            "positive_outcomes": sum(1 for r in results if r.impact_direction == "positive"),
            "negative_outcomes": sum(1 for r in results if r.impact_direction == "negative"),
        }
    
    def run_sensitivity_analysis(
        self,
        scenario_id: str,
        company_id: str,
        baseline_indicators: Dict[str, float],
        perturbation: float = 0.1,
    ) -> SensitivityAnalysis:
        """
        Run sensitivity analysis on scenario parameters.
        
        Args:
            scenario_id: Scenario to analyze
            company_id: Company to analyze for
            baseline_indicators: Current indicator values
            perturbation: Perturbation factor for sensitivity
            
        Returns:
            SensitivityAnalysis result
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Run baseline simulation
        baseline_result = self.run_simulation(
            scenario_id, company_id, baseline_indicators
        )
        baseline_impact = baseline_result.overall_impact
        
        sensitivities: Dict[str, float] = {}
        elasticities: Dict[str, float] = {}
        
        # Perturb each indicator and measure sensitivity
        for indicator, base_change in scenario.affected_indicators.items():
            # Increase by perturbation
            perturbed_up = scenario.affected_indicators.copy()
            perturbed_up[indicator] = base_change * (1 + perturbation)
            
            temp_scenario = Scenario(
                scenario_id="temp_sens",
                name=scenario.name,
                description=scenario.description,
                scenario_type=scenario.scenario_type,
                affected_indicators=perturbed_up,
                duration_days=scenario.duration_days,
                probability=scenario.probability,
            )
            self._scenarios["temp_sens"] = temp_scenario
            
            result_up = self.run_simulation(
                "temp_sens", company_id, baseline_indicators
            )
            
            del self._scenarios["temp_sens"]
            
            # Calculate sensitivity
            impact_change = result_up.overall_impact - baseline_impact
            sensitivities[indicator] = abs(impact_change / perturbation)
            
            # Calculate elasticity
            if baseline_impact > 0:
                pct_impact_change = impact_change / baseline_impact
                elasticities[indicator] = pct_impact_change / perturbation
            else:
                elasticities[indicator] = 0.0
        
        # Sort by sensitivity
        sorted_params = sorted(
            sensitivities.keys(),
            key=lambda x: sensitivities[x],
            reverse=True,
        )
        
        # Find critical thresholds
        critical_thresholds: Dict[str, float] = {}
        for indicator in scenario.affected_indicators.keys():
            # Threshold where impact becomes "critical" (0.3)
            if sensitivities.get(indicator, 0) > 0:
                threshold = 0.3 / sensitivities[indicator] * perturbation
                critical_thresholds[indicator] = threshold
        
        return SensitivityAnalysis(
            analysis_id=f"sens_{self._simulation_counter}",
            scenario_id=scenario_id,
            company_id=company_id,
            parameter_sensitivities=sensitivities,
            top_sensitive_params=sorted_params[:5],
            elasticities=elasticities,
            critical_thresholds=critical_thresholds,
        )
    
    def compare_scenarios(
        self,
        scenario_ids: List[str],
        company_id: str,
        baseline_indicators: Dict[str, float],
    ) -> Dict[str, Any]:
        """Compare multiple scenarios."""
        results = {}
        
        for scenario_id in scenario_ids:
            if scenario_id in self._scenarios:
                result = self.run_simulation(
                    scenario_id, company_id, baseline_indicators
                )
                results[scenario_id] = {
                    "name": self._scenarios[scenario_id].name,
                    "overall_impact": result.overall_impact,
                    "direction": result.impact_direction,
                    "severity": result.severity,
                    "peak_impact": result.peak_impact,
                    "recovery_days": result.recovery_time_days,
                }
        
        # Rank by impact
        ranked = sorted(
            results.items(),
            key=lambda x: x[1]["overall_impact"],
            reverse=True,
        )
        
        return {
            "scenarios": results,
            "ranking": [s[0] for s in ranked],
            "worst_case": ranked[0][0] if ranked else None,
            "best_case": ranked[-1][0] if ranked else None,
        }
    
    def add_propagation_rule(self, rule: ImpactPropagation) -> None:
        """Add a custom propagation rule."""
        self._propagation_rules.append(rule)
    
    def get_simulation_result(
        self,
        simulation_id: str,
    ) -> Optional[SimulationResult]:
        """Get a simulation result by ID."""
        return self._simulation_results.get(simulation_id)
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario."""
        if scenario_id in self._scenarios:
            del self._scenarios[scenario_id]
            return True
        return False
