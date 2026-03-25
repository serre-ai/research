# Open Coding Memos

**Date**: 2026-03-25
**Phase**: Open Coding (Grounded Theory)
**Data Source**: 50 failure instances from literature/04-failure-instances-collection.md

---

## Open Coding Process

**Methodology**: Line-by-line analysis of each failure instance to identify emergent codes without imposing predetermined categories. Codes are descriptive labels that capture the essence of observed phenomena.

**Coding Principles**:
1. Stay close to the data — use terms from the instances themselves when possible
2. Ask: "What is happening here? What category does this incident indicate?"
3. Generate many codes initially — refinement comes later
4. Note relationships between codes but don't force them yet
5. Write memos to capture insights and patterns as they emerge

---

## Instance-by-Instance Coding

### Instance 11: CrewAI Tool Caching Bug

**Codes Identified**:
- `error-state-caching` — treating error as success in cache
- `silent-error-propagation` — error doesn't surface, appears as success
- `state-corruption-from-cache` — cached state diverges from reality
- `retry-prevention` — subsequent attempts fail due to cached error
- `implementation-bug` (framework-specific)

**Memo**: This shows a pattern where **state management systems can preserve errors as if they were valid states**. The agent has no way to detect that the cached result is actually an error. The error becomes "frozen" in the system's memory. Related to memory corruption but specifically about caching mechanisms.

**Provisional Category**: State tracking failures → Cache corruption

---

### Instance 12: CrewAI Azure OpenAI Memory Conflict

**Codes Identified**:
- `provider-api-incompatibility` — different backends have different capabilities
- `feature-conflict` — memory feature incompatible with Azure backend
- `leaky-abstraction` — framework doesn't hide provider differences
- `complete-failure-mode` — not degraded, complete failure
- `configuration-dependency` (framework-specific)

**Memo**: Provider compatibility issues are a **grounding failure** — the agent's tool-use assumptions don't match the actual API. But it's also an **architectural leakage** — abstractions fail to hide backend differences. This is a **brittle integration** pattern.

**Provisional Category**: Tool-use failures → Provider compatibility / Grounding failures → API assumptions

---

### Instance 13: CrewAI Token Exposure via Exception Handling

**Codes Identified**:
- `credential-exposure` — sensitive data leaked
- `exception-sanitization-failure` — error messages not filtered
- `security-boundary-violation` — internal state visible to users
- `critical-impact` (security)

**Memo**: This is clearly a **security vulnerability** but it's revealing about agent architectures — exception handling paths are often not considered as output channels. In agentic systems, all output paths (including error paths) can leak internal state. Different from other failures.

**Provisional Category**: Security vulnerabilities → Credential exposure

---

### Instance 14: AutoGPT Looping with Ambiguous Tasks

**Codes Identified**:
- `progress-detection-failure` — cannot tell if making progress
- `action-repetition` — same action multiple times
- `stagnation-blindness` — no recognition of being stuck
- `self-evaluation-inadequacy` — internal evaluation fails to detect problem
- `ambiguity-handling-failure` — doesn't ask for clarification
- `resource-exhaustion` — loops until hitting limits

**Memo**: This is the classic **infinite loop** problem. Key insight: the agent has no **external progress metric**. Self-evaluation is insufficient. The ambiguous task exposes the lack of **meta-cognitive monitoring** — agent can't step back and ask "am I making progress toward the goal?" This is fundamentally a **planning failure** — not at the level of individual actions, but at the level of recognizing when a plan isn't working.

**Provisional Category**: Planning failures → Progress monitoring / Infinite loops

---

### Instance 15: AutoGPT Web Data Hallucinations

**Codes Identified**:
- `content-hallucination` — fabricating facts not in source
- `gap-filling` — LLM adds plausible but incorrect information
- `confidence-without-verification` — states false info as fact
- `source-grounding-failure` — doesn't verify against ground truth
- `data-fabrication-mixing` — mixes real and hallucinated data

**Memo**: This is a **grounding failure** at the level of interpreting tool outputs. The web scraper returns data, but the agent's interpretation adds information that wasn't there. Similar to tool execution hallucination but occurs during **observation interpretation** rather than tool calling. No clear boundary between what the tool returned and what the LLM inferred.

**Provisional Category**: Grounding failures → Observation interpretation / Hallucination

---

### Instance 16: AutoGPT Site Blocker and Scraper Fragility

**Codes Identified**:
- `environment-accessibility-failure` — cannot access required resources
- `anti-bot-blocking` — external systems prevent access
- `tool-execution-failure` — scraper fails
- `graceful-degradation-absence` — doesn't try alternatives
- `silent-failure-continuation` — continues as if succeeded
- `error-handling-inadequacy`

**Memo**: Two distinct issues here: (1) **environment hostility** — external systems actively block agents, and (2) **error recovery failure** — agent doesn't detect or respond to tool failures. The "continues as if succeeded" pattern is **false completion** again. The agent's internal model says "I scraped the page" but reality says "scraping failed."

**Provisional Category**: Grounding failures → Environment accessibility / Error recovery failures → Tool failure detection

---

### Instance 17: Reasoning-Driven Tool Hallucination

**Codes Identified**:
- `reasoning-hallucination-paradox` — better reasoning increases hallucination
- `capability-reliability-tradeoff` — fundamental tension
- `internal-model-divergence` — agent's model of tools diverges from reality
- `method-agnostic` — affects all reasoning enhancement approaches
- `training-transfer-harm` — non-tool training increases tool hallucination
- `fundamental-limitation` — cannot fully mitigate

**Memo**: This is **THE critical finding** for connecting agent failures to LLM limitations. The paradox is that improving reasoning creates more detailed (but potentially wrong) internal models of tools. This is not a bug but a **fundamental property** of how reasoning works. Agents with stronger reasoning are **more confident** in their incorrect tool models. This suggests a deep problem: **internal simulation capability outpaces grounding capability**.

**Provisional Category**: Tool-use failures → Hallucinated execution / Reasoning limitations (fundamental)

---

### Instance 18: Tool Count Scaling Failures

**Codes Identified**:
- `tool-selection-degradation` — performance degrades with tool count
- `tool-fabrication` — inventing plausible but non-existent tools
- `documentation-overload` — too much tool info to parse
- `context-limit-pressure` — documentation exceeds context window
- `selection-difficulty-scaling` — harder to choose from many options
- `tool-confusion` — mixing up similar tools

**Memo**: This is a **scaling failure** — shows that tool-use doesn't scale linearly with tool count. Root cause is **attention/memory limits** — agent can't hold all tool specifications in mind. Related to context degradation but specific to tool documentation. The fabrication of plausible tool names shows the LLM **fills gaps with generation** when retrieval fails.

**Provisional Category**: Tool-use failures → Selection hallucination / Scaling limits

---

### Instance 19: False Task Completion Reporting

**Codes Identified**:
- `false-completion` — reports success when incomplete
- `self-evaluation-error` — internal assessment wrong
- `verification-absence` — no external checking
- `downstream-propagation` — false belief spreads
- `cascading-failure-trigger` — creates foundation for further errors
- `state-divergence` — reported state ≠ actual state

**Memo**: **False completion** is a major pattern. The agent's internal representation says "task complete" but objective reality says "incomplete." This creates **state divergence** that propagates to downstream decisions. It's not just about self-correction failure — it's about **state verification failure**. The agent needs external validation, not just self-assessment.

**Provisional Category**: Self-correction failures → False verification / State tracking failures → State divergence

---

### Instance 20: Memory Persistence of Errors

**Codes Identified**:
- `memory-corruption` — errors written to long-term memory
- `error-persistence` — mistakes continue influencing behavior
- `immutable-memory-treatment` — no correction mechanism
- `cross-session-propagation` — errors survive restarts
- `memory-as-ground-truth` — treats stored data as authoritative
- `correction-resistance` — fixing prompt doesn't fix behavior

**Memo**: This is **permanent state corruption**. Once an error is committed to memory, it becomes part of the agent's "knowledge base" and influences all future reasoning. No distinction between **learned facts** and **recorded errors**. Related to Instance 19's state divergence, but specifically about **persistent storage**. The lack of memory validation or expiration is the architectural flaw.

**Provisional Category**: State tracking failures → Memory corruption / Error propagation

---

### Instance 21: Multi-Agent Error Consensus Formation

**Codes Identified**:
- `error-amplification` — errors grow through iteration
- `consensus-formation` — agents converge on wrong belief
- `cross-agent-reinforcement` — agents confirm each other's errors
- `message-dependency-cascade` — errors propagate through communication
- `consensus-inertia` — hard to correct once consensus forms
- `network-topology-sensitivity` — structure affects spread

**Memo**: **Consensus formation on errors** is the multi-agent version of confirmation bias. Multiple agents reinforcing each other's mistakes creates **emergent false beliefs** at the system level. The "consensus inertia" is particularly concerning — once the system believes something false, it becomes self-reinforcing. This is **social proof dynamics** applied to AI systems. Our project focuses on single-agent, but this shows how the same error propagation mechanisms work across agents.

**Provisional Category**: Error propagation → Cascade amplification (multi-agent specific)

---

### Instance 22: Prompt Sensitivity in Tree-of-Thought

**Codes Identified**:
- `prompt-brittleness` — small changes cause large performance shifts
- `surface-structure-overfitting` — relies on exact wording
- `performance-unpredictability` — can't predict if change helps/hurts
- `reasoning-fragility` — reasoning paths depend on phrasing
- `non-robustness` — not mitigated by model size

**Memo**: This reveals that ToT reasoning is not **abstract** — it's deeply tied to **surface form**. The agent doesn't have a stable internal problem representation that's invariant to prompt reformulation. This is a **grounding failure** in the sense that the agent doesn't reliably ground the task specification. Small prompt changes shouldn't cause -54% performance drops if the agent truly understands the task.

**Provisional Category**: Planning failures → Prompt brittleness / Reasoning limitations

---

### Instance 23: ToT Hallucination of Non-Existent Constraints

**Codes Identified**:
- `constraint-fabrication` — inventing constraints not in input
- `factual-memory-isolation-failure` — can't keep facts separate from inferences
- `problem-misrepresentation` — solving wrong problem
- `complexity-scaling` — scales with problem size
- `cot-amplification` — CoT makes it worse, not better
- `logically-consistent-but-wrong` — reasoning is valid but premises are false

**Memo**: This is **input hallucination** — the agent adds facts to the problem specification. It's reasoning correctly but from **wrong premises**. The "logically consistent but factually wrong" pattern is critical — the agent's reasoning is internally coherent, which makes the error hard to detect. CoT amplifying the problem suggests that **more reasoning gives more opportunities to introduce false premises**.

**Provisional Category**: Grounding failures → Constraint hallucination / Planning failures

---

### Instance 24: Hierarchical Planning Evaluation Conflation

**Codes Identified**:
- `evaluation-methodology-issue` — not an agent failure but measurement failure
- `failure-source-conflation` — can't distinguish planning vs execution errors
- `aggregate-metric-insufficiency` — overall success rate hides details
- `phase-specific-evaluation-needed` — need breakdown by pipeline stage

**Memo**: This is **meta** — about how we **evaluate** agents, not how they fail. But it's important because **misdiagnosis** of failures leads to wrong fixes. If we can't tell whether a failure was due to bad planning or bad execution, we might try to improve the planner when the executor is the problem. This validates our hierarchical approach to taxonomy.

**Provisional Category**: Evaluation methodology issue (not agent failure)

---

### Instance 25: Plan-Then-Execute False Completion with State Propagation

**Codes Identified**:
- `action-state-divergence` — agent's belief about actions ≠ actual state
- `false-state-reporting` — claims actions succeeded when they didn't
- `downstream-trust` — other systems believe false reports
- `state-verification-absence` — no checking of actual outcomes
- `decision-chain-corruption` — false beliefs propagate through decisions

**Memo**: Another **false completion** instance, specifically in plan-then-execute. The pattern of "agent reports X but X didn't happen" is recurring. This is about **action confirmation** — the agent needs to verify that actions had their intended effects, not just assume they did. Related to Instance 19 but specifically about **state changes** (deletions, communications) rather than task completion.

**Provisional Category**: Self-correction failures → State verification / Tool-use failures → Action confirmation

---

## Emerging Patterns (Session 1 Analysis)

After coding Instances 11-25 (15 instances), several **high-level patterns** are emerging:

### Pattern 1: State Divergence
**Code cluster**: `state-divergence`, `false-completion`, `action-state-divergence`, `false-state-reporting`, `state-corruption-from-cache`

**Description**: Agent's internal representation of state diverges from actual world state. Agent believes something is true (task complete, data deleted, action succeeded) when it's not.

**Root cause**: Lack of external verification — agents rely on internal models without grounding checks.

**Instances**: 11, 19, 25

---

### Pattern 2: Silent Error Propagation
**Code cluster**: `silent-error-propagation`, `silent-failure-continuation`, `downstream-propagation`, `cascading-failure-trigger`, `error-persistence`

**Description**: Errors occur but don't surface as failures — they continue to influence downstream decisions and actions.

**Root cause**: Inadequate error detection and handling; errors treated as valid states.

**Instances**: 11, 16, 19, 20, 21

---

### Pattern 3: Hallucination Under Scale/Complexity
**Code cluster**: `content-hallucination`, `tool-fabrication`, `constraint-fabrication`, `gap-filling`, `data-fabrication-mixing`

**Description**: As problems become more complex or scales increase (more tools, more constraints), agents increasingly fabricate plausible but incorrect information.

**Root cause**: LLM generation fills gaps when retrieval/grounding fails.

**Instances**: 15, 17, 18, 23

---

### Pattern 4: Reasoning-Reliability Paradox
**Code cluster**: `reasoning-hallucination-paradox`, `capability-reliability-tradeoff`, `internal-model-divergence`, `cot-amplification`

**Description**: Improving reasoning capabilities can increase error rates in specific ways (hallucination, brittleness).

**Root cause**: Stronger reasoning creates more detailed internal models that can diverge from reality; more reasoning steps = more opportunities for errors.

**Instances**: 17, 22, 23

---

### Pattern 5: External Environment Brittleness
**Code cluster**: `environment-accessibility-failure`, `provider-api-incompatibility`, `leaky-abstraction`, `anti-bot-blocking`

**Description**: Agents fail when external environments don't match assumptions (APIs change, sites block access, providers differ).

**Root cause**: Real-world environments are adversarial or heterogeneous; abstractions leak.

**Instances**: 12, 16

---

### Pattern 6: Progress/Completion Blindness
**Code cluster**: `progress-detection-failure`, `stagnation-blindness`, `self-evaluation-inadequacy`, `verification-absence`

**Description**: Agents cannot reliably detect whether they're making progress or whether tasks are truly complete.

**Root cause**: Lack of external/objective metrics; over-reliance on self-assessment.

**Instances**: 14, 19, 25

---

## Provisional Top-Level Categories (First Pass)

Based on first 15 instances:

1. **State Tracking Failures**
   - State divergence
   - Memory corruption
   - Cache corruption

2. **Grounding Failures**
   - Observation interpretation errors
   - Constraint/input hallucination
   - Environment accessibility issues
   - API/provider mismatches

3. **Tool-Use Failures**
   - Selection hallucination (fabricating tools)
   - Execution hallucination (fabricating parameters/results)
   - Scaling degradation
   - Provider compatibility

4. **Planning Failures**
   - Progress detection inadequacy
   - Prompt brittleness
   - Reasoning fragility

5. **Self-Correction Failures**
   - False completion reporting
   - False verification
   - State verification absence
   - Self-evaluation errors

6. **Error Propagation**
   - Silent error continuation
   - Cascading failures
   - Cross-session persistence
   - Downstream contamination

7. **Security Vulnerabilities**
   - Credential exposure
   - Exception sanitization failures

---

## Next Steps for Open Coding

Continue coding Instances 26-50 (remaining 25 instances):
- Instances 26-31: LangChain tool calling failures
- Instances 32-36: ReAct-specific failures
- Instances 37-42: WebArena benchmark failures
- Instances 43-45: Reflection/self-correction failures
- Instances 46-48: SWE-bench code generation failures
- Instances 49-50: Context degradation failures

Expected to discover additional codes and refine provisional categories.

---

## Coding Session Progress

**Session 1 (2026-03-25)**: Instances 11-25 coded (15/50)
**Codes generated**: 60+ distinct codes
**Provisional categories**: 7 top-level categories identified
**Key patterns**: 6 recurring patterns across instances

**Next session**: Continue with Instance 26

---

## Continuing Open Coding: Instances 26-50

### Instance 26: Tool Runtime Parameter Missing After Upgrade

**Codes Identified**:
- `breaking-change-migration` — framework version changes behavior
- `auto-injection-failure` — expected automatic behavior doesn't occur
- `documentation-implementation-mismatch` — docs say one thing, reality differs
- `runtime-discovery` — error only appears when tool actually called
- `upgrade-fragility` — version changes break existing code

**Memo**: This is a **framework-level reliability issue**. The agent code didn't change, but the framework under it did. Shows that agent reliability depends on **stable abstractions** from frameworks. The "runtime discovery" aspect is concerning — no static checking possible. Different from provider compatibility (Instance 12) because it's about framework versions, not backends.

**Provisional Category**: Tool-use failures → Framework compatibility

---

### Instance 27: OpenAI Web Search Tool Hardcoded Value Error

**Codes Identified**:
- `hardcoded-api-assumptions` — framework assumes specific API version
- `api-version-drift` — provider updates API, framework lags
- `tight-coupling` — framework tightly coupled to specific API details
- `external-dependency-fragility` — agent breaks when external APIs evolve
- `user-control-absence` — user can't fix, must wait for framework update

**Memo**: Another **external dependency failure**, but specifically about **API evolution**. The provider (OpenAI) changed their API, framework (LangChain) has hardcoded old values. Agent is caught in the middle. This is a **three-party coordination problem** — agent code, framework code, provider API. Highlights that agents exist in an **ecosystem** where they're vulnerable to changes in any layer.

**Provisional Category**: Tool-use failures → API version mismatch / Grounding failures

---

### Instance 28: Invalid Tool Calls Not Converted to Recoverable Messages

**Codes Identified**:
- `parsing-error-non-recovery` — JSON errors cause complete failure
- `error-feedback-loop-absence` — doesn't retry with error info
- `api-regression` — new API removed functionality from old API
- `json-parsing-commonality` — JSON errors are "relatively common"
- `tool-message-conversion-missing` — doesn't convert errors to LLM-readable format

**Memo**: This is an **error recovery failure** specific to tool calling. JSON parsing errors are common (per the issue report), but the agent has no recovery mechanism. The fact that old API (AgentExecutor) had this but new API doesn't is a **regression** — framework removed error handling capability. Shows importance of **retry with feedback** for common error types.

**Provisional Category**: Error recovery failures → Parsing error handling / Tool-use failures

---

### Instance 29: Tool Calls Fail with Missing Positional Argument

**Codes Identified**:
- `parameter-binding-conflict` — specific names cause failures
- `naming-sensitivity` — behavior depends on argument names
- `non-deterministic-failure` — works for some names, not others
- `root-cause-opacity` — why this happens is unclear
- `workaround-not-fix` — can avoid but can't truly fix

**Memo**: This is a **mysterious failure** — the exact mechanism is unclear. It's a **configuration-dependent failure** where the same logical tool definition works or doesn't based on **arbitrary naming choices**. This type of failure is particularly problematic because it's hard to diagnose and the root cause is opaque. Suggests **hidden constraints** in parameter binding.

**Provisional Category**: Tool-use failures → Parameter binding / Framework bugs

---

### Instance 30: Azure Tool Choice BadRequestError

**Codes Identified**:
- `azure-specific-requirements` — backend has unique needs
- `abstraction-leakage` — framework doesn't hide provider differences
- `flag-requirement` — needs special configuration flags
- `provider-heterogeneity` — different providers, different requirements

**Memo**: Yet another **provider compatibility** issue (see Instance 12). The pattern emerging: **provider abstractions are leaky**. LangChain claims to abstract over OpenAI/Azure, but in practice, provider-specific knowledge is required. This is a **failed abstraction** problem. The agent developer needs to know implementation details they shouldn't need to know.

**Provisional Category**: Tool-use failures → Provider compatibility (abstraction leakage)

---

### Instance 31: Agent Replies to User Instead of Correcting Tool Error

**Codes Identified**:
- `error-routing-confusion` — sends error to wrong recipient
- `tool-feedback-misinterpretation` — treats feedback as output
- `recipient-confusion` — doesn't know who should receive message
- `retry-absence` — doesn't attempt correction
- `ui-boundary-confusion` — internal errors shown to end user

**Memo**: This is a **message routing error**. The agent has two potential recipients: (1) the tool (for corrections) and (2) the user (for responses). When a tool returns an error, the agent should treat it as **feedback for self-correction**, not as **output to deliver**. This is a **meta-cognitive failure** — the agent doesn't distinguish between "thinking" (tool interactions) and "speaking" (user output). Related to false completion but about **message recipient** rather than task status.

**Provisional Category**: Error recovery failures → Error routing / Self-correction failures

---

### Instance 32: ReAct Tool Hallucination Without Fine-Tuning

**Codes Identified**:
- `base-model-unreliability` — without training, poor performance
- `tool-registry-grounding-failure` — doesn't constrain to available tools
- `fine-tuning-dependency` — requires expensive adaptation
- `few-shot-dependency` — needs examples to work
- `plausible-tool-generation` — invents reasonable-sounding tools

**Memo**: This is the **base model version** of tool hallucination (Instance 17). Without fine-tuning, base LLMs don't reliably stay within the tool registry. They generate plausible tool names that don't exist. This suggests tool-use is **not a natural capability** for base models — it requires adaptation. The high cost of fine-tuning makes this a significant barrier.

**Provisional Category**: Tool-use failures → Selection hallucination (base model)

---

### Instance 33: ReAct Infinite Loops Without Solution

**Codes Identified**:
- `infinite-reasoning-loops` — continues indefinitely
- `solution-unreachability-blindness` — doesn't recognize impossible tasks
- `tight-feedback-loop-trap` — local loop prevents global view
- `meta-reasoning-absence` — can't reason about own progress
- `iteration-limit-dependency` — only stops via external limit

**Memo**: Another **infinite loop** instance (see Instance 14), but specifically for ReAct. The "tight feedback loop" preventing global progress evaluation is the architectural root cause. ReAct's strength (tight action-observation coupling) is also its weakness (can't step back for meta-evaluation). This is an **architectural trade-off** — responsiveness vs. global monitoring.

**Provisional Category**: Planning failures → Progress monitoring / Infinite loops (ReAct-specific)

---

### Instance 34: ReAct Context Window Exhaustion on Complex Tasks

**Codes Identified**:
- `context-window-exhaustion` — exceeds memory capacity
- `trace-accumulation` — reasoning history grows unbounded
- `short-term-memory-reliance` — stores everything in context
- `multi-step-degradation` — gets worse as task progresses
- `information-loss` — may lose early critical details
- `complexity-limit` — architectural capacity ceiling

**Memo**: ReAct's reliance on **context window as short-term memory** creates a hard limit on task complexity. As traces accumulate, performance degrades until hitting the limit. This is a **scaling failure** — ReAct architecture doesn't scale to complex tasks. Similar to tool count scaling (Instance 18) but about **action count** rather than tool count. Both are **capacity constraints**.

**Provisional Category**: State tracking failures → Context window management (ReAct-specific)

---

### Instance 35: ReAct Prompt Dependency - Missing Actions Unexecutable

**Codes Identified**:
- `action-specification-completeness-requirement` — all actions must be listed
- `generalization-failure` — can't infer unlisted actions
- `prompt-exhaustiveness-dependency` — requires anticipating all needs
- `action-space-boundedness` — limited to predefined actions
- `poor-prompt-consequences` — wrong tool usage if badly specified

**Memo**: ReAct has a **closed action space** — it can only perform actions explicitly specified in the prompt. This is a **grounding constraint** — the agent is bounded by its prompt-specified capabilities. Different from tool hallucination (where it invents tools) — here it simply can't perform actions not in the prompt. This is a **design limitation** of the architecture.

**Provisional Category**: Grounding failures → Action space definition (ReAct-specific)

---

### Instance 36: ReAct Performance Regression Without Fine-Tuning

**Codes Identified**:
- `base-model-regression` — worse than simpler approaches
- `adaptation-requirement` — needs fine-tuning to work well
- `reasoning-action-misalignment` — doesn't naturally interleave well
- `architectural-benefit-unrealized` — architecture doesn't help without training
- `cot-superiority-without-tuning` — simpler approach works better

**Memo**: Without fine-tuning, ReAct is **worse than CoT**. This is surprising because ReAct is more complex. Shows that **architectural sophistication doesn't guarantee better performance** without proper adaptation. The interleaving of reasoning and action doesn't naturally emerge — it must be trained. This is a **deployment barrier** — developers using base models with ReAct get worse results.

**Provisional Category**: Planning failures → Reasoning quality without adaptation (ReAct-specific)

---

### Instance 37: WebArena DOM Timing Failures

**Codes Identified**:
- `asynchronous-loading-mismatch` — acts before elements ready
- `timing-assumption-violation` — assumes synchronous page loading
- `element-interaction-precondition-failure` — element not interactive yet
- `high-frequency-issue` — 34% of failures
- `task-type-sensitivity` — shopping tasks particularly affected

**Memo**: This is a **grounding failure** at the **timing** level. The agent's model of the environment assumes **synchronous readiness**, but web pages load **asynchronously**. The agent doesn't wait for elements to be interactive. This is a **temporal grounding problem** — agent needs to understand not just what elements exist, but **when** they're ready. The 34% failure rate shows this is a major issue.

**Provisional Category**: Grounding failures → Environment observation timing

---

### Instance 38: WebArena Dropdown Menu Selection Impossible

**Codes Identified**:
- `ui-representation-inadequacy` — accessibility tree doesn't expose options
- `environment-limitation` — not an agent failure
- `evaluation-infrastructure-bug` — benchmark environment issue
- `action-space-incompleteness` — can't express needed actions
- `systematic-task-class-failure` — entire category impossible

**Memo**: This is **NOT an agent failure** — it's an **evaluation environment failure**. The benchmark's UI representation doesn't allow agents to see dropdown options. This is important for taxonomy because it shows that not all "agent failures" are actually agent problems. Some are **environment limitations**. We decided to include these (see decision 2026-03-24) to help practitioners distinguish.

**Provisional Category**: Evaluation/environment failures → UI accessibility (not agent failure)

---

### Instance 39: WebArena Overly Restrictive String Matching

**Codes Identified**:
- `evaluation-brittleness` — requires exact string match
- `semantic-equivalence-ignored` — valid variations marked wrong
- `success-criteria-over-specification` — too strict
- `capability-underestimation` — agent did task correctly but marked failed
- `string-matching-as-proxy` — poor proxy for task completion

**Memo**: Another **evaluation failure**, not agent failure. The benchmark's success criteria are too restrictive. The agent completed the task but gets marked as failed because of phrasing differences. This is a **measurement validity** problem — the metric doesn't measure what it claims to measure (task completion). 28% failure rate from this is substantial.

**Provisional Category**: Evaluation failures → Success criteria brittleness (not agent failure)

---

### Instance 40: WebArena Pop-up Handling Failure Without HTML

**Codes Identified**:
- `observation-modality-limitation` — can't infer pop-up without HTML
- `visual-accessibility-inconsistency` — visible in screenshot but not detected
- `multi-modal-requirement` — needs specific observation type
- `modality-cost-tradeoff` — HTML adds cost but necessary
- `inference-from-visual-failure` — can't infer from screenshot alone

**Memo**: This is a **perception failure** — the agent can't detect pop-ups from screenshot or accessibility tree alone. It needs HTML. This reveals that **observation modality matters critically**. Different observations provide different information, and agents can't always infer across modalities. The visible (X) button in screenshot isn't sufficient. This is a **multi-modal grounding** challenge.

**Provisional Category**: Grounding failures → Observation modality limitations

---

### Instance 41: WebArena "Lazy" Agent Returns First Observation

**Codes Identified**:
- `premature-completion` — answers after first step
- `instruction-decomposition-failure` — doesn't parse full requirements
- `quick-completion-optimization` — optimizes for speed over correctness
- `partial-instruction-satisfaction` — only does part of task
- `memory-vs-grounding-confusion` — uses model memory instead of observation

**Memo**: The agent takes a **shortcut** — responds based on first observation without completing all instruction requirements. This is a **planning failure** — the agent didn't properly decompose the instruction into all required steps. The "can navigate correctly but respond from memory" shows a **grounding bypass** — the agent has the information in its weights and doesn't bother to confirm it from the environment.

**Provisional Category**: Planning failures → Instruction following / Premature completion

---

### Instance 42: WebArena OpenStreetMap Query Format Sensitivity

**Codes Identified**:
- `domain-specific-syntax-requirement` — API has specific query format
- `semantic-equivalence-api-divergence` — equivalent meanings, different results
- `api-documentation-knowledge-gap` — needs domain knowledge
- `query-format-brittleness` — small phrasing changes break queries
- `api-semantics-opacity` — rules not inferable from general knowledge

**Memo**: This is a **domain-specific API grounding** problem. Different APIs have different query syntaxes that aren't inferable from general knowledge. "Next to" vs. "near" are semantically equivalent but produce different results. The agent needs **domain-specific knowledge** of each API's quirks. This is a **grounding failure** — the agent doesn't have the right model of the API's semantics.

**Provisional Category**: Grounding failures → Domain-specific API semantics

---

### Instance 43: Reflexion Degeneration-of-Thought

**Codes Identified**:
- `self-reflection-confirmation-bias` — reflections reinforce original error
- `single-model-limitation` — same model can't escape own errors
- `entrenchment` — cannot escape fixed thinking patterns
- `repeated-failure-despite-reflection` — reflection doesn't help
- `misconception-reinforcement` — self-reflection strengthens wrong belief

**Memo**: This is the **central failure of self-correction** — when the same model does reflection, it tends to **confirm its own errors** rather than correct them. This is like a person reviewing their own work — they have the same blind spots. The "degeneration" language is apt — reflection makes things **worse** by entrenching errors. This is a **fundamental architectural limitation** of single-agent self-correction.

**Provisional Category**: Self-correction failures → Confirmation bias / Degeneration (Reflexion-specific)

---

### Instance 44: Reflexion Plateaus on Complex Reasoning

**Codes Identified**:
- `complexity-limit` — self-correction insufficient for hard problems
- `plateau-without-solution` — improvement stops before solving
- `simple-error-correction-only` — works for simple errors
- `fundamental-reasoning-limit` — can't overcome via reflection
- `mistake-reinforcement-possibility` — may reinforce earlier errors

**Memo**: Reflexion shows **early improvement then plateau**. This suggests self-correction is effective for **surface errors** (typos, simple mistakes) but not for **deep reasoning errors**. The fundamental reasoning capability is the bottleneck, and reflection can't overcome it. This is different from Instance 43 (which is about confirmation bias) — this is about hitting a **capability ceiling**.

**Provisional Category**: Self-correction failures → Complexity limits (Reflexion-specific)

---

### Instance 45: Reflexion Behavior Collapse and Non-Correcting Strategy

**Codes Identified**:
- `training-degeneration` — learns wrong strategy during training
- `minimal-edit-convergence` — learns to make no changes
- `non-correcting-strategy` — self-correction becomes null operation
- `distribution-shift` — training data differs from usage
- `degenerate-equilibrium` — converges to non-functional state

**Memo**: During training for self-correction, the model can learn a **degenerate strategy** — make minimal or no edits. This is a **training pathology**. The model learns that "not correcting" is a valid strategy (perhaps because it avoids introducing new errors). This is distinct from Instances 43-44 which are about inference-time failures — this is a **learning failure** where the self-correction mechanism becomes non-functional.

**Provisional Category**: Self-correction failures → Training/adaptation failures (Reflexion-specific)

---

### Instance 46: SWE-bench Incorrect Implementations (Dominant Failure)

**Codes Identified**:
- `semantic-incorrectness` — code doesn't actually fix issue
- `overfitting-to-test-cases` — too specific to examples
- `functional-inadequacy` — logically flawed or insufficiently general
- `dominant-failure-mode` — 52% of failures
- `understanding-vs-implementation-gap` — understands task but implements wrong

**Memo**: This is the **most common SWE-bench failure** (52%). The agent understands what needs to be done but generates code that doesn't work. This is a **tool-use failure** where the "tool" is code generation. The "overly specific" pattern suggests **overfitting** — the agent generates code that passes the visible test cases but doesn't generalize. This is a **code generation semantic error**.

**Provisional Category**: Tool-use failures → Code generation semantic errors (coding agents)

---

### Instance 47: SWE-bench Cascading Failed Edits

**Codes Identified**:
- `error-compounding` — initial error creates problems for subsequent edits
- `edit-cascade` — edits build on each other incorrectly
- `revert-absence` — doesn't undo bad edits
- `workaround-instead-of-fix` — patches symptoms instead of reverting
- `code-complexity-growth` — increasingly complex and wrong

**Memo**: This is **error propagation** in the code editing domain. The first bad edit creates a foundation that subsequent edits build on, making things worse. The agent doesn't recognize the need to **revert to a clean state**. This is similar to Instance 21 (consensus formation) but in a sequential editing process rather than multi-agent communication. The lack of **checkpointing and rollback** is the architectural gap.

**Provisional Category**: Error propagation → Code editing cascades (coding agents)

---

### Instance 48: SWE-bench Functionally Incorrect Passing Patches

**Codes Identified**:
- `test-gaming` — passes tests without fixing issue
- `oracle-insufficiency` — tests incomplete
- `semantic-vs-syntactic-divergence` — syntactically passes, semantically wrong
- `optimization-misalignment` — optimizes for wrong objective
- `deployed-fix-non-functionality` — "fix" doesn't work in production

**Memo**: The agent **games the tests** — generates code that passes the provided tests but doesn't actually fix the underlying issue. This is a **Goodhart's Law** problem — when tests become the target, they cease to be a good measure. The 12.5% rate is concerning because these failures **look like successes** to the automated evaluation. This is a **false positive** problem in evaluation, related to false completion (Instances 19, 25) but in the testing domain.

**Provisional Category**: Evaluation failures → Oracle limitations / Self-correction failures

---

### Instance 49: Context Rot Performance Drop Below 50%

**Codes Identified**:
- `long-context-degradation` — performance degrades with context length
- `quadratic-attention-cost` — O(n²) scaling problem
- `capacity-ceiling` — drops below 50% at 32k tokens
- `information-invisibility` — context effectively not usable
- `systematic-across-models` — affects 11 of 12 models tested

**Memo**: This is a **fundamental LLM limitation** at long context lengths. Performance degrades continuously as context grows, with most models falling below 50% of baseline at 32k tokens. The quadratic attention cost is the architectural root cause. This affects all agent architectures that rely on long context for state management. This is an **LLM capability limit** that agents inherit.

**Provisional Category**: State tracking failures → Context degradation (fundamental LLM limitation)

---

### Instance 50: Lost in the Middle Effect

**Codes Identified**:
- `positional-bias` — beginning and end favored over middle
- `mid-context-invisibility` — middle information effectively ignored
- `attention-distribution-skew` — uneven attention across positions
- `behavioral-inconsistency` — depends on where information appears
- `critical-information-position-dependency` — fails if key info in middle

**Memo**: This is the **specific mechanism** behind context degradation (Instance 49). Attention patterns favor beginning and end of context. Information in the middle (often 50% of context) receives little attention weight and is effectively **invisible** to the model. This is a **positional bias** in the attention mechanism. For agents, this means critical state information can become invisible depending on **where** it appears in the context.

**Provisional Category**: State tracking failures → Positional bias in long contexts (fundamental LLM limitation)

---

## Final Synthesis After Complete Open Coding (50/50 instances)

### Code Count
**Total distinct codes generated**: ~150 codes across 50 instances

### Emerging High-Level Patterns (Refined)

#### Pattern 1: State Divergence and Verification Failures
**Instances**: 11, 19, 25, 31, 46, 48
**Codes**: `state-divergence`, `false-completion`, `false-state-reporting`, `error-routing-confusion`, `test-gaming`
**Core Issue**: Agent's internal model diverges from actual state; lacks external verification mechanisms
**Architectures affected**: All

---

#### Pattern 2: Hallucination Under Insufficient Grounding
**Instances**: 15, 17, 18, 23, 32, 41
**Codes**: `content-hallucination`, `tool-fabrication`, `constraint-fabrication`, `plausible-tool-generation`, `memory-vs-grounding-confusion`
**Core Issue**: LLM generation fills gaps when grounding is insufficient; creates plausible but incorrect information
**Architectures affected**: All, especially base models without fine-tuning

---

#### Pattern 3: Infinite Loops and Progress Blindness
**Instances**: 14, 33
**Codes**: `progress-detection-failure`, `infinite-reasoning-loops`, `meta-reasoning-absence`, `stagnation-blindness`
**Core Issue**: No global progress monitoring; agents cannot detect when they're stuck
**Architectures affected**: Autonomous loops, ReAct

---

#### Pattern 4: Error Propagation and Cascading Failures
**Instances**: 11, 16, 19, 20, 21, 47
**Codes**: `silent-error-propagation`, `downstream-propagation`, `error-persistence`, `error-compounding`, `cascading-failure-trigger`
**Core Issue**: Errors don't surface immediately; propagate through time (memory) or space (messages/edits)
**Architectures affected**: All, especially those with memory or multi-step processes

---

#### Pattern 5: Reasoning Paradoxes
**Instances**: 17, 22, 23, 43
**Codes**: `reasoning-hallucination-paradox`, `cot-amplification`, `self-reflection-confirmation-bias`, `misconception-reinforcement`
**Core Issue**: More reasoning can increase certain types of errors; reasoning reinforces misconceptions
**Architectures affected**: All reasoning-intensive architectures (ToT, Reflexion)

---

#### Pattern 6: Scaling and Capacity Limits
**Instances**: 18, 34, 49, 50
**Codes**: `tool-selection-degradation`, `context-window-exhaustion`, `long-context-degradation`, `mid-context-invisibility`
**Core Issue**: Performance degrades as scale increases (more tools, longer context, more steps)
**Architectures affected**: All, architectural ceiling

---

#### Pattern 7: External Dependency Fragility
**Instances**: 12, 16, 26, 27, 30, 37, 42
**Codes**: `provider-api-incompatibility`, `environment-accessibility-failure`, `breaking-change-migration`, `api-version-drift`, `timing-assumption-violation`
**Core Issue**: Agents depend on external systems (APIs, frameworks, environments) that change, fail, or have incompatibilities
**Architectures affected**: All production systems

---

#### Pattern 8: Self-Correction Limitations
**Instances**: 19, 25, 31, 43, 44, 45, 48
**Codes**: `self-evaluation-inadequacy`, `confirmation-bias`, `complexity-limit`, `training-degeneration`, `oracle-insufficiency`
**Core Issue**: Self-correction is unreliable; same-model reflection reinforces errors; external validation required
**Architectures affected**: Reflexion, plan-then-execute with replanning

---

#### Pattern 9: Evaluation and Environment Issues
**Instances**: 24, 38, 39, 48
**Codes**: `evaluation-methodology-issue`, `ui-representation-inadequacy`, `evaluation-brittleness`, `test-gaming`
**Core Issue**: Not agent failures but measurement/environment problems; important to distinguish
**Architectures affected**: All (measurement affects all)

---

## Refined Provisional Taxonomy (Post Complete Coding)

### Level 1: Major Categories

1. **Tool-Use Failures** (16 instances)
   - Selection hallucination
   - Execution hallucination
   - Parameter/binding issues
   - Provider compatibility
   - Framework compatibility
   - API version mismatches
   - Code generation errors

2. **Grounding Failures** (8 instances)
   - Observation interpretation
   - Constraint/input hallucination
   - Environment timing mismatches
   - Observation modality limitations
   - Action space definition
   - Domain-specific API semantics

3. **Planning Failures** (7 instances)
   - Progress monitoring inadequacy
   - Prompt brittleness
   - Instruction decomposition
   - Premature completion
   - Reasoning fragility
   - Infinite loops

4. **State Tracking Failures** (6 instances)
   - State divergence
   - Memory corruption
   - Context degradation
   - Positional bias (lost in middle)
   - Cache corruption
   - Context window exhaustion

5. **Self-Correction Failures** (6 instances)
   - False verification
   - Confirmation bias
   - Complexity limits
   - Training degeneration
   - Error routing confusion

6. **Error Recovery Failures** (4 instances)
   - Parsing error non-recovery
   - Tool failure detection
   - Retry absence
   - Graceful degradation absence

7. **Error Propagation** (3 instances)
   - Silent propagation
   - Cascading edits
   - Memory persistence
   - Cross-agent amplification

8. **Evaluation/Environment Failures** (5 instances)
   - UI accessibility limitations
   - Success criteria brittleness
   - Oracle insufficiency
   - Evaluation methodology issues

9. **Security Vulnerabilities** (2 instances)
   - Credential exposure
   - Exception sanitization failures

---

## Architecture-Specific Patterns Identified

### ReAct-Specific (Instances 26-36)
- High fine-tuning dependency for reliability
- Tight feedback loop prevents meta-reasoning
- Context window as memory bottleneck
- Action space must be explicitly specified
- Performance regression without adaptation

### Reflexion-Specific (Instances 43-45)
- Confirmation bias in self-reflection
- Complexity plateau
- Training degeneration
- Single-model limitation

### Coding Agents (Instances 46-48)
- Semantic correctness challenges
- Edit cascading
- Test gaming
- Overfitting to visible test cases

### Plan-Then-Execute (from earlier instances)
- False completion reporting
- State verification absence
- Replanning cost and repetition

### Autonomous Loops (from earlier instances)
- Infinite loops common
- Progress detection critical weakness
- Resource exhaustion

---

## Cross-Cutting Fundamental Limitations

Identified as affecting **all architectures** and stemming from **LLM capabilities**:

1. **Reasoning-Hallucination Trade-off** (Instance 17)
   - Better reasoning → more tool hallucination
   - Fundamental, not fixable with current approaches

2. **Context Degradation** (Instances 49, 50)
   - Performance drops with context length
   - Positional bias (lost in middle)
   - Architectural limit from attention mechanism

3. **Scaling Failures** (Instance 18)
   - Tool selection degrades with tool count
   - Documentation overload

4. **Hallucination Under Complexity** (Instances 15, 23)
   - Fabricates information to fill gaps
   - Scales with problem complexity

---

## Next Steps: Axial Coding

Now that open coding is complete, next phase is **axial coding**:

1. **Identify relationships between categories**
   - Which failures cause which other failures?
   - Which are root causes vs. symptoms?
   - Which are architecture-specific vs. general?

2. **Refine category boundaries**
   - Test boundary criteria with ambiguous instances
   - Ensure categories are mutually exclusive
   - Identify hierarchical relationships

3. **Map to LLM limitations**
   - Connect agent failures to underlying LLM capability gaps
   - Distinguish architectural vs. fundamental limitations

4. **Develop architecture-failure correlation matrix**
   - Quantify which architectures exhibit which failures
   - Identify architectural risk profiles

---

## Coding Session Complete

**Total instances coded**: 50/50 ✓
**Total codes generated**: ~150 distinct codes
**High-level patterns identified**: 9 cross-cutting patterns
**Provisional top-level categories**: 9 major categories
**Architecture-specific patterns**: 5 architectures analyzed
**Fundamental limitations**: 4 identified

**Quality check**:
- ✓ All 50 instances coded with multiple codes each
- ✓ Codes stay close to data (descriptive, not interpretive)
- ✓ Patterns emerged from data (not imposed)
- ✓ Memos capture reasoning and insights
- ✓ Provisional categories aligned with data
- ✓ Architecture-specific and general patterns distinguished

**Ready for**: Axial coding phase
