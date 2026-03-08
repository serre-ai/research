"""B7: 3-SAT at Phase Transition (Intractability Gap).

Task: Determine satisfiability of a 3-SAT formula near the phase transition
(clause-to-variable ratio alpha ~ 4.27).

Complexity: 3-SAT is NP-complete.
Prediction: Accuracy degrades sharply at alpha ~ 4.27. CoT provides no
systematic improvement at the phase transition.
"""

import random as _random
import itertools

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
) -> tuple[bool, list[bool] | None]:
    """Check satisfiability by exhaustive enumeration (for small n).

    For larger n, uses DPLL-style backtracking.
    Returns (is_sat, assignment_or_None).
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


def _dpll_solve(
    clauses: list[list[int]], n_vars: int
) -> tuple[bool, list[bool] | None]:
    """Simple DPLL SAT solver."""
    assignment: dict[int, bool] = {}

    def _propagate(
        clauses: list[list[int]], assignment: dict[int, bool]
    ) -> list[list[int]] | None:
        """Unit propagation. Returns simplified clauses or None if conflict."""
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
                    return None  # Conflict
                if len(new_clause) == 1:
                    # Unit clause: force assignment
                    lit = new_clause[0]
                    var = abs(lit)
                    assignment[var] = lit > 0
                    changed = True
                else:
                    new_clauses.append(new_clause)

            clauses = new_clauses

        return clauses

    def _solve(
        clauses: list[list[int]], assignment: dict[int, bool]
    ) -> bool:
        result = _propagate(clauses, assignment)
        if result is None:
            return False
        clauses = result

        if len(clauses) == 0:
            return True

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
            return True

        # Try True
        saved = dict(assignment)
        assignment[unassigned] = True
        if _solve(list(clauses), assignment):
            return True

        # Try False
        assignment.clear()
        assignment.update(saved)
        assignment[unassigned] = False
        if _solve(list(clauses), assignment):
            return True

        assignment.clear()
        assignment.update(saved)
        return False

    if _solve(list(clauses), assignment):
        result_assignment = [
            assignment.get(v, False) for v in range(1, n_vars + 1)
        ]
        return True, result_assignment
    return False, None


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
    n_clauses = round(ALPHA * n_vars)

    instances: list[dict] = []
    for i in range(n_instances):
        clauses = _generate_3sat_formula(rng, n_vars, n_clauses)

        is_sat, assignment = _check_satisfiability(clauses, n_vars)
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
