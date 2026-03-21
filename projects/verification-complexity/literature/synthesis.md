# Literature Synthesis: Verification Complexity for LLM Outputs

Date: 2026-03-21
Status: Phase 1 complete — ready to begin formal framework

---

## The Novel Contribution Space

After surveying ~60 papers across classical complexity theory, LLM verification methods, and scalable oversight, the key finding is: **nobody has connected the classical verification complexity hierarchy to the LLM capability hierarchy in a unified framework.** The pieces exist independently but haven't been assembled.

### What exists (don't re-derive)
1. P vs NP defines the fundamental generation-verification asymmetry
2. IP = PSPACE (Shamir 1992) — interaction extends verification from NP to PSPACE
3. PCP theorem — probabilistic verification can be made O(1)-query
4. Fixed-depth transformers are TC^0-bounded; CoT extends to P (Merrill & Sabharwal)
5. SAT verification is P; planning verification ranges from P to PSPACE depending on representation
6. Self-consistency empirically works for math, fails for planning (well-documented)
7. Process vs outcome supervision are statistically equivalent (Jia et al. ICML 2025)
8. LLMs cannot self-correct reasoning without external feedback (Huang et al. ICLR 2024)
9. Debate protocols can verify PSPACE-hard computations with constant human queries (Brown-Cohen et al.)

### What's missing (our contribution space)
1. **No complexity-theoretic grounding of the GV-Gap for LLMs** — Song et al. (ICLR 2025) define it operationally; we can ground it in TC^0 vs P separation
2. **No verification complexity taxonomy by reasoning domain** — classical results exist per-domain but aren't mapped onto the LLM capability hierarchy
3. **No formal conditions for when easy-to-hard verification generalization succeeds** — empirically shown for math (Sun et al., Hosseini et al.) but no complexity-theoretic characterization
4. **No unified framework connecting our 6 gap types to verification complexity** — each type has different verification properties but nobody has built a coherent table
5. **No impossibility results for self-verification** — empirical evidence (Huang et al.) but no formal theorem

---

## Key References by Topic

### Classical Verification Complexity
- **Goldwasser, Micali & Rackoff (1985)** — Interactive proof systems, zero-knowledge proofs
- **Babai (1985)** — Arthur-Merlin games, AM/MA classes
- **Shamir (1992)** — IP = PSPACE via sumcheck protocol
- **Arora et al. (1998)** — PCP theorem: NP = PCP(log n, O(1))
- **Babai, Fortnow & Lund (1991)** — MIP = NEXP
- **Ji et al. (2020)** — MIP* = RE

### Verification by Domain
- **Math proofs**: Verification in P (NP paradigm). LLM autoformalization still hard (Wu et al. NeurIPS 2022)
- **Code**: Rice's theorem (general undecidability), type checking in P, model checking PSPACE-complete. "Verification ceiling" limits synthetic code training (arXiv:2509.20837)
- **Planning**: Plan verification P for ground STRIPS, coNP-complete for ground HTN, PSPACE-hard for lifted HTN (Behnke et al. AAAI 2024, ICAPS 2025). Kambhampati et al. (ICML 2024): LLMs can't self-verify plans
- **Optimization**: Feasibility verification P, optimality verification coNP-complete. Three-level hierarchy: feasibility < generation < optimality verification
- **Creative tasks**: No decidable correctness criterion — falls outside our framework (this is a feature, not a bug)

### LLM Verification Methods
- **Self-consistency** (Wang et al. ICLR 2023): Assumes independence (CJT). Fails when errors are correlated — 53/56 model-dataset pairs show no improvement on long-context tasks (Tao et al. 2024). "Consensus is not verification" (2026): agreement ≠ correctness
- **Reward models**: Overoptimization follows scaling laws (Gao et al. ICML 2023). KL regularization fails for heavy-tailed error (Kwa et al. NeurIPS 2024). Reward hacking cascades to emergent misalignment (Anthropic 2025)
- **Process reward models**: Empirically superior (Lightman et al. ICLR 2024), but statistically equivalent to outcome supervision (Jia et al. ICML 2025). The gap is algorithmic, not information-theoretic
- **Generative verifiers** (GenRM, Hosseini et al. ICLR 2025): Reframe verification as generation. Easy-to-hard generalization: 28% → 44.6% on MATH
- **Self-correction**: LLMs can't self-correct without external feedback (Huang et al. ICLR 2024). RL-based self-correction partially works (SCoRe, ICLR 2025: +15.6% on MATH)

### Scalable Oversight
- **Debate** (Irving et al. 2018): Verifies PSPACE with poly-time judges. Doubly-efficient debate: constant human queries for any poly-time computation (Brown-Cohen et al. ICML 2024). Obfuscated arguments problem addressed by prover-estimator debate (2025)
- **Scaling laws for oversight** (Engels et al. NeurIPS 2025): Success drops sharply with capability gap. Only debate exceeds 50% at 400-Elo gap
- **Weak-to-strong generalization** (Burns et al. 2023): GPT-2 supervision elicits GPT-3.5 performance from GPT-4, but with limits. Refinement produces inconsistent estimators (2025)
- **Verification ceiling** (2025): Synthetic data quality bounded by verifier capability

### The Generation-Verification Gap (Empirical)
- **Song et al. (ICLR 2025)**: GV-Gap scales monotonically with pre-training FLOPs — larger models are relatively better at verification
- **Solver-Verifier Gap dynamics** (ICLR 2026): Coupled differential equations model. Self-improvement follows exponential curves toward a limit determined by the gap
- **Weaver (Stanford 2025)**: Multiple weak verifiers can be aggregated to shrink the gap

---

## Proposed Paper Structure

Based on the literature gap, the paper should:

### Core Framework (Section 3)
**Definition 1: Verification Complexity Class.** For a reasoning task F with correctness criterion V(x,y), define VC(F) as the complexity class of the verification problem {(x,y) : V(x,y) = 1}. This is the complexity of checking a candidate solution.

**Definition 2: Generation-Verification Gap.** For task F, GV-Gap(F) = GC(F) - VC(F), where GC(F) is the generation complexity. When GV-Gap > 0, verification is strictly easier than generation.

**Definition 3: Model-Relative GV-Gap.** For a model class M (e.g., TC^0 for transformers, P for CoT-augmented), the effective gap is GV-Gap_M(F) = max(GC(F), cap(M)) - VC(F). The model's capability class caps the generation complexity.

### Verification Complexity by Gap Type (Section 4)

| Gap Type | Generation Complexity | Verification Complexity | GV-Gap | Implication |
|----------|----------------------|------------------------|--------|-------------|
| Type 1: Sensitivity | > TC^0 | P | Large | Reward models work; self-consistency works |
| Type 2: Depth | NC^1 / P | P | Moderate | Verification tractable; CoT closes generation gap |
| Type 3: Serial | P | P | None after CoT | Verification = tracing steps; CoT makes generation tractable too |
| Type 4: Algorithmic | P (with right algo) | P (check output) | Conditional | Verification easy IF you know what to check; generation needs knowledge |
| Type 5: Intractability | NP-hard | Feasibility: P, Optimality: coNP | Split | Can verify feasibility but not optimality |
| Type 6: Architectural | Undefined | Undefined | N/A | No decidable V(x,y) for many architectural failures |

### Key Theorems

**Theorem 1 (Verification Advantage).** A mitigation strategy S is effective for task F if and only if VC(F) falls within the augmented model's capability class cap(M+S), regardless of GC(F).

**Theorem 2 (Self-Consistency Condition).** Self-consistency improves accuracy on task F only if: (a) VC(F) ∈ P (the model can verify individual samples), AND (b) per-sample accuracy > 0.5, AND (c) errors across samples are sufficiently independent. Condition (c) fails when errors arise from shared architectural biases (Type 6) or shared computational limitations (Type 5).

**Theorem 3 (GV-Gap Collapse).** For planning tasks with hierarchical representations (HTN), VC(F) ≥ coNP, and the GV-Gap collapses: verifying plan correctness is as hard as generating a correct plan.

**Theorem 4 (Oversight Ceiling).** For task F, no oversight protocol with a verifier bounded by capability class C can reliably distinguish correct from incorrect solutions when VC(F) ∉ C. Interactive protocols (debate) extend C from P to PSPACE but not beyond.

### Empirical Validation (Section 5)
Test predictions on existing benchmarks:
- GSM8K / MATH (VC = P) → self-consistency should work ✓
- PlanBench (VC ranges from P to PSPACE) → self-consistency should degrade with plan complexity
- SAT instances near phase transition (VC = P but generation NP-hard) → self-consistency should work (large GV-Gap)
- Creative writing (VC undefined) → self-consistency should show no systematic improvement

---

## Critical Assessment: Can We Make NeurIPS?

**Timeline**: 6.5 weeks to May 6. Tight but feasible if we:
- Scope to Theorems 1-3 (drop Theorem 4 / oversight to future work)
- Use existing benchmarks only (no synthetic tasks)
- Keep empirical section targeted (3-4 experiments, not comprehensive)

**Novelty**: The bridge between classical verification complexity and LLM training methods is genuinely novel. Song et al. (ICLR 2025) defined the GV-Gap operationally but didn't ground it in complexity theory. Nobody has mapped verification complexity onto reasoning gap types.

**Risk**: Theorems may end up being "obvious" corollaries of known results (e.g., "if VC(F) ∈ P then reward models can learn to verify" is close to tautological). The value is in the unified framework and the predictions it makes, not in any single theorem.

**Decision**: Proceed with NeurIPS as primary target. If by April 15 the theorems aren't landing, pivot to ICLR 2027.
