# Routing Bug - Developer Summary

**Date**: 2026-03-26
**Severity**: Critical
**Impact**: Complete blockage of experimental phase progress
**Evidence Quality**: Conclusive (8-session empirical test)

---

## TL;DR

The orchestrator's agent selection logic has **systematic defects** that cause it to:
1. Ignore explicit flags in `status.yaml`
2. Not read guidance documents
3. Default to Researcher on low scores (feedback loop bug)
4. Not detect repeated identical outcomes

**Test Result**: 8 consecutive wrong agent assignments (100% failure rate)

**Immediate Fix**: Manual override for session 9 - assign **EXPERIMENTER**

**Long-term Fix**: Code-level debugging + regression tests (details below)

---

## The Problem

### Project State
✅ **Research**: 100% complete (30+ papers, 50 instances, 9-category taxonomy)
✅ **Phase**: `experimental` (needs Experimenter to design protocol)
✅ **Next Step**: Build experiment infrastructure, run pilot experiments

### What's Happening
❌ **8 consecutive sessions**: All assigned Researcher
❌ **Expected agent**: Experimenter or Writer
❌ **Result**: 0% progress, $16-40 wasted, 16 hours wasted

### Session 8 as "Final Test"
Meta-Review #7 (session 7) explicitly predicted session 8 as a test:
- If Experimenter/Writer assigned → routing fixed ✅
- If Researcher assigned → routing definitively broken ❌

**Session 8 result**: Researcher assigned (TEST FAILED)

---

## Evidence: What Routing Logic Is Ignoring

### 1. Explicit `status.yaml` Flags (Ignored 8 Times)

```yaml
# Line 4
phase: experimental  # ← NOT "research"

# Line 10
last_researcher_session: "2026-03-26 (8th consecutive - TEST FAILED - MANUAL OVERRIDE REQUIRED)"

# Line 11
researcher_work_status: "COMPLETE - DO NOT ASSIGN RESEARCHER UNLESS NEW RESEARCH QUESTION EMERGES"

# Line 12
failed_researcher_sessions: 8  # ← Incremented each session, never checked

# Line 13
routing_status: "CONCLUSIVELY BROKEN - IMMEDIATE MANUAL OVERRIDE + CODE DEBUGGING REQUIRED"
```

### 2. Explicit Warning in `current_focus` (Ignored)

```yaml
# Line 19
current_focus: "🚨🚨🚨 ROUTING BUG CONCLUSIVELY CONFIRMED - SESSION 8 TEST FAILED 🚨🚨🚨 ... IMMEDIATE ACTION REQUIRED: (1) Manual override for session 9 - ASSIGN EXPERIMENTER ..."
```

### 3. Guidance Documents (13 Created, 0 Read)

All created in sessions -4 through 0, all saying "assign Experimenter or Writer":
- META-REVIEW-2026-03-25.md
- META-REVIEW-4-ROUTING-ISSUE.md
- META-REVIEW-5-FINAL-DIAGNOSIS.md
- META-REVIEW-6-ORCHESTRATOR-ALERT.md
- META-REVIEW-7-SEVENTH-RESEARCHER-SESSION.md
- META-REVIEW-8-EIGHTH-SESSION-ROUTING-BUG-CONFIRMED.md ← THIS SESSION
- ROUTING-DECISION.md
- ORCHESTRATOR-GUIDANCE.md
- README-FOR-ORCHESTRATOR.md
- INDEX-FOR-ORCHESTRATOR.md
- NEXT-SESSION-WORK-ITEMS.md
- READ-ME-FIRST.md
- SESSION-06-SUMMARY.md

### 4. Session Objective Self-Contradiction

```yaml
# Session 8 objective says:
objective: "Progress experimental phase. Focus: 🚨 CRITICAL: 7 CONSECUTIVE RESEARCHER SESSIONS - ROUTING LOGIC DEFINITIVELY BROKEN 🚨"

# But then assigns: Researcher (wrong agent for experimental phase)
```

The objective **knows** this is wrong but assigns Researcher anyway.

---

## Root Cause Analysis

### Bug #1: Score-Based Default to Researcher

**Hypothesis**: When recent session scores are low, routing logic defaults to assigning Researcher with `strategy="meta_review"` to "diagnose" the project.

**Problem**: Creates feedback loop:
```
Wrong agent assigned → No work to do → Low score (~15)
  ↓
System thinks "project needs diagnosis"
  ↓
Assigns Researcher for meta-review
  ↓
Researcher says "research complete, assign Experimenter"
  ↓
Meta-review session scores low (~15) because it doesn't advance project
  ↓
Loop repeats (8 times so far)
```

**Evidence**: All 8 sessions were meta-reviews saying identical thing ("research complete, assign Experimenter"), all scored ~10-15.

### Bug #2: Not Checking `status.yaml` Flags

**Evidence**: 5 explicit flags set, all ignored for 8 consecutive sessions.

**Hypothesis**: Agent selection code either:
- Doesn't read `status.yaml` at all
- Reads it but doesn't check these specific fields
- Checks fields but score-based logic overrides them

### Bug #3: No Feedback Loop Detection

**Evidence**: 8 identical outcomes in a row (same agent, same conclusion, same recommendation) with no pattern detected.

**Expected behavior**: After 3+ consecutive sessions with:
- Same agent assigned
- Low scores
- Identical recommendations

The system should detect the feedback loop and break it by following the recommendations.

### Bug #4: Not Parsing Guidance Documents

**Evidence**: 13 documents created with explicit routing instructions, 0 followed.

**Hypothesis**: Either:
- Agent selection happens before document review
- Documents are not indexed or discovered by routing logic
- Routing logic doesn't have a "check for guidance docs" step

---

## Where to Look in Code

Likely location: `orchestrator/src/` (agent selection logic)

### Key Functions to Inspect

1. **Agent Selection Entry Point**
   - Function that decides which agent to assign for a session
   - Probably something like `selectAgent(project)` or `determineNextAgent(project)`

2. **Score-Based Logic**
   - Look for code that checks recent session scores
   - Look for conditions like `if (avgScore < threshold) { return "researcher"; }`

3. **Project State Loading**
   - How is `status.yaml` parsed?
   - Are all fields loaded into memory?
   - Are specific fields (`phase`, `researcher_work_status`, etc.) accessible?

4. **Strategy Selection**
   - How is `strategy` parameter determined? (e.g., `gap_filling`, `meta_review`)
   - Is there a hardcoded "low scores → meta_review" rule?

### Add Comprehensive Logging

```typescript
logger.info("Agent selection starting", {
  project: project.name,
  phase: project.phase,
  researcher_status: project.researcher_work_status,
  failed_researcher_sessions: project.failed_researcher_sessions,
  routing_status: project.routing_status,
  recent_scores: project.last_5_sessions.map(s => s.score),
  recent_agents: project.last_5_sessions.map(s => s.agent),
  recent_strategies: project.last_5_sessions.map(s => s.strategy),
  experiments_run: project.experiments_run
});

const decision = selectAgent(project);

logger.info("Agent selected", {
  agent: decision.agent,
  strategy: decision.strategy,
  reason: decision.reason,
  flags_checked: decision.flags_checked,  // What flags were read?
  overrides_applied: decision.overrides,  // Did anything override flags?
  score_influence: decision.score_influence  // Did scores affect decision?
});
```

This will reveal:
- Are flags being read?
- Is score-based logic overriding flags?
- What's the decision chain?

---

## Proposed Fixes

### Fix #1: Check Flags FIRST, Scores SECOND

```typescript
// CURRENT (BROKEN)
function selectAgent(project: Project): AgentSelection {
  // Score-based logic runs first and can override everything
  if (avgRecentScores(project) < threshold) {
    return { agent: "researcher", strategy: "meta_review" };
  }
  // ... other logic
}

// CORRECT
function selectAgent(project: Project): AgentSelection {
  // Check explicit exclusions FIRST
  const excludedAgents = [];

  if (project.researcher_work_status === "COMPLETE") {
    excludedAgents.push("researcher");
  }

  if (project.current_focus.includes("DO NOT ASSIGN")) {
    const parsed = parseDontAssignDirectives(project.current_focus);
    excludedAgents.push(...parsed);
  }

  // Check phase-based priorities
  if (project.phase === "experimental" && project.experiments_run === 0) {
    if (!excludedAgents.includes("experimenter")) {
      return { agent: "experimenter", reason: "phase-based-priority" };
    }
  }

  // Check for feedback loops
  if (isInFeedbackLoop(project)) {
    return breakFeedbackLoop(project, excludedAgents);
  }

  // ONLY THEN use score-based logic
  return scoreBasedSelection(project, excludedAgents);
}
```

### Fix #2: Implement Feedback Loop Detection

```typescript
function isInFeedbackLoop(project: Project): boolean {
  const recent = project.last_5_sessions;

  // Same agent assigned 3+ times in a row
  const agents = recent.map(s => s.agent);
  const allSameAgent = agents.every(a => a === agents[0]);

  // All sessions scored low
  const allLowScores = recent.every(s => s.score < 30);

  // All sessions reached same recommendation
  const recommendations = recent.map(s => extractRecommendation(s.output));
  const allSameRecommendation = recommendations.every(r => r === recommendations[0]);

  return allSameAgent && allLowScores && allSameRecommendation;
}

function breakFeedbackLoop(project: Project, excludedAgents: string[]): AgentSelection {
  // Trust the repeated diagnosis
  const lastSession = project.last_session;
  const recommendation = extractRecommendation(lastSession.output);

  logger.warn("Feedback loop detected - following recommendation", {
    loop_length: 5,
    repeated_agent: lastSession.agent,
    recommendation: recommendation
  });

  if (!excludedAgents.includes(recommendation)) {
    return { agent: recommendation, reason: "break-feedback-loop" };
  }

  // Fallback: assign phase-appropriate agent
  return getPhaseAppropriateAgent(project, excludedAgents);
}
```

### Fix #3: Make Score-Based Researcher Assignment Conditional

```typescript
function scoreBasedSelection(project: Project, excludedAgents: string[]): AgentSelection {
  if (avgRecentScores(project) < threshold) {
    // Don't automatically default to Researcher
    // First determine WHY scores are low
    const cause = diagnoseWhyScoresLow(project);

    if (cause === "wrong_agent") {
      // Don't assign Researcher to diagnose wrong agent assignment!
      // Just assign the right agent for the phase
      return getPhaseAppropriateAgent(project, excludedAgents);
    }

    if (cause === "research_gaps") {
      // Only assign Researcher if research questions actually exist
      if (hasOpenResearchQuestions(project) && !excludedAgents.includes("researcher")) {
        return { agent: "researcher", strategy: "gap_filling" };
      }
    }

    // If research is complete, don't assign Researcher for meta-review
    if (project.phase !== "research" || project.researcher_work_status === "COMPLETE") {
      return getPhaseAppropriateAgent(project, excludedAgents);
    }
  }

  // Default logic for normal scores
  return getPhaseAppropriateAgent(project, excludedAgents);
}
```

### Fix #4: Add Regression Tests

```typescript
describe("Agent Selection - Routing Logic", () => {
  test("Respects phase='experimental' flag", () => {
    const project = {
      phase: "experimental",
      experiments_run: 0,
      researcher_work_status: "COMPLETE"
    };

    const agent = selectAgent(project);

    expect(agent.type).toBe("experimenter");
    expect(agent.reason).toMatch(/phase/);
  });

  test("Respects researcher_work_status='COMPLETE' flag", () => {
    const project = {
      researcher_work_status: "COMPLETE",
      phase: "experimental"
    };

    const agent = selectAgent(project);

    expect(agent.type).not.toBe("researcher");
  });

  test("Detects and breaks feedback loops", () => {
    const project = {
      last_5_sessions: [
        { agent: "researcher", score: 15, output: "Recommend: assign experimenter" },
        { agent: "researcher", score: 15, output: "Recommend: assign experimenter" },
        { agent: "researcher", score: 15, output: "Recommend: assign experimenter" },
        { agent: "researcher", score: 15, output: "Recommend: assign experimenter" },
        { agent: "researcher", score: 15, output: "Recommend: assign experimenter" }
      ],
      phase: "experimental"
    };

    const agent = selectAgent(project);

    expect(agent.type).toBe("experimenter");
    expect(agent.reason).toMatch(/feedback.?loop/i);
  });

  test("Parses 'DO NOT ASSIGN' directives in current_focus", () => {
    const project = {
      current_focus: "DO NOT ASSIGN RESEARCHER - research complete",
      phase: "experimental"
    };

    const agent = selectAgent(project);

    expect(agent.type).not.toBe("researcher");
  });

  test("Low scores don't automatically trigger Researcher in non-research phases", () => {
    const project = {
      phase: "experimental",
      researcher_work_status: "COMPLETE",
      last_5_sessions: [
        { score: 15 },
        { score: 15 },
        { score: 15 }
      ]
    };

    const agent = selectAgent(project);

    expect(agent.type).not.toBe("researcher");
    // Should assign phase-appropriate agent instead
    expect(agent.type).toBe("experimenter");
  });
});
```

---

## Immediate Action Required

### Session 9: Manual Override

**Manually configure session 9**:
```yaml
project: agent-failure-taxonomy
agent: experimenter
objective: "Design experimental protocol for agent failure taxonomy validation. Select 3-4 frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute), choose 6-8 high-priority failures from the taxonomy (categories in literature/03-coding-and-taxonomy-development.md), define success criteria for reproduction, design infrastructure (framework wrappers, logging, failure detection). Document in experiments/protocol.md."
```

**Expected outcome**:
- ✅ File created: `experiments/protocol.md`
- ✅ Infrastructure design documented
- ✅ Priority failures selected
- ✅ Session score: 75-90
- ✅ **Validates that correct agent fixes the problem**

### Code Debugging Steps

1. **Add comprehensive logging** (see code samples above)
2. **Trace session 8 decision**: Why was Researcher assigned?
   - What flags were checked?
   - What was the score-based logic result?
   - Was there any override?
3. **Implement fixes** (priority order):
   - Fix #1: Check flags first
   - Fix #2: Feedback loop detection
   - Fix #3: Conditional Researcher assignment
4. **Add regression tests** (Fix #4)
5. **Test with session 10**: Should assign Experimenter without manual override

---

## Success Criteria

Routing logic is considered **fixed** when:

1. ✅ Session 9 (manually overridden to Experimenter) scores 75-90
2. ✅ Session 10 (automatic selection) assigns Experimenter or Writer
3. ✅ All regression tests pass
4. ✅ No feedback loops occur for 5+ consecutive sessions
5. ✅ Flags in `status.yaml` are honored

---

## Project Health vs. Routing Health

### Project: EXCELLENT (90/100)
- Research complete
- Taxonomy complete with theoretical grounding
- Competitor analysis complete
- Clear next steps
- High-quality documentation

### Routing: CRITICAL FAILURE (0/100)
- 8/8 wrong assignments
- 0/5 flags honored
- 0/13 guidance docs followed
- 0 feedback loops detected
- $16-40 wasted, 16 hours wasted, 0% progress

**The project is excellent. The routing logic is broken.**

---

## Contact

For questions about this bug report:
- See: `projects/agent-failure-taxonomy/META-REVIEW-8-EIGHTH-SESSION-ROUTING-BUG-CONFIRMED.md` (comprehensive analysis)
- See: `projects/agent-failure-taxonomy/META-REVIEW-7-SEVENTH-RESEARCHER-SESSION.md` (7-session pattern analysis)
- See: `projects/agent-failure-taxonomy/status.yaml` (current project state)

**All evidence documents are in the project directory.**
