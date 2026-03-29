# Agent Failure Taxonomy Experiment Infrastructure

This directory contains the implementation infrastructure for controlled agent failure experiments.

## Structure

```
src/
├── frameworks/           # Agent framework wrappers
│   ├── base.py          # Abstract base class for all frameworks
│   ├── langgraph_react.py
│   ├── langgraph_plan_execute.py
│   ├── langgraph_reflexion.py
│   └── autogpt_simplified.py
├── tasks/               # Task generators for each failure type
│   ├── base.py         # Abstract task generator
│   ├── tool_fabrication.py
│   ├── infinite_loops.py
│   ├── context_degradation.py
│   ├── self_correction.py
│   ├── false_completion.py
│   └── cascading_errors.py
├── logging/            # Logging and checkpoint utilities
│   ├── logger.py       # Structured logging
│   └── checkpoint.py   # Crash recovery checkpoints
├── analysis/           # Statistical analysis and visualization
│   ├── stats.py        # Statistical tests
│   └── viz.py          # Publication-ready figures
└── utils/              # Shared utilities
    ├── cost_tracker.py # API cost tracking
    └── validators.py   # Output validation

```

## Installation

```bash
cd projects/agent-failure-taxonomy
pip install -r requirements.txt
```

## Usage

### Running an Experiment

```python
from src.frameworks.langgraph_react import LangGraphReact
from src.tasks.tool_fabrication import ToolFabricationTask
from src.logging.logger import ExperimentLogger

# Initialize
framework = LangGraphReact(model="gpt-4o", temperature=0.0)
task_gen = ToolFabricationTask(tool_count=30)
logger = ExperimentLogger(experiment_name="tool_fabrication")

# Generate task
task = task_gen.generate(instance_id=1)

# Run agent
result = framework.run(task)

# Log results
logger.log_run(
    run_id=result.run_id,
    framework="langgraph-react",
    task=task,
    result=result,
    failure_detected=result.tool_fabrication_detected
)
```

### Running a Batch Experiment

```python
from src.utils.batch_runner import BatchRunner

runner = BatchRunner(
    experiment_spec="experiments/tool-fabrication/spec.yaml",
    checkpoint_dir="experiments/tool-fabrication/checkpoints"
)

# Run canary
canary_results = runner.run_canary()

# If canary passes, run full experiment
if canary_results.all_diagnostics_passed:
    full_results = runner.run_full()
```

## Design Principles

1. **Modular**: Each component (framework, task, logging) is independent
2. **Reproducible**: Deterministic task generation with seeds
3. **Resumable**: Checkpoint every 10 runs for crash recovery
4. **Cost-tracked**: Every API call logged with cost
5. **Validated**: Automatic output validation and failure detection

## Testing

```bash
pytest src/tests/
```

## License

MIT
