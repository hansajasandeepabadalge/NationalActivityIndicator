"""
Script to generate training data with stratified sampling
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.layer2.ml_classification.training_data_generator import TrainingDataGenerator


def main():
    print("="*80)
    print("TRAINING DATA GENERATION - Day 3 Task A3.1")
    print("="*80)

    # Initialize generator
    generator = TrainingDataGenerator()

    # Step 1: Select stratified articles
    print("\n[Step 1] Selecting articles with stratified sampling...")
    print("-" * 80)
    selected_articles = generator.select_stratified_articles(
        target_count=100,
        articles_per_indicator=20
    )

    # Step 2: Export for manual review
    print("\n[Step 2] Exporting articles for manual labeling...")
    print("-" * 80)
    generator.export_for_manual_review(
        articles=selected_articles,
        output_path="backend/data/training/training_articles_raw.json"
    )

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("1. Open: backend/data/training/training_articles_raw.json")
    print("2. For each article:")
    print("   - Read title and content BLIND (don't look at rule_based_predictions)")
    print("   - Assign 1-3 indicators to 'manual_labels' field")
    print("   - Add confidence scores to 'manual_confidences' field")
    print("   - THEN compare with rule_based_predictions")
    print("   - Accept rule-based for high confidence (>0.8) to save time")
    print("3. Save corrected version as: training_articles_labeled.json")
    print("4. Run next script to create train/val split")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
