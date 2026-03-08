"""B9: Negation Sensitivity (Architectural Gap -- variant).

Task: Answer the same question with and without negation, verify consistency.

Complexity: Not a complexity-class issue -- tests sensitivity to negation
in the autoregressive architecture.
Prediction: Accuracy degrades with negation depth. CoT may help with
explicit negation tracking but the gap persists for implicit negation.
"""

import random as _random

TASK_NAME = "B9_negation_sensitivity"
DIFFICULTY_PARAMS: dict[int, int] = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}

# Propositions with known truth values (simple facts)
_PROPOSITIONS: list[tuple[str, bool]] = [
    ("water boils at 100 degrees Celsius at sea level", True),
    ("the Earth orbits the Sun", True),
    ("humans have three arms", False),
    ("the speed of light is infinite", False),
    ("2 + 2 equals 4", True),
    ("the Moon is larger than the Earth", False),
    ("diamonds are harder than glass", True),
    ("fish can breathe in air without water", False),
    ("gold is a chemical element", True),
    ("the Pacific Ocean is the smallest ocean", False),
    ("iron is attracted to magnets", True),
    ("sound travels faster than light", False),
    ("DNA has a double helix structure", True),
    ("penguins can fly long distances", False),
    ("the chemical formula for water is H2O", True),
    ("mercury is a solid at room temperature", False),
    ("the Great Wall of China is visible from space with the naked eye", False),
    ("oxygen is necessary for human survival", True),
    ("pi is exactly equal to 3", False),
    ("lightning is hotter than the surface of the Sun", True),
]


def _apply_negations(proposition: str, truth_value: bool, depth: int) -> tuple[str, bool]:
    """Apply a specified number of negation layers.

    Returns the negated sentence and the resulting truth value.

    Each negation wraps the proposition in "it is NOT the case that ..."
    """
    current = proposition
    current_value = truth_value

    for d in range(depth):
        if d == 0:
            current = f"it is NOT the case that {current}"
        elif d == 1:
            current = f"it is NOT true that {current}"
        elif d == 2:
            current = f"it is NOT the case that {current}"
        elif d == 3:
            current = f"it is NOT correct that {current}"
        else:
            current = f"it is NOT the case that {current}"
        current_value = not current_value

    return current, current_value


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate negation sensitivity instances.

    Each instance presents a proposition wrapped in a specified number of
    negation layers and asks whether the resulting statement is true or false.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls negation depth).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    neg_depth = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        # Pick a base proposition
        base_prop, base_truth = rng.choice(_PROPOSITIONS)

        # Apply negation layers
        negated_prop, final_truth = _apply_negations(base_prop, base_truth, neg_depth)

        answer = "True" if final_truth else "False"

        prompt = (
            f"Determine whether the following statement is true or false.\n\n"
            f"Statement: Is it true that {negated_prop}?\n\n"
            f"Answer with just 'True' or 'False'."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "negation_depth": neg_depth,
                "base_proposition": base_prop,
                "base_truth": base_truth,
                "final_truth": final_truth,
            },
        })

    return instances
