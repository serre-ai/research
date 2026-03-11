# Deepwork Infrastructure Roadmap

**Created**: 2026-03-10
**Updated**: 2026-03-11
**Goal**: Remote-first autonomous research platform with visual monitoring

## Current State (Updated 2026-03-11)

**VPS deployed and operational.** Remote-first infrastructure is live.

### What's Running

- **VPS** (89.167.5.50): Hetzner CPX21, Ubuntu 24.04, 3.7GB RAM, 75GB disk (6% used)
- **Daemon**: systemd-managed `deepwork-daemon.service`, polling every 30m, auto-restart
- **API**: Express REST + WebSocket on port 3001, proxied by nginx on port 80
- **PostgreSQL 16**: 121,146 eval results, 243 eval_runs, project records, materialized views
- **Python venv**: All analysis/eval deps installed at `~/deepwork/.venv`
- **Security**: fail2ban, UFW (22/80/443), API key auth, .env chmod 600

### What Exists in Codebase

**Orchestrator** (`orchestrator/`):
- 12 TypeScript source files (all restored). Build passes cleanly.
- `index.ts` wired with `run` command: starts daemon loop + API server
- `api.ts`: REST endpoints (projects, eval, budget, health) + WebSocket
- `daemon.ts`: polling loop, project scoring, session management
- `session-runner.ts`: Claude Agent SDK integration (needs SDK package for runtime)
- Deploy configs: systemd units, nginx conf, setup script

**Evaluation** (`benchmarks/`):
- 4 model clients (Anthropic, OpenAI, OpenRouter, vLLM)
- Checkpoint/resume, analysis pipeline, cost monitoring
- 121,614 instances across 9 models × 9 tasks × 3 conditions

**Site** (`site/`): Astro dashboard pages (overview, eval monitor, budget tracker) with mock data

## Target Architecture

```
Hetzner VPS (CPX21, ~$8/mo)                    External Services
┌──────────────────────────────────┐       ┌──────────────────────┐
│  systemd services                │       │  Anthropic API       │
│  ├── deepwork-daemon             │──────>│  OpenAI API          │
│  │   (orchestrator + REST API)   │       │  OpenRouter API      │
│  ├── deepwork-eval@.service      │──────>│  GitHub              │
│  │   (Python eval jobs)          │       │  Slack webhooks      │
│  └── postgresql                  │       └──────────────────────┘
│                                  │
│  Data:                           │       Frontend (Vercel/CF)
│  ├── PostgreSQL (query layer)    │       └── deepwork.site
│  ├── Git repo (source of truth)  │           ├── Dashboard
│  ├── Checkpoints (JSONL)         │           ├── Eval monitor
│  └── Transcripts (.jsonl)        │           └── Budget tracker
└──────────────────────────────────┘               │
         ▲                                         │
         └─── REST/WebSocket API ──────────────────┘
```

## Key Design Decisions

### Database: PostgreSQL on VPS
- Git/YAML stays as source of truth (version-controlled, crash-safe)
- Postgres is the read-optimized mirror for fast dashboard queries
- Eval scripts write to both JSONL checkpoints AND Postgres
- Tables: projects, eval_results, eval_runs, sessions, decisions, budget_events
- Not SQLite: need concurrent reads (dashboard) + writes (daemon/eval)

### Open-Source Model Inference: OpenRouter API (not Modal)
- OpenRouter provides API access to all open-source models at negligible cost (~$0.22 for all 6 models)
- Eliminates Modal GPU provisioning, cold starts, and infrastructure management
- Modal serving code preserved in codebase for reproducibility validation on dedicated hardware
- vLLM client kept as provider option for future local/self-hosted inference

### Dashboard: Frontend on Vercel, API on VPS
- Website deployment stays on Vercel/Cloudflare (fast, existing workflow)
- VPS exposes REST + WebSocket API that the frontend calls
- HTTPS + API key auth (single-user system)
- Dashboard views: eval monitor, results explorer, budget tracker, session viewer, system health

### Orchestrator: Daemon + API in one process
- The existing daemon loop becomes the main VPS process (systemd)
- Add Express/Fastify routes to the same process for the API layer
- No separate API service — keeps it simple, single process reads same state
- WebSocket for real-time eval progress and log streaming

### Notifications: Slack (existing Notifier class)
- Push alerts for: eval completion, budget warnings, daemon failures
- Daily summary cron job
- GitHub mobile app for PR/commit monitoring

## Implementation Phases

### Phases 1-4: COMPLETE (deployed 2026-03-11)
- [x] VPS Foundation — provisioned, configured, secured
- [x] Orchestrator — all TS sources, build passes, daemon running
- [x] Database — PostgreSQL 16, schema applied, 121K rows backfilled
- [x] API Layer — REST + WebSocket, nginx proxy, API key auth

### Phase 5: Web Dashboard (next infrastructure sprint)
- [ ] Point `api.deepwork.site` DNS A record to 89.167.5.50
- [ ] Run `certbot --nginx -d api.deepwork.site` for HTTPS
- [ ] Wire dashboard pages to call VPS API (replace mock data with fetch calls)
- [ ] Deploy updated site to Vercel/Cloudflare

### Phase 6: Notifications & Polish
- [ ] Add `SLACK_WEBHOOK_URL` to VPS `.env`
- [ ] Daily summary cron job
- [ ] Nightly backup to Hetzner Storage Box ($4/mo)
- [ ] GitHub Actions for LaTeX compilation on push
- [ ] Merge `main` and `research/reasoning-gaps` branches (resolve conflicts)

### Phase 7: VPS Scale-Up
- [ ] Resize VPS from CPX21 → CPX31 (4 vCPU, 8GB RAM, 160GB, ~$16/mo)
- [ ] Increase `MAX_CONCURRENT_SESSIONS` from 2 → 4
- [ ] Run eval jobs on VPS instead of locally (transfer checkpoints + scripts)
- [ ] Add swap (2-4GB) as safety net for memory spikes
- **Rationale**: Agent sessions are API-bound, not compute-bound. Doubling RAM is the highest-leverage upgrade — enables 4 concurrent agents and co-located eval jobs for ~$8/mo more. GPU/dedicated server not justified while OpenRouter inference costs pennies.

## Monthly Budget

| Item | Cost | Notes |
|------|------|-------|
| Hetzner CPX21 VPS | $8 | Running since 2026-03-10 |
| Anthropic API | $200-400 | Eval + sessions |
| OpenAI API | $50-100 | Eval only |
| OpenRouter API | $1-5 | Open-source models |
| **Total** | **$259-513** | Well within $1,000/month budget |

**Spent to date**: ~$83 (Anthropic ~$15, OpenAI ~$60, OpenRouter ~$0.22, VPS ~$8)
**Planned next**: ~$98 (Sonnet 4.6 ~$55, o3 ~$40, B2 recal ~$3-5)
