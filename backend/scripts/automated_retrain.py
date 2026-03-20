"""Automated periodic retraining with champion/challenger model versioning.

Usage examples:
  python scripts/automated_retrain.py --once
  python scripts/automated_retrain.py --interval-hours 24
  python scripts/automated_retrain.py --interval-hours 24 --min-score-improvement 0.005
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.model_registry import ModelRegistry
from scripts.train_model import train_and_evaluate


def run_single_cycle(min_score_improvement: float, minimum_accuracy: float) -> bool:
    models_dir = Path(__file__).parent.parent / "models"
    challenger_dir = models_dir / "challengers"
    challenger_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    challenger_path = challenger_dir / f"challenger_{timestamp}.pkl"

    print("=" * 72)
    print(f"Retraining cycle started at {datetime.now().isoformat()}")
    print("=" * 72)

    result = train_and_evaluate(
        output_model_path=challenger_path,
        minimum_accuracy=minimum_accuracy,
    )

    if not result.get("success"):
        print(f"x Training failed: {result.get('error', 'Unknown error')}")
        return False

    registry = ModelRegistry(models_dir=models_dir)
    version_id = registry.register_challenger(
        artifact_path=Path(result["model_path"]),
        metrics=result["metrics"],
        metadata=result.get("training_context", {}),
    )

    decision = registry.evaluate_and_promote(
        challenger_version=version_id,
        min_score_improvement=min_score_improvement,
    )

    print(f"Challenger version: {version_id}")
    print(f"Promotion decision: {'PROMOTED' if decision.promoted else 'REJECTED'}")
    print(f"Reason: {decision.reason}")

    champion = registry.get_champion()
    if champion:
        print(f"Serving champion version: {champion['version_id']}")
        print(f"Serving champion score: {champion.get('score', 0.0):.4f}")

    print("Retraining cycle completed.")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated model retraining manager")
    parser.add_argument("--once", action="store_true", help="Run one retraining cycle and exit")
    parser.add_argument(
        "--interval-hours",
        type=float,
        default=24.0,
        help="Hours between retraining cycles (default: 24)",
    )
    parser.add_argument(
        "--min-score-improvement",
        type=float,
        default=0.003,
        help="Minimum score margin for champion promotion (default: 0.003)",
    )
    parser.add_argument(
        "--minimum-accuracy",
        type=float,
        default=0.55,
        help="Minimum accepted challenger accuracy (default: 0.55)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.once:
        run_single_cycle(args.min_score_improvement, args.minimum_accuracy)
        return

    interval_seconds = max(60, int(args.interval_hours * 3600))
    print(
        f"Starting periodic retraining loop: every {args.interval_hours} hours "
        f"({interval_seconds} seconds)."
    )

    while True:
        try:
            run_single_cycle(args.min_score_improvement, args.minimum_accuracy)
        except Exception as exc:
            print(f"x Retraining cycle crashed: {exc}")

        print(f"Sleeping for {interval_seconds} seconds before next cycle...")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
