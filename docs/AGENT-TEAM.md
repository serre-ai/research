# Agent Team Architecture

This document defines the agent team structure, coordination protocols, and operational standards for the Deepwork research platform. Each agent is a specialized Claude Code session configured with a specific system prompt, tool set, and behavioral profile.

## Agent Roles

### Core Research Agents

#### Researcher

Primary agent during the **research phase**. Conducts literature review, identifies gaps in existing work, designs experiments, and performs data analysis. The Researcher produces the raw intellectual material that all downstream agents depend on.

- **Scope**: Literature search and synthesis, gap identification, hypothesis formation, experiment design, data analysis and interpretation.
- **Key outputs**: Literature notes, gap analyses, experiment designs, analysis reports, knowledge graph claims.
- **Quality bar**: Every literature review covers a minimum of 20 papers. Every gap claim is supported by explicit evidence of absence in the surveyed work.

#### Writer

Primary agent during the **drafting** and **revision** phases. Transforms research artifacts into publication-ready papers. The Writer owns the paper structure, prose quality, and LaTeX formatting.

- **Scope**: Paper drafting (all sections), revision in response to reviews, LaTeX formatting, figure descriptions, notation management.
- **Key outputs**: LaTeX source files, figure specifications, notation tables.
- **Quality bar**: Every draft must be structurally complete (no placeholder sections) before handoff to Reviewer. Prose must be clear enough that a graduate student in the field can follow every argument.

#### Experimenter

Designs and runs empirical evaluations. Works closely with the closed-loop experiment system to test hypotheses autonomously.

- **Scope**: Benchmark design, eval script development, experiment execution, result analysis, statistical testing.
- **Key outputs**: Experiment specs, eval scripts, result datasets, analysis reports, knowledge graph findings.
- **Quality bar**: Every experiment has a pre-registered hypothesis, defined success criteria, and proper statistical analysis (effect sizes, confidence intervals, not just p-values).

#### Theorist

Develops formal frameworks, proofs, and theoretical foundations. Uses extended thinking for complex mathematical reasoning.

- **Scope**: Formal definitions, theorem statements and proofs, complexity-theoretic analysis, framework development.
- **Key outputs**: Formal frameworks, proofs, theoretical notes, knowledge graph definitions and proof claims.
- **Quality bar**: Every proof is rigorous enough to withstand scrutiny from a theory reviewer. No hand-waving.

### Quality Agents

#### Reviewer

Quality gate agent used at **phase transitions** and **before submission**. Provides honest, constructive, venue-calibrated review.

- **Scope**: Critical evaluation of papers, scoring against venue standards, identifying logical gaps, verifying experimental claims, checking completeness.
- **Key outputs**: Structured reviews with scores, severity-tagged weaknesses, specific improvement suggestions.
- **Quality bar**: Reviews must be at least as thorough as a conscientious NeurIPS/ICML reviewer.

#### Critic

Adversarial review agent. Harder than Reviewer — actively tries to break arguments. Produces ACCEPT/REVISE/REJECT verdicts that drive session chaining.

- **Scope**: Adversarial analysis, finding hidden assumptions, stress-testing claims, challenging methodology.
- **Key outputs**: Verdicts (ACCEPT/REVISE/REJECT) with detailed reasoning.
- **Quality bar**: If the Critic accepts, the paper should survive real peer review.

#### Editor

Consistency and polish agent used during **revision** and **before submission**.

- **Scope**: Notation standardization, citation completeness, cross-reference verification, style enforcement, accessibility checks.
- **Key outputs**: Edit reports with specific, located, actionable fixes.
- **Quality bar**: After an Editor pass, the paper should have zero broken references, zero undefined notation, and zero uncited claims.

### Intelligence Agents

#### Planner (new)

The **Research Planner** replaces phase-based scheduling. Runs at the start of each daemon cycle to produce specific, high-value session briefs.

- **Scope**: Knowledge graph analysis, gap identification, contradiction detection, risk assessment, session brief composition, post-session evaluation.
- **Key outputs**: `SessionBrief` objects with specific objectives, context composition, model selection, and deliverables.
- **Quality bar**: Every brief must specify a concrete intellectual objective — not "run a writer" but "resolve the B2 anomaly by testing revised token budget formula."
- **See**: [Research Planner Roadmap](roadmaps/research-planner.md)

#### Verifier (new)

Ensures every paper claim is traceable to supporting evidence. Runs automatically after paper edits.

- **Scope**: Claim extraction from LaTeX, evidence linking (data, figures, proofs, citations), consistency checking, gap flagging.
- **Key outputs**: Verification reports with claim-evidence links and status (verified/stale/missing/contradicted).
- **Quality bar**: Every numerical claim in the paper has a verified evidence link. Zero stale claims at submission time.
- **See**: [Verification Layer Roadmap](roadmaps/verification-layer.md)

### Strategic Agents

#### Strategist

Portfolio management and cross-project coordination agent. Runs monthly or on-demand.

- **Scope**: Portfolio health assessment, cross-project insight transfer, idea generation, venue targeting, budget oversight.
- **Key outputs**: Monthly portfolio reports, cross-project insights, project recommendations.
- **Quality bar**: Recommendations must be justified with specific evidence from project status files and knowledge graph.
- **See**: [Cross-Project Intelligence Roadmap](roadmaps/cross-project-intelligence.md)

#### Scout

Continuous literature monitoring agent. Feeds the literature intelligence system.

- **Scope**: arXiv monitoring, Semantic Scholar queries, citation tracking, relevance assessment, literature alerts.
- **Key outputs**: Literature alerts with relevance scores and implications for active claims.
- **Quality bar**: 80%+ of alerts rated as genuinely relevant. Concurrent work detected before submission.
- **See**: [Literature Intelligence Roadmap](roadmaps/literature-intelligence.md)

#### Engineer

Platform maintenance and infrastructure agent.

- **Scope**: Bug fixes, feature implementation, deployment, monitoring, database migrations.
- **Key outputs**: Code changes, infrastructure updates, backlog ticket resolution.
- **Quality bar**: All changes pass TypeScript compilation and don't break existing functionality.

---

## Agent Assignment by Phase

| Phase | Primary Agent | Secondary Agents | Intelligence Layer |
|-------|--------------|-----------------|-------------------|
| **Research** | Researcher | Theorist, Scout | Planner composes briefs; Knowledge graph captures claims |
| **Empirical Evaluation** | Experimenter | Researcher | Closed-loop experiment system; Planner identifies hypotheses to test |
| **Analysis** | Experimenter | Writer | Knowledge graph updated with findings; Verifier links data to claims |
| **Drafting** | Writer | Researcher (on call) | Planner selects sections; Verifier runs after each edit |
| **Revision** | Writer | Critic, Reviewer | Review simulation before submission; Verifier ensures evidence links |
| **Final** | Editor | Reviewer, Verifier | Full verification pass; Review simulation for acceptance prediction |

---

## Adaptive Session Composition

The Planner doesn't just pick an agent — it composes a full session configuration. See [Adaptive Sessions Roadmap](roadmaps/adaptive-sessions.md).

| Task Type | Model | Thinking | Turns | Context Strategy |
|-----------|-------|----------|-------|-----------------|
| Deep theoretical proof | Opus 4.6 | Extended | 100 | Narrow: proof + prerequisites |
| Literature sweep | Haiku 4.5 | Standard | 30 | Broad: project state + queries |
| Data analysis | Sonnet 4.6 | Standard | 40 | Medium: data + claims |
| Paper writing (new section) | Opus 4.6 | Extended | 80 | Medium: section + knowledge subgraph |
| Paper editing (polish) | Sonnet 4.6 | Standard | 30 | Narrow: section being edited |
| Experiment design | Sonnet 4.6 | Extended | 40 | Medium: hypothesis + benchmarks |
| Strategic planning | Opus 4.6 | Extended | 20 | Broad: all projects + budget |
| Quick fix | Haiku 4.5 | Standard | 5 | Narrow: specific file |
| Review response | Opus 4.6 | Extended | 60 | Full: paper + reviews + knowledge graph |
| LaTeX debugging | Haiku 4.5 | Standard | 10 | Narrow: build errors only |

### Context Composition

Each session's prompt is assembled from layers, with the Planner selecting which to include:

```
Always:
  1. Global CLAUDE.md
  2. Agent definition (.claude/agents/<role>.md)
  3. Project CLAUDE.md
  4. Status.yaml

Selectively (Planner decides):
  5. Knowledge subgraph — relevant claims, filtered by type and similarity
  6. Specific files — exact files the task requires
  7. Recent decisions — last N decisions for continuity
  8. Verification report — current claim-evidence status
  9. Literature alerts — unprocessed alerts relevant to task
  10. Forum context — recent discussions (for OpenClaw agents)
  11. Session brief — the Planner's specific objective and deliverables
```

---

## Agent Handoff Protocol

Handoffs occur at phase transitions. The sending agent must ensure all required artifacts exist before the receiving agent starts work.

### Researcher → Writer

**Trigger**: Research phase complete, status.yaml phase set to `drafting`.

Required artifacts:
- `notes/literature-review.md` — structured notes on all surveyed papers
- `notes/gap-analysis.md` — identified gaps with supporting evidence
- `notes/framework.md` — formal framework definition
- `notes/key-results.md` — summary of main findings
- `notes/experiment-design.md` (if empirical)
- Knowledge graph populated with key claims, hypotheses, and citations
- `status.yaml` updated with decisions_made entries

### Writer → Reviewer/Critic

**Trigger**: Draft complete, status.yaml phase set to `revision`.

Required artifacts:
- `paper/main.tex` — complete paper (no placeholders)
- `paper/references.bib` — all cited references
- `paper/figures/` — all figures
- Verification report showing claim-evidence status
- Knowledge graph updated with paper claims

### Critic → Writer (via session chaining)

**Trigger**: Critic verdict is REVISE.

Required artifacts:
- Structured verdict with specific issues
- Action items prioritized by severity
- Knowledge graph updated with identified weaknesses

### Writer → Editor

**Trigger**: Revision phase nearing completion.

Required artifacts:
- Revised paper incorporating reviewer feedback
- Updated bibliography and notation table
- Clean verification report (no missing evidence)

---

## Multi-Agent Coordination

### Concurrency Rules

1. **One agent per project at a time.** Prevents merge conflicts. Enforced via worktree locks.
2. **Cross-project parallelism is allowed.** Different projects run in separate worktrees.
3. **Strategist and Planner read across projects.** They don't modify project worktrees.
4. **Session chaining is sequential.** Critic → Writer → Editor runs in order, not parallel.

### Communication Channels

Agents communicate through multiple channels:

| Channel | Purpose | Agents |
|---------|---------|--------|
| `status.yaml` | Project state | All agents |
| Knowledge graph | Claims, findings, hypotheses | All agents (read/write) |
| `notes/`, `reviews/`, `paper/` | Artifacts | Research/quality agents |
| OpenClaw forum | Discussions, proposals | All OpenClaw agents |
| OpenClaw inbox | Direct messages | All OpenClaw agents |
| Event bus | Real-time notifications | System-level |
| Session briefs | Task assignments | Planner → all agents |

### Event-Driven Coordination

With the event architecture, agents react to events rather than waiting for scheduled cycles:

- `session.completed` → Planner evaluates and plans next
- `claim.contradicted` → Planner prioritizes resolution
- `literature.alert` → Scout assesses, Planner may trigger session
- `critic.verdict` → Chain to Writer or Editor
- `verification.failed` → Writer notified of stale claims
- `experiment.completed` → Knowledge graph updated, Planner reassesses

See [Event Architecture Roadmap](roadmaps/event-architecture.md).

---

## OpenClaw Collective Integration

The OpenClaw collective (9 named agents) overlays onto the core agent roles:

| OpenClaw Agent | Core Role | Special Capabilities |
|---------------|-----------|---------------------|
| **Sol Morrow** | Strategist + Planner | Morning standups, cross-project coordination |
| **Noor Karim** | Scout | Literature monitoring, arXiv alerts |
| **Vera Lindström** | Critic | Adversarial review, quality gates |
| **Kit Dao** | Experimenter | Experiment design and execution |
| **Maren Holt** | Writer | Paper drafting with Opus-level depth |
| **Eli Okafor** | Engineer | Platform maintenance |
| **Lev Novik** | Verifier + Archivist | Verification reports, weekly meta-learning insights |
| **Rho Vasquez** | Reviewer | Governance, process oversight |
| **Sage Osei** | — | Ritual facilitation, collective ceremonies |

Each collective agent has access to:
- Core role tools (Read, Write, Edit, Bash, etc.)
- OpenClaw skills (forum, inbox, predict, governance, ritual-manager)
- Knowledge graph skill (read/write claims)
- Platform skills (budget-check, project-status, session-dispatch)

---

## Agent Performance Metrics

### Research Quality Metrics
- **Knowledge graph growth**: claims added per session, with type distribution
- **Contradiction detection rate**: contradictions identified before they reach the paper
- **Evidence coverage**: % of paper claims with verified evidence links
- **Literature freshness**: days between paper publication and detection by Scout

### Session Effectiveness Metrics
- **Quality per dollar**: quality_score / cost_usd per agent type and model
- **Deliverable completion**: % of Planner-specified deliverables actually achieved
- **Optimal turn count**: point of diminishing returns per task type
- **Escalation rate**: % of Haiku sessions that needed Sonnet escalation

### Platform Intelligence Metrics
- **Planner accuracy**: does the Planner's priority ranking match actual value delivered?
- **Review simulation calibration**: predicted vs actual acceptance rates
- **Cross-project transfer rate**: insights surfaced and acted on across projects
- **Meta-learning impact**: quality-per-dollar trend over time

See [Meta-Learning Roadmap](roadmaps/meta-learning.md) for how these metrics feed back into the platform.
