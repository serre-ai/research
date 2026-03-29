# Experimental Protocol Design: Agent Failure Taxonomy Validation

**Date**: 2026-03-29
**Purpose**: Design rigorous controlled experiments to validate taxonomy and quantify architecture-failure correlations
**Status**: Draft protocol for pre-registration

---

## Experimental Goals

### Primary Goals
1. **Validate taxonomy categories** — Confirm that documented failure modes are reproducible in controlled settings
2. **Quantify frequency distributions** — Measure how often each failure type occurs across architectures
3. **Test architecture-failure correlations** — Verify claims about which architectures exhibit which failures

### Secondary Goals
4. **Establish baseline infrastructure** — Build reusable framework for future agent experiments
5. **Generate publication-ready data** — Produce tables and figures for paper Results section

---

## Framework Selection

**Criteria**:
- Open source and actively maintained
- Representative of major architectural patterns
- Documented API for programmatic control
- Supports multiple LLM backends
- Well-documented failure modes in literature

**Selected Frameworks** (3 frameworks for pilot):

### 1. **LangGraph** (ReAct pattern)
- **Architecture**: Observation-Reasoning-Action loop
- **Rationale**: Most widely studied pattern; extensive documentation; flexible
- **Expected failures**: Infinite loops (3.1), context exhaustion (4.3), tool hallucination (1.1)
- **API**: LangChain LCEL + graph state management
- **Backend**: OpenAI GPT-4o-mini (cost-effective for pilot)

### 2. **ReAct (Direct Implementation)** (Plan-then-execute variant)
- **Architecture**: Explicit planning phase before execution
- **Rationale**: Tests whether planning reduces certain failures
- **Expected failures**: False completion (5.1), state divergence (4.1)
- **API**: Custom implementation with OpenAI function calling
- **Backend**: OpenAI GPT-4o-mini

### 3. **Anthropic MCP** (Tool-use pattern)
- **Architecture**: Direct tool use without intermediate reasoning steps
- **Rationale**: Modern baseline; tests whether ReAct overhead is necessary
- **Expected failures**: Tool fabrication (1.1), parameter errors (1.2)
- **API**: Anthropic SDK with tool definitions
- **Backend**: Claude 3.5 Sonnet (cross-family validation)

**Deferred to Future Work**:
- AutoGPT (autonomous loop) — requires infrastructure setup
- Reflexion — needs reflection implementation
- Multi-agent frameworks — complexity scope

---

## Failure Mode Selection

**Selection Criteria**:
- High frequency in literature (multiple documented instances)
- High reproducibility (Easy or High in Instance Collection)
- Spans multiple taxonomy categories (validates structure)
- Testable in controlled environment (no production-only failures)
- Cost-effective to test at scale

**Selected Failures** (6 failures for pilot):

### Priority 1: Tool Fabrication (Category 1.1)
**Instance**: #18 — Tool count scaling failures
**Test Design**:
- Provide agent with N tools (vary N = 5, 10, 20, 40)
- Task requires specific tool use
- Measure: fabrication rate (calls to non-existent tools)
**Expected Result**: Fabrication rate increases with tool count
**Architecture Variation**: Should affect all frameworks similarly (LLM-level limitation)
**Budget**: 10 instances × 4 tool counts × 3 frameworks × $0.05/instance = **$6.00**

### Priority 2: Infinite Loops (Category 3.1)
**Instance**: #14 — AutoGPT looping on ambiguous tasks
**Test Design**:
- Provide ambiguous or impossible task
- Measure: iteration count before timeout, action repetition rate
- Timeout: 10 iterations
**Expected Result**: ReAct/LangGraph more susceptible than plan-then-execute
**Architecture Variation**: Testing hypothesis about architectural mitigation
**Budget**: 10 instances × 3 frameworks × $0.10/instance = **$3.00**

### Priority 3: False Completion (Category 5.1)
**Instance**: #19 — False task completion reporting
**Test Design**:
- Multi-step task with objective completion criteria
- Agent must report when complete
- Measure: false positive rate (reports complete when not), false negative rate
**Expected Result**: Higher in frameworks without external verification
**Architecture Variation**: Plan-then-execute may have higher rate
**Budget**: 10 instances × 3 frameworks × $0.08/instance = **$2.40**

### Priority 4: Context Degradation (Category 4.3)
**Instance**: #49 — Performance <50% at 32k tokens
**Test Design**:
- Long conversation with information scattered through context
- Task requires integrating information from early + middle + late context
- Measure: accuracy vs. context length (8k, 16k, 24k tokens)
**Expected Result**: Performance drops at 16k+, especially for middle context
**Architecture Variation**: Minimal (fundamental LLM limitation)
**Budget**: 10 instances × 3 context lengths × 3 frameworks × $0.15/instance = **$13.50**

### Priority 5: Tool Hallucination After Execution (Category 1.2)
**Instance**: #17 — Reasoning-driven tool hallucination
**Test Design**:
- Provide tools with clear output format
- Measure: fabricated tool outputs (agent claims tool returned X when it returned Y)
- Compare: with vs. without CoT prompting
**Expected Result**: CoT increases hallucination rate (C8 trade-off)
**Architecture Variation**: Should affect all, but magnitude may vary
**Budget**: 10 instances × 2 prompting modes × 3 frameworks × $0.08/instance = **$4.80**

### Priority 6: State Divergence (Category 4.1)
**Instance**: #25 — Reports "data deleted" when data still exists
**Test Design**:
- Multi-step task with state changes (create file, modify, delete)
- Agent must track state and report current state
- Measure: state tracking accuracy after each action
**Expected Result**: Accuracy degrades with task length
**Architecture Variation**: Frameworks with external state verification perform better
**Budget**: 10 instances × 3 frameworks × $0.10/instance = **$3.00**

---

## Total Pilot Budget Estimate

| Failure Mode | Instances | Cost |
|--------------|-----------|------|
| Tool Fabrication | 120 | $6.00 |
| Infinite Loops | 30 | $3.00 |
| False Completion | 30 | $2.40 |
| Context Degradation | 90 | $13.50 |
| Tool Hallucination | 60 | $4.80 |
| State Divergence | 30 | $3.00 |
| **Canary runs** | ~50 | $2.00 |
| **Buffer (15%)** | — | $5.20 |
| **TOTAL** | 360+ | **$40.00** |

**Note**: Pilot budget exceeds $2 threshold → **pre-registration required**

---

## Experimental Design Details

### Instance Generation
- **Seed-based**: All instances use deterministic seeds for reproducibility
- **Validation set**: Generate 10 instances per test, hold out 3 for spot-checking
- **Ground truth**: All instances have programmatically verifiable correct answers
- **Difficulty range**: Mix of easy (baseline sanity check) and medium difficulty

### Evaluation Metrics

**Per-failure metrics**:
1. **Tool Fabrication Rate**: `# fabricated calls / # total tool calls`
2. **Loop Detection Rate**: `# loops detected / # instances with loops`
3. **False Completion Rate**: `# false completions / # total instances`
4. **Context Degradation Slope**: `Δ accuracy / Δ context_length`
5. **Hallucination Rate**: `# hallucinated outputs / # tool calls`
6. **State Tracking Accuracy**: `# correct state reports / # state queries`

**Cross-cutting metrics**:
- Task completion rate (successful task finish)
- Cost per instance (API spend)
- Latency per instance (wall-clock time)
- Token usage (input + output tokens)

### Controls
- **Fixed LLM backend per framework** (no confounding model effects in pilot)
- **Temperature = 0.0** (deterministic sampling where possible)
- **Same system prompts across frameworks** (control for prompt effects)
- **Timeout limits** (10 iterations for loops, 5 minutes wall-clock)

### Data Collection Format
JSON logs with:
```json
{
  "instance_id": "string",
  "framework": "langgraph|react|mcp",
  "failure_mode": "tool_fabrication|...",
  "task_description": "string",
  "ground_truth": "object",
  "agent_trajectory": [
    {
      "step": 0,
      "observation": "string",
      "reasoning": "string",
      "action": {"tool": "name", "params": {}},
      "result": "string"
    }
  ],
  "metrics": {
    "completion_status": "success|failure|timeout",
    "failure_detected": true,
    "failure_type": "string",
    "cost_usd": 0.05,
    "latency_seconds": 12.3,
    "tokens": {"input": 1500, "output": 200}
  }
}
```

---

## Success Criteria

### Canary Run (Pre-Full Experiment)
**Must pass ALL criteria before full run**:

1. **Pipeline Completion**: 100% of instances produce parseable output
2. **Extraction Success**: <5% extraction failures (can't parse agent output)
3. **Baseline Sanity**:
   - Tool fabrication: 0-20% on N=5 tools (easy case)
   - Infinite loops: 0% on unambiguous tasks (control instances)
   - False completion: 0-10% on single-step tasks
4. **Cost Within Budget**: Actual cost <2× estimated per-instance cost
5. **Framework Stability**: No framework crashes or unrecoverable errors

### Full Experiment Success
1. **Reproducibility**: At least 4 of 6 failure modes reproduce in controlled setting
2. **Architecture Correlation**: At least 2 architecture-specific patterns confirmed
3. **Quantification**: Frequency distributions for all 6 failure modes
4. **Publication Ready**: Results tables + 2-3 figures generated

---

## Analysis Plan (Pre-Registered)

### Analysis 1: Taxonomy Validation
**Hypothesis**: Documented failure modes from literature reproduce in controlled settings
**Test**: For each failure mode, measure occurrence rate > baseline (0%)
**Success criterion**: ≥4 of 6 failure modes show rate >5%

### Analysis 2: Architecture-Failure Correlation
**Hypothesis**: Different architectures exhibit different failure profiles
**Test**: Chi-square test for independence between architecture and failure type
**Success criterion**: p < 0.05, Cramér's V > 0.3 (medium effect)

### Analysis 3: Tool Count Scaling
**Hypothesis**: Tool fabrication scales with tool count
**Test**: Linear regression of fabrication rate ~ tool count
**Success criterion**: Positive slope, R² > 0.7

### Analysis 4: Context Length Effect
**Hypothesis**: Performance degrades linearly with context length >16k tokens
**Test**: Linear regression of accuracy ~ context length (16k-24k range)
**Success criterion**: Negative slope, p < 0.05

### Analysis 5: CoT Hallucination Trade-off
**Hypothesis**: CoT prompting increases tool hallucination (C8 trade-off)
**Test**: Paired t-test comparing hallucination rate: CoT vs. Direct
**Success criterion**: CoT > Direct, p < 0.05, Cohen's d > 0.5

### Analysis 6: Cross-Framework Comparison
**Hypothesis**: LangGraph (ReAct) has higher loop rate than plan-then-execute
**Test**: Proportion test comparing loop rates
**Success criterion**: LangGraph > ReAct direct, p < 0.05

**Multiple Testing Correction**: Bonferroni correction (α = 0.05/6 = 0.0083)

---

## Infrastructure Requirements

### Code Structure
```
src/
├── frameworks/
│   ├── langgraph_wrapper.py    # LangGraph agent wrapper
│   ├── react_wrapper.py         # ReAct implementation
│   └── mcp_wrapper.py           # Anthropic MCP wrapper
├── tasks/
│   ├── tool_fabrication.py      # Instance generator
│   ├── infinite_loops.py
│   ├── false_completion.py
│   ├── context_degradation.py
│   ├── tool_hallucination.py
│   └── state_divergence.py
├── evaluation/
│   ├── metrics.py               # Metric calculators
│   ├── ground_truth.py          # Answer verification
│   └── trajectory_parser.py     # Extract actions from logs
├── runners/
│   ├── single_instance.py       # Run one instance
│   ├── canary.py                # Canary run orchestrator
│   └── full_experiment.py       # Full run with checkpointing
└── utils/
    ├── logging.py               # Structured logging
    ├── cost_tracking.py         # API cost monitoring
    └── checkpointing.py         # Save/resume state
```

### Dependencies
- `langgraph` (LangChain graph framework)
- `anthropic` (Claude API)
- `openai` (GPT API)
- `pandas`, `numpy` (data analysis)
- `scipy` (statistical tests)
- `pyyaml` (config files)
- `pytest` (unit tests)

---

## Timeline

### Phase 1: Infrastructure (1 session)
- Implement framework wrappers
- Build 1-2 task generators (tool fabrication, infinite loops)
- Create evaluation pipeline
- Write unit tests

### Phase 2: Canary Run (1 session)
- Run 5-10 instances per failure mode
- Validate pipeline completeness
- Check cost estimates
- Debug issues

### Phase 3: Full Run (1-2 sessions)
- Run all 360+ instances
- Monitor for crashes/errors
- Checkpoint progress
- Track budget

### Phase 4: Analysis (1 session)
- Run pre-registered statistical tests
- Generate results tables
- Create publication figures
- Write analysis report

**Total estimated time**: 4-5 sessions (20-25 hours)
**Total estimated cost**: $40 (pilot) + $0 (infrastructure)

---

## Risk Mitigation

### Risk 1: Frameworks are unstable
**Mitigation**: Start with most stable (LangGraph), add others incrementally
**Fallback**: Drop to 2 frameworks if one proves too unreliable

### Risk 2: Cost exceeds budget
**Mitigation**: Canary run with strict cost checks; halt if >2× estimate
**Fallback**: Reduce instance count or framework count

### Risk 3: Failures don't reproduce
**Mitigation**: Start with highest-reproducibility failures (Easy/High)
**Fallback**: Document non-reproduction as negative result (still valuable!)

### Risk 4: Infrastructure takes longer than expected
**Mitigation**: Build incrementally; prioritize 1-2 failures for proof-of-concept
**Fallback**: Defer some failures to future work

---

## Next Steps

1. ✅ **This document** — Protocol design complete
2. **Create pre-registration spec** — `experiments/pilot-validation/spec.yaml`
3. **Submit for critic review** — Wait for approval before implementation
4. **Build infrastructure** — Start with framework wrappers and 1 task
5. **Run canary** — 5-10 instances of tool fabrication as proof-of-concept
6. **Iterate** — Debug issues, refine protocol based on canary results

---

## Design Decisions Log

**Decision 1**: Use 3 frameworks (not 4) for pilot
**Rationale**: ReAct pattern (LangGraph), Plan-then-execute (custom ReAct), Modern baseline (MCP) covers key architectural variations. AutoGPT and Reflexion require more infrastructure. Can expand in future work.

**Decision 2**: Use different LLM backends per framework (GPT-4o-mini vs Claude)
**Rationale**: Validates that failures are architectural, not model-specific. Cross-family comparison is critical. Cost difference is minimal for pilot scale.

**Decision 3**: Prioritize tool-use and planning failures over self-correction
**Rationale**: Tool-use (16 instances) and planning (7 instances) are highest frequency in literature. Self-correction failures (Reflexion) require architecture not in pilot scope.

**Decision 4**: $40 budget for pilot
**Rationale**: 360 instances at $0.05-0.15 each. Conservative estimates with 15% buffer. Well within monthly $1000 platform budget. Can scale up if pilot succeeds.

**Decision 5**: Pre-register 6 analyses
**Rationale**: Prevents p-hacking. Covers taxonomy validation, architecture correlation, and specific theoretical predictions (tool scaling, CoT trade-off). Bonferroni correction keeps false positive rate low.

---

## Protocol Complete

**Status**: Ready for pre-registration and critic review
**Confidence**: High — based on systematic literature review and grounded theory taxonomy
**Next Agent**: Experimenter (self) to create spec.yaml, then Critic for review
