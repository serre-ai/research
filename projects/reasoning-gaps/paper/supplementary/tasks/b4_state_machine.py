"""B4: State Tracking Machine (Serial Composition Gap -- variant).

Task: Simulate a simple finite automaton for k steps and report final state.

Complexity: FSA simulation requires Omega(k) steps for constant-depth circuits.
Prediction: Same as B3 -- accuracy degrades with k. CoT of length O(k) needed.
"""

import random as _random
import string

TASK_NAME = "B4_state_machine"
# (k transitions, number of states)
DIFFICULTY_PARAMS: dict[int, tuple[int, int]] = {
    1: (3, 4),
    2: (5, 4),
    3: (10, 4),
    4: (20, 4),
    5: (50, 4),
}

# Use letters for state names
STATE_NAMES = list(string.ascii_uppercase)
# Binary input alphabet
ALPHABET = ["0", "1"]


def _random_transition_table(
    rng: _random.Random, n_states: int
) -> dict[str, dict[str, str]]:
    """Generate a random deterministic transition table.

    Returns a dict mapping (state, symbol) -> next_state.
    """
    states = STATE_NAMES[:n_states]
    table: dict[str, dict[str, str]] = {}
    for s in states:
        table[s] = {}
        for sym in ALPHABET:
            table[s][sym] = rng.choice(states)
    return table


def _format_transition_table(table: dict[str, dict[str, str]]) -> str:
    """Format the transition table for the prompt."""
    lines: list[str] = []
    for state in sorted(table.keys()):
        for sym in ALPHABET:
            next_state = table[state][sym]
            lines.append(f"  {state} --{sym}--> {next_state}")
    return "\n".join(lines)


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate state machine simulation instances.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls k transitions).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    k, n_states = DIFFICULTY_PARAMS[difficulty]
    states = STATE_NAMES[:n_states]

    instances: list[dict] = []
    for i in range(n_instances):
        # Generate random transition table
        table = _random_transition_table(rng, n_states)

        # Generate random input string of length k
        input_str = "".join(rng.choice(ALPHABET) for _ in range(k))

        # Choose random start state
        start_state = rng.choice(states)

        # Simulate to get ground truth
        current = start_state
        for sym in input_str:
            current = table[current][sym]
        answer = current

        # Build prompt
        table_str = _format_transition_table(table)
        states_str = ", ".join(states)

        prompt = (
            f"A finite state machine has states: {{{states_str}}}.\n"
            f"The input alphabet is {{0, 1}}.\n"
            f"Transition rules:\n{table_str}\n\n"
            f"Starting state: {start_state}\n"
            f"Input sequence: {input_str}\n\n"
            f"Process each input symbol left to right and follow the "
            f"transition rules. What is the final state?\n"
            f"Answer with just the state letter."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "k": k,
                "n_states": n_states,
                "start_state": start_state,
                "input_string": input_str,
                "transition_table": table,
            },
        })

    return instances
