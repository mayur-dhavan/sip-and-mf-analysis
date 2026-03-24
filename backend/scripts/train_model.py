"""
ML Model Training Script - Beast Mode

This script trains a stacked ensemble model with threshold optimization to
predict mutual fund volatility risk. It uses:
- 5-year historical data
- expanded technical indicators
- broad India-focused ticker universe
- robust cross-validation and threshold tuning for minority-class recall

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
import hashlib
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    StackingClassifier,
)
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    f1_score,
    roc_auc_score,
    precision_score,
    recall_score,
    fbeta_score,
)
from sklearn.linear_model import LogisticRegression
import joblib
from typing import List, Tuple, Optional, Dict, Any

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("Warning: XGBoost not installed. Using GradientBoosting as fallback.")

from app.services.data_fetcher import DataFetcher
from app.services.feature_calculator import FeatureCalculator
from app.services.feature_config import FEATURE_COLS
MANUAL_BENCHMARKS = ["^NSEI", "^NSMIDCP", "^NSEBANK"]
MAX_AMFI_TRAINING_SCHEMES = 90


def _generate_adaptive_labels(features_df: pd.DataFrame) -> tuple[pd.Series, Dict[str, float]]:
    """Create risk labels with adaptive fallback to avoid severe class collapse."""
    future_return = (features_df['Close'].shift(-15) - features_df['Close']) / features_df['Close']
    base_labels = (future_return < -0.02).astype(int)
    base_positive_rate = float(base_labels.mean()) if len(base_labels) else 0.0

    # If base rule produces too few positives, use quantile-based tail risk labeling.
    if base_positive_rate < 0.12:
        dynamic_cutoff = float(future_return.quantile(0.20))
        labels = (future_return <= dynamic_cutoff).astype(int)
        strategy = "quantile_20"
    elif base_positive_rate > 0.42:
        dynamic_cutoff = float(future_return.quantile(0.30))
        labels = (future_return <= dynamic_cutoff).astype(int)
        strategy = "quantile_30"
    else:
        dynamic_cutoff = -0.02
        labels = base_labels
        strategy = "fixed_minus_2pct"

    effective_positive_rate = float(labels.mean()) if len(labels) else 0.0
    diagnostics = {
        "base_positive_rate": base_positive_rate,
        "effective_positive_rate": effective_positive_rate,
        "dynamic_cutoff": dynamic_cutoff,
        "strategy": strategy,
    }
    return labels, diagnostics


def get_training_tickers() -> List[str]:
    """Build a broader but bounded training universe from DataFetcher registry."""
    fetcher = DataFetcher()
    registry = fetcher._fund_registry

    mapped_tickers = sorted({
        str(item["yahoo_ticker"]).strip()
        for item in registry
        if item.get("yahoo_ticker")
    })

    amfi_candidates_live = sorted({
        f"AMFI:{str(item['amfi_code']).strip()}"
        for item in registry
        if str(item.get("amfi_code", "")).strip().isdigit()
        and item.get("source") == "mfapi_index"
        and "direct" in str(item.get("name", "")).lower()
        and "growth" in str(item.get("name", "")).lower()
    })

    amfi_candidates_static_verified = sorted({
        f"AMFI:{str(item['amfi_code']).strip()}"
        for item in registry
        if str(item.get("amfi_code", "")).strip().isdigit()
        and item.get("source") == "static"
        and item.get("is_supported")
    })

    def stable_rank(value: str) -> str:
        return hashlib.md5(value.encode("utf-8")).hexdigest()

    sampled_amfi_live = sorted(amfi_candidates_live, key=stable_rank)[:MAX_AMFI_TRAINING_SCHEMES]
    sampled_amfi_static = sorted(amfi_candidates_static_verified, key=stable_rank)[:40]

    universe = sorted(set(mapped_tickers + sampled_amfi_live + sampled_amfi_static + MANUAL_BENCHMARKS))
    return universe


def prepare_training_data(tickers: List[str]) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Fetch data for multiple tickers and prepare training dataset with expanded features.
    """
    data_fetcher = DataFetcher()
    feature_calculator = FeatureCalculator()
    
    all_features = []
    all_labels = []
    successful_tickers = []
    label_diagnostics = []
    
    print(f"Fetching data for {len(tickers)} tickers...")
    
    for ticker in tickers:
        try:
            print(f"  Processing {ticker}...")
            
            # Fetch NAV data
            nav_df = data_fetcher.fetch_nav_data(ticker, period="5y")
            
            # Calculate technical indicators (all expanded features)
            features_df = feature_calculator.calculate_all_features(nav_df)
            
            # Adaptive label generation prevents a near-all-stable class in low-vol regimes.
            features_df['Label'], label_info = _generate_adaptive_labels(features_df)
            features_df['Future_Return_15'] = (
                features_df['Close'].shift(-15) - features_df['Close']
            ) / features_df['Close']
            
            # Drop rows with NaN values
            valid_cols = FEATURE_COLS + ['Label', 'Future_Return_15']
            features_df = features_df.dropna(subset=valid_cols)
            
            if len(features_df) > 0:
                all_features.append(features_df[FEATURE_COLS])
                all_labels.append(features_df['Label'])
                successful_tickers.append(ticker)
                label_diagnostics.append({"ticker": ticker, **label_info})
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

    if label_diagnostics:
        avg_base = np.mean([d["base_positive_rate"] for d in label_diagnostics])
        avg_eff = np.mean([d["effective_positive_rate"] for d in label_diagnostics])
        quantile_count = sum(1 for d in label_diagnostics if d["strategy"] != "fixed_minus_2pct")
        print(
            "Label diagnostics -> "
            f"Avg base positive rate: {avg_base:.3f}, "
            f"Avg effective positive rate: {avg_eff:.3f}, "
            f"Adaptive schemes: {quantile_count}/{len(label_diagnostics)}"
        )
    
    return combined_features, combined_labels, successful_tickers


def optimize_threshold(y_true: pd.Series, proba_high_risk: np.ndarray) -> Tuple[float, Dict[str, float]]:
    """Tune threshold with high-risk emphasis while keeping precision floor."""
    best_threshold = 0.5
    best_obj = -1.0
    best_metrics = {"f_beta": 0.0, "precision": 0.0, "recall": 0.0}

    target_positive_rate = float(np.mean(y_true))

    for threshold in np.arange(0.18, 0.70, 0.02):
        preds = (proba_high_risk >= threshold).astype(int)
        precision = precision_score(y_true, preds, pos_label=1, zero_division=0)
        recall = recall_score(y_true, preds, pos_label=1, zero_division=0)
        f_beta = fbeta_score(y_true, preds, beta=1.5, pos_label=1, zero_division=0)
        predicted_positive_rate = float(np.mean(preds))

        # Penalize thresholds with very low precision to avoid too many false alarms.
        precision_penalty = max(0.0, 0.42 - precision) * 0.35
        recall_penalty = max(0.0, 0.45 - recall) * 0.25
        rate_penalty = abs(predicted_positive_rate - target_positive_rate) * 0.18
        objective = f_beta - precision_penalty - recall_penalty - rate_penalty

        if objective > best_obj:
            best_obj = objective
            best_threshold = float(threshold)
            best_metrics = {
                "f_beta": float(f_beta),
                "precision": float(precision),
                "recall": float(recall),
                "predicted_positive_rate": float(predicted_positive_rate),
                "target_positive_rate": float(target_positive_rate),
            }

    return best_threshold, best_metrics


def train_and_evaluate(
    output_model_path: Optional[Path] = None,
    minimum_accuracy: float = 0.55,
) -> Dict[str, Any]:
    """
    Train ensemble model with cross-validation and evaluate performance.
    Uses StandardScaler + VotingClassifier (XGBoost/GradientBoosting + RandomForest).
    """
    print("=" * 60)
    print("ML Model Training - Beast Mode Stacked Predictor")
    print("=" * 60)
    print()
    
    # Prepare training data
    training_tickers = get_training_tickers()
    print(f"Ticker universe size: {len(training_tickers)}")

    try:
        features_df, labels, successful_tickers = prepare_training_data(training_tickers)
    except Exception as e:
        print(f"\nx Failed to prepare training data: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to prepare training data: {str(e)}",
        }
    
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
    
    # Build stacked ensemble model
    print("\nBuilding stacked ensemble model...")
    
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
            max_depth=7,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            scale_pos_weight=len(y_train[y_train == 0]) / max(len(y_train[y_train == 1]), 1),
            eval_metric='logloss',
            reg_lambda=1.5,
            reg_alpha=0.2,
        )
        print("  Using XGBoost as boosting backbone")
    else:
        boost_model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42
        )
        print("  Using GradientBoosting fallback backbone")

    extra_trees = ExtraTreesClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1,
    )

    meta_model = LogisticRegression(
        solver='liblinear',
        class_weight='balanced',
        max_iter=1500,
        random_state=42,
    )
    
    ensemble = StackingClassifier(
        estimators=[
            ('rf', rf_model),
            ('xt', extra_trees),
            ('boost', boost_model),
        ],
        final_estimator=meta_model,
        cv=5,
        stack_method='predict_proba',
        n_jobs=-1,
        passthrough=False,
    )
    model = ensemble
    
    # Cross-validation
    print("\nRunning 5-fold stratified cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted', n_jobs=-1)
    print(f"  CV F1 scores: {[f'{s:.3f}' for s in cv_scores]}")
    print(f"  Mean CV F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    # Threshold tuning using validation split from training set
    X_fit, X_val, y_fit, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )

    print("\nTraining model for threshold tuning...")
    model.fit(X_fit, y_fit)
    val_proba = model.predict_proba(X_val)[:, 1]
    decision_threshold, threshold_metrics = optimize_threshold(y_val, val_proba)
    print(f"  Tuned decision threshold: {decision_threshold:.2f}")
    print(
        "  Validation metrics @ threshold -> "
        f"F1.5: {threshold_metrics['f_beta']:.3f}, "
        f"Precision: {threshold_metrics['precision']:.3f}, "
        f"Recall: {threshold_metrics['recall']:.3f}"
    )

    # Refit on full training set after choosing threshold
    print("\nTraining final model on full training set...")
    model.fit(X_train, y_train)
    print("+ Model training complete")
    
    # Evaluate on test set
    print("\nEvaluating model performance on test set...")
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= decision_threshold).astype(int)
    
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    auc = roc_auc_score(y_test, y_proba)
    print(f"\nTest Accuracy: {accuracy:.2%}")
    print(f"Test F1 (weighted): {f1:.3f}")
    print(f"Test ROC-AUC: {auc:.3f}")
    
    print("\nClassification Report:")
    report_dict = classification_report(
        y_test, y_pred,
        target_names=['Stable (0)', 'High_Risk (1)'],
        digits=3,
        output_dict=True,
    )
    print(classification_report(
        y_test, y_pred,
        target_names=['Stable (0)', 'High_Risk (1)'],
        digits=3
    ))
    
    # Feature importance (from Random Forest base model in stack)
    print("\nFeature Importance (RandomForest base learner):")
    rf_fitted = model.named_estimators_['rf']
    for name, importance in sorted(zip(FEATURE_COLS, rf_fitted.feature_importances_), key=lambda x: -x[1]):
        bar = '#' * int(importance * 50)
        print(f"  {name:25s}: {importance:.3f} {bar}")
    
    # Save model if accuracy meets threshold
    if accuracy >= minimum_accuracy:
        print(f"\n+ Accuracy ({accuracy:.2%}) meets minimum threshold ({minimum_accuracy:.0%})")
        
        models_dir = Path(__file__).parent.parent / 'models'
        models_dir.mkdir(exist_ok=True)
        model_path = output_model_path or (models_dir / 'volatility_model.pkl')
        model_path.parent.mkdir(parents=True, exist_ok=True)

        high_risk_metrics = report_dict.get('High_Risk (1)', {})
        stable_metrics = report_dict.get('Stable (0)', {})
        
        # Save both model and feature columns for validation
        artifact = {
            'model': model,
            'feature_cols': FEATURE_COLS,
            'accuracy': accuracy,
            'f1_score': f1,
            'roc_auc': float(auc),
            'decision_threshold': float(decision_threshold),
            'cv_f1_mean': float(cv_scores.mean()),
            'cv_f1_std': float(cv_scores.std()),
            'high_risk_precision': float(high_risk_metrics.get('precision', 0.0)),
            'high_risk_recall': float(high_risk_metrics.get('recall', 0.0)),
            'high_risk_f1': float(high_risk_metrics.get('f1-score', 0.0)),
            'stable_precision': float(stable_metrics.get('precision', 0.0)),
            'stable_recall': float(stable_metrics.get('recall', 0.0)),
            'stable_f1': float(stable_metrics.get('f1-score', 0.0)),
            'training_period': '5y',
            'ticker_universe_size': len(training_tickers),
            'successful_tickers': successful_tickers,
        }
        joblib.dump(artifact, model_path)
        
        print(f"+ Model saved to: {model_path}")
        print("\nTraining complete! Model is ready for use.")
        return {
            "success": True,
            "model_path": str(model_path),
            "metrics": {
                "accuracy": float(accuracy),
                "f1_weighted": float(f1),
                "roc_auc": float(auc),
                "cv_f1_mean": float(cv_scores.mean()),
                "cv_f1_std": float(cv_scores.std()),
                "decision_threshold": float(decision_threshold),
                "high_risk_precision": float(high_risk_metrics.get('precision', 0.0)),
                "high_risk_recall": float(high_risk_metrics.get('recall', 0.0)),
                "high_risk_f1": float(high_risk_metrics.get('f1-score', 0.0)),
                "stable_precision": float(stable_metrics.get('precision', 0.0)),
                "stable_recall": float(stable_metrics.get('recall', 0.0)),
                "stable_f1": float(stable_metrics.get('f1-score', 0.0)),
                "ticker_universe_size": len(training_tickers),
                "successful_ticker_count": len(successful_tickers),
            },
            "training_context": {
                "training_period": "5y",
                "successful_tickers": successful_tickers,
            },
        }
    else:
        print(f"\nx Accuracy ({accuracy:.2%}) below minimum threshold ({minimum_accuracy:.0%})")
        print("Consider adding more training data or tuning hyperparameters.")
        return {
            "success": False,
            "error": f"Accuracy below threshold: {accuracy:.4f} < {minimum_accuracy:.4f}",
            "metrics": {
                "accuracy": float(accuracy),
                "f1_weighted": float(f1),
                "roc_auc": float(auc),
            },
        }


if __name__ == "__main__":
    train_and_evaluate()
