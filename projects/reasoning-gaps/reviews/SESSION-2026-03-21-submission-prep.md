# Writer Session Report
**Date**: 2026-03-21
**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Draft version**: v1.0 (final submission)
**Phase**: submission-prep

---

## Work Done

### 1. Paper Compilation
- Compiled paper using tectonic LaTeX engine
- Verified successful compilation: 19 pages (9 main + 10 appendix), 314 KB PDF
- Reviewed compilation warnings: only cosmetic (underfull boxes), no errors
- Confirmed all references, citations, and cross-references resolve correctly

### 2. Submission Package Creation
- Generated submission.zip package (1.5 MB total)
- Package contents verified:
  - main.pdf (314 KB, 19 pages)
  - main.tex (67 KB)
  - neurips_2026.sty (13 KB)
  - benchmarks/analysis_output/ (all figures, tables, stats)
- Tested package integrity: no corruption, all files extractable

### 3. Documentation Created
- **SUBMISSION_README.md**: Complete submission instructions
  - Compilation instructions (tectonic and pdflatex)
  - Paper structure summary
  - Key contributions and results
  - Reproducibility information
  - Dataset statistics
  - Build date and checklist

- **SUBMISSION_CHECKLIST.md**: Comprehensive verification checklist
  - Document requirements (✅ all verified)
  - Content requirements (✅ all verified)
  - Anonymization (✅ verified)
  - Figures and tables (✅ all referenced)
  - References (✅ complete)
  - Reproducibility (✅ documented)
  - Supplementary materials (✅ organized)
  - Submission package (✅ ready)
  - Technical verification (✅ clean compilation)
  - Content quality (✅ verified)

### 4. Status Updates
- Updated status.yaml:
  - Added `paper_compilation` entry (complete)
  - Updated `next_steps` (removed completed tasks)
  - Updated `notes` (compilation successful)
  - Updated `current_activity` (ready for portal upload)
  - Added decision log entry for compilation and packaging

### 5. Quality Verification
- **Page limit**: 9 pages main content ✅ (within NeurIPS limit)
- **Anonymization**: "Anonymous" author, no identifying information ✅
- **Figures**: All 5 figures referenced in text ✅
- **Tables**: All 4 main tables referenced in text ✅
- **Citations**: 40+ references, all valid ✅
- **Statistical rigor**: 95% bootstrap CIs, 10,000 resamples ✅
- **Reproducibility**: Complete documentation in supplementary materials ✅

---

## Critic Requirements Addressed

No critic review exists for this submission. This is the initial submission to NeurIPS 2026.

---

## Key Results Verified in Paper

### Framework Validation
- Types 2,3 (depth/serial gaps): CoT lift = +0.351
- Types 5,6 (intractability/architectural gaps): CoT lift = +0.094
- Difference validates theoretical predictions (p < 0.001)

### Intervention Analysis
- Type 4 (computational gap): Tool-use lift = +0.635
- Tool use 4× more effective than CoT alone
- Budget sweep validates Proposition 2 predictions

### Model-Specific Results
- Claude 4.6 Opus: 100% on B3 (CoT), 75% on B6 (CoT)
- 2× next best model, demonstrating capacity effects
- All results include 95% bootstrap confidence intervals

### Empirical Scale
- 12 models evaluated (5 families)
- 209,438 total instances
- 9 diagnostic tasks (B1-B9)
- 4 evaluation conditions

---

## Open Issues

**None**. All submission requirements verified and complete.

---

## Next Steps

### Immediate (Today/Tomorrow)
1. **Upload to NeurIPS submission portal**
   - Create/log in to account
   - Upload main.pdf
   - Upload source files (if required)
   - Enter metadata (title, abstract, keywords)
   - Confirm reproducibility checklist
   - Submit before deadline

### Post-Submission
2. **Monitor submission status**
   - Track submission confirmation
   - Note submission ID
   - Monitor for any portal issues

3. **Prepare for review period**
   - Review common NeurIPS reviewer questions
   - Prepare potential rebuttal materials
   - Consider additional analyses if needed

### If Revisions Needed
4. **Reviewer response preparation**
   - Address comments systematically
   - Run additional experiments if requested
   - Update paper based on feedback
   - Prepare detailed response document

---

## Compilation Details

### Build Command
```bash
cd /home/deepwork/deepwork/projects/reasoning-gaps/paper
./build-paper.sh --skip-analysis
```

### Build Output
```
[3/5] Compiling LaTeX with tectonic...
note: Running TeX ...
note: Rerunning TeX because "main.out" changed ...
note: Rerunning TeX because "main.aux" changed ...
note: Running xdvipdfmx ...
note: Writing `main.pdf` (314.20 KiB)
```

### Warnings
- Underfull \hbox warnings: Cosmetic only (LaTeX line-breaking)
- Underfull \vbox warnings: Cosmetic only (page-breaking)
- No overfull boxes (no text overflow)
- No undefined references
- No missing citations

---

## Files Created/Modified

### Created
- `/projects/reasoning-gaps/paper/SUBMISSION_README.md` (4.8 KB)
- `/projects/reasoning-gaps/paper/SUBMISSION_CHECKLIST.md` (7.2 KB)
- `/projects/reasoning-gaps/paper/main.pdf` (314 KB) [gitignored]
- `/projects/reasoning-gaps/paper/submission.zip` (1.5 MB)
- `/projects/reasoning-gaps/reviews/SESSION-2026-03-21-submission-prep.md` (this file)

### Modified
- `/projects/reasoning-gaps/status.yaml` (updated progress, decisions, notes)
- `/projects/reasoning-gaps/paper/main.tex` (minor: recompiled)

### Git Commits
1. `17ed39b3` - "paper(reasoning-gaps): compile paper and create submission package"
2. `f82fa56c` - "paper(reasoning-gaps): add comprehensive submission checklist"

---

## Decision Log Entry

**Date**: 2026-03-21
**Decision**: Compile paper and create submission package using tectonic
**Rationale**: Paper compilation successful: 19 pages (9 main + 10 appendix), 314 KB PDF, clean compilation with only cosmetic warnings. submission.zip package (1.5 MB) contains all required files: main.pdf, main.tex, neurips_2026.sty, and benchmarks/analysis_output/ directory with all figures/tables. SUBMISSION_README.md created with complete checklist, reproducibility instructions, and verification that all submission requirements met. Paper ready for NeurIPS portal upload.

---

## Summary

The paper is **submission-ready**. All NeurIPS 2026 requirements verified:

✅ Document format (19 pages, NeurIPS style)
✅ Page limit (9 main pages, within limit)
✅ Anonymization (verified)
✅ Compilation (clean, tectonic)
✅ Figures/Tables (all referenced)
✅ Citations (complete, valid)
✅ Reproducibility (fully documented)
✅ Submission package (1.5 MB, integrity verified)
✅ Documentation (README + checklist)

**Next action**: Upload submission.zip to NeurIPS 2026 conference portal.

---

## Paper Metadata

**Title**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Venue**: NeurIPS 2026
**Format**: 19 pages (9 main + 10 appendix)
**File size**: 314 KB (PDF), 1.5 MB (submission package)
**Models evaluated**: 12 (Claude, GPT, Llama, Mistral, Qwen)
**Total instances**: 209,438
**Statistical rigor**: 95% bootstrap CIs, 10,000 resamples
**Deadline**: 45 days from 2026-03-21

**Status**: ✅ **READY FOR SUBMISSION**
