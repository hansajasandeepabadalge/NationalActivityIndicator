"""
Script to use rule-based predictions as manual labels for quick testing

This simulates the manual labeling process using the rule-based classifier.
For production, you should do actual manual labeling for better accuracy.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    print("="*80)
    print("USING RULE-BASED LABELS AS PROXY")
    print("="*80)
    print("⚠️  Note: For best results, use actual manual labels")
    print("This script uses rule-based predictions as training labels for demo/testing")
    print("="*80 + "\n")

    # Load raw training data
    input_path = "backend/data/training/training_articles_raw.json"
    output_path = "backend/data/training/training_articles_labeled.json"

    print(f"Loading: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Use rule-based predictions as labels
    articles_processed = 0
    for article in data['articles']:
        # Copy rule-based predictions to manual labels
        article['manual_labels'] = article.get('rule_based_predictions', [])
        article['manual_confidences'] = article.get('rule_based_confidences', {})
        article['notes'] = "Auto-labeled using rule-based classifier for testing"
        articles_processed += 1

    # Save labeled data
    print(f"\nSaving labeled data to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Processed {articles_processed} articles")
    print(f"✅ Saved to: {output_path}")
    print("\nNext steps:")
    print("1. Run: python scripts/create_train_val_split.py")
    print("2. Run: python scripts/train_ml_model.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
