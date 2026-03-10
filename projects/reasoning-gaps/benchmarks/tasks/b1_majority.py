r"""B1: Masked Majority (Sensitivity Gap -- AC^0 boundary).

Task: Given a binary string with some positions masked, determine the
majority value among unmasked positions.

Complexity: MAJORITY in TC^0 \ AC^0.
Prediction: Without CoT, accuracy degrades with n. Short CoT (counting)
should close the gap.
"""

import random as _random

TASK_NAME = "B1_masked_majority"
DIFFICULTY_PARAMS: dict[int, int] = {1: 10, 2: 20, 3: 50, 4: 100, 5: 200}


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate masked majority instances.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls string length n).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    n = DIFFICULTY_PARAMS[difficulty]
    # Mask about 20% of positions, at least 1
    n_masked = max(1, n // 5)

    instances: list[dict] = []
    for i in range(n_instances):
        # Generate random binary string
        bits = [rng.choice([0, 1]) for _ in range(n)]

        # Choose mask positions
        mask_positions = set(rng.sample(range(n), min(n_masked, n)))

        # Build display string
        display = ""
        visible_bits: list[int] = []
        for j, b in enumerate(bits):
            if j in mask_positions:
                display += "?"
            else:
                display += str(b)
                visible_bits.append(b)

        # Compute ground truth
        ones = sum(visible_bits)
        zeros = len(visible_bits) - ones
        if ones > zeros:
            answer = "1"
        elif zeros > ones:
            answer = "0"
        else:
            # Tie -- break randomly using the RNG for balanced distribution
            if visible_bits:
                tie_target = rng.choice([0, 1])
                # Find a visible position that is NOT tie_target and flip it
                opposite = 1 - tie_target
                for j in range(n):
                    if j not in mask_positions and bits[j] == opposite:
                        bits[j] = tie_target
                        break
                # Rebuild
                display = ""
                visible_bits = []
                for j, b in enumerate(bits):
                    if j in mask_positions:
                        display += "?"
                    else:
                        display += str(b)
                        visible_bits.append(b)
                ones = sum(visible_bits)
                zeros = len(visible_bits) - ones
                answer = "1" if ones > zeros else "0"
            else:
                answer = "0"  # fallback (shouldn't happen)

        prompt = (
            f"Consider the binary string: {display}\n"
            f"The '?' characters are masked and should be ignored.\n"
            f"Among the visible (unmasked) bits, is the majority 0 or 1?\n"
            f"Answer with just '0' or '1'."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "n": n,
                "n_masked": len(mask_positions),
                "n_visible": len(visible_bits),
                "ones": ones,
                "zeros": zeros,
            },
        })

    return instances
