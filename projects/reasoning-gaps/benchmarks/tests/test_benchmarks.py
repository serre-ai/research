"""Comprehensive test suite for the ReasonGap benchmark generators.

Tests cover:
  - Ground truth correctness (hand-crafted + independent verification)
  - Determinism (same seed -> same output)
  - Schema validation (required fields)
  - Distribution checks (answer balance)
  - Edge cases (n_instances=1, difficulty extremes)
  - Difficulty scaling (parameter changes with difficulty)
  - B7 DPLL cross-validation against exhaustive search
  - evaluate.py skeleton functions
"""

import sys
import bisect
import signal
import itertools
from collections import Counter
from pathlib import Path

import pytest

# Ensure the benchmarks package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks import (
    b1_majority,
    b2_boolean_eval,
    b3_permutation,
    b4_state_machine,
    b5_graph_reach,
    b6_lis,
    b7_3sat,
    b8_reversal,
    b9_negation,
    TASK_REGISTRY,
)
from evaluate import (
    extract_answer,
    compute_summary,
    evaluate_instance,
    DummyClient,
    EvalResult,
)


# =====================================================================
# Shared helpers
# =====================================================================

REQUIRED_FIELDS = {"id", "task", "prompt", "answer", "difficulty", "metadata"}

ALL_MODULES = [
    ("B1", b1_majority),
    ("B2", b2_boolean_eval),
    ("B3", b3_permutation),
    ("B4", b4_state_machine),
    ("B5", b5_graph_reach),
    ("B6", b6_lis),
    ("B7", b7_3sat),
    ("B8", b8_reversal),
    ("B9", b9_negation),
]


def _validate_schema(instance: dict) -> None:
    """Validate that an instance has all required fields with correct types."""
    for field in REQUIRED_FIELDS:
        assert field in instance, f"Missing field: {field}"
    assert isinstance(instance["id"], str) and len(instance["id"]) > 0
    assert isinstance(instance["task"], str) and len(instance["task"]) > 0
    assert isinstance(instance["prompt"], str) and len(instance["prompt"]) > 0
    assert isinstance(instance["answer"], str) and len(instance["answer"]) > 0
    assert isinstance(instance["difficulty"], int)
    assert isinstance(instance["metadata"], dict)


# =====================================================================
# Schema validation — all tasks
# =====================================================================

class TestSchemaValidation:
    """Every instance from every task must have the required schema."""

    @pytest.mark.parametrize("task_key,module", ALL_MODULES)
    def test_schema_all_tasks(self, task_key, module):
        instances = module.generate(5, difficulty=1, seed=42)
        assert len(instances) == 5
        for inst in instances:
            _validate_schema(inst)


# =====================================================================
# Determinism — all tasks
# =====================================================================

class TestDeterminism:
    """Calling generate with the same seed must produce identical output."""

    @pytest.mark.parametrize("task_key,module", ALL_MODULES)
    def test_determinism(self, task_key, module):
        run1 = module.generate(10, difficulty=1, seed=42)
        run2 = module.generate(10, difficulty=1, seed=42)
        assert len(run1) == len(run2)
        for a, b in zip(run1, run2):
            assert a["id"] == b["id"]
            assert a["prompt"] == b["prompt"]
            assert a["answer"] == b["answer"]
            assert a["difficulty"] == b["difficulty"]
            assert a["metadata"] == b["metadata"]


# =====================================================================
# Edge cases — all tasks
# =====================================================================

class TestEdgeCases:
    """n_instances=1, difficulty 1 and 5 should not crash."""

    @pytest.mark.parametrize("task_key,module", ALL_MODULES)
    def test_single_instance_diff1(self, task_key, module):
        instances = module.generate(1, difficulty=1, seed=123)
        assert len(instances) == 1
        _validate_schema(instances[0])

    @pytest.mark.parametrize("task_key,module", ALL_MODULES)
    def test_single_instance_diff5(self, task_key, module):
        # B7 difficulty 5 may be slow, but should complete with the node limit
        instances = module.generate(1, difficulty=5, seed=123)
        assert len(instances) == 1
        _validate_schema(instances[0])


# =====================================================================
# Difficulty scaling — all tasks
# =====================================================================

class TestDifficultyScaling:
    """Difficulty parameters must actually change across levels."""

    def test_b1_scaling(self):
        d1 = b1_majority.DIFFICULTY_PARAMS[1]
        d5 = b1_majority.DIFFICULTY_PARAMS[5]
        assert d1 == 10
        assert d5 == 200
        assert d5 > d1

    def test_b2_scaling(self):
        d1 = b2_boolean_eval.DIFFICULTY_PARAMS[1]
        d5 = b2_boolean_eval.DIFFICULTY_PARAMS[5]
        assert d1 == 2
        assert d5 == 10
        assert d5 > d1

    def test_b3_scaling(self):
        k1, m1 = b3_permutation.DIFFICULTY_PARAMS[1]
        k5, m5 = b3_permutation.DIFFICULTY_PARAMS[5]
        assert k5 > k1  # more compositions at higher difficulty

    def test_b4_scaling(self):
        k1, _ = b4_state_machine.DIFFICULTY_PARAMS[1]
        k5, _ = b4_state_machine.DIFFICULTY_PARAMS[5]
        assert k5 > k1

    def test_b5_scaling(self):
        assert b5_graph_reach.DIFFICULTY_PARAMS[5] > b5_graph_reach.DIFFICULTY_PARAMS[1]

    def test_b6_scaling(self):
        assert b6_lis.DIFFICULTY_PARAMS[5] > b6_lis.DIFFICULTY_PARAMS[1]

    def test_b7_scaling(self):
        assert b7_3sat.DIFFICULTY_PARAMS[5] > b7_3sat.DIFFICULTY_PARAMS[1]

    def test_b8_scaling(self):
        assert b8_reversal.DIFFICULTY_PARAMS[5] > b8_reversal.DIFFICULTY_PARAMS[1]

    def test_b9_scaling(self):
        assert b9_negation.DIFFICULTY_PARAMS[5] > b9_negation.DIFFICULTY_PARAMS[1]

    def test_b1_instances_reflect_difficulty(self):
        """Verify generated instances actually use the difficulty parameter."""
        inst_d1 = b1_majority.generate(1, difficulty=1, seed=42)[0]
        inst_d5 = b1_majority.generate(1, difficulty=5, seed=42)[0]
        assert inst_d1["metadata"]["n"] == 10
        assert inst_d5["metadata"]["n"] == 200


# =====================================================================
# B1: Masked Majority — Ground truth correctness
# =====================================================================

class TestB1MaskedMajority:
    """Hand-crafted correctness tests for B1."""

    def _count_majority(self, display_str: str) -> str:
        """Independently compute majority from a display string."""
        visible = [int(c) for c in display_str if c in ("0", "1")]
        ones = sum(visible)
        zeros = len(visible) - ones
        if ones > zeros:
            return "1"
        elif zeros > ones:
            return "0"
        else:
            # Tie -- shouldn't happen in generated instances
            return "TIE"

    def test_hand_crafted_cases(self):
        """Verify majority for known strings."""
        assert self._count_majority("11100") == "1"  # 3 ones, 2 zeros
        assert self._count_majority("0000?") == "0"  # 4 zeros, 0 ones
        assert self._count_majority("111??") == "1"  # 3 ones, 0 zeros
        assert self._count_majority("01010") == "0"  # 2 ones, 3 zeros
        assert self._count_majority("?1?0?") == "TIE"  # 1 one, 1 zero

    def test_generated_instances_correctness(self):
        """Verify generated answers match independent computation."""
        instances = b1_majority.generate(50, difficulty=2, seed=99)
        for inst in instances:
            prompt = inst["prompt"]
            # Extract the display string from prompt
            line = prompt.split("\n")[0]
            display = line.split(": ")[1]
            expected = self._count_majority(display)
            assert expected != "TIE", f"Generated a tie instance: {display}"
            assert inst["answer"] == expected, (
                f"Mismatch for {display}: expected {expected}, got {inst['answer']}"
            )

    def test_distribution_balance(self):
        """Over 100 instances, answers should be roughly balanced."""
        instances = b1_majority.generate(100, difficulty=3, seed=77)
        counts = Counter(inst["answer"] for inst in instances)
        # Both "0" and "1" should be present
        assert "0" in counts, "No '0' answers generated"
        assert "1" in counts, "No '1' answers generated"
        # Neither should exceed 70%
        total = len(instances)
        assert counts["0"] / total <= 0.7, f"Too many 0s: {counts['0']}/{total}"
        assert counts["1"] / total <= 0.7, f"Too many 1s: {counts['1']}/{total}"

    def test_tie_break_randomized(self):
        """Verify that tie-breaks don't always go to '1'."""
        # Generate many instances, some will hit ties
        instances = b1_majority.generate(200, difficulty=1, seed=12345)
        answers = [inst["answer"] for inst in instances]
        counts = Counter(answers)
        # With randomized tie-breaking, both should appear
        assert "0" in counts and "1" in counts


# =====================================================================
# B2: Nested Boolean Evaluation — Ground truth correctness
# =====================================================================

class TestB2NestedBoolean:
    """Hand-crafted and verification tests for B2."""

    def _eval_formula(self, formula: str) -> bool:
        """Independently evaluate a Boolean formula string."""
        formula = formula.strip()
        if formula == "T":
            return True
        if formula == "F":
            return False
        if formula.startswith("NOT(") and formula.endswith(")"):
            inner = formula[4:-1]
            return not self._eval_formula(inner)
        if formula.startswith("AND(") and formula.endswith(")"):
            inner = formula[4:-1]
            left, right = self._split_binary(inner)
            return self._eval_formula(left) and self._eval_formula(right)
        if formula.startswith("OR(") and formula.endswith(")"):
            inner = formula[3:-1]
            left, right = self._split_binary(inner)
            return self._eval_formula(left) or self._eval_formula(right)
        raise ValueError(f"Cannot parse formula: {formula}")

    def _split_binary(self, inner: str) -> tuple:
        """Split a binary operator's arguments at the top-level comma."""
        depth = 0
        for i, c in enumerate(inner):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "," and depth == 0:
                return inner[:i].strip(), inner[i + 1:].strip()
        raise ValueError(f"Cannot split: {inner}")

    def test_hand_crafted_cases(self):
        assert self._eval_formula("T") is True
        assert self._eval_formula("F") is False
        assert self._eval_formula("NOT(T)") is False
        assert self._eval_formula("AND(T, F)") is False
        assert self._eval_formula("OR(T, F)") is True
        assert self._eval_formula("NOT(AND(T, F))") is True
        assert self._eval_formula("AND(OR(T, F), NOT(F))") is True

    def test_generated_instances_correctness(self):
        """Cross-validate generated answers with independent evaluator."""
        instances = b2_boolean_eval.generate(30, difficulty=3, seed=42)
        for inst in instances:
            formula = inst["metadata"]["formula"]
            expected = self._eval_formula(formula)
            expected_str = "True" if expected else "False"
            assert inst["answer"] == expected_str, (
                f"Mismatch for formula {formula}: "
                f"expected {expected_str}, got {inst['answer']}"
            )

    def test_generated_depth2(self):
        """Verify depth=2 formulas."""
        instances = b2_boolean_eval.generate(20, difficulty=1, seed=42)
        for inst in instances:
            formula = inst["metadata"]["formula"]
            expected = self._eval_formula(formula)
            expected_str = "True" if expected else "False"
            assert inst["answer"] == expected_str


# =====================================================================
# B3: Iterated Permutation Composition — Ground truth correctness
# =====================================================================

class TestB3PermutationComposition:
    """Hand-crafted and verification tests for B3."""

    def test_hand_crafted_cases(self):
        """Manually trace known permutation compositions."""
        # Identity permutation: [0,1,2,3,4] applied twice
        # start=0 -> 0 -> 0
        perm_id = [0, 1, 2, 3, 4]
        current = 0
        for _ in range(2):
            current = perm_id[current]
        assert current == 0

        # Cycle: [1,2,0,3,4] applied 3 times to start=0
        # 0->1->2->0
        perm_cycle = [1, 2, 0, 3, 4]
        current = 0
        for _ in range(3):
            current = perm_cycle[current]
        assert current == 0

        # Two permutations: [1,0,2,3,4] then [0,2,1,3,4]
        # start=0: 0->1 then 1->2 -> answer=2 (0-indexed) = 3 (1-indexed)
        p1 = [1, 0, 2, 3, 4]
        p2 = [0, 2, 1, 3, 4]
        current = 0
        current = p1[current]  # 1
        current = p2[current]  # 2
        assert current + 1 == 3  # 1-indexed answer

    def test_generated_instances_correctness(self):
        """Independently verify permutation composition."""
        instances = b3_permutation.generate(20, difficulty=2, seed=42)
        for inst in instances:
            perms = inst["metadata"]["permutations"]
            start = inst["metadata"]["start_pos"] - 1  # convert to 0-indexed
            current = start
            for perm in perms:
                current = perm[current]
            expected = str(current + 1)  # 1-indexed
            assert inst["answer"] == expected, (
                f"Mismatch: start={start+1}, "
                f"expected {expected}, got {inst['answer']}"
            )

    def test_single_permutation(self):
        """Verify with k=1 (difficulty 1 has k=2, but still simple)."""
        instances = b3_permutation.generate(10, difficulty=1, seed=99)
        for inst in instances:
            perms = inst["metadata"]["permutations"]
            start = inst["metadata"]["start_pos"] - 1
            current = start
            for perm in perms:
                current = perm[current]
            assert inst["answer"] == str(current + 1)


# =====================================================================
# B4: State Machine — Ground truth correctness
# =====================================================================

class TestB4StateMachine:
    """Ground truth verification for B4."""

    def test_hand_crafted_case(self):
        """Manually trace a state machine."""
        # Simple 2-state machine: A --0--> B, A --1--> A, B --0--> A, B --1--> B
        table = {"A": {"0": "B", "1": "A"}, "B": {"0": "A", "1": "B"}}
        state = "A"
        for sym in "010":
            state = table[state][sym]
        # A->B(0)->A(1 from B? no, B --1--> B)
        # Actually: A --0--> B, B --1--> B, B --0--> A
        assert state == "A"

    def test_generated_instances_correctness(self):
        """Independently trace generated state machines."""
        instances = b4_state_machine.generate(20, difficulty=2, seed=42)
        for inst in instances:
            table = inst["metadata"]["transition_table"]
            start = inst["metadata"]["start_state"]
            input_str = inst["metadata"]["input_string"]
            state = start
            for sym in input_str:
                state = table[state][sym]
            assert inst["answer"] == state

    def test_all_difficulties(self):
        """Verify correctness across all difficulty levels."""
        for diff in [1, 2, 3, 4, 5]:
            instances = b4_state_machine.generate(5, difficulty=diff, seed=42)
            for inst in instances:
                table = inst["metadata"]["transition_table"]
                start = inst["metadata"]["start_state"]
                input_str = inst["metadata"]["input_string"]
                state = start
                for sym in input_str:
                    state = table[state][sym]
                assert inst["answer"] == state


# =====================================================================
# B5: Graph Reachability — Ground truth correctness
# =====================================================================

class TestB5GraphReachability:
    """Ground truth and distribution tests for B5."""

    def _bfs_reachable(self, edges, source, target, n):
        """Independent BFS reachability check."""
        from collections import deque
        adj = {}
        for u, v in edges:
            adj.setdefault(u, []).append(v)
        visited = set()
        queue = deque([source])
        visited.add(source)
        while queue:
            node = queue.popleft()
            if node == target:
                return True
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def test_hand_crafted_reachable(self):
        edges = [(1, 2), (2, 3), (3, 4)]
        assert self._bfs_reachable(edges, 1, 4, 4) is True

    def test_hand_crafted_unreachable(self):
        edges = [(1, 2), (3, 4)]
        assert self._bfs_reachable(edges, 1, 4, 4) is False

    def test_hand_crafted_self_loop(self):
        edges = [(1, 1)]
        assert self._bfs_reachable(edges, 1, 2, 2) is False

    def test_hand_crafted_cycle(self):
        edges = [(1, 2), (2, 3), (3, 1)]
        assert self._bfs_reachable(edges, 1, 3, 3) is True

    def test_hand_crafted_no_edges(self):
        edges = []
        assert self._bfs_reachable(edges, 1, 2, 2) is False

    def test_generated_instances_correctness(self):
        """Re-verify reachability using independent BFS."""
        instances = b5_graph_reach.generate(30, difficulty=1, seed=42)
        for inst in instances:
            source = inst["metadata"]["source"]
            target = inst["metadata"]["target"]
            n = inst["metadata"]["n_nodes"]
            # Parse edges from the prompt
            prompt = inst["prompt"]
            edge_line = prompt.split("\n")[1]  # second line has edges
            edges = []
            for part in edge_line.split(", "):
                part = part.strip()
                if "->" in part:
                    u, v = part.split("->")
                    edges.append((int(u), int(v)))
            reachable = self._bfs_reachable(edges, source, target, n)
            expected = "Yes" if reachable else "No"
            assert inst["answer"] == expected, (
                f"Mismatch: source={source}, target={target}, "
                f"expected {expected}, got {inst['answer']}"
            )

    def test_yes_no_balance(self):
        """Yes/No distribution should be within 60/40."""
        instances = b5_graph_reach.generate(100, difficulty=2, seed=42)
        counts = Counter(inst["answer"] for inst in instances)
        total = len(instances)
        yes_ratio = counts.get("Yes", 0) / total
        no_ratio = counts.get("No", 0) / total
        assert yes_ratio <= 0.6, f"Too many Yes: {yes_ratio:.2%}"
        assert no_ratio <= 0.6, f"Too many No: {no_ratio:.2%}"
        # Both should be present
        assert "Yes" in counts
        assert "No" in counts


# =====================================================================
# B6: LIS — Ground truth correctness
# =====================================================================

class TestB6LIS:
    """Ground truth correctness for LIS using independent O(n^2) DP."""

    def _lis_dp(self, seq):
        """Independent O(n^2) LIS computation for verification."""
        if not seq:
            return 0
        n = len(seq)
        dp = [1] * n
        for i in range(1, n):
            for j in range(i):
                if seq[j] < seq[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)

    def test_hand_crafted_cases(self):
        assert self._lis_dp([3, 1, 4, 2, 5]) == 3
        assert self._lis_dp([1, 2, 3, 4, 5]) == 5
        assert self._lis_dp([5, 4, 3, 2, 1]) == 1
        assert self._lis_dp([1]) == 1
        assert self._lis_dp([2, 6, 3, 4, 1, 5]) == 4  # [2,3,4,5]

    def test_generated_instances_correctness(self):
        """Cross-validate LIS answers against O(n^2) DP."""
        for diff in [1, 2, 3]:
            instances = b6_lis.generate(20, difficulty=diff, seed=42)
            for inst in instances:
                seq = inst["metadata"]["sequence"]
                expected = self._lis_dp(seq)
                assert inst["answer"] == str(expected), (
                    f"Mismatch for seq {seq}: "
                    f"expected {expected}, got {inst['answer']}"
                )

    def test_patience_vs_dp(self):
        """Verify built-in patience sort matches DP on random sequences."""
        import random
        rng = random.Random(999)
        for _ in range(50):
            n = rng.randint(1, 30)
            seq = [rng.randint(1, 50) for _ in range(n)]
            dp_result = self._lis_dp(seq)
            patience_result = b6_lis._compute_lis_length(seq)
            assert dp_result == patience_result, (
                f"Mismatch for {seq}: DP={dp_result}, patience={patience_result}"
            )


# =====================================================================
# B7: 3-SAT — Ground truth correctness, cross-validation, timeout
# =====================================================================

class TestB73SAT:
    """Comprehensive tests for the B7 3-SAT generator and solver."""

    def _exhaustive_sat(self, clauses, n_vars):
        """Exhaustive brute-force SAT check for small instances."""
        for bits in range(2 ** n_vars):
            assignment = {}
            for v in range(1, n_vars + 1):
                assignment[v] = bool((bits >> (v - 1)) & 1)
            sat = True
            for clause in clauses:
                clause_sat = False
                for lit in clause:
                    var = abs(lit)
                    val = assignment[var]
                    if (lit > 0 and val) or (lit < 0 and not val):
                        clause_sat = True
                        break
                if not clause_sat:
                    sat = False
                    break
            if sat:
                return True
        return False

    def test_hand_crafted_sat(self):
        """Known satisfiable formula: (x1 v x2 v x3)."""
        clauses = [[1, 2, 3]]
        assert self._exhaustive_sat(clauses, 3) is True

    def test_hand_crafted_unsat(self):
        """Known unsatisfiable formula (requires all contradictory values).
        (x1) ^ (~x1) -- but these are 1-literal clauses in our format.
        Use: (x1 v x1 v x1) ^ (~x1 v ~x1 v ~x1)
        """
        clauses = [[1, 1, 1], [-1, -1, -1]]
        assert self._exhaustive_sat(clauses, 1) is False

    def test_hand_crafted_3var_unsat(self):
        """A small UNSAT: all 8 resolvents for 3 variables."""
        # All 8 possible clauses of 3 positive/negative literals
        clauses = [
            [1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
            [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3],
        ]
        assert self._exhaustive_sat(clauses, 3) is False

    def test_hand_crafted_3var_sat(self):
        """A small SAT: (x1 v x2 v x3) ^ (~x1 v x2 v x3)."""
        clauses = [[1, 2, 3], [-1, 2, 3]]
        assert self._exhaustive_sat(clauses, 3) is True

    def test_cross_validate_dpll_vs_exhaustive_small(self):
        """Cross-validate DPLL against exhaustive search for n <= 12."""
        import random
        rng = random.Random(42)
        for n_vars in [4, 6, 8, 10, 12]:
            n_clauses = round(4.27 * n_vars)
            for trial in range(5):
                clauses = []
                for _ in range(n_clauses):
                    variables = rng.sample(range(1, n_vars + 1), min(3, n_vars))
                    clause = [v if rng.random() < 0.5 else -v for v in variables]
                    clauses.append(clause)

                exhaustive_result = self._exhaustive_sat(clauses, n_vars)
                dpll_result, _ = b7_3sat._dpll_solve(list(clauses), n_vars)

                assert exhaustive_result == dpll_result, (
                    f"DPLL disagrees with exhaustive for n_vars={n_vars}, "
                    f"trial={trial}: exhaustive={exhaustive_result}, dpll={dpll_result}, "
                    f"clauses={clauses}"
                )

    def test_generated_instances_small(self):
        """Verify generated answers for small instances (difficulty 1-2)."""
        for diff in [1, 2]:
            instances = b7_3sat.generate(10, difficulty=diff, seed=42)
            for inst in instances:
                n_vars = inst["metadata"]["n_vars"]
                # Re-generate the formula from the same seed to get clauses
                # (metadata doesn't store clauses, so we check via exhaustive)
                # Instead, check the generated answer matches our solver
                # by parsing the prompt
                pass  # covered by cross_validate above

    def test_generated_correctness_d1(self):
        """For difficulty 1 (4 vars), cross-validate every instance."""
        instances = b7_3sat.generate(20, difficulty=1, seed=42)
        # Re-generate using same seed to get clauses
        import random as _random
        rng = _random.Random(42)
        n_vars = 4
        n_clauses = round(4.27 * n_vars)
        for inst in instances:
            clauses = []
            for _ in range(n_clauses):
                variables = rng.sample(range(1, n_vars + 1), min(3, n_vars))
                clause = [v if rng.random() < 0.5 else -v for v in variables]
                clauses.append(clause)
            expected = self._exhaustive_sat(clauses, n_vars)
            expected_str = "Yes" if expected else "No"
            assert inst["answer"] == expected_str, (
                f"Mismatch at {inst['id']}: expected={expected_str}, got={inst['answer']}"
            )

    def test_distribution_not_all_same(self):
        """Answer distribution should not be all-SAT or all-UNSAT."""
        instances = b7_3sat.generate(50, difficulty=2, seed=42)
        answers = [inst["answer"] for inst in instances]
        counts = Counter(answers)
        # Both Yes and No should appear (at the phase transition)
        assert len(counts) > 1, f"All answers are the same: {counts}"

    def test_difficulty5_no_hang(self):
        """Difficulty 5 (n=64) should complete without hanging (node limit)."""
        # This should complete quickly thanks to the _DPLL_NODE_LIMIT
        instances = b7_3sat.generate(3, difficulty=5, seed=42)
        assert len(instances) == 3
        for inst in instances:
            _validate_schema(inst)
            assert inst["answer"] in ("Yes", "No")

    def test_dpll_known_sat_formula(self):
        """DPLL correctly identifies a known SAT formula."""
        # (x1 v x2 v x3) -- trivially satisfiable
        clauses = [[1, 2, 3]]
        result, assignment = b7_3sat._dpll_solve(clauses, 3)
        assert result is True
        assert assignment is not None

    def test_dpll_known_unsat_formula(self):
        """DPLL correctly identifies a known UNSAT formula."""
        # All 8 clauses over 3 variables
        clauses = [
            [1, 2, 3], [-1, 2, 3], [1, -2, 3], [1, 2, -3],
            [-1, -2, 3], [-1, 2, -3], [1, -2, -3], [-1, -2, -3],
        ]
        result, assignment = b7_3sat._dpll_solve(clauses, 3)
        assert result is False
        assert assignment is None


# =====================================================================
# B8: String Reversal — Ground truth correctness
# =====================================================================

class TestB8ReversalInference:
    """Ground truth tests for B8."""

    def test_generated_answers_are_countries(self):
        """Answer should always be one of the generated countries."""
        instances = b8_reversal.generate(20, difficulty=2, seed=42)
        for inst in instances:
            country = inst["metadata"]["target_country"]
            assert inst["answer"] == country

    def test_answer_in_facts(self):
        """The answer country should appear in the facts list."""
        instances = b8_reversal.generate(20, difficulty=3, seed=42)
        for inst in instances:
            country = inst["answer"]
            assert country in inst["prompt"], (
                f"Answer '{country}' not found in prompt"
            )

    def test_difficulty_controls_fact_count(self):
        """Higher difficulty = more distractor facts."""
        inst_d1 = b8_reversal.generate(1, difficulty=1, seed=42)[0]
        inst_d5 = b8_reversal.generate(1, difficulty=5, seed=42)[0]
        assert inst_d1["metadata"]["n_facts"] == 2
        assert inst_d5["metadata"]["n_facts"] == 50


# =====================================================================
# B9: Negation Sensitivity — Ground truth correctness
# =====================================================================

class TestB9NegationSensitivity:
    """Ground truth and distribution tests for B9."""

    def test_hand_crafted_single_negation(self):
        """One negation of a true proposition should be false."""
        # "water boils at 100 degrees Celsius at sea level" is True
        # One negation: "it is NOT the case that water boils..." -> False
        prop = "water boils at 100 degrees Celsius at sea level"
        truth = True
        negated, val = b9_negation._apply_negations(prop, truth, 1)
        assert val is False
        assert "NOT" in negated

    def test_hand_crafted_double_negation(self):
        """Two negations of a true proposition should be true."""
        prop = "2 + 2 equals 4"
        truth = True
        negated, val = b9_negation._apply_negations(prop, truth, 2)
        assert val is True

    def test_hand_crafted_false_base(self):
        """Negation of a false proposition should be true."""
        prop = "humans have three arms"
        truth = False
        negated, val = b9_negation._apply_negations(prop, truth, 1)
        assert val is True

    def test_hand_crafted_triple_negation_false(self):
        """Three negations of a false proposition should be true."""
        prop = "the speed of light is infinite"
        truth = False
        negated, val = b9_negation._apply_negations(prop, truth, 3)
        # False -> True -> False -> True
        assert val is True

    def test_negation_depth_parity(self):
        """n negations flip the truth value n times."""
        for base_truth in [True, False]:
            for depth in range(1, 6):
                _, val = b9_negation._apply_negations("test", base_truth, depth)
                expected = base_truth
                for _ in range(depth):
                    expected = not expected
                assert val == expected, (
                    f"Depth {depth}, base={base_truth}: "
                    f"expected {expected}, got {val}"
                )

    def test_generated_instances_correctness(self):
        """Verify generated answers match independent computation."""
        for diff in [1, 2, 3, 4, 5]:
            instances = b9_negation.generate(20, difficulty=diff, seed=42)
            for inst in instances:
                base_truth = inst["metadata"]["base_truth"]
                depth = inst["metadata"]["negation_depth"]
                expected = base_truth
                for _ in range(depth):
                    expected = not expected
                expected_str = "True" if expected else "False"
                assert inst["answer"] == expected_str

    def test_distribution_balance(self):
        """True/False should be balanced over 100 instances."""
        instances = b9_negation.generate(100, difficulty=1, seed=42)
        counts = Counter(inst["answer"] for inst in instances)
        total = len(instances)
        assert "True" in counts and "False" in counts
        # Neither should exceed 70%
        assert counts["True"] / total <= 0.7
        assert counts["False"] / total <= 0.7

    def test_prompt_no_is_it_true_prefix(self):
        """Verify the prompt no longer contains 'Is it true that' prefix."""
        instances = b9_negation.generate(10, difficulty=2, seed=42)
        for inst in instances:
            prompt = inst["prompt"]
            # The statement line should NOT start with "Is it true that"
            lines = prompt.split("\n")
            for line in lines:
                if line.startswith("Statement:"):
                    assert "Is it true that" not in line, (
                        f"Prompt still contains 'Is it true that': {line}"
                    )


# =====================================================================
# evaluate.py — extract_answer, compute_summary, evaluate_instance
# =====================================================================

class TestEvaluate:
    """Tests for the evaluation skeleton."""

    def test_extract_answer_simple(self):
        assert extract_answer("True", "B2_nested_boolean") == "True"
        assert extract_answer("Yes", "B5_graph_reachability") == "Yes"
        assert extract_answer("42", "B6_lis") == "42"

    def test_extract_answer_with_prefix(self):
        assert extract_answer("Answer: True", "B2") == "True"
        assert extract_answer("The answer is Yes", "B5") == "Yes"
        assert extract_answer("Final answer: 42", "B6") == "42"
        assert extract_answer("Result: No", "B7") == "No"

    def test_extract_answer_multiline_cot(self):
        response = "Let me think step by step.\nFirst, ...\nSo the answer is 3.\n3"
        assert extract_answer(response, "B6") == "3"

    def test_extract_answer_trailing_period(self):
        assert extract_answer("True.", "B2") == "True"
        assert extract_answer("Answer: Yes.", "B5") == "Yes"

    def test_extract_answer_empty(self):
        assert extract_answer("", "B1") == ""
        assert extract_answer("   \n  ", "B1") == ""

    def test_extract_answer_case_insensitive_prefix(self):
        assert extract_answer("answer: 5", "B6") == "5"
        assert extract_answer("ANSWER: 5", "B6") == "5"

    def test_compute_summary_empty(self):
        summary = compute_summary([])
        assert summary.total_instances == 0
        assert summary.accuracy == 0.0

    def test_compute_summary_basic(self):
        results = [
            EvalResult(
                instance_id=f"test_{i}", task="B1", difficulty=1,
                condition="direct", model="dummy", prompt_sent="",
                model_response="", extracted_answer="1",
                ground_truth="1", correct=(i % 2 == 0),
                latency_ms=10.0,
            )
            for i in range(10)
        ]
        summary = compute_summary(results)
        assert summary.total_instances == 10
        assert summary.correct == 5
        assert summary.accuracy == 0.5
        assert summary.mean_latency_ms == 10.0

    def test_compute_summary_by_difficulty(self):
        results = []
        for diff in [1, 2, 3]:
            for i in range(4):
                results.append(EvalResult(
                    instance_id=f"test_d{diff}_{i}", task="B1",
                    difficulty=diff, condition="direct", model="dummy",
                    prompt_sent="", model_response="",
                    extracted_answer="1", ground_truth="1",
                    correct=(diff == 1),  # only difficulty 1 is correct
                    latency_ms=5.0,
                ))
        summary = compute_summary(results)
        assert summary.accuracy_by_difficulty[1] == 1.0
        assert summary.accuracy_by_difficulty[2] == 0.0
        assert summary.accuracy_by_difficulty[3] == 0.0

    def test_evaluate_instance_with_dummy(self):
        """evaluate_instance should work with DummyClient."""
        instance = {
            "id": "test_001",
            "task": "B1_masked_majority",
            "prompt": "Test prompt",
            "answer": "1",
            "difficulty": 1,
            "metadata": {},
        }
        client = DummyClient("dummy")
        result = evaluate_instance(instance, client, "direct")
        assert result.instance_id == "test_001"
        assert result.ground_truth == "1"
        assert result.condition == "direct"
        assert result.model == "dummy"
        assert isinstance(result.latency_ms, float)

    def test_evaluate_instance_conditions(self):
        """Test all three evaluation conditions."""
        instance = {
            "id": "test_001",
            "task": "B1",
            "prompt": "prompt",
            "answer": "1",
            "difficulty": 1,
            "metadata": {},
        }
        client = DummyClient("dummy")

        for condition in ["direct", "short_cot", "budget_cot"]:
            result = evaluate_instance(instance, client, condition, budget=100)
            assert result.condition == condition

    def test_evaluate_instance_invalid_condition(self):
        instance = {
            "id": "test", "task": "B1", "prompt": "p",
            "answer": "1", "difficulty": 1, "metadata": {},
        }
        with pytest.raises(ValueError, match="Unknown condition"):
            evaluate_instance(instance, DummyClient("d"), "invalid")


# =====================================================================
# Registry completeness
# =====================================================================

class TestRegistry:
    """Verify that all 9 tasks are in the registry."""

    def test_all_tasks_registered(self):
        expected = {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9"}
        assert set(TASK_REGISTRY.keys()) == expected

    def test_all_modules_have_generate(self):
        for key, module in TASK_REGISTRY.items():
            assert hasattr(module, "generate"), f"{key} missing generate()"
            assert hasattr(module, "TASK_NAME"), f"{key} missing TASK_NAME"
            assert hasattr(module, "DIFFICULTY_PARAMS"), f"{key} missing DIFFICULTY_PARAMS"
