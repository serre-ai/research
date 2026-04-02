# Formal Framework: Depth-Complexity Correspondence

Date: 2026-04-01
Status: Draft

## 1. Setup and Notation

### 1.1 Task Model

A **reasoning task** is a family of decision problems $\{f_n\}_{n \in \mathbb{N}}$ where $f_n : \{0,1\}^n \to \{0,1\}$.

The **circuit complexity** of a task is the minimum boolean circuit size $s(n)$ required to compute $f_n$. We write $f \in \text{SIZE}(s(n))$ when $f_n$ has circuits of size $s(n)$.

Standard complexity classes give us the hierarchy:
- $\text{AC}^0 \subset \text{TC}^0 \subseteq \text{NC}^1 \subseteq \text{P}$

### 1.2 Transformer Model

Following Li et al. (2024) and Merrill & Sabharwal (2024), a **constant-depth transformer** $\mathcal{T}$ with:
- $L$ layers (constant)
- embedding dimension $d = O(\log n)$
- bounded precision $p$ bits

Without CoT, $\mathcal{T}$ computes functions in $\text{AC}^0$ (bounded precision, Li et al.) or $\text{TC}^0$ (unbounded precision, Merrill & Sabharwal).

### 1.3 Chain-of-Thought as Sequential Computation

A **CoT execution** of depth $k$ on input $x \in \{0,1\}^n$ is a sequence:

$$x = z_0 \xrightarrow{\mathcal{T}} z_1 \xrightarrow{\mathcal{T}} z_2 \xrightarrow{\mathcal{T}} \cdots \xrightarrow{\mathcal{T}} z_k$$

where each $z_i$ is the concatenation of $x$ with all previously generated tokens, and $\mathcal{T}$ generates one token per step.

**Key result (Li et al., 2024):** With $T$ CoT steps, a constant-depth bounded-precision transformer can compute any function computable by boolean circuits of size $T$.

This gives us the bridge: **CoT depth $k$ buys computational power equivalent to circuits of size $k$.**

## 2. The Optimal Depth Function

### 2.1 Definition

**Definition 1 (Optimal CoT Depth).** For a task $f$ with circuit complexity $s(n)$ and a transformer $\mathcal{T}$ with per-step error probability $\eta \in (0, 1)$, the **optimal depth** is:

$$d^*(f, n, \eta) = \arg\max_{k \geq 0} \; \text{acc}(k, f, n, \eta)$$

where $\text{acc}(k, f, n, \eta)$ is the probability that $\mathcal{T}$ with $k$ CoT steps produces the correct answer on a uniformly random input of size $n$.

### 2.2 The Accuracy Function

We decompose accuracy into two competing factors:

$$\text{acc}(k, f, n, \eta) = \underbrace{C(k, s(n))}_{\text{computational sufficiency}} \cdot \underbrace{R(k, \eta)}_{\text{reliability}}$$

**Computational sufficiency** $C(k, s(n))$: The probability that $k$ CoT steps provide enough computational power to solve the task. By Li et al., $k$ steps give circuits of size $k$, so:

$$C(k, s(n)) = \begin{cases} 1 & \text{if } k \geq s(n) \\ g(k / s(n)) & \text{if } k < s(n) \end{cases}$$

where $g: [0,1] \to [0,1]$ is a monotone increasing function with $g(0) = \beta_0$ (baseline accuracy from heuristics/memorization) and $g(1) = 1$.

**Reliability** $R(k, \eta)$: The probability that a $k$-step chain contains no fatal error. Under independent errors:

$$R(k, \eta) = (1 - \eta)^k$$

This is the noise ceiling — it decreases exponentially with depth.

### 2.3 The Inverted-U

The product $C(k, s(n)) \cdot R(k, \eta)$ creates an inverted-U:

- For small $k$: $C$ is low (insufficient computation), $R$ is high → accuracy limited by computation
- For $k \approx s(n)$: $C \approx 1$, $R$ still reasonable → peak accuracy
- For large $k \gg s(n)$: $C = 1$ (computation sufficient), but $R$ decays exponentially → accuracy drops

**This is the formal mechanism behind Wu et al.'s Theorem 4.2**, but grounded in circuit complexity rather than abstract parameters.

## 3. Main Theorems

### Theorem 1 (TC^0 Depth Bound)

**Statement:** For tasks $f \in \text{TC}^0$ (computable by the transformer without CoT), the optimal depth satisfies $d^*(f, n, \eta) = O(1)$ for any constant $\eta > 0$.

**Proof sketch:** If $f \in \text{TC}^0$, then $\mathcal{T}$ can compute $f$ in a single forward pass ($k = 0$). Computational sufficiency $C(0, s(n)) = 1$. Any additional CoT steps only decrease reliability by factor $(1-\eta)$ per step. Therefore $d^* = 0$.

More precisely: $\text{acc}(0) = 1$ and $\text{acc}(k) = (1-\eta)^k < 1$ for all $k > 0$. So $d^* = 0$.

**Note:** This is almost trivial — the interesting content is in what happens for tasks OUTSIDE TC^0.

### Theorem 2 (Circuit Complexity Depth Scaling)

**Statement:** For a task $f$ with minimum circuit size $s(n)$ where $s(n) > \omega(1)$ (i.e., $f \notin \text{TC}^0$), the optimal depth satisfies:

$$d^*(f, n, \eta) = \Theta\left(\frac{s(n)}{\log(1/(1-\eta))}\right)$$

In particular, for small $\eta$:

$$d^*(f, n, \eta) \approx \frac{s(n)}{\eta}$$

**Proof sketch:**

We need to maximize $\text{acc}(k) = C(k, s(n)) \cdot (1-\eta)^k$.

Case 1: $k < s(n)$. Here $C(k, s(n)) < 1$ and accuracy is limited by insufficient computation.

Case 2: $k \geq s(n)$. Here $C(k, s(n)) = 1$ and $\text{acc}(k) = (1-\eta)^k$, which is maximized at $k = s(n)$ (the minimum sufficient depth).

But this assumes a sharp threshold at $k = s(n)$, which is unrealistic. With a smooth transition, the optimal $k$ is near $s(n)$ but shifted by the noise rate:

Taking the derivative of $\log \text{acc}(k) = \log C(k, s(n)) + k \log(1-\eta)$ and setting to zero:

$$\frac{C'(k, s(n))}{C(k, s(n))} = -\log(1-\eta) \approx \eta$$

The optimal $k$ is where the marginal gain from more computation equals the marginal loss from noise.

### Theorem 3 (Noise Ceiling)

**Statement:** For any task $f$ and CoT depth $k > d^*(f, n, \eta)$, the accuracy degrades as:

$$\text{acc}(k) \leq \text{acc}(d^*) \cdot (1-\eta)^{k - d^*}$$

**Proof sketch:** Once $k \geq s(n)$, computational sufficiency is saturated ($C = 1$). Additional steps only add noise. Each extra step multiplies reliability by $(1-\eta)$, giving exponential decay beyond $d^*$.

### Theorem 4 (Complexity-Conditioned Scaling Laws)

**Statement:** For standard complexity classes, the optimal depth scales as:

| Complexity Class | Circuit Size $s(n)$ | Optimal Depth $d^*(n, \eta)$ |
|---|---|---|
| $\text{TC}^0$ | $O(1)$ | $O(1)$ |
| $\text{NC}^1$ | $O(n^{O(1)})$ with $O(\log n)$ depth | $O(\log n / \eta)$ |
| $\text{P}$ | $\text{poly}(n)$ | $O(\text{poly}(n) / \eta)$ |
| $\text{NP}$ (search) | $2^{O(n)}$ worst case | $\Omega(2^{O(n)})$ — infeasible |

**Implications:**
- Tasks in NC^1 (e.g., boolean formula evaluation, comparison sorting): moderate CoT depth helps
- Tasks in P \ NC^1 (if they exist): polynomial CoT depth needed
- NP-complete tasks: no feasible CoT depth suffices in the worst case — LLMs must rely on heuristics

### Theorem 5 (Dispute Resolution)

**Statement:** Given two sets of evaluation tasks $\mathcal{E}_1, \mathcal{E}_2$ with different circuit complexity distributions, the empirically observed relationship between CoT depth and performance can be opposite:

- If $\mathcal{E}_1$ contains mostly tasks with $s(n) \gg k_{\text{eval}}$ (complex tasks, short evaluation depth): longer CoT improves performance (Yeo et al. regime)
- If $\mathcal{E}_2$ contains mostly tasks with $s(n) \ll k_{\text{eval}}$ (simple tasks, long evaluation depth): longer CoT degrades performance (Wu et al. / Hassid et al. regime)

**Proof:** Direct consequence of the inverted-U shape of $\text{acc}(k)$. If evaluation operates left of the peak, more depth helps. If right of the peak, more depth hurts.

## 4. Connecting to Wu et al.'s Theorem 4.2

Wu et al. prove: $N^*(M, T) = TZ/(M(Z+1))$ where $T$ = task difficulty, $M$ = model capability.

Our mapping:
- Their $T$ → our $s(n)$ (circuit complexity). Wu et al. parameterize difficulty by arithmetic tree depth; we generalize to circuit complexity class.
- Their $M$ → relates to $1/\eta$ (model capability inversely correlates with per-step error). More capable models make fewer errors per step, so optimal depth shifts.
- Their $Z$ from Lambert W → arises from the specific functional form of their noise model. Our noise model is more general (any monotone decreasing $R(k, \eta)$).

**Our refinement:** Wu et al.'s theorem holds for their specific arithmetic task family. We prove it extends to ALL tasks when parameterized by circuit complexity, and we show WHY the inverted-U arises from the computation-reliability tradeoff.

## 5. Open Questions and Proof Challenges

### 5.1 The Sharpness of the Threshold

The biggest weakness in the framework is the computational sufficiency function $C(k, s(n))$. We assumed a relatively sharp threshold at $k = s(n)$. In practice:
- Transformers can solve some instances of hard problems via heuristics (SAT on structured instances)
- The transition from "insufficient computation" to "sufficient computation" may be gradual
- Average-case vs. worst-case complexity matters

**Approach:** Prove results under both sharp and smooth threshold models. Show that the qualitative conclusions (inverted-U, complexity-conditioned scaling) hold in both cases.

### 5.2 Correlated Errors

The independent error model $(1-\eta)^k$ is clean but may not be realistic:
- Early errors can cause cascading failures (one wrong step corrupts all subsequent reasoning)
- Self-correction can mitigate some errors (model notices and backtracks)
- Error rate may depend on step content, not just step count

**Approach:** Prove main results under independent errors, then show robustness: if errors are positively correlated (cascading), the noise ceiling is LOWER (stronger result). If negatively correlated (self-correction), the ceiling is higher but still exists.

### 5.3 The NP Gap

For NP-complete tasks, our framework says optimal CoT depth is infeasible ($2^{O(n)}$ worst case). But LLMs do solve some NP instances in practice. This is because:
- LLMs exploit structure (average-case, not worst-case)
- Many "NP" benchmarks have polynomial-size solutions with hints
- The framework should distinguish average-case from worst-case

**Approach:** Prove worst-case bounds, then discuss average-case implications separately. The worst-case result is still valuable: it explains why CoT doesn't help much on truly hard combinatorial instances.

### 5.4 Depth vs. Length Bridge

The dispute papers measure token LENGTH, not logical DEPTH. We need:
- A formal mapping: $\ell$ tokens encode $d$ logical steps (with $\ell/d$ = "verbosity ratio")
- Show that our depth results translate to length under reasonable verbosity assumptions
- Chen et al.'s Deep-Thinking Ratio (DTR) may provide the empirical bridge

## 6. Proof Strategy

1. **Theorem 1 (TC^0 bound):** Nearly trivial from Li et al. + noise model. Write this first.
2. **Theorem 3 (Noise ceiling):** Also straightforward — pure noise analysis beyond $d^*$.
3. **Theorem 4 (Complexity-conditioned scaling):** Instantiate the general framework for each complexity class. Requires connecting circuit size bounds to CoT steps via Li et al.
4. **Theorem 2 (General scaling):** The hardest — requires characterizing the $C(k, s(n))$ transition carefully. May need to restrict to specific task families for tight bounds.
5. **Theorem 5 (Dispute resolution):** Follows from Theorem 4 + empirical task complexity analysis.
