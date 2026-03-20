"""Model registry for champion/challenger lifecycle management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any, Dict, Optional, Tuple


@dataclass
class PromotionDecision:
    promoted: bool
    reason: str
    challenger_version: str
    champion_version: Optional[str]


class ModelRegistry:
    """Version and promotion management for trained model artifacts."""

    def __init__(self, models_dir: Optional[Path] = None) -> None:
        base_models_dir = models_dir or (Path(__file__).resolve().parents[2] / "models")
        self.models_dir = base_models_dir
        self.registry_dir = self.models_dir / "registry"
        self.versions_dir = self.registry_dir / "versions"
        self.manifest_path = self.registry_dir / "manifest.json"
        self.serving_model_path = self.models_dir / "volatility_model.pkl"

        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def load_manifest(self) -> Dict[str, Any]:
        if not self.manifest_path.exists():
            manifest = {
                "created_at": self._now_iso(),
                "updated_at": self._now_iso(),
                "champion_version": None,
                "versions": [],
            }
            self._save_manifest(manifest)
            return manifest

        with self.manifest_path.open("r", encoding="utf-8") as fp:
            return json.load(fp)

    def register_challenger(
        self,
        artifact_path: Path,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        manifest = self.load_manifest()
        version_id = datetime.now(timezone.utc).strftime("v%Y%m%dT%H%M%SZ")
        version_filename = f"{version_id}_volatility_model.pkl"
        version_path = self.versions_dir / version_filename

        shutil.copy2(artifact_path, version_path)

        entry = {
            "version_id": version_id,
            "artifact_path": str(version_path),
            "created_at": self._now_iso(),
            "status": "challenger",
            "metrics": metrics,
            "metadata": metadata or {},
            "score": self._score_metrics(metrics),
        }
        manifest["versions"].append(entry)
        manifest["updated_at"] = self._now_iso()
        self._save_manifest(manifest)
        return version_id

    def evaluate_and_promote(
        self,
        challenger_version: str,
        min_score_improvement: float = 0.003,
    ) -> PromotionDecision:
        manifest = self.load_manifest()
        versions = {item["version_id"]: item for item in manifest["versions"]}

        if challenger_version not in versions:
            raise ValueError(f"Challenger version '{challenger_version}' not found in registry.")

        challenger = versions[challenger_version]
        champion_version = manifest.get("champion_version")
        champion = versions.get(champion_version) if champion_version else None

        if champion is None:
            self._promote(manifest, challenger_version)
            return PromotionDecision(
                promoted=True,
                reason="No champion exists yet; first valid model promoted.",
                challenger_version=challenger_version,
                champion_version=None,
            )

        challenger_score = float(challenger.get("score", 0.0))
        champion_score = float(champion.get("score", 0.0))

        if challenger_score >= champion_score + min_score_improvement:
            self._promote(manifest, challenger_version)
            return PromotionDecision(
                promoted=True,
                reason=(
                    f"Challenger score {challenger_score:.4f} exceeded champion "
                    f"{champion_score:.4f} by >= {min_score_improvement:.4f}."
                ),
                challenger_version=challenger_version,
                champion_version=champion_version,
            )

        self._mark_status(manifest, challenger_version, "rejected")
        return PromotionDecision(
            promoted=False,
            reason=(
                f"Challenger score {challenger_score:.4f} did not exceed champion "
                f"{champion_score:.4f} by required margin {min_score_improvement:.4f}."
            ),
            challenger_version=challenger_version,
            champion_version=champion_version,
        )

    def get_champion(self) -> Optional[Dict[str, Any]]:
        manifest = self.load_manifest()
        champion_version = manifest.get("champion_version")
        if not champion_version:
            return None
        for item in manifest.get("versions", []):
            if item["version_id"] == champion_version:
                return item
        return None

    def _promote(self, manifest: Dict[str, Any], version_id: str) -> None:
        for item in manifest["versions"]:
            if item["version_id"] == version_id:
                item["status"] = "champion"
                artifact_path = Path(item["artifact_path"])
                shutil.copy2(artifact_path, self.serving_model_path)
            elif item["status"] == "champion":
                item["status"] = "retired"

        manifest["champion_version"] = version_id
        manifest["updated_at"] = self._now_iso()
        self._save_manifest(manifest)

    def _mark_status(self, manifest: Dict[str, Any], version_id: str, status: str) -> None:
        for item in manifest["versions"]:
            if item["version_id"] == version_id:
                item["status"] = status
                break
        manifest["updated_at"] = self._now_iso()
        self._save_manifest(manifest)

    def _save_manifest(self, manifest: Dict[str, Any]) -> None:
        with self.manifest_path.open("w", encoding="utf-8") as fp:
            json.dump(manifest, fp, indent=2)

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _score_metrics(metrics: Dict[str, float]) -> float:
        # Weighted objective emphasizing risk detection quality and calibration.
        return (
            0.30 * float(metrics.get("high_risk_f1", 0.0))
            + 0.20 * float(metrics.get("high_risk_recall", 0.0))
            + 0.20 * float(metrics.get("f1_weighted", 0.0))
            + 0.20 * float(metrics.get("roc_auc", 0.0))
            + 0.10 * float(metrics.get("accuracy", 0.0))
        )
