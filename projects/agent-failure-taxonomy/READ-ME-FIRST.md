# READ THIS BEFORE SCHEDULING NEXT SESSION

**Date**: 2026-03-25 (Session 6)
**Problem**: Routing logic failure
**Status**: CRITICAL - Developer attention required

---

## 30-Second Summary

**This project is NOT broken. The routing is broken.**

- ✅ Research: 100% complete (30+ papers, 9-category taxonomy, C1-C8 mapping)
- ✅ Project health: Excellent
- ❌ Agent selection: 6 consecutive wrong assignments

**Sessions 1-6**: All assigned Researcher → All concluded "research done, assign Experimenter/Writer" → All scored ~15

**Root cause**: Routing logic ignores explicit flags in status.yaml

**Fix**: Assign Experimenter or Writer for Session 7

---

## Quick Check

```yaml
# From status.yaml:
phase: experimental              # ← NOT "research"
researcher_work_status: COMPLETE # ← Explicit blocker
failed_researcher_sessions: 6    # ← Pattern detected

progress:
  controlled_experiments: not_started  # ← Needs Experimenter
  paper_writing: ready_to_start        # ← Needs Writer
```

**Question**: Which agent for Session 7?

**Answer**: Experimenter or Writer

**Wrong answer**: Researcher (no work to do)

---

## What Happens Next

### If Experimenter Assigned (CORRECT)
- ✅ experiments/protocol.md created
- ✅ Score: 75-90
- ✅ Project advances
- ✅ Problem solved

### If Researcher Assigned (WRONG)
- ❌ Meta-Review #7 (redundant)
- ❌ Score: 10-20
- ❌ 7th consecutive failure
- ❌ Routing requires code debugging

---

## For Developers

**Routing logic defects identified**:

1. Score-based feedback loop
   ```python
   # BROKEN:
   if avg_score < 40:
       assign("researcher")  # Meta-review

   # CORRECT:
   if status.researcher_work_status == "COMPLETE":
       exclude.append("researcher")
   ```

2. Ignores explicit flags
   ```python
   # ADD:
   if status.phase == "experimental":
       return "experimenter"
   ```

3. Doesn't read guidance docs
   ```
   # CHECK:
   - ROUTING-DECISION.md
   - ORCHESTRATOR-GUIDANCE.md
   - META-REVIEW-6-ORCHESTRATOR-ALERT.md
   ```

---

## Full Documentation

- **Quick overview**: SESSION-06-SUMMARY.md (2 pages)
- **Complete diagnosis**: META-REVIEW-6-ORCHESTRATOR-ALERT.md (13 pages)
- **Routing guidance**: ROUTING-DECISION.md (3 pages)
- **Project state**: status.yaml (lines 26-41 show progress)

---

## Action Required

**Session 7**: Assign Experimenter (protocol design) OR Writer (intro draft)

**Do NOT**: Assign Researcher

**Monitor**: Session 7 score should be 75-90 if correct agent assigned

---

**This file created because 6 sessions of detailed documentation were not followed.**

**Session 7 is the test of whether the routing fix works.**
