"""
ML Classifier with Adaptive Model Selection

Automatically selects the best model based on dataset size:
- Small data (<100 samples): LogisticRegression (prevents overfitting)
- Large data (≥100 samples): XGBoost (better performance, original plan)

This enables seamless scaling from small to large datasets.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import joblib
import json

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score, precision_score, recall_score,
    classification_report, confusion_matrix
)

from app.layer2.ml_classification.feature_extractor import FeatureExtractor
from app.layer2.ml_classification.adaptive_model_selector import (
    get_model_for_indicator,
    print_selection_summary,
    get_model_info
)
from app.core.config import settings


class MLClassifier:
    """Multi-label classifier using Binary Relevance strategy"""

    def __init__(self, feature_extractor: Optional[FeatureExtractor] = None, model_type: str = "auto"):
        """
        Initialize ML classifier with adaptive model selection.

        Args:
            feature_extractor: Fitted FeatureExtractor instance
            model_type: Model selection strategy
                - "auto": Automatically choose based on data size (recommended)
                - "logistic": Force LogisticRegression
                - "xgboost": Force XGBoost (if available)
        """
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

        # Feature extractor
        self.feature_extractor = feature_extractor or FeatureExtractor()

        # Model selection type
        self.model_type = model_type

        # Binary Relevance: one model per indicator (created during training)
        self.models = {}

        # Fitted flag
        self.is_fitted = False

        # Training metadata
        self.training_metadata = {}

    def train(
        self,
        train_articles: List[Dict],
        train_labels: np.ndarray,
        val_articles: Optional[List[Dict]] = None,
        val_labels: Optional[np.ndarray] = None
    ) -> Dict:
        """
        Train all 10 binary classifiers.

        Args:
            train_articles: List of training article dictionaries
            train_labels: Binary label matrix (n_samples, 10)
            val_articles: Optional validation articles
            val_labels: Optional validation labels (n_samples, 10)

        Returns:
            Dictionary with training results
        """
        print("\n" + "="*60)
        print("TRAINING ML CLASSIFIER")
        print("="*60)

        # Fit feature extractor if not fitted
        if not self.feature_extractor.is_fitted:
            print("\nFitting feature extractor...")
            self.feature_extractor.fit(train_articles)

        # Extract features
        print(f"\nExtracting features from {len(train_articles)} training articles...")
        X_train = self.feature_extractor.transform_batch(train_articles)
        y_train = train_labels

        n_samples = X_train.shape[0]
        n_features = X_train.shape[1]

        print(f"  Training data shape: {X_train.shape}")
        print(f"  Labels shape: {y_train.shape}")

        # Validate labels
        if y_train.shape[1] != 10:
            raise ValueError(f"Expected 10 indicator labels, got {y_train.shape[1]}")

        # Adaptive model selection based on dataset size
        print(f"\n{'='*60}")
        print(f"ADAPTIVE MODEL SELECTION")
        print(f"{'='*60}")
        print(f"Dataset size: {n_samples} samples, {n_features} features")
        print(f"Samples per feature: {n_samples / n_features:.2f}")
        print(f"Model type: {self.model_type}")
        print()

        # Train each binary classifier
        print(f"Training {len(self.indicator_ids)} binary classifiers...")
        per_indicator_results = {}

        for i, indicator_id in enumerate(self.indicator_ids):
            y_indicator = y_train[:, i]
            positive_count = y_indicator.sum()
            negative_count = len(y_indicator) - positive_count

            print(f"\n  [{i+1}/10] {indicator_id}")
            print(f"    Positive: {positive_count}, Negative: {negative_count}")

            if positive_count == 0:
                print(f"    ⚠️  Skipping (no positive examples)")
                per_indicator_results[indicator_id] = {
                    'skipped': True,
                    'reason': 'no_positive_examples'
                }
                continue

            if positive_count < 3:
                print(f"    ⚠️  Warning: Very few positive examples ({positive_count})")

            # Create model using adaptive selector
            self.models[indicator_id] = get_model_for_indicator(
                n_samples=n_samples,
                n_features=n_features,
                indicator_id=indicator_id,
                model_type=self.model_type,
                verbose=True
            )

            # Train model
            self.models[indicator_id].fit(X_train, y_indicator)

            # Training accuracy
            y_pred_train = self.models[indicator_id].predict(X_train)
            train_f1 = f1_score(y_indicator, y_pred_train, zero_division=0)

            print(f"    Training F1: {train_f1:.3f}")

            # Get model info
            model_info = get_model_info(self.models[indicator_id])

            per_indicator_results[indicator_id] = {
                'positive_examples': int(positive_count),
                'negative_examples': int(negative_count),
                'train_f1': float(train_f1),
                'model_type': model_info['type']
            }

        self.is_fitted = True

        # Print model selection summary
        print_selection_summary(self.models, n_samples, n_features)

        # Evaluate on validation set if provided
        val_results = None
        if val_articles is not None and val_labels is not None:
            print(f"\n" + "-"*60)
            print(f"VALIDATION EVALUATION")
            print("-"*60)
            val_results = self.evaluate(val_articles, val_labels, dataset_name="Validation")

        # Store metadata
        self.training_metadata = {
            'n_train_samples': len(train_articles),
            'n_features': n_features,
            'model_selection_type': self.model_type,
            'per_indicator_results': per_indicator_results,
            'val_results': val_results
        }

        print("\n" + "="*60)
        print("TRAINING COMPLETE")
        print("="*60 + "\n")

        return self.training_metadata

    def predict_proba(self, articles: List[Dict]) -> np.ndarray:
        """
        Predict probability matrix for articles.

        Args:
            articles: List of article dictionaries

        Returns:
            Probability matrix (n_samples, 10) with values in [0, 1]
        """
        if not self.is_fitted:
            raise ValueError("MLClassifier must be trained before prediction. Call train() first.")

        # Extract features
        X = self.feature_extractor.transform_batch(articles)

        # Get predictions from each binary classifier
        proba_matrix = np.zeros((len(articles), 10))

        for i, indicator_id in enumerate(self.indicator_ids):
            model = self.models.get(indicator_id)

            # Check if model was trained (has coef_ attribute after fitting)
            if model is None or not hasattr(model, 'coef_'):
                # Model not trained (e.g., no positive examples)
                proba_matrix[:, i] = 0.0
                continue

            try:
                # Get probability of positive class
                proba = model.predict_proba(X)
                if proba.shape[1] == 2:
                    proba_matrix[:, i] = proba[:, 1]  # Probability of class 1
                else:
                    proba_matrix[:, i] = 0.0  # Only negative class exists
            except Exception as e:
                # If prediction fails, default to 0
                print(f"Warning: Could not predict for {indicator_id}: {e}")
                proba_matrix[:, i] = 0.0

        return proba_matrix

    def predict(
        self,
        articles: List[Dict],
        threshold: float = 0.5
    ) -> np.ndarray:
        """
        Predict binary labels for articles.

        Args:
            articles: List of article dictionaries
            threshold: Classification threshold (default 0.5)

        Returns:
            Binary label matrix (n_samples, 10)
        """
        proba = self.predict_proba(articles)
        return (proba >= threshold).astype(int)

    def classify_article(
        self,
        article_text: str,
        article_title: str = "",
        article_category: str = "",
        min_confidence: float = 0.3
    ) -> List[Dict]:
        """
        Classify a single article and return indicator assignments.

        Args:
            article_text: Article content
            article_title: Article title
            article_category: PESTEL category
            min_confidence: Minimum confidence threshold

        Returns:
            List of dicts with indicator_id, confidence
        """
        if not self.is_fitted:
            raise ValueError("MLClassifier must be trained before prediction")

        # Create article dict
        article = {
            'title': article_title,
            'content': article_text,
            'category': article_category
        }

        # Get probabilities
        proba = self.predict_proba([article])[0]

        # Build result list
        results = []
        for i, indicator_id in enumerate(self.indicator_ids):
            confidence = float(proba[i])

            if confidence >= min_confidence:
                results.append({
                    'indicator_id': indicator_id,
                    'confidence': confidence,
                    'method': 'ml'
                })

        # Sort by confidence (highest first)
        results.sort(key=lambda x: x['confidence'], reverse=True)

        return results

    def evaluate(
        self,
        articles: List[Dict],
        labels: np.ndarray,
        dataset_name: str = "Test"
    ) -> Dict:
        """
        Evaluate classifier on a dataset.

        Args:
            articles: List of article dictionaries
            labels: True binary labels (n_samples, 10)
            dataset_name: Name for reporting (e.g., "Validation", "Test")

        Returns:
            Dictionary with evaluation metrics
        """
        print(f"\nEvaluating on {dataset_name} set ({len(articles)} articles)...")

        # Get predictions
        y_pred_proba = self.predict_proba(articles)
        y_pred = (y_pred_proba >= 0.5).astype(int)
        y_true = labels

        # Overall metrics
        macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
        micro_f1 = f1_score(y_true, y_pred, average='micro', zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        macro_precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
        macro_recall = recall_score(y_true, y_pred, average='macro', zero_division=0)

        print(f"\n  Overall Metrics:")
        print(f"    Weighted F1: {weighted_f1:.3f} ← PRIMARY METRIC")
        print(f"    Macro F1: {macro_f1:.3f}")
        print(f"    Micro F1: {micro_f1:.3f}")
        print(f"    Macro Precision: {macro_precision:.3f}")
        print(f"    Macro Recall: {macro_recall:.3f}")

        # Per-indicator metrics
        print(f"\n  Per-Indicator F1 Scores:")
        per_indicator_metrics = {}

        for i, indicator_id in enumerate(self.indicator_ids):
            y_true_ind = y_true[:, i]
            y_pred_ind = y_pred[:, i]

            # Skip if no positive examples
            if y_true_ind.sum() == 0:
                print(f"    {indicator_id}: N/A (no examples)")
                per_indicator_metrics[indicator_id] = {
                    'f1': None,
                    'precision': None,
                    'recall': None,
                    'support': 0
                }
                continue

            f1 = f1_score(y_true_ind, y_pred_ind, zero_division=0)
            precision = precision_score(y_true_ind, y_pred_ind, zero_division=0)
            recall = recall_score(y_true_ind, y_pred_ind, zero_division=0)
            support = int(y_true_ind.sum())

            print(f"    {indicator_id}: F1={f1:.3f}, P={precision:.3f}, R={recall:.3f}, N={support}")

            per_indicator_metrics[indicator_id] = {
                'f1': float(f1),
                'precision': float(precision),
                'recall': float(recall),
                'support': support
            }

        # Success check
        print(f"\n  Target: Weighted F1 > 0.60")
        if weighted_f1 >= 0.60:
            print(f"  ✅ SUCCESS: {weighted_f1:.3f} >= 0.60")
        elif weighted_f1 >= 0.55:
            print(f"  ⚠️  CLOSE: {weighted_f1:.3f} (acceptable, proceed)")
        else:
            print(f"  ❌ BELOW TARGET: {weighted_f1:.3f} < 0.60 (consider fallback)")

        return {
            'dataset_name': dataset_name,
            'n_samples': len(articles),
            'weighted_f1': float(weighted_f1),
            'macro_f1': float(macro_f1),
            'micro_f1': float(micro_f1),
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'per_indicator': per_indicator_metrics
        }

    def save(self, model_dir: str):
        """
        Save trained model to disk.

        Args:
            model_dir: Directory to save models (e.g., 'backend/models/ml_classifier/')
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted MLClassifier. Call train() first.")

        output_path = Path(model_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save feature extractor
        self.feature_extractor.save(output_path / "feature_extractor.pkl")

        # Save all models
        models_dict = {}
        for indicator_id, model in self.models.items():
            if hasattr(model, 'coef_'):  # Check if trained
                models_dict[indicator_id] = model

        joblib.dump(models_dict, output_path / "ml_models.pkl")

        # Save metadata
        with open(output_path / "training_metadata.json", 'w') as f:
            json.dump(self.training_metadata, f, indent=2)

        # Save model version
        with open(output_path / "model_version.txt", 'w') as f:
            f.write("v1.0\n")

        print(f"\n✓ ML Classifier saved to: {model_dir}")
        print(f"  Files:")
        print(f"    - feature_extractor.pkl")
        print(f"    - ml_models.pkl ({len(models_dict)} trained models)")
        print(f"    - training_metadata.json")
        print(f"    - model_version.txt")

    @staticmethod
    def load(model_dir: str) -> 'MLClassifier':
        """
        Load trained model from disk.

        Args:
            model_dir: Directory containing saved models

        Returns:
            Loaded MLClassifier instance
        """
        model_path = Path(model_dir)

        # Load feature extractor
        feature_extractor = FeatureExtractor.load(model_path / "feature_extractor.pkl")

        # Load models
        models_dict = joblib.load(model_path / "ml_models.pkl")

        # Load metadata
        with open(model_path / "training_metadata.json", 'r') as f:
            training_metadata = json.load(f)

        # Create classifier instance
        classifier = MLClassifier(feature_extractor=feature_extractor)
        classifier.models = models_dict
        classifier.is_fitted = True
        classifier.training_metadata = training_metadata

        print(f"\n✓ ML Classifier loaded from: {model_dir}")
        print(f"  Loaded {len(models_dict)} trained models")

        return classifier

    def get_feature_importance(self, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get feature importance for each indicator (LogReg coefficients).

        Args:
            top_n: Number of top features to return per indicator

        Returns:
            Dict mapping indicator_id to list of (feature_name, coefficient) tuples
        """
        if not self.is_fitted:
            raise ValueError("Model must be trained first")

        feature_names = self.feature_extractor.get_feature_names()
        importance_dict = {}

        for indicator_id in self.indicator_ids:
            # Check if model exists (may have been skipped during training)
            if indicator_id not in self.models:
                importance_dict[indicator_id] = []
                continue

            model = self.models[indicator_id]

            if not hasattr(model, 'coef_'):
                importance_dict[indicator_id] = []
                continue

            # Get coefficients (absolute value)
            coefs = np.abs(model.coef_[0])

            # Get top features
            top_indices = np.argsort(coefs)[-top_n:][::-1]
            top_features = [
                (feature_names[idx], float(coefs[idx]))
                for idx in top_indices
            ]

            importance_dict[indicator_id] = top_features

        return importance_dict

    def print_model_summary(self):
        """Print summary of trained model with adaptive model information"""
        print("\n" + "="*60)
        print("ML CLASSIFIER SUMMARY")
        print("="*60)

        if self.is_fitted and self.training_metadata:
            n_features = self.training_metadata.get('n_features', 'N/A')
            model_selection_type = self.training_metadata.get('model_selection_type', 'auto')

            # Count model types
            model_types = {}
            for indicator_id, model in self.models.items():
                if hasattr(model, '__class__'):
                    model_type = type(model).__name__
                    model_types[model_type] = model_types.get(model_type, 0) + 1

            print(f"Architecture: Binary Relevance (Adaptive)")
            print(f"Model Selection: {model_selection_type}")
            print(f"Number of Indicators: {len(self.indicator_ids)}")
            print(f"Feature Dimensions: {n_features} (adaptive)")
            print(f"Fitted: {self.is_fitted}")

            print(f"\nModel Types Used:")
            for model_type, count in model_types.items():
                print(f"  {model_type}: {count} indicators")

            print(f"\nTraining Info:")
            print(f"  Training samples: {self.training_metadata.get('n_train_samples', 'N/A')}")

            val_results = self.training_metadata.get('val_results')
            if val_results:
                print(f"\nValidation Performance:")
                print(f"  Weighted F1: {val_results['weighted_f1']:.3f}")
                print(f"  Macro F1: {val_results['macro_f1']:.3f}")
        else:
            print(f"Model Selection: {self.model_type}")
            print(f"Number of Indicators: {len(self.indicator_ids)}")
            print(f"Fitted: {self.is_fitted}")

        print("="*60 + "\n")
