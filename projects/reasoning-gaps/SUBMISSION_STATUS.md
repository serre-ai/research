# NeurIPS 2026 Submission Status

**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Status**: ✅ **SUBMISSION-READY**
**Date**: 2026-03-21
**Deadline**: 45 days from today

---

## Quick Links

- **Paper PDF**: `paper/main.pdf` (314 KB, 19 pages)
- **Submission Package**: `paper/submission.zip` (1.5 MB)
- **Submission README**: `paper/SUBMISSION_README.md`
- **Submission Checklist**: `paper/SUBMISSION_CHECKLIST.md`
- **Session Report**: `reviews/SESSION-2026-03-21-submission-prep.md`
- **Pull Request**: https://github.com/oddurs/deepwork/pull/2

---

## Submission Package Contents

```
submission.zip (1.5 MB)
├── main.pdf                    (314 KB, 19 pages)
├── main.tex                    (67 KB)
├── neurips_2026.sty            (13 KB)
└── benchmarks/analysis_output/
    ├── stats.tex
    ├── figures/
    │   ├── accuracy_vs_difficulty.pdf
    │   ├── cot_lift_heatmap.pdf
    │   ├── phase_transition.pdf
    │   ├── scale_sensitivity.pdf
    │   ├── intervention_comparison.pdf
    │   ├── tool_use_comparison.pdf
    │   └── budget_sensitivity.pdf
    └── tables/
        ├── main_accuracy.tex
        ├── cot_lift.tex
        ├── scale_analysis.tex
        ├── confidence_intervals.csv
        └── (additional tables)
```

---

## Paper Specifications

### Format
- **Venue**: NeurIPS 2026
- **Style**: neurips_2026.sty
- **Pages**: 19 total (9 main + 10 appendix)
- **Page limit**: 9 pages main content ✅ (within limit)
- **PDF size**: 314 KB
- **Compilation**: tectonic (clean, cosmetic warnings only)

### Content
- **Title**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
- **Author**: Anonymous (anonymized for review)
- **Abstract**: 200 words
- **Sections**: 8 (Intro, Background, Framework, Benchmark, Setup, Results, Discussion, Conclusion)
- **Appendices**: 4 (Definitions/Proofs, Full Results, Task Specs, Additional Analyses)
- **Figures**: 5 (all referenced)
- **Tables**: 4 main (all referenced)
- **References**: 40+ (complete BibTeX)

---

## Research Summary

### Theoretical Framework
- **6-type taxonomy** of reasoning gaps
- **5 propositions** with formal proofs/sketches
- Grounded in computational complexity theory (TC⁰, NC¹, L, P, NP)
- Testable predictions about CoT, scaling, and tool use

### Empirical Evaluation
- **12 models** from 5 families
  - Claude: 3.5 Haiku, 4.6 Sonnet, 4.6 Opus, 4.6 Sonnet
  - OpenAI: GPT-4o-mini, GPT-4o, o3
  - Llama: 3.1 8B, 3.1 70B
  - Mistral: Ministral 8B, Mistral Small 24B
  - Qwen: 2.5 7B, 2.5 72B
- **9 diagnostic tasks** (B1-B9)
  - B1: Masked Majority (Type 1: Sensitivity)
  - B2: Nested Boolean (Type 2: Depth)
  - B3: Permutation Composition (Type 3: Serial)
  - B4: State Machine (Type 3: Serial)
  - B5: Graph Reachability (Type 2: Depth)
  - B6: Longest Increasing Subsequence (Type 4: Algorithmic)
  - B7: 3-SAT (Type 5: Intractability)
  - B8: Reversal Inference (Type 6: Architectural)
  - B9: Negation Sensitivity (Type 6: Architectural)
- **4 evaluation conditions**
  - Direct (no CoT)
  - Short CoT (unconstrained)
  - Budget CoT (calibrated token budget)
  - Tool use (Python code execution)
- **209,438 total instances**
  - 159,162 base evaluation
  - 3,000 tool-use evaluation
  - 15,000 budget sweep
  - 32,276 additional conditions

### Key Results
- **Framework validation**: Types 2,3 (depth/serial) CoT lift = +0.351 vs Types 5,6 (intractability/architectural) = +0.094 (p < 0.001)
- **Tool use**: Type 4 (computational gap) tool-use lift = +0.635, 4× CoT alone
- **Budget sensitivity**: B2 sharp threshold at 1.0×, B3 monotonic improvement (validates Proposition 2)
- **Model capacity**: Claude 4.6 Opus 100% on B3 (CoT), 75% on B6 (CoT), 2× next best
- **Statistical rigor**: All results with 95% bootstrap CIs (10,000 resamples)

---

## Verification Checklist

### Document Requirements
- [x] Paper compiles (tectonic, no errors)
- [x] Page limit (9 main pages, within limit)
- [x] PDF size (314 KB, reasonable)
- [x] Format (NeurIPS 2026 style)

### Content Requirements
- [x] Abstract (complete, quantitative result)
- [x] Introduction (motivation, contributions, roadmap)
- [x] Related work (thematic, fair)
- [x] Methods (formal, rigorous)
- [x] Experiments (fully described)
- [x] Results (all claims supported)
- [x] Discussion (limitations addressed)
- [x] Conclusion (contributions summarized)

### Anonymization
- [x] Author: "Anonymous"
- [x] No author names
- [x] No affiliations
- [x] No identifying URLs
- [x] No self-citations (N/A)

### Figures and Tables
- [x] All figures referenced
- [x] All tables referenced
- [x] Captions complete
- [x] High quality
- [x] Readable

### References
- [x] Bibliography complete (40+)
- [x] All citations valid
- [x] BibTeX format correct
- [x] No broken references

### Reproducibility
- [x] Code documented
- [x] Data format documented
- [x] Setup fully described
- [x] Statistical methods documented
- [x] Supplementary materials organized

### Submission Package
- [x] main.pdf (✅)
- [x] main.tex (✅)
- [x] neurips_2026.sty (✅)
- [x] benchmarks/analysis_output/ (✅)
- [x] submission.zip integrity (✅)

---

## Next Actions

### Immediate (Today/Tomorrow)
1. **Upload to NeurIPS submission portal**
   - URL: https://neurips.cc/Conferences/2026/CallForPapers
   - Log in with conference account
   - Upload submission.zip
   - Enter metadata (title, abstract, keywords)
   - Confirm reproducibility checklist
   - Submit before deadline

### Post-Submission
2. **Monitor submission status**
   - Note submission ID
   - Save confirmation email
   - Track review timeline

3. **Prepare for review period**
   - Review common reviewer questions
   - Prepare rebuttal materials
   - Consider additional analyses

### If Revisions Needed
4. **Reviewer response**
   - Address comments systematically
   - Run additional experiments if needed
   - Update paper based on feedback
   - Prepare detailed response document

---

## Project Timeline

### Completed Phases
- ✅ **Literature review** (90 papers, comprehensive survey)
- ✅ **Formal framework** (6 types, 5 propositions, proofs)
- ✅ **Benchmark design** (9 tasks, difficulty calibration)
- ✅ **Analysis infrastructure** (pipeline, stats, visualizations)
- ✅ **Empirical evaluation** (12 models, 209,438 instances)
- ✅ **Paper writing** (19 pages, all sections complete)
- ✅ **Submission preparation** (compilation, documentation, packaging)

### Budget Summary
- Base evaluation (6 open-source models via OpenRouter): ~$0.22
- Claude models: ~$330 (Haiku + Sonnet + Opus)
- OpenAI models: ~$100 (GPT-4o-mini + GPT-4o)
- Tool-use evaluation: ~$27
- Budget sweep: ~$8
- **Total**: ~$465 (under $1,000 monthly budget ✅)

---

## Files Created

### Documentation
- `paper/SUBMISSION_README.md` (4.8 KB)
- `paper/SUBMISSION_CHECKLIST.md` (7.2 KB)
- `SUBMISSION_STATUS.md` (this file)

### Session Reports
- `reviews/SESSION-2026-03-21-submission-prep.md` (full session)

### Build Outputs
- `paper/main.pdf` (314 KB) [gitignored]
- `paper/submission.zip` (1.5 MB)

---

## Git Status

### Branch
- `research/reasoning-gaps` (up to date with origin)

### Recent Commits
1. `17ed39b3` - "paper(reasoning-gaps): compile paper and create submission package"
2. `f82fa56c` - "paper(reasoning-gaps): add comprehensive submission checklist"
3. `b7118dc7` - "paper(reasoning-gaps): add submission prep session report"

### Pull Request
- **#2**: "NeurIPS 2026 Submission: Reasoning Gaps Paper (Submission-Ready)"
- **Status**: Open
- **URL**: https://github.com/oddurs/deepwork/pull/2

---

## Contact for Questions

- **Primary contact**: Via NeurIPS submission system (anonymous review)
- **Repository**: https://github.com/oddurs/deepwork (private during review)

---

## Summary

✅ **ALL REQUIREMENTS MET**

The paper is complete, compiled, verified, and packaged. All NeurIPS 2026 submission requirements satisfied. Submission package (submission.zip, 1.5 MB) ready for upload to conference portal.

**Status**: Ready for immediate submission to NeurIPS 2026.

---

**Last updated**: 2026-03-21 10:15 UTC
**Version**: v1.0 (final submission)
