# NeurIPS 2026 Camera-Ready Preparation Guide

**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Created**: March 22, 2026
**Status**: PREPARATION GUIDE (conditional on acceptance)

---

## Overview

This guide provides a complete workflow for preparing the camera-ready version of the paper if accepted to NeurIPS 2026. Camera-ready preparation typically occurs in August-September 2026, after notification of acceptance.

**IMPORTANT**: This document is a preparation guide only. Camera-ready work cannot begin until:
1. Paper is submitted (deadline: May 6, 2026)
2. Reviews are received and rebuttal submitted (expected: July 2026)
3. Acceptance notification received (expected: August 2026)
4. Camera-ready instructions released by NeurIPS

---

## Timeline (Estimated)

| Date | Event |
|------|-------|
| April 5, 2026 | Portal opens |
| May 6, 2026 | Submission deadline |
| May-July 2026 | Review period |
| July 2026 | Rebuttal period |
| **August 2026** | **Acceptance notification** |
| **September 2026** | **Camera-ready deadline (estimated)** |
| December 6-12, 2026 | NeurIPS 2026 conference |

Camera-ready deadline is typically **4-6 weeks after acceptance notification**.

---

## Camera-Ready Checklist

### Phase 1: De-anonymization (Day 1-2)

#### Author Information
- [ ] Add author names to paper
- [ ] Add author affiliations
- [ ] Add author email addresses (corresponding author marked with *)
- [ ] Verify author order is correct
- [ ] Update OpenReview submission with author information

**Author Block Template** (update `main.tex`):
```latex
\author{%
  Author Name 1\thanks{Corresponding author: email@institution.edu} \\
  Institution Name \\
  \texttt{email1@institution.edu} \\
  \And
  Author Name 2 \\
  Institution Name \\
  \texttt{email2@institution.edu} \\
  % Add additional authors as needed
}
```

#### Acknowledgments
- [ ] Add acknowledgments section before references
- [ ] Thank funding sources (grants, fellowships)
- [ ] Thank compute providers (if applicable)
- [ ] Thank reviewers for feedback (standard practice)
- [ ] Thank colleagues who provided feedback
- [ ] Acknowledge dataset/benchmark creators (if using external benchmarks)

**Acknowledgments Template**:
```latex
\section*{Acknowledgments}
We thank the anonymous NeurIPS reviewers for their thoughtful feedback, which substantially improved this work. [Add specific acknowledgments: funding sources, compute grants, colleagues, etc.]
```

#### Metadata Updates
- [ ] Ensure title matches final version (may have changed during revision)
- [ ] Update abstract if revised during rebuttal
- [ ] Verify keywords match subject areas
- [ ] Check that all author ORCID iDs are included (if required)

---

### Phase 2: Content Revisions from Reviewer Feedback (Day 3-7)

#### Incorporate Reviewer Feedback
- [ ] Review all reviewer comments from initial reviews
- [ ] Review all reviewer comments from rebuttal response
- [ ] Identify all promised changes from rebuttal
- [ ] Implement each promised change:
  - [ ] Additional experiments (if any)
  - [ ] Clarifications to text
  - [ ] Additional related work citations
  - [ ] Expanded discussion sections
  - [ ] Additional ablations
  - [ ] Improved figures/tables
- [ ] Track each change in a revision log

**Revision Log Format**:
```markdown
## Camera-Ready Revisions

### Reviewer 1
- [ ] R1.1: Clarify TC⁰ assumption in Section 3.2 (promised in rebuttal)
- [ ] R1.2: Add comparison to [Song et al. 2026] (promised in rebuttal)

### Reviewer 2
- [ ] R2.1: Expand discussion of limitation in Section 6
- [ ] R2.2: Add error bars to Figure 3

### Reviewer 3
- [ ] R3.1: Include tool-use ablation results from rebuttal
```

#### Address Meta-Reviewer Requests
- [ ] Read meta-reviewer comments carefully
- [ ] Implement any specific requests from meta-reviewer
- [ ] Ensure all meta-reviewer concerns are addressed

---

### Phase 3: Figure and Table Polish (Day 5-8)

#### Figure Quality
- [ ] Regenerate all figures at publication quality (300+ DPI)
- [ ] Ensure all text in figures is readable (font size ≥ 8pt)
- [ ] Use colorblind-friendly color schemes
- [ ] Verify figures render correctly in grayscale
- [ ] Add detailed captions (should be understandable without main text)
- [ ] Ensure all axis labels are clear and units specified
- [ ] Check figure aspect ratios and sizing
- [ ] Verify all figures referenced in text

**Figure Checklist per Figure**:
```markdown
Figure 1: CoT Effectiveness by Gap Type
- [ ] DPI ≥ 300
- [ ] Font size ≥ 8pt
- [ ] Colorblind-safe palette
- [ ] Grayscale readable
- [ ] Caption complete
- [ ] Axis labels clear
- [ ] Referenced in Section 5.1
```

#### Table Quality
- [ ] Verify all numerical values are correct
- [ ] Add confidence intervals where appropriate
- [ ] Use consistent number formatting (decimal places)
- [ ] Bold/highlight key results
- [ ] Ensure table captions are complete
- [ ] Check column headers are clear
- [ ] Verify all tables fit page width
- [ ] Ensure all tables referenced in text

#### Figure/Table Placement
- [ ] Check that all floats (figures/tables) appear near their first reference
- [ ] Avoid orphaned floats (figures far from their text)
- [ ] Ensure no figures/tables pushed to end of paper
- [ ] Verify appendix figures are clearly labeled

---

### Phase 4: References and Citations (Day 6-9)

#### Bibliography Completeness
- [ ] Verify all cited works are in bibliography
- [ ] Check for uncited works in bibliography (remove if not referenced)
- [ ] Add any new citations from reviewer suggestions
- [ ] Verify all arXiv papers have been updated to published versions (if applicable)
- [ ] Check for preprints that have been published since submission

**Citation Update Checklist**:
- [ ] Check Song et al. (TMLR 2026) - verify published version
- [ ] Check Raju & Netrapalli (arXiv 2026) - check if published
- [ ] Check Ye et al. (arXiv 2026) - check if published
- [ ] Update Yang et al. (NeurIPS 2025) with final publication details

#### Citation Formatting
- [ ] Ensure all citations use consistent format
- [ ] Verify DOIs are included (if required by NeurIPS style)
- [ ] Check author name formatting (first/last name order)
- [ ] Verify venue names are complete and correct
- [ ] Check page numbers are included
- [ ] Verify year is correct for all citations

#### Citation Hygiene
- [ ] Search for common citation errors:
  - [ ] "et al." used correctly (only when >2 authors in text, all authors in bib)
  - [ ] Conference vs journal formatting
  - [ ] Capitalization in titles
  - [ ] Special characters rendered correctly
- [ ] Run BibTeX and check for warnings
- [ ] Verify no duplicate entries

---

### Phase 5: Supplementary Materials (Day 7-10)

#### Code Release
- [ ] Clean up evaluation code
- [ ] Add comprehensive README
- [ ] Add requirements.txt or environment.yml
- [ ] Include example usage
- [ ] Add license (MIT or Apache 2.0 recommended)
- [ ] Test on fresh environment
- [ ] Add reproduction instructions
- [ ] Create GitHub repository (can be anonymized for submission, de-anonymized for camera-ready)

**Code Repository Structure**:
```
reasoning-gaps/
├── README.md                 # Overview, installation, usage
├── LICENSE                   # Open source license
├── requirements.txt          # Dependencies
├── benchmarks/              # Benchmark tasks
│   ├── B1_parity.py
│   ├── B2_formula_eval.py
│   └── ...
├── experiments/             # Evaluation scripts
│   ├── run_evaluation.py
│   ├── analysis_pipeline.py
│   └── results/
└── notebooks/               # Analysis notebooks
    └── results_analysis.ipynb
```

#### Data Release
- [ ] Prepare benchmark dataset files
- [ ] Include data format documentation
- [ ] Add data generation scripts (if synthetic)
- [ ] Verify data completeness (all 9 benchmarks)
- [ ] Include evaluation outputs (model responses, scores)
- [ ] Add metadata (model versions, dates, costs)
- [ ] Verify data adheres to any license requirements

#### Extended Results
- [ ] Include full results tables (all models, all conditions)
- [ ] Add per-instance analysis
- [ ] Include additional ablations mentioned but not in main paper
- [ ] Add computational cost analysis
- [ ] Include statistical test details
- [ ] Add supplementary figures

**Supplementary PDF Structure**:
```
1. Extended Results
   - Full accuracy tables (all model × task × condition combinations)
   - Per-task breakdown with confidence intervals
   - Statistical test details (effect sizes, p-values)

2. Additional Ablations
   - Prompt variations
   - Temperature sensitivity
   - Budget scaling analysis (extended)

3. Benchmark Specifications
   - Complete task definitions
   - Example problems with solutions
   - Difficulty calibration details

4. Theoretical Details
   - Full proofs for all propositions
   - Additional lemmas
   - Complexity-theoretic background

5. Error Analysis
   - Failure mode categorization
   - Example errors by gap type
   - Qualitative analysis
```

---

### Phase 6: Presentation Materials (Day 10-14)

#### Conference Poster
- [ ] Design poster (standard size: 36" × 48" or A0)
- [ ] Include: title, authors, affiliations
- [ ] Structure: Introduction → Framework → Experiments → Results → Conclusions
- [ ] Use large fonts (title ≥ 72pt, body ≥ 24pt)
- [ ] Include key figures from paper
- [ ] Add QR code to paper/code
- [ ] Export to PDF (high resolution)
- [ ] Print test version to check readability

**Poster Template Sections**:
1. Title and Authors (top)
2. Problem and Gap (left column)
3. Formal Framework (center-left)
4. Empirical Validation (center-right)
5. Key Results (right column)
6. Conclusions and Future Work (bottom)

#### Presentation Slides (if spotlight/oral)
- [ ] Check if paper accepted as spotlight/oral (different from poster)
- [ ] Create slide deck (NeurIPS typically: 5-minute spotlight or 15-minute oral)
- [ ] Structure:
  - [ ] Slide 1: Title, authors, one-sentence contribution
  - [ ] Slide 2-3: Problem motivation and gap
  - [ ] Slide 4-5: Formal framework (high-level)
  - [ ] Slide 6-8: Empirical results (key figures)
  - [ ] Slide 9: Conclusions and takeaways
- [ ] Practice timing
- [ ] Export to PDF

#### Video Presentation (if required)
NeurIPS sometimes requests pre-recorded video presentations:
- [ ] Check camera-ready instructions for video requirements
- [ ] Record 5-minute presentation
- [ ] Include: motivating example, framework overview, key results
- [ ] Use slides + voiceover
- [ ] Export to required format (typically MP4, 1920×1080)
- [ ] Upload to designated platform

---

### Phase 7: Final Verification (Day 12-14)

#### LaTeX Compilation
- [ ] Compile with `pdflatex` three times (for references)
- [ ] Run `bibtex` to process bibliography
- [ ] Check for LaTeX warnings:
  - [ ] No undefined references
  - [ ] No missing citations
  - [ ] No overfull hboxes (or acceptable only)
  - [ ] No multiply defined labels
- [ ] Verify PDF renders correctly
- [ ] Check PDF file size (typically must be < 10 MB)

#### Page Limit Verification
- [ ] Check NeurIPS 2026 camera-ready page limit (typically 9 pages main + unlimited appendix)
- [ ] Verify main content fits within limit
- [ ] Check that appendix is clearly marked
- [ ] Ensure references are not counted toward page limit

#### Formatting Compliance
- [ ] Verify using NeurIPS 2026 camera-ready style file (may differ from submission style)
- [ ] Check margins are correct
- [ ] Verify font sizes (body text typically 10pt)
- [ ] Ensure line spacing is correct
- [ ] Check that no content is cut off

#### Content Review
- [ ] Proofread entire paper (fresh read-through)
- [ ] Check for typos and grammatical errors
- [ ] Verify all equations are correctly formatted
- [ ] Check mathematical notation consistency
- [ ] Verify all symbols defined before use
- [ ] Ensure all acronyms expanded on first use
- [ ] Check for consistent terminology throughout

#### Figure/Table Final Check
- [ ] All figures render correctly in PDF
- [ ] All tables display properly
- [ ] All captions are complete
- [ ] All labels are legible
- [ ] No overlapping text or elements
- [ ] Color schemes are consistent

#### Link and Reference Check
- [ ] All \cref and \ref commands work
- [ ] All \cite commands resolve
- [ ] All URLs in paper are accessible (if any)
- [ ] All DOIs are correct (if included)
- [ ] All footnotes render correctly

---

### Phase 8: OpenReview Upload (Day 14)

#### Prepare Upload Package
- [ ] Create camera-ready PDF: `reasoning_gaps_camera_ready.pdf`
- [ ] Create source package: `reasoning_gaps_source.zip` containing:
  - [ ] main.tex
  - [ ] neurips_2026.sty (camera-ready version)
  - [ ] All figure files
  - [ ] All table files
  - [ ] Bibliography file (.bib)
  - [ ] Any additional LaTeX files
- [ ] Create supplementary package: `reasoning_gaps_supplementary.zip` containing:
  - [ ] Code repository
  - [ ] Data files
  - [ ] Extended results PDF
  - [ ] README

#### OpenReview Submission
- [ ] Log in to OpenReview
- [ ] Navigate to accepted paper submission page
- [ ] Upload camera-ready PDF
- [ ] Upload source files (if required)
- [ ] Upload supplementary materials
- [ ] Update metadata:
  - [ ] Add author names
  - [ ] Add affiliations
  - [ ] Add acknowledgments
  - [ ] Update abstract (if revised)
  - [ ] Update keywords (if revised)
- [ ] Verify all uploads successful
- [ ] Check PDF preview renders correctly
- [ ] Submit before deadline

#### Copyright Form
- [ ] Complete NeurIPS copyright transfer form (if required)
- [ ] Determine copyright arrangement:
  - [ ] NeurIPS holds copyright (typical)
  - [ ] Authors retain copyright (if allowed)
  - [ ] CC-BY license (if allowed)
- [ ] Upload signed copyright form

---

## Common Camera-Ready Revisions

Based on typical NeurIPS reviewer feedback, anticipate these common revision requests:

### Theoretical Clarity
- Strengthen formal definitions (especially Definition 1-6)
- Add intuitive explanations before formal statements
- Include more examples illustrating non-obvious concepts
- Clarify assumptions in propositions

### Empirical Rigor
- Add more statistical tests
- Include confidence intervals on all results
- Report effect sizes, not just significance
- Add ablation studies
- Include failure case analysis

### Related Work
- Add recent concurrent work (papers published after submission)
- Strengthen positioning vs closely related work
- Acknowledge limitations of prior work fairly
- Add missing relevant citations

### Presentation
- Improve figure quality and readability
- Clarify table captions
- Reduce jargon in introduction
- Add roadmap paragraph
- Improve section transitions

### Limitations and Future Work
- Expand limitations section
- Discuss threats to validity
- Acknowledge scope boundaries
- Suggest concrete next steps (not vague "future work")

---

## Checklist: Day-by-Day Timeline

If camera-ready deadline is **14 days** from acceptance notification:

### Week 1: Content and Revisions
- **Day 1-2**: De-anonymize paper, add acknowledgments, review all reviewer feedback
- **Day 3-5**: Implement all promised changes from rebuttal, address reviewer concerns
- **Day 6-7**: Update references, check for newly published versions of preprints

### Week 2: Polish and Materials
- **Day 8-10**: Polish figures/tables, prepare supplementary materials (code, data, extended results)
- **Day 11-12**: Create poster, prepare presentation (if spotlight/oral)
- **Day 13**: Final proofreading, verification, compile and test
- **Day 14**: Upload to OpenReview, submit copyright form, verify submission

---

## Files to Prepare

### Paper Files
- `main.tex` — De-anonymized LaTeX source
- `main.pdf` — Camera-ready PDF
- `neurips_2026.sty` — Camera-ready style file
- `references.bib` — Updated bibliography
- All figure/table files

### Supplementary Files
- `supplementary.pdf` — Extended results and details
- `code.zip` — Evaluation code and scripts
- `data.zip` — Benchmark data and results
- `README.md` — Instructions for code/data

### Presentation Files
- `poster.pdf` — Conference poster (36" × 48")
- `slides.pdf` — Spotlight/oral presentation (if applicable)
- `video.mp4` — Pre-recorded presentation (if required)

### Administrative Files
- `copyright_form.pdf` — Signed copyright transfer form
- `camera_ready_checklist.md` — Verification checklist

---

## NeurIPS Camera-Ready Requirements (Typical)

Based on previous NeurIPS conferences, expect:

### Page Limit
- Main content: **9 pages** (title, abstract, body, references)
- Appendix: **Unlimited** (clearly marked, supplementary material)
- Acknowledgments: Does NOT count toward page limit

### File Format
- PDF/A format (for archival)
- File size: < 10 MB (main paper)
- Fonts: All fonts embedded
- Resolution: Figures at 300+ DPI

### Style File
- Use NeurIPS 2026 camera-ready style (will be provided after acceptance)
- DO NOT modify style file
- Use `\usepackage[final]{neurips_2026}` (not `[preprint]`)

### Supplementary Material
- No size limit (within reason, < 100 MB typical)
- Can include: code, data, videos, extended proofs, additional experiments
- Supplementary material is optional but recommended

---

## Contact and Support

### NeurIPS 2026 Program Chairs
Check camera-ready instructions for contact information (typically provided in acceptance email).

### OpenReview Support
- Technical issues: support@openreview.net
- Submission questions: program-chairs@neurips.cc

---

## Contingency Planning

### If Camera-Ready Deadline is Tight
**Prioritize in this order:**
1. De-anonymization and acknowledgments (required)
2. Promised changes from rebuttal (required)
3. Figure/table improvements (high impact)
4. Reference updates (medium impact)
5. Supplementary materials (desirable but optional)
6. Poster/presentation (can be done closer to conference)

### If Major Revisions Requested
If meta-reviewer requests substantial changes:
- **Day 1**: Assess scope of changes, create detailed plan
- **Day 2-8**: Focus exclusively on requested changes
- **Day 9-12**: Integrate changes, test, verify
- **Day 13-14**: Final polish and upload
- **Defer**: Poster and supplementary materials to later (if necessary)

### If Additional Experiments Requested
If reviewers request new experiments:
- Assess feasibility within camera-ready timeline
- If infeasible, contact program chairs to request extension or clarification
- Consider running experiments asynchronously and including in supplementary material
- Update paper text to reference supplementary experiments

---

## Post-Upload Tasks

After camera-ready upload:

### Archive
- [ ] Archive all camera-ready materials in project repository
- [ ] Tag GitHub release: `v1.0-camera-ready`
- [ ] Archive submitted PDF separately
- [ ] Save all reviewer comments and rebuttal

### Publicity
- [ ] Prepare Twitter/social media announcement
- [ ] Draft blog post summarizing contributions
- [ ] Update personal website with paper link
- [ ] Add to Google Scholar profile
- [ ] Update CV/resume

### Code Release
- [ ] De-anonymize GitHub repository
- [ ] Add paper link to repository README
- [ ] Add citation information
- [ ] Announce code release on social media

### Conference Preparation
- [ ] Book travel to NeurIPS (December 6-12, 2026)
- [ ] Register for conference
- [ ] Book accommodation
- [ ] Print poster (high quality)
- [ ] Prepare for poster presentation:
  - [ ] Practice 2-minute summary
  - [ ] Prepare answers to anticipated questions
  - [ ] Bring laptop with slides/code demo

---

## Notes

**This guide is comprehensive but conditional.** Actual camera-ready requirements will be specified by NeurIPS 2026 program committee in the acceptance notification email (expected August 2026).

**Key principle**: Camera-ready is not a complete rewrite. Focus on:
1. Fulfilling promises from rebuttal
2. Fixing errors and typos
3. Polishing presentation
4. Adding acknowledgments and de-anonymizing

**Do not** introduce new contributions, change the framing, or make major structural changes unless explicitly requested by reviewers.

---

**Last Updated**: March 22, 2026
**Next Review**: After acceptance notification (August 2026)
