"""
Training Data Generator with Stratified Sampling

Generates high-quality training data using stratified sampling to ensure:
- Balanced representation of all indicators
- Mix of high and low confidence predictions
- Diverse article characteristics
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime

from app.layer2.data_ingestion.article_loader import ArticleLoader
from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.ml_classification.training_data_schema import (
    TrainingArticle, TrainingDataset, TrainingValidationSplit
)


class TrainingDataGenerator:
    """Generate stratified training data for ML classifier"""

    def __init__(self):
        self.article_loader = ArticleLoader()
        self.rule_classifier = RuleBasedClassifier()
        self.indicator_ids = [
            "POL_UNREST",
            "ECO_INFLATION",
            "ECO_CURRENCY",
            "ECO_CONSUMER_CONF",
            "ECO_SUPPLY_CHAIN",
            "ECO_TOURISM",
            "ENV_WEATHER",
            "OPS_TRANSPORT",
            "TEC_POWER",
            "SOC_HEALTHCARE"
        ]

    def select_stratified_articles(
        self,
        target_count: int = 100,
        articles_per_indicator: int = 20
    ) -> List[Dict]:
        """
        Select articles using stratified sampling strategy.

        Strategy:
        1. For each indicator, find 20 candidate articles (200 total pool)
        2. Include both HIGH confidence (>0.7) and LOW confidence (<0.4) articles
        3. Add 20 "confusing" multi-label articles
        4. Select final 100 most diverse articles

        Args:
            target_count: Final number of articles to select (default 100)
            articles_per_indicator: Candidates per indicator (default 20)

        Returns:
            List of selected article dictionaries with rule-based predictions
        """
        print(f"Loading all available articles...")
        all_articles = self.article_loader.load_articles(limit=None)  # Load all 240
        print(f"Loaded {len(all_articles)} articles")

        # Step 1: Classify all articles with rule-based classifier
        print("Classifying articles with rule-based classifier...")
        article_classifications = []

        for article in all_articles:
            # Handle both Pydantic models and dicts
            if hasattr(article, 'model_dump'):
                article_dict = article.model_dump()
            else:
                article_dict = article

            classifications = self.rule_classifier.classify_article(
                article_text=article_dict.get('content', ''),
                article_title=article_dict.get('title', '')
            )

            article_classifications.append({
                'article': article_dict,
                'classifications': classifications
            })

        # Step 2: Build candidate pools per indicator
        print(f"\nBuilding candidate pools ({articles_per_indicator} per indicator)...")
        indicator_pools = defaultdict(list)

        for item in article_classifications:
            article = item['article']
            classifications = item['classifications']

            # Add to each relevant indicator's pool
            for classification in classifications:
                indicator_id = classification['indicator_id']
                confidence = classification['confidence']
                indicator_pools[indicator_id].append({
                    'article': article,
                    'confidence': confidence,
                    'total_indicators': len(classifications)
                })

        # Step 3: Stratified sampling per indicator
        selected_articles = {}  # Use dict to avoid duplicates
        selection_metadata = {}  # Track why each article was selected

        for indicator_id in self.indicator_ids:
            pool = indicator_pools[indicator_id]

            if not pool:
                print(f"  ⚠️  {indicator_id}: No articles found")
                continue

            # Sort by confidence
            pool_sorted = sorted(pool, key=lambda x: x['confidence'], reverse=True)

            # Select diverse subset:
            # - Top 10 high confidence (>0.7)
            # - Bottom 5 low confidence (<0.4)
            # - 5 medium confidence (0.4-0.7)
            high_conf = [p for p in pool_sorted if p['confidence'] > 0.7][:10]
            low_conf = [p for p in pool_sorted if p['confidence'] < 0.4][-5:]
            med_conf = [p for p in pool_sorted if 0.4 <= p['confidence'] <= 0.7][:5]

            indicator_selection = high_conf + med_conf + low_conf

            for item in indicator_selection:
                article_id = item['article']['article_id']
                if article_id not in selected_articles:
                    selected_articles[article_id] = item['article']
                    selection_metadata[article_id] = []

                selection_metadata[article_id].append({
                    'indicator': indicator_id,
                    'confidence': item['confidence'],
                    'reason': 'stratified_sampling'
                })

            print(f"  ✓ {indicator_id}: Selected {len(indicator_selection)} articles "
                  f"(high={len(high_conf)}, med={len(med_conf)}, low={len(low_conf)})")

        # Step 4: Add "confusing" multi-label articles
        print(f"\nAdding multi-label articles...")
        multi_label_articles = [
            item for item in article_classifications
            if len(item['classifications']) >= 2  # 2+ indicators
        ]
        multi_label_articles_sorted = sorted(
            multi_label_articles,
            key=lambda x: len(x['classifications']),
            reverse=True
        )

        added_multi = 0
        for item in multi_label_articles_sorted[:20]:
            article_id = item['article']['article_id']
            if article_id not in selected_articles:
                selected_articles[article_id] = item['article']
                selection_metadata[article_id] = [{
                    'reason': 'multi_label',
                    'indicator_count': len(item['classifications'])
                }]
                added_multi += 1

        print(f"  ✓ Added {added_multi} multi-label articles")

        # Step 5: If we have more than target, prioritize diversity
        if len(selected_articles) > target_count:
            print(f"\nReducing from {len(selected_articles)} to {target_count} articles...")
            # Score articles by diversity (prefer multi-label, diverse sources, etc.)
            scored_articles = []
            for article_id, article in selected_articles.items():
                metadata = selection_metadata[article_id]
                diversity_score = len(metadata)  # More reasons = more diverse
                scored_articles.append((article_id, article, diversity_score))

            scored_articles.sort(key=lambda x: x[2], reverse=True)
            selected_articles = {
                article_id: article
                for article_id, article, _ in scored_articles[:target_count]
            }

        # Step 6: Prepare final output with rule-based predictions
        print(f"\nPreparing final dataset with {len(selected_articles)} articles...")
        final_articles = []

        for article_id, article in selected_articles.items():
            # Get rule-based predictions for this article
            rule_predictions = self.rule_classifier.classify_article(
                article_text=article.get('content', ''),
                article_title=article.get('title', '')
            )

            article_with_predictions = {
                **article,
                'rule_based_predictions': [pred['indicator_id'] for pred in rule_predictions],
                'rule_based_confidences': {pred['indicator_id']: pred['confidence'] for pred in rule_predictions}
            }
            final_articles.append(article_with_predictions)

        # Print selection statistics
        self._print_selection_stats(final_articles)

        return final_articles

    def _print_selection_stats(self, articles: List[Dict]):
        """Print statistics about selected articles"""
        print("\n" + "="*60)
        print("SELECTION STATISTICS")
        print("="*60)

        # Count articles per indicator (from rule-based predictions)
        indicator_counts = defaultdict(int)
        for article in articles:
            for indicator in article.get('rule_based_predictions', []):
                indicator_counts[indicator] += 1

        print(f"\nArticles per indicator (from rule-based):")
        for indicator_id in self.indicator_ids:
            count = indicator_counts[indicator_id]
            print(f"  {indicator_id}: {count} articles")

        # Average indicators per article
        avg_indicators = sum(
            len(article.get('rule_based_predictions', []))
            for article in articles
        ) / len(articles)
        print(f"\nAverage indicators per article: {avg_indicators:.2f}")

        # PESTEL category distribution
        category_counts = defaultdict(int)
        for article in articles:
            category = article.get('category', 'Unknown')
            category_counts[category] += 1

        print(f"\nPESTEL category distribution:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count} articles")

        print("="*60 + "\n")

    def export_for_manual_review(
        self,
        articles: List[Dict],
        output_path: str = "backend/data/training/training_articles_raw.json"
    ):
        """
        Export articles to JSON for manual review/labeling.

        Args:
            articles: List of article dictionaries with rule-based predictions
            output_path: Path to save JSON file
        """
        # Create directory if needed
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Prepare export data
        export_data = {
            'metadata': {
                'export_date': datetime.utcnow().isoformat(),
                'total_articles': len(articles),
                'labeling_instructions': (
                    "LABELING PROTOCOL:\n"
                    "1. Read title and content BLIND (don't look at rule_based_predictions yet)\n"
                    "2. Assign 1-3 primary indicators based on your judgment\n"
                    "3. THEN compare with rule_based_predictions\n"
                    "4. Focus manual effort on DISAGREEMENTS (most valuable)\n"
                    "5. Accept rule-based for high confidence cases (>0.8) to save time\n"
                    "6. Add labels to 'manual_labels' field\n"
                    "7. Add confidence scores to 'manual_confidences' field"
                ),
                'indicators': self.indicator_ids
            },
            'articles': []
        }

        for article in articles:
            # Convert datetime to string if present
            published_at = article.get('published_at', '')
            if hasattr(published_at, 'isoformat'):
                published_at = published_at.isoformat()
            elif published_at is None:
                published_at = ''

            export_article = {
                'article_id': article['article_id'],
                'title': article['title'],
                'content': article.get('content', ''),
                'category': article.get('category', ''),
                'published_at': str(published_at),
                'source': article.get('source', ''),

                # Rule-based baseline (for comparison)
                'rule_based_predictions': article.get('rule_based_predictions', []),
                'rule_based_confidences': article.get('rule_based_confidences', {}),

                # TO BE FILLED MANUALLY
                'manual_labels': [],  # Add your labels here
                'manual_confidences': {},  # Add your confidence scores here
                'notes': ""  # Add any notes about labeling decisions
            }
            export_data['articles'].append(export_article)

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Exported {len(articles)} articles to: {output_path}")
        print(f"  Please review and add manual labels to 'manual_labels' field")
        print(f"  Save corrected version to: training_articles_labeled.json")

    def import_manual_labels(
        self,
        labeled_file_path: str = "backend/data/training/training_articles_labeled.json"
    ) -> TrainingDataset:
        """
        Import manually labeled articles and create TrainingDataset.

        Args:
            labeled_file_path: Path to manually labeled JSON file

        Returns:
            TrainingDataset with manually labeled articles
        """
        with open(labeled_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        training_articles = []
        label_counts = defaultdict(int)
        total_labels = 0

        for article_data in data['articles']:
            # Use manual labels if provided, otherwise fall back to rule-based
            labels = article_data.get('manual_labels') or article_data.get('rule_based_predictions', [])
            confidences = article_data.get('manual_confidences') or article_data.get('rule_based_confidences', {})

            # Create TrainingArticle
            training_article = TrainingArticle(
                article_id=article_data['article_id'],
                title=article_data['title'],
                content=article_data['content'],
                labels=labels,
                confidence_per_label=confidences,
                labeler="developer_a",
                labeling_method="manual" if article_data.get('manual_labels') else "rule_based",
                category=article_data.get('category'),
                published_at=article_data.get('published_at'),
                source=article_data.get('source'),
                rule_based_predictions=article_data.get('rule_based_predictions'),
                rule_based_confidences=article_data.get('rule_based_confidences')
            )
            training_articles.append(training_article)

            # Count labels
            for label in labels:
                label_counts[label] += 1
            total_labels += len(labels)

        # Create dataset
        dataset = TrainingDataset(
            articles=training_articles,
            dataset_version="v1.0",
            total_articles=len(training_articles),
            indicators_covered=list(label_counts.keys()),
            label_distribution=dict(label_counts),
            avg_labels_per_article=total_labels / len(training_articles) if training_articles else 0
        )

        print(f"\n✓ Imported {len(training_articles)} labeled articles")
        print(f"  Average labels per article: {dataset.avg_labels_per_article:.2f}")
        print(f"  Label distribution:")
        for indicator, count in sorted(label_counts.items()):
            print(f"    {indicator}: {count} articles")

        return dataset

    def create_train_val_split(
        self,
        dataset: TrainingDataset,
        split_ratio: float = 0.8,
        random_seed: int = 42
    ) -> Tuple[TrainingDataset, TrainingDataset, TrainingValidationSplit]:
        """
        Split dataset into training and validation sets with stratification.

        Args:
            dataset: Complete training dataset
            split_ratio: Train/val split ratio (default 0.8 = 80% train, 20% val)
            random_seed: Random seed for reproducibility

        Returns:
            Tuple of (train_dataset, val_dataset, split_info)
        """
        random.seed(random_seed)

        # Group articles by their labels for stratification
        label_to_articles = defaultdict(list)
        for article in dataset.articles:
            for label in article.labels:
                label_to_articles[label].append(article)

        train_articles = []
        val_articles = []

        # Stratified split: ensure each label is represented in both sets
        for label, articles in label_to_articles.items():
            random.shuffle(articles)
            split_idx = int(len(articles) * split_ratio)
            train_articles.extend(articles[:split_idx])
            val_articles.extend(articles[split_idx:])

        # Remove duplicates (articles may appear multiple times due to multi-label)
        train_articles = list({article.article_id: article for article in train_articles}.values())
        val_articles = list({article.article_id: article for article in val_articles}.values())

        # Create datasets
        train_label_counts = defaultdict(int)
        for article in train_articles:
            for label in article.labels:
                train_label_counts[label] += 1

        val_label_counts = defaultdict(int)
        for article in val_articles:
            for label in article.labels:
                val_label_counts[label] += 1

        train_dataset = TrainingDataset(
            articles=train_articles,
            dataset_version=dataset.dataset_version + "_train",
            total_articles=len(train_articles),
            indicators_covered=list(train_label_counts.keys()),
            label_distribution=dict(train_label_counts),
            avg_labels_per_article=sum(len(a.labels) for a in train_articles) / len(train_articles)
        )

        val_dataset = TrainingDataset(
            articles=val_articles,
            dataset_version=dataset.dataset_version + "_val",
            total_articles=len(val_articles),
            indicators_covered=list(val_label_counts.keys()),
            label_distribution=dict(val_label_counts),
            avg_labels_per_article=sum(len(a.labels) for a in val_articles) / len(val_articles)
        )

        split_info = TrainingValidationSplit(
            train_article_ids=[a.article_id for a in train_articles],
            val_article_ids=[a.article_id for a in val_articles],
            train_size=len(train_articles),
            val_size=len(val_articles),
            split_ratio=split_ratio,
            train_label_distribution=dict(train_label_counts),
            val_label_distribution=dict(val_label_counts),
            random_seed=random_seed
        )

        print(f"\n✓ Created train/val split:")
        print(f"  Training: {len(train_articles)} articles")
        print(f"  Validation: {len(val_articles)} articles")
        print(f"  Ratio: {split_ratio:.1%} / {1-split_ratio:.1%}")
        print(f"\n  Train label distribution:")
        for label, count in sorted(train_label_counts.items()):
            print(f"    {label}: {count}")
        print(f"\n  Val label distribution:")
        for label, count in sorted(val_label_counts.items()):
            print(f"    {label}: {count}")

        return train_dataset, val_dataset, split_info

    def save_split(
        self,
        train_dataset: TrainingDataset,
        val_dataset: TrainingDataset,
        split_info: TrainingValidationSplit,
        output_dir: str = "backend/data/training"
    ):
        """Save train/val split to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save datasets
        with open(output_path / "training_split.json", 'w', encoding='utf-8') as f:
            json.dump(train_dataset.model_dump(), f, indent=2, default=str)

        with open(output_path / "validation_split.json", 'w', encoding='utf-8') as f:
            json.dump(val_dataset.model_dump(), f, indent=2, default=str)

        with open(output_path / "split_info.json", 'w', encoding='utf-8') as f:
            json.dump(split_info.model_dump(), f, indent=2, default=str)

        print(f"\n✓ Saved split files to: {output_dir}")
        print(f"  - training_split.json")
        print(f"  - validation_split.json")
        print(f"  - split_info.json")
