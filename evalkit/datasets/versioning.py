"""evalkit/datasets/versioning.py — Dataset versioning."""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict

from evalkit.datasets.loader import Dataset


@dataclass
class DatasetVersion:
    """Metadata about a dataset version."""

    version: str
    name: str
    created_at: str
    case_count: int
    checksum: str
    changelog: str = ""


class DatasetRegistry:
    """Manages versioned datasets with checksums and changelogs."""

    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)
        self.manifest_path = self.base_dir / "manifest.json"
        self._manifest: dict = self._load_manifest()

    def _load_manifest(self) -> dict:
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text())
        return {"datasets": {}}

    def _save_manifest(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(self._manifest, indent=2)
        )

    def _checksum(self, path: Path) -> str:
        content = path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]

    def register(
        self,
        dataset: Dataset,
        version: str,
        changelog: str = "",
    ) -> DatasetVersion:
        """Save and register a new dataset version."""

        version_dir = self.base_dir / dataset.name / version
        data_path = version_dir / "data.json"

        dataset.to_json(data_path)

        checksum = self._checksum(data_path)

        meta = DatasetVersion(
            version=version,
            name=dataset.name,
            created_at=datetime.now(timezone.utc).isoformat(),
            case_count=len(dataset),
            checksum=checksum,
            changelog=changelog,
        )

        if dataset.name not in self._manifest["datasets"]:
            self._manifest["datasets"][dataset.name] = {"versions": {}}

        self._manifest["datasets"][dataset.name]["versions"].append(
            asdict(meta)
        )

        self._manifest["datasets"][dataset.name]["current"] = version

        self._save_manifest()

        return meta

    def load(
        self,
        name: str,
        version: str | None = None,
    ) -> Dataset:
        """Load a dataset by name and optional version."""

        entry = self._manifest["datasets"].get(name)

        if entry is None:
            raise ValueError(f"Dataset '{name}' not found in registry")

        if version is None:
            version = entry["current"]

        data_path = self.base_dir / name / version / "data.json"

        return Dataset.from_json(
            data_path,
            name=f"{name}@{version}",
        )

    def history(self, name: str) -> list[DatasetVersion]:
        """Get the version history of a dataset."""

        entry = self._manifest["datasets"].get(name, {})
        versions = entry.get("versions", [])

        return [DatasetVersion(**v) for v in versions]


# Usage:
registry = DatasetRegistry("datasets/")

# Register version 1
dataset_v1 = Dataset.from_json("qa_golden.json")
registry.register(
    dataset_v1,
    version="v1",
    changelog="Initial golden set",
)

# Later: register version 2
dataset_v2 = Dataset.from_json("qa_golden_v2.json")
registry.register(
    dataset_v2,
    version="v2",
    changelog="Added 15 cases for edge cases, fixed 3 incorrect expected values",
)

# Load the current version
dataset = registry.load("qa_golden")

# Load a specific version for comparison
old_dataset = registry.load("qa_golden", version="v1")