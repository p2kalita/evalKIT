"""example_eval.py — Putting it all together."""


from evalkit.datasets.loader import Dataset
from evalkit.scorers.deterministic import ExactMatch, Contains
from evalkit.runners.base import Runner
from evalkit.types import EvalCase


def my_qa_system(question: str) -> str:
    """Stub system — replace with a real LLM call."""

    answers = {
        "what is the capital of france?": "Paris",
        "what is 2 + 2?": "The answer is 4.",
        "who wrote Hamlet?": "William Shakespeare wrote Hamlet.",
    }

    return answers.get(question.lower(), "I don't know.")


# Load dataset
dataset = Dataset(
    name="qa_basic",
    cases=[
        EvalCase(
            input="What is the capital of France?",
            expected="Paris",
            tags=["geography"],
        ),
        EvalCase(
            input="What is 2 + 2?",
            expected="4",
            tags=["math"],
        ),
        EvalCase(
            input="Who wrote Hamlet?",
            expected="William Shakespeare",
            tags=["literature"],
        ),
    ],
)

# Configure scorers
scorers = [
    ExactMatch(),
    Contains(),
]

# Run evaluation
runner = Runner(
    system=my_qa_system,
    scorers=scorers,
)

report = runner.run(dataset)

print("\n" + report.summary())