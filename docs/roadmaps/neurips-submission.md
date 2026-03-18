# NeurIPS 2026 Submission: Final Sprint Roadmap

> From "paper-complete" to "camera-ready submission that reviewers can't ignore."

**Project**: reasoning-gaps
**Paper**: "On the Reasoning Gaps of Large Language Models: A Formal Characterization"
**Current state**: 12 models, 159,162 instances, NeurIPS format, Opus integrated
**Deadline**: NeurIPS 2026 abstract ~late May, full paper ~early June

---

## Live Progress Tracker

> **Last updated**: 2026-03-18 (Sprint Day 1)
> **Branch**: `research/reasoning-gaps`
> **VPS**: 89.167.5.50 (deepwork-vps)

### Phase 1: Critical Experiments

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | Opus 4.6 evaluation (13,500 instances) | **DONE** | 27/27 combos complete, zero failures, ~$272. Downloaded to local, loader.py updated, analysis re-run. |
| 1.2a | Tool-use condition implementation | **DONE** | `tool_executor.py`, `query_with_tools()` in anthropic/openai clients, evaluate.py `--condition tool_use` |
| 1.2b | Tool-use evaluation (B5, B6) | **RUNNING** | Launched 2026-03-18 on VPS. 6 combos (3 models × 2 tasks), 3K instances, ~$27. Log: `~/tool_use_eval.log` |
| 1.3a | Budget sensitivity implementation | **DONE** | `--budget-multipliers` CLI flag, separate checkpoints per multiplier |
| 1.3b | Budget sensitivity evaluation (B2, B3) | **RUNNING** | Launched 2026-03-18 on VPS. 30 combos (3 models × 2 tasks × 5 multipliers), ~$8. Log: `~/budget_sweep_eval.log`. 3/30 done. |

### Phase 2: Analysis & Paper Revision

| # | Task | Status | Depends on |
|---|------|--------|------------|
| 2.1 | Integrate Opus results (tables, figures, text) | **DONE** | Added Opus column to all tables, regenerated 5 figures, new within-family scaling subsection. 12 models, 159,162 instances, 319 CIs. |
| 2.2 | Tool-use results section | BLOCKED | Tool-use eval (1.2b) — ETA ~2-3h |
| 2.3 | B8 reframing (calibration/negative control) | **DONE** | Reframed as calibration distinguishing in-context from training-time reversal. B9 strengthened as primary Type 6 evidence. |
| 2.4 | Budget sensitivity section + figure | BLOCKED | Budget sweep eval (1.3b) — ETA ~4-5h |
| 2.5 | Real-world mapping section | **DONE** | 6 published failures mapped to taxonomy types in Discussion. |
| 2.6 | Song et al. differentiation | **DONE** | Descriptive vs. complexity-theoretic grounding contrast sharpened in Related Work. |

### Phase 3: Submission Polish

| # | Task | Status | Depends on |
|---|------|--------|------------|
| 3.1 | NeurIPS checklist + ethics statement | NOT STARTED | All Phase 2 |
| 3.2 | Double-blind anonymization | NOT STARTED | Can start now |
| 3.3 | Supplementary materials package | NOT STARTED | All Phase 2 |
| 3.4 | Figure quality pass (300dpi, colorblind-safe) | NOT STARTED | All Phase 2 |
| 3.5 | Final LaTeX checks (page count, refs) | NOT STARTED | All Phase 3 items |
| 3.6 | Proofreading pass | NOT STARTED | Everything |

### Key Opus Findings (integrated into paper)

| Finding | Significance |
|---------|-------------|
| B3 (Perm Comp): **1.000** with CoT | Serial gap fully closed at frontier scale — confirms Prop 3 |
| B6 (LIS): **0.75** with CoT (2× next best) | Algorithmic gap narrows dramatically at scale |
| B7 (3-SAT): 0.72 (CoT lift +0.02) | Intractability gap persists — confirms Prop 5 |
| B2 (Bool): **0.99** with CoT | Depth gap fully closed at frontier scale |
| B9 (Negation): **1.00** with CoT | Negation sensitivity yields to CoT at Opus scale |
| CoT lifts: Types 2,3 = +35.1%, Types 5,6 = +9.4% | 4:1 ratio holds with 12 models |

### Key Files

| File | Purpose |
|------|---------|
| `projects/reasoning-gaps/paper/main.tex` | Paper LaTeX source |
| `projects/reasoning-gaps/benchmarks/evaluate.py` | Core evaluation script |
| `projects/reasoning-gaps/benchmarks/run_evaluation.py` | Batch evaluation runner |
| `projects/reasoning-gaps/benchmarks/tool_executor.py` | Sandboxed Python execution for tool_use |
| `projects/reasoning-gaps/benchmarks/analysis/loader.py` | Result loader (Opus model mapping added) |
| `projects/reasoning-gaps/benchmarks/results/analysis/` | Analysis output (tables, figures) |
| `projects/reasoning-gaps/status.yaml` | Project state |

---

## Remaining Work

### Day 1-2: Integrate Experiment Results (after VPS evals complete)

**3a. Download results from VPS**
```bash
scp "deepwork-vps:~/deepwork/projects/reasoning-gaps/benchmarks/results/*tool_use*" results/
scp "deepwork-vps:~/deepwork/projects/reasoning-gaps/benchmarks/results/*budget_cot*0.*" results/
```

**3b. Tool-use results section**
- New subsection in Experiments: "Tool Augmentation (Type 4 Validation)"
- B6 across 4 conditions: direct (~25%), short_cot (~40%), budget_cot (~30%), tool_use (expected >90%)
- B5 tool_use results to disambiguate Type 2 vs Type 4
- New figure: bar chart comparing conditions on B6 (add to `analysis/plots.py`)
- Remove limitation point about missing tool-use condition (~line 695)

**3c. Budget sensitivity section + figure**
- Expand existing §5.2 with empirical budget curves
- Budget vs. accuracy for B2/B3 at 0.25x, 0.5x, 1.0x, 2.0x, 4.0x
- Test Proposition 4 monotonicity empirically
- New figure: line plot, x=budget multiplier, y=accuracy, lines per model
- Add to `analysis/plots.py`

### Day 2-3: Submission Polish

| Task | Time | Notes |
|------|------|-------|
| 3.1 NeurIPS checklist | 1h | Reproducibility answers in new appendix |
| 3.2 Anonymization | 5min | "Deepwork Research" → "Anonymous", remove email (line 42-43) |
| 3.3 Supplementary materials | 2h | Assemble code/, data/, results/, figures/ package |
| 3.4 Figure quality pass | 1h | 300dpi (already set), colorblind-safe palette (already set), NeurIPS column width |
| 3.5 LaTeX checks | 30min | ≤9 pages main, switch `[preprint,nonatbib]` to `[nonatbib]`, verify refs |
| 3.6 Proofreading | 1h | Terminology consistency, all numbers match tables |

---

## Budget

| Item | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Opus 4.6 evaluation | $250-300 | ~$272 | **DONE** |
| Tool-use condition (B5+B6) | $30-50 | ~$27 est | RUNNING |
| Budget sensitivity (B2+B3) | $20-30 | ~$8 est | RUNNING |
| **Sprint total** | **$300-380** | **~$307** | **On budget** |

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| All 6 gap types have empirical evidence | B8 reframed, B9 carries Type 6 | **DONE** |
| Frontier model tested | Opus 4.6 in all tables and figures | **DONE** |
| Type 4 prediction (tool use) validated | B6 tool-use accuracy >90% vs CoT ~40% | PENDING |
| Proposition 4 empirically tested | Budget vs. accuracy monotonicity curves | PENDING |
| Real-world applicability demonstrated | 6 published failures mapped | **DONE** |
| NeurIPS format compliance | ≤9 pages, checklist, anonymized | NOT STARTED |
| Reproducibility package ready | Code + data + configs in supplementary | NOT STARTED |
| All numbers consistent | Abstract, text, tables, figures agree | **DONE** (12 models, 159K) |

---

## Verification Commands

```bash
# Check VPS eval progress
ssh deepwork-vps "tail -5 ~/tool_use_eval.log && echo '---' && tail -5 ~/budget_sweep_eval.log"

# Verify analysis output
python3 analyze.py --results-dir results/ --output-dir results/analysis/ --skip-plots

# Page count check
pdfinfo main.pdf | grep Pages

# Final compile
pdflatex main.tex && pdflatex main.tex  # twice for refs
```
