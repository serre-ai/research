# Initial Synthesis: Emerging Patterns from Literature Survey

**Date**: 2026-03-24
**Status**: Preliminary synthesis based on 20+ papers and 10 documented failure instances
**Purpose**: Identify recurring patterns, test hypotheses, guide next survey steps

---

## Cross-Cutting Failure Patterns

### 1. The Error Recovery Gap

**Pattern**: Agents consistently fail to recover gracefully from errors. Errors either:
- Propagate silently through subsequent steps (cascading failures)
- Cause complete task failure requiring manual intervention
- Get ignored, with agent continuing on incorrect assumptions

**Evidence**:
- LangChain #947: Agent generates fake tool results instead of retrying
- LangChain #33504: JSON parsing errors don't trigger automatic retry
- AutoGPT: Error propagation compounds through self-feedback loop
- CrewAI: Agents loop indefinitely after repeated failures
- Production (Toqan, Parcha): Agents can't recover from WebSocket drops or context issues

**Underlying cause**: Most agent architectures lack:
- Explicit error detection mechanisms beyond generic exception handling
- Retry strategies with backoff and error feedback
- Circuit breakers to prevent repeated failing actions
- Checkpointing/rollback capabilities

**Implication for taxonomy**: "Error recovery" likely needs to be a top-level category, not just sub-category of tool-use or execution

---

### 2. The Evaluation-Action Gap

**Pattern**: Agents struggle to accurately evaluate their own actions and outputs. Self-correction often fails because:
- Same model that made error tries to detect it (confirmation bias)
- Evaluation requires different capabilities than action generation
- Models confidently assert incorrect evaluations

**Evidence**:
- Voyager: Self-verification fails to recognize spider string as success signal
- Reflexion: Agents repeat same flawed reasoning across reflection iterations
- Multiple studies: "Intrinsic self-correction doesn't work well"
- Self-correction only succeeds with external feedback or different evaluation model

**Underlying cause**: Fundamental LLM limitation - models can't reliably meta-reason about their own outputs without external ground truth

**Implication for taxonomy**: Self-correction failures are distinct from execution failures - agent "succeeds" at action but fails to recognize it, or vice versa

---

### 3. The Grounding Problem Across Modalities

**Pattern**: Agents fail to correctly map between:
- Abstract instructions ↔ concrete actions
- Symbolic representations ↔ environment observations
- Domain concepts ↔ tool/API constraints

**Evidence**:
- Voyager: "Copper sword" doesn't exist in Minecraft, but model generates syntactically valid code
- WebArena: Can't interpret UI accessibility tree correctly (dropdown menus)
- Visual grounding: "UI grounding remains one of the major issues"
- Perceptual grounding: Linking instructions to high-dimensional sensory data

**Underlying cause**: LLMs operate on text representations of world, not direct environmental interaction. Mapping layer is fragile.

**Implication for taxonomy**: Grounding failures are distinct from planning or reasoning failures - agent may reason correctly about incorrect world model

---

### 4. The Context Degradation Cascade

**Pattern**: Agent performance degrades over long conversations/task horizons:
- < 4 minutes: ~100% success
- > 4 hours: < 10% success
- Information from middle of context effectively lost
- Repetition of completed subtasks

**Evidence**:
- AutoGPT: Forgets what it already did, repeats subtasks
- Long-running tasks: Dramatic performance drop after 4 hours
- Context window fills with noise (Parcha production example)
- "Lost in the middle" problem - start/end accessible, middle not

**Underlying cause**: Finite context windows + lack of memory architecture + degraded attention over long contexts

**Implication for taxonomy**: State tracking failures have temporal dimension - short-term vs. long-term memory failures are qualitatively different

---

### 5. The Coordination Brittleness Pattern

**Pattern**: Multi-agent systems fail at very high rates (41-86.7%) primarily due to inter-agent issues, not individual agent capabilities

**Evidence**:
- MAST taxonomy: Inter-agent misalignment is #1 failure mode
- CrewAI: Manager-worker architecture fails to coordinate effectively
- Production failures: 79% from specification/coordination, not technical implementation

**Underlying cause**: Coordination requires:
- Shared understanding of goals and state
- Communication protocol reliability
- Task decomposition agreement
- Conflict resolution mechanisms

**Implication for project scope**: Multi-agent is already covered by MAST (2025) - our focus on single-agent is correct differentiation

---

### 6. The Tool-Use Fragility Spectrum

**Pattern**: Tool-use failures cluster into distinct types with different characteristics:

| Failure Type | Severity | Detection | Recovery |
|--------------|----------|-----------|----------|
| Parsing errors (malformed JSON) | Moderate | Easy (syntax check) | Easy (retry with error msg) |
| Fabricated execution | Critical | Hard (requires validation) | Hard (model may persist) |
| Semantic errors (wrong parameters) | High | Medium (requires domain knowledge) | Medium (feedback may help) |
| Provider incompatibility | High | Easy (consistent failure) | Hard (requires code fix) |
| Nested call failures | High | Medium (may look like success) | Medium (requires plan revision) |

**Evidence**:
- LangChain issues: All 6 GitHub issues are tool-related, but different subtypes
- GPT-4o: Only 28% accuracy on nested API calls (NESTFUL)
- Fabrication issue (#947): Critical because undetectable without validation
- Parsing issue (#33504): "Relatively common", needs retry mechanism

**Underlying cause**: Tool-use requires multiple capabilities:
- Structured output generation (JSON)
- Semantic understanding of tool purpose
- Parameter extraction from context
- Result interpretation and integration
- Error handling and retry logic

**Implication for taxonomy**: Tool-use category needs fine-grained subcategories - not all tool failures are equivalent

---

## Architecture-Specific Failure Correlations

### ReAct (Interleaved Reasoning-Acting)

**Strengths**: Tight feedback loop allows quick error detection and correction

**Failure modes observed**:
- Tool-use errors (parsing, fabrication) - see LangChain issues
- Limited lookahead - commits to actions without considering downstream effects
- Susceptible to hallucination when not grounded in tool feedback

**Hypothesis validation**: Partial support for H3 (ReAct → more tool-use errors)

---

### Plan-then-Execute

**Strengths**: Potentially faster and cheaper for tasks with stable, predictable environments

**Failure modes observed**:
- Sub-optimal trajectories when plans are incorrect
- Expensive replanning when plans fail
- Difficulty debugging "hallucinated API calls" that derail workflow
- Poor handling of dynamic/unexpected conditions

**Hypothesis validation**: Supports H3 (plan-then-execute → more plan-repair failures)

---

### Autonomous Loop (AutoGPT-style)

**Strengths**: Full autonomy enables tackling complex, open-ended goals

**Failure modes observed**:
- Infinite loops without progress detection
- Memory loss over extended sessions
- Error propagation through self-feedback
- Over-autonomy (doesn't ask clarifying questions)
- High cost (every step requires LLM call)

**Hypothesis validation**: Supports H3 (autonomous loop → more resource management failures)

---

### Reflection/Self-Correction

**Strengths**: Explicit self-evaluation can catch errors before committing

**Failure modes observed**:
- Degeneration-of-thought (repeating same flawed reasoning)
- Confirmation bias when same model does action and evaluation
- Imprecise evaluators reinforce suboptimal patterns
- Performance sometimes degrades after self-correction attempts

**Hypothesis validation**: Supports H3 (reflection → more self-evaluation failures)

---

### Tree-of-Thought

**Strengths**: Exhaustive search can find solutions other architectures miss

**Failure modes observed**:
- Redundant exploration of low-value paths
- High resource costs without proportional success improvement
- Difficulty with classical planning despite low-width serialization
- Implementation complexity (all components must be finely tuned)

**Hypothesis validation**: Supports H3 (ToT → more resource/efficiency failures)

---

## Hypothesis Assessment

### H1: Failures cluster into 5-7 independent categories (architectural, not model-specific)

**Status**: Likely TRUE, but needs refinement

**Evidence**:
- Existing taxonomies identify 3-15 categories (MAST: 14 in 3 clusters; DEFT: 14 in 3 dimensions; three-phase: 3 phases)
- Our preliminary coding identifies 8 provisional categories from just 10 instances
- Same failure types appear across different LLMs (GPT-4, GPT-3.5, Gemini, open-source)

**Refinement needed**:
- Distinguish failure vs. error vs. limitation
- Some categories may be too broad (e.g., "tool-use" needs subcategories)
- Need boundary criteria to separate overlapping categories

---

### H2: Most failures (>60%) stem from planning and state tracking, not knowledge/tool-use

**Status**: Likely FALSE or needs significant revision

**Evidence AGAINST**:
- Tool-use errors are extremely prevalent in our sample (5/10 instances)
- LangChain issues are dominated by tool-calling problems
- Production failures often cited tool-agent interaction debugging as hardest problem
- GPT-4o: Only 28% accuracy on nested API calls

**Evidence FOR**:
- AutoGPT memory/planning issues are well-documented
- Long-running task failures correlate with planning horizon
- Context degradation affects state tracking significantly

**Revised hypothesis**: Tool-use and planning/state-tracking are roughly equal contributors (~40% each), with smaller contributions from grounding, self-correction, security, and resource management

---

### H3: Failure mode frequency shifts predictably with agent architecture

**Status**: Strongly SUPPORTED, needs quantification

**Evidence**:
- ReAct: Tool-use errors (LangChain issues)
- Plan-then-execute: Plan-repair difficulties
- Autonomous loop: Infinite loops and memory loss (AutoGPT)
- Reflection: Self-evaluation failures (Reflexion degeneration)
- Tree-of-thought: Resource exhaustion and redundant exploration

**Next step**: Need controlled experiments to quantify failure frequency distribution across architectures. Can't just rely on published results (selection bias).

---

## Coverage Gaps in Existing Taxonomies

### MAST (Multi-Agent System Failure Taxonomy, 2025)
- **Scope**: Multi-agent systems only
- **Strength**: Grounded theory from 150+ traces, 3 clear categories
- **Gap**: Doesn't cover single-agent failures, no architecture comparison
- **Our differentiation**: Focus on single-agent with architecture mapping

### DEFT (Deep Research Failure Taxonomy, 2024)
- **Scope**: Deep research agents only (domain-specific)
- **Strength**: Fine-grained 14 failure modes in 3 dimensions
- **Gap**: Not generalizable to other agent types, no architecture analysis
- **Our differentiation**: Cross-domain, cross-architecture

### Three-Phase Taxonomy (2025)
- **Scope**: General agent failures in 3 phases (planning, execution, generation)
- **Strength**: Simple, intuitive structure
- **Gap**: High-level only, no fine-grained categories, no frequency data
- **Our differentiation**: Hierarchical with clear boundary criteria, frequency analysis

### System-Level Reliability Taxonomy (2024)
- **Scope**: 15 failure patterns in production AI systems
- **Strength**: Covers full stack including retrieval, orchestration
- **Gap**: Not agent-specific, mixed abstraction levels
- **Our differentiation**: Agent-specific, consistent abstraction level

### Common gaps across all taxonomies:
1. **No frequency data** - which failures are most common?
2. **No boundary criteria** - how to distinguish overlapping categories?
3. **No architecture comparison** - how does architecture affect failure distribution?
4. **No LLM limitation mapping** - which failures are fundamental vs. fixable?
5. **No controlled reproduction** - are failures reliably reproducible?

---

## Emerging Taxonomy Structure (Very Preliminary)

Based on 10 instances, provisional structure:

```
1. Planning Failures
   1.1. Goal decomposition errors
   1.2. Multi-step coordination
   1.3. Infinite loops / progress detection

2. Tool-Use Failures
   2.1. Structured output generation (parsing)
   2.2. Fabricated/hallucinated execution
   2.3. Semantic errors (wrong parameters)
   2.4. Provider compatibility
   2.5. Multi-step orchestration (nested calls)

3. State Tracking Failures
   3.1. Short-term memory (within session)
   3.2. Long-term memory (across sessions)
   3.3. Context degradation
   3.4. State synchronization

4. Error Recovery Failures
   4.1. Error detection
   4.2. Retry strategies
   4.3. Error propagation/cascades
   4.4. Graceful degradation

5. Grounding Failures
   5.1. Environment observation misinterpretation
   5.2. Domain constraint violation
   5.3. Sensory-symbolic mapping
   5.4. UI/API accessibility

6. Self-Correction Failures
   6.1. Self-evaluation accuracy
   6.2. Degeneration-of-thought
   6.3. Confirmation bias
   6.4. Reflection without external feedback

7. Security Vulnerabilities
   7.1. Prompt injection (direct)
   7.2. Prompt injection (indirect/RAG poisoning)
   7.3. Tool poisoning
   7.4. Credential exposure

8. Resource Management Failures
   8.1. Infinite loops
   8.2. Context overflow
   8.3. Cost exhaustion
   8.4. Redundant computation
```

**Note**: This structure is highly preliminary and based on only 10 instances. Will be revised during open coding of 50+ instances.

---

## Methodological Insights

### What's Working

1. **Grounded theory approach**: Letting categories emerge from data rather than imposing top-down structure
2. **Detailed instance documentation**: Template captures enough context for later analysis
3. **Multi-source collection**: Papers, GitHub issues, production reports give diverse perspectives
4. **Architecture awareness**: Tracking which architecture each failure occurs in enables H3 testing

### Challenges Identified

1. **Boundary ambiguity**: Some failures could fit multiple categories (e.g., tool fabrication = tool-use + self-correction failure?)
2. **Abstraction level**: Hard to maintain consistent level (e.g., "parsing error" vs "tool-use failure" vs "structured output generation")
3. **Causality attribution**: Root causes often unclear - is it LLM limitation, architecture choice, or implementation bug?
4. **Selection bias**: Published papers and GitHub issues over-represent certain failure types

### Next Steps to Address

1. **Inter-rater reliability**: Once we have provisional categories, need second coder to validate boundaries
2. **Controlled experiments**: Reproduce failures in controlled settings to understand causality
3. **Frequency analysis**: Need quantitative data, not just existence proofs
4. **Negative cases**: Document scenarios where agents surprisingly succeed (e.g., WebArena verified fixes improved 16%)

---

## Implications for Controlled Experiments

### Priority Failure Types to Reproduce

Based on prevalence, severity, and architecture-specificity:

1. **Tool call fabrication** (LangChain #947)
   - Test across: ReAct, Plan-then-execute, Custom agent
   - Measure: Frequency, detection difficulty, impact on output quality

2. **Infinite loops** (AutoGPT, CrewAI)
   - Test across: Autonomous loop, ReAct, Plan-then-execute
   - Measure: Loop types (oscillation, retry, replan), detection time, mitigation effectiveness

3. **Context degradation** (long-running tasks)
   - Test across: All architectures
   - Measure: Performance vs. time/turns, information loss patterns

4. **Nested API call failures** (NESTFUL benchmark)
   - Test across: ReAct, Plan-then-execute
   - Measure: Success rate vs. chain length, error propagation

5. **Self-correction failure** (Reflexion degeneration)
   - Test across: Reflection-based, ReAct with self-check
   - Measure: Improvement rate, degeneration frequency, confidence calibration

6. **Prompt injection** (Slack AI, ChatGPT)
   - Test across: RAG-augmented agents
   - Measure: Attack success rate, detection difficulty, mitigation effectiveness

### Experimental Design Considerations

- **Baseline**: Test each failure type on simple task where agent typically succeeds - establishes baseline
- **Stress test**: Gradually increase complexity/difficulty until failure emerges - identifies threshold
- **Architecture comparison**: Same task across 3+ architectures - quantifies architecture effect
- **Mitigation testing**: Test proposed fixes - validates that mitigation actually works

---

## Concurrent Work Risk Update

**Risk level**: MODERATE (unchanged)

**Recent publications** (2024-2025):
- MAST (multi-agent) - not competing, different scope
- DEFT (research agents) - domain-specific, not competing
- Three-phase taxonomy - too high-level, not competing
- Multiple agent papers mention failures but no comprehensive taxonomy

**Monitoring strategy**:
- Weekly arXiv search for "agent failure", "agent taxonomy", "LLM agent evaluation"
- Check ACL/EMNLP/NeurIPS submissions when deadlines approach
- Monitor GitHub repos of major agent frameworks for taxonomy/failure analysis

**Differentiation preserved if**:
- We complete hierarchical taxonomy with boundary criteria
- We provide quantitative frequency analysis across architectures
- We map failures to underlying LLM limitations
- We include controlled reproduction experiments

---

## Next Session Priorities

1. **Continue instance collection** (target: 40 more instances to reach 50 total)
   - More production failures (especially prompt injection, security)
   - More plan-then-execute specific failures
   - More tree-of-thought failures
   - More GitHub issues (AutoGPT, CrewAI repositories)

2. **Deep-read existing taxonomy papers**
   - MAST: Extract detailed failure definitions from 150 traces
   - DEFT: Extract failure modes for research agents
   - Three-phase: Compare category boundaries

3. **Begin preliminary open coding**
   - Code first 10 instances with descriptive tags
   - Look for emergent patterns not captured in provisional structure
   - Test category boundaries (can instances be cleanly assigned?)

4. **Synthesize existing literature review sections**
   - Group related work by theme (benchmarks, architectures, taxonomies)
   - Identify consensus and disagreements
   - Map gaps our work will fill

**Estimated completion**: Next 2-3 sessions should reach 50 instances and complete initial open coding, ready for axial coding phase.
