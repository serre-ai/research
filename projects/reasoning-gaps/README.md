# Reasoning Gaps: A Formal Characterization of LLM Reasoning Limits

**Status**: ✅ Submission-ready for NeurIPS 2026
**Last updated**: 2026-03-21
**Phase**: submission-prep (complete)

---

## Quick Links

- **Submission Guide**: [SUBMISSION_GUIDE.md](./SUBMISSION_GUIDE.md) — Complete instructions for NeurIPS portal upload
- **Project Brief**: [BRIEF.md](./BRIEF.md) — Research goals and methodology
- **Current Status**: [status.yaml](./status.yaml) — Detailed project state
- **Paper**: [paper/main.pdf](./paper/main.pdf) — Final compiled paper (314 KB, 19 pages)
- **Submission Package**: [paper/submission.zip](./paper/submission.zip) — Complete submission materials (1.5 MB)

---

## Project Overview

This project investigates the formal characterization of reasoning limitations in large language models, bridging computational complexity theory with empirical LLM evaluation.

**Title**: On the Reasoning Gaps of Large Language Models: A Formal Characterization

**Venue**: NeurIPS 2026

**Deadline**: ~45 days from 2026-03-21 (May 5, 2026)

---

## Key Contributions

1. **Formal Framework**: Six-type taxonomy of reasoning gaps grounded in complexity theory (TC⁰, NC¹, P, NP)
2. **Theoretical Results**: Five propositions with proofs characterizing when gaps exist and can be closed
3. **ReasonGap Benchmark**: Nine diagnostic tasks (B1-B9) isolating specific gap types
4. **Empirical Validation**: 12 models, 5 families, 209,438 instances, 4 evaluation conditions

---

## Results Summary

### Framework Validation
- Types 2,3 (depth/serial gaps): CoT lift = **+0.351**
- Types 5,6 (intractability/architectural gaps): CoT lift = **+0.094**
- Validates theoretical predictions (p < 0.001)

### Intervention Analysis
- Type 4 (computational gap): Tool-use lift = **+0.635** (4× CoT alone)
- Budget sweep: Sharp threshold for exponential complexity, monotonic for serial
- Model scaling: Opus 4.6 achieves 100% on B3 CoT, 75% on B6 CoT (2× next best)

### Empirical Scale
- **12 models**: Claude 3.5 Haiku, Claude 4.6 Sonnet/Opus, GPT-4o-mini/4o/o3, Llama 3.1 8B/70B, Ministral 8B, Mistral Small 24B, Qwen 2.5 7B/72B
- **5 families**: Claude, GPT, Llama, Mistral, Qwen
- **9 tasks**: B1-B9 diagnostic suite
- **4 conditions**: direct, short_cot, budget_cot, tool_use
- **209,438 instances**: Complete evaluation with 95% bootstrap CIs

---

## Directory Structure

```
projects/reasoning-gaps/
├── README.md                    # This file
├── BRIEF.md                     # Research goals and methodology
├── SUBMISSION_GUIDE.md          # Portal upload instructions
├── status.yaml                  # Current project state
├── notes/                       # Research notes and session logs
├── literature/                  # Literature survey and references
├── benchmarks/                  # Task specifications and data
│   └── analysis_output/         # Generated figures, tables, stats
├── experiments/                 # Evaluation and analysis code
├── paper/                       # LaTeX source and output
│   ├── main.tex                 # Paper source
│   ├── main.pdf                 # Compiled paper (314 KB, 19 pages)
│   ├── submission.zip           # Complete submission package (1.5 MB)
│   ├── SUBMISSION_README.md     # Technical documentation
│   ├── SUBMISSION_CHECKLIST.md  # Verification checklist
│   └── build-paper.sh           # Automated build script
└── reviews/                     # Session reports and reviews
```

---

## Current Status

### Completed ✅
- [x] Literature review (90 papers across 3 areas)
- [x] Formal framework (6-type taxonomy, 5 propositions with proofs)
- [x] Benchmark design (9 tasks: B1-B9)
- [x] Analysis infrastructure (statistical tests, visualizations, pipeline)
- [x] Base evaluation (12 models × 9 tasks × 3 conditions = 159,162 instances)
- [x] Tool-use evaluation (3 models × 2 tasks × 1 condition = 3,000 instances)
- [x] Budget sweep (3 models × 2 tasks × 5 multipliers = 15,000 instances)
- [x] Additional conditions (+32,276 instances)
- [x] Paper writing (19 pages: 9 main + 10 appendix)
- [x] Paper compilation (clean, tectonic, 2026-03-21)
- [x] Submission package creation (submission.zip, 1.5 MB)
- [x] Documentation (README, CHECKLIST, GUIDE)
- [x] Final verification (2026-03-21 afternoon)

### Next Steps
- [ ] Upload to NeurIPS 2026 submission portal
- [ ] Monitor submission confirmation
- [ ] Prepare for review period

---

## How to Use This Repository

### To Submit the Paper
1. Read [SUBMISSION_GUIDE.md](./SUBMISSION_GUIDE.md) for complete instructions
2. Upload [paper/main.pdf](./paper/main.pdf) to NeurIPS portal
3. Upload [paper/submission.zip](./paper/submission.zip) if source files requested
4. Copy metadata from SUBMISSION_GUIDE.md
5. Submit before deadline

### To Reproduce Results
1. See [paper/SUBMISSION_README.md](./paper/SUBMISSION_README.md) for build instructions
2. Task generators in `benchmarks/` (B1-B9)
3. Evaluation harness in `experiments/`
4. Analysis pipeline: `experiments/run_full_analysis.py`
5. Build script: `paper/build-paper.sh`

### To Understand the Research
1. Read [BRIEF.md](./BRIEF.md) for research goals
2. Read [status.yaml](./status.yaml) for detailed progress
3. Read research notes in `notes/` for development history
4. Read session reports in `reviews/` for detailed work logs

---

## Key Dates

**Project started**: 2026-03-07
**Literature review complete**: 2026-03-13
**Framework complete**: 2026-03-10
**Evaluation complete**: 2026-03-18
**Paper complete**: 2026-03-21
**Submission deadline**: ~2026-05-05 (45 days from 2026-03-21)

---

## Metrics

**Total instances**: 209,438
- Base evaluation: 159,162
- Tool-use: 3,000
- Budget sweep: 15,000
- Additional conditions: 32,276

**Budget spent**: ~$307 (within $1,000 monthly budget)
- Opus 4.6 evaluation: ~$272
- Tool-use evaluation: ~$27
- Budget sweep: ~$8

**Statistical rigor**: 95% bootstrap confidence intervals, 10,000 resamples, Bonferroni correction

---

## Contact

For questions about this research, see the paper or contact via the NeurIPS submission system.

---

## Citation (After Publication)

```bibtex
@inproceedings{reasoninggaps2026,
  title={On the Reasoning Gaps of Large Language Models: A Formal Characterization},
  author={Anonymous},
  booktitle={Neural Information Processing Systems (NeurIPS)},
  year={2026}
}
```

---

**Status**: ✅ **READY FOR SUBMISSION**

All NeurIPS 2026 requirements verified. See [SUBMISSION_GUIDE.md](./SUBMISSION_GUIDE.md) for upload instructions.

*Last verified: 2026-03-21*
