"""
Adaptive Model Selector for ML Classification

Automatically selects the best model based on dataset size:
- Small data (<100 samples): LogisticRegression (prevents overfitting)
- Large data (≥100 samples): XGBoost (better performance)

This enables seamless scaling from small to large datasets while
maintaining optimal performance at each scale.
"""

from typing import Any, Dict
import warnings

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    warnings.warn("XGBoost not installed. Will use LogisticRegression for all dataset sizes.")

from sklearn.linear_model import LogisticRegression


def get_model_for_indicator(
    n_samples: int,
    n_features: int,
    indicator_id: str,
    model_type: str = "auto",
    verbose: bool = True
) -> Any:
    """
    Select appropriate model based on dataset size.

    Args:
        n_samples: Number of training samples
        n_features: Number of features
        indicator_id: Indicator identifier (for logging)
        model_type: Model selection strategy
            - "auto": Automatically choose based on data size (recommended)
            - "logistic": Force LogisticRegression
            - "xgboost": Force XGBoost (if available)
        verbose: Print selection reasoning

    Returns:
        Sklearn-compatible classifier instance

    Selection Logic:
        - n_samples < 100: LogisticRegression (better for small data)
        - n_samples ≥ 100 AND samples_per_feature ≥ 2: XGBoost (original plan)
        - XGBoost unavailable: LogisticRegression (fallback)
    """
    # Force specific model type if requested
    if model_type == "xgboost":
        if not XGBOOST_AVAILABLE:
            if verbose:
                print(f"⚠️  [{indicator_id}] XGBoost not available, falling back to LogisticRegression")
            model_type = "logistic"
        else:
            if verbose:
                print(f"🔧 [{indicator_id}] Forcing XGBoost (manual override)")
            return _create_xgboost_model()

    if model_type == "logistic":
        if verbose:
            print(f"🔧 [{indicator_id}] Forcing LogisticRegression (manual override)")
        return _create_logistic_regression_model()

    # Auto mode: decide based on data characteristics
    if model_type == "auto":
        # Calculate samples per feature ratio
        samples_per_feature = n_samples / n_features if n_features > 0 else 0

        # Decision logic
        if n_samples < 100:
            # Small dataset: Use LogisticRegression
            reason = f"n_samples={n_samples} < 100 (small data)"
            model = _create_logistic_regression_model()
            model_name = "LogisticRegression"

        elif samples_per_feature < 2:
            # Not enough samples per feature for tree models
            reason = f"samples/feature={samples_per_feature:.1f} < 2 (insufficient ratio)"
            model = _create_logistic_regression_model()
            model_name = "LogisticRegression"

        elif not XGBOOST_AVAILABLE:
            # XGBoost not installed
            reason = "XGBoost not available"
            model = _create_logistic_regression_model()
            model_name = "LogisticRegression"

        else:
            # Large dataset: Use XGBoost (original plan)
            reason = f"n_samples={n_samples} ≥ 100, ratio={samples_per_feature:.1f} ≥ 2 ✅ ORIGINAL PLAN"
            model = _create_xgboost_model()
            model_name = "XGBoost"

        if verbose:
            print(f"🤖 [{indicator_id}] Selected {model_name}: {reason}")

        return model

    else:
        raise ValueError(f"Invalid model_type: {model_type}. Use 'auto', 'logistic', or 'xgboost'")


def _create_logistic_regression_model() -> LogisticRegression:
    """
    Create LogisticRegression model optimized for small datasets.

    Hyperparameters chosen for:
    - Overfitting prevention (L2 regularization)
    - Class imbalance handling
    - Stability with limited samples
    """
    return LogisticRegression(
        C=1.0,                    # Light L2 regularization
        penalty='l2',             # Ridge regularization
        class_weight='balanced',  # Handle class imbalance automatically
        max_iter=1000,            # Sufficient for convergence
        random_state=42,          # Reproducibility
        solver='lbfgs'            # Good for small-medium datasets
    )


def _create_xgboost_model() -> Any:
    """
    Create XGBoost model optimized for large datasets.

    Hyperparameters from original plan (Day 3):
    - Designed for 100+ samples per indicator
    - Balanced between performance and overfitting prevention
    - Matches original plan specifications
    """
    if not XGBOOST_AVAILABLE:
        raise ImportError("XGBoost is not installed. Install with: pip install xgboost")

    return xgb.XGBClassifier(
        max_depth=6,              # Tree depth (original plan)
        learning_rate=0.1,        # Step size shrinkage
        n_estimators=100,         # Number of trees (original plan)
        min_child_weight=3,       # Minimum sum of instance weight in child
        subsample=0.8,            # Row sampling ratio
        colsample_bytree=0.8,     # Column sampling ratio
        scale_pos_weight=1,       # Class imbalance (will be auto-tuned per indicator)
        random_state=42,          # Reproducibility
        eval_metric='logloss',    # Evaluation metric
        use_label_encoder=False   # Suppress warning
    )


def get_model_info(model: Any) -> Dict[str, Any]:
    """
    Get information about a model instance.

    Args:
        model: Model instance

    Returns:
        Dictionary with model type and key hyperparameters
    """
    model_type = type(model).__name__

    if model_type == "LogisticRegression":
        return {
            "type": "LogisticRegression",
            "C": model.C,
            "penalty": model.penalty,
            "solver": model.solver,
            "class_weight": model.class_weight
        }
    elif model_type == "XGBClassifier":
        return {
            "type": "XGBoost",
            "max_depth": model.max_depth,
            "learning_rate": model.learning_rate,
            "n_estimators": model.n_estimators,
            "min_child_weight": model.min_child_weight
        }
    else:
        return {
            "type": model_type,
            "class": str(model.__class__)
        }


def print_selection_summary(models: Dict[str, Any], n_samples: int, n_features: int):
    """
    Print summary of model selections.

    Args:
        models: Dictionary mapping indicator_id to model instance
        n_samples: Number of training samples
        n_features: Number of features
    """
    print("\n" + "="*70)
    print("MODEL SELECTION SUMMARY")
    print("="*70)
    print(f"Dataset: {n_samples} samples, {n_features} features")
    print(f"Samples per feature: {n_samples / n_features:.2f}")
    print()

    # Count model types
    model_types = {}
    for model in models.values():
        model_type = type(model).__name__
        model_types[model_type] = model_types.get(model_type, 0) + 1

    print("Models Selected:")
    for model_type, count in model_types.items():
        print(f"  {model_type}: {count} indicators")

    print()

    # Decision explanation
    if n_samples < 100:
        print("💡 Decision: Using LogisticRegression for small dataset")
        print(f"   When data grows to 100+ samples, system will automatically")
        print(f"   switch to XGBoost (original plan)")
    else:
        print("✅ Decision: Using XGBoost (ORIGINAL PLAN)")
        print(f"   Large dataset detected, optimal model selected")

    print("="*70 + "\n")


# Usage example and testing
if __name__ == "__main__":
    print("Testing Adaptive Model Selector\n")

    # Test 1: Small dataset (current)
    print("[Test 1] Small Dataset (36 samples, 59 features)")
    model_small = get_model_for_indicator(36, 59, "POL_UNREST", "auto")
    assert type(model_small).__name__ == "LogisticRegression", "Should use LogReg for small data"
    print("✅ Correctly selected LogisticRegression\n")

    # Test 2: Medium dataset
    print("[Test 2] Medium Dataset (80 samples, 59 features)")
    model_medium = get_model_for_indicator(80, 59, "ECO_INFLATION", "auto")
    assert type(model_medium).__name__ == "LogisticRegression", "Should still use LogReg"
    print("✅ Correctly selected LogisticRegression\n")

    # Test 3: Large dataset (original plan)
    print("[Test 3] Large Dataset (150 samples, 61 features)")
    model_large = get_model_for_indicator(150, 61, "POL_UNREST", "auto")
    if XGBOOST_AVAILABLE:
        assert type(model_large).__name__ == "XGBClassifier", "Should use XGBoost for large data"
        print("✅ Correctly selected XGBoost (ORIGINAL PLAN)\n")
    else:
        assert type(model_large).__name__ == "LogisticRegression", "Should fallback to LogReg"
        print("✅ Correctly fell back to LogisticRegression (XGBoost not installed)\n")

    # Test 4: Model info
    print("[Test 4] Model Info Extraction")
    info = get_model_info(model_small)
    print(f"Model info: {info}")
    assert info["type"] == "LogisticRegression"
    print("✅ Model info extraction working\n")

    print("🎉 All tests passed!")
    print("\nAdaptive Model Selector ready for production use.")
    print("\nTo integrate:")
    print("  1. Update ml_classifier.py to use get_model_for_indicator()")
    print("  2. Set ML_MODEL_TYPE='auto' in config.py")
    print("  3. System will automatically scale from LogReg → XGBoost")
