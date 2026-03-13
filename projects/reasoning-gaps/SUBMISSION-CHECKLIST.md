# NeurIPS 2026 Submission Checklist

**Project**: reasoning-gaps
**Title**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Venue**: NeurIPS 2026
**Deadline**: May 4, 2026
**Target submission**: Early April 2026

---

## Pre-Submission Tasks

### Data Collection
- [x] Complete 9-model evaluations (121,614 instances) - Done 2026-03-11
- [ ] Complete o3 evaluation (VPS, started 2026-03-12 19:21)
- [ ] Complete Sonnet 4.6 evaluation (VPS, queued)
- [ ] Complete B2 budget_cot recalibration (VPS, queued)
- [ ] Verify all evaluation results are valid (0% failure rate target)

### Analysis
- [x] Build complete analysis pipeline - Done 2026-03-10
- [x] Test pipeline with synthetic data - Done 2026-03-10
- [ ] Run full analysis with 11 models + recalibrated B2
- [ ] Generate all final figures (4 main figures)
- [ ] Generate all final tables (2 main tables + appendix table)
- [ ] Verify statistical significance of key claims
- [ ] Run robustness checks

### Paper Content
- [x] Draft all 8 sections - Done 2026-03-12
- [x] Complete appendix (proofs, benchmark specs, results) - Done 2026-03-12
- [x] Complete bibliography (49 entries) - Done 2026-03-13
- [ ] Update Section 5 with final 11-model results
- [ ] Remove B2 footnote after recalibration complete
- [ ] Update all quantitative claims with final data
- [ ] Update all figure captions with final data
- [ ] Verify all cross-references resolve correctly
- [ ] Check all citations render correctly

### Paper Quality
- [ ] Consistency pass: terminology used consistently throughout
- [ ] Consistency pass: notation used consistently throughout
- [ ] Grammar and spelling check
- [ ] Check figure quality and readability
- [ ] Verify all tables format correctly
- [ ] Check abstract accurately reflects final results
- [ ] Verify contributions match what paper delivers
- [ ] Ensure limitations section is comprehensive

### Format Conversion
- [ ] Switch to NeurIPS 2026 format (`neurips_2026.sty`)
- [ ] Update document class and preamble as needed
- [ ] Recompile and verify no LaTeX errors
- [ ] Check page limit compliance (9 pages + unlimited appendix)
- [ ] Verify figures render correctly in NeurIPS format
- [ ] Check bibliography formatting matches NeurIPS style
- [ ] Verify author information formatted correctly
- [ ] Add acknowledgments section if needed

### LaTeX Compilation
- [ ] Compile on system with full LaTeX installation
- [ ] Verify PDF renders correctly
- [ ] Check all mathematical notation renders properly
- [ ] Verify all hyperlinks work
- [ ] Check PDF metadata (title, authors)
- [ ] Generate final PDF for submission

### Supplementary Materials
- [ ] Prepare code release (evaluation scripts, benchmark code)
- [ ] Prepare data release (evaluation results, analysis outputs)
- [ ] Write README for supplementary materials
- [ ] Verify reproducibility of main results
- [ ] Package supplementary materials as required by NeurIPS

### Final Review
- [ ] Complete internal review pass (clarity, flow, accuracy)
- [ ] Verify all theoretical claims are precise and correct
- [ ] Check all empirical claims are supported by data
- [ ] Ensure related work is comprehensive and fair
- [ ] Verify discussion addresses potential criticisms
- [ ] Check that limitations are honestly stated

### Pre-Submission Verification
- [ ] Re-read entire paper start to finish
- [ ] Check abstract standalone clarity
- [ ] Verify introduction motivates well
- [ ] Check conclusion summarizes effectively
- [ ] Verify all figures have informative captions
- [ ] Check all tables are self-contained
- [ ] Ensure paper is accessible to NeurIPS audience

### Submission System
- [ ] Create NeurIPS 2026 submission account
- [ ] Upload final PDF to submission system
- [ ] Upload supplementary materials
- [ ] Enter paper metadata (title, authors, abstract, keywords)
- [ ] Select appropriate subject areas
- [ ] Acknowledge ethical considerations
- [ ] Review conflicts of interest
- [ ] Double-check all submitted files
- [ ] Submit before deadline with buffer

---

## Timeline Estimate

Assuming VPS evaluations complete by **March 16, 2026**:

- **March 16-17**: Run full analysis pipeline, generate final figures/tables
- **March 18**: Update paper Section 5 with final results
- **March 19**: Consistency pass and quality checks
- **March 20**: Convert to NeurIPS format, LaTeX compilation
- **March 21-23**: Final review and polishing
- **March 24-31**: Submission window (7-day buffer)
- **April 1**: Final backstop (34 days before deadline)

**Buffer**: 34+ days before May 4 deadline

---

## Key Files

- **Paper**: `paper/main.tex` (1,489 lines)
- **Analysis pipeline**: `experiments/run_full_analysis.py`
- **Evaluation results**: `benchmarks/results/raw/*.json`
- **Figures**: `benchmarks/results/figures/`
- **Bibliography**: Embedded in `paper/main.tex` (lines 747-1228)
- **Supplementary**: `benchmarks/` (code), `experiments/` (analysis scripts)

---

## Contact and Support

- NeurIPS 2026 submission portal: https://neurips.cc/Conferences/2026
- Submission deadline: May 4, 2026
- Paper format guidelines: Available from NeurIPS website

---

**Last updated**: 2026-03-13
**Status**: Awaiting VPS evaluation completion
