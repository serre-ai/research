"""B6: Longest Increasing Subsequence (Algorithmic Gap).

Task: Find the length of the longest increasing subsequence of a given sequence.

Complexity: LIS in P (O(n log n) algorithm), but requires non-trivial
algorithmic reasoning.
Prediction: Accuracy degrades with n. CoT helps moderately.
Code/tool execution should dramatically outperform CoT.
"""

import random as _random
import bisect

TASK_NAME = "B6_longest_increasing_subsequence"
DIFFICULTY_PARAMS: dict[int, int] = {1: 5, 2: 10, 3: 20, 4: 50, 5: 100}


def _compute_lis_length(seq: list[int]) -> int:
    """Compute the length of the longest strictly increasing subsequence.

    Uses the O(n log n) patience sorting algorithm.
    """
    # tails[i] is the smallest tail element for an increasing subsequence
    # of length i+1
    tails: list[int] = []
    for x in seq:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate Longest Increasing Subsequence instances.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls sequence length n).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]

    instances: list[dict] = []
    for i in range(n_instances):
        # Generate a random permutation (without replacement) from [1, 2n]
        # to match the paper's "permutation" specification
        seq = rng.sample(range(1, 2 * n + 1), n)

        lis_length = _compute_lis_length(seq)
        answer = str(lis_length)

        seq_str = ", ".join(str(x) for x in seq)

        prompt = (
            f"Find the length of the longest strictly increasing "
            f"subsequence of the following sequence:\n\n"
            f"[{seq_str}]\n\n"
            f"A subsequence does not need to be contiguous. "
            f"For example, in [3, 1, 4, 2, 5], the longest strictly "
            f"increasing subsequence is [1, 4, 5] or [1, 2, 5], "
            f"with length 3.\n\n"
            f"What is the length? Answer with just the number."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "n": n,
                "sequence": seq,
                "lis_length": lis_length,
            },
        })

    return instances
