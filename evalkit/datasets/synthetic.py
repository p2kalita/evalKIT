import json
import anthropic

from evalkit.types import EvalCase


class SyntheticGenerator:
    """Generates synthetic test cases using an LLM."""

    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic()
        self.model = model

    def generate(
        self,
        task_description: str,
        num_cases: int = 10,
        difficulty: str = "mixed",
        existing_inputs: list[str] | None = None,
    ) -> list[EvalCase]:
        """Generate synthetic test cases for a task."""

        existing_text = ""

        if existing_inputs:
            examples = "\n".join(
                f"- {inp}" for inp in existing_inputs[:10]
            )
            existing_text = (
                f"\n\nHere are some existing inputs "
                f"(generate DIFFERENT ones):\n{examples}"
            )

        prompt = f"""Generate {num_cases} test cases for this task:

{task_description}

Difficulty level: {difficulty}
{existing_text}

Return a JSON array where each item has:
- "input": the test input
- "expected": the expected correct output
- "tags": list of relevant tags including difficulty
- "metadata": any helpful context

Return ONLY the JSON array, no other text."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        raw_text = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1]
            raw_text = raw_text.rsplit("\n```", 1)[0]

        items = json.loads(raw_text)

        cases = []

        for item in items:
            cases.append(
                EvalCase(
                    input=item["input"],
                    expected=item.get("expected"),
                    metadata=item.get("metadata", {}),
                    tags=item.get("tags", ["synthetic"]),
                )
            )

        return cases