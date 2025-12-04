"""
Layer 4: Business Insights Engine - SQLAlchemy Models
"""
from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, Boolean,
    TIMESTAMP, ForeignKey, ARRAY, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.session import Base


class RiskOpportunityDefinition(Base):
    """Master catalog of all risk and opportunity types"""
    __tablename__ = "risk_opportunity_definitions"

    definition_id = Column(Integer, primary_key=True, autoincrement=True)

    # Identification
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200))

    # Classification
    type = Column(String(20), nullable=False, index=True)  # 'risk' or 'opportunity'
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(100))

    # Trigger conditions
    trigger_logic = Column(JSONB, nullable=False)

    # Scoring configuration
    impact_formula = Column(Text)
    probability_formula = Column(Text)
    urgency_formula = Column(Text)

    # Default values
    default_impact = Column(DECIMAL(4, 2))
    default_probability = Column(DECIMAL(3, 2))
    default_urgency = Column(Integer)

    # Applicability
    applicable_industries = Column(ARRAY(Text))
    applicable_business_scales = Column(ARRAY(Text))

    # Content
    description_template = Column(Text)
    explanation_template = Column(Text)

    # Recommendations
    immediate_actions = Column(JSONB)
    short_term_actions = Column(JSONB)
    medium_term_actions = Column(JSONB)

    # Metadata
    severity_mapping = Column(JSONB)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    version = Column(Integer, default=1)


class BusinessInsight(Base):
    """Generated business insights (risks and opportunities)"""
    __tablename__ = "business_insights"

    insight_id = Column(Integer, primary_key=True, autoincrement=True)

    # Reference
    definition_id = Column(Integer, ForeignKey('risk_opportunity_definitions.definition_id'))
    company_id = Column(String(50), nullable=False, index=True)

    # Classification
    insight_type = Column(String(20), nullable=False, index=True)  # 'risk' or 'opportunity'
    category = Column(String(50), nullable=False)

    # Identification
    title = Column(String(200), nullable=False)
    description = Column(Text)

    # Scoring
    probability = Column(DECIMAL(3, 2))  # 0.00 to 1.00
    impact = Column(DECIMAL(4, 2))  # 0 to 10
    urgency = Column(Integer)  # 1 to 5
    confidence = Column(DECIMAL(3, 2))  # 0.00 to 1.00

    final_score = Column(DECIMAL(6, 2))
    severity_level = Column(String(20), index=True)  # 'critical', 'high', 'medium', 'low'

    # Temporal
    detected_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    expected_impact_time = Column(TIMESTAMP)
    expected_duration_hours = Column(Integer)

    # Status
    status = Column(String(50), default='active', index=True)
    # 'active', 'acknowledged', 'in_progress', 'resolved', 'expired'

    acknowledged_at = Column(TIMESTAMP)
    acknowledged_by = Column(String(100))

    resolved_at = Column(TIMESTAMP)
    resolution_notes = Column(Text)

    # Impact tracking
    actual_impact = Column(Text)
    actual_outcome = Column(Text)
    lessons_learned = Column(Text)

    # Related data
    triggering_indicators = Column(JSONB)
    related_insights = Column(ARRAY(Integer))
    affected_operations = Column(ARRAY(Text))

    # Priority
    priority_rank = Column(Integer, index=True)
    is_urgent = Column(Boolean, default=False, index=True)
    requires_immediate_action = Column(Boolean, default=False)

    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


# Composite indexes for BusinessInsight
Index('idx_insights_company_time', BusinessInsight.company_id, BusinessInsight.detected_at.desc())
Index('idx_insights_type_severity', BusinessInsight.insight_type, BusinessInsight.severity_level)
Index('idx_insights_status_time', BusinessInsight.status, BusinessInsight.detected_at.desc())


class InsightRecommendation(Base):
    """Action recommendations for insights"""
    __tablename__ = "insight_recommendations"

    recommendation_id = Column(Integer, primary_key=True, autoincrement=True)
    insight_id = Column(Integer, ForeignKey('business_insights.insight_id'), index=True)

    # Recommendation details
    category = Column(String(50))  # 'immediate', 'short_term', 'medium_term', 'long_term'
    priority = Column(Integer, index=True)  # 1 = highest

    action_title = Column(String(200), nullable=False)
    action_description = Column(Text)

    # Implementation details
    responsible_role = Column(String(100))
    estimated_effort = Column(String(50))
    estimated_cost = Column(String(50))
    estimated_timeframe = Column(String(100))

    # Expected outcomes
    expected_benefit = Column(Text)
    success_metrics = Column(ARRAY(Text))

    # Resources needed
    required_resources = Column(JSONB)

    # Status tracking
    status = Column(String(50), default='pending', index=True)
    # 'pending', 'in_progress', 'completed', 'dismissed'

    assigned_to = Column(String(100))
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)

    # Outcomes
    implementation_notes = Column(Text)
    outcome_achieved = Column(Boolean)
    actual_benefit = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())


class InsightFeedback(Base):
    """User feedback on insights for system learning"""
    __tablename__ = "insight_feedback"

    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    insight_id = Column(Integer, ForeignKey('business_insights.insight_id'), index=True)
    company_id = Column(String(50), nullable=False, index=True)

    # Feedback type
    feedback_type = Column(String(50))
    # 'accuracy', 'relevance', 'usefulness', 'outcome'

    # Ratings (1-5 scale)
    accuracy_rating = Column(Integer)
    relevance_rating = Column(Integer)
    usefulness_rating = Column(Integer)
    timeliness_rating = Column(Integer)

    # Qualitative feedback
    comments = Column(Text)

    # Outcome verification
    did_risk_materialize = Column(Boolean)
    did_opportunity_exist = Column(Boolean)
    was_action_taken = Column(Boolean)
    action_effectiveness = Column(String(50))

    # Impact assessment
    actual_business_impact = Column(Text)
    financial_impact_estimate = Column(DECIMAL(15, 2))

    # Improvement suggestions
    what_was_wrong = Column(Text)
    what_was_missing = Column(Text)
    suggestions = Column(Text)

    # Metadata
    provided_by = Column(String(100))
    provided_at = Column(TIMESTAMP, server_default=func.now())


Index('idx_feedback_company_time', InsightFeedback.company_id, InsightFeedback.provided_at.desc())


class ScenarioSimulation(Base):
    """What-if scenario analyses"""
    __tablename__ = "scenario_simulations"

    simulation_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)

    # Scenario details
    scenario_name = Column(String(200), nullable=False)
    scenario_description = Column(Text)

    # Input assumptions
    assumptions = Column(JSONB, nullable=False)

    # Simulation results
    predicted_risks = Column(JSONB)
    predicted_opportunities = Column(JSONB)
    estimated_impact = Column(JSONB)

    # Recommendations
    recommended_contingencies = Column(JSONB)
    preparation_actions = Column(JSONB)

    # Status
    status = Column(String(50), default='draft', index=True)
    # 'draft', 'active', 'archived'

    # Metadata
    created_by = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


Index('idx_scenarios_company_time', ScenarioSimulation.company_id, ScenarioSimulation.created_at.desc())


class CompetitiveIntelligence(Base):
    """Competitor-related insights"""
    __tablename__ = "competitive_intelligence"

    intel_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String(50), nullable=False, index=True)

    # Competitor information
    competitor_name = Column(String(200))
    competitor_industry = Column(String(100))

    # Intelligence type
    intel_type = Column(String(50))
    # 'weakness', 'strength', 'movement', 'vulnerability'

    # Details
    description = Column(Text)
    source = Column(String(200))
    confidence_level = Column(DECIMAL(3, 2))

    # Impact on your business
    relevance_score = Column(DECIMAL(3, 2))
    potential_opportunity = Column(Text)
    suggested_response = Column(Text)

    # Status
    status = Column(String(50), default='new', index=True)
    # 'new', 'monitoring', 'acted_on', 'expired'

    # Temporal
    detected_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    expires_at = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, server_default=func.now())


Index('idx_competitive_intel_company_time', CompetitiveIntelligence.company_id, CompetitiveIntelligence.detected_at.desc())


class InsightTracking(Base):
    """TimescaleDB hypertable: Daily insight snapshots"""
    __tablename__ = "insight_tracking"

    time = Column(TIMESTAMP, primary_key=True, nullable=False)
    company_id = Column(String(50), primary_key=True, nullable=False, index=True)

    # Daily snapshot
    total_active_risks = Column(Integer)
    total_active_opportunities = Column(Integer)

    # By severity
    critical_risks = Column(Integer)
    high_risks = Column(Integer)
    medium_risks = Column(Integer)
    low_risks = Column(Integer)

    # By category
    operational_risks = Column(Integer)
    financial_risks = Column(Integer)
    competitive_risks = Column(Integer)
    reputational_risks = Column(Integer)
    compliance_risks = Column(Integer)
    strategic_risks = Column(Integer)

    # Opportunities
    market_opportunities = Column(Integer)
    cost_opportunities = Column(Integer)
    strategic_opportunities = Column(Integer)

    # Actions
    recommendations_generated = Column(Integer)
    actions_taken = Column(Integer)
    actions_completed = Column(Integer)

    # Outcomes
    risks_materialized = Column(Integer)
    risks_avoided = Column(Integer)
    opportunities_captured = Column(Integer)
    opportunities_missed = Column(Integer)


Index('idx_insight_tracking_company_time', InsightTracking.company_id, InsightTracking.time.desc())


class InsightScoreHistory(Base):
    """TimescaleDB hypertable: Insight score evolution"""
    __tablename__ = "insight_score_history"

    time = Column(TIMESTAMP, primary_key=True, nullable=False)
    insight_id = Column(Integer, primary_key=True, nullable=False, index=True)

    # Score components
    probability = Column(DECIMAL(3, 2))
    impact = Column(DECIMAL(4, 2))
    urgency = Column(Integer)
    confidence = Column(DECIMAL(3, 2))

    final_score = Column(DECIMAL(6, 2))
    severity_level = Column(String(20))

    # Contributing factors
    triggering_indicators = Column(JSONB)


Index('idx_score_history_insight_time', InsightScoreHistory.insight_id, InsightScoreHistory.time.desc())
