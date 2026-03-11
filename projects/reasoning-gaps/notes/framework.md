# Formal Framework: Reasoning Gaps in Large Language Models

**Project**: reasoning-gaps
**Date**: 2026-03-11
**Status**: In development

---

## 1. Core Definitions

### Definition 1.1: Problem Instance and Problem Class

Let $\Sigma$ be a finite alphabet. A **problem instance** is a string $x \in \Sigma^*$ together with a correct output $y \in \Sigma^*$.

A **problem class** $\mathcal{P}$ is a language $L \subseteq \Sigma^* \times \Sigma^*$ together with a set of structural properties $\Pi = \{\pi_1, \pi_2, \ldots\}$ that characterize the problem.

**Examples of structural properties**:
- **Compositional depth** $d$: Number of sequential operations required
- **Recursion depth** $r$: Maximum nesting level in hierarchical structure
- **Working memory load** $m$: Number of simultaneous bindings to track
- **State transitions** $s$: Number of intermediate states to maintain
- **Abstraction level** $a$: Distance from training distribution (to be formalized)

### Definition 1.2: Model Class

A **model class** $\mathcal{M}$ is a set of functions $f: \Sigma^* \rightarrow \Sigma^*$ with specified architectural constraints.

**Primary model class**: Autoregressive transformers with:
- $L$ layers
- $d_{\text{model}}$ hidden dimension
- $n_{\text{heads}}$ attention heads
- Softmax attention mechanism
- Causal masking for autoregressive generation

**Notation**: We write $\text{AT}(L, d_{\text{model}}, n_{\text{heads}})$ for this class.

### Definition 1.3: Performance Metric

Let $\mathcal{D}$ be a distribution over problem instances. For a model $f \in \mathcal{M}$ and problem class $\mathcal{P}$, define:

$$\text{Acc}(f, \mathcal{P}, \mathcal{D}) = \Pr_{(x,y) \sim \mathcal{D}}[f(x) = y]$$

For tasks with partial credit, we can use normalized distance metrics:
$$\text{Score}(f, \mathcal{P}, \mathcal{D}) = \mathbb{E}_{(x,y) \sim \mathcal{D}}[1 - \frac{d(f(x), y)}{d_{\max}}]$$

where $d$ is an appropriate distance metric (e.g., edit distance) and $d_{\max}$ normalizes to $[0,1]$.

### Definition 1.4: Reasoning Gap (Formal)

A **reasoning gap** is a tuple $G = (\mathcal{P}, \mathcal{M}, \mathcal{D}, \delta, \theta)$ where:
- $\mathcal{P}$ is a problem class with structural properties $\Pi$
- $\mathcal{M}$ is a model class
- $\mathcal{D}$ is a distribution over problem instances in $\mathcal{P}$
- $\delta \in (0, 1)$ is the **performance degradation threshold**
- $\theta \in (0, 1)$ is the **baseline performance level**

We say the gap $G$ **exists** if:
$$\sup_{f \in \mathcal{M}} \text{Performance}(f, \mathcal{P}, \mathcal{D}) < \theta - \delta$$

That is, even the best model in $\mathcal{M}$ performs at least $\delta$ worse than the baseline threshold $\theta$.

**Interpretation**:
- $\theta$ represents "adequate performance" (e.g., 0.90 for high-stakes tasks)
- $\delta$ represents "significant degradation" (e.g., 0.20 drop)
- A gap exists when models systematically fail to achieve adequate performance

### Definition 1.5: Gap Type Classification

We classify gaps by their **fundamental cause**:

1. **Architectural gap**: Performance degradation due to computational complexity bounds
   - Formal: $\mathcal{P} \notin \text{Complexity}(\mathcal{M})$ where $\text{Complexity}(\mathcal{M})$ is the complexity class corresponding to $\mathcal{M}$
   - Example: If $\mathcal{M} = \text{AT}$ and $\text{Complexity}(\text{AT}) \subseteq \text{TC}^0$, then problems requiring $\text{NC}^1$ exhibit architectural gaps

2. **Capacity gap**: Performance degradation due to insufficient model capacity
   - Formal: $\mathcal{P} \in \text{Complexity}(\mathcal{M})$ but $\exists f \in \mathcal{M}'$ with larger capacity such that Performance$(f, \mathcal{P}, \mathcal{D}) \geq \theta$
   - Example: Tasks requiring large circuits within TC⁰ that smaller models cannot implement

3. **Training gap**: Performance degradation due to training distribution mismatch
   - Formal: $\mathcal{P} \in \text{Complexity}(\mathcal{M})$ and capacity is sufficient, but training distribution $\mathcal{D}_{\text{train}}$ doesn't cover $\mathcal{D}_{\text{test}}$ adequately
   - Example: Novel compositions not seen during training

---

## 2. Theoretical Foundations

### Theorem 2.1: Transformer Expressiveness (Merrill et al., 2022)

Autoregressive transformers with saturated attention and floating-point precision can be simulated by constant-depth threshold circuits:

$$\text{AT}(L, d, h) \subseteq \text{TC}^0$$

**Implications**:
- Transformers can solve problems in TC⁰ (includes MAJORITY, PARITY)
- Cannot solve problems requiring $\omega(1)$ depth (constant depth)
- Bounded by threshold gates with polynomial size

### Theorem 2.2: Complexity Hierarchy

$$\text{AC}^0 \subsetneq \text{TC}^0 \subsetneq \text{NC}^1 \subsetneq \text{P}$$

Where:
- **AC⁰**: Constant-depth circuits with unbounded fan-in AND/OR gates
- **TC⁰**: Constant-depth circuits with threshold gates
- **NC¹**: Log-depth circuits with bounded fan-in
- **P**: Polynomial-time Turing machines

**Key separations**:
- PARITY $\notin$ AC⁰ but PARITY $\in$ TC⁰
- Tree evaluation with depth $\omega(1)$ requires NC¹
- Problems requiring sequential memory access may need P

### Proposition 2.3: Chain-of-Thought Extension

Chain-of-thought with $T$ intermediate steps extends transformer computation to depth $O(T)$.

**Formal model**: Each CoT step corresponds to one full transformer pass. With $T$ steps, total depth is $O(T \cdot L)$ where $L$ is layers per pass.

**Complexity implication**: $T$-step CoT can solve problems in depth-$O(T)$ circuits.

**Limitation**: Depth is still bounded by context length and practical $T$ values. Cannot solve problems requiring unbounded or data-dependent depth.

---

## 3. Gap Taxonomy with Formal Characterization

### Gap Type 1: Compositional Depth Gaps

**Informal**: Failures on problems requiring many sequential operations

**Formal characterization**:
- **Problem property**: Compositional depth $d$ where $d > k$ for some threshold $k$
- **Structural definition**: Problem requires chain of $d$ sequential operations $f_d \circ f_{d-1} \circ \cdots \circ f_1(x)$
- **Complexity bound**: If $d = O(1)$ and each $f_i \in$ TC⁰, then composition $\in$ TC⁰
- **Gap condition**: If $d = \omega(1)$ (superconstant), may require depth beyond TC⁰

**Examples**:
- Function composition: $f^{(k)}(x) = f(f(\cdots f(x)))$ with $k > d_{\max}$
- Multi-step logical inference with $> k$ sequential deductions
- Iterative algorithms requiring $> k$ iterations

**Empirical prediction**: Performance degrades as $d$ increases, with sharp transition around $d = d_{\text{crit}}$

**CoT mitigation**: Can help if $d \cdot c \leq T$ where $c$ is cost per step and $T$ is CoT budget

### Gap Type 2: Recursive Structure Gaps

**Informal**: Failures on problems with hierarchical recursive structure

**Formal characterization**:
- **Problem property**: Recursion depth $r$ and branching factor $b$
- **Structural definition**: Binary tree evaluation, nested structures, recursive function calls
- **Complexity bound**: Tree evaluation with depth $\omega(1)$ requires NC¹
  - TC⁰ circuits have constant depth, cannot handle unbounded recursion
  - NC¹ allows $O(\log n)$ depth for tree reduction
- **Gap condition**: Problems with $r = \omega(1)$ or requiring parallel reduction exhibit architectural gaps

**Examples**:
- Evaluating nested Boolean formulas: $(((A \land B) \lor C) \land (D \lor (E \land F)))$
- Tree-structured inference
- Recursive program evaluation

**Empirical prediction**: Performance drops for trees with depth $> O(1)$ and cannot be fully mitigated by increasing model size within transformer architecture

**CoT mitigation**: Can serialize tree traversal but requires $O(b^r)$ steps for depth-first traversal, exponential in depth

### Gap Type 3: Working Memory Gaps

**Informal**: Failures on problems requiring simultaneous tracking of many entities

**Formal characterization**:
- **Problem property**: Working memory load $m$ = number of simultaneous variable bindings
- **Structural definition**: Problems requiring $m$ distinct active bindings in "working memory"
- **Architectural constraint**: Attention entropy limits (Wang et al., 2024)
  - Self-attention has bounded capacity for simultaneous bindings
  - Total attention entropy increases with $m$, leading to dispersion
- **Gap condition**: When $m > m_{\text{capacity}}$ for model's attention resources

**Examples**:
- N-back task with $N > m_{\text{capacity}}$
- Tracking states of $> m_{\text{capacity}}$ entities in reasoning
- Multi-variable constraint satisfaction with $> m_{\text{capacity}}$ variables

**Empirical prediction**: Gradual degradation as $m$ increases, with soft threshold around $m_{\text{capacity}} \approx 7 \pm 2$ (analogous to human working memory limits)

**CoT mitigation**: Partial help via externalization (write down bindings in text), but still limited by context processing

### Gap Type 4: State Transition Gaps

**Informal**: Failures on problems requiring explicit state tracking across steps

**Formal characterization**:
- **Problem property**: Number of state transitions $s$ and state space size $|S|$
- **Structural definition**: Problems modeling as state machines, requiring tracking current state through transitions
- **Architectural constraint**: Lack of persistent latent state (Liu et al., 2025)
  - LLMs rely on manifest context, not internal state
  - State must be explicitly represented in text
- **Gap condition**: When $|S|$ is large or state transitions are implicit/complex

**Examples**:
- Simulating finite automata with many states
- Game state tracking (chess, tic-tac-toe with complex states)
- Maintaining conversation context across turns without explicit re-prompting

**Empirical prediction**: Performance degrades with state space size and transition complexity

**CoT mitigation**: Helps significantly via explicit state externalization in reasoning steps

### Gap Type 5: Counterfactual Reasoning Gaps

**Informal**: Failures when reasoning requires dynamic modification of world model

**Formal characterization**:
- **Problem property**: Counterfactual distance $c_{\text{dist}}$ = amount of world knowledge that must be modified
- **Structural definition**: Given factual knowledge $K$ and counterfactual premise $P$, reason about world $K'$ where $K' = K \setminus K_{\text{conflict}} \cup P$
- **Architectural constraint**: Cannot dynamically modify internal knowledge graph
  - Parameters encode factual knowledge from training
  - No mechanism for temporary knowledge override
- **Gap condition**: When $|K_{\text{conflict}}|$ is large or conflicts are deep (affect many dependent facts)

**Examples**:
- "If gravity were repulsive, how would planets move?"
- "If the sky were green, what would that imply about atmospheric composition?"
- Reasoning about alternate history scenarios

**Empirical prediction**: 25-40% accuracy drop from interventional to counterfactual reasoning (Miller et al., 2024)

**CoT mitigation**: Limited effectiveness; requires explicit listing of modified facts, but still reversion to parametric knowledge

### Gap Type 6: Abstraction and Transfer Gaps

**Informal**: Failures when problem differs from training distribution in surface features

**Formal characterization**:
- **Problem property**: Distribution shift magnitude $\Delta_{\text{dist}}$ between training and test
- **Structural definition**: Problems with identical logical structure but different surface features (content, format, vocabulary)
- **Architectural constraint**: Training distribution dependence (Zhang et al., 2025)
  - Pattern matching rather than abstract reasoning
  - Success depends on overlap with training distribution
- **Gap condition**: When $\Delta_{\text{dist}}$ is large in relevant dimensions

**Examples**:
- Logic puzzles with unfamiliar content (abstract symbols vs. familiar objects)
- Mathematical reasoning with unusual notation
- Compositional generalization to unseen combinations

**Empirical prediction**: Severe degradation (100% → 0%) on novel compositions far from training distribution

**CoT mitigation**: Helps via providing in-distribution example patterns in prompts

---

## 4. Formal Characterization of CoT Effectiveness

### Definition 4.1: Serial Decomposability

A problem class $\mathcal{P}$ is **$(T, \epsilon)$-serially decomposable** if there exists a decomposition into $T$ sequential steps such that:
1. Each step can be solved by a model in $\mathcal{M}$ with accuracy $\geq 1 - \epsilon$
2. Errors do not compound significantly: total error $\leq T \cdot \epsilon$

### Theorem 4.2: CoT Effectiveness for Serially Decomposable Problems

For a problem class $\mathcal{P}$ that is $(T, \epsilon)$-serially decomposable:
- **CoT with $\geq T$ steps can achieve accuracy $\geq 1 - T\epsilon$**
- This holds even if $\mathcal{P}$ requires depth $> O(1)$ circuits

**Proof sketch**: Each CoT step solves one subproblem with error $\epsilon$. Union bound over $T$ steps gives total error $\leq T\epsilon$.

### Theorem 4.3: CoT Ineffectiveness for Non-Decomposable Problems

For problems requiring **true parallelism** or **recursive reduction** that cannot be efficiently serialized:
- CoT provides at most polynomial speedup (serializing parallel computation)
- If problem requires exponential time to serialize, CoT is ineffective

**Examples**:
- Parallel tree reduction: Serial traversal requires $O(2^d)$ steps for depth-$d$ tree
- Simultaneous constraint satisfaction: Cannot decompose without considering all constraints together

### Corollary 4.4: CoT Gap Closure Characterization

Chain-of-thought **closes** gaps when:
1. Problem is serially decomposable with $T \leq T_{\text{max}}$ (context length limit)
2. Each step within TC⁰ capability
3. Error accumulation manageable ($T\epsilon < \delta$)

Chain-of-thought **masks** gaps when:
1. Success depends on training distribution overlap (providing similar examples)
2. Problem is not serially decomposable but appears similar to training data
3. Intermediate steps are fluent but logically inconsistent

---

## 5. Scale Dependence Classification

### Definition 5.1: Gap Scalability

A reasoning gap $G = (\mathcal{P}, \mathcal{M}, \mathcal{D}, \delta, \theta)$ is:

1. **Scale-invariant** if: $\forall M_1, M_2 \in \mathcal{M}$ with $M_2$ having larger capacity, Performance$(M_2, \mathcal{P}, \mathcal{D})$ - Performance$(M_1, \mathcal{P}, \mathcal{D}) < \epsilon$ for small $\epsilon$
   - Gap persists regardless of model size
   - Caused by architectural limitations

2. **Scale-dependent** if: $\exists$ sequence $\{M_i\}$ with increasing capacity such that Performance$(M_i, \mathcal{P}, \mathcal{D}) \rightarrow 1$ as $i \rightarrow \infty$
   - Gap narrows with scale
   - Caused by capacity constraints, not fundamental architecture

3. **Training-dependent** if: Gap exists for models trained on distribution $\mathcal{D}_{\text{train}}$ but not for models trained on $\mathcal{D}'_{\text{train}}$ that covers $\mathcal{D}_{\text{test}}$
   - Gap is contingent on training data
   - Not architectural or capacity-related

### Proposition 5.2: Theoretical Predictions

**Scale-invariant gaps** (Architectural):
- Recursive structure gaps beyond TC⁰ (Gap Type 2)
- Counterfactual reasoning requiring dynamic knowledge modification (Gap Type 5)

**Scale-dependent gaps** (Capacity):
- Compositional depth gaps within TC⁰ but requiring large circuits (Gap Type 1)
- Working memory gaps near capacity threshold (Gap Type 3)

**Training-dependent gaps**:
- Abstraction/transfer gaps (Gap Type 6)
- Some compositional gaps with training distribution overlap (Gap Type 1)

### Hypothesis 5.3: Empirical Predictions (H3)

For reasoning gap types:
1. **Recursive structure gaps**: Performance scaling curve flattens early, asymptotes below threshold
2. **Compositional depth gaps**: Performance scaling follows smooth curve, can reach threshold with sufficient scale
3. **Working memory gaps**: Scales logarithmically with capacity (more parameters → slightly higher $m_{\text{capacity}}$)
4. **Abstraction gaps**: Training loss is better predictor than parameter count

---

## 6. Mitigation Framework

### Decision Framework for Interventions

Given a reasoning gap $G = (\mathcal{P}, \mathcal{M}, \mathcal{D}, \delta, \theta)$:

**Step 1: Classify gap type** (Types 1-6 above)

**Step 2: Determine gap scalability** (Scale-invariant, scale-dependent, training-dependent)

**Step 3: Select intervention**:

| Gap Type | Scalability | Recommended Intervention | Effectiveness |
|----------|-------------|-------------------------|---------------|
| Compositional (within TC⁰) | Scale-dependent | CoT + scaling | High |
| Compositional (beyond TC⁰) | Scale-invariant | Architectural: Recursive mechanisms | Required |
| Recursive structure | Scale-invariant | Architectural: Memory/stack | Required |
| Working memory | Scale-dependent | CoT externalization + tools | Medium-High |
| State transition | Training-dependent | CoT + explicit state tracking | High |
| Counterfactual | Scale-invariant | Fine-tuning + prompting | Low-Medium |
| Abstraction/transfer | Training-dependent | Few-shot prompting + fine-tuning | Medium |

**Step 4: Validate empirically** with diagnostic benchmarks

---

## 7. Formal Connections to Hypotheses

### Hypothesis H1: LLM reasoning failures cluster around problems requiring unbounded working memory or recursive variable binding

**Formal statement**: For problem classes $\mathcal{P}$ with properties:
- Working memory load $m > m_{\text{capacity}}$ (Gap Type 3)
- Recursion depth $r = \omega(1)$ (Gap Type 2)

The reasoning gap $G = (\mathcal{P}, \text{AT}, \mathcal{D}, 0.20, 0.90)$ exists with high probability.

**Theoretical justification**:
- Transformers $\subseteq$ TC⁰ (Theorem 2.1)
- TC⁰ has constant depth, cannot handle unbounded recursion (Theorem 2.2)
- Attention entropy limits working memory (Wang et al., 2024)

### Hypothesis H2: Chain-of-thought closes gaps for problems reducible to serial composition but not for problems requiring true parallel/recursive decomposition

**Formal statement**:
- For $(T, \epsilon)$-serially decomposable problems with $T \leq T_{\text{max}}$: CoT closes gap (Theorem 4.2)
- For problems requiring parallel/recursive computation not efficiently serializable: CoT ineffective (Theorem 4.3)

**Theoretical justification**: CoT extends depth to $O(T)$ but maintains bounded depth, cannot handle problems requiring unbounded or exponential decomposition.

### Hypothesis H3: Reasoning gaps narrow predictably with scale for some problem classes but remain constant for others, and the distinction is theoretically characterizable

**Formal statement**:
- Scale-invariant gaps (Definition 5.1.1) exist for problems beyond TC⁰
- Scale-dependent gaps (Definition 5.1.2) exist for problems within TC⁰ but requiring large circuits
- The distinction is characterized by complexity-theoretic placement (Proposition 5.2)

**Theoretical justification**: Scaling increases circuit size within TC⁰ but cannot change fundamental depth/recursion limitations.

---

## 8. Next Steps

1. ✅ Define reasoning gap formally (Definition 1.4)
2. ✅ Characterize gap types with formal properties (Section 3)
3. ✅ Formalize CoT effectiveness conditions (Section 4)
4. ✅ Classify scale dependence (Section 5)
5. **NEXT**: Design diagnostic benchmarks instantiating each gap type
6. **NEXT**: Develop formal proofs for key theorems
7. **NEXT**: Connect to empirical evaluation plan

---

## References to Literature

**Core complexity theory**:
- [Merrill22-TC0]: Transformers ⊆ TC⁰
- [Strobl24-Survey]: Comprehensive expressiveness survey
- [Chiang23-Uniform]: Uniformity results

**Empirical gap evidence**:
- [MemCap24]: Working memory limits via attention entropy
- [CoT-Mirage]: CoT distribution dependence
- [Comp-Collapse]: Compositional reasoning failures
- [CF-Knowledge, Exec-CF]: Counterfactual reasoning gaps
- [Abstract-Reason]: Abstraction failures

**Scaling and emergence**:
- [Emergent-Abilities, Emergent-Survey]: Emergence phenomena
- [Exec-CF]: 72B scale persistence of gaps

**Mitigation strategies**:
- [LTM-Prompting]: Least-to-Most decomposition
- [Feedback-Memory]: Recursive architecture modifications
- [Memory-Tuning]: Formal limits of prompt tuning
