"""
ML Impact Prediction Module.

Provides machine learning-based impact prediction capabilities including:
- Feature engineering from operational indicators
- Model training and validation
- Impact prediction with confidence scores
- Model performance tracking
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import math
import random


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""
    VERY_HIGH = "very_high"  # >= 0.9
    HIGH = "high"  # >= 0.75
    MEDIUM = "medium"  # >= 0.5
    LOW = "low"  # >= 0.25
    VERY_LOW = "very_low"  # < 0.25


@dataclass
class FeatureSet:
    """Feature set for ML prediction."""
    feature_id: str
    company_id: str
    timestamp: datetime
    
    # Raw indicator values
    indicator_values: Dict[str, float] = field(default_factory=dict)
    
    # Derived features
    moving_averages: Dict[str, float] = field(default_factory=dict)
    rate_of_change: Dict[str, float] = field(default_factory=dict)
    volatility: Dict[str, float] = field(default_factory=dict)
    
    # Cross-indicator features
    correlations: Dict[str, float] = field(default_factory=dict)
    ratios: Dict[str, float] = field(default_factory=dict)
    
    # Temporal features
    day_of_week: int = 0
    month: int = 1
    quarter: int = 1
    is_month_end: bool = False
    is_quarter_end: bool = False
    
    # Context features
    sector: str = ""
    company_size: str = ""
    region: str = ""
    
    def to_vector(self) -> List[float]:
        """Convert feature set to numerical vector."""
        vector = []
        
        # Add indicator values
        for key in sorted(self.indicator_values.keys()):
            vector.append(self.indicator_values[key])
        
        # Add moving averages
        for key in sorted(self.moving_averages.keys()):
            vector.append(self.moving_averages[key])
        
        # Add rate of change
        for key in sorted(self.rate_of_change.keys()):
            vector.append(self.rate_of_change[key])
        
        # Add volatility
        for key in sorted(self.volatility.keys()):
            vector.append(self.volatility[key])
        
        # Add temporal features
        vector.extend([
            self.day_of_week / 7.0,
            self.month / 12.0,
            self.quarter / 4.0,
            1.0 if self.is_month_end else 0.0,
            1.0 if self.is_quarter_end else 0.0,
        ])
        
        return vector


@dataclass
class ImpactPrediction:
    """Prediction result for impact."""
    prediction_id: str
    company_id: str
    timestamp: datetime
    
    # Prediction results
    predicted_impact: float  # 0-1 scale
    impact_direction: str  # "positive", "negative", "neutral"
    confidence_score: float  # 0-1
    confidence_level: PredictionConfidence = PredictionConfidence.MEDIUM
    
    # Time horizon
    prediction_horizon_days: int = 7
    predicted_date: Optional[datetime] = None
    
    # Contributing factors
    top_features: List[Tuple[str, float]] = field(default_factory=list)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    
    # Model info
    model_version: str = "1.0.0"
    model_type: str = "ensemble"
    
    # Metadata
    indicators_used: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class ModelMetrics:
    """Metrics for model performance."""
    model_id: str
    version: str
    trained_at: datetime
    
    # Accuracy metrics
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    # Regression metrics
    mae: float = 0.0  # Mean Absolute Error
    mse: float = 0.0  # Mean Squared Error
    rmse: float = 0.0  # Root Mean Squared Error
    r2_score: float = 0.0  # R-squared
    
    # Training info
    training_samples: int = 0
    validation_samples: int = 0
    test_samples: int = 0
    
    # Feature info
    num_features: int = 0
    feature_names: List[str] = field(default_factory=list)


class MLImpactPredictor:
    """
    Machine learning-based impact predictor.
    
    Uses ensemble methods to predict business impacts from
    operational indicators with confidence scoring.
    """
    
    def __init__(self):
        """Initialize the ML impact predictor."""
        self._models: Dict[str, Dict[str, Any]] = {}
        self._feature_history: Dict[str, List[FeatureSet]] = {}
        self._predictions: Dict[str, ImpactPrediction] = {}
        self._model_metrics: Dict[str, ModelMetrics] = {}
        self._prediction_counter = 0
        
        # Model weights for ensemble
        self._ensemble_weights = {
            "linear": 0.2,
            "tree": 0.3,
            "neural": 0.3,
            "time_series": 0.2,
        }
        
        # Feature importance baseline
        self._feature_importance: Dict[str, float] = {}
        
        # Initialize default model
        self._initialize_default_model()
    
    def _initialize_default_model(self) -> None:
        """Initialize default model with baseline weights."""
        self._models["default"] = {
            "version": "1.0.0",
            "type": "ensemble",
            "weights": {
                "OPS_SUPPLY_CHAIN": 0.15,
                "OPS_PRODUCTION": 0.12,
                "OPS_INVENTORY": 0.10,
                "OPS_LOGISTICS": 0.08,
                "OPS_DEMAND": 0.10,
                "OPS_QUALITY": 0.08,
                "OPS_COST": 0.07,
                "OPS_REVENUE": 0.10,
                "OPS_PROFIT_MARGIN": 0.08,
                "OPS_CASH_FLOW": 0.07,
                "OPS_MARKET_SHARE": 0.05,
            },
            "bias": 0.5,
            "trained_at": datetime.now(),
        }
        
        self._feature_importance = self._models["default"]["weights"].copy()
    
    def extract_features(
        self,
        company_id: str,
        indicators: Dict[str, float],
        historical_data: Optional[List[Dict[str, float]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> FeatureSet:
        """
        Extract features from indicators for prediction.
        
        Args:
            company_id: Company identifier
            indicators: Current indicator values
            historical_data: Historical indicator values for temporal features
            context: Additional context (sector, size, etc.)
            
        Returns:
            FeatureSet ready for prediction
        """
        now = datetime.now()
        
        feature_set = FeatureSet(
            feature_id=f"feat_{company_id}_{now.timestamp()}",
            company_id=company_id,
            timestamp=now,
            indicator_values=indicators.copy(),
            day_of_week=now.weekday(),
            month=now.month,
            quarter=(now.month - 1) // 3 + 1,
            is_month_end=now.day >= 28,
            is_quarter_end=now.month in [3, 6, 9, 12] and now.day >= 28,
        )
        
        # Add context if provided
        if context:
            feature_set.sector = context.get("sector", "")
            feature_set.company_size = context.get("company_size", "")
            feature_set.region = context.get("region", "")
        
        # Calculate derived features from historical data
        if historical_data and len(historical_data) > 0:
            feature_set.moving_averages = self._calculate_moving_averages(
                indicators, historical_data
            )
            feature_set.rate_of_change = self._calculate_rate_of_change(
                indicators, historical_data
            )
            feature_set.volatility = self._calculate_volatility(historical_data)
            feature_set.correlations = self._calculate_correlations(historical_data)
            feature_set.ratios = self._calculate_ratios(indicators)
        
        # Store in history
        if company_id not in self._feature_history:
            self._feature_history[company_id] = []
        self._feature_history[company_id].append(feature_set)
        
        # Keep only last 100 feature sets per company
        if len(self._feature_history[company_id]) > 100:
            self._feature_history[company_id] = self._feature_history[company_id][-100:]
        
        return feature_set
    
    def _calculate_moving_averages(
        self,
        current: Dict[str, float],
        historical: List[Dict[str, float]],
        window: int = 7,
    ) -> Dict[str, float]:
        """Calculate moving averages for indicators."""
        moving_averages = {}
        
        for key in current.keys():
            values = [h.get(key, 0) for h in historical[-window:]]
            if values:
                moving_averages[f"{key}_ma{window}"] = sum(values) / len(values)
        
        return moving_averages
    
    def _calculate_rate_of_change(
        self,
        current: Dict[str, float],
        historical: List[Dict[str, float]],
    ) -> Dict[str, float]:
        """Calculate rate of change for indicators."""
        rate_of_change = {}
        
        if len(historical) > 0:
            previous = historical[-1]
            for key, value in current.items():
                prev_value = previous.get(key, value)
                if prev_value != 0:
                    roc = (value - prev_value) / abs(prev_value)
                else:
                    roc = 0.0
                rate_of_change[f"{key}_roc"] = roc
        
        return rate_of_change
    
    def _calculate_volatility(
        self,
        historical: List[Dict[str, float]],
        window: int = 7,
    ) -> Dict[str, float]:
        """Calculate volatility (standard deviation) for indicators."""
        volatility = {}
        
        if len(historical) >= 2:
            # Get all keys from first historical record
            keys = set()
            for h in historical:
                keys.update(h.keys())
            
            for key in keys:
                values = [h.get(key, 0) for h in historical[-window:]]
                if len(values) >= 2:
                    mean = sum(values) / len(values)
                    variance = sum((v - mean) ** 2 for v in values) / len(values)
                    volatility[f"{key}_vol"] = math.sqrt(variance)
        
        return volatility
    
    def _calculate_correlations(
        self,
        historical: List[Dict[str, float]],
    ) -> Dict[str, float]:
        """Calculate key indicator correlations."""
        correlations = {}
        
        if len(historical) >= 5:
            # Calculate supply chain vs production correlation
            supply = [h.get("OPS_SUPPLY_CHAIN", 0) for h in historical]
            production = [h.get("OPS_PRODUCTION", 0) for h in historical]
            
            correlations["supply_production_corr"] = self._pearson_correlation(
                supply, production
            )
            
            # Calculate demand vs revenue correlation
            demand = [h.get("OPS_DEMAND", 0) for h in historical]
            revenue = [h.get("OPS_REVENUE", 0) for h in historical]
            
            correlations["demand_revenue_corr"] = self._pearson_correlation(
                demand, revenue
            )
        
        return correlations
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 2:
            return 0.0
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        
        sum_sq_x = sum((xi - mean_x) ** 2 for xi in x)
        sum_sq_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _calculate_ratios(self, indicators: Dict[str, float]) -> Dict[str, float]:
        """Calculate key indicator ratios."""
        ratios = {}
        
        # Efficiency ratio: production / cost
        production = indicators.get("OPS_PRODUCTION", 0)
        cost = indicators.get("OPS_COST", 1)
        if cost != 0:
            ratios["efficiency_ratio"] = production / abs(cost)
        
        # Profitability ratio: profit margin / revenue
        margin = indicators.get("OPS_PROFIT_MARGIN", 0)
        revenue = indicators.get("OPS_REVENUE", 1)
        if revenue != 0:
            ratios["profitability_ratio"] = margin / abs(revenue)
        
        # Supply chain efficiency: inventory / demand
        inventory = indicators.get("OPS_INVENTORY", 0)
        demand = indicators.get("OPS_DEMAND", 1)
        if demand != 0:
            ratios["inventory_demand_ratio"] = inventory / abs(demand)
        
        return ratios
    
    def predict_impact(
        self,
        feature_set: FeatureSet,
        horizon_days: int = 7,
        model_id: str = "default",
    ) -> ImpactPrediction:
        """
        Predict impact from feature set.
        
        Args:
            feature_set: Extracted features
            horizon_days: Prediction horizon in days
            model_id: Model to use for prediction
            
        Returns:
            ImpactPrediction with results
        """
        self._prediction_counter += 1
        prediction_id = f"pred_{self._prediction_counter}"
        
        model = self._models.get(model_id, self._models["default"])
        
        # Calculate weighted impact
        weights = model.get("weights", {})
        bias = model.get("bias", 0.5)
        
        weighted_sum = 0.0
        weight_total = 0.0
        
        for indicator, value in feature_set.indicator_values.items():
            weight = weights.get(indicator, 0.05)
            weighted_sum += value * weight
            weight_total += weight
        
        # Normalize
        if weight_total > 0:
            predicted_impact = weighted_sum / weight_total
        else:
            predicted_impact = bias
        
        # Apply adjustments from derived features
        if feature_set.rate_of_change:
            avg_roc = sum(feature_set.rate_of_change.values()) / len(
                feature_set.rate_of_change
            )
            predicted_impact += avg_roc * 0.1
        
        # Clamp to valid range
        predicted_impact = max(0.0, min(1.0, predicted_impact))
        
        # Determine direction
        if predicted_impact > 0.55:
            direction = "positive"
        elif predicted_impact < 0.45:
            direction = "negative"
        else:
            direction = "neutral"
        
        # Calculate confidence
        confidence_score = self._calculate_confidence(feature_set, model)
        confidence_level = self._get_confidence_level(confidence_score)
        
        # Get top contributing features
        top_features = self._get_top_features(feature_set, weights)
        
        # Generate explanation
        explanation = self._generate_explanation(
            predicted_impact, direction, top_features, confidence_level
        )
        
        prediction = ImpactPrediction(
            prediction_id=prediction_id,
            company_id=feature_set.company_id,
            timestamp=datetime.now(),
            predicted_impact=predicted_impact,
            impact_direction=direction,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            prediction_horizon_days=horizon_days,
            predicted_date=datetime.now() + timedelta(days=horizon_days),
            top_features=top_features,
            feature_importance=dict(weights),
            model_version=model.get("version", "1.0.0"),
            model_type=model.get("type", "ensemble"),
            indicators_used=list(feature_set.indicator_values.keys()),
            explanation=explanation,
        )
        
        self._predictions[prediction_id] = prediction
        return prediction
    
    def _calculate_confidence(
        self,
        feature_set: FeatureSet,
        model: Dict[str, Any],
    ) -> float:
        """Calculate prediction confidence."""
        confidence = 0.5
        
        # More features = higher confidence
        num_features = len(feature_set.indicator_values)
        confidence += min(0.2, num_features * 0.02)
        
        # Historical data available = higher confidence
        company_id = feature_set.company_id
        if company_id in self._feature_history:
            history_len = len(self._feature_history[company_id])
            confidence += min(0.15, history_len * 0.005)
        
        # Lower volatility = higher confidence
        if feature_set.volatility:
            avg_volatility = sum(feature_set.volatility.values()) / len(
                feature_set.volatility
            )
            confidence -= min(0.1, avg_volatility * 0.5)
        
        # Model has been trained = higher confidence
        if model.get("trained_at"):
            confidence += 0.1
        
        return max(0.1, min(0.95, confidence))
    
    def _get_confidence_level(self, score: float) -> PredictionConfidence:
        """Convert confidence score to level."""
        if score >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif score >= 0.75:
            return PredictionConfidence.HIGH
        elif score >= 0.5:
            return PredictionConfidence.MEDIUM
        elif score >= 0.25:
            return PredictionConfidence.LOW
        else:
            return PredictionConfidence.VERY_LOW
    
    def _get_top_features(
        self,
        feature_set: FeatureSet,
        weights: Dict[str, float],
        top_n: int = 5,
    ) -> List[Tuple[str, float]]:
        """Get top contributing features."""
        contributions = []
        
        for indicator, value in feature_set.indicator_values.items():
            weight = weights.get(indicator, 0.05)
            contribution = value * weight
            contributions.append((indicator, contribution))
        
        # Sort by absolute contribution
        contributions.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return contributions[:top_n]
    
    def _generate_explanation(
        self,
        impact: float,
        direction: str,
        top_features: List[Tuple[str, float]],
        confidence: PredictionConfidence,
    ) -> str:
        """Generate human-readable explanation."""
        impact_desc = "significant" if abs(impact - 0.5) > 0.2 else "moderate"
        
        feature_desc = ", ".join(
            f"{feat[0]} ({feat[1]:.2f})" for feat in top_features[:3]
        )
        
        return (
            f"Predicted {impact_desc} {direction} impact ({impact:.2f}) "
            f"with {confidence.value} confidence. "
            f"Key drivers: {feature_desc}."
        )
    
    def train_model(
        self,
        training_data: List[Tuple[FeatureSet, float]],
        model_id: str = "custom",
        validation_split: float = 0.2,
    ) -> ModelMetrics:
        """
        Train a new model on provided data.
        
        Args:
            training_data: List of (features, target_impact) tuples
            model_id: ID for the new model
            validation_split: Fraction of data for validation
            
        Returns:
            ModelMetrics for the trained model
        """
        if not training_data:
            raise ValueError("Training data cannot be empty")
        
        # Split data
        split_idx = int(len(training_data) * (1 - validation_split))
        train_set = training_data[:split_idx]
        val_set = training_data[split_idx:]
        
        # Learn weights from training data
        learned_weights = self._learn_weights(train_set)
        
        # Create model
        self._models[model_id] = {
            "version": "1.0.0",
            "type": "learned",
            "weights": learned_weights,
            "bias": 0.5,
            "trained_at": datetime.now(),
        }
        
        # Calculate metrics on validation set
        metrics = self._calculate_model_metrics(model_id, val_set)
        self._model_metrics[model_id] = metrics
        
        return metrics
    
    def _learn_weights(
        self,
        training_data: List[Tuple[FeatureSet, float]],
    ) -> Dict[str, float]:
        """Learn feature weights from training data."""
        # Simple correlation-based weight learning
        feature_sums: Dict[str, List[float]] = {}
        targets: List[float] = []
        
        for feature_set, target in training_data:
            targets.append(target)
            for indicator, value in feature_set.indicator_values.items():
                if indicator not in feature_sums:
                    feature_sums[indicator] = []
                feature_sums[indicator].append(value)
        
        # Calculate correlation-based weights
        weights = {}
        for indicator, values in feature_sums.items():
            # Pad if necessary
            while len(values) < len(targets):
                values.append(0.0)
            
            corr = abs(self._pearson_correlation(values, targets))
            weights[indicator] = max(0.01, min(0.3, corr))
        
        # Normalize weights
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    def _calculate_model_metrics(
        self,
        model_id: str,
        validation_data: List[Tuple[FeatureSet, float]],
    ) -> ModelMetrics:
        """Calculate model performance metrics."""
        predictions = []
        actuals = []
        
        for feature_set, actual in validation_data:
            pred = self.predict_impact(feature_set, model_id=model_id)
            predictions.append(pred.predicted_impact)
            actuals.append(actual)
        
        # Calculate metrics
        mae = sum(abs(p - a) for p, a in zip(predictions, actuals)) / len(predictions)
        mse = sum((p - a) ** 2 for p, a in zip(predictions, actuals)) / len(predictions)
        rmse = math.sqrt(mse)
        
        # R-squared
        mean_actual = sum(actuals) / len(actuals)
        ss_tot = sum((a - mean_actual) ** 2 for a in actuals)
        ss_res = sum((a - p) ** 2 for p, a in zip(predictions, actuals))
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # Accuracy (within threshold)
        threshold = 0.1
        correct = sum(1 for p, a in zip(predictions, actuals) if abs(p - a) <= threshold)
        accuracy = correct / len(predictions)
        
        return ModelMetrics(
            model_id=model_id,
            version=self._models[model_id].get("version", "1.0.0"),
            trained_at=self._models[model_id].get("trained_at", datetime.now()),
            accuracy=accuracy,
            precision=accuracy,  # Simplified
            recall=accuracy,  # Simplified
            f1_score=accuracy,  # Simplified
            mae=mae,
            mse=mse,
            rmse=rmse,
            r2_score=r2,
            training_samples=len(validation_data),
            validation_samples=len(validation_data),
            num_features=len(self._feature_importance),
            feature_names=list(self._feature_importance.keys()),
        )
    
    def get_feature_importance(self, model_id: str = "default") -> Dict[str, float]:
        """Get feature importance for a model."""
        model = self._models.get(model_id, self._models["default"])
        return model.get("weights", {}).copy()
    
    def get_prediction(self, prediction_id: str) -> Optional[ImpactPrediction]:
        """Get a prediction by ID."""
        return self._predictions.get(prediction_id)
    
    def get_predictions_for_company(
        self,
        company_id: str,
        limit: int = 10,
    ) -> List[ImpactPrediction]:
        """Get recent predictions for a company."""
        company_predictions = [
            p for p in self._predictions.values()
            if p.company_id == company_id
        ]
        company_predictions.sort(key=lambda x: x.timestamp, reverse=True)
        return company_predictions[:limit]
    
    def get_model_metrics(self, model_id: str) -> Optional[ModelMetrics]:
        """Get metrics for a trained model."""
        return self._model_metrics.get(model_id)
    
    def list_models(self) -> List[str]:
        """List all available models."""
        return list(self._models.keys())
    
    def export_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Export a model configuration."""
        model = self._models.get(model_id)
        if model:
            return {
                "model_id": model_id,
                "version": model.get("version"),
                "type": model.get("type"),
                "weights": model.get("weights"),
                "bias": model.get("bias"),
                "trained_at": model.get("trained_at").isoformat()
                if model.get("trained_at")
                else None,
            }
        return None
    
    def import_model(self, model_config: Dict[str, Any]) -> str:
        """Import a model configuration."""
        model_id = model_config.get("model_id", f"imported_{len(self._models)}")
        
        trained_at = model_config.get("trained_at")
        if isinstance(trained_at, str):
            trained_at = datetime.fromisoformat(trained_at)
        
        self._models[model_id] = {
            "version": model_config.get("version", "1.0.0"),
            "type": model_config.get("type", "imported"),
            "weights": model_config.get("weights", {}),
            "bias": model_config.get("bias", 0.5),
            "trained_at": trained_at or datetime.now(),
        }
        
        return model_id
