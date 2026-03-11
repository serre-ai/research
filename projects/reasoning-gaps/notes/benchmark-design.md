# Diagnostic Benchmark Design: Reasoning Gap Evaluation

**Project**: reasoning-gaps
**Date**: 2026-03-11
**Status**: Design phase

---

## Design Principles

### Requirements (from CLAUDE.md)
1. **Known ground truth**: All tasks must have computable, verifiable correct answers
2. **Controlled difficulty parameters**: Systematic variation to isolate effects
3. **Minimal data contamination risk**: Synthetic generation, not from public datasets
4. **Gap type isolation**: Each benchmark targets specific gap type from taxonomy

### Evaluation Metrics

**Primary metrics**:
- **Exact Match (EM)**: Binary correctness (0 or 1)
- **Partial Credit**: Task-specific scoring (e.g., edit distance, component correctness)

**Secondary metrics**:
- **Error type classification**: Categorize failures (shortcuts, hallucinations, etc.)
- **Scaling curves**: Performance vs. difficulty parameter
- **Confidence calibration**: Model confidence vs. actual accuracy

### Benchmark Structure

Each benchmark consists of:
1. **Task family**: General problem class
2. **Difficulty parameters**: Controllable variables (depth, width, count, etc.)
3. **Instance generation**: Deterministic algorithm for creating test cases
4. **Ground truth computation**: Algorithm for correct answer
5. **Evaluation procedure**: Scoring method
6. **Baseline expectations**: Predicted performance based on gap theory

---

## Benchmark Suite Overview

| ID | Benchmark Name | Gap Type | Key Parameter | Range | Expected Difficulty |
|----|----------------|----------|---------------|-------|---------------------|
| B1 | Function Composition Chain | Compositional Depth | Chain length $d$ | 1-20 | Sharp drop at $d \approx 5-7$ |
| B2 | Nested Boolean Formulas | Recursive Structure | Tree depth $r$ | 1-10 | Degradation with $r$, floor early |
| B3 | Multi-Entity State Tracking | Working Memory | Entity count $m$ | 1-15 | Gradual drop after $m \approx 7$ |
| B4 | Finite Automaton Simulation | State Transition | State count $\|S\|$ | 2-20 | Degradation with $\|S\|$ |
| B5 | Counterfactual Physics | Counterfactual | Conflict depth $c$ | 1-5 | 25-40% drop from factual |
| B6 | Abstract Logic Puzzles | Abstraction/Transfer | Content distance $\Delta$ | 0-5 | Large gap familiar vs. abstract |
| B7 | Novel Function Composition | Comp. Generalization | Composition novelty | Seen/Unseen | Severe: 100% → 0% |
| B8 | Iterative Algorithm Trace | Compositional Depth | Iteration count $k$ | 1-30 | Similar to B1 |
| B9 | Tree Arithmetic Evaluation | Recursive Structure | Tree depth $r$, branching $b$ | varies | Similar to B2 |

---

## B1: Function Composition Chain

### Motivation
Tests compositional depth gaps (Type 1.1). Measures ability to apply sequential operations correctly.

### Task Description
Apply a simple function $f$ exactly $d$ times to input $x$, computing $f^{(d)}(x)$.

### Difficulty Parameters
- **Primary**: Chain length $d \in [1, 20]$
- **Secondary**: Function complexity $c \in \{\text{simple}, \text{moderate}, \text{complex}\}$

### Function Variants
1. **Simple**: $f(x) = x + 1$ (increment)
2. **Moderate**: $f(x) = 2x + 1$ (linear transform)
3. **Complex**: $f(x) = (x \mod 10) \cdot 2 + 1$ (modular arithmetic)

### Instance Format
```
Apply the function f(x) = x + 1 exactly 7 times to the input x = 3.

What is the result?
```

### Ground Truth
- $f^{(d)}(x)$ computed by $d$ applications of $f$
- For $f(x) = x + 1$: $f^{(d)}(x) = x + d$
- For $f(x) = 2x + 1$: Recursive or closed form

### Evaluation
- **Exact Match**: Final answer correct (integer comparison)
- **Partial Credit**: None (discrete answer)
- **Error Analysis**:
  - Off-by-one errors
  - Shortcuts (computing $x + d$ directly instead of iterating)
  - Arithmetic errors

### Expected Results
- **Prediction**: Sharp performance drop at $d_{\text{crit}} \approx 5-7$
- **CoT effect**: Should extend threshold to higher $d$ (test with/without CoT)
- **Scale effect**: Larger models slightly higher $d_{\text{crit}}$

### Dataset Size
- 10 instances per $d$ value
- 20 values of $d$ (1-20)
- 3 function variants
- **Total**: 600 instances

---

## B2: Nested Boolean Formulas

### Motivation
Tests recursive structure gaps (Type 1.2). Measures ability to evaluate hierarchical trees.

### Task Description
Evaluate a nested Boolean formula with variables assigned truth values.

### Difficulty Parameters
- **Primary**: Tree depth $r \in [1, 10]$
- **Secondary**: Branching factor $b \in \{2, 3\}$ (binary or ternary operators)
- **Tertiary**: Operator mix (only AND/OR vs. full Boolean)

### Formula Generation
1. Generate random binary tree of depth $r$
2. Internal nodes: Boolean operators $\{\land, \lor, \neg\}$
3. Leaves: Variables $\{A, B, C, \ldots\}$
4. Assign random truth values to variables

### Instance Format
```
Given the following truth values:
A = True, B = False, C = True, D = False

Evaluate the Boolean formula:
((A ∧ B) ∨ (C ∧ D))

What is the result (True or False)?
```

### Ground Truth
- Recursive evaluation from leaves up
- Standard Boolean logic semantics

### Evaluation
- **Exact Match**: True/False correct
- **Partial Credit**: For deeper trees, track which sub-formulas evaluated correctly
- **Error Analysis**:
  - Which depth level errors appear
  - Operator confusion
  - Variable substitution errors

### Expected Results
- **Prediction**: Performance degradation with depth $r$
- **Threshold**: $r \approx 4-5$ for significant errors
- **CoT effect**: Can help by explicitly evaluating sub-formulas, but exponential blowup for large $b$
- **Scale invariance**: Should see early plateau (architectural limit)

### Dataset Size
- 20 instances per $(r, b)$ combination
- 10 values of $r$ (1-10)
- 2 branching factors
- **Total**: 400 instances

---

## B3: Multi-Entity State Tracking

### Motivation
Tests working memory gaps (Type 2.1). Measures ability to track simultaneous variable bindings.

### Task Description
Track states of $m$ entities through a sequence of updates, then answer query about final states.

### Difficulty Parameters
- **Primary**: Entity count $m \in [1, 15]$
- **Secondary**: Update count $u \in [5, 10, 20]$
- **Tertiary**: Query complexity (single entity vs. comparison)

### Instance Format
```
You are tracking the locations of 5 people: Alice, Bob, Carol, Dave, and Eve.

Initial locations:
- Alice: Kitchen
- Bob: Bedroom
- Carol: Garden
- Dave: Living Room
- Eve: Garage

Updates:
1. Alice moves to the Bedroom
2. Bob moves to the Kitchen
3. Carol moves to the Living Room
4. Dave moves to the Garden
5. Eve moves to the Kitchen
6. Alice moves to the Garden
7. Bob moves to the Garage
8. Carol moves to the Kitchen

Question: Where is Alice now?
Answer: Garden

Question: Who is in the Kitchen?
Answer: Carol and Eve
```

### Ground Truth
- Simulate state updates sequentially
- Track all entity states
- Answer query from final state

### Evaluation
- **Exact Match**: Correct answer to query
- **Partial Credit**: For multi-part answers, fraction correct
- **Error Analysis**:
  - Confusion between entities
  - Outdated state (not tracking latest update)
  - Working memory overflow patterns

### Expected Results
- **Prediction**: Gradual degradation starting around $m \approx 7-8$
- **Working memory limit**: Performance should track human-like capacity
- **CoT effect**: High - explicit state writing should significantly help
- **Scale effect**: Weak - logarithmic improvement with parameters

### Dataset Size
- 10 instances per $(m, u)$ combination
- 15 entity counts × 3 update counts
- **Total**: 450 instances

---

## B4: Finite Automaton Simulation

### Motivation
Tests state transition gaps (Type 2.2). Measures ability to simulate state machines.

### Task Description
Simulate a finite automaton on an input string, report final state or accept/reject.

### Difficulty Parameters
- **Primary**: State count $|S| \in [2, 20]$
- **Secondary**: Alphabet size $|\Sigma| \in [2, 4]$
- **Tertiary**: Transition complexity (deterministic vs. pattern-based)

### Instance Format
```
Consider a finite automaton with states {q0, q1, q2, q3} and alphabet {a, b}.

Transitions:
- From q0 on 'a' → q1
- From q0 on 'b' → q0
- From q1 on 'a' → q2
- From q1 on 'b' → q0
- From q2 on 'a' → q3
- From q2 on 'b' → q1
- From q3 on 'a' → q3
- From q3 on 'b' → q0

Start state: q0
Accept states: {q3}

Simulate the automaton on input string: "aaab"

What is the final state?
Answer: q0

Is the string accepted?
Answer: No (q0 is not an accept state)
```

### Ground Truth
- Standard FSA simulation algorithm
- Track current state through transitions

### Evaluation
- **Exact Match**: Final state or accept/reject correct
- **Partial Credit**: Trace intermediate states, credit for correct partial trace
- **Error Analysis**:
  - At which transition errors appear
  - State confusion patterns

### Expected Results
- **Prediction**: Degradation with $|S|$, especially if transitions not explicit
- **CoT effect**: Very high - explicit state tracking should nearly eliminate gap
- **Scale effect**: Training-dependent - models can learn to externalize state

### Dataset Size
- 10 instances per $|S|$
- 19 state counts (2-20)
- **Total**: 190 instances

---

## B5: Counterfactual Physics Reasoning

### Motivation
Tests counterfactual reasoning gaps (Type 3.1). Measures ability to reason about modified world models.

### Task Description
Answer physics questions under counterfactual premise that modifies physical laws.

### Difficulty Parameters
- **Primary**: Conflict depth $c$ = number of dependent facts affected
- **Secondary**: Explicitness of counterfactual (clearly stated vs. implicit)

### Instance Format
```
[FACTUAL VERSION - Baseline]
In our universe, gravity is an attractive force.

Question: If you drop a ball from a height, what happens?
Answer: The ball falls downward toward the ground.

[COUNTERFACTUAL VERSION - Test]
Imagine a universe where gravity is a REPULSIVE force instead of attractive. In this universe, massive objects push away from each other rather than pull together.

Question: In this universe, if you drop a ball from a height, what happens?
Expected Answer: The ball would be pushed away from the Earth (upward).

Question: In this universe, would planets orbit stars?
Expected Answer: No, the repulsive gravity would push planets away from stars. No stable orbits would form as in our universe.
```

### Ground Truth
- Factual baseline: Standard physics
- Counterfactual: Modified physics with specified change
- Manually curated with expert validation

### Evaluation
- **Comparison metric**: Factual accuracy vs. counterfactual accuracy
- **Expected drop**: 25-40% based on literature
- **Error Analysis**:
  - Context-ignoring: Reverts to factual answer
  - Context-overfitting: Extreme/incorrect counterfactual reasoning
  - Partial modification: Some facts updated, others not

### Expected Results
- **Prediction**: Significant performance drop (25-40%)
- **CoT effect**: Low-medium - can help list modified facts but reversion persists
- **Scale effect**: Training-dependent - instruction tuning helps

### Dataset Size
- 50 factual-counterfactual pairs
- 5 conflict depths (1-5 dependent facts)
- **Total**: 100 instances (50 factual, 50 counterfactual)

---

## B6: Abstract Logic Puzzles

### Motivation
Tests abstraction and transfer gaps (Type 3.2). Measures content effect and abstract reasoning.

### Task Description
Solve isomorphic logic puzzles with varying content domains (familiar vs. abstract).

### Difficulty Parameters
- **Primary**: Content distance $\Delta \in [0, 5]$ (familiar → abstract)
- **Secondary**: Puzzle complexity (number of constraints)

### Content Levels
0. **Highly familiar**: People, common objects, everyday scenarios
1. **Somewhat familiar**: Less common but recognizable concepts
2. **Domain-specific**: Technical but learnable (chemistry, music theory)
3. **Unfamiliar**: Rare concepts or foreign cultural references
4. **Abstract symbols**: Letters, numbers, geometric shapes
5. **Novel symbols**: Made-up symbols like △, ⊕, ※

### Instance Format
```
[LEVEL 0 - Highly Familiar]
Alice, Bob, and Carol are standing in a line.
- Alice is taller than Bob.
- Bob is taller than Carol.

Who is the shortest?
Answer: Carol

[LEVEL 5 - Novel Symbols]
Three entities △, ○, and □ are ordered by property ℏ.
- △ has greater ℏ than ○.
- ○ has greater ℏ than □.

Which entity has minimum ℏ?
Answer: □
```

### Ground Truth
- Isomorphic logical structure
- Same inference steps required
- Only surface features differ

### Evaluation
- **Performance by level**: Track accuracy across content distance
- **Gap size**: Δ(accuracy) = Acc(level 0) - Acc(level 5)
- **Error analysis**: Type of errors at each level

### Expected Results
- **Prediction**: Significant content effect - performance drops with $\Delta$
- **Gap size**: 20-50% accuracy drop from familiar to abstract
- **CoT effect**: Medium - examples in prompt can reduce gap
- **Scale effect**: Training-dependent - diverse training helps

### Dataset Size
- 30 base puzzle templates
- 6 content levels (0-5)
- **Total**: 180 instances

---

## B7: Novel Function Composition (Compositional Generalization)

### Motivation
Tests compositional generalization gaps (Type 3.3). Measures systematic generalization to novel combinations.

### Task Description
Learn primitive functions from examples, then compose them in novel ways.

### Difficulty Parameters
- **Primary**: Composition novelty (seen in training vs. completely novel)
- **Secondary**: Composition depth

### Setup
- **Primitive functions**: $f_1, f_2, f_3$ (e.g., add 1, double, square)
- **Training compositions**: Subset of all possible 2-function compositions
  - Seen: $f_1 \circ f_2, f_2 \circ f_3, f_3 \circ f_1$
- **Test compositions**: Novel combinations
  - Unseen: $f_1 \circ f_3, f_2 \circ f_1, f_3 \circ f_2$

### Instance Format
```
[TRAINING EXAMPLES PROVIDED IN PROMPT]
You are given the following functions:
- f1(x) = x + 1
- f2(x) = 2 * x
- f3(x) = x * x

Examples:
- f1(f2(3)) = f1(6) = 7
- f2(f3(3)) = f2(9) = 18
- f3(f1(3)) = f3(4) = 16

[TEST - SEEN COMPOSITION]
Compute: f1(f2(5))
Answer: f1(10) = 11

[TEST - UNSEEN COMPOSITION]
Compute: f2(f1(5))
Answer: f2(6) = 12

[Expected: High accuracy on seen, low on unseen if gap exists]
```

### Ground Truth
- Correct function composition by definition

### Evaluation
- **Accuracy by composition type**:
  - Seen during training (in prompt examples)
  - Unseen but simple
  - Unseen and novel
- **Gap magnitude**: Acc(seen) - Acc(unseen)

### Expected Results
- **Prediction**: Severe gap on novel compositions (literature: 100% → 0%)
- **CoT effect**: Low - generates fluent but incorrect reasoning
- **Scale effect**: Training-dependent - systematic generalization training needed

### Dataset Size
- 10 primitive function sets
- 6 compositions each (3 seen, 3 unseen)
- **Total**: 60 instances

---

## B8: Iterative Algorithm Trace

### Motivation
Alternative test for compositional depth gaps (Type 1.1) using familiar algorithmic context.

### Task Description
Trace execution of iterative algorithm (e.g., GCD, Fibonacci) for $k$ iterations.

### Difficulty Parameters
- **Primary**: Iteration count $k \in [1, 30]$
- **Secondary**: Algorithm complexity

### Algorithms
1. **Simple**: Euclidean GCD
2. **Moderate**: Iterative Fibonacci
3. **Complex**: Collatz sequence

### Instance Format
```
Trace the Euclidean GCD algorithm for inputs a = 48, b = 18.

Algorithm:
while b ≠ 0:
    temp = b
    b = a mod b
    a = temp

Iteration 1: a = 48, b = 18
  temp = 18
  b = 48 mod 18 = 12
  a = 18

Iteration 2: a = 18, b = 12
  temp = 12
  b = 18 mod 12 = 6
  a = 12

Iteration 3: a = 12, b = 6
  temp = 6
  b = 12 mod 6 = 0
  a = 6

Result: GCD(48, 18) = 6

Question: What is the final value?
Answer: 6

Question: How many iterations were executed?
Answer: 3
```

### Ground Truth
- Execute algorithm, record all intermediate states
- Count iterations

### Evaluation
- **Exact Match**: Final result and iteration count
- **Partial Credit**: Trace correctness per iteration

### Expected Results
- Similar to B1 (Function Composition Chain)
- **Prediction**: Degradation with $k$, threshold around 5-10
- **CoT effect**: High - step-by-step tracing natural fit

### Dataset Size
- 10 instances per $(k, \text{algorithm})$ combination
- 3 algorithms × 10 iteration counts
- **Total**: 300 instances

---

## B9: Tree Arithmetic Evaluation

### Motivation
Alternative test for recursive structure gaps (Type 1.2) using arithmetic trees.

### Task Description
Evaluate arithmetic expression tree with operations at internal nodes, values at leaves.

### Difficulty Parameters
- **Primary**: Tree depth $r \in [1, 10]$
- **Secondary**: Branching factor $b \in [2, 3]$

### Instance Format
```
Evaluate the following arithmetic expression tree:

        +
       / \
      *   -
     / \ / \
    3  4 8  2

Evaluation:
- Left subtree (*): 3 * 4 = 12
- Right subtree (-): 8 - 2 = 6
- Root (+): 12 + 6 = 18

Answer: 18
```

### Ground Truth
- Recursive tree evaluation (post-order traversal)

### Evaluation
- **Exact Match**: Numerical answer
- **Partial Credit**: Subtree evaluation correctness

### Expected Results
- Similar to B2 (Boolean formulas)
- **Prediction**: Degradation with depth, asymptotic floor
- **CoT effect**: Medium - can serialize but exponential steps
- **Scale invariance**: Should see plateau (architectural)

### Dataset Size
- 20 instances per $(r, b)$ combination
- 10 depths × 2 branching factors
- **Total**: 400 instances

---

## Experimental Design

### Evaluation Protocol

**Phase 1: Single-model baseline**
- Select representative model (e.g., Claude 3.5 Sonnet, GPT-4)
- Evaluate on all benchmarks
- Test with and without CoT
- Establish baseline performance curves

**Phase 2: Multi-model comparison**
- Evaluate across model families:
  - Claude family (Haiku, Sonnet, Opus)
  - GPT family (GPT-4, GPT-4 Turbo)
  - Open-source (Llama 3, Mistral)
- At least 3 model families (per CLAUDE.md requirement)

**Phase 3: Scale analysis**
- Within each family, test across scales (small, medium, large)
- Identify scale-dependent vs. scale-invariant gaps
- Plot performance scaling curves

**Phase 4: Mitigation evaluation**
- Test interventions:
  - Chain-of-thought prompting
  - Few-shot examples
  - Explicit instruction variations
- Measure mitigation effectiveness per gap type

### Statistical Analysis

**Per benchmark**:
- Mean accuracy and 95% confidence intervals
- Performance curves vs. difficulty parameter
- Threshold detection (where performance drops significantly)

**Cross-benchmark**:
- Correlation between gap types
- Factor analysis: Which gaps cluster together?
- Model ranking consistency across gaps

**Hypothesis testing**:
- H1: Performance on working memory and recursive gaps significantly worse than baseline
- H2: CoT significantly improves serially-decomposable gaps but not recursive gaps
- H3: Scale-dependent gaps show smooth scaling; scale-invariant gaps plateau early

---

## Implementation Plan

### Benchmark Generation Scripts

For each benchmark B1-B9:
1. **Generator**: Python script creating instances with specified parameters
2. **Validator**: Compute ground truth, verify consistency
3. **Format**: JSON with fields:
   ```json
   {
     "benchmark_id": "B1",
     "instance_id": "B1_d5_s1_001",
     "difficulty_params": {"d": 5, "complexity": "simple"},
     "prompt": "...",
     "ground_truth": "...",
     "metadata": {...}
   }
   ```

### Evaluation Infrastructure

1. **Model interface**: Unified API wrapper for different model families
2. **Batch evaluation**: Parallel evaluation for efficiency
3. **Result storage**: Database with prompt, response, correctness, metadata
4. **Analysis pipeline**: Scripts for computing metrics, generating plots

### Artifacts

Deliverables:
1. **Benchmark datasets**: JSON files for all 9 benchmarks (~3000 instances total)
2. **Evaluation code**: Python package for running evaluations
3. **Results database**: SQLite with all evaluation results
4. **Analysis notebooks**: Jupyter notebooks with visualizations and statistics
5. **Public release**: GitHub repo with benchmarks, code, leaderboard

---

## Budget Estimate

### API Costs

Assumptions:
- 3000 benchmark instances
- 10 models tested
- 2 conditions per model (with/without CoT)
- Average 500 tokens per instance (prompt + response)
- Cost: ~$0.01 per instance (varies by model)

**Estimated total**: $600 for full evaluation
- Within $1000 monthly budget
- Leaves room for iterations and additional experiments

### Compute Resources

- Benchmark generation: Minimal (CPU only)
- Evaluation: API-based, no local compute needed
- Analysis: Standard laptop sufficient

---

## Next Steps

1. ✅ Design benchmark specifications
2. **NEXT**: Implement benchmark generators for B1-B3 (start with core gaps)
3. **NEXT**: Pilot evaluation on single model to validate benchmarks
4. **NEXT**: Refine based on pilot results
5. **NEXT**: Full multi-model evaluation
6. **NEXT**: Statistical analysis and results synthesis

---

## Validation Criteria

Before running full evaluation, validate that:
- [ ] Benchmarks have controlled difficulty parameters
- [ ] Ground truth is computable and verified
- [ ] Instances are diverse (no trivial patterns)
- [ ] No data contamination (check against common datasets)
- [ ] Clear connection to gap types in taxonomy
- [ ] Pilot testing shows expected difficulty range (not too easy/hard)
- [ ] Inter-rater reliability for any manual components

---

## References

- Benchmark design informed by:
  - [MemCap24]: N-back task design
  - [CoT-Mirage]: Compositional task methodology
  - [Comp-Collapse]: Task difficulty parameters
  - [CF-Knowledge]: Counterfactual task design
  - [Abstract-Reason]: Content effect measurement
