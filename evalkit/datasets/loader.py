"""evalkit/datasets/loader.py — Dataset loading and validation."""

import json
from pathlib import Path

from evalkit.types import EvalCase


class Dataset:
    """A collection of evaluation cases with loading and filtering."""

    def __init__(self, name: str, cases: list[EvalCase]):
        self.name = name
        self.cases = cases

    def __len__(self) -> int:
        return len(self.cases)

    def __iter__(self):
        return iter(self.cases)

    def __getitem__(self, index: int) -> EvalCase:
        return self.cases[index]

    def filter_by_tag(self, tag: str) -> "Dataset":
        """Return a new Dataset with only cases matching the tag."""

        filtered = [c for c in self.cases if tag in c.tags]
        return Dataset(name=f"{self.name}[{tag}]", cases=filtered)

    def sample(self, n: int, seed: int = 42) -> "Dataset":
        """Return a random sample of n cases."""

        import random

        rng = random.Random(seed)
        sampled = rng.sample(self.cases, min(n, len(self.cases)))
        return Dataset(name=f"{self.name}[sample={n}]", cases=sampled)

    
    @classmethod
    def from_json(
        cls,
        path: str | Path,
        name: str | None = None,
    ) -> "Dataset":
        """Load a Dataset from a JSON file.

        Expected format:

        [
            {"input": "...", "expected": "...", "tags": ["tag1"]},
            ...
        ]
        """

        path = Path(path)

        if name is None:
            name = path.stem

        with open(path) as f:
            raw = json.load(f)

        cases = []

        for i, item in enumerate(raw):
            if "input" not in item:
                raise ValueError(
                    f"Case {i} in {path} missing required 'input' field"
                )

            cases.append(
                EvalCase(
                    input=item["input"],
                    expected=item.get("expected"),
                    metadata=item.get("metadata", {}),
                    tags=item.get("tags", []),
                )
            )

        return cls(name=name, cases=cases)


    @classmethod
    def from_jsonl(
        cls,
        path: str | Path,
        name: str | None = None,
    ) -> "Dataset":
        """Load a Dataset from a JSONL file (one JSON object per line)."""

        path = Path(path)

        if name is None:
            name = path.stem

        cases = []

        with open(path) as f:
            for i, line in enumerate(f):
                line = line.strip()

                if not line:
                    continue

                item = json.loads(line)

                if "input" not in item:
                    raise ValueError(
                        f"Line {i+1} in {path} missing required 'input' field"
                    )

                cases.append(
                    EvalCase(
                        input=item["input"],
                        expected=item.get("expected"),
                        metadata=item.get("metadata", {}),
                        tags=item.get("tags", []),
                    )
                )

        return cls(name=name, cases=cases)


    def to_json(self, path: str | Path) -> None:
        """Save the dataset to a JSON file."""

        path = Path(path)
        data = []

        for case in self.cases:
            item = {"input": case.input}

            if case.expected is not None:
                item["expected"] = case.expected

            if case.metadata:
                item["metadata"] = case.metadata

            if case.tags:
                item["tags"] = case.tags

            data.append(item)

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=2)


    def stats(self) -> dict:
        """Return basic statistics about the dataset."""

        all_tags = [
            tag
            for c in self.cases
            for tag in c.tags
        ]

        tag_counts = {}

        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "name": self.name,
            "total_cases": len(self.cases),
            "with_expected": sum(
                1
                for c in self.cases
                if c.expected is not None
            ),
            "without_expected": sum(
                1
                for c in self.cases
                if c.expected is None
            ),
            "tags": tag_counts,
        }