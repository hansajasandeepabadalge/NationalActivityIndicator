"""
Script to tune hybrid classifier weights on validation set
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.layer2.ml_classification.ml_classifier import MLClassifier
from app.layer2.ml_classification.hybrid_classifier import HybridClassifier
from app.layer2.ml_classification.training_data_schema import TrainingDataset


def main():
    print("="*80)
    print("TUNE HYBRID WEIGHTS")
    print("="*80 + "\n")

    # Load ML classifier
    print("[Step 1] Loading trained ML classifier...")
    ml_classifier = MLClassifier.load("backend/models/ml_classifier")

    # Load validation data
    print("\n[Step 2] Loading validation data...")
    with open("backend/data/training/validation_split.json", 'r') as f:
        val_dataset_dict = json.load(f)

    val_dataset = TrainingDataset(**val_dataset_dict)

    # Convert to articles and labels
    val_articles = []
    val_labels_list = []

    indicator_ids = [
        "POL_UNREST", "ECO_INFLATION", "ECO_CURRENCY", "ECO_CONSUMER_CONF",
        "ECO_SUPPLY_CHAIN", "ECO_TOURISM", "ENV_WEATHER", "OPS_TRANSPORT",
        "TEC_POWER", "SOC_HEALTHCARE"
    ]

    for article in val_dataset.articles:
        if hasattr(article, 'model_dump'):
            article_dict = article.model_dump()
        else:
            article_dict = article

        val_articles.append(article_dict)

        # Create label vector
        labels = article_dict.get('labels', [])
        label_vector = [1 if ind in labels else 0 for ind in indicator_ids]
        val_labels_list.append(label_vector)

    val_labels = np.array(val_labels_list, dtype=np.int32)

    print(f"  Validation articles: {len(val_articles)}")
    print(f"  Labels shape: {val_labels.shape}")

    # Create hybrid classifier
    print("\n[Step 3] Tuning hybrid weights...")
    hybrid = HybridClassifier(ml_classifier=ml_classifier)
    hybrid.tune_weights(val_articles, val_labels)

    # Evaluate hybrid
    print("\n[Step 4] Evaluating hybrid performance...")
    results = hybrid.evaluate_hybrid(val_articles, val_labels)

    # Save weights
    print("\n[Step 5] Saving tuned weights...")
    hybrid.save_weights("backend/models/ml_classifier/hybrid_weights.json")

    print("\n" + "="*80)
    print("HYBRID TUNING COMPLETE")
    print("="*80)
    print(f"\nHybrid Weighted F1: {results['weighted_f1']:.3f}")
    print(f"Improvement vs Rule-based: {results['improvement_vs_rule']:+.3f}")
    if results['ml_only_f1'] > 0:
        print(f"Improvement vs ML-only: {results['improvement_vs_ml']:+.3f}")

    print("\n✅ Hybrid classifier ready for use!")
    print("\nTo enable in production:")
    print("  Set USE_HYBRID_CLASSIFICATION = True in config.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
