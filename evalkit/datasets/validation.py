"""evalkit/datasets/validation.py — Dataset quality checks."""

from dataclasses import dataclass

from evalkit.datasets.loader import Dataset


@dataclass
class ValidationIssue:
    """A single validation issue found in the dataset."""

    severity: str  # "error" or "warning"
    case_index: int
    message: str


def validate_dataset(dataset: Dataset) -> list[ValidationIssue]:
    """Run quality checks on a dataset. Returns list of issues."""

    issues = []

    # Check for empty dataset
    if len(dataset) == 0:
        issues.append(
            ValidationIssue(
                severity="error",
                case_index=-1,
                message="Dataset is empty",
            )
        )
        return issues

    # Check each case
    seen_inputs = {}

    for i, case in enumerate(dataset):
        # Empty input
        if not case.input.strip():
            issues.append(
                ValidationIssue(
                    severity="error",
                    case_index=i,
                    message="Empty input",
                )
            )

        # Duplicate inputs
        normalized = case.input.strip().lower()

        if normalized in seen_inputs:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    case_index=i,
                    message=f"Duplicate input (same as case {seen_inputs[normalized]})",
                )
            )
        else:
            seen_inputs[normalized] = i

        # Very short expected values (might be incomplete)
        if case.expected is not None and len(case.expected.strip()) < 2:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    case_index=i,
                    message=f"Very short expected value: '{case.expected}'",
                )
            )

        # Input equals expected (trivial test)
        if (
            case.expected is not None
            and case.input.strip() == case.expected.strip()
        ):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    case_index=i,
                    message="Input equals expected (trivial test case)",
                )
            )

    # Check tag consistency
    all_tags = set()

    for case in dataset:
        all_tags.update(case.tags)

    if not all_tags:
        issues.append(
            ValidationIssue(
                severity="warning",
                case_index=-1,
                message="No tags found — consider tagging cases for filtering",
            )
        )

    # Check expected coverage
    no_expected = sum(1 for c in dataset if c.expected is None)

    if no_expected == len(dataset):
        issues.append(
            ValidationIssue(
                severity="warning",
                case_index=-1,
                message="No cases have expected values — only reference-free scorers will work",
            )
        )

    return issues


def print_validation_report(
    issues: list[ValidationIssue],
) -> None:
    """Print a formatted validation report."""

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if not issues:
        print("Dataset validation: PASSED (no issues)")
        return

    print(
        f"Dataset validation: {len(errors)} errors, "
        f"{len(warnings)} warnings\n"
    )

    for issue in errors:
        loc = (
            f"case {issue.case_index}"
            if issue.case_index >= 0
            else "global"
        )
        print(f"  ERROR [{loc}]: {issue.message}")

    for issue in warnings:
        loc = (
            f"case {issue.case_index}"
            if issue.case_index >= 0
            else "global"
        )
        print(f"  WARNING [{loc}]: {issue.message}")