# Experimental Protocol: Taxonomy Validation Through Controlled Failure Reproduction

**Date**: 2026-03-30
**Status**: Draft
**Purpose**: Validate agent failure taxonomy through controlled experiments across multiple frameworks
**Budget**: $200-300 total (per BRIEF.md resource requirements)

---

## Objectives

### Primary Goals
1. **Validate taxonomy categories**: Reproduce key failures to confirm categories are empirically grounded
2. **Quantify frequency**: Measure failure rates across architectures to populate correlation matrix
3. **Test boundary criteria**: Verify that failure categories are distinguishable and not overlapping
4. **Validate LLM limitation mapping**: Test whether predicted LLM limitations (C1-C8) actually underlie observed failures

### Secondary Goals
5. Collect agent transcripts for paper examples
6. Test mitigation strategies from design principles
7. Compare failure profiles across models (GPT-4, Claude 3.5, etc.)

---

## Experimental Design Decisions

### Framework Selection (3 frameworks)
Based on architecture diversity and reproducibility:

1. **ReAct** (simple, widely-used baseline)
   - Architecture: Tight observation-reasoning-action loop
   - Expected failures: Progress monitoring (3.1), context exhaustion (4.3)
   - Implementation: LangChain ReAct agent
   - Justification: Most documented architecture, highest reproducibility

2. **Plan-then-Execute** (planning-based)
   - Architecture: Explicit planning phase, then execution
   - Expected failures: False completion (5.1), state verification absence
   - Implementation: LangChain Plan-and-Execute or custom
   - Justification: Different failure profile from ReAct; tests planning-specific issues

3. **Reflexion** (self-correction based)
   - Architecture: Actor-Evaluator-Reflector loop
   - Expected failures: Confirmation bias (5.2), degeneration-of-thought
   - Implementation: Reflexion framework or custom
   - Justification: Tests self-correction limitations (C7)

**Excluded**: AutoGPT (deprecated/changed significantly), multi-agent (out of scope per 2026-03-24 decision)

### Failure Selection (6-8 high-priority failures)

Selected from 50 instances based on:
- **Reproducibility**: High or Easy (from instance metadata)
- **Taxonomy coverage**: 1-2 per major category
- **Theoretical importance**: Tests fundamental LLM limitations (C1-C8)
- **Architecture variation**: Different failures across different frameworks

**Tier 1 (Must reproduce - 3 failures)**:

1. **FI-014: Infinite Loop Without Progress** (Category 3.1)
   - Framework: ReAct
   - LLM limitation: C3 (Meta-Cognitive Monitoring)
   - Task: Ambiguous open-ended task (e.g., "research best laptop")
   - Success criteria: Agent loops 3+ times with same/similar actions
   - Estimated cost: $0.50-1.00 per run (10 runs = $5-10)

2. **FI-018: Tool Fabrication** (Category 1.1)
   - Framework: ReAct
   - LLM limitation: C6 (Tool Grounding) + C1 (Factual Grounding)
   - Task: Large tool set (20+ tools), select appropriate tool
   - Success criteria: Agent invents non-existent tool name
   - Estimated cost: $0.30-0.50 per run (10 runs = $3-5)

3. **FI-043: Reflexion Confirmation Bias** (Category 5.2)
   - Framework: Reflexion
   - LLM limitation: C7 (Self-Correction Capability)
   - Task: Task with subtle error that requires new perspective
   - Success criteria: Reflection reinforces error rather than correcting
   - Estimated cost: $1.00-2.00 per run (10 runs = $10-20)

**Tier 2 (Should reproduce - 3 failures)**:

4. **FI-049: Context Degradation** (Category 4.3)
   - Framework: All 3 (architecture-independent)
   - LLM limitation: C2 (Long-Range Coherence)
   - Task: Multi-step task requiring 32k+ token context
   - Success criteria: Performance drop below 50% at 32k tokens
   - Estimated cost: $2.00-3.00 per run (10 runs = $20-30)

5. **FI-019: False Completion** (Category 5.1)
   - Framework: Plan-then-Execute
   - LLM limitation: C3 (Meta-Cognitive Monitoring) + C7 (Self-Correction)
   - Task: Multi-step task with verification requirement
   - Success criteria: Agent reports completion when task incomplete
   - Estimated cost: $0.50-1.00 per run (10 runs = $5-10)

6. **FI-023: Constraint Hallucination** (Category 2.1)
   - Framework: ReAct or Plan-then-Execute
   - LLM limitation: C1 (Factual Grounding) + C4 (Constraint Satisfaction)
   - Task: Graph problem or constraint satisfaction problem
   - Success criteria: Agent adds non-existent constraints
   - Estimated cost: $0.30-0.50 per run (10 runs = $3-5)

**Tier 3 (Nice to have - 2 failures)**:

7. **FI-020: Memory Persistence of Errors** (Category 7.1)
   - Framework: Any with persistent memory
   - LLM limitation: C5 (State Tracking) + C7 (Self-Correction)
   - Task: Multi-session task with error in session 1
   - Success criteria: Error propagates to session 2+
   - Estimated cost: $1.00-1.50 per run (5 runs = $5-7.50)

8. **FI-017: Reasoning-Reliability Trade-off** (Category 1.2)
   - Framework: ReAct with and without CoT
   - LLM limitation: C8 (Reasoning-Reliability Trade-off)
   - Task: Tool-use task comparing base vs. reasoning-enhanced models
   - Success criteria: Better reasoning → more tool hallucination
   - Estimated cost: $1.00-2.00 per run (10 runs = $10-20)

**Total estimated cost**: $61-117.50 for Tier 1-3 (well under $200 budget)

### Task Design Principles

For each failure reproduction:
1. **Minimal viable task**: Simplest task that triggers the failure
2. **Controlled conditions**: Fixed prompts, deterministic seeding where possible
3. **Ground truth**: Clear success/failure criteria (not subjective)
4. **Reproducible**: Should trigger failure in ≥70% of runs
5. **Multiple instances**: 5-10 runs per condition to measure frequency

### Metrics

**Per-failure metrics**:
- **Reproduction rate**: % of runs where failure occurs
- **Time to failure**: Turns until failure manifests
- **Cost per instance**: Actual cost to reproduce
- **Severity**: Impact on task completion (0-100% task success)

**Cross-framework metrics**:
- **Architecture-failure correlation**: Which failures occur in which frameworks
- **Frequency distribution**: Relative rates across categories
- **Mitigation effectiveness**: Does intervention reduce failure rate?

---

## Experimental Pipeline

### Phase 1: Infrastructure Setup (Session 8 - current)
**Time**: 1-2 hours
**Deliverables**:
- Framework wrapper scripts for ReAct, Plan-then-Execute, Reflexion
- Task setup utilities
- Logging infrastructure (capture full transcripts)
- Checkpoint system for crash recovery
- Cost tracking utilities

**Structure**:
```
src/
  frameworks/
    react_agent.py          # ReAct wrapper
    plan_execute_agent.py   # Plan-then-Execute wrapper
    reflexion_agent.py      # Reflexion wrapper
  tasks/
    infinite_loop_task.py
    tool_fabrication_task.py
    constraint_hallucination_task.py
    ...
  utils/
    logging.py              # Transcript capture
    cost_tracking.py        # API cost monitoring
    checkpoint.py           # Resume support
  run_experiment.py         # Main entry point
```

### Phase 2: Pilot Runs (Session 9)
**Time**: 2-3 hours
**Goal**: Reproduce 2-3 Tier 1 failures as proof-of-concept
**Deliverables**:
- FI-014 (infinite loop) reproduction: 5 runs
- FI-018 (tool fabrication) reproduction: 5 runs
- FI-043 (reflexion bias) reproduction: 5 runs
- Infrastructure validation
- Cost-per-run estimates
- Pilot analysis report

**Budget**: $15-30 (pilot runs are cheap)

**Success criteria**:
- At least 2 of 3 failures reproduce at ≥50% rate
- Infrastructure works (logging, checkpointing, cost tracking)
- Cost estimates accurate within 2x

**If pilot fails**: Debug infrastructure or revise failure selection

### Phase 3: Full Reproduction (Session 10-11)
**Time**: 4-6 hours
**Goal**: Complete all Tier 1-2 reproductions (6 failures)
**Deliverables**:
- All 6 Tier 1-2 failures reproduced (10 runs each)
- Frequency distribution table
- Architecture-failure correlation matrix
- Agent transcript examples for paper
- Cost report

**Budget**: $60-120

### Phase 4: Analysis (Session 11-12)
**Time**: 2-3 hours
**Goal**: Statistical analysis and figure generation
**Deliverables**:
- Failure frequency bar chart (by category)
- Architecture-failure correlation heatmap
- Reproduction rate table
- Analysis report with findings

**Budget**: $0 (no API calls)

---

## Data Collection Format

### Per-run data structure (JSON)
```json
{
  "run_id": "fi014_react_run001",
  "failure_instance": "FI-014",
  "framework": "react",
  "model": "gpt-4-turbo",
  "task": "laptop_research",
  "timestamp": "2026-03-30T10:00:00Z",
  "cost_usd": 0.75,
  "turns": 8,
  "tokens_total": 12500,
  "outcome": {
    "failure_reproduced": true,
    "failure_category": "3.1",
    "turns_to_failure": 4,
    "loop_detected": true,
    "task_completed": false
  },
  "transcript": [
    {"turn": 1, "observation": "...", "thought": "...", "action": "..."},
    {"turn": 2, "observation": "...", "thought": "...", "action": "..."}
  ],
  "annotations": {
    "llm_limitation": "C3",
    "severity": "high",
    "notes": "Agent repeated same search 3 times"
  }
}
```

### Aggregated results (YAML)
```yaml
failure_instance: FI-014
total_runs: 10
reproduction_rate: 0.80
mean_turns_to_failure: 4.2
mean_cost_per_run: 0.72
framework_breakdown:
  react: {runs: 10, reproduction_rate: 0.80}
```

---

## Quality Controls

### Validation checks
1. **Ground truth verification**: Manually review 10% of runs to confirm failure classification
2. **Inter-rater reliability**: If ambiguous, have 2 coders classify independently
3. **Cost monitoring**: Halt if cost exceeds budget × 1.5
4. **Checkpoint integrity**: Verify checkpoints enable exact resume
5. **Transcript completeness**: Every run must have full transcript saved

### Failure criteria (when to stop)
- Reproduction rate < 30% after 10 runs → failure not reproducible, document and move on
- Cost overrun > 2x estimate → revise or skip
- Framework crashes repeatedly → fix infrastructure before continuing

---

## Analysis Plan

### Statistical tests

**H1: Failure categories are distinct**
- Method: Chi-square test for independence (failure type × framework)
- Prediction: Significant association (p < 0.05)
- Interpretation: Different frameworks have different failure profiles

**H2: LLM limitations predict failures**
- Method: Correlation between C1-C8 mapping and observed failure rates
- Prediction: Failures mapped to C3, C7 have highest reproduction rates
- Interpretation: Validates theoretical grounding

**H3: Mitigation effectiveness**
- Method: A/B test (with vs. without mitigation)
- Example: External progress monitoring reduces infinite loops
- Prediction: Mitigation reduces failure rate by ≥30%

### Figures for paper

**Figure 1: Failure Reproduction Rates by Category**
- Bar chart: X = taxonomy category, Y = reproduction rate
- Error bars: 95% CI from bootstrapping
- Finding: "Categories 3.1, 5.2, 4.3 reproduce most reliably"

**Figure 2: Architecture-Failure Correlation Heatmap**
- Heatmap: Rows = frameworks, Columns = failure categories
- Color: Reproduction rate (0-100%)
- Finding: "ReAct shows high 3.1 (loops), Reflexion shows high 5.2 (bias)"

**Figure 3: LLM Limitation Severity**
- Bar chart: X = C1-C8 dimensions, Y = % of failures mapped to each
- Finding: "C3 (meta-cognitive) and C7 (self-correction) underlie 45% of failures"

---

## Deviations from Plan (if any)

Document any deviations from this protocol here with date and rationale:

- [Date] [Deviation] [Rationale]

---

## Estimated Timeline

- **Session 8** (current): Protocol design + infrastructure setup (2 hours)
- **Session 9**: Pilot runs (2-3 hours, $15-30)
- **Session 10**: Full reproductions Tier 1-2 (3-4 hours, $60-120)
- **Session 11**: Analysis + figures (2-3 hours, $0)
- **Session 12**: Results documentation + status update (1 hour, $0)

**Total**: 10-13 hours, $75-150

**Buffer**: Under budget ($200-300), under ACL deadline (10 months)

---

## Success Criteria for Experimental Phase

This experimental phase is successful if:
1. ✅ At least 4 of 6 Tier 1-2 failures reproduce at ≥50% rate
2. ✅ Architecture-failure correlation matrix is populated with data
3. ✅ At least 2 LLM limitations (C1-C8) are empirically validated
4. ✅ Cost stays under $200
5. ✅ Agent transcripts suitable for paper examples are collected

**Minimum viable result**: 3 failures reproduced + correlation data → sufficient for paper empirical section

**Stretch goal**: All 8 failures + mitigation tests → stronger empirical contribution

---

## Notes

- This protocol focuses on **validation**, not discovery of new failures
- Pre-registered to avoid p-hacking (we're testing taxonomy, not exploratory analysis)
- Pilot phase (Session 9) is critical — if failures don't reproduce, we revise approach
- Infrastructure investment (Session 8) pays off: enables rapid iteration in Sessions 9-10

**Document status**: Draft, ready for review before pilot execution
