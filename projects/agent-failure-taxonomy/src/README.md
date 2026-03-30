# Agent Failure Taxonomy: Experimental Infrastructure

This directory contains the implementation for controlled experiments validating the agent failure taxonomy.

## Structure

```
src/
├── frameworks/          # Agent framework wrappers
│   ├── react_agent.py          # ReAct implementation
│   ├── plan_execute_agent.py   # Plan-then-Execute implementation
│   └── reflexion_agent.py      # Reflexion implementation
├── tasks/               # Task definitions for failure reproduction
│   ├── infinite_loop_task.py
│   ├── tool_fabrication_task.py
│   └── ...
├── utils/               # Utilities
│   ├── logging.py              # Transcript logging
│   ├── cost_tracking.py        # Budget monitoring
│   └── checkpoint.py           # Crash recovery
└── run_experiment.py    # Main experiment runner
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Run cost estimates
python src/utils/cost_tracking.py
```

## Usage

### Running a Single Experiment

```python
from src.frameworks.react_agent import ReActAgent
from src.tasks.infinite_loop_task import InfiniteLoopTask
from src.utils.logging import TranscriptLogger
from src.utils.cost_tracking import CostTracker

# Initialize
agent = ReActAgent(model="gpt-4-turbo")
task = InfiniteLoopTask()
logger = TranscriptLogger("pilot_experiment")
tracker = CostTracker(budget_usd=50.0)

# Run
run_data = logger.create_run(
    run_id="fi014_react_run001",
    failure_instance="FI-014",
    framework="react",
    model="gpt-4-turbo",
    task="laptop_research"
)

# Execute agent loop
# ... (implementation specific)

# Save results
logger.save_run(run_data)
tracker.print_status()
```

### Running Batch Experiments

```python
from src.utils.checkpoint import ExperimentQueue, create_run_plan

# Create run plan
queue = ExperimentQueue("fi014_infinite_loop")
runs = create_run_plan("FI-014", "react", "gpt-4-turbo", "laptop_research", 10)
queue.add_runs(runs)

# Process queue (with automatic checkpointing)
while not queue.is_complete():
    run = queue.get_next_run()
    # ... execute run ...
    queue.mark_completed(run['run_id'])
```

## Experimental Protocol

See `../experiments/00-experimental-protocol.md` for:
- Framework selection rationale
- Failure prioritization
- Task design principles
- Budget allocation
- Analysis plan

## Data Output

All experimental data goes to:
- `experiments/data/`: Individual run JSON files
- `experiments/results/`: Aggregated analysis
- `experiments/checkpoints/`: Recovery checkpoints

## Cost Tracking

Budget limit: $200-300 total
- Pilot runs (Session 9): $15-30
- Full runs (Session 10): $60-120
- Analysis (Session 11): $0

Track with: `CostTracker.print_status()`

## Development Status

- [x] Protocol designed
- [x] Utilities implemented (logging, cost tracking, checkpointing)
- [ ] Framework wrappers (pending)
- [ ] Task implementations (pending)
- [ ] Main runner script (pending)
- [ ] Pilot experiments (Session 9)

## Notes

- All experiments pre-registered to avoid p-hacking
- Checkpointing enables crash recovery
- Budget enforcement prevents overruns
- Full transcripts captured for paper examples
