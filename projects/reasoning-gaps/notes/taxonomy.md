# Taxonomy of Reasoning Gaps in Large Language Models

**Project**: reasoning-gaps
**Date**: 2026-03-11
**Status**: In development

---

## Overview

This taxonomy organizes reasoning gaps according to three complementary perspectives:

1. **Complexity-theoretic**: What computational complexity class is required?
2. **Architectural**: What architectural constraint causes the failure?
3. **Empirical**: What observable failure patterns manifest?

Each gap type is characterized across all three perspectives, providing a unified framework for understanding, predicting, and addressing reasoning limitations.

---

## Taxonomy Structure

```
Reasoning Gaps
│
├── Computational Gaps (architectural limits)
│   ├── Compositional Depth Gaps
│   ├── Recursive Structure Gaps
│   └── Parallel Processing Gaps
│
├── Resource Gaps (capacity/scale limits)
│   ├── Working Memory Gaps
│   ├── State Transition Gaps
│   └── Long-Range Dependency Gaps
│
└── Distributional Gaps (training-dependent)
    ├── Counterfactual Reasoning Gaps
    ├── Abstraction & Transfer Gaps
    └── Compositional Generalization Gaps
```

---

## I. Computational Gaps (Architectural Limits)

These gaps arise from fundamental computational complexity constraints. They are **scale-invariant**: increasing model size within the transformer architecture will not close them.

### 1.1 Compositional Depth Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Sequential composition requiring depth $d = \omega(1)$
- **Required complexity**: Depth-$d$ circuits
- **Transformer bound**: TC⁰ (constant depth)
- **Gap**: Problems requiring superconstant depth beyond TC⁰

**Architectural constraint**:
- Fixed number of layers $L$ limits sequential computation depth
- Each layer performs one "step" of computation
- Cannot perform unbounded sequential operations in single forward pass

**Empirical manifestations**:
- Performance degrades as compositional chain length increases
- Sharp degradation beyond threshold depth $d_{\text{crit}} \approx 5-7$ operations
- Errors accumulate with increasing depth
- Models may shortcut (skip intermediate steps) or hallucinate steps

**Formal properties**:
```
Problem: f_d ∘ f_{d-1} ∘ ⋯ ∘ f_1(x)
Property: d = depth of composition
Gap exists when: d > d_crit ≈ O(L) for L layers
Complexity: If d = ω(1), may require depth > TC⁰
```

**Example tasks**:
1. **Function composition**: Apply function $f$ exactly $k$ times where $k > d_{\text{crit}}$
   - $f^{(10)}(x) = f(f(f(f(f(f(f(f(f(f(x))))))))))$
   - Input: $x = 2$, $f(x) = x + 1$
   - Expected: $f^{(10)}(2) = 12$

2. **Multi-hop reasoning**: Chain of $k$ logical deductions
   - Premise 1: A → B
   - Premise 2: B → C
   - ...
   - Premise $k$: Y → Z
   - Question: Does A imply Z? (requires $k$-hop chain)

3. **Iterative algorithms**: Simulate $k$ iterations
   - GCD via Euclidean algorithm with $k > d_{\text{crit}}$ iterations
   - Iterative numerical methods

**CoT mitigation potential**: **HIGH**
- CoT extends effective depth by $T$ steps
- Can solve problems with $d \leq T$ if each step within TC⁰
- Limitation: $T$ bounded by context length, error accumulation

**Scale dependence**: **Partially scale-dependent**
- Within TC⁰: Scale helps (larger circuits, better approximations)
- Beyond TC⁰: Scale-invariant (architectural limit)

---

### 1.2 Recursive Structure Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Hierarchical tree structures requiring depth $r = \omega(1)$
- **Required complexity**: NC¹ (log-depth circuits for parallel tree reduction)
- **Transformer bound**: TC⁰ (constant depth, cannot do unbounded tree reduction)
- **Gap**: Problems requiring recursive decomposition beyond constant depth

**Architectural constraint**:
- Transformers process sequences linearly, not hierarchically
- No explicit stack or recursion mechanism
- Tree structures must be flattened to sequences
- Cannot efficiently perform parallel tree reduction

**Empirical manifestations**:
- Failures on deeply nested structures (parentheses, brackets, trees)
- Cannot evaluate nested Boolean formulas beyond shallow depth
- Struggles with recursive programs or fractal patterns
- Position-based rather than structure-based processing

**Formal properties**:
```
Problem: Binary tree evaluation T with depth r and branching b
Property: r = depth, b = branching factor
Gap exists when: r = ω(1) (superconstant depth)
Complexity: NC¹ (log-depth parallel reduction)
TC⁰ limitation: Constant depth insufficient for recursive reduction
```

**Example tasks**:
1. **Nested Boolean formula evaluation**:
   - $((A \land B) \lor ((C \land D) \land (E \lor F)))$
   - Depth $r = 4$: requires 4 levels of reduction
   - TC⁰ can handle $r = O(1)$, fails for $r = \omega(1)$

2. **Tree arithmetic**:
   - Binary tree with values at leaves, operators at internal nodes
   - Depth $r$: compute result via bottom-up evaluation
   - Parallel reduction: $O(r)$ depth
   - Sequential: $O(2^r)$ steps

3. **Recursive program evaluation**:
   - Fibonacci: `fib(n) = fib(n-1) + fib(n-2)`
   - For $n > $ small threshold, requires recursive call tree
   - Exponential number of calls without memoization

4. **Balanced parentheses**:
   - Check if deeply nested parentheses are balanced
   - Requires stack-like processing
   - Depth = maximum nesting level

**CoT mitigation potential**: **LOW-MEDIUM**
- Can serialize tree traversal (DFS, BFS)
- But serialization requires $O(|T|)$ steps where $|T|$ = tree size
- For depth $r$ and branching $b$: $|T| = O(b^r)$ (exponential)
- Context length limits practical tree size

**Scale dependence**: **Scale-invariant** (Architectural)
- Fundamental limitation: constant depth vs. recursive structure
- Increasing parameters doesn't add recursive capability
- Requires architectural modification (explicit stack, recursion)

---

### 1.3 Parallel Processing Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Tasks requiring simultaneous parallel operations
- **Required complexity**: Depends on task, often NC¹ or P
- **Transformer bound**: TC⁰ (can do some parallelism via threshold gates)
- **Gap**: Problems requiring coordination of many parallel operations

**Architectural constraint**:
- Self-attention provides some parallelism (all positions attend to all others)
- But coordination limited by constant depth
- Cannot simulate massive parallel computation efficiently

**Empirical manifestations**:
- Struggles with problems requiring "looking at all parts simultaneously"
- Cannot efficiently solve NP-complete problems (as expected)
- Difficulties with constraint satisfaction requiring global view

**Formal properties**:
```
Problem: Parallel operations on n elements requiring coordination
Property: Degree of parallelism p and coordination depth d
Gap exists when: p is large and coordination depth d = ω(1)
Example: Constraint satisfaction with global constraints
```

**Example tasks**:
1. **Graph problems**: Shortest path in large graphs requiring parallel edge relaxation
2. **Constraint satisfaction**: Sudoku, SAT with global constraints
3. **Parallel reduction**: Summing large array (TC⁰ can do via threshold gates, but complex coordination harder)

**CoT mitigation potential**: **LOW**
- Serializing parallel computation often requires exponential blowup
- CoT inherently sequential

**Scale dependence**: **Scale-invariant** (Architectural)
- Fundamental parallelism vs. depth trade-off

---

## II. Resource Gaps (Capacity/Scale Limits)

These gaps arise from bounded resources (memory, attention, capacity). They are **scale-dependent**: increasing model size can help, though with diminishing returns.

### 2.1 Working Memory Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Problems within TC⁰ but requiring tracking $m$ simultaneous bindings
- **Required complexity**: TC⁰ (theoretically sufficient)
- **Transformer bound**: Attention entropy limits effective $m$ (Wang et al., 2024)
- **Gap**: Practical working memory limit $m_{\text{capacity}} \approx 7 \pm 2$

**Architectural constraint**:
- Attention scores must sum to 1 (softmax normalization)
- Tracking $m$ items requires splitting attention across $m$ positions
- High $m$ → attention dispersion → high entropy → information loss
- Scarcity of attentional resources, not storage

**Empirical manifestations**:
- N-back task performance degrades with $N$
- Failures when tracking many entities simultaneously
- Confusion between similar variables/entities
- Better performance when information externalized (written in context)

**Formal properties**:
```
Problem: Track m distinct variable bindings simultaneously
Property: m = working memory load
Gap exists when: m > m_capacity ≈ 7 ± 2 (empirical)
Architectural cause: Attention entropy H(A) increases with m
Performance: Degrades gradually as m increases
```

**Example tasks**:
1. **N-back task**: Remember item from N positions ago
   - $N = 3$: Track last 3 items (within capacity)
   - $N = 10$: Track last 10 items (exceeds capacity)
   - Performance drops significantly as $N$ increases

2. **Multi-entity state tracking**:
   - Track states of $m$ characters in a story
   - Each character has location, emotional state, knowledge
   - $m = 3$ characters: manageable
   - $m = 10$ characters: frequent confusion

3. **Variable binding in programs**:
   - Track values of $m$ variables through program execution
   - `x = 5, y = 7, z = x + y, w = z * 2, ...`
   - Errors increase with number of active variables

4. **Constraint tracking**:
   - Remember $m$ constraints while solving problem
   - $m$ small: high accuracy
   - $m$ large: constraint violations

**CoT mitigation potential**: **HIGH**
- Externalizing working memory to text very effective
- Write down variable bindings, entity states explicitly
- Reduces attention entropy by creating persistent records
- Limitation: Context length still bounded

**Scale dependence**: **Weakly scale-dependent**
- Larger models have slightly higher $m_{\text{capacity}}$
- But logarithmic scaling: doubling parameters doesn't double capacity
- Fundamental attention entropy constraint remains

---

### 2.2 State Transition Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Finite state machines, temporal reasoning
- **Required complexity**: Regular languages (finite automata), within TC⁰
- **Transformer bound**: Theoretically sufficient
- **Gap**: Lack of persistent latent state (Liu et al., 2025)

**Architectural constraint**:
- Transformers are stateless functions: $f(x) = y$
- No internal state preserved between calls
- Must rely on explicit context (manifest state in text)
- Cannot maintain implicit state across turns

**Empirical manifestations**:
- Failures on tasks requiring state machine simulation
- Cannot maintain conversation state without re-prompting
- Struggles with temporal reasoning requiring state tracking
- Better when state explicitly written out

**Formal properties**:
```
Problem: Simulate finite automaton with |S| states, s transitions
Property: |S| = state space size, s = number of transitions
Gap exists when: |S| is large or transitions implicit
Architectural cause: No persistent latent state, must use manifest context
Performance: Degrades with state space size and transition complexity
```

**Example tasks**:
1. **Finite automaton simulation**:
   - Given FSA with $|S|$ states and input string
   - Simulate transitions, report final state
   - Small $|S|$: accurate
   - Large $|S|$ or complex transition function: errors

2. **Game state tracking**:
   - Chess: Track board state through move sequence
   - Must maintain accurate state representation
   - Errors accumulate with longer game sequences

3. **Conversation state**:
   - Multi-turn dialogue requiring state persistence
   - Example: "Remember preference X" in turn 1, recall in turn 5
   - Failures when state not explicitly in recent context

4. **Temporal reasoning**:
   - Event sequences with state changes
   - "After event A, state is X. After event B, state becomes Y."
   - Track state evolution over time

**CoT mitigation potential**: **VERY HIGH**
- Explicit state externalization highly effective
- Write current state after each transition
- Makes implicit state explicit in text
- Near-complete mitigation when state fully externalized

**Scale dependence**: **Training-dependent**
- Models can learn to externalize state if trained appropriately
- Scale helps with learning this strategy
- Not fundamental architectural limitation

---

### 2.3 Long-Range Dependency Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Problems requiring information integration across long distances in sequence
- **Required complexity**: Depends on task, often within TC⁰
- **Transformer bound**: Self-attention can theoretically access any position
- **Gap**: Practical limitations from attention dilution, position bias

**Architectural constraint**:
- Attention scores decrease with distance (typical learned pattern)
- Position embeddings may not generalize to unseen distances
- Softmax entropy increases with sequence length
- Quadratic complexity limits practical context length

**Empirical manifestations**:
- Worse performance on information far from query position
- Position bias: better at beginning/end, worse in middle
- "Lost in the middle" phenomenon
- Failures on tasks requiring global context integration

**Formal properties**:
```
Problem: Integrate information from positions separated by distance d
Property: d = maximum dependency distance
Gap exists when: d exceeds effective attention range
Architectural cause: Attention dilution, position bias
Performance: Degrades with distance d
```

**Example tasks**:
1. **Long-range coreference**:
   - Resolve pronoun to antecedent $d$ tokens away
   - Performance decreases with $d$

2. **Document-level QA**:
   - Answer requires information from multiple distant locations
   - Challenging when information spread across long document

3. **Long-context reasoning**:
   - "Needle in haystack" tests
   - Find and integrate information from very long contexts

**CoT mitigation potential**: **MEDIUM**
- Can help by explicitly retrieving and restating distant information
- Brings long-range dependencies into local context

**Scale dependence**: **Scale-dependent**
- Larger context windows help (architectural scaling)
- Better position embeddings with scale
- But still bounded by practical context limits

---

## III. Distributional Gaps (Training-Dependent)

These gaps arise from mismatches between training and test distributions. They are **training-dependent**: improved training data or fine-tuning can close them.

### 3.1 Counterfactual Reasoning Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Reasoning about hypothetical scenarios contradicting world knowledge
- **Required complexity**: Within TC⁰ (no additional computational complexity)
- **Transformer bound**: Sufficient computational power
- **Gap**: Cannot dynamically modify internal world model (parametric knowledge)

**Architectural constraint**:
- World knowledge encoded in parameters from training
- No mechanism for temporary knowledge override
- Cannot create "sandbox" world model for counterfactuals
- Two failure modes:
  - **Context-ignoring**: Revert to parametric knowledge, ignore counterfactual premise
  - **Context-overfitting**: Blindly follow prompt without reasoning

**Empirical manifestations**:
- 25-40% accuracy drop from interventional to counterfactual reasoning (Miller et al., 2024)
- Reversion to factual knowledge even when instructed otherwise
- "If gravity were repulsive..." → still describes attractive gravity
- Struggles with alternate history, physics, or rules

**Formal properties**:
```
Problem: Given factual knowledge K and counterfactual premise P
Task: Reason about world K' = K \ K_conflict ∪ P
Property: c_dist = |K_conflict| (amount of knowledge to override)
Gap exists when: c_dist is large or conflicts are deep
Architectural cause: No dynamic knowledge modification mechanism
Performance: 25-40% drop from factual to counterfactual
```

**Example tasks**:
1. **Counterfactual physics**:
   - "If gravity were repulsive instead of attractive, how would planets move?"
   - Requires overriding deep physical knowledge
   - Models often revert to factual gravity behavior

2. **Alternate history**:
   - "If the Roman Empire never fell, what would modern Europe look like?"
   - Requires modifying historical knowledge and downstream implications
   - Struggles with consistent alternate timeline

3. **Rule modification**:
   - "In a version of chess where pawns move backwards, what strategy should White use?"
   - Requires temporarily overriding chess rules
   - Often reverts to standard chess reasoning

4. **Hypothetical scenarios**:
   - "If humans could photosynthesize, how would society differ?"
   - Requires systematic modification of biological and social facts

**CoT mitigation potential**: **LOW-MEDIUM**
- Can help by explicitly listing modified facts
- But strong parametric knowledge still causes reversion
- Fluent counterfactual reasoning often logically inconsistent

**Scale dependence**: **Training-dependent**
- Fine-tuning on counterfactual examples can help
- Instruction-tuning to follow hypothetical premises
- Not fundamentally scale-dependent (architectural issue: no dynamic knowledge editing)
- Possible mitigation: Retrieval-augmented generation with counterfactual databases

---

### 3.2 Abstraction & Transfer Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Problems with identical logical structure but different surface features
- **Required complexity**: Same as underlying logical structure (often within TC⁰)
- **Transformer bound**: Sufficient computational power
- **Gap**: Training distribution dependence, pattern matching vs. abstract reasoning

**Architectural constraint**:
- Models learn statistical patterns from training data
- Surface features entangled with logical structure
- No explicit separation of form and content
- "Content effect": Better performance on familiar topics (Kumar et al., 2024)

**Empirical manifestations**:
- Worse performance on unfamiliar content domains
- Logic puzzles: Familiar content (people, places) >> abstract symbols
- Mathematical reasoning: Standard notation >> unusual notation
- Confirmation bias toward training distribution patterns

**Formal properties**:
```
Problem: Isomorphic problems P1 ≅ P2 with different surface features
Property: Δ_dist = distribution distance between surface features
Gap exists when: Δ_dist is large (unfamiliar content)
Architectural cause: No explicit abstraction mechanism, pattern matching
Performance: Degrades with Δ_dist (content effect)
```

**Example tasks**:
1. **Logic puzzles with varying content**:
   - **Familiar**: "If Alice is taller than Bob, and Bob is taller than Carol, who is shortest?"
   - **Abstract**: "If △ >ₕ ○, and ○ >ₕ □, which has minimum h value?"
   - Same logical structure, different surface features
   - Performance significantly worse on abstract version

2. **Mathematical reasoning with unusual notation**:
   - **Standard**: "Solve: 2x + 3 = 7"
   - **Unusual**: "Solve: 2⊗x ⊕ 3 = 7 where ⊗ is multiplication, ⊕ is addition"
   - Same computation, unfamiliar symbols
   - Performance drop despite equivalent problem

3. **Analogical reasoning**:
   - Transfer solution pattern from familiar to unfamiliar domain
   - "A is to B as C is to ?" with unfamiliar concepts
   - Struggles when analogy involves out-of-distribution content

4. **Cross-lingual reasoning**:
   - Same logical problem in different languages
   - Performance varies by language representation in training

**CoT mitigation potential**: **MEDIUM-HIGH**
- Few-shot prompting with similar examples helps significantly
- Provides in-distribution patterns to anchor on
- Explicit abstraction instructions ("Ignore the content, focus on structure")
- Limitation: Requires good exemplars in prompt

**Scale dependence**: **Training-dependent**
- Fine-tuning on diverse content domains helps
- More diverse pre-training data reduces content effect
- Instruction-tuning for "abstract reasoning" mode
- Scale helps indirectly via more diverse training data

---

### 3.3 Compositional Generalization Gaps

**Complexity-theoretic characterization**:
- **Problem class**: Novel combinations of familiar components
- **Required complexity**: Often within TC⁰
- **Transformer bound**: Sufficient computational power for individual components
- **Gap**: Training distribution doesn't cover combinatorial space

**Architectural constraint**:
- Training on subset of compositional space
- Combinatorial explosion: Cannot cover all combinations
- Models learn specific compositions seen in training
- Fail on novel combinations (Zhang et al., 2025)

**Empirical manifestations**:
- Dramatic failure on novel compositions: 100% → 0% accuracy (Zhang et al., 2025)
- Success on seen transformations, failure on unseen combinations
- Fluent but incorrect outputs (hallucinated reasoning)
- Length generalization failures

**Formal properties**:
```
Problem: Composition of primitives P = f_n ∘ ⋯ ∘ f_1
Training: Covers subset C_train ⊂ All compositions
Test: Sample from C_test where C_test ∩ C_train may be small
Property: Δ_comp = composition distance from training
Gap exists when: Δ_comp is large (novel composition)
Architectural cause: Memorization of training compositions
Performance: Severe degradation (100% → 0%) on novel compositions
```

**Example tasks**:
1. **Function composition generalization** (Zhang et al., 2025):
   - Train on: $f_1 \circ f_2$, $f_2 \circ f_3$, $f_3 \circ f_1$
   - Test on: $f_1 \circ f_3$ (novel combination)
   - Result: 100% train accuracy → 0% test accuracy

2. **Semantic parsing**:
   - Train on: "Show flights to Boston", "Show flights from Denver"
   - Test on: "Show flights from Boston to Denver" (novel composition)
   - Failure despite seeing all component phrases

3. **Multi-hop reasoning with novel paths**:
   - Train on: A→B→C, B→D→E paths
   - Test on: A→D→E path (novel composition of seen relations)
   - Fails even though all individual relations seen

4. **Instruction following**:
   - Train on individual instructions: "Sort list", "Remove duplicates"
   - Test on: "Sort list then remove duplicates" (novel composition)
   - May fail or execute in wrong order

**CoT mitigation potential**: **LOW-MEDIUM**
- CoT helps if it provides in-distribution decomposition examples
- But on truly novel compositions, CoT steps are fluent but wrong
- "Pseudo-reasoning": Looks like reasoning but doesn't solve problem
- Least-to-Most prompting helps on some tasks, not universally (Zhou et al., 2024)

**Scale dependence**: **Training-dependent**
- More training data covering more compositions helps
- But combinatorial space grows exponentially
- Cannot exhaustively cover all compositions via scale alone
- Possible mitigation: Meta-learning, compositional training curricula, systematic generalization training

---

## Cross-Cutting Analysis

### Gap Interactions

Reasoning gaps often interact and compound:

1. **Compositional + Working Memory**: Long compositional chains requiring simultaneous tracking of intermediate results
   - Example: Nested function application with state
   - Compounds both gap types

2. **Recursive + Abstraction**: Recursive structures with unfamiliar content
   - Example: Tree evaluation with abstract symbols
   - Worse than either gap alone

3. **Counterfactual + Compositional**: Chained reasoning in counterfactual world
   - Example: Multi-step physics prediction with modified laws
   - Reversion to factual knowledge at any step breaks chain

### Universal Patterns

Across gap types, common patterns emerge:

1. **Threshold effects**: Performance often exhibits sharp transitions
   - Below threshold: high accuracy
   - Above threshold: rapid degradation
   - Examples: Compositional depth ~5-7, working memory ~7±2

2. **Error accumulation**: Multi-step tasks show compounding errors
   - Each step has error rate ε
   - After T steps: total error ≈ Tε (if independent)
   - Can be worse if errors cascade

3. **Distribution sensitivity**: Performance highly dependent on:
   - Training distribution overlap
   - Surface feature similarity
   - Format/prompt alignment

4. **Externalization helps**: Making implicit explicit reduces gaps
   - CoT externalizes intermediate steps
   - Explicit state tracking
   - Tool use for working memory

---

## Diagnostic Framework

### How to Classify a Reasoning Failure

Given an observed failure, classify by:

**Step 1: Identify computational requirements**
- Does problem require depth > O(1)? → Compositional or Recursive gap
- Recursive structure? → Recursive gap
- Parallel coordination? → Parallel gap

**Step 2: Check resource constraints**
- Tracking many variables? → Working Memory gap
- State machine simulation? → State Transition gap
- Long-range dependencies? → Long-Range Dependency gap

**Step 3: Assess distribution factors**
- Counterfactual scenario? → Counterfactual gap
- Unfamiliar content? → Abstraction gap
- Novel composition? → Compositional Generalization gap

**Step 4: Test scalability**
- Persists across model sizes? → Likely architectural (computational gap)
- Improves with scale? → Likely resource gap
- Fixable with fine-tuning? → Likely distributional gap

---

## Summary Table

| Gap Type | Category | Complexity | Scale Dependence | CoT Mitigation | Key Reference |
|----------|----------|------------|-----------------|----------------|---------------|
| Compositional Depth | Computational | Beyond TC⁰ if d=ω(1) | Partial | High | Comp-Collapse |
| Recursive Structure | Computational | NC¹ (depth ω(1)) | Invariant | Low | Merrill22-TC0 |
| Parallel Processing | Computational | Varies | Invariant | Low | - |
| Working Memory | Resource | Within TC⁰ | Weak | High | MemCap24 |
| State Transition | Resource | Within TC⁰ | Training | Very High | LatentPersist25 |
| Long-Range Dependency | Resource | Within TC⁰ | Scale | Medium | - |
| Counterfactual | Distributional | Within TC⁰ | Training | Low-Medium | CF-Knowledge, Exec-CF |
| Abstraction/Transfer | Distributional | Within TC⁰ | Training | Medium-High | Abstract-Reason |
| Comp. Generalization | Distributional | Within TC⁰ | Training | Low-Medium | CoT-Mirage |

---

## Next Steps

1. ✅ Define taxonomy structure
2. ✅ Characterize each gap type across three perspectives
3. ✅ Identify interactions and universal patterns
4. **NEXT**: Design diagnostic benchmark tasks instantiating each type
5. **NEXT**: Develop evaluation metrics for each gap type
6. **NEXT**: Plan empirical evaluation across model families

---

## References

All references from literature-review.md apply. Key citations for each gap type noted in table above.
