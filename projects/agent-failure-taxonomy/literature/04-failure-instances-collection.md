# Failure Instance Collection

**Date**: 2026-03-25
**Scope**: Detailed failure instances from production systems, GitHub issues, and research papers
**Format**: Each instance includes: description, source, architecture, root cause, symptoms, impact

---

## Instance Format Template

```
### Instance ID: [Number]
**Description**: Brief summary of failure
**Source**: Citation or URL
**Architecture**: ReAct / Plan-then-execute / Autonomous loop / ToT / Reflection / Multi-agent
**Category**: Provisional taxonomy category
**Root Cause**: Underlying reason for failure
**Symptoms**: Observable manifestations
**Impact**: Consequences (task failure / degraded performance / security issue / cost)
**Reproducibility**: Easy / Medium / Hard
**Mitigation**: Known fixes or workarounds
```

---

## Production System Failures

### Instance 11: CrewAI Tool Caching Bug
**Description**: Tool usage logic bug caused results to be cached even when tool execution returned errors, preventing tool from being used again in subsequent attempts
**Source**: [CrewAI v1.1.0 Release Notes](https://community.crewai.com/t/new-release-crewai-1-1-0-is-out/7142)
**Date**: October 2025
**Architecture**: Multi-agent (manager-worker)
**Category**: Tool-use failures → Result validation
**Root Cause**: Incorrect caching logic that cached error states as if they were successful results
**Symptoms**:
- Tool appears to succeed on first call but returns error
- Subsequent attempts to use same tool fail silently
- Agent continues without recognizing tool is broken
**Impact**: Task failure — agent cannot complete tasks requiring repeated tool use after initial failure
**Reproducibility**: Easy — reliably occurs when tool returns error on first call
**Mitigation**: Fixed in CrewAI v1.1.0 — proper error handling before caching

---

### Instance 12: CrewAI Azure OpenAI Memory Conflict
**Description**: When memory is enabled, Azure OpenAI provider fails with "Unsupported response_format" error
**Source**: [CrewAI Issue #3986](https://github.com/crewAIInc/crewAI/issues/3986)
**Date**: November 28, 2025
**Architecture**: Any (provider compatibility issue)
**Category**: Tool-use failures → Provider compatibility
**Root Cause**: CrewAI sends response_format parameter not supported by Azure OpenAI API when memory features are enabled
**Symptoms**:
- LLM call fails with Azure API error
- Only occurs when memory=True
- Works fine with OpenAI but not Azure
**Impact**: Complete task failure — cannot use memory features with Azure backend
**Reproducibility**: Easy — 100% reproducible with Azure + memory enabled
**Mitigation**: Disable memory or switch to OpenAI provider (workaround, not fix)

---

### Instance 13: CrewAI Token Exposure via Exception Handling
**Description**: When CrewAI platform encountered provisioning failures, exception handling exposed internal GitHub token to users
**Source**: [Noma Security Analysis](https://noma.security/blog/uncrew-the-risk-behind-a-leaked-internal-github-token-at-crewai/)
**Date**: 2025
**Architecture**: Platform infrastructure
**Category**: Security vulnerabilities → Credential exposure
**Root Cause**: Exception messages included sensitive environment variables without sanitization
**Symptoms**:
- Stack traces visible to users during platform errors
- GitHub token visible in exception output
- No exception filtering or sanitization
**Impact**: Critical security vulnerability — exposed write access to CrewAI repositories
**Reproducibility**: Medium — requires triggering specific provisioning failure
**Mitigation**: Sanitize exception messages, never include credentials in error output

---

### Instance 14: AutoGPT Looping with Ambiguous Tasks
**Description**: Agent enters infinite loops when tasks are ambiguous, repeatedly attempting same failed action without recognizing it's making no progress
**Source**: [AutoGPT Review 2025](https://sider.ai/blog/ai-tools/autogpt-review-is-autonomous-ai-ready-for-real-work-in-2025)
**Date**: 2024-2025 (persistent issue)
**Architecture**: Autonomous loop
**Category**: Planning failures → Progress detection / Infinite loops
**Root Cause**: No explicit progress detection mechanism; agent relies on self-evaluation which fails to recognize stagnation
**Symptoms**:
- Same action repeated multiple times (10+ iterations)
- No observable progress toward goal
- Agent does not ask for clarification
- Eventually hits token/cost limits
**Impact**: Task failure + cost exhaustion — wastes resources without completing task
**Reproducibility**: Medium — reliably occurs with ambiguous tasks, but task-dependent
**Mitigation**: 2024 updates added loop detection, but issue persists in production

---

### Instance 15: AutoGPT Web Data Hallucinations
**Description**: Agent hallucinates facts when processing web data, presents false information as ground truth
**Source**: [AutoGPT Review 2025](https://sider.ai/blog/ai-tools/autogpt-review-is-autonomous-ai-ready-for-real-work-in-2025)
**Date**: 2024-2025 (persistent issue)
**Architecture**: Autonomous loop
**Category**: Grounding failures → Web content interpretation + Hallucinations
**Root Cause**: LLM fills gaps in scraped web data with plausible but incorrect information; no verification against source
**Symptoms**:
- Facts stated with confidence that don't appear in source
- Mixing of actual scraped data with fabricated details
- No indication that information is uncertain
**Impact**: Incorrect outputs — agent produces wrong answers while appearing confident
**Reproducibility**: Medium — probabilistic, depends on web content and model state
**Mitigation**: No reliable fix identified; verification against ground truth required

---

### Instance 16: AutoGPT Site Blocker and Scraper Fragility
**Description**: External site blockers (anti-bot measures) and flaky web scrapers cause execution to break
**Source**: [AutoGPT Review 2025](https://sider.ai/blog/ai-tools/autogpt-review-is-autonomous-ai-ready-for-real-work-in-2025)
**Date**: 2024-2025
**Architecture**: Autonomous loop
**Category**: Grounding failures → Environment accessibility + Error recovery
**Root Cause**: Web scraping tools fail when sites use bot protection; no graceful degradation
**Symptoms**:
- Scraper returns empty results or errors
- Agent continues as if scraping succeeded
- No retry with alternative methods
**Impact**: Task failure — agent cannot access required information
**Reproducibility**: High — many major sites block automated access
**Mitigation**: Robust scraping tools, browser automation, fallback strategies

---

## Research Paper Failures

### Instance 17: Reasoning-Driven Tool Hallucination
**Description**: Enhancing reasoning capabilities (via RL or CoT) proportionally increases tool hallucination rates
**Source**: [The Reasoning Trap, arXiv:2510.22977](https://arxiv.org/html/2510.22977v1)
**Date**: October 2025
**Architecture**: All (fundamental limitation)
**Category**: Tool-use failures → Hallucinated execution + Reasoning limitations
**Root Cause**: Stronger reasoning creates more detailed internal models of tools that diverge from actual behavior; effect is method-agnostic and task-agnostic
**Symptoms**:
- Models with better math reasoning hallucinate tools more
- Training on non-tool tasks increases tool hallucination
- Effect appears with SFT and inference-time prompting
**Impact**: Fundamental trade-off — cannot improve reasoning without increasing hallucination
**Reproducibility**: Easy — consistently reproduced across models and training methods
**Mitigation**: No full mitigation; preference optimization reduces hallucinations but degrades utility

---

### Instance 18: Tool Count Scaling Failures
**Description**: As number of available tools increases, agents increasingly call wrong tools or fabricate non-existent tools
**Source**: [The Reasoning Trap, arXiv:2510.22977](https://arxiv.org/html/2510.22977v1) + [Agent Hallucinations Survey, arXiv:2509.18970](https://arxiv.org/html/2509.18970v1)
**Date**: 2025
**Architecture**: All
**Category**: Tool-use failures → Selection hallucination
**Root Cause**: Tool documentation becomes harder to parse with many tools; token limits force truncation; selection becomes harder
**Symptoms**:
- Function selection errors increase with tool count
- Calling non-existent tools (names that seem plausible)
- Confusing similar tools
**Impact**: Task failure — wrong or non-existent tools cannot complete task
**Reproducibility**: Easy — scales predictably with number of tools
**Mitigation**: Tool organization, better documentation, retrieval-augmented tool selection

---

### Instance 19: False Task Completion Reporting
**Description**: Agents report tasks as complete when they have not actually finished, creating false system states accepted by downstream decision chains
**Source**: [Architecting Resilient LLM Agents, arXiv:2509.08646](https://arxiv.org/pdf/2509.08646)
**Date**: February 2026
**Architecture**: Plan-then-execute (but affects others)
**Category**: Self-correction failures → False verification + State tracking
**Root Cause**: Agent's self-evaluation incorrectly assesses task completion; no external verification
**Symptoms**:
- Agent claims "Task completed successfully"
- Objective evaluation shows task incomplete
- Downstream agents/systems accept false completion
- Cascading failures as wrong assumptions propagate
**Impact**: Critical — creates false beliefs in system that propagate and compound
**Reproducibility**: Medium — depends on task complexity and completion criteria
**Mitigation**: External verification, objective completion criteria, human-in-loop for critical tasks

---

### Instance 20: Memory Persistence of Errors
**Description**: Errors written to long-term memory (vector stores, knowledge bases) continue influencing future reasoning even after original source is corrected
**Source**: [OWASP ASI08](https://adversa.ai/blog/cascading-failures-in-agentic-ai-complete-owasp-asi08-security-guide-2026/)
**Date**: 2025-2026
**Architecture**: Any with persistent memory
**Category**: State tracking failures → Memory corruption + Error propagation
**Root Cause**: No mechanism to invalidate or correct past memories; memories treated as immutable ground truth
**Symptoms**:
- Agent repeats errors from past sessions
- Correcting prompt doesn't fix behavior
- Error persists across sessions and restarts
- No visible indication that memory is corrupted
**Impact**: Persistent degradation — agent permanently learns incorrect information
**Reproducibility**: Easy — reliably occurs when errors are committed to memory
**Mitigation**: Memory validation, expiration, correction mechanisms; versioning

---

### Instance 21: Multi-Agent Error Consensus Formation
**Description**: In multi-agent systems, minor inaccuracies gradually solidify into system-level false consensus through iteration, with errors amplifying through message dependencies
**Source**: [From Spark to Fire, arXiv:2603.04474](https://arxiv.org/abs/2603.04474v1)
**Date**: March 2026
**Architecture**: Multi-agent
**Category**: Error propagation → Cascade amplification + Coordination
**Root Cause**: Agents reinforce each other's errors through collaborative messages; recursive context reuse amplifies mistakes
**Symptoms**:
- Initial small error grows with each agent interaction
- Eventually reaches "consensus" state that is wrong
- Once consensus formed, extremely difficult to correct (consensus inertia)
- Network topology affects error spread rate
**Impact**: System-level failure — entire MAS believes and acts on false information
**Reproducibility**: Medium — requires specific message passing patterns
**Mitigation**: Diverse information sources, external validation, consensus skepticism

---

### Instance 22: Prompt Sensitivity in Tree-of-Thought
**Description**: ToT accuracy drops precipitously (up to -54%) under prompt perturbations like narrative reframing, misleading constraints, or example reordering
**Source**: Multiple 2025 analyses
**Date**: 2025
**Architecture**: Tree-of-Thought
**Category**: Planning failures → Prompt brittleness + Reasoning limitations
**Root Cause**: LLMs overfit to prompt surface structure; reasoning paths heavily dependent on exact wording
**Symptoms**:
- Identical task with rephrased prompt yields dramatically different performance
- Not mitigated by model size
- Direction of change (better/worse) is unpredictable
- Adding "misleading" constraints can help or hurt
**Impact**: Unreliable performance — cannot predict agent behavior under prompt variations
**Reproducibility**: Easy — reliably occurs with systematic prompt variations
**Mitigation**: Prompt ensembling, instruction tuning for robustness (partial fixes only)

---

### Instance 23: ToT Hallucination of Non-Existent Constraints
**Description**: On constraint satisfaction tasks (e.g., graph coloring), LLMs systematically hallucinate spurious edges/constraints not in input, causing cascading logical failures
**Source**: 2025 LLM reasoning failure studies
**Date**: 2025
**Architecture**: Tree-of-Thought (but affects others)
**Category**: Grounding failures → Constraint hallucination + Planning failures
**Root Cause**: Fundamental limitation in factual memory isolation — model adds plausible but wrong constraints
**Symptoms**:
- Agent references edges/constraints not in problem specification
- Hallucination rate scales linearly with problem complexity
- Chain-of-thought prompting accentuates (not mitigates) the problem
- Leads to logically consistent but factually wrong solutions
**Impact**: Task failure — correct reasoning applied to wrong problem produces wrong answer
**Reproducibility**: High — systematic pattern across constraint problems
**Mitigation**: No reliable fix; external validation of constraints required

---

### Instance 24: Hierarchical Planning Evaluation Conflation
**Description**: Outcome-based evaluation alone obscures failure sources by conflating planning errors, execution mistakes, and ineffective feedback use
**Source**: [Why Do LLM-based Web Agents Fail, arXiv:2603.14248](https://arxiv.org/html/2603.14248)
**Date**: March 2026
**Architecture**: Plan-then-execute (but applies to others)
**Category**: Evaluation methodology issue (meta-failure)
**Root Cause**: Aggregate success/failure metrics don't distinguish where in agent pipeline failure occurred
**Symptoms**:
- Cannot tell if failure was due to bad planning, bad execution, or bad replanning
- Same aggregate performance can hide different failure modes
- Architecture comparison misleading without phase-specific evaluation
**Impact**: Research/development impact — cannot improve agents without knowing where they fail
**Reproducibility**: N/A (evaluation issue)
**Mitigation**: Hierarchical evaluation across planning, execution, replanning phases

---

### Instance 25: Plan-Then-Execute False Completion with State Propagation
**Description**: Agent claims to have deleted data or ceased communication when it hasn't, creating false system states accepted downstream
**Source**: [Architecting Resilient LLM Agents, arXiv:2509.08646](https://arxiv.org/pdf/2509.08646)
**Date**: February 2026
**Architecture**: Plan-then-execute
**Category**: Self-correction failures → State verification + Tool-use
**Root Cause**: Agent's internal model of actions taken diverges from actual system state; no state verification
**Symptoms**:
- Agent reports "Data deleted" but data still exists
- Agent reports "Communication stopped" but continues sending messages
- Downstream systems trust agent's reported state
- False state propagates through decision chains
**Impact**: Critical — system operates on false assumptions about world state
**Reproducibility**: Medium — requires multi-step tasks with state changes
**Mitigation**: External state verification, action confirmation, state reconciliation

---

## Architecture-Specific Failure Patterns

### Plan-Then-Execute Cluster

**Instances**: 19, 24, 25
**Common Pattern**: Initial plan commitment without feedback causes failures to compound; replanning is expensive and may repeat mistakes
**Root Cause**: Separation of planning and execution phases prevents tight feedback loop
**Mitigation**: Hybrid approaches with periodic replanning checkpoints

---

### Autonomous Loop Cluster (AutoGPT-style)

**Instances**: 14, 15, 16
**Common Pattern**: Progress detection failures lead to infinite loops and wasted resources; hallucinations from web data
**Root Cause**: Over-reliance on self-evaluation without external validation; no progress metrics
**Mitigation**: Explicit progress tracking, loop detection, external verification

---

### Tool Hallucination Cluster

**Instances**: 17, 18
**Common Pattern**: Better reasoning paradoxically increases tool hallucination; scales with tool count
**Root Cause**: Fundamental LLM limitation — cannot fully eliminate without sacrificing capability
**Mitigation**: Partial fixes only (preference optimization trades capability for reliability)

---

### State/Memory Corruption Cluster

**Instances**: 19, 20, 25
**Common Pattern**: Errors committed to memory or reported as truth persist and propagate
**Root Cause**: No validation or correction mechanisms for committed state
**Mitigation**: Memory validation, state reconciliation, external verification

---

### Tree-of-Thought Cluster

**Instances**: 22, 23
**Common Pattern**: Prompt brittleness and constraint hallucination; CoT can amplify rather than fix
**Root Cause**: Overfitting to prompt structure + factual memory isolation failures
**Mitigation**: Prompt ensembling, constraint validation (partial fixes)

---

## Summary Statistics

**Total Instances Documented**: 25 (10 from previous sessions + 15 new)

**By Architecture**:
- Autonomous loop: 4 instances
- Plan-then-execute: 3 instances
- Multi-agent: 3 instances
- Tree-of-Thought: 2 instances
- All architectures: 13 instances

**By Category** (provisional):
- Tool-use failures: 7 instances
- State tracking / Memory: 4 instances
- Planning failures: 4 instances
- Grounding failures: 4 instances
- Self-correction failures: 3 instances
- Security vulnerabilities: 2 instances
- Error propagation: 1 instance

**By Source**:
- Production systems (GitHub issues): 6 instances
- Research papers: 9 instances
- Previous survey: 10 instances

**Reproducibility**:
- Easy: 11 instances
- Medium: 11 instances
- Hard: 3 instances

---

## Next Collection Priorities

To reach 50 instances target, need 25 more. Focus areas:

1. **LangChain GitHub issues** (5-10 instances)
   - Tool calling failures
   - Memory issues
   - Error handling

2. **ReAct-specific failures** (3-5 instances)
   - Currently underrepresented
   - Need architectural balance

3. **Benchmark failures** (5-10 instances)
   - WebArena, SWE-bench, AgentBench specific failures
   - Deep-read papers for detailed examples

4. **Reflection/self-correction failures** (3-5 instances)
   - Reflexion degeneration examples
   - Self-evaluation accuracy

5. **Context degradation examples** (3-5 instances)
   - Long-running task failures
   - "Lost in the middle" concrete examples

**Target**: 50 instances by end of next session, enabling open coding phase

---

## LangChain Tool Calling Failures

### Instance 26: Tool Runtime Parameter Missing After Upgrade
**Description**: After upgrading to LangChain v1.0, tools cannot be called due to missing runtime parameter despite documentation stating it should be auto-injected
**Source**: [LangChain Issue #34045](https://github.com/langchain-ai/langchain/issues/34045)
**Date**: November 2025
**Architecture**: ReAct (LangChain agent)
**Category**: Tool-use failures → Framework compatibility
**Root Cause**: Breaking change in v1.0 where runtime parameter injection behavior changed without clear migration path
**Symptoms**:
- Tool calls fail with "missing runtime parameter" error
- Documentation claims auto-injection but doesn't work
- No error until runtime when tool is actually invoked
**Impact**: Complete task failure — tools cannot execute
**Reproducibility**: Easy — 100% reproducible after upgrade to v1.0
**Mitigation**: Manual parameter injection or downgrade (workaround, not fix)

---

### Instance 27: OpenAI Web Search Tool Hardcoded Value Error
**Description**: Latest OpenAI web_search tool raises ValueError due to hardcoded "web_search_preview" in langchain-core, but OpenAI now uses "web_search"
**Source**: [LangChain Issue #32735](https://github.com/langchain-ai/langchain/issues/32735)
**Date**: August 2025
**Architecture**: ReAct (LangChain agent)
**Category**: Tool-use failures → Provider API version mismatch
**Root Cause**: Hardcoded function name in framework doesn't match updated OpenAI API
**Symptoms**:
- ValueError when attempting to use web_search tool
- Error message references old "web_search_preview" name
- Tool cannot be invoked at all
**Impact**: Complete tool failure — cannot use OpenAI web search
**Reproducibility**: Easy — 100% reproducible with latest OpenAI API
**Mitigation**: Framework update required (not under user control)

---

### Instance 28: Invalid Tool Calls Not Converted to Recoverable Messages
**Description**: create_agent function doesn't handle invalid_tool_calls from JSON parsing errors, lacking retry mechanism that AgentExecutor has
**Source**: [LangChain Issue #33504](https://github.com/langchain-ai/langchain/issues/33504)
**Date**: October 2025
**Architecture**: ReAct (LangChain agent)
**Category**: Error recovery failures → Parsing error handling
**Root Cause**: create_agent API missing handle_parsing_errors mechanism; doesn't convert invalid_tool_calls to ToolMessage for LLM retry
**Symptoms**:
- JSON parsing errors during tool calls cause complete failure
- No automatic retry with error feedback to LLM
- Issue reports note JSON parsing failures are "relatively common"
**Impact**: Task failure — agent cannot recover from common parsing errors
**Reproducibility**: Medium — depends on LLM producing malformed JSON
**Mitigation**: Use legacy AgentExecutor with handle_parsing_errors (regression in new API)

---

### Instance 29: Tool Calls Fail with Missing Positional Argument
**Description**: Tool calls sometimes fail with missing positional argument error, but renaming the argument makes issue disappear (naming conflict)
**Source**: [LangChain Issue #34029](https://github.com/langchain-ai/langchain/issues/34029)
**Date**: November 2025
**Architecture**: ReAct (LangChain agent)
**Category**: Tool-use failures → Parameter binding
**Root Cause**: Unclear naming conflict in parameter binding mechanism; specific argument names cause failures
**Symptoms**:
- Tool call fails with "missing positional argument" error
- Same tool works if argument is renamed
- Non-deterministic across different tool definitions
**Impact**: Task failure — specific tool configurations cannot work
**Reproducibility**: Medium — depends on argument naming
**Mitigation**: Rename arguments to avoid conflicts (workaround, root cause unclear)

---

### Instance 30: Azure Tool Choice BadRequestError
**Description**: Using gpt-oss-120b on Azure AI Foundry with tool choice="auto" raises BadRequestError requiring additional flags
**Source**: [LangChain Issue #32425](https://github.com/langchain-ai/langchain/issues/32425)
**Date**: August 2025
**Architecture**: ReAct (LangChain agent)
**Category**: Tool-use failures → Provider compatibility
**Root Cause**: Azure-specific requirements not handled by LangChain abstraction; requires --enable-auto-tool-choice and --tool-call-parser flags
**Symptoms**:
- BadRequestError when using tool_choice="auto"
- Works with OpenAI but not Azure
- Error message references Azure-specific flags
**Impact**: Complete failure on Azure backend
**Reproducibility**: Easy — 100% reproducible with Azure gpt-oss-120b
**Mitigation**: Provider-specific configuration (LangChain abstraction leaks)

---

### Instance 31: Agent Replies to User Instead of Correcting Tool Error
**Description**: When tool returns error message, agent replies directly to user instead of correcting action and resending to tool
**Source**: [LangChain Deepagents Issue #947](https://github.com/langchain-ai/deepagents/issues/947)
**Date**: January 2026
**Architecture**: ReAct (LangChain agent)
**Category**: Error recovery failures → Error routing + Tool-use
**Root Cause**: Agent misinterprets tool error as final output to user rather than feedback for self-correction
**Symptoms**:
- Tool returns error message
- Agent sends error message to user as final response
- Wrong message shown to wrong recipient in UI
- No retry or correction attempt
**Impact**: Task failure + poor UX — user sees internal error messages
**Reproducibility**: High — consistently occurs when tools return errors
**Mitigation**: Better error handling logic to distinguish tool feedback from user output

---

## ReAct-Specific Failures

### Instance 32: ReAct Tool Hallucination Without Fine-Tuning
**Description**: Without fine-tuning or few-shot examples, ReAct models hallucinate unavailable tools or functions, attempting to use non-existent capabilities
**Source**: [Latenode LangChain ReAct Guide](https://latenode.com/blog/langchain-react-agent-complete-implementation-guide-working-examples-2025)
**Date**: 2025
**Architecture**: ReAct
**Category**: Tool-use failures → Selection hallucination + Grounding
**Root Cause**: Base LLM without fine-tuning doesn't reliably constrain tool selection to available tools; hallucinates plausible but non-existent tools
**Symptoms**:
- Agent attempts to call tools not in tool registry
- Tool names seem plausible but don't exist
- Without few-shot examples, hallucination rate is high
- Reliability and accuracy significantly compromised
**Impact**: Task failure — hallucinated tools cannot execute
**Reproducibility**: High — predictably occurs without fine-tuning
**Mitigation**: Fine-tuning or extensive few-shot examples (significant cost)

---

### Instance 33: ReAct Infinite Loops Without Solution
**Description**: Agent enters infinite reasoning loops when unable to find solution, continuing to take actions indefinitely without recognizing stagnation
**Source**: [Latenode LangChain ReAct Guide](https://latenode.com/blog/langchain-react-agent-complete-implementation-guide-working-examples-2025) + [NVIDIA ReAct Docs](https://docs.nvidia.com/nemo/agent-toolkit/1.1/workflows/about/react-agent.html)
**Date**: 2025
**Architecture**: ReAct
**Category**: Planning failures → Progress detection + Infinite loops
**Root Cause**: Tight feedback loop without global progress evaluation; agent cannot meta-reason about whether it's making progress
**Symptoms**:
- Same reasoning pattern repeated across many iterations
- No convergence toward solution
- Eventually hits iteration limit or timeout
- Without single-agent self-evaluation, becomes trapped in execution loop
**Impact**: Task failure + resource exhaustion
**Reproducibility**: Medium — depends on task complexity and difficulty
**Mitigation**: Iteration limits, timeouts, explicit progress tracking (prevents indefinite loops but doesn't fix reasoning)

---

### Instance 34: ReAct Context Window Exhaustion on Complex Tasks
**Description**: Complex multi-step tasks exceed context window as ReAct stores reasoning traces, observations, and actions in short-term memory
**Source**: [Latenode LangChain ReAct Guide](https://latenode.com/blog/langchain-react-agent-complete-implementation-guide-working-examples-2025)
**Date**: 2025
**Architecture**: ReAct
**Category**: State tracking failures → Context window management
**Root Cause**: ReAct relies on LLM context window for all short-term memory; complex tasks with many steps accumulate too much context
**Symptoms**:
- Performance degradation as task progresses
- Eventually hits context limit
- May lose critical early information
- Cannot complete tasks requiring many reasoning-action cycles
**Impact**: Task failure on complex multi-step problems
**Reproducibility**: High — predictably fails for tasks exceeding context capacity
**Mitigation**: Context compression, summarization, external memory (significant architecture changes)

---

### Instance 35: ReAct Prompt Dependency - Missing Actions Unexecutable
**Description**: Every possible action must be outlined in input prompts; if action not included, model cannot perform it
**Source**: [Latenode LangChain ReAct Guide](https://latenode.com/blog/langchain-react-agent-complete-implementation-guide-working-examples-2025)
**Date**: 2025
**Architecture**: ReAct
**Category**: Grounding failures → Action space definition
**Root Cause**: ReAct relies on explicit action specification in prompts; cannot generalize to actions not described
**Symptoms**:
- Agent fails on tasks requiring undocumented actions
- May hallucinate similar action or fail silently
- Poorly tuned prompts lead to inefficient reasoning or incorrect tool usage
**Impact**: Limited capability — can only perform pre-specified actions
**Reproducibility**: High — consistently fails for actions not in prompt
**Mitigation**: Comprehensive prompt engineering (requires anticipating all needed actions)

---

### Instance 36: ReAct Performance Regression Without Fine-Tuning
**Description**: Without fine-tuning, ReAct performance is worse than simple Chain-of-Thought prompting, contradicting claimed benefits
**Source**: [Latenode LangChain ReAct Guide](https://latenode.com/blog/langchain-react-agent-complete-implementation-guide-working-examples-2025)
**Date**: 2025
**Architecture**: ReAct
**Category**: Planning failures → Reasoning quality without adaptation
**Root Cause**: ReAct reasoning-action interleaving requires model adaptation; base models don't naturally follow ReAct pattern effectively
**Symptoms**:
- Lower success rate than CoT on same tasks
- Reasoning steps don't effectively use action observations
- Actions don't align well with reasoning
**Impact**: Performance degradation compared to simpler approaches
**Reproducibility**: High — validated in original ReAct paper and replicated
**Mitigation**: Fine-tuning required (developers often neglect, leading to poor performance)

---

## WebArena Benchmark Failures

### Instance 37: WebArena DOM Timing Failures
**Description**: Agents attempt interactions before elements are fully loaded, causing actions to fail
**Source**: [WebArena Verified Paper](https://openreview.net/pdf?id=94tlGxmqkN) + [Invariant Labs Analysis](https://invariantlabs.ai/blog/what-we-learned-from-analyzing-web-agents)
**Date**: 2024-2025
**Architecture**: All web agents
**Category**: Grounding failures → Environment observation timing
**Root Cause**: Asynchronous page loading; agents don't wait for elements to be interactive before attempting actions
**Symptoms**:
- Actions fail with "element not found" or "element not interactive"
- 34% of WebArena failures attributed to timing issues
- Shopping tasks particularly affected (43% of timing failures)
**Impact**: High task failure rate from preventable timing errors
**Reproducibility**: High — systematic issue across web agents
**Mitigation**: Explicit wait conditions, element readiness checks

---

### Instance 38: WebArena Dropdown Menu Selection Impossible
**Description**: WebArena environment interface doesn't allow agents to select from dropdown menus due to Playwright UI accessibility tree issues
**Source**: [WebArena Verified Paper](https://openreview.net/pdf?id=94tlGxmqkN) + [Invariant Labs Analysis](https://invariantlabs.ai/blog/what-we-learned-from-analyzing-web-agents)
**Date**: 2024-2025
**Architecture**: All web agents
**Category**: Evaluation/environment failures → UI accessibility
**Root Cause**: Playwright's accessibility tree representation doesn't expose dropdown options in actionable format
**Symptoms**:
- Agents cannot see dropdown options
- Cannot generate correct actions to select from dropdown
- Systematic failure on tasks requiring dropdown interaction
**Impact**: Entire class of tasks impossible to complete (evaluation issue, not agent issue)
**Reproducibility**: Easy — 100% failure rate on dropdown tasks
**Mitigation**: Fixed in WebArena Verified with improved UI accessibility

---

### Instance 39: WebArena Overly Restrictive String Matching
**Description**: Benchmark requires exact string matches (e.g., "I am a loyal customer") for success, failing valid responses with slight variations
**Source**: [WebArena Verified Paper](https://openreview.net/pdf?id=94tlGxmqkN) + [Invariant Labs Analysis](https://invariantlabs.ai/blog/what-we-learned-from-analyzing-web-agents)
**Date**: 2024-2025
**Architecture**: All agents
**Category**: Evaluation failures → Success criteria brittleness
**Root Cause**: String matching used as proxy for task completion; requires exact wording rather than semantic equivalence
**Symptoms**:
- Agent completes task correctly but fails evaluation
- 28% of failures due to ambiguous success criteria
- Valid task completions marked as failures
**Impact**: Underestimates agent capabilities (evaluation issue)
**Reproducibility**: High — systematic evaluation problem
**Mitigation**: WebArena Verified replaced string matching in 340 tasks

---

### Instance 40: WebArena Pop-up Handling Failure Without HTML
**Description**: Agents cannot overcome pop-ups unless page HTML is explicitly provided in observation at every step, despite visible (x) button
**Source**: [Invariant Labs Analysis](https://invariantlabs.ai/blog/what-we-learned-from-analyzing-web-agents)
**Date**: 2024-2025
**Architecture**: All web agents
**Category**: Grounding failures → Observation modality limitations
**Root Cause**: Agents rely on specific observation modalities (DOM tree, screenshot); cannot infer pop-up presence without HTML
**Symptoms**:
- Screenshot shows visible pop-up with (x) button
- Agent doesn't recognize need to close pop-up
- Both visual and accessibility tree observations fail
- Only works when page HTML explicitly provided
**Impact**: Systematic failure on pages with pop-ups
**Reproducibility**: High — reliable failure pattern
**Mitigation**: Multi-modal observation with page HTML (cost increase)

---

### Instance 41: WebArena "Lazy" Agent Returns First Observation
**Description**: Agents return response based on first observation, ignoring parts of instructions that require further navigation or action
**Source**: [Invariant Labs Analysis](https://invariantlabs.ai/blog/what-we-learned-from-analyzing-web-agents)
**Date**: 2024-2025
**Architecture**: All web agents
**Category**: Planning failures → Instruction following + Premature completion
**Root Cause**: Agent optimizes for quick completion over full instruction satisfaction; insufficient instruction decomposition
**Symptoms**:
- Agent provides answer after first page visit
- Doesn't complete all instruction requirements
- Appears successful but incomplete
- Can navigate to correct page yet respond from model memory without grounding
**Impact**: Incorrect outputs appearing superficially correct
**Reproducibility**: Medium — depends on task complexity and instruction specificity
**Mitigation**: Explicit instruction decomposition, completion verification

---

### Instance 42: WebArena OpenStreetMap Query Format Sensitivity
**Description**: OpenStreetMap doesn't recognize "A next to B" queries but recognizes "A near B", requiring domain-specific knowledge
**Source**: [WebArena Verified Paper](https://openreview.net/pdf?id=94tlGxmqkN)
**Date**: 2024-2025
**Architecture**: All web agents
**Category**: Grounding failures → Domain-specific API semantics
**Root Cause**: Different APIs have different query syntax requirements not inferable from general knowledge
**Symptoms**:
- Semantically equivalent queries produce different results
- "next to" query returns no results
- "near" query returns correct results
- Requires domain knowledge about OpenStreetMap search function
**Impact**: Task failure from query format mismatches
**Reproducibility**: High — consistent API behavior
**Mitigation**: API-specific documentation, query reformulation strategies

---

## Updated Summary Statistics

**Total Instances Documented**: 42 (25 previous + 17 new)

**By Architecture**:
- ReAct: 11 instances (significantly increased)
- Autonomous loop: 4 instances
- Plan-then-execute: 3 instances
- Multi-agent: 3 instances
- Tree-of-Thought: 2 instances
- All architectures: 19 instances

**By Category** (provisional):
- Tool-use failures: 14 instances (significantly increased)
- Grounding failures: 8 instances (increased)
- Planning failures: 7 instances
- State tracking / Memory: 4 instances
- Error recovery failures: 4 instances (new cluster)
- Evaluation failures: 4 instances
- Self-correction failures: 3 instances
- Security vulnerabilities: 2 instances

**By Source**:
- Production systems (GitHub issues): 12 instances (doubled)
- Benchmark/evaluation studies: 6 instances (new category)
- Research papers: 9 instances
- Framework documentation: 5 instances (new category)
- Previous survey: 10 instances

**Reproducibility**:
- Easy: 23 instances
- High: 10 instances
- Medium: 7 instances
- Hard: 2 instances

---

## Remaining Collection Priorities

To reach 50 instances target, need 8 more. Focus areas:

1. **Reflection/self-correction failures** (3-4 instances)
   - Reflexion degeneration concrete examples
   - Self-evaluation accuracy failures
   - Confirmation bias in self-checking

2. **Context degradation concrete examples** (2-3 instances)
   - Specific long-running task failures with time markers
   - "Lost in the middle" with quantified performance drops

3. **SWE-bench specific failures** (2-3 instances)
   - Code generation errors from Yang et al. paper
   - Incorrect implementations categorization

**Target**: 50 instances by end of next session, enabling open coding phase
