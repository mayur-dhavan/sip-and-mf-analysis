"""ML Engine component for volatility prediction - Enhanced version."""

import joblib
import os
from typing import Dict, Union
import numpy as np
from pathlib import Path


# All feature columns matching training
FEATURE_COLS = [
    'RSI', 'SMA_50', 'SMA_20', 'EMA_20',
    'Rolling_Volatility_30', 'Rolling_Volatility_10',
    'Daily_Return', 'ROC_10',
    'MACD', 'MACD_Signal', 'MACD_Hist',
    'BB_Width', 'NAV_to_SMA50_Ratio', 'Volatility_Ratio'
]

# Mapping from API feature keys to column names
FEATURE_KEY_MAP = {
    'rsi': 'RSI',
    'sma_50': 'SMA_50',
    'sma_20': 'SMA_20',
    'ema_20': 'EMA_20',
    'rolling_volatility_30': 'Rolling_Volatility_30',
    'rolling_volatility_10': 'Rolling_Volatility_10',
    'daily_return': 'Daily_Return',
    'roc_10': 'ROC_10',
    'macd': 'MACD',
    'macd_signal': 'MACD_Signal',
    'macd_hist': 'MACD_Hist',
    'bb_width': 'BB_Width',
    'nav_to_sma50_ratio': 'NAV_to_SMA50_Ratio',
    'volatility_ratio': 'Volatility_Ratio',
}


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
            else:
                self._model = artifact
                self._feature_cols = FEATURE_COLS
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
            # Build feature array in the correct column order
            feature_values = []
            for col in self._feature_cols:
                # Find the right key
                key = None
                for k, v in FEATURE_KEY_MAP.items():
                    if v == col:
                        key = k
                        break
                
                if key is None or key not in features:
                    raise PredictionError(f"Missing required feature: {col}")
                
                val = features[key]
                # Replace nan/inf with 0
                if np.isnan(val) or np.isinf(val):
                    val = 0.0
                feature_values.append(val)
            
            feature_array = np.array([feature_values])
            
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
