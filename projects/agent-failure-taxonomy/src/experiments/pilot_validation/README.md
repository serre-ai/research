# Pilot Validation Experiment Infrastructure

Complete implementation of the pilot taxonomy validation experiment testing 3 high-priority agent failures.

## Overview

This infrastructure enables controlled reproduction of agent failures across frameworks with automated detection and analysis.

**Experiment**: Pilot Taxonomy Validation
**Failures Tested**: Tool Fabrication (1.1), Infinite Loop (3.1), Context Degradation (4.3)
**Framework**: LangGraph (ReAct architecture)
**Budget**: $10.50 estimated (canary: $2.50, full: $8.00)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     run_pilot.py                            │
│              (Experiment Orchestration)                      │
└───┬─────────────────────────────┬──────────────────────┬────┘
    │                             │                      │
    ▼                             ▼                      ▼
┌──────────────────┐  ┌─────────────────────┐  ┌───────────────────┐
│ task_generators  │  │ framework_wrapper   │  │ failure_detectors │
│                  │  │                     │  │                   │
│ - Tool Fab       │  │ - LangGraphWrapper  │  │ - Tool Fab        │
│ - Infinite Loop  │  │ - AutoGPTWrapper    │  │ - Infinite Loop   │
│ - Context Degrad │  │ - ExecutionTrace    │  │ - Context Degrad  │
└──────────────────┘  └─────────────────────┘  └───────────────────┘
         │                      │                        │
         └──────────────────────┼────────────────────────┘
                                ▼
                      ┌─────────────────┐
                      │ Traces (JSON)   │
                      │ Results (JSON)  │
                      │ Analysis (MD)   │
                      └─────────────────┘
```

## Components

### 1. `framework_wrapper.py`
**Purpose**: Abstract interface for running agents across frameworks

**Key Classes**:
- `AgentFramework`: Base class with trace recording
- `LangGraphWrapper`: ReAct agent implementation
- `AutoGPTWrapper`: Autonomous loop implementation
- `ExecutionTrace`: Captures full execution history

**Usage**:
```python
from framework_wrapper import create_agent

agent = create_agent('langgraph', model='gpt-4o-mini', temperature=0.7)
agent.setup(tools=my_tools, system_prompt="You are helpful.")
trace = agent.run(task="Complete this task", max_iterations=20)
```

### 2. `task_generators.py`
**Purpose**: Generate tasks designed to trigger specific failures

**Key Classes**:
- `ToolFabricationTaskGenerator`: Creates tasks with 15 tools to trigger fabrication
- `InfiniteLoopTaskGenerator`: Creates ambiguous tasks to trigger loops
- `ContextDegradationTaskGenerator`: Creates long-context tasks to measure degradation

**Usage**:
```python
from task_generators import create_task_generator

generator = create_task_generator('tool_fabrication')
tasks = generator.generate_batch(5)  # 5 variants

for task in tasks:
    print(task.task_description)
    print(task.expected_failure)
```

### 3. `failure_detectors.py`
**Purpose**: Automated detection of failures from execution traces

**Key Classes**:
- `ToolFabricationDetector`: Checks tool calls against registry
- `InfiniteLoopDetector`: Detects repeated action patterns (edit distance)
- `ContextDegradationDetector`: Measures position-based accuracy drop
- `ReflexionBiasDetector`: Detects repeated wrong answers despite reflection
- `JSONRecoveryDetector`: Detects JSON errors without retry

**Usage**:
```python
from failure_detectors import create_detector

detector = create_detector('tool_fabrication', tools_registry=['add', 'multiply'])
result = detector.detect(trace_dict)

if result.failure_detected:
    print(f"Confidence: {result.confidence}")
    print(f"Evidence: {result.evidence}")
    print(f"Metrics: {result.metrics}")
```

### 4. `run_pilot.py`
**Purpose**: Main experiment orchestration script

**Modes**:
1. **Canary**: Test infrastructure with 3 tool fabrication trials
2. **Full**: Run all 3 failures × 5 trials = 15 tests
3. **Analyze**: Generate detailed analysis report

**Usage**:
```bash
# Step 1: Run canary to validate infrastructure
python run_pilot.py --canary --model gpt-4o-mini

# Step 2: If canary passes, run full pilot
python run_pilot.py --full --model gpt-4o-mini

# Step 3: Analyze results
python run_pilot.py --analyze
```

## Setup

### Prerequisites
```bash
# Python 3.9+
python --version

# Install dependencies
pip install langgraph langchain-openai openai

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### Directory Structure
```
experiments/pilot-taxonomy-validation/
├── spec.yaml                    # Pre-registration spec
├── results/
│   ├── canary_results.json     # Canary diagnostic results
│   ├── full_pilot_results.json # Full experiment results
│   └── analysis.md             # Detailed analysis
├── logs/
│   ├── tool_fabrication_0_trace.json
│   ├── infinite_loop_0_trace.json
│   └── ...
└── data/                       # Raw data (if needed)
```

## Running the Experiment

### Phase 1: Canary Run (~$2.50, 5 minutes)

```bash
cd projects/agent-failure-taxonomy/src/experiments/pilot_validation
python run_pilot.py --canary
```

**Expected Output**:
```
==============================================================
CANARY RUN: Tool Fabrication (3 trials)
==============================================================

 Running: tool_fabrication_0
  ✓ Completed in 8.2s
 Running: tool_fabrication_1
  ✓ Completed in 7.9s
 Running: tool_fabrication_2
  ✓ Completed in 8.5s

==============================================================
CANARY DIAGNOSTICS
==============================================================
✓ PASS pipeline_completion: 3/3 trials completed
✓ PASS extraction_success: 3/3 had extractable tool calls
✓ PASS cost_within_budget: Average cost $0.75 per trial (budget: $1.50)
✓ PASS baseline_sanity: 3/3 showed reasonable behavior

✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓✓
CANARY PASSED - Proceed to full pilot
==============================================================
```

**Decision**: If all diagnostics pass → proceed to Phase 2. If any fail → fix infrastructure first.

### Phase 2: Full Pilot (~$8.00, 15-20 minutes)

```bash
python run_pilot.py --full
```

**Expected Output**:
```
==============================================================
FULL PILOT: 3 Failures × 5 Trials = 15 Total
==============================================================

==============================================================
Testing: Tool Fabrication
==============================================================

  Running: tool_fabrication_0
    ✓ DETECTED (confidence: 1.00)
  Running: tool_fabrication_1
    ✓ DETECTED (confidence: 1.00)
  ...

==============================================================
Testing: Infinite Loop
==============================================================
  ...

==============================================================
PILOT VALIDATION SUMMARY
==============================================================

✓ SUCCESS Tool Fabrication
  Detection rate: 80% (4/5)

✓ SUCCESS Infinite Loop
  Detection rate: 60% (3/5)

✗ FAILED Context Degradation
  Detection rate: 40% (2/5)

==============================================================
Overall Validation: 2/3 failures reproduced (66%)

✓✓ PARTIAL VALIDATION - Core categories validated
→ Refine test design for failed cases
==============================================================
```

### Phase 3: Analysis

```bash
python run_pilot.py --analyze
```

Generates detailed breakdown of each trial with evidence and metrics.

## Interpreting Results

### Success Criteria

**Per-failure**:
- Success: ≥60% detection rate (≥3 of 5 trials)
- Partial: 40-59% detection rate (2 of 5 trials)
- Failure: <40% detection rate (<2 of 5 trials)

**Overall**:
- **Strong Validation** (≥2/3 failures): Taxonomy empirically confirmed → proceed to full protocol
- **Partial Validation** (1/3 failures): Core categories validated → refine failed tests
- **Weak Validation** (0/3 failures): Re-examine taxonomy or test design

### Common Issues

**Tool Fabrication Not Detected**:
- Check: Are tools clearly described?
- Fix: Add more tool descriptions to increase confusion
- Alternative: Test with more tools (20 instead of 15)

**Infinite Loop Not Detected**:
- Check: Is task ambiguous enough?
- Fix: Remove all completion criteria from prompt
- Alternative: Test without iteration limits (careful!)

**Context Degradation Not Detected**:
- Check: Is context long enough?
- Fix: Increase padding to reach 32k+ tokens
- Alternative: Use harder recall questions

## Cost Control

**Budget Tracking**:
- Canary: $2.50 estimated
- Full pilot: $8.00 estimated
- Total: $10.50 estimated (max: $15.00)

**Cost per trial** (GPT-4o-mini):
- Tool Fabrication: ~$0.60 (moderate length, 10 iterations)
- Infinite Loop: ~$0.80 (may hit iteration limit)
- Context Degradation: ~$0.60 (long context but simple task)

**Optimization strategies**:
1. Use GPT-4o-mini by default (10x cheaper than GPT-4)
2. Hard iteration limits (max_iterations=20)
3. Timeouts to prevent runaway costs (timeout_seconds=300)
4. Real-time cost tracking in experiment output

## Next Steps After Pilot

### If Strong Validation (≥2/3 passed):
1. Update `status.yaml`: controlled_experiments.status = "pilot_complete"
2. Write up pilot results in `experiments/pilot-taxonomy-validation/analysis.md`
3. Design full 6-failure protocol (add 3 more failures)
4. Estimate budget for full protocol (~$45-75)
5. Create new spec for full validation

### If Partial Validation (1/3 passed):
1. Analyze failed tests: why didn't failures reproduce?
2. Refine task generators for failed cases
3. Re-run failed tests with adjusted tasks
4. Document what worked vs. what didn't
5. Consider alternative frameworks for hard-to-reproduce failures

### If Weak Validation (0/3 passed):
1. **Critical examination**: Are taxonomy categories valid?
2. Review original instances: did we misinterpret the failures?
3. Test on different frameworks (maybe LangGraph isn't representative)
4. Consult with domain experts (researchers who study agents)
5. Consider revising taxonomy based on empirical findings

## Troubleshooting

### Import Errors
```bash
# If langgraph not found:
pip install langgraph langchain-openai

# If openai not found:
pip install openai
```

### API Rate Limits
```python
# Add sleep between trials in run_pilot.py:
import time
time.sleep(1)  # 1 second between calls
```

### Trace Not Saving
```bash
# Check permissions on experiments directory:
chmod -R u+w experiments/pilot-taxonomy-validation/
```

### Git Permission Issues
If you encounter git permission errors when committing:
```bash
# Check git objects permissions:
ls -la .git/objects/

# Fix if needed:
chmod -R u+w .git/objects/
```

## File Reference

**Generated Files**:
- `experiments/pilot-taxonomy-validation/results/canary_results.json`: Canary diagnostics
- `experiments/pilot-taxonomy-validation/results/full_pilot_results.json`: Full experiment data
- `experiments/pilot-taxonomy-validation/logs/*.json`: Individual execution traces
- `experiments/pilot-taxonomy-validation/analysis.md`: Detailed analysis report

**Configuration**:
- `experiments/pilot-taxonomy-validation/spec.yaml`: Pre-registration specification
- `src/experiments/pilot_validation/*.py`: Implementation code

## Contact

For questions or issues:
1. Check `notes/06-experimental-validation-protocol.md` for detailed protocol
2. Review `EXPERIMENTAL-PROTOCOL-SUMMARY.md` for quick reference
3. Check execution traces in `logs/` directory for debugging

---

**Status**: Ready for execution (infrastructure complete, waiting for OpenAI API key and budget approval)
**Last Updated**: 2026-03-27
**Estimated Cost**: $10.50 (canary + full pilot)
**Estimated Time**: 25-30 minutes total
