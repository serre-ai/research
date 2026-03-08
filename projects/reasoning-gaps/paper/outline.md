# Paper Outline: On the Reasoning Gaps of Large Language Models

## 1. Introduction (1.5 pages)
- LLMs demonstrate remarkable but unreliable reasoning
- Failures are not random — they are systematic and predictable
- Two disconnected literatures: complexity theory (TC⁰ bounds) and empirical failure catalogs
- **Our contribution**: A formal taxonomy connecting each empirical failure type to a complexity boundary, with diagnostic benchmarks and testable predictions
- Preview of key results: 6 gap types, 9 diagnostic tasks, evaluation across 12 model configurations

## 2. Background (1.5 pages)
### 2.1 Circuit Complexity Classes
- AC⁰, TC⁰, NC¹, L, NL, P, NP — definitions and key separations
- TC⁰ vs NC¹ open question and its significance

### 2.2 Transformer Expressiveness
- Log-precision transformers ⊆ TC⁰ (Merrill & Sabharwal 2022, 2023)
- CoT hierarchy: log → L, linear → REG, poly → P (Merrill & Sabharwal 2024)
- Precision matters: constant → AC⁰, log → TC⁰, arbitrary → Turing complete

### 2.3 Empirical Landscape
- Brief survey of documented reasoning failures (GSM-Symbolic, compositional decay, planning failures, reversal curse)

## 3. Formal Framework (2.5 pages)
### 3.1 Definitions
- Definition 1: Reasoning task (parameterized function family)
- Definition 2: Model capability class C(M)
- Definition 3: Reasoning gap (systematic failure outside capability class)
- Definition 4: Gap closure (technique brings task into capability class)

### 3.2 Reasoning Gap Taxonomy
- Type 1: Sensitivity Gap (AC⁰ boundary)
- Type 2: Depth Gap (TC⁰/NC¹ boundary)
- Type 3: Serial Composition Gap (linear depth required)
- Type 4: Algorithmic Gap (P, requires learned algorithms)
- Type 5: Intractability Gap (beyond P)
- Type 6: Architectural Gap (autoregressive/attention constraints)

### 3.3 Formal Results
- Propositions 1–5: existence, characterization, CoT predictions (conditional on standard assumptions)
- Table mapping each gap type to complexity boundary, CoT prediction, and tool-use prediction

## 4. The ReasonGap Benchmark Suite (2 pages)
### 4.1 Design Principles
- Parameterized difficulty, known complexity, procedural generation, contamination control

### 4.2 Tasks
- B1–B9: One or more tasks per gap type (brief description of each)
- Table: task, gap type, complexity class, difficulty parameter, evaluation format

### 4.3 Evaluation Protocol
- Models (proprietary + open-source, 12 configurations)
- Conditions (direct, short CoT, budget CoT, tool-augmented)
- Metrics (accuracy, gap score, CoT lift, scale sensitivity)

## 5. Empirical Results (3 pages)
### 5.1 Main Results
- Table/figure: accuracy × difficulty × condition for each task
- Verification of gap type predictions

### 5.2 CoT Analysis
- CoT lift by gap type — confirms Type 2/3 benefit, Type 5/6 invariance
- CoT budget analysis — required budget matches theoretical prediction
- Faithfulness: CoT is more faithful on tasks where it's computationally necessary

### 5.3 Scale Analysis
- Which gaps narrow with scale? (Type 4 somewhat; Types 1,5,6 not)
- Which gaps narrow with CoT budget? (Types 1–3 yes; Types 5–6 no)

### 5.4 Tool Use
- Code execution closes Type 4 gaps dramatically
- Does not help Types 5–6

## 6. Discussion (1 page)
### 6.1 Implications for LLM Development
- Scaling alone cannot close all gaps
- CoT is effective for specific, predictable gap types
- Tool augmentation is the strongest general-purpose mitigation

### 6.2 Cognitive Science Parallel
- System 1 (forward pass) ≈ TC⁰ computation
- System 2 (deliberate reasoning) ≈ CoT serial computation
- Working memory limits parallel attention dispersion

### 6.3 Limitations
- Taxonomy is not exhaustive (may not cover all failure types)
- Conditional on unproven complexity separations
- Benchmark tasks are synthetic (real-world reasoning is messier)

## 7. Related Work (1 page)
- Transformer expressiveness: Merrill, Sabharwal, Strobl et al.
- Empirical reasoning failures: Song et al. taxonomy, GSM-Symbolic, Faith and Fate
- CoT analysis: faithfulness literature, test-time scaling
- Reasoning benchmarks: BIG-Bench, GSM8K, ARC, MATH

## 8. Conclusion (0.5 pages)
- Reasoning gaps are systematic, predictable, and formally characterizable
- The gap taxonomy provides both explanatory power and practical guidance
- Call to action: benchmark-driven development targeted at specific gap types

## Appendix
- A: Full benchmark task specifications
- B: Detailed per-model results
- C: Proofs of propositions
- D: Benchmark generation code

---

## Page Budget (NeurIPS: 9 pages + references + appendix)
| Section | Pages |
|---|---|
| Introduction | 1.5 |
| Background | 1.5 |
| Formal Framework | 2.5 |
| Benchmark Suite | 2.0 |
| Empirical Results | 3.0 |
| Discussion | 1.0 |
| Related Work | 1.0 |
| Conclusion | 0.5 |
| **Total** | **13** → need to trim to 9 |

Will need to compress Background and Related Work, move detailed results to appendix.
