# Deepwork Infrastructure Roadmap

**Created**: 2026-03-10
**Updated**: 2026-03-11
**Goal**: Remote-first autonomous research platform with visual monitoring

## Current State

Evaluation phase largely complete — 9/12 models evaluated locally, no active eval jobs running:
- 121,614 evaluation instances collected across 9 models × 9 tasks × 3 conditions (zero failures)
- API models (Haiku, GPT-4o-mini, GPT-4o) evaluated via Anthropic/OpenAI APIs
- Open-source models (Llama 8B/70B, Ministral 8B, Mistral Small 24B, Qwen 7B/72B) evaluated via OpenRouter API — eliminated need for Modal GPU deployment
- Total eval cost: ~$75 (Anthropic ~$15, OpenAI ~$60, OpenRouter ~$0.22)
- 3 models pending cost decisions: Sonnet 4.6, Opus 4.6, o3
- Analysis pipeline ready but full analysis not yet run on complete dataset
- Claude Code sessions are interactive and local
- No remote monitoring or notifications
- No persistent database — all state in YAML/JSONL flat files
- Orchestrator daemon exists in compiled JS but isn't deployed anywhere

### What Already Exists

**Orchestrator** (`orchestrator/`):
- 5 TypeScript source files: index.ts, project-manager.ts, session-manager.ts, git-engine.ts, yaml.ts
- 7 compiled-only JS modules: daemon.js, session-runner.js, budget-tracker.js, notifier.js, monitor.js, transcript-writer.js, logger.js
- The daemon has: polling loop, project scoring/prioritization, concurrent session management, budget enforcement, heartbeat, graceful shutdown, failure backoff, Slack notifications, transcript recording
- SessionRunner integrates with `@anthropic-ai/claude-agent-sdk` for headless Claude Code

**Evaluation Infrastructure** (`benchmarks/`, `experiments/`):
- Model clients for Anthropic, OpenAI, vLLM, and OpenRouter
- Checkpoint/resume system (crash-safe JSONL)
- Analysis pipeline with statistical tests, visualizations, LaTeX output
- Modal serving code preserved but not deployed (OpenRouter was cheaper/simpler)

**CLI** (`cli/`): Ink/React terminal dashboard (display-only, reads status files)

**Website** (`site/`): Astro-based deepwork.site

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

### Phase 1: VPS Foundation
- Provision Hetzner CPX21 ($8/mo)
- Clone repo, install deps, copy .env (including OpenRouter key)
- Test: orchestrator reads project state
- Run any remaining eval jobs (Sonnet/Opus/o3 if decided)

### Phase 2: Restore Orchestrator
- Reconstruct 7 TypeScript source files from compiled JS
- Wire SessionManager -> SessionRunner
- Add CLI subcommands: daemon, health, eval, logs
- Create systemd service files
- Test daemon loop on VPS

### Phase 3: Database
- Install PostgreSQL on VPS
- Design and create schema (projects, eval_results, sessions, budget_events, etc.)
- Add Postgres writes to eval pipeline (alongside existing JSONL)
- Add sync: daemon reads status.yaml -> inserts into projects table
- Backfill existing eval results into Postgres

### Phase 4: API Layer
- Add REST endpoints to daemon process (Express/Fastify)
- Endpoints: projects, eval progress, budget, health, sessions, decisions
- Add WebSocket for real-time eval progress + log streaming
- API key auth
- Test from curl / Postman

### Phase 5: Web Dashboard
- Design dashboard views (eval monitor, results, budget, sessions, health)
- Integrate into deepwork.site (or separate dashboard subdomain)
- Real-time eval progress bars, accuracy heatmaps
- Budget burn rate charts
- Session transcript browser
- System health panel

### Phase 6: Notifications & Polish
- Slack webhook integration (Notifier class exists)
- Daily summary cron
- Nightly backup to Hetzner Storage Box ($4/mo)
- GitHub Actions for LaTeX compilation
- End-to-end crash recovery test

## Monthly Budget

| Item | Cost | Notes |
|------|------|-------|
| Hetzner CPX21 VPS | $8 | |
| Hetzner Storage Box (1TB backup) | $4 | |
| Anthropic API (sessions + eval) | $200-400 | |
| OpenAI API (eval) | $50-100 | |
| OpenRouter API (open-source eval) | $1-5 | Replaced Modal GPU — 100x cheaper |
| Vercel (website hosting) | $0-20 | |
| Slack | $0 | |
| **Total** | **$263-537** | Well within $1,000/month budget |

Note: Modal GPU line item removed. OpenRouter eliminated the need for GPU infrastructure for open-source model evaluation, saving an estimated $100-200/month.
