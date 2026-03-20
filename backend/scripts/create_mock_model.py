"""
Create a mock ML model for testing purposes.
This allows the application to run without training data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Create a simple trained model with dummy data
print("Creating mock model for testing...")

# Create dummy training data
X_dummy = np.array([
    [30, 100, 5],   # Low RSI, high SMA, low volatility -> Stable
    [70, 100, 15],  # High RSI, high SMA, high volatility -> High Risk
    [50, 100, 10],  # Medium values
    [40, 95, 8],
    [60, 105, 12],
])

y_dummy = np.array([0, 1, 0, 0, 1])  # 0=Stable, 1=High_Risk

# Train a simple model
model = RandomForestClassifier(
    n_estimators=10,
    max_depth=5,
    random_state=42
)

model.fit(X_dummy, y_dummy)

# Save the model
models_dir = Path(__file__).parent.parent / 'models'
models_dir.mkdir(exist_ok=True)

model_path = models_dir / 'volatility_model.pkl'
joblib.dump(model, model_path)

print(f"✓ Mock model saved to: {model_path}")
print("\nNote: This is a mock model for testing only.")
print("Run 'python scripts/train_model.py' to train a proper model with real data.")
