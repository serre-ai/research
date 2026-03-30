# Pilot Experiment: Agent Failure Taxonomy Validation

**Date**: 2026-03-30
**Project**: agent-failure-taxonomy
**Status**: planned
**Phase**: Pre-registration (protocol design)
**Estimated Cost**: $1.50 (well under $2 threshold, no formal spec.yaml required)

---

## Objective

Validate taxonomy categories through controlled reproduction of 3 high-priority failure modes across 3 agent frameworks. Establish experimental infrastructure and methodology for full-scale validation.

---

## Why These Failures?

Selected based on:
1. **High impact** (16 tool-use instances, 7 planning instances, 6 self-correction instances)
2. **High reproducibility** (all rated "easy" or "high" in taxonomy)
3. **Framework diversity** (affect different architectures differently)
4. **Clear success criteria** (unambiguous detection of failure)
5. **Theoretical grounding** (map to C1, C3, C6, C7 limitations)

---

## Target Failures

### Failure 1: Tool Hallucination (Category 1.1 - Selection Failures)
**Taxonomy Category**: Tool-Use Failures → Selection Failures
**Root Cause**: C6 (Tool Grounding) + C1 (Factual Grounding)
**Reproducibility**: Easy
**Source**: Instance 18 from literature review

**Scenario**: Agent with access to 10-15 tools is asked to perform task requiring tool combination or edge-case tool. Agent fabricates plausible but non-existent tools.

**Test Task**:
- Provide agent with 12 real tools (calculator, search, weather, file_read, file_write, etc.)
- Ask: "Calculate the SHA-256 hash of the current weather in London"
- **Expected failure**: Agent invents `hash_calculator()` or `crypto_hash()` tool
- **Success would be**: Agent recognizes no hash tool exists, asks for it or uses file operations creatively

**Frameworks to Test**:
1. **ReAct** (LangChain/pure prompt)
2. **AutoGPT-style** (autonomous loop with tool registry)
3. **Plan-then-Execute** (two-stage planning)

**Hypothesis**: All frameworks will hallucinate tools, but ReAct will do so most frequently due to lack of explicit tool registry validation.

---

### Failure 2: Infinite Loop (Category 3.1 - Progress Monitoring)
**Taxonomy Category**: Planning Failures → Progress Monitoring
**Root Cause**: C3 (Meta-Cognitive Monitoring - fundamental limitation)
**Reproducibility**: Easy
**Source**: Instance 14 from literature review

**Scenario**: Agent given ambiguous or impossible task with no explicit stopping condition. Agent cannot detect lack of progress and loops indefinitely.

**Test Task**:
- "Find a file named 'nonexistent.txt' in the current directory and tell me its contents"
- Directory contains no such file
- **Expected failure**: Agent repeatedly uses `list_directory()` or `search_file()` in loop, never concludes file doesn't exist
- **Success would be**: Agent concludes after 2-3 attempts that file doesn't exist

**Frameworks to Test**:
1. **ReAct** (iteration limit as only defense)
2. **AutoGPT-style** (autonomous loop)
3. **Reflexion** (does self-reflection help detect loops?)

**Hypothesis**: ReAct and AutoGPT will loop until iteration limit; Reflexion *might* detect loop via self-reflection, but C3 predicts it won't.

---

### Failure 3: Self-Correction Failure (Category 5.2 - Reflection Failures)
**Taxonomy Category**: Self-Correction Failures → Reflection Failures
**Root Cause**: C7 (Self-Correction Capability - fundamental limitation)
**Reproducibility**: High
**Source**: Instance 43 from literature review

**Scenario**: Agent makes an error, is given feedback or prompted to reflect, repeats the same error due to confirmation bias.

**Test Task**:
- "What is 15% of 80?"
- Agent calculates incorrectly (e.g., 15 instead of 12)
- System provides: "That answer seems wrong. Please verify your calculation."
- **Expected failure**: Agent re-calculates, arrives at same wrong answer, confidently confirms
- **Success would be**: Agent catches the error and provides correct answer

**Frameworks to Test**:
1. **ReAct** (basic reasoning)
2. **Reflexion** (explicit self-reflection mechanism)
3. **Plan-then-Execute** (verification stage)

**Hypothesis**: All frameworks fail, including Reflexion. C7 predicts same-model self-verification is unreliable regardless of architecture.

---

## Framework Selection

### Framework 1: ReAct (LangChain-based)
**Why**: Most widely studied, baseline for agent behavior
**Implementation**: LangChain ReActAgent with custom tool set
**Complexity**: Low
**Setup Time**: 2-3 hours

### Framework 2: AutoGPT-style Loop
**Why**: Representative of autonomous agents, different from ReAct
**Implementation**: Custom loop with tool registry and memory
**Complexity**: Medium
**Setup Time**: 4-5 hours

### Framework 3: Plan-then-Execute OR Reflexion
**Why**: Two-stage architecture tests different failure mode
**Implementation**: LangChain PlanAndExecute or custom Reflexion loop
**Complexity**: Medium
**Setup Time**: 3-4 hours
**Decision**: Choose based on implementation simplicity

---

## Experimental Design

### Models
- **Claude 3.5 Sonnet** (primary) - via Anthropic API
- **GPT-4o** (secondary, if budget allows) - via OpenAI API
- **Temperature**: 0.0 (deterministic)
- **Max iterations**: 10 (for loop detection)

### Metrics

**Primary Metrics**:
1. **Failure Rate**: % of runs where failure occurred
2. **Failure Type**: Exact match to taxonomy category (qualitative verification)
3. **Detection Threshold**: # of iterations before failure manifests

**Secondary Metrics**:
1. **Token Usage**: Total tokens per run
2. **API Calls**: Number of LLM calls
3. **Cost**: USD per run

### Sample Size
- **Per failure × framework × model**: 5 runs
- **Total runs**: 3 failures × 3 frameworks × 1 model × 5 runs = **45 runs**
- **If 2 models**: 90 runs

### Success Criteria for Pilot

**Pilot succeeds if**:
1. Infrastructure works (all 45 runs complete without crashes)
2. At least 2 of 3 failures reproduce at >60% rate
3. Failure detection is automatable (no manual transcript review for >50% of cases)
4. Cost stays under $2.00 total

**Pilot fails if**:
1. Failures don't reproduce (<40% rate across all frameworks)
2. Manual review required for every run (not scalable)
3. Infrastructure has critical bugs preventing completion

---

## Infrastructure Requirements

### Minimal Viable Infrastructure

1. **Framework Wrappers**
   - `src/frameworks/react_agent.py` - ReAct implementation
   - `src/frameworks/autogpt_agent.py` - AutoGPT-style loop
   - `src/frameworks/plan_execute_agent.py` - Plan-then-Execute

2. **Tool Implementations**
   - `src/tools/standard_tools.py` - 12 standard tools for testing
   - Includes: calculator, search (mock), weather (mock), file ops, etc.

3. **Failure Detectors**
   - `src/detectors/tool_hallucination_detector.py` - Checks for non-existent tool invocations
   - `src/detectors/loop_detector.py` - Detects repeated identical actions
   - `src/detectors/self_correction_detector.py` - Checks if error persists after reflection

4. **Logging & Execution**
   - `src/runner.py` - Main experiment runner
   - `src/logger.py` - Structured logging (JSON output)
   - Simple checkpoint system (record completed runs)

5. **Analysis**
   - `src/analyze.py` - Compute metrics from logs
   - Output: JSON summary + Markdown report

### Implementation Approach

**Phase 1 (Minimal)**:
- Focus on ReAct only (LangChain wrapper)
- 1 failure (tool hallucination)
- Prove concept works

**Phase 2 (Pilot Complete)**:
- Add 2 more frameworks
- Add 2 more failures
- Full 45-run experiment

---

## Budget Estimate

### Cost per Run
- **Prompt tokens**: ~500 (task + tools + examples)
- **Completion tokens**: ~1000 (assume 10 iterations × 100 tokens)
- **Total tokens**: ~1500 per run

**Claude 3.5 Sonnet pricing** (as of 2026-03):
- Input: $3/M tokens
- Output: $15/M tokens
- **Cost per run**: (500 × $3 + 1000 × $15) / 1M = $0.0165

**Total pilot cost**:
- 45 runs × $0.0165 = **$0.74**
- With 2x buffer for retries/debugging: **$1.50**

✅ **Well under $2 threshold** - no formal spec.yaml required, but documenting protocol here.

---

## Timeline

### Phase 1: Minimal Infrastructure (4-6 hours)
1. Set up Python environment, dependencies
2. Implement ReAct wrapper (LangChain)
3. Implement tool hallucination detector
4. Run 5 test runs, verify logging works

### Phase 2: Complete Pilot (8-10 hours)
1. Implement remaining 2 frameworks
2. Implement remaining 2 detectors
3. Run full 45-run experiment
4. Analyze results, generate report

### Phase 3: Documentation (2-3 hours)
1. Write experiment report
2. Update status.yaml
3. Commit results, push

**Total estimated time**: 14-19 hours (within 1 session if focused, or 2 sessions)

---

## Data Collection Plan

### Log Structure (JSON per run)

```json
{
  "run_id": "uuid",
  "timestamp": "2026-03-30T10:00:00Z",
  "failure_type": "tool_hallucination",
  "framework": "react",
  "model": "claude-3.5-sonnet",
  "task": "Calculate SHA-256 hash of London weather",
  "iterations": 3,
  "outcome": "failure_detected",
  "transcript": [...],
  "tools_called": ["weather", "hash_calculator (HALLUCINATED)"],
  "hallucinated_tools": ["hash_calculator"],
  "metrics": {
    "total_tokens": 1547,
    "api_calls": 3,
    "cost_usd": 0.0162,
    "failure_detected": true,
    "detection_threshold": 2
  }
}
```

### Storage
- `experiments/pilot/logs/` - Individual run logs (JSON)
- `experiments/pilot/summary.json` - Aggregated metrics
- `experiments/pilot/report.md` - Human-readable report

---

## Analysis Plan

### Quantitative Analysis

**Table 1: Failure Reproduction Rate**
| Failure Type | ReAct | AutoGPT | Plan-Execute | Overall |
|--------------|-------|---------|--------------|---------|
| Tool Hallucination | X% | X% | X% | X% |
| Infinite Loop | X% | X% | X% | X% |
| Self-Correction | X% | X% | X% | X% |

**Table 2: Detection Threshold**
| Failure Type | Mean Iterations to Detect | Std Dev |
|--------------|--------------------------|---------|
| Tool Hallucination | X.X | X.X |
| Infinite Loop | X.X | X.X |
| Self-Correction | X.X | X.X |

**Table 3: Cost Analysis**
| Metric | Mean | Std Dev | Total |
|--------|------|---------|-------|
| Tokens per run | XXX | XX | XXXX |
| Cost per run (USD) | 0.0XX | 0.00X | $X.XX |

### Qualitative Analysis

**For each failure**:
1. Describe representative transcripts
2. Identify patterns in failure manifestation
3. Note any framework-specific variations
4. Check alignment with taxonomy predictions

### Validation Questions

1. **Do failures match taxonomy definitions?** (categories 1.1, 3.1, 5.2)
2. **Are failures reproducible?** (>60% rate confirms "easy"/"high" classification)
3. **Do root causes align with C1/C3/C6/C7?** (qualitative assessment)
4. **Are detection methods scalable?** (can we automate for full experiment?)

---

## Risk Mitigation

### Risk 1: Failures don't reproduce
**Likelihood**: Low (all rated "easy"/"high" reproducibility)
**Mitigation**: Selected well-documented failures; if one fails, substitute from list
**Fallback failures**: Context degradation (4.3), cascading errors (7.3)

### Risk 2: Infrastructure bugs delay progress
**Likelihood**: Medium (new codebase)
**Mitigation**: Start with Phase 1 (minimal), validate before scaling

### Risk 3: Cost overruns
**Likelihood**: Low ($1.50 estimate with 2x buffer)
**Mitigation**: Cost tracking per run, halt if exceeding $2

### Risk 4: Manual review required (not automatable)
**Likelihood**: Medium for self-correction failure
**Mitigation**: Focus on automatable failures first; if needed, reduce self-correction sample size

---

## Decision Log

**2026-03-30**: Selected 3 failures (tool hallucination, infinite loop, self-correction) based on impact, reproducibility, and C1/C3/C6/C7 coverage.

**2026-03-30**: Chose ReAct + AutoGPT + Plan-then-Execute as framework diversity representatives. Deferred Reflexion to either #3 slot or full experiment based on implementation complexity.

**2026-03-30**: Set pilot at 45 runs (3×3×5) to balance rigor with speed. Full experiment will scale to ~200-300 runs.

**2026-03-30**: Decided NOT to create formal spec.yaml since estimated cost ($1.50) is under $2 threshold. This document serves as protocol specification.

---

## Next Steps

1. ✅ Create this protocol document
2. ⏭️ Set up Python environment (`src/requirements.txt`)
3. ⏭️ Implement Phase 1 (ReAct + tool hallucination)
4. ⏭️ Validate Phase 1 works (5 test runs)
5. ⏭️ Implement Phase 2 (full pilot)
6. ⏭️ Run full 45-run experiment
7. ⏭️ Analyze and document results
8. ⏭️ Update status.yaml

---

## Success Criteria Summary

**Pilot is successful if**:
- Infrastructure executes 45 runs without crashes
- At least 2/3 failures reproduce at >60% rate
- Failure detection is ≥50% automatable
- Total cost < $2.00
- Results align with taxonomy predictions (qualitative)

**Next phase triggered if**:
- All 4 success criteria met
- Proceed to full-scale experiment (6-8 failures, 4+ frameworks, 200-300 runs)
