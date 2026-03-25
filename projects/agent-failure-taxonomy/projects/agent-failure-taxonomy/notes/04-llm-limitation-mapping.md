# Mapping Agent Failures to Underlying LLM Limitations

**Date**: 2026-03-25
**Purpose**: Connect agent-level failure taxonomy to fundamental LLM capability gaps
**Key Differentiation**: Bridges agent failures to reasoning-gaps project; provides theoretical grounding

---

## Why This Mapping Matters

Most agent failure taxonomies categorize **symptoms** (what goes wrong) but don't connect to **underlying causes** (why it goes wrong at the LLM level). This mapping:

1. **Distinguishes correctable from fundamental**: Some failures can be fixed with better prompts/architecture; others are LLM capability limits requiring new research
2. **Guides mitigation strategies**: Understanding root cause determines whether to fix the agent, the framework, or wait for better LLMs
3. **Connects to reasoning research**: Shows how abstract reasoning limitations manifest in agentic settings
4. **Predicts future failures**: As agents become more complex, understanding LLM limits predicts new failure modes

---

## LLM Capability Dimensions

Based on literature review and failure analysis, LLMs have limitations across these dimensions:

### C1: Factual Grounding
- **Capability**: Reliably separate memorized knowledge from generated inference
- **Limitation**: Cannot isolate facts from plausible generation; fills gaps with fabrication
- **Measurement**: Hallucination rate on grounded tasks

### C2: Long-Range Coherence
- **Capability**: Maintain consistent representation across long contexts
- **Limitation**: Attention degrades quadratically (O(n²)); positional bias; "lost in middle"
- **Measurement**: Performance degradation at 32k+ tokens

### C3: Meta-Cognitive Monitoring
- **Capability**: Reason about own reasoning process and progress
- **Limitation**: Cannot reliably detect stagnation, loops, or own errors
- **Measurement**: Self-evaluation accuracy; loop detection rates

### C4: Constraint Satisfaction
- **Capability**: Reliably maintain and apply complex constraints
- **Limitation**: Invents spurious constraints; violates stated constraints as complexity grows
- **Measurement**: Constraint violation rate on CSP tasks

### C5: State Tracking
- **Capability**: Maintain accurate model of dynamic external state
- **Limitation**: Internal model diverges from reality; no state reconciliation mechanism
- **Measurement**: State divergence in multi-step tasks

### C6: Tool Grounding
- **Capability**: Accurate internal model of tool semantics and constraints
- **Limitation**: Tool representations diverge from actual behavior; scaling with tool count
- **Measurement**: Tool hallucination rate; selection accuracy

### C7: Self-Correction Capability
- **Capability**: Identify and correct own errors
- **Limitation**: Same-model reflection reinforces errors (confirmation bias); complexity limits
- **Measurement**: Correction success rate; plateau points

### C8: Reasoning-Reliability Trade-off
- **Capability**: Enhanced reasoning without increased errors
- **Limitation**: Stronger reasoning proportionally increases certain error types (hallucination)
- **Measurement**: Performance-hallucination correlation

---

## Mapping: Agent Failures → LLM Limitations

### Tool-Use Failures

#### 1.1 Selection Failures (Tool Fabrication)
**Primary LLM Limitation**: **C6: Tool Grounding** + **C1: Factual Grounding**

**Mechanism**:
- Agent needs to select from available tools
- Large tool sets exceed working memory capacity
- When retrieval fails, LLM generation fills gap with plausible tool name
- No mechanism to verify tool exists before attempting call

**Evidence**:
- Instance 18: Tool hallucination scales with tool count (C6 scaling limitation)
- Instance 32: Base models fabricate plausible tools without fine-tuning (C6 + C1)

**Mitigation path**:
- Architectural: Tool retrieval, organization, filtering
- LLM improvement: Better factual grounding, tool-use fine-tuning
- External: Tool registry validation before execution

**Fixable?**: Partially. Architectural changes help but C6 scaling is fundamental at current LLM capabilities.

---

#### 1.2 Execution Failures (Hallucinated Execution)
**Primary LLM Limitation**: **C8: Reasoning-Reliability Trade-off** + **C6: Tool Grounding**

**Mechanism**:
- Enhanced reasoning creates detailed internal tool models
- Internal models diverge from actual tool behavior
- Agent "simulates" tool execution internally instead of grounding to actual behavior
- Stronger reasoning → more divergence → more hallucination

**Evidence**:
- Instance 17: Reasoning enhancement proportionally increases tool hallucination (C8 paradox)
- Training on non-tool tasks (math) increases subsequent tool hallucination

**Mitigation path**:
- Preference optimization (trades capability for reliability — not a real solution)
- External: Verification of tool outputs
- LLM improvement: Separate reasoning from tool simulation

**Fixable?**: No with current approaches. This is a **fundamental trade-off** requiring new research direction.

---

#### 1.3 Integration Failures (Provider/Framework Issues)
**Primary LLM Limitation**: None (these are ecosystem failures, not LLM failures)

**Mechanism**:
- Agent depends on external systems (APIs, frameworks)
- External systems change without agent knowledge
- No LLM capability issue

**Mitigation path**: Better versioning, compatibility testing, graceful degradation

**Fixable?**: Yes, through better software engineering practices.

---

#### 1.4 Code Generation Errors (Semantic Incorrectness)
**Primary LLM Limitation**: **C4: Constraint Satisfaction** + **C3: Meta-Cognitive Monitoring**

**Mechanism**:
- Agent must generate code satisfying complex specifications
- LLM struggles to maintain all constraints simultaneously (C4)
- Cannot reliably verify own code correctness (C3)
- May overfit to visible test cases instead of generalizing

**Evidence**:
- Instance 46: 52% of SWE-bench failures are semantically incorrect implementations (C4)
- Instance 48: 12.5% pass tests but functionally wrong (C3 - can't self-verify)

**Mitigation path**:
- Architectural: Test-driven development, verification tools
- LLM improvement: Better constraint tracking, verification capabilities

**Fixable?**: Partially. Better prompting helps simple cases; complex specs exceed current capabilities.

---

### Grounding Failures

#### 2.1 Input Grounding (Constraint Hallucination)
**Primary LLM Limitation**: **C1: Factual Grounding** + **C4: Constraint Satisfaction**

**Mechanism**:
- Agent must extract constraints/requirements from task description
- Complex tasks exceed working memory (C4)
- LLM adds plausible but non-existent constraints (C1)
- Hallucination rate scales with problem complexity

**Evidence**:
- Instance 23: Hallucinating graph edges not in input (C1 + C4)
- Linear scaling with complexity

**Mitigation path**:
- External: Constraint extraction validation
- Prompting: Explicit constraint listing, verification
- LLM improvement: Better factual memory isolation

**Fixable?**: Partially through external validation; fundamental limit for very complex specs.

---

#### 2.2 Observation Grounding (Tool Output Misinterpretation)
**Primary LLM Limitation**: **C1: Factual Grounding** + **C6: Tool Grounding**

**Mechanism**:
- Tool returns observation (scraped data, API response, etc.)
- LLM interprets observation, adding inferences
- Cannot reliably separate what tool returned vs. what LLM inferred (C1)
- Creates coherent narrative mixing fact and fabrication

**Evidence**:
- Instance 15: Web scraping hallucinations — mixes real and fabricated data (C1)
- Stated with confidence, no uncertainty markers

**Mitigation path**:
- Architectural: Separate observation storage from interpretation
- Prompting: Explicit "what did the tool return exactly?" verification
- LLM improvement: Factual grounding, uncertainty quantification

**Fixable?**: Partially. Can reduce with careful prompting but cannot eliminate.

---

#### 2.3 API Grounding (Domain-Specific Syntax)
**Primary LLM Limitation**: **C6: Tool Grounding** (knowledge limitation, not capability)

**Mechanism**:
- Different APIs have different syntax/semantics
- LLM may not have seen specific API during training
- Relies on general knowledge or inference
- Cannot always infer domain-specific quirks

**Evidence**:
- Instance 42: OpenStreetMap "next to" vs "near" — semantically equivalent but API treats differently

**Mitigation path**:
- Documentation: Provide API-specific examples
- Fine-tuning: Train on domain-specific APIs
- External: Query reformulation, API documentation retrieval

**Fixable?**: Yes through better documentation and training. Not a fundamental limitation.

---

### Planning Failures

#### 3.1 Progress Monitoring (Infinite Loops)
**Primary LLM Limitation**: **C3: Meta-Cognitive Monitoring**

**Mechanism**:
- Agent takes actions in loop (observation → reasoning → action)
- Cannot step back to evaluate whether making global progress
- No internal "am I stuck?" detection mechanism
- Self-evaluation focuses on local action quality, not global trajectory

**Evidence**:
- Instance 14: AutoGPT loops on ambiguous tasks (C3)
- Instance 33: ReAct loops without solution (C3)
- Tight feedback loop prevents meta-reasoning

**Mitigation path**:
- Architectural: External progress metrics, iteration limits, explicit meta-reasoning steps
- Prompting: "Are you making progress?" check after N steps
- LLM improvement: Meta-cognitive capabilities

**Fixable?**: Architecturally yes (add external monitoring). LLM-level no (C3 is fundamental limitation).

---

#### 3.2 Instruction Processing (Decomposition Failures)
**Primary LLM Limitation**: **C4: Constraint Satisfaction** + **C2: Long-Range Coherence**

**Mechanism**:
- Complex instructions have multiple requirements
- Agent must decompose into sub-goals and track completion
- May satisfy partial requirements and stop (C4 - constraint tracking)
- Forgets earlier requirements if instruction is long (C2)

**Evidence**:
- Instance 41: "Lazy" agent returns after first observation (C4 - partial satisfaction)
- Doesn't complete all instruction requirements

**Mitigation path**:
- Architectural: Explicit decomposition step, completion checklist
- Prompting: Number requirements, check each explicitly
- LLM improvement: Better constraint tracking across contexts

**Fixable?**: Mostly yes through decomposition prompting. Very complex instructions may exceed capacity.

---

#### 3.3 Reasoning Quality (Prompt Brittleness)
**Primary LLM Limitation**: **Surface Form Dependence** (specific limitation of current LLMs)

**Mechanism**:
- LLM reasoning heavily dependent on prompt surface structure
- Small rephrasings cause large performance changes (-54% in ToT)
- Cannot extract stable abstract task representation
- Overfits to training data phrasing

**Evidence**:
- Instance 22: ToT accuracy drops with prompt perturbations
- Not mitigated by model size

**Mitigation path**:
- Prompting: Ensemble over multiple prompt variants
- Training: Instruction tuning for robustness
- LLM improvement: Abstract task representation

**Fixable?**: Partially through ensembling. Fundamental issue with current transformer architectures.

---

### State Tracking Failures

#### 4.1 State Divergence (False State Reporting)
**Primary LLM Limitation**: **C5: State Tracking** + **C3: Meta-Cognitive Monitoring**

**Mechanism**:
- Agent maintains internal model of world state
- Takes actions that change state
- Internal model doesn't update to match reality (C5)
- Cannot verify own state model against ground truth (C3)
- Reports state based on internal model, not reality

**Evidence**:
- Instance 25: Reports "data deleted" when data still exists (C5)
- Instance 19: Reports task complete when incomplete (C5 + C3)

**Mitigation path**:
- Architectural: External state verification, action confirmation
- Design principle: Never trust agent's state reports; always verify
- LLM improvement: State reconciliation mechanisms

**Fixable?**: Architecturally yes (external verification required). LLM-level unlikely soon.

---

#### 4.2 Memory Issues (Memory Corruption)
**Primary LLM Limitation**: **C5: State Tracking** + **No Error Correction in Memory**

**Mechanism**:
- Errors written to long-term memory (vector store, etc.)
- Memory treated as immutable ground truth
- No validation or correction mechanism
- Corrupted memory contaminates future reasoning

**Evidence**:
- Instance 20: Memory persistence of errors across sessions

**Mitigation path**:
- Architectural: Memory validation, expiration, versioning, correction protocols
- Design: Distinguish confidence levels in stored information
- LLM improvement: Uncertainty-aware memory

**Fixable?**: Yes through architectural changes (memory systems with validation).

---

#### 4.3 Context Management (Context Degradation)
**Primary LLM Limitation**: **C2: Long-Range Coherence** (fundamental)

**Mechanism**:
- Attention cost scales O(n²) with context length
- Performance degrades continuously with context growth
- Positional bias: beginning/end >> middle
- Information in middle 50% effectively invisible

**Evidence**:
- Instance 49: Performance < 50% at 32k tokens (C2)
- Instance 50: Lost in middle effect (C2 positional bias)
- Systematic across 11 of 12 models tested

**Mitigation path**:
- Architectural: Compression, summarization, retrieval, external memory
- Cannot fix by prompting — fundamental attention mechanism limit
- LLM improvement: New attention mechanisms (linear attention, etc.)

**Fixable?**: No with current architectures. Architectural workarounds (external memory) trade latency for capacity.

---

### Self-Correction Failures

#### 5.1 Verification Failures (False Completion)
**Primary LLM Limitation**: **C3: Meta-Cognitive Monitoring** + **C7: Self-Correction Capability**

**Mechanism**:
- Agent evaluates own work
- Self-evaluation is unreliable (C3)
- Same model that made error tries to detect it (C7)
- Confirmation bias: agent's reasoning style consistent across production and evaluation

**Evidence**:
- Instance 19: Reports completion when incomplete (C3 + C7)
- Instance 48: Code passes tests but functionally wrong (C7)

**Mitigation path**:
- Architectural: External verification required (different model, tools, humans)
- Cannot rely on same-model self-evaluation for high-stakes decisions
- LLM improvement: Better calibration, uncertainty quantification

**Fixable?**: No through self-evaluation alone. External verification necessary.

---

#### 5.2 Reflection Failures (Degeneration-of-Thought)
**Primary LLM Limitation**: **C7: Self-Correction Capability** (fundamental for same-model reflection)

**Mechanism**:
- Reflexion uses same model for Actor, Evaluator, Reflector
- Reflection reinforces original reasoning patterns (confirmation bias)
- Cannot escape entrenched errors — no external perspective
- Simple errors correctable; complex errors entrench

**Evidence**:
- Instance 43: Reflexion degeneration — repeats same error despite reflection (C7)
- Instance 44: Plateaus on complex tasks (C7 complexity limit)

**Mitigation path**:
- Architectural: Multi-model reflection (different models as critics)
- Diverse personas for evaluation (MAR framework)
- External: Verification tools, human feedback

**Fixable?**: No with single-model reflection. Requires external perspective.

---

#### 5.3 Error Routing (Wrong Recipient)
**Primary LLM Limitation**: **C3: Meta-Cognitive Monitoring** (boundary confusion)

**Mechanism**:
- Agent must distinguish between:
  - Internal messages (to tools, for self-correction)
  - External messages (to user, final output)
- Boundary confusion: sends tool errors to user
- Cannot meta-reason about message recipient

**Evidence**:
- Instance 31: Sends tool error to user instead of correcting (C3)

**Mitigation path**:
- Architectural: Explicit routing logic, message type tagging
- Prompting: Clear instruction about internal vs external messages

**Fixable?**: Yes through clear architecture and prompting.

---

### Error Recovery Failures

**Primary LLM Limitation**: None (these are architectural/framework issues, not LLM limitations)

**Mechanism**:
- Errors occur (parsing errors, tool failures, etc.)
- Agent architecture doesn't provide recovery mechanisms
- Not LLM capability limit — architectural design gap

**Mitigation path**: Better error handling logic, retry mechanisms, graceful degradation

**Fixable?**: Yes through better architecture.

---

### Error Propagation

**Primary LLM Limitation**: Indirect — caused by other limitations (C5 state tracking, C3 monitoring, C7 self-correction)

**Mechanism**:
- Primary failure occurs (state divergence, hallucination, etc.)
- Agent doesn't detect error (C3)
- Error incorporated into memory/state (C5)
- Downstream decisions based on error
- Cannot correct without external intervention (C7)

**Evidence**:
- Instance 20: Memory propagation (C5 + C7)
- Instance 47: Edit cascades (C5 + C3)
- Instance 21: Multi-agent consensus (C3 + C7)

**Mitigation path**:
- Architectural: Error isolation, checkpointing, external validation
- Design: Assume errors will occur; design for containment

**Fixable?**: Yes architecturally through isolation and validation. Root cause (primary failures) may be fundamental.

---

### Evaluation/Environment Failures

**Primary LLM Limitation**: None (not agent failures)

---

### Security Vulnerabilities

**Primary LLM Limitation**: None (architectural security issues, not LLM capability)

---

## Summary: Fundamental vs. Correctable

### Fundamental LLM Limitations (Unlikely to Fix Soon)

1. **Reasoning-Reliability Trade-off** (C8)
   - Better reasoning → more hallucination
   - **Affects**: Tool execution hallucination
   - **Implication**: Must accept trade-off or find new training methods

2. **Long-Range Coherence** (C2)
   - O(n²) attention cost, positional bias
   - **Affects**: Context degradation, lost in middle
   - **Implication**: Need architectural workarounds (external memory, compression)

3. **Meta-Cognitive Monitoring** (C3)
   - Cannot reliably detect own errors, stagnation, loops
   - **Affects**: Progress monitoring, self-verification, error routing
   - **Implication**: External monitoring required

4. **Self-Correction Capability** (C7)
   - Same-model reflection reinforces errors
   - **Affects**: Reflexion, verification, false completion
   - **Implication**: External verification required (different model/tool/human)

5. **Factual Grounding** (C1)
   - Cannot isolate facts from generation
   - **Affects**: All hallucination types
   - **Implication**: External validation required for critical information

---

### Partially Correctable (Architectural Mitigation Possible)

1. **Tool Grounding** (C6)
   - Tool representations diverge from reality
   - **Mitigation**: Better documentation, retrieval, validation
   - **Limit**: Scaling with tool count is fundamental

2. **Constraint Satisfaction** (C4)
   - Struggles with complex constraint sets
   - **Mitigation**: Decomposition, explicit tracking
   - **Limit**: Very complex specs exceed capacity

3. **State Tracking** (C5)
   - Internal state diverges from reality
   - **Mitigation**: External state verification, reconciliation
   - **Limit**: Agent won't spontaneously request verification

---

### Fully Correctable (Architectural/Engineering Issues)

1. **Error Recovery Failures**
   - Better error handling logic

2. **Integration Failures**
   - Better versioning, compatibility testing

3. **Security Vulnerabilities**
   - Output sanitization, security-aware design

4. **Memory Corruption**
   - Memory validation, versioning, correction protocols

---

## Implications for Agent Design

### Design Principle 1: Never Trust Self-Evaluation
**Reason**: C3, C7 are fundamental limitations
**Implication**: Critical decisions require external verification (different model, tool, human)

### Design Principle 2: Assume State Divergence Will Occur
**Reason**: C5 is inherent to internal modeling
**Implication**: Design for state reconciliation, not state correctness

### Design Principle 3: External Memory for Complex/Long Tasks
**Reason**: C2 context degradation is fundamental
**Implication**: Don't rely on context window beyond 8-16k tokens

### Design Principle 4: Validate All Generated Information
**Reason**: C1 factual grounding fails under ambiguity
**Implication**: Critical facts need external validation (retrieval, computation, human)

### Design Principle 5: Isolate Errors
**Reason**: C3, C7 prevent reliable error detection/correction
**Implication**: Checkpointing, rollback, modular isolation

### Design Principle 6: Choose Architectures Based on Failure Profiles
**Reason**: Different architectures exhibit different failure patterns
**Implication**: Match architecture to task criticality and failure tolerance

---

## Connection to Reasoning-Gaps Project

This mapping bridges our agent failure taxonomy to the reasoning-gaps project by showing:

1. **How abstract reasoning limitations manifest in agents**: C3 meta-cognitive monitoring → infinite loops; C4 constraint satisfaction → hallucinated constraints

2. **Novel failure modes in agentic settings**: C8 reasoning-reliability trade-off discovered in agent context; wouldn't appear in standard reasoning benchmarks

3. **Architectural amplification of limitations**: Agent architectures can amplify LLM limitations (ReAct tight loop prevents C3 meta-reasoning) or mitigate them (external memory works around C2)

4. **Research priorities**: Identifies which LLM capabilities most critically impact agent reliability (C3, C7, C1 most pervasive)

---

## Next Steps

1. **Quantify limitation severity**: Which LLM limitations cause most frequent/severe agent failures?
2. **Test mitigation strategies**: For each limitation, test architectural mitigations empirically
3. **Develop capability benchmarks**: Create tests specifically for C1-C8 in agentic contexts
4. **Compare models**: Do different LLMs have different limitation profiles? (GPT-4 vs Claude vs open models)

---

## Mapping Complete

**Dimensions defined**: 8 LLM capability dimensions (C1-C8)
**Failures mapped**: All 9 major categories mapped to underlying limitations
**Fundamental limitations identified**: 5 unlikely to fix soon
**Design principles derived**: 6 principles for robust agent design
**Research priorities**: Meta-cognitive monitoring (C3) and self-correction (C7) most critical gaps

**Key contribution**: This mapping distinguishes **what can be fixed now** (architecture) vs. **what requires LLM research** (capabilities) vs. **what requires accepting trade-offs** (fundamental limits)