# Pilot Failure Reproduction Experiment

**Status**: Infrastructure complete, ready for execution
**Date**: 2026-03-29
**Estimated Cost**: ~$9-15 USD (full pilot)

---

## Objective

Validate the agent failure taxonomy through controlled reproduction of three high-priority failure modes:

1. **Tool hallucination (1.1)**: Agent fabricates or misuses tools as tool count scales
2. **Infinite loops (3.1)**: Agent fails to make progress on ambiguous tasks
3. **False completion (5.1)**: Agent claims completion but requirements not met

---

## Design Overview

### Tasks (9 total)

**Tool Hallucination** (3 tasks):
- `tool_scaling_5`: Simple task with 5 decoy tools + 1 correct tool
- `tool_scaling_10`: Same task with 10 decoy tools + 1 correct tool
- `tool_scaling_20`: Same task with 20 decoy tools + 1 correct tool

**Infinite Loops** (3 tasks):
- `ambiguous_goal_0`: "Research everything about machine learning..."
- `ambiguous_goal_1`: "Find the best restaurant... keep searching until certain..."
- `ambiguous_goal_2`: "Optimize this code until perfect..."

**False Completion** (3 tasks):
- `complex_verification_0`: Multi-step task requiring 5 sub-goals
- `complex_verification_1`: Multi-step program with 5 requirements
- `complex_verification_2`: Research task with 5 mandatory elements

### Frameworks (1 for pilot)

- **ReAct**: Standard reasoning-action agent (LangChain implementation)

Future: Plan-then-execute, Autonomous loop

### Models (2)

- **gpt-4o-mini**: Fast, cheap baseline
- **claude-3-5-sonnet**: Current best agent model

### Total Runs

9 tasks × 1 framework × 2 models = **18 instances**

---

## Predictions

### P1: Tool Hallucination Scales with Tool Count

- **Hypothesis**: As tool count increases from 5 → 10 → 20, hallucination rate increases
- **Expected**: ≥20% increase in hallucination rate at 20 tools vs. 5 tools
- **Taxonomy category**: 1.1 Tool Selection Failures
- **LLM limitation**: C6 (Tool Grounding)

### P2: Infinite Loops on Ambiguous Tasks

- **Hypothesis**: Agents will loop endlessly on tasks with unclear completion criteria
- **Expected**: ≥50% of ambiguous task runs timeout or show no progress
- **Taxonomy category**: 3.1 Progress Monitoring
- **LLM limitation**: C3 (Meta-Cognitive Monitoring)

### P3: False Completion on Complex Tasks

- **Hypothesis**: Agents claim completion before meeting all requirements
- **Expected**: ≥30% of complex verification tasks end with <80% requirements met
- **Taxonomy category**: 5.1 Verification Failures
- **LLM limitation**: C3 (Meta-Cognitive Monitoring), C7 (Self-Correction)

---

## Infrastructure

### Code Structure

```
src/
├── frameworks/
│   └── react_agent.py           # ReAct implementation with logging
├── tasks/
│   └── task_definitions.py      # 9 task definitions with ground truth
├── utils/
│   ├── logger.py                # Structured logging (traces, costs, metrics)
│   └── failure_detection.py    # Automated failure classification
└── run_experiment.py            # Main experiment runner
```

### Automated Failure Detection

**FailureDetector** classifies runs as:

- ✅ **Success**: Task completed correctly (ground truth matched)
- ❌ **Tool hallucination**: Non-existent tool used or wrong tool selected
- ❌ **Infinite loop**: Same action repeated ≥3 times
- ❌ **No progress**: Identical observations for ≥5 consecutive steps
- ❌ **False completion**: Agent claims done but success criteria not met
- ❌ **Timeout**: Max iterations (15) reached
- ❌ **Error**: Infrastructure failure

### Logging

Every run produces:
- **Trace file**: Full step-by-step execution (JSON)
- **Metadata**: Outcome, failure type, steps, tokens, cost
- **Summary stats**: Aggregated across all runs

---

## Execution Plan

### Phase 1: Canary Run (NEXT STEP)

**Purpose**: Validate pipeline before spending budget on full run

**Scope**: 1 task (tool_scaling_5) × 1 framework (ReAct) × 1 model (gpt-4o-mini) = 1 instance

**Cost**: ~$0.10

**Diagnostics**:
1. ✓ Pipeline completes without infrastructure errors
2. ✓ Agent outputs are parseable (action/observation logs extractable)
3. ✓ Failure detection works (can classify outcome)
4. ✓ Cost within 2x of estimate

**Command**:
```bash
python src/run_experiment.py \
    --spec experiments/pilot-failure-reproduction/spec.yaml \
    --canary
```

**Expected output**: `experiments/pilot-failure-reproduction/canary-results/`
- Trace file for the single instance
- `canary_summary.json` with diagnostics

**Decision**: If all 4 diagnostics pass → proceed to Phase 2. If any fail → debug before full run.

---

### Phase 2: Full Pilot Run

**Scope**: 9 tasks × 1 framework × 2 models = 18 instances

**Cost**: ~$9-15 USD

**Command**:
```bash
python src/run_experiment.py \
    --spec experiments/pilot-failure-reproduction/spec.yaml
```

**Expected output**: `experiments/pilot-failure-reproduction/results/`
- 18 trace files (full execution logs)
- `full_summary.json` with aggregate statistics

**Timeline**: ~30-60 minutes (depends on agent step counts)

---

### Phase 3: Analysis

**Manual analysis required**:

1. **Verify failure detection accuracy**:
   - Spot-check 5 random traces to confirm automated classification matches manual review
   - Adjust failure detection heuristics if needed

2. **Compute failure rates by category**:
   - Tool hallucination: % of tool scaling tasks with fabrication
   - Infinite loops: % of ambiguous tasks with loops or no progress
   - False completion: % of complex tasks ending with <80% requirements

3. **Compare models**:
   - gpt-4o-mini vs claude-3-5-sonnet failure rates
   - Which failures are model-specific vs. universal?

4. **Test predictions**:
   - P1: Does hallucination rate increase 5 → 10 → 20 tools?
   - P2: Do ≥50% of ambiguous tasks fail?
   - P3: Do ≥30% of complex tasks show false completion?

5. **Validate taxonomy**:
   - Are the three failure categories reproducible and distinct?
   - Do failures map to predicted LLM limitations (C3, C6, C7)?

**Output**: Analysis document in `experiments/pilot-failure-reproduction/analysis.md`

---

## Success Criteria

**Pilot succeeds if**:

1. ✅ At least 2 of 3 failure categories reproduced at >30% rate
2. ✅ Automated detection ≥80% accurate on spot-check
3. ✅ Total cost <$20 (within budget)

**This validates**:
- Taxonomy categories represent real, reproducible phenomena (not one-off anecdotes)
- Infrastructure is ready for larger experiments
- Failure patterns are detectable and measurable

---

## Next Steps After Pilot

### If Pilot Succeeds

1. **Scale up experiments**:
   - Add plan-then-execute and autonomous loop frameworks
   - Increase to 30 instances per task for statistical power
   - Add more model families (Llama, Qwen, Ministral)

2. **Expand failure coverage**:
   - Test remaining 6 taxonomy categories
   - Add context degradation (4.3), cascading errors (7.2)

3. **Generate paper figures**:
   - Figure 1: Failure distribution by category (bar chart)
   - Figure 2: Tool hallucination vs. tool count (line plot)
   - Figure 3: Architecture-failure correlation matrix (heatmap)

4. **Write empirical results section**:
   - Integrate experimental data with taxonomy
   - Quantify architecture-specific failure rates
   - Validate LLM limitation mapping (C1-C8)

### If Pilot Fails

1. **Debug infrastructure**:
   - Fix failure detection bugs
   - Improve task definitions
   - Adjust success criteria

2. **Revise predictions**:
   - If no failures detected → tasks may be too easy
   - If all instances fail → tasks may be too hard
   - Calibrate difficulty

3. **Consider alternative frameworks**:
   - LangChain may abstract away some failures
   - Try raw OpenAI/Anthropic APIs for more control

---

## Budget Tracking

| Phase | Cost Estimate | Status |
|-------|--------------|--------|
| Canary run | $0.10 | Planned |
| Full pilot | $9-15 | Planned |
| Buffer | $5 | Reserved |
| **Total** | **~$15** | **Within $645 remaining** |

---

## Dependencies

**Python packages** (see `src/requirements.txt`):
- langchain
- langchain-openai
- langchain-anthropic
- openai
- anthropic
- pyyaml

**API keys required**:
- `OPENAI_API_KEY` (for gpt-4o-mini)
- `ANTHROPIC_API_KEY` (for claude-3-5-sonnet)

**Install**:
```bash
cd projects/agent-failure-taxonomy
pip install -r src/requirements.txt
```

---

## Notes

- **Mock tools**: Current implementation uses mock tools (canned responses) to avoid external API dependencies. This is sufficient for testing failure *patterns* (hallucination, loops, false completion), though results won't reflect real-world tool behavior.

- **Temperature**: Set to 0.0 for deterministic behavior. Each task run should be reproducible.

- **Max iterations**: 15 steps per task. Sufficient for simple tasks; longer tasks may timeout (this is intentional for loop detection).

- **No parallelization**: Runs sequentially to avoid API rate limits and ensure clean logs. Full pilot should complete in <1 hour.

- **Critic review**: Spec.yaml requires critic approval before full run (for experiments >$2). Canary is under $2 threshold, can run immediately.

---

## Ready to Execute

✅ Spec.yaml complete
✅ Infrastructure built (7 Python modules)
✅ Tasks defined (9 instances)
✅ Failure detection implemented
✅ Logging and aggregation ready

**Next action**: Run canary experiment

```bash
cd /home/deepwork/deepwork-agent/.worktrees/agent-failure-taxonomy/projects/agent-failure-taxonomy
pip install -r src/requirements.txt
python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml --canary
```
