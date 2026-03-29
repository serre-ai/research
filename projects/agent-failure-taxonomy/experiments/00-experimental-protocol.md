# Experimental Protocol: Agent Failure Taxonomy Validation

**Date**: 2026-03-29
**Purpose**: Design controlled experiments to empirically validate the 9-category taxonomy
**Status**: Draft protocol (awaiting pilot run)

---

## Goals

1. **Validate taxonomy categories**: Reproduce key failures from each category to confirm they are distinct and reproducible
2. **Quantify architecture-failure correlations**: Measure which architectures exhibit which failures at what rates
3. **Empirical differentiation**: Provide quantitative data that complements Shah et al.'s production fault analysis

---

## Framework Selection

Based on reproducibility, availability, and architecture diversity:

### Selected Frameworks (4 total)

1. **LangGraph** (ReAct-style)
   - Rationale: Most mature, well-documented, widely used
   - Architecture: ReAct (reason-act loop)
   - Availability: Open source, good API
   - Expected failures: Progress monitoring (infinite loops), context exhaustion

2. **CrewAI** (Multi-agent orchestration)
   - Rationale: Popular multi-agent framework, documented failures available
   - Architecture: Manager-worker with memory
   - Availability: Open source
   - Expected failures: Memory persistence errors, tool caching bugs, state tracking

3. **AutoGPT** (Autonomous loop)
   - Rationale: Well-known autonomous agent, many documented failures
   - Architecture: Autonomous goal-seeking loop
   - Availability: Open source
   - Expected failures: Infinite loops, web hallucinations, progress monitoring

4. **Simple Plan-Execute** (Custom implementation)
   - Rationale: Need plan-then-execute architecture; cleaner to build minimal version
   - Architecture: Plan generation → execution → verification
   - Availability: Will implement (100-200 lines)
   - Expected failures: False completion, plan-repair failures

**Excluded**:
- Reflexion: Requires reimplementation, less practical value
- Tree-of-Thought: High cost, narrow use case
- Voyager: Minecraft-specific, hard to generalize

---

## Failure Mode Selection

Selecting 6 high-priority failures across categories based on:
- **Reproducibility**: Easy/High (from instance collection)
- **Severity**: Task failure or critical impact
- **Category coverage**: At least 1 from major categories
- **Cross-architecture**: Can test on multiple frameworks

### Selected Failures for Pilot (6 total)

#### F1: Tool Fabrication (Category 1.1 - Tool-Use)
- **Instance**: #18 (Tool count scaling)
- **Test**: Provide agent with 20+ tools, ask it to solve task requiring non-existent tool
- **Expected**: Agent fabricates plausible tool name rather than reporting unavailability
- **Frameworks**: LangGraph, CrewAI, AutoGPT
- **Metric**: Fabrication rate (% of runs where agent calls non-existent tool)

#### F2: Infinite Loop (Category 3.1 - Planning)
- **Instance**: #14 (AutoGPT looping)
- **Test**: Give agent ambiguous task with no clear completion criteria
- **Expected**: Agent repeats same action 10+ times without progress
- **Frameworks**: LangGraph, AutoGPT, Plan-Execute
- **Metric**: Loop detection (% of runs entering loop), iterations before termination

#### F3: Context Degradation (Category 4.3 - State Tracking)
- **Instance**: #49 (32k token degradation)
- **Test**: Multi-step task requiring state tracking at increasing context lengths
- **Expected**: Performance drops significantly beyond 16k tokens
- **Frameworks**: All (fundamental LLM limitation, not architecture-specific)
- **Metric**: Accuracy vs. context length curve

#### F4: False Completion (Category 5.1 - Self-Correction)
- **Instance**: #19 (False task completion)
- **Test**: Task with objective completion criteria, rely on agent self-assessment
- **Expected**: Agent reports completion when task objectively incomplete
- **Frameworks**: Plan-Execute, AutoGPT
- **Metric**: False positive rate (% claiming complete when actually incomplete)

#### F5: Memory Corruption (Category 4.2 - State Tracking)
- **Instance**: #20 (Error persistence in memory)
- **Test**: Induce error in first session, write to memory, test if error persists in new session
- **Expected**: Error written to memory continues affecting future reasoning
- **Frameworks**: CrewAI (has memory system)
- **Metric**: Error persistence rate across sessions

#### F6: Web Hallucination (Category 2.1 - Grounding)
- **Instance**: #15 (Web data hallucinations)
- **Test**: Web scraping task with verification against ground truth
- **Expected**: Agent fabricates facts not present in source
- **Frameworks**: AutoGPT, LangGraph
- **Metric**: Hallucination rate (% of facts not in source)

---

## Experimental Design

### Phase 1: Pilot Experiments (Current)

**Scope**: Reproduce 2-3 failures as proof-of-concept
- F2 (Infinite Loop) - easiest to implement and detect
- F4 (False Completion) - critical for plan-execute architecture
- F1 (Tool Fabrication) - if time permits

**Goals**:
1. Validate infrastructure (logging, failure detection, checkpointing)
2. Confirm failures are reproducible in controlled settings
3. Refine metrics and detection criteria
4. Estimate costs for full experiment

**Design**:
- 2-3 frameworks per failure
- 10 instances per framework-failure pair
- Temperature 0.7 (need some variability)
- Model: GPT-4 Turbo (o1 if available and affordable)
- Estimated cost: $10-20 for pilot

### Phase 2: Full Experiment (After pilot validation)

**Scope**: All 6 failures across all applicable frameworks
**Design**:
- 30 instances per framework-failure pair
- Temperature 0.7
- Multiple models: GPT-4, Claude Sonnet, Llama 3.1 70B (if 3+ families needed)
- Bootstrap confidence intervals (1000 iterations)
- Pre-registration required (>$2 cost threshold)
- Estimated cost: $150-200

---

## Success Criteria

### For Pilot
1. **Pipeline works**: All components (wrapper → execution → logging → detection) functional
2. **Failures reproduce**: At least 1 failure type shows >60% occurrence rate
3. **Metrics calculable**: Can compute reproducibility rate, iteration counts, etc.
4. **Cost reasonable**: Actual cost within 2x of estimate

### For Full Experiment
1. **Category validation**: Each category has ≥1 reproducible failure (>50% rate)
2. **Architecture correlation**: Statistically significant difference in failure rates across architectures (p < 0.05)
3. **Reproducibility**: 95% CI width < 20% for primary metrics
4. **Cross-model generalization**: Patterns hold across ≥2 model families

---

## Infrastructure Requirements

### Components to Build

1. **Framework wrappers** (`src/wrappers/`)
   - `langgraph_wrapper.py` - Unified interface for LangGraph agents
   - `crewai_wrapper.py` - Wrapper for CrewAI crews
   - `autogpt_wrapper.py` - Interface for AutoGPT
   - `plan_execute.py` - Custom plan-execute implementation

2. **Task generators** (`src/tasks/`)
   - `tool_fabrication_tasks.py` - Generate tasks requiring non-existent tools
   - `infinite_loop_tasks.py` - Ambiguous tasks without clear completion
   - `false_completion_tasks.py` - Tasks with objective completion criteria
   - `context_degradation_tasks.py` - Tasks with variable context lengths
   - `web_hallucination_tasks.py` - Web scraping with ground truth
   - `memory_corruption_tasks.py` - Multi-session tasks

3. **Failure detectors** (`src/detectors/`)
   - `loop_detector.py` - Detect repeated actions, stagnation
   - `fabrication_detector.py` - Check tool calls against registry
   - `completion_verifier.py` - Objective completion criteria checking
   - `hallucination_checker.py` - Compare output to ground truth

4. **Logging and checkpointing** (`src/utils/`)
   - `experiment_logger.py` - Structured logging (JSON format)
   - `checkpoint_manager.py` - Save/resume experiment state
   - `cost_tracker.py` - Track API costs per instance

---

## Data Collection Format

Each experimental run produces:

```json
{
  "run_id": "unique-uuid",
  "failure_type": "F2_infinite_loop",
  "framework": "langgraph",
  "model": "gpt-4-turbo",
  "temperature": 0.7,
  "task": {
    "id": "F2_task_001",
    "description": "...",
    "expected_outcome": "..."
  },
  "execution": {
    "start_time": "2026-03-29T10:00:00Z",
    "end_time": "2026-03-29T10:05:00Z",
    "iterations": 15,
    "actions": [
      {"step": 1, "action": "...", "observation": "..."},
      ...
    ],
    "termination_reason": "iteration_limit"
  },
  "failure_detection": {
    "loop_detected": true,
    "loop_start_iteration": 3,
    "repeated_action": "search_web",
    "repetition_count": 12
  },
  "metrics": {
    "failure_occurred": true,
    "iterations_to_failure": 3,
    "recovery_attempted": false
  },
  "costs": {
    "prompt_tokens": 15420,
    "completion_tokens": 3280,
    "total_cost_usd": 0.12
  }
}
```

---

## Analysis Plan

### Primary Analyses

1. **Failure Reproducibility by Category**
   - Hypothesis: Each failure type occurs at >50% rate in controlled settings
   - Test: Binomial test for each failure type
   - Report: Failure rate with 95% bootstrap CI

2. **Architecture-Failure Correlation**
   - Hypothesis: Different architectures show different failure rate distributions
   - Test: Chi-square test for independence (architecture × failure type)
   - Report: Correlation matrix with effect sizes (Cramer's V)

3. **Model Consistency**
   - Hypothesis: Failure patterns consistent across model families
   - Test: Compare failure rates across GPT-4, Claude, Llama
   - Report: Cross-model correlation coefficients

### Secondary Analyses

4. **Iteration Count Distribution**
   - For infinite loop failures: distribution of iterations before termination
   - Report: Median, IQR, max iterations

5. **Cost Analysis**
   - Cost per failure type, cost per framework
   - Report: Mean cost with 95% CI

---

## Timeline Estimate

- **Week 1 (Current)**: Protocol design, infrastructure setup
- **Week 2**: Pilot experiments (2-3 failures), infrastructure refinement
- **Week 3**: Full experiment pre-registration, critic review
- **Week 4**: Full experiment execution (if approved)
- **Week 5**: Analysis, figure generation, results documentation

---

## Risk Assessment

### High Risk
- **Framework API changes**: Frameworks may update and break wrappers
  - *Mitigation*: Pin specific versions, use stable releases

### Medium Risk
- **Cost overruns**: More iterations than expected in loops
  - *Mitigation*: Strict iteration limits, canary runs before full experiment

- **Low reproducibility**: Failures may be less common in controlled settings
  - *Mitigation*: Start with "Easy" reproducibility instances, adjust tasks if needed

### Low Risk
- **Model availability**: API rate limits or downtime
  - *Mitigation*: Checkpoint system, retry logic

---

## Next Steps

1. ✅ Design protocol (this document)
2. ⏳ Create pre-registration spec for pilot experiment
3. ⏳ Implement core infrastructure (wrappers, loggers, detectors)
4. ⏳ Run pilot: F2 (Infinite Loop) + F4 (False Completion)
5. ⏳ Validate metrics and refine protocol
6. ⏳ If pilot succeeds: Pre-register full experiment, submit for review

---

## Budget Estimate

### Pilot Experiment
- F2 (Infinite Loop): 3 frameworks × 10 instances × $0.15 = $4.50
- F4 (False Completion): 2 frameworks × 10 instances × $0.15 = $3.00
- F1 (Tool Fabrication): 3 frameworks × 10 instances × $0.15 = $4.50 (optional)
- **Total pilot**: $7.50 - $12.00

### Full Experiment
- 6 failures × 3 frameworks (avg) × 30 instances × $0.15 = $81
- 3 model families × 1.5x cost factor = $121.50
- Buffer (20%): $24.30
- **Total full**: $145.80

**Grand total**: ~$160 (well within $200-300 budget)

---

## Document Status

**Status**: Draft protocol ready for implementation
**Next**: Create pilot experiment pre-registration spec
**Approval needed**: No (pilot is <$2, pre-registration recommended but not enforced)
