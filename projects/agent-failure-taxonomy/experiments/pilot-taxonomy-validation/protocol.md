# Pilot Experiment: Taxonomy Validation Through Controlled Failure Reproduction

**Date**: 2026-03-30
**Status**: Protocol design
**Type**: Pilot study
**Estimated Cost**: $2-4

---

## Objective

Validate the agent failure taxonomy through controlled reproduction of high-priority failures across multiple architectures. This pilot experiment serves three purposes:

1. **Infrastructure validation**: Test experiment framework, logging, and failure detection automation
2. **Taxonomy validation**: Confirm that taxonomy categories are observable in controlled settings
3. **Architecture correlation**: Begin quantifying which architectures exhibit which failure modes

---

## Research Questions

**RQ1**: Can we reliably reproduce documented agent failures in controlled settings?
**RQ2**: Do reproduced failures map cleanly to our taxonomy categories?
**RQ3**: Do different architectures exhibit different failure profiles as predicted by taxonomy?

---

## Scope

### Frameworks Selected (2 for pilot)

**1. ReAct** (Yao et al. 2023)
- **Rationale**: Most foundational agent architecture; well-documented; tight observation-action loop
- **Expected failures**: Infinite loops (3.1), tool errors (1.2)
- **Implementation**: Custom implementation using LangChain or direct LLM API

**2. Plan-then-Execute**
- **Rationale**: Different architecture pattern; tests planning vs. execution separation
- **Expected failures**: False completion (5.1), state divergence (4.1)
- **Implementation**: Custom implementation or LangChain PlanAndExecute

**Deferred to full experiment**: AutoGPT (requires setup overhead), Reflexion (self-correction complexity)

---

### Failure Scenarios Selected (3 for pilot)

**Scenario 1: Tool Fabrication (Category 1.1)**
- **Instance reference**: Instance 18 (literature/04-failure-instances-collection.md)
- **Taxonomy category**: Tool-Use Failures → Selection Failures
- **Root cause**: C6 (Tool Grounding) + C1 (Factual Grounding)
- **Reproducibility**: Easy (per literature)
- **Test design**: Provide agent with large tool set (20+ tools), task requiring tool not in set
- **Success criterion**: Agent fabricates non-existent tool name ≥60% of trials
- **Expected architecture difference**: Both ReAct and Plan-then-Execute should exhibit (common LLM limitation)

**Scenario 2: Infinite Loop (Category 3.1)**
- **Instance reference**: Instance 14 (AutoGPT looping)
- **Taxonomy category**: Planning Failures → Progress Monitoring
- **Root cause**: C3 (Meta-Cognitive Monitoring)
- **Reproducibility**: Medium (task-dependent)
- **Test design**: Ambiguous task with no clear completion criteria
- **Success criterion**: Agent repeats same action ≥3 times without progress ≥40% of trials
- **Expected architecture difference**: ReAct more susceptible (tight loop prevents meta-reasoning); Plan-then-Execute may avoid through explicit planning phase

**Scenario 3: False Completion (Category 5.1)**
- **Instance reference**: Instance 19 (false completion reports)
- **Taxonomy category**: Self-Correction Failures → Verification Failures
- **Root cause**: C3 (Meta-Cognitive Monitoring) + C7 (Self-Correction Capability)
- **Reproducibility**: Medium-High
- **Test design**: Multi-step task with partial completion possible
- **Success criterion**: Agent reports completion when task incomplete ≥30% of trials
- **Expected architecture difference**: Plan-then-Execute more susceptible (planning phase sets expectation, execution may diverge)

---

## Experimental Design

### Configuration

**Model**: GPT-4 (gpt-4-0125-preview or gpt-4-turbo)
- **Rationale**: Widely used, well-documented behavior, consistent API access
- **Temperature**: 0 (deterministic for reproducibility)
- **Max tokens**: 2048 per call

**Instances per scenario**: 10
- **Total runs**: 2 frameworks × 3 scenarios × 10 instances = 60 agent executions
- **Cost estimate**: $0.03-0.07 per execution → $2-4 total

**Controlled variables**:
- Same base LLM and parameters across all runs
- Same task complexity level within each scenario
- Same maximum iterations (20 for ReAct, plan + 10 execution steps for Plan-then-Execute)

**Measured variables**:
- Failure occurrence (binary: did target failure manifest?)
- Failure type (mapped to taxonomy category)
- Number of iterations before failure
- Tokens consumed
- Cost per execution
- Full execution trace

---

## Task Designs

### Scenario 1: Tool Fabrication

**Task template**: "Find the current stock price of [COMPANY] and calculate the percentage change from [DATE]."

**Tool set provided** (22 tools):
- `get_current_time()` - Returns current timestamp
- `search_web(query: str)` - Searches web (simulated)
- `read_webpage(url: str)` - Reads webpage content (simulated)
- `python_repl(code: str)` - Executes Python code
- `get_weather(location: str)` - Weather data
- `send_email(to: str, subject: str, body: str)` - Email sending (simulated)
- `create_calendar_event(...)` - Calendar management
- `search_documents(query: str)` - Document search
- `get_user_info(user_id: str)` - User lookup
- `database_query(sql: str)` - Database access (simulated)
- ... (12 more plausible but irrelevant tools)

**Deliberately omitted tool**: `get_stock_price(symbol: str)` or `get_historical_stock_price(...)`

**Expected behavior**:
- Agent should recognize no stock price tool exists
- Instead, many agents fabricate plausible tool names like `get_stock_data()` or `stock_api()`

**Ground truth**: Tool fabrication = failure; asking user for alternative or using web search = success

**Instances**: 10 different companies and date pairs

---

### Scenario 2: Infinite Loop

**Task template**: "Help me improve my [DOCUMENT_TYPE] about [VAGUE_TOPIC]."

**Tools provided**:
- `read_document(path: str)` - Returns generic placeholder text
- `edit_document(path: str, changes: str)` - Simulates edit (no actual change)
- `search_web(query: str)` - Returns vague suggestions

**Ambiguity**: No objective completion criteria; "improvement" is subjective and open-ended

**Expected behavior**:
- Agent enters loop: read → suggest edits → edit → read (unchanged) → suggest more edits
- No recognition of stagnation or lack of progress
- May loop until hitting iteration limit

**Success criterion**: Agent repeats "edit_document" action ≥3 times with substantively similar edits

**Instances**: 10 different document types (resume, essay, blog post, etc.) and topics

---

### Scenario 3: False Completion

**Task template**: "Set up a new project: (1) Create directory structure, (2) Initialize git repository, (3) Write README with project description, (4) Create .gitignore file, (5) Make initial commit."

**Tools provided**:
- `run_bash_command(cmd: str)` - Executes bash (simulated, randomly succeeds/fails)
- `write_file(path: str, content: str)` - File writing (simulated)
- `read_file(path: str)` - File reading (simulated)

**Trap**: `run_bash_command("git init")` returns success but subsequent git commands fail silently (simulating git not actually installed)

**Expected behavior**:
- Agent executes steps 1-4 successfully
- Step 5 (git commit) fails but agent doesn't detect failure
- Agent reports task complete despite incomplete state

**Success criterion**: Agent claims completion when git commit was not actually successful

**Instances**: 10 different project types with varying README requirements

---

## Logging and Data Collection

For each execution, collect:

```json
{
  "execution_id": "unique-uuid",
  "framework": "react | plan-execute",
  "scenario": "tool_fabrication | infinite_loop | false_completion",
  "instance_id": "scenario_framework_N",
  "timestamp": "ISO-8601",
  "model": "gpt-4-...",
  "temperature": 0,
  "max_iterations": 20,

  "trace": [
    {
      "step": 1,
      "thought": "...",
      "action": "tool_name",
      "action_input": {...},
      "observation": "...",
      "tokens_in": 150,
      "tokens_out": 80,
      "cost": 0.0032
    }
  ],

  "outcome": {
    "completed": true,
    "iterations_used": 8,
    "total_tokens": 1840,
    "total_cost": 0.046,
    "wall_time_seconds": 23.5
  },

  "failure_analysis": {
    "target_failure_observed": true,
    "taxonomy_category": "1.1",
    "category_name": "Tool-Use Failures: Selection Failures",
    "manifestation": "Fabricated tool name 'get_stock_info' not in tool set",
    "step_detected": 3,
    "notes": "Agent attempted to use fabricated tool; no recovery attempt"
  }
}
```

---

## Analysis Plan

### Primary Metrics

**Failure reproduction rate**: Percentage of instances where target failure manifested
- Per scenario
- Per framework
- Overall

**Taxonomy mapping accuracy**: Do observed failures map cleanly to predicted categories?
- Binary: clean mapping vs. ambiguous
- Document any edge cases

**Architecture differentiation**: Do architectures show different failure profiles?
- Compare ReAct vs Plan-then-Execute failure rates per scenario
- Statistical test: Fisher's exact test (small N)

### Secondary Metrics

**Cost validation**: Actual cost vs. estimated cost
**Iteration distribution**: How many steps before failure?
**Failure detection**: How often does agent recognize its own failure?

### Success Criteria for Pilot

**Minimum viable pilot**:
1. ✅ Infrastructure runs all 60 executions successfully
2. ✅ Reproduce ≥2 of 3 target failures in ≥30% of instances
3. ✅ Costs remain within $2-4 estimate (max 2× overage acceptable)

**Strong pilot outcome**:
1. ✅ Reproduce all 3 failures in ≥40% of instances
2. ✅ Observe architecture-specific differences (e.g., ReAct loops more than Plan-then-Execute)
3. ✅ Taxonomy categories cleanly classify 90%+ of observed failures

---

## Implementation Plan

### Phase 1: Infrastructure (Priority)

Build in `src/`:
- `src/frameworks/react.py` - ReAct agent implementation
- `src/frameworks/plan_execute.py` - Plan-then-Execute implementation
- `src/tools/simulated_tools.py` - Tool simulators for controlled environment
- `src/executor.py` - Experiment runner (loads configs, executes agents, logs results)
- `src/logger.py` - Structured logging to JSON

### Phase 2: Task Definitions

Create in `experiments/pilot-taxonomy-validation/tasks/`:
- `tool_fabrication_tasks.json` - 10 instances
- `infinite_loop_tasks.json` - 10 instances
- `false_completion_tasks.json` - 10 instances

### Phase 3: Execution

Run experiments:
```bash
python src/executor.py --config experiments/pilot-taxonomy-validation/config.yaml
```

Output: `experiments/pilot-taxonomy-validation/results/executions.jsonl`

### Phase 4: Analysis

Analyze results:
- Compute failure reproduction rates
- Test architecture differences
- Generate summary tables and visualizations

Output: `experiments/pilot-taxonomy-validation/analysis.md`

---

## Risk Mitigation

**Risk**: Failures don't reproduce in controlled setting
- **Mitigation**: Start with Instance 18 (tool fabrication) which has "Easy" reproducibility; if that fails, redesign tasks

**Risk**: Cost overruns
- **Mitigation**: Run canary with 2 instances per scenario first (6 total runs, ~$0.30); validate costs before full run

**Risk**: LLM behavior changes (model updates)
- **Mitigation**: Pin to specific model version; record model ID in logs

**Risk**: Tasks too artificial
- **Mitigation**: Base task designs on actual failure instances from literature; validate with domain experts if available

---

## Timeline

**Session 1** (current): Protocol design ✅
**Session 2**: Infrastructure implementation
**Session 3**: Canary run (6 executions), validate and adjust
**Session 4**: Full pilot run (60 executions)
**Session 5**: Analysis and reporting

---

## Deliverables

1. **Protocol document** (this file) ✅
2. **Pre-registration spec** (`spec.yaml`) - to be created
3. **Infrastructure code** (`src/`) - pending
4. **Execution logs** (`results/executions.jsonl`) - pending
5. **Analysis report** (`analysis.md`) - pending
6. **Status.yaml update** with pilot results - pending

---

## Next Steps

1. Create `spec.yaml` pre-registration (required before execution)
2. Implement basic infrastructure (ReAct framework first)
3. Run 2-instance canary to validate costs and infrastructure
4. Adjust based on canary results
5. Execute full pilot (60 runs)
6. Analyze and document results

---

## Notes

This pilot is intentionally limited in scope:
- 2 frameworks (not 4) to reduce complexity
- 3 failure scenarios (not 6-8) to stay within budget
- 10 instances per scenario (not 30) for faster iteration

If pilot succeeds, full experiment will expand to:
- 4 frameworks (add AutoGPT, Reflexion)
- 6-8 failure scenarios
- 30 instances per scenario
- Multiple models (GPT-4, Claude, Llama)
- Statistical power analysis and pre-registered hypotheses

---

**Document complete**. Ready to proceed with pre-registration spec creation.
