# NeurIPS 2026 OpenReview Submission Guide

**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Date**: March 22, 2026
**Deadline**: May 6, 2026 (AoE) - Abstract deadline: May 4, 2026 (AoE)
**Days Remaining**: ~45 days

---

## Submission Portal

**OpenReview URL**: https://openreview.net/group?id=NeurIPS.cc/2026/Conference

The submission portal opens on **April 5, 2026**.

---

## Pre-Submission Requirements

### 1. OpenReview Account
- [ ] All authors must have OpenReview profiles created
- [ ] Ensure profile information is complete and up-to-date
- [ ] Log in at: https://openreview.net/

### 2. Verify Files Ready
All files are prepared in the `submission.zip` package (1.5 MB):

- [x] `main.pdf` — Complete paper (315 KB, 19 pages)
- [x] `main.tex` — LaTeX source (67 KB)
- [x] `neurips_2026.sty` — Style file (13 KB)
- [x] `benchmarks/analysis_output/` — All figures and tables

---

## Submission Checklist

### Step 1: Portal Access (After April 5, 2026)
1. Navigate to: https://openreview.net/group?id=NeurIPS.cc/2026/Conference
2. Click "NeurIPS 2026 Conference Submission" button
3. Log in with your OpenReview credentials
4. Start a new submission

### Step 2: Enter Metadata

#### Title
```
On the Reasoning Gaps of Large Language Models: A Formal Characterization
```

#### Abstract (Exact text from paper)
```
Large language models demonstrate remarkable reasoning capabilities on many tasks yet fail systematically on others that appear structurally similar. We develop a formal framework characterizing these reasoning gaps by connecting empirical failures to computational complexity theory. We define a taxonomy of six reasoning gap types grounded in the known circuit complexity bounds of transformers, derive five propositions predicting when chain-of-thought prompting should succeed or fail, and validate these predictions through evaluation of twelve models across 209,438 problem instances. Our results show that Types 2 and 3 gaps (depth and serial composition) exhibit mean CoT accuracy lift of +0.351, while Types 5 and 6 gaps (intractability and architectural limitations) show lift of only +0.094, consistent with theoretical predictions. We further demonstrate that tool augmentation provides 4× greater improvement than CoT alone for computational bottlenecks (Type 4). These findings suggest that reasoning gaps are not uniform—some are fundamental architectural constraints while others are addressable through scaffolding.
```

#### Keywords (Suggested)
- reasoning gaps
- chain of thought
- transformer expressiveness
- computational complexity
- circuit complexity
- large language models
- formal verification
- diagnostic benchmarks

#### Subject Areas (Select from NeurIPS categories)
Primary:
- Theory of Deep Learning
- Machine Learning Theory

Secondary:
- Large Language Models
- Evaluation and Interpretability
- Computational Complexity

### Step 3: Upload Files

#### Main Paper (Required)
- Upload: `main.pdf` (315 KB, 19 pages)
- Verify: PDF displays correctly in preview
- Confirm: Anonymization is correct (authors listed as "Anonymous")

#### Source Files (If Required by NeurIPS)
The portal may request LaTeX source files. If so:
- Option 1: Upload `submission.zip` (contains all files)
- Option 2: Upload individual files:
  - `main.tex`
  - `neurips_2026.sty`
  - All files from `benchmarks/analysis_output/` (figures and tables)

#### Supplementary Materials (Optional)
If the portal has a separate supplementary section:
- Upload: Additional documentation from `supplementary/` directory
- Include: Code, extended results, benchmark specifications

### Step 4: Author Information

Since the paper must be anonymized for review:
- DO NOT enter real author names yet
- Use "Anonymous" as author name
- Leave affiliations blank or as "Anonymous Institution"
- These will be updated if the paper is accepted

### Step 5: Conflicts of Interest

Declare conflicts with:
- Any researchers you've collaborated with in the past 3 years
- Anyone at your institution
- Anyone who has been your advisor or advisee

(This ensures fair reviewer assignment)

### Step 6: Reproducibility Checklist

NeurIPS requires a reproducibility checklist. Answer based on paper content:

**Code Availability**: Yes
- All evaluation code documented in supplementary materials
- Benchmark generators provided for all 9 tasks (B1-B9)
- Analysis pipeline fully automated

**Data Availability**: Yes
- Dataset format documented
- 209,438 evaluation instances
- Complete instance generation code provided

**Experimental Setup**: Fully Described
- 12 models specified with exact versions
- 9 benchmark tasks with controlled difficulty
- 4 evaluation conditions documented
- All hyperparameters listed

**Statistical Methods**: Documented
- Bootstrap confidence intervals (95%, 10,000 resamples)
- McNemar's test for paired comparisons
- All methods described in Section 5

**Computational Resources**: Documented
- Model API costs estimated (~$500 total)
- Evaluation runtime documented
- No special hardware required for reproduction

**Random Seeds**: N/A
- Evaluation is deterministic (no randomness)

### Step 7: Ethics Statement (If Required)

**Potential Negative Impacts**: Minimal
- This is a theoretical and empirical study of model capabilities
- No human subjects, no sensitive data
- Benchmarks are synthetic and non-harmful

**Broader Impacts**: Positive
- Helps practitioners understand LLM limitations
- Provides guidance on when to trust model outputs
- Contributes to safer AI deployment

### Step 8: Final Review

Before submitting:
- [ ] Preview the submission in OpenReview
- [ ] Verify PDF renders correctly
- [ ] Check all metadata is accurate
- [ ] Confirm abstract matches paper
- [ ] Verify page count (9 pages main content - within limit)
- [ ] Ensure anonymization is complete

### Step 9: Submit

1. Click "Submit" button
2. Confirm submission in any pop-up dialogs
3. Save the submission confirmation email
4. Note your submission ID for reference

---

## After Submission

### Immediate Actions
- [ ] Save submission confirmation email
- [ ] Bookmark your submission page on OpenReview
- [ ] Note the submission ID
- [ ] Share confirmation with co-authors

### During Review Period
- Monitor OpenReview for:
  - Reviewer questions (if any)
  - Requests for clarification
  - Updates from conference organizers

### Expected Timeline
- **May 6, 2026**: Submission deadline
- **June-August 2026**: Review period (estimated)
- **September 2026**: Notification of acceptance/rejection (estimated)
- **December 6-12, 2026**: Conference dates

---

## Troubleshooting

### PDF Upload Issues
- **Problem**: PDF too large
- **Solution**: Current PDF is 315 KB - well under typical 10 MB limit

### Missing Files
- **Problem**: Portal says files are missing
- **Solution**: All files are in `submission.zip` - extract and upload individually if needed

### Compilation Errors
- **Problem**: Portal cannot compile LaTeX
- **Solution**:
  1. Upload pre-compiled `main.pdf` instead
  2. Paper already compiles cleanly with tectonic/pdflatex
  3. See `SUBMISSION_README.md` for compilation instructions

### Anonymization Issues
- **Problem**: Portal flags identifying information
- **Solution**:
  - Paper already anonymized (verified in checklist)
  - Author field is "Anonymous"
  - No identifying URLs or affiliations

---

## Contact Information

**Conference Organizers**: Via OpenReview portal
**Technical Support**: OpenReview support team
**Submission Questions**: NeurIPS 2026 program chairs

---

## Important Notes

### Page Limit
✅ **Met**: 9 pages main content (within NeurIPS limit)
- Total: 19 pages (9 main + 10 appendix)
- Appendix does not count toward page limit

### Formatting
✅ **Correct**: Uses `neurips_2026.sty` style file
- Font size: Correct
- Margins: Correct
- References: Proper BibTeX formatting

### Anonymization
✅ **Complete**:
- No author names in PDF
- No affiliations
- No identifying URLs or acknowledgments
- Citations to own work: N/A (no self-citations)

---

## Quick Reference

**What to Upload**: `main.pdf` (315 KB) + source files if requested
**When to Submit**: Between April 5 - May 6, 2026
**Where to Submit**: https://openreview.net/group?id=NeurIPS.cc/2026/Conference
**Page Limit**: 9 pages main (✅ met)
**Anonymization**: Required (✅ complete)

---

## Files Location

All submission materials are in this directory:
```
/home/deepwork/deepwork/.worktrees/reasoning-gaps/projects/reasoning-gaps/paper/
```

Primary files:
- `main.pdf` - The paper (extracted from submission.zip)
- `submission.zip` - Complete submission package (1.5 MB)
- `SUBMISSION_README.md` - Technical documentation
- `SUBMISSION_CHECKLIST.md` - Pre-submission verification

---

## Verification Status

**Last Verified**: March 22, 2026
**Status**: ✅ READY FOR SUBMISSION
**All Checklist Items**: ✅ Complete

The paper is fully prepared and ready to upload to the NeurIPS 2026 OpenReview portal when it opens on April 5, 2026.
