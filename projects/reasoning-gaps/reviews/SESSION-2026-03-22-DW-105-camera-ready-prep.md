# Writer Session Report: DW-105 Camera-Ready Preparation

**Date**: 2026-03-22
**Task**: DW-105 - NeurIPS: Camera-ready preparation (conditional)
**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Status**: Guide created (task premature - awaiting acceptance)

---

## Task Assessment

### Task Status: PREMATURE (Preparation Guide Created)

Linear task DW-105 requests camera-ready preparation for NeurIPS 2026. However, camera-ready work cannot begin until:

1. **Paper submission** (deadline: May 6, 2026) — Portal opens April 5
2. **Review period** (May-July 2026) — Reviews expected July 2026
3. **Rebuttal submission** (July 2026) — Response to reviewer feedback
4. **Acceptance notification** (August 2026) — ~25% acceptance rate
5. **Camera-ready instructions** (August 2026) — Provided with acceptance

**Current state**: Paper ready for submission (phase: awaiting-portal) but not yet submitted. Camera-ready work is ~5-6 months premature.

**Timeline**:
- Today: March 22, 2026
- Submission deadline: May 6, 2026 (45 days away)
- Expected acceptance notification: August 2026 (140+ days away)
- Expected camera-ready deadline: September 2026 (170+ days away)

### Why Camera-Ready Cannot Be Done Now

Camera-ready preparation requires:

1. **Reviewer feedback**: Changes promised in rebuttal must be incorporated
2. **Meta-reviewer guidance**: Specific revisions requested for final version
3. **Acceptance confirmation**: Camera-ready only relevant if paper accepted
4. **Official instructions**: NeurIPS provides camera-ready style file and requirements only after acceptance
5. **De-anonymization approval**: Cannot de-anonymize until acceptance confirmed

None of these prerequisites are currently available.

---

## Work Completed

Since direct camera-ready preparation is premature, I created comprehensive preparation infrastructure to enable rapid execution when acceptance occurs.

### Created: CAMERA_READY_GUIDE.md (4,682 lines)

**Location**: `projects/reasoning-gaps/paper/CAMERA_READY_GUIDE.md`

**Contents**: Complete workflow for camera-ready preparation, including:

#### 1. Timeline and Overview
- Estimated timeline from submission to camera-ready (May-September 2026)
- Camera-ready deadline context (typically 4-6 weeks after acceptance)
- Prerequisite checklist (acceptance notification, instructions, reviewer feedback)

#### 2. Phase-by-Phase Checklist (8 Phases)

**Phase 1: De-anonymization (Day 1-2)**
- Author information (names, affiliations, emails)
- Acknowledgments section (funding, compute, reviewers, colleagues)
- Metadata updates (title, abstract, keywords, ORCID)
- LaTeX templates for author block and acknowledgments

**Phase 2: Content Revisions from Reviewer Feedback (Day 3-7)**
- Incorporate all reviewer comments from initial reviews
- Implement all changes promised in rebuttal
- Address meta-reviewer requests
- Revision log format for tracking changes

**Phase 3: Figure and Table Polish (Day 5-8)**
- Figure quality standards (300+ DPI, colorblind-safe, readable fonts)
- Table improvements (confidence intervals, formatting, clarity)
- Float placement optimization
- Per-figure checklist template

**Phase 4: References and Citations (Day 6-9)**
- Bibliography completeness (add reviewer suggestions, update preprints)
- Citation formatting consistency
- Citation hygiene (et al., DOIs, special characters)
- Specific papers to check (Song et al., Raju & Netrapalli, Ye et al.)

**Phase 5: Supplementary Materials (Day 7-10)**
- Code release (clean repo, README, license, reproduction instructions)
- Data release (benchmark datasets, evaluation outputs, metadata)
- Extended results (full tables, ablations, statistical details)
- Supplementary PDF structure template

**Phase 6: Presentation Materials (Day 10-14)**
- Conference poster (36" × 48", design template, sections)
- Presentation slides (5-min spotlight or 15-min oral, structure)
- Video presentation (if required, 1920×1080, MP4)

**Phase 7: Final Verification (Day 12-14)**
- LaTeX compilation (pdflatex + bibtex, check warnings)
- Page limit verification (9 pages main + unlimited appendix)
- Formatting compliance (margins, fonts, line spacing)
- Content review (proofread, equations, notation, acronyms)
- Figure/table final check
- Link and reference validation

**Phase 8: OpenReview Upload (Day 14)**
- Prepare upload packages (PDF, source, supplementary)
- OpenReview submission workflow
- Copyright form completion

#### 3. Common Camera-Ready Revisions

Based on typical NeurIPS reviewer feedback:
- **Theoretical clarity**: Definitions, intuitions, examples, assumptions
- **Empirical rigor**: Statistical tests, confidence intervals, effect sizes, ablations
- **Related work**: Concurrent work, positioning, fair acknowledgment
- **Presentation**: Figure quality, captions, jargon reduction, transitions
- **Limitations**: Expanded discussion, threats to validity, concrete future work

#### 4. Day-by-Day Timeline

14-day camera-ready timeline from acceptance notification:
- **Week 1**: De-anonymization, reviewer feedback implementation, reference updates
- **Week 2**: Figure/table polish, supplementary materials, presentation prep, upload

#### 5. Files to Prepare

Complete file list:
- **Paper files**: main.tex, main.pdf, style file, references.bib, figures/tables
- **Supplementary files**: supplementary.pdf, code.zip, data.zip, README.md
- **Presentation files**: poster.pdf, slides.pdf, video.mp4 (if required)
- **Administrative files**: copyright_form.pdf, checklist

#### 6. NeurIPS Requirements (Typical)

Expected requirements based on previous conferences:
- **Page limit**: 9 pages main + unlimited appendix
- **File format**: PDF/A, < 10 MB, fonts embedded, 300+ DPI figures
- **Style file**: NeurIPS 2026 camera-ready style (final option, not preprint)
- **Supplementary material**: Optional, < 100 MB typical

#### 7. Contingency Planning

Strategies for tight deadlines or major revisions:
- **Prioritization order**: De-anonymization → rebuttal promises → figures → references → supplementary → poster
- **Major revisions requested**: Focused timeline, contact program chairs if infeasible
- **Additional experiments**: Feasibility assessment, extension request, async execution

#### 8. Post-Upload Tasks

After camera-ready submission:
- **Archive**: Tag release, save materials, preserve reviewer comments
- **Publicity**: Social media, blog post, website update, Google Scholar
- **Code release**: De-anonymize repo, add paper link, citation info
- **Conference prep**: Travel booking, registration, poster printing, presentation practice

---

## Guide Design Principles

The guide is designed to be:

1. **Comprehensive**: Covers all aspects of camera-ready preparation
2. **Actionable**: Checklists, templates, specific instructions at each step
3. **Realistic**: 14-day timeline assumes dedicated work, with contingency plans
4. **Conditional**: Explicitly notes that work cannot begin until acceptance
5. **Evidence-based**: Uses typical NeurIPS requirements and common reviewer feedback patterns
6. **Project-specific**: References this paper's figures, tables, benchmarks, and structure

---

## Why This Approach

### Preparatory Planning Reduces Execution Friction

Creating the guide now (before acceptance) provides several benefits:

1. **Faster execution**: When acceptance arrives, can begin immediately without planning overhead
2. **Comprehensive coverage**: Time to think through all requirements without deadline pressure
3. **Reduced stress**: Clear roadmap reduces cognitive load during intense camera-ready period
4. **Quality assurance**: Checklist prevents forgetting critical steps
5. **Time management**: Day-by-day timeline helps allocate effort efficiently

### Similar to Rejection Contingency Plan (DW-106)

This follows the same preparatory planning approach as the rejection contingency plan created earlier today (DW-106):
- **Plan created before triggering event** (acceptance or rejection)
- **Operationally complete** so execution can begin immediately
- **Reduces decision-making under time pressure**
- **Improves outcome quality** by thoughtful advance planning

### Conditional Execution

The guide is **conditional on acceptance**:
- Cannot de-anonymize before acceptance
- Cannot incorporate reviewer feedback without reviews
- Cannot use camera-ready style file before it's released
- Cannot prepare poster/presentation before acceptance confirmed

But having the guide ready means the **14-day camera-ready period can be fully utilized for execution** rather than planning.

---

## Current Project Status

### Paper Submission Status
- **Phase**: awaiting-portal (portal opens April 5, 2026)
- **Submission deadline**: May 6, 2026 (45 days away)
- **Files ready**: main.pdf (315 KB, 19 pages), submission.zip (1.5 MB)
- **Guides created**:
  - OPENREVIEW_SUBMISSION_GUIDE.md (comprehensive submission instructions)
  - SUBMISSION_QUICK_START.md (5-minute reference)
  - CAMERA_READY_GUIDE.md (this guide, created today)

### Contingency Planning Completed
- **Rebuttal preparation**: REBUTTAL_PREPARATION_GUIDE.md (DW-104, created 2026-03-22)
- **Rejection contingency**: REJECTION_CONTINGENCY_PLAN.md (DW-106, created 2026-03-22)
- **Camera-ready preparation**: CAMERA_READY_GUIDE.md (DW-105, created today)

### What Can Be Done Now vs Later

**Can do now**:
- ✅ Create preparation guides (done)
- ✅ Verify submission materials ready (done)
- ✅ Plan camera-ready workflow (done)

**Cannot do until acceptance** (August 2026):
- ❌ De-anonymize paper (requires acceptance confirmation)
- ❌ Incorporate reviewer feedback (requires reviews)
- ❌ Prepare poster/presentation (requires acceptance)
- ❌ Upload camera-ready files (requires acceptance notification)

---

## Recommendation

**Task DW-105 Status**: BLOCKED until acceptance notification (expected August 2026)

**Rationale**:
1. Camera-ready work requires acceptance confirmation (not yet submitted)
2. Requires reviewer feedback (reviews expected July 2026)
3. Requires NeurIPS camera-ready instructions (provided with acceptance)
4. Timeline: ~5-6 months premature

**Preparation Complete**:
- ✅ CAMERA_READY_GUIDE.md created (4,682 lines)
- ✅ Complete workflow from de-anonymization to upload
- ✅ Day-by-day 14-day timeline
- ✅ Checklists, templates, and contingency plans
- ✅ Ready to execute immediately when acceptance occurs

**Next Action**: Reschedule DW-105 for **August 2026** (after expected acceptance notification).

---

## Files Created

1. **projects/reasoning-gaps/paper/CAMERA_READY_GUIDE.md** (NEW)
   - 4,682 lines
   - 8 preparation phases
   - 14-day timeline
   - Complete checklist

2. **projects/reasoning-gaps/reviews/SESSION-2026-03-22-DW-105-camera-ready-prep.md** (THIS FILE)
   - Session documentation
   - Task assessment
   - Recommendation

---

## Summary

Linear task DW-105 requests camera-ready preparation, but the task is **5-6 months premature** — the paper has not been submitted yet (portal opens April 5), and camera-ready work requires acceptance notification (expected August 2026).

Instead of attempting premature camera-ready work, I created **comprehensive preparation infrastructure** (CAMERA_READY_GUIDE.md, 4,682 lines) covering all 8 phases of camera-ready preparation from de-anonymization to OpenReview upload. This guide enables **rapid execution when acceptance occurs** (expected late August 2026, camera-ready deadline ~4 weeks later).

The guide includes:
- Phase-by-phase workflow (de-anonymization → revisions → polish → upload)
- Day-by-day 14-day timeline
- Complete checklists and templates
- NeurIPS requirements and common revisions
- Contingency planning for tight deadlines or major revisions
- Post-upload tasks (publicity, code release, conference prep)

**Recommendation**: Mark DW-105 as **blocked** until acceptance notification (August 2026). All preparation work is complete and ready for immediate execution if/when acceptance occurs.

---

**Session End**: March 22, 2026
**Files Modified**: 2 (CAMERA_READY_GUIDE.md created, session report created)
**Status**: Preparation guide complete, task appropriately blocked
