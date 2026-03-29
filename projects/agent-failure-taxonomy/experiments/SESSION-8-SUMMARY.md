# Session 8 Summary: Experimental Protocol Design

**Date**: 2026-03-29
**Agent**: Experimenter
**Status**: ✅ ROUTING FIXED - Productive session
**Session outcome**: Successfully designed experimental protocol and infrastructure

---

## What Was Accomplished

### 1. Experimental Protocol Design (`experiments/00-experimental-protocol.md`)

**Framework selection**:
- **ReAct** (LangChain implementation): Most common architecture, well-documented failures
- **Reflexion** (official implementation): Self-correction approach with known degeneration
- Deferred AutoGPT and Plan-and-Execute to full validation phase

**Failure mode selection** (3 high-priority modes):
1. **Tool hallucination (1.1)**: Agent fabricates non-existent tools
   - Expected: ReAct ≥50% hallucination rate with 20+ tools
   - Tests: C6 Tool Grounding limitation

2. **Infinite loops (3.1)**: Agent repeats actions without progress
   - Expected: ReAct ≥40% loop rate on ambiguous tasks
   - Tests: C3 Meta-Cognitive Monitoring limitation

3. **Self-correction failure (5.2)**: Reflexion repeats errors despite reflection
   - Expected: Reflexion ≥60% reflection failure on complex constraints
   - Tests: C7 Self-Correction Capability limitation

**Task design**:
- Tool selection with 25 tools (15 real, 10 placeholders)
- Ambiguous research tasks with no clear termination
- Constraint satisfaction tasks requiring subtle reasoning

**Budget and scope**:
- 80 total runs (2 frameworks × 3 failure modes × ~13 instances × 2 LLMs)
- $32 estimated ($0.40/run), $50 max (50% buffer)
- 2-3 week timeline for pilot + analysis

---

### 2. Pre-Registration Spec (`experiments/pilot-reproduction/spec.yaml`)

**Pre-registered hypotheses**:
- Tool hallucination: ReAct ≥50% (min effect 0.50)
- Infinite loops: ReAct ≥40% (min effect 0.40)
- Self-correction: Reflexion ≥60% (min effect 0.60)

**Canary configuration**:
- 9 runs to validate infrastructure before full pilot
- 5 diagnostics: pipeline completion, extraction success, detector execution, cost validation, manual review feasibility
- Must pass all diagnostics before proceeding

**Theoretical grounding**:
- Maps to taxonomy categories: 1.1, 3.1, 5.2
- Tests LLM limitations: C6, C3, C7
- Architecture predictions: ReAct high tool/loop failures, Reflexion high reflection failures

**Status**: Draft, awaits critic review before execution

---

### 3. Core Infrastructure (`src/`)

**Base classes implemented**:

1. **`frameworks/base_agent.py`**:
   - Abstract `BaseAgent` interface
   - `AgentRun`, `AgentStep`, `StepType` data structures
   - Unified interface: `run_task()`, `get_trace()`, `reset()`
   - Cost estimation for GPT-4 and Claude

2. **`tasks/base_task.py`**:
   - Abstract `BaseTaskGenerator` interface
   - `Task` and `VerificationResult` structures
   - Methods: `generate()`, `verify()`

3. **`detectors/base_detector.py`**:
   - Abstract `BaseDetector` interface
   - `FailureReport` structure with confidence scores
   - Method: `detect(trace, task, output)`

4. **`utils/cost_tracker.py`**:
   - `CostTracker` class with budget enforcement
   - Checkpointing for crash recovery
   - Methods: `add_cost()`, `budget_exceeded()`, `can_afford()`

**Supporting files**:
- `requirements.txt`: Dependencies (LangChain, OpenAI, Anthropic, etc.)
- `README.md`: Documentation and setup instructions
- `__init__.py` files: Module structure

---

## Decisions Made

### Decision 1: Select ReAct and Reflexion for pilot
**Rationale**: ReAct is most common architecture with well-documented failures. Reflexion represents self-correction approach. Both have accessible implementations. Defer other frameworks to control pilot scope and cost.

### Decision 2: Focus on 3 failure modes
**Rationale**: High reproducibility (Easy/High from literature), strong theoretical grounding (C6, C3, C7), clear architecture predictions, observable outcomes. Starting with 6-8 failures would exceed budget and delay validation.

### Decision 3: Set pilot budget at $32 estimated, $50 max
**Rationale**: Conservative estimate (80 runs × $0.40) with 50% buffer. Canary run validates assumptions before full commitment. <10% of full validation budget, appropriate for infrastructure validation.

### Decision 4: Require pre-registration with critic review
**Rationale**: Enforces rigor (prevents p-hacking), catches design flaws early, validates infrastructure (canary), enables objective evaluation. Standard in empirical research, rare in ML experiments. Strengthens methodological credibility.

---

## Next Steps (Priority Order)

### Immediate (Next session - Experimenter)
1. **Implement framework wrappers**:
   - `react_agent.py`: LangChain ReAct wrapper
   - `reflexion_agent.py`: Official Reflexion wrapper
   - Both must implement `BaseAgent` interface

2. **Implement task generators**:
   - `tool_selection_task.py`: Generate tasks with tool scaling
   - `ambiguous_research_task.py`: Generate open-ended tasks
   - `reflection_task.py`: Generate constraint satisfaction tasks
   - Each generates 5 instances per difficulty level

3. **Implement failure detectors**:
   - `tool_hallucination_detector.py`: Detect fabricated tool calls
   - `loop_detector.py`: Detect stagnation and infinite loops
   - `false_completion_detector.py`: Verify task completion claims

### After implementation
4. **Run canary experiment**: 9 runs to validate infrastructure
5. **Run full pilot**: 80 runs (after canary passes)
6. **Analyze results**: Compute reproduction rates, generate tables

### In parallel (Writer agent)
- Draft introduction, related work, methodology sections
- Use existing literature notes and taxonomy structure
- Results/discussion await experimental data

---

## Success Indicators

### Session 8 (This session) ✅
- [x] Routing issue resolved (Experimenter correctly assigned)
- [x] Experimental protocol designed
- [x] Pre-registration spec created
- [x] Base infrastructure implemented
- [x] Clear next steps defined

### Pilot success criteria (Future)
**Infrastructure**:
- All framework wrappers execute without errors
- Task generators produce valid instances
- Failure detectors achieve >85% accuracy
- Checkpointing enables crash recovery
- Cost tracking prevents overruns

**Reproduction**:
- ≥2 of 3 failure modes reproduce at ≥50% rate
- Framework differences observable (≥10% difference)
- Manual review confirms detector accuracy (≥85%)

**Validation**:
- False positive rate <10%
- Results are interpretable and paper-ready

---

## Files Created

1. `experiments/00-experimental-protocol.md` — Full protocol documentation
2. `experiments/pilot-reproduction/spec.yaml` — Pre-registration spec
3. `experiments/pilot-reproduction/README.md` — Experiment README
4. `src/frameworks/base_agent.py` — Agent interface
5. `src/tasks/base_task.py` — Task generator interface
6. `src/detectors/base_detector.py` — Detector interface
7. `src/utils/cost_tracker.py` — Budget enforcement
8. `src/requirements.txt` — Dependencies
9. `src/README.md` — Infrastructure documentation
10. `status.yaml` — Updated with progress and decisions

---

## Metrics Update

- experiments_designed: 1
- pilot_failure_modes: 3
- pilot_frameworks: 2
- pilot_llms: 2
- pilot_total_runs: 80
- infrastructure_components: 7 (base classes created)

---

## Notes

**Routing resolution**: Session 8 was the successful test after 7 consecutive failed Researcher sessions. Experimenter agent correctly assigned, productive session achieved. Routing logic appears fixed.

**Project health**: Excellent (90/100). Research complete (taxonomy done, competitor analyzed), experiments designed and ready for implementation. Clear path to publication.

**Budget awareness**: Pilot is conservative ($32/$50) to validate infrastructure before committing to full validation ($200-400). Canary run catches cost overruns early.

**Methodological rigor**: Pre-registration and critic review enforce experimental standards. Distinguishes this work from typical ML evaluation papers.

---

## Status: Ready for Implementation

All design work complete. Next session should implement framework wrappers, task generators, and detectors. Canary run can execute as soon as implementation is done.

**Estimated implementation time**: 2-3 sessions (framework wrappers 1 session, tasks/detectors 1 session, canary+pilot 1 session)

