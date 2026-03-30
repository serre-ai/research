# Pilot Failure Reproduction Experiment

**Status**: Infrastructure complete, awaiting canary run
**Estimated Cost**: $2.00 (full run), $0.10 (canary)
**Timeline**: 1-2 hours for full experiment

## Overview

This experiment validates the agent failure taxonomy through controlled reproduction of high-priority failures across multiple frameworks. It tests whether failures observed in production/literature can be systematically reproduced and whether they map cleanly to the 9-category taxonomy.

## Hypothesis

The 9-category agent failure taxonomy will successfully categorize failures reproduced in controlled experiments. Specifically:

1. **Tool-use failures** (fabrication, hallucinated execution) will reproduce across all frameworks (>80%)
2. **Planning failures** (infinite loops, progress monitoring) will reproduce in ReAct/autonomous architectures (>60%)
3. **Self-correction failures** (false completion) will reproduce in plan-then-execute frameworks (>60%)
4. Reproduction rates will match taxonomy reproducibility ratings

## Experimental Design

### Frameworks Tested (3)
- **ReAct (LangChain)**: Observation → Thought → Action loop
- **AutoGPT Lite**: Simplified autonomous loop pattern
- **Plan-then-Execute**: Custom planner + executor

### Failure Scenarios (6)

| Scenario | Category | LLM Limitation | Expected Rate |
|----------|----------|----------------|---------------|
| Tool Fabrication | 1.1 Selection Failures | C6 + C1 | >80% |
| Tool Hallucination | 1.2 Execution Failures | C8 | >60% |
| Infinite Loop | 3.1 Progress Monitoring | C3 | >60% |
| Progress Stagnation | 3.1 Progress Monitoring | C3 | >60% |
| False Completion | 5.1 Verification Failures | C3 + C7 | >60% |
| Context Degradation | 4.3 Context Management | C2 | >80% |

### Models
- Claude Haiku 4.5 (primary)
- GPT-4o-mini (comparison)

### Sample Size
- **Canary**: 36 trials (3 scenarios × 2 frameworks × 2 models × 3 instances)
- **Full run**: 360 trials (6 scenarios × 3 frameworks × 2 models × 10 instances)

## Setup

### 1. Install Dependencies

```bash
cd projects/agent-failure-taxonomy/src
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Verify Setup

```bash
python run_experiment.py --help
```

## Running the Experiment

### Canary Run (Recommended First)

The canary run tests 3 scenarios with minimal cost to validate the pipeline:

```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --mode canary
```

**Expected output**:
- 36 trials complete in ~10 minutes
- Cost: ~$0.10
- Results: `experiments/pilot-failure-reproduction/data/canary-results.jsonl`

### Canary Diagnostics

After canary run, check:

```bash
# Count trials
wc -l experiments/pilot-failure-reproduction/data/canary-results.jsonl

# Check reproduction rates (should see at least 1 success)
grep -c '"reproduction_success": true' experiments/pilot-failure-reproduction/data/canary-results.jsonl

# Review failures
grep '"failure_detected"' experiments/pilot-failure-reproduction/data/canary-results.jsonl | head
```

**Canary success criteria**:
- ✅ All 36 trials complete without framework errors
- ✅ At least 1 of 3 scenarios reproduces (≥12 successful reproductions)
- ✅ Complete logs for all trials
- ✅ Cost within 2x estimate (~$0.10 → max $0.20)

### Full Run (After Canary Success)

```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --mode full
```

**Expected output**:
- 360 trials complete in ~60-90 minutes
- Cost: ~$2.00
- Results: `experiments/pilot-failure-reproduction/data/full-results.jsonl`

## Analysis

After full run, analyze results:

```bash
# Count reproductions by scenario
python -c "
import json
from collections import Counter

trials = []
with open('experiments/pilot-failure-reproduction/data/full-results.jsonl') as f:
    for line in f:
        record = json.loads(line)
        if '_schema' not in record:
            trials.append(record)

# Count by scenario
scenarios = Counter(t['scenario'] for t in trials)
successes = Counter(t['scenario'] for t in trials if t['reproduction_success'])

for scenario in scenarios:
    total = scenarios[scenario]
    success = successes[scenario]
    rate = 100 * success / total if total else 0
    print(f'{scenario:25s} {success:3d}/{total:3d} ({rate:5.1f}%)')
"
```

Expected output (hypothesis):
```
tool_fabrication          48/60  (80.0%)  ← Should be >80%
tool_hallucination        36/60  (60.0%)  ← Should be >60%
infinite_loop             36/60  (60.0%)  ← Should be >60%
progress_stagnation       36/60  (60.0%)  ← Should be >60%
false_completion          36/60  (60.0%)  ← Should be >60%
context_degradation       48/60  (80.0%)  ← Should be >80%
```

### Architecture Correlation

```bash
# Compare frameworks
python -c "
import json
from collections import defaultdict

trials = []
with open('experiments/pilot-failure-reproduction/data/full-results.jsonl') as f:
    for line in f:
        record = json.loads(line)
        if '_schema' not in record:
            trials.append(record)

by_framework = defaultdict(lambda: {'total': 0, 'success': 0})
for t in trials:
    key = t['framework']
    by_framework[key]['total'] += 1
    if t['reproduction_success']:
        by_framework[key]['success'] += 1

for fw, stats in sorted(by_framework.items()):
    rate = 100 * stats['success'] / stats['total']
    print(f'{fw:20s} {stats[\"success\"]:3d}/{stats[\"total\"]:3d} ({rate:5.1f}%)')
"
```

## Deliverables

After successful full run:

1. **Data files**:
   - `data/canary-results.jsonl` (36 trials)
   - `data/full-results.jsonl` (360 trials)

2. **Analysis reports** (to be generated):
   - `analysis/reproduction-rates.md` (by scenario, framework, model)
   - `analysis/category-fit.md` (taxonomy validation)
   - `analysis/architecture-correlation.md` (framework-specific patterns)

3. **Figures** (to be generated with pub_style):
   - `figures/reproduction-by-scenario.pdf`
   - `figures/architecture-heatmap.pdf`

## Troubleshooting

### No reproductions in canary

**Problem**: 0 successful reproductions in canary run
**Diagnosis**: Check logs for errors:
```bash
grep '"error"' experiments/pilot-failure-reproduction/data/canary-results.jsonl
```

**Common causes**:
- API key not set
- LangChain version incompatibility
- Tool definitions incorrect

### High cost in canary

**Problem**: Canary costs >$0.20
**Diagnosis**: Check token usage:
```bash
python -c "
import json
trials = []
with open('experiments/pilot-failure-reproduction/data/canary-results.jsonl') as f:
    for line in f:
        record = json.loads(line)
        if '_schema' not in record:
            trials.append(record)

tokens = [t['metrics']['total_tokens'] for t in trials]
print(f'Avg tokens/trial: {sum(tokens)/len(tokens):.0f}')
print(f'Max tokens/trial: {max(tokens)}')
"
```

**Solution**: If >3000 tokens/trial, reduce `max_iterations` in spec.yaml

### Framework errors

**Problem**: Trials fail with exceptions
**Check**:
```bash
grep -A 5 '"error"' experiments/pilot-failure-reproduction/data/canary-results.jsonl
```

**Common fixes**:
- Update LangChain: `pip install -U langchain langchain-anthropic`
- Check tool definitions in `src/scenarios/tool_failures.py`

## Next Steps

After successful experiment:

1. **Update status.yaml** with results
2. **Generate analysis reports** using statistical tests from spec
3. **Create figures** for paper inclusion
4. **Write results section** for paper (ACL 2027 format)
5. **Plan follow-up experiments** for remaining scenarios

## Contact

For questions about this experiment, see:
- `spec.yaml` for detailed design
- `src/README.md` for infrastructure details
- `projects/agent-failure-taxonomy/status.yaml` for project status
