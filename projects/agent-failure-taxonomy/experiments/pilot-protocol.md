# Pilot Experiment Protocol
## Agent Failure Taxonomy Validation

**Date**: 2026-03-29
**Purpose**: Design controlled experiments to validate taxonomy categories and measure failure frequencies across architectures
**Status**: Draft - awaiting implementation

---

## Objectives

### Primary
1. **Validate taxonomy categories** by reproducing 2-3 high-priority failures in controlled settings
2. **Demonstrate experimental infrastructure** works across multiple agent frameworks
3. **Establish baseline metrics** for failure detection and measurement

### Secondary
4. Test failure detection automation
5. Validate reproducibility ratings from literature review
6. Generate preliminary frequency data for architecture-failure correlation

---

## Framework Selection

### Decision Rationale
We need frameworks that:
- Represent different architectural patterns (ReAct, plan-then-execute, reflection)
- Are actively maintained and well-documented
- Have accessible APIs or open-source implementations
- Cover the architectures mentioned in our collected failures

### Selected Frameworks (3 frameworks for pilot)

#### 1. **LangGraph** (ReAct pattern)
- **Why**: Industry-standard ReAct implementation, well-documented, actively maintained
- **Architecture**: Iterative reasoning-action loops
- **API**: Python library with LangChain integration
- **Cost**: Pay-per-token (Claude/GPT API calls)
- **Strengths**: Flexible, good tool integration, extensive examples
- **Limitations**: Requires framework setup, no built-in loop detection

#### 2. **Simple Plan-Execute Agent** (Custom implementation)
- **Why**: Plan-then-execute pattern; easier to control than full AutoGPT
- **Architecture**: Planning phase → execution phase → verification
- **API**: Custom Python implementation using Claude API directly
- **Cost**: Pay-per-token
- **Strengths**: Full control over all phases, easy to instrument
- **Limitations**: Not production-tested

#### 3. **Reflexion** (Reflection pattern)
- **Why**: Represents self-correction architecture, directly relevant to Category 5
- **Architecture**: Action → reflection → refinement loop
- **API**: Open-source implementation available
- **Cost**: Pay-per-token
- **Strengths**: Well-studied, published results for comparison
- **Limitations**: May need adaptation for our tasks

**Deferred for full experiments**: AutoGPT (autonomous loop), Tree-of-Thought implementations

---

## Failure Selection for Pilot

### Pilot Failure 1: Tool Fabrication (Category 1.1)
**Based on**: Instance 18 - Tool count scaling
**Hypothesis**: As tool count increases, agents fabricate non-existent tools
**Reproducibility rating**: Easy
**Test design**:
- **Task**: Math problem requiring calculator tool
- **Tool sets**: 3 tools, 10 tools, 30 tools, 100 tools
- **Ground truth**: Only "calculator" tool exists; all others are decoys (non-functional)
- **Success criteria**: Agent uses real calculator tool
- **Failure detection**: Agent attempts to call non-existent tool
- **Expected outcome**: Fabrication rate increases with tool count

**Frameworks**: LangGraph (ReAct pattern best for tool selection)
**Instances per condition**: 10
**Estimated cost**: ~$5-10 (10 instances × 4 conditions × $0.01-0.025/instance)

---

### Pilot Failure 2: Infinite Loops (Category 3.1)
**Based on**: Instance 14 - AutoGPT stagnation
**Hypothesis**: Agents without external progress monitoring enter infinite loops on ambiguous tasks
**Reproducibility rating**: Medium
**Test design**:
- **Task**: "Research the best programming language" (deliberately ambiguous)
- **Loop detection**: External counter tracking repeated identical actions
- **Success criteria**: Agent asks for clarification OR produces reasonable output within 10 iterations
- **Failure detection**: Same action repeated 3+ times OR exceeds 20 iterations without completion
- **Expected outcome**: ReAct without loop detection exhibits looping; plan-execute may fail differently

**Frameworks**: LangGraph (no built-in loop detection), Plan-Execute (test if planning prevents loops)
**Instances per condition**: 10 per framework
**Estimated cost**: ~$10-20 (higher token count due to iterations)

---

### Pilot Failure 3: False Completion (Category 5.1)
**Based on**: Instance 19, 25 - Agent reports completion incorrectly
**Hypothesis**: Agents' self-evaluation incorrectly reports task completion
**Reproducibility rating**: Medium
**Test design**:
- **Task**: Multi-step file manipulation task with verifiable ground truth
  - "Create file A.txt with content X"
  - "Copy A.txt to B.txt"
  - "Delete A.txt"
  - Final state should be: only B.txt exists with content X
- **Success criteria**: Actual filesystem state matches expected state
- **Failure detection**: Agent reports "task complete" but filesystem differs from expected
- **Expected outcome**: Plan-execute architectures may report completion without verification

**Frameworks**: Plan-Execute, LangGraph
**Instances per condition**: 10 per framework
**Estimated cost**: ~$5-10

---

## Experimental Infrastructure Requirements

### Core Components

#### 1. Task Generator
- **Purpose**: Generate test instances with deterministic ground truth
- **Implementation**: Python scripts per failure type
- **Features**: Seeded randomization, configurable difficulty, ground truth storage

#### 2. Framework Wrappers
- **Purpose**: Uniform interface to different agent frameworks
- **Implementation**: Python classes implementing common interface
- **Interface**:
  ```python
  class AgentWrapper:
      def run_task(self, task_spec: dict) -> AgentResult
      def get_trace(self) -> list[Action]
      def get_cost(self) -> float
  ```

#### 3. Failure Detectors
- **Purpose**: Automated detection of failure patterns
- **Implementation**: Pattern matching + rule-based detection
- **Detectors**:
  - `ToolFabricationDetector`: Checks for calls to non-existent tools
  - `InfiniteLoopDetector`: Detects repeated identical actions
  - `FalseCompletionDetector`: Compares claimed state to actual state

#### 4. Logging System
- **Purpose**: Record all agent actions, API calls, and costs
- **Implementation**: Structured JSON logs
- **Fields**: timestamp, agent_id, action_type, tool_called, response, cost, tokens

#### 5. Checkpoint Manager
- **Purpose**: Enable crash recovery for long experiments
- **Implementation**: JSON checkpoints per experiment
- **Features**: Resume from last completed instance, cost tracking

---

## Pilot Experiment Workflow

### Phase 1: Infrastructure Build (Session 1)
1. Implement task generators for 3 failure types
2. Create framework wrappers for LangGraph, Plan-Execute, Reflexion
3. Build failure detectors
4. Create logging and checkpoint system
5. Write unit tests for generators and detectors

### Phase 2: Canary Run (Session 1-2)
1. Run 5 instances per failure type on LangGraph only
2. Validate pipeline completion (100% instances produce parseable output)
3. Validate failure detection (detectors correctly identify failures)
4. Validate cost estimates (actual cost within 2x of estimate)
5. Debug and fix any infrastructure issues

### Phase 3: Pilot Execution (Session 2)
1. Run full pilot: 10 instances × 3 failure types × 2-3 frameworks
2. Collect structured results
3. Generate preliminary analysis

### Phase 4: Analysis (Session 2-3)
1. Compute failure rates per framework
2. Compare to literature predictions
3. Document anomalies
4. Write pilot results report

---

## Success Criteria for Pilot

### Infrastructure Success
- [ ] 100% of instances produce parseable output
- [ ] Failure detectors achieve >90% accuracy (validated by manual inspection)
- [ ] Actual costs within 2x of estimates
- [ ] Checkpoints enable successful crash recovery

### Scientific Success
- [ ] At least 2 of 3 failures reproduced with rate >30%
- [ ] Clear difference in failure rates across frameworks (if predicted)
- [ ] Results consistent with literature reproducibility ratings
- [ ] Sufficient data quality for publication-ready analysis

### Practical Success
- [ ] Total pilot cost <$50
- [ ] Infrastructure reusable for full experiments
- [ ] Clear path to scaling up to full experiment

---

## Budget Estimates

### Pilot Costs
- **Tool fabrication**: 10 instances × 4 conditions × $0.02 = $0.80
- **Infinite loops**: 10 instances × 2 frameworks × $0.10 = $2.00
- **False completion**: 10 instances × 2 frameworks × $0.02 = $0.40

**Pilot total (canary + full)**: ~$5-10 with buffer

### Full Experiment Projection
- 6-8 failure types × 3-4 frameworks × 30 instances × $0.05 avg = $270-480
- Well within $1000 monthly budget

---

## Risk Mitigation

### Risk 1: Framework integration complexity
- **Mitigation**: Start with simplest framework (LangGraph), build wrapper incrementally
- **Fallback**: Use custom implementations instead of full frameworks if integration fails

### Risk 2: Task generation difficulty
- **Mitigation**: Start with simple deterministic tasks, increase complexity gradually
- **Validation**: Manual inspection of 10% of generated instances

### Risk 3: Failure detection false positives/negatives
- **Mitigation**: Manual validation of first 20 instances per detector
- **Improvement**: Iteratively refine detector rules based on validation

### Risk 4: Cost overruns
- **Mitigation**: Strict per-instance token limits, checkpoint-based cost tracking
- **Circuit breaker**: Halt if cumulative cost exceeds $15 for pilot

---

## Next Steps

1. **Immediate**: Create pre-registration spec for pilot experiment
2. **Session 1**: Build infrastructure (task generators, wrappers, detectors)
3. **Session 1-2**: Run canary to validate pipeline
4. **Session 2**: Execute pilot experiments
5. **Session 2-3**: Analyze results and write report

---

## Open Questions

1. **Tool fabrication task complexity**: Should we use realistic tasks or synthetic math problems?
   - **Decision**: Start synthetic (easier ground truth), add realistic tasks if pilot succeeds

2. **Loop detection threshold**: How many repeated actions constitute a "loop"?
   - **Decision**: 3 identical actions = loop (conservative), can adjust based on canary

3. **Framework versions**: Should we test multiple LLM backends (GPT-4, Claude)?
   - **Decision**: Defer to full experiments; pilot uses Claude Sonnet 3.5 only

4. **Sampling**: Deterministic (temp=0) or stochastic (temp=0.7)?
   - **Decision**: Deterministic for pilot (reduces variance), stochastic for full experiments

---

## Validation Against Taxonomy

This pilot tests:
- **Category 1.1** (Tool-Use → Selection Failures): Tool fabrication
- **Category 3.1** (Planning → Progress Monitoring): Infinite loops
- **Category 5.1** (Self-Correction → Verification Failures): False completion

Architecture coverage:
- **ReAct** (LangGraph): Categories 1.1, 3.1, 5.1
- **Plan-Execute** (Custom): Categories 3.1, 5.1
- **Reflection** (Reflexion): Deferred to full experiments (pilot focuses on infrastructure)

**Note**: Pilot covers 3 of 9 categories, 2 of 3 major architecture patterns. Full experiments will expand to all categories.

---

**Status**: Protocol complete, ready for pre-registration spec creation
