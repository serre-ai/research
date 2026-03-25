# Recent Taxonomies and Concurrent Work (2025-2026)

**Date**: 2026-03-25
**Scope**: Recent agent failure taxonomies, concurrent work analysis, and critical new findings from 2025-2026 literature

---

## Critical Concurrent Taxonomies (2025-2026)

### 1. Characterizing Faults in Agentic AI (2026) — NEW MAJOR COMPETITOR

**Paper**: "Characterizing Faults in Agentic AI: A Taxonomy of Types, Symptoms, and Root Causes"
**Source**: [arXiv:2603.06847](https://arxiv.org/html/2603.06847v1)
**Date**: March 2026 (2 weeks ago!)

**Scope**: Comprehensive analysis of real-world faults across agentic AI systems

**Taxonomy Structure**:
- **37 fault categories** grouped into **13 major categories**
- 5 high-level dimensions corresponding to core agent capabilities required for autonomy
- Analysis of **385 real-world faults** from production systems

**Key Finding**: Faults in agentic AI systems differ fundamentally from those in traditional software systems

**Impact on Our Project**:
- **CRITICAL CONCURRENT WORK** — most comprehensive single-agent taxonomy published
- Very recent (March 2026), directly competing with our scope
- Advantage: Based on real-world faults (385 instances), not just literature
- Our differentiation: Architecture comparison, controlled reproduction, LLM limitation mapping
- **URGENT**: Need to deep-read this paper immediately to understand overlap and differentiation

**Risk Assessment**: HIGH — direct competition, very recent, comprehensive scope

---

### 2. AgentErrorTaxonomy (September 2025)

**Paper**: "Where LLM Agents Fail and How They Can Learn From Failures"
**Source**: [arXiv:2509.25370](https://arxiv.org/abs/2509.25370)
**Date**: September 2025

**Scope**: Modular classification of failure modes with learning mechanisms

**Taxonomy Structure**:
- 5 modules: Memory, Reflection, Planning, Action, System-level operations
- Designed as **causal lens** for understanding how failures originate, propagate, and interact
- Includes **AgentErrorBench**: first dataset of systematically annotated failure trajectories from ALFWorld, GAIA, and WebShop

**Key Contributions**:
- Error propagation identified as primary bottleneck — single root-cause failure cascades into successive errors
- Memory and reflection errors are most common sources of propagation
- Early detection and correction are critical — cascades are difficult to reverse once started
- Mechanisms that strengthen memory retrieval and reflection can substantially reduce propagation risk

**Learning Focus**: Distinguishes between failure taxonomies (what goes wrong) and remediation strategies (how to fix it)

**Impact on Our Project**:
- Modular structure aligns with our hierarchical approach
- Strong focus on error propagation — validates our "Error Recovery Gap" pattern
- Dataset of annotated failures is valuable resource
- Our differentiation: Architecture comparison, production vs. benchmark failures, finer-grained categories

**Risk Assessment**: MODERATE — complementary focus on learning from failures, but overlaps in taxonomy

---

### 3. Three-Phase Failure Taxonomy (August 2025) — Already Documented

**Paper**: "Exploring Autonomous Agents: A Closer Look at Why They Fail When Completing Tasks"
**Source**: [arXiv:2508.13143](https://arxiv.org/html/2508.13143v1)
**Date**: August 2025

Already covered in previous literature notes. Three-tier taxonomy aligned with task phases.

---

### 4. MAST: Multi-Agent System Failure Taxonomy (March 2025) — Already Documented

**Paper**: "Why Do Multi-Agent LLM Systems Fail?"
**Source**: [arXiv:2503.13657](https://arxiv.org/abs/2503.13657)
**Date**: March 2025

Already covered in previous notes. 14 failure modes in 3 categories, focused on multi-agent systems.

---

### 5. Agentic Artificial Intelligence Survey (January 2026)

**Paper**: "Agentic Artificial Intelligence (AI): Architectures, Taxonomies, and Evaluation of Large Language Model Agents"
**Source**: [arXiv:2601.12560](https://arxiv.org/html/2601.12560v1)
**Date**: January 2026

**Scope**: Comprehensive survey of agent architectures and taxonomies (not failure-specific)

**Relevance**: Provides architectural classification that may inform our architecture-failure correlation analysis

---

### 6. AgentRx: Diagnosing Agent Failures (February 2026)

**Paper**: "AgentRx: Diagnosing AI Agent Failures from Execution Trajectories"
**Source**: [arXiv:2602.02475](https://arxiv.org/pdf/2602.02475)
**Date**: February 2026

**Scope**: Diagnostic tool for identifying failure causes from execution traces

**Relevance**: Tool-focused rather than taxonomy-focused, but may contain failure categorization

**Note**: Need to review for potential failure categorization scheme

---

## Error Propagation and Cascading Failures (2025-2026)

### From Spark to Fire: Error Cascades in Multi-Agent Systems (March 2026)

**Paper**: "From Spark to Fire: Modeling and Mitigating Error Cascades in LLM-Based Multi-Agent Collaboration"
**Source**: [arXiv:2603.04474](https://arxiv.org/abs/2603.04474v1)
**Date**: March 2026

**Key Findings**:

1. **Cascade Amplification**: In multi-agent systems, collaborative mechanisms cause minor inaccuracies to gradually solidify into system-level false consensus through iteration, with errors propagating and amplifying through message dependencies

2. **Three Vulnerability Classes**:
   - **Cascade amplification**: Errors grow through recursive context reuse
   - **Topological sensitivity**: Network structure affects error spread
   - **Consensus inertia**: Once errors reach consensus, extremely difficult to correct

3. **Structural Problem**: Under recursive context reuse, collaborative structures frequently exhibit cascading amplification of errors

**Implications**:
- Error cascades are not just linear propagation — they amplify through feedback loops
- Multi-agent systems are particularly vulnerable (validates MAST findings)
- Our focus on single-agent avoids multi-agent cascade complexity, but single agents still have internal cascades

---

### OWASP ASI08: Cascading Failures in Agentic AI (2025-2026)

**Source**: [OWASP Security Guide 2026](https://adversa.ai/blog/cascading-failures-in-agentic-ai-complete-owasp-asi08-security-guide-2026/)

**Key Insight**: Unlike traditional software failures that remain localized, agentic AI cascades:
- Propagate across autonomous agents
- Amplify through feedback loops
- Compound into system-wide catastrophes
- **Persist in memory**: Errors written to long-term agentic AI memory, vector stores, or knowledge bases continue influencing future agent reasoning even after the original source is corrected

**Security Perspective**: Cascading failures are now recognized as a top security vulnerability (OWASP ASI08)

---

## Tool Hallucination and Fabrication (2025)

### The Reasoning Trap: Enhanced Reasoning Amplifies Tool Hallucination

**Paper**: "The Reasoning Trap: How Enhancing LLM Reasoning Amplifies Tool Hallucination"
**Source**: [arXiv:2510.22977](https://arxiv.org/html/2510.22977v1) | [OpenReview](https://openreview.net/forum?id=vHKUXkrpVs)
**Date**: October 2025

**Critical Paradox Discovered**:
Stronger reasoning often coincides with increased hallucination. Research shows that progressively enhancing reasoning through reinforcement learning increases tool hallucination proportionally with task performance gains.

**Key Findings**:

1. **Reasoning-Hallucination Trade-off**:
   - As models get better at step-by-step reasoning, they hallucinate tools more
   - Effect transcends overfitting — training on non-tool tasks (e.g., mathematics) still amplifies subsequent tool hallucination
   - Method-agnostic: appears with supervised fine-tuning AND inference-time prompting (CoT)

2. **Root Cause**:
   - Execution hallucinations arise when agent's internal representation of tool behaviors diverges from actual functionality
   - Tool Documentation deficiencies: redundant info, incomplete/inaccurate descriptions, lack of standardization
   - Tool-calling hallucinations increase with tool count → function selection errors, calling non-existent tools

3. **Mitigation Challenges**:
   - Fundamental reliability–capability trade-off: reducing hallucination consistently degrades utility
   - Prompt engineering offers only superficial relief
   - Preference optimization (DPO) reduces hallucinations at expense of tool-use proficiency

4. **Catastrophic Nature**:
   - When agent hallucinates during execution, it's catastrophic — fabricating API parameters, inventing success confirmations after failures, executing actions based on false beliefs

**Implication for Taxonomy**:
- Tool hallucination is NOT just a tool-use error — it's deeply connected to reasoning capabilities
- Cannot be fully mitigated without sacrificing capability
- Distinguishes between:
  - **Selection hallucination**: Calling wrong or non-existent tools
  - **Execution hallucination**: Fabricating parameters or results
  - **Verification hallucination**: Falsely confirming success

---

### Survey: LLM-based Agents Suffer from Hallucinations

**Paper**: "LLM-based Agents Suffer from Hallucinations: A Survey of Taxonomy, Methods, and Directions"
**Source**: [arXiv:2509.18970](https://arxiv.org/html/2509.18970v1)
**Date**: September 2025

**Key Insight**: In LLM-based agents, hallucinations are not "linguistic errors", but rather a broad category of fabricated or misjudged "human-like behaviors" that may occur at any stage of the agent's pipeline

**Agent-Specific Hallucination Types**:
- Planning hallucinations: Impossible goals, non-existent constraints
- Tool hallucinations: Fabricated tools, incorrect parameters
- Observation hallucinations: Misinterpreting environment feedback
- Memory hallucinations: False recollections, fabricated history

**Fundamental Challenge**: "You cannot eliminate hallucinations — they're inherent to how LLMs work"

---

## Plan-Then-Execute Architecture Failures (2025-2026)

### Hierarchical Planning and Evaluation Framework

**Paper**: "Why Do LLM-based Web Agents Fail? A Hierarchical Planning Perspective"
**Source**: [arXiv:2603.14248](https://arxiv.org/html/2603.14248)
**Date**: March 2026

**Key Findings**:

1. **Outcome-based evaluation is insufficient**:
   - Aggregate success rates obscure failure sources by conflating planning errors, execution mistakes, and ineffective feedback use
   - Hierarchical evaluation frameworks make these failure modes explicit

2. **Process-based evaluation across phases**:
   - Planning errors
   - Execution mistakes
   - Replanning effectiveness
   - Enables more precise diagnosis and targeted comparison across architectures

3. **Plan-Then-Execute Weaknesses**:
   - Initial latency: Must call powerful planner LLM and wait for entire multi-step plan before first action
   - Plan optimality: Cannot adapt to unexpected conditions discovered during execution
   - Replanning costs: When something goes wrong, must regenerate entire plan
   - Failure handling: If root cause not identified correctly, replanning may repeat same mistake

**Validation**: Confirms our preliminary findings on plan-then-execute trade-offs (efficiency vs. flexibility)

---

### Resilient Plan-Then-Execute Architecture Design

**Paper**: "Architecting Resilient LLM Agents: A Guide to Secure Plan-..."
**Source**: [arXiv:2509.08646](https://arxiv.org/pdf/2509.08646)
**Date**: September 2025

**Advantages of Plan-Then-Execute**:
- Predictability, security, and reasoning quality for complex tasks
- Mitigates common single-step failures: repetitive loops, suboptimal paths, losing focus

**Documented Failure Modes**:
1. **False completion reporting**: Agents report tasks complete when they are not (February 2026 study)
2. **False system states**: Agents claim to have deleted data or ceased communication when they haven't — creates false states accepted by downstream decision chains
3. **Unstable behaviors**: Agents with autonomy, memory, and tool access exhibit hallucinated task outcomes, misunderstand authority, break under social pressure
4. **Unpredictable multi-agent interactions**: AI agents can be overly trusting and easily misled by each other — AI-to-AI communication as potential backdoor

---

## Tree-of-Thought Limitations (2025)

**Sources**: Multiple 2025 analyses and implementations

**Documented Failure Modes**:

1. **High Time and Token Costs**:
   - Tree-of-thought approaches suffer from high time and token cost
   - Resource-intensive without proportional success improvement

2. **Linear Reasoning Failures**:
   - While ReAct excels in sequential tasks, it remains linear
   - ToT helps with problems requiring strategic planning or combinatorial search
   - But implementation quality heavily determines effectiveness

3. **Prompting Technique Breakdown**:
   - Prompting techniques have significant limitations in real-world agentic tasks
   - "Tricks that made models appear to plan, without fundamentally changing how models processed information"
   - Break down when faced with dynamic environments, unexpected tool responses, complex state management

4. **LLM Reasoning Failures on Constraint Satisfaction**:
   - LLMs systematically hallucinate non-existent problem features (spurious edges in graph coloring)
   - Causes cascading logical failures even when all input data available
   - Hallucination rates scale linearly with problem complexity
   - **Accentuated by chain-of-thought prompting** — not mitigated by it

5. **Prompt Sensitivity**:
   - Accuracy can drop precipitously (up to -54%) or increase under prompt perturbations
   - Narrative reframing, misleading constraint injection, example reordering all cause instability
   - Not mitigated by model size or parameter count
   - Directionality of performance changes is unpredictable

**Sources**: [Prompt Engineering Guide](https://www.promptingguide.ai/techniques/tot) | [IBM ToT explainer](https://www.ibm.com/think/topics/tree-of-thoughts) | [CoForge ReAct vs ToT](https://www.coforge.com/what-we-know/blog/react-tree-of-thought-and-beyond-the-reasoning-frameworks-behind-autonomous-ai-agents) | [Aya Data AI reasoning](https://www.ayadata.ai/how-ai-agents-actually-think-planning-reasoning-and-why-it-matters-for-enterprise-ai/)

---

## Production Failures from GitHub Issues

### AutoGPT Issues (2024-2025)

**Source**: [AutoGPT GitHub Issues](https://github.com/Significant-Gravitas/AutoGPT/issues)

**Recent Failures** (December 2025):
- Builder and platform backend bugs
- HTML conversion failures
- 107K+ errors from unused Otto Server Action
- Redis event bus connection failures (fixed in recent releases)

**Persistent Failure Modes** (2025):
- **Looping and dead ends** when tasks are ambiguous
- **Hallucinations** especially with web data
- **Fragile execution**: External site blockers and flaky scrapers break flows
- Community reports highlight looping and failure risks remain relevant for 2025 users

**Project Status**: "No longer leading the pack but playing catch-up" — framework has some life but ongoing reliability challenges

**Source**: [AutoGPT Review 2025](https://sider.ai/blog/ai-tools/autogpt-review-is-autonomous-ai-ready-for-real-work-in-2025) | [AutoGPT Releases](https://github.com/Significant-Gravitas/AutoGPT/releases)

---

### CrewAI Issues (2024-2025)

**Source**: [CrewAI GitHub Issues](https://github.com/crewAIInc/crewAI/issues)

**High-Severity Bugs** (November 2025):
- Unsupported `response_format` with Azure OpenAI when memory enabled
- LLM call failures: "Azure API call failed: Unsupported `response_format`"
- High-level abstraction makes failures hard to diagnose — "black box" feel when troubleshooting

**Bug Fixes in Recent Releases** (October 2025, v1.1.0):
- Tool usage logic bug: Early-caching results even when errors occurred, preventing tools from being used again
- Explicit exceptions now raised when flows fail
- Fixes for OpenAI tool call stream finalization and event handling

**Critical Security Issue**:
- When CrewAI platform encountered provisioning failures, it did not securely handle exceptions
- Result: Exposure of CrewAI-owned internal GitHub token to users
- Demonstrates failure to handle exceptions can create security vulnerabilities

**Source**: [CrewAI Issue #3986](https://github.com/crewAIInc/crewAI/issues/3986) | [CrewAI v1.1.0 Release](https://community.crewai.com/t/new-release-crewai-1-1-0-is-out/7142) | [Noma Security Analysis](https://noma.security/blog/uncrew-the-risk-behind-a-leaked-internal-github-token-at-crewai/)

---

## Concurrent Work Risk Assessment (Updated 2026-03-25)

### Risk Level: **HIGH** (elevated from MODERATE)

**Critical New Development**:
"Characterizing Faults in Agentic AI" (March 2026) represents direct competition with comprehensive scope (37 categories, 385 real-world faults, 5 dimensions). Published 2 weeks ago.

### Competing Papers (2025-2026):

| Paper | Date | Scope | Categories | Data | Overlap |
|-------|------|-------|-----------|------|---------|
| Characterizing Faults in Agentic AI | Mar 2026 | Single + Multi | 37 in 13 groups | 385 real faults | **HIGH** |
| AgentErrorTaxonomy | Sep 2025 | Single agent | 5 modules | 3 benchmarks | MODERATE |
| MAST | Mar 2025 | Multi-agent only | 14 in 3 clusters | 150 traces | LOW |
| Three-phase | Aug 2025 | General | 3 phases | 3 frameworks | LOW |
| Reasoning Trap | Oct 2025 | Tool hallucination | Subtypes | Experiments | LOW |

### Our Differentiation Strategy (Revised):

Given the March 2026 comprehensive fault taxonomy, we must clearly differentiate:

1. **Architecture-Failure Correlation** (H3):
   - Quantitative analysis of how failure distribution changes with architecture
   - Controlled experiments across ReAct, Plan-then-execute, ToT, Reflection
   - No existing work provides this cross-architecture comparison

2. **LLM Limitation Mapping**:
   - Connect agent failures to fundamental LLM reasoning limitations
   - Bridge to reasoning-gaps project
   - Distinguish architectural failures (fixable) from fundamental limitations (not fixable)

3. **Controlled Reproduction**:
   - Reproduce key failures across multiple frameworks
   - Validate that failures are reliably reproducible
   - Test mitigation strategies empirically

4. **Production vs. Benchmark**:
   - Include production failures (GitHub issues, deployment reports)
   - Existing taxonomies focus on benchmark failures
   - Real-world failures may differ from controlled benchmark failures

5. **Hierarchical Structure with Boundary Criteria**:
   - Clear definitions for each category
   - Explicit boundary criteria for ambiguous cases
   - Inter-rater reliability validation

### Action Items:

1. **URGENT**: Deep-read "Characterizing Faults in Agentic AI" (2026) to understand detailed overlap
2. Review AgentErrorTaxonomy methodology for comparison
3. Emphasize architecture comparison and LLM limitation mapping in paper framing
4. Consider reaching out to authors for collaboration vs. differentiation discussion
5. Monitor arXiv weekly for additional concurrent work

### Timeline Implications:

- ACL 2027 submission: February 2027 (11 months)
- Need to complete taxonomy and experiments before competing papers further saturate space
- Accelerate controlled experiments to establish empirical differentiation
- Consider pre-print publication to establish priority once core results are ready

---

## Summary: Key Takeaways

### Major Findings:

1. **Reasoning-Hallucination Paradox**: Better reasoning → more tool hallucination (cannot be fully fixed)
2. **Error Cascades**: Not just linear propagation — amplify through feedback loops, persist in memory
3. **Architecture-Specific Patterns**: Evidence for H3 accumulating (plan-then-execute replanning, ToT resource costs, ReAct tool errors)
4. **Production Reliability**: Persistent issues in AutoGPT and CrewAI show gap between theory and practice
5. **False Completion**: Agents reporting success when they failed creates dangerous downstream effects

### Implications for Taxonomy Structure:

Based on recent findings, provisional taxonomy refinements:

1. **Error Recovery** → Should be top-level category (not sub-category)
2. **Tool Hallucination** → Distinguish selection vs. execution vs. verification hallucinations
3. **Cascading Failures** → Separate category with amplification mechanisms
4. **False Verification** → Agents claiming success/completion when wrong
5. **Reasoning-Driven Failures** → CoT/ToT can amplify rather than fix certain failures

### Next Steps:

1. Deep-read "Characterizing Faults in Agentic AI" (March 2026) — URGENT
2. Deep-read "AgentErrorTaxonomy" (September 2025)
3. Deep-read "Reasoning Trap" (October 2025) for tool hallucination details
4. Continue failure instance collection with focus on architecture-specific examples
5. Begin controlled experiments to establish differentiation through empirical data

---

**Papers Surveyed This Session**: 10+ new papers
**New Failure Instances Identified**: 15+ from AutoGPT, CrewAI, and recent research
**Concurrent Work Risk**: Elevated to HIGH due to March 2026 comprehensive taxonomy
