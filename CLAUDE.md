# Deepwork Research Platform

## Project Overview
AI-driven research platform that uses Claude Code to autonomously research, write, and iterate on Turing Award-caliber papers, lectures, and experiments. Multiple projects run simultaneously with human oversight.

## Repository Structure
- `orchestrator/` - Core platform engine (TypeScript, Node.js)
- `cli/` - CLI dashboard tool (Ink/React)
- `projects/<name>/` - Individual research projects
- `shared/` - Templates, prompts, utilities shared across projects
- `.claude/` - Claude Code configuration, commands, agents

## Conventions

### Git
- **Conventional commits**: `type(scope): description`
- Types: `paper`, `research`, `code`, `data`, `feat`, `fix`, `docs`, `chore`
- Branch naming: `research/<project>`, `paper/<project>/<version>`, `feature/<desc>`
- All merges to `main` via PR
- **No co-authored-by trailers** — keep commits clean
- **Worktree workflow**: Each project session runs in `.worktrees/<project>/` on its own branch
- Commit frequently, push after every commit
- Create PRs to `main` at milestones (phase transitions, significant findings)

### Code Style
- TypeScript for orchestrator and CLI
- ESM modules (`"type": "module"` in package.json)
- Use `node:` prefix for Node.js built-in imports
- Prefer async/await over callbacks
- Minimal dependencies — use Node.js built-ins where possible

### Research Projects
- Each project has a `BRIEF.md` (goals), `status.yaml` (state), and `CLAUDE.md` (agent instructions)
- Papers use LaTeX (preferred) or Markdown
- Status files are the single source of truth for project state

### When Working on a Research Project
- Read `projects/<name>/BRIEF.md` first to understand goals
- Check `projects/<name>/status.yaml` for current state
- Follow the project's `CLAUDE.md` for project-specific instructions
- Make conventional commits with the project name as scope
- Update `status.yaml` after significant progress
- Make decisions autonomously and log them in `status.yaml`

### Decision Protocol
All decisions are made autonomously by Claude. No human escalation required.

For every decision:
1. Use extended thinking (highest reasoning level) for critical choices — research direction, methodology, theoretical claims, paper scope
2. Make the decision and proceed immediately
3. Log the decision in `decisions_made` in `status.yaml` with date, decision, and rationale
4. For lower-stakes decisions (formatting, organization, naming), decide without logging

### Budget & Resources
- Monthly budget: $1,000 for external APIs and compute
- Track spending in `budget.yaml`
- 2× Claude Code Max accounts for interactive sessions
- See `config.yaml` for full resource configuration
