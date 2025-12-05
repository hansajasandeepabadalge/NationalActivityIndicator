"""
Script to create train/validation split from labeled data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.layer2.ml_classification.training_data_generator import TrainingDataGenerator


def main():
    print("="*80)
    print("CREATE TRAIN/VALIDATION SPLIT")
    print("="*80 + "\n")

    generator = TrainingDataGenerator()

    # Import labeled data
    print("[Step 1] Importing labeled articles...")
    dataset = generator.import_manual_labels(
        "backend/data/training/training_articles_labeled.json"
    )

    # Create split
    print("\n[Step 2] Creating 80/20 train/validation split...")
    train_dataset, val_dataset, split_info = generator.create_train_val_split(
        dataset=dataset,
        split_ratio=0.8,
        random_seed=42
    )

    # Save split
    print("\n[Step 3] Saving split files...")
    generator.save_split(
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        split_info=split_info,
        output_dir="backend/data/training"
    )

    print("\n" + "="*80)
    print("SPLIT CREATION COMPLETE")
    print("="*80)
    print("\nNext step:")
    print("  python scripts/train_ml_model.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
