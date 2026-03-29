# Agent Failure Taxonomy: Experimental Infrastructure

This directory contains the experimental infrastructure for reproducing and validating agent failure modes identified in the taxonomy.

## Structure

```
src/
├── frameworks/         # Agent framework wrappers (ReAct, plan-execute, autonomous)
├── tasks/              # Task definitions with ground truth and success criteria
├── utils/              # Shared utilities (logging, failure detection, metrics)
└── run_experiment.py   # Main experiment runner
```

## Quick Start

```bash
# Install dependencies
pip install langchain langchain-openai langchain-anthropic openai anthropic pyyaml

# Run canary experiment
python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml --canary

# Run full pilot experiment
python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml
```

## Design Philosophy

1. **Minimal dependencies**: Use LangChain for standard frameworks, avoid heavy agent libraries
2. **Deterministic where possible**: Temperature 0, fixed seeds, reproducible tasks
3. **Checkpoint everything**: Resume from crashes, log every API call
4. **Failure-aware**: Detect and classify failures automatically, log raw traces for manual review

## Failure Detection

Each task definition includes:
- **Ground truth**: Correct answer or expected state
- **Success criteria**: Boolean function that checks completion
- **Failure patterns**: Regex/heuristics to detect specific failure modes

Automated detection classifies:
- ✅ Success: Task completed correctly
- ❌ Tool hallucination: Non-existent tool used
- ❌ Infinite loop: Same action repeated ≥3 times
- ❌ False completion: Agent claims done but criteria not met
- ❌ Timeout: Max iterations reached
- ❌ Error: Infrastructure failure
