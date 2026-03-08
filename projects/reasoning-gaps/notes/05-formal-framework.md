# Formal Framework: Reasoning Gap Taxonomy

## Core Definitions

### Definition 1: Reasoning Task
A *reasoning task* is a family of functions F = {f_n : Σ^n → Σ*}_{n ∈ ℕ} parameterized by input size n, with a decidable correctness criterion.

### Definition 2: Model Capability Class
Given a model class M (e.g., log-precision transformers of depth d), the *capability class* C(M) is the set of reasoning tasks F such that M solves F with probability ≥ 2/3 on uniformly random instances for all n.

For standard transformer variants (from Merrill, Sabharwal, Strobl et al.):
- C(T_const) ⊆ AC⁰  [constant-bit precision, no CoT]
- C(T_log)   ⊆ TC⁰  [log-precision, no CoT]
- C(T_log + CoT(k))   ⊆ L     [log-precision + O(log n) CoT steps]
- C(T_log + CoT(n))   ⊇ REG   [log-precision + O(n) CoT steps]
- C(T_log + CoT(n^c)) = P     [log-precision + poly(n) CoT steps]

### Definition 3: Reasoning Gap
A model class M has a *reasoning gap* on task F if:
1. F has a polynomial-time solution (F ∈ P)
2. F ∉ C(M) — the task is outside the model's capability class
3. The model's accuracy on F decreases systematically with n (not random failure)

A reasoning gap is *structural* if it follows from complexity-theoretic bounds on C(M). It is *empirical* if observed experimentally without a known proof.

### Definition 4: Gap Closure
A technique T (e.g., CoT, tool use) *closes* a gap on F for model M if F ∈ C(M + T). A technique *partially closes* a gap if it improves accuracy but does not achieve constant accuracy as n grows.

## Reasoning Gap Taxonomy

Six gap types, ordered by the complexity boundary they reflect:

### Type 1: Sensitivity Gap (AC⁰ boundary)
- **Boundary**: Problems requiring high boolean sensitivity, outside AC⁰
- **Examples**: Parity, majority on subsets, exact counting
- **Formal**: Functions with boolean sensitivity s(f) = Ω(n) are not in AC⁰ (Linial-Mansour-Nisan)
- **Empirical signature**: Accuracy → 0 as n grows; errors correlate with input sensitivity
- **CoT prediction**: Even short CoT (O(log n) steps) closes this gap for MAJORITY-type problems. Parity requires Ω(n) steps.
- **Learnability caveat**: Even if expressible, high-sensitivity functions may be unlearnable (Hahn & Rofin 2024)

### Type 2: Depth Gap (TC⁰ boundary)
- **Boundary**: Problems requiring circuit depth > O(1), outside TC⁰ (conditional on TC⁰ ≠ NC¹)
- **Examples**: Boolean formula evaluation, word problem for S₅, arbitrary CFL parsing
- **Formal**: If TC⁰ ≠ NC¹, these problems require super-constant depth
- **Empirical signature**: Accuracy degrades with formula depth / nesting level
- **CoT prediction**: O(log n) CoT steps should close this gap (sufficient to simulate NC¹)
- **Key test**: Performance should degrade with nesting depth, not problem size per se

### Type 3: Serial Composition Gap (needs linear sequential depth)
- **Boundary**: Problems requiring Ω(n) sequential steps
- **Examples**: Iterated permutation composition, long-range state tracking, multi-step arithmetic
- **Formal**: Regular languages require O(n) CoT steps for constant-depth transformers
- **Empirical signature**: Accuracy degrades linearly with number of composition steps
- **CoT prediction**: Requires O(n) CoT steps. Log CoT insufficient. This is the gap CoT is specifically designed to close.
- **Key distinction from Type 2**: Depth gap is about nesting; serial gap is about length of sequential computation

### Type 4: Algorithmic Gap (needs complex algorithm within P)
- **Boundary**: Problems in P requiring sophisticated algorithms (graph algorithms, DP)
- **Examples**: Shortest path, graph connectivity, dynamic programming, sorting networks
- **Formal**: In theory, poly CoT → P, so these are within reach. In practice, the model must learn/discover the algorithm.
- **Empirical signature**: Accuracy depends on whether training distribution contains algorithmic traces
- **CoT prediction**: Poly CoT sufficient in principle. In practice, tool use (code execution) closes this gap more reliably than CoT.
- **Key insight**: The gap here is often learnability, not expressiveness

### Type 5: Intractability Gap (beyond P)
- **Boundary**: NP-hard problems — no polynomial-time algorithm exists (assuming P ≠ NP)
- **Examples**: 3-SAT, planning/Blocksworld, constraint satisfaction, NP-hard graph problems
- **Formal**: Even poly CoT reaches only P. These problems have no polynomial solution.
- **Empirical signature**: Accuracy degrades sharply at phase transitions (e.g., 3-SAT α ≈ 4.27)
- **CoT prediction**: CoT cannot close this gap. Tool use with exponential-time solvers can but defeats the purpose.
- **Key insight**: LLMs may approximate heuristic solutions but cannot systematically solve NP-hard instances

### Type 6: Architectural Gap (structural constraints beyond complexity)
- **Boundary**: Limitations from autoregressive structure, training objective, or attention mechanism
- **Examples**: Reversal curse (A→B but not B→A), negation insensitivity, causal masking artifacts
- **Formal**: Not captured by standard complexity classes — these are properties of the computation model itself
- **Empirical signature**: Failures persist regardless of scale, CoT, or problem size
- **CoT prediction**: CoT does not help — these are not depth/computation problems
- **Key insight**: Some gaps require architectural changes, not more computation

## Predictions Matrix

| Gap Type | Scales with n? | CoT helps? | CoT amount needed | Tool use helps? | Scales with model size? |
|---|---|---|---|---|---|
| Sensitivity | Yes | Partially | Ω(n) for parity | No | Minimal |
| Depth | Yes (nesting) | Yes | O(log n) | No | Moderate |
| Serial | Yes (steps) | Yes | O(n) | Partially | Moderate |
| Algorithmic | Yes (complexity) | In theory | O(poly(n)) | Yes (strongly) | Moderate |
| Intractability | Yes (phase transition) | No | N/A | Only with solver | Minimal |
| Architectural | No (constant) | No | N/A | Sometimes | Minimal |

## Formal Results (Conditional)

**Proposition 1** (Sensitivity Gap Existence): Under standard circuit complexity assumptions, there exist reasoning tasks with boolean sensitivity s(f) = n that no constant-depth transformer can solve for all n, regardless of width.

**Proposition 2** (Depth Gap Existence): If TC⁰ ≠ NC¹, there exist reasoning tasks solvable in NC¹ that no constant-depth log-precision transformer can solve, but O(log n) CoT steps suffice.

**Proposition 3** (Serial Gap Characterization): For iterated composition of k functions from a domain of size m, constant-depth transformers require Ω(k) CoT steps. This is tight: O(k) steps suffice.

**Proposition 4** (CoT Monotonicity for Serial Gaps): For Type 3 gaps, model accuracy is monotonically non-decreasing in CoT budget up to the optimal budget O(n), after which additional CoT provides no benefit (and may degrade accuracy per the "overthinking" phenomenon).

**Proposition 5** (Intractability Invariance): For Type 5 gaps, accuracy at the NP-hard phase transition does not improve with CoT budget beyond a constant factor, for any polynomial CoT budget.

## Connection to Empirical Literature

| Empirical Finding | Gap Type | Citation |
|---|---|---|
| Multi-digit multiplication failure | Type 3 (Serial) | Dziri et al. NeurIPS 2023 |
| GSM-Symbolic irrelevant clause sensitivity | Type 6 (Architectural) | Mirzadeh et al. ICLR 2025 |
| Planning failure in Blocksworld | Type 5 (Intractability) | Kambhampati et al. ICML 2024 |
| Alice in Wonderland counting collapse | Type 1/3 (Sensitivity/Serial) | Nezhurina et al. 2024 |
| Reversal curse | Type 6 (Architectural) | Berglund et al. ICLR 2024 |
| 3-SAT phase transition accuracy drop | Type 5 (Intractability) | Hazra et al. 2025 |
| Graph connectivity failure | Type 2/4 (Depth/Algorithmic) | Saparov et al. ICLR 2025 |
| Causal reasoning post hoc fallacy | Type 6 (Architectural) | Joshi et al. EMNLP 2024 |
| Working memory / N-back degradation | Type 3 (Serial) | Gong & Zhang 2024 |
| Negation insensitivity | Type 6 (Architectural) | arXiv:2503.22395 |
| Compositional depth decay | Type 2 (Depth) | Dziri et al. NeurIPS 2023 |
| CoT helps only on math/symbolic | Types 2,3 only | Sprague et al. 2024 |

## Key Novelty

No prior work has:
1. Defined reasoning gap formally with a complexity-theoretic grounding
2. Created a taxonomy where each gap type maps to a specific complexity boundary
3. Made testable predictions about which techniques close which gaps
4. Designed benchmarks specifically to isolate each gap type

The Strobl et al. survey (TACL 2024) characterizes what transformers CAN express. We characterize what they CANNOT do and WHY, connecting to the empirical failure literature.
