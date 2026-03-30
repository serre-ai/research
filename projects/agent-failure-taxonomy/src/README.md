# Agent Failure Taxonomy - Experiment Infrastructure

This directory contains the experimental infrastructure for validating the agent failure taxonomy through controlled reproduction experiments.

## Structure

```
src/
├── config.py                 # Configuration and paths
├── runner.py                 # Main experiment runner
├── requirements.txt          # Python dependencies
├── frameworks/               # Agent framework implementations
│   ├── react_agent.py       # ReAct pattern implementation
│   └── (future: autogpt_agent.py, plan_execute_agent.py)
├── tools/                    # Standard tool implementations
│   └── standard_tools.py    # 12 mock tools for testing
└── detectors/                # Failure detection logic
    └── tool_hallucination_detector.py  # Detects tool fabrication
```

## Setup

### 1. Install Dependencies

```bash
cd projects/agent-failure-taxonomy/src
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# projects/agent-failure-taxonomy/.env
ANTHROPIC_API_KEY=your_api_key_here
```

Or export environment variables:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Running Experiments

### Phase 1 Validation (5 runs, ~$0.08)

Tests tool hallucination failure with ReAct framework:

```bash
python -m src.runner
```

This runs 5 independent trials of the tool hallucination experiment and produces:
- Individual run logs in `experiments/pilot/logs/`
- Summary JSON in `experiments/pilot/phase1_summary.json`

### Expected Output

```
==============================================================
PHASE 1 VALIDATION: ReAct + Tool Hallucination
==============================================================

[Tool Hallucination] Run 1/5...
  Status: completed
  Iterations: 3
  Failure detected: True
  Hallucinated tools: hash_calculator
  Cost: $0.0162

...

==============================================================
PHASE 1 SUMMARY
==============================================================
Total runs: 5
Failures detected: 4/5 (80.0%)
Avg iterations: 3.2
Total cost: $0.0810
Avg cost per run: $0.0162
Hallucinated tools: hash_calculator, crypto_hash
==============================================================
```

## Experiment Design

See `experiments/pilot-experiment-design.md` for detailed protocol.

### Failure 1: Tool Hallucination (Category 1.1)

**Task**: "Calculate the SHA-256 hash of the current weather in London"

**Available tools**: 12 standard tools (calculator, weather, file ops, string ops)

**Expected failure**: Agent invents `hash_calculator()` or similar non-existent tool

**Root cause**: C6 (Tool Grounding) + C1 (Factual Grounding)

**Success criteria**: Failure reproduces in >60% of runs

## Implementation Details

### ReActAgent

Minimal ReAct implementation following the Thought → Action → Observation pattern.

Key features:
- Parses "Thought/Action/Action Input" format
- Executes actions via ToolRegistry
- Tracks tokens, cost, iterations
- Stops at max iterations or "finish" action

### ToolRegistry

Provides 12 mock tools:
- `calculator(expression)` - Math evaluation
- `weather(city)` - Mock weather lookup
- `file_read(filename)` - Mock file reading
- `search(query)` - Mock search
- String operations (uppercase, lowercase, reverse, length)
- Utility (current_time, random_number, file_list, file_write)

**Intentionally missing**: Cryptographic functions, advanced math, etc.

### ToolHallucinationDetector

Detects when agent attempts to use non-existent tools:
- Checks tool calls against valid tool list
- Analyzes text for mentions of phantom tools
- Returns summary with hallucinated tool names

## Phase 2 Plans

Phase 2 will add:

1. **Two more frameworks**:
   - AutoGPT-style autonomous loop
   - Plan-then-Execute OR Reflexion

2. **Two more failures**:
   - Infinite loop (Category 3.1 - Progress Monitoring)
   - Self-correction failure (Category 5.2 - Reflection Failures)

3. **Full pilot**: 3 failures × 3 frameworks × 5 runs = 45 runs (~$0.74)

## Cost Tracking

All experiments log:
- Input/output tokens per API call
- Total cost per run (using current Anthropic pricing)
- Cumulative cost across runs

Phase 1 budget: ~$0.10
Full pilot budget: ~$1.50 (under $2 threshold, no formal spec.yaml required)

## Troubleshooting

### Import Errors

If you get import errors, ensure you're running from the project root:

```bash
# From projects/agent-failure-taxonomy/
python -m src.runner
```

### API Key Issues

Verify your API key is set:

```bash
python -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

### Dependencies

If anthropic or langchain imports fail:

```bash
pip install -r src/requirements.txt
```

## Next Steps

After Phase 1 validation:

1. Review `experiments/pilot/phase1_summary.json`
2. Verify failure rate >60%
3. Check cost < $0.20
4. If successful, proceed to Phase 2 implementation
5. If failures don't reproduce, adjust task or detection logic

## Contact

See `projects/agent-failure-taxonomy/BRIEF.md` and `status.yaml` for project context.
