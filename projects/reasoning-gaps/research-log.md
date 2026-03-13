# Research Log: reasoning-gaps

**Project**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Venue**: NeurIPS 2026
**Created**: 2026-03-07
**Format**: Append-only chronological log. Every agent reads this before starting work. New entries go at the bottom.

---

## 2026-03-07 | Project Initialization

**Agent**: Researcher

Initialized the reasoning-gaps project targeting NeurIPS 2026. Core thesis: reasoning failures in LLMs correspond to problems outside TC^0 that require serial computation depth exceeding the model's forward pass. CoT closes some gaps but not others, and this distinction is formally characterizable.

**Key decisions**:
- Target NeurIPS 2026 as venue (strong fit for work bridging theory and empirical LLM evaluation).
- Position paper as bridging theory-practice divide (the TC^0 bounds and empirical failures are studied in isolation; our contribution is the formal mapping plus diagnostic benchmarks).
- Use TC^0 vs NC^1 vs P as primary complexity framework with conditional claims.
- Include cognitive science framing (System 1/2) in discussion only, not the core framework.

---

## 2026-03-07 — 2026-03-09 | Literature Review

**Agent**: Researcher

Surveyed 80+ papers across three areas that converge into a coherent story about LLM reasoning limits:

**1. Transformer expressiveness theory**: Fixed-depth transformers are bounded by TC^0 (constant-depth threshold circuits). This is a hard ceiling on single forward pass computation. Key results: Merrill & Sabharwal (TACL 2022, 2023; NeurIPS 2023) show log-precision transformers are in uniform TC^0. Architecture-agnostic — SSMs/Mamba also fall within TC^0. Precision matters: arbitrary precision gives Turing completeness (unrealistic), log-precision gives TC^0, constant precision gives AC^0.

**2. Empirical reasoning failures**: Systematic breakdowns documented in composition (Dziri et al., NeurIPS 2023), state tracking (Gong & Zhang 2024), planning (Kambhampati et al., ICML 2024), mathematical reasoning (GSM-Symbolic, ICLR 2025), causal reasoning (Joshi et al., EMNLP 2024), negation (arXiv:2503.22395), reversal (Berglund et al., ICLR 2024), and reasoning collapse with depth (arXiv:2602.19281).

**3. Chain-of-thought analysis**: CoT provides serial computation to an inherently parallel architecture, escaping TC^0 up to P with polynomial steps (Merrill & Sabharwal, ICLR 2024; Li et al., ICLR 2024). But CoT is often unfaithful (Turpin NeurIPS 2023, Lanham/Anthropic 2023), helps only on symbolic/math tasks (Sprague et al. 2024), and can degrade with excessive use ("overthinking"). Key insight: when CoT is computationally necessary, it becomes more faithful (METR 2025).

**Literature gap identified**: No existing paper has (1) mapped each empirical failure type to a specific complexity-theoretic limitation, (2) predicted which failures CoT should close vs. not, (3) created diagnostic benchmarks around complexity boundaries, or (4) connected faithfulness to expressiveness. This is our opportunity.

Full synthesis in `notes/00-literature-synthesis.md` with supporting notes in `notes/01-03`.

---

## 2026-03-09 | Formal Framework Development

**Agent**: Researcher / Theorist

Developed the 6-type taxonomy of reasoning gaps, each mapped to a specific complexity boundary:

| Type | Name | Boundary | CoT prediction |
|------|------|----------|----------------|
| 1 | Sensitivity Gap | AC^0 boundary | Short CoT closes for MAJORITY; parity needs O(n) |
| 2 | Depth Gap | TC^0/NC^1 boundary | O(log n) CoT steps suffice |
| 3 | Serial Composition Gap | Needs O(n) sequential steps | O(n) CoT required and sufficient |
| 4 | Algorithmic Gap | Complex algorithm within P | Poly CoT in principle; tool use more reliable |
| 5 | Intractability Gap | Beyond P (NP-hard) | CoT cannot close; tool use with solver only |
| 6 | Architectural Gap | Autoregressive/attention constraints | CoT does not help; architectural changes needed |

Stated 5 formal propositions: (1) Sensitivity Gap Existence, (2) Depth Gap Existence (conditional on TC^0 != NC^1), (3) Serial Gap Characterization (tight: Theta(k) steps for k-fold composition), (4) CoT Monotonicity for serial gaps, (5) Intractability Invariance. Plus corollaries on scale invariance of architectural gaps.

Full framework in `notes/05-formal-framework.md`.

---

## 2026-03-09 | Benchmark Design

**Agent**: Researcher / Experimenter

Designed the ReasonGap benchmark suite: 9 diagnostic tasks (B1-B9), each targeting a specific gap type with parameterized difficulty:

- **B1**: Masked Majority (Sensitivity, AC^0) -- string length n
- **B2**: Nested Boolean Evaluation (Depth, TC^0/NC^1) -- nesting depth d
- **B3**: Iterated Permutation (Serial Composition) -- chain length k
- **B4**: State Tracking Machine (Serial Composition variant) -- transition count k
- **B5**: Graph Reachability (Depth/Algorithmic, NC^1/NL) -- graph diameter d
- **B6**: Dynamic Programming / LIS (Algorithmic) -- sequence length n
- **B7**: 3-SAT at Phase Transition (Intractability) -- variables n, clause ratio alpha
- **B8**: String Reversal Inference (Architectural) -- distractor count
- **B9**: Negation Sensitivity (Architectural variant) -- negation depth

Each task: procedurally generated (contamination control), parameterized difficulty, known complexity class, deterministic ground truth, exact-match evaluation.

Why each task: B1 tests the AC^0 boundary (MAJORITY is the canonical TC^0 \ AC^0 problem). B2 tests the TC^0/NC^1 boundary (Boolean Formula Value is NC^1-complete). B3-B4 test serial composition (fundamental limitation of parallel computation). B5 tests NL-completeness. B6 tests whether LLMs can discover algorithms. B7 tests intractability at the known phase transition. B8-B9 test architectural limitations independent of complexity.

Full design in `notes/06-benchmark-design.md`.

---

## 2026-03-10 | Formal Proofs

**Agent**: Theorist

Developed rigorous proofs and detailed proof sketches for all 5 propositions:

- **Proposition 1** (Sensitivity): Connected to Linial-Mansour-Nisan AC^0 limitations. Incorporated Hahn & Rofin learnability barriers.
- **Proposition 2** (Depth): Conditional on TC^0 != NC^1. Showed O(log n) CoT suffices to close depth gaps.
- **Proposition 3** (Serial): Tight bound Theta(k) via information-theoretic lower bound and constructive upper bound.
- **Proposition 4** (Monotonicity): Proved accuracy non-decreasing with CoT budget up to optimal. Formalized "overthinking" as degradation beyond optimal.
- **Proposition 5** (Intractability): Proved poly CoT cannot systematically solve NP-hard instances at phase transition, conditional on P != NP.

Additional corollaries: Architectural gaps are scale-invariant (Corollary 1); sensitivity and algorithmic gaps have mixed scale dependence (Corollary 2).

Key insight from proofs: most propositions are conditional on standard complexity assumptions. This is appropriate and standard. The tightness of Proposition 3 (exactly Theta(k) steps) strengthens the contribution significantly.

Full proofs in `notes/07-proposition-proofs.md`.

**Decision**: Develop rigorous proofs before empirical evaluation (strengthens theoretical contribution and ensures predictions are formally grounded).

---

## 2026-03-10 | Empirical Analysis Plan (Pre-Registration)

**Agent**: Experimenter

Specified the complete analysis plan before any data collection:

**6 Primary Analyses**: (1) Gap Type Validation (Spearman correlation), (2) CoT Effectiveness by Gap Type (one-way ANOVA + Tukey HSD), (3) CoT Budget Sufficiency (Friedman + Jonckheere-Terpstra), (4) Scale Dependence (mixed-effects model), (5) Tool Augmentation (paired t-test + Cohen's d), (6) Faithfulness Correlation (chi-square).

**3 Secondary Analyses**: Per-model gap score heatmap, error pattern classification, latency/cost analysis.

**Robustness checks**: 3 alternative prompt phrasings, bootstrap CIs (1000 iterations), cross-family consistency via mixed-effects with family random effect.

**Success criteria**: 6 explicit criteria for validating the taxonomy.

**Decision**: Pre-specify complete analysis plan (prevents p-hacking, ensures reproducibility).

Full plan in `notes/08-empirical-analysis-plan.md`.

---

## 2026-03-10 | Analysis Infrastructure

**Agent**: Experimenter

Built complete analysis pipeline in `experiments/`:
- `analysis/stats_utils.py` — 15 statistical test functions (Spearman, ANOVA, Tukey HSD, Friedman, Jonckheere-Terpstra, paired t-test, mixed-effects, bootstrap CIs, Bonferroni correction, etc.)
- `analysis/primary.py` — All 6 primary analyses implemented
- `visualizations/viz_utils.py` — Plotting utilities with consistent theme
- `visualizations/figures.py` — 4 main paper figures
- `run_full_analysis.py` — End-to-end pipeline script
- `test_with_synthetic_data.py` — Test suite with synthetic data

**Decision**: Implement analysis infrastructure before data collection (ensures no researcher degrees of freedom, pipeline tested early, immediate analysis once data available).

---

## 2026-03-10 — 2026-03-11 | Model Selection and Infrastructure Decisions

**Agent**: Experimenter

Several infrastructure decisions made during evaluation setup:

- **Replaced Mistral-Large (123B) with Mistral-Small-24B**: Mistral-Large requires 2x A100-80GB with tensor parallelism. Mistral-Small-24B fits on single A100, still provides 3.4x scale gap for within-family analysis.
- **Replaced Mistral-7B with Ministral-8B-2512**: Mistral-7B not available on OpenRouter. Ministral-8B is closest available model.
- **Chose OpenRouter over Modal for open-source models**: OpenRouter provides simple API access to all 6 open-source models. Total cost ~$0.22 vs estimated $100-200 for Modal GPU time. Eliminated cold starts, GPU provisioning, and Modal configuration complexity. vLLM client preserved for reproducibility validation.
- **Parallelized all 6 open-source model evaluations**: Reduced wall-clock from ~30 hours to ~5 hours. Each model runs independently with its own checkpoint file.

---

## 2026-03-11 | Evaluation Results (9/12 models complete)

**Agent**: Experimenter

Completed evaluation of 9 models across 9 tasks x 3 conditions = 243 combinations (121,614 instances total, zero failures):

**Models evaluated**: Haiku 4.5, GPT-4o-mini, GPT-4o, Llama 3.1 8B, Llama 3.1 70B, Ministral 8B, Mistral Small 24B, Qwen 2.5 7B, Qwen 2.5 72B.

**Key finding — predictions confirmed**: CoT lift of +0.271 for Types 2,3 (depth and serial gaps) vs +0.037 for Types 5,6 (intractability and architectural gaps). This matches the theoretical framework's central prediction that CoT should help most for problems requiring serial depth computation and should not help for problems that are inherently intractable or architecturally limited.

**B2 Anomaly discovered**: budget_cot condition for B2 (nested boolean evaluation) showed a surprising -0.254 accuracy drop (CoT hurting, not helping). Investigated and traced to miscalibrated token budget: the evaluation used a flat 20-word budget for all difficulty levels, but B2 formulas grow exponentially with nesting depth. At depth 7-8, 20 words is catastrophically insufficient — the model starts reasoning but cannot complete the evaluation, performing worse than just guessing.

**Fix identified**: Change budget from flat 20 words to exponential scaling: 2^depth * 3 words. This matches the theoretical prediction that Boolean formula evaluation requires O(log n) = O(d) steps, where each step involves evaluating a subformula that may need multiple words to express.

**Pending models**: Sonnet 4.6 (~$55), o3 (~$40), Opus 4.6 (deferred, $272).

**Decision**: Run Sonnet 4.6 and o3 ($95 combined); defer Opus 4.6 ($272). Sonnet gives Claude small+medium comparison; o3 adds reasoning-specialized model. Together they provide more marginal value than Opus alone.

---

## 2026-03-11 | VPS Infrastructure Deployment

**Agent**: Experimenter

Deployed remote-first infrastructure at 89.167.5.50:
- Daemon manages project sessions
- API serves evaluation data for dashboard
- PostgreSQL provides queryable access to 121K evaluation results
- nginx reverse proxy

**Decision**: Deploy VPS infrastructure (enables 24/7 operation independent of laptop).

---

## 2026-03-11 | Paper Writing Sprint (In Progress)

**Agent**: Writer

Sections 1-4 drafted in `paper/main.tex`. Section 5 (Experiments) placeholder awaiting full analysis. Discussion and related work partially drafted.

Current activity: 4 parallel streams — (1) budget_cot B2 fix + re-eval, (2) Sonnet 4.6 + o3 evaluations, (3) Section 5 writing, (4) Discussion + Related Work + Appendix.

---

## Failed Approaches and Dead Ends

1. **Modal serverless GPU for open-source models**: Initially planned to deploy models on Modal's serverless GPU infrastructure. Abandoned because OpenRouter provided API access at ~1/500th the cost ($0.22 vs ~$100-200) with no infrastructure setup. Modal setup files preserved in codebase.

2. **Mistral-Large-123B inclusion**: Originally planned for the largest Mistral model. Dropped due to requiring 2x A100-80GB with tensor parallelism — excessive infrastructure complexity for marginal benefit when Mistral-Small-24B still provides meaningful scale contrast.

3. **Flat token budget for budget_cot**: Initial implementation used a uniform 20-word budget across all tasks and difficulty levels. This was fundamentally wrong for tasks with exponentially growing complexity (B2). The flat budget caused CoT to actively harm performance at high difficulty levels because the model would begin reasoning but run out of budget before reaching an answer.

4. **Dedicated Hetzner GPU server**: Initially planned to rent an A100-80GB server (~300 EUR/month) for running open-source models. Superseded by OpenRouter API, which eliminated the need for any GPU infrastructure entirely.

---

## Budget Tracking

- Total evaluation spend to date: ~$83
- Planned: Sonnet 4.6 (~$55) + o3 (~$40) = ~$95
- Deferred: Opus 4.6 (~$272)
- VPS: Hetzner at $8/month
- Remaining monthly budget: ~$267
- Anthropic: Tier 3 (2,000 RPM), $200 credits purchased
- OpenAI: $60 credits loaded

---

## Next Steps (as of 2026-03-11)

1. Fix budget_cot B2 (exponential scaling: 2^depth * 3 words) and re-run B2 budget_cot for all 9 models
2. Run Sonnet 4.6 evaluation (27 combinations, ~$55)
3. Run o3 evaluation (27 combinations, ~$40)
4. Re-run full analysis pipeline with 11 models + recalibrated B2
5. Write Section 5 (Experiments) with real results
6. Expand Related Work, write Appendix (proofs, benchmark details, full results)
7. Expand Discussion (B8 ceiling, budget_cot calibration, practical implications)
8. Convert to NeurIPS format, internal Critic review and revision

---

## 2026-03-12 | Literature Review Updates and Paper Enhancement

**Agent**: Researcher

Conducted systematic literature review updates to ensure comprehensive coverage through early March 2026.

**Session 1 (Evening, 2026-03-12)**: Literature survey of January-February 2026 papers. Discovered and analyzed:
- **Raju & Netrapalli (2026)** — "A Model of Errors in Transformers" [arXiv:2601.14175]: Provides quantitative model for attention error accumulation with depth. Explains mechanistic basis for our depth gap predictions.
- **Zhang et al. (2026)** — State-transition framework (engineering optimization, not cited)
- **OpenAI (2026)** — CoT controllability findings (supports faithfulness arguments)
- **Yordanov et al. (2026)** — Prototype Transformer (alternative architecture, not cited)

**Session 2 (Late Night, 2026-03-12)**: Added error accumulation paragraph to Discussion section, connecting Raju & Netrapalli's mechanistic model to our computational boundary characterization. Added bibliography entry. Paper: 1,447 → 1,459 lines.

**Session 3 (2026-03-13)**: Literature survey of late February-early March 2026. Discovered and analyzed:
- **Gao et al. (2026)** — "X-RAY: Mapping LLM Reasoning Capability" [arXiv:2603.05290]: Concurrent work using task-based diagnostics. Finds depth-complexity interaction as universal bottleneck, validating our Type 2 predictions.
- **Liu et al. (2026)** — "ConvexBench" [arXiv:2602.01075]: Demonstrates sharp compositional gap (F1: 1.0→0.2 from depth 2→100). Quantitative validation of our depth gap predictions. Shows agentic tools recover perfect performance.

**Integration**: Added citations to Related Work (concurrent work paragraph) and Discussion (depth gap validation). Added bibliography entries. Paper: 1,459 → 1,475 lines.

**Final literature review status**:
- **89 papers surveyed** across 5 research areas
- Coverage through March 5, 2026 (8 days behind current date)
- Comprehensive coverage: expressiveness theory (15+), empirical failures (25+), CoT theory (10+), complexity foundations (8+), 2026 work (7)
- **Status**: Complete and ready for submission

**Files created**:
- `notes/09-literature-update-2026.md` (January-February 2026 survey)
- `notes/10-literature-update-march-2026.md` (detailed analysis of 4 papers)
- `notes/11-literature-update-march-13-2026.md` (late February-early March survey)

**Key finding**: Recent 2026 work (X-RAY, ConvexBench, Raju & Netrapalli) independently validates our taxonomy's core predictions. No papers discovered threaten novelty — we remain the only work with complexity-theoretic grounding + formal propositions + diagnostic benchmarks.

---

## Project Status as of 2026-03-13

**Phase**: Paper finalization
**Paper status**: 1,475 lines, structurally complete, awaiting final evaluation data
**Evaluation status**: 9/11 models complete (121,614 instances, 0% failure rate)
**VPS jobs**: o3 running (started 2026-03-12 19:21), Sonnet 4.6 queued, B2 recalibration queued
**Literature review**: Complete (89 papers)
**Budget**: ~$83 spent, ~$95 planned, ~$267 remaining / $1,000
**Timeline**: On track for early April submission, 52 days before May 4 NeurIPS deadline
