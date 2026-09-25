"""evalkit/scorers/base.py — Scorer protocol and base class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from evalkit.types import ScoreType


@dataclass
class ScoreResult:
    """Result from a single scorer on a single case."""

    name: str
    score: float              # normalized: 0.0 to 1.0 for numeric, 0/1 for binary
    passed: bool
    reason: str = ""
    raw_value: Any = None     # original value before normalization


class Scorer(ABC):
    """Abstract base class for all scorers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this scorer."""
        ...

    @property
    def score_type(self) -> ScoreType:
        """The type of score this scorer produces."""
        return ScoreType.BINARY

    @property
    def threshold(self) -> float:
        """Score threshold for pass/fail. Default 0.5."""
        return 0.5

    @abstractmethod
    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any,
    ) -> ScoreResult:
        """Score a single output.

        Args:
            output: The system's output to evaluate.
            expected: The reference/expected answer (optional).
            **kwargs: Additional context (input, metadata, etc.).

        Returns:
            ScoreResult with the evaluation.
        """
        ...

    def score_batch(
        self,
        outputs: list[str],
        expecteds: list[str | None],
        **kwargs: Any,
    ) -> list[ScoreResult]:
        """Score a batch of outputs. Default: sequential scoring."""

        results = []

        for output, expected in zip(outputs, expecteds):
            results.append(
                self.score(output, expected, **kwargs)
            )

        return results