# Experimental Protocol: Pilot Failure Reproduction Study

**Date**: 2026-03-29
**Status**: Design phase
**Purpose**: Validate taxonomy categories through controlled reproduction of high-priority failures across multiple agent frameworks

---

## Research Objectives

### Primary Goals
1. **Validate taxonomy applicability**: Confirm that our 9-category taxonomy accurately categorizes failures across different agent architectures
2. **Establish reproducibility**: Demonstrate that documented failures can be systematically reproduced in controlled settings
3. **Quantify architecture-failure correlation**: Measure which architectures exhibit which failure types at what frequencies
4. **Infrastructure validation**: Build and test evaluation infrastructure for full-scale experiments

### Secondary Goals
5. **Cost estimation**: Validate budget estimates for full experimental validation
6. **Methodology refinement**: Identify issues in experimental setup before scaling
7. **Baseline measurements**: Establish baseline failure rates for comparison in future work

---

## Framework Selection

Based on taxonomy coverage and architectural diversity:

### 1. ReAct (Yao et al. 2023)
**Architecture**: Reasoning + acting in interleaved loop
**Why selected**: Most-studied agent architecture, high prevalence in literature (22% of instances)
**Implementation**: LangChain ReAct agent with GPT-4 and Claude-3.5-Sonnet
**Expected failures**: Infinite loops (3.1), tool hallucination (1.1), context exhaustion (4.3)

### 2. LangGraph Plan-then-Execute
**Architecture**: Hierarchical planning with execution separation
**Why selected**: Represents plan-then-execute paradigm, different failure profile than ReAct
**Implementation**: LangGraph with explicit planning and execution phases
**Expected failures**: False completion (5.1), state divergence (4.1), partial satisfaction (3.2)

### 3. AutoGPT (Autonomous Loop)
**Architecture**: Fully autonomous multi-step execution with memory
**Why selected**: Production system with documented failures, autonomous loop architecture
**Implementation**: AutoGPT v0.5+ or similar autonomous agent
**Expected failures**: Infinite loops (3.1), memory corruption (4.2), web hallucinations (2.2)

### 4. Reflexion (Shinn et al. 2023)
**Architecture**: Self-reflection with episodic memory
**Why selected**: Tests self-correction limitations (C7), unique reflection mechanism
**Implementation**: Reflexion framework with Actor-Evaluator-Reflector
**Expected failures**: Confirmation bias (5.2), degeneration-of-thought (5.2), complexity plateaus (5.2)

**Total**: 4 frameworks × 2 models (GPT-4, Claude-3.5) = 8 architecture-model combinations

---

## Failure Selection

Selected for high priority (frequency + severity), reproducibility, and taxonomy coverage:

### Priority 1: Tool Fabrication (Category 1.1)
**Taxonomy**: Tool-use failures → Selection failures
**LLM Limitation**: C6 (Tool Grounding) + C1 (Factual Grounding)
**Source Instance**: Instance 18 — tool count scaling causes fabrication
**Reproduction Task**: Provide agent with 20+ tools, require selection for ambiguous task
**Success Criteria**: Agent invents non-existent tool name in ≥30% of trials
**Expected Architectures**: All, especially ReAct and AutoGPT

---

### Priority 2: Infinite Loops (Category 3.1)
**Taxonomy**: Planning failures → Progress monitoring
**LLM Limitation**: C3 (Meta-Cognitive Monitoring)
**Source Instance**: Instance 14 — AutoGPT loops on ambiguous tasks
**Reproduction Task**: Ambiguous task with no clear stopping condition (e.g., "research topic X thoroughly")
**Success Criteria**: Agent repeats same action ≥5 times without progress in ≥50% of trials
**Expected Architectures**: ReAct, AutoGPT (tight loops prevent meta-reasoning)

---

### Priority 3: False Completion (Category 5.1)
**Taxonomy**: Self-correction failures → Verification failures
**LLM Limitation**: C3 (Meta-Cognitive Monitoring) + C7 (Self-Correction)
**Source Instance**: Instance 19 — reports task complete when incomplete
**Reproduction Task**: Multi-step task with complex requirements, rely on agent's completion signal
**Success Criteria**: Agent signals completion with ≥1 requirement unsatisfied in ≥25% of trials
**Expected Architectures**: Plan-then-execute, AutoGPT

---

### Priority 4: Context Degradation (Category 4.3)
**Taxonomy**: State tracking failures → Context management
**LLM Limitation**: C2 (Long-Range Coherence) — FUNDAMENTAL
**Source Instance**: Instance 49 — performance < 50% at 32k tokens
**Reproduction Task**: Task requiring information from early context after 16k, 24k, 32k tokens
**Success Criteria**: Accuracy drops ≥20% from 8k to 32k context in ≥70% of model-task combinations
**Expected Architectures**: All (fundamental limitation)

---

### Priority 5: Confirmation Bias in Reflection (Category 5.2)
**Taxonomy**: Self-correction failures → Reflection failures
**LLM Limitation**: C7 (Self-Correction Capability) — FUNDAMENTAL for same-model
**Source Instance**: Instance 43 — Reflexion repeats same error despite reflection
**Reproduction Task**: Task where initial approach is plausible but wrong, measure if reflection corrects
**Success Criteria**: Agent maintains incorrect approach after reflection in ≥40% of trials
**Expected Architectures**: Reflexion (by design), possibly ReAct with self-reflection prompts

---

### Priority 6: State Divergence (Category 4.1)
**Taxonomy**: State tracking failures → State divergence
**LLM Limitation**: C5 (State Tracking)
**Source Instance**: Instance 25 — reports "data deleted" when data still exists
**Reproduction Task**: File manipulation task, measure agent's internal state vs. actual file system state
**Success Criteria**: Agent's state report differs from ground truth in ≥30% of trials
**Expected Architectures**: All, especially AutoGPT and plan-then-execute

---

## Task Design

### General Principles
1. **Deterministic evaluation**: All tasks have verifiable ground truth
2. **Controlled difficulty**: Tasks designed to trigger specific failures
3. **Minimal confounds**: Isolate target failure mode from other potential issues
4. **Realistic scenarios**: Tasks reflect real-world agent use cases
5. **Automated detection**: Failure detection does not require manual review

---

### Task 1: Tool-Count Scaling (Tool Fabrication)
**Setup**:
- Provide agent with 25 tools (20 real, 5 plausible decoys that don't exist)
- Task: "Find the current weather in Berlin"
- Tools include: weather APIs, web search, file operations, math tools, etc.
- Correct tool: `get_weather(location)`

**Ground Truth**: Agent should select `get_weather` tool

**Failure Detection**:
- Parse tool calls from agent trace
- Check if any called tool is not in the provided tool registry
- Flag as "tool fabrication" if agent invents tool name

**Measurement**:
- Tool fabrication rate (% trials with fabricated tools)
- Correct tool selection rate
- Tool confusion rate (selects wrong real tool)

**Expected Outcome**: As tool count increases, fabrication rate increases (C6 limitation)

---

### Task 2: Ambiguous Research Task (Infinite Loops)
**Setup**:
- Task: "Research the history of neural networks and summarize key developments"
- No explicit stopping condition
- Provide web search tool and note-taking tool
- Set iteration limit at 20 steps

**Ground Truth**: Agent should stop after gathering sufficient information (subjective, but detectable)

**Failure Detection**:
- Track action sequences
- Detect if same action (e.g., "search for 'neural network history'") repeated ≥3 times
- Measure progress: unique information gathered per step
- Flag "infinite loop" if ≥5 consecutive steps add no new information

**Measurement**:
- Loop detection rate (% trials with ≥5 repeated actions)
- Progress stagnation rate (% trials with ≥5 steps without new info)
- Average iterations before stopping

**Expected Outcome**: ReAct and AutoGPT loop more frequently than plan-then-execute (C3 limitation)

---

### Task 3: Multi-Step File Task (False Completion)
**Setup**:
- Task: "Create a file `report.txt` with the current date, search for weather in London, and append the weather to the file"
- Three clear requirements: (1) create file, (2) get weather, (3) append to file
- Agent must signal "task complete" when done

**Ground Truth**: All 3 requirements satisfied

**Failure Detection**:
- After agent signals completion, check file system:
  - Does `report.txt` exist? (requirement 1)
  - Does it contain a date string? (requirement 1)
  - Does it contain weather information? (requirement 2 + 3)
- Flag "false completion" if agent signals done but any requirement unsatisfied

**Measurement**:
- False completion rate (% trials where agent signals done but requirements unmet)
- Partial satisfaction rate (% trials where 1-2 of 3 requirements met)
- Overcorrection rate (% trials where agent never signals completion despite success)

**Expected Outcome**: Plan-then-execute and AutoGPT exhibit false completion (C3 + C7 limitation)

---

### Task 4: Long-Context Retrieval (Context Degradation)
**Setup**:
- Provide document with key fact at position P (varied: beginning, 25%, 50%, 75%, end)
- Pad context to target length (8k, 16k, 24k, 32k tokens)
- Task: "What is [specific fact] mentioned in the document?"

**Ground Truth**: Specific fact from position P

**Failure Detection**:
- Compare agent's answer to ground truth fact
- Binary: correct or incorrect
- Measure accuracy as function of context length and position

**Measurement**:
- Accuracy vs. context length curve
- Positional bias: accuracy at beginning vs. middle vs. end
- Degradation rate: slope of accuracy decline

**Expected Outcome**: All architectures show <50% accuracy at 32k tokens with middle-positioned facts (C2 fundamental limitation)

---

### Task 5: Incorrect Initial Strategy (Confirmation Bias)
**Setup**:
- Task with plausible but incorrect approach that seems reasonable
- Example: "Sort this list: [5, 3, 8, 1, 9]" but provide subtly broken sorting algorithm as context
- Reflexion framework: Actor tries, Evaluator assesses, Reflector suggests improvement

**Ground Truth**: Correctly sorted list [1, 3, 5, 8, 9]

**Failure Detection**:
- Track whether agent's approach changes after reflection
- Measure if error persists across reflection cycles
- Flag "confirmation bias" if same error appears in ≥3 consecutive attempts

**Measurement**:
- Error persistence rate across reflection cycles
- Correction success rate (% trials where reflection leads to correct answer)
- Degeneration rate (% trials where performance worsens with reflection)

**Expected Outcome**: Reflexion shows ≥40% error persistence despite reflection (C7 fundamental limitation for same-model)

---

### Task 6: File Manipulation with State Tracking (State Divergence)
**Setup**:
- Task: "Create file `test.txt`, write 'hello', delete it, then tell me if the file exists"
- Agent performs actions and must report final state
- Ground truth: file should NOT exist after deletion

**Failure Detection**:
- After agent reports state, check actual file system
- Compare agent's state claim to ground truth
- Flag "state divergence" if agent's report differs from reality

**Measurement**:
- State divergence rate (% trials with incorrect state report)
- Direction of divergence (false positive vs. false negative)
- State reconciliation attempts (does agent verify before reporting?)

**Expected Outcome**: All architectures show ≥30% state divergence without external verification (C5 limitation)

---

## Experimental Design

### Models
- **GPT-4-turbo** (OpenAI): Baseline, most capable general model
- **Claude-3.5-Sonnet** (Anthropic): Alternative frontier model, different training

**Rationale**: 2 models × 4 frameworks = 8 conditions; sufficient for pilot while managing costs

---

### Sample Size (Pilot)
- **Per failure type**: 20 trials per framework-model combination
- **Total trials**: 6 failures × 4 frameworks × 2 models × 20 trials = 960 trials
- **Canary run**: 5 trials per combination = 120 trials

**Power analysis**: With 20 trials per condition, can detect effect sizes of d ≥ 0.6 at 80% power

---

### Controlled Variables
- Temperature: 0.0 (deterministic, reduce sampling variance)
- System prompt: Standardized per framework
- Tool descriptions: Identical across frameworks
- Timeout: 5 minutes per trial
- Max iterations: 20 steps per trial

---

### Randomization
- Trial order randomized
- For tasks with position-dependent effects (Task 4), counterbalance positions
- Tool orderings randomized (Task 1)

---

## Data Collection

### Per-Trial Logging
Record for each trial:
1. **Metadata**: trial_id, framework, model, task, timestamp
2. **Input**: full task description, tools provided, ground truth
3. **Trace**: complete agent execution trace (all observations, thoughts, actions)
4. **Output**: agent's final answer or action sequence
5. **Evaluation**: binary success/failure, detected failure types, metrics
6. **Cost**: API calls, tokens, latency, estimated USD cost

**Format**: JSON Lines (one JSON object per trial)

---

### Checkpoint System
- **Purpose**: Enable recovery from crashes, avoid re-running completed trials
- **Format**: `checkpoint-{framework}-{model}-{task}.json` with list of completed trial IDs
- **Update frequency**: After every 10 trials

---

### Cost Tracking
- **Per trial**: log tokens (input + output) and compute cost based on model pricing
- **Cumulative**: running total across all trials
- **Budget limit**: Stop if cumulative cost exceeds $4.50 (leaving $0.50 buffer from $5 total)

---

## Success Criteria

### Infrastructure Validation
- [ ] All 4 frameworks successfully execute at least 1 trial each
- [ ] Automated failure detection achieves ≥95% agreement with manual review on 20-sample validation set
- [ ] Checkpoint system successfully recovers from simulated crash
- [ ] Cost per trial within 2× of estimate

---

### Taxonomy Validation
- [ ] ≥4 of 6 targeted failure types successfully reproduced in controlled setting
- [ ] Reproduced failures match taxonomy category definitions
- [ ] Failure categorization shows inter-rater reliability κ ≥ 0.7 (if manual coding needed)

---

### Architecture-Failure Correlation
- [ ] ≥2 significant architecture effects detected (p < 0.05 with Bonferroni correction)
- [ ] Effect sizes match theoretical predictions (e.g., ReAct loops more than plan-then-execute)
- [ ] Fundamental limitations (C2, C3, C7) show consistent failure rates across architectures

---

### Budget Adherence
- [ ] Total pilot cost ≤ $5.00
- [ ] Per-trial cost estimates accurate within 2× for full-scale planning

---

## Analysis Plan

### Primary Analyses (Pre-registered)

#### Analysis 1: Failure Reproduction Validation
**Hypothesis**: Each of 6 targeted failure types can be reproduced at ≥20% base rate
**Method**: Proportion test for each failure type across all conditions
**Metric**: Failure occurrence rate with 95% CI (Wilson score interval)
**Success**: ≥4 of 6 failure types occur at p ≥ 0.20

---

#### Analysis 2: Architecture-Failure Correlation
**Hypothesis**: Failure rates differ significantly across architectures as predicted by taxonomy
**Method**: Chi-square test for independence (architecture × failure type)
**Effect size**: Cramér's V
**Predictions**:
- ReAct shows higher loop rate than plan-then-execute (p < 0.05)
- Reflexion shows higher confirmation bias than others (p < 0.05)
- Context degradation shows NO architecture effect (fundamental limitation)

---

#### Analysis 3: Model Comparison
**Hypothesis**: GPT-4 and Claude-3.5 show similar failure profiles (failure is architectural, not model-specific)
**Method**: Proportion test for each failure type across models
**Metric**: Absolute difference in failure rates
**Success**: No failure type shows >20% absolute difference between models

---

#### Analysis 4: Fundamental vs. Correctable Distinction
**Hypothesis**: Fundamental limitations (C2, C3, C7) show high failure rates across all architectures; correctable limitations (C4, C5, C6) show architecture-dependent rates
**Method**: Mixed-effects logistic regression with failure type (fundamental vs. correctable) and architecture as predictors
**Metric**: Interaction term significance
**Success**: Significant interaction (p < 0.05) indicating differential architecture effects

---

### Secondary Analyses (Exploratory)

1. **Cost-performance trade-off**: Do more expensive models (more tokens, more reasoning) exhibit different failure profiles?
2. **Iteration count effects**: Do failures occur more frequently in early vs. late iterations?
3. **Cascading failures**: Do multiple failure types co-occur in single trials?

---

## Mitigation Validation (Future Work)

Not included in pilot but designed for follow-up:

1. **External monitoring**: Add progress detection module, measure loop reduction
2. **External verification**: Add state verification step, measure false completion reduction
3. **Multi-model reflection**: Use different model for reflection, measure confirmation bias reduction
4. **Tool retrieval**: Use embedding-based tool selection, measure fabrication reduction

**Pilot focus**: Establish baseline failure rates before testing mitigations

---

## Timeline

### Week 1 (Current)
- [x] Design experimental protocol
- [ ] Create pre-registration spec
- [ ] Build framework wrappers and logging infrastructure
- [ ] Implement automated failure detection for all 6 failure types

### Week 2
- [ ] Run canary experiment (120 trials, ~$0.50)
- [ ] Validate infrastructure and refine based on canary results
- [ ] Run full pilot experiment (960 trials, ~$4.50)

### Week 3
- [ ] Analyze results (4 pre-registered analyses)
- [ ] Generate figures (failure distribution, architecture correlation matrix)
- [ ] Write analysis report
- [ ] Update taxonomy based on empirical findings

---

## Budget Estimate

### Cost Model
**Assumptions**:
- GPT-4-turbo: $10/1M input tokens, $30/1M output tokens
- Claude-3.5-Sonnet: $3/1M input tokens, $15/1M output tokens
- Average trial: 2k input tokens, 1k output tokens
- Tool descriptions add ~500 tokens per trial

**Per-trial estimates**:
- GPT-4: (2.5k × $10 + 1k × $30) / 1M = $0.055
- Claude-3.5: (2.5k × $3 + 1k × $15) / 1M = $0.0225
- Weighted average (50/50): $0.039

**Canary run**: 120 trials × $0.039 = $4.68
**Full pilot**: 960 trials × $0.039 = $37.44

**Adjustment for session budget**: Run 6 failures × 2 frameworks × 2 models × 10 trials = 240 trials
**Adjusted cost**: 240 trials × $0.039 = $9.36 → Too high for $5 budget

**Revised pilot scope**: 6 failures × 2 frameworks × 2 models × 5 trials = 120 trials
**Revised cost**: 120 trials × $0.039 = $4.68 ≈ $5.00 ✓

**Final sample size**: 5 trials per framework-model-failure combination

---

## Risks and Limitations

### Technical Risks
1. **Framework compatibility**: Different frameworks may require different task formats
2. **Failure detection accuracy**: Automated detection may miss subtle failures
3. **Cost overruns**: Agents may generate more tokens than estimated

**Mitigation**: Canary run validates all infrastructure before full pilot

---

### Scientific Limitations
1. **Small sample size**: 5 trials per condition limits statistical power
2. **Framework versions**: Results specific to current framework implementations
3. **Task generalization**: 1 task per failure type may not capture all variants
4. **Model selection**: Only 2 models tested (GPT-4, Claude-3.5)

**Mitigation**: Pilot is for validation, not definitive; full-scale experiments follow

---

### Scope Constraints
1. **No mitigation testing**: Pilot establishes baselines only
2. **No multi-agent**: Focus on single-agent architectures
3. **No production data**: Controlled tasks, not real-world complexity

**Mitigation**: Clearly scope pilot as infrastructure validation and baseline establishment

---

## Deliverables

### Code
- [ ] `src/frameworks/react_agent.py` — ReAct implementation
- [ ] `src/frameworks/plan_execute_agent.py` — LangGraph plan-then-execute
- [ ] `src/frameworks/autogpt_agent.py` — AutoGPT wrapper (if feasible; may use alternative autonomous loop)
- [ ] `src/frameworks/reflexion_agent.py` — Reflexion implementation
- [ ] `src/tasks/` — 6 task implementations with ground truth and failure detection
- [ ] `src/evaluation/detector.py` — Automated failure detection
- [ ] `src/evaluation/runner.py` — Experiment execution with checkpointing
- [ ] `src/analysis/analyze.py` — Statistical analysis scripts

### Data
- [ ] `experiments/pilot-reproduction/data/trials.jsonl` — All trial results
- [ ] `experiments/pilot-reproduction/data/checkpoints/` — Recovery checkpoints
- [ ] `experiments/pilot-reproduction/data/costs.json` — Cost tracking

### Results
- [ ] `experiments/pilot-reproduction/results/analysis-report.md` — Full statistical analysis
- [ ] `experiments/pilot-reproduction/results/figures/` — Publication-ready figures
- [ ] `experiments/pilot-reproduction/results/summary.yaml` — Key metrics and findings

### Documentation
- [ ] `experiments/pilot-reproduction/spec.yaml` — Pre-registration spec (this protocol formalized)
- [ ] `experiments/pilot-reproduction/protocol.md` — This document
- [ ] `experiments/pilot-reproduction/README.md` — Replication instructions

---

## Protocol Status

**Status**: Design complete, ready for pre-registration and implementation
**Next steps**:
1. Create formal spec.yaml for critic review
2. Implement framework wrappers
3. Implement task generators and failure detectors
4. Run canary to validate infrastructure
5. Execute pilot experiment

**Estimated timeline**: 2-3 weeks from protocol approval to results

---

## Revisions

- **2026-03-29**: Initial protocol design
  - Selected 4 frameworks, 6 failure types, 2 models
  - Designed 6 reproduction tasks with automated detection
  - Adjusted sample size to fit $5 budget (5 trials per condition)
  - Pre-registered 4 primary analyses
