"""Dynamic CoT budget calculator for ReasonGap benchmarks.

Computes a word budget for the budget_cot condition based on the task type
and instance metadata, following the theoretical complexity of each task:

| Task | Budget Formula              | Rationale                          |
|------|-----------------------------|------------------------------------|
| B1   | O(n) where n = string len   | Need to count bits                 |
| B2   | O(2^d) where d = depth      | Exponential formula evaluation     |
| B3   | O(k) where k = compositions | Must trace each step               |
| B4   | O(k) where k = transitions  | Must trace each step               |
| B5   | O(d) where d = est diameter | BFS-like reasoning                 |
| B6   | O(n^2) where n = seq length | DP reasoning                       |
| B7   | O(n) where n = variables    | Can't do better than heuristic     |
| B8   | O(n_facts)                  | Just lookup + inverse              |
| B9   | O(d) where d = neg depth    | Track each negation                |

A multiplier (default 3x) is applied to the theoretical minimum to give
models room. Budgets are clamped to [MIN_BUDGET, MAX_BUDGET].
"""

from __future__ import annotations

import math
from typing import Any

MIN_BUDGET: int = 20
MAX_BUDGET: int = 2000
DEFAULT_MULTIPLIER: float = 3.0


def _budget_b1(instance: dict[str, Any], multiplier: float) -> int:
    """B1 Masked Majority: O(n) words where n = string length."""
    metadata = instance.get("metadata", {})
    n = metadata.get("n", metadata.get("n_visible", 20))
    return round(n * multiplier)


def _budget_b2(instance: dict[str, Any], multiplier: float) -> int:
    """B2 Nested Boolean: O(2^depth) words for exponential formula evaluation.

    Nested boolean formulas have exponential structure with depth.
    To properly evaluate them, we need reasoning budget that scales
    exponentially with depth, not logarithmically.
    """
    metadata = instance.get("metadata", {})
    depth = metadata.get("depth", 3)
    # Formula evaluation requires exponential reasoning space
    # Base formula: 2^depth nodes × multiplier
    return round((2 ** depth) * multiplier)


def _budget_b3(instance: dict[str, Any], multiplier: float) -> int:
    """B3 Permutation Composition: O(k) words where k = compositions."""
    metadata = instance.get("metadata", {})
    k = metadata.get("k", 4)
    # Each composition step needs a few words to describe the mapping
    words_per_step = 5
    return round(k * words_per_step * multiplier)


def _budget_b4(instance: dict[str, Any], multiplier: float) -> int:
    """B4 State Machine: O(k) words where k = transitions."""
    metadata = instance.get("metadata", {})
    k = metadata.get("k", 5)
    # Each transition step: "state X, read Y -> state Z"
    words_per_step = 6
    return round(k * words_per_step * multiplier)


def _budget_b5(instance: dict[str, Any], multiplier: float) -> int:
    """B5 Graph Reachability: O(d) words where d = estimated diameter.

    We estimate diameter as roughly sqrt(n_nodes) for sparse random graphs.
    """
    metadata = instance.get("metadata", {})
    n_nodes = metadata.get("n_nodes", 10)
    estimated_diameter = max(3, round(math.sqrt(n_nodes)))
    words_per_step = 8  # describing BFS frontier expansion
    return round(estimated_diameter * words_per_step * multiplier)


def _budget_b6(instance: dict[str, Any], multiplier: float) -> int:
    """B6 LIS: O(n^2) words where n = sequence length."""
    metadata = instance.get("metadata", {})
    n = metadata.get("n", 10)
    # DP reasoning: for each element, consider all previous elements
    # But cap the quadratic growth so we don't explode
    raw = min(n * n, 500)  # cap inner computation
    return round(raw * multiplier)


def _budget_b7(instance: dict[str, Any], multiplier: float) -> int:
    """B7 3-SAT: O(n) words where n = variables."""
    metadata = instance.get("metadata", {})
    n_vars = metadata.get("n_vars", 8)
    # Heuristic reasoning: try assignments, check clauses
    words_per_var = 10
    return round(n_vars * words_per_var * multiplier)


def _budget_b8(instance: dict[str, Any], multiplier: float) -> int:
    """B8 Reversal Inference: O(n_facts) words."""
    metadata = instance.get("metadata", {})
    n_facts = metadata.get("n_facts", 5)
    # Scan facts, find matching one, reverse
    words_per_fact = 8
    return round(n_facts * words_per_fact * multiplier)


def _budget_b9(instance: dict[str, Any], multiplier: float) -> int:
    """B9 Negation Sensitivity: O(d) words where d = negation depth."""
    metadata = instance.get("metadata", {})
    neg_depth = metadata.get("negation_depth", 2)
    # Track each negation flip
    words_per_level = 10
    return round(neg_depth * words_per_level * multiplier)


# Registry mapping task identifiers to budget functions.
# Keys are checked with upper-cased, underscore-stripped prefixes.
_BUDGET_FNS: dict[str, Any] = {
    "B1": _budget_b1,
    "B2": _budget_b2,
    "B3": _budget_b3,
    "B4": _budget_b4,
    "B5": _budget_b5,
    "B6": _budget_b6,
    "B7": _budget_b7,
    "B8": _budget_b8,
    "B9": _budget_b9,
}


def _resolve_task_key(task: str) -> str | None:
    """Resolve a task identifier like 'B1_masked_majority' to 'B1'.

    Matches only if the task string starts with a known key followed
    by end-of-string, underscore, or space (to avoid 'B99' matching 'B9').
    """
    task_upper = task.upper()
    for key in sorted(_BUDGET_FNS.keys(), key=len, reverse=True):
        if task_upper == key:
            return key
        if task_upper.startswith(key + "_") or task_upper.startswith(key + " "):
            return key
    return None


def compute_budget(
    task: str,
    instance: dict[str, Any],
    multiplier: float = DEFAULT_MULTIPLIER,
) -> int:
    """Compute the word budget for a budget_cot evaluation.

    Args:
        task: Task identifier (e.g., "B1", "B1_masked_majority").
        instance: Instance dict containing 'metadata' with task parameters.
        multiplier: Multiplier on the theoretical minimum (default 3.0).

    Returns:
        Word budget clamped to [MIN_BUDGET, MAX_BUDGET].

    Raises:
        ValueError: If the task identifier is not recognized.
    """
    key = _resolve_task_key(task)
    if key is None:
        raise ValueError(
            f"Unknown task '{task}'. Expected one of: {sorted(_BUDGET_FNS.keys())}"
        )

    budget_fn = _BUDGET_FNS[key]
    raw_budget = budget_fn(instance, multiplier)
    return max(MIN_BUDGET, min(MAX_BUDGET, raw_budget))
