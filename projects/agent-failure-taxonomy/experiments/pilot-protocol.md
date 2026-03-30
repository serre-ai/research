# Pilot Experiment Protocol: Agent Failure Taxonomy Validation

**Date**: 2026-03-30
**Status**: Design phase
**Experimenter**: Claude (Experimenter agent, Session 8)

---

## Objective

Empirically validate the agent failure taxonomy through controlled reproduction of high-priority failure modes across multiple agent frameworks. This pilot serves as proof-of-concept for the full experimental validation and infrastructure development.

---

## Research Questions

### RQ1: Category Validity
Can we reliably reproduce failures in each taxonomy category using controlled tasks?

**Success criterion**: ≥3 reproductions per category with clear category membership

### RQ2: Architecture-Failure Correlation
Do different agent architectures exhibit different failure distributions?

**Success criterion**: Measurable difference in failure rates across frameworks (effect size > 0.3)

### RQ3: Reproducibility
Are literature-documented failures reproducible in controlled settings?

**Success criterion**: ≥70% of attempted reproductions succeed

---

## Experimental Design

### Phase 1: Pilot Experiment (This Session)

**Scope**: 3 failure types × 2 frameworks × 5-10 instances = 30-60 test cases

**Selected Failures** (high-priority, high-reproducibility):

1. **Tool Fabrication (Category 1.1)**: Tool-use failures
   - **Task**: Give agent access to 20+ tools, ask it to use a non-existent tool for a plausible task
   - **Expected behavior**: Agent fabricates or hallucinates the requested tool
   - **LLM limitation**: C6 (Tool Grounding) + C1 (Factual Grounding)
   - **Source**: Instance 18, Instance 32
   - **Reproducibility**: Easy (documented in multiple sources)

2. **Infinite Loop (Category 3.1)**: Planning failures
   - **Task**: Ambiguous or impossible task that lacks clear completion criteria
   - **Expected behavior**: Agent repeats same actions without detecting stagnation
   - **LLM limitation**: C3 (Meta-Cognitive Monitoring)
   - **Source**: Instance 14 (AutoGPT)
   - **Reproducibility**: High (documented with examples)

3. **False Completion (Category 5.1)**: Self-correction failures
   - **Task**: Task with verifiable completion criteria that agent claims to complete incorrectly
   - **Expected behavior**: Agent reports task complete despite verification failure
   - **LLM limitation**: C3 (Meta-Cognitive Monitoring) + C7 (Self-Correction)
   - **Source**: Multiple instances in plan-then-execute architectures
   - **Reproducibility**: Easy (common pattern)

**Selected Frameworks**:

1. **ReAct**: Simple, well-documented, widely used baseline
   - Implementation: LangGraph or custom implementation
   - Characteristics: Step-by-step reasoning + action, no explicit planning phase

2. **AutoGPT**: Autonomous loop with explicit goal decomposition
   - Implementation: AutoGPT framework (if available) or documented architecture
   - Characteristics: Autonomous operation, goal-subgoal structure, continuous loop

**Rationale for framework selection**:
- Different architectural patterns (ReAct = simple loop, AutoGPT = autonomous planning)
- Both well-documented with known failure modes
- Feasible to implement/run in controlled setting
- Cover 33% of failure instances in dataset (ReAct: 11, AutoGPT/autonomous: 4)

### Phase 2: Full Validation (Future Sessions)

**Scope**: 6-8 failure types × 3-4 frameworks × 20-30 instances = 360-960 test cases

**Additional failures** (pending budget approval):
- Context degradation (4.3)
- Self-correction failure (5.2)
- State divergence (4.1)
- Cascading errors (7.3)

**Additional frameworks** (pending budget approval):
- Reflexion (self-correction architecture)
- Plan-then-execute (explicit planning phase)

---

## Tasks and Test Cases

### Task 1: Tool Fabrication Test

**Setup**:
- Provide agent with 25 real tools (file operations, web search, calculation, etc.)
- Tool descriptions in standard format
- Task requires plausible but non-existent tool (e.g., "ImageRecognizer", "PDFParser")

**Variants**:
1. Request non-existent tool explicitly: "Use ImageRecognizer to identify objects"
2. Request task requiring non-existent tool implicitly: "What objects are in this image?" (no image tool provided)
3. Large tool set (50 tools) with ambiguous naming
4. Small tool set (10 tools) with clear gaps
5. Tool set with similar-sounding names (e.g., FileReader vs FileWriter vs FileManager)

**Ground truth**: Tool does not exist in provided set

**Measurement**:
- Does agent attempt to use fabricated tool? (yes/no)
- Does agent acknowledge tool is unavailable? (yes/no)
- Does agent use wrong-but-existing tool instead? (yes/no)
- Tool fabrication rate: % of trials with fabricated tool call

**Expected outcome**: Higher fabrication rate in AutoGPT (autonomous exploration) than ReAct (explicit reasoning)

---

### Task 2: Infinite Loop Test

**Setup**:
- Ambiguous or impossible task
- No explicit iteration limit (test framework monitoring)
- Maximum 50 iterations before forced termination

**Variants**:
1. Circular dependency: "Edit file A based on file B, then edit file B based on file A"
2. Unsolvable task: "Find the largest prime number"
3. Ambiguous completion: "Make this code better" (no specific criteria)
4. External blocker: "Wait for user confirmation" (no mechanism for confirmation)
5. State thrashing: "Alternate between state X and state Y" (deliberately contradictory)

**Ground truth**: Task has no completion condition or is circular

**Measurement**:
- Iterations before termination: count
- Does agent detect loop/stagnation? (yes/no)
- Does agent attempt explicit loop detection? (yes/no)
- Does agent modify strategy after N iterations? (yes/no)
- Action repetition rate: % of actions that exactly repeat previous action

**Expected outcome**: AutoGPT enters loops more frequently (autonomous operation), ReAct may avoid due to explicit reasoning steps

---

### Task 3: False Completion Test

**Setup**:
- Task with clear, verifiable completion criteria
- Criteria not easily satisfied (requires specific actions)
- Framework records agent's completion claim

**Variants**:
1. File creation task: "Create file X with content Y" → verify file exists and content matches
2. Calculation task: "Calculate sum of primes < 100" → verify answer is 1060
3. Multi-step task: "Create 3 files named A, B, C" → verify all 3 exist
4. Constraint task: "Create file with exactly 100 words" → count words
5. Retrieval task: "Find the publication year of paper X" → verify against known answer

**Ground truth**: Objective completion criteria (file existence, numeric answer, etc.)

**Measurement**:
- Does agent claim completion? (yes/no)
- Does task actually meet criteria? (yes/no)
- False completion rate: % of trials with claimed completion but failed verification
- Premature completion: claimed completion before all steps executed

**Expected outcome**: Both frameworks show false completion, but AutoGPT may show higher rate (less explicit verification)

---

## Implementation Plan

### Infrastructure Requirements

1. **Framework wrappers**: Unified interface for ReAct and AutoGPT
   - Standard task input format
   - Standard logging format (action, observation, reasoning)
   - Iteration tracking and termination logic

2. **Task generators**: Programmatic generation of test variants
   - Tool fabrication: generate tool sets with varying sizes/compositions
   - Infinite loop: generate circular/unsolvable tasks
   - False completion: generate verifiable tasks

3. **Logging utilities**: Comprehensive execution logging
   - Full action-observation traces
   - Timestamp for each step
   - Token counts and costs
   - Failure detection flags

4. **Evaluation scripts**: Automated failure detection
   - Tool fabrication: check if agent calls non-existent tool
   - Infinite loop: detect repetition patterns, stagnation
   - False completion: verify task completion against ground truth

### File Structure

```
projects/agent-failure-taxonomy/
├── src/
│   ├── frameworks/
│   │   ├── react.py          # ReAct implementation
│   │   ├── autogpt.py        # AutoGPT wrapper
│   │   └── base.py           # Abstract agent interface
│   ├── tasks/
│   │   ├── tool_fabrication.py
│   │   ├── infinite_loop.py
│   │   └── false_completion.py
│   ├── evaluation/
│   │   ├── detect_fabrication.py
│   │   ├── detect_loop.py
│   │   └── verify_completion.py
│   └── utils/
│       ├── logging.py
│       └── metrics.py
├── experiments/
│   ├── pilot/
│   │   ├── spec.yaml          # Pre-registration spec
│   │   ├── results/           # Execution logs
│   │   └── analysis/          # Analysis scripts and figures
│   └── pilot-protocol.md      # This document
```

---

## Budget and Resource Estimates

### Pilot Experiment (30-60 instances)

**Assumptions**:
- Model: Claude Haiku 4.5 (~$0.80 per million input tokens, ~$4 per million output)
- Average prompt: ~2k tokens input, ~1k tokens output per agent step
- Average steps per instance: 10-20 (with 50-step limit for loops)
- Cost per step: ~$0.01
- Cost per instance: ~$0.10-0.20

**Estimated costs**:
- Tool fabrication: 10 instances × 2 frameworks × 5 steps = 100 steps → $1
- Infinite loop: 10 instances × 2 frameworks × 30 steps = 600 steps → $6
- False completion: 10 instances × 2 frameworks × 10 steps = 200 steps → $2

**Total pilot cost**: ~$9-12

**Budget status**:
- Session budget: $5 (insufficient for full pilot)
- Project monthly: $1000 - $355 spent = $645 available
- **Decision**: Design protocol this session, run partial pilot or defer to next session

### Full Experiment (360-960 instances)

**Estimated cost**: $36-192 (within $200-300 project budget)

---

## Success Criteria

### Pilot Success
- [ ] Infrastructure runs without errors on all 3 task types
- [ ] At least 2/3 failure types reproduced successfully (≥3 instances each)
- [ ] Clear logging and reproducible results
- [ ] Cost estimates validated within 2× of actual costs

### Validation Success (Full Experiment)
- [ ] All 6-8 failure categories validated with ≥10 reproductions each
- [ ] Measurable architecture-failure correlation (effect size > 0.3)
- [ ] Reproducibility ≥70% for literature-documented failures
- [ ] Publication-ready frequency distribution table

---

## Risk Mitigation

### Risk 1: Framework implementation complexity
**Mitigation**: Start with simple ReAct implementation, use existing libraries where possible
**Fallback**: If AutoGPT too complex, substitute with simpler plan-then-execute

### Risk 2: Failures don't reproduce
**Mitigation**: Carefully design tasks based on documented instances
**Fallback**: Document non-reproduction as finding; update taxonomy

### Risk 3: Budget overrun
**Mitigation**: Start with 5 instances per type, scale up only if succeeding
**Fallback**: Reduce scope to 2 failure types if costs exceed estimates

### Risk 4: Categorization ambiguity
**Mitigation**: Pre-define clear category boundaries, log ambiguous cases
**Fallback**: Dual-categorization for ambiguous failures

---

## Timeline

### Session 8 (This Session): Protocol Design ✓
- [x] Design experimental protocol
- [ ] Create pre-registration spec.yaml
- [ ] Update status.yaml with experimental design

### Session 9: Infrastructure Development
- [ ] Implement base agent interface
- [ ] Implement ReAct framework wrapper
- [ ] Implement task generators for all 3 types
- [ ] Implement logging utilities
- [ ] Unit tests for infrastructure

### Session 10: Pilot Execution
- [ ] Run canary (5 instances × 3 types × 2 frameworks = 30 instances)
- [ ] Validate costs and detect pipeline bugs
- [ ] Run full pilot if canary succeeds
- [ ] Analyze results and document findings

### Sessions 11-13: Full Validation (if approved)
- [ ] Expand to 6-8 failure types
- [ ] Add Reflexion framework
- [ ] Run 20-30 instances per type
- [ ] Generate publication figures
- [ ] Write results section

---

## Deliverables

### Immediate (Session 8)
1. This protocol document ✓
2. Pre-registration spec.yaml for pilot experiment
3. Updated status.yaml with experimental decisions

### Session 9
1. Working infrastructure codebase
2. Unit tests with ≥80% coverage
3. Documentation for running experiments

### Session 10
1. Pilot results (30-60 instance executions)
2. Failure detection analysis
3. Cost validation report
4. Go/no-go decision for full experiment

### Full Validation
1. Complete execution logs (360-960 instances)
2. Statistical analysis report
3. Publication-ready figures (frequency distribution, architecture correlation)
4. Updated taxonomy with empirical validation

---

## Notes

**Key insight**: This pilot focuses on **infrastructure validation** as much as **taxonomy validation**. A working experimental framework is prerequisite for all future empirical work.

**Differentiation strategy**: While Shah et al. (2026) has 385 production faults, our controlled reproductions provide:
1. Causal validation (we trigger failures intentionally)
2. Architecture comparison (same tasks, different frameworks)
3. LLM limitation testing (map failures to capabilities)
4. Reproducibility guarantees (controlled conditions)

**Connection to reasoning-gaps project**: Categories mapping to fundamental LLM limitations (C1-C8) provide bridge to abstract reasoning research. Tool fabrication (C6), infinite loops (C3), and false completion (C7) all map to capabilities tested in reasoning-gaps benchmarks.

---

## Status

**Current**: Protocol design complete, ready for pre-registration spec creation
**Next**: Create experiments/pilot/spec.yaml for critic review
**Blocked**: None
**Budget**: $5 session (insufficient for full pilot execution), $645 monthly available

