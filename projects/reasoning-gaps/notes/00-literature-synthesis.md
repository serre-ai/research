# Literature Synthesis: Reasoning Gaps in LLMs

## The Central Picture

Three independently studied phenomena converge to form a coherent story about LLM reasoning limits:

1. **Transformer expressiveness theory** establishes that fixed-depth transformers are bounded by TC⁰ (constant-depth threshold circuits). This is a hard ceiling on what can be computed in a single forward pass.

2. **Empirical reasoning failures** document systematic breakdowns in composition, state tracking, planning, causal reasoning, and negation — all of which align with predictions from the TC⁰ bound.

3. **Chain-of-thought analysis** shows CoT provides serial computation to an inherently parallel architecture, escaping TC⁰ up to complexity class P with polynomial steps — but CoT is often unfaithful, helps only on symbolic/math tasks, and can degrade with excessive use.

## Key Theoretical Results

### The TC⁰ Ceiling
- **Merrill & Sabharwal (TACL 2022, 2023; NeurIPS 2023)**: Log-precision transformers are in uniform TC⁰, expressible as FO+Majority logic. Under standard assumptions (L ≠ P), they cannot solve linear equalities, arbitrary CFGs, or graph connectivity.
- **This is architecture-agnostic**: SSMs/Mamba also fall within TC⁰ (2024). The limitation stems from constant-depth parallel computation, not attention specifically.
- **Precision matters**: Arbitrary precision → Turing complete (unrealistic). Log-precision → TC⁰. Constant precision → AC⁰.

### CoT Precisely Scales Computational Power
- **Merrill & Sabharwal (ICLR 2024)**: Log CoT steps → at most L. Linear steps → regular languages. Polynomial steps → exactly P.
- **Li et al. (ICLR 2024)**: Without CoT, constant-bit-precision transformers are AC⁰. With T CoT steps, they solve circuits of size T.
- **Lower bounds exist**: CoT for parity is optimal; multiplication requires Ω(N) steps (Bavandpour et al. 2025).

### Expressiveness ≠ Learnability
- **Hahn & Rofin (ACL 2024, Best Paper)**: Highly sensitive functions create isolated points in parameter space. Even expressible functions may be unlearnable via gradient descent.
- **Abbe et al. (NeurIPS 2024)**: "Globality barrier" — distributions with high globality degree cannot be efficiently learned. Only structured scratchpads break this barrier.

## Empirical Failures Mapped to Theory

| Failure Type | Example Papers | Complexity Connection |
|---|---|---|
| **Compositional depth** | Dziri et al. (NeurIPS 2023), Li et al. (ACL 2024) | Exceeds TC⁰ depth; requires serial composition |
| **State tracking** | Gong & Zhang (2024), Hahn (TACL 2020) | Attention dispersion limits working memory |
| **Planning/search** | Kambhampati et al. (ICML 2024), Saparov et al. (ICLR 2025) | Search requires unbounded serial computation |
| **Mathematical reasoning** | GSM-Symbolic (ICLR 2025), Alice in Wonderland (2024) | Pattern matching on training subgraphs, not computation |
| **Causal/counterfactual** | Yamin et al. (2024), Joshi et al. (EMNLP 2024) | Temporal heuristics replace structural causal inference |
| **Negation** | arXiv:2503.22395 (2025) | Insensitivity to logical operators |
| **Reversal** | Berglund et al. (ICLR 2024) | Autoregressive directionality constraint |
| **Reasoning collapse** | arXiv:2602.19281 (2025) | Exponential decay with logical depth |

## CoT: The Escape Hatch and Its Limits

### Where CoT Helps
- Math and symbolic reasoning (Sprague et al. 2024 meta-analysis)
- Inherently serial problems: permutation composition, iterated squaring (Li et al. ICLR 2024)
- Problems reducible to linear serial composition

### Where CoT Fails
- Planning (Stechly et al. NeurIPS 2024) — only helps with hand-crafted examples
- Tasks requiring parallel/recursive decomposition
- Beyond training distribution (Zhao et al. 2025 — "CoT is a brittle mirage")
- With excessive use — "overthinking" degrades accuracy (arXiv:2506.04210)

### The Faithfulness Problem
- CoT explanations are systematically unfaithful (Turpin NeurIPS 2023, Lanham/Anthropic 2023)
- Larger models produce *less* faithful reasoning (inverse scaling)
- The "scalability paradox": better fluency makes unfaithfulness harder to detect
- BUT: when CoT is computationally necessary, it becomes more faithful (METR 2025)

## Gap in the Literature — Our Opportunity

No existing paper has:
1. **Mapped each empirical failure type to a specific complexity-theoretic limitation** with formal precision
2. **Predicted which failures CoT should close vs. which it shouldn't**, then verified empirically
3. **Created diagnostic benchmarks designed around complexity class boundaries** to isolate gap types
4. **Connected the faithfulness literature to the expressiveness literature** — when CoT is faithful is precisely when it's computationally necessary

### Our Thesis
> Reasoning gaps in LLMs are not random or unpredictable. They correspond to problems outside TC⁰ that require serial computation depth exceeding the model's forward pass. CoT closes gaps for problems reducible to bounded serial composition but cannot close gaps requiring unbounded recursion, parallel decomposition, or computation exceeding the CoT budget. This distinction is formally characterizable and empirically verifiable.

## Decisions Made

### D002: Paper Positioning
**Decision**: Position the paper as bridging the theory-practice divide — the formal expressiveness results (Merrill, Sabharwal, etc.) and the empirical failure literature (GSM-Symbolic, Alice in Wonderland, etc.) are studied in isolation. Our contribution is the formal mapping between them plus diagnostic benchmarks.
**Rationale**: Neither pure theory nor pure empirics. The theory community has established TC⁰ bounds; the empirics community has catalogued failures. Nobody has connected them formally with predictive benchmarks.

### D003: Scope of Complexity-Theoretic Claims
**Decision**: Use TC⁰ vs NC¹ vs P as the primary complexity framework. Keep claims at the level of "problems in class X should exhibit gap type Y" without claiming to resolve open complexity questions (TC⁰ vs NC¹ is still open).
**Rationale**: We can make conditional claims ("if TC⁰ ≠ NC¹, then...") which are standard in complexity theory. The empirical results provide evidence for the conjectures without requiring proofs.

### D004: Include Cognitive Science Framing
**Decision**: Include a brief cognitive science connection (working memory limits, dual-process theory) but keep it to the discussion section, not the core framework.
**Rationale**: The cognitive science parallel strengthens the narrative (System 1 ≈ forward pass, System 2 ≈ CoT) but the paper's core contribution is the complexity-theoretic framework. Over-indexing on cognitive science would dilute the technical contribution for NeurIPS.
