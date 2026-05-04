"""
Layer Integration Module

Provides data flow orchestration and contract validation between:
- Layer 2 (National Activity Indicators)
- Layer 3 (Operational Indicators)
- Layer 4 (Business Insights)
"""

from .contracts import (
    # Enums
    PESTELCategory,
    TrendDirection,
    SeverityLevel,
    # Layer 2 contracts
    IndicatorValueOutput,
    IndicatorTrendOutput,
    IndicatorEventOutput,
    Layer2Output,
    # Layer 3 contracts
    Layer3Input,
    OperationalIndicatorOutput,
    Layer3Output,
    # Layer 4 contracts
    Layer4Input,
    # Validation functions
    validate_layer2_output,
    validate_layer3_output,
    validate_layer4_input,
)
from .adapters import (
    Layer2ToLayer3Adapter,
    Layer3ToLayer4Adapter,
    MockDataGenerator,
)
from .pipeline import (
    IntegrationPipeline,
    PipelineBuilder,
    PipelineMetrics,
    create_pipeline,
)

__all__ = [
    # Enums
    "PESTELCategory",
    "TrendDirection",
    "SeverityLevel",
    # Contracts
    "IndicatorValueOutput",
    "IndicatorTrendOutput",
    "IndicatorEventOutput",
    "Layer2Output",
    "Layer3Input",
    "OperationalIndicatorOutput",
    "Layer3Output",
    "Layer4Input",
    # Validation
    "validate_layer2_output",
    "validate_layer3_output",
    "validate_layer4_input",
    # Adapters
    "Layer2ToLayer3Adapter",
    "Layer3ToLayer4Adapter",
    "MockDataGenerator",
    # Pipeline
    "IntegrationPipeline",
    "PipelineBuilder",
    "PipelineMetrics",
    "create_pipeline",
]
