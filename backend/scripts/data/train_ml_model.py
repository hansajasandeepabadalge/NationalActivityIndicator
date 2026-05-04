"""
Script to train ML model and hybrid classifier
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.layer2.ml_classification.ml_training_pipeline import MLTrainingPipeline


def main():
    print("="*80)
    print("TRAIN ML MODEL AND HYBRID CLASSIFIER")
    print("="*80 + "\n")

    pipeline = MLTrainingPipeline()

    # Train model
    report = pipeline.run_training(
        train_dataset_path="backend/data/training/training_split.json",
        val_dataset_path="backend/data/training/validation_split.json",
        output_model_dir="backend/models/ml_classifier",
        min_f1_threshold=0.60
    )

    print("\n" + "="*80)
    print("TRAINING REPORT SUMMARY")
    print("="*80)
    print(f"\nWeighted F1: {report['performance']['weighted_f1']:.3f}")
    print(f"Success: {report['performance']['success']}")
    print(f"Acceptable: {report['performance']['acceptable']}")

    if report['performance']['acceptable']:
        print("\n✅ Model training successful!")
        print("\nNext steps:")
        print("  1. python scripts/tune_hybrid_weights.py")
        print("  2. python scripts/test_hybrid_classifier.py")
    else:
        print("\n⚠️  Model F1 below acceptable threshold")
        print("Consider:")
        print("  - Adding more training data")
        print("  - Using enhanced rule-based approach")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
