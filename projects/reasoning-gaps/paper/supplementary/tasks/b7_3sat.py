"""B7: 3-SAT at Phase Transition (Intractability Gap).

Task: Determine satisfiability of a 3-SAT formula near the phase transition
(clause-to-variable ratio alpha ~ 4.27).

Complexity: 3-SAT is NP-complete.
Prediction: Accuracy degrades sharply at alpha ~ 4.27. CoT provides no
systematic improvement at the phase transition.
"""

from __future__ import annotations

import random as _random

TASK_NAME = "B7_3sat"
DIFFICULTY_PARAMS: dict[int, int] = {1: 4, 2: 8, 3: 16, 4: 32, 5: 64}
ALPHA = 4.27  # Phase transition ratio


def _generate_3sat_formula(
    rng: _random.Random, n_vars: int, n_clauses: int
) -> list[list[int]]:
    """Generate a random 3-SAT formula.

    Each clause is a list of 3 literals. A literal is a nonzero integer:
    positive means the variable, negative means its negation.
    Variables are numbered 1 to n_vars.
    """
    clauses: list[list[int]] = []
    for _ in range(n_clauses):
        # Pick 3 distinct variables
        variables = rng.sample(range(1, n_vars + 1), min(3, n_vars))
        # Randomly negate each
        clause = [v if rng.random() < 0.5 else -v for v in variables]
        clauses.append(clause)
    return clauses


def _check_satisfiability(
    clauses: list[list[int]], n_vars: int
) -> tuple[bool | None, list[bool] | None]:
    """Check satisfiability by exhaustive enumeration (for small n).

    For larger n, uses DPLL-style backtracking.
    Returns (is_sat, assignment_or_None). Returns (None, None) on timeout.
    """
    if n_vars <= 20:
        # Exhaustive for small instances
        for assignment_bits in range(2**n_vars):
            assignment = {}
            for v in range(1, n_vars + 1):
                assignment[v] = bool((assignment_bits >> (v - 1)) & 1)

            sat = True
            for clause in clauses:
                clause_sat = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment[var]
                    if lit > 0 and val:
                        clause_sat = True
                        break
                    elif lit < 0 and not val:
                        clause_sat = True
                        break
                if not clause_sat:
                    sat = False
                    break

            if sat:
                return True, [assignment.get(v, False) for v in range(1, n_vars + 1)]

        return False, None
    else:
        # DPLL-style solver for larger instances
        return _dpll_solve(clauses, n_vars)


# Maximum number of recursive calls before aborting (prevents hanging on large instances)
_DPLL_NODE_LIMIT = 500_000


class _DPLLTimeout(Exception):
    """Raised when DPLL exceeds its node budget."""
    pass


def _dpll_solve(
    clauses: list[list[int]], n_vars: int
) -> tuple[bool | None, list[bool] | None]:
    """Simple DPLL SAT solver with immutable assignment passing and node limit."""
    node_count = [0]  # mutable counter in closure

    def _propagate(
        clauses: list[list[int]], assignment: dict[int, bool]
    ) -> tuple[list[list[int]] | None, dict[int, bool]]:
        """Unit propagation. Returns (simplified_clauses, updated_assignment) or (None, ...) if conflict.

        Does NOT mutate the incoming assignment -- returns a new copy.
        """
        assignment = dict(assignment)  # copy to avoid mutation
        changed = True
        while changed:
            changed = False
            new_clauses: list[list[int]] = []
            for clause in clauses:
                # Remove false literals, check for true literals
                new_clause: list[int] = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        val = assignment[var]
                        if (lit > 0 and val) or (lit < 0 and not val):
                            satisfied = True
                            break
                        # else: literal is false, skip it
                    else:
                        new_clause.append(lit)

                if satisfied:
                    continue
                if len(new_clause) == 0:
                    return None, assignment  # Conflict
                if len(new_clause) == 1:
                    # Unit clause: force assignment
                    lit = new_clause[0]
                    var = abs(lit)
                    assignment[var] = lit > 0
                    changed = True
                else:
                    new_clauses.append(new_clause)

            clauses = new_clauses

        return clauses, assignment

    def _solve(
        clauses: list[list[int]], assignment: dict[int, bool]
    ) -> tuple[bool, dict[int, bool]]:
        node_count[0] += 1
        if node_count[0] > _DPLL_NODE_LIMIT:
            raise _DPLLTimeout()

        result, assignment = _propagate(clauses, assignment)
        if result is None:
            return False, assignment
        clauses = result

        if len(clauses) == 0:
            return True, assignment

        # Find unassigned variable
        unassigned = None
        for clause in clauses:
            for lit in clause:
                var = abs(lit)
                if var not in assignment:
                    unassigned = var
                    break
            if unassigned is not None:
                break

        if unassigned is None:
            return True, assignment

        # Try True -- pass a copy of assignment (immutable pattern)
        true_assignment = dict(assignment)
        true_assignment[unassigned] = True
        sat, true_assignment = _solve(list(clauses), true_assignment)
        if sat:
            return True, true_assignment

        # Try False -- pass a copy of assignment (immutable pattern)
        false_assignment = dict(assignment)
        false_assignment[unassigned] = False
        sat, false_assignment = _solve(list(clauses), false_assignment)
        if sat:
            return True, false_assignment

        return False, assignment

    try:
        sat, final_assignment = _solve(list(clauses), {})
        if sat:
            result_assignment = [
                final_assignment.get(v, False) for v in range(1, n_vars + 1)
            ]
            return True, result_assignment
        return False, None
    except _DPLLTimeout:
        # Could not determine within node limit -- signal to caller
        return None, None


def _format_clause(clause: list[int]) -> str:
    """Format a clause as a human-readable string."""
    parts: list[str] = []
    for lit in clause:
        var = abs(lit)
        if lit > 0:
            parts.append(f"x{var}")
        else:
            parts.append(f"~x{var}")
    return f"({' v '.join(parts)})"


def generate(
    n_instances: int, difficulty: int, seed: int = 42
) -> list[dict]:
    """Generate 3-SAT instances at the phase transition.

    Args:
        n_instances: Number of instances to generate.
        difficulty: Difficulty level 1-5 (controls number of variables).
        seed: Random seed for reproducibility.

    Returns:
        List of task instance dicts.
    """
    rng = _random.Random(seed)
    n_vars = DIFFICULTY_PARAMS[difficulty]
    n_clauses = int(ALPHA * n_vars)

    _MAX_RETRIES = 50  # avoid infinite loops on pathologically hard regimes

    instances: list[dict] = []
    for i in range(n_instances):
        # Retry with fresh random formulas if solver times out
        for _attempt in range(_MAX_RETRIES):
            clauses = _generate_3sat_formula(rng, n_vars, n_clauses)
            is_sat, assignment = _check_satisfiability(clauses, n_vars)
            if is_sat is not None:
                break
        else:
            raise RuntimeError(
                f"B7 generate: failed to produce a solvable instance after "
                f"{_MAX_RETRIES} attempts (n_vars={n_vars}). "
                f"Consider raising _DPLL_NODE_LIMIT."
            )
        answer = "Yes" if is_sat else "No"

        # Format formula
        clause_strs = [_format_clause(c) for c in clauses]
        formula_str = " ^ ".join(clause_strs)

        variables_str = ", ".join(f"x{v}" for v in range(1, n_vars + 1))

        prompt = (
            f"Determine if the following 3-SAT formula is satisfiable.\n\n"
            f"Variables: {variables_str}\n"
            f"Formula: {formula_str}\n\n"
            f"Where 'v' means OR, '^' means AND, and '~' means NOT.\n"
            f"Is this formula satisfiable? Answer with just 'Yes' or 'No'."
        )

        instances.append({
            "id": f"{TASK_NAME}_d{difficulty}_{i:04d}",
            "task": TASK_NAME,
            "prompt": prompt,
            "answer": answer,
            "difficulty": difficulty,
            "metadata": {
                "n_vars": n_vars,
                "n_clauses": n_clauses,
                "alpha": n_clauses / n_vars,
                "is_satisfiable": is_sat,
            },
        })

    return instances
