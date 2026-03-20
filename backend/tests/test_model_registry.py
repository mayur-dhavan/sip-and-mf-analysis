"""Unit tests for model registry champion/challenger lifecycle."""

from pathlib import Path
import tempfile

from app.services.model_registry import ModelRegistry


def _dummy_model_file(path: Path) -> None:
    path.write_bytes(b"dummy-model")


def test_first_challenger_becomes_champion():
    with tempfile.TemporaryDirectory() as tmp:
        models_dir = Path(tmp) / "models"
        registry = ModelRegistry(models_dir=models_dir)

        challenger_file = models_dir / "challenger.pkl"
        challenger_file.parent.mkdir(parents=True, exist_ok=True)
        _dummy_model_file(challenger_file)

        version = registry.register_challenger(
            artifact_path=challenger_file,
            metrics={
                "accuracy": 0.80,
                "f1_weighted": 0.81,
                "roc_auc": 0.84,
                "high_risk_f1": 0.70,
                "high_risk_recall": 0.75,
            },
        )

        decision = registry.evaluate_and_promote(version)
        champion = registry.get_champion()

        assert decision.promoted is True
        assert champion is not None
        assert champion["version_id"] == version
        assert (models_dir / "volatility_model.pkl").exists()


def test_weaker_challenger_is_rejected_when_champion_exists():
    with tempfile.TemporaryDirectory() as tmp:
        models_dir = Path(tmp) / "models"
        registry = ModelRegistry(models_dir=models_dir)

        first = models_dir / "first.pkl"
        second = models_dir / "second.pkl"
        first.parent.mkdir(parents=True, exist_ok=True)
        _dummy_model_file(first)
        _dummy_model_file(second)

        v1 = registry.register_challenger(
            artifact_path=first,
            metrics={
                "accuracy": 0.90,
                "f1_weighted": 0.91,
                "roc_auc": 0.93,
                "high_risk_f1": 0.80,
                "high_risk_recall": 0.82,
            },
        )
        registry.evaluate_and_promote(v1)

        v2 = registry.register_challenger(
            artifact_path=second,
            metrics={
                "accuracy": 0.82,
                "f1_weighted": 0.83,
                "roc_auc": 0.84,
                "high_risk_f1": 0.65,
                "high_risk_recall": 0.70,
            },
        )
        decision = registry.evaluate_and_promote(v2, min_score_improvement=0.002)

        champion = registry.get_champion()
        assert decision.promoted is False
        assert champion is not None
        assert champion["version_id"] == v1
