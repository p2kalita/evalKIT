"""evalkit/config.py — Configuration management for evalkit."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EvalConfig:
    """Global configuration for an evalkit evaluation session."""

    project_name: str = "evalkit"
    datasets_dir: Path = field(
        default_factory=lambda: Path("datasets")
    )
    results_dir: Path = field(
        default_factory=lambda: Path("results")
    )
    golden_dir: Path = field(
        default_factory=lambda: Path("golden")
    )

    # LLM provider settings
    default_provider: str = "anthropic"
    default_model: str = "claude-sonnet-4-6"
    judge_model: str = "claude-sonnet-4-6"

    # Runner settings
    max_concurrency: int = 5
    timeout_seconds: int = 30
    max_retries: int = 2

    # Scoring thresholds
    pass_threshold: float = 0.7
    regression_tolerance: float = 0.05  # 5% drop allowed

    def ensure_dirs(self) -> None:
        """Create required directories if they do not exist."""

        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.golden_dir.mkdir(parents=True, exist_ok=True)