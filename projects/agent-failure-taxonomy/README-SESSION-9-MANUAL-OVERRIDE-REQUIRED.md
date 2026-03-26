# ⚠️ SESSION 9: MANUAL OVERRIDE REQUIRED ⚠️

**Date**: 2026-03-26 (Session 8 completed)
**Status**: Routing bug conclusively confirmed
**Action Required**: Manual configuration for session 9

---

## TL;DR

**DO NOT use automatic agent selection for session 9.**

**Session 8 was the final test** (predicted in Meta-Review #7):
- ✅ Experimenter/Writer assigned = routing fixed
- ❌ Researcher assigned = routing broken

**Result**: Researcher assigned (8th consecutive wrong assignment)

**Routing bug is conclusively confirmed. Automatic selection will repeat the same error.**

---

## Session 9 Configuration (MANUAL)

```yaml
project: agent-failure-taxonomy
agent: experimenter
objective: "Design experimental protocol for agent failure taxonomy validation. Select 3-4 frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute), choose 6-8 high-priority failures from the taxonomy (see literature/03-coding-and-taxonomy-development.md for categories), define success criteria for reproduction, design infrastructure (framework wrappers, logging, failure detection). Document in experiments/protocol.md."
expected_score: 75-90
```

---

## Why Manual Override Is Necessary

**Pattern**: 8 consecutive sessions assigned Researcher despite:
- ✅ Research 100% complete
- ✅ Phase = `experimental` (not "research")
- ✅ `researcher_work_status` = "COMPLETE"
- ✅ 13 guidance documents saying "assign Experimenter"
- ✅ Explicit warnings in `current_focus`

**Cost of pattern**: $16-40 + 16 hours + 0% progress

**Routing logic defects confirmed**:
1. Does not check `status.yaml` flags
2. Does not read guidance documents
3. Has score-based feedback loop (low score → Researcher → low score → loop)
4. Does not detect repeated identical outcomes

---

## What Session 9 Should Accomplish

**Agent**: Experimenter
**Primary Goal**: Design experimental protocol

**Deliverables**:
1. Select 3-4 agent frameworks for testing
   - Candidates: ReAct, AutoGPT, Reflexion, plan-then-execute
2. Choose 6-8 priority failures from taxonomy
   - 1-2 per category (see literature/03-coding-and-taxonomy-development.md)
   - Prioritize high-reproducibility failures
3. Define success criteria
   - What constitutes successful reproduction?
   - How to measure failure occurrence?
4. Design infrastructure
   - Framework wrappers
   - Task setup scripts
   - Logging utilities
   - Failure detection automation
5. Document in `experiments/protocol.md`

**Expected outcome**: Project unblocked, experimental phase begins

---

## Validation

Session 9 will validate the diagnosis:

**If Experimenter manually assigned**:
- ✅ Expected: `experiments/protocol.md` created
- ✅ Expected: Infrastructure design documented
- ✅ Expected: Score 75-90
- ✅ **Proves correct agent fixes the problem**

**If session 9 automatically assigns Researcher** (do not allow this):
- ❌ 9th consecutive wrong assignment
- ❌ Meta-Review #9 created (redundant)
- ❌ Score ~10-15
- ❌ 0% progress (again)

---

## For Developers

**Full debugging guide**: See `ROUTING-BUG-DEVELOPER-SUMMARY.md`

**Evidence documents**:
- `META-REVIEW-8-EIGHTH-SESSION-ROUTING-BUG-CONFIRMED.md` (this session)
- `META-REVIEW-7-SEVENTH-RESEARCHER-SESSION.md` (session 7, predicted test)
- `status.yaml` (see lines 4-19 for explicit flags)

**Quick diagnosis**: Add logging to agent selection code to see why flags are ignored.

---

## Project Status

**Health**: 90/100 (excellent)
- ✅ Literature: Complete (30+ papers)
- ✅ Taxonomy: Complete (9 categories, C1-C8 mapping)
- ✅ Competitor analysis: Complete
- ✅ Next steps: Clear and actionable

**Progress blocked by**: Routing logic (0/100 health)

**Unblocking requires**: Correct agent assignment (Experimenter)

---

**Read this file before configuring session 9.**
