"""Iterated carry addition: Add two n-digit numbers, requiring sequential carry propagation.

CoT complexity: c(n) = Theta(n) (carry propagation is inherently serial).
Prediction: d* = min(n, floor(1/eta)). Second linear-complexity task
for robustness alongside parity.

Unlike summing single-digit numbers (which LLMs can chunk), adding two
large n-digit numbers requires genuine sequential processing because
each digit's carry depends on the previous digit's result.
"""

import random as _random

TASK_NAME = "carry_addition"

# n = number of digits per operand; c(n) ≈ n (carry propagation)
DIFFICULTY_PARAMS: dict[int, int] = {
    1: 4,
    2: 8,
    3: 12,
    4: 16,
    5: 24,
    6: 32,
    7: 40,
}


def cot_complexity(difficulty: int) -> int:
    """Return the CoT complexity c(n) ≈ n for this difficulty level."""
    return DIFFICULTY_PARAMS[difficulty]


def _make_n_digit_number(rng: _random.Random, n: int) -> int:
    """Generate a random n-digit number (first digit nonzero)."""
    digits = [rng.randint(1, 9)] + [rng.randint(0, 9) for _ in range(n - 1)]
    return int("".join(str(d) for d in digits))


def generate(n_instances: int, difficulty: int, seed: int = 42) -> list[dict]:
    """Generate carry addition instances.

    Each instance: add two n-digit numbers where most digit pairs produce
    carries (ensuring serial dependency).

    Returns list of dicts with keys: task, difficulty, n, prompt_text,
    ground_truth, instance_id, cot_complexity.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        # Generate two n-digit numbers with many carries
        # Use digits 5-9 to ensure most columns produce carries
        a_digits = [rng.randint(5, 9) for _ in range(n)]
        b_digits = [rng.randint(5, 9) for _ in range(n)]
        a_digits[0] = max(a_digits[0], 1)  # ensure n digits
        b_digits[0] = max(b_digits[0], 1)

        a = int("".join(str(d) for d in a_digits))
        b = int("".join(str(d) for d in b_digits))
        answer = str(a + b)

        instances.append({
            "task": TASK_NAME,
            "difficulty": difficulty,
            "n": n,
            "prompt_text": f"What is {a} + {b}?",
            "ground_truth": answer,
            "instance_id": f"{TASK_NAME}_d{difficulty}_{i}",
            "cot_complexity": n,
        })

    return instances
