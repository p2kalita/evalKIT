"""evalkit/scorers/composite.py — Composite scorers."""

from typing import Any

from evalkit.scorers.base import Scorer, ScoreResult
from evalkit.types import ScoreType


class AllOf(Scorer):
    """Passes only if all child scorers pass."""

    def __init__(self, scorers: list[Scorer]):
        self._scorers = scorers

    @property
    def name(self) -> str:
        names = ", ".join(s.name for s in self._scorers)
        return f"all_of({names})"

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any
    ) -> ScoreResult:
        results = [
            s.score(output, expected, **kwargs) for s in self._scorers
        ]

        all_passed = all(r.passed for r in results)

        avg_score = (
            sum(r.score for r in results) / len(results)
            if results
            else 0.0
        )

        failed = [r for r in results if not r.passed]

        reason = "; ".join(
            r.reason for r in failed
        ) if failed else ""

        return ScoreResult(
            name=self.name,
            score=avg_score if all_passed else 0.0,
            passed=all_passed,
            reason=reason,
        )


class AnyOf(Scorer):
    """Passes if ANY child scorer passes."""

    def __init__(self, scorers: list[Scorer]):
        self._scorers = scorers

    @property
    def name(self) -> str:
        names = ", ".join(s.name for s in self._scorers)
        return f"any_of({names})"

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any
    ) -> ScoreResult:
        results = [
            s.score(output, expected, **kwargs)
            for s in self._scorers
        ]

        any_passed = any(r.passed for r in results)

        best = max(results, key=lambda r: r.score)

        return ScoreResult(
            name=self.name,
            score=best.score,
            passed=any_passed,
            reason=best.reason if any_passed else "No scorer passed",
        )