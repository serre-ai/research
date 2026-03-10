# Agent Team Architecture

This document defines the agent team structure, coordination protocols, and operational standards for the Deepwork research platform. Each agent is a specialized Claude Code session configured with a specific system prompt, tool set, and behavioral profile.

## Agent Roles

### Researcher

Primary agent during the **research phase**. Conducts literature review, identifies gaps in existing work, designs experiments, and performs data analysis. The Researcher produces the raw intellectual material that all downstream agents depend on.

- **Scope**: Literature search and synthesis, gap identification, hypothesis formation, experiment design, data analysis and interpretation.
- **Key outputs**: Literature notes, gap analyses, experiment designs, analysis reports.
- **Quality bar**: Every literature review covers a minimum of 20 papers. Every gap claim is supported by explicit evidence of absence in the surveyed work.

### Writer

Primary agent during the **drafting** and **revision** phases. Transforms research artifacts into publication-ready papers. The Writer owns the paper structure, prose quality, and LaTeX formatting.

- **Scope**: Paper drafting (all sections), revision in response to reviews, LaTeX formatting, figure descriptions, notation management.
- **Key outputs**: LaTeX source files, figure specifications, notation tables.
- **Quality bar**: Every draft must be structurally complete (no placeholder sections) before handoff to Reviewer. Prose must be clear enough that a graduate student in the field can follow every argument.

### Reviewer

Quality gate agent used at **phase transitions** and **before submission**. Provides honest, constructive, venue-calibrated review. The Reviewer's job is to find problems before external reviewers do.

- **Scope**: Critical evaluation of papers, scoring against venue standards, identifying logical gaps, verifying experimental claims, checking completeness.
- **Key outputs**: Structured reviews with scores, severity-tagged weaknesses, specific improvement suggestions.
- **Quality bar**: Reviews must be at least as thorough as a conscientious NeurIPS/ICML reviewer. Every weakness must include a concrete suggestion for how to fix it.

### Strategist

Portfolio management agent that runs **monthly** or **on-demand**. The Strategist looks across all projects simultaneously and makes resource allocation and prioritization decisions.

- **Scope**: Portfolio health assessment, idea generation and scoring, venue targeting and deadline tracking, project continuation/pivot/kill decisions, budget oversight.
- **Key outputs**: Monthly portfolio reports, project recommendations, idea backlog updates.
- **Quality bar**: Portfolio recommendations must be justified with specific evidence from project status files and venue timelines.

### Editor

Consistency and polish agent used during the **revision phase** and **before submission**. The Editor ensures that a paper meets professional standards for formatting, notation, citations, and style.

- **Scope**: Notation standardization, citation completeness and BibTeX validation, cross-reference verification, style enforcement, accessibility checks.
- **Key outputs**: Edit reports with specific, located, actionable fixes.
- **Quality bar**: After an Editor pass, the paper should have zero broken references, zero undefined notation, and zero uncited claims.

---

## Agent Assignment by Phase

| Phase | Primary Agent | Secondary Agents | Activities |
|-------|--------------|-----------------|------------|
| **Research** | Researcher | Strategist (at start) | Literature review, gap identification, hypothesis formation, experiment design, data collection and analysis |
| **Drafting** | Writer | Researcher (on call) | Paper structure, section drafting, figure creation, notation table, initial references |
| **Revision** | Writer | Reviewer, Editor | Respond to review comments, rewrite sections, add experiments, polish prose and formatting |
| **Final** | Editor | Reviewer, Writer | Final consistency pass, citation audit, cross-reference check, formatting verification, submission preparation |

Within each phase, the primary agent runs sessions regularly. Secondary agents are invoked for specific tasks (e.g., Researcher answers a factual question during drafting, Reviewer provides a mid-phase check).

---

## Agent Handoff Protocol

Handoffs occur at phase transitions. The sending agent must ensure all required artifacts exist before the receiving agent starts work. The orchestrator validates artifact presence before launching the next agent.

### Researcher to Writer

**Trigger**: Research phase complete, status.yaml phase set to `drafting`.

Required artifacts:
- `notes/literature-review.md` — structured notes on all surveyed papers with per-paper summaries
- `notes/gap-analysis.md` — identified gaps with supporting evidence
- `notes/framework.md` — formal framework definition (definitions, theorems, key notation)
- `notes/key-results.md` — summary of main findings, experimental results, or theoretical contributions
- `notes/experiment-design.md` (if empirical) — hypothesis, variables, controls, metrics, analysis plan
- `status.yaml` updated with `decisions_made` entries covering all critical research direction choices

### Writer to Reviewer

**Trigger**: Draft complete, status.yaml phase set to `revision` or submission review requested.

Required artifacts:
- `paper/main.tex` — complete paper with all sections drafted (no TODOs or placeholders)
- `paper/references.bib` — BibTeX file with all cited references
- `paper/figures/` — all figures referenced in the paper
- `paper/notation.md` — notation table mapping symbols to definitions
- `status.yaml` updated with drafting progress and any deviations from the research plan

### Reviewer to Writer

**Trigger**: Review complete, revision needed.

Required artifacts:
- `reviews/review-YYYY-MM-DD.md` — structured review with scores, strengths, weaknesses (severity-tagged), questions, and specific suggestions
- `reviews/action-items.md` — prioritized list of changes extracted from the review
- `status.yaml` updated with review scores and recommended next steps

### Strategist to Researcher

**Trigger**: New project approved or existing project direction changed.

Required artifacts:
- `BRIEF.md` — approved project brief with goals, scope, venue target, and timeline
- `status.yaml` — initialized with phase `research`, allocated resources, and deadline
- Portfolio report entry documenting why this project was approved/prioritized

### Writer to Editor

**Trigger**: Revision phase nearing completion, pre-submission polish needed.

Required artifacts:
- `paper/main.tex` — revised paper incorporating reviewer feedback
- `paper/references.bib` — updated bibliography
- `paper/notation.md` — current notation table

### Editor to Writer

**Trigger**: Edit pass complete, fixes needed that require rewriting.

Required artifacts:
- `reviews/edit-report-YYYY-MM-DD.md` — structured list of issues with locations, types, severities, and suggested fixes
- Issues tagged as `auto-fixed` (Editor applied the fix directly) vs `needs-rewrite` (Writer must address)

---

## Multi-Agent Coordination

### Concurrency Rules

1. **One agent per project at a time.** This prevents merge conflicts and ensures a coherent work stream. The orchestrator enforces this via worktree locks.
2. **Cross-project parallelism is allowed.** Reviewer can work on Project A while Writer works on Project B simultaneously, since they operate in separate worktrees on separate branches.
3. **Strategist is the exception.** The Strategist reads all project status files in read-only mode from the main branch. It does not modify project worktrees. Its outputs go to `docs/reports/`.

### Conflict Prevention

- Each project session runs in `.worktrees/<project>/` on its own branch.
- Agents commit and push frequently. No long-lived uncommitted changes.
- Handoff artifacts are committed before phase transition.
- The orchestrator checks for uncommitted changes before launching a new agent session.

### Communication Between Agents

Agents do not communicate directly. All inter-agent communication happens through artifacts in the repository:
- `status.yaml` is the primary state channel.
- `notes/` directory contains research artifacts.
- `reviews/` directory contains review artifacts.
- `paper/` directory contains the paper itself.

If an agent needs input from another agent's domain, it records the question in `status.yaml` under `pending_questions`, and the orchestrator routes it to the appropriate agent in the next session.

---

## Session Configuration

| Agent | maxTurns | Thinking Level | Typical Duration | Key Tools |
|-------|----------|---------------|-----------------|-----------|
| **Researcher** | 50 | Extended (for research direction, methodology) | 30-60 min | WebSearch, WebFetch, Read, Write, Grep, Bash |
| **Writer** | 40 | Standard (extended for framing decisions) | 30-45 min | Read, Write, Edit, Bash (LaTeX compilation) |
| **Reviewer** | 30 | Extended (for evaluation judgments) | 20-30 min | Read, Grep, Write |
| **Strategist** | 30 | Extended (all decisions are critical) | 15-30 min | Read, Grep, Write, WebSearch |
| **Editor** | 25 | Standard | 15-25 min | Read, Write, Edit, Grep, Bash (LaTeX checks) |

### Tool Restrictions

- **Reviewer** has no Write access to `paper/` — it writes only to `reviews/`. This separation ensures the Reviewer does not silently fix issues instead of reporting them.
- **Strategist** has no Write access to project worktrees — it writes only to `docs/reports/` and can update idea backlog files.
- **Editor** has Write access to `paper/` for auto-fixable issues (broken references, BibTeX formatting) but must report substantive changes rather than making them silently.

---

## Prompt Composition

Each agent session's system prompt is assembled from multiple layers, with later layers taking precedence:

```
1. Global CLAUDE.md          — Repository conventions, git workflow, decision protocol
2. Agent definition           — .claude/agents/<role>.md — role-specific instructions
3. Project CLAUDE.md          — projects/<name>/CLAUDE.md — project-specific context
4. Phase instructions         — Injected based on status.yaml phase field
5. Current status context     — Serialized status.yaml for immediate situational awareness
```

The orchestrator reads these files and composes them into the session's system prompt before launching the agent. This layered approach means:
- Global standards are always present.
- Agent-specific behavior overrides global defaults where appropriate.
- Project-specific instructions can further specialize the agent.
- Phase instructions focus the agent on the current task.
- Status context gives the agent immediate awareness of where things stand.

---

## Agent Performance Metrics

Metrics are tracked per session and aggregated monthly in the Strategist's portfolio report.

### Researcher
- **Papers surveyed per session**: target 10-20 in a focused literature review session
- **Gaps identified**: number of novel, actionable gaps found per review
- **Synthesis quality**: assessed by Reviewer — does the literature review accurately represent the field?
- **Experiment design completeness**: does the design cover hypothesis, variables, controls, metrics, and analysis plan?

### Writer
- **Pages drafted per session**: target 3-5 pages of polished prose per session
- **Revision turnaround time**: sessions between receiving review and completing revision
- **Structural completeness**: percentage of sections in complete (non-placeholder) state
- **Notation consistency**: zero undefined or reused symbols (checked by Editor)

### Reviewer
- **Issues found per page**: target 2-5 substantive issues per page (too few suggests shallow review, too many suggests premature review)
- **False positive rate**: fraction of raised issues that Writer reasonably rejects as non-issues
- **Suggestion specificity**: percentage of weaknesses that include a concrete fix suggestion (target: 100%)
- **Score calibration**: do scores predict eventual venue acceptance? Tracked over time.

### Strategist
- **Portfolio health score**: aggregate metric based on project phases, timelines, and quality indicators
- **Idea quality**: fraction of generated ideas that become active projects
- **Decision accuracy**: do continue/pivot/kill recommendations prove correct in hindsight?
- **Budget utilization**: actual spend vs. allocated budget, with variance analysis

### Editor
- **Consistency improvements per pass**: number of notation, style, and reference issues fixed
- **Citation completeness**: percentage of claims with citations before vs. after edit pass
- **Zero-defect rate**: fraction of edit passes that achieve zero broken references and zero undefined notation
- **Turnaround time**: sessions required to complete an edit pass
