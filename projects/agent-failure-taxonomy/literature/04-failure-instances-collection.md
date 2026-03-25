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
