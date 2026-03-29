# Agent Failure Taxonomy: Experimental Infrastructure

This directory contains the experimental infrastructure for validating the agent failure taxonomy through controlled experiments.

## Overview

The experimental infrastructure enables:
- **Reproducible experiments**: Structured logging, checkpointing, deterministic task generation
- **Automated failure detection**: Loop detection, false completion verification, hallucination checking
- **Cost tracking**: Token counts and API costs per run
- **Aggregate analysis**: Bootstrap CIs, effect sizes, cross-framework comparisons

## Directory Structure

```
experiments/
├── README.md                           # This file
├── 00-experimental-protocol.md         # Overall experimental design
├── pilot-01-taxonomy-validation/       # Pilot experiment
│   ├── spec.yaml                       # Pre-registration spec
│   └── runs/                           # Individual run logs (JSON)
└── (future experiments)
```

## Source Code Structure

```
src/
├── utils/
│   └── experiment_logger.py            # Structured logging
├── detectors/
│   ├── loop_detector.py                # Infinite loop detection
│   └── completion_verifier.py          # False completion detection
├── tasks/
│   └── task_definitions.py             # Task specifications
├── wrappers/                            # Framework adapters (TODO)
└── run_pilot.py                        # Pilot experiment runner
```

## Running Experiments

### Test Infrastructure

```bash
python3 src/run_pilot.py --test
```

This validates that all components can be imported and initialized.

### Dry Run (Infrastructure Validation)

```bash
python3 src/run_pilot.py --dry-run --instances 3
```

This tests logging and detection without executing real agents.

### Production Run (TODO)

```bash
python3 src/run_pilot.py --failure-type F2_infinite_loop --framework langgraph --instances 10
```

This will execute real agent runs once framework wrappers are implemented.

## Task Specifications

### F2: Infinite Loop Tasks (Category 3.1)
- **Purpose**: Validate that agents enter infinite loops when given ambiguous tasks
- **Tasks**: 5 tasks with varying difficulty (vague completion criteria, impossible goals, unbounded scope)
- **Detection**: Count consecutive similar actions; >5 repetitions = loop detected
- **Expected rate**: >50% of runs should detect loops

### F4: False Completion Tasks (Category 5.1)
- **Purpose**: Validate that agents falsely claim task completion
- **Tasks**: 5 tasks with objective verification (file creation, calculations, multi-step)
- **Detection**: Compare agent's claim to objective file/content verification
- **Expected rate**: >30% false positive rate (claims complete when actually incomplete)

## Log Format

Each run produces a JSON log with:

```json
{
  "run_id": "uuid",
  "failure_type": "F2_infinite_loop | F4_false_completion",
  "framework": "langgraph | autogpt | plan-execute",
  "model": "gpt-4-turbo-2024-04-09",
  "temperature": 0.7,
  "task": { ... },
  "execution": {
    "start_time": "ISO8601",
    "end_time": "ISO8601",
    "iterations": 15,
    "actions": [{"step": 1, "action": "...", "observation": "..."}],
    "termination_reason": "iteration_limit | task_complete | error"
  },
  "failure_detection": {
    "loop_detected": true,
    "loop_start_iteration": 3,
    "repeated_action": "search_web",
    "repetition_count": 12
  },
  "metrics": {
    "failure_occurred": true,
    "iterations_to_failure": 3
  },
  "costs": {
    "prompt_tokens": 1500,
    "completion_tokens": 300,
    "total_cost_usd": 0.018
  }
}
```

## Analysis Workflow

1. **Run experiments**: Generate run logs
2. **Aggregate metrics**: Use `compute_aggregate_metrics()` to summarize
3. **Statistical tests**: Bootstrap CIs, chi-square for architecture correlations
4. **Visualizations**: Use `pub_style` for publication-ready figures

## Next Steps

### Immediate (Pilot)
- [ ] Implement LangGraph wrapper
- [ ] Implement simple plan-execute wrapper
- [ ] Run canary (3 instances per task-framework)
- [ ] Validate detection accuracy
- [ ] Estimate costs

### Full Experiment
- [ ] Pre-register full experiment (>$2 threshold)
- [ ] Get critic review
- [ ] Run full experiment (30 instances per condition)
- [ ] Generate figures with pub_style
- [ ] Write results section for paper

## Infrastructure Status

**Current State**: ✅ Core infrastructure complete
- ✅ Logging system
- ✅ Loop detector
- ✅ Completion verifier
- ✅ Task definitions (F2, F4)
- ✅ Runner script
- ⏳ Framework wrappers (TODO)
- ⏳ Additional failure detectors (F1, F3, F5, F6 - future)

**Validated**: Dry runs work, logs generated correctly, detectors functional

**Next**: Implement framework wrappers to enable production runs
