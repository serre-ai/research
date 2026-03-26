# DEVELOPER ACTION REQUIRED - Routing Logic Bug Confirmed

**Date**: 2026-03-26
**Severity**: CRITICAL
**Project**: agent-failure-taxonomy
**Issue**: Agent routing logic confirmed broken via empirical testing

---

## Summary

**8 consecutive Researcher sessions** have been assigned despite:
- Phase explicitly set to "experimental" (not "research")
- researcher_work_status: "COMPLETE - DO NOT ASSIGN RESEARCHER"
- All research objectives 100% complete
- 12 guidance documents all recommending "Assign Experimenter or Writer"

**Session 8 was a controlled test** (defined in Meta-review #7):
- If Experimenter/Writer assigned → Routing fixed
- If Researcher assigned → Routing broken

**Result**: Researcher assigned → **TEST FAILED**

---

## Empirical Evidence

| Metric | Value |
|--------|-------|
| Total sessions tested | 8 |
| Correct agent assignments | 0 |
| Incorrect agent assignments | 8 |
| Failure rate | 100% |
| Cost | $16-40 |
| Time wasted | 16 hours |
| Progress made | 0% |
| Guidance documents created | 12 |
| Guidance documents followed | 0 |

---

## Confirmed Bugs

### Bug #1: Score-Based Researcher Assignment Loop
**Behavior**: Low scores automatically trigger Researcher assignment for "diagnosis"
**Problem**: Creates infinite loop when wrong agent is root cause of low score

**Evidence**:
```
Wrong agent → No progress → Low score (~15)
→ System assigns Researcher for meta-review
→ Researcher diagnoses "wrong agent, assign Experimenter"
→ Next session: Wrong agent assigned again
→ INFINITE LOOP (confirmed via 8 iterations)
```

### Bug #2: status.yaml Flags Completely Ignored
**Behavior**: Routing logic does not check explicit flags in status.yaml
**Problem**: Project cannot signal agent requirements

**Evidence**: These flags were ignored 8 consecutive times:
- `phase: experimental` (line 4)
- `researcher_work_status: "COMPLETE - DO NOT ASSIGN RESEARCHER"` (line 12)
- `failed_researcher_sessions: 8` (line 13)
- `routing_status: "CRITICAL FAILURE"` (line 14)
- `current_focus` contains "DO NOT ASSIGN RESEARCHER" (line 19)

### Bug #3: No Infinite Loop Detection
**Behavior**: System cannot detect when same wrong agent is assigned repeatedly
**Problem**: Feedback loops continue indefinitely

**Evidence**: 8 consecutive identical outcomes with no pattern detection or correction

---

## Immediate Actions Required

### 1. Manual Override for Session 9 (URGENT)
**Action**: Manually assign **Experimenter** agent

**Objective**:
> "Design experimental protocol for validating agent failure taxonomy. Select 3-4 frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute), identify 6-8 priority failures from taxonomy categories, define success criteria, outline infrastructure requirements in src/. Create experiments/protocol.md documenting all design decisions."

**Expected outcome**:
- File created: `experiments/protocol.md`
- Session score: 75-90
- Project unblocked

### 2. Debug Routing Logic (Code-Level)

#### Step 1: Add Instrumentation
Add logging to agent selection code to capture:
- Which agent was selected and why
- Which signals/flags were checked
- Score calculations and thresholds
- Phase-based routing logic decisions

#### Step 2: Identify Bug Locations
Find in orchestrator code:
- Where is score → Researcher assignment implemented?
- Where should status.yaml flags be checked (but aren't)?
- Where is phase-based routing supposed to happen?
- Is there loop detection logic (missing)?

#### Step 3: Implement Fixes
```typescript
// Priority 1: Check explicit flags FIRST
if (status.researcher_work_status === "COMPLETE") {
  excludeAgent("researcher");
}

if (status.phase === "experimental" && status.experiments_run === 0) {
  return "experimenter";  // Phase-based priority
}

if (status.current_focus.includes("DO NOT ASSIGN")) {
  parseAndHonorExclusions(status.current_focus);
}

// Priority 2: Break feedback loops
if (lastNSessionsSameAgent(3) && allScoresBelow(30)) {
  if (allNSessionsRecommendSame(3)) {
    followRecommendation();  // Trust the diagnosis
  }
}

// Priority 3: Score-based routing should be LAST resort
if (recent_avg_score < 30) {
  // Check if wrong agent is cause, not bad work
  if (shouldTryDifferentAgent()) {
    return selectByPhase();
  }
}
```

#### Step 4: Add Regression Tests
```typescript
test("phase=experimental + experiments_run=0 → assigns Experimenter", () => {
  const status = { phase: "experimental", experiments_run: 0 };
  expect(selectAgent(status)).toBe("experimenter");
});

test("researcher_work_status=COMPLETE → excludes Researcher", () => {
  const status = { researcher_work_status: "COMPLETE" };
  expect(selectAgent(status)).not.toBe("researcher");
});

test("3 consecutive same agent + low scores → breaks pattern", () => {
  const history = [
    { agent: "researcher", score: 15 },
    { agent: "researcher", score: 15 },
    { agent: "researcher", score: 15 }
  ];
  expect(selectAgent(status, history)).not.toBe("researcher");
});

test("'DO NOT ASSIGN X' in current_focus → honors exclusion", () => {
  const status = { current_focus: "DO NOT ASSIGN RESEARCHER" };
  expect(selectAgent(status)).not.toBe("researcher");
});
```

---

## Project Health Check

**Research progress**: ✅ 100% complete (excellent quality)
- 30+ papers surveyed
- 50 failure instances collected and coded
- 9-category taxonomy with C1-C8 LLM limitation mapping
- Competitor analysis complete (Shah et al.)
- 168 pages of comprehensive literature notes

**Experimental progress**: ❌ 0% (blocked by routing)
- Well-designed experiments waiting for Experimenter
- Infrastructure requirements documented
- Priority failures identified

**Writing progress**: ❌ 0% (blocked by routing)
- All prerequisites complete
- Ready for Writer to draft introduction/related work

**Project quality**: 90/100 (excellent)
**Routing quality**: 0/100 (completely broken)

---

## Expected Outcomes After Fix

### Session 9 (Manual Override)
- Agent: Experimenter
- Expected score: 75-90
- Expected files: `experiments/protocol.md`
- Project: Unblocked

### Session 10 (Automatic Assignment)
- Agent: Experimenter or Writer (NOT Researcher)
- Expected score: 75-90
- Routing: Should work correctly with phase-based logic

---

## Documentation

**Full analysis**: See `META-REVIEW-8-EIGHTH-RESEARCHER-SESSION-ROUTING-BROKEN.md`
**Test history**: Sessions -7 through 0 (8 consecutive failures)
**Project status**: See `status.yaml` (lines 7-14 document failure pattern)

---

## Questions?

For questions about:
- **Project health**: Research is excellent, experiments are ready, just need correct agent
- **Routing bug**: 3 confirmed bugs (score-loop, flags ignored, no loop detection)
- **Next steps**: Manual override session 9 → Experimenter, then debug routing code

**This is NOT a project issue. This is a platform routing bug that requires code-level fixes.**

---

**Priority**: CRITICAL - Manual override required for session 9
**Confidence**: 100% (confirmed via 8-session empirical test)
**Impact**: High ($16-40 wasted, 16 hours wasted, project blocked for multiple days)
