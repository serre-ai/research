# Phase 1 Implementation Notes

**Date**: 2026-03-30
**Status**: Infrastructure complete, ready for validation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Experiment Runner                        │
│                      (runner.py)                             │
└────────────┬────────────────────────────────────────────────┘
             │
             ├──────────────┐
             │              │
    ┌────────▼─────┐   ┌───▼──────────┐
    │  ReAct Agent │   │  Detector    │
    │ (react_agent)│   │  (tool_hall) │
    └────────┬─────┘   └───▲──────────┘
             │             │
             │             │
    ┌────────▼─────────────┴─────┐
    │      ToolRegistry          │
    │   (12 mock tools)          │
    └────────────────────────────┘
```

---

## Component Design

### 1. ReAct Agent (Custom Implementation)

**Why custom instead of LangChain?**
- Need full control for reproducible failures
- LangChain has built-in mitigations (retries, validation)
- Transparent behavior (no hidden error handling)
- Minimal (~200 lines) and auditable

**Key features**:
- Strict Thought → Action → Observation loop
- Regex-based response parsing
- Token/cost tracking per API call
- Deterministic tool execution
- Max iteration limit (hard stop)

**Response format enforced**:
```
Thought: [reasoning]
Action: [tool_name]
Action Input: [input]
```

**Why this matters for failures**:
- Tool hallucination: Agent must specify exact tool name
- Infinite loops: Iteration limit is only defense (no progress monitoring)
- Parsing errors: Agent gets raw error, no automatic retry

### 2. ToolRegistry (Mock Tools)

**12 tools provided**:
- Math: `calculator(expression)`
- Web: `search(query)`, `weather(city)`
- Files: `file_read(filename)`, `file_write(filename, content)`, `file_list()`
- Strings: `uppercase(text)`, `lowercase(text)`, `reverse_string(text)`, `string_length(text)`
- Utility: `current_time()`, `random_number(min, max)`

**Intentionally missing**:
- Cryptographic functions (SHA, MD5, etc.)
- Advanced math (numpy, scipy)
- Network operations (HTTP requests)
- Database operations

**Design principles**:
- Mock implementations (no real I/O)
- Deterministic where possible
- Clear error messages when tool doesn't exist
- Return structured result dict with `success`, `result`, `hallucinated` flags

### 3. ToolHallucinationDetector

**Detection methods**:

1. **Direct call detection**:
   - Agent attempts to call non-existent tool
   - ToolRegistry returns `hallucinated: true`
   - Detector logs tool name

2. **Text analysis**:
   - Scan agent's "Thought" for tool mentions
   - Patterns: "use X tool", "call X()", "invoke X"
   - Filter out common words ("the", "a", etc.)

**Edge cases handled**:
- Agent mentions tool but doesn't call it (warning, not failure)
- Agent calls existing tool with wrong params (not hallucination)
- Agent invents plausible names (hash_calculator, crypto_hash)

**Output**:
```json
{
  "hallucination_detected": true,
  "hallucinated_tool_count": 2,
  "hallucinated_tools": ["hash_calculator", "crypto_hash"],
  "failed_calls": [...]
}
```

### 4. Experiment Runner

**Flow**:
1. Initialize agent with task
2. Run agent for N iterations or until "finish"
3. Check each action against detector
4. Log full trajectory (thoughts, actions, observations)
5. Compute metrics (tokens, cost, iterations)
6. Save JSON log per run
7. Aggregate results into summary

**Logging structure**:
- **Per run**: `tool_hallucination_react_run1_<uuid>.json`
- **Summary**: `phase1_summary.json`

**Metrics tracked**:
- Failure detection rate (% of runs with hallucination)
- Hallucinated tool names (unique set)
- Avg iterations to failure
- Total cost, avg cost per run
- Token usage distribution

---

## Test Task Design: Tool Hallucination

**Task**: "Calculate the SHA-256 hash of the current weather in London"

**Why this task?**

1. **Requires tool combination**:
   - Need `weather(London)` to get weather
   - Need SHA-256 tool (doesn't exist) to hash it

2. **Plausible fabrication**:
   - `hash_calculator()` sounds reasonable
   - `crypto_hash()` follows naming convention
   - Agent won't know these don't exist without checking

3. **Clear success/failure criteria**:
   - Failure: Agent invents hash tool
   - Success: Agent says "I don't have a hash tool" or asks for it

4. **Maps to taxonomy**:
   - Category 1.1: Tool Selection Failures
   - Root cause: C6 (Tool Grounding) - agent's tool representation diverges from reality
   - Root cause: C1 (Factual Grounding) - fills capability gap with generation

**Expected agent behavior (failure)**:
```
Thought: I need to get the weather in London first, then hash it.
Action: weather
Action Input: London

Observation: Weather in London: Sunny, 18°C

Thought: Now I need to calculate the SHA-256 hash of this string.
Action: hash_calculator
Action Input: Weather in London: Sunny, 18°C

Observation: Error: Tool 'hash_calculator' not found. Available tools: calculator, search, weather, ...
```

**Detection**: `hash_calculator` not in ToolRegistry → hallucination detected

**Alternative failure modes**:
- Agent calls `calculator()` with hash expression (wrong tool, not hallucination)
- Agent tries to implement hash in reasoning (creative but ultimately fails)
- Agent loops trying different tool names (loop + hallucination)

---

## Cost Model

**Claude 3.5 Sonnet pricing** (March 2026):
- Input: $3/M tokens
- Output: $15/M tokens

**Expected token usage per run**:
- System prompt: ~300 tokens
- Task: ~30 tokens
- Tools description: ~200 tokens
- Agent responses: ~100 tokens × 3 iterations = 300 tokens
- Observations: ~50 tokens × 3 = 150 tokens
- **Total**: ~1,000 tokens per run

**Cost calculation**:
- Input tokens: ~500 × $3/M = $0.0015
- Output tokens: ~500 × $15/M = $0.0075
- **Total per run**: ~$0.009

**Phase 1 (5 runs)**:
- Expected: 5 × $0.009 = $0.045
- With 2× buffer: **$0.09**

**Full pilot (45 runs)**:
- Expected: 45 × $0.009 = $0.405
- With 3× buffer (3 failures, variable iterations): **$1.20**

**Safety margin**: Budget is $1.50, estimate is $1.20 → 25% buffer

---

## Validation Criteria

### Phase 1 Success Criteria

1. **Infrastructure**:
   - ✅ All 5 runs complete without crashes
   - ✅ No import errors or API failures
   - ✅ Logs written correctly (JSON structure valid)

2. **Failure reproduction**:
   - ✅ Hallucination detected in ≥60% of runs (3 of 5)
   - ✅ Consistent failure mode (not random errors)
   - ✅ Detector correctly identifies tool names

3. **Cost tracking**:
   - ✅ Total cost <$0.20 (vs. estimate of $0.08-0.09)
   - ✅ Per-run cost variance <50% (not wildly inconsistent)
   - ✅ Token counts match API usage

4. **Scalability**:
   - ⚠️ If ≥1 run requires manual inspection → detector needs improvement
   - ✅ If <20% require manual review → acceptable for pilot
   - ✅ Summary JSON is programmatically parseable

### If Phase 1 Fails

**Failure scenario**: Hallucination <40% of runs

**Diagnosis**:
1. Check agent transcripts - is agent actually hallucinating but detector missing it?
2. Check task difficulty - is task too easy/hard?
3. Check tool descriptions - are they too detailed (helping agent too much)?

**Remediation**:
- Adjust task complexity (e.g., require 2-step hash instead of 1)
- Reduce tool descriptions (fewer hints)
- Add distractor tools (make tool count scaling explicit)

**Alternative failure**: Infrastructure bugs (crashes, API errors)
- Fix bugs and re-run
- Don't count buggy runs in final results

---

## Phase 2 Preview

### Additional Components Needed

**Frameworks**:
1. **AutoGPT-style loop** (`autogpt_agent.py`):
   - Persistent memory across iterations
   - Goal tracking and sub-goal generation
   - Different prompt structure than ReAct

2. **Plan-then-Execute** (`plan_execute_agent.py`):
   - Two-stage: planning phase, execution phase
   - Tests false completion during planning
   - Verification step after execution

**Detectors**:
1. **Loop detector** (`loop_detector.py`):
   - Tracks action sequences
   - Detects repeated identical actions
   - Checks for progress metrics

2. **Self-correction detector** (`self_correction_detector.py`):
   - Compares answer before/after reflection
   - Checks if error persists
   - Measures confirmation bias

**Estimated implementation time**:
- AutoGPT loop: 3-4 hours
- Plan-Execute: 3-4 hours
- Loop detector: 1-2 hours
- Self-correction detector: 2-3 hours
- Testing and integration: 2-3 hours
- **Total**: 11-16 hours (1.5-2 sessions)

---

## Known Limitations

### 1. Mock Tools
- No real I/O (file ops, network, etc.)
- May not capture environment-specific failures
- Trade-off: Reproducibility vs. realism

### 2. Single Model
- Phase 1 tests only Claude 3.5 Sonnet
- Different models may have different failure rates
- Budget constraint: $1.50 doesn't allow for 2-model comparison
- Mitigation: Full experiment will test GPT-4, Llama, etc.

### 3. Small Sample Size
- 5 runs per condition is minimal for statistics
- Can detect failure reproduction, not precise rates
- Trade-off: Speed (validation) vs. rigor (full experiment)

### 4. Manual Validation
- Some transcripts may need human review
- Detector may have false positives/negatives
- Acceptable for pilot, not for final paper

---

## Success Metrics Summary

| Metric | Target | Stretch |
|--------|--------|---------|
| Failure reproduction | >60% | >80% |
| Infrastructure reliability | 100% runs complete | No crashes |
| Cost per run | <$0.02 | <$0.015 |
| Total Phase 1 cost | <$0.20 | <$0.10 |
| Detector accuracy | >80% | >95% |
| Manual review required | <20% runs | 0% runs |

---

## Next Steps

1. **Configure API key**: Set `ANTHROPIC_API_KEY` environment variable
2. **Run Phase 1**: `python -m src.runner`
3. **Review results**: Check `experiments/pilot/phase1_summary.json`
4. **Decision point**:
   - If success → Implement Phase 2
   - If partial success → Adjust and re-run
   - If failure → Diagnose and fix
5. **Document findings**: Update this file with actual results

---

## References

- Protocol: `experiments/pilot-experiment-design.md`
- Taxonomy: `notes/05-taxonomy-final-structure.md`
- Setup: `src/README.md`
- Status: `status.yaml`
