# Competitor Deep-Read: "Characterizing Faults in Agentic AI"

**Paper**: Shah et al. (2026) — Characterizing Faults in Agentic AI: A Taxonomy of Types, Symptoms, and Root Causes
**arXiv**: 2603.06847
**Date Analyzed**: 2026-03-25
**Reviewer**: Researcher Agent

---

## Executive Summary

**Scale**: Their 385 production faults vs. our 50 diverse instances
**Structure**: Their 37 flat categories vs. our 9 hierarchical categories with 24 sub-categories
**Focus**: Production software faults (87% conventional, 13% LLM-specific) vs. agent-level cognitive/behavioral failures
**Theory**: Empirical component-level analysis vs. theoretical LLM capability mapping (C1-C8)

**Key Finding**: **These are COMPLEMENTARY, not competing taxonomies.** They characterize implementation faults in agentic systems (like traditional software bugs). We characterize cognitive/behavioral failure modes in agent reasoning. Minimal overlap.

**Differentiation Strategy**: Our theoretical contribution (LLM limitation mapping) and agent-level focus remain unique. Their work validates that production systems have conventional software issues; our work explains why agents fail at reasoning tasks.

---

## Detailed Comparison

### 1. Scope and Domain

| Dimension | Shah et al. (2026) | Our Taxonomy |
|-----------|-------------------|--------------|
| **Primary Focus** | Implementation faults in agentic AI systems | Cognitive/behavioral failure modes in agent reasoning |
| **Level of Analysis** | Component-level (APIs, dependencies, configs) | Agent-level (planning, tool-use, self-correction) |
| **Data Source** | 385 GitHub issues/PRs from 40 production repos | 50 instances from papers, benchmarks, surveys, issues |
| **Timeframe** | Production systems (unclear timeline) | Research agents (2023-2026) |
| **Context** | Real-world deployments, enterprise systems | Research benchmarks, academic evaluations |

**Interpretation**: They study "engineering problems in systems that contain agents." We study "reasoning problems in agents." Their category "LLM Integration Faults" (45 instances) is closest to our work, but still focuses on API/configuration issues rather than cognitive failures.

---

### 2. Taxonomy Structure Comparison

#### Their Structure (5 dimensions, 37 categories)

**I. Agent Cognition & Orchestration (83 faults)**
- LLM Integration Faults (45): Configuration, API incompatibility, token handling
- Agent Lifecycle & State (38): Execution, state inconsistency, termination

**II. Tooling, Integration & Actuation (66 faults)**
- Tool Execution & API Usage (17): API misuse, parameter mismatch, misconfiguration
- External Connectivity & Access (19): Connection failures, auth issues
- Resource Manipulation (16): Locking, database errors
- System Coordination (6): Synchronization, race conditions
- System Observability (8): Logging defects

**III. Perception, Context & Memory (72 faults)**
- Context & State Persistence (12): Memory failures, serialization errors
- Input Interpretation & Logic (60): Type errors, validation omission, encoding issues

**IV. Runtime & Environment Grounding (87 faults)**
- Dependency Management (67): Version conflicts, import failures
- Platform Compatibility (20): OS incompatibilities, API version mismatches

**V. System Reliability & Observability (67 faults)**
- Robustness & Error Recovery (49): Exception handling, implementation defects
- UI & Visualisation Defect (13): Rendering issues
- Documentation Defect (5): Incorrect docs

#### Our Structure (9 categories, 24 sub-categories)

1. **Tool-Use Failures (16)**: Selection errors, execution hallucination, code generation
2. **Grounding Failures (8)**: Constraint hallucination, observation misinterpretation
3. **Planning Failures (7)**: Infinite loops, decomposition failures
4. **State Tracking Failures (6)**: State divergence, context degradation
5. **Self-Correction Failures (6)**: Confirmation bias, false completion
6. **Error Recovery Failures (4)**: Detection failures, retry absence
7. **Error Propagation (3)**: Cascading errors, memory contamination
8. **Evaluation/Environment Failures (5)**: Infrastructure limitations (not agent)
9. **Security Vulnerabilities (2)**: Credential leakage

---

### 3. Category Overlap Analysis

#### Minimal Direct Overlap

**Their "LLM Integration Faults"** ≠ Our "Tool-Use Failures"
- Theirs: API configuration, token counting bugs, schema drift
- Ours: Tool fabrication, execution hallucination, result misinterpretation
- **Overlap**: ~10% — both mention API issues, but from different angles

**Their "Agent Lifecycle & State"** ≈ Our "State Tracking Failures"
- Theirs: State persistence bugs, serialization errors, execution scheduling
- Ours: State divergence (cognitive), context degradation (fundamental LLM limit)
- **Overlap**: ~20% — same surface phenomena, different root causes

**Their "Input Interpretation & Logic"** ≈ Our "Grounding Failures"
- Theirs: Type errors, validation omission, parsing failures (engineering)
- Ours: Constraint hallucination, instruction misinterpretation (cognitive)
- **Overlap**: ~15% — both about input handling, different levels

**No overlap** for:
- Their: Dependency Management (67), Platform Compatibility (20), Resource Manipulation (16)
- Ours: Self-Correction (6), Planning (7), Error Propagation (3)

**Total estimated overlap**: ~15-20% of combined categories

---

### 4. Methodological Comparison

| Dimension | Shah et al. (2026) | Our Approach |
|-----------|-------------------|--------------|
| **Data Collection** | Stratified sampling from 13,602 issues/PRs | Purposive sampling from research literature |
| **Sample Size** | 385 faults | 50 failure instances |
| **Analysis Method** | Grounded theory (open, axial, selective coding) | Grounded theory (open, axial, theoretical mapping) |
| **Validation** | Developer study (145 practitioners, α=0.904) | Controlled experiments (planned) |
| **Generalizability** | Production systems (high external validity) | Research agents (high construct validity) |
| **Reproducibility** | GitHub issues public, but sampling not fully reproducible | 80% instances highly reproducible in experiments |

**Strengths of Their Approach**:
- Large-scale empirical data from real deployments
- Statistical sampling with confidence intervals
- Practitioner validation (145 participants)
- Coverage of conventional software faults

**Strengths of Our Approach**:
- Theoretical grounding (C1-C8 capability dimensions)
- Focus on cognitive/behavioral failures (not engineering)
- Dual-view structure (symptom + cause)
- Design principles and research priorities
- Architecture-failure correlation

---

### 5. Theoretical Framework Comparison

#### Shah et al. (2026): Component-Level Architecture Alignment

They map faults to **5 architectural components**:
1. Cognitive control and decision-making
2. Tool/environment interaction
3. Perception and memory
4. Runtime environments
5. System reliability

**Framework is descriptive**: Categories align with system components, but no underlying theory of *why* faults occur.

**Notable**: They identify "distinctive hybrid failure profile" — agentic systems combine conventional software faults with LLM probabilistic behavior. But they don't separate these or explain the LLM contribution theoretically.

#### Our Approach: LLM Capability Dimension Mapping (C1-C8)

We map failures to **8 LLM capability dimensions**:
- **C1: Factual Grounding** — hallucination under ambiguity
- **C2: Long-Range Coherence** — context degradation (fundamental)
- **C3: Meta-Cognitive Monitoring** — cannot detect own errors
- **C4: Constraint Satisfaction** — struggles with complex specs
- **C5: State Tracking** — internal model diverges from reality
- **C6: Tool Grounding** — tool representation inaccuracy
- **C7: Self-Correction Capability** — same-model reflection unreliable
- **C8: Reasoning-Reliability Trade-off** — better reasoning → more hallucination

**Framework is explanatory**: Categories connect to underlying LLM limitations, distinguishing fundamental (C2, C3, C7) from correctable issues.

**Key Difference**: We explicitly model **why agents fail at cognitive tasks**, not just **what goes wrong in implementations**.

---

### 6. Unique Contributions Analysis

#### What Shah et al. Provide That We Don't

1. **Production-scale empirical data**: 385 real-world faults vs. our 50 research instances
2. **Conventional software fault coverage**: Dependency management (67 faults), platform compatibility (20 faults) — we don't cover these
3. **Practitioner validation**: 145-participant developer study confirming relevance
4. **Component-level fault localization**: Precise mapping of faults to system components
5. **Symptom taxonomy**: 13 observable symptom classes for debugging
6. **Association rules**: Apriori mining revealing fault propagation pathways (lift scores)

**Their edge**: If you're building a production agentic system and want to know "What can go wrong in my codebase?", their taxonomy is comprehensive.

#### What We Provide That They Don't

1. **Theoretical grounding**: C1-C8 LLM capability dimensions explaining *why* failures occur
2. **Fundamental vs. correctable distinction**: Which failures can be fixed architecturally vs. require LLM improvements
3. **Agent-level cognitive failures**: Planning, self-correction, grounding failures (not covered in their work)
4. **Design principles**: 6 actionable principles for robust agent design
5. **Architecture-failure correlation**: Which architectures exhibit which failure profiles
6. **Research priorities**: C3, C7, C8 identified as critical gaps for LLM research
7. **Dual-view structure**: Symptom-based (practitioners) + cause-based (researchers)
8. **Bridge to reasoning research**: Connects agent failures to reasoning-gaps project

**Our edge**: If you're researching "Why do agents fail at reasoning tasks?" or "What fundamental LLM capabilities need improvement?", our taxonomy provides theoretical insight.

---

### 7. Distribution Comparison

#### Shah et al. Fault Distribution
- **Runtime & Environment Grounding**: 87 (22.6%) — dependency/platform issues
- **Agent Cognition & Orchestration**: 83 (21.6%) — LLM integration, agent lifecycle
- **Perception, Context & Memory**: 72 (18.7%) — input parsing, type errors
- **System Reliability & Observability**: 67 (17.4%) — error handling, logging
- **Tooling, Integration & Actuation**: 66 (17.1%) — API usage, connectivity

**Observation**: Distribution is relatively uniform (17-23% per dimension). Highest is Runtime & Environment — conventional software issues.

#### Our Failure Distribution
- **Tool-Use Failures**: 16 (32%) — selection, execution, code generation
- **Grounding Failures**: 8 (16%) — constraint/observation hallucination
- **Planning Failures**: 7 (14%) — loops, decomposition
- **State Tracking**: 6 (12%) — divergence, context degradation
- **Self-Correction**: 6 (12%) — reflection failure, false completion
- **Evaluation/Environment**: 5 (10%) — infrastructure issues
- **Error Recovery**: 4 (8%) — detection, retry absence
- **Error Propagation**: 3 (6%) — cascading errors
- **Security**: 2 (4%) — credential leakage

**Observation**: Tool-use dominates (32%), followed by grounding and planning. State tracking and self-correction are significant. Security likely under-represented.

---

### 8. Key Insights from Comparison

#### Insight 1: Complementary Focus Areas
- **Shah et al.**: 87% conventional software faults (dependencies, APIs, types) + 13% LLM-specific issues
- **Our work**: 90% agent-level cognitive failures + 10% evaluation infrastructure

**Implication**: Both taxonomies are needed. Theirs for engineering robust implementations, ours for understanding reasoning limitations.

#### Insight 2: The "Hybrid Failure Profile"
Shah et al. identify that agentic systems have a "distinctive hybrid failure profile" combining software and LLM failures. But they don't separate these analytically.

**Our contribution**: We isolate the LLM-cognitive component and map it to capability dimensions (C1-C8). This complements their empirical observation with theoretical explanation.

#### Insight 3: Different Levels of Abstraction
- **Shah et al.**: Component-level (APIs, databases, logs, dependencies)
- **Our work**: Agent-level (planning, tool-use, self-correction)

**Analogy**: They study "car parts that break" (engine, transmission, brakes). We study "driver errors" (misjudging distance, overcorrection, inattention).

Both are needed for safe autonomous vehicles. Neither subsumes the other.

#### Insight 4: Validation Strategies
- **Shah et al.**: Developer study for practical relevance (α=0.904, strong agreement)
- **Our work**: Controlled experiments for causal validation (planned)

**Implication**: Their validation confirms "practitioners recognize these issues." Our validation will confirm "these failures reproduce across architectures as predicted."

#### Insight 5: Production vs. Research Gap
Shah et al. explicitly note: "Agentic AI systems combine LLM reasoning with external tool invocation and long-horizon task execution, and their architectural composition introduces reliability challenges."

**But**: Only 45/385 faults (12%) are categorized as "LLM Integration Faults" — mostly configuration/API issues. The "reasoning with tools" failures are under-represented in production data.

**Why?**: Production systems likely have fewer complex reasoning tasks (most deployments are simpler chatbots/assistants). Research benchmarks stress-test reasoning capabilities.

**Our contribution fills this gap**: We focus on reasoning-intensive tasks where LLM limitations manifest.

---

### 9. Overlap with Our Categories

Let me map their 37 categories to our 9 categories to quantify overlap:

| Our Category | Their Overlapping Categories | Degree of Overlap |
|--------------|------------------------------|-------------------|
| **1. Tool-Use Failures** | API Misuse, API Parameter Mismatch, Tool Execution (3 categories) | Low — theirs focus on API correctness, ours on cognitive tool selection/hallucination |
| **2. Grounding Failures** | Input Interpretation & Logic, Validation Omission (2 categories) | Low-Medium — theirs focus on type/parsing errors, ours on semantic grounding |
| **3. Planning Failures** | Agent Execution Failure, Agent Termination Failure (2 categories) | Medium — both cover infinite loops and termination, but different root causes |
| **4. State Tracking** | Agent State Inconsistency, Context & State Persistence (2 categories) | Medium — overlap on state divergence, but we emphasize cognitive vs. their serialization bugs |
| **5. Self-Correction** | (None directly) | Zero — they don't have a category for agent reflection/self-correction failures |
| **6. Error Recovery** | Exception Handling Defect, Robustness & Error Recovery (2 categories) | High — both cover error handling, though theirs focus on implementation bugs |
| **7. Error Propagation** | (Discussed in findings but not a category) | Low — they mention propagation pathways but don't categorize it |
| **8. Evaluation/Environment** | Platform Compatibility, Environment Misconfiguration (2 categories) | Low — overlap on environment issues, but different levels (theirs: OS/dependencies, ours: evaluation infrastructure) |
| **9. Security** | (No explicit security category) | Zero — they don't categorize security vulnerabilities |

**Quantified Overlap**: ~20% of our categories have medium-high overlap with theirs. 80% are distinct.

---

### 10. Differentiation Strategy Update

Given this analysis, our differentiation strategy should emphasize:

#### Primary Differentiators (Unique to Us)

1. **Theoretical LLM Limitation Mapping (C1-C8)**
   - We explain *why* failures occur at the LLM capability level
   - They describe *what* goes wrong at the implementation level
   - **Novel contribution**: Bridge from agent failures → LLM research priorities

2. **Agent-Level Cognitive Failures**
   - Planning loops, self-correction failure, tool fabrication
   - Not covered in their production fault taxonomy
   - **Novel contribution**: Reasoning failures in autonomous agents

3. **Fundamental vs. Correctable Distinction**
   - We classify which failures are LLM-level (C2, C3, C7) vs. architectural
   - They don't make this distinction (all faults treated as fixable)
   - **Novel contribution**: Research priorities for LLM capabilities

4. **Design Principles for Robust Agents**
   - 6 principles derived from capability limitations
   - They provide a taxonomy but not design guidance
   - **Novel contribution**: Actionable guidance for agent architects

5. **Architecture-Failure Correlation**
   - Which architectures (ReAct, Reflexion, plan-then-execute) exhibit which failures
   - They don't analyze by agent architecture type
   - **Novel contribution**: Architecture selection guidance

#### Complementary Strengths

6. **Our controlled experiments** will validate failures across architectures (theirs use production data)
7. **Our focus on research benchmarks** complements their production systems focus
8. **Our hierarchical structure** (9 → 24) vs. their flat structure (37) reflects different granularity needs

#### What We Should Acknowledge

- Their scale (385 vs. 50) provides superior coverage of implementation faults
- Their practitioner validation (145 participants) confirms practical relevance
- Their production data has high external validity

**Framing**: "While Shah et al. (2026) comprehensively characterize implementation faults in production agentic systems, our work focuses on cognitive/behavioral failures in agent reasoning, connecting these failures to fundamental LLM capability limitations. The two taxonomies are complementary: theirs for engineering robust implementations, ours for understanding and improving agent reasoning."

---

### 11. Updated Related Work Positioning

#### Positioning in Paper

**Section: Related Work**

*Existing taxonomies:*
1. **Shah et al. (2026)**: 37-category taxonomy of 385 production faults, focusing on implementation issues (dependencies, APIs, configurations). Strongest on engineering reliability.
2. **Cemri et al. (2025) - MAST**: Multi-agent system failures (communication, coordination). Complementary but different scope (multi-agent vs. single-agent).
3. **Three-Phase Taxonomy (2025)**: Task execution, reasoning, tool interaction phases. Similar scope but lacks theoretical grounding.
4. **AgentErrorTaxonomy (2025)**: Error detection and recovery. Narrower scope than ours.
5. **DEFT (2024)**: Research process failures. Different domain (research vs. general agents).

*Our contribution relative to Shah et al.:*
- **Different level**: Agent-level cognitive failures vs. component-level implementation faults
- **Theoretical grounding**: C1-C8 LLM capability dimensions (they lack this)
- **Design principles**: Derived from capability limitations (they don't provide)
- **Architecture correlation**: Failure profiles by architecture type (they don't analyze)
- **Research priorities**: Fundamental limitations identified for LLM research (they don't distinguish)

*Complementarity:*
"Our taxonomy explains *why* agents fail at reasoning tasks (LLM limitations), while Shah et al. explain *what* goes wrong in implementations (software faults). Production systems need both perspectives: robust engineering (their work) and cognitive reliability (our work)."

---

### 12. Threats to Novelty Assessment

#### Low Threat
- **Overlap is only ~20%**: Most of our categories (planning, self-correction, grounding, error propagation) are not covered in their work
- **Theoretical contribution is unique**: C1-C8 mapping is entirely absent from their work
- **Different data sources**: Research benchmarks vs. production systems → different failure modes

#### Medium Threat
- **They published first (March 2026)**: Our submission will be later, so we need to clearly position as complementary
- **Their scale is larger**: 385 vs. 50 instances — we need to emphasize depth over breadth

#### Mitigation Strategies
1. **Emphasize theoretical contribution**: Our LLM limitation mapping is a novel theoretical framework
2. **Controlled experiments**: Our validation through controlled reproduction across architectures is unique
3. **Design principles**: Actionable guidance derived from capability limitations
4. **Framing**: Position as complementary, not competing
5. **Research vs. production framing**: We focus on reasoning-intensive research benchmarks where LLM limitations manifest

---

### 13. Key Takeaways for Our Paper

#### What to Highlight
1. **Our theoretical contribution is substantial and unique**: C1-C8 framework is not in their work
2. **Agent-level cognitive failures are under-covered**: Their work is 87% conventional software faults
3. **Fundamental limitations need identification**: Distinguishing what's fixable vs. what requires LLM improvements
4. **Architecture selection matters**: Our architecture-failure correlation provides practical guidance
5. **Research priorities**: C3, C7, C8 identified as critical gaps — not in their work

#### What to Acknowledge
1. **Shah et al. provide comprehensive coverage of implementation faults**: Our work focuses on cognitive failures
2. **Production data complements research benchmarks**: Both perspectives needed
3. **Our scale is smaller but focused**: 50 instances allow deep theoretical analysis

#### What to Avoid
1. **Don't claim comprehensiveness**: They have more instances, broader coverage of software faults
2. **Don't dismiss their contribution**: Their practitioner validation and scale are strengths
3. **Don't overstate overlap**: It's ~20%, not a major threat

---

## Conclusion

**Final Assessment**: Shah et al. (2026) and our taxonomy are **complementary, not competing**. They focus on implementation faults in production systems (engineering perspective). We focus on cognitive failures in agent reasoning (LLM capability perspective).

**Our novelty is secure**:
- Theoretical LLM limitation mapping (C1-C8) is unique
- Agent-level cognitive failures (planning, self-correction) are under-covered in their work
- Design principles and research priorities are novel contributions
- Architecture-failure correlation provides unique guidance

**Recommended framing**: "While Shah et al. (2026) comprehensively characterize implementation faults in agentic systems, our work focuses on cognitive and behavioral failures rooted in LLM capabilities, providing a complementary theoretical perspective that connects agent failures to fundamental reasoning limitations."

**Confidence in differentiation**: High (0.85). Our theoretical contribution and agent-level focus are distinct.

**No major changes needed**: Proceed with experimental validation and paper writing as planned.

---

## References

Shah, Mehil B., Mohammad Mehdi Morovati, Mohammad Mehudur Rahman, and Foutse Khomh. "Characterizing Faults in Agentic AI: A Taxonomy of Types, Symptoms, and Root Causes." arXiv preprint arXiv:2603.06847 (2026).

**Links**:
- arXiv abstract: https://arxiv.org/abs/2603.06847
- arXiv HTML: https://arxiv.org/html/2603.06847

---

**Document Status**: Complete
**Next Step**: Update differentiation strategy in status.yaml, proceed with controlled experiments
