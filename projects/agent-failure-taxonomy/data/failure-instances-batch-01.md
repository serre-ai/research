# Failure Instances Batch 01

Collection date: 2026-03-24
Source: Literature survey - seed papers and production reports

---

## FI-001: AutoGPT Infinite Loop Without Progress

### Source Information
- **Source type**: Blog Post / Technical Analysis
- **Source URL**: https://www.marktechpost.com/2023/07/11/breaking-down-autogpt/
- **Date reported**: 2023-07
- **Agent framework**: AutoGPT
- **Base LLM**: GPT-4

### Task Context
- **Task type**: General task automation
- **Task complexity**: Moderate
- **Task horizon**: Long-running (5-20 turns)
- **Task description**: AutoGPT attempting to accomplish user-specified goals through autonomous task decomposition and execution

### Failure Description
#### Observable Behavior
Agent repeatedly cycles through the same subtasks without making progress toward the goal. Loop continues until manual intervention (hitting token limit or user stop).

#### Expected Behavior
Agent should recognize when a strategy is not working, attempt alternative approaches, or signal that the task cannot be completed.

#### Failure Impact
- **Impact severity**: High
- **Recovery**: Manual intervention (user must stop and restart with different prompt)
- **Consequences**: Cost overrun (token consumption), user frustration, wasted time

### Root Cause Hypothesis
#### Immediate Cause
Combination of limited function set and GPT-4's constrained reasoning ability creates "looping quagmire"

#### Underlying Cause
- Finite context window limits ability to remember what has already been attempted
- Lack of meta-reasoning about progress toward goal
- No detection mechanism for repeated actions

#### LLM-Level Limitation
- Long-range dependency tracking (can't maintain state over many turns)
- Lack of explicit self-monitoring/meta-cognition

### Failure Category (preliminary)
- **Provisional category**: Resource management / State tracking
- **Sub-category**: Infinite loop without progress detection

### Architecture Factors
- **Agent architecture**: Autonomous loop with self-feedback
- **Architecture-specific factors**: Relies on own feedback without external validation; no loop detection in original implementation

### Reproducibility
- **Reproducible**: Yes (was common in early AutoGPT versions)
- **Reproduction notes**: More common with complex, ambiguous goals; less common after 2024 updates added loop detection

### Mitigation Strategies
#### Attempted
2024 updates added loop detection and prevention mechanisms - appears to have reduced frequency

#### Potential
- Hard turn limits
- Explicit state tracking of attempted strategies
- Similarity detection for consecutive actions
- External progress evaluation

#### Limitations
Detecting "true loops" vs. "appropriate repetition" is challenging - some tasks legitimately require multiple similar attempts

### Related Failures
FI-007 (CrewAI loop), FI-015 (Toqan infinite loop)

### Notes
This was one of the most widely reported AutoGPT failures in 2023. The problem was severe enough that AutoGPT development prioritized loop detection in 2024 updates.

---

## FI-002: AutoGPT Memory Loss and Repeated Subtasks

### Source Information
- **Source type**: Technical Analysis
- **Source URL**: https://www.marktechpost.com/2023/07/11/breaking-down-autogpt/
- **Date reported**: 2023
- **Agent framework**: AutoGPT
- **Base LLM**: GPT-4

### Task Context
- **Task type**: General task automation
- **Task complexity**: Complex
- **Task horizon**: Extended (>20 turns)
- **Task description**: Multi-step tasks requiring coordination across many subtasks

### Failure Description
#### Observable Behavior
Agent unable to remember what it has already done; repeatedly attempts the same subtask multiple times as if it's the first attempt

#### Expected Behavior
Agent maintains working memory of completed subtasks and their outcomes; does not duplicate work

#### Failure Impact
- **Impact severity**: High
- **Recovery**: Often requires restart with better-structured goal decomposition
- **Consequences**: Inefficiency, cost overrun, unpredictable behavior

### Root Cause Hypothesis
#### Immediate Cause
Finite context window overflow - older conversation turns fall out of context

#### Underlying Cause
Lack of long-term memory architecture - relies entirely on context window for state tracking

#### LLM-Level Limitation
Fixed context window (even with 32K+ tokens, still finite); no inherent memory consolidation mechanism

### Failure Category (preliminary)
- **Provisional category**: State tracking
- **Sub-category**: Long-term memory failure / Context degradation

### Architecture Factors
- **Agent architecture**: Autonomous loop
- **Architecture-specific factors**: No persistent memory beyond LLM context window; no hierarchical memory (short/medium/long term)

### Reproducibility
- **Reproducible**: Yes (especially on tasks requiring >20 turns)
- **Reproduction notes**: Reproducibility increases with task complexity and number of subtasks

### Mitigation Strategies
#### Attempted
Some AutoGPT variants added external memory stores

#### Potential
- Hierarchical memory architecture (short/medium/long term)
- Explicit task completion tracking in structured format
- Periodic state summarization
- External database for completed work

#### Limitations
Adding memory increases architectural complexity; requires decisions about what to remember vs. forget

### Related Failures
FI-012 (context degradation), FI-018 (Parcha context noise)

---

## FI-003: Voyager Hallucinated Non-Existent Items

### Source Information
- **Source type**: Paper / Technical Report
- **Source URL**: https://voyager.minedojo.org/
- **Date reported**: 2023
- **Agent framework**: Voyager
- **Base LLM**: GPT-4

### Task Context
- **Task type**: Embodied/robotics (Minecraft)
- **Task complexity**: Moderate
- **Task horizon**: Multi-turn (<5 per subtask)
- **Task description**: Automatic curriculum suggests goals; agent generates code to achieve them

### Failure Description
#### Observable Behavior
Agent suggests or attempts to create items that don't exist in Minecraft: "copper sword", "copper chest plate", using cobblestone as fuel (not valid in-game)

#### Expected Behavior
Agent only suggests goals achievable with game mechanics; verifies item/recipe validity before attempting

#### Failure Impact
- **Impact severity**: Moderate
- **Recovery**: Automatic (self-verification module catches some; automatic curriculum can retry later)
- **Consequences**: Wasted API calls, incorrect code generation, need for retry

### Root Cause Hypothesis
#### Immediate Cause
GPT-4 generates syntactically valid Minecraft code for semantically invalid game operations

#### Underlying Cause
Hallucination - model confabulates plausible-sounding game mechanics that don't actually exist

#### LLM-Level Limitation
- Lack of grounding in actual game rules/mechanics
- Tendency to generate plausible-sounding but incorrect information
- Inadequate constraints on code generation

### Failure Category (preliminary)
- **Provisional category**: Grounding / Hallucination
- **Sub-category**: Domain constraint violation

### Architecture Factors
- **Agent architecture**: Skill library + automatic curriculum + iterative code generation
- **Architecture-specific factors**: Self-verification module sometimes catches these; can iterate with feedback

### Reproducibility
- **Reproducible**: Yes (frequently observed)
- **Reproduction notes**: More common with domain-specific constraints not explicit in prompt

### Mitigation Strategies
#### Attempted
Self-verification module checks code execution results against expectations (partially effective)

#### Potential
- Explicit knowledge base of valid items/recipes
- Validation layer between code generation and execution
- Fine-tuning on Minecraft mechanics
- Constraint-guided code generation

#### Limitations
Maintaining comprehensive domain knowledge base is labor-intensive; constraints may limit creativity in valid scenarios

### Related Failures
FI-004 (Voyager self-verification failure), FI-020 (hallucination cascade)

---

## FI-004: Voyager Self-Verification Malfunction

### Source Information
- **Source type**: Paper / Technical Report
- **Source URL**: https://voyager.minedojo.org/
- **Date reported**: 2023
- **Agent framework**: Voyager
- **Base LLM**: GPT-4

### Task Context
- **Task type**: Embodied/robotics (Minecraft)
- **Task complexity**: Moderate
- **Task horizon**: Multi-turn (<5)
- **Task description**: Agent attempts to kill spider; self-verification checks if task succeeded

### Failure Description
#### Observable Behavior
Agent successfully kills spider (spider string drops as evidence), but self-verification module fails to interpret the spider string as evidence of successful spider-killing

#### Expected Behavior
Self-verification correctly parses environment feedback and recognizes task completion signals

#### Failure Impact
- **Impact severity**: Moderate
- **Recovery**: Automatic (automatic curriculum can retry)
- **Consequences**: False negative (success reported as failure), unnecessary retries

### Root Cause Hypothesis
#### Immediate Cause
Self-verification prompt or parsing logic fails to correctly map environment observation ("spider string") to task success criterion ("killed spider")

#### Underlying Cause
- Grounding problem: mapping between environment observations and semantic task goals
- Evaluation brittleness: small variations in observations lead to misclassification

#### LLM-Level Limitation
Implicit reasoning about causal relationships (spider string → spider was killed); may require explicit domain knowledge

### Failure Category (preliminary)
- **Provisional category**: Self-correction / Grounding
- **Sub-category**: Evaluation failure (false negative)

### Architecture Factors
- **Agent architecture**: Self-verification module evaluates action outcomes
- **Architecture-specific factors**: Same LLM does action generation and evaluation - prone to same grounding issues

### Reproducibility
- **Reproducible**: Partially (depends on specific observation variations)
- **Reproduction notes**: More common when success signals are indirect rather than explicit

### Mitigation Strategies
#### Attempted
Iterative prompting to improve self-verification accuracy

#### Potential
- Explicit success criteria in structured format
- Separate evaluation model or rule-based checker
- Few-shot examples of observation-to-success mappings
- Ground truth validation on subset

#### Limitations
Perfect evaluation requires solving grounding problem; rule-based checkers are brittle

### Related Failures
FI-003 (Voyager hallucination), FI-013 (reflection degeneration)

---

## FI-005: LangChain Tool Call Fabrication

### Source Information
- **Source type**: GitHub Issue
- **Source URL**: https://github.com/langchain-ai/deepagents/issues/947
- **Date reported**: 2024
- **Agent framework**: LangChain (DeepAgents)
- **Base LLM**: Not specified (likely GPT-4 or GPT-4o)

### Task Context
- **Task type**: General (tool-augmented task)
- **Task complexity**: Moderate
- **Task horizon**: Multi-turn (<5)
- **Task description**: Agent receives tool error; expected to retry with corrected parameters

### Failure Description
#### Observable Behavior
Instead of executing tool, LLM generates fake Observation output and continues to final answer without actually calling the tool

#### Expected Behavior
Agent executes tool, receives real observation, uses actual results to inform response

#### Failure Impact
- **Impact severity**: Critical
- **Recovery**: Not automatic (agent continues with fabricated results)
- **Consequences**: Incorrect output based on hallucinated data, user receives false information

### Root Cause Hypothesis
#### Immediate Cause
LLM generates text in the format of a tool observation rather than triggering actual tool call

#### Underlying Cause
- Ambiguity in prompt about when to generate observation vs. when to call tool
- Model may "shortcut" tool calling when it's confident about result
- Inadequate type enforcement (text generation vs. structured tool call)

#### LLM-Level Limitation
Text generation model doesn't inherently distinguish between "describe what tool would return" and "call tool and return actual result"

### Failure Category (preliminary)
- **Provisional category**: Tool-use
- **Sub-category**: Fabricated execution / Hallucinated tool results

### Architecture Factors
- **Agent architecture**: Tool-augmented LLM
- **Architecture-specific factors**: Relies on LLM to decide when to call tools vs. generate text; no strict enforcement

### Reproducibility
- **Reproducible**: Yes (reported with both custom and official models)
- **Reproduction notes**: More likely when tool error occurred previously; model may avoid "failed" tool

### Mitigation Strategies
#### Attempted
Issue reports this as bug needing fix in LangChain

#### Potential
- Strict structured output format (JSON schema) for tool calls
- Separate tool-calling decision from text generation
- Validation layer: if tool was specified, verify actual execution occurred
- Penalize/block text generation in observation format

#### Limitations
Enforcement may reduce flexibility; some tasks benefit from model reasoning about hypothetical tool results

### Related Failures
FI-006 (LangChain parsing errors), FI-010 (nested API call failures)

### Notes
This is one of the most concerning failure modes - agent confidently proceeds with fabricated data, no visible error signal to user

---

## FI-006: LangChain JSON Parsing Errors in Tool Calls

### Source Information
- **Source type**: GitHub Issue
- **Source URL**: https://github.com/langchain-ai/langchain/issues/33504
- **Date reported**: 2024
- **Agent framework**: LangChain
- **Base LLM**: Various

### Task Context
- **Task type**: Various (tool-augmented tasks)
- **Task complexity**: Moderate
- **Task horizon**: Multi-turn (<5)
- **Task description**: Agent attempts to call tools but generates malformed JSON

### Failure Description
#### Observable Behavior
create_agent has no mechanism to convert invalid_tool_calls into ToolMessage objects that LLM can process. Agent cannot retry after JSON parsing failure.

#### Expected Behavior
JSON parsing failures trigger automatic retry with error message; agent corrects malformed JSON

#### Failure Impact
- **Impact severity**: High
- **Recovery**: Manual (agent doesn't auto-recover)
- **Consequences**: Task failure despite agent being capable of succeeding with valid JSON

### Root Cause Hypothesis
#### Immediate Cause
LLM generates syntactically invalid JSON for tool call parameters

#### Underlying Cause
- LLMs imperfect at generating structured output consistently
- Error handling missing in create_agent (unlike older AgentExecutor)
- No feedback loop from parsing error to retry

#### LLM-Level Limitation
Even GPT-4 occasionally generates malformed JSON, especially with complex nested structures

### Failure Category (preliminary)
- **Provisional category**: Tool-use
- **Sub-category**: Structured output generation / Parsing error

### Architecture Factors
- **Agent architecture**: Tool-calling agent
- **Architecture-specific factors**: create_agent API lacks error handling that AgentExecutor had; regression in robustness

### Reproducibility
- **Reproducible**: Yes (relatively common according to issue discussion)
- **Reproduction notes**: More common with complex tool schemas; increased frequency with longer conversations

### Mitigation Strategies
#### Attempted
Issue requests adding handle_parsing_errors capability to create_agent

#### Potential
- Automatic retry with parsing error message
- JSON schema validation before sending to parser
- Structured output mode (when available from LLM provider)
- Fallback to simpler tool call format

#### Limitations
Retries consume additional tokens/cost; excessive retries may indicate deeper problem

### Related Failures
FI-005 (tool call fabrication), FI-008 (Gemini tool calling issues)

### Notes
Issue author notes "JSON parsing failures are relatively common" and "automatic retry capability is essential for production robustness"

---

## FI-007: CrewAI Agent Loop Without Convergence

### Source Information
- **Source type**: Community Report
- **Source URL**: https://community.crewai.com/t/agents-keeps-going-in-a-loop/1053
- **Date reported**: 2024
- **Agent framework**: CrewAI
- **Base LLM**: Not specified

### Task Context
- **Task type**: Data extraction
- **Task complexity**: Moderate
- **Task horizon**: Long-running (5-20 turns)
- **Task description**: Agent attempting data extraction task

### Failure Description
#### Observable Behavior
Agent repeatedly attempts same extraction process without success; loop continues indefinitely

#### Expected Behavior
Agent recognizes repeated failures, either succeeds after adjustment or signals task is not completable

#### Failure Impact
- **Impact severity**: High
- **Recovery**: Manual intervention required
- **Consequences**: Token/cost exhaustion, user frustration

### Root Cause Hypothesis
#### Immediate Cause
Agent doesn't detect it's repeating the same failed strategy

#### Underlying Cause
- No action history tracking or loop detection
- Insufficient feedback about why extraction failed
- Context degradation over multiple failed attempts

#### LLM-Level Limitation
Limited self-monitoring; can't recognize behavioral loops without explicit state tracking

### Failure Category (preliminary)
- **Provisional category**: Resource management / Self-correction
- **Sub-category**: Infinite loop without convergence

### Architecture Factors
- **Agent architecture**: Multi-agent CrewAI system
- **Architecture-specific factors**: May lack loop detection mechanisms present in other frameworks

### Reproducibility
- **Reproducible**: Yes (user reported consistent occurrence)
- **Reproduction notes**: Unclear what specific task characteristics trigger this

### Mitigation Strategies
#### Attempted
Unknown from report

#### Potential
- Hard turn limit
- Action deduplication
- Explicit failure signaling after N attempts
- Progress metrics (is each attempt getting closer?)

#### Limitations
Distinguishing "appropriate repetition with refinement" from "unproductive loop" requires semantic understanding

### Related Failures
FI-001 (AutoGPT infinite loop), FI-015 (Toqan repetition)

---

## FI-008: LangChain Gemini Tool Calling Failure

### Source Information
- **Source type**: GitHub Issue
- **Source URL**: https://github.com/langchain-ai/langchain/issues/29418
- **Date reported**: 2024
- **Agent framework**: LangChain with Gemini
- **Base LLM**: Google Gemini

### Task Context
- **Task type**: Various (tool-augmented)
- **Task complexity**: Simple to moderate
- **Task horizon**: Multi-turn (<5)
- **Task description**: Agent attempts to use tools with Gemini backend

### Failure Description
#### Observable Behavior
Tool calling broken for Gemini with legacy agent; ToolMessage.name not being set correctly

#### Expected Behavior
Tool calls work consistently across LLM providers; ToolMessage properly populated

#### Failure Impact
- **Impact severity**: High (complete tool-use failure)
- **Recovery**: Requires code fix
- **Consequences**: Gemini backend unusable for tool-augmented tasks

### Root Cause Hypothesis
#### Immediate Cause
ToolMessage.name field not being populated for Gemini responses

#### Underlying Cause
- Provider-specific integration bug
- Differences in how Gemini structures tool call responses vs. OpenAI
- Inadequate testing across providers

#### LLM-Level Limitation
Not LLM limitation - integration/compatibility issue

### Failure Category (preliminary)
- **Provisional category**: Tool-use
- **Sub-category**: Provider compatibility / Integration bug

### Architecture Factors
- **Agent architecture**: LangChain tool-calling agent
- **Architecture-specific factors**: Provider abstraction layer doesn't fully normalize tool call formats

### Reproducibility
- **Reproducible**: Yes (consistent for Gemini + legacy agent combination)
- **Reproduction notes**: Specific to Gemini provider with legacy agent

### Mitigation Strategies
#### Attempted
GitHub issue filed; presumably fix is in progress

#### Potential
- Improved provider abstraction with consistent tool call format
- Comprehensive cross-provider testing
- Provider-specific adapters

#### Limitations
Supporting multiple providers with different APIs is inherently complex

### Related Failures
FI-006 (LangChain JSON parsing), FI-021 (retriever compatibility)

---

## FI-009: WebArena Dropdown Menu Accessibility Failure

### Source Information
- **Source type**: Paper / Technical Report
- **Source URL**: https://webarena.dev/ | https://openreview.net/pdf?id=94tlGxmqkN
- **Date reported**: 2024
- **Agent framework**: Various (tested on WebArena benchmark)
- **Base LLM**: GPT-4

### Task Context
- **Task type**: Web navigation
- **Task complexity**: Simple to moderate
- **Task horizon**: Multi-turn (<5)
- **Task description**: Agent needs to select option from dropdown menu

### Failure Description
#### Observable Behavior
Agent cannot select from dropdown menus due to UI accessibility tree issues in Playwright

#### Expected Behavior
Agent can interact with all standard UI elements including dropdowns

#### Failure Impact
- **Impact severity**: Moderate (affects specific task types)
- **Recovery**: Not automatic (environment limitation)
- **Consequences**: Tasks requiring dropdown selection fail, artificially low success rates

### Root Cause Hypothesis
#### Immediate Cause
Playwright's accessibility tree representation doesn't expose dropdown menus in selectable format

#### Underlying Cause
Environment/tooling limitation, not agent limitation

#### LLM-Level Limitation
Not applicable (tooling issue)

### Failure Category (preliminary)
- **Provisional category**: Grounding / Tool-use
- **Sub-category**: Environment limitation / UI accessibility

### Architecture Factors
- **Agent architecture**: Web navigation agent
- **Architecture-specific factors**: Depends on Playwright for web interaction; limited by Playwright's capabilities

### Reproducibility
- **Reproducible**: Yes (consistent environment limitation)
- **Reproduction notes**: Affects all agents using WebArena environment with dropdown-dependent tasks

### Mitigation Strategies
#### Attempted
WebArena Verified (2024) attempted to fix environment issues

#### Potential
- Improved accessibility tree representation
- Alternative dropdown interaction methods
- Environment redesign to avoid dropdowns

#### Limitations
Fixing requires changes to Playwright or environment infrastructure

### Related Failures
FI-022 (grounding challenges), FI-023 (visual grounding)

### Notes
This is example of "agent failure" that's actually environment/evaluation limitation - important to distinguish

---

## FI-010: GPT-4o Nested API Call Failures

### Source Information
- **Source type**: Technical Report / Benchmark
- **Source URL**: https://dev.to/terzioglub/why-llm-agents-break-when-you-give-them-tools-and-what-to-do-about-it-f5
- **Date reported**: 2024
- **Agent framework**: Various
- **Base LLM**: GPT-4o

### Task Context
- **Task type**: Various (complex tool workflows)
- **Task complexity**: Complex
- **Task horizon**: Multi-turn (<5 per sequence)
- **Task description**: Tasks requiring chained/nested API calls where output of one call feeds into next

### Failure Description
#### Observable Behavior
GPT-4o achieved only 28% full sequence match accuracy on NESTFUL benchmark (nested API call sequences)

#### Expected Behavior
Agent successfully chains API calls with 80%+ accuracy (comparable to simpler single-call tasks)

#### Failure Impact
- **Impact severity**: High
- **Recovery**: Usually requires retry or simplified workflow
- **Consequences**: Complex workflows unreliable, error compounds at each step

### Root Cause Hypothesis
#### Immediate Cause
Error rate compounds at each step when tools need to be chained

#### Underlying Cause
- Difficulty tracking state across multiple tool calls
- Each call introduces opportunity for error (parameter extraction, result parsing)
- Complexity of reasoning about data flow through API chain

#### LLM-Level Limitation
Multi-step procedural reasoning with tool integration; maintaining bindings between variables across steps

### Failure Category (preliminary)
- **Provisional category**: Tool-use / Planning
- **Sub-category**: Multi-step tool orchestration

### Architecture Factors
- **Agent architecture**: Tool-augmented with API chaining
- **Architecture-specific factors**: Error propagation through chain; no checkpoint/rollback mechanism

### Reproducibility
- **Reproducible**: Yes (benchmark results)
- **Reproduction notes**: Reproducible on NESTFUL benchmark; increases with chain length

### Mitigation Strategies
#### Attempted
Unknown from source

#### Potential
- Break long chains into smaller validated segments
- Explicit state tracking between calls
- Retry with error feedback for each step
- Plan validation before execution

#### Limitations
Breaking chains may reduce efficiency; validation overhead adds latency/cost

### Related Failures
FI-005 (tool fabrication), FI-006 (parsing errors), FI-011 (semantic errors)

---

## Summary Statistics (Batch 01)

**Total instances documented**: 10
**Date range**: 2023-2024
**Frameworks covered**: AutoGPT (2), Voyager (2), LangChain (4), CrewAI (1), WebArena benchmark (1)
**LLM models**: GPT-4 (7), GPT-4o (1), Gemini (1), Not specified (1)

**Provisional category distribution**:
- Tool-use: 5
- State tracking: 2
- Resource management: 2
- Grounding: 3
- Self-correction: 2
- Planning: 1

(Note: Some instances tagged with multiple categories)

**Next batch priorities**:
- More plan-then-execute failures
- Reflection/self-correction failures
- Production deployment failures (Toqan, Parcha)
- Security vulnerabilities (prompt injection examples)
- Context degradation instances
- Tree-of-thought specific failures
