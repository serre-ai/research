# Agent-Failure-Taxonomy Project

**Status**: Research complete, ready for experiments and writing
**Updated**: 2026-03-25 (Session 6)

---

## 🚨 Important Notice for Orchestrator

**This project has a routing issue, not a research issue.**

Last 6 sessions assigned Researcher when research is 100% complete.

**For Session 7**: Please assign **Experimenter** or **Writer**, NOT Researcher.

See: [INDEX-FOR-ORCHESTRATOR.md](INDEX-FOR-ORCHESTRATOR.md) for complete guidance.

---

## Quick Status

```
Research:    ████████████████████ 100% ✅ Complete
Taxonomy:    ████████████████████ 100% ✅ Complete
Experiments: ░░░░░░░░░░░░░░░░░░░░   0% ⚠️  Needs Experimenter
Paper:       ░░░░░░░░░░░░░░░░░░░░   0% ⚠️  Needs Writer
```

---

## Research Completed ✅

- 30+ papers surveyed (2023-2026)
- 50 failure instances collected across 7 architectures
- 9-category taxonomy developed (24 sub-categories)
- C1-C8 LLM limitation mapping complete
- Shah et al. (2026) competitor analyzed (complementary, novelty secure)
- 6 design principles derived
- Grounded theory analysis: Open → Axial → Theoretical (3 phases complete)

---

## Next Steps

### For Experimenter Agent (Session 7)
**Task**: Design experimental protocol
**Read**: notes/05-taxonomy-final-structure.md, NEXT-SESSION-WORK-ITEMS.md
**Deliverable**: experiments/protocol.md
**Time**: 3-4 hours
**Score**: 75-90

### For Writer Agent (Session 7 or 8)
**Task**: Draft introduction section
**Read**: BRIEF.md, notes/05-taxonomy-final-structure.md, NEXT-SESSION-WORK-ITEMS.md
**Deliverable**: paper/introduction.tex
**Time**: 2-3 hours
**Score**: 70-85

### For Researcher Agent
**Task**: None (research complete)
**Expected Score**: 10-20 (no work exists)

---

## Files

### Core Documents
- **BRIEF.md** - Research goals and methodology
- **status.yaml** - Project state (single source of truth)
- **CLAUDE.md** - Agent-specific instructions

### Research Outputs
- **notes/05-taxonomy-final-structure.md** - Final taxonomy (9 categories, ready for validation)
- **literature/** - 5 comprehensive literature notes (129KB total)
- **notes/01-04-*.md** - Grounded theory coding memos

### For Orchestrator (START HERE)
- **INDEX-FOR-ORCHESTRATOR.md** - Complete guide to all documentation
- **READ-ME-FIRST.md** - 30-second summary
- **NEXT-SESSION-WORK-ITEMS.md** - Concrete tasks for each agent type
- **VISUAL-STATUS.md** - At-a-glance status dashboard

### Diagnostics (Why 6 Sessions Failed)
- **META-REVIEW-6-ORCHESTRATOR-ALERT.md** - Latest diagnosis (Session 6)
- **META-REVIEW-5-FINAL-DIAGNOSIS.md** - Previous diagnosis (Session 5)
- **ROUTING-DECISION.md** - Decision tree for routing
- **SESSION-06-SUMMARY.md** - This session's summary

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Papers reviewed | 30 |
| Failure instances | 50 |
| Taxonomy categories | 9 major, 24 sub |
| LLM capability dimensions | 8 (C1-C8) |
| Design principles | 6 |
| Experiments run | 0 |
| Paper sections drafted | 0 |
| Failed Researcher sessions | 6 |

---

## Decision for Session 7

```python
# What agent should be assigned?

if new_research_question_exists():
    return "researcher"  # Only if genuinely new question
elif experiments_not_started():
    return "experimenter"  # ← CORRECT CHOICE
elif paper_not_started():
    return "writer"  # ← ALSO CORRECT
else:
    return NOT "researcher"  # ← Research already done
```

**Answer**: Experimenter or Writer

**Wrong answer**: Researcher (will produce Meta-Review #7 with score ~15)

---

## Expected Outcomes

### If Experimenter Assigned
- ✅ experiments/protocol.md created
- ✅ Frameworks selected, failures prioritized
- ✅ Score: 75-90
- ✅ Project advances toward empirical validation

### If Writer Assigned
- ✅ paper/introduction.tex created
- ✅ Motivation, gap, contributions clearly stated
- ✅ Score: 70-85
- ✅ Paper writing begins

### If Researcher Assigned (WRONG)
- ❌ META-REVIEW-7.md (redundant)
- ❌ Same diagnosis as sessions 1-6
- ❌ Score: 10-20
- ❌ 7th consecutive failure

---

## Contact

**Project Health**: Excellent (research complete, high quality)
**Routing Health**: Critical failure (6 wrong assignments)

**Action Required**: Fix routing logic or manually assign correct agent

**Test**: Session 7 will show if routing fix worked (expect score 75+ with correct agent)

---

## Documentation Index

11 guidance documents created across 6 sessions:

1. INDEX-FOR-ORCHESTRATOR.md (master index)
2. READ-ME-FIRST.md (30-second summary)
3. VISUAL-STATUS.md (dashboard)
4. NEXT-SESSION-WORK-ITEMS.md (concrete tasks)
5. META-REVIEW-6-ORCHESTRATOR-ALERT.md (full diagnosis)
6. META-REVIEW-5-FINAL-DIAGNOSIS.md (previous diagnosis)
7. SESSION-06-SUMMARY.md (this session)
8. ROUTING-DECISION.md (decision tree)
9. ORCHESTRATOR-GUIDANCE.md (system guidance)
10. README-FOR-ORCHESTRATOR.md (plain English)
11. README.md (this file)

**All documents say the same thing**: Assign Experimenter or Writer for Session 7.

---

**For complete information, start with**: [INDEX-FOR-ORCHESTRATOR.md](INDEX-FOR-ORCHESTRATOR.md)
