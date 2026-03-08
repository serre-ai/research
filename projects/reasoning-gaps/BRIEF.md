# Reasoning Gaps: A Formal Characterization of LLM Reasoning Limits

## Title
On the Reasoning Gaps of Large Language Models: A Formal Characterization

## Target Venue
NeurIPS 2026

## Research Area
LLM Capabilities × AI/ML Theory

## Motivation
Large language models demonstrate remarkable reasoning abilities on many benchmarks, yet fail unpredictably on seemingly simple problems. These failures are not random — they reveal systematic "reasoning gaps" that correlate with structural properties of the underlying problem. Understanding these gaps is essential both for building more capable systems and for knowing when to trust model outputs.

## Research Goals

### Primary
1. **Formally characterize** the classes of reasoning problems where autoregressive LLMs systematically fail, connecting empirical gaps to properties from computational complexity and formal language theory.
2. **Develop a taxonomy** of reasoning gap types (compositional, recursive, counterfactual, etc.) grounded in both theory and large-scale empirical evaluation.
3. **Propose mitigation strategies** — identify which gaps can be closed via prompting/scaffolding vs. which require architectural changes.

### Secondary
4. Investigate whether chain-of-thought and related techniques close gaps or merely mask them.
5. Connect reasoning gap patterns across model scales to refine understanding of emergence.

## Hypotheses
- H1: LLM reasoning failures cluster around problems requiring unbounded working memory or recursive variable binding, mirroring known limitations of bounded-depth threshold circuits.
- H2: Chain-of-thought closes gaps for problems reducible to serial composition but not for problems requiring true parallel/recursive decomposition.
- H3: Reasoning gaps narrow predictably with scale for some problem classes but remain constant for others, and the distinction is theoretically characterizable.

## Methodology
1. **Literature survey**: Existing work on transformer expressiveness, circuit complexity bounds, and empirical reasoning benchmarks.
2. **Formal framework**: Define reasoning gap formally; connect to TC⁰/NC¹ complexity classes and known transformer expressiveness results.
3. **Benchmark construction**: Design diagnostic tasks that isolate specific gap types (compositional depth, variable binding, state tracking, etc.).
4. **Empirical evaluation**: Test across model families (Claude, GPT, open-source) and scales.
5. **Mitigation analysis**: Evaluate prompting strategies, tool use, and scaffolding against the taxonomy.

## Expected Contributions
- A formal framework connecting LLM reasoning failures to computational complexity
- A diagnostic benchmark suite for reasoning gap evaluation
- Empirical results across model families and scales
- Actionable guidance on which gaps are addressable via prompting vs. architecture

## Timeline
- **Phase 1** (Weeks 1–3): Literature review & formal framework
- **Phase 2** (Weeks 4–6): Benchmark design & construction
- **Phase 3** (Weeks 7–10): Empirical evaluation
- **Phase 4** (Weeks 11–13): Analysis, mitigation experiments, paper writing
