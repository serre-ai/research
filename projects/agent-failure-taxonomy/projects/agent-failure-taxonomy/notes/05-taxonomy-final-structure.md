# Final Taxonomy Structure: Agent Failure Modes

**Date**: 2026-03-25
**Status**: Substantially complete, ready for empirical validation
**Methodology**: Grounded theory (open coding → axial coding → theoretical mapping)
**Data**: 50 failure instances from diverse sources (2023-2026)

---

## Overview

This taxonomy categorizes failure modes in LLM-based autonomous agents, providing:
1. **Hierarchical structure**: 9 major categories, 24 sub-categories
2. **Theoretical grounding**: Mapped to 8 LLM capability dimensions
3. **Dual-view design**: Symptom-based (practitioners) + cause-based (researchers)
4. **Architecture correlation**: Which architectures exhibit which failures
5. **Design principles**: 6 principles for robust agent design

---

## The 9 Major Categories

### 1. Tool-Use Failures (16 instances)
**Definition**: Agent incorrectly selects, executes, or integrates tools

**Sub-categories**:
- **1.1 Selection Failures**: Tool fabrication, wrong tool selection, tool confusion
- **1.2 Execution Failures**: Parameter errors, hallucinated execution, result misinterpretation
- **1.3 Integration Failures**: Provider/framework/API compatibility issues
- **1.4 Code Generation Errors**: Semantic incorrectness, test overfitting (coding agents)

**Root LLM Limitations**: C6 (Tool Grounding), C1 (Factual Grounding), C8 (Reasoning-Reliability Trade-off)

**Fixability**: Partially correctable (selection/execution), fully correctable (integration)

**Example**: Instance 18 — Tool count scaling causes fabrication of plausible but non-existent tools

---

### 2. Grounding Failures (8 instances)
**Definition**: Agent's model of environment/task diverges from reality

**Sub-categories**:
- **2.1 Input Grounding**: Constraint hallucination, instruction misinterpretation, action space misunderstanding
- **2.2 Observation Grounding**: Tool output misinterpretation, timing violations, modality limitations
- **2.3 API Grounding**: Domain-specific syntax mismatches, provider assumptions

**Root LLM Limitations**: C1 (Factual Grounding), C4 (Constraint Satisfaction), C6 (Tool Grounding)

**Fixability**: Partially correctable through external validation

**Example**: Instance 23 — ToT hallucinates non-existent constraints in graph problems, applies correct reasoning to wrong problem

---

### 3. Planning Failures (7 instances)
**Definition**: Agent's planning/reasoning process fails to produce effective action sequences

**Sub-categories**:
- **3.1 Progress Monitoring**: Stagnation detection failure, infinite loops, premature completion
- **3.2 Instruction Processing**: Decomposition failures, partial satisfaction
- **3.3 Reasoning Quality**: Prompt brittleness, performance without adaptation

**Root LLM Limitations**: C3 (Meta-Cognitive Monitoring), C4 (Constraint Satisfaction)

**Fixability**: Architecturally correctable (external monitoring), LLM-level fundamental (C3)

**Example**: Instance 14 — AutoGPT enters infinite loop on ambiguous tasks, no progress detection

---

### 4. State Tracking Failures (6 instances)
**Definition**: Agent's representation of system state diverges from actual state

**Sub-categories**:
- **4.1 State Divergence**: False state reporting, action-state misalignment
- **4.2 Memory Issues**: Memory corruption, cache corruption, cross-session persistence
- **4.3 Context Management**: Context exhaustion, long-context degradation, positional bias

**Root LLM Limitations**: C5 (State Tracking), C2 (Long-Range Coherence — fundamental)

**Fixability**: State divergence correctable (external verification), context degradation fundamental

**Example**: Instance 49 — Performance drops below 50% at 32k tokens across 11 of 12 models (C2 fundamental limit)

---

### 5. Self-Correction Failures (6 instances)
**Definition**: Agent's attempts to verify or correct its work fail

**Sub-categories**:
- **5.1 Verification Failures**: False completion, false action confirmation, test gaming
- **5.2 Reflection Failures**: Confirmation bias (Reflexion), degeneration-of-thought, complexity plateaus
- **5.3 Error Routing**: Sending errors to wrong recipient

**Root LLM Limitations**: C3 (Meta-Cognitive Monitoring), C7 (Self-Correction Capability — fundamental)

**Fixability**: Not fixable with same-model self-evaluation; requires external verification

**Example**: Instance 43 — Reflexion repeats same error despite reflection; self-reflection reinforces misconceptions

---

### 6. Error Recovery Failures (4 instances)
**Definition**: Agent fails to detect, handle, or recover from errors

**Sub-categories**:
- **6.1 Error Detection**: Tool failure undetected, silent continuation
- **6.2 Error Handling**: Parsing error non-recovery, retry absence, no graceful degradation

**Root LLM Limitations**: None (architectural/framework issues)

**Fixability**: Fully correctable through better error handling logic

**Example**: Instance 28 — LangChain JSON parsing errors cause complete failure; no retry mechanism

---

### 7. Error Propagation (3 instances)
**Definition**: Errors spread through time (memory) or space (messages/edits)

**Sub-categories**:
- **7.1 Temporal Propagation**: Memory persistence, cross-session contamination
- **7.2 Spatial Propagation**: Cascading edits, cross-agent amplification
- **7.3 Causal Chains**: One failure triggering downstream failures

**Root LLM Limitations**: Indirect — enabled by C5 (State Tracking), C3 (Monitoring), C7 (Self-Correction)

**Fixability**: Architecturally correctable through isolation and checkpointing

**Example**: Instance 20 — Errors written to memory persist across sessions, contaminating all future reasoning

---

### 8. Evaluation/Environment Failures (5 instances) [NOT AGENT FAILURES]
**Definition**: Perceived failures caused by measurement/environment issues, not agent

**Sub-categories**:
- **8.1 Environment Limitations**: UI accessibility issues, element representation inadequacy
- **8.2 Evaluation Criteria**: Overly restrictive matching, oracle insufficiency
- **8.3 Methodology**: Failure source conflation, aggregate metric inadequacy

**Root LLM Limitations**: None (evaluation infrastructure issues)

**Fixability**: Fix evaluation infrastructure, not agent

**Example**: Instance 38 — WebArena dropdown selection impossible due to Playwright accessibility tree limitations

**Note**: Included to help practitioners distinguish agent problems from infrastructure problems

---

### 9. Security Vulnerabilities (2 instances)
**Definition**: Agent exposes sensitive information or creates security risks

**Sub-categories**:
- **9.1 Information Leakage**: Credential exposure, exception sanitization failures

**Root LLM Limitations**: None (security implementation issues)

**Fixability**: Fully correctable through secure coding practices

**Example**: Instance 13 — CrewAI exception handling exposes GitHub token to users

**Note**: Likely under-represented in current dataset; production systems probably have more

---

## LLM Capability Dimensions (C1-C8)

### Fundamental Limitations (Unlikely to Fix Soon)

**C1: Factual Grounding**
- Cannot reliably separate facts from generation
- Fills gaps with plausible fabrication
- **Affects**: All hallucination types
- **Design response**: External validation required

**C2: Long-Range Coherence**
- O(n²) attention cost, positional bias
- Performance < 50% at 32k tokens
- **Affects**: Context degradation, lost in middle
- **Design response**: External memory, compression, retrieval

**C3: Meta-Cognitive Monitoring**
- Cannot reliably detect own errors, stagnation, loops
- No "am I stuck?" mechanism
- **Affects**: Progress monitoring, self-verification
- **Design response**: External monitoring required

**C7: Self-Correction Capability**
- Same-model reflection reinforces errors
- Confirmation bias in self-evaluation
- **Affects**: Reflexion, verification, false completion
- **Design response**: External verification (different model/tool/human)

**C8: Reasoning-Reliability Trade-off**
- Better reasoning → more tool hallucination
- Fundamental paradox, not a bug
- **Affects**: Tool execution hallucination
- **Design response**: Accept trade-off or external verification

---

### Partially Correctable Limitations

**C4: Constraint Satisfaction**
- Struggles with complex constraint sets
- Invents spurious constraints
- **Mitigation**: Decomposition, explicit tracking
- **Limit**: Very complex specs exceed capacity

**C5: State Tracking**
- Internal state diverges from reality
- No spontaneous reconciliation
- **Mitigation**: External state verification
- **Limit**: Agent won't request verification unprompted

**C6: Tool Grounding**
- Tool representations diverge from reality
- Scaling with tool count
- **Mitigation**: Better documentation, retrieval
- **Limit**: Scaling degradation is fundamental

---

## Architecture-Failure Correlation Matrix

| Architecture | High-Risk Failures | Mitigation Strategy |
|--------------|-------------------|---------------------|
| **ReAct** | Progress monitoring (infinite loops), Context exhaustion, Fine-tuning dependency | Iteration limits, external memory, fine-tune or use few-shot |
| **Plan-then-Execute** | False completion, State verification absence | External validation checkpoints, action confirmation |
| **Reflexion** | Confirmation bias, Degeneration-of-thought, Complexity plateau | Multi-model reflection, diverse critics, external validation |
| **Autonomous Loop** | Infinite loops, Resource exhaustion, Web hallucinations | Progress metrics, cost limits, validation |
| **Tree-of-Thought** | Prompt brittleness, Constraint hallucination, High cost | Prompt ensembling, constraint validation, selective use |
| **Coding Agents** | Semantic incorrectness (52%), Edit cascades, Test gaming | TDD, checkpointing, comprehensive test suites |

**Note**: Percentages are from current data; controlled experiments needed for rigorous quantification

---

## Design Principles for Robust Agents

### Principle 1: Never Trust Self-Evaluation
**Reason**: C3 and C7 are fundamental limitations — same-model self-assessment is unreliable
**Implementation**: Critical decisions require external verification (different model, tool, human)
**Example**: Don't rely on agent's "task complete" claim; verify with ground truth

---

### Principle 2: Assume State Divergence Will Occur
**Reason**: C5 is inherent to internal modeling — agents' internal state will diverge from reality
**Implementation**: Design for state reconciliation, not state correctness; periodic state verification
**Example**: After actions that change state (deletions, writes), verify actual state

---

### Principle 3: External Memory for Complex/Long Tasks
**Reason**: C2 context degradation is fundamental — performance drops at long context
**Implementation**: Don't rely on context window beyond 8-16k tokens; use retrieval, compression, external memory
**Example**: Long research tasks need external note-taking, not pure in-context tracking

---

### Principle 4: Validate All Generated Information
**Reason**: C1 factual grounding fails under ambiguity — LLM fills gaps with generation
**Implementation**: Critical facts need external validation (retrieval, computation, human check)
**Example**: Web scraping results should be validated against source, not trusted as stated

---

### Principle 5: Isolate Errors
**Reason**: C3 and C7 prevent reliable error detection/correction — errors will propagate
**Implementation**: Checkpointing, rollback, modular isolation, error boundaries
**Example**: Code editing should have rollback points; don't let bad edits cascade

---

### Principle 6: Choose Architectures Based on Failure Profiles
**Reason**: Different architectures exhibit different failure patterns
**Implementation**: Match architecture to task criticality and failure tolerance
**Example**: High-stakes tasks need plan-then-execute with checkpoints; exploratory tasks can use ReAct

---

## Cross-Cutting Patterns

### Pattern 1: State Divergence
- Agent's internal model ≠ actual reality
- Affects categories: 4 (State Tracking), 5 (Self-Correction), 1 (Tool-Use)
- **Central to many failures**

### Pattern 2: Silent Error Propagation
- Errors don't surface immediately; spread through memory/messages/edits
- Affects categories: 7 (Error Propagation), 4 (State Tracking), 6 (Error Recovery)

### Pattern 3: Hallucination Under Insufficient Grounding
- LLM generation fills gaps when retrieval/grounding fails
- Affects categories: 1 (Tool-Use), 2 (Grounding), 3 (Planning)

### Pattern 4: Reasoning Paradoxes
- More reasoning can increase certain error types
- Affects categories: 1 (Tool-Use), 5 (Self-Correction)
- **Fundamental trade-off**

### Pattern 5: Scaling Failures
- Performance degrades as scale increases (tools, context, complexity)
- Affects categories: 1 (Tool-Use), 4 (State Tracking)

### Pattern 6: Meta-Cognitive Blindness
- Agents cannot reliably evaluate own progress/correctness
- Affects categories: 3 (Planning), 5 (Self-Correction)
- **Most pervasive limitation**

---

## Differentiation vs. Concurrent Work

### Our Taxonomy vs. "Characterizing Faults in Agentic AI" (March 2026)

| Dimension | Our Approach | Their Approach |
|-----------|-------------|----------------|
| **Scale** | 50 instances, diverse sources | 385 instances, production faults |
| **Structure** | 9-category hierarchical | 37-category flat |
| **Theory** | Mapped to 8 LLM capabilities | Empirical categorization |
| **View** | Dual (symptom + cause) | Symptom-based |
| **Output** | Design principles, research priorities | Comprehensive categorization |
| **Validation** | Grounded theory + experiments | Production data |

**Our Edge**: Theoretical contribution, LLM limitation mapping, design guidance, bridge to reasoning research

**Their Edge**: Empirical scale, real-world production data

**Complementary**: Our theory explains their observations; their data validates our categories

---

## Research Priorities

Based on frequency and severity of failures across categories:

### Priority 1: Meta-Cognitive Monitoring (C3)
- Most pervasive limitation
- Affects planning, self-correction, progress monitoring
- **Research question**: Can LLMs be trained for reliable self-monitoring?

### Priority 2: Self-Correction Capability (C7)
- Same-model reflection fundamentally unreliable
- Critical for autonomous operation
- **Research question**: What external verification is sufficient? Multi-model vs. tool-based?

### Priority 3: Reasoning-Reliability Trade-off (C8)
- Paradoxical: better reasoning → more hallucination
- Challenges fundamental assumptions
- **Research question**: Can this trade-off be broken, or must we accept it?

### Priority 4: Long-Range Coherence (C2)
- Hard limit on task complexity
- Attention mechanism architectural constraint
- **Research question**: What alternatives to quadratic attention preserve capabilities?

### Priority 5: Factual Grounding (C1)
- Underlies most hallucination types
- Persistent across models and training methods
- **Research question**: How to reliably separate retrieval from generation?

---

## Next Steps for Validation

### 1. Controlled Experiments
**Goal**: Quantify architecture-failure correlations
**Method**: Reproduce key failures (tool hallucination, infinite loops, false completion) across 3+ frameworks
**Output**: Frequency distribution table, architecture risk profiles

### 2. Boundary Testing
**Goal**: Verify category boundaries are clear and mutually exclusive
**Method**: Code additional ambiguous instances, check classification agreement
**Output**: Inter-rater reliability metrics, refined boundary criteria

### 3. Mitigation Evaluation
**Goal**: Test which architectural changes reduce which failures
**Method**: Implement mitigations (external memory, verification, etc.) and measure impact
**Output**: Mitigation effectiveness table

### 4. Model Comparison
**Goal**: Compare limitation profiles across LLMs
**Method**: Test C1-C8 capabilities on GPT-4, Claude, Llama
**Output**: Model capability matrix

---

## Taxonomy Summary Statistics

**Total instances**: 50
**Major categories**: 9
**Sub-categories**: 24
**Codes generated**: ~150
**Cross-cutting patterns**: 9
**LLM dimensions**: 8 (C1-C8)
**Fundamental limitations**: 5
**Design principles**: 6
**Architecture patterns**: 11

**Coverage by source**:
- Research papers: 15 instances (30%)
- GitHub issues: 12 instances (24%)
- Benchmarks: 11 instances (22%)
- Framework docs: 5 instances (10%)
- Surveys: 10 instances (20%)

**Coverage by architecture**:
- All architectures: 21 instances (42%)
- ReAct: 11 instances (22%)
- Autonomous loop: 4 instances (8%)
- Reflection: 3 instances (6%)
- Coding agents: 3 instances (6%)
- Plan-then-execute: 3 instances (6%)
- Multi-agent: 3 instances (6%)
- ToT: 2 instances (4%)

**Reproducibility**:
- Easy: 29 instances (58%)
- High: 11 instances (22%)
- Medium: 9 instances (18%)
- Hard: 1 instance (2%)

---

## Paper Outline (Preliminary)

### 1. Introduction
- Agent deployment increasing, failures poorly understood
- Existing work: individual failure reports, partial taxonomies
- Gap: No comprehensive taxonomy with theoretical grounding
- Contributions: Hierarchical taxonomy, LLM limitation mapping, design principles

### 2. Related Work
- Agent architectures (ReAct, plan-then-execute, Reflexion, etc.)
- Existing taxonomies (MAST, Three-Phase, AgentErrorTaxonomy, Characterizing Faults)
- LLM limitations (reasoning, hallucination, context, self-correction)

### 3. Methodology
- Grounded theory approach
- Data collection (50 instances, 2023-2026)
- Open coding → axial coding → theoretical mapping
- Validation: controlled experiments

### 4. Taxonomy Structure
- 9 major categories, 24 sub-categories
- Definitions, examples, boundary criteria
- Tables: category distribution, reproducibility, sources

### 5. LLM Limitation Mapping
- 8 capability dimensions (C1-C8)
- Failure-to-limitation connections
- Fundamental vs. correctable distinction
- Table: mapping matrix

### 6. Architecture-Failure Correlation
- Architecture-specific patterns
- Risk profiles and trade-offs
- Table: correlation matrix
- Controlled experiment results

### 7. Design Principles
- 6 principles with rationale
- Implementation guidance
- Mitigation strategies evaluation

### 8. Discussion
- Research priorities
- Fundamental limitations vs. engineering gaps
- Implications for agent deployment
- Limitations of current study

### 9. Conclusion
- Summary of contributions
- Future work: expanded experiments, model comparison, capability benchmarks

---

## Status

**Phase**: Taxonomy development substantially complete
**Confidence**: High (0.8) — grounded in systematic analysis
**Next**: Controlled experiments for empirical validation
**Timeline**: Ready for paper writing alongside experiments
**Venue**: ACL 2027 (February 2027 deadline)

**Ready to proceed with**:
- Competitor deep-read (can now compare structures)
- Controlled experiment design
- Paper introduction and related work sections
- Taxonomy visualization (hierarchical diagram)

---

## Key Insights

1. **Most failures have LLM capability roots**: Only 3 of 9 categories are pure architectural/engineering issues
2. **Meta-cognitive monitoring (C3) is the critical gap**: Agents cannot reliably monitor their own reasoning
3. **Self-correction requires external verification**: Same-model reflection is fundamentally unreliable (C7)
4. **State divergence is everywhere**: Central pattern across categories 1, 4, 5, 7
5. **Some "failures" are trade-offs**: C8 reasoning-reliability paradox, architectural capacity limits
6. **Context degradation is a hard wall**: C2 limits all architectures at ~32k tokens
7. **Evaluation issues obscure true capabilities**: 10% of "failures" are actually infrastructure problems
8. **Architecture choice matters**: Different architectures have different failure profiles

---

## Document Complete

This taxonomy provides:
- ✅ Comprehensive categorization (9 categories, 24 sub-categories)
- ✅ Theoretical grounding (mapped to LLM capabilities)
- ✅ Practical guidance (6 design principles)
- ✅ Research priorities (C3, C7, C8, C2, C1)
- ✅ Architecture selection guidance (risk profiles)
- ✅ Fundamental vs. correctable distinction

**Ready for publication after empirical validation**