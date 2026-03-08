"""ReasonGap benchmark task generators.

Each module exports a `generate(n_instances, difficulty, seed)` function
that returns a list of task instance dicts.
"""

from . import (
    b1_majority,
    b2_boolean_eval,
    b3_permutation,
    b4_state_machine,
    b5_graph_reach,
    b6_lis,
    b7_3sat,
    b8_reversal,
    b9_negation,
)

TASK_REGISTRY: dict[str, object] = {
    "B1": b1_majority,
    "B2": b2_boolean_eval,
    "B3": b3_permutation,
    "B4": b4_state_machine,
    "B5": b5_graph_reach,
    "B6": b6_lis,
    "B7": b7_3sat,
    "B8": b8_reversal,
    "B9": b9_negation,
}

__all__ = [
    "TASK_REGISTRY",
    "b1_majority",
    "b2_boolean_eval",
    "b3_permutation",
    "b4_state_machine",
    "b5_graph_reach",
    "b6_lis",
    "b7_3sat",
    "b8_reversal",
    "b9_negation",
]
