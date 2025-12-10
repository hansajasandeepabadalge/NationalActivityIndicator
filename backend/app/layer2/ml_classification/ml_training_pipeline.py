"""
ML Training Pipeline

Orchestrates the complete ML training workflow:
1. Load training data
2. Extract features
3. Train ML classifier
4. Evaluate on validation set
5. Save models
6. Generate training report
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from app.layer2.ml_classification.feature_extractor import FeatureExtractor
from app.layer2.ml_classification.ml_classifier import MLClassifier
from app.layer2.ml_classification.training_data_schema import TrainingDataset


class MLTrainingPipeline:
    """Orchestrate ML training workflow"""

    def __init__(self):
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

    def run_training(
        self,
        train_dataset_path: str,
        val_dataset_path: str,
        output_model_dir: str = "backend/models/ml_classifier",
        min_f1_threshold: float = 0.60
    ) -> Dict:
        """
        Run complete training pipeline.

        Args:
            train_dataset_path: Path to training dataset JSON
            val_dataset_path: Path to validation dataset JSON
            output_model_dir: Directory to save trained models
            min_f1_threshold: Minimum weighted F1 to consider success

        Returns:
            Training report dictionary
        """
        print("\n" + "="*80)
        print("ML TRAINING PIPELINE - Day 3 Task A3.2")
        print("="*80)

        start_time = datetime.now()

        # Step 1: Load datasets
        print("\n[Step 1] Loading training and validation datasets...")
        print("-" * 80)
        train_dataset, train_articles, train_labels = self._load_dataset(train_dataset_path)
        val_dataset, val_articles, val_labels = self._load_dataset(val_dataset_path)

        print(f"  Training: {len(train_articles)} articles")
        print(f"  Validation: {len(val_articles)} articles")

        # Step 2: Initialize and train classifier
        print("\n[Step 2] Training ML Classifier...")
        print("-" * 80)

        feature_extractor = FeatureExtractor()
        classifier = MLClassifier(feature_extractor=feature_extractor)

        training_results = classifier.train(
            train_articles=train_articles,
            train_labels=train_labels,
            val_articles=val_articles,
            val_labels=val_labels
        )

        # Step 3: Evaluate performance
        print("\n[Step 3] Performance Evaluation...")
        print("-" * 80)

        val_results = training_results['val_results']
        weighted_f1 = val_results['weighted_f1']

        success = weighted_f1 >= min_f1_threshold

        if success:
            print(f"  ✅ SUCCESS: Weighted F1 = {weighted_f1:.3f} >= {min_f1_threshold:.2f}")
        elif weighted_f1 >= 0.55:
            print(f"  ⚠️  ACCEPTABLE: Weighted F1 = {weighted_f1:.3f} (close to target)")
            print(f"  Proceeding with model save...")
        else:
            print(f"  ❌ BELOW TARGET: Weighted F1 = {weighted_f1:.3f} < {min_f1_threshold:.2f}")
            print(f"  Consider:")
            print(f"    - Adding more training data")
            print(f"    - Adjusting feature engineering")
            print(f"    - Using fallback: enhanced rule-based")

        # Step 4: Save model (if acceptable)
        if weighted_f1 >= 0.55:  # Save if close enough
            print("\n[Step 4] Saving trained model...")
            print("-" * 80)
            classifier.save(output_model_dir)
        else:
            print("\n[Step 4] Model NOT saved (F1 too low)")
            print("-" * 80)

        # Step 5: Generate training report
        print("\n[Step 5] Generating training report...")
        print("-" * 80)

        report = self._generate_training_report(
            classifier=classifier,
            training_results=training_results,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            weighted_f1=weighted_f1,
            min_f1_threshold=min_f1_threshold,
            start_time=start_time,
            end_time=datetime.now()
        )

        # Save report
        report_path = Path(output_model_dir) / "training_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"  ✓ Training report saved to: {report_path}")

        # Step 6: Print feature importance
        print("\n[Step 6] Feature Importance Analysis...")
        print("-" * 80)
        self._print_feature_importance(classifier, top_n=5)

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "="*80)
        print("TRAINING PIPELINE COMPLETE")
        print("="*80)
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Weighted F1: {weighted_f1:.3f}")
        print(f"  Status: {'✅ SUCCESS' if success else '⚠️ ACCEPTABLE' if weighted_f1 >= 0.55 else '❌ FAILED'}")
        print(f"  Model saved: {'Yes' if weighted_f1 >= 0.55 else 'No'}")
        print("="*80 + "\n")

        return report

    def _load_dataset(
        self,
        dataset_path: str
    ) -> Tuple[TrainingDataset, List[Dict], np.ndarray]:
        """
        Load dataset and convert to training format.

        Args:
            dataset_path: Path to dataset JSON

        Returns:
            Tuple of (dataset, articles, label_matrix)
        """
        with open(dataset_path, 'r') as f:
            dataset_dict = json.load(f)

        dataset = TrainingDataset(**dataset_dict)

        # Convert to articles list and label matrix
        articles = []
        label_matrix = []

        for training_article in dataset.articles:
            # Convert TrainingArticle to dict
            if hasattr(training_article, 'model_dump'):
                article_dict = training_article.model_dump()
            else:
                article_dict = training_article

            articles.append(article_dict)

            # Create binary label vector
            labels = article_dict.get('labels', [])
            label_vector = [
                1 if indicator_id in labels else 0
                for indicator_id in self.indicator_ids
            ]
            label_matrix.append(label_vector)

        label_matrix = np.array(label_matrix, dtype=np.int32)

        return dataset, articles, label_matrix

    def _generate_training_report(
        self,
        classifier: MLClassifier,
        training_results: Dict,
        train_dataset: TrainingDataset,
        val_dataset: TrainingDataset,
        weighted_f1: float,
        min_f1_threshold: float,
        start_time: datetime,
        end_time: datetime
    ) -> Dict:
        """Generate comprehensive training report"""

        duration = (end_time - start_time).total_seconds()

        report = {
            'metadata': {
                'model_version': 'v1.0',
                'training_date': start_time.isoformat(),
                'duration_seconds': duration,
                'model_type': 'LogisticRegression (Binary Relevance)',
                'feature_dimensions': 61
            },
            'datasets': {
                'train': {
                    'n_samples': train_dataset.total_articles,
                    'label_distribution': train_dataset.label_distribution,
                    'avg_labels_per_article': train_dataset.avg_labels_per_article
                },
                'val': {
                    'n_samples': val_dataset.total_articles,
                    'label_distribution': val_dataset.label_distribution,
                    'avg_labels_per_article': val_dataset.avg_labels_per_article
                }
            },
            'hyperparameters': {
                'C': 1.0,
                'penalty': 'l2',
                'class_weight': 'balanced',
                'max_iter': 1000,
                'solver': 'lbfgs'
            },
            'performance': {
                'weighted_f1': weighted_f1,
                'min_threshold': min_f1_threshold,
                'success': weighted_f1 >= min_f1_threshold,
                'acceptable': weighted_f1 >= 0.55,
                'validation_results': training_results.get('val_results', {})
            },
            'per_indicator_training': training_results.get('per_indicator_results', {}),
            'feature_importance': classifier.get_feature_importance(top_n=5)
        }

        return report

    def _print_feature_importance(self, classifier: MLClassifier, top_n: int = 5):
        """Print feature importance for each indicator"""

        importance_dict = classifier.get_feature_importance(top_n=top_n)

        for indicator_id in self.indicator_ids:
            top_features = importance_dict.get(indicator_id, [])

            if not top_features:
                print(f"  {indicator_id}: No model trained")
                continue

            print(f"\n  {indicator_id}:")
            for rank, (feature_name, importance) in enumerate(top_features, 1):
                print(f"    {rank}. {feature_name}: {importance:.4f}")

    def cross_validate(
        self,
        dataset_path: str,
        k_folds: int = 5,
        random_seed: int = 42
    ) -> Dict:
        """
        Perform k-fold cross-validation.

        Args:
            dataset_path: Path to complete dataset
            k_folds: Number of folds
            random_seed: Random seed

        Returns:
            Cross-validation results
        """
        print("\n" + "="*80)
        print(f"K-FOLD CROSS-VALIDATION (k={k_folds})")
        print("="*80)

        # Load dataset
        with open(dataset_path, 'r') as f:
            dataset_dict = json.load(f)

        dataset = TrainingDataset(**dataset_dict)
        all_articles = dataset.articles

        # Convert to numpy arrays
        articles_list = [
            art.model_dump() if hasattr(art, 'model_dump') else art
            for art in all_articles
        ]

        labels_list = []
        for article in articles_list:
            labels = article.get('labels', [])
            label_vector = [
                1 if indicator_id in labels else 0
                for indicator_id in self.indicator_ids
            ]
            labels_list.append(label_vector)

        labels_array = np.array(labels_list, dtype=np.int32)

        # Shuffle
        np.random.seed(random_seed)
        indices = np.random.permutation(len(articles_list))

        # Split into folds
        fold_size = len(articles_list) // k_folds
        fold_scores = []

        for fold in range(k_folds):
            print(f"\n[Fold {fold + 1}/{k_folds}]")
            print("-" * 80)

            # Split indices
            val_start = fold * fold_size
            val_end = (fold + 1) * fold_size if fold < k_folds - 1 else len(articles_list)

            val_indices = indices[val_start:val_end]
            train_indices = np.concatenate([indices[:val_start], indices[val_end:]])

            # Create train/val sets
            train_articles = [articles_list[i] for i in train_indices]
            train_labels = labels_array[train_indices]

            val_articles = [articles_list[i] for i in val_indices]
            val_labels = labels_array[val_indices]

            # Train and evaluate
            feature_extractor = FeatureExtractor()
            classifier = MLClassifier(feature_extractor=feature_extractor)

            classifier.train(train_articles, train_labels)
            results = classifier.evaluate(val_articles, val_labels, dataset_name=f"Fold {fold + 1}")

            fold_scores.append(results['weighted_f1'])

        # Summary
        mean_f1 = np.mean(fold_scores)
        std_f1 = np.std(fold_scores)

        print("\n" + "="*80)
        print("CROSS-VALIDATION SUMMARY")
        print("="*80)
        print(f"  Mean Weighted F1: {mean_f1:.3f} ± {std_f1:.3f}")
        print(f"  Fold scores: {[f'{score:.3f}' for score in fold_scores]}")
        print("="*80 + "\n")

        return {
            'k_folds': k_folds,
            'mean_f1': float(mean_f1),
            'std_f1': float(std_f1),
            'fold_scores': [float(s) for s in fold_scores]
        }
