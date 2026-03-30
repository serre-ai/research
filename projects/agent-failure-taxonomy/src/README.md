# Agent Failure Taxonomy - Experimental Infrastructure

This directory contains the infrastructure for controlled experiments validating the agent failure taxonomy.

## Structure

```
src/
├── frameworks/          # Agent framework wrappers
│   ├── base.py         # Abstract base classes (BaseAgent, AgentStep, AgentResult, Tool)
│   ├── react.py        # ReAct implementation
│   └── autogpt.py      # AutoGPT wrapper (TODO)
├── tasks/              # Task generators for failure modes
│   ├── tool_fabrication.py    # Category 1.1: Tool fabrication
│   ├── infinite_loop.py       # Category 3.1: Infinite loops (TODO)
│   └── false_completion.py    # Category 5.1: False completion (TODO)
├── evaluation/         # Failure detection scripts
│   ├── detect_fabrication.py # Detect tool fabrication (TODO)
│   ├── detect_loop.py         # Detect infinite loops (TODO)
│   └── verify_completion.py   # Verify task completion (TODO)
└── utils/
    ├── logging.py      # Experiment logging and checkpointing
    └── metrics.py      # Analysis utilities (TODO)
```

## Usage

### 1. Create an Agent

```python
from frameworks.react import create_react_agent

agent = create_react_agent(
    model="claude-haiku-4-5-20251001",
    temperature=1.0,
    max_steps=50,
    verbose=True
)
```

### 2. Generate Tasks

```python
from tasks.tool_fabrication import generate_tool_fabrication_dataset

tasks = generate_tool_fabrication_dataset(
    num_instances=10,
    variant="explicit_request",  # or None for mixed variants
    seed=42
)
```

### 3. Run Experiment

```python
from utils.logging import ExperimentLogger

logger = ExperimentLogger(experiment_name="pilot")

for task in tasks:
    result = agent.run(
        task_description=task["task_description"],
        tools=task["tools"],
        task_id=task["task_id"]
    )

    logger.log_execution(result.to_dict())
    logger.log_cost(result.task_id, result.total_cost, result.total_tokens)
```

### 4. Analyze Results

```python
# Get summary statistics
summary = logger.summary()
print(f"Total cost: ${summary['total_cost_usd']:.2f}")
print(f"Success rate: {summary['success_rate']}")

# Check total cost before continuing
if logger.get_total_cost() > max_budget:
    print("Budget exceeded!")
    break
```

## Task Variants

### Tool Fabrication (Category 1.1)

Tests whether agents fabricate non-existent tools.

**Variants:**
1. `explicit_request`: Directly asks for non-existent tool
2. `implicit_request`: Task requires unavailable capability
3. `large_tool_set`: 50+ tools to exceed working memory
4. `small_tool_set`: 10 tools, clear gap (control)
5. `similar_names`: Tools with confusable names

**Expected failures:**
- Agent attempts to call fabricated tool
- Agent doesn't recognize tool is missing
- Agent blends similar tool names

**Ground truth:**
- Tool exists/doesn't exist (boolean)
- Expected tool selection behavior

### Infinite Loop (Category 3.1) - TODO

Tests whether agents detect stagnation and circular dependencies.

**Variants:**
1. Circular dependency (edit A based on B, edit B based on A)
2. Unsolvable task (find largest prime)
3. Ambiguous completion criteria
4. External blocker (wait for unavailable input)
5. State thrashing (contradictory goals)

**Expected failures:**
- Agent repeats same actions without progress
- No stagnation detection
- Iteration count exceeds threshold

**Ground truth:**
- Task is circular/unsolvable
- Progress is impossible

### False Completion (Category 5.1) - TODO

Tests whether agents accurately verify task completion.

**Variants:**
1. File creation with verification
2. Calculation with known answer
3. Multi-step task with all steps required
4. Constraint satisfaction (exact word count)
5. Retrieval with ground truth

**Expected failures:**
- Agent claims completion without meeting criteria
- Premature completion before all steps
- False positive in self-verification

**Ground truth:**
- Objective completion criteria
- Actual vs. claimed completion

## Implementation Status

**Completed (Session 8):**
- [x] Base agent interface
- [x] ReAct framework wrapper (with mock LLM calls)
- [x] Tool fabrication task generator (5 variants)
- [x] Experiment logger with checkpointing
- [x] Cost estimation utilities

**Next Session (Session 9):**
- [ ] Infinite loop task generator
- [ ] False completion task generator
- [ ] AutoGPT framework wrapper
- [ ] Evaluation scripts (fabrication detection, loop detection, completion verification)
- [ ] Actual LLM API integration (replace mocks)
- [ ] Unit tests

**Future:**
- [ ] Additional frameworks (Reflexion, plan-then-execute)
- [ ] Additional failure types (context degradation, state divergence, etc.)
- [ ] Visualization tools
- [ ] Statistical analysis scripts

## Design Principles

1. **Reproducibility**: All tasks use deterministic seeding
2. **Crash recovery**: Checkpointing allows resuming interrupted experiments
3. **Cost tracking**: Every execution logs cost to prevent budget overruns
4. **Framework independence**: Same tasks run on different frameworks
5. **Clear ground truth**: Every task has objective success criteria

## Notes

- Current ReAct implementation uses mock LLM calls for testing infrastructure
- Full implementation will integrate actual LLM APIs (Anthropic, OpenAI)
- Tool execution is currently mocked; real tools will be implemented as needed
- Each framework should produce standardized AgentResult format for consistent analysis
