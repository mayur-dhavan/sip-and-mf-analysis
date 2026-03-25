"""ML Engine component for volatility prediction - Enhanced version."""

import joblib
import os
from typing import Dict, Union
import numpy as np
import pandas as pd
from pathlib import Path
from app.services.feature_config import FEATURE_COLS, FEATURE_KEY_MAP


HF_SPACE_REPO = "mayur6901/sip-mf-volatility-predictor"
HF_MODEL_FILENAME = "volatility_model.pkl"


class ModelNotFoundError(Exception):
    """Raised when the ML model file is not found."""
    pass


class PredictionError(Exception):
    """Raised when prediction fails."""
    pass


def _download_model_from_hf(dest_path: str) -> str:
    """Download model from Hugging Face Space if not available locally."""
    try:
        from huggingface_hub import hf_hub_download
        print(f"Model not found locally. Downloading from HF Space: {HF_SPACE_REPO} ...")
        downloaded = hf_hub_download(
            repo_id=HF_SPACE_REPO,
            filename=HF_MODEL_FILENAME,
            repo_type="space",
        )
        # Copy to expected local path so future loads are instant
        dest = Path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(downloaded, dest)
        print(f"Model downloaded to {dest}")
        return str(dest)
    except Exception as e:
        print(f"HF download failed: {e}")
        raise ModelNotFoundError(
            f"Model not found locally and HF download failed: {e}"
        )


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
        """Load pre-trained model from disk, downloading from HF if needed."""
        path = model_path or self.model_path
        
        if not os.path.exists(path):
            path = _download_model_from_hf(path)
        
        try:
            artifact = joblib.load(path)
            # Support both new artifact format and legacy raw model
            if isinstance(artifact, dict) and 'model' in artifact:
                self._model = artifact['model']
                self._feature_cols = artifact.get('feature_cols', FEATURE_COLS)
                loaded_threshold = float(artifact.get('decision_threshold', 0.5))
                override = os.getenv("MODEL_DECISION_THRESHOLD_OVERRIDE")
                if override is not None:
                    try:
                        loaded_threshold = float(override)
                    except ValueError:
                        pass
                # Guard against pathological thresholds that can collapse outputs.
                self._decision_threshold = float(np.clip(loaded_threshold, 0.15, 0.85))
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
            elif hasattr(self._model, "decision_function"):
                score = float(self._model.decision_function(feature_array)[0])
                high_risk_probability = float(1.0 / (1.0 + np.exp(-score)))
            else:
                high_risk_probability = float(self._model.predict(feature_array)[0])

            high_risk_probability = float(np.clip(high_risk_probability, 0.0, 1.0))

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
