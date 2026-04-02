"""Parity task: What is the XOR of all input bits?

CoT complexity: c(n) = Theta(n) (Amiri et al., ICML 2025).
Prediction: d* = min(n, floor(1/eta)). Easy regime for small n,
hard regime (noise-capped) for large n.
"""

import random as _random

TASK_NAME = "parity"

# n = number of bits; c(n) ≈ n
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
    """Return the CoT complexity c(n) for this difficulty level."""
    return DIFFICULTY_PARAMS[difficulty]


def generate(n_instances: int, difficulty: int, seed: int = 42) -> list[dict]:
    """Generate parity instances.

    Returns list of dicts with keys: task, difficulty, n, prompt_text,
    ground_truth, instance_id, cot_complexity.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        bits = [rng.choice([0, 1]) for _ in range(n)]
        answer = str(sum(bits) % 2)
        bit_str = " ".join(str(b) for b in bits)

        instances.append({
            "task": TASK_NAME,
            "difficulty": difficulty,
            "n": n,
            "prompt_text": f"What is the XOR (parity) of all the following bits? Answer 0 if the count of 1s is even, 1 if odd.\n\n{bit_str}",
            "ground_truth": answer,
            "instance_id": f"{TASK_NAME}_d{difficulty}_{i}",
            "cot_complexity": n,
        })

    return instances
