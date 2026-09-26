"""evalkit/scorers/deterministic.py — Deterministic scorers."""

import re
from typing import Any

from evalkit.scorers.base import Scorer, ScoreResult
from evalkit.types import ScoreType

# 25-09-2026 --------> Day 1 added foundation - ExactMatch, Contains

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

# 26-09-2026 --------> Day 2 added ContainsAll, JsonMatch

"""evalkit/scorers/deterministic.py — Adding ContainsAll and JsonMatch."""

class ContainsAll(Scorer):
    """Scores based on how many required keywords/phrases are present."""

    def __init__(self, key: str = "required_facts", case_sensitive: bool = False):
        self._key = key
        self._case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        return "contains_all"

    @property
    def score_type(self) -> ScoreType:
        return ScoreType.NUMERIC

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any
    ) -> ScoreResult:
        metadata = kwargs.get("metadata", {})
        required = metadata.get(self._key, [])

        if not required:
            return ScoreResult(
                name=self.name,
                score=1.0,
                passed=True,
                reason="No required items specified"
            )

        check_output = output if self._case_sensitive else output.lower()
        found = []
        missing = []

        for item in required:
            check_item = item if self._case_sensitive else item.lower()

            if check_item in check_output:
                found.append(item)
            else:
                missing.append(item)

        score = len(found) / len(required)
        passed = score >= self.threshold

        return ScoreResult(
            name=self.name,
            score=score,
            passed=passed,
            reason=f"Missing: {missing}" if missing else "All items found",
            raw_value={"found": found, "missing": missing},
        )


class JsonMatch(Scorer):
    """Scores based on field-level matching of JSON outputs."""

    def __init__(self, fields: list[str] | None = None):
        self._fields = fields  # None = compare all fields

    @property
    def name(self) -> str:
        return "json_match"

    @property
    def score_type(self) -> ScoreType:
        return ScoreType.NUMERIC

    def score(
        self,
        output: str,
        expected: str | None = None,
        **kwargs: Any
    ) -> ScoreResult:
        import json as json_mod

        if expected is None:
            return ScoreResult(
                name=self.name,
                score=0.0,
                passed=False,
                reason="No expected value for JSON comparison"
            )

        try:
            output_obj = json_mod.loads(output)
        except json_mod.JSONDecodeError as e:
            return ScoreResult(
                name=self.name,
                score=0.0,
                passed=False,
                reason=f"Output is not valid JSON: {e}"
            )

        try:
            expected_obj = json_mod.loads(expected)
        except json_mod.JSONDecodeError as e:
            return ScoreResult(
                name=self.name,
                score=0.0,
                passed=False,
                reason=f"Expected is not valid JSON: {e}"
            )

        fields = self._fields or list(expected_obj.keys())

        if not fields:
            return ScoreResult(
                name=self.name,
                score=1.0,
                passed=True,
                reason="No fields to compare"
            )

        matches = 0
        mismatches = []

        for field in fields:
            exp_val = expected_obj.get(field)
            out_val = output_obj.get(field)

            if str(exp_val).lower() == str(out_val).lower():
                matches += 1
            else:
                mismatches.append(
                    f"{field}: expected '{exp_val}', got '{out_val}'"
                )

        score = matches / len(fields)
        passed = score >= self.threshold

        return ScoreResult(
            name=self.name,
            score=score,
            passed=passed,
            reason="; ".join(mismatches) if mismatches else "All fields match",
        )