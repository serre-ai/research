# Agent Failure Taxonomy Experiment Infrastructure

**Purpose**: Controlled reproduction of agent failures across frameworks
**Status**: In development
**Created**: 2026-03-29

---

## Architecture

```
src/
├── frameworks/          # Agent framework wrappers
│   ├── base.py         # Abstract base class for all frameworks
│   ├── react.py        # ReAct implementation
│   ├── autogpt.py      # AutoGPT implementation
│   ├── reflexion.py    # Reflexion implementation
│   └── plan_execute.py # Plan-then-Execute implementation
├── tasks/              # Task generators and validators
│   ├── tool_fabrication.py
│   ├── ambiguous_loop.py
│   └── reflection_error.py
├── evaluation/         # Failure detection and metrics
│   ├── extractors.py   # Extract failure signals from traces
│   ├── validators.py   # Validate against ground truth
│   └── metrics.py      # Compute failure rates, statistics
├── utils/              # Utilities
│   ├── logging.py      # Structured logging
│   ├── checkpointing.py # Crash recovery
│   └── cost_tracking.py # API cost tracking
└── run_experiment.py   # Main experiment runner
```

---

## Design Principles

### 1. Framework Abstraction
All agent frameworks implement a common interface:
```python
class AgentFramework(ABC):
    @abstractmethod
    def execute(self, task: Task, config: Config) -> AgentTrace:
        """Execute task and return complete trace"""
        pass
```

This allows:
- Drop-in framework comparison
- Consistent logging across frameworks
- Unified failure extraction

### 2. Deterministic Failure Detection
Failure signals are extracted deterministically from traces:
- Tool fabrication: Check if tool name exists in provided tool list
- Infinite loop: Check iteration count and state change patterns
- Error persistence: Compare initial vs. final answers after reflection

No manual coding or subjective judgment needed.

### 3. Checkpointing for Crash Recovery
Each instance execution is checkpointed:
```python
checkpoint = {
    "instance_id": "tool_fab_1",
    "framework": "react",
    "model": "gpt-4o",
    "status": "completed",
    "result": {...}
}
```

If experiment crashes, resume from last checkpoint.

### 4. Cost Tracking
Every API call is logged with cost estimate:
```python
api_call = {
    "timestamp": "2026-03-29T12:00:00",
    "model": "gpt-4o",
    "input_tokens": 8192,
    "output_tokens": 4096,
    "cost_usd": 0.061
}
```

Cumulative cost tracked; experiment halts if budget exceeded.

### 5. Structured Output
All results stored in JSON for easy analysis:
```json
{
  "instance_id": "tool_fab_1",
  "framework": "react",
  "model": "gpt-4o-2024-08-06",
  "scenario": "tool_fabrication",
  "execution": {
    "iterations": 3,
    "timeout": false,
    "error": null
  },
  "failure_signals": {
    "tool_fabricated": true,
    "fabricated_tool": "search_google",
    "selected_tool": "search_google",
    "correct_tool": "search_wikipedia"
  },
  "trace": {...},
  "cost_usd": 0.052
}
```

---

## Implementation Status

### Phase 1: Base Infrastructure (Current)
- [ ] Abstract framework base class
- [ ] Task specification dataclasses
- [ ] Logging utilities
- [ ] Checkpointing system
- [ ] Cost tracking

### Phase 2: Framework Wrappers
- [ ] ReAct (LangChain)
- [ ] AutoGPT (standalone)
- [ ] Reflexion (custom)
- [ ] Plan-Execute (LangChain)

### Phase 3: Task Generators
- [ ] Tool fabrication scenario
- [ ] Ambiguous loop scenario
- [ ] Reflection error scenario

### Phase 4: Evaluation Pipeline
- [ ] Failure signal extractors
- [ ] Ground truth validators
- [ ] Metric computation

### Phase 5: Experiment Runner
- [ ] Main execution loop
- [ ] Canary run support
- [ ] Results aggregation

---

## Usage (Planned)

### Run Full Experiment
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --output experiments/pilot-failure-reproduction/results/
```

### Run Canary Only
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --canary-only \
  --output experiments/pilot-failure-reproduction/canary-results.yaml
```

### Resume from Checkpoint
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --resume experiments/pilot-failure-reproduction/checkpoint.json \
  --output experiments/pilot-failure-reproduction/results/
```

---

## Dependencies

### Core
- `python >= 3.10`
- `pydantic >= 2.0` - Data validation
- `pyyaml >= 6.0` - Config parsing
- `openai >= 1.0` - GPT-4o API
- `anthropic >= 0.18` - Claude API

### Frameworks
- `langchain >= 0.1.0` - ReAct, Plan-Execute
- `autogpt >= 0.5.0` - AutoGPT
- Custom Reflexion implementation (no package)

### Analysis
- `pandas >= 2.0` - Data manipulation
- `numpy >= 1.24` - Numerical operations
- `scipy >= 1.10` - Statistical tests

### Optional
- `tenacity >= 8.0` - Retry logic
- `tqdm >= 4.65` - Progress bars

---

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Testing

### Unit Tests
```bash
pytest src/tests/
```

### Integration Tests
```bash
pytest src/tests/integration/ --slow
```

### Dry Run (No API Calls)
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --dry-run
```

---

## Next Steps

1. Implement base infrastructure (checkpointing, logging, cost tracking)
2. Create ReAct wrapper as reference implementation
3. Build tool fabrication task generator
4. Test end-to-end with single instance
5. Add remaining frameworks and scenarios
6. Run canary experiment
7. Execute full pilot experiment

---

## Notes

- All API calls should have retry logic (rate limits, transient failures)
- Timeout handling: 5 minutes per instance (configurable)
- Logging: Both file and console, structured JSON for analysis
- Error handling: Continue experiment even if single instance fails
- Results: Commit to git after each successful run (with checkpoint)
