# Serre AI — Forge Research Platform

## Project Overview
AI-driven research platform that uses Claude Code to autonomously research, write, and iterate on Turing Award-caliber papers, lectures, and experiments. Multiple projects run simultaneously with human oversight.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────┐
│   forge/    │────▶│  orchestrator/   │────▶│ PostgreSQL │
│  Next.js 16     │     │  Express + WS    │     │            │
│  port 3000      │     │  port 3001       │     │  deepwork  │
└─────────────────┘     └──────────────────┘     └────────────┘
       │                        │
       │ proxy /api/*           │ daemon sessions
       │ auth gate              │ eval jobs
       └────────────────────────┘
```

Everything runs on a single Hetzner VPS at `forge.serre.ai` (89.167.5.50). Nginx terminates SSL and proxies to both services.

## Repository Structure
- `orchestrator/` — Express REST API + WebSocket + daemon engine (TypeScript)
- `forge/` — Next.js 16 dashboard (React 19, TanStack Query, Tailwind)
- `cli/` — Terminal dashboard (Ink/React) — legacy, not actively developed
- `projects/<name>/` — Individual research projects (papers, benchmarks, data)
- `shared/` — Templates and prompts shared across projects
- `.claude/` — Claude Code configuration, commands, agents

## Deployment

### VPS Services (systemd)
| Service | Unit | Port | What |
|---------|------|------|------|
| Dashboard | `forge-site.service` | 3000 | Next.js production server |
| API + Daemon | `forge-daemon.service` | 3001 | Express + WebSocket + daemon |

**Daemon status (as of 2026-03-31):** Stopped and disabled. The daemon loop and API run in the same process — stopping the service kills both. Re-enable with:
```bash
ssh deepwork-vps-root "systemctl enable --now forge-daemon.service"
```

### serre.ai (Vercel)
Institutional site at `site/`. Deployed automatically by Vercel on push to `main`. Builds are skipped when the commit doesn't touch `site/` (configured via ignored build step).

### Deploy workflow
```bash
# After pushing changes:
ssh deepwork-vps "cd ~/deepwork && git pull"

# Site changes:
ssh deepwork-vps "cd ~/deepwork/forge && npm run build"
ssh deepwork-vps-root "systemctl restart forge-site"

# API changes:
ssh deepwork-vps-root "systemctl restart forge-daemon"
```

### SSH aliases
- `deepwork-vps` — user `deepwork`
- `deepwork-vps-root` — root access

## Conventions

### Git
- **Conventional commits**: `type(scope): description`
- Types: `paper`, `research`, `code`, `data`, `feat`, `fix`, `docs`, `chore`
- All work happens on `main`. See `docs/GIT-WORKFLOW.md` for the full workflow.
- Agent worktree branches are ephemeral — created and deleted within a single session.
- No long-lived feature branches.
- **No co-authored-by trailers** — keep commits clean
- Commit frequently, push after every commit
- Create PRs to `main` at milestones

### Code Style
- TypeScript everywhere (orchestrator, forge, cli)
- ESM modules (`"type": "module"` in package.json) for orchestrator
- Use `node:` prefix for Node.js built-in imports in orchestrator
- Prefer async/await over callbacks
- Minimal dependencies — use Node.js built-ins where possible

### Workspace
This is an npm workspace. Root `package.json` lists `orchestrator`, `cli`, `site`, `forge`. Be aware that dependency hoisting can cause React version conflicts — see `forge/CLAUDE.md` for details.

### Research Projects
- Each project has `BRIEF.md` (goals), `status.yaml` (state), `CLAUDE.md` (agent instructions)
- Papers use LaTeX (preferred) or Markdown
- Status files are the single source of truth for project state

### When Working on a Research Project
- Read `projects/<name>/BRIEF.md` first to understand goals
- Check `projects/<name>/status.yaml` for current state
- Follow the project's `CLAUDE.md` for project-specific instructions
- Make conventional commits with the project name as scope
- Update `status.yaml` after significant progress
- Make decisions autonomously and log them in `status.yaml`

### Destructive & External Operations — MANDATORY RULES
**NEVER perform destructive or state-changing operations on external services without explicit user confirmation.** This includes but is not limited to:
- Archiving, deleting, or modifying issues/projects/cycles in Linear, GitHub, or any other external tool
- Sending messages to Slack, email, or any communication platform
- Modifying DNS records, server configurations, or cloud resources
- Dropping or altering database tables on production/VPS

**Even if a plan says to do it, STOP and ask first.** Plans are proposals, not authorization. The user must explicitly approve each destructive action before execution.

This applies to ALL teams, workspaces, and accounts — not just DeepWork. Never assume data in external services is "debris" or safe to delete.

### Linear Workspace
- The Linear workspace contains multiple teams. **Only operate on the DW (DeepWork) team** unless explicitly told otherwise.
- The **EV team is a separate project** — never archive, delete, or modify EV issues, projects, or cycles.
- DW Team ID: `77e7bcae-30d7-4257-b043-6f0b004abc65`
- EV Team ID: `8513b969-e338-4196-97f9-1a15bcaf9962` — **DO NOT TOUCH**

### Decision Protocol
All decisions are made autonomously by Claude. No human escalation required.

For every decision:
1. Use extended thinking for critical choices — research direction, methodology, theoretical claims, paper scope
2. Make the decision and proceed immediately
3. Log the decision in `decisions_made` in `status.yaml` with date, decision, and rationale
4. For lower-stakes decisions (formatting, organization, naming), decide without logging

### Budget & Resources
- Monthly budget: $1,000 for external APIs and compute
- Track spending in `budget.yaml`
- 2× Claude Code Max accounts for interactive sessions
- See `config.yaml` for full resource configuration
