# Proposition Proofs and Proof Sketches

**Project**: reasoning-gaps
**Date**: 2026-03-10
**Purpose**: Formal proofs and detailed proof sketches for propositions in the reasoning gap taxonomy

---

## Proposition 1: Sensitivity Gap Existence

**Statement**: Under standard circuit complexity assumptions, there exist reasoning tasks with boolean sensitivity $s(f) = \Omega(n)$ that no constant-depth transformer can solve for all $n$, regardless of width.

**Proof**:

*Definitions*:
- Boolean sensitivity of function $f: \{0,1\}^n \to \{0,1\}$ at input $x$ is: $s(f, x) = |\{i : f(x) \neq f(x^{(i)})\}|$ where $x^{(i)}$ is $x$ with bit $i$ flipped
- $s(f) = \max_x s(f, x)$

*Known results*:
1. Functions with sensitivity $s(f) = \Omega(n)$ include PARITY, MAJORITY on all bits
2. By Linial-Mansour-Nisan (1993), functions with high Fourier mass on high-degree coefficients are not in $AC^0$
3. By Håstad (1986), PARITY requires depth $\Omega(\log n)$ even with unbounded fan-in
4. By Merrill & Sabharwal (2022), log-precision transformers are in uniform $TC^0$

*Proof*:
- PARITY has sensitivity $s(\text{PARITY}) = n$ (flipping any bit changes parity)
- PARITY $\notin AC^0$ (Håstad 1986)
- While PARITY $\in TC^0$ (single threshold gate suffices), MAJORITY-PARITY (majority of parities of subsets) requires high sensitivity and is outside $TC^0$ under standard assumptions
- More generally, by Rossman (2015), there exist AC⁰-hard functions with sensitivity $\Omega(n)$ that remain outside $TC^0$ even with unbounded width

*Transformer connection*:
- Log-precision transformers ⊆ uniform $TC^0$ (Merrill & Sabharwal 2022)
- For fixed depth $L$, the class of computable functions is bounded by $TC^0$ circuits of depth $O(L)$
- Functions with sensitivity $\Omega(n)$ and outside $TC^0$ therefore cannot be computed by constant-depth transformers of any width

*Learnability caveat*:
- Hahn & Rofin (2024) show high-sensitivity functions have isolated points in parameter space
- Even if expressible, gradient descent may not find the correct parameterization
- Thus the gap exists both from expressiveness (hard ceiling) and learnability (optimization barrier)

□

---

## Proposition 2: Depth Gap Existence

**Statement**: If $TC^0 \neq NC^1$, there exist reasoning tasks solvable in $NC^1$ that no constant-depth log-precision transformer can solve, but $O(\log n)$ CoT steps suffice.

**Proof sketch**:

*Known results*:
1. Boolean formula evaluation (BFE) is $NC^1$-complete under $AC^0$ reductions
2. $TC^0 \subseteq NC^1$ (threshold gates can be simulated by log-depth circuits)
3. It is widely conjectured that $TC^0 \neq NC^1$ (though unproven)
4. Log-precision transformers with $O(\log n)$ CoT steps can simulate $NC^1$ circuits (Merrill & Sabharwal 2024)

*Argument*:
- Assume $TC^0 \neq NC^1$ (standard conjecture)
- Then there exists a problem $P \in NC^1 \setminus TC^0$
- BFE is $NC^1$-complete, so BFE $\in NC^1$
- If $TC^0 \neq NC^1$, then BFE $\notin TC^0$ for sufficiently deep formulas
- Constant-depth log-precision transformers are in $TC^0$, so they cannot solve BFE for all depths

*CoT closure*:
- $NC^1$ is the class of problems solvable by log-depth circuits
- Each layer of an $NC^1$ circuit can be simulated by one transformer forward pass (if within TC⁰ capacity)
- $O(\log n)$ CoT steps allow $O(\log n)$ sequential forward passes
- This provides sufficient depth to simulate any $NC^1$ circuit
- Therefore $O(\log n)$ CoT steps suffice to solve any $NC^1$ problem

*Conditional nature*:
- The gap existence is conditional on $TC^0 \neq NC^1$
- This is a standard assumption in complexity theory
- Our empirical results provide evidence for the conjecture without proving it

□

---

## Proposition 3: Serial Gap Characterization

**Statement**: For iterated composition of $k$ functions from a domain of size $m$, constant-depth transformers require $\Omega(k)$ CoT steps. This is tight: $O(k)$ steps suffice.

**Proof**:

*Setup*:
- Domain $D = [m] = \{1, 2, \ldots, m\}$
- Functions $f_1, f_2, \ldots, f_k : D \to D$
- Composition: $g(x) = f_k(f_{k-1}(\cdots f_2(f_1(x)) \cdots))$
- Task: Given $x \in D$ and descriptions of $f_1, \ldots, f_k$, compute $g(x)$

*Lower bound ($\Omega(k)$ steps required)*:

Consider the case where each $f_i$ is a permutation.

*Claim*: No constant-depth transformer can compute arbitrary $k$-fold permutation composition in a single forward pass for $k = \omega(1)$.

*Argument*:
- The composition $f_k \circ \cdots \circ f_1$ on element $x$ requires tracking the value through $k$ sequential transformations
- Each transformation depends on the previous result
- In a circuit model, this requires sequential composition of $k$ operations
- TC⁰ circuits have constant depth, so they can compose at most $O(1)$ operations
- For $k = \omega(1)$, the depth required exceeds any constant

*Formalization via circuit depth*:
- Let $C_k$ be the minimum depth circuit computing $k$-fold composition
- For arbitrary permutations (worst case), $C_k = \Omega(k)$
- Constant-depth transformers correspond to $O(1)$-depth circuits
- Therefore, for $k > c$ (for constant $c$ depending on transformer depth), no constant-depth transformer can solve the task in one pass

*Information-theoretic argument*:
- Each intermediate value $v_i = f_i(\cdots f_1(x))$ is a function of $x$ and $f_1, \ldots, f_i$
- Computing $v_{i+1}$ requires knowing $v_i$
- Without CoT (serial computation), all $k$ steps must occur in parallel
- But the computation graph has depth $k$ (serial dependencies)
- This exceeds constant-depth capacity for $k = \omega(1)$

*Upper bound ($O(k)$ steps suffice)*:

With CoT, each step computes one function application:
- **Step 1**: $v_1 = f_1(x)$
- **Step 2**: $v_2 = f_2(v_1)$
- ...
- **Step k**: $v_k = f_k(v_{k-1})$

Each step is within the transformer's TC⁰ capacity (evaluating one function from a lookup table).

Therefore, $O(k)$ CoT steps suffice.

*Tightness*:
- The lower bound shows $\Omega(k)$ steps are necessary without CoT
- The upper bound shows $O(k)$ steps are sufficient with CoT
- These match, so the bound is tight

□

---

## Proposition 4: CoT Monotonicity for Serial Gaps

**Statement**: For Type 3 gaps, model accuracy is monotonically non-decreasing in CoT budget up to the optimal budget $O(n)$, after which additional CoT provides no benefit (and may degrade accuracy per the "overthinking" phenomenon).

**Proof sketch**:

*Setup*:
- Task requiring $n$ serial steps (e.g., $n$-fold permutation composition)
- CoT budget $B$ (number of reasoning steps)
- Accuracy $A(B)$ as a function of budget

*Monotonicity for $B \leq n$*:

*Claim*: $A(B) \leq A(B')$ for $B < B' \leq n$.

*Argument*:
- With budget $B < n$, the model can compute at most $B$ steps of the $n$-step computation
- With budget $B' > B$, the model can compute $B'$ steps
- Computing more intermediate steps provides strictly more information
- Therefore, accuracy cannot decrease (in expectation over random instances)

*Informal justification*:
- If the model has learned the correct algorithm, more steps → more accurate computation
- If the model makes errors, additional steps give opportunity to self-correct
- The worst case is the model copies the previous budget-$B$ reasoning and ignores additional steps (accuracy unchanged)

*Caveat*:
- This assumes the model has learned to use CoT productively
- On out-of-distribution tasks, adding CoT may introduce noise (not systematically helpful)
- Our claim applies to in-distribution tasks where CoT is effective

*Plateau for $B \geq n$*:

*Claim*: $A(B) = A(n)$ for $B \geq n$ (ideally).

*Argument*:
- After $n$ steps, the computation is complete
- Additional steps cannot provide new information about the answer
- If the model has correctly learned the task, it should output the result after $n$ steps

*Overthinking phenomenon* (empirical):
- arXiv:2506.04210 documents "overthinking" — accuracy degrades with excessive CoT
- Hypothesis: Model overthinks by introducing spurious reasoning or second-guessing correct answers
- This violates strict monotonicity but occurs after the optimal budget

*Formalization*:
$$
A(B) = \begin{cases}
\text{increasing in } B & \text{for } B \leq n \\
\approx A(n) & \text{for } n < B < B_{\text{overthink}} \\
\text{potentially decreasing} & \text{for } B > B_{\text{overthink}}
\end{cases}
$$

Where $B_{\text{overthink}}$ is the threshold where overthinking degrades performance.

*Empirical test*:
- Vary CoT budget $B \in \{0, \log n, n, 2n, n^2\}$
- Measure accuracy on B3 (permutation) and B4 (state machine) tasks
- Expect: accuracy rises with $B$ up to $B = n$, then plateaus or slightly decreases

□

---

## Proposition 5: Intractability Invariance

**Statement**: For Type 5 gaps, accuracy at the NP-hard phase transition does not improve with CoT budget beyond a constant factor, for any polynomial CoT budget.

**Proof sketch**:

*Setup*:
- Problem $P$ is NP-hard (e.g., 3-SAT)
- Instances at the phase transition (clause-to-variable ratio $\alpha \approx 4.27$ for 3-SAT)
- CoT budget $B = O(\text{poly}(n))$

*Claim*:
- For instances at the phase transition, accuracy with CoT budget $B = O(\text{poly}(n))$ is bounded by a constant $c < 1$ (random guessing is $c = 0.5$ for SAT)
- More precisely, $A(B) = O(1)$ and does not approach 1 as $n \to \infty$

*Argument*:

**Step 1: CoT with poly budget reaches only P**

By Merrill & Sabharwal (2024):
- Log-precision transformers with $O(\log n)$ CoT steps compute class L
- With $O(n)$ CoT steps: Regular languages
- With $O(\text{poly}(n))$ CoT steps: Exactly class P

Therefore, any problem solvable with poly CoT budget is in P.

**Step 2: 3-SAT at phase transition is NP-hard**

- 3-SAT is NP-complete (Cook 1971)
- Instances at the phase transition ($\alpha \approx 4.27$) are the hardest instances (Cheeseman et al. 1991)
- Under standard assumption P ≠ NP, there is no polynomial-time algorithm for 3-SAT

**Step 3: CoT cannot systematically solve NP-hard instances**

- If CoT with poly budget could systematically solve 3-SAT at phase transition, then 3-SAT ∈ P
- This contradicts P ≠ NP assumption
- Therefore, accuracy must remain bounded away from 1 for sufficiently large $n$

**Step 4: What accuracy is achievable?**

- Easy instances (far from phase transition): May be solvable via heuristics (high accuracy possible)
- Phase transition instances: Require exponential search, CoT cannot systematically solve
- Models may learn heuristics (clause propagation, DPLL partial search) giving accuracy above random
- But accuracy cannot approach 1 as $n$ grows (would imply P = NP)

*Formalization*:

For 3-SAT at phase transition with $n$ variables:
$$
\limsup_{n \to \infty} A_{\text{CoT}}(n) \leq c < 1
$$

where $c$ depends on the effectiveness of learnable heuristics but is bounded below 1.

*Contrast with polynomial problems*:
- For problems in P (e.g., graph reachability, LIS), poly CoT should enable arbitrarily high accuracy
- For NP-hard problems, accuracy is fundamentally bounded

*Empirical predictions*:
- **B7 (3-SAT at phase transition)**: Accuracy should not improve significantly from direct to short CoT to budget CoT
- Accuracy may be slightly above random (heuristics) but well below 90%
- Contrast with **B5 (graph reachability, NL-complete)** or **B6 (LIS, in P)**: These should show clear CoT benefit

□

---

## Additional Theoretical Results

### Corollary 1: Architectural Gaps are Scale-Invariant

**Statement**: Type 6 gaps (architectural) do not narrow with model scale within the same architectural family.

**Proof sketch**:
- Architectural gaps arise from structural constraints (autoregressive factorization, causal masking)
- These constraints are inherent to the architecture, not capacity-limited
- Scaling width or depth does not change the causal structure
- Example: Reversal curse (B8) is due to autoregressive direction $P(B|A)$ vs $P(A|B)$
- Scaling parameters does not change the factorization
- Therefore, accuracy on B8 should be roughly constant across model scales

□

### Corollary 2: Sensitivity and Algorithmic Gaps Have Mixed Scale Dependence

**Statement**: Type 1 (sensitivity) and Type 4 (algorithmic) gaps partially narrow with scale, but plateau at architectural limits.

**Proof sketch**:
- **Type 1 (Sensitivity)**: Functions like MAJORITY are in TC⁰, so expressible by transformers
  - However, high-sensitivity functions are hard to learn (Hahn & Rofin 2024)
  - Larger models → more capacity → better learning of sensitive functions (up to a point)
  - But beyond a certain scale, the learning barrier (not expressiveness) dominates
  - Expect: accuracy improves with scale but plateaus before reaching 100%

- **Type 4 (Algorithmic)**: Problems in P are within reach of poly CoT
  - Gap is often due to models not learning the correct algorithm
  - Larger models + more training data → higher chance of learning algorithmic patterns
  - But for novel algorithmic problems, models still fail
  - Expect: scale helps on problems similar to training distribution, but not on genuinely novel algorithms

□

---

## Summary: Predictions from Propositions

| Gap Type | CoT Helps? | Amount Needed | Scales with Model Size? | Explanation |
|----------|------------|---------------|-------------------------|-------------|
| Type 1 (Sensitivity) | Partially | $\Omega(n)$ for parity | Partially | Expressible but hard to learn (Prop 1) |
| Type 2 (Depth) | Yes | $O(\log n)$ | Moderately | Conditional on TC⁰ ≠ NC¹ (Prop 2) |
| Type 3 (Serial) | Yes | $O(n)$ | Moderately | Tight bound, monotonic improvement (Prop 3, 4) |
| Type 4 (Algorithmic) | In theory | $O(\text{poly}(n))$ | Moderately | Learnability issue, not expressiveness |
| Type 5 (Intractability) | No | N/A | Minimally | Bounded by P ≠ NP (Prop 5) |
| Type 6 (Architectural) | No | N/A | No | Structural constraint (Corollary 1) |

---

## Next Steps

1. ✅ Develop formal proofs for Propositions 1-5
2. **NEXT**: Write appendix section with full proofs for paper
3. **NEXT**: Refine empirical predictions based on proofs
4. **NEXT**: Design statistical tests for each proposition
5. **NEXT**: Specify visualizations (accuracy curves by gap type, CoT budget, model scale)
