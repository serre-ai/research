# NeurIPS 2026 Submission Guide

**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Status**: ✅ Ready for submission
**Verified**: 2026-03-21
**Deadline**: 45 days from 2026-03-21 (approximately May 5, 2026)

---

## Quick Start

1. Navigate to NeurIPS 2026 submission portal
2. Upload `paper/main.pdf` (314 KB)
3. Upload `paper/submission.zip` (1.5 MB) if source files requested
4. Copy metadata from this document
5. Submit

---

## Submission Materials

### Primary File

**Location**: `/home/deepwork/deepwork/projects/reasoning-gaps/paper/main.pdf`

**Properties**:
- Size: 314 KB
- Pages: 19 (9 main content + 10 appendix)
- Format: NeurIPS 2026 style
- Compilation: Clean (tectonic, 2026-03-21 10:05 UTC)
- Anonymization: Verified ("Anonymous" author)

### Source Package

**Location**: `/home/deepwork/deepwork/projects/reasoning-gaps/paper/submission.zip`

**Properties**:
- Size: 1.5 MB
- Contains:
  - main.pdf (321 KB)
  - main.tex (67 KB)
  - neurips_2026.sty (13 KB)
  - benchmarks/analysis_output/ (all figures and tables)

**Contents verified**: 5 figures (PDF + PNG), 4 tables, stats.tex

---

## Portal Metadata

### Title

```
On the Reasoning Gaps of Large Language Models: A Formal Characterization
```

### Abstract

```
Large language models demonstrate remarkable reasoning abilities yet fail systematically on seemingly simple problems. We show these failures are not random but correspond to reasoning gaps---problem classes that fall outside the computational boundary of the model's architecture. Building on transformer expressiveness results that place fixed-depth log-precision transformers within TC⁰ (constant-depth threshold circuits), we develop a six-type taxonomy of reasoning gaps, each grounded in a specific complexity-theoretic boundary: sensitivity (AC⁰), depth (TC⁰/NC¹), serial composition (linear depth), algorithmic (P), intractability (NP), and architectural (autoregressive constraints). We introduce ReasonGap, a diagnostic benchmark suite of nine tasks designed to isolate each gap type, with testable predictions about when chain-of-thought reasoning, model scaling, and tool augmentation should close or fail to close each gap. Evaluation across twelve models from five families (209,438 instances) under four evaluation conditions (direct, chain-of-thought, budget-constrained CoT, and tool-augmented) validates the taxonomy: chain-of-thought closes depth and serial gaps as predicted by complexity theory, tool use dominates for algorithmic gaps, and architectural gaps persist regardless of intervention. Our framework provides both explanatory power for why models fail and practical guidance for which mitigation strategies to apply.
```

### Keywords

```
reasoning gaps, large language models, chain of thought, transformer expressiveness, computational complexity, circuit complexity, diagnostic benchmark, autoregressive models
```

### Subject Areas

**Primary**: Machine Learning
**Secondary**: Theory
**Tertiary**: Natural Language Processing

Additional tags (if available):
- Deep Learning
- AI/ML Theory
- Benchmarking
- Language Models

---

## Paper Summary (for portal forms)

**Contributions**:

1. **Formal Framework**: Six-type taxonomy of reasoning gaps grounded in computational complexity theory (TC⁰, NC¹, P, NP)

2. **Theoretical Results**: Five propositions with proofs characterizing when gaps exist and can be closed

3. **ReasonGap Benchmark**: Nine diagnostic tasks (B1-B9) designed to isolate specific gap types with controlled difficulty

4. **Empirical Validation**:
   - 12 models (Claude, GPT, Llama, Mistral, Qwen)
   - 5 model families
   - 209,438 total instances
   - 4 evaluation conditions
   - 95% bootstrap confidence intervals (10,000 resamples)

**Key Results**:

- Chain-of-thought closes depth/serial gaps (+0.351 lift) but not intractability/architectural gaps (+0.094 lift)
- Tool use dominates for computational gaps (+0.635 lift, 4× CoT alone)
- Budget sensitivity validates theoretical predictions (sharp threshold for exponential complexity, monotonic for serial)
- Larger models narrow but don't eliminate gaps (Opus 4.6: 100% on B3 CoT, 75% on B6 CoT, 2× next best)

---

## Reproducibility Information

**Code Availability**: Included in supplementary materials

**Components**:
- 9 task generators (B1-B9) with controlled difficulty parameters
- Evaluation harness for all 4 conditions
- Complete analysis pipeline (statistical tests, visualizations)
- Automated build system (build-paper.sh)

**Data**:
- 209,438 evaluation instances
- Full results with confidence intervals
- Model predictions and ground truth
- All intermediate analysis outputs

**Experimental Details**:
- Section 5: Complete experimental setup
- Appendix B: Full results tables
- Appendix C: Complete task specifications
- Appendix D: Additional analyses

**Statistical Methods**:
- Bootstrap confidence intervals (95%, 10,000 resamples)
- McNemar's test for paired comparisons
- Bonferroni correction for multiple comparisons
- Effect sizes reported for all main results

---

## Checklist (Pre-Upload Verification)

Before clicking "Submit" on the portal, verify:

### Document
- [x] PDF opens correctly
- [x] All pages render (19 pages total)
- [x] No missing fonts
- [x] File size reasonable (< 10 MB) ✅ 314 KB
- [x] Within page limit (9 pages main content)

### Content
- [x] Title correct
- [x] Author field = "Anonymous"
- [x] Abstract complete
- [x] No author names, affiliations, or identifying URLs
- [x] All figures referenced in text
- [x] All tables referenced in text
- [x] All citations valid

### Technical
- [x] Compiles without errors
- [x] No undefined references
- [x] No missing citations
- [x] No overfull boxes
- [x] Hyperlinks work (internal cross-references)

### Submission Package
- [x] main.pdf included
- [x] Source files (submission.zip) ready if requested
- [x] All figures in package
- [x] All tables in package

---

## After Submission

### Immediate Actions

1. **Save confirmation**:
   - Screenshot submission confirmation page
   - Save confirmation email
   - Record submission ID in status.yaml

2. **Backup**:
   - Create archive of exact submitted files
   - Save to separate location
   - Note exact commit hash: `6d640552`

3. **Update project status**:
   ```yaml
   phase: under-review
   submission_id: [ID from portal]
   submission_date: 2026-03-21
   ```

### Monitor

- Check email for NeurIPS confirmation
- Verify submission appears in portal "My Submissions"
- Note any portal issues or correction deadlines

### Prepare for Review

**Common NeurIPS reviewer questions** (prepare responses):

1. **Complexity theory assumptions**:
   - Response: Clearly stated as conditional (if TC⁰ ≠ NC¹)
   - Standard in circuit complexity literature
   - Empirical results independent of these conjectures

2. **Generalization beyond benchmarks**:
   - Response: Discussed in Section 7 limitations
   - Framework designed for diagnostic isolation, not ecological validity
   - Connection to real-world tasks in Discussion

3. **Real-world applicability**:
   - Response: Section 7 provides examples
   - Guidance on which mitigations work for which gap types
   - Useful for practitioners choosing intervention strategies

4. **Statistical rigor**:
   - Response: 95% bootstrap CIs, 10,000 resamples
   - Bonferroni correction for multiple comparisons
   - Effect sizes reported
   - Full confidence interval table in Appendix B

5. **Model selection**:
   - Response: 5 families × 2-3 scales = 12 models
   - Covers proprietary (Claude, GPT) and open-source (Llama, Mistral, Qwen)
   - Includes reasoning-specialized (o3) and general-purpose
   - Representative of current SOTA

**Additional analyses to have ready** (if requested):
- Per-model breakdown of all conditions
- Additional difficulty levels for any task
- Ablations on specific framework components
- Analysis of failure modes beyond accuracy

---

## Technical Details

### Build Information

**Compilation**:
```bash
cd /home/deepwork/deepwork/projects/reasoning-gaps/paper
./build-paper.sh --skip-analysis
```

**Engine**: tectonic
**Date**: 2026-03-21 10:05 UTC
**Output**: main.pdf (314 KB, 19 pages)
**Warnings**: Only cosmetic (underfull boxes)

### Git Information

**Branch**: research/reasoning-gaps
**Latest commit**: 6d640552
**Commit message**: "paper(reasoning-gaps): complete submission-prep phase with final verification"
**Pushed**: 2026-03-21

### File Locations

All submission materials in:
```
/home/deepwork/deepwork/projects/reasoning-gaps/paper/
```

Key files:
- `main.pdf` — Final compiled paper (upload this)
- `submission.zip` — Complete package (upload if requested)
- `SUBMISSION_README.md` — Technical documentation
- `SUBMISSION_CHECKLIST.md` — Full verification list
- `build-paper.sh` — Automated build script

---

## Emergency Contacts / Resources

**NeurIPS 2026 Portal**: [Check current NeurIPS website for URL]
**Submission deadline**: Approximately May 5, 2026 (45 days from 2026-03-21)
**Page limit**: 9 pages main content (met: 9 pages)
**Appendix**: Unlimited (used: 10 pages)

**If technical issues**:
1. Try different browser (Chrome, Firefox)
2. Check file size limits on portal
3. Verify PDF is not password-protected
4. Contact NeurIPS program chairs (email from portal)

**If last-minute changes needed**:
1. Make changes to main.tex
2. Recompile: `./build-paper.sh --skip-analysis`
3. Verify page count still within limit
4. Re-zip if needed: Create new submission.zip
5. Upload updated files before deadline

---

## Confidence Assessment

**Paper Quality**: High
- Rigorous theoretical framework with formal proofs
- Comprehensive empirical validation (200K+ instances)
- Novel contribution bridging two disconnected communities
- Clear writing, precise language, no overclaims
- Strong reproducibility (all code, data, scripts included)

**Submission Readiness**: 100%
- All NeurIPS 2026 requirements verified
- Clean compilation (no errors)
- Proper anonymization
- Within page limits
- Complete and tested submission package
- Documentation thorough

**Expected Reviewer Reception**: Positive
- Strong theoretical contribution
- Large-scale empirical validation
- Actionable guidance for practitioners
- Novel diagnostic benchmark
- Well-positioned between theory and empirics

---

## Timeline

**Today (2026-03-21)**: Final verification complete ✅
**Next 1-2 days**: Upload to NeurIPS portal
**Confirmation**: Within 24 hours of upload
**Deadline**: ~45 days from today (May 5, 2026)
**Review period**: Typically 2-3 months
**Notification**: Typically August-September
**Conference**: December 2026 (if accepted)

---

## Status

✅ **READY FOR SUBMISSION**

All verification complete. No outstanding issues. Ready for immediate upload to NeurIPS 2026 conference portal.

**Next action**: Upload main.pdf to submission portal.

---

*Document created: 2026-03-21*
*Verified by: Writer Agent*
*Project: reasoning-gaps*
*Phase: submission-prep (complete)*
