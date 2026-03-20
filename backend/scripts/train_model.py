"""
ML Model Training Script - Enhanced Version

This script trains an ensemble model (XGBoost + Random Forest with soft voting)
to predict mutual fund volatility risk. Uses expanded technical indicators,
cross-validation, and hyperparameter tuning for better accuracy.

Usage:
    python scripts/train_model.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib
from typing import List, Tuple

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("Warning: XGBoost not installed. Using GradientBoosting as fallback.")

from app.services.data_fetcher import DataFetcher
from app.services.feature_calculator import FeatureCalculator


# Expanded training tickers - Indian Small/Mid-Cap Mutual Funds and equity ETFs
TRAINING_TICKERS = [
    "NIPPONINDIA.NS",
    "0P0000XVKR.BO",   # Axis Small Cap Fund
    "0P0000XVL1.BO",   # SBI Small Cap Fund
    "0P00013CZ6.BO",   # HDFC Small Cap Fund
    "0P0000XVKY.BO",   # Kotak Small Cap Fund
    "0P0001BAP8.BO",   # Quant Small Cap Fund
    "0P0000XVLR.BO",   # DSP Small Cap Fund
    "0P0001BHGZ.BO",   # ICICI Pru Smallcap Fund
    "^NSEI",            # Nifty 50 (benchmark for general market)
    "^NSMIDCP",         # Nifty Midcap index
]

# All feature columns used for training
FEATURE_COLS = [
    'RSI', 'SMA_50', 'SMA_20', 'EMA_20',
    'Rolling_Volatility_30', 'Rolling_Volatility_10',
    'Daily_Return', 'ROC_10',
    'MACD', 'MACD_Signal', 'MACD_Hist',
    'BB_Width', 'NAV_to_SMA50_Ratio', 'Volatility_Ratio'
]


def prepare_training_data(tickers: List[str]) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Fetch data for multiple tickers and prepare training dataset with expanded features.
    """
    data_fetcher = DataFetcher()
    feature_calculator = FeatureCalculator()
    
    all_features = []
    all_labels = []
    
    print(f"Fetching data for {len(tickers)} tickers...")
    
    for ticker in tickers:
        try:
            print(f"  Processing {ticker}...")
            
            # Fetch NAV data
            nav_df = data_fetcher.fetch_nav_data(ticker, period="3y")
            
            # Calculate technical indicators (all expanded features)
            features_df = feature_calculator.calculate_all_features(nav_df)
            
            # Calculate 15-day forward returns for labeling
            features_df['Future_Return'] = (
                features_df['Close'].shift(-15) - features_df['Close']
            ) / features_df['Close']
            
            # Generate labels: 1 if 15-day return < -2%, else 0
            features_df['Label'] = (features_df['Future_Return'] < -0.02).astype(int)
            
            # Drop rows with NaN values
            valid_cols = FEATURE_COLS + ['Label']
            features_df = features_df.dropna(subset=valid_cols)
            
            if len(features_df) > 0:
                all_features.append(features_df[FEATURE_COLS])
                all_labels.append(features_df['Label'])
                print(f"    + {len(features_df)} samples collected")
            else:
                print(f"    x No valid samples after dropping NaN")
                
        except Exception as e:
            print(f"    x Error processing {ticker}: {str(e)}")
            continue
    
    if not all_features:
        raise ValueError("No training data collected. Check ticker symbols and data availability.")
    
    # Combine all data
    combined_features = pd.concat(all_features, ignore_index=True)
    combined_labels = pd.concat(all_labels, ignore_index=True)
    
    print(f"\nTotal samples collected: {len(combined_features)}")
    print(f"High_Risk samples (label=1): {int(combined_labels.sum())}")
    print(f"Stable samples (label=0): {len(combined_labels) - int(combined_labels.sum())}")
    print(f"Features used: {len(FEATURE_COLS)} -> {FEATURE_COLS}")
    
    return combined_features, combined_labels


def train_and_evaluate():
    """
    Train ensemble model with cross-validation and evaluate performance.
    Uses StandardScaler + VotingClassifier (XGBoost/GradientBoosting + RandomForest).
    """
    print("=" * 60)
    print("ML Model Training - Enhanced Volatility Predictor")
    print("=" * 60)
    print()
    
    # Prepare training data
    try:
        features_df, labels = prepare_training_data(TRAINING_TICKERS)
    except Exception as e:
        print(f"\nx Failed to prepare training data: {str(e)}")
        return
    
    # Replace any remaining inf values
    features_df = features_df.replace([np.inf, -np.inf], np.nan)
    features_df = features_df.fillna(features_df.median())
    
    # Split into train/test sets (80/20)
    print("\nSplitting data into train/test sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        features_df, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Build ensemble model with StandardScaler
    print("\nBuilding ensemble model...")
    
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=3,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    
    if HAS_XGBOOST:
        boost_model = XGBClassifier(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            scale_pos_weight=len(y_train[y_train == 0]) / max(len(y_train[y_train == 1]), 1),
            eval_metric='logloss',
        )
        print("  Using XGBoost + RandomForest ensemble")
    else:
        boost_model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42
        )
        print("  Using GradientBoosting + RandomForest ensemble")
    
    # Create pipeline with scaling + voting ensemble
    ensemble = VotingClassifier(
        estimators=[('rf', rf_model), ('boost', boost_model)],
        voting='soft',
        weights=[1, 1.5]  # Slightly favor gradient boosting
    )
    
    model = Pipeline([
        ('scaler', StandardScaler()),
        ('ensemble', ensemble)
    ])
    
    # Cross-validation
    print("\nRunning 5-fold stratified cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted', n_jobs=-1)
    print(f"  CV F1 scores: {[f'{s:.3f}' for s in cv_scores]}")
    print(f"  Mean CV F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Train on full training set
    print("\nTraining final model on full training set...")
    model.fit(X_train, y_train)
    print("+ Model training complete")
    
    # Evaluate on test set
    print("\nEvaluating model performance on test set...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"\nTest Accuracy: {accuracy:.2%}")
    print(f"Test F1 (weighted): {f1:.3f}")
    
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=['Stable (0)', 'High_Risk (1)'],
        digits=3
    ))
    
    # Feature importance (from Random Forest in the ensemble)
    print("\nFeature Importance (RandomForest):")
    rf_fitted = model.named_steps['ensemble'].estimators_[0]
    for name, importance in sorted(zip(FEATURE_COLS, rf_fitted.feature_importances_), key=lambda x: -x[1]):
        bar = '#' * int(importance * 50)
        print(f"  {name:25s}: {importance:.3f} {bar}")
    
    # Save model if accuracy meets threshold
    if accuracy >= 0.55:
        print(f"\n+ Accuracy ({accuracy:.2%}) meets minimum threshold (55%)")
        
        models_dir = Path(__file__).parent.parent / 'models'
        models_dir.mkdir(exist_ok=True)
        
        model_path = models_dir / 'volatility_model.pkl'
        
        # Save both model and feature columns for validation
        artifact = {
            'model': model,
            'feature_cols': FEATURE_COLS,
            'accuracy': accuracy,
            'f1_score': f1,
        }
        joblib.dump(artifact, model_path)
        
        print(f"+ Model saved to: {model_path}")
        print("\nTraining complete! Model is ready for use.")
    else:
        print(f"\nx Accuracy ({accuracy:.2%}) below minimum threshold (55%)")
        print("Consider adding more training data or tuning hyperparameters.")


if __name__ == "__main__":
    train_and_evaluate()
