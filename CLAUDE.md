# Deepwork Research Platform

## Project Overview
AI-driven research platform that uses Claude Code to autonomously research, write, and iterate on Turing Award-caliber papers, lectures, and experiments. Multiple projects run simultaneously with human oversight.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────┐
│   site-next/    │────▶│  orchestrator/   │────▶│ PostgreSQL │
│  Next.js 16     │     │  Express + WS    │     │            │
│  port 3000      │     │  port 3001       │     │  deepwork  │
└─────────────────┘     └──────────────────┘     └────────────┘
       │                        │
       │ proxy /api/*           │ daemon sessions
       │ auth gate              │ eval jobs
       └────────────────────────┘
```

Everything runs on a single Hetzner VPS at `research.oddurs.com` (89.167.5.50). Nginx terminates SSL and proxies to both services.

## Repository Structure
- `orchestrator/` — Express REST API + WebSocket + daemon engine (TypeScript)
- `site-next/` — Next.js 16 dashboard (React 19, TanStack Query, Tailwind)
- `cli/` — Terminal dashboard (Ink/React) — legacy, not actively developed
- `projects/<name>/` — Individual research projects (papers, benchmarks, data)
- `shared/` — Templates and prompts shared across projects
- `.claude/` — Claude Code configuration, commands, agents

## Deployment

### VPS Services (systemd)
| Service | Unit | Port | What |
|---------|------|------|------|
| Dashboard | `deepwork-site.service` | 3000 | Next.js production server |
| API | `deepwork-daemon.service` | 3001 | Express + WebSocket + daemon |

### Deploy workflow
```bash
# After pushing changes:
ssh deepwork-vps "cd ~/deepwork && git pull"

# Site changes:
ssh deepwork-vps "cd ~/deepwork/site-next && npm run build"
ssh deepwork-vps-root "systemctl restart deepwork-site"

# API changes:
ssh deepwork-vps-root "systemctl restart deepwork-daemon"
```

### SSH aliases
- `deepwork-vps` — user `deepwork`
- `deepwork-vps-root` — root access

## Conventions

### Git
- **Conventional commits**: `type(scope): description`
- Types: `paper`, `research`, `code`, `data`, `feat`, `fix`, `docs`, `chore`
- Branch naming: `research/<project>`, `paper/<project>/<version>`, `feature/<desc>`
- All merges to `main` via PR
- **No co-authored-by trailers** — keep commits clean
- Commit frequently, push after every commit
- Create PRs to `main` at milestones

### Code Style
- TypeScript everywhere (orchestrator, site-next, cli)
- ESM modules (`"type": "module"` in package.json) for orchestrator
- Use `node:` prefix for Node.js built-in imports in orchestrator
- Prefer async/await over callbacks
- Minimal dependencies — use Node.js built-ins where possible

### Workspace
This is an npm workspace. Root `package.json` lists `orchestrator`, `cli`, `site`, `site-next`. Be aware that dependency hoisting can cause React version conflicts — see `site-next/CLAUDE.md` for details.

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
