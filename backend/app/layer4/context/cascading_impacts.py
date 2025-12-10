"""
Layer 4: Cascading Impact Analyzer

Models how impacts propagate through interconnected systems.
Tracks cause-and-effect chains for comprehensive impact assessment.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class ImpactPhase(Enum):
    """Phases of cascading impact"""
    IMMEDIATE = "immediate"  # 0-24 hours
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1+ months


@dataclass
class CascadeNode:
    """A node in the cascade chain"""
    node_id: str
    node_type: str  # 'event', 'industry', 'indicator', 'outcome'
    name: str
    description: str
    
    # Impact characteristics
    impact_magnitude: float  # 0-1
    impact_phase: ImpactPhase
    delay_days: int
    
    # Parent nodes (what caused this)
    parent_nodes: List[str] = field(default_factory=list)
    
    # Child nodes (what this causes)
    child_nodes: List[str] = field(default_factory=list)


@dataclass
class CascadeChain:
    """A complete cascade chain from trigger to outcomes"""
    chain_id: str
    trigger_event: str
    trigger_severity: float
    
    # All nodes in the chain
    nodes: List[CascadeNode]
    
    # Summary metrics
    total_depth: int
    total_affected_areas: int
    peak_impact_magnitude: float
    peak_impact_phase: ImpactPhase
    
    # Timeline
    estimated_resolution_days: int
    
    # Industries affected
    affected_industries: List[str]
    
    # Key outcomes
    key_outcomes: List[str]
    
    # Intervention points
    intervention_points: List[Dict[str, Any]]
    
    # Generated timestamp
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PropagationModel:
    """Model for how a specific event type propagates"""
    event_type: str
    initial_domain: str
    
    # Propagation rules
    propagation_paths: List[Dict[str, Any]]
    """
    List of propagation paths:
    [
        {
            "from": "port_operations",
            "to": "import_availability",
            "delay_days": 2,
            "magnitude_multiplier": 0.9
        }
    ]
    """
    
    # Dampening factor per step
    dampening_factor: float
    
    # Maximum propagation depth
    max_depth: int


class CascadingImpactAnalyzer:
    """
    Analyzes cascading impacts through interconnected systems.
    
    Features:
    - Multi-hop impact propagation
    - Timeline-based cascade modeling
    - Intervention point identification
    - Resolution timeline estimation
    """
    
    def __init__(self):
        self._propagation_models = self._load_propagation_models()
        self._cascade_templates = self._load_cascade_templates()
        
        logger.info(f"Initialized CascadingImpactAnalyzer with {len(self._propagation_models)} propagation models")
    
    def analyze_cascade(
        self,
        trigger_event: str,
        trigger_severity: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> CascadeChain:
        """
        Analyze full cascade chain from trigger event.
        
        Args:
            trigger_event: Initial triggering event
            trigger_severity: Severity of trigger (0-1)
            context: Optional additional context
            
        Returns:
            Complete CascadeChain analysis
        """
        # Find matching propagation model
        model = self._find_propagation_model(trigger_event)
        
        if model:
            return self._build_cascade_from_model(model, trigger_severity, context)
        else:
            # Use template-based approach
            return self._build_cascade_from_templates(trigger_event, trigger_severity, context)
    
    def trace_impact_path(
        self,
        source: str,
        target: str,
        max_hops: int = 5,
    ) -> Optional[List[CascadeNode]]:
        """
        Trace the path from source to target through cascade chains.
        
        Args:
            source: Starting point (event or domain)
            target: End point (outcome or domain)
            max_hops: Maximum hops to search
            
        Returns:
            Path of CascadeNodes if found, None otherwise
        """
        # BFS to find path
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            if len(path) > max_hops:
                continue
            
            # Get neighbors from all propagation models
            neighbors = self._get_neighbors(current)
            
            for neighbor, delay, magnitude in neighbors:
                if neighbor == target:
                    # Found path
                    return self._build_path_nodes(path + [target])
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_timeline_projection(
        self,
        cascade: CascadeChain,
    ) -> List[Dict[str, Any]]:
        """
        Get timeline projection for cascade.
        
        Args:
            cascade: Cascade chain to project
            
        Returns:
            Timeline of expected events
        """
        timeline = []
        base_date = datetime.now()
        
        # Group nodes by phase
        phase_order = [ImpactPhase.IMMEDIATE, ImpactPhase.SHORT_TERM, 
                       ImpactPhase.MEDIUM_TERM, ImpactPhase.LONG_TERM]
        
        for phase in phase_order:
            phase_nodes = [n for n in cascade.nodes if n.impact_phase == phase]
            
            if phase_nodes:
                # Calculate date range for phase
                min_delay = min(n.delay_days for n in phase_nodes)
                max_delay = max(n.delay_days for n in phase_nodes)
                
                timeline.append({
                    "phase": phase.value,
                    "start_date": (base_date + timedelta(days=min_delay)).strftime("%Y-%m-%d"),
                    "end_date": (base_date + timedelta(days=max_delay)).strftime("%Y-%m-%d"),
                    "events": [
                        {
                            "name": n.name,
                            "description": n.description,
                            "day": n.delay_days,
                            "magnitude": round(n.impact_magnitude, 2),
                        }
                        for n in sorted(phase_nodes, key=lambda x: x.delay_days)
                    ],
                })
        
        return timeline
    
    def identify_intervention_points(
        self,
        cascade: CascadeChain,
    ) -> List[Dict[str, Any]]:
        """
        Identify points where intervention can break the cascade.
        
        Args:
            cascade: Cascade chain to analyze
            
        Returns:
            List of intervention points with recommendations
        """
        interventions = []
        
        for node in cascade.nodes:
            # High-impact nodes with multiple children are good intervention points
            if len(node.child_nodes) >= 2 and node.impact_magnitude >= 0.5:
                interventions.append({
                    "node_id": node.node_id,
                    "node_name": node.name,
                    "phase": node.impact_phase.value,
                    "delay_days": node.delay_days,
                    "downstream_impact": len(node.child_nodes),
                    "intervention_effectiveness": self._calculate_intervention_effectiveness(node, cascade),
                    "recommended_actions": self._get_intervention_actions(node),
                    "urgency": "critical" if node.delay_days <= 2 else "high" if node.delay_days <= 7 else "moderate",
                })
        
        # Sort by effectiveness and urgency
        interventions.sort(
            key=lambda i: (i["urgency"] == "critical", i["intervention_effectiveness"]),
            reverse=True,
        )
        
        return interventions
    
    def estimate_total_impact(
        self,
        cascade: CascadeChain,
        industry: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Estimate total impact of cascade.
        
        Args:
            cascade: Cascade chain to analyze
            industry: Optional industry filter
            
        Returns:
            Impact estimation summary
        """
        # Filter nodes by industry if specified
        if industry:
            relevant_nodes = [
                n for n in cascade.nodes
                if industry.lower() in n.name.lower() or industry.lower() in n.description.lower()
            ]
        else:
            relevant_nodes = cascade.nodes
        
        if not relevant_nodes:
            return {
                "total_impact_score": 0.0,
                "industry_filter": industry,
                "message": "No relevant impacts found",
            }
        
        # Calculate cumulative impact (with dampening)
        total_impact = sum(n.impact_magnitude for n in relevant_nodes)
        peak_impact = max(n.impact_magnitude for n in relevant_nodes)
        avg_impact = total_impact / len(relevant_nodes)
        
        # Phase breakdown
        phase_impacts = defaultdict(float)
        for node in relevant_nodes:
            phase_impacts[node.impact_phase.value] += node.impact_magnitude
        
        return {
            "total_impact_score": round(total_impact, 2),
            "peak_impact": round(peak_impact, 2),
            "average_impact": round(avg_impact, 2),
            "affected_areas": len(relevant_nodes),
            "phase_breakdown": dict(phase_impacts),
            "estimated_recovery_days": cascade.estimated_resolution_days,
            "severity_rating": self._rate_severity(peak_impact),
            "industry_filter": industry,
        }
    
    def _find_propagation_model(self, trigger_event: str) -> Optional[PropagationModel]:
        """Find matching propagation model for event."""
        for model in self._propagation_models:
            if model.event_type.lower() in trigger_event.lower() or trigger_event.lower() in model.event_type.lower():
                return model
        return None
    
    def _build_cascade_from_model(
        self,
        model: PropagationModel,
        severity: float,
        context: Optional[Dict[str, Any]],
    ) -> CascadeChain:
        """Build cascade chain using propagation model."""
        nodes: List[CascadeNode] = []
        node_id_counter = 0
        
        # Create trigger node
        trigger_node = CascadeNode(
            node_id=f"node_{node_id_counter}",
            node_type="event",
            name=model.event_type,
            description=f"Initial trigger: {model.event_type}",
            impact_magnitude=severity,
            impact_phase=ImpactPhase.IMMEDIATE,
            delay_days=0,
            parent_nodes=[],
            child_nodes=[],
        )
        nodes.append(trigger_node)
        node_id_counter += 1
        
        # Track current magnitude and process queue
        current_level_nodes = {model.initial_domain: trigger_node}
        
        for depth in range(1, model.max_depth + 1):
            next_level_nodes = {}
            
            for path in model.propagation_paths:
                from_domain = path["from"]
                to_domain = path["to"]
                
                if from_domain in current_level_nodes:
                    parent = current_level_nodes[from_domain]
                    
                    # Calculate magnitude with dampening
                    magnitude = parent.impact_magnitude * path["magnitude_multiplier"] * model.dampening_factor
                    
                    if magnitude > 0.1:  # Threshold to stop cascade
                        delay = parent.delay_days + path["delay_days"]
                        phase = self._determine_phase(delay)
                        
                        # Check if we already created this node
                        if to_domain not in next_level_nodes:
                            new_node = CascadeNode(
                                node_id=f"node_{node_id_counter}",
                                node_type="outcome" if depth == model.max_depth else "domain",
                                name=to_domain,
                                description=f"Impact on {to_domain}",
                                impact_magnitude=magnitude,
                                impact_phase=phase,
                                delay_days=delay,
                                parent_nodes=[parent.node_id],
                                child_nodes=[],
                            )
                            parent.child_nodes.append(new_node.node_id)
                            nodes.append(new_node)
                            next_level_nodes[to_domain] = new_node
                            node_id_counter += 1
            
            current_level_nodes = next_level_nodes
            if not current_level_nodes:
                break
        
        # Build chain summary
        affected_industries = set()
        outcomes = []
        
        for node in nodes:
            if node.node_type == "outcome":
                outcomes.append(node.name)
            # Extract industry from node names
            for ind in ["retail", "manufacturing", "logistics", "hospitality", "agriculture"]:
                if ind in node.name.lower():
                    affected_industries.add(ind)
        
        return CascadeChain(
            chain_id=f"cascade_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            trigger_event=model.event_type,
            trigger_severity=severity,
            nodes=nodes,
            total_depth=len(set(n.delay_days for n in nodes)),
            total_affected_areas=len(nodes),
            peak_impact_magnitude=max(n.impact_magnitude for n in nodes),
            peak_impact_phase=max(nodes, key=lambda n: n.impact_magnitude).impact_phase,
            estimated_resolution_days=max(n.delay_days for n in nodes) + 7,
            affected_industries=list(affected_industries),
            key_outcomes=outcomes[:5],
            intervention_points=[],
        )
    
    def _build_cascade_from_templates(
        self,
        trigger_event: str,
        severity: float,
        context: Optional[Dict[str, Any]],
    ) -> CascadeChain:
        """Build cascade chain using templates when no model exists."""
        # Find matching template
        template = None
        for t in self._cascade_templates:
            if t["trigger"] in trigger_event.lower() or trigger_event.lower() in t["trigger"]:
                template = t
                break
        
        if not template:
            # Use generic template
            template = self._cascade_templates[0]
        
        # Build nodes from template
        nodes = []
        node_id = 0
        
        for stage in template["stages"]:
            node = CascadeNode(
                node_id=f"node_{node_id}",
                node_type=stage["type"],
                name=stage["name"],
                description=stage["description"],
                impact_magnitude=severity * stage["magnitude_factor"],
                impact_phase=ImpactPhase(stage["phase"]),
                delay_days=stage["delay_days"],
                parent_nodes=[f"node_{node_id - 1}"] if node_id > 0 else [],
                child_nodes=[],
            )
            
            if node_id > 0:
                nodes[node_id - 1].child_nodes.append(node.node_id)
            
            nodes.append(node)
            node_id += 1
        
        return CascadeChain(
            chain_id=f"cascade_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            trigger_event=trigger_event,
            trigger_severity=severity,
            nodes=nodes,
            total_depth=len(nodes),
            total_affected_areas=len(nodes),
            peak_impact_magnitude=max(n.impact_magnitude for n in nodes),
            peak_impact_phase=max(nodes, key=lambda n: n.impact_magnitude).impact_phase,
            estimated_resolution_days=max(n.delay_days for n in nodes) + 7,
            affected_industries=template.get("industries", []),
            key_outcomes=[n.name for n in nodes if n.node_type == "outcome"],
            intervention_points=[],
        )
    
    def _get_neighbors(self, current: str) -> List[Tuple[str, int, float]]:
        """Get all neighbors from propagation models."""
        neighbors = []
        
        for model in self._propagation_models:
            for path in model.propagation_paths:
                if path["from"] == current:
                    neighbors.append((
                        path["to"],
                        path["delay_days"],
                        path["magnitude_multiplier"],
                    ))
        
        return neighbors
    
    def _build_path_nodes(self, path: List[str]) -> List[CascadeNode]:
        """Build CascadeNode list from path."""
        nodes = []
        cumulative_delay = 0
        
        for i, step in enumerate(path):
            nodes.append(CascadeNode(
                node_id=f"path_{i}",
                node_type="domain",
                name=step,
                description=f"Step {i + 1}: {step}",
                impact_magnitude=1.0 - (0.1 * i),
                impact_phase=self._determine_phase(cumulative_delay),
                delay_days=cumulative_delay,
                parent_nodes=[f"path_{i-1}"] if i > 0 else [],
                child_nodes=[f"path_{i+1}"] if i < len(path) - 1 else [],
            ))
            cumulative_delay += 2
        
        return nodes
    
    def _determine_phase(self, delay_days: int) -> ImpactPhase:
        """Determine impact phase based on delay."""
        if delay_days <= 1:
            return ImpactPhase.IMMEDIATE
        elif delay_days <= 7:
            return ImpactPhase.SHORT_TERM
        elif delay_days <= 28:
            return ImpactPhase.MEDIUM_TERM
        else:
            return ImpactPhase.LONG_TERM
    
    def _calculate_intervention_effectiveness(
        self,
        node: CascadeNode,
        cascade: CascadeChain,
    ) -> float:
        """Calculate how effective intervening at this node would be."""
        # Count downstream impacts
        downstream_count = self._count_downstream(node.node_id, cascade)
        total_nodes = len(cascade.nodes)
        
        # More downstream = more effective intervention
        effectiveness = downstream_count / total_nodes
        
        # Earlier intervention is better
        if node.delay_days <= 2:
            effectiveness *= 1.3
        elif node.delay_days <= 7:
            effectiveness *= 1.1
        
        return min(1.0, effectiveness)
    
    def _count_downstream(self, node_id: str, cascade: CascadeChain) -> int:
        """Count all downstream nodes from a given node."""
        count = 0
        to_process = [node_id]
        visited = set()
        
        while to_process:
            current_id = to_process.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            current_node = next((n for n in cascade.nodes if n.node_id == current_id), None)
            if current_node:
                count += len(current_node.child_nodes)
                to_process.extend(current_node.child_nodes)
        
        return count
    
    def _get_intervention_actions(self, node: CascadeNode) -> List[str]:
        """Get recommended intervention actions for a node."""
        actions = []
        
        if "supply" in node.name.lower():
            actions.extend([
                "Activate alternative suppliers",
                "Increase safety stock levels",
            ])
        elif "transport" in node.name.lower() or "logistics" in node.name.lower():
            actions.extend([
                "Arrange alternative transport",
                "Pre-position critical inventory",
            ])
        elif "power" in node.name.lower():
            actions.extend([
                "Deploy backup power systems",
                "Adjust production schedules",
            ])
        elif "price" in node.name.lower() or "cost" in node.name.lower():
            actions.extend([
                "Review pricing strategy",
                "Negotiate with suppliers",
            ])
        else:
            actions.extend([
                "Monitor situation closely",
                "Prepare contingency plans",
            ])
        
        return actions
    
    def _rate_severity(self, peak_impact: float) -> str:
        """Rate severity based on peak impact."""
        if peak_impact >= 0.8:
            return "critical"
        elif peak_impact >= 0.6:
            return "severe"
        elif peak_impact >= 0.4:
            return "major"
        elif peak_impact >= 0.2:
            return "moderate"
        else:
            return "minor"
    
    def _load_propagation_models(self) -> List[PropagationModel]:
        """Load propagation models."""
        return [
            PropagationModel(
                event_type="port_strike",
                initial_domain="port_operations",
                propagation_paths=[
                    {"from": "port_operations", "to": "import_availability", "delay_days": 2, "magnitude_multiplier": 0.9},
                    {"from": "import_availability", "to": "manufacturing_inputs", "delay_days": 3, "magnitude_multiplier": 0.85},
                    {"from": "manufacturing_inputs", "to": "production_capacity", "delay_days": 2, "magnitude_multiplier": 0.8},
                    {"from": "production_capacity", "to": "retail_inventory", "delay_days": 5, "magnitude_multiplier": 0.7},
                    {"from": "retail_inventory", "to": "consumer_prices", "delay_days": 3, "magnitude_multiplier": 0.6},
                ],
                dampening_factor=0.95,
                max_depth=5,
            ),
            PropagationModel(
                event_type="fuel_shortage",
                initial_domain="fuel_availability",
                propagation_paths=[
                    {"from": "fuel_availability", "to": "transport_operations", "delay_days": 1, "magnitude_multiplier": 0.95},
                    {"from": "transport_operations", "to": "delivery_capacity", "delay_days": 1, "magnitude_multiplier": 0.9},
                    {"from": "delivery_capacity", "to": "retail_stock", "delay_days": 2, "magnitude_multiplier": 0.85},
                    {"from": "delivery_capacity", "to": "manufacturing_logistics", "delay_days": 2, "magnitude_multiplier": 0.8},
                    {"from": "manufacturing_logistics", "to": "production_output", "delay_days": 3, "magnitude_multiplier": 0.75},
                ],
                dampening_factor=0.9,
                max_depth=5,
            ),
            PropagationModel(
                event_type="power_outage",
                initial_domain="power_supply",
                propagation_paths=[
                    {"from": "power_supply", "to": "manufacturing_operations", "delay_days": 0, "magnitude_multiplier": 0.95},
                    {"from": "power_supply", "to": "cold_chain", "delay_days": 0, "magnitude_multiplier": 0.9},
                    {"from": "manufacturing_operations", "to": "production_output", "delay_days": 1, "magnitude_multiplier": 0.85},
                    {"from": "cold_chain", "to": "food_retail", "delay_days": 1, "magnitude_multiplier": 0.8},
                    {"from": "cold_chain", "to": "hospitality_food", "delay_days": 1, "magnitude_multiplier": 0.8},
                ],
                dampening_factor=0.9,
                max_depth=4,
            ),
            PropagationModel(
                event_type="currency_crisis",
                initial_domain="exchange_rate",
                propagation_paths=[
                    {"from": "exchange_rate", "to": "import_costs", "delay_days": 1, "magnitude_multiplier": 0.95},
                    {"from": "import_costs", "to": "manufacturing_costs", "delay_days": 7, "magnitude_multiplier": 0.8},
                    {"from": "import_costs", "to": "retail_costs", "delay_days": 7, "magnitude_multiplier": 0.75},
                    {"from": "manufacturing_costs", "to": "product_prices", "delay_days": 14, "magnitude_multiplier": 0.7},
                    {"from": "retail_costs", "to": "consumer_prices", "delay_days": 14, "magnitude_multiplier": 0.65},
                    {"from": "consumer_prices", "to": "demand_levels", "delay_days": 21, "magnitude_multiplier": 0.5},
                ],
                dampening_factor=0.85,
                max_depth=6,
            ),
        ]
    
    def _load_cascade_templates(self) -> List[Dict[str, Any]]:
        """Load cascade templates for common scenarios."""
        return [
            {
                "trigger": "generic",
                "stages": [
                    {"type": "event", "name": "Initial Event", "description": "Triggering event", "magnitude_factor": 1.0, "phase": "immediate", "delay_days": 0},
                    {"type": "domain", "name": "Direct Impact", "description": "Immediate effects", "magnitude_factor": 0.9, "phase": "immediate", "delay_days": 1},
                    {"type": "domain", "name": "Secondary Impact", "description": "Propagated effects", "magnitude_factor": 0.7, "phase": "short_term", "delay_days": 3},
                    {"type": "outcome", "name": "Business Impact", "description": "Business-level effects", "magnitude_factor": 0.5, "phase": "short_term", "delay_days": 7},
                ],
                "industries": [],
            },
            {
                "trigger": "supply_chain",
                "stages": [
                    {"type": "event", "name": "Supply Disruption", "description": "Supply chain disruption", "magnitude_factor": 1.0, "phase": "immediate", "delay_days": 0},
                    {"type": "domain", "name": "Inventory Impact", "description": "Inventory depletion", "magnitude_factor": 0.9, "phase": "short_term", "delay_days": 3},
                    {"type": "domain", "name": "Production Impact", "description": "Production slowdown", "magnitude_factor": 0.8, "phase": "short_term", "delay_days": 7},
                    {"type": "domain", "name": "Delivery Impact", "description": "Delivery delays", "magnitude_factor": 0.7, "phase": "medium_term", "delay_days": 14},
                    {"type": "outcome", "name": "Revenue Impact", "description": "Revenue decline", "magnitude_factor": 0.6, "phase": "medium_term", "delay_days": 21},
                ],
                "industries": ["retail", "manufacturing", "logistics"],
            },
            {
                "trigger": "labor",
                "stages": [
                    {"type": "event", "name": "Labor Action", "description": "Strike or labor shortage", "magnitude_factor": 1.0, "phase": "immediate", "delay_days": 0},
                    {"type": "domain", "name": "Operations Impact", "description": "Reduced operations", "magnitude_factor": 0.85, "phase": "immediate", "delay_days": 1},
                    {"type": "domain", "name": "Service Impact", "description": "Service disruption", "magnitude_factor": 0.75, "phase": "short_term", "delay_days": 3},
                    {"type": "outcome", "name": "Customer Impact", "description": "Customer experience degradation", "magnitude_factor": 0.6, "phase": "short_term", "delay_days": 5},
                ],
                "industries": ["logistics", "hospitality", "retail"],
            },
        ]


# Export for easy importing
__all__ = [
    "CascadingImpactAnalyzer",
    "CascadeChain",
    "CascadeNode",
    "PropagationModel",
    "ImpactPhase",
]
