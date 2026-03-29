# Next Session: Implement Framework Wrappers

**Date Created**: 2026-03-29 (end of Session 8)
**For**: Session 9 (Experimenter agent)
**Priority**: HIGH — Blocking canary run

---

## Session 8 Completion Status

✅ **Experimental protocol designed** (notes/06-experimental-protocol-design.md)
✅ **Pre-registration spec created** (experiments/pilot-validation/spec.yaml)
✅ **Core infrastructure built** (src/utils/: logging, cost tracking, checkpointing)
✅ **Framework interface defined** (src/frameworks/__init__.py: AgentFramework ABC)
✅ **Tool fabrication task complete** (src/tasks/tool_fabrication.py)
✅ **Status.yaml updated** with decisions and metrics

---

## Critical Path for Session 9

The **blocking work** to run the canary experiment is:

### 1. Framework Wrappers (HIGHEST PRIORITY)
**Directory**: `src/frameworks/`

Need to implement 3 wrappers, each implementing `AgentFramework.run()`:

#### a. LangGraph Wrapper
**File**: `src/frameworks/langgraph_wrapper.py`
- **Architecture**: ReAct pattern (Observation-Reasoning-Action loop)
- **Backend**: OpenAI GPT-4o-mini-2024-07-18
- **Dependencies**: `langgraph`, `langchain`, `langchain-openai`
- **Key Features**:
  - State management with graph nodes
  - Tool integration via LangChain LCEL
  - Iteration limit enforcement (max_iterations=10)
  - Token counting for cost tracking
  - Trajectory logging (observation, reasoning, action, result per step)

**Implementation Notes**:
- Use LangGraph's `StateGraph` for agent loop
- Define state schema: `{"messages": [], "tools": [], "iterations": 0}`
- Use `ToolNode` for tool execution
- Capture full trajectory for evaluation

#### b. ReAct Direct Wrapper
**File**: `src/frameworks/react_wrapper.py`
- **Architecture**: Plan-then-execute variant (explicit planning phase before execution)
- **Backend**: OpenAI GPT-4o-mini-2024-07-18
- **Dependencies**: `openai` (function calling)
- **Key Features**:
  - Two-phase execution: (1) Plan generation, (2) Plan execution
  - OpenAI function calling for tools
  - Explicit completion criteria
  - State verification between phases

**Implementation Notes**:
- Phase 1: Generate high-level plan with `system` prompt
- Phase 2: Execute plan with function calling
- Track state after each action
- Capture planning phase in trajectory

#### c. Anthropic MCP Wrapper
**File**: `src/frameworks/mcp_wrapper.py`
- **Architecture**: Direct tool use (no intermediate reasoning steps)
- **Backend**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Dependencies**: `anthropic`
- **Key Features**:
  - Direct tool calling via Anthropic SDK
  - Single-turn or multi-turn tool use
  - Streaming response handling
  - Token counting from API response

**Implementation Notes**:
- Use `anthropic.tools` API for tool definitions
- Handle tool use responses in loop
- No explicit ReAct observation-reasoning-action pattern
- Simpler than ReAct but still needs iteration control

---

### 2. Task Generators (MEDIUM PRIORITY)
**Directory**: `src/tasks/`

Need **minimum 2 additional tasks** for canary run:

#### a. Infinite Loops Task
**File**: `src/tasks/infinite_loops.py`
- **Category**: 3.1 Planning Failures → Progress Monitoring
- **Test Design**: Provide ambiguous or impossible task, measure loop detection
- **Metrics**: iteration_count, action_repetition_rate, timeout_occurred
- **Ground Truth**: Task is impossible/ambiguous → should timeout or ask for clarification

#### b. False Completion Task
**File**: `src/tasks/false_completion.py`
- **Category**: 5.1 Self-Correction Failures → Verification
- **Test Design**: Multi-step task with objective completion criteria
- **Metrics**: false_positive_rate (reports complete when not), false_negative_rate
- **Ground Truth**: All steps must be completed in order

**Note**: Defer context_degradation, tool_hallucination, state_divergence to post-canary. Canary only needs 3 tasks.

---

### 3. Experiment Runners (MEDIUM PRIORITY)
**Directory**: `src/runners/`

#### a. Single Instance Runner
**File**: `src/runners/single_instance.py`
- **Purpose**: Run one task instance on one framework, log result
- **Inputs**: framework, task_generator, instance_id, ground_truth
- **Outputs**: Trajectory, metrics, cost
- **Uses**: ExperimentLogger, CostTracker

#### b. Canary Runner
**File**: `src/runners/canary.py`
- **Purpose**: Run canary suite (5 instances × 3 tasks × 3 frameworks)
- **Checks**: All 7 diagnostics from spec.yaml
- **Outputs**: Pass/fail per diagnostic, canary-results.yaml
- **Critical**: STOP if any diagnostic fails

---

## Implementation Order (Recommended)

1. **LangGraph Wrapper** (Start here — most documentation available)
2. **Infinite Loops Task** (Simple task, good test case)
3. **Single Instance Runner** (Needed to test wrappers)
4. **ReAct Direct Wrapper** (Custom implementation, moderate complexity)
5. **False Completion Task** (More complex task)
6. **Anthropic MCP Wrapper** (Different API, defer if time limited)
7. **Canary Runner** (Orchestrates everything)

---

## Testing Strategy

For each component, **test immediately** after implementation:

### Testing Framework Wrappers
```python
from src.frameworks.langgraph_wrapper import LangGraphAgent
from src.tasks.tool_fabrication import ToolFabricationTask

# Create simple test
agent = LangGraphAgent(model="gpt-4o-mini-2024-07-18", temperature=0.0)
task = ToolFabricationTask(num_tools=5, seed=42)
task_desc, tools, correct_tool, ground_truth = task.generate_instance(0)

# Run agent
result = agent.run(task_description=task_desc, tools=tools)

# Verify result structure
assert "trajectory" in result
assert "completion_status" in result
assert "token_counts" in result
print(f"Framework test passed: {len(result['trajectory'])} steps")
```

### Testing Task Generators
```python
from src.tasks.infinite_loops import InfiniteLoopsTask

task = InfiniteLoopsTask(seed=42)
task_desc, tools, correct_response, ground_truth = task.generate_instance(0)

# Verify determinism
task2 = InfiniteLoopsTask(seed=42)
task_desc2, _, _, _ = task2.generate_instance(0)
assert task_desc == task_desc2  # Same seed → same instance
print("Task determinism verified")
```

### Testing Single Instance Runner
```python
from src.runners.single_instance import run_single_instance

result = run_single_instance(
    framework_name="langgraph",
    task_type="tool_fabrication_n5",
    instance_id="test_0",
    seed=42,
    output_dir="experiments/test-runs"
)

# Verify log file created
assert Path("experiments/test-runs/test_0.json").exists()
print("Single instance runner test passed")
```

---

## Dependencies to Install

Add to `requirements.txt` or install directly:

```bash
pip install openai anthropic langgraph langchain langchain-openai pyyaml
```

**Specific versions** (as of 2026-03-29):
- `openai>=1.0.0`
- `anthropic>=0.20.0`
- `langgraph>=0.1.0`
- `langchain>=0.1.0`
- `langchain-openai>=0.1.0`
- `pyyaml>=6.0`

---

## Expected Session 9 Outcomes

**Minimum Viable** (to proceed to canary):
- ✅ 1 framework wrapper working (LangGraph recommended)
- ✅ 2 task generators (tool_fabrication ✓ + infinite_loops)
- ✅ Single instance runner functional
- ✅ Manual test: Run 1 instance successfully

**Ideal** (full canary ready):
- ✅ All 3 framework wrappers working
- ✅ 3 task generators (tool_fabrication ✓ + infinite_loops + false_completion)
- ✅ Single instance runner + canary runner functional
- ✅ Canary ready to run (just needs `python src/runners/canary.py`)

**Stretch** (bonus):
- Unit tests for wrappers and tasks
- Error handling and retry logic
- Logging validation
- Cost estimate verification

---

## Blockers and Risks

### Risk 1: LangGraph API Changes
**Mitigation**: Use latest documentation, check examples in LangGraph repo
**Fallback**: Implement custom ReAct loop without LangGraph (more work but feasible)

### Risk 2: Framework Wrappers More Complex Than Expected
**Mitigation**: Start with simplest (LangGraph has good docs), defer Anthropic if needed
**Fallback**: Run canary with 1-2 frameworks instead of 3

### Risk 3: Token Counting Inaccurate
**Mitigation**: Use API-returned token counts (more reliable than tiktoken estimates)
**Fallback**: Over-estimate costs, use conservative budget

### Risk 4: Time Constraint (80 turns, $5 budget)
**Mitigation**: Focus on LangGraph wrapper + infinite_loops task + single runner
**Fallback**: Defer full canary to Session 10, do manual testing in Session 9

---

## Quick Reference: Files to Read

**Before starting**:
1. `notes/06-experimental-protocol-design.md` — Understand experimental design
2. `experiments/pilot-validation/spec.yaml` — See exact requirements
3. `src/frameworks/__init__.py` — AgentFramework interface to implement
4. `src/README.md` — Infrastructure overview

**During implementation**:
- `src/utils/logging.py` — See ExperimentLogger usage
- `src/utils/cost_tracking.py` — See CostTracker usage
- `src/tasks/tool_fabrication.py` — Example task generator pattern

**For testing**:
- `experiments/pilot-validation/spec.yaml` → canary.diagnostics — What to check

---

## Success Criteria for Session 9

**Must Have**:
- [ ] At least 1 framework wrapper functional (LangGraph)
- [ ] At least 1 additional task generator (infinite_loops)
- [ ] Single instance runner works end-to-end
- [ ] Manual test passes (run 1 instance, get valid trajectory)

**Should Have**:
- [ ] All 3 framework wrappers functional
- [ ] 3 task generators total (tool_fabrication, infinite_loops, false_completion)
- [ ] Canary runner implemented
- [ ] Cost tracking verified accurate

**Nice to Have**:
- [ ] Unit tests for new components
- [ ] Error handling and retries
- [ ] Documentation updated (src/README.md)

---

## Estimated Time Breakdown

**LangGraph Wrapper**: 15-20 turns (most documentation available)
**ReAct Direct Wrapper**: 20-25 turns (custom implementation)
**Anthropic MCP Wrapper**: 15-20 turns (different API)
**Infinite Loops Task**: 10-15 turns (straightforward)
**False Completion Task**: 10-15 turns (moderate complexity)
**Single Instance Runner**: 10-15 turns (orchestration logic)
**Canary Runner**: 15-20 turns (diagnostics + reporting)

**Total Estimate**: 95-130 turns (but only need 50-60 for minimum viable)

**Session 9 Budget**: 80 turns, $5 API spend
**Recommended Focus**: LangGraph (20) + Infinite Loops (12) + Single Runner (15) + Testing (15) = **62 turns**

---

## End of Handoff

**Status**: Session 8 complete, infrastructure ready
**Next Agent**: Experimenter (Session 9)
**Blocking**: Framework wrappers (critical path)
**Estimated Sessions to Canary**: 1-2 sessions (depending on implementation complexity)
**Estimated Sessions to Full Pilot**: 3-4 sessions total

**Good luck with Session 9! The infrastructure is solid, now we just need the wrappers to bring it all together.**
