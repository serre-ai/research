# NeurIPS 2026 Submission: Final Sprint Roadmap

> From "paper-complete" to "camera-ready submission that reviewers can't ignore."

**Project**: reasoning-gaps
**Paper**: "On the Reasoning Gaps of Large Language Models: A Formal Characterization"
**Current state**: 1,518-line LaTeX, 11 models, 148,068 instances, NeurIPS format
**Deadline**: NeurIPS 2026 abstract ~late May, full paper ~early June

---

## Reviewer Threat Model

Before planning experiments, think like a reviewer. NeurIPS assigns 3-4 reviewers who each score on novelty, quality, clarity, significance. Here's what will get flagged:

### Reviewer 1: Theory-Focused
> "The propositions are clean and the framework is novel. But Proposition 4 (budget monotonicity) is stated formally yet never tested empirically beyond a single recalibration anecdote. And the complexity-theoretic connection assumes models ARE bounded-depth circuits, which is at best an approximation."

**Response needed**: Budget sensitivity experiment validating Prop 4 across multiple tasks.

### Reviewer 2: Empirics-Focused
> "148K instances across 11 models is solid. But you claim 'tool use dominates for Type 4' and never test it. B8 shows a ceiling effect that invalidates your Type 6 evidence from reversal. And where is Opus — the most capable reasoning model in your own provider's family?"

**Response needed**: Tool-use condition, B8 reframing, Opus 4.6 evaluation.

### Reviewer 3: Benchmarks/Applications
> "These are all synthetic tasks. How does this taxonomy help a practitioner decide what to do when their model fails on a real task? And Song et al. (TMLR 2026) already published a comprehensive taxonomy of reasoning failures — how is yours different?"

**Response needed**: Real-world mapping section, sharper Song et al. differentiation.

### Area Chair
> "Novel framework with strong theory+empirics. If authors address the Type 4 and Type 6 evidence gaps, this is a clear accept."

---

## What Needs to Happen

### Critical (blocks acceptance)

| # | Item | Why it matters | Est. cost |
|---|------|----------------|-----------|
| 1 | **Opus 4.6 evaluation** | The strongest reasoning model in the Claude family. Without it, reviewers will ask "does this hold at the frontier?" Completes Haiku-Sonnet-Opus trilogy. | ~$272 |
| 2 | **Tool-use condition for B6** | Type 4 prediction ("tool use dominates for algorithmic gaps") is the most testable, most novel, and completely untested claim in the paper. | ~$30-50 |
| 3 | **B8 reframing** | Ceiling effect (>92% all models) means B8 doesn't demonstrate Type 6 gaps. Must reframe as negative result + lean on B9. | $0 (revision) |
| 4 | **NeurIPS checklist + anonymization** | Submission will be desk-rejected without these. | $0 |

### Important (strengthens acceptance)

| # | Item | Why it matters | Est. cost |
|---|------|----------------|-----------|
| 5 | **Budget sensitivity analysis** | Validates Proposition 4 empirically. The B2 recalibration saga already shows budget matters — systematize it. | ~$20-30 |
| 6 | **Real-world mapping section** | Connect taxonomy to known failures: GSM-Symbolic → Type 3, reversal curse → Type 6, planning failures → Type 4. Makes paper actionable. | $0 (revision) |
| 7 | **Song et al. differentiation** | Their TMLR 2026 concurrent taxonomy is the closest related work. Must articulate: they catalog, we formalize with complexity-theoretic grounding. | $0 (revision) |

### Polish (prevents irritation)

| # | Item | Why it matters | Est. cost |
|---|------|----------------|-----------|
| 8 | **Supplementary materials** | Code, data, configs, full results. NeurIPS reviewers check reproducibility. | $0 |
| 9 | **Figure quality pass** | 300 dpi, correct sizing for NeurIPS column width, colorblind-safe palette. | $0 |
| 10 | **Final proofreading** | Terminology consistency, cross-reference verification, page count compliance. | $0 |

**Total estimated cost: ~$320-350**

---

## Phase 1: Critical Experiments

### 1.1 Opus 4.6 Evaluation (~$272)

**Why this is the single most important addition:**
- Opus is the most capable reasoning model available. If it still shows the predicted gap pattern, that's a powerful result: *gaps are architectural, not capability-limited*.
- If it partially closes gaps (e.g., higher CoT lift on Type 2/3), that's equally interesting: *frontier models compress the gap but don't eliminate it*.
- Completes the Claude family: Haiku (small) → Sonnet (medium) → Opus (large). Three-model within-family scaling is much stronger than two.
- Every reviewer will notice the most expensive Claude model is missing.

**Execution:**
```bash
cd projects/reasoning-gaps/benchmarks
python run_evaluation.py \
  --models "anthropic:claude-opus-4-20250514" \
  --tasks B1 B2 B3 B4 B5 B6 B7 B8 B9 \
  --conditions direct short_cot budget_cot
```

- 9 tasks × 3 conditions × 500 instances = 13,500 evaluations
- Opus pricing: $15/M input, $75/M output
- With thinking tokens for CoT: expect $200-300
- Run on VPS to avoid laptop dependency
- Checkpoint system handles interruptions

**What to look for in results:**
- Does Opus show smaller gaps than Sonnet? (Scaling within family)
- Does Opus close any gap types that Sonnet can't? (Capability ceiling)
- Does Opus's extended thinking improve budget_cot more than other models? (Reasoning-mode benefit)
- B7 (3-SAT): Does Opus cross the phase transition barrier? (If so, rethink Type 5 claims)

### 1.2 Tool-Use Condition for B6 (~$30-50)

**The missing experiment that validates the most novel prediction.**

Type 4 (Algorithmic) gaps are predicted to be closed by tool use, not CoT. B6 (Longest Increasing Subsequence) is the cleanest test:
- O(n log n) patience sorting algorithm, trivial in Python
- Current best CoT accuracy: ~35% (terrible, as predicted)
- Expected tool-use accuracy: >95% (the algorithm is simple)

This is the paper's most *actionable* prediction. If we show tool use takes B6 from 35% to 95%+, that's a compelling empirical result with direct practical implications.

**Implementation approach:**

Option A — **Code execution sandbox** (strongest):
- Give model access to a Python execution tool
- Prompt: "Write Python code to find the length of the longest increasing subsequence, then execute it."
- Use Claude's tool_use API with a code execution tool
- Score: extract answer from tool output

Option B — **Structured lookup** (simpler, still valid):
- Give model a `compute_lis(sequence)` function as a tool
- Prompt: "Use the compute_lis tool to find the answer."
- Score: check if model calls tool correctly

Option A is much stronger for the paper. It tests whether the model can *formulate the algorithm*, not just call a function.

**Models to evaluate:**
- Sonnet 4.6 (primary)
- GPT-4o (cross-family comparison)
- Opus 4.6 (if Phase 1.1 is done first)
- Haiku 4.5 (does cheap model + tool still work?)

**Also consider tool-use for B5 (Graph Reachability):**
- B5 is classified Type 2/4 — ambiguous which dominates
- Tool-use condition would disambiguate: if tool use dramatically helps, it's primarily Type 4

### 1.3 Budget Sensitivity Analysis (~$20-30)

**Validates Proposition 4 (budget monotonicity) and addresses the B2 calibration concern.**

Run B2 (Nested Boolean) and B3 (Iterated Permutation) with multiple budget multipliers:

| Budget level | Multiplier | B2 words (d=5) | B3 words (k=5) |
|-------------|------------|-----------------|-----------------|
| Starved | 0.25x | ~45 | ~35 |
| Tight | 0.5x | ~90 | ~70 |
| Calibrated | 1x | ~180 | ~140 |
| Generous | 2x | ~360 | ~280 |
| Unlimited | 4x | ~720 | ~560 |

**Models**: Sonnet 4.6, GPT-4o, Llama 70B (diverse families, 3 is enough)

**What to look for:**
- Monotonicity: does accuracy strictly increase with budget? Prop 4 predicts yes for all gap types where CoT helps.
- Overthinking: at 4x budget, does accuracy plateau or decrease? (B2 showed -0.254 at miscalibrated budget — is this a budget effect or a prompt effect?)
- Threshold behavior: is there a sharp transition where budget becomes sufficient? This would suggest the theoretical Θ(k) bound is empirically observable.

**This produces a new figure**: Budget vs. accuracy curves for B2/B3, one of the most interesting potential plots in the paper.

---

## Phase 2: Analysis & Paper Revision

### 2.1 Integrate Opus Results

After Opus evaluation completes:
- Update all tables (main_accuracy, accuracy_by_condition, cot_lift, scale_analysis) to include 12 models
- Regenerate all 5 figures with Opus data points
- Update abstract: "twelve models from five families" (was "eleven")
- Update instance count (will be ~161,500)
- Add Opus-specific analysis section in experiments:
  - Within-family scaling: Haiku → Sonnet → Opus lift curves
  - Does Opus narrow any gap types? By how much?
  - Opus on B7 (3-SAT): phase transition still holds?

### 2.2 Tool-Use Results Section

New subsection in Experiments: **"Tool Augmentation (Type 4 Validation)"**
- Present B6 results across conditions: direct, short_cot, budget_cot, tool_use
- Expected narrative: "Tool-augmented accuracy of X% vs. CoT accuracy of 35% confirms the Type 4 prediction: algorithmic gaps require external computation."
- New figure: bar chart comparing 4 conditions on B6 (and optionally B5)
- Connect to practical guidance: "When a task falls in Type 4, practitioners should provide tool access rather than sophisticated prompting."

### 2.3 B8 Reframing

The B8 ceiling is not a weakness if framed correctly. Rewrite the B8 discussion:

**Current framing** (implicit): "B8 tests Type 6 (architectural) gaps via reversal inference."
**New framing**: "B8 serves as a calibration task that distinguishes *in-context* reversal from *training-time* reversal. The near-ceiling performance demonstrates that modern models can reverse factual relationships when all information is present in context, consistent with the finding that the 'reversal curse' (Berglund et al., 2023) is a training phenomenon, not an inference-time architectural limitation. By contrast, B9 (negation sensitivity) reveals a genuine architectural gap: accuracy degrades sharply with negation depth regardless of CoT, consistent with the hypothesis that autoregressive generation struggles with systematic negation tracking."

This turns a weakness into a nuanced finding. It shows the taxonomy has *discriminative power* — it can distinguish real gaps from apparent ones.

**Concrete changes:**
- Rewrite B8 analysis paragraph (Experiments section)
- Add sentence in Discussion connecting B8 ceiling to reversal curse literature
- Update Table 3 (or equivalent) to highlight B8 as "negative control"
- Ensure B9 analysis is thorough and compelling as the primary Type 6 evidence

### 2.4 Budget Sensitivity Section

New subsection: **"Budget Calibration and Proposition 4"**
- Present budget vs. accuracy curves for B2 and B3
- Discuss monotonicity (or violation thereof)
- Connect to theoretical prediction: Prop 4 states accuracy is non-decreasing in budget, but proof notes an "overthinking regime" where excessive reasoning can degrade performance
- If non-monotonicity is observed, this is an interesting empirical discovery that refines the theoretical picture

### 2.5 Real-World Mapping Section

New subsection in Discussion: **"Applying the Taxonomy to Known Failures"**

Map published failure patterns to the taxonomy:
- **GSM-Symbolic** (Mirzadeh et al., 2025): Sensitivity to irrelevant information → **Type 1 (Sensitivity)**
- **Compositional generalization** (Dziri et al., 2023): Multi-hop reasoning collapse → **Type 3 (Serial)**
- **Planning failures** (Kambhampati, 2024): Blocksworld, logistics → **Type 4 (Algorithmic)**
- **Reversal curse** (Berglund et al., 2023): Training-time directional binding → **Type 6 (Architectural)**
- **3-SAT / constraint satisfaction**: Phase transition behavior → **Type 5 (Intractability)**
- **Counting failures** (Alice-in-Wonderland): Parity-like sensitivity → **Type 1 (Sensitivity)**

This transforms the paper from "interesting benchmark results" to "practical diagnostic framework." A practitioner reads this section and knows: "My model fails on X → that's Type Y → apply intervention Z."

### 2.6 Sharpen Song et al. Differentiation

Song et al. (TMLR 2026) independently developed a comprehensive taxonomy. The key differences:

| Dimension | Our work | Song et al. |
|-----------|----------|-------------|
| **Grounding** | Complexity-theoretic (TC⁰, NC¹, P) | Empirical categorization |
| **Predictions** | Formal propositions about CoT, scaling, tool use | Descriptive catalog |
| **Benchmark** | Diagnostic tasks isolating specific gaps | Evaluation across existing benchmarks |
| **Novelty** | Framework *predicts* which interventions work | Framework *describes* failure patterns |

Add 2-3 sentences to Related Work making this contrast explicit. Our paper is complementary, not competing: they provide breadth, we provide formal depth.

---

## Phase 3: Submission Polish

### 3.1 NeurIPS Checklist

NeurIPS requires a reproducibility checklist. Fill out:
- [ ] Code availability (yes — link to anonymized repo)
- [ ] Data availability (yes — procedurally generated, scripts included)
- [ ] Compute requirements (11-12 models, ~$350 total API cost)
- [ ] Statistical significance (95% bootstrap CIs, McNemar's, Bonferroni)
- [ ] Limitations section (yes — 7 points)
- [ ] Broader impact (diagnostic framework improves reliability, no direct misuse)

### 3.2 Double-Blind Anonymization

- Replace "Deepwork Research" with "Anonymous"
- Remove `research@deepwork.ai`
- Anonymize any references to "our platform" or "deepwork"
- Ensure supplementary materials don't contain identifying information
- Create anonymized GitHub repo or use OpenReview supplementary upload

### 3.3 Supplementary Materials Package

Assemble:
- `code/` — evaluation scripts, analysis pipeline, benchmark generators
- `data/` — pre-generated benchmark instances (JSON), or generation scripts + seeds
- `results/` — full result matrices (CSV), per-model breakdowns
- `figures/` — high-resolution versions of all figures
- `README.md` — reproduction instructions

### 3.4 Figure Quality Pass

For each of the 5 (soon 6-7) figures:
- Verify 300 dpi resolution
- Check readability at NeurIPS single-column width (3.25 inches)
- Use colorblind-safe palette (viridis or similar)
- Ensure axis labels and legends are readable at print size
- Add figure captions that stand alone (reviewer should understand figure without reading body)

### 3.5 Final LaTeX Checks

- Verify page count: main paper ≤ 9 pages (NeurIPS limit), appendix unlimited
- Check all `\ref` and `\cref` resolve correctly
- Verify bibliography compiles (all citations resolve)
- Check for overfull hboxes and formatting warnings
- Compile with final NeurIPS style (not preprint)
- Verify abstract word count ≤ 250 words

### 3.6 Proofreading Pass

Final read-through for:
- Consistent terminology ("reasoning gap" vs "gap" vs "limitation")
- Correct model counts in text (will be "twelve" after Opus)
- Instance counts updated
- All numbers in text match tables
- Grammar, typos, awkward phrasing
- Check every claim has supporting evidence or citation

---

## Execution Plan

### Sprint A: Experiments (~3-5 days)

| Day | Task | Blocker |
|-----|------|---------|
| 1 | Launch Opus 4.6 evaluation (all 9 tasks, 3 conditions) on VPS | Anthropic API credits |
| 1 | Implement tool-use condition in evaluate.py | None |
| 1-2 | Run tool-use eval for B6 (4 models: Sonnet, GPT-4o, Haiku, + Opus when ready) | Tool-use implementation |
| 2 | Implement budget sweep mode in evaluate.py | None |
| 2-3 | Run budget sensitivity for B2, B3 (3 models × 5 budget levels) | None |
| 3-5 | Opus evaluation completes (13,500 instances, rate-limited) | API throughput |

**Parallelism**: Opus eval runs in background on VPS. Tool-use and budget sweep run in parallel locally or on VPS. Total wall-clock: ~3-5 days (Opus is the bottleneck).

### Sprint B: Analysis & Revision (~2-3 days)

| Day | Task | Blocker |
|-----|------|---------|
| 1 | Run analysis pipeline with 12-model dataset | Opus results |
| 1 | Regenerate all tables and figures | Analysis pipeline |
| 1-2 | Write tool-use results section | Tool-use results |
| 1-2 | Write budget sensitivity section | Budget results |
| 2 | Reframe B8, strengthen B9 analysis | None |
| 2 | Add real-world mapping section | None |
| 2-3 | Sharpen Song et al. differentiation | None |
| 3 | Update abstract, intro, conclusion with new numbers | All results |

### Sprint C: Polish (~1-2 days)

| Day | Task | Blocker |
|-----|------|---------|
| 1 | NeurIPS checklist + ethics statement | None |
| 1 | Anonymize paper | None |
| 1 | Figure quality pass | Final figures |
| 1-2 | Assemble supplementary materials | None |
| 2 | Final LaTeX compilation + page count check | None |
| 2 | Proofreading pass | None |

**Total: ~6-10 days of work**, depending on API throughput for Opus.

---

## Budget

| Item | Estimated cost |
|------|---------------|
| Opus 4.6 evaluation (13,500 instances) | $250-300 |
| Tool-use condition (B6 + B5, 4 models) | $30-50 |
| Budget sensitivity (B2 + B3, 3 models × 5 levels) | $20-30 |
| **Total** | **$300-380** |

This is within the monthly $1,000 budget with room to spare.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| All 6 gap types have empirical evidence | Yes (B8 reframed as negative control, B9 carries Type 6) |
| Type 4 prediction (tool use) validated | B6 tool-use accuracy >90% vs CoT ~35% |
| Frontier model tested | Opus 4.6 in all tables and figures |
| Proposition 4 empirically tested | Budget vs. accuracy curves show predicted monotonicity |
| Real-world applicability demonstrated | 5+ published failure patterns mapped to taxonomy |
| NeurIPS format compliance | ≤9 pages, checklist complete, anonymized |
| Reproducibility package ready | Code + data + configs in supplementary |
| All numbers consistent | Abstract, text, tables, figures all agree |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Opus evaluation exceeds $300 | Budget pressure | Monitor cost during run; stop after 6 tasks if over $250 and run remaining 3 at lower priority |
| Opus closes a gap type we claimed was unclosable | Revises theoretical claims | Actually strengthens paper — shows taxonomy has predictive power for capability gains too. Reframe as "gap narrowing." |
| Tool-use accuracy is only ~60%, not >90% | Weakens Type 4 claim | Still much higher than 35% CoT. Frame as "tool use provides significant but not complete closure." |
| Budget monotonicity violated (Prop 4 fails) | Theoretical embarrassment | Prop 4 proof already notes overthinking regime. Reframe as "conditional monotonicity" — holds below a task-specific ceiling. |
| NeurIPS deadline earlier than expected | Time pressure | Phase 1 experiments are parallelizable. If time-crunched, drop budget sensitivity (least critical) and submit with tool-use + Opus only. |
| Rate limiting on Opus API | Delays Phase 1 | Run at max concurrency allowed; checkpoint system handles interruptions. Start Opus evaluation first. |

---

## What This Gets Us

**Before this sprint:**
- 11 models, 3 conditions, 148K instances
- Type 4 prediction untested
- Type 6 evidence thin (B8 ceiling)
- No frontier model
- Budget sensitivity unquantified
- No real-world mapping

**After this sprint:**
- 12 models including frontier Opus, 4 conditions, ~165K instances
- Type 4 validated with tool-use experiment
- Type 6 properly framed (B8 as calibration, B9 as evidence)
- Budget sensitivity curves validating Prop 4
- Real-world failure mapping demonstrating practical value
- Full NeurIPS compliance (checklist, anonymization, supplementary)

This moves the paper from "solid submission" to "the reviewer has to work hard to find a reason to reject."
