"""Daily retrain cycle: train a new model and upload to Hugging Face Space.

This script is designed to be run as a Render Cron Job once per day.
It will:
  1. Train a new model using the existing training pipeline
  2. If the new model passes quality thresholds, upload it to HF Space
  3. Optionally clear the backend NAV cache via the API

Environment variables required:
  HF_TOKEN          - Hugging Face write token (repo write access)

Optional:
  BACKEND_URL       - Backend base URL for cache clearing (default: https://sip-mf-analysis-api.onrender.com)
  MIN_ACCURACY      - Minimum accuracy to accept (default: 0.55)
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

HF_SPACE_REPO = "mayur6901/sip-mf-volatility-predictor"
HF_MODEL_FILENAME = "volatility_model.pkl"


def upload_model_to_hf(model_path: str) -> bool:
    """Upload trained model artifact to Hugging Face Space."""
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("x HF_TOKEN not set — skipping upload")
        return False

    try:
        from huggingface_hub import HfApi

        api = HfApi(token=hf_token)
        print(f"Uploading {model_path} to {HF_SPACE_REPO}/{HF_MODEL_FILENAME} ...")
        api.upload_file(
            path_or_fileobj=model_path,
            path_in_repo=HF_MODEL_FILENAME,
            repo_id=HF_SPACE_REPO,
            repo_type="space",
            commit_message=f"Daily retrain {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        )
        print("+ Model uploaded to HF Space successfully")
        return True
    except Exception as e:
        print(f"x HF upload failed: {e}")
        return False


def clear_backend_cache() -> bool:
    """Call the backend clear-cache endpoint so fresh data is fetched for next predictions."""
    import requests

    backend_url = os.getenv("BACKEND_URL", "https://sip-mf-analysis-api.onrender.com")
    try:
        resp = requests.post(f"{backend_url}/api/clear-cache/", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            print(f"+ Backend cache cleared ({data.get('evicted', '?')} entries evicted)")
            return True
        print(f"x Backend cache clear returned {resp.status_code}")
        return False
    except Exception as e:
        print(f"x Cache clear request failed: {e}")
        return False


def main() -> None:
    from scripts.train_model import train_and_evaluate

    min_accuracy = float(os.getenv("MIN_ACCURACY", "0.55"))
    models_dir = Path(__file__).parent.parent / "models"
    output_path = models_dir / "volatility_model.pkl"

    print("=" * 72)
    print(f"Daily retrain started at {datetime.now(timezone.utc).isoformat()}")
    print("=" * 72)

    result = train_and_evaluate(
        output_model_path=output_path,
        minimum_accuracy=min_accuracy,
    )

    if not result.get("success"):
        print(f"x Training failed: {result.get('error', 'Unknown')}")
        sys.exit(1)

    metrics = result.get("metrics", {})
    print(f"\nNew model metrics:")
    print(f"  Accuracy:  {metrics.get('accuracy', 0):.4f}")
    print(f"  F1:        {metrics.get('f1_weighted', 0):.4f}")
    print(f"  ROC-AUC:   {metrics.get('roc_auc', 0):.4f}")
    print(f"  Threshold: {metrics.get('decision_threshold', 0.5):.2f}")

    uploaded = upload_model_to_hf(str(output_path))
    if uploaded:
        clear_backend_cache()

    print("\nDaily retrain complete.")


if __name__ == "__main__":
    main()
