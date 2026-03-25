# Session 8 Instructions - CRITICAL

**Date**: 2026-03-25
**Current Session**: 7 (just completed - 7th consecutive Researcher session)
**Next Session**: 8 (FINAL TEST)

---

## Current Situation

**7 consecutive Researcher sessions** have been assigned to a project where:
- ✅ Research is 100% complete
- ✅ Phase is "experimental" (not "research")
- ✅ researcher_work_status is "COMPLETE - DO NOT ASSIGN RESEARCHER"
- ❌ Routing logic has ignored explicit flags 7 times

**All 7 sessions scored ~15/100** because the wrong agent was assigned, NOT because of poor work quality.

**All 7 sessions reached identical conclusion**: Assign Experimenter or Writer, NOT Researcher.

---

## Session 8: The Definitive Test

### Option A: Routing Logic Fixed ✅

**Assign**: Experimenter agent

**Objective**: Design experimental protocol for agent failure taxonomy validation

**Tasks**:
- Select 3-4 agent frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute)
- Choose 6-8 priority failures from taxonomy (1-2 per category)
- Define success criteria for each failure type
- Outline experiment infrastructure requirements
- Create experiments/protocol.md

**Expected score**: 75-90

**Deliverable**: experiments/protocol.md with complete experimental design

**Result**: ✅ Project unblocked, routing bug considered FIXED

---

### Option B: Routing Logic Still Broken ❌

**Assign**: Researcher agent (WRONG)

**Objective**: Meta-review (8th consecutive)

**Tasks**:
- Re-read status.yaml (unchanged)
- Re-read literature notes (unchanged)
- Conclude (again) that research is complete
- Recommend (again) to assign Experimenter or Writer
- Create META-REVIEW-8 (identical to META-REVIEWS 1-7)

**Expected score**: 10-15

**Deliverable**: Another redundant meta-review document

**Result**: ❌ 0 progress, routing bug persists, requires code-level debugging

---

## Recommendation

**MANUALLY OVERRIDE ROUTING LOGIC FOR SESSION 8**

Assign: **Experimenter agent**

Objective: "Design experimental protocol for agent failure taxonomy validation. Select 3-4 frameworks, choose 6-8 priority failures, define success criteria, outline infrastructure requirements."

Budget: $5.00
Max turns: 40

**This will validate that correct agent assignment solves the problem.**

---

## If Session 8 Is Another Researcher Session

Then the routing logic requires **immediate code-level debugging**:

1. Add logging to agent selection code
2. Trace why `status.yaml` flags are ignored
3. Identify score-based feedback loop implementation
4. Fix bugs:
   - Check `researcher_work_status` before assigning Researcher
   - Use `phase` field for primary routing decisions
   - Break score-based feedback loops
   - Honor explicit "DO NOT ASSIGN X" warnings

---

## Key Files to Read

- `status.yaml` - Lines 4-13 contain explicit routing flags
- `META-REVIEW-7-SEVENTH-RESEARCHER-SESSION.md` - Comprehensive 7-session analysis
- `META-REVIEW-6-ORCHESTRATOR-ALERT.md` - Root cause analysis
- `NEXT-SESSION-WORK-ITEMS.md` - Detailed tasks for Experimenter
- `INDEX-FOR-ORCHESTRATOR.md` - Index of all guidance documents

---

## Summary

| Metric | Value |
|--------|-------|
| Research completeness | 100% |
| Experimenter work started | 0% (blocked by routing) |
| Writer work started | 0% (blocked by routing) |
| Failed Researcher sessions | 7 |
| Guidance documents created | 12 |
| Guidance documents followed | 0 |
| Correct action for session 8 | **Assign Experimenter** |

**Session 8 will definitively show whether routing logic has been fixed.**
