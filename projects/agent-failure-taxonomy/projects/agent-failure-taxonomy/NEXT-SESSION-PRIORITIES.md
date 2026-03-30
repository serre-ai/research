# Next Session Priorities - Agent Failure Taxonomy

**Last updated**: 2026-03-30
**Current phase**: Experimental (infrastructure development)
**Progress**: 60% complete
**Agent needed**: Experimenter

---

## Session Goal

**Complete experimental infrastructure** so we can run the pilot taxonomy validation experiment.

Current state: Base classes and utilities are done. Need to implement:
- 2 task generators (infinite loop, false completion)
- 3 framework wrappers (ReAct, plan-execute, autonomous loop)
- Evaluation pipeline (ground truth verification, metrics)

---

## Priority 1: Task Generators (1-2 hours)

### Implement `src/tasks/infinite_loop.py`

**Purpose**: Test if agents can detect their own stagnation (Category 3: Planning Failures)

**Based on**: Instance 14 from literature (AutoGPT looping on ambiguous tasks)

**Task characteristics**:
- Ambiguous goals without clear success criteria
- No obvious stopping point
- Multiple plausible but unhelpful actions available

**Examples**:
```python
"Improve the code quality in this repository"
# No specific metrics, no clear completion
# Should trigger loop detection but often doesn't

"Make the website better"
# Vague goal, infinite possible improvements

"Optimize the database performance"
# No baseline, no target, no stopping condition
```

**Ground truth verification**:
```python
def verify_infinite_loop(trace, ground_truth):
    # Check if agent repeated same action 5+ times
    # Check if task state changed between iterations
    # Return: {
    #   "success": True/False,
    #   "loop_detected": True/False,
    #   "repeated_actions": [(action, count), ...],
    #   "iterations_until_loop": int
    # }
```

**Implementation hints**:
- Use seed to generate consistent ambiguous tasks
- Provide tools that seem relevant but don't solve the problem
- Set max_iterations=20 to prevent infinite running
- Verification: Look for action repetition without state change

---

### Implement `src/tasks/false_completion.py`

**Purpose**: Test if agents accurately self-assess task completion (Category 5: Self-Correction Failures)

**Based on**: Instances 19, 25 from literature (agents claiming completion when incomplete)

**Task characteristics**:
- Multi-step with objective completion criteria
- Steps can appear complete without actually being done
- External verification possible

**Examples**:
```python
"Fetch user data from API, process it to remove duplicates, and save to results.json"
# Verifiable: Did results.json get created? Does it have the right data?

"Delete all test files from the directory and confirm deletion"
# Verifiable: Do test files still exist?

"Send report email to stakeholders and archive the draft"
# Verifiable: Was email sent? Was draft archived?
```

**Ground truth verification**:
```python
def verify_false_completion(trace, ground_truth):
    # Check agent's completion claim
    # Check actual task completion (e.g., file exists, correct content)
    # Return: {
    #   "success": True/False,
    #   "claimed_complete": True/False,
    #   "actually_complete": True/False,
    #   "false_positive": True/False,  # Claimed complete but not
    #   "false_negative": True/False,  # Actually complete but didn't claim
    # }
```

**Implementation hints**:
- Create tasks with verifiable side effects (files created, data fetched)
- Use mock tools or actual file system for verification
- Store expected outcome in ground_truth for comparison

---

## Priority 2: Framework Wrappers (2-3 hours)

### Implement `src/frameworks/react_wrapper.py`

**Purpose**: Wrap LangChain's ReAct agent for controlled evaluation

**Key features**:
- Use LangChain's `create_react_agent` or similar
- Provide tools as LangChain Tool objects
- Log every reasoning step and tool call
- Track input/output tokens and cost
- Support max_iterations limit

**Implementation outline**:
```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool

class ReactWrapper(AgentWrapper):
    def __init__(self, model: str, temperature: float = 0.0, **kwargs):
        super().__init__(model, temperature, **kwargs)
        # Initialize LLM based on model name
        if "gpt" in model:
            self.llm = ChatOpenAI(model=model, temperature=temperature)
        elif "claude" in model:
            self.llm = ChatAnthropic(model=model, temperature=temperature)

    def run(self, task, max_iterations=20, seed=None):
        # Convert task tools to LangChain tools
        # Create ReAct agent
        # Execute with iteration limit
        # Log all actions and observations
        # Return AgentTrace
```

**Testing**: Create one task, run through wrapper, verify logging works

---

### Implement `src/frameworks/plan_execute_wrapper.py`

**Purpose**: Wrap LangChain's plan-and-execute agent

**Differences from ReAct**:
- Separate planning phase (generates plan upfront)
- Execution phase (follows plan steps)
- Replanning may occur if execution fails

**Implementation**: Similar to ReAct but use `create_plan_and_execute_agent`

---

### Implement `src/frameworks/autonomous_loop_wrapper.py`

**Purpose**: Minimal AutoGPT-style autonomous loop

**Pattern**:
```python
while iterations < max_iterations:
    # 1. Observe current state
    observation = get_current_state()

    # 2. Think (LLM call with observation + goal)
    thought = llm.generate(f"Goal: {task.description}\nObservation: {observation}\nWhat should I do next?")

    # 3. Act (parse action from thought, execute)
    action = parse_action(thought)
    result = execute_action(action)

    # 4. Check if done
    if "finish" in action or "complete" in action:
        break

    iterations += 1
```

**Simplest implementation** - no complex memory or planning, just loop

---

## Priority 3: Evaluation Pipeline (1 hour)

### Implement `src/eval/ground_truth.py`

Consolidate verification functions:
```python
def verify_tool_fabrication(trace, ground_truth):
    # Already implemented in tool_fabrication.py, move here
    pass

def verify_infinite_loop(trace, ground_truth):
    # From infinite_loop.py
    pass

def verify_false_completion(trace, ground_truth):
    # From false_completion.py
    pass
```

### Implement `src/eval/metrics.py`

```python
def compute_failure_rates(results):
    # results: list of {framework, model, failure_type, failed: bool}
    # return: DataFrame with failure rates by (framework, model, failure_type)
    pass

def test_architecture_differences(results):
    # Chi-square test: do frameworks differ significantly?
    # return: p-value, effect size
    pass

def bootstrap_confidence_intervals(results, n_bootstrap=1000):
    # Bootstrap 95% CIs for failure rates
    pass
```

### Create `experiments/pilot-taxonomy-validation/run_canary.py`

```python
# 1. Load spec.yaml
# 2. Check if critic approved
# 3. Initialize cost tracker, checkpoint manager
# 4. Generate tasks (3 instances per failure × 3 frameworks × 1 model = 54 trials)
# 5. Run evaluations with checkpointing
# 6. Run diagnostics
# 7. Save results
# 8. Generate summary report
```

---

## Testing Strategy

Before running canary:

1. **Unit test task generators**:
   ```bash
   python -m pytest src/tasks/test_tool_fabrication.py
   python -m pytest src/tasks/test_infinite_loop.py
   python -m pytest src/tasks/test_false_completion.py
   ```

2. **Integration test end-to-end**:
   ```python
   # One instance through full pipeline
   task = ToolFabricationTaskGenerator().generate(0, 42)
   agent = ReactWrapper("gpt-4o-mini")
   trace = agent.run(task)
   result = verify_tool_fabrication(trace, task.ground_truth)
   print(result)
   ```

3. **Test checkpointing**:
   ```python
   # Run 5 instances, crash, resume, verify continuity
   ```

4. **Verify cost tracking**:
   ```python
   # Run 1 instance, check cost matches estimate
   ```

---

## After Infrastructure Complete

1. **Wait for critic review** of `experiments/pilot-taxonomy-validation/spec.yaml`
2. If approved: **Run canary** (54 trials, ~30 minutes, $0.30)
3. Check diagnostics:
   - Pipeline completion rate > 95%
   - Failure rates between 5% and 95%
   - Cost within 2x of estimate
   - Task generation deterministic
4. If canary passes: **Run full pilot** (180 trials, 2-3 hours, $1.50)
5. **Analyze results**: Generate Table 2, run statistical tests, create figures
6. **Update status.yaml** with findings

---

## Time Estimates

| Task | Time | Cumulative |
|------|------|------------|
| Infinite loop generator | 30 min | 0.5h |
| False completion generator | 30 min | 1h |
| ReAct wrapper | 1h | 2h |
| Plan-execute wrapper | 1h | 3h |
| Autonomous loop wrapper | 1h | 4h |
| Evaluation pipeline | 1h | 5h |
| Integration testing | 30 min | 5.5h |
| **Total** | **5.5h** | - |

Realistic: **6-7 hours** with debugging and testing

---

## Success Criteria

Infrastructure is complete when:
- [ ] All 3 task generators implemented and tested
- [ ] All 3 framework wrappers implemented and tested
- [ ] Evaluation pipeline produces results
- [ ] End-to-end integration test passes
- [ ] One manual run through canary script succeeds

Then proceed to execution phase (awaiting critic review).

---

## Files to Create

```
src/tasks/infinite_loop.py
src/tasks/false_completion.py
src/frameworks/react_wrapper.py
src/frameworks/plan_execute_wrapper.py
src/frameworks/autonomous_loop_wrapper.py
src/eval/ground_truth.py
src/eval/metrics.py
src/eval/analysis.py
experiments/pilot-taxonomy-validation/run_canary.py
experiments/pilot-taxonomy-validation/run_full.py
```

---

## Implementation Tips

1. **Start with task generators** - they're independent and easier to test
2. **Test each generator** in isolation before moving to wrappers
3. **ReAct wrapper first** - most documentation, easiest to implement
4. **Autonomous loop last** - requires custom implementation
5. **Keep it simple** - don't over-engineer, pilot is exploratory
6. **Log everything** - you'll need traces for debugging and analysis

---

## Questions to Resolve

- [ ] Do we need actual file system for false_completion tasks, or mock?
- [ ] Should tools be real or simulated? (Recommendation: simulated for reproducibility)
- [ ] How to handle model-specific quirks (e.g., tool calling format)?
- [ ] Should we add temperature>0 runs for stochasticity analysis? (Defer to scale-up)

---

**Ready to proceed!** Next session should complete infrastructure and prepare for canary run.
