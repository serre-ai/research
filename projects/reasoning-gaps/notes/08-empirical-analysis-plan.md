# Empirical Analysis Plan

**Project**: reasoning-gaps
**Date**: 2026-03-10
**Purpose**: Detailed specification of statistical analyses, visualizations, and evaluation protocol for ReasonGap benchmark suite

---

## Overview

This document specifies the complete empirical analysis pipeline from raw model responses to paper-ready results. All analyses should be reproducible, automated, and version-controlled.

---

## 1. Data Collection Protocol

### 1.1 Benchmark Generation

For each task B1-B9, generate instances at multiple difficulty levels:

| Task | Difficulty Parameter | Values | Instances per Value |
|------|---------------------|--------|---------------------|
| B1: Majority | String length $n$ | [10, 20, 40, 80, 160] | 100 |
| B2: Boolean Eval | Nesting depth $d$ | [2, 3, 4, 5, 6, 7, 8] | 100 |
| B3: Permutation | Chain length $k$ | [5, 10, 15, 20, 25, 30] | 100 |
| B4: State Machine | Transition count $k$ | [10, 20, 30, 40, 50] | 100 |
| B5: Graph Reach | Graph diameter $d$ | [3, 5, 7, 9, 11] | 100 |
| B6: LIS | Sequence length $n$ | [10, 20, 30, 40, 50] | 100 |
| B7: 3-SAT | Variables $n$, $\alpha$ | [10, 20, 30], α=[3.5, 4.27, 5.0] | 100 per (n, α) |
| B8: Reversal | Number of facts | [5, 10, 15, 20] | 100 |
| B9: Negation | Negation depth | [1, 2, 3, 4] | 100 |

**Total instances**: ~6,900 instances × 4 conditions × 12 models = **~331,200 evaluations**

**Storage**: Each evaluation result stored as JSON with:
```json
{
  "instance_id": "b1_n20_inst042",
  "task": "B1",
  "difficulty": 20,
  "condition": "short_cot",
  "model": "claude-sonnet-3.5",
  "prompt_sent": "...",
  "model_response": "...",
  "extracted_answer": "1",
  "ground_truth": "1",
  "correct": true,
  "latency_ms": 1234.5,
  "tokens_used": {"input": 120, "output": 85},
  "metadata": {"budget": null, "cot_steps_detected": 3}
}
```

### 1.2 Model Configurations

**12 model configurations**:

| Family | Model | Size | Access |
|--------|-------|------|--------|
| Claude | Haiku 3.5 | ~10B | API |
| Claude | Sonnet 3.5 | ~100B | API |
| Claude | Opus 3 | ~500B | API |
| GPT | GPT-4o-mini | ~10B | API |
| GPT | GPT-4o | ~100B | API |
| GPT | o3 | Unknown | API |
| Llama | Llama 3.1 8B | 8B | Local |
| Llama | Llama 3.1 70B | 70B | Local |
| Mistral | Mistral 7B | 7B | Local |
| Mistral | Mistral Large | 123B | Local/API |
| Qwen | Qwen 2.5 7B | 7B | Local |
| Qwen | Qwen 2.5 72B | 72B | Local |

**Size categories** (for analysis):
- Small: <20B (Haiku, GPT-4o-mini, Llama 8B, Mistral 7B, Qwen 7B)
- Medium: 20-100B (Sonnet, GPT-4o, Llama 70B, Qwen 72B, Mistral Large)
- Large: >100B (Opus, o3)

### 1.3 Conditions

Four evaluation conditions per task:

1. **Direct**: Force immediate answer, no reasoning
   - Prompt: "Answer with just the final answer. Do not explain."

2. **Short CoT**: Unconstrained chain-of-thought
   - Prompt: "Think step by step, then provide your final answer."

3. **Budget CoT**: Fixed reasoning budget
   - For each task, budgets: $[\log n, n, 2n]$ words (approx 1.3× tokens)
   - Prompt: "Think step by step (using at most B words), then provide your final answer."

4. **Tool-augmented**: Code execution allowed (B5, B6, B7 only)
   - Prompt: "You may write Python code to solve this. Provide code and final answer."

---

## 2. Primary Analyses

### 2.1 Analysis 1: Gap Type Validation

**Goal**: Verify that each benchmark task exhibits the predicted gap pattern.

**Method**:
- For each task, fit accuracy vs. difficulty curve
- Test for systematic degradation (gap presence)
- Classify gap as fundamental or contingent based on CoT response

**Statistical test**:
- Spearman correlation between difficulty and accuracy (expect negative)
- $H_0$: $\rho = 0$ (no systematic degradation)
- $H_1$: $\rho < 0$ (systematic degradation)
- Significance level: $\alpha = 0.01$ (Bonferroni correction for 9 tasks)

**Per-task predictions**:

| Task | Gap Type | Expected Pattern | CoT Expected to Help? |
|------|----------|------------------|----------------------|
| B1 | Sensitivity | Acc ↓ with $n$ | Yes (counting) |
| B2 | Depth | Acc ↓ with $d$ | Yes (O(log n) steps) |
| B3 | Serial | Acc ↓ with $k$ | Yes (O(k) steps) |
| B4 | Serial | Acc ↓ with $k$ | Yes (O(k) steps) |
| B5 | Depth/Algo | Acc ↓ with $d$ | Partially |
| B6 | Algorithmic | Acc ↓ with $n$ | Moderately, tool use better |
| B7 | Intractability | Acc ≈ constant at α=4.27 | No |
| B8 | Architectural | Acc ≈ constant, low | No |
| B9 | Architectural | Acc ↓ with negation depth | Minimally |

**Visualization**: 9-panel figure (one per task)
- X-axis: difficulty parameter
- Y-axis: accuracy (0-1)
- Lines: one per condition (direct, short CoT, budget CoT)
- Error bars: 95% confidence intervals (bootstrapped)

### 2.2 Analysis 2: CoT Effectiveness by Gap Type

**Goal**: Quantify "CoT lift" for each gap type and verify predictions from Proposition 4.

**Metric**: CoT lift
$$
\text{Lift}(M, T, C) = \frac{\text{Acc}_{\text{CoT}}(M, T, C) - \text{Acc}_{\text{direct}}(M, T, C)}{\text{Acc}_{\text{direct}}(M, T, C)}
$$

Relative improvement from adding CoT.

**Method**:
- Compute lift for each (model, task, difficulty) triple
- Group by gap type (average across tasks of same type)
- Test hypothesis: Types 2-3 have significantly higher lift than Types 5-6

**Statistical test**:
- One-way ANOVA with gap type as factor
- Post-hoc: Tukey HSD for pairwise comparisons
- Expected ordering: Lift(Type 2,3) > Lift(Type 1,4) > Lift(Type 5,6)

**Visualization**: Box plot
- X-axis: Gap type (1-6)
- Y-axis: CoT lift (% improvement)
- Boxes: distribution across all (model, difficulty) combinations
- Overlay: individual task markers

### 2.3 Analysis 3: CoT Budget Sufficiency

**Goal**: Test Proposition 4 (monotonicity in budget) and identify optimal budget per gap type.

**Method**:
- For tasks B1-B4 (clear CoT predictions), vary budget: [log n, n, 2n]
- Fit accuracy curves as function of budget
- Test for monotonicity: $\text{Acc}(B_1) \leq \text{Acc}(B_2)$ for $B_1 < B_2 \leq n$
- Identify plateau: budget $B^*$ where accuracy stops increasing

**Statistical test**:
- Friedman test (non-parametric repeated measures)
- $H_0$: Median accuracy equal across budgets
- $H_1$: Monotonic increase with budget (Jonckheere-Terpstra trend test)

**Expected results**:
- **B1 (Majority)**: Plateau at $B \approx \log n$ (just need to count)
- **B2 (Boolean eval)**: Plateau at $B \approx d$ (one step per depth level)
- **B3, B4 (Serial)**: Plateau at $B \approx k$ (one step per composition)

**Visualization**: Line plots per task
- X-axis: CoT budget (log scale)
- Y-axis: Accuracy
- Lines: One per difficulty level
- Mark plateau point $B^*$ where curve flattens

### 2.4 Analysis 4: Scale Dependence

**Goal**: Determine which gap types narrow with model scale (Corollary 1, 2).

**Method**:
- Group models by size: Small (<20B), Medium (20-100B), Large (>100B)
- For each (task, difficulty), compute: $\Delta_{\text{scale}} = \text{Acc}_{\text{large}} - \text{Acc}_{\text{small}}$
- Group by gap type and test if $\Delta_{\text{scale}} > 0$ systematically

**Statistical test**:
- Mixed-effects model:
  $$
  \text{Acc}_{i,j,k} = \beta_0 + \beta_1 \cdot \log(\text{Size}_i) + \beta_2 \cdot \text{Difficulty}_j + \beta_3 \cdot \text{GapType}_k + \epsilon
  $$

  Where $\beta_1$ captures scale effect, $\beta_3$ captures gap type effect.

- Test: $H_0: \beta_1 = 0$ vs $H_1: \beta_1 > 0$ (scale helps)
- Interaction test: Does $\beta_1$ vary by gap type?

**Expected results** (from Corollaries 1-2):
- **Type 1, 4**: Moderate positive $\beta_1$ (scale helps partially)
- **Type 2, 3**: Moderate positive $\beta_1$ (scale + depth/width improves capacity)
- **Type 5, 6**: Near-zero $\beta_1$ (scale invariant)

**Visualization**: Scatter plot
- X-axis: Model size (log scale)
- Y-axis: Accuracy
- Color: Gap type
- Fit regression lines per gap type
- Highlight slope differences

### 2.5 Analysis 5: Tool Augmentation Effectiveness

**Goal**: Quantify how much tool use (code execution) closes gaps compared to CoT alone.

**Method**:
- For tasks B5, B6, B7 (where tools are most relevant), compare:
  - Direct
  - Short CoT
  - Tool-augmented
- Compute tool lift: $\frac{\text{Acc}_{\text{tool}} - \text{Acc}_{\text{CoT}}}{\text{Acc}_{\text{CoT}}}$

**Expected results**:
- **B5 (Graph reach)**: Moderate tool lift (graph algorithms help)
- **B6 (LIS)**: Large tool lift (DP algorithm much more reliable than CoT)
- **B7 (3-SAT)**: Minimal tool lift at phase transition (NP-hard, tools don't help systematically)

**Statistical test**:
- Paired t-test: Acc(tool) vs Acc(CoT) for each task
- Effect size: Cohen's d

**Visualization**: Bar chart
- X-axis: Task (B5, B6, B7)
- Y-axis: Accuracy
- Grouped bars: Direct / CoT / Tool
- Show tool lift as percentage above bars

### 2.6 Analysis 6: Faithfulness Correlation

**Goal**: Test hypothesis that CoT is more faithful when computationally necessary (Section 6 discussion).

**Method**:
- For each task, classify as:
  - **CoT necessary**: Types 2-3 (depth/serial gaps where CoT theoretically helps)
  - **CoT not necessary**: Types 1, 5-6 (sensitivity, intractability, architectural)
- Manual inspection: Rate CoT reasoning as "faithful" (follows logical steps) or "unfaithful" (spurious)
- Compute faithfulness rate per group

**Sampling**:
- Select 50 instances per task (random sample stratified by difficulty)
- Total: 450 instances × 12 models = 5,400 CoT traces
- Two annotators (researchers), measure inter-rater agreement (Cohen's κ)

**Expected result**:
- Faithfulness rate higher for Tasks B2-B4 (CoT necessary) than B1, B7-B9 (CoT not necessary)

**Statistical test**:
- Chi-square test: Association between "CoT necessary" and "faithful"
- $H_0$: Independence
- $H_1$: Positive association

**Visualization**: Stacked bar chart
- X-axis: Gap type
- Y-axis: Proportion of traces
- Stacked: Faithful / Unfaithful
- Overlay: Binary marker for "CoT theoretically necessary"

---

## 3. Secondary Analyses

### 3.1 Per-Model Characterization

**Goal**: Identify which models exhibit which gaps most strongly.

**Method**:
- For each model, compute gap score per type:
  $$
  \text{GapScore}(M, T) = 1 - \frac{\text{Acc}_{\text{hard}}(M, T)}{\text{Acc}_{\text{easy}}(M, T)}
  $$

  Measures degradation from easy to hard instances.

- Rank models by gap score for each type

**Visualization**: Heatmap
- Rows: Models (12)
- Columns: Gap types (6)
- Color: Gap score (0 = no gap, 1 = complete failure on hard)

**Use case**: Identify which models have architectural gaps (Type 6) vs only capacity gaps (Types 1-4).

### 3.2 Error Pattern Analysis

**Goal**: Characterize failure modes for each gap type.

**Method**:
- For incorrect responses, classify error type:
  - **Off-by-one**: Close to correct answer (common in serial gaps)
  - **Random**: No structure (common in intractability gaps)
  - **Systematic bias**: Consistent wrong direction (common in architectural gaps)
  - **Partial solution**: Correct initial steps, wrong final answer (common in depth gaps)

**Sampling**: 100 errors per (task, condition)

**Expected patterns**:
- **B3, B4 (Serial)**: Off-by-one errors (model "loses track" midway)
- **B7 (3-SAT)**: Random guesses (no systematic pattern)
- **B8 (Reversal)**: Systematic bias (defaults to A→B fact)

**Visualization**: Error distribution pie charts per task

### 3.3 Latency and Cost Analysis

**Goal**: Quantify computational cost of different mitigation strategies.

**Metrics**:
- Latency (ms per instance)
- Token count (input + output)
- API cost ($ per 1M tokens)

**Comparison**:
- Direct vs Short CoT: Latency increase?
- Short CoT vs Tool: Which is faster for algorithmic tasks?

**Visualization**: Scatter plot
- X-axis: Accuracy improvement from Direct to CoT/Tool
- Y-axis: Latency increase (log scale)
- Points: (Task, model, condition) combinations
- Pareto frontier: Identify strategies with best accuracy/cost tradeoff

---

## 4. Robustness Checks

### 4.1 Prompt Sensitivity

**Goal**: Verify results are not artifacts of specific prompt wording.

**Method**:
- For each task, generate 3 alternative prompts with equivalent instructions
- Rerun evaluation on subset (20% of instances)
- Measure variance in accuracy across prompts

**Criterion**: If variance < 5% across prompts, results are robust.

### 4.2 Instance Sampling Variance

**Goal**: Ensure 100 instances per difficulty level provide stable estimates.

**Method**:
- Bootstrap resampling (1000 iterations)
- Compute 95% confidence intervals for all reported accuracies
- If CI width < 0.05, sample size is sufficient

### 4.3 Cross-Family Consistency

**Goal**: Verify gap patterns hold across model families (not family-specific artifacts).

**Method**:
- For each gap type, test if pattern holds within each family:
  - Claude family (Haiku, Sonnet, Opus)
  - GPT family (4o-mini, 4o, o3)
  - Open-source (Llama, Mistral, Qwen)
- Use mixed-effects model with family as random effect

**Expected**: Main effects (gap type, difficulty) significant; family random effect small.

---

## 5. Visualization Standards

### Figure 1: Accuracy vs Difficulty (9-panel grid)
- **Dimensions**: 3×3 grid (one per task)
- **Format**: Line plots with error bars
- **Colors**: Consistent condition colors (Direct=red, Short CoT=blue, Budget CoT=green, Tool=purple)
- **Export**: PDF, 8"×8", 300 DPI

### Figure 2: CoT Lift by Gap Type
- **Format**: Box plot with overlay scatter
- **X-axis**: Gap types 1-6
- **Y-axis**: CoT lift (% improvement)
- **Export**: PDF, 6"×4", 300 DPI

### Figure 3: Scale Dependence
- **Format**: Scatter plot with regression lines
- **X-axis**: Model size (log scale)
- **Y-axis**: Accuracy (averaged across difficulties)
- **Colors**: One per gap type
- **Export**: PDF, 6"×4", 300 DPI

### Figure 4: Tool Augmentation Effectiveness
- **Format**: Grouped bar chart
- **X-axis**: Tasks B5, B6, B7
- **Y-axis**: Accuracy
- **Groups**: Direct / CoT / Tool
- **Export**: PDF, 5"×3", 300 DPI

### Table 1: Summary Statistics
- Rows: Tasks B1-B9
- Columns: Gap type, Complexity class, Direct acc, CoT acc, Lift, Scale effect
- Format: LaTeX booktabs, 3 decimal precision

### Table 2: Per-Model Performance Matrix
- Rows: Models (12)
- Columns: Tasks (9)
- Entries: Accuracy (averaged across difficulties)
- Color scale: Red (low) to green (high)
- Format: LaTeX with xcolor

---

## 6. Statistical Reporting Standards

All reported results must include:

1. **Point estimate**: Mean accuracy or lift
2. **Uncertainty**: 95% confidence interval (bootstrapped, 1000 iterations)
3. **Effect size**: Cohen's d for comparisons, $\eta^2$ for ANOVA
4. **Statistical test**: Test name, test statistic, p-value
5. **Sample size**: Number of instances, models, conditions

**Example**:
> CoT lift for Type 2 gaps (M=0.34, 95% CI [0.28, 0.40]) significantly exceeded Type 5 gaps (M=0.05, 95% CI [0.01, 0.09]), t(238) = 12.3, p < 0.001, d = 1.58.

**Significance thresholds**:
- $p < 0.05$: Suggestive
- $p < 0.01$: Significant (Bonferroni-corrected)
- $p < 0.001$: Highly significant

---

## 7. Reproducibility Checklist

All analyses must be:

- [ ] **Automated**: Run via single script (`make analysis`)
- [ ] **Version-controlled**: Analysis scripts in `experiments/analysis/`
- [ ] **Deterministic**: Set random seeds for all sampling/bootstrapping
- [ ] **Documented**: README with dependencies, usage, expected runtime
- [ ] **Tested**: Unit tests for statistical functions
- [ ] **Archived**: Raw data, intermediate results, final figures all saved

**File structure**:
```
projects/reasoning-gaps/
├── benchmarks/
│   ├── data/           # Generated benchmark instances (JSON)
│   ├── results/        # Raw evaluation results (JSON)
│   └── analysis/       # Analysis scripts (Python, R)
├── figures/            # Publication-ready figures (PDF)
├── tables/             # LaTeX tables
└── paper/
    └── results.tex     # Auto-generated results section
```

---

## 8. Timeline

**Phase 1: Data Collection** (Est. 2-3 days)
- Generate all benchmark instances
- Run evaluations across 12 models × 4 conditions × 9 tasks
- Store results in structured database

**Phase 2: Primary Analyses** (Est. 2 days)
- Run Analyses 1-6
- Generate Figures 1-4 and Tables 1-2
- Write results section draft

**Phase 3: Secondary Analyses** (Est. 1 day)
- Per-model characterization
- Error pattern analysis
- Latency/cost analysis

**Phase 4: Robustness Checks** (Est. 1 day)
- Prompt sensitivity
- Bootstrap CI
- Cross-family consistency

**Phase 5: Write-up** (Est. 1 day)
- Integrate all results into paper Section 5
- Create appendix with detailed tables
- Final figure polishing

**Total**: ~7 days from data collection to paper-ready results

---

## 9. Success Criteria

Results successfully support the paper if:

1. ✅ **Gap existence**: All tasks show significant accuracy degradation with difficulty (Analysis 1)
2. ✅ **CoT predictions**: Types 2-3 show significantly higher lift than Types 5-6 (Analysis 2)
3. ✅ **Budget sufficiency**: Optimal budget matches theoretical prediction within 2× (Analysis 3)
4. ✅ **Scale invariance**: Type 6 shows near-zero scale effect (Analysis 4)
5. ✅ **Tool effectiveness**: B6 shows large tool lift, B7 shows minimal (Analysis 5)
6. ✅ **Faithfulness**: Positive correlation with computational necessity (Analysis 6)

If all 6 criteria met, taxonomy is empirically validated.

---

## Next Steps

1. ✅ Complete analysis plan specification
2. **NEXT**: Write analysis scripts (Python + R for stats)
3. **NEXT**: Run pilot evaluation (small subset) to test pipeline
4. **NEXT**: Full evaluation once infrastructure provisioned
5. **NEXT**: Execute analysis pipeline and generate results
