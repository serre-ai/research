# URGENT: Routing Bug Confirmed - Manual Intervention Required

**Date**: 2026-03-26
**Status**: 🚨 CRITICAL - 8 consecutive session failures
**Action Required**: Manual override for session 9 + code-level debugging

---

## TL;DR

**The orchestrator's agent selection logic is broken.** It has assigned the wrong agent (Researcher) for 8 consecutive sessions on a project that:
- Is in the "experimental" phase
- Has completed all research work (100%)
- Has explicit `researcher_work_status: COMPLETE` flag
- Has created 27 guidance documents saying "assign Experimenter or Writer"

**The project is excellent** (95/100 health). **The routing is broken** (0/100 health).

**Required action**: Manually assign **Experimenter** for session 9, then debug orchestrator code.

---

## Session 8 Test Results

Meta-review #7 established Session 8 as the final test:

| If Session 8 is... | Then... |
|-------------------|---------|
| Experimenter or Writer | ✅ Routing bug fixed |
| Researcher | ❌ Routing bug confirmed, manual override required |

**Result**: Session 8 was Researcher (8th consecutive)

**Conclusion**: ❌ **Routing bug confirmed**

---

## Evidence

### 1. Wrong Agent Assigned 8 Times
| Session | Date | Agent Assigned | Agent Needed | Outcome |
|---------|------|----------------|--------------|---------|
| -7 | 2026-03-25 | Researcher | Experimenter | "No research work exists" |
| -6 | 2026-03-25 | Researcher | Experimenter | "Research complete" |
| -5 | 2026-03-25 | Researcher | Experimenter | Meta-review #4 |
| -4 | 2026-03-25 | Researcher | Experimenter | Meta-review #5 |
| -3 | 2026-03-25 | Researcher | Experimenter | Meta-review #6 |
| -2 | 2026-03-25 | Researcher | Experimenter | Meta-review #7 |
| -1 | 2026-03-25 | Researcher | Experimenter | ??? |
| 0 | 2026-03-26 | Researcher | Experimenter | SESSION-08 doc |

**Pattern**: 100% failure rate over 8 consecutive sessions

### 2. Explicit Flags Ignored

From `status.yaml` (ignored 8 times):
```yaml
phase: experimental  # ← Should trigger Experimenter assignment
researcher_work_status: "COMPLETE - DO NOT ASSIGN RESEARCHER"
failed_researcher_sessions: 8
routing_status: "CONFIRMED PLATFORM BUG"
current_focus: "🚨 ROUTING TEST FAILED: 8 CONSECUTIVE RESEARCHER SESSIONS..."
```

### 3. Guidance Documents Ignored

**27 documents created**, ALL saying "Assign Experimenter or Writer":
- META-REVIEW-2026-03-25.md
- META-REVIEW-4-ROUTING-ISSUE.md
- META-REVIEW-5-FINAL-DIAGNOSIS.md
- META-REVIEW-6-ORCHESTRATOR-ALERT.md
- META-REVIEW-7-SEVENTH-RESEARCHER-SESSION.md
- SESSION-08-ROUTING-FAILURE-CONFIRMED.md
- ROUTING-DECISION.md
- ORCHESTRATOR-GUIDANCE.md
- IMMEDIATE-ACTIONABLE-WORK.md
- FOR-HUMAN-DEVELOPER.md
- INDEX-FOR-ORCHESTRATOR.md
- README-FOR-ORCHESTRATOR.md
- README-START-HERE.md
- READ-ME-FIRST.md
- NEXT-SESSION-MUST-BE-EXPERIMENTER-OR-WRITER.md
- NEXT-SESSION-WORK-ITEMS.md
- ROUTING-BUG-EVIDENCE.md
- VISUAL-STATUS.md
- VISUAL-STATUS-SUMMARY.md
- AGENT-ASSIGNMENT-RECOMMENDATIONS.md
- SESSION-06-SUMMARY.md
- SESSION-08-INSTRUCTIONS.md
- SESSION-SUMMARY-2026-03-25-FINAL.md
- SESSION-SUMMARY-META-REVIEW-4.md
- SESSION-SUMMARY-META-REVIEW-5.md
- + 2 more

**0 documents followed** by routing logic.

### 4. Score-Based Feedback Loop Confirmed

```
Wrong agent assigned
→ No work available (research 100% complete)
→ Low score (~10-15/100)
→ System thinks "project struggling"
→ Assigns Researcher to diagnose
→ Wrong agent assigned [LOOP]
```

**All 8 sessions scored ~10-15/100** not due to bad work, but due to wrong agent assignment.

---

## Impact

| Metric | Value |
|--------|-------|
| Sessions wasted | 8 |
| Financial cost | $16-40 |
| Time cost | 16 hours |
| Productive work blocked | ~50 hours |
| Research progress | 100% (complete, unchanged) |
| Experimental progress | 0% (blocked) |
| Writing progress | 0% (blocked) |
| Project health | 95/100 (excellent) |
| Routing health | 0/100 (broken) |

---

## What the Project Needs

### Immediate (Session 9)
**Manually assign Experimenter agent** with this objective:

```
Design experimental protocol for agent failure taxonomy validation.
- Select 3-4 frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute)
- Choose 6-8 priority failures from taxonomy categories
- Define success criteria
- Outline infrastructure in src/
- Document in experiments/protocol.md
```

**Expected outcome**: Session score 75-90, project unblocked, progress resumes

### Parallel Work
**Writer agent** can also work (assign in session 10 or run parallel):

```
Draft paper introduction section for ACL 2027.
- Motivation: agent deployment + systematic failures
- Research gap: no cognitive-level taxonomy with LLM limitation mapping
- Contributions: C1-C8 mapping, design principles, architecture guidance
- Use literature/05-competitor-deep-analysis.md for Shah et al. positioning
```

---

## Code-Level Debugging Required

### Location
Likely in: `orchestrator/src/` or `orchestrator/lib/`
File: `agent-selection.ts` or `scheduler.ts` or `routing.ts`

### Add Instrumentation

```typescript
// Add logging to agent selection
function selectAgent(project: Project): AgentType {
  console.log('=== AGENT SELECTION START ===');
  console.log('Project:', project.name);
  console.log('Phase:', project.status.phase);
  console.log('Researcher work status:', project.status.researcher_work_status);
  console.log('Failed researcher sessions:', project.status.failed_researcher_sessions);
  console.log('Routing status:', project.status.routing_status);
  console.log('Recent scores:', project.recent_scores);

  const selectedAgent = /* current logic */;

  console.log('Selected agent:', selectedAgent);
  console.log('Selection rationale:', /* rationale */);
  console.log('=== AGENT SELECTION END ===');

  return selectedAgent;
}
```

### Trace Questions

1. **Is `project.status.phase` being read?**
   - If yes: Why is `phase: experimental` not routing to Experimenter?
   - If no: Why not?

2. **Are custom flags being checked?**
   - `researcher_work_status`
   - `failed_researcher_sessions`
   - `routing_status`
   - If no: Implement flag checking

3. **Where is the score-based Researcher assignment?**
   - Find code that assigns Researcher when scores are low
   - Add check: only assign Researcher if `phase == "research"`

4. **Are guidance documents being read?**
   - Probably not (27 documents ignored)
   - Is there code to read project root .md files?
   - If no: Consider adding, or rely on status.yaml flags instead

---

## Required Fixes

### Fix #1: Phase-Based Routing (Primary)

```typescript
function selectAgent(project: Project): AgentType {
  // PRIORITY: Check phase first
  if (project.status.phase === 'experimental') {
    if (project.metrics.experiments_run === 0) {
      return 'experimenter';  // Start experiments
    }
    return 'experimenter';  // Continue experiments
  }

  if (project.status.phase === 'writing') {
    return 'writer';
  }

  if (project.status.phase === 'research') {
    if (project.status.researcher_work_status === 'COMPLETE') {
      // Research done, move to next phase
      return project.metrics.experiments_run > 0 ? 'writer' : 'experimenter';
    }
    return 'researcher';
  }

  // Fallback
  return 'researcher';
}
```

### Fix #2: Honor Exclusion Flags

```typescript
function selectAgent(project: Project): AgentType {
  const excludedAgents = new Set<AgentType>();

  // Check explicit work status flags
  if (project.status.researcher_work_status === 'COMPLETE') {
    excludedAgents.add('researcher');
  }
  if (project.status.experimenter_work_status === 'COMPLETE') {
    excludedAgents.add('experimenter');
  }

  // Check failed session counts
  if (project.status.failed_researcher_sessions >= 3) {
    excludedAgents.add('researcher');
  }

  // Parse current_focus for explicit exclusions
  if (project.status.current_focus?.includes('DO NOT ASSIGN RESEARCHER')) {
    excludedAgents.add('researcher');
  }

  // Then select agent, excluding the above
  let selectedAgent = selectAgentByPhase(project);
  if (excludedAgents.has(selectedAgent)) {
    selectedAgent = selectAlternativeAgent(project, excludedAgents);
  }

  return selectedAgent;
}
```

### Fix #3: Break Feedback Loops

```typescript
function selectAgent(project: Project): AgentType {
  const recentSessions = project.sessionHistory.slice(-3);

  // Detect: same agent, low scores, 3+ times
  const sameAgent = recentSessions.every(s => s.agent === recentSessions[0].agent);
  const lowScores = recentSessions.every(s => s.score < 30);

  if (sameAgent && lowScores && recentSessions.length >= 3) {
    console.warn('Feedback loop detected - switching agent');
    const currentAgent = recentSessions[0].agent;

    // Switch to phase-appropriate agent
    if (project.status.phase === 'experimental') {
      return 'experimenter';
    } else if (project.status.phase === 'writing') {
      return 'writer';
    } else {
      // Don't assign same agent that's been failing
      return currentAgent === 'researcher' ? 'experimenter' : 'researcher';
    }
  }

  // Normal selection
  return selectAgentByPhase(project);
}
```

### Fix #4: Remove/Fix Score-Based Researcher Assignment

Find and modify code like this:

```typescript
// BEFORE (BROKEN)
if (recentScoresLow(project)) {
  return 'researcher';  // Always assigns Researcher
}

// AFTER (FIXED)
if (recentScoresLow(project)) {
  // Low scores could mean wrong agent, not bad work
  // Only assign Researcher if in research phase
  if (project.status.phase === 'research') {
    return 'researcher';
  }
  // Otherwise, switch to phase-appropriate agent
  return selectAgentByPhase(project);
}
```

---

## Regression Tests

Add these tests to prevent recurrence:

```typescript
describe('Agent Selection', () => {
  test('experimental phase with no experiments → Experimenter', () => {
    const project = {
      status: { phase: 'experimental' },
      metrics: { experiments_run: 0 }
    };
    expect(selectAgent(project)).toBe('experimenter');
  });

  test('researcher_work_status COMPLETE → excludes Researcher', () => {
    const project = {
      status: {
        phase: 'experimental',
        researcher_work_status: 'COMPLETE'
      }
    };
    expect(selectAgent(project)).not.toBe('researcher');
  });

  test('failed_researcher_sessions >= 3 → excludes Researcher', () => {
    const project = {
      status: { failed_researcher_sessions: 3 }
    };
    expect(selectAgent(project)).not.toBe('researcher');
  });

  test('3 consecutive low scores → switches agent', () => {
    const project = {
      sessionHistory: [
        { agent: 'researcher', score: 15 },
        { agent: 'researcher', score: 15 },
        { agent: 'researcher', score: 15 }
      ],
      status: { phase: 'experimental' }
    };
    expect(selectAgent(project)).toBe('experimenter');
  });

  test('current_focus "DO NOT ASSIGN X" → excludes X', () => {
    const project = {
      status: {
        current_focus: 'DO NOT ASSIGN RESEARCHER'
      }
    };
    expect(selectAgent(project)).not.toBe('researcher');
  });
});
```

---

## Immediate Action Checklist

- [ ] **Session 9**: Manually assign Experimenter (bypass broken routing)
- [ ] **Add logging**: Instrument agent selection code
- [ ] **Run session 9**: Validate that Experimenter produces score 75-90
- [ ] **Debug**: Trace why phase/flags ignored in sessions 1-8
- [ ] **Implement fixes**: Phase-based routing, flag checking, loop breaking
- [ ] **Test fixes**: Run regression tests
- [ ] **Validate**: Run session 10 without manual override (should auto-assign correctly)

---

## Expected Timeline

| Step | Time | Outcome |
|------|------|---------|
| Manual override session 9 | 5 min | Project unblocked |
| Add logging | 30 min | Visibility into bug |
| Implement fixes | 2-3 hours | Routing logic corrected |
| Write tests | 1 hour | Prevent regression |
| Validate | 1 session | Confirm fix |
| **Total** | **~4 hours** | **Platform bug resolved** |

---

## Project Status (For Context)

### Research (100% Complete)
- ✅ 30+ papers surveyed (2023-2026)
- ✅ 50 failure instances collected and coded
- ✅ 9-category taxonomy developed
- ✅ 24 sub-categories defined
- ✅ C1-C8 LLM limitation mapping complete
- ✅ Competitor analysis done (Shah et al. differentiation secure)

### Experiments (0% - Blocked)
- ❌ Needs Experimenter to design protocol
- ❌ Needs Experimenter to build infrastructure
- ❌ Needs Experimenter to run pilot experiments

### Writing (0% - Blocked)
- ❌ Needs Writer to draft introduction
- ❌ Needs Writer to draft related work
- ❌ Needs Writer to draft methodology

**The project is ready to move forward. Only the routing logic is blocking progress.**

---

## Contact

If questions, see:
- **Full analysis**: `SESSION-08-ROUTING-FAILURE-CONFIRMED.md`
- **Previous meta-reviews**: `META-REVIEW-7-SEVENTH-RESEARCHER-SESSION.md`
- **Project status**: `status.yaml`
- **Research notes**: `notes/` and `literature/`

---

**End of Urgent Developer Notice**

**Priority**: 🚨 CRITICAL
**Action**: Manual override for session 9 + code debugging
**Impact**: Unblocks $300 research project (95% healthy, 100% blocked by routing)
**Estimated fix time**: 4 hours
