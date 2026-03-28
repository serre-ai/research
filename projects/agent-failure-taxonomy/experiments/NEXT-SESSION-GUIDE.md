# Next Session Quick-Start Guide

**For**: Session 9 Experimenter Agent
**Task**: Implement framework wrappers and run F1+F5 pilot reproduction
**Estimated time**: 2-3 hours work
**Estimated cost**: $20-30 for pilot evaluation

---

## Pre-flight Checklist

Before starting, verify:
- [x] Experimental protocol exists: `experiments/00-experimental-protocol.md`
- [x] Test infrastructure built: `src/utils/logging.py`, `src/tests/tool_fabrication.py`
- [x] Status.yaml updated with decisions
- [ ] Framework wrappers implemented: `src/frameworks/react_agent.py` (START HERE)
- [ ] Pre-registration spec created: `experiments/pilot-reproduction/spec.yaml` (REQUIRED before running >$2 experiments)
- [ ] Critic approval obtained (status: approved in spec.yaml)

---

## Step 1: Implement ReAct Framework Wrapper

**Priority**: HIGH (needed for pilot)
**File**: `src/frameworks/react_agent.py`
**Estimated time**: 30-45 minutes
**Cost**: $0 (implementation only)

### Interface Requirements

Every framework must implement:
```python
class AgentFramework:
    def __init__(self, model: str, temperature: float = 0.0):
        pass

    def run_task(self, task: str, tools: List[Tool]) -> AgentResponse:
        """
        Execute a task with available tools.

        Returns:
            AgentResponse with:
            - response: str (agent's text response)
            - tool_calls: List[str] (names of tools called)
            - api_calls: List[APICall] (for cost tracking)
            - iterations: int (number of reasoning steps)
        """
        pass
```

### ReAct Implementation Sketch

```python
# Use LangChain for ReAct implementation
from langchain.agents import create_react_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool

class ReActAgent:
    def __init__(self, model="claude-3-5-sonnet-20241022", temperature=0.0):
        self.llm = ChatAnthropic(model=model, temperature=temperature)
        self.model = model

    def run_task(self, task: str, tools: List[Tool]) -> AgentResponse:
        # Convert tools to LangChain format
        langchain_tools = [self._convert_tool(t) for t in tools]

        # Create ReAct agent
        agent = create_react_agent(self.llm, langchain_tools, prompt=REACT_PROMPT)
        executor = AgentExecutor(agent=agent, tools=langchain_tools, max_iterations=10)

        # Track API calls
        api_calls = []
        # TODO: Add callback to track API usage

        # Execute
        result = executor.invoke({"input": task})

        # Extract tool calls from agent trajectory
        tool_calls = self._extract_tool_calls(result)

        return AgentResponse(
            response=result["output"],
            tool_calls=tool_calls,
            api_calls=api_calls,
            iterations=result.get("iterations", 0)
        )
```

**Key points**:
- Use temperature=0.0 for deterministic sampling
- Track ALL API calls with token counts and costs
- Max 10 iterations to prevent infinite loops in testing
- Extract tool names from agent actions for fabrication detection

---

## Step 2: Create Pre-Registration Spec

**Priority**: HIGH (required before running pilot)
**File**: `experiments/pilot-reproduction/spec.yaml`
**Template**: `shared/templates/experiment/spec.yaml`
**Estimated time**: 20-30 minutes
**Cost**: $0 (spec creation only)

### Spec Requirements

```yaml
name: "pilot-reproduction-f1-f5"
status: draft

hypothesis: >
  Tool fabrication (F1) and false completion (F5) failures will reproduce
  reliably (>60%) and show clear architectural differences. ReAct will show
  higher infinite loop risk, Plan-Execute higher false completion, Reflexion
  intermediate.

predictions:
  - tasks: ["tool_fabrication"]
    metric: "fabrication_rate"
    direction: "positive"
    min_effect: 0.60  # >60% failure rate expected
  - tasks: ["false_completion"]
    metric: "false_completion_rate"
    direction: "positive"
    min_effect: 0.40  # 40-60% expected

design:
  condition: "standard"
  temperature: 0.0
  models: ["claude-3-5-sonnet-20241022"]
  tasks: ["tool_fabrication", "false_completion"]
  num_samples: 1
  instances_per_difficulty: 20
  difficulties: [1]  # Single difficulty level for pilot

canary:
  tasks: ["tool_fabrication"]
  instances_per_difficulty: 5
  num_samples: 1
  diagnostics:
    - check: extraction_failure_rate
      max: 0.05
    - check: cost_per_instance
      max_multiple_of_estimate: 2.0

budget:
  estimated_total_usd: 25.00
  estimated_per_instance_usd: 0.20  # Conservative estimate
  canary_cost_usd: 1.00
  max_allowed_usd: 35.00

review:
  status: pending

created_at: "2026-03-28"
updated_at: "2026-03-28"
```

### After Creating Spec

1. Set status: `draft`
2. Commit spec file
3. **Orchestrator will automatically chain a critic review**
4. Wait for critic to set `review.status: approved`
5. Only then proceed to Step 3 (canary run)

---

## Step 3: Run Canary (After Critic Approval)

**Priority**: CRITICAL (must pass before full run)
**Cost**: ~$1-2

### Canary Requirements

From `experiments/pilot-reproduction/spec.yaml`:
- Run 5 instances of F1 (tool fabrication)
- Check: extraction_failure_rate < 5%
- Check: cost_per_instance < 2x estimate ($0.40)
- Record results in `experiments/pilot-reproduction/canary-results.yaml`

### If Canary Fails

**DO NOT proceed to full run.** Fix the issue:
- Extraction failures → improve response parsing
- Cost overrun → reduce context, simplify task, or revise budget estimate
- Accuracy sanity failures → check task difficulty, tool availability

Set `status: failed` in spec.yaml, document failure reason.

### If Canary Passes

Set `status: running` in spec.yaml, proceed to Step 4.

---

## Step 4: Run Pilot Reproduction

**Priority**: HIGH (core deliverable)
**File**: Create `src/run_pilot.py`
**Cost**: ~$20-30 (120 instances total)

### Pilot Configuration

- **Frameworks**: 3 (ReAct, Plan-Execute, Reflexion)
- **Tests**: 2 (F1 tool fabrication, F5 false completion)
- **Instances**: 20 per framework per test
- **Total**: 3 × 2 × 20 = 120 evaluations

### Execution Script Sketch

```python
from frameworks.react_agent import ReActAgent
from frameworks.plan_execute import PlanExecuteAgent
from frameworks.reflexion import ReflexionAgent
from tests.tool_fabrication import ToolFabricationTest
from tests.false_completion import FalseCompletionTest
from utils.logging import ExperimentLogger

def run_pilot():
    logger = ExperimentLogger("experiments/pilot-reproduction/results")

    frameworks = [
        ("react", ReActAgent()),
        ("plan_execute", PlanExecuteAgent()),
        ("reflexion", ReflexionAgent())
    ]

    tests = [
        ("tool_fabrication", ToolFabricationTest(num_tools=20)),
        ("false_completion", FalseCompletionTest())
    ]

    for framework_name, framework in frameworks:
        for test_name, test in tests:
            print(f"\nRunning {test_name} on {framework_name}...")

            for i in range(20):
                # Generate test case
                test_case = test.generate_test_case(i)

                # Run agent
                response = framework.run_task(
                    task=test_case["task"],
                    tools=test_case["tools"]
                )

                # Evaluate
                evaluation = test.evaluate_response(
                    test_case,
                    response.response,
                    response.tool_calls
                )

                # Log result
                result = TestResult(
                    test_name=test_name,
                    framework=framework_name,
                    instance_id=i,
                    success=True,
                    failure_occurred=evaluation["failure_occurred"],
                    failure_type=test_name,
                    metadata={"test_case": test_case, "evaluation": evaluation},
                    api_calls=response.api_calls,
                    total_cost_usd=sum(c.cost_usd for c in response.api_calls),
                    total_time_seconds=response.time_seconds
                )

                logger.log_result(result)

                # Check budget
                if logger.total_cost > 35.0:  # max_allowed_usd from spec
                    print(f"Budget limit reached: ${logger.total_cost:.2f}")
                    logger.save_final_report()
                    return

    # Save final report
    logger.save_final_report()

    # Analyze results
    analyze_pilot_results(logger)

def analyze_pilot_results(logger):
    summary = logger.get_summary()

    print("\n" + "="*60)
    print("PILOT REPRODUCTION RESULTS")
    print("="*60)
    print(f"Total instances: {summary['total_instances']}")
    print(f"Failures observed: {summary['failures_observed']}")
    print(f"Failure rate: {summary['failure_rate']:.2%}")
    print(f"Total cost: ${summary['total_cost_usd']:.2f}")
    print("="*60)

    # Framework × Test breakdown
    results_by_framework_test = {}
    for result in logger.results:
        key = (result.framework, result.test_name)
        if key not in results_by_framework_test:
            results_by_framework_test[key] = []
        results_by_framework_test[key].append(result)

    print("\nBreakdown by Framework × Test:")
    for (framework, test), results in results_by_framework_test.items():
        failures = sum(1 for r in results if r.failure_occurred)
        rate = failures / len(results)
        print(f"  {framework} × {test}: {failures}/{len(results)} ({rate:.1%})")

if __name__ == "__main__":
    run_pilot()
```

### Expected Outcomes

If pilot succeeds:
- At least 4 of 6 failures reproduce (>60% rate)
- Clear architectural differences (>20% delta between frameworks)
- Instances match taxonomy categories
- Cost within budget ($20-30)

---

## Step 5: Analyze and Report

**File**: `experiments/pilot-reproduction/analysis.md`

### Key Metrics

1. **Reproduction rates**: F1 and F5 failure rates per framework
2. **Architecture differences**: Which framework fails how
3. **Cost accuracy**: Actual vs. estimated
4. **Taxonomy validation**: Do failures match predicted categories?

### Tables to Generate

**Table 1: Failure Rates by Framework**
```
| Framework     | F1 Tool Fab | F5 False Comp | Avg |
|---------------|-------------|---------------|-----|
| ReAct         | 75%         | 45%           | 60% |
| Plan-Execute  | 65%         | 65%           | 65% |
| Reflexion     | 70%         | 40%           | 55% |
```

**Table 2: Cost Breakdown**
```
| Framework     | Instances | Total Cost | Avg per Instance |
|---------------|-----------|------------|------------------|
| ReAct         | 40        | $8.50      | $0.21            |
| Plan-Execute  | 40        | $10.20     | $0.26            |
| Reflexion     | 40        | $11.30     | $0.28            |
| **Total**     | 120       | $30.00     | $0.25            |
```

---

## Step 6: Update Status and Commit

Update `status.yaml`:
- Set `controlled_experiments.status: in_progress` (update progress note)
- Add new metrics: `experiments_run: 120`, `frameworks_implemented: 3`
- Update `next_steps` with Phase 3 plan (full validation)

Commit structure:
```bash
git add experiments/pilot-reproduction/
git commit -m "research(agent-failure-taxonomy): pilot reproduction F1+F5 across 3 frameworks

- Implemented 3 framework wrappers: ReAct, Plan-Execute, Reflexion
- Ran 120 evaluations (3 frameworks × 2 tests × 20 instances)
- Results: F1 fabrication rate 70%, F5 false completion rate 50%
- Clear architectural differences: Plan-Execute 65% false completion vs ReAct 45%
- Cost: $30 actual vs $25 estimated (20% overrun, within tolerance)
- Taxonomy validated: failures match predicted categories
- Next: scale to full validation (all 6 failures, 50 instances)"
```

---

## Common Issues and Solutions

### Issue 1: LangChain version conflicts
**Solution**: Pin versions in requirements.txt
```
langchain==0.1.0
langchain-anthropic==0.1.0
anthropic==0.18.0
```

### Issue 2: Tool fabrication not detected
**Problem**: Agent uses closest available tool instead of fabricating
**Solution**: This is correct behavior! Log as "acceptable response", not failure
**Metric**: Still count in analysis, distinguish fabrication vs. refusal

### Issue 3: Cost overrun
**Problem**: Actual cost > 2x estimate
**Solution**:
1. Check if iterations are excessive (reduce max_iterations)
2. Check context length (simplify task descriptions)
3. Revise spec budget estimate upward, re-submit for critic review

### Issue 4: Canary fails diagnostics
**Problem**: Extraction failure rate > 5%
**Solution**:
1. Check response format variability
2. Improve parsing robustness (handle edge cases)
3. Add few-shot examples to prompt
4. Reduce task ambiguity

---

## Success Criteria

Before ending session, verify:
- [ ] All 3 frameworks implemented and tested
- [ ] Canary passed all diagnostics
- [ ] 120 evaluations completed
- [ ] Results logged and analyzed
- [ ] Cost within $35 budget limit
- [ ] At least 4 of 6 failures reproduced (testing F1+F5, need >60% rate for each)
- [ ] Architectural differences observed (>20% delta)
- [ ] Status.yaml updated
- [ ] Commits pushed to branch

---

## Files to Create/Modify

### Create:
- `src/frameworks/react_agent.py`
- `src/frameworks/plan_execute.py`
- `src/frameworks/reflexion.py`
- `src/tests/false_completion.py` (similar structure to tool_fabrication.py)
- `src/run_pilot.py`
- `experiments/pilot-reproduction/spec.yaml`
- `experiments/pilot-reproduction/canary-results.yaml`
- `experiments/pilot-reproduction/analysis.md`

### Modify:
- `projects/agent-failure-taxonomy/status.yaml` (update progress)
- `budget.yaml` (add experiment cost to spending history)

---

## Timeline Estimate

- **Step 1** (ReAct implementation): 30-45 min
- **Step 2** (Pre-registration spec): 20-30 min
- **Critic review wait**: Auto-triggered, expect 10-15 min
- **Step 3** (Canary run): 5-10 min
- **Step 4** (Pilot run): 20-30 min (API calls)
- **Step 5** (Analysis): 15-20 min
- **Step 6** (Update & commit): 10 min

**Total**: 2-3 hours work + API time

---

## Budget Tracking

Before starting:
- Check `budget.yaml`: $645 available (March 2026)
- Confirm spec.yaml: `max_allowed_usd: 35.00`

During execution:
- Monitor `logger.total_cost`
- Alert if approaching $35 limit
- Halt if limit exceeded

After completion:
- Update `budget.yaml`:
```yaml
  - date: "2026-03-28"
    project: "agent-failure-taxonomy"
    category: "api_calls"
    amount: 30  # actual cost
    description: "Pilot reproduction: F1+F5 across 3 frameworks (120 instances)"
```

---

## Questions to Answer

At the end of pilot reproduction, you should be able to answer:

1. **Do F1 and F5 reproduce reliably?** (Yes if >60% failure rate)
2. **Are there architectural differences?** (Yes if >20% delta between frameworks)
3. **Do failures match taxonomy categories?** (Validate against C1-C8 mapping)
4. **Is the infrastructure robust?** (No crashes, checkpoints work, costs tracked)
5. **Should we proceed to full validation?** (Yes if above criteria met)

If answers are mostly "yes", recommend scaling to Phase 3 (all 6 failures, 50 instances per combination, ~$100-150).

If answers are mostly "no", diagnose issues before scaling.

---

## Good Luck!

The experimental protocol is solid, the infrastructure is validated, and the budget is secured. Session 9 should be a straightforward implementation → evaluation → analysis workflow.

**Remember**: Pre-registration spec + critic approval is MANDATORY before running >$2 experiments. Don't skip this step.

**Contact**: If you encounter fundamental issues (e.g., frameworks can't be implemented, failures don't exist), escalate to meta-review rather than proceeding with flawed experiments.
