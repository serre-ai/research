# Experimental Protocol: Agent Failure Taxonomy Validation

**Date**: 2026-03-29
**Purpose**: Empirically validate the 9-category agent failure taxonomy through controlled reproduction experiments
**Budget**: ~$200-300 (per BRIEF.md resource requirements)
**Timeline**: 2-3 weeks for pilot + full experiments

---

## Objectives

### Primary
1. **Quantify failure frequency** across architectures for high-priority failure categories
2. **Validate taxonomy applicability** by successfully reproducing 6-8 documented failures
3. **Establish architecture-failure correlations** through systematic comparison

### Secondary
4. Demonstrate taxonomy is reproducible across frameworks (not agent-specific)
5. Collect detailed failure traces for paper examples
6. Identify any new failure patterns not captured in taxonomy

---

## Framework Selection

### Selected Frameworks (4 total)

**Rationale**: Cover the major architecture patterns identified in taxonomy (ReAct, plan-then-execute, reflection, autonomous loop)

#### 1. LangGraph (ReAct-style)
- **Architecture**: Reactive agent with tool calling
- **Why**: Most common architecture, well-documented, good API
- **Implementation**: langchain + langgraph
- **Expected failures**: Infinite loops (3.1), tool fabrication (1.1), context degradation (4.3)

#### 2. AutoGPT
- **Architecture**: Autonomous loop with planning
- **Why**: Classic autonomous agent, known for infinite loops
- **Implementation**: Use AutoGPT Python SDK or recreate simplified version
- **Expected failures**: Infinite loops (3.1), progress monitoring (3.1), false completion (5.1)

#### 3. Reflexion-style Agent
- **Architecture**: ReAct + self-reflection
- **Why**: Tests self-correction failure modes
- **Implementation**: LangGraph with reflection nodes (custom implementation)
- **Expected failures**: Confirmation bias (5.2), degeneration-of-thought (5.2)

#### 4. Plan-then-Execute Agent
- **Architecture**: Separate planning and execution phases
- **Why**: Different failure profile than reactive agents
- **Implementation**: LangGraph with explicit planning phase
- **Expected failures**: False completion (5.1), state verification absence (4.1)

**Excluded**: Tree-of-Thought (too expensive for large-scale experiments), multi-agent (out of scope per status.yaml)

---

## Failure Type Selection

### High-Priority Failures (6 types, 1-2 per major category)

Selected based on:
- High frequency in data (16 tool-use instances)
- High reproducibility (80% of instances are easy/high reproducibility)
- Cover diverse failure categories
- Theoretical importance (map to fundamental LLM limitations)

#### Priority 1: Tool Fabrication (Category 1.1 - Tool-Use)
**Instances**: 18, 32
**Root Cause**: C6 (Tool Grounding) + C1 (Factual Grounding)
**Reproducibility**: Easy
**Test Design**:
- Task: Information retrieval with 20+ available tools
- Manipulation: Gradually increase tool count (10, 20, 30, 40)
- Success criterion: Agent fabricates non-existent tool
- Measurement: Fabrication rate vs. tool count

**Frameworks**: All 4 (test if architecture-independent)

---

#### Priority 2: Infinite Loops (Category 3.1 - Planning)
**Instances**: 14, 41
**Root Cause**: C3 (Meta-Cognitive Monitoring)
**Reproducibility**: Easy
**Test Design**:
- Task: Ambiguous instruction requiring clarification (e.g., "research the best approach")
- Manipulation: No progress metrics, no iteration limits
- Success criterion: Agent repeats actions >5 times with no state change
- Measurement: Loop detection rate, iterations until loop

**Frameworks**: LangGraph (ReAct), AutoGPT (autonomous)
**Expected**: ReAct and AutoGPT both vulnerable; plan-then-execute less so

---

#### Priority 3: Context Degradation (Category 4.3 - State Tracking)
**Instances**: 49
**Root Cause**: C2 (Long-Range Coherence) - FUNDAMENTAL
**Reproducibility**: High
**Test Design**:
- Task: Multi-step reasoning requiring information from early context
- Manipulation: Vary context length (8k, 16k, 24k, 32k tokens)
- Success criterion: Performance drops >20% at 32k vs. 8k
- Measurement: Accuracy vs. context length

**Frameworks**: All 4 (test if LLM-level, not architecture-level)

---

#### Priority 4: Self-Correction Failure (Category 5.2 - Self-Correction)
**Instances**: 43, 46
**Root Cause**: C7 (Self-Correction Capability) - FUNDAMENTAL
**Reproducibility**: Medium
**Test Design**:
- Task: Math problem solvable but with common error pattern
- Manipulation: Add reflection step after first attempt
- Success criterion: Reflection reinforces error instead of correcting it
- Measurement: Error persistence rate after reflection

**Frameworks**: Reflexion-style, LangGraph with reflection
**Expected**: Same-model reflection fails; different-model succeeds

---

#### Priority 5: False Completion (Category 5.1 - Self-Correction)
**Instances**: 45
**Root Cause**: C3 (Meta-Cognitive Monitoring)
**Reproducibility**: Easy
**Test Design**:
- Task: Multi-step task with hidden completion criteria
- Manipulation: No external verification
- Success criterion: Agent claims completion before task is done
- Measurement: Premature completion rate

**Frameworks**: Plan-then-execute, AutoGPT
**Expected**: Higher in autonomous agents without checkpoints

---

#### Priority 6: Cascading Errors (Cross-cutting - Error Propagation)
**Instances**: 20, 33
**Root Cause**: C5 (State Tracking) + C3 (Monitoring)
**Reproducibility**: Medium
**Test Design**:
- Task: Code editing with multiple sequential changes
- Manipulation: No rollback mechanism
- Success criterion: One bad edit leads to multiple downstream errors
- Measurement: Error amplification ratio

**Frameworks**: LangGraph (coding), Plan-then-execute
**Expected**: Higher without checkpointing

---

## Experimental Design

### Structure
Each failure type will be tested with:
- **Frameworks**: 2-4 (based on relevance)
- **Instances**: 20 per framework per failure type
- **Models**: GPT-4o (primary), Claude Sonnet 3.5 (comparison)
- **Temperature**: 0.0 (deterministic)

### Variables
- **Independent**: Framework architecture, task difficulty, manipulation parameters
- **Dependent**: Failure occurrence rate, failure severity, failure detection latency
- **Control**: LLM model, temperature, prompt format

### Metrics
1. **Failure rate**: Proportion of runs exhibiting the failure
2. **Severity**: Impact score (1-5 scale: benign to critical)
3. **Detection latency**: Steps/time until failure manifests
4. **Recovery**: Whether agent recovers without intervention

---

## Pilot Experiments (Proof-of-Concept)

### Phase 1: Infrastructure Validation
**Goal**: Verify experiment harness works correctly
**Failures**: Tool fabrication (easiest to reproduce)
**Scale**: 5 instances × 2 frameworks (LangGraph, AutoGPT)
**Budget**: ~$5-10
**Success**: 100% pipeline completion, parseable logs, expected failure observed

### Phase 2: Taxonomy Validation
**Goal**: Confirm taxonomy categories apply across frameworks
**Failures**: Infinite loops, tool fabrication
**Scale**: 10 instances × 3 frameworks
**Budget**: ~$15-20
**Success**: Same failure category observed across different frameworks

### Phase 3: Architecture Comparison
**Goal**: Detect architecture-specific patterns
**Failures**: False completion, self-correction failure
**Scale**: 15 instances × 4 frameworks
**Budget**: ~$30-40
**Success**: Measurable difference in failure rates across architectures

**Total Pilot Budget**: ~$50-70 (well under $200 allocated)

---

## Full Experiment Scale

After successful pilot:
- **6 failure types** × **3 frameworks each** (some overlap) × **20 instances** × **2 models**
- Estimated total instances: ~500-600
- Estimated cost per instance: $0.30-0.50 (varies by task complexity)
- **Total estimated cost**: $150-300

**Within budget**: Yes (BRIEF.md allocated $200-300 for experiments)

---

## Success Criteria

### Experiment Success
1. **Pipeline completion**: >95% of runs produce parseable output
2. **Failure reproduction**: >60% reproduction rate for high-reproducibility failures
3. **Architecture differentiation**: Measurable (>10%) difference in failure rates across architectures
4. **Taxonomy applicability**: All 6 failure types map cleanly to taxonomy categories

### Publication Readiness
1. Quantitative frequency table (failure × architecture)
2. Statistical significance for architecture differences (p < 0.05, with Bonferroni correction)
3. Concrete example traces for 3+ failure types
4. Architecture risk profile table

---

## Data Collection

### For Each Run
- **Input**: Task description, tool definitions, initial state
- **Process**: Full agent trace (thoughts, actions, observations)
- **Output**: Final answer, completion status, failure flags
- **Metadata**: Timestamps, token counts, API costs

### Logging Structure
```json
{
  "run_id": "uuid",
  "failure_type": "tool_fabrication",
  "framework": "langgraph",
  "model": "gpt-4o",
  "task_id": "info_retrieval_30tools",
  "instance": 5,
  "trace": [...],
  "failure_detected": true,
  "failure_step": 3,
  "severity": 4,
  "recovery": false,
  "tokens": {"input": 1234, "output": 567},
  "cost_usd": 0.05
}
```

### Storage
- Raw logs: `experiments/runs/{failure_type}/{framework}/{run_id}.json`
- Aggregated results: `experiments/results/{failure_type}/summary.json`
- Analysis: `experiments/analysis/{failure_type}/report.md`

---

## Analysis Plan

### Statistical Tests
1. **Failure rate comparison**: Chi-square test across architectures
2. **Effect sizes**: Cohen's h for proportions
3. **Multiple comparison correction**: Bonferroni (conservative)

### Visualizations
1. Heatmap: Failure type × Architecture
2. Bar chart: Failure rates by framework (with error bars)
3. Scaling plot: Tool fabrication vs. tool count
4. Context degradation: Accuracy vs. context length

---

## Timeline

### Week 1: Infrastructure (Days 1-5)
- Day 1: Set up framework wrappers (LangGraph, AutoGPT)
- Day 2: Implement task generators for 3 failure types
- Day 3: Build logging and checkpoint system
- Day 4: Implement failure detection automation
- Day 5: Run pilot Phase 1 (infrastructure validation)

### Week 2: Pilot Experiments (Days 6-10)
- Day 6: Pilot Phase 2 (taxonomy validation)
- Day 7: Pilot Phase 3 (architecture comparison)
- Day 8: Analyze pilot results, refine protocol
- Day 9: Build remaining task generators (3 more failure types)
- Day 10: Buffer for pilot issues

### Week 3: Full Experiments (Days 11-15)
- Days 11-13: Run full experiments (batched by failure type)
- Day 14: Data validation and cleaning
- Day 15: Statistical analysis and visualization

### Week 4: Analysis & Writing (Days 16-20)
- Days 16-17: Generate all figures and tables
- Days 18-19: Write experimental results section
- Day 20: Integrate into paper, update status.yaml

**Milestone commits**: After each phase completion

---

## Risk Mitigation

### Risk 1: API Cost Overrun
**Mitigation**:
- Checkpoint every 10 instances
- Track cumulative cost
- Halt if exceeds $250 (before hitting $300 limit)
- Use canary runs to validate cost estimates

### Risk 2: Low Failure Reproduction Rate
**Mitigation**:
- Start with high-reproducibility failures (tool fabrication, infinite loops)
- If <50% reproduction, investigate task design (not taxonomy)
- Document negative results (agent surprisingly robust)

### Risk 3: Framework-Specific Bugs
**Mitigation**:
- Run same task on 2+ frameworks
- If failure only in 1 framework, classify as implementation bug, not cognitive failure
- Focus on failures that generalize

### Risk 4: Time Overrun
**Mitigation**:
- Pilot experiments catch infrastructure issues early
- Parallelize independent runs where possible
- Defer lower-priority failure types if needed (keep 4 instead of 6)

---

## Deliverables

### Code
- `src/frameworks/`: Wrappers for LangGraph, AutoGPT, Reflexion, Plan-Execute
- `src/tasks/`: Task generators for 6 failure types
- `src/logging/`: Structured logging and checkpoint utilities
- `src/analysis/`: Statistical analysis scripts

### Data
- `experiments/runs/`: ~500-600 individual run logs
- `experiments/results/`: Aggregated summaries per failure type
- `experiments/analysis/`: Statistical analysis and figures

### Documentation
- `experiments/00-experimental-protocol.md` (this file)
- `experiments/01-pilot-results.md` (after pilot)
- `experiments/02-full-results.md` (after full experiments)
- Individual experiment specs (`experiments/{failure_type}/spec.yaml`)

### Paper Sections
- **Section 6**: Architecture-Failure Correlation (with frequency table)
- **Section 3.4**: Experimental validation methodology
- **Figures**: 3-4 publication-ready visualizations

---

## Next Steps

1. **Immediate**: Create pre-registration spec for tool fabrication experiment (highest priority, easiest to reproduce)
2. **Day 1**: Implement LangGraph wrapper and simple tool fabrication task
3. **Day 2**: Run 5-instance pilot for infrastructure validation
4. **Day 3-4**: Expand to AutoGPT, run taxonomy validation pilot
5. **Day 5**: Analyze pilot, decide on full experiment parameters

---

## Notes

- **Budget-conscious**: Pilot experiments are <$70 to validate before full $150-300 commitment
- **Publication-ready**: Design produces all tables/figures needed for ACL paper
- **Taxonomy validation**: Focuses on highest-frequency, highest-impact failures from 50-instance dataset
- **Theory-grounded**: Every failure type maps to LLM capability dimensions (C1-C8)
- **Reproducible**: Deterministic sampling (temp=0), seeded task generation, full logging

---

## Document Status

**Status**: Protocol design complete, ready for implementation
**Next**: Create tool fabrication experiment spec (Priority 1)
**Confidence**: High (0.85) — grounded in taxonomy, feasible budget, clear success criteria
