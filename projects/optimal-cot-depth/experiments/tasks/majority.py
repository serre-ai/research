"""Majority task (TC^0): Is the majority of input bits 1?

CoT complexity: c(n) = 0.
Prediction: d* = 0 for all n. Any CoT should hurt accuracy.
"""

import random as _random

TASK_NAME = "majority"
COT_COMPLEXITY = 0  # TC^0 — solvable without CoT

# n = number of bits
DIFFICULTY_PARAMS: dict[int, int] = {1: 10, 2: 50, 3: 200}


def generate(n_instances: int, difficulty: int, seed: int = 42) -> list[dict]:
    """Generate majority instances.

    Returns list of dicts with keys: task, difficulty, n, prompt_text,
    ground_truth, instance_id, cot_complexity.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        bits = [rng.choice([0, 1]) for _ in range(n)]
        ones = sum(bits)
        zeros = n - ones
        # Ensure no ties
        if ones == zeros:
            bits[-1] = 1 - bits[-1]
            ones = sum(bits)
            zeros = n - ones

        answer = "1" if ones > zeros else "0"
        bit_str = " ".join(str(b) for b in bits)

        instances.append({
            "task": TASK_NAME,
            "difficulty": difficulty,
            "n": n,
            "prompt_text": f"What is the majority bit in the following sequence?\n\n{bit_str}",
            "ground_truth": answer,
            "instance_id": f"{TASK_NAME}_d{difficulty}_{i}",
            "cot_complexity": COT_COMPLEXITY,
        })

    return instances
