

def my_system(question: str) -> str:
    """The system under test - in practice, an LLM call."""
    # Placeholder: replace with your actual LLM call
    return "Paris"


# Dataset: list of (input, expected_output) paris
dataset = [
    ("What is the capital of France?", "Paris"),
    ("What is the capital of Germany?", "Berlin"),
    ("What is the capital of Japan?", "Tokyo"),
]



# Scorer: exact match
def exact_match(output: str, expected: str) -> bool:
    return output.strip().lower() == expected.strip().lower()


# Runner: execute and report
def run_eval():
    results = []
    for question, expected in dataset:
        output = my_system(question)
        passed = exact_match(output, expected)
        results.append({"input": question, "expected": expected,
                        "output": output, "passed": passed})
        status = "PASS" if passed else "FAIL"
        print(f" {status}: {question} -> {output}")

    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    print(f"\nPass rate: {pass_rate:.0%}")
    return results

if __name__ == "__main__":
    run_eval()
