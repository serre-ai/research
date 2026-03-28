# Agent Failure Taxonomy: Experimental Infrastructure

This directory contains the infrastructure for controlled reproduction of agent failures across multiple architectures.

## Directory Structure

```
src/
├── frameworks/          # Agent framework implementations
│   ├── react_agent.py        # ReAct architecture (LangChain)
│   ├── plan_execute.py       # Plan-then-execute architecture
│   └── reflexion.py          # Reflexion architecture
├── tests/              # Failure reproduction tests
│   ├── tool_fabrication.py   # F1: Tool selection hallucination
│   ├── infinite_loops.py     # F2: Progress monitoring failure
│   ├── context_degradation.py # F3: Long-context performance
│   ├── self_correction.py    # F4: Reflection degeneration
│   ├── false_completion.py   # F5: Premature task completion
│   └── state_divergence.py   # F6: State tracking errors
├── utils/              # Shared utilities
│   ├── logging.py           # API call logging, cost tracking
│   ├── checkpoint.py        # Checkpoint/resume system
│   └── metrics.py           # Evaluation metrics
└── README.md           # This file
```

## Usage

### Running a Single Test

```python
from frameworks.react_agent import ReActAgent
from tests.tool_fabrication import ToolFabricationTest

# Initialize framework
agent = ReActAgent(model="claude-3-5-sonnet-20241022")

# Initialize test
test = ToolFabricationTest(num_tools=20)

# Run test
result = test.run(agent, num_instances=10)

# Analyze results
print(f"Fabrication rate: {result.fabrication_rate}")
print(f"Total cost: ${result.total_cost:.4f}")
```

### Running Full Evaluation

```python
from experiments.run_evaluation import run_full_evaluation

# Run all tests across all frameworks
results = run_full_evaluation(
    frameworks=["react", "plan_execute", "reflexion"],
    tests=["tool_fabrication", "false_completion"],
    instances_per_test=20,
    checkpoint_dir="experiments/pilot-reproduction/checkpoints"
)
```

## Design Principles

1. **Framework Independence**: Tests should be runnable across any framework implementing the base interface
2. **Deterministic**: Fixed random seeds, temperature=0.0, controlled environment
3. **Checkpointing**: All evaluations can be resumed after crashes
4. **Cost Tracking**: Every API call logged with cost attribution
5. **Reproducibility**: Full configuration and results stored for each run

## Models

Default model: `claude-3-5-sonnet-20241022` (consistent across all frameworks)

Alternative models can be specified for comparative studies.

## Cost Estimates

Per-instance costs (approximate, Claude Sonnet 3.5):
- F1 Tool Fabrication: $0.005
- F2 Infinite Loops: $0.010-0.020 (varies with loop depth)
- F3 Context Degradation: $0.015-0.030 (varies with context length)
- F4 Self-Correction: $0.008-0.015 (multiple reflection cycles)
- F5 False Completion: $0.005-0.010
- F6 State Divergence: $0.004-0.008

Pilot run (F1 + F5, 20 instances × 3 frameworks): ~$1.80-3.60

## Next Steps

1. Implement ReAct wrapper with LangChain
2. Implement tool fabrication test
3. Run pilot (10 instances) to validate infrastructure
4. Expand to additional frameworks and tests
