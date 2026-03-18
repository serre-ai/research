"""B2: Nested Boolean Evaluation (Depth Gap -- TC^0/NC^1 boundary).

Task: Evaluate a Boolean formula with nested AND/OR/NOT operations.

Complexity: Boolean Formula Value in NC^1 (NC^1-complete under AC^0 reductions).
Prediction: Accuracy degrades with depth d, not width. O(log n) CoT steps
should suffice. Performance cliff at depth > transformer's effective depth.
"""

import random as _random

TASK_NAME = "B2_nested_boolean"
DIFFICULTY_PARAMS: dict[int, int] = {1: 2, 2: 3, 3: 5, 4: 7, 5: 10}


def _generate_formula(rng: _random.Random, depth: int) -> tuple[str, bool]:
    """Recursively generate a Boolean formula and its value.

    Args:
        rng: Seeded Random instance.
        depth: Remaining nesting depth.

    Returns:
        (formula_string, truth_value)
    """
    if depth == 0:
        val = rng.choice([True, False])
        return ("T" if val else "F", val)

    op = rng.choice(["AND", "OR", "NOT"])

    if op == "NOT":
        sub_formula, sub_val = _generate_formula(rng, depth - 1)
        return (f"NOT({sub_formula})", not sub_val)
    else:
        # Binary operator: generate two children, each at depth - 1
        # Randomly reduce depth of one child to add variety
        left_depth = depth - 1
        right_depth = rng.randint(0, depth - 1)
        left_formula, left_val = _generate_formula(rng, left_depth)
        right_formula, right_val = _generate_formula(rng, right_depth)

        if op == "AND":
            result = left_val and right_val
        else:  # OR
            result = left_val or right_val

        return (f"{op}({left_formula}, {right_formula})", result)


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate nested Boolean evaluation instances.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls nesting depth).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    depth = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        formula, value = _generate_formula(rng, depth)
        answer = "True" if value else "False"

        prompt = (
            f"Evaluate the following Boolean expression, where T = True "
            f"and F = False:\n\n"
            f"{formula}\n\n"
            f"What is the result? Answer with just 'True' or 'False'."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "depth": depth,
                "formula": formula,
            },
        })

    return instances
