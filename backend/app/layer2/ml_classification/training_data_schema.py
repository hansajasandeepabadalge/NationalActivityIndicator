"""
Training Data Schema for ML Classification

Defines Pydantic models for training data management.
"""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class TrainingArticle(BaseModel):
    """Schema for a labeled training article"""

    article_id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Article content/body")

    # Labels
    labels: List[str] = Field(
        default_factory=list,
        description="List of indicator IDs (e.g., ['POL_UNREST', 'ECO_INFLATION'])"
    )
    confidence_per_label: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence score for each label (0-1)"
    )

    # Metadata
    labeler: str = Field(default="developer_a", description="Who labeled this article")
    labeling_date: datetime = Field(default_factory=datetime.utcnow, description="When it was labeled")
    labeling_method: str = Field(default="manual", description="How it was labeled (manual, rule_based, assisted)")

    # Original article metadata
    category: Optional[str] = Field(None, description="PESTEL category if available")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    source: Optional[str] = Field(None, description="News source")

    # Rule-based baseline (for comparison)
    rule_based_predictions: Optional[List[str]] = Field(
        None,
        description="Predictions from rule-based classifier for comparison"
    )
    rule_based_confidences: Optional[Dict[str, float]] = Field(
        None,
        description="Confidences from rule-based classifier"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "article_id": "article_001",
                "title": "Nationwide strike paralyzes transport sector",
                "content": "Workers announced a nationwide strike affecting public transport...",
                "labels": ["POL_UNREST", "OPS_TRANSPORT"],
                "confidence_per_label": {
                    "POL_UNREST": 0.95,
                    "OPS_TRANSPORT": 0.85
                },
                "labeler": "developer_a",
                "category": "Political"
            }
        }
    }


class TrainingDataset(BaseModel):
    """Schema for a complete training dataset"""

    articles: List[TrainingArticle] = Field(..., description="List of labeled articles")

    # Metadata
    dataset_version: str = Field(default="v1.0", description="Dataset version")
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    total_articles: int = Field(0, description="Total number of articles")
    indicators_covered: List[str] = Field(default_factory=list, description="List of indicators with labels")

    # Statistics
    label_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of articles per indicator"
    )
    avg_labels_per_article: float = Field(0.0, description="Average labels per article")

    # Quality metrics
    inter_annotator_agreement: Optional[float] = Field(
        None,
        description="Agreement score if multiple labelers"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "articles": [],
                "dataset_version": "v1.0",
                "total_articles": 100,
                "indicators_covered": ["POL_UNREST", "ECO_INFLATION", "ECO_CURRENCY"],
                "label_distribution": {
                    "POL_UNREST": 15,
                    "ECO_INFLATION": 12,
                    "ECO_CURRENCY": 10
                },
                "avg_labels_per_article": 1.5
            }
        }
    }


class TrainingValidationSplit(BaseModel):
    """Schema for train/validation split"""

    train_article_ids: List[str] = Field(..., description="Article IDs in training set")
    val_article_ids: List[str] = Field(..., description="Article IDs in validation set")

    train_size: int = Field(0, description="Number of training articles")
    val_size: int = Field(0, description="Number of validation articles")
    split_ratio: float = Field(0.8, description="Train/val split ratio (default 0.8)")

    # Per-indicator distribution check
    train_label_distribution: Dict[str, int] = Field(default_factory=dict)
    val_label_distribution: Dict[str, int] = Field(default_factory=dict)

    split_date: datetime = Field(default_factory=datetime.utcnow)
    random_seed: int = Field(42, description="Random seed for reproducibility")

    model_config = {
        "json_schema_extra": {
            "example": {
                "train_article_ids": ["article_001", "article_002"],
                "val_article_ids": ["article_099", "article_100"],
                "train_size": 80,
                "val_size": 20,
                "split_ratio": 0.8,
                "train_label_distribution": {"POL_UNREST": 12, "ECO_INFLATION": 10},
                "val_label_distribution": {"POL_UNREST": 3, "ECO_INFLATION": 2}
            }
        }
    }
        }
