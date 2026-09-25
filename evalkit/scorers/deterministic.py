"""evalkit/scorers/deterministic.py — Deterministic scorers."""

import re
from typing import Any

from evalkit.scorers.base import Scorer, ScoreResult
from evalkit.types import ScoreType


class ExactMatch(Scorer):
    """Scores 1.0 if output exactly matches expected, 0.0 otherwise."""

    def __init__(
        self,
        case_sensitive: bool = False,
        strip: bool = True,
    ):
        self.case_sensitive = case_sensitive
        self.strip = strip

    @property
    def name(self) -> str:
        return "exact_match"

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any,
    ) -> ScoreResult:
        if expected is None:
            return ScoreResult(
                name=self.name,
                score=0.0,
                passed=False,
                reason="No expected value provided for exact match",
            )

        a = output.strip() if self.strip else output
        b = expected.strip() if self.strip else expected

        if not self.case_sensitive:
            a = a.lower()
            b = b.lower()

        match = a == b

        return ScoreResult(
            name=self.name,
            score=1.0 if match else 0.0,
            passed=match,
            reason="" if match else f"Expected '{expected}', got '{output}'",
        )


class Contains(Scorer):
    """Scores 1.0 if output contains the expected string."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "contains"

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any,
    ) -> ScoreResult:
        if expected is None:
            return ScoreResult(
                name=self.name,
                score=0.0,
                passed=False,
                reason="No expected value provided for contains check",
            )

        a = output if self.case_sensitive else output.lower()
        b = expected if self.case_sensitive else expected.lower()

        found = b in a

        return ScoreResult(
            name=self.name,
            score=1.0 if found else 0.0,
            passed=found,
            reason="" if found else f"'{expected}' not found in output",
        )


class RegexMatch(Scorer):
    """Scores 1.0 if output matches the given regex pattern."""

    def __init__(self, pattern: str, flags: int = 0):
        self._pattern = re.compile(pattern, flags)
        self._pattern_str = pattern

    @property
    def name(self) -> str:
        return f"regex({self._pattern_str})"

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any,
    ) -> ScoreResult:
        match = bool(self._pattern.search(output))

        return ScoreResult(
            name=self.name,
            score=1.0 if match else 0.0,
            passed=match,
            reason="" if match else f"Pattern /{self._pattern_str}/ not found",
        )