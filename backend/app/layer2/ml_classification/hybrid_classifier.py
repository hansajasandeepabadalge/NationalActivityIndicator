"""
Hybrid Classifier - Combines Rule-Based and ML Predictions

Strategy:
- Start conservative: 0.7 rule-based + 0.3 ML (trust proven system)
- Tune per-indicator weights on validation set
- Context-aware conflict resolution
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import json
from pathlib import Path

from app.layer2.ml_classification.rule_based_classifier import RuleBasedClassifier
from app.layer2.ml_classification.ml_classifier import MLClassifier


class HybridClassifier:
    """Combine rule-based and ML predictions with per-indicator weight tuning"""

    def __init__(
        self,
        rule_classifier: Optional[RuleBasedClassifier] = None,
        ml_classifier: Optional[MLClassifier] = None,
        default_weight_rule: float = 0.7,
        default_weight_ml: float = 0.3
    ):
        """
        Initialize hybrid classifier.

        Args:
            rule_classifier: RuleBasedClassifier instance
            ml_classifier: Trained MLClassifier instance
            default_weight_rule: Default weight for rule-based (0.7)
            default_weight_ml: Default weight for ML (0.3)
        """
        self.rule_classifier = rule_classifier or RuleBasedClassifier()
        self.ml_classifier = ml_classifier

        # Default weights (conservative: trust rule-based more)
        self.default_weight_rule = default_weight_rule
        self.default_weight_ml = default_weight_ml

        # Per-indicator weights (learned from validation)
        self.indicator_weights = {}

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

        # Flag for whether weights have been tuned
        self.weights_tuned = False

    def classify(
        self,
        article_text: str,
        article_title: str = "",
        article_category: str = "",
        min_confidence: float = 0.3
    ) -> List[Dict]:
        """
        Classify article using hybrid approach.

        Args:
            article_text: Article content
            article_title: Article title
            article_category: PESTEL category
            min_confidence: Minimum confidence threshold

        Returns:
            List of dicts with indicator_id, confidence, method
        """
        # Get rule-based predictions
        rule_predictions = self.rule_classifier.classify_article(
            article_text=article_text,
            article_title=article_title
        )

        rule_confidences = {
            pred['indicator_id']: pred['confidence']
            for pred in rule_predictions
        }

        # Get ML predictions (if available)
        ml_confidences = {}
        if self.ml_classifier and self.ml_classifier.is_fitted:
            ml_predictions = self.ml_classifier.classify_article(
                article_text=article_text,
                article_title=article_title,
                article_category=article_category,
                min_confidence=0.0  # Get all predictions
            )

            ml_confidences = {
                pred['indicator_id']: pred['confidence']
                for pred in ml_predictions
            }

        # Merge predictions
        hybrid_results = self._merge_predictions(
            rule_confidences=rule_confidences,
            ml_confidences=ml_confidences
        )

        # Apply confidence threshold
        filtered_results = [
            result for result in hybrid_results
            if result['confidence'] >= min_confidence
        ]

        # Sort by confidence (highest first)
        filtered_results.sort(key=lambda x: x['confidence'], reverse=True)

        # Apply conflict resolution (limit to top 4)
        if len(filtered_results) > 4:
            filtered_results = filtered_results[:4]

        return filtered_results

    def _merge_predictions(
        self,
        rule_confidences: Dict[str, float],
        ml_confidences: Dict[str, float]
    ) -> List[Dict]:
        """
        Merge rule-based and ML predictions with weighted averaging.

        Args:
            rule_confidences: Dict of indicator_id -> confidence from rules
            ml_confidences: Dict of indicator_id -> confidence from ML

        Returns:
            List of hybrid predictions
        """
        all_indicators = set(rule_confidences.keys()) | set(ml_confidences.keys())

        results = []

        for indicator_id in all_indicators:
            rule_conf = rule_confidences.get(indicator_id, 0.0)
            ml_conf = ml_confidences.get(indicator_id, 0.0)

            # Get weights for this indicator
            weight_rule = self.indicator_weights.get(
                indicator_id,
                self.default_weight_rule
            )
            weight_ml = 1 - weight_rule

            # Context-aware weight adjustment
            if rule_conf > 0.8:
                # High-confidence rule: trust it more
                weight_rule = 0.9
                weight_ml = 0.1
            elif rule_conf < 0.3:
                # Low-confidence rule: trust ML more
                weight_rule = 0.4
                weight_ml = 0.6

            # Calculate hybrid confidence
            hybrid_conf = (rule_conf * weight_rule) + (ml_conf * weight_ml)

            # Determine method
            if rule_conf > 0 and ml_conf > 0:
                method = "hybrid"
            elif rule_conf > 0:
                method = "rule_only"
                hybrid_conf = rule_conf * weight_rule  # Discount by weight
            elif ml_conf > 0:
                method = "ml_only"
                hybrid_conf = ml_conf * weight_ml  # Discount by weight
            else:
                continue  # Both zero, skip

            results.append({
                'indicator_id': indicator_id,
                'confidence': float(hybrid_conf),
                'method': method,
                'rule_confidence': float(rule_conf),
                'ml_confidence': float(ml_conf),
                'weight_rule': float(weight_rule),
                'weight_ml': float(weight_ml)
            })

        return results

    def tune_weights(
        self,
        val_articles: List[Dict],
        val_labels: np.ndarray
    ):
        """
        Tune per-indicator weights on validation set using grid search.

        Args:
            val_articles: List of validation article dicts
            val_labels: True binary labels (n_samples, 10)
        """
        if not self.ml_classifier or not self.ml_classifier.is_fitted:
            print("⚠️  ML classifier not available. Using default weights.")
            return

        print("\n" + "="*60)
        print("TUNING HYBRID WEIGHTS")
        print("="*60)

        # Get predictions from both classifiers
        print(f"\nGetting predictions for {len(val_articles)} validation articles...")

        rule_predictions_all = []
        ml_predictions_all = []

        for article in val_articles:
            # Rule-based
            rule_preds = self.rule_classifier.classify_article(
                article_text=article.get('content', ''),
                article_title=article.get('title', '')
            )
            rule_conf_dict = {
                pred['indicator_id']: pred['confidence']
                for pred in rule_preds
            }
            rule_predictions_all.append(rule_conf_dict)

            # ML
            ml_preds = self.ml_classifier.classify_article(
                article_text=article.get('content', ''),
                article_title=article.get('title', ''),
                article_category=article.get('category', ''),
                min_confidence=0.0
            )
            ml_conf_dict = {
                pred['indicator_id']: pred['confidence']
                for pred in ml_preds
            }
            ml_predictions_all.append(ml_conf_dict)

        # Grid search for each indicator
        print(f"\nGrid search for optimal weights per indicator...")
        print(f"  Testing weights: [0.0, 0.1, 0.2, ..., 1.0]")

        weight_candidates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        for i, indicator_id in enumerate(self.indicator_ids):
            y_true = val_labels[:, i]

            # Skip if no positive examples
            if y_true.sum() == 0:
                print(f"\n  {indicator_id}: Skipped (no examples)")
                self.indicator_weights[indicator_id] = self.default_weight_rule
                continue

            best_f1 = 0.0
            best_weight_rule = self.default_weight_rule

            # Try each weight
            for weight_rule in weight_candidates:
                weight_ml = 1 - weight_rule

                # Calculate hybrid predictions
                y_pred = []
                for rule_conf_dict, ml_conf_dict in zip(rule_predictions_all, ml_predictions_all):
                    rule_conf = rule_conf_dict.get(indicator_id, 0.0)
                    ml_conf = ml_conf_dict.get(indicator_id, 0.0)

                    hybrid_conf = (rule_conf * weight_rule) + (ml_conf * weight_ml)
                    y_pred.append(1 if hybrid_conf >= 0.5 else 0)

                y_pred = np.array(y_pred)

                # Calculate F1
                from sklearn.metrics import f1_score
                f1 = f1_score(y_true, y_pred, zero_division=0)

                if f1 > best_f1:
                    best_f1 = f1
                    best_weight_rule = weight_rule

            # Store best weight
            self.indicator_weights[indicator_id] = best_weight_rule

            print(f"\n  {indicator_id}:")
            print(f"    Best weight: {best_weight_rule:.1f} rule / {1-best_weight_rule:.1f} ML")
            print(f"    Best F1: {best_f1:.3f}")

        self.weights_tuned = True

        print("\n" + "="*60)
        print("WEIGHT TUNING COMPLETE")
        print("="*60)
        self._print_weight_summary()

    def _print_weight_summary(self):
        """Print summary of tuned weights"""
        print("\nTuned Weights Summary:")
        print("-" * 60)

        for indicator_id in self.indicator_ids:
            weight_rule = self.indicator_weights.get(indicator_id, self.default_weight_rule)
            weight_ml = 1 - weight_rule

            # Interpret weight
            if weight_rule >= 0.8:
                interpretation = "Trust rule-based (ML weak)"
            elif weight_rule >= 0.6:
                interpretation = "Prefer rule-based"
            elif weight_rule >= 0.4:
                interpretation = "Balanced"
            elif weight_rule >= 0.2:
                interpretation = "Prefer ML"
            else:
                interpretation = "Trust ML (rules weak)"

            print(f"  {indicator_id}: {weight_rule:.1f}R / {weight_ml:.1f}ML  ({interpretation})")

        print("-" * 60 + "\n")

    def evaluate_hybrid(
        self,
        val_articles: List[Dict],
        val_labels: np.ndarray,
        min_confidence: float = 0.5
    ) -> Dict:
        """
        Evaluate hybrid classifier on validation set.

        Args:
            val_articles: Validation articles
            val_labels: True labels (n_samples, 10)
            min_confidence: Classification threshold

        Returns:
            Evaluation results
        """
        print("\n" + "="*60)
        print("EVALUATING HYBRID CLASSIFIER")
        print("="*60)

        # Get predictions
        y_pred_matrix = np.zeros((len(val_articles), 10))

        for idx, article in enumerate(val_articles):
            predictions = self.classify(
                article_text=article.get('content', ''),
                article_title=article.get('title', ''),
                article_category=article.get('category', ''),
                min_confidence=0.0  # Get all, apply threshold later
            )

            for pred in predictions:
                indicator_idx = self.indicator_ids.index(pred['indicator_id'])
                y_pred_matrix[idx, indicator_idx] = pred['confidence']

        # Apply threshold
        y_pred = (y_pred_matrix >= min_confidence).astype(int)
        y_true = val_labels

        # Calculate metrics
        from sklearn.metrics import f1_score, precision_score, recall_score

        weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
        macro_precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
        macro_recall = recall_score(y_true, y_pred, average='macro', zero_division=0)

        print(f"\n  Hybrid Performance:")
        print(f"    Weighted F1: {weighted_f1:.3f}")
        print(f"    Macro F1: {macro_f1:.3f}")
        print(f"    Macro Precision: {macro_precision:.3f}")
        print(f"    Macro Recall: {macro_recall:.3f}")

        # Compare with rule-only and ML-only
        print(f"\n  Component Performance:")

        # Rule-only
        rule_only_preds = np.zeros((len(val_articles), 10))
        for idx, article in enumerate(val_articles):
            rule_preds = self.rule_classifier.classify_article(
                article_text=article.get('content', ''),
                article_title=article.get('title', '')
            )
            for pred in rule_preds:
                indicator_idx = self.indicator_ids.index(pred['indicator_id'])
                rule_only_preds[idx, indicator_idx] = pred['confidence']

        rule_only_binary = (rule_only_preds >= min_confidence).astype(int)
        rule_f1 = f1_score(y_true, rule_only_binary, average='weighted', zero_division=0)
        print(f"    Rule-only F1: {rule_f1:.3f}")

        # ML-only
        if self.ml_classifier and self.ml_classifier.is_fitted:
            ml_only_proba = self.ml_classifier.predict_proba([
                {'title': art.get('title', ''), 'content': art.get('content', ''), 'category': art.get('category', '')}
                for art in val_articles
            ])
            ml_only_binary = (ml_only_proba >= min_confidence).astype(int)
            ml_f1 = f1_score(y_true, ml_only_binary, average='weighted', zero_division=0)
            print(f"    ML-only F1: {ml_f1:.3f}")
        else:
            ml_f1 = 0.0
            print(f"    ML-only F1: N/A (not trained)")

        # Check improvement
        print(f"\n  Improvement:")
        improvement_vs_rule = weighted_f1 - rule_f1
        improvement_vs_ml = weighted_f1 - ml_f1

        print(f"    vs Rule-based: {improvement_vs_rule:+.3f}")
        if ml_f1 > 0:
            print(f"    vs ML-only: {improvement_vs_ml:+.3f}")

        if weighted_f1 >= max(rule_f1, ml_f1):
            print(f"    ✅ Hybrid is best!")
        else:
            print(f"    ⚠️  Hybrid not improving (check weights)")

        print("="*60 + "\n")

        return {
            'weighted_f1': float(weighted_f1),
            'macro_f1': float(macro_f1),
            'rule_only_f1': float(rule_f1),
            'ml_only_f1': float(ml_f1),
            'improvement_vs_rule': float(improvement_vs_rule),
            'improvement_vs_ml': float(improvement_vs_ml)
        }

    def save_weights(self, path: str):
        """Save tuned weights to file"""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        weights_data = {
            'default_weight_rule': self.default_weight_rule,
            'default_weight_ml': self.default_weight_ml,
            'indicator_weights': self.indicator_weights,
            'weights_tuned': self.weights_tuned
        }

        with open(output_path, 'w') as f:
            json.dump(weights_data, f, indent=2)

        print(f"✓ Hybrid weights saved to: {path}")

    def load_weights(self, path: str):
        """Load tuned weights from file"""
        with open(path, 'r') as f:
            weights_data = json.load(f)

        self.default_weight_rule = weights_data['default_weight_rule']
        self.default_weight_ml = weights_data['default_weight_ml']
        self.indicator_weights = weights_data['indicator_weights']
        self.weights_tuned = weights_data['weights_tuned']

        print(f"✓ Hybrid weights loaded from: {path}")
