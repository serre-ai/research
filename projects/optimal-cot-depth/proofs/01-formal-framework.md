# Formal Framework: Depth-Complexity Correspondence

Date: 2026-04-01
Revised: 2026-04-01 (post-review fixes)
Status: Draft — all main theorems proved

## Key Changes from Initial Draft

1. **Theorem 2 was wrong.** d* = Θ(s(n)) is incorrect. The correct result is d* = min(c(n), ⌊1/η⌋). The proof showed that for hard tasks (c(n) > 1/η), the Regime 1 optimum at k = 1/η gives higher accuracy than k = c(n) because noise destroys you before you accumulate enough computation.

2. **Replaced circuit size s(n) with CoT complexity c(n)** as the primary parameter. c(n) is the minimum CoT steps needed — a more natural and often tighter quantity than circuit size.

3. **S_max ≤ 1** (expressivity ≠ capability). Never assume perfect accuracy.

4. **Self-correction model added.** Effective error rate η_eff = η(1-γ). Ceiling shifts to 1/η_eff.

5. **Dispute resolution demoted** from theorem to corollary. It's a direct consequence of the inverted-U, not a deep result.

## 1. Setup

### CoT Complexity

**Definition.** c_f(n) = minimum autoregressive steps for any constant-depth transformer to compute f_n on all inputs of size n.

**Known bounds:**
- c(n) ≤ s_f(n) by Li et al. (circuit size upper bound)
- c(n) = 0 for f ∈ TC^0
- c(n) = Θ(n) for parity (Amiri et al., tight)
- c(n) = l for l-fold composition (Barcelo et al., exact)

### Accuracy Decomposition

acc(k) = S(k, c) · R(k, η)

Where:
- S(k, c) = S_max · min(k/c, 1) — linear sufficiency with cap
- R(k, η) = (1-η)^k — independent errors
- S_max ≤ 1 — gap between expressivity and realized capability

## 2. Main Theorem: Depth-Complexity Scaling

### Statement

d*(f, n, η) = min(c(n), ⌊k*⌋)

where k* = -1/ln(1-η) ≈ 1/η for small η.

Two regimes:
- **Easy tasks** (c(n) ≤ k*): d* = c(n). Model fully solves the task.
- **Hard tasks** (c(n) > k*): d* = ⌊k*⌋ ≈ ⌊1/η⌋. Noise caps useful depth. This is the **capability ceiling**.

### Proof

**Regime 1 (k < c):** acc(k) = S_max · (k/c) · (1-η)^k

Maximize h(k) = k · (1-η)^k:
h'(k) = (1-η)^k [1 + k·ln(1-η)]

h'(k) = 0 ⟹ k* = -1/ln(1-η)

h''(k*) < 0, so k* is the unique maximum.

**Regime 2 (k ≥ c):** acc(k) = S_max · (1-η)^k, maximized at k = c.

**Case (a): c ≤ k*.** h is increasing on [0, k*], so increasing on [0, c]. The Regime 1 function approaches acc(c) = S_max · (1-η)^c from below. By continuity, the maximum is at k = c. ∎

**Case (b): c > k*.** Compare acc(k*) with acc(c):

acc(k*)/acc(c) = (k*/c) · (1-η)^{k*-c}

Take log with x = c/k* > 1:
ln(acc(k*)/acc(c)) = -ln(x) + (x-1)·k*·(-ln(1-η)) = -ln(x) + (x-1)

Since k* = -1/ln(1-η), the second term simplifies to x-1.

For x > 1: (x-1) - ln(x) > 0 (strict convexity of e^t).

Therefore acc(k*) > acc(c) whenever c > k*, so d* = ⌊k*⌋. ∎

**Boundary:** At c = k* (x = 1): (1-1) - ln(1) = 0. acc(k*) = acc(c). Continuous transition. ∎

### Numerical Example

η = 0.05, so k* = -1/ln(0.95) ≈ 19.5, ⌊k*⌋ = 19.

| Task | c(n) | d* | Regime | Peak accuracy |
|------|------|-----|--------|---------------|
| Majority | 0 | 0 | TC^0 | S_max |
| 5-fold comp | 5 | 5 | Easy | S_max · 0.95^5 ≈ 0.77·S_max |
| 10-fold comp | 10 | 10 | Easy | S_max · 0.95^10 ≈ 0.60·S_max |
| Parity (n=15) | 15 | 15 | Easy | S_max · 0.95^15 ≈ 0.46·S_max |
| Parity (n=50) | 50 | 19 | Hard (capped) | S_max · (19/50) · 0.95^19 ≈ 0.14·S_max |
| Parity (n=200) | 200 | 19 | Hard (capped) | S_max · (19/200) · 0.95^19 ≈ 0.04·S_max |

Key observation: for large n, parity accuracy drops to near zero because the model can never accumulate enough computation. This matches empirical reality — transformers can't do parity on long inputs.

## 3. Noise Ceiling Theorem

### Statement

For k ≥ c: acc(k) = acc(c) · (1-η)^{k-c}

### Proof

Sufficiency saturates: S(k,c) = S_max for k ≥ c.
acc(k) = S_max · (1-η)^k = S_max · (1-η)^c · (1-η)^{k-c} = acc(c) · (1-η)^{k-c}. ∎

Universal decay: (1-η) per step, independent of task. For η = 0.05, accuracy halves every ⌈ln(2)/η⌉ = 14 extra steps.

## 4. Self-Correction Extension

### Model

Each step: error with prob η, correction with prob γ (if error occurred).
Effective rate: η_eff = η(1-γ).

### Result

d* = min(c(n), ⌊1/η_eff⌋) = min(c(n), ⌊1/(η(1-γ))⌋)

Self-correction raises the ceiling but doesn't eliminate it (for γ < 1).

### Examples

| η | γ | η_eff | Ceiling |
|---|---|-------|---------|
| 0.10 | 0 | 0.10 | 10 |
| 0.10 | 0.5 | 0.05 | 20 |
| 0.10 | 0.9 | 0.01 | 100 |
| 0.05 | 0.5 | 0.025 | 40 |

### Why γ < 1 in practice

Correcting an error requires recognizing it. Error recognition has its own failure rate. If recognition fails, the error propagates. As γ → 1, the model must be nearly perfect at error detection — but if it were that good, it wouldn't make the error in the first place.

## 5. Relationship to Wu et al.'s Theorem 4.2

Wu et al.: N*(M, T) = TZ/(M(Z+1)) where T = difficulty, M = capability, Z from Lambert W.

Our framework:
- T → c(n) (CoT complexity, grounded in circuit complexity)
- M → related to 1/η (capability ↔ low error rate)

### Key difference: the capability ceiling

Wu et al.'s N* grows without bound as T → ∞ (for fixed M). Our d* saturates at 1/η. This is because Wu et al. don't have an explicit noise model — their analysis captures the computational scaling but misses the noise ceiling.

With the ceiling, our framework makes a stronger prediction: **no task benefits from more than 1/η steps**, regardless of difficulty. Wu et al. can't make this prediction.

### When they agree

For easy tasks (c(n) < 1/η), both frameworks predict d* ∝ c(n). The disagreement is only in the hard-task regime.

## 6. Remaining Open Questions

### 6.1 Smooth Sufficiency Functions

Assumption 2 (linear S) is a simplification. The true S might be:
- Sigmoidal (sharp phase transition at k ≈ c)
- Concave (diminishing marginal returns per step)
- Step function (nothing until k = c, then full capability)

The qualitative result (inverted U, two regimes) holds for ALL monotone increasing S combined with monotone decreasing R. The exact expression for d* changes but the capability ceiling at 1/η persists.

### 6.2 Correlated Errors

Positively correlated errors (cascading): R(k) decays FASTER than (1-η)^k. The ceiling is LOWER — strengthening our result. The independent-error model is a best case for the reasoner.

Negatively correlated errors (self-correction across steps): handled by Proposition 3 with effective rate η_eff.

### 6.3 Unknown CoT Complexity

For real tasks (MATH, AIME, coding), c(n) is unknown. The framework is theoretically precise but cannot yet make quantitative predictions for arbitrary tasks. Empirical estimation of c(n) (via measuring where the accuracy peak occurs) is a path forward — and our framework tells you exactly what you're measuring.

### 6.4 Depth vs. Length Bridge

Still needed: formal mapping between logical depth (our c(n)) and token length. Chen et al.'s Deep-Thinking Ratio (DTR) is the best empirical bridge. Under a "verbosity ratio" v = tokens_per_step, optimal token length = v · d*.
