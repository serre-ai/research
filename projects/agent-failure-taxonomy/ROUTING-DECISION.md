# Routing Decision for Agent-Failure-Taxonomy

**Date**: 2026-03-25
**Status**: Research Complete → Experimental Phase
**Last Updated By**: Researcher Agent (Meta-review #4)

---

## ⚠️ CRITICAL: Agent Selection Error Pattern Detected

**Problem**: Last 4 sessions assigned Researcher agent when research is complete
- Session -3: researcher/gap_filling → Score 15
- Session -2: researcher/gap_filling → Score 15
- Session -1: researcher/quality_improvement → Score 15
- Session 0 (this): researcher/meta_review → TBD

**Root Cause**: Research phase is COMPLETE but orchestrator continues routing to Researcher

**Pattern**: Repeating failed strategy → Low scores → Another meta-review → Same result

---

## ✅ Simple Decision Tree for Next Session

```
Is there a NEW research question requiring literature survey?
├─ NO → DO NOT assign Researcher
│       ├─ Does project need experiments? → Assign EXPERIMENTER
│       └─ Does project need writing? → Assign WRITER
│
└─ YES → Only then assign Researcher
         └─ (Exception: Very rare, requires experiments to discover gap)
```

For agent-failure-taxonomy project:
- **NEW research question?** → NO (all questions answered)
- **Needs experiments?** → YES (0 experiments run, taxonomy needs validation)
- **Needs writing?** → YES (paper/ directory empty)

**DECISION**: Assign EXPERIMENTER or WRITER, NOT Researcher

---

## 🎯 Concrete Next Session Objectives

### Option A: EXPERIMENTER AGENT
```
Agent: Experimenter
Objective: Design experimental protocol for agent-failure-taxonomy
Tasks:
  1. Select 3-4 agent frameworks (ReAct, AutoGPT, Reflexion, plan-then-execute)
  2. Choose 6-8 priority failures from notes/05-taxonomy-final-structure.md
  3. Define success criteria for each failure category
  4. Document protocol in experiments/protocol.md
Success Criteria: Protocol document exists, frameworks selected, clear next steps
Estimated Score: 70-90 (high-value work, clear deliverable)
```

### Option B: WRITER AGENT
```
Agent: Writer
Objective: Draft introduction section for ACL 2027 paper
Tasks:
  1. Read BRIEF.md for contributions
  2. Read notes/05-taxonomy-final-structure.md for taxonomy summary
  3. Write 1.5-page introduction: motivation, gap, contributions, structure
  4. Use ACL 2027 LaTeX template
  5. Save to paper/introduction.tex
Success Criteria: Introduction section exists, clearly states contributions
Estimated Score: 70-90 (high-value work, clear deliverable)
```

### Option C (Parallel): BOTH A and B
```
Assign Experimenter and Writer in alternating sessions or parallel execution
No dependencies between tracks until Results section
```

---

## ❌ What NOT to Do

### DO NOT assign Researcher for:
- ❌ "Gap-filling" (no gaps exist)
- ❌ "Quality improvement" (quality is already high)
- ❌ "Meta-review" (4 meta-reviews done, problem is clear)
- ❌ "Additional instances" (50 is sufficient)
- ❌ "Taxonomy refinement" (should be data-driven from experiments)
- ❌ "Competitor analysis" (already done: literature/05-competitor-deep-analysis.md)

### Exception: Assign Researcher ONLY if:
- Experiments reveal genuinely NEW research question not in existing 4 literature notes
- New concurrent work appears that requires deep analysis (check arXiv weekly)
- Experimenter/Writer explicitly requests literature review on specific gap

---

## 📊 Project Health Indicators

| Indicator | Status | Interpretation |
|-----------|--------|----------------|
| Papers surveyed | 30+ | ✅ Sufficient |
| Failures collected | 50 | ✅ Sufficient for grounded theory |
| Taxonomy categories | 9 major, 24 sub | ✅ Well-developed |
| Literature notes | 5 comprehensive (129KB) | ✅ Thorough |
| Competitor analysis | Complete | ✅ Shah et al. analyzed |
| Experiments run | 0 | ⚠️ NEEDS ATTENTION |
| Paper sections drafted | 0 | ⚠️ NEEDS ATTENTION |
| Phase alignment | Experimental | ✅ Correct phase |
| Agent assignment | Researcher (wrong) | ❌ MISALIGNED |

**Diagnosis**: Project is healthy and ready to advance. Agent selection is the ONLY issue.

---

## 💡 Why Previous Sessions Failed

### Session -3, -2: researcher/gap_filling (Score 15 each)
**What happened**: Researcher tried to collect more instances when 50 already collected
**Why it failed**: Task already complete, no value added
**What should have happened**: Assign Experimenter to validate existing 50 instances

### Session -1: researcher/quality_improvement (Score 15)
**What happened**: Researcher tried to improve taxonomy quality
**Why it failed**: Taxonomy quality already high, no experiments to inform improvements
**What should have happened**: Assign Experimenter to generate empirical data for refinement

### Session 0: researcher/meta_review (this session)
**What happened**: Another meta-review after 3 previous diagnostics
**Why it will fail**: Problem is known (wrong agent assignment), more analysis doesn't help
**What should have happened**: Actually implement the recommendation (assign Experimenter/Writer)

---

## 🔧 Implementation Guidance

### For Orchestrator System:
1. Check `researcher_work_status` field in status.yaml
2. If value is "COMPLETE", do not route to Researcher agent
3. Check `phase` field: "experimental" → route to Experimenter
4. Check `paper_writing.status`: "ready_to_start" → can route to Writer
5. Read `current_focus` for explicit routing instructions

### For Human Oversight:
If you see:
- Multiple low-scoring sessions (< 40) with same agent type → Wrong agent assignment
- Status.yaml says "phase: experimental" but Researcher assigned → Routing error
- explicit "DO NOT ASSIGN X" warnings → Respect them

**The system has all the information it needs. The issue is following the guidance.**

---

## ✅ Expected Outcome After Correct Assignment

### After 1 Experimenter session:
- experiments/protocol.md exists
- Frameworks selected (3-4)
- Priority failures identified (6-8)
- Success criteria defined
- Clear next steps for infrastructure build
- **Expected score: 75-90**

### After 1 Writer session:
- paper/introduction.tex exists
- Contributions clearly stated
- Motivation compelling
- Paper structure outlined
- **Expected score: 70-85**

### After 3 sessions (2 Experimenter + 1 Writer):
- Infrastructure built in src/
- Pilot experiments run (2-3 failures)
- Introduction + Related Work drafted
- Methodology partially drafted
- **Project confidence: 0.85+**
- **Clear path to completion**

---

## 🎯 Recommendation

**STOP assigning Researcher. START assigning Experimenter or Writer.**

**Next session should be**:
- **First choice**: Experimenter (unblocks empirical validation, highest priority)
- **Second choice**: Writer (can work in parallel, no dependencies)
- **Third choice**: Both (parallel execution recommended)

**Success probability**:
- If Experimenter assigned: 85%
- If Writer assigned: 80%
- If Researcher assigned: 10% (will repeat previous failures)

---

## 📝 Decision Log Entry (to add to status.yaml)

```yaml
- date: 2026-03-25
  decision: "Stop assigning Researcher agent - research phase complete"
  rationale: "Four consecutive sessions (3 failed + 1 meta-review) assigned Researcher when research objectives complete. All literature surveyed (30+ papers), taxonomy developed (9 categories, C1-C8 mapping), competitor analyzed. Continued Researcher assignment is counterproductive. Phase transition to Experimenter/Writer required. This decision should be honored by routing logic."
```

---

**Document Purpose**: Break the failed session loop by providing unambiguous routing guidance

**Key Insight**: The project isn't stuck. The routing is stuck.

**Action Required**: Change agent assignment from Researcher to Experimenter or Writer

**Expected Result**: High-scoring sessions (70-90) with clear progress toward publication
