"""B3: Iterated Permutation Composition (Serial Gap).

Task: Apply a sequence of k permutations to an initial element and report
the final position.

Complexity: Iterated permutation composition requires Omega(k) sequential steps.
Prediction: Accuracy degrades linearly with k. Requires O(k) CoT steps.
Log CoT insufficient. Domain size m has secondary effect.
"""

import random as _random

TASK_NAME = "B3_permutation_composition"
# (k compositions, domain size m)
DIFFICULTY_PARAMS: dict[int, tuple[int, int]] = {
    1: (2, 5),
    2: (4, 5),
    3: (8, 5),
    4: (16, 5),
    5: (32, 5),
}


def _random_permutation(rng: _random.Random, m: int) -> list[int]:
    """Generate a random permutation of [0, 1, ..., m-1].

    Returns a list p where p[i] is the image of position i.
    """
    perm = list(range(m))
    rng.shuffle(perm)
    return perm


def _format_permutation(perm: list[int]) -> str:
    """Format a permutation as a human-readable mapping.

    Uses 1-indexed positions for clarity.
    """
    mappings = ", ".join(f"{i+1}->{p+1}" for i, p in enumerate(perm))
    return f"[{mappings}]"


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate iterated permutation composition instances.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls k compositions).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    k, m = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        # Generate k random permutations
        perms = [_random_permutation(rng, m) for _ in range(k)]

        # Choose random starting position (1-indexed for the prompt)
        start_pos = rng.randint(0, m - 1)

        # Compute ground truth by applying permutations sequentially
        current = start_pos
        for perm in perms:
            current = perm[current]
        answer = str(current + 1)  # 1-indexed answer

        # Build prompt
        perm_lines = "\n".join(
            f"  sigma_{j+1} = {_format_permutation(p)}"
            for j, p in enumerate(perms)
        )
        application_order = " then ".join(
            f"sigma_{j+1}" for j in range(k)
        )

        prompt = (
            f"Starting at position {start_pos + 1}, apply the following "
            f"permutations in order: {application_order}.\n\n"
            f"Each permutation maps position i to a new position. "
            f"The notation [1->3, 2->1, 3->2] means position 1 goes to 3, "
            f"position 2 goes to 1, position 3 goes to 2.\n\n"
            f"Permutations:\n{perm_lines}\n\n"
            f"What is the final position? Answer with just the position number."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "k": k,
                "m": m,
                "start_pos": start_pos + 1,
                "permutations": perms,
            },
        })

    return instances
