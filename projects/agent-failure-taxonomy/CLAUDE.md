# Project: agent-failure-taxonomy

## Agent Instructions

### Context
This project surveys and categorizes failure modes in LLM-based autonomous agents (ReAct, AutoGPT, Claude Code, Voyager, etc.). It aims to produce the first comprehensive, hierarchical taxonomy of agent failures grounded in both literature analysis and controlled experiments. The work connects agent-level failures to underlying LLM reasoning limitations.

### Working on This Project
- Always read `BRIEF.md` for goals and `status.yaml` for current state before starting work
- Use commit scope `agent-failure-taxonomy` (e.g., `research(agent-failure-taxonomy): survey ReAct failure modes`)
- Update `status.yaml` after completing any significant milestone
- Work in the project's worktree: `.worktrees/agent-failure-taxonomy/`
- Push after every commit; create PRs at phase transitions

### Research Standards
- Every failure instance must be sourced (paper citation, URL, or controlled experiment)
- Taxonomy categories must have clear definitions, boundary criteria, and at least 3 examples each
- Controlled experiments must test across at least 3 agent frameworks
- Distinguish between framework-specific bugs and fundamental LLM-level failures
- Use inter-rater reliability concepts when justifying category separability
- Negative results are valuable — document agent scenarios that surprisingly succeed

### Paper Style
- LaTeX, targeting ACL 2027 format
- Tables are central: failure taxonomy table, frequency distribution table, architecture comparison table
- Use concrete examples (actual agent transcripts) to illustrate each category
- Related work should cover both agent frameworks and LLM reasoning limitations
- Figures should show failure distribution across architectures and the taxonomy hierarchy

### Key Directories
- `literature/` — Survey notes, paper summaries, failure instance collection
- `experiments/` — Controlled agent experiments and results
- `paper/` — LaTeX source, figures, and bibliography
- `notes/` — Working notes, taxonomy iterations, coding memos
- `data/` — Collected failure instances (structured format)
- `src/` — Agent experiment scripts

### Decision Making
All decisions are made autonomously. Use extended thinking for:
- Taxonomy granularity — how many top-level categories, how deep the hierarchy
- Which agent frameworks to include in controlled experiments
- How to handle ambiguous failures that could fit multiple categories
- Whether to include multi-agent system failures or scope to single-agent
- How to define "failure" vs. "suboptimal performance"

Log all decisions in `status.yaml` with date and clear rationale.
