# Agent Failure Taxonomy - Experiment Infrastructure

## Overview

This directory contains the experimental infrastructure for validating the agent failure taxonomy through controlled experiments.

## Structure

```
src/
├── tasks/                  # Task generators for each failure type
│   ├── tool_fabrication.py
│   ├── infinite_loop.py
│   └── false_completion.py
├── frameworks/             # Agent framework wrappers
│   ├── base.py
│   ├── langraph_wrapper.py
│   ├── plan_execute_wrapper.py
│   └── reflexion_wrapper.py
├── detectors/              # Failure pattern detectors
│   ├── tool_fabrication_detector.py
│   ├── infinite_loop_detector.py
│   └── false_completion_detector.py
├── utils/                  # Shared utilities
│   ├── logging.py
│   ├── checkpoint.py
│   └── cost_tracker.py
├── run_experiment.py       # Main experiment runner
└── analyze_results.py      # Analysis and visualization
```

## Setup

```bash
cd projects/agent-failure-taxonomy/src
pip install -r requirements.txt
```

## Usage

### Running Canary Experiment
```bash
python run_experiment.py --spec ../experiments/pilot-experiment-spec.yaml --mode canary
```

### Running Full Pilot
```bash
python run_experiment.py --spec ../experiments/pilot-experiment-spec.yaml --mode full
```

### Analyzing Results
```bash
python analyze_results.py --results ../experiments/pilot-results/ --output ../experiments/pilot-analysis.md
```

## Design Principles

1. **Modularity**: Each component (task generator, framework wrapper, detector) has a clean interface
2. **Reusability**: Infrastructure designed to support multiple experiment types
3. **Reproducibility**: Seeded randomization, deterministic ground truth, comprehensive logging
4. **Crash Recovery**: Checkpoint system enables resuming from any point
5. **Cost Control**: Per-instance and cumulative cost tracking with circuit breakers
