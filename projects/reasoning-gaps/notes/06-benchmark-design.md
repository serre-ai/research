# Diagnostic Benchmark Suite: ReasonGap

## Design Principles

Each benchmark task:
1. Has a **parameterized difficulty** (size n) with controlled scaling
2. Has a **known complexity classification** grounding the gap type
3. Has **algorithmic ground truth** (verifiable correct answers)
4. Has a **prediction** from our taxonomy about CoT effect and scaling behavior
5. Uses **exact-match or multiple-choice** evaluation (no ambiguity)
6. Is **novel enough** to avoid training data contamination (procedurally generated)

## Benchmark Tasks

### B1: Masked Majority (Sensitivity Gap — AC⁰ boundary)
- **Task**: Given a binary string of length n with some positions masked, determine the majority value among unmasked positions
- **Difficulty parameter**: n (string length), k (number of masked positions)
- **Complexity**: MAJORITY ∈ TC⁰ \ AC⁰
- **Format**: "Given string 10110?1?0, where ? are ignored, is the majority of visible bits 0 or 1?"
- **Prediction**: Without CoT, accuracy degrades with n. Short CoT (counting) should close the gap.
- **Contamination control**: Procedurally generated with random strings and mask positions

### B2: Nested Boolean Evaluation (Depth Gap — TC⁰/NC¹ boundary)
- **Task**: Evaluate a Boolean formula with nested AND/OR/NOT operations
- **Difficulty parameter**: d (nesting depth), w (formula width)
- **Complexity**: Boolean Formula Value ∈ NC¹ (NC¹-complete under AC⁰ reductions)
- **Format**: "Evaluate: NOT(AND(OR(T, F), NOT(AND(F, OR(T, T)))))"
- **Prediction**: Accuracy degrades with depth d, not width. O(log n) CoT steps should suffice. Performance cliff at depth > transformer's effective depth.
- **Contamination control**: Random formula generation with balanced depth trees

### B3: Iterated Permutation (Serial Composition Gap)
- **Task**: Apply a sequence of k permutations to an initial element and report the final position
- **Difficulty parameter**: k (number of compositions), m (domain size)
- **Complexity**: Iterated permutation composition requires Ω(k) sequential steps
- **Format**: "Starting at position 3, apply σ₁ then σ₂ then σ₃. Permutations: σ₁ = [2,4,1,3], σ₂ = [3,1,4,2], σ₃ = [4,3,2,1]. Final position?"
- **Prediction**: Accuracy degrades linearly with k. Requires O(k) CoT steps. Log CoT insufficient. Domain size m has secondary effect.
- **Contamination control**: Random permutations, variable domain sizes, variable chain lengths

### B4: State Tracking Machine (Serial Composition Gap — variant)
- **Task**: Simulate a simple finite automaton for k steps and report final state
- **Difficulty parameter**: k (number of transitions), s (number of states)
- **Complexity**: FSA simulation requires Ω(k) steps for constant-depth circuits
- **Format**: "Machine with states {A,B,C}, transitions: A→1→B, A→0→C, B→1→A, B→0→B, C→1→C, C→0→A. Start: A. Input: 10110. Final state?"
- **Prediction**: Same as B3 — accuracy degrades with k. CoT of length O(k) needed.
- **Contamination control**: Random transition tables, random input strings

### B5: Graph Reachability (Depth/Algorithmic Gap — NC¹/NL boundary)
- **Task**: Determine if there is a path from node s to node t in a directed graph
- **Difficulty parameter**: n (number of nodes), e (number of edges), d (graph diameter)
- **Complexity**: STCON ∈ NL (NL-complete). If TC⁰ ≠ NL, no constant-depth transformer can solve this.
- **Format**: "Edges: 1→2, 2→3, 3→5, 1→4, 4→5. Is there a path from 1 to 5? (Yes/No)"
- **Prediction**: Accuracy degrades with graph diameter. CoT helps but requires Ω(d) steps for diameter-d graphs.
- **Contamination control**: Erdős–Rényi random graphs with controlled density and planted paths

### B6: Dynamic Programming — Longest Increasing Subsequence (Algorithmic Gap)
- **Task**: Find the length of the longest increasing subsequence of a given sequence
- **Difficulty parameter**: n (sequence length)
- **Complexity**: LIS ∈ P (O(n log n) algorithm), but requires non-trivial algorithmic reasoning
- **Format**: "Sequence: [3, 1, 4, 1, 5, 9, 2, 6]. Length of longest increasing subsequence?"
- **Prediction**: Accuracy degrades with n. CoT helps moderately. Code/tool execution should dramatically outperform CoT.
- **Contamination control**: Random integer sequences with controlled range

### B7: 3-SAT at Phase Transition (Intractability Gap)
- **Task**: Determine satisfiability of a 3-SAT formula near the phase transition (clause-to-variable ratio α ≈ 4.27)
- **Difficulty parameter**: n (number of variables), α (clause ratio)
- **Complexity**: 3-SAT is NP-complete
- **Format**: "Variables: x1, x2, x3, x4. Clauses: (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x4 ∨ x2) ∧ ... Is this satisfiable? (Yes/No)"
- **Prediction**: Accuracy degrades sharply at α ≈ 4.27. CoT provides no systematic improvement at the phase transition. Easy instances (α << 4.27 or α >> 4.27) may be solved.
- **Contamination control**: Random 3-SAT instances with controlled α, seeded generation

### B8: String Reversal Inference (Architectural Gap)
- **Task**: Given "The capital of Freedonia is Xanadu", answer "Which country has capital Xanadu?"
- **Difficulty parameter**: Number of distractor facts, novelty of entities
- **Complexity**: Not a complexity-class issue — this is an autoregressive structural limitation
- **Format**: Present facts in A→B direction, query in B→A direction with novel entities
- **Prediction**: Accuracy should be significantly lower for reversed queries regardless of CoT, model size, or problem "complexity". The gap is constant, not scaling with n.
- **Contamination control**: Fictional entities, procedurally generated facts

### B9: Negation Sensitivity (Architectural Gap — variant)
- **Task**: Answer the same question with and without negation, verify consistency
- **Difficulty parameter**: Negation depth (single, double, triple negation)
- **Format**: "Is it true that it is NOT the case that NOT all birds can fly?" paired with equivalent positive statement
- **Prediction**: Accuracy degrades with negation depth. CoT may help with explicit negation tracking but the gap persists for implicit negation.
- **Contamination control**: Procedurally generated propositions with controlled negation structure

## Evaluation Protocol

### Models
- **Proprietary**: Claude (Haiku, Sonnet, Opus), GPT (4o-mini, 4o, o3)
- **Open-source**: Llama 3.x (8B, 70B), Mistral (7B, Large), Qwen (7B, 72B)
- Total: ~12 model configurations

### Conditions per task
1. **Direct** (no CoT): Force immediate answer
2. **Short CoT**: "Think step by step" (unconstrained)
3. **Budget CoT**: Fixed CoT token budgets (log n, n, n², tokens)
4. **Tool-augmented**: Allow code execution (for B6, B7)

### Metrics
- Accuracy (exact match) at each difficulty level n
- **Gap score**: Rate of accuracy degradation as f(n) — fit to constant, log, linear, exponential decay
- **CoT lift**: Difference between direct and CoT accuracy
- **Scale sensitivity**: Accuracy difference between smallest and largest model in each family

### Instance counts
- 100 instances per difficulty level per task
- 5 difficulty levels per task (scaling from easy to hard)
- Total: ~100 × 5 × 9 tasks × 4 conditions × 12 models = ~216,000 evaluations
- Estimated API cost: ~$100–150 for proprietary models
- Estimated GPU time: ~48–72 hours on A100 for open-source models

## Expected Results Pattern

```
Task          | Direct | Short CoT | Budget CoT | Tool Use
──────────────┼────────┼───────────┼────────────┼─────────
B1 Majority   |  ↓↓    |   ↑↑      |    ↑↑      |   N/A
B2 Bool Eval  |  ↓↓↓   |   ↑↑      |    ↑↑      |   N/A
B3 Perm Comp  |  ↓↓↓   |   ↑       |    ↑↑↑     |   ↑↑
B4 State Track|  ↓↓↓   |   ↑       |    ↑↑↑     |   ↑↑
B5 Graph Reach|  ↓↓    |   ↑       |    ↑↑      |   ↑↑
B6 LIS        |  ↓↓    |   ↑       |    ↑       |   ↑↑↑
B7 3-SAT      |  ↓↓↓   |   ↗       |    ↗       |   ↑↑↑
B8 Reversal   |  ↓     |   →       |    →       |   N/A
B9 Negation   |  ↓↓    |   ↑       |    ↑       |   N/A

↓ = degrades with n, ↑ = improves, → = no change, ↗ = marginal
```

The key empirical predictions:
1. CoT lift is largest for Types 2–3, moderate for Type 1, minimal for Types 5–6
2. Tool use dominates CoT for Type 4 (algorithmic) tasks
3. Type 5 (intractability) shows phase-transition behavior at α ≈ 4.27
4. Type 6 (architectural) gaps are constant regardless of intervention
5. Required CoT budget matches theoretical prediction (log n for Type 2, linear n for Type 3)
