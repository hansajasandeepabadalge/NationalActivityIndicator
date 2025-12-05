"""
Layer Integration Contracts

Defines the data schemas and validation for inter-layer communication.
These contracts ensure type safety and data integrity between layers.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


# =============================================================================
# Enums for Type Safety
# =============================================================================

class PESTELCategory(str, Enum):
    """PESTEL analysis categories"""
    POLITICAL = "Political"
    ECONOMIC = "Economic"
    SOCIAL = "Social"
    TECHNOLOGICAL = "Technological"
    ENVIRONMENTAL = "Environmental"
    LEGAL = "Legal"


class TrendDirection(str, Enum):
    """Trend direction for indicators"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"


class SeverityLevel(str, Enum):
    """Severity levels for events and risks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# Layer 2 Output Contract
# =============================================================================

class IndicatorValueOutput(BaseModel):
    """Single indicator value from Layer 2"""
    indicator_id: str
    indicator_name: str
    pestel_category: PESTELCategory
    timestamp: datetime
    value: float = Field(ge=0, le=100)
    raw_count: int = Field(ge=0)
    sentiment_score: Optional[float] = Field(default=None, ge=-1, le=1)
    confidence: float = Field(default=1.0, ge=0, le=1)
    source_count: int = Field(default=1, ge=1)
    
    class Config:
        use_enum_values = True


class IndicatorTrendOutput(BaseModel):
    """Trend information for an indicator"""
    indicator_id: str
    direction: TrendDirection
    change_percent: float
    period_days: int = Field(default=7, ge=1)
    
    class Config:
        use_enum_values = True


class IndicatorEventOutput(BaseModel):
    """Event detected by Layer 2"""
    event_id: int
    indicator_id: str
    timestamp: datetime
    event_type: str
    severity: SeverityLevel
    value_before: Optional[float] = None
    value_after: Optional[float] = None
    description: Optional[str] = None
    
    class Config:
        use_enum_values = True


class Layer2Output(BaseModel):
    """
    Complete output from Layer 2 National Activity Indicators
    
    This is the contract that Layer 3 expects to receive.
    """
    timestamp: datetime
    calculation_window_hours: int = Field(default=24, ge=1)
    
    # Current indicator values
    indicators: Dict[str, IndicatorValueOutput]
    
    # Trend information
    trends: Dict[str, IndicatorTrendOutput] = Field(default_factory=dict)
    
    # Detected events/anomalies
    events: List[IndicatorEventOutput] = Field(default_factory=list)
    
    # Aggregated metrics
    overall_sentiment: float = Field(ge=-1, le=1)
    activity_level: float = Field(ge=0, le=100)
    
    # Metadata
    article_count: int = Field(ge=0)
    source_diversity: int = Field(ge=0)
    data_quality_score: float = Field(ge=0, le=1)
    
    @validator('indicators')
    def validate_indicators_not_empty(cls, v):
        if not v:
            raise ValueError("indicators cannot be empty")
        return v


# =============================================================================
# Layer 3 Input/Output Contracts
# =============================================================================

class Layer3Input(BaseModel):
    """
    Input expected by Layer 3 from Layer 2
    
    This includes national indicators plus company context.
    """
    national_indicators: Layer2Output
    company_profile: Dict[str, Any]
    industry_config: Optional[Dict[str, Any]] = None


class OperationalIndicatorOutput(BaseModel):
    """Single operational indicator from Layer 3"""
    indicator_code: str
    indicator_name: str
    value: float = Field(ge=0, le=100)
    trend: TrendDirection
    impact_score: float = Field(ge=-1, le=1)
    contributing_national_indicators: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0, le=1)
    
    class Config:
        use_enum_values = True


class Layer3Output(BaseModel):
    """
    Complete output from Layer 3 Operational Indicators
    
    This is the contract that Layer 4 expects to receive.
    """
    timestamp: datetime
    company_id: str
    company_name: str
    industry: str
    
    # Operational indicators (0-100 scale)
    indicators: Dict[str, OperationalIndicatorOutput]
    
    # Aggregated by category
    supply_chain_health: float = Field(ge=0, le=100)
    workforce_health: float = Field(ge=0, le=100)
    infrastructure_health: float = Field(ge=0, le=100)
    cost_pressure: float = Field(ge=0, le=100)
    market_conditions: float = Field(ge=0, le=100)
    financial_health: float = Field(ge=0, le=100)
    regulatory_burden: float = Field(ge=0, le=100)
    
    # Overall assessment
    overall_operational_health: float = Field(ge=0, le=100)
    critical_issues: List[str] = Field(default_factory=list)
    
    # Trends
    trends: Dict[str, TrendDirection] = Field(default_factory=dict)
    
    # Source traceability
    source_national_indicators: List[str] = Field(default_factory=list)
    
    @validator('indicators')
    def validate_indicators_not_empty(cls, v):
        if not v:
            raise ValueError("indicators cannot be empty")
        return v


# =============================================================================
# Layer 4 Input Contract
# =============================================================================

class Layer4Input(BaseModel):
    """
    Input expected by Layer 4 from Layer 3
    
    This includes operational indicators plus additional context.
    """
    operational_indicators: Layer3Output
    company_profile: Dict[str, Any]
    historical_context: Optional[Dict[str, Any]] = None
    industry_benchmarks: Optional[Dict[str, Any]] = None


# =============================================================================
# Validation Functions
# =============================================================================

def validate_layer2_output(data: Dict[str, Any]) -> Layer2Output:
    """
    Validate and parse Layer 2 output
    
    Args:
        data: Raw dictionary from Layer 2
        
    Returns:
        Validated Layer2Output object
        
    Raises:
        ValidationError: If data doesn't match contract
    """
    return Layer2Output(**data)


def validate_layer3_output(data: Dict[str, Any]) -> Layer3Output:
    """
    Validate and parse Layer 3 output
    
    Args:
        data: Raw dictionary from Layer 3
        
    Returns:
        Validated Layer3Output object
        
    Raises:
        ValidationError: If data doesn't match contract
    """
    return Layer3Output(**data)


def validate_layer4_input(data: Dict[str, Any]) -> Layer4Input:
    """
    Validate and parse Layer 4 input
    
    Args:
        data: Raw dictionary for Layer 4
        
    Returns:
        Validated Layer4Input object
        
    Raises:
        ValidationError: If data doesn't match contract
    """
    return Layer4Input(**data)


# =============================================================================
# Schema Documentation
# =============================================================================

LAYER2_SCHEMA_DOCS = """
Layer 2 Output Schema
=====================

The Layer 2 National Activity Indicators module produces:

1. `indicators`: Dictionary of IndicatorValueOutput
   - indicator_id: Unique identifier (e.g., "ECON_GDP_SENTIMENT")
   - value: Normalized score 0-100
   - sentiment_score: -1 to 1
   - confidence: 0-1

2. `trends`: Direction of change for each indicator
   - direction: "rising", "falling", "stable"
   - change_percent: Percentage change over period

3. `events`: Detected anomalies and threshold breaches
   - event_type: "threshold_breach", "anomaly_detected", etc.
   - severity: "low", "medium", "high", "critical"

4. `overall_sentiment`: Aggregate sentiment -1 to 1
5. `activity_level`: Overall activity score 0-100
6. `data_quality_score`: Confidence in the data 0-1
"""

LAYER3_SCHEMA_DOCS = """
Layer 3 Output Schema
=====================

The Layer 3 Operational Indicators module produces:

1. `indicators`: Dictionary of OperationalIndicatorOutput
   - indicator_code: "OPS_SUPPLY_CHAIN", "OPS_WORKFORCE_AVAIL", etc.
   - value: Translated score 0-100
   - trend: "rising", "falling", "stable"
   - impact_score: Business impact -1 to 1

2. Category Aggregates (0-100):
   - supply_chain_health
   - workforce_health
   - infrastructure_health
   - cost_pressure
   - market_conditions
   - financial_health
   - regulatory_burden

3. `overall_operational_health`: Aggregate health 0-100
4. `critical_issues`: List of critical problems detected
5. `source_national_indicators`: Traceability to Layer 2
"""
