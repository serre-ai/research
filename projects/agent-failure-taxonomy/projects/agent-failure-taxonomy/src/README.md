# Agent Failure Reproduction Infrastructure

This directory contains the experimental infrastructure for reproducing agent failures in controlled settings across multiple frameworks.

## Structure

```
src/
├── frameworks/          # Agent framework implementations
│   ├── react_agent.py   # LangChain ReAct implementation
│   ├── autogpt_agent.py # Simplified AutoGPT pattern
│   └── plan_execute.py  # Plan-then-execute architecture
├── scenarios/           # Failure scenario definitions
│   ├── tool_failures.py # Tool fabrication & hallucination scenarios
│   ├── planning_failures.py # Infinite loop & stagnation scenarios
│   └── verification_failures.py # False completion scenarios
├── eval/                # Evaluation and logging utilities
│   ├── logger.py        # Structured logging for all trials
│   ├── classifier.py    # Automatic failure detection/classification
│   └── analyzer.py      # Reproduction rate and correlation analysis
└── run_experiment.py    # Main experiment runner

## Usage

### Running Canary Experiment
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --mode canary \
  --output experiments/pilot-failure-reproduction/data/canary-results.jsonl
```

### Running Full Experiment
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --mode full \
  --output experiments/pilot-failure-reproduction/data/trials.jsonl
```

### Analyzing Results
```bash
python src/eval/analyzer.py \
  --input experiments/pilot-failure-reproduction/data/trials.jsonl \
  --output experiments/pilot-failure-reproduction/analysis/
```

## Design Principles

1. **Deterministic seeding**: All random elements use fixed seeds for reproducibility
2. **Comprehensive logging**: Every trial logs prompts, responses, tool calls, classifications
3. **Crash recovery**: Experiments checkpoint after each trial; can resume from failures
4. **Cost tracking**: Real-time cost monitoring with automatic halts at budget limits
5. **Framework isolation**: Each framework wrapper has identical interface but independent implementation

## Dependencies

```bash
pip install langchain langchain-anthropic langchain-openai pydantic python-dotenv
```

## Environment Variables

Create `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```
