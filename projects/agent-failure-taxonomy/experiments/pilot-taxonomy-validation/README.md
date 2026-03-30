# Pilot Taxonomy Validation Experiment

**Status**: Draft - awaiting critic review
**Created**: 2026-03-30
**Estimated cost**: $1.50 (canary: $0.30)

## Overview

This pilot experiment validates our 9-category agent failure taxonomy by reproducing 3 high-priority failure modes across 3 agent architectures and 2 model families. The goal is to confirm that:

1. **Failures are reproducible** in controlled settings
2. **Categories are distinct** (failures clearly map to single categories)
3. **Architecture matters** (different architectures show different failure frequencies)

## Failures Under Test

### 1. Tool Fabrication (Category 1: Tool-Use Failures)
- **Based on**: Instance 18 from literature review
- **Description**: Agent calls non-existent tools when tool count is high
- **Hypothesis**: Occurs at >15% rate when tool count exceeds 20
- **Ground truth**: Pre-defined valid tool list
- **Task**: Present agent with 25 tools (20 real, 5 non-existent decoys in documentation)

### 2. Infinite Loop (Category 3: Planning Failures)
- **Based on**: Instance 14 (AutoGPT looping)
- **Description**: Agent repeats same failed action without recognizing stagnation
- **Hypothesis**: Occurs at >30% rate on ambiguous tasks
- **Ground truth**: Action sequence analysis (5+ repeated actions with no state change)
- **Task**: Ambiguous task like "improve the code quality" without specific criteria

### 3. False Completion (Category 5: Self-Correction Failures)
- **Based on**: Instances 19, 25 from literature review
- **Description**: Agent reports task complete when objectively incomplete
- **Hypothesis**: Occurs at >20% rate on multi-step tasks
- **Ground truth**: External verification of task completion criteria
- **Task**: Multi-step task like "fetch data, process it, and save results" with verifiable outputs

## Architecture Comparison

Testing across 3 frameworks to measure architecture-failure correlation:

1. **ReAct** (via LangChain)
   - Prediction: High infinite loop risk, moderate tool fabrication
2. **Plan-then-Execute** (via LangChain)
   - Prediction: High false completion risk, low infinite loop risk
3. **Autonomous Loop** (minimal AutoGPT-style)
   - Prediction: Highest infinite loop risk, high false completion

## Expected Outputs

### Data Files
- `results/tool_fabrication_{framework}_{model}.jsonl` - Per-instance results
- `results/infinite_loop_{framework}_{model}.jsonl`
- `results/false_completion_{framework}_{model}.jsonl`
- `results/summary_statistics.json` - Aggregated failure rates

### Analysis Outputs
- Table: Failure rate by architecture (for paper)
- Figure: Failure frequency heatmap (architecture × failure type)
- Statistical tests: Chi-square for architecture differences

### Validation Checks
- [ ] All 3 failure types are reproducible (>5% occurrence)
- [ ] At least 2 of 3 meet predicted thresholds
- [ ] Framework differences are statistically significant (p < 0.05)
- [ ] Cost within 2x of estimate

## Infrastructure Requirements

See `src/` directory for implementation:

1. **Task Generators** (`src/tasks/`)
   - `tool_fabrication.py` - Generate tool sets with decoys
   - `infinite_loop.py` - Generate ambiguous tasks
   - `false_completion.py` - Generate multi-step verification tasks

2. **Framework Wrappers** (`src/frameworks/`)
   - `react_wrapper.py` - LangChain ReAct implementation
   - `plan_execute_wrapper.py` - LangChain plan-execute
   - `autonomous_loop_wrapper.py` - Minimal AutoGPT-style loop

3. **Evaluation** (`src/eval/`)
   - `ground_truth.py` - Automated verification for each failure type
   - `metrics.py` - Compute failure rates, statistics
   - `analysis.py` - Generate tables and figures

4. **Infrastructure** (`src/utils/`)
   - `logger.py` - Structured logging of agent traces
   - `checkpoint.py` - Save/resume evaluation state
   - `cost_tracker.py` - Track API costs per call

## Next Steps

1. **Awaiting critic review** of spec.yaml
2. After approval: Build infrastructure in `src/`
3. Run canary (54 trials, $0.30)
4. If canary passes: Run full pilot (180 trials, $1.50)
5. Analyze results and update status.yaml
6. If successful: Design scale-up experiment (6 failures, 2160 trials)

## Timeline

- Infrastructure build: 1 session (this session)
- Canary run: 30 minutes
- Full pilot: 2-3 hours (with checkpointing)
- Analysis: 1 hour

Total: Can complete in 1-2 sessions after critic approval
