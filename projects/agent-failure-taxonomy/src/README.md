# Agent Failure Taxonomy: Experimental Infrastructure

This directory contains the infrastructure for running controlled agent failure reproduction experiments.

## Structure

```
src/
├── frameworks/         # Agent framework wrappers
│   ├── base_agent.py
│   ├── react_agent.py
│   ├── reflexion_agent.py
│   └── plan_execute_agent.py
├── tasks/             # Task generators with ground truth
│   ├── base_task.py
│   ├── tool_selection_task.py
│   ├── ambiguous_research_task.py
│   └── reflection_task.py
├── detectors/         # Failure mode detectors
│   ├── base_detector.py
│   ├── tool_hallucination_detector.py
│   ├── loop_detector.py
│   └── false_completion_detector.py
├── eval/              # Evaluation pipeline
│   ├── runner.py
│   ├── logger.py
│   └── analyzer.py
└── utils/             # Utilities
    ├── cost_tracker.py
    ├── checkpoint.py
    └── config.py
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."

# Run canary test
python -m src.eval.runner --experiment pilot-reproduction --mode canary

# Run full experiment (after canary passes)
python -m src.eval.runner --experiment pilot-reproduction --mode full
```

## Usage

See `experiments/00-experimental-protocol.md` for full documentation.

## Development Status

- [x] Protocol design
- [x] Pre-registration spec
- [ ] Framework wrappers (in progress)
- [ ] Task generators (in progress)
- [ ] Failure detectors (pending)
- [ ] Evaluation pipeline (pending)
