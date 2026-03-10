# A Taxonomy of Failure Modes in LLM-Based Autonomous Agents

## Title
A Taxonomy of Failure Modes in LLM-Based Autonomous Agents

## Target Venue
ACL 2027 (February 2027 submission)

## Research Area
Agent Architectures × LLM Capabilities

## Motivation
LLM-based autonomous agents (ReAct, AutoGPT, Claude Code, Voyager, etc.) are deployed in increasingly complex settings, yet they fail in systematic ways that are poorly documented and understood. Individual failure reports exist in papers, blog posts, and public demonstrations, but no comprehensive taxonomy connects these failures to underlying causes or predicts when agents will fail. Without such a taxonomy, practitioners cannot design robust agents, and researchers cannot prioritize improvements. This survey fills that gap.

## Research Goals

### Primary
1. **Collect and categorize** 100+ documented agent failures from published work, public demonstrations, and controlled experiments into a rigorous, hierarchical taxonomy.
2. **Identify root causes** by mapping each failure category to underlying LLM limitations (planning capacity, state tracking, tool-use grounding, feedback loop dynamics).
3. **Characterize how failure modes shift** across agent architectures (ReAct vs. plan-then-execute vs. tree-of-thought vs. multi-agent), providing actionable guidance for architecture selection.

### Secondary
4. Propose mitigation strategies for each failure category, distinguishing between prompting fixes, architectural changes, and fundamental limitations.
5. Connect the agent failure taxonomy to the reasoning gap framework from the reasoning-gaps project, showing how abstract reasoning limitations manifest in agentic settings.

## Hypotheses
- **H1**: Agent failures cluster into 5–7 distinct categories that are largely independent of the underlying LLM, suggesting the failures are architectural rather than model-specific.
- **H2**: Most agent failures (>60%) stem from planning and state tracking limitations rather than knowledge gaps or tool-use errors.
- **H3**: Failure mode frequency shifts predictably with agent architecture choices — e.g., ReAct agents exhibit more planning failures while plan-then-execute agents exhibit more plan-repair failures.

## Methodology
1. **Literature survey**: Systematic collection of agent failure reports from papers (2023–2026), blog posts, GitHub issues, and public demonstrations. Target: 100+ distinct failure instances.
2. **Taxonomy development**: Iterative coding of failures using grounded theory methodology. Start with open coding, refine through axial coding, produce hierarchical taxonomy.
3. **Controlled experiments**: Reproduce key failure types in controlled settings across 3+ agent frameworks to validate taxonomy categories and measure frequency.
4. **Architecture analysis**: Map each taxonomy category to specific architectural decisions, quantifying how architecture choice affects failure distribution.
5. **Mitigation evaluation**: For each category, evaluate existing and novel mitigation strategies, classifying them as effective, partially effective, or ineffective.

## Expected Contributions
- A hierarchical taxonomy of LLM agent failure modes with clear definitions and examples
- Quantitative analysis of failure mode frequency across architectures
- Architecture selection guidance based on failure mode profiles
- Connection between agent failures and fundamental LLM reasoning limitations
- A curated dataset of 100+ labeled agent failure instances for community use

## Timeline
- **Phase 1** (Weeks 1–3): Literature survey and failure collection — gather 100+ failure instances
- **Phase 2** (Weeks 4–5): Taxonomy development — iterative coding and refinement
- **Phase 3** (Weeks 6–7): Controlled experiments — reproduce and validate key failure types
- **Phase 4** (Weeks 8–9): Paper writing — draft all sections, create figures

## Resource Requirements
- **Compute**: ~20K API calls for controlled agent experiments across frameworks. Estimated $200–300.
- **Data**: Publicly available papers, GitHub repositories, blog posts. No special access needed.
- **External tools**: Agent frameworks (LangChain, AutoGPT, CrewAI) for controlled experiments.
- **Estimated cost**: $300/month for 2 months.

## Risk Factors
- **Taxonomy subjectivity**: Risk that categories are not cleanly separable. Mitigate with inter-rater reliability testing and clear boundary criteria.
- **Scope creep**: 100+ failures across many frameworks could balloon. Mitigate by fixing the collection period and using sampling for less-studied frameworks.
- **Prior work overlap**: Partial taxonomies exist in individual papers. Mitigate by being comprehensive and explicitly building on (not ignoring) prior partial categorizations.
