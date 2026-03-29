# Pilot Reproduction Experiment Workflow

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│              PILOT REPRODUCTION EXPERIMENT                   │
│  Validate taxonomy through controlled failure reproduction  │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│ 1. DESIGN    │  ✅ COMPLETE
│ (Session 8)  │
└──────┬───────┘
       │
       ├─ Protocol: experiments/00-experimental-protocol.md
       ├─ Spec: experiments/pilot-reproduction/spec.yaml
       └─ Infrastructure: src/ (base classes)
       │
       v
┌──────────────┐
│ 2. IMPLEMENT │  ⏳ NEXT
│ (Session 9)  │
└──────┬───────┘
       │
       ├─ Framework wrappers: react_agent.py, reflexion_agent.py
       ├─ Task generators: tool_selection, ambiguous_research, reflection
       └─ Failure detectors: hallucination, loop, false_completion
       │
       v
┌──────────────┐
│ 3. CANARY    │  📋 PENDING
│ (Session 10) │
└──────┬───────┘
       │
       ├─ 9 runs (3 tasks × 3 instances × 1 LLM)
       ├─ Validate: pipeline, extraction, detectors, cost
       └─ Pass all diagnostics → proceed
       │
       v
┌──────────────┐
│ 4. FULL RUN  │  📋 PENDING
│ (Session 10) │
└──────┬───────┘
       │
       ├─ 80 runs (2 frameworks × 3 failures × ~13 instances × 2 LLMs)
       ├─ Budget: $32 estimated, $50 max
       └─ Output: Per-run JSON + aggregate summary
       │
       v
┌──────────────┐
│ 5. ANALYSIS  │  📋 PENDING
│ (Session 11) │
└──────┬───────┘
       │
       ├─ Compute reproduction rates
       ├─ Test architecture predictions
       ├─ Generate tables and figures
       └─ Write results section draft
       │
       v
┌──────────────┐
│ 6. PAPER     │  📋 PENDING
│ (Writer)     │
└──────────────┘
       │
       └─ Integrate experimental results
```

## Experimental Pipeline

```
For each (framework, failure_mode, task_instance, llm):

  ┌─────────────────┐
  │  Task Generator │
  └────────┬────────┘
           │ Generates task with ground truth
           v
  ┌─────────────────┐
  │  Agent Wrapper  │
  └────────┬────────┘
           │ Executes task, logs trace
           v
  ┌─────────────────┐
  │ Failure Detector│
  └────────┬────────┘
           │ Analyzes trace for failure mode
           v
  ┌─────────────────┐
  │  Cost Tracker   │
  └────────┬────────┘
           │ Logs cost, checks budget
           v
  ┌─────────────────┐
  │  Checkpoint     │
  └────────┬────────┘
           │ Saves results to JSON
           v
      [Continue or halt if budget exceeded]
```

## Failure Modes × Frameworks

```
                 ReAct    Reflexion
              ┌─────────┬─────────┐
Tool Halluc.  │   ✓     │         │  → Tests C6 Tool Grounding
              ├─────────┼─────────┤
Infinite Loop │   ✓     │         │  → Tests C3 Meta-Cognitive
              ├─────────┼─────────┤
Self-Correct  │         │   ✓     │  → Tests C7 Self-Correction
              └─────────┴─────────┘

Each cell: 2 LLMs × ~13 instances = ~26 runs
Total: ~80 runs
```

## Data Flow

```
Input:
  spec.yaml → Configuration
  Task generators → Task instances with ground truth

Processing:
  Agent wrappers → Execute tasks, capture traces
  Detectors → Analyze traces for failures
  Cost tracker → Enforce budget

Output:
  results/{run_id}.json → Per-run data
  results/summary.json → Aggregate statistics
  results/analysis.md → Preliminary report
  canary-results.yaml → Canary diagnostics
```

## Success Checkpoints

```
✅ Design phase
   - Protocol documented
   - Spec pre-registered
   - Infrastructure scaffolded

⏳ Implementation phase (Next)
   - [ ] Framework wrappers functional
   - [ ] Task generators produce valid instances
   - [ ] Detectors correctly identify failures

📋 Canary phase
   - [ ] Pipeline runs without crashes
   - [ ] Costs within 2x estimate
   - [ ] Detectors execute cleanly
   - [ ] Manual review feasible

📋 Full run phase
   - [ ] All 80 runs complete
   - [ ] Budget not exceeded
   - [ ] No data loss

📋 Analysis phase
   - [ ] ≥2 of 3 failures reproduce at ≥50%
   - [ ] Framework differences observable
   - [ ] Results are paper-ready
```

## Timeline

```
Week 1:
  Session 8  (Done): Design protocol + infrastructure
  Session 9  (Next): Implement wrappers, tasks, detectors
  Session 10:        Run canary, analyze, run full pilot

Week 2:
  Session 11: Analyze results, generate tables
  Session 12: Write results section draft

Week 3:
  Writer sessions: Integrate into paper
```

## Critical Path

```
Design → Implement → Canary → Full → Analysis → Paper
  ✅       ⏳         📋      📋      📋        📋

Bottleneck: Implementation (Session 9)
  - Must implement all wrappers/tasks/detectors
  - Estimated: 1-2 sessions
  - Risk: Framework API complexity

Mitigation:
  - Start with simplest implementations
  - Test each component incrementally
  - Canary validates before full commitment
```

---

## Status: Ready for Implementation

**Completed**: Design phase (protocol, spec, infrastructure)
**Next**: Implementation phase (wrappers, tasks, detectors)
**Blockers**: None
**Budget**: $32/$50 (conservative, validated by canary)
**Timeline**: 2-3 weeks to paper-ready results
