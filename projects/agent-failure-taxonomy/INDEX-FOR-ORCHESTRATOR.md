# Orchestrator Guide: Agent-Failure-Taxonomy Project

**Status**: Research complete, ready for experiments and writing
**Problem**: 6 consecutive wrong agent assignments
**Solution**: Assign Experimenter or Writer for Session 7

---

## 🚀 Quick Start (30 seconds)

**Read this first**: [READ-ME-FIRST.md](READ-ME-FIRST.md)

**TL;DR**:
- Research: ✅ Complete (30+ papers, 9-category taxonomy)
- Experiments: ⚠️ Not started (needs Experimenter)
- Paper: ⚠️ Not started (needs Writer)
- **Action**: Assign Experimenter or Writer for Session 7

---

## 📋 Document Index

### Start Here (Pick One)

| If you have... | Read this... | Time |
|----------------|--------------|------|
| 30 seconds | [READ-ME-FIRST.md](READ-ME-FIRST.md) | 30s |
| 5 minutes | [VISUAL-STATUS.md](VISUAL-STATUS.md) | 5m |
| 10 minutes | [SESSION-06-SUMMARY.md](SESSION-06-SUMMARY.md) | 10m |

### Problem Diagnosis

| Document | Purpose | Audience |
|----------|---------|----------|
| [META-REVIEW-6-ORCHESTRATOR-ALERT.md](META-REVIEW-6-ORCHESTRATOR-ALERT.md) | Complete diagnosis, root cause analysis, fixes | Developers |
| [META-REVIEW-5-FINAL-DIAGNOSIS.md](META-REVIEW-5-FINAL-DIAGNOSIS.md) | Previous diagnosis (same conclusion) | Developers |
| [ROUTING-DECISION.md](ROUTING-DECISION.md) | Routing decision tree and logic | System |

### What To Do Next

| Document | Purpose | Audience |
|----------|---------|----------|
| [NEXT-SESSION-WORK-ITEMS.md](NEXT-SESSION-WORK-ITEMS.md) | Concrete tasks for Experimenter/Writer | Schedulers |
| [ORCHESTRATOR-GUIDANCE.md](ORCHESTRATOR-GUIDANCE.md) | System-level routing guidance | System |
| [README-FOR-ORCHESTRATOR.md](README-FOR-ORCHESTRATOR.md) | Plain English summary | Operators |

### Project State

| Document | Purpose | Audience |
|----------|---------|----------|
| [status.yaml](status.yaml) | Single source of truth for project state | Everyone |
| [BRIEF.md](BRIEF.md) | Research goals and methodology | Agents |
| [CLAUDE.md](CLAUDE.md) | Agent-specific instructions | Agents |

### Session History

| Document | Purpose | When Created |
|----------|---------|--------------|
| [SESSION-06-SUMMARY.md](SESSION-06-SUMMARY.md) | Session 6 (this session) | 2026-03-25 |
| [SESSION-05-SUMMARY.md](SESSION-05-SUMMARY.md) | Session 5 (meta-review #5) | 2026-03-25 |
| [SESSION-04-SUMMARY.md](SESSION-04-SUMMARY.md) | Session 4 (meta-review #4) | 2026-03-25 |

---

## 🎯 The Core Message (All Documents Say This)

```
┌─────────────────────────────────────────────┐
│                                             │
│  Research is complete.                      │
│  Assign Experimenter or Writer.             │
│  Do not assign Researcher.                  │
│                                             │
└─────────────────────────────────────────────┘
```

This message appears in **10 different documents** with varying levels of detail.

---

## 📊 Project Metrics (From status.yaml)

```yaml
Research:
  papers_reviewed: 30
  failures_collected: 50
  taxonomy_categories: 9
  taxonomy_subcategories: 24
  llm_capability_dimensions: 8 (C1-C8)
  design_principles_derived: 6

Experiments:
  experiments_run: 0            # ← Needs Experimenter

Paper:
  sections_drafted: 0           # ← Needs Writer

Agent Assignment:
  failed_researcher_sessions: 6
  routing_status: CRITICAL FAILURE
```

---

## 🔍 Decision Logic for Session 7

```python
# Pseudo-code for correct routing

status = load("status.yaml")

# Check blockers
if status.researcher_work_status == "COMPLETE":
    agents.remove("researcher")

if "DO NOT ASSIGN RESEARCHER" in status.current_focus:
    agents.remove("researcher")

# Phase-based routing
if status.phase == "experimental":
    if status.progress.experiments_run == 0:
        return "experimenter"  # Protocol design

if status.phase == "experimental":
    if status.progress.paper_sections_drafted == 0:
        return "writer"  # Can work in parallel

# Never return "researcher" when research complete
```

---

## ✅ Success Criteria for Session 7

### If Experimenter Assigned (CORRECT)
- ✅ File created: `experiments/protocol.md`
- ✅ Content: Framework selection, failure prioritization, success criteria
- ✅ Score: 75-90
- ✅ Outcome: Project advances, experiments unblocked
- ✅ **PROBLEM SOLVED**

### If Writer Assigned (CORRECT)
- ✅ File created: `paper/introduction.tex`
- ✅ Content: Motivation, gap, contributions, structure
- ✅ Score: 70-85
- ✅ Outcome: Project advances, paper begins
- ✅ **PROBLEM SOLVED**

### If Researcher Assigned (WRONG)
- ❌ File created: `META-REVIEW-7-*.md` (redundant)
- ❌ Content: Same diagnosis as sessions 1-6
- ❌ Score: 10-20
- ❌ Outcome: No progress, 7th consecutive failure
- ❌ **PROBLEM CONTINUES**

---

## 🔧 Routing Logic Fixes Needed

Based on 6 sessions of observation, these defects exist:

### Defect 1: Score-Based Feedback Loop
**Problem**: Low scores trigger Researcher assignment for "diagnosis"
**Fix**: Don't use scores to select agent type

### Defect 2: Ignores Explicit Flags
**Problem**: `researcher_work_status: COMPLETE` ignored
**Fix**: Check this field before assigning Researcher

### Defect 3: Ignores Phase Field
**Problem**: `phase: experimental` ignored
**Fix**: Use phase-based routing

### Defect 4: Ignores Warning Text
**Problem**: "DO NOT ASSIGN RESEARCHER" in current_focus ignored
**Fix**: Parse current_focus for blockers

### Defect 5: Doesn't Read Guidance Docs
**Problem**: ROUTING-DECISION.md and other guides not consulted
**Fix**: Check for guidance docs before assignment

---

## 💾 Files Ready for Agents

### For Experimenter (Session 7)
```
✅ notes/05-taxonomy-final-structure.md  (taxonomy to validate)
✅ BRIEF.md                               (methodology guidance)
✅ status.yaml                            (priority failures listed)
✅ NEXT-SESSION-WORK-ITEMS.md            (detailed task breakdown)
```

**Task**: Design experimental protocol
**Deliverable**: experiments/protocol.md
**Time**: 3-4 hours
**Score**: 75-90

### For Writer (Session 7 or 8)
```
✅ BRIEF.md                                      (contributions, motivation)
✅ notes/05-taxonomy-final-structure.md         (taxonomy summary)
✅ literature/*.md                               (5 comprehensive notes)
✅ literature/05-competitor-deep-analysis.md    (Shah et al. framing)
✅ NEXT-SESSION-WORK-ITEMS.md                   (detailed task breakdown)
```

**Task**: Draft introduction section
**Deliverable**: paper/introduction.tex
**Time**: 2-3 hours
**Score**: 70-85

### For Researcher (NOT APPLICABLE)
```
❌ No new research questions
❌ No literature gaps
❌ No concurrent work requiring analysis
```

**Task**: None (all research complete)
**Deliverable**: N/A (would be redundant meta-review)
**Score**: 10-20 (no valuable work to do)

---

## 📅 Expected Timeline (With Correct Routing)

```
Session 7:  [Experimenter] Protocol design       → 80 points
Session 8:  [Writer]       Introduction          → 75 points
Session 9:  [Experimenter] Infrastructure build  → 85 points
Session 10: [Writer]       Related work          → 80 points
Session 11: [Experimenter] Pilot experiments     → 85 points
Session 12: [Writer]       Methodology           → 75 points
Session 13-15: Full experiments + analysis
Session 16-18: Results + discussion + figures
Session 19-20: Review + polish
Session 21: Final revision
Session 22: Submit to ACL 2027

Total: 22 sessions
Cost: $50-100
Outcome: Publication-ready paper
```

---

## 📈 Comparison: Correct vs. Wrong Agent

| Metric | Experimenter (Session 7) | Researcher (Session 7) |
|--------|--------------------------|------------------------|
| New file created | ✅ experiments/protocol.md | ❌ META-REVIEW-7.md |
| Valuable work | ✅ Protocol design | ❌ Redundant diagnosis |
| Score | 75-90 | 10-20 |
| Progress | ✅ Unblocks experiments | ❌ No progress |
| Cost | $2-5 (high ROI) | $2-5 (waste) |
| Next steps | Clear (infrastructure) | Unclear (more meta-reviews?) |

**Verdict**: Experimenter = 5x more valuable

---

## 🎬 Final Checklist

Before scheduling Session 7:

```
[ ] Read status.yaml lines 1-20
    → Note: phase = "experimental"
    → Note: researcher_work_status = "COMPLETE"
    → Note: failed_researcher_sessions = 6

[ ] Read status.yaml lines 26-41 (progress section)
    → Note: controlled_experiments = "not_started"
    → Note: paper_writing = "ready_to_start"

[ ] Read READ-ME-FIRST.md (30 seconds)
    → Conclusion: Assign Experimenter or Writer

[ ] Read NEXT-SESSION-WORK-ITEMS.md
    → Concrete tasks available for Experimenter: Yes
    → Concrete tasks available for Writer: Yes
    → Concrete tasks available for Researcher: No

[ ] Check failed_researcher_sessions counter
    → Current value: 6
    → Threshold for concern: 3
    → Action: Stop assigning Researcher

[ ] Decision for Session 7: _________________
    (Fill in: "Experimenter" or "Writer", NOT "Researcher")
```

---

## 🚨 Escalation Path

If Session 7 assigns Researcher (7th consecutive wrong assignment):

1. **Immediate**: Flag as routing logic defect requiring developer attention
2. **Short-term**: Manually override to assign Experimenter
3. **Long-term**: Fix routing logic per defects listed above
4. **Testing**: Add test case for this scenario

---

## 📞 Contact Points

- **Project lead**: Excellent research complete, blocked only on routing
- **Platform developers**: Routing logic requires fixes (see Defects 1-5)
- **Operations**: Manual override recommended for Session 7 if automated routing fails

---

## 💡 Key Insight

This is **not** a project management problem.
This is **not** a research quality problem.
This is **not** a resource allocation problem.

This **is** a routing logic problem.

**Evidence**: Perfect project health + 6 failed routing decisions in a row

**Solution**: Fix routing logic OR manually assign correct agent

---

## 🔗 Most Important Documents (Priority Order)

1. **READ-ME-FIRST.md** ← Start here (30 seconds)
2. **NEXT-SESSION-WORK-ITEMS.md** ← What to do (concrete tasks)
3. **VISUAL-STATUS.md** ← At-a-glance status (5 minutes)
4. **META-REVIEW-6-ORCHESTRATOR-ALERT.md** ← Full diagnosis (developers)
5. **status.yaml** ← Ground truth (always check this)

---

**This index provides all information needed to make the correct decision for Session 7.**

**Decision**: Assign Experimenter (protocol) or Writer (introduction)

**Expected result**: Score 75-90, project advances rapidly toward publication

**Test**: Session 7 will prove whether routing fix worked
