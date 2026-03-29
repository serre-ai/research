# Experimental Protocol: Agent Failure Taxonomy Validation

**Date**: 2026-03-29
**Purpose**: Empirically validate taxonomy through controlled reproduction of key failure modes
**Experimenter**: Claude (Experimenter Agent, Session 8)
**Status**: Protocol design phase

---

## Objectives

### Primary
1. **Validate taxonomy applicability**: Confirm that our 9 categories accurately describe failures across different agent frameworks
2. **Quantify frequency**: Measure failure mode frequency across architectures
3. **Test architecture-failure correlation**: Validate preliminary correlation matrix from taxonomy

### Secondary
4. **Validate reproducibility estimates**: Test whether "highly reproducible" instances can be reliably reproduced
5. **Measure mitigation effectiveness**: Test whether predicted mitigations actually reduce failures
6. **Establish baseline for future work**: Create benchmark tasks for agent failure testing

---

## Framework Selection

### Criteria
- **Architecture diversity**: Cover at least 3 distinct architectures from taxonomy
- **Reproducibility**: Open-source, well-documented, actively maintained
- **Control**: Can modify prompts, tools, task definitions
- **Observability**: Can log internal state, tool calls, reasoning steps

### Selected Frameworks (3 core + 1 optional)

#### 1. ReAct (via LangChain)
- **Architecture**: Reactive reasoning-and-acting loop
- **Why**: Most common architecture; 11 instances in our data; high baseline for comparison
- **Implementation**: LangChain's ReAct agent with custom tools
- **Expected failures**: Infinite loops (3.1), tool fabrication (1.1), context degradation (4.3)

#### 2. Plan-then-Execute (Custom Implementation)
- **Architecture**: Upfront planning followed by execution
- **Why**: Different failure profile; predicted low planning failures, high state verification issues
- **Implementation**: Two-stage: GPT-4 generates plan, then executor follows steps
- **Expected failures**: False completion (5.1), state divergence (4.1)

#### 3. Reflexion (Simplified Implementation)
- **Architecture**: Self-reflection and correction loop
- **Why**: Tests C7 (self-correction capability); predicted confirmation bias
- **Implementation**: Task attempt → reflection → retry with reflection context
- **Expected failures**: Confirmation bias (5.2), degeneration-of-thought (5.2)

#### 4. AutoGPT-style Autonomous Loop (Optional, if budget allows)
- **Architecture**: Autonomous goal-driven loop with memory
- **Why**: High-profile failures in our data; complex failure interactions
- **Implementation**: Simplified version: goal → plan → act → evaluate → loop
- **Expected failures**: Infinite loops (3.1), progress monitoring failure (3.1), memory issues (4.2)

**Decision**: Start with 3 core frameworks (ReAct, Plan-Execute, Reflexion). Add AutoGPT if pilot shows low costs.

---

## Failure Mode Selection

### Selection Criteria
- **Coverage**: At least 1 failure per major category
- **Reproducibility**: Only "Easy" or "High" reproducibility instances
- **Theoretical importance**: Prioritize failures connected to fundamental limitations (C1-C8)
- **Architecture variance**: Mix of architecture-specific and cross-cutting failures

### Selected Failures (6 core)

#### F1: Tool Fabrication (Category 1.1)
- **Instance**: Instance 18 - Tool hallucination scales with tool count
- **LLM Limitation**: C6 (Tool Grounding) + C1 (Factual Grounding)
- **Reproducibility**: Easy
- **Test Design**: Provide agent with 20-30 tools, task requires subset, measure fabrication rate
- **Success Metric**: % of tool calls to non-existent tools
- **Frameworks**: ReAct, Plan-Execute
- **Expected Result**: Both architectures show fabrication; ReAct higher due to no planning phase

#### F2: Infinite Loops (Category 3.1)
- **Instance**: Instance 14 - AutoGPT enters infinite loop on ambiguous tasks
- **LLM Limitation**: C3 (Meta-Cognitive Monitoring)
- **Reproducibility**: High
- **Test Design**: Ambiguous task with no clear completion criteria, measure loop detection
- **Success Metric**: # iterations before manual termination; self-detected stagnation (yes/no)
- **Frameworks**: ReAct, AutoGPT-style (if implemented)
- **Expected Result**: High loop rate in ReAct; no self-detection

#### F3: Context Degradation (Category 4.3)
- **Instance**: Instance 49 - Performance drops below 50% at 32k tokens
- **LLM Limitation**: C2 (Long-Range Coherence) - FUNDAMENTAL
- **Reproducibility**: Easy
- **Test Design**: Multi-step reasoning task with increasing context length (4k, 8k, 16k, 32k tokens)
- **Success Metric**: Task success rate vs. context length
- **Frameworks**: All (architecture-independent)
- **Expected Result**: Degradation at 16k+, severe at 32k+ across all architectures

#### F4: Self-Correction Failure / Confirmation Bias (Category 5.2)
- **Instance**: Instance 43 - Reflexion repeats same error despite reflection
- **LLM Limitation**: C7 (Self-Correction Capability) - FUNDAMENTAL
- **Reproducibility**: High
- **Test Design**: Task with common error pattern, allow self-reflection, measure correction
- **Success Metric**: Error correction rate; repetition of same error (yes/no)
- **Frameworks**: Reflexion, Plan-Execute (with reflection step)
- **Expected Result**: Low correction rate; same errors repeated; reflection reinforces misconceptions

#### F5: False Completion (Category 5.1)
- **Instance**: Instance 25 - Agent claims completion without verifying state
- **LLM Limitation**: C3 (Meta-Cognitive Monitoring) + C5 (State Tracking)
- **Reproducibility**: High
- **Test Design**: Multi-step task with verifiable completion criteria, agent claims done, check actual state
- **Success Metric**: False completion rate (claims done but task incomplete)
- **Frameworks**: Plan-Execute, ReAct
- **Expected Result**: Plan-Execute higher (single verification point); ReAct lower (iterative)

#### F6: State Divergence (Category 4.1)
- **Instance**: Instance 37 - Agent's internal state model ≠ actual state after actions
- **LLM Limitation**: C5 (State Tracking)
- **Reproducibility**: High
- **Test Design**: Task with state-changing actions (create/delete/modify), compare agent's stated beliefs vs. actual state
- **Success Metric**: State divergence frequency; magnitude of divergence
- **Frameworks**: All
- **Expected Result**: Divergence increases with # of state changes; no spontaneous reconciliation

---

## Experimental Design

### Task Design Principles
1. **Ground truth available**: Can automatically verify success/failure
2. **Minimal confounds**: Isolate target failure mode
3. **Controllable difficulty**: Can vary to test scaling behavior
4. **Representative**: Reflects real agent use cases

### Common Parameters
- **Temperature**: 0.0 (deterministic for reproducibility)
- **Model**: GPT-4o (2024-11-20) as baseline; may add Claude Sonnet 3.7 if budget allows
- **Instances per condition**: 20 (sufficient for frequency estimation with CI)
- **Timeout**: 5 minutes per task attempt
- **Max iterations**: 20 (for looping architectures)

### Measurement Protocol
1. **Automatic logging**: All tool calls, reasoning traces, state snapshots
2. **Ground truth comparison**: Automated verification where possible
3. **Manual coding**: For ambiguous failures, two-coder agreement (self + documented criteria)
4. **Confidence intervals**: Bootstrap 95% CI for all frequency estimates

---

## Pilot Experiment Design

**Goal**: Validate infrastructure and cost estimates before full run

### Pilot Scope
- **Failures**: F1 (Tool Fabrication) + F2 (Infinite Loops)
- **Frameworks**: ReAct only (simplest to implement)
- **Instances**: 5 per failure type
- **Model**: GPT-4o

### Pilot Success Criteria
1. **Infrastructure works**: Logging, checkpointing, ground truth verification all functional
2. **Failures reproduce**: At least 1 instance of each failure type observed
3. **Cost within budget**: Actual cost ≤ 2x estimated cost per instance
4. **Data quality**: Can extract all planned metrics from logs

### Pilot Budget Estimate
- **F1 Tool Fabrication**: 5 instances × ~500 tokens/instance × $0.0025/1k tokens = $0.006
- **F2 Infinite Loops**: 5 instances × ~2000 tokens/instance (will timeout) × $0.0025/1k tokens = $0.025
- **Total pilot**: ~$0.03

### Full Experiment Budget Estimate (if pilot succeeds)
- **6 failure types** × **3 frameworks avg** × **20 instances** × **~1000 tokens avg** × **$0.0025/1k**
- = 360 instances × 1000 tokens × $0.0025/1k = **~$0.90**
- Add 50% buffer for retries, debugging: **$1.35 total**

**Well within $2 threshold, but still do pre-registration spec as good practice.**

---

## Infrastructure Requirements

### Code Structure
```
src/
  frameworks/
    react_agent.py       # ReAct implementation
    plan_execute.py      # Plan-then-execute implementation
    reflexion.py         # Reflexion implementation
  tasks/
    tool_fabrication.py  # F1 task generator
    infinite_loop.py     # F2 task generator
    context_degradation.py  # F3 task generator
    self_correction.py   # F4 task generator
    false_completion.py  # F5 task generator
    state_divergence.py  # F6 task generator
  utils/
    logging.py           # Structured logging
    evaluation.py        # Ground truth verification
    checkpointing.py     # Crash recovery
  run_experiment.py      # Main experiment runner
```

### Data Structure
```
experiments/
  results/
    pilot/
      f1_tool_fabrication/
        logs/            # Raw logs per instance
        summary.json     # Aggregated metrics
      f2_infinite_loops/
        logs/
        summary.json
    full/
      [same structure, all 6 failures]
  checkpoints/           # Resumable state
  analysis/
    figures/             # Generated plots
    reports/             # Analysis markdown files
```

---

## Analysis Plan

### Primary Analyses (Pre-Registered)

#### A1: Taxonomy Category Validation
- **Hypothesis**: Observed failures map cleanly to taxonomy categories
- **Method**: Code each failure instance to categories; measure inter-rater reliability (self vs. documented criteria)
- **Success**: >90% agreement with taxonomy category assignments

#### A2: Frequency Estimation
- **Hypothesis**: Failure frequencies vary by architecture
- **Method**: Estimate failure rate per framework with 95% bootstrap CI
- **Output**: Table of failure rates by framework
- **Success**: CIs do not overlap for hypothesized differences

#### A3: Architecture-Failure Correlation
- **Hypothesis**: Preliminary correlation matrix is accurate
- **Method**: Chi-square test for independence between architecture and failure type
- **Output**: Updated correlation matrix with statistical significance
- **Success**: Predicted high-risk combinations show higher rates (p < 0.05)

#### A4: Fundamental vs. Correctable
- **Hypothesis**: C2, C3, C7 limitations appear across all architectures (fundamental); others are architecture-dependent (correctable)
- **Method**: Compare failure rates for C2/C3/C7-linked failures across architectures
- **Output**: Variance analysis; fundamental failures show low inter-architecture variance
- **Success**: C2/C3/C7 failures show consistent rates; others vary significantly

### Secondary Analyses (Exploratory)

#### E1: Reproducibility Validation
- **Method**: Compare pilot reproduction rate to literature-reported "reproducibility" ratings
- **Question**: Do our "highly reproducible" estimates hold?

#### E2: Scaling Behavior
- **Method**: For F1 and F3, vary difficulty parameter (tool count, context length)
- **Question**: Are failure rates linear, threshold, or exponential in difficulty?

---

## Success Criteria (Overall Experiment)

1. **Taxonomy validated**: A1 shows >90% category agreement
2. **Architecture differences confirmed**: A2 shows distinguishable frequency profiles
3. **Theoretical grounding supported**: A4 confirms fundamental vs. correctable distinction
4. **Publication-ready data**: Can generate tables/figures for paper

---

## Risks and Mitigations

### Risk 1: Failures don't reproduce
- **Likelihood**: Low (selected only "Easy"/"High" reproducibility)
- **Impact**: High (invalidates taxonomy)
- **Mitigation**: Pilot test first; if pilot fails, revise task design before full run

### Risk 2: Cost exceeds estimate
- **Likelihood**: Medium (agent loops can be expensive)
- **Impact**: Medium (have $5 budget)
- **Mitigation**: Strict timeouts; pilot validates costs; halt if approaching budget

### Risk 3: Infrastructure bugs delay experiments
- **Likelihood**: Medium (new code)
- **Impact**: Low (time not critical; no deadline pressure)
- **Mitigation**: Incremental development; pilot catches bugs before full run

### Risk 4: Results are ambiguous
- **Likelihood**: Medium (some failures are subtle)
- **Impact**: Medium (weaker claims in paper)
- **Mitigation**: Pre-registered success criteria; clear ground truth; conservative interpretation

---

## Timeline (This Session)

1. **Protocol design** (this document): 20 minutes ✅
2. **Pre-registration spec**: 15 minutes
3. **Infrastructure skeleton**: 30 minutes
4. **Pilot F1 (Tool Fabrication)**: 20 minutes
5. **Pilot F2 (Infinite Loops)**: 20 minutes
6. **Analysis and report**: 20 minutes
7. **Status update**: 10 minutes

**Total**: ~135 minutes (within session limits)

---

## Next Steps

1. Create pre-registration spec (`experiments/pilot/spec.yaml`)
2. Build infrastructure (`src/frameworks/react_agent.py`, `src/tasks/tool_fabrication.py`)
3. Run pilot F1
4. Run pilot F2
5. Analyze pilot results
6. Update status.yaml
7. Commit and push

---

## Document Status

**Completed**: 2026-03-29
**Ready for**: Pre-registration spec creation
**Decision log**: Will be added to status.yaml after pilot completion
