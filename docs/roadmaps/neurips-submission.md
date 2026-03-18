# NeurIPS 2026 Submission: Final Sprint Roadmap

> From "paper-complete" to "camera-ready submission that reviewers can't ignore."

**Project**: reasoning-gaps
**Paper**: "On the Reasoning Gaps of Large Language Models: A Formal Characterization"
**Current state**: 12 models, 209,438 instances, 9 conditions, all evals complete, auto-build pipeline on VPS
**Deadline**: NeurIPS 2026 abstract ~late May, full paper ~early June

---

## Live Progress Tracker

> **Last updated**: 2026-03-18 (end of Day 1)
> **Branch**: `research/reasoning-gaps`
> **VPS**: 89.167.5.50 (deepwork-vps)

### Phase 1: Critical Experiments — COMPLETE

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | Opus 4.6 evaluation (13,500 instances) | **DONE** | 27/27 combos, zero failures, ~$272 |
| 1.2a | Tool-use condition implementation | **DONE** | `tool_executor.py`, `query_with_tools()`, evaluate.py `--condition tool_use` |
| 1.2b | Tool-use evaluation (B5, B6) | **DONE** | 6 result files (3 models × 2 tasks), ~3K instances |
| 1.3a | Budget sensitivity implementation | **DONE** | `--budget-multipliers` CLI flag, separate checkpoints per multiplier |
| 1.3b | Budget sensitivity evaluation (B2, B3) | **DONE** | 30 result files (3 models × 2 tasks × 5 multipliers: 0.25x–4.0x) |

### Phase 2: Analysis & Paper Revision — COMPLETE

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Integrate Opus results | **DONE** | 12 models in all tables/figures, within-family scaling subsection |
| 2.2 | Tool-use results section | **DONE** | §5.9 "Tool Augmentation Validates Type 4 Prediction", bar chart figure |
| 2.3 | B8 reframing | **DONE** | Reframed as calibration/negative control |
| 2.4 | Budget sensitivity section + figure | **DONE** | §5.4 expanded, line plot (accuracy vs multiplier) figure |
| 2.5 | Real-world mapping | **DONE** | 6 published failures mapped in Discussion |
| 2.6 | Song et al. differentiation | **DONE** | Complexity-theoretic vs descriptive contrast in Related Work |
| 2.7 | Auto-generation pipeline | **DONE** | `build-paper.sh` → analyze.py → tectonic → submission.zip. API at `/api/paper/*` |

### Phase 3: Submission Polish — CURRENT SPRINT

| # | Task | Status | Agent | Depends on |
|---|------|--------|-------|------------|
| 3.0 | **Page compression (18→9 pages)** | NOT STARTED | A | — |
| 3.1 | NeurIPS checklist + ethics statement | NOT STARTED | B | 3.0 |
| 3.2 | Double-blind anonymization | NOT STARTED | B | — |
| 3.3 | Supplementary materials package | NOT STARTED | C | 3.0 |
| 3.4 | Figure quality pass | NOT STARTED | C | 3.0 |
| 3.5 | Final LaTeX checks (format, refs, page count) | NOT STARTED | D | 3.0–3.4 |
| 3.6 | Number consistency audit | NOT STARTED | D | 3.0 |
| 3.7 | Proofreading pass | NOT STARTED | D | 3.0–3.6 |

---

## Phase 3 Sprint: Agent Team Plan

### CRITICAL: Page Count

**The paper main body is currently ~18 pages. NeurIPS requires ≤9.** This is the single biggest task and gates everything else.

Current structure (1,542 lines):
```
§1 Introduction         (64–88)     ~1.5 pages
§2 Background           (89–136)    ~1.5 pages
§3 Formal Framework     (137–259)   ~3 pages
§4 Benchmark Suite      (260–332)   ~2 pages
§5 Experiments          (333–644)   ~8 pages (8 subsections!)
§6 Discussion           (645–721)   ~2 pages
§7 Related Work         (722–772)   ~1.5 pages
§8 Conclusion           (773–792)   ~0.5 pages
— Bibliography          (793–1047)  (doesn't count)
— Appendix              (1048–1542) (doesn't count)
```

### Agent A: Page Compression (blocking)

**Goal**: Cut main body from ~18 to ≤9 pages while preserving all key claims and evidence.

**Strategy** (roughly 9 pages of cuts needed):

1. **§3 Formal Framework → compress to ~1.5 pages** (save ~1.5 pages)
   - Keep Definition 1 (reasoning gap) and the 6-type taxonomy table
   - Move all proposition statements to a compact theorem list (1-liner each)
   - Proofs already in appendix — just reference them
   - Cut verbose prose around definitions

2. **§4 Benchmark Suite → compress to ~1 page** (save ~1 page)
   - Replace per-task descriptions with a single summary table: Task | Gap Type | Input | Difficulty Param | Key Prediction
   - Full task details already in Appendix B

3. **§5 Experiments → compress to ~4 pages** (save ~4 pages)
   - Merge §5.1 (Setup) into a compact paragraph
   - §5.2 (Main Results): keep Table 1 + 2 key paragraphs
   - §5.3 (CoT Effectiveness): merge into §5.2 as "CoT lift" paragraph
   - §5.4 (Budget Sensitivity): 1 paragraph + figure reference (move details to appendix)
   - §5.5 (Scale Analysis): 1 paragraph (move table to appendix)
   - §5.6–5.8 (Phase Transition, o3, Claude): merge into single "Case Studies" paragraph
   - §5.9 (Tool Augmentation): keep as 1 paragraph — it's a key prediction validation

4. **§6 Discussion → compress to ~0.75 pages** (save ~1.25 pages)
   - Real-world mapping: compact to a brief paragraph
   - Merge limitations into conclusion

5. **§7 Related Work → compress to ~0.5 pages** (save ~1 page)
   - Merge into Discussion as a subsection, or compress significantly

6. **Move to Appendix**:
   - Scale analysis table (Table 4)
   - Detailed per-model case study data
   - Extended budget sensitivity curves
   - CoT lift heatmap can stay (it's a key figure)

**Files**: `paper/main.tex`
**Verification**: Compile and check `pdfinfo main.pdf | grep Pages` ≤ 12 (9 main + refs + appendix start)

### Agent B: NeurIPS Compliance

**Goal**: Checklist, anonymization, ethics.

1. **Anonymization** (quick)
   - Line 44–46: "Deepwork Research" → "Anonymous"
   - Line 46: remove `\texttt{research@deepwork.ai}`
   - Search for any other identifying references

2. **NeurIPS Paper Checklist** (new appendix section)
   - Answer all questions from the [NeurIPS 2026 checklist](https://neurips.cc/public/guides/PaperChecklist)
   - Reproducibility: code will be in supplementary, all hyperparameters in Appendix
   - Compute: report total API cost (~$307)
   - Ethics: no human subjects, no PII, benchmarks are synthetic

3. **Format switch**
   - Line 4: `[preprint,nonatbib]` → just `[nonatbib]` (removes preprint header)

**Files**: `paper/main.tex`
**Depends on**: Can start anonymization + format switch immediately. Checklist after 3.0.

### Agent C: Supplementary Materials + Figure Quality

**Goal**: Package code/data for reproducibility; ensure figures meet NeurIPS standards.

1. **Supplementary materials** — create `paper/supplementary/` with:
   - `README.md` — overview of contents
   - `code/` — symlinks or copies of `benchmarks/evaluate.py`, `run_evaluation.py`, `tool_executor.py`, analysis pipeline
   - `data/` — task generators (B1–B9 in `benchmarks/tasks/`)
   - `results/` — summary CSVs (not raw JSON — too large)
   - `configs/` — model configs, prompt templates

2. **Figure quality**
   - Verify all figures are PDF (vector) not PNG
   - Check NeurIPS column width compliance (≤5.5in single, ≤11.7in double)
   - Verify colorblind-safe palette (already using seaborn "colorblind")
   - Font sizes ≥ 8pt in all figure labels

**Files**: `paper/supplementary/`, `benchmarks/analysis/plots.py`
**Depends on**: 3.0 (compressed paper may change which figures are in main vs appendix)

### Agent D: Final Verification

**Goal**: Numbers match, refs work, no LaTeX warnings, proofread.

1. **Number consistency audit**
   - Abstract says "209,438 instances" — verify against `stats.tex`
   - "twelve models from five families" — verify
   - All `\stat*` macros resolve correctly
   - Table/figure cross-references all valid

2. **LaTeX checks**
   - Zero LaTeX warnings on compile
   - All `\cref` references resolve
   - Bibliography: no "?" references
   - No overfull hboxes > 1pt

3. **Proofreading**
   - Terminology consistency ("chain-of-thought" vs "CoT", "reasoning gap" vs "gap")
   - Grammar, typos
   - Claim-evidence alignment: every claim in abstract/intro has support in experiments

**Files**: `paper/main.tex`, `benchmarks/analysis_output/stats.tex`
**Depends on**: All other agents complete.

---

## Sprint Dependency Graph

```
      Agent A: Page Compression
      ├──→ Agent B: Checklist (after 3.0)
      ├──→ Agent C: Supplementary + Figures (after 3.0)
      └──→ Agent D: Verification (after A, B, C)

Agent B: Anonymization + Format (can start immediately, parallel with A)
```

**Execution order**:
1. Agent B starts anonymization + format switch (immediate, 5 min)
2. Agent A starts page compression (main task, gates everything)
3. Agent B writes checklist (after A finishes)
4. Agent C packages supplementary + checks figures (after A finishes)
5. Agent D runs verification (after A, B, C)
6. Final build on VPS: `POST /api/paper/build`

---

## Manual Steps (human required)

These cannot be automated and require Oddur's action:

| Step | When | Action |
|------|------|--------|
| **M1. Review compressed paper** | After Agent A | Read the 9-page version. Check that no key arguments were lost. This is the most important review. |
| **M2. Approve anonymization** | After Agent B | Verify no identifying info remains (affiliations, GitHub links, acknowledgments) |
| **M3. Final PDF review** | After Agent D | Visual check: layout, figure placement, table formatting, page breaks |
| **M4. NeurIPS abstract submission** | ~Late May 2026 | Submit abstract on OpenReview portal. Requires: title, abstract text, keywords, author list |
| **M5. NeurIPS full paper submission** | ~Early June 2026 | Upload: main PDF (≤9 pages), supplementary ZIP. Requires OpenReview account. |
| **M6. Supplementary review** | Before M5 | Check that supplementary package includes everything a reviewer would need to reproduce |
| **M7. DNS + SSL for web download** | Optional | Point `api.deepwork.site` A record → 89.167.5.50, then `certbot --nginx` for HTTPS |

---

## Build Pipeline (VPS)

All paper generation runs on VPS. No local builds needed.

```bash
# Trigger build (from anywhere)
curl -X POST http://89.167.5.50/api/paper/build

# Check status
curl http://89.167.5.50/api/paper/status

# Download PDF
curl http://89.167.5.50/api/paper/pdf -o reasoning-gaps.pdf

# Download full submission package
curl http://89.167.5.50/api/paper/download -o submission.zip

# View build log
curl http://89.167.5.50/api/paper/log
```

---

## Budget

| Item | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Opus 4.6 evaluation | $250–300 | ~$272 | **DONE** |
| Tool-use condition (B5+B6) | $30–50 | ~$27 | **DONE** |
| Budget sensitivity (B2+B3) | $20–30 | ~$8 | **DONE** |
| **Sprint total** | **$300–380** | **~$307** | **Under budget** |

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| All 6 gap types have empirical evidence | B8 reframed, B9 carries Type 6 | **DONE** |
| Frontier model tested | Opus 4.6 in all tables and figures | **DONE** |
| Type 4 prediction (tool use) validated | B6 tool-use results integrated | **DONE** |
| Proposition 4 empirically tested | Budget sensitivity curves integrated | **DONE** |
| Real-world applicability demonstrated | 6 published failures mapped | **DONE** |
| NeurIPS format compliance | ≤9 pages, checklist, anonymized | **NOT STARTED** |
| Reproducibility package ready | Code + data + configs in supplementary | **NOT STARTED** |
| All numbers consistent | Abstract, text, tables, figures agree | **NEEDS RE-CHECK** (209K) |
| Auto-build pipeline | VPS: analyze → compile → zip → API download | **DONE** |

---

## Verification Commands

```bash
# Trigger full build on VPS
curl -X POST http://89.167.5.50/api/paper/build

# Check build status
curl http://89.167.5.50/api/paper/status

# Page count check (on VPS)
ssh deepwork-vps "cd ~/deepwork/projects/reasoning-gaps/paper && pdfinfo main.pdf | grep Pages"

# Check instance count matches
ssh deepwork-vps "head -1 ~/deepwork/projects/reasoning-gaps/benchmarks/analysis_output/stats.tex"

# Download and inspect locally
curl http://89.167.5.50/api/paper/pdf -o /tmp/reasoning-gaps.pdf && open /tmp/reasoning-gaps.pdf
```
