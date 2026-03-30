# Serre AI

Autonomous AI research platform. Claude Code agents conduct literature reviews, develop formal frameworks, design experiments, and write papers targeting top ML/AI venues — running 24/7 with human oversight at decision boundaries.

## What This Is

A TypeScript platform that orchestrates multiple concurrent research projects. Each project gets its own Claude Code agent session running in an isolated git worktree. A daemon scheduler prioritizes work, enforces budgets, creates PRs, and logs everything.

**Active projects:**
- **Reasoning Gaps** (NeurIPS 2026) — Formally characterizing LLM reasoning failures via computational complexity
- **Agent Failure Taxonomy** (ACL 2027) — Surveying and categorizing failure modes in LLM-based autonomous agents

## Architecture

```
deepwork/
├── orchestrator/        # Core platform (TypeScript)
│   └── src/
│       ├── daemon.ts           # Scheduling loop, project prioritization
│       ├── session-runner.ts   # Claude Agent SDK integration
│       ├── session-manager.ts  # Worktree lifecycle, auto-PR creation
│       ├── git-engine.ts       # Git/GitHub operations
│       ├── project-manager.ts  # status.yaml CRUD
│       ├── budget-tracker.ts   # Spending enforcement
│       ├── logger.ts           # JSONL activity logging
│       ├── monitor.ts          # Health monitoring
│       ├── notifier.ts         # Webhook notifications
│       └── transcript-writer.ts # Session transcript capture
├── site/                # Research website (Astro + Tailwind)
├── cli/                 # Terminal dashboard (Ink/React)
├── projects/            # Research projects (briefs, status, papers)
├── shared/              # Templates, prompts, agent definitions
├── docs/                # Platform documentation
└── .claude/             # Agent configuration
```

## How It Works

1. **Daemon** wakes every 30 minutes, scores active projects by deadline proximity, staleness, and budget
2. **Session Runner** launches Claude Code via the Agent SDK in each project's worktree
3. Agents read their brief and status file, pick up where they left off, do research, commit, push
4. **Auto-PR** creates GitHub PRs when sessions produce commits
5. **Budget Tracker** enforces daily/monthly spend limits
6. **Transcripts** save full agent conversation logs to `.sessions/` for review
7. **Notifications** fire webhooks on session completion, failures, and budget alerts

## Setup

```bash
# Clone and install
git clone git@github.com:oddurs/deepwork.git
cd deepwork
npm install --workspaces
npm run build --workspace=orchestrator

# Configure
cp .env.example .env  # Add ANTHROPIC_API_KEY, etc.

# Run a single session
node orchestrator/dist/index.js start reasoning-gaps --agent researcher --turns 10

# Start the daemon
node orchestrator/dist/index.js run --interval 30 --max-sessions 2 --budget 40
```

## CLI Commands

```
deepwork run                     Start daemon scheduler
  --interval <minutes>           Poll interval (default: 30)
  --max-sessions <n>             Max concurrent sessions (default: 2)
  --budget <usd>                 Daily budget (default: 40)

deepwork start <project>         Run a single session
  --agent <type>                 researcher|writer|reviewer|editor|strategist
  --turns <n>                    Max turns (default: 50)

deepwork list                    List all projects
deepwork health                  Daemon status, budget, disk, errors
deepwork budget                  Spending breakdown
deepwork activity [count]        Recent event log
```

## Environment

```bash
ANTHROPIC_API_KEY=sk-ant-...     # Required: Claude API key
NOTIFICATION_WEBHOOK_URL=...     # Optional: Slack/Discord webhook
DAILY_BUDGET_USD=40              # Daily spend limit
MAX_CONCURRENT_SESSIONS=2        # Parallel agent sessions
POLL_INTERVAL_MINUTES=30         # Daemon cycle interval
```

## Research Projects

Each project lives in `projects/<name>/` with:
- `BRIEF.md` — Goals, hypotheses, methodology, timeline
- `status.yaml` — Single source of truth for project state
- `CLAUDE.md` — Agent-specific instructions

Projects follow conventional commits (`research(project): description`) and run on isolated branches (`research/<project>`).

## Infrastructure

- **VPS**: Hetzner (Ubuntu 24.04, 4GB RAM) running the daemon via systemd
- **GPU**: Modal (scale-to-zero, T4/A100 on demand)
- **CI**: GitHub Actions for site deployment
- **Monitoring**: Health heartbeats, activity logs, spending records

## Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full documentation index covering operations, infrastructure, agent roles, quality standards, and the 12-month roadmap.

---

Oddur Sigurdsson · [Serre AI](https://oddurs.github.io/deepwork)
