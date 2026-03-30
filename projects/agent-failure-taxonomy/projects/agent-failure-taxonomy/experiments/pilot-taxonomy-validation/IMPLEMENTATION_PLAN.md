# Implementation Plan - Pilot Taxonomy Validation

**Status**: Infrastructure ~60% complete
**Next session**: Complete task generators and framework wrappers

## Completed ✅

### Core Infrastructure
- [x] Base task generator interface (`src/tasks/base.py`)
- [x] Base agent wrapper interface (`src/frameworks/base.py`)
- [x] Cost tracking with budget limits (`src/utils/cost_tracker.py`)
- [x] Checkpoint management (`src/utils/checkpoint.py`)
- [x] Structured trace logging (`src/utils/logger.py`)
- [x] Tool fabrication task generator (`src/tasks/tool_fabrication.py`)

### Experiment Design
- [x] Pre-registration spec (`spec.yaml`)
- [x] Experiment README
- [x] Requirements file
- [x] Environment template

## In Progress 🚧

### Task Generators (1/3 complete)
- [x] Tool fabrication
- [ ] Infinite loop detection
- [ ] False completion reporting

### Framework Wrappers (0/3 complete)
- [ ] ReAct (LangChain)
- [ ] Plan-then-execute (LangChain)
- [ ] Autonomous loop (minimal AutoGPT-style)

## Not Started ⏸️

### Evaluation & Analysis
- [ ] Ground truth verification (`src/eval/ground_truth.py`)
- [ ] Metrics computation (`src/eval/metrics.py`)
- [ ] Figure generation (`src/eval/analysis.py`)

### Execution Scripts
- [ ] Canary run script
- [ ] Full experiment runner
- [ ] Results aggregation

## Implementation Order (Next Session)

### Phase 1: Complete Task Generators (1-2 hours)

**Task 2: Infinite Loop Generator** (`src/tasks/infinite_loop.py`)
- Generate ambiguous tasks without clear completion criteria
- Verification: Check if agent repeats same action 5+ times
- Example: "Improve the code quality" without specific metrics

**Task 3: False Completion Generator** (`src/tasks/false_completion.py`)
- Generate multi-step tasks with verifiable completion criteria
- Verification: External check of actual task completion
- Example: "Fetch data, process it, save results" with checkable outputs

### Phase 2: Framework Wrappers (2-3 hours)

**ReAct Wrapper** (`src/frameworks/react_wrapper.py`)
- Use LangChain's ReAct agent
- Provide tools as LangChain tools
- Log all reasoning steps and tool calls
- Track costs per API call

**Plan-Execute Wrapper** (`src/frameworks/plan_execute_wrapper.py`)
- Use LangChain's plan-and-execute agent
- Separate planning and execution phases
- Log plan and execution traces separately

**Autonomous Loop Wrapper** (`src/frameworks/autonomous_loop_wrapper.py`)
- Minimal AutoGPT-style loop: observe → think → act → repeat
- No explicit planning phase
- Iteration limit as stopping condition

### Phase 3: Evaluation Pipeline (1 hour)

**Ground Truth Verification** (`src/eval/ground_truth.py`)
- Implement verification functions for each failure type
- Tool fabrication: Check if called tools are in available set
- Infinite loop: Analyze action sequence for repetition
- False completion: Compare claimed vs. actual completion

**Metrics** (`src/eval/metrics.py`)
- Compute failure rates by (framework, model, failure_type)
- Statistical significance tests (chi-square for architecture differences)
- Confidence intervals (bootstrap)

### Phase 4: Execution & Analysis (1 hour)

**Runner Scripts**
- `run_canary.py`: Execute canary with 54 trials
- `run_full.py`: Execute full experiment with 180 trials
- `aggregate_results.py`: Combine checkpoints into summary

**Analysis**
- Generate Table 2 for paper (failure rate by architecture)
- Generate heatmap figure (architecture × failure type)
- Statistical tests for architecture differences

## Testing Strategy

Before full run:
1. **Unit test** each task generator with deterministic seeds
2. **Integration test** one instance end-to-end per framework
3. **Canary run** (54 trials, ~$0.30) to validate full pipeline
4. **Full run** only if canary passes all diagnostics

## Risk Mitigation

**Cost Overruns**
- Hard budget limit in CostTracker ($2.50)
- Canary first to validate cost estimates
- Checkpointing allows stopping and resuming

**Infrastructure Bugs**
- Comprehensive logging of all actions
- Manual inspection of first few instances
- Canary diagnostics catch pipeline issues

**Low Failure Rates**
- If <5% occurrence, task generation may need tuning
- Can adjust difficulty (e.g., increase tool count to 30+)
- Pilot is exploratory - low rates are still useful data

## Timeline Estimate

- **Remaining implementation**: 4-5 hours
- **Canary run**: 30 minutes
- **Canary analysis**: 30 minutes
- **Full run** (if canary passes): 2-3 hours
- **Analysis and figures**: 1-2 hours

**Total**: ~8-11 hours across 2 sessions

## Success Criteria

Infrastructure is ready when:
- [x] All base classes implemented
- [x] At least 1 task generator working
- [ ] All 3 task generators implemented and tested
- [ ] All 3 framework wrappers implemented and tested
- [ ] End-to-end test produces valid checkpoint
- [ ] Cost tracking works correctly
- [ ] Logging produces analyzable traces

Experiment succeeds if:
- At least 2 of 3 failure types are reproducible (>5% rate)
- Framework differences are observable (>10% delta)
- Cost within 2x of estimate
- Data quality allows statistical analysis

## Notes

- This is a **pilot** - expect to iterate on task generation
- Primary goal is infrastructure validation, not final data
- Negative results (low failure rates) are still publishable if methodology is sound
- Can scale up to 6 failures × 4 frameworks × 30 instances after pilot succeeds
