# Agent Failure Taxonomy: Experiment Infrastructure

**Status**: Under development (Session 8, 2026-03-29)
**Purpose**: Controlled experiments to validate agent failure taxonomy

---

## Directory Structure

```
src/
├── frameworks/          # Agent framework wrappers
│   ├── __init__.py      # Abstract AgentFramework base class
│   ├── langgraph_wrapper.py        # LangGraph (ReAct pattern) [TODO]
│   ├── react_wrapper.py            # Direct ReAct implementation [TODO]
│   └── mcp_wrapper.py              # Anthropic MCP [TODO]
│
├── tasks/               # Task generators for each failure mode
│   ├── tool_fabrication.py         # Tool count scaling (Category 1.1) ✓
│   ├── infinite_loops.py           # Progress monitoring (Category 3.1) [TODO]
│   ├── false_completion.py         # Verification failures (Category 5.1) [TODO]
│   ├── context_degradation.py      # Long-context failures (Category 4.3) [TODO]
│   ├── tool_hallucination.py       # Execution hallucination (Category 1.2) [TODO]
│   └── state_divergence.py         # State tracking (Category 4.1) [TODO]
│
├── evaluation/          # Metric calculators and ground truth verification
│   ├── metrics.py                  # Per-failure metric functions [TODO]
│   ├── ground_truth.py             # Answer verification [TODO]
│   └── trajectory_parser.py        # Extract actions from logs [TODO]
│
├── runners/             # Experiment orchestration
│   ├── single_instance.py          # Run one instance [TODO]
│   ├── canary.py                   # Canary run with diagnostics [TODO]
│   └── full_experiment.py          # Full run with checkpointing [TODO]
│
└── utils/               # Core utilities
    ├── logging.py                   # Structured JSONL logging ✓
    ├── cost_tracking.py             # API cost monitoring ✓
    └── checkpointing.py             # Crash recovery ✓
```

---

## Core Utilities (Completed)

### `utils/logging.py`
- **`ExperimentLogger`**: Structured JSONL logging for all experiment runs
- Logs instance results, canary diagnostics, experiment start/complete events
- Human-readable console output with status emojis
- Load and filter logs programmatically for analysis

### `utils/cost_tracking.py`
- **`CostTracker`**: Monitors API costs and enforces budget limits
- Pricing for GPT-4o-mini, GPT-4o, Claude 3.5 Sonnet/Haiku (2026 rates)
- Raises exception if budget limit exceeded (fail-fast)
- Summary stats: cumulative cost, call count, budget remaining

### `utils/checkpointing.py`
- **`CheckpointManager`**: Save/resume experiment progress
- Crash recovery: mark instances complete, get remaining instances
- Progress tracking: completed, remaining, progress_pct
- Reset functionality for re-runs

---

## Framework Interface

All framework wrappers implement `AgentFramework` abstract base class:

```python
class AgentFramework(ABC):
    def run(
        self,
        task_description: str,
        tools: List[Dict[str, Any]],
        initial_observation: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run agent on task. Returns trajectory, final_answer, completion_status."""
        pass
```

**Planned frameworks**:
1. **LangGraph** — ReAct pattern (GPT-4o-mini backend)
2. **ReAct Direct** — Plan-then-execute variant (GPT-4o-mini backend)
3. **Anthropic MCP** — Direct tool use (Claude 3.5 Sonnet backend)

---

## Task Generators

Each task generator creates instances with:
- **Deterministic generation**: Seed-based for reproducibility
- **Ground truth**: Programmatically verifiable correct answers
- **Evaluation function**: Compute failure-specific metrics

### Example: `tool_fabrication.py` (Completed)

```python
generator = ToolFabricationTask(num_tools=20, seed=42)
task_desc, tools, correct_tool, ground_truth = generator.generate_instance(instance_id=0)

# After running agent:
metrics = generator.evaluate_response(trajectory, ground_truth)
# → fabrication_rate, used_correct_tool, num_fabricated_calls
```

**Tool Fabrication Test**:
- Varies tool count: N = 5, 10, 20, 40
- Tests whether agents fabricate non-existent tool names
- Expected: Fabrication rate scales with tool count (C6 limitation)

---

## Next Steps (Priority Order)

### Phase 1: Framework Wrappers (1 session)
1. Implement `langgraph_wrapper.py` (LangGraph + OpenAI)
2. Implement `react_wrapper.py` (custom ReAct with function calling)
3. Implement `mcp_wrapper.py` (Anthropic SDK with tools)

### Phase 2: Task Generators (1 session)
1. Implement `infinite_loops.py` (ambiguous task loop detection)
2. Implement remaining task generators as needed for canary

### Phase 3: Runners (1 session)
1. Implement `single_instance.py` (run one instance, log result)
2. Implement `canary.py` (run canary suite, check diagnostics)
3. Implement `full_experiment.py` (full run with checkpointing)

### Phase 4: Canary Run (1 session)
1. Run canary with tool_fabrication + infinite_loops
2. Validate all diagnostics pass
3. Debug issues, refine protocol

---

## Dependencies

Required Python packages (add to `requirements.txt`):

```txt
# LLM APIs
openai>=1.0.0
anthropic>=0.20.0

# Agent frameworks
langgraph>=0.1.0
langchain>=0.1.0
langchain-openai>=0.1.0

# Data processing
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# Utilities
pyyaml>=6.0
pytest>=7.4.0
```

---

## Usage Example (Future)

```python
from src.frameworks.langgraph_wrapper import LangGraphAgent
from src.tasks.tool_fabrication import ToolFabricationTask
from src.utils.logging import ExperimentLogger
from src.utils.cost_tracking import CostTracker

# Initialize
logger = ExperimentLogger("pilot-validation", output_dir="experiments/pilot-validation/logs")
cost_tracker = CostTracker(budget_limit_usd=50.0)

# Create framework and task
agent = LangGraphAgent(model="gpt-4o-mini-2024-07-18", temperature=0.0, max_iterations=10)
task = ToolFabricationTask(num_tools=20, seed=42)

# Generate instance
task_desc, tools, correct_tool, ground_truth = task.generate_instance(instance_id=0)

# Run agent
result = agent.run(task_description=task_desc, tools=tools)

# Track cost
cost = cost_tracker.add_call(
    model=agent.model,
    input_tokens=result["token_counts"]["input"],
    output_tokens=result["token_counts"]["output"],
)

# Evaluate
metrics = task.evaluate_response(result["trajectory"], ground_truth)

# Log
logger.log_instance(
    instance_id="tool_fab_n20_i0",
    framework="langgraph",
    task_type="tool_fabrication_n20",
    ground_truth=ground_truth,
    agent_trajectory=result["trajectory"],
    completion_status=result["completion_status"],
    failure_detected=metrics["fabrication_rate"] > 0,
    failure_type="tool_fabrication" if metrics["fabrication_rate"] > 0 else None,
    cost_usd=cost,
    latency_seconds=result.get("latency_seconds", 0),
    token_counts=result["token_counts"],
)
```

---

## Testing

Run unit tests with:
```bash
pytest src/ -v
```

Test coverage should include:
- Cost tracking accuracy
- Checkpoint save/load
- Log parsing
- Task instance generation (deterministic seeds)
- Ground truth verification

---

## Status Summary

**Completed** (Session 8):
- ✅ Core utilities (logging, cost tracking, checkpointing)
- ✅ Framework interface (abstract base class)
- ✅ Tool fabrication task generator

**In Progress**:
- 🔄 Framework wrappers (0/3 implemented)

**TODO**:
- ⏳ Remaining task generators (5 failures)
- ⏳ Evaluation metrics
- ⏳ Experiment runners
- ⏳ Unit tests

**Estimated Completion**: 3-4 more sessions (15-20 hours)
