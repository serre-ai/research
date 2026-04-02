"""Multi-step arithmetic: Sum n single-digit numbers sequentially.

CoT complexity: c(n) = n-1 (each addition is one step).
Prediction: d* = min(n-1, floor(1/eta)). Second linear-complexity task
for robustness alongside parity.
"""

import random as _random

TASK_NAME = "arithmetic"

# n = count of numbers to sum; c(n) = n-1
DIFFICULTY_PARAMS: dict[int, int] = {
    1: 5,
    2: 10,
    3: 15,
    4: 20,
    5: 30,
    6: 40,
    7: 50,
}


def cot_complexity(difficulty: int) -> int:
    """Return the CoT complexity c(n) = n-1 for this difficulty level."""
    return DIFFICULTY_PARAMS[difficulty] - 1


def generate(n_instances: int, difficulty: int, seed: int = 42) -> list[dict]:
    """Generate multi-step addition instances.

    Returns list of dicts with keys: task, difficulty, n, prompt_text,
    ground_truth, instance_id, cot_complexity.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        numbers = [rng.randint(1, 9) for _ in range(n)]
        answer = str(sum(numbers))
        nums_str = " + ".join(str(x) for x in numbers)

        instances.append({
            "task": TASK_NAME,
            "difficulty": difficulty,
            "n": n,
            "prompt_text": f"Compute the sum:\n\n{nums_str}",
            "ground_truth": answer,
            "instance_id": f"{TASK_NAME}_d{difficulty}_{i}",
            "cot_complexity": n - 1,
        })

    return instances
