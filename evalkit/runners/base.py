"""evalkit/runners/base.py — Evaluation runner."""

import time
from typing import Any, Callable

from evalkit.types import EvalCase, EvalResult, EvalReport
from evalkit.datasets.loader import Dataset
from evalkit.scorers.base import Scorer, ScoreResult


# Type alias for the system under test
SystemFn = Callable[[str], str]


class Runner:
    """Executes evaluations: system + dataset + scorers = report."""

    def __init__(
        self,
        system: SystemFn,
        scorers: list[Scorer],
        pass_threshold: float = 0.5,
    ):
        self.system = system
        self.scorers = scorers
        self.pass_threshold = pass_threshold

    def run_case(self, case: EvalCase) -> EvalResult:
        """Run the system on a single case and score the output."""

        start = time.perf_counter()
        error = None

        try:
            output = self.system(case.input)
        except Exception as e:
            output = ""
            error = f"{type(e).__name__}: {e}"

        latency_ms = (time.perf_counter() - start) * 1000

        # Apply all scorers
        scores: dict[str, float] = {}
        all_results: list[ScoreResult] = []

        for scorer in self.scorers:
            try:
                result = scorer.score(
                    output=output,
                    expected=case.expected,
                    input=case.input,
                    metadata=case.metadata,
                )

                scores[result.name] = result.score
                all_results.append(result)

            except Exception as e:
                scores[scorer.name] = 0.0
                all_results.append(
                    ScoreResult(
                        name=scorer.name,
                        score=0.0,
                        passed=False,
                        reason=f"Scorer error: {e}",
                    )
                )

        # A case passes if the average score meets the threshold
        avg_score = (
            sum(scores.values()) / len(scores)
            if scores
            else 0.0
        )

        passed = (
            avg_score >= self.pass_threshold
            and error is None
        )

        return EvalResult(
            case=case,
            output=output,
            scores=scores,
            passed=passed,
            latency_ms=latency_ms,
            error=error,
            metadata={
                "scorer_details": [
                    {
                        "name": r.name,
                        "score": r.score,
                        "passed": r.passed,
                        "reason": r.reason,
                    }
                    for r in all_results
                ]
            },
        )

    def run(self, dataset: Dataset) -> EvalReport:
        """Run the full evaluation on a dataset."""

        results = []

        for i, case in enumerate(dataset):
            print(
                f"\r  [{i+1}/{len(dataset)}] "
                f"{case.input[:60]}...",
                end=" ",
            )

            result = self.run_case(case)

            status = "PASS" if result.passed else "FAIL"

            print(
                f"[{status} {result.latency_ms:.0f}ms]"
            )

            results.append(result)

        report = EvalReport(
            name=dataset.name,
            results=results,
        )

        # Calculate average scores per scorer
        for scorer in self.scorers:
            scorer_scores = [
                r.scores.get(scorer.name, 0.0)
                for r in results
            ]

            if scorer_scores:
                report.avg_scores[scorer.name] = (
                    sum(scorer_scores) / len(scorer_scores)
                )

        report.avg_latency_ms = (
            sum(r.latency_ms for r in results) / len(results)
            if results
            else 0.0
        )

        return report