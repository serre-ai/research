# Axial Coding: Category Relationships and Boundary Refinement

**Date**: 2026-03-25
**Phase**: Axial Coding (Grounded Theory)
**Input**: 50 coded instances, 9 provisional categories, 150 codes

---

## Purpose of Axial Coding

Axial coding goes beyond open coding's descriptive labels to:
1. **Identify relationships** between categories (causal, temporal, hierarchical)
2. **Refine category boundaries** to ensure mutual exclusivity
3. **Distinguish root causes from symptoms**
4. **Map architectural vs. fundamental limitations**
5. **Build theoretical framework** connecting agent failures to LLM capabilities

---

## Category Relationship Analysis

### Relationship Type 1: Causal Chains (X causes Y)

#### Grounding Failures → Tool-Use Failures
**Relationship**: Insufficient grounding causes tool selection/execution errors

**Evidence**:
- Instance 32: ReAct tool hallucination — agent doesn't ground to available tool registry → fabricates plausible tools
- Instance 27: API version mismatch — agent's API model doesn't match reality → tool call fails
- Instance 42: Domain-specific syntax — agent doesn't ground to API semantics → wrong query format

**Implication**: **Grounding failures are often root causes** of tool-use failures. The agent's internal model of tools diverges from reality.

**Boundary question**: Is "tool selection hallucination" a grounding failure or tool-use failure?
- **Answer**: It's **both** — grounding is the root cause, tool-use is the symptom. We should classify by **proximal failure** (tool-use) but note **root cause** (grounding).

---

#### State Tracking Failures → Error Propagation
**Relationship**: State divergence enables errors to propagate silently

**Evidence**:
- Instance 11: Cache corruption → cached error treated as success → propagates to future attempts
- Instance 20: Memory corruption → error persists across sessions → contaminates future reasoning
- Instance 25: False state reporting → downstream systems trust false state → cascading failures

**Implication**: **State tracking failures create conditions for error propagation**. If the agent's state diverges from reality, errors become invisible and spread.

**Boundary question**: When does a state tracking failure become error propagation?
- **Answer**: State tracking failure = initial divergence. Error propagation = the spreading/cascading that follows. Classify by **primary phenomenon** observed.

---

#### Planning Failures → Infinite Loops → Resource Exhaustion
**Relationship**: Progress monitoring inadequacy causes loops which exhaust resources

**Evidence**:
- Instance 14: AutoGPT looping — ambiguous task → no progress detection → infinite loop → cost exhaustion
- Instance 33: ReAct infinite loops — impossible task → no meta-reasoning → iteration limit hit

**Implication**: This is a **causal chain** where planning failure (root) → loop (manifestation) → resource issue (consequence). Classify as **planning failure** with loop as the symptom.

---

#### Self-Correction Failures → False Completion → State Divergence → Cascading Errors
**Relationship**: Multi-step causal chain

**Evidence**:
- Instance 19: False completion → agent believes task done → downstream accepts false state → cascading decisions based on wrong assumptions

**Implication**: **Cascading causality** — one failure type triggers another. This validates the need for tracking **failure chains** not just individual failures.

---

### Relationship Type 2: Mutual Reinforcement (X amplifies Y, Y amplifies X)

#### Reasoning Enhancement ↔ Tool Hallucination (Paradox)
**Relationship**: Better reasoning increases tool hallucination; hallucination undermines reasoning

**Evidence**:
- Instance 17: Reasoning-hallucination paradox — stronger reasoning → more detailed tool models → more divergence from reality → more hallucination

**Implication**: This is a **fundamental trade-off**, not just a failure. It's a constraint on the entire system. This belongs in a special category: **Fundamental Limitations** rather than correctable failures.

---

#### Error Propagation ↔ Memory/State Systems
**Relationship**: Memory enables propagation; propagation corrupts memory

**Evidence**:
- Instance 20: Memory persistence — error written to memory → influences future reasoning → more errors written → memory becomes progressively more corrupted

**Implication**: Systems with memory have **bidirectional failure dynamics** — memory can be corrupted by errors, and corrupted memory generates more errors. This is a **positive feedback loop**.

---

### Relationship Type 3: Common Root Cause (X and Y both caused by Z)

#### Tool Hallucination + Constraint Hallucination ← LLM Generation Bias
**Common Root**: LLM fills information gaps with plausible generation

**Evidence**:
- Instance 18: Tool fabrication — too many tools → documentation overload → LLM generates plausible tool name
- Instance 23: Constraint hallucination — complex problem → working memory limit → LLM adds plausible constraint
- Instance 15: Web content hallucination — incomplete scraped data → LLM fills gaps with plausible facts

**Implication**: These are **manifestations of the same LLM behavior** in different domains. The underlying cause is: **LLM generation fills gaps when retrieval fails**. This suggests a unified category: **Hallucination Under Insufficient Grounding**.

---

#### Context Exhaustion + Lost in the Middle ← Attention Mechanism Limits
**Common Root**: Quadratic attention cost and positional bias

**Evidence**:
- Instance 49: Context rot — O(n²) scaling → performance degradation at long context
- Instance 50: Lost in middle — attention favors extremes → middle content invisible

**Implication**: Both stem from **attention architecture limitations**. Should be grouped together as **Context-Based State Tracking Failures** with shared fundamental cause.

---

### Relationship Type 4: Architectural Trade-offs (X enables Y but causes Z)

#### ReAct: Tight Feedback Loop
**Trade-off**: Enables responsiveness but prevents meta-reasoning

**Evidence**:
- Instance 33: Infinite loops — tight loop allows quick action-observation but no global progress view
- Instance 34: Context exhaustion — storing all traces in context enables tight loop but hits capacity

**Implication**: This is not a "failure" but an **architectural choice with inherent constraints**. Classifying these as "failures" is misleading. Better framing: **Architectural Capacity Limits**.

---

#### Plan-Then-Execute: Initial Planning
**Trade-off**: Enables reasoning quality but creates commitment and replanning cost

**Evidence**:
- Instance 25: False completion — upfront planning without feedback → state divergence
- Lit note: Replanning expensive → may repeat mistakes if root cause not identified

**Implication**: Architectural trade-off between **reasoning depth vs. adaptability**. Not a pure failure.

---

### Relationship Type 5: Hierarchical (X is a specific instance of Y)

#### Tool-Use Failures: Hierarchy

**Top level**: Tool-Use Failures
- **Selection failures** (choosing wrong/non-existent tool)
  - Tool fabrication (Instance 18, 32)
  - Tool confusion (Instance 18)
  - Wrong tool selection
- **Execution failures** (using tool incorrectly)
  - Parameter errors (Instance 29)
  - Hallucinated parameters (Instance 17)
  - Result interpretation errors
- **Integration failures** (framework/provider issues)
  - Provider compatibility (Instance 12, 30)
  - Framework compatibility (Instance 26)
  - API version mismatch (Instance 27)

**Implication**: Tool-use failures have clear **sub-types** that should be represented in hierarchy.

---

#### Grounding Failures: Hierarchy

**Top level**: Grounding Failures
- **Input grounding** (misunderstanding task/environment)
  - Constraint hallucination (Instance 23)
  - Instruction misinterpretation (Instance 41)
  - Action space assumptions (Instance 35)
- **Observation grounding** (misinterpreting tool outputs)
  - Observation interpretation errors (Instance 15)
  - Timing mismatches (Instance 37)
  - Modality limitations (Instance 40)
- **API grounding** (misunderstanding APIs/tools)
  - Domain-specific syntax (Instance 42)
  - Provider assumptions (Instance 12)

**Implication**: Grounding has **three distinct phases** in agent pipeline where it can fail.

---

## Boundary Refinement: Ambiguous Cases

### Case 1: Is "false completion" self-correction or state tracking?

**Instance 19**: Agent reports task complete when it's not

**Arguments for Self-Correction**:
- Involves self-evaluation mechanism
- Would be caught by better verification
- About agent assessing its own work

**Arguments for State Tracking**:
- Creates state divergence (reported ≠ actual)
- Root issue is state management
- Symptom is incorrect internal state

**Resolution**: **Primary category: Self-Correction Failures → False Verification**. **Secondary tag: State Tracking** (creates state divergence as consequence). Use **primary + secondary tagging** for failures that span categories.

---

### Case 2: Is "infinite loop" a planning or error recovery failure?

**Instances 14, 33**: Agent loops indefinitely

**Arguments for Planning**:
- Failure to detect lack of progress
- Missing meta-cognitive monitoring
- Planning system should recognize stagnation

**Arguments for Error Recovery**:
- Agent not recognizing it's stuck (error state)
- Not recovering from repeated failure
- Should trigger replanning

**Resolution**: **Primary category: Planning Failures → Progress Monitoring**. The root issue is **lack of global progress evaluation** in the planning system. Error recovery would be a mitigation, but the absence of progress monitoring is the architectural gap.

---

### Case 3: Is "tool hallucination" a tool-use or reasoning failure?

**Instance 17**: Better reasoning increases tool hallucination

**Arguments for Tool-Use**:
- Manifests as incorrect tool calls
- Proximal failure is in tool interaction
- User experiences tool errors

**Arguments for Reasoning**:
- Caused by reasoning enhancement
- Internal reasoning process creates wrong model
- Fundamental reasoning limitation

**Resolution**: **Dual classification needed**:
- **Symptom level** (for practitioners): Tool-Use Failures → Hallucinated Execution
- **Root cause level** (for researchers): Fundamental LLM Limitations → Reasoning-Reliability Trade-off

Taxonomy should have **two views**: symptom-based (what practitioners observe) and cause-based (what researchers study).

---

### Case 4: Are evaluation failures "agent failures"?

**Instances 38, 39**: Benchmark environment/criteria issues

**Arguments for Inclusion**:
- Practitioners experience them as "agent failures"
- Important to distinguish from true agent issues
- Helps debug whether problem is agent or evaluation

**Arguments for Exclusion**:
- Not actually agent failures
- Dilutes taxonomy focus
- Should be in separate evaluation methodology paper

**Resolution**: **Include but clearly separate**. Create **Evaluation/Environment Failures** as distinct top-level category with clear note that these are **not agent failures** but **measurement/infrastructure issues**. This helps practitioners diagnose correctly.

---

## Refined Category Structure (Hierarchical)

### Version 2.0: Post-Axial Coding

#### 1. Tool-Use Failures (16 instances)
**Definition**: Agent incorrectly selects, executes, or integrates tools

**Sub-categories**:
- 1.1 Selection Failures
  - Tool fabrication/hallucination
  - Wrong tool selection
  - Tool confusion
- 1.2 Execution Failures
  - Parameter errors
  - Hallucinated execution
  - Result interpretation errors
- 1.3 Integration Failures
  - Provider compatibility issues
  - Framework version incompatibilities
  - API version mismatches
- 1.4 Code Generation Errors (coding agents)
  - Semantic incorrectness
  - Overfitting to test cases

**Root causes**: Grounding failures (1.1, 1.2), External dependency changes (1.3), LLM generation limits (1.4)

**Architecture correlation**: All architectures, especially base models without fine-tuning

---

#### 2. Grounding Failures (8 instances)
**Definition**: Agent's model of the environment/task diverges from reality

**Sub-categories**:
- 2.1 Input Grounding
  - Constraint/feature hallucination
  - Instruction misinterpretation
  - Action space misunderstanding
- 2.2 Observation Grounding
  - Tool output misinterpretation
  - Timing assumption violations
  - Modality limitations
- 2.3 API Grounding
  - Domain-specific syntax mismatches
  - Provider capability assumptions
  - Environment accessibility

**Root causes**: LLM knowledge limits, observation modality constraints, external environment variability

**Architecture correlation**: All architectures; web agents particularly affected by timing/modality issues

---

#### 3. Planning Failures (7 instances)
**Definition**: Agent's planning or reasoning process fails to produce effective action sequences

**Sub-categories**:
- 3.1 Progress Monitoring
  - Stagnation detection failure
  - Infinite loops
  - Premature completion
- 3.2 Instruction Processing
  - Decomposition failures
  - Partial satisfaction
- 3.3 Reasoning Quality
  - Prompt brittleness
  - Reasoning fragility
  - Performance without adaptation

**Root causes**: Lack of meta-cognitive monitoring, prompt dependence, architectural adaptation requirements

**Architecture correlation**: ReAct (tight loop prevents meta-reasoning), ToT (prompt sensitive), base models (need fine-tuning)

---

#### 4. State Tracking Failures (6 instances)
**Definition**: Agent's representation of system state diverges from actual state

**Sub-categories**:
- 4.1 State Divergence
  - False state reporting
  - Action-state misalignment
- 4.2 Memory Issues
  - Memory corruption
  - Cache corruption
  - Cross-session error persistence
- 4.3 Context Management
  - Context window exhaustion
  - Long context degradation
  - Positional bias (lost in middle)

**Root causes**: Lack of external verification (4.1), No memory validation (4.2), Attention mechanism limits (4.3)

**Architecture correlation**: ReAct (context as memory), systems with persistent memory (4.2), all long-context systems (4.3)

---

#### 5. Self-Correction Failures (6 instances)
**Definition**: Agent's attempts to verify or correct its work fail

**Sub-categories**:
- 5.1 Verification Failures
  - False completion reporting
  - False action confirmation
  - Test gaming (coding agents)
- 5.2 Reflection Failures (Reflexion)
  - Confirmation bias
  - Degeneration-of-thought
  - Complexity plateaus
  - Training degeneration
- 5.3 Error Routing
  - Sending errors to wrong recipient

**Root causes**: Same-model self-evaluation limits (5.2), Lack of external ground truth (5.1), Recipient confusion (5.3)

**Architecture correlation**: Reflexion (5.2 specific), plan-then-execute (5.1 common), all architectures need external validation

---

#### 6. Error Recovery Failures (4 instances)
**Definition**: Agent fails to detect, handle, or recover from errors

**Sub-categories**:
- 6.1 Error Detection
  - Tool failure undetected
  - Silent error continuation
- 6.2 Error Handling
  - Parsing error non-recovery
  - Retry absence
  - No graceful degradation

**Root causes**: Inadequate error handling logic, framework regression, missing recovery mechanisms

**Architecture correlation**: All architectures; framework-dependent implementations

---

#### 7. Error Propagation (3 instances)
**Definition**: Errors spread through time (memory) or space (messages/edits)

**Sub-categories**:
- 7.1 Temporal Propagation
  - Memory persistence of errors
  - Cross-session contamination
- 7.2 Spatial Propagation
  - Cascading edits (coding agents)
  - Cross-agent amplification (multi-agent)
- 7.3 Causal Chains
  - One failure triggering downstream failures

**Root causes**: State tracking failures (enable propagation), Lack of error isolation, Feedback loops

**Architecture correlation**: Systems with memory (7.1), Coding agents (7.2), Multi-agent (7.2), All with causal chains (7.3)

---

#### 8. Evaluation/Environment Failures (5 instances) [NOT AGENT FAILURES]
**Definition**: Perceived failures caused by measurement/environment issues, not agent

**Sub-categories**:
- 8.1 Environment Limitations
  - UI accessibility issues
  - Element representation inadequacy
- 8.2 Evaluation Criteria Issues
  - Overly restrictive string matching
  - Oracle insufficiency
- 8.3 Evaluation Methodology
  - Failure source conflation
  - Aggregate metric inadequacy

**Root causes**: Benchmark design issues, Test incompleteness, Measurement validity

**Architecture correlation**: N/A — these are not agent failures

**Note**: Included to help practitioners distinguish agent vs. infrastructure problems

---

#### 9. Security Vulnerabilities (2 instances)
**Definition**: Agent exposes sensitive information or creates security risks

**Sub-categories**:
- 9.1 Information Leakage
  - Credential exposure
  - Exception sanitization failures

**Root causes**: Output path not secured, Error handling not sanitized

**Architecture correlation**: All production systems

**Note**: Likely under-represented in current dataset (only 2 instances); production systems probably have more

---

## Fundamental LLM Limitations (Cross-Cutting)

These are **not failures to fix** but **constraints to design around**:

### L1: Reasoning-Reliability Trade-off
- Better reasoning → more tool hallucination
- Cannot be eliminated without sacrificing capability
- Affects: Tool-use failures, Self-correction failures
- **Design implication**: Need external verification for high-stakes decisions

### L2: Context Degradation
- Performance drops at long context (50% at 32k tokens)
- Positional bias (lost in middle)
- O(n²) attention cost
- Affects: State tracking failures, Planning failures
- **Design implication**: Need compression, retrieval, external memory

### L3: Hallucination Under Insufficient Grounding
- LLM fills gaps with generation when retrieval fails
- Scales with complexity and ambiguity
- Affects: Tool-use failures, Grounding failures
- **Design implication**: Provide complete documentation, validate outputs

### L4: Scaling Failures
- Tool selection degrades with tool count
- Context limits bound task complexity
- Affects: Tool-use failures, State tracking failures
- **Design implication**: Organize/filter tools, limit complexity

---

## Architecture-Failure Correlation Matrix (Preliminary)

| Architecture | High-Risk Failures | Medium-Risk | Low-Risk |
|--------------|-------------------|-------------|----------|
| **ReAct** | Progress monitoring (infinite loops), Context exhaustion, Fine-tuning dependency | Tool hallucination, Grounding failures | N/A |
| **Plan-then-Execute** | False completion, State verification, Replanning cost | N/A | Infinite loops (upfront planning prevents) |
| **Reflexion** | Confirmation bias, Degeneration, Complexity plateau | All general failures | N/A |
| **Autonomous Loop** | Infinite loops, Resource exhaustion | Progress detection, Web hallucinations | N/A |
| **ToT** | Prompt brittleness, Constraint hallucination, High cost | N/A | N/A |
| **Coding Agents** | Semantic incorrectness, Edit cascades, Test gaming | N/A | N/A |

**Note**: This is preliminary based on current 50 instances. Controlled experiments needed to quantify frequencies.

---

## Key Insights from Axial Coding

1. **Causal chains are common**: Many observed failures are symptoms of deeper root causes. Need both symptom-based (for practitioners) and cause-based (for researchers) views.

2. **Fundamental limitations vs. correctable failures**: 4 LLM limitations are constraints to design around, not bugs to fix. Conflating these leads to wrong solutions.

3. **Architecture trade-offs, not just failures**: Some "failures" are inherent to architectural choices. Better framing: capacity limits, not defects.

4. **State divergence is central**: Many failure types create or result from divergence between agent's internal model and reality. External verification is the key mitigation across categories.

5. **Error propagation is underappreciated**: Failures don't stay local — they spread through memory, messages, and causal chains. Need error isolation mechanisms.

6. **Hierarchical structure needed**: Flat taxonomy hides important relationships. Two-level hierarchy (category → sub-category) provides right granularity.

7. **Multi-view taxonomy needed**: Practitioners need symptom-based view; researchers need cause-based view. Both should be provided.

---

## Next Steps

1. **Test boundary criteria**: Take ambiguous instances and verify they map clearly to refined categories
2. **Map all 50 instances to refined hierarchy**: Ensure no gaps or overlaps
3. **Deep-read competitor paper**: Now that our structure is stable, compare to "Characterizing Faults in Agentic AI" (37 categories) to articulate differentiation
4. **Quantify architecture correlation**: Move from qualitative observations to quantitative frequency analysis (requires controlled experiments)
5. **Develop mitigation strategies**: For each category, identify architectural changes, prompting strategies, or external tools that reduce failures

---

## Axial Coding Session Complete

**Relationships identified**: 5 types (causal, mutual reinforcement, common root, trade-offs, hierarchical)
**Boundaries refined**: 4 ambiguous cases resolved with primary + secondary tagging
**Category structure**: Evolved from flat 9 categories to hierarchical 9 categories with 2-3 sub-categories each
**Fundamental limitations**: Distinguished 4 LLM constraints from correctable failures
**Architecture correlation**: Preliminary matrix developed, needs empirical validation

**Ready for**: Testing refined categories against data, competitor analysis, controlled experiments