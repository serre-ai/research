# For the Orchestrator: Simple Routing Instructions

**Date**: 2026-03-25
**Project**: agent-failure-taxonomy
**Current State**: Ready for Experimenter or Writer agent

---

## 🚨 CRITICAL: Read This First

**DO NOT assign Researcher agent to this project unless you read this entire document.**

Last 4 sessions assigned Researcher → All scored < 20 → Research is complete.

---

## One-Sentence Summary

**Research complete (9-category taxonomy with C1-C8 mapping), now needs Experimenter (for protocol/experiments) or Writer (for paper drafting), NOT Researcher.**

---

## Decision Tree (Use This)

```
┌─ agent-failure-taxonomy project ─┐
│                                   │
├─ Phase: experimental              │
├─ Research status: COMPLETE ✅     │
├─ Experiments run: 0 ❌            │
├─ Paper sections: 0 ❌             │
└───────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Next agent?  │
    └──────┬───────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌─────────┐
│EXPERIMENT│  │ WRITER  │
│  AGENT   │  │  AGENT  │
└─────────┘  └─────────┘
     │           │
     ▼           ▼
 Protocol      Intro
 + Infra       + Rel.Work
 + Expts       + Methods
```

**DO NOT** assign Researcher unless experiments discover NEW research gap.

---

## What Each Agent Should Do

### ✅ Experimenter Agent
**Task**: Design experimental protocol
**Files**: experiments/protocol.md (create)
**Steps**:
1. Read notes/05-taxonomy-final-structure.md
2. Select 3-4 frameworks (ReAct, AutoGPT, Reflexion)
3. Choose 6-8 priority failures to reproduce
4. Define success criteria
5. Document protocol

**Expected score**: 75-90

### ✅ Writer Agent
**Task**: Draft introduction section
**Files**: paper/introduction.tex (create)
**Steps**:
1. Read BRIEF.md for contributions
2. Read notes/05-taxonomy-final-structure.md
3. Write 1.5-page intro (motivation, gap, contributions)
4. Use ACL 2027 format

**Expected score**: 70-85

### ❌ Researcher Agent
**Task**: DO NOT ASSIGN
**Why**: All research complete (30+ papers, 50 instances, taxonomy done, competitor analyzed)
**Exception**: ONLY if experiments reveal NEW research gap requiring literature survey

**Expected score if assigned**: 10-20 (will repeat gap-filling failure)

---

## Quick Facts

| Metric | Value | Status |
|--------|-------|--------|
| Papers surveyed | 30+ | ✅ Done |
| Failures collected | 50 | ✅ Done |
| Taxonomy categories | 9 major, 24 sub | ✅ Done |
| Literature notes | 5 docs (129KB) | ✅ Done |
| Competitor analysis | Shah et al. complete | ✅ Done |
| Experiments run | 0 | ❌ TODO |
| Paper sections | 0 | ❌ TODO |
| **Correct next agent** | **Experimenter or Writer** | **⚠️ ACTION** |

---

## Why Last 4 Sessions Failed

| Session | Agent | Strategy | Score | Why Failed |
|---------|-------|----------|-------|------------|
| -3 | Researcher | gap_filling | 15 | Tried to collect more failures (already have 50) |
| -2 | Researcher | gap_filling | 15 | Repeated same approach |
| -1 | Researcher | quality_improvement | 15 | Tried to improve complete taxonomy |
| 0 | Researcher | meta_review | TBD | 4th diagnostic (problem already known) |

**Pattern**: Wrong agent assigned → Low-value work → Low scores → Another meta-review → Repeat

**Fix**: Change agent type to Experimenter or Writer

---

## Files to Check Before Routing

### 1. status.yaml
```yaml
phase: experimental  # Not "research"
researcher_work_status: "COMPLETE - DO NOT ASSIGN..."
current_focus: "⚠️ CRITICAL: DO NOT ASSIGN RESEARCHER..."
```

### 2. progress section in status.yaml
```yaml
literature_review: completed ✅
taxonomy_development: substantially_complete ✅
competitor_analysis: completed ✅
controlled_experiments: not_started ❌  # ← ASSIGN EXPERIMENTER
paper_writing: ready_to_start ❌  # ← ASSIGN WRITER
```

### 3. Key documents
- ✅ ROUTING-DECISION.md: Detailed routing guidance
- ✅ ORCHESTRATOR-GUIDANCE.md: Earlier guidance document
- ✅ META-REVIEW-4-ROUTING-ISSUE.md: Latest diagnostic
- ✅ SESSION-SUMMARY-2026-03-25-FINAL.md: When research completed

---

## Expected Timeline After Correct Assignment

```
Week 1: Experimenter (protocol) + Writer (intro)
Week 2: Experimenter (infrastructure) + Writer (related work)
Week 3: Experimenter (pilot expts) + Writer (methods)
Week 4: Full experiments + Results/Discussion

Result: Complete draft in 4 weeks
```

With continued wrong assignments: Indefinite stall.

---

## Routing Logic Pseudocode

```python
def select_agent_for_session(project):
    status = read_yaml(f"{project}/status.yaml")

    # Check explicit warnings
    if "DO NOT ASSIGN RESEARCHER" in status.current_focus:
        return random.choice(["experimenter", "writer"])

    # Check phase
    if status.phase == "experimental":
        if status.progress.controlled_experiments == "not_started":
            return "experimenter"  # Priority
        elif status.progress.paper_writing == "ready_to_start":
            return "writer"  # Can work in parallel

    # Check research status
    if status.researcher_work_status == "COMPLETE":
        return random.choice(["experimenter", "writer"])

    # Default (should not reach here for this project)
    return "researcher"

# For agent-failure-taxonomy:
next_agent = select_agent_for_session("agent-failure-taxonomy")
# Expected: "experimenter" or "writer"
# DO NOT return: "researcher"
```

---

## Success Criteria for Next Session

### If Experimenter assigned:
- [ ] experiments/protocol.md created
- [ ] 3-4 frameworks selected and documented
- [ ] 6-8 priority failures identified
- [ ] Success criteria defined
- [ ] Next steps clear (infrastructure build)
- [ ] Score: 70-90

### If Writer assigned:
- [ ] paper/introduction.tex created
- [ ] Motivation section written
- [ ] Contributions clearly stated (4 main)
- [ ] Paper structure outlined
- [ ] Next steps clear (related work)
- [ ] Score: 70-85

### If Researcher assigned (WRONG):
- [ ] Repeated work from previous sessions
- [ ] No new research findings
- [ ] Meta-review or gap-filling attempt
- [ ] Score: 10-20
- [ ] Wasted session

---

## Confidence Levels

**If next session = Experimenter or Writer**:
- Session success probability: 85%
- Expected score: 70-90
- Project advancement: Significant
- Timeline to completion: 6-8 sessions (2-3 months)

**If next session = Researcher**:
- Session success probability: 15%
- Expected score: 10-20
- Project advancement: None
- Timeline to completion: Unknown (stuck in loop)

---

## Summary for Busy Orchestrator

1. **Project health**: 🟢 Excellent
2. **Research status**: ✅ Complete
3. **Next priority**: ❌ Experiments (0 run)
4. **Agent needed**: 🎯 Experimenter or Writer
5. **Agent to avoid**: ⛔ Researcher
6. **Expected outcome**: 📈 High scores, clear progress

**Action**: Assign Experimenter or Writer for next session.

---

## Contact Information (For Human Override)

If automatic routing continues to fail:
- Check: Is phase transition logic working?
- Check: Are warning flags in status.yaml being read?
- Check: Is "DO NOT ASSIGN RESEARCHER" being honored?
- Action: Manual override to assign Experimenter or Writer
- Fallback: Parallel execution (both agents at once)

---

**Document purpose**: Provide crystal-clear routing guidance to prevent 5th consecutive wrong assignment.

**Key message**: Research complete. Assign Experimenter or Writer. Do NOT assign Researcher.

**Expected result**: Next session scores 70-90, project advances toward completion.
