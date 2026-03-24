# Initial Survey: Seed Papers and Foundational Agent Frameworks

**Date**: 2026-03-24
**Scope**: Foundational LLM agent papers (2023-2024), core agent frameworks, and initial failure reports

## Key Papers

| Paper | Year | Venue | Relevance |
|-------|------|-------|-----------|
| Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" | 2023 | ICLR | Foundational ReAct framework - interleaved reasoning and acting |
| Wang et al., "Voyager: An Open-Ended Embodied Agent with Large Language Models" | 2023 | arXiv | Minecraft agent with documented code generation and hallucination failures |
| Xie et al., "AgentBench: Evaluating LLMs as Agents" | 2024 | ICLR | First comprehensive benchmark across 8 environments, identifies key failure patterns |
| Zhou et al., "WebArena: A Realistic Web Environment for Building Autonomous Agents" | 2023 | arXiv | Web agent benchmark - 14.41% success rate, reveals UI and string matching failures |
| Yang et al., "SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering" | 2024 | NeurIPS | GitHub issue solving - 12.47% success rate, categorizes 9 failure types |
| "Where LLM Agents Fail and How They Can Learn from Failures" | 2025 | arXiv | Identifies planning brittleness, tool-use errors, and hallucination cascades as major failure modes |
| Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" | 2025 | arXiv | MAST taxonomy: 14 failure modes in 3 categories from 150 MAS execution traces |
| "Exploring Autonomous Agents: A Closer Look at Why They Fail When Completing Tasks" | 2025 | arXiv | Three-phase failure taxonomy: planning, execution, response generation |
| "DEFT: Deep Research Failure Taxonomy" | 2024 | arXiv | 14 failure modes across reasoning, retrieval, and generation dimensions |

## Foundational Agent Frameworks

### ReAct (2023)
- **Approach**: Interleaves reasoning traces with task-specific actions
- **Key contribution**: Synergy between reasoning (planning, tracking exceptions) and acting (gathering information from environment)
- **Performance**: Outperforms chain-of-thought on HotpotQA and Fever benchmarks
- **Known limitations**: Susceptible to hallucination and error propagation when not grounded in external information
- **Source**: [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) | [Project site](https://react-lm.github.io/)

### AutoGPT (2023-2024)
- **Approach**: Fully autonomous agent with goal decomposition and self-feedback
- **Known failures**:
  - **Infinite loops**: Limited functions + GPT-4 reasoning constraints → looping without progress
  - **Memory failures**: Finite context window → forgetting prior actions, repeating same subtasks
  - **Error propagation**: Relies on own feedback, compounds errors without human correction
  - **Hallucinations**: Presents false information as fact, suggests impossible goals (e.g., "copper sword" in Minecraft)
  - **High costs**: Each step requires GPT-4 call, maxes out tokens frequently
  - **Over-autonomy**: Doesn't ask clarifying questions or allow corrective intervention
- **Evolution**: 2024 updates added loop detection, plugin ecosystem, resource optimization, logging/monitoring
- **Sources**: [autogpt.net](https://autogpt.net/auto-gpt-understanding-its-constraints-and-limitations/) | [MarkTechPost analysis](https://www.marktechpost.com/2023/07/11/breaking-down-autogpt-what-it-is-its-features-limitations-artificial-general-intelligence-agi-and-impact-of-autonomous-agents-on-generative-ai/)

### Voyager (2023)
- **Approach**: Lifelong learning agent in Minecraft with automatic curriculum, skill library, iterative code generation
- **Known failures**:
  - **Model dependency**: GPT-3.5 and open-source LLMs fail at even basic tasks (collecting dirt) - requires GPT-4
  - **Code generation failures**: Faulty code generation despite iterative nudging, gets stuck and needs intervention
  - **Self-verification malfunctions**: Fails to interpret environment feedback correctly (e.g., spider string as evidence of success)
  - **Hallucinations**: Suggests impossible goals (e.g., using cobblestone as fuel, creating non-existent items like "copper sword")
  - **Cost**: GPT-4 dependency makes it expensive ($0.15 more per call than GPT-3.5)
  - **Isolated learning**: Learns without social context, unlike human intelligence
- **Sources**: [arXiv:2305.16291](https://arxiv.org/abs/2305.16291) | [Project site](https://voyager.minedojo.org/)

## Evaluation Benchmarks and Performance

### AgentBench (2024, ICLR)
- **Coverage**: 8 environments (OS, database, knowledge graph, games, web browsing, shopping)
- **Evaluation**: 29 LLMs tested in multi-turn, open-ended generation setting
- **Key finding**: Significant performance gap between API-based commercial LLMs and open-source models ≤70B
- **Main obstacles**: Poor long-term reasoning, decision-making, and instruction following
- **Source**: [arXiv:2308.03688](https://arxiv.org/abs/2308.03688) | [GitHub](https://github.com/THUDM/AgentBench)

### WebArena (2023-2024)
- **Task**: Realistic web navigation and task completion
- **Performance**: Best GPT-4 agents: 14.41% success rate vs. 78.24% human performance
- **Known failures**:
  - **UI accessibility**: Playwright issues prevent dropdown menu selection
  - **Brittle evaluation**: String matching requires exact matches (e.g., "I am a loyal customer"), overly restrictive
  - **Environment sensitivity**: OpenStreetMap query variations ("next to" vs "near") require domain knowledge
  - **False positives**: Permissive string matching and page-level checks inflate success rates by 1.4-5.2%
- **WebArena Verified (2024)**: Fixed 46 instruction-checker misalignments, replaced string matching in 340 tasks, reduced false negatives by ~11%
- **Key insight**: Many agent failures are easy to fix - addressing evaluation issues yielded up to 16% improvement
- **Sources**: [arXiv:2307.13854](https://arxiv.org/abs/2307.13854) | [WebArena site](https://webarena.dev/) | [Invariant Labs analysis](https://invariantlabs.ai/blog/what-we-learned-from-analyzing-web-agents)

### SWE-bench and SWE-agent (2024, NeurIPS)
- **Task**: Automatically fix GitHub issues from 2,294 real-world software engineering problems
- **Performance**: SWE-agent with GPT-4 Turbo solves 12.47% (vs. 3.8% for retrieval-augmented baseline)
- **Function-level debugging**: 87.7% pass@1 success rate
- **Most common failure**: Incorrect implementations (GPT-4o auto-categorized 248 unresolved trajectories into 9 categories)
- **Interface impact**: Without custom file editor interface, performance drops by 7.7 percentage points (10.3% → 2.6%)
- **Cost analysis**: Successful instances median $1.21 and 12 steps vs. unsuccessful $2.52 and 21 steps
- **Evolution**: mini-swe-agent (2024) matches performance with much simpler implementation
- **Sources**: [arXiv:2405.15793](https://arxiv.org/abs/2405.15793) | [GitHub](https://github.com/SWE-agent/SWE-agent)

## Tool Use Errors and API Misuse

### Common Tool Use Failures
1. **Nested API call failures**: GPT-4o achieves only 28% full sequence accuracy on NESTFUL benchmark (nested API sequences)
2. **Semantic errors**: Hallucinated API calls, misuse of method signatures, non-existent file paths, incorrect SQL queries
3. **Fabricated tool execution**: LLM generates fake observation output instead of actually executing tool - continues with made-up results
4. **Error compounding**: Error rate compounds at each step when tools need to be chained together

### Security and Evaluation Concerns
- **API misuse**: Direct model interaction enables threat actors to inject custom system prompts and parameters
- **Risky behaviors**: ToolEmu benchmark (36 high-stakes tools, 144 test cases) focuses on identifying agent misuse with serious consequences
- **Robustness testing**: Inject intentional failures (API errors, null responses) to test recovery - key metric is proportion of failures handled appropriately
- **Validation requirements**: Schema checks, syntax checks, semantic validation before using LLM outputs

### Key Insight
Tool use works well for simple cases, but complex multi-step workflows with chained API calls remain a major challenge as of 2024.

**Sources**: [DEV Community analysis](https://dev.to/terzioglub/why-llm-agents-break-when-you-give-them-tools-and-what-to-do-about-it-f5) | [CrewAI Issue #3154](https://github.com/crewAIInc/crewAI/issues/3154) | [Evidently AI benchmarks](https://www.evidentlyai.com/blog/ai-agent-benchmarks)

## Memory and State Tracking Limitations

### Core Problems
1. **Stateless behavior**: Without memory, LLM systems repeatedly reprocess context, fail to build continuity
2. **Context growth**: Naive prompt injection of past interactions → rapidly growing context windows → increased cost and instability
3. **Context degradation ("context rot")**: As context size grows, models overlook critical information, produce inconsistent outputs
4. **Cost impracticality**: Passing entire conversation history is prohibitively expensive in production

### State Tracking Challenges
- Complex temporal reasoning required
- Retrieval of subtle user preferences buried in noisy, unstructured logs
- Many frameworks lack persistent memory, formal plan validation, recovery mechanisms

### Key Insight
Memory in LLM systems is not a storage problem but a structuring challenge - requires new architectures, not just longer context.

**Sources**: [arXiv:2603.19935 (Memori)](https://arxiv.org/html/2603.19935) | [arXiv:2510.01353 (MEMTRACK)](https://arxiv.org/pdf/2510.01353)

## Error Propagation and Hallucination Cascades

### Cascade Mechanisms
- **Token-level propagation**: LLM treats every generated token as ground truth → single planted detail propagates into unsafe orders/advice
- **Multi-step compounding**: Long chain-of-thought or multi-step instructions → context degradation → cascading errors
- **Citation network spread**: Fabricated citations enter published literature → propagate through citation networks → mislead future researchers

### GPT-4 Hallucination Rates (2024 Studies)
- **General improvement**: GPT-4 significantly reduces hallucinations vs. GPT-3.5, but not fully reliable
- **Medical study findings**: 50-83% hallucination rates in adversarial scenarios (GPT-4o showed fewer but not eliminated)
- **Enterprise impact**: Small hallucination rates become large-scale integrity problems - errors propagate across systems, decisions, and trust

**Sources**: [Nature Communications Medicine study](https://www.nature.com/articles/s43856-025-01021-3) | [OpenAI hallucination analysis](https://openai.com/index/why-language-models-hallucinate/) | [Balbix analysis](https://www.balbix.com/blog/hallucinations-agentic-hype/)

## Existing Failure Taxonomies

### MAST: Multi-Agent System Failure Taxonomy (2025)
- **Method**: Grounded theory analysis of 150+ MAS execution traces (avg 15,000+ lines each)
- **Categories**: 14 distinct failure modes in 3 clusters:
  1. System design issues
  2. Inter-agent misalignment
  3. Task verification
- **Failure rates**: 41-86.7% across 7 SOTA open-source MAS
- **Source**: [arXiv:2503.13657](https://arxiv.org/abs/2503.13657)

### Three-Phase Failure Taxonomy (2025)
- **Phases**:
  1. Task planning
  2. Task execution
  3. Response generation
- **Evaluation**: 3 open-source frameworks × 2 LLM backbones
- **Performance**: ~50% task completion rate
- **Source**: [arXiv:2508.13143](https://arxiv.org/html/2508.13143v1)

### DEFT: Deep Research Failure Taxonomy (2024)
- **Scope**: Specialized for deep research agents
- **Structure**: 14 fine-grained failure modes across 3 dimensions:
  1. Reasoning
  2. Retrieval
  3. Generation
- **Source**: [arXiv:2512.01948](https://arxiv.org/pdf/2512.01948)

### System-Level Reliability Taxonomy (2024)
- **Coverage**: 15 unique failure patterns including:
  - Hallucinations and multi-step planning collapse
  - Tool-use faults
  - Version drift in multi-stage retrieval pipelines
  - Agent-based orchestration failures
- **Source**: [arXiv:2511.19933](https://arxiv.org/pdf/2511.19933)

## Summary

### Consensus Patterns
Across multiple taxonomies and benchmarks, several failure modes recur:
1. **Planning failures**: Multi-step planning collapse, goal decomposition errors, plan-repair failures
2. **Tool-use errors**: API misuse, hallucinated tool calls, fabricated execution results, nested call failures
3. **State tracking failures**: Memory loss, context degradation, inability to maintain task state over time
4. **Error propagation**: Single errors cascade through multi-turn interactions, compounding over time
5. **Hallucinations**: Impossible goals, fabricated information, false confidence in incorrect outputs
6. **Evaluation brittleness**: Many reported "failures" are actually evaluation issues (string matching, UI problems)

### Performance Gap
Even best-in-class agents (GPT-4-based) achieve only 12-14% success rates on realistic benchmarks (WebArena, SWE-bench) compared to 78%+ human performance. This ~60 percentage point gap suggests fundamental limitations in current architectures.

### Open Questions
1. Are these failures primarily architectural (fixable with better agent design) or model-level (requiring better base LLMs)?
2. What is the distribution of failures across different agent architectures (ReAct vs. plan-then-execute vs. tree-of-thought)?
3. Which failure modes are most amenable to mitigation strategies (prompting, architecture changes, external tools)?
4. How do failure rates scale with task complexity and time horizon?

## Implications for This Project

### Methodology Validation
The existence of multiple emerging failure taxonomies (MAST, DEFT, three-phase) validates our grounded theory approach. However, these taxonomies focus on:
- Multi-agent systems (MAST) - we're focusing on single-agent
- Specific domains (DEFT for research agents) - we want cross-domain
- High-level categories - we need fine-grained, actionable taxonomy

**Opportunity**: Build the first comprehensive, hierarchical, single-agent failure taxonomy grounded in both literature and controlled experiments across multiple architectures.

### Coverage Gaps Identified
Current taxonomies lack:
1. Systematic mapping of failures to underlying LLM limitations
2. Quantitative analysis of failure mode frequency across architectures
3. Clear boundary criteria and inter-rater reliability analysis
4. Controlled reproduction of failures across multiple frameworks
5. Connection to fundamental reasoning limitations (link to reasoning-gaps project)

### Concurrent Work Risk Assessment
**Risk level**: MODERATE
- Multiple taxonomies published 2024-2025 shows active research area
- However, no comprehensive single-agent taxonomy covering multiple architectures with controlled experiments
- Our hierarchical approach with architecture mapping and LLM limitation connection distinguishes us
- Need to monitor arXiv closely for similar work through end of 2026

### Next Steps
1. Deep-read all taxonomy papers (MAST, DEFT, three-phase, system-level) to extract detailed failure definitions
2. Collect failure instances from GitHub issues for AutoGPT, SWE-agent, LangChain agents
3. Fetch and analyze full papers for ReAct, Voyager, AgentBench, WebArena, SWE-agent
4. Search for plan-then-execute and tree-of-thought agent failures (architecture diversity)
5. Begin structured failure instance template design
