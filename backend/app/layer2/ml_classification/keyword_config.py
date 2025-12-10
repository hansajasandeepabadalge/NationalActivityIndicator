"""Keyword mappings for rule-based classification

This module defines keywords for 10+ indicators across PESTEL categories.
Each indicator has keywords with different weights (high, medium, low).
"""

INDICATOR_KEYWORDS = {
    "POL_UNREST": {
        "name": "Political Unrest",
        "pestel": "Political",
        "keywords": {
            "high_weight": ["protest", "strike", "demonstration", "riot", "unrest", "hartal"],
            "medium_weight": ["walkout", "boycott", "civil disobedience", "march"],
            "low_weight": ["dissent", "opposition", "rally"]
        }
    },
    "ECO_INFLATION": {
        "name": "Inflation Pressure",
        "pestel": "Economic",
        "keywords": {
            "high_weight": ["inflation", "price increase", "cost rise", "expensive"],
            "medium_weight": ["costly", "rising prices", "price hike"],
            "low_weight": ["affordability", "purchasing power"]
        }
    },
    "ECO_CURRENCY": {
        "name": "Currency Instability",
        "pestel": "Economic",
        "keywords": {
            "high_weight": ["LKR", "rupee", "exchange rate", "currency", "depreciation"],
            "medium_weight": ["forex", "foreign exchange", "devaluation"],
            "low_weight": ["dollar", "USD"]
        }
    },
    "ECO_CONSUMER_CONF": {
        "name": "Consumer Confidence",
        "pestel": "Economic",
        "keywords": {
            "high_weight": ["consumer confidence", "spending", "purchasing"],
            "medium_weight": ["shopping", "buying", "afford"],
            "low_weight": ["consumer sentiment"]
        }
    },
    "ECO_SUPPLY_CHAIN": {
        "name": "Supply Chain Issues",
        "pestel": "Economic",
        "keywords": {
            "high_weight": ["shortage", "supply chain", "stock out", "unavailable"],
            "medium_weight": ["inventory", "import delay", "logistics"],
            "low_weight": ["supply", "distribution"]
        }
    },
    "ECO_TOURISM": {
        "name": "Tourism Activity",
        "pestel": "Economic",
        "keywords": {
            "high_weight": ["tourist", "tourism", "arrival", "visitor"],
            "medium_weight": ["hotel", "resort", "travel"],
            "low_weight": ["hospitality"]
        }
    },
    "ENV_WEATHER": {
        "name": "Weather Severity",
        "pestel": "Environmental",
        "keywords": {
            "high_weight": ["flood", "drought", "cyclone", "storm"],
            "medium_weight": ["heavy rain", "extreme weather", "monsoon"],
            "low_weight": ["weather", "climate"]
        }
    },
    "OPS_TRANSPORT": {
        "name": "Transport Disruption",
        "pestel": "Technological",
        "keywords": {
            "high_weight": ["road closure", "traffic", "transport strike", "delay"],
            "medium_weight": ["commute", "vehicle", "route"],
            "low_weight": ["travel", "transport"]
        }
    },
    "TEC_POWER": {
        "name": "Power Outage",
        "pestel": "Technological",
        "keywords": {
            "high_weight": ["power cut", "load shedding", "electricity shortage", "outage"],
            "medium_weight": ["blackout", "power failure"],
            "low_weight": ["electricity", "power"]
        }
    },
    "SOC_HEALTHCARE": {
        "name": "Healthcare Stress",
        "pestel": "Social",
        "keywords": {
            "high_weight": ["hospital", "medicine shortage", "healthcare crisis"],
            "medium_weight": ["medical", "treatment", "doctor strike"],
            "low_weight": ["healthcare", "health"]
        }
    },
}

# Weights for keyword matching
KEYWORD_WEIGHTS = {
    "high_weight": 1.0,
    "medium_weight": 0.6,
    "low_weight": 0.3
}
