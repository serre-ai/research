"""l-fold function composition: Compute f_l(f_{l-1}(...f_1(x)...))

CoT complexity: c = l exactly (Barcelo et al., ICML 2025).
Prediction: d* = min(l, floor(1/eta)). Exact calibration task.
"""

import random as _random

TASK_NAME = "composition"

# l = number of compositions; c = l exactly
DIFFICULTY_PARAMS: dict[int, int] = {
    1: 2,
    2: 4,
    3: 6,
    4: 8,
    5: 10,
    6: 15,
    7: 20,
    8: 25,
}

# Simple linear functions: f(x) = ax + b with small integer coefficients
_FUNCTIONS = [
    (2, 1, "2x + 1"),
    (3, -1, "3x - 1"),
    (1, 5, "x + 5"),
    (2, -3, "2x - 3"),
    (1, 7, "x + 7"),
    (3, 2, "3x + 2"),
    (2, -1, "2x - 1"),
    (1, -4, "x - 4"),
]


def cot_complexity(difficulty: int) -> int:
    """Return the CoT complexity c = l for this difficulty level."""
    return DIFFICULTY_PARAMS[difficulty]


def generate(n_instances: int, difficulty: int, seed: int = 42) -> list[dict]:
    """Generate l-fold function composition instances.

    Returns list of dicts with keys: task, difficulty, l, prompt_text,
    ground_truth, instance_id, cot_complexity.
    """
    rng = _random.Random(seed)
    l = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        # Pick l functions (with replacement from the pool)
        funcs = [rng.choice(_FUNCTIONS) for _ in range(l)]
        # Pick starting value
        x = rng.randint(1, 10)

        # Compute ground truth by applying functions sequentially
        current = x
        for a, b, _ in funcs:
            current = a * current + b
        answer = str(current)

        # Build prompt
        func_lines = []
        for j, (a, b, label) in enumerate(funcs, 1):
            func_lines.append(f"  f_{j}(x) = {label}")
        func_text = "\n".join(func_lines)

        composition = " ∘ ".join(f"f_{j}" for j in range(l, 0, -1))

        instances.append({
            "task": TASK_NAME,
            "difficulty": difficulty,
            "l": l,
            "prompt_text": (
                f"Given the following functions:\n{func_text}\n\n"
                f"Compute ({composition})({x}), i.e., apply f_1 first, then f_2, "
                f"and so on up to f_{l}.\n\n"
                f"What is the final value?"
            ),
            "ground_truth": answer,
            "instance_id": f"{TASK_NAME}_d{difficulty}_{i}",
            "cot_complexity": l,
        })

    return instances
