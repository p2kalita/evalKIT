"""evalkit/types.py — Core type definitions for evalkit."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ScoreType(Enum):
    """Classification of score types."""

    BINARY = "binary"          # pass/fail
    NUMERIC = "numeric"        # 0.0 to 1.0
    LIKERT = "likert"          # 1 to 5 scale
    CATEGORICAL = "categorical"  # labels like "good", "bad", "neutral"


@dataclass
class EvalCase:
    """A single evaluation case: input + optional expected output."""

    input: str
    expected: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class EvalResult:
    """Result of scoring a single case."""

    case: EvalCase
    output: str
    scores: dict[str, float]
    passed: bool
    metadata: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
    error: str | None = None

    failed: int = 0
    pass_rate: float = 0.0
    avg_scores: dict[str, float] = field(default_factory=dict)
    avg_latency_ms: float = 0.0

    def __post_init__(self):
        self.total = len(self.results)
        self.passed = sum(1 for r in self.results if r.passed)
        self.failed = self.total - self.passed
        self.pass_rate = self.passed / self.total if self.total > 0 else 0.0

    def summary(self) -> str:
        lines = [
            f"Eval: {self.name}",
            f"Total:    {self.total}",
            f"Passed:   {self.passed}",
            f"Failed:   {self.failed}",
            f"Pass rate: {self.pass_rate:.1%}",
        ]

        for name, avg in self.avg_scores.items():
            lines.append(f"  {name}: Avg {avg:.3f}")

        if self.avg_latency_ms:
            lines.append(
                f"  Avg latency: {self.avg_latency_ms:.0f}ms"
            )

        return "\n".join(lines)
