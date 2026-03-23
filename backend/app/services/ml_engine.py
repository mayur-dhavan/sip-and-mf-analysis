"""ML Engine component for volatility prediction - Enhanced version."""

import joblib
import os
from typing import Dict, Union
import numpy as np
import pandas as pd
from pathlib import Path
from app.services.feature_config import FEATURE_COLS, FEATURE_KEY_MAP



class ModelNotFoundError(Exception):
    """Raised when the ML model file is not found."""
    pass


class PredictionError(Exception):
    """Raised when prediction fails."""
    pass


class MLEngine:
    """Handles ML model loading and volatility prediction."""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            base_dir = Path(__file__).parent.parent.parent
            model_path = base_dir / "models" / "volatility_model.pkl"
        
        self.model_path = str(model_path)
        self._model = None
        self._feature_cols = FEATURE_COLS
        self._decision_threshold = 0.5
    
    def load_model(self, model_path: str = None) -> object:
        """Load pre-trained model from disk."""
        path = model_path or self.model_path
        
        if not os.path.exists(path):
            raise ModelNotFoundError(
                f"Model file not found at '{path}'. Please train the model first."
            )
        
        try:
            artifact = joblib.load(path)
            # Support both new artifact format and legacy raw model
            if isinstance(artifact, dict) and 'model' in artifact:
                self._model = artifact['model']
                self._feature_cols = artifact.get('feature_cols', FEATURE_COLS)
                self._decision_threshold = float(artifact.get('decision_threshold', 0.5))
            else:
                self._model = artifact
                self._feature_cols = FEATURE_COLS
                self._decision_threshold = 0.5
            return self._model
        except Exception as e:
            raise ModelNotFoundError(
                f"Failed to load model from '{path}': {str(e)}"
            )
    
    def predict_volatility(self, features: Dict[str, float]) -> int:
        """
        Predict volatility risk for given features.
        
        Args:
            features: Dict with lowercase feature keys matching FEATURE_KEY_MAP
            
        Returns:
            0 for Stable, 1 for High_Risk
        """
        if self._model is None:
            self.load_model()
        
        try:
            feature_array = self._build_feature_array(features)

            prediction = self._model.predict(feature_array)
            result = int(prediction[0])
            
            if result not in [0, 1]:
                raise PredictionError(
                    f"Invalid prediction output: {result}. Expected 0 or 1."
                )
            
            return result
            
        except PredictionError:
            raise
        except Exception as e:
            raise PredictionError(f"Prediction failed: {str(e)}")

    def predict_with_confidence(self, features: Dict[str, float]) -> tuple[int, float, float]:
        """
        Predict class plus probability metadata.

        Returns:
            Tuple[prediction, high_risk_probability, confidence]
        """
        if self._model is None:
            self.load_model()

        try:
            feature_array = self._build_feature_array(features)
            high_risk_probability = 0.5
            if hasattr(self._model, "predict_proba"):
                probs = self._model.predict_proba(feature_array)[0]
                if len(probs) >= 2:
                    high_risk_probability = float(probs[1])
                else:
                    high_risk_probability = float(probs[0])

            prediction = int(high_risk_probability >= self._decision_threshold)

            confidence = max(high_risk_probability, 1.0 - high_risk_probability)
            return prediction, high_risk_probability, float(confidence)
        except Exception as e:
            raise PredictionError(f"Prediction with confidence failed: {str(e)}")

    def _build_feature_array(self, features: Dict[str, float]) -> pd.DataFrame:
        """Build one-row DataFrame in model column order with safe value handling."""
        feature_values = []
        for col in self._feature_cols:
            key = None
            for k, v in FEATURE_KEY_MAP.items():
                if v == col:
                    key = k
                    break

            if key is None or key not in features:
                raise PredictionError(f"Missing required feature: {col}")

            val = features[key]
            if np.isnan(val) or np.isinf(val):
                val = 0.0
            feature_values.append(val)

        return pd.DataFrame([feature_values], columns=self._feature_cols)
