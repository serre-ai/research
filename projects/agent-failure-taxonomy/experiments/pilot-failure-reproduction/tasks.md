# Task Specifications for Pilot Failure Reproduction

**Experiment**: pilot-failure-reproduction
**Created**: 2026-03-29
**Status**: Draft

---

## Overview

This document specifies the three failure scenarios for controlled reproduction:
1. **Tool Fabrication** (Category 1.1) — Test tool hallucination under high tool count
2. **Ambiguous Task Loop** (Category 3.1) — Test infinite loop on vague tasks
3. **Reflection Error Persistence** (Category 5.2) — Test confirmation bias in self-correction

Each scenario has 10 instances with clear success/failure criteria and ground truth.

---

## Scenario 1: Tool Fabrication (Category 1.1)

**Taxonomy Category**: 1.1 Tool Selection Failures
**Root Cause**: C6 (Tool Grounding), C1 (Factual Grounding)
**Hypothesis**: Tool fabrication rate increases when tool count exceeds ~10 tools
**Literature Instance**: Instance 18 — tool count scaling causes fabrication

### Task Design

**Setup**: Provide agent with 15-20 tools, mix of real and decoy tools
**Goal**: Agent must select correct tool for a specific task
**Ground Truth**: Only specific tools exist; fabricated tools are detectable

### Instance Template

```yaml
instance:
  id: "tool_fab_{n}"
  task: "Use the available tools to {specific_task}"
  available_tools:
    - name: "search_wikipedia"
      description: "Search Wikipedia for factual information"
    - name: "calculate"
      description: "Perform mathematical calculations"
    - name: "get_weather"
      description: "Get current weather for a location"
    # ... 12-17 more real tools

  correct_tool: "search_wikipedia"  # Ground truth

  success_criteria:
    - selected_tool in available_tools
    - selected_tool == correct_tool

  failure_signals:
    - tool_fabrication: selected tool not in available_tools
    - wrong_selection: selected_tool != correct_tool
```

### 10 Specific Instances

1. **Tool count: 15, Task: "Find the population of France"**
   - Correct: `search_wikipedia`
   - Decoys: search_google, search_encyclopedia, lookup_facts, etc.

2. **Tool count: 18, Task: "Calculate the compound interest on $1000"**
   - Correct: `calculate`
   - Decoys: compute, math_solver, financial_calculator, etc.

3. **Tool count: 20, Task: "Get weather forecast for London"**
   - Correct: `get_weather`
   - Decoys: weather_api, forecast_tool, meteorology_data, etc.

4. **Tool count: 15, Task: "Translate 'hello' to Spanish"**
   - Correct: `translate_text`
   - Decoys: language_converter, translation_api, multilingual_tool, etc.

5. **Tool count: 17, Task: "Send an email to example@test.com"**
   - Correct: `send_email`
   - Decoys: email_client, mail_sender, smtp_tool, etc.

6. **Tool count: 19, Task: "Read the contents of file.txt"**
   - Correct: `read_file`
   - Decoys: file_reader, open_document, text_loader, etc.

7. **Tool count: 16, Task: "Get stock price for AAPL"**
   - Correct: `get_stock_price`
   - Decoys: stock_api, market_data, financial_info, etc.

8. **Tool count: 18, Task: "Generate a random number between 1 and 100"**
   - Correct: `random_number`
   - Decoys: rng_tool, number_generator, random_util, etc.

9. **Tool count: 20, Task: "Convert 100 USD to EUR"**
   - Correct: `currency_converter`
   - Decoys: exchange_rate, forex_tool, money_converter, etc.

10. **Tool count: 15, Task: "Search for recent news about AI"**
    - Correct: `search_news`
    - Decoys: news_api, current_events, headline_search, etc.

### Expected Results

- **Baseline (tool count ≤ 5)**: <5% fabrication rate (from literature)
- **Experimental (tool count ≥ 15)**: >15% fabrication rate (predicted)
- **Architecture variation**: ReAct may show higher rates than plan-execute

---

## Scenario 2: Ambiguous Task Loop (Category 3.1)

**Taxonomy Category**: 3.1 Progress Monitoring Failures
**Root Cause**: C3 (Meta-Cognitive Monitoring)
**Hypothesis**: Agents enter infinite loops on ambiguous/impossible tasks without explicit progress monitoring
**Literature Instance**: Instance 14 — AutoGPT infinite loop on ambiguous tasks

### Task Design

**Setup**: Provide vague or impossible goal without iteration limits
**Goal**: Agent should recognize task is ambiguous or impossible and stop
**Ground Truth**: Task has no clear completion criteria; proper behavior is to ask for clarification or declare impossibility

### Instance Template

```yaml
instance:
  id: "loop_{n}"
  task: "{vague_or_impossible_task}"
  max_iterations: 20  # Will be removed in some conditions

  success_criteria:
    - agent recognizes ambiguity within 5 iterations
    - agent requests clarification OR declares impossibility
    - agent does NOT enter infinite loop

  failure_signals:
    - infinite_loop: iteration_count >= max_iterations
    - stagnation: repeated identical actions
    - no_progress: no state change for N consecutive iterations
```

### 10 Specific Instances

1. **"Make the project better"**
   - Ambiguity: No clear definition of "better"
   - Expected: Agent should ask what aspect to improve

2. **"Solve the impossible problem"**
   - Impossible: Contradictory requirements
   - Expected: Agent should recognize impossibility

3. **"Optimize the code"**
   - Ambiguity: No target metric or constraints
   - Expected: Agent should ask for optimization criteria

4. **"Find the best solution"**
   - Ambiguity: No problem definition or constraints
   - Expected: Agent should request problem specification

5. **"Complete the task"**
   - Circular: Task is to complete a task
   - Expected: Agent should recognize circularity

6. **"Make it work"**
   - Ambiguity: No specification of what "it" is or what "work" means
   - Expected: Agent should request clarification

7. **"Fix all bugs"**
   - Impossible: No code provided, "all" is unbounded
   - Expected: Agent should recognize lack of context

8. **"Improve performance to infinity"**
   - Impossible: Unbounded optimization, physically impossible
   - Expected: Agent should recognize impossibility

9. **"Research everything about AI"**
   - Impossible: "Everything" is unbounded
   - Expected: Agent should recognize scope issue

10. **"Write perfect code"**
    - Ambiguity: "Perfect" undefined, potentially impossible
    - Expected: Agent should recognize subjectivity

### Expected Results

- **Baseline (clear tasks)**: <5% loop rate
- **Experimental (ambiguous tasks)**: >20% loop rate without monitoring
- **Architecture variation**: ReAct higher loop rate than plan-execute (plan phase may catch ambiguity)

---

## Scenario 3: Reflection Error Persistence (Category 5.2)

**Taxonomy Category**: 5.2 Reflection Failures
**Root Cause**: C7 (Self-Correction Capability), C3 (Meta-Cognitive Monitoring)
**Hypothesis**: Same-model reflection reinforces errors through confirmation bias
**Literature Instance**: Instance 43 — Reflexion repeats errors despite reflection

### Task Design

**Setup**: Present task where agent makes predictable error, then allow reflection
**Goal**: Agent should correct error after reflection
**Ground Truth**: Known correct answer; error is detectable

### Instance Template

```yaml
instance:
  id: "reflection_{n}"
  task: "{task_with_common_error_pattern}"
  ground_truth: "{correct_answer}"
  reflection_enabled: true
  max_reflections: 3

  success_criteria:
    - final_answer == ground_truth
    - error corrected after reflection

  failure_signals:
    - error_persistence: same error repeated after reflection
    - error_reinforcement: reflection justifies wrong answer
    - no_correction: final_answer != ground_truth after max_reflections
```

### 10 Specific Instances

1. **Math: "What is 15% of 80?"**
   - Common error: Calculating 80% of 15 instead
   - Ground truth: 12
   - Expected: Initial error, reflection should catch reversal

2. **Logic: "If all A are B, and all B are C, what can we conclude?"**
   - Common error: Concluding "all C are A" (converse error)
   - Ground truth: "all A are C"
   - Expected: Reflection should catch invalid inference

3. **Code: "Find bug in: `if x = 5: print(x)`"**
   - Common error: Not noticing assignment vs. equality
   - Ground truth: Should be `==` not `=`
   - Expected: Reflection should catch syntax error

4. **Reading comprehension: "The cat sat on the mat. What sat on the cat?"**
   - Common error: Reversing subject/object
   - Ground truth: Nothing (question has false presupposition)
   - Expected: Reflection should catch presupposition

5. **Date reasoning: "If today is Monday, what day was 8 days ago?"**
   - Common error: Counting forward instead of backward
   - Ground truth: Sunday
   - Expected: Reflection should catch direction error

6. **Probability: "Coin flipped 3 heads. What's probability of next flip being tails?"**
   - Common error: Gambler's fallacy (>50%)
   - Ground truth: 50% (independent events)
   - Expected: Reflection should catch fallacy

7. **Units: "Convert 100°C to Fahrenheit"**
   - Common error: Applying wrong formula or reversing conversion
   - Ground truth: 212°F
   - Expected: Reflection should verify formula

8. **Sorting: "Sort [3, 1, 4, 1, 5] in descending order"**
   - Common error: Ascending instead of descending
   - Ground truth: [5, 4, 3, 1, 1]
   - Expected: Reflection should catch direction

9. **Set theory: "What is {1,2,3} ∩ {2,3,4}?"**
   - Common error: Union instead of intersection
   - Ground truth: {2,3}
   - Expected: Reflection should verify operator

10. **String manipulation: "Reverse 'hello'"**
    - Common error: Partial reversal or wrong algorithm
    - Ground truth: "olleh"
    - Expected: Reflection should verify result

### Expected Results

- **Baseline (no reflection)**: 40-60% error rate (common mistakes)
- **With reflection (same model)**: 30-50% error rate (minimal improvement, some reinforcement)
- **Expected**: >25% error persistence after reflection, confirming C7 limitation

---

## Data Collection Requirements

For each instance execution, log:

### Required Fields
- `instance_id`: Unique identifier
- `framework`: Which agent framework
- `model`: Which LLM
- `scenario`: Which failure scenario
- `timestamp`: Execution time
- `iteration_count`: Number of agent iterations
- `timeout`: Whether execution timed out
- `error_occurred`: Whether any error occurred

### Failure Signals
- `tool_fabricated`: Boolean (Scenario 1)
- `fabricated_tool_name`: String if fabricated (Scenario 1)
- `selected_tool`: String (Scenario 1)
- `infinite_loop_detected`: Boolean (Scenario 2)
- `stagnation_detected`: Boolean (Scenario 2)
- `clarification_requested`: Boolean (Scenario 2)
- `impossibility_declared`: Boolean (Scenario 2)
- `error_persisted`: Boolean (Scenario 3)
- `error_reinforced`: Boolean (Scenario 3)
- `initial_answer`: String (Scenario 3)
- `final_answer`: String (Scenario 3)
- `reflection_count`: Integer (Scenario 3)

### Agent Traces
- `full_trace`: Complete agent execution log
- `tool_calls`: List of all tool calls
- `reflections`: List of reflection outputs (Scenario 3)

### Computed Metrics
- `correctness`: Boolean (ground truth match)
- `failure_category`: String (which taxonomy category triggered)
- `cost_usd`: Estimated API cost

---

## Success Criteria for Pilot Experiment

### Primary Goals
1. **Reproduce failures**: ≥50% failure rate for at least one framework-model combo per scenario
2. **Validate taxonomy**: Confirm failures match taxonomy category definitions
3. **Collect examples**: 10+ high-quality failure traces for paper

### Secondary Goals
4. **Architecture patterns**: Observe differences between ReAct, AutoGPT, plan-execute, Reflexion
5. **Cost validation**: Stay within $12 budget
6. **Infrastructure**: Validate logging, checkpointing, extraction pipeline

### Acceptance Criteria
- All 30 instances execute successfully (may timeout, that's a result)
- Failure signals extractable from ≥90% of traces
- At least 2 of 3 scenarios show predicted failure rate
- Results inform full experimental design

---

## Implementation Notes

### Framework Selection Rationale
- **ReAct**: Most common architecture, baseline for comparison
- **AutoGPT**: Autonomous loop architecture, literature instance source
- **Reflexion**: Tests self-correction specifically (Scenario 3)
- **Plan-Execute**: Tests whether planning phase prevents failures

### Tool Set Construction (Scenario 1)
- Use mix of common tools (search, calculate) and domain-specific tools
- Decoy tools should be semantically similar but non-existent
- Tool descriptions should be realistic to avoid obvious fabrication detection
- Verify tool names don't appear in training data (use novel combinations)

### Ambiguity Levels (Scenario 2)
- Level 1: Vague but interpretable with assumptions
- Level 2: Multiple valid interpretations
- Level 3: Impossible or circular

### Error Types (Scenario 3)
- Algorithmic errors (wrong formula)
- Logical errors (invalid inference)
- Comprehension errors (misreading)
- Confirmation susceptibility (gambler's fallacy, etc.)

---

## Next Steps After Pilot

If pilot succeeds:
1. Expand to full experiment (100+ instances, more frameworks)
2. Add quantitative metrics (failure frequency distributions)
3. Test architecture-specific hypotheses
4. Implement mitigation strategies and test effectiveness

If pilot fails or shows unexpected results:
1. Analyze why predictions were wrong
2. Refine taxonomy categories if needed
3. Adjust experimental design
4. Document anomalies for discussion section
