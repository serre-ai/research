# Agent Failure Taxonomy - Experimental Infrastructure

This directory contains the infrastructure for reproducing agent failures in controlled settings.

## Directory Structure

```
src/
├── tasks/              # Task generators for each failure type
│   ├── base.py        # Base task generator interface
│   ├── tool_fabrication.py
│   ├── infinite_loop.py
│   └── false_completion.py
├── frameworks/         # Agent framework wrappers
│   ├── base.py        # Base agent interface
│   ├── react_wrapper.py
│   ├── plan_execute_wrapper.py
│   └── autonomous_loop_wrapper.py
├── eval/              # Evaluation and analysis
│   ├── ground_truth.py   # Automated verification
│   ├── metrics.py        # Statistical analysis
│   └── analysis.py       # Figure generation
└── utils/             # Shared utilities
    ├── logger.py         # Structured logging
    ├── checkpoint.py     # State persistence
    └── cost_tracker.py   # API cost tracking
```

## Design Principles

1. **Deterministic**: Same seed produces same task instance
2. **Reproducible**: Full agent traces logged for manual inspection
3. **Crash-resistant**: Checkpointing allows resume after interruption
4. **Cost-aware**: Track and limit API spending in real-time
5. **Modular**: Easy to add new failure types and frameworks

## Task Generator Interface

```python
class TaskGenerator(ABC):
    """Base class for generating tasks that test specific failure modes."""

    @abstractmethod
    def generate(self, instance_id: int, seed: int) -> Task:
        """Generate a task instance.

        Args:
            instance_id: Unique identifier for this instance
            seed: Random seed for deterministic generation

        Returns:
            Task object with:
                - description: Natural language task description
                - ground_truth: Expected correct behavior
                - verification_fn: Function to check if agent succeeded
                - metadata: Additional context
        """
        pass
```

## Agent Wrapper Interface

```python
class AgentWrapper(ABC):
    """Base class for agent framework wrappers."""

    @abstractmethod
    def run(self, task: Task, max_iterations: int = 20) -> AgentTrace:
        """Execute agent on task.

        Args:
            task: Task to execute
            max_iterations: Maximum iterations before timeout

        Returns:
            AgentTrace with:
                - actions: List of (action, observation) tuples
                - final_answer: Agent's claimed result
                - metadata: Framework-specific info
                - cost: API cost in USD
        """
        pass
```

## Evaluation Pipeline

```python
# Example usage
from src.tasks.tool_fabrication import ToolFabricationTask
from src.frameworks.react_wrapper import ReactAgent
from src.eval.ground_truth import verify_no_fabrication

# Generate task
task_gen = ToolFabricationTask(num_tools=25, num_decoys=5)
task = task_gen.generate(instance_id=1, seed=42)

# Run agent
agent = ReactAgent(model="gpt-4o-mini", temperature=0.0)
trace = agent.run(task, max_iterations=20)

# Evaluate
result = verify_no_fabrication(trace, task.ground_truth)
# result.success: bool
# result.failure_type: str | None
# result.details: dict
```

## Cost Tracking

All API calls are logged with cost estimates:

```python
# Automatic tracking in agent wrappers
trace = agent.run(task)
print(f"Cost: ${trace.cost:.4f}")

# Session-level tracking
from src.utils.cost_tracker import CostTracker
tracker = CostTracker(max_budget_usd=2.50)
tracker.record(trace.cost)
if tracker.is_over_budget():
    raise BudgetExceededError()
```

## Checkpointing

Experiments can be resumed after crashes:

```python
from src.utils.checkpoint import CheckpointManager

checkpoint = CheckpointManager("experiments/pilot/checkpoints")

for instance_id in range(180):
    if checkpoint.is_completed(instance_id):
        continue  # Skip already completed

    result = run_instance(instance_id)
    checkpoint.save(instance_id, result)
```

## Next Steps

1. Implement base classes (`base.py` files)
2. Implement task generators for 3 failure types
3. Implement 3 framework wrappers
4. Add evaluation and analysis tools
5. Run canary experiment
