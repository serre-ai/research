# Evaluation & Infrastructure Roadmap

**Project**: reasoning-gaps (NeurIPS 2026)
**Created**: 2026-03-10
**Updated**: 2026-03-11
**Goal**: Complete empirical evaluation + migrate to remote-first infrastructure

---

## Phase 1: Evaluation Infrastructure (COMPLETE)

All pre-evaluation work is done. Streams A-G delivered:

- [x] **Stream A** — Benchmark validation, bug fixes, 195 tests passing
- [x] **Stream B** — Model clients (Anthropic, OpenAI, vLLM) with rate limiting, retry, cost tracking
- [x] **Stream C** — Answer extraction with task-specific parsers, refusal detection, 50+ test patterns
- [x] **Stream D** — Checkpoint/resume (crash-safe JSONL), dynamic CoT budgets, parallel evaluation
- [x] **Stream E** — Integration tests, live dry run with Haiku (caught 3 bugs)
- [x] **Stream F** — Analysis pipeline (tables, figures, bootstrap CIs, McNemar's test, LaTeX output)
- [x] **Stream G** — Batch orchestration, Modal serving, per-model endpoint routing
- [x] **Stream H** — OpenRouter client added as new provider for open-source models

## Phase 2: Empirical Evaluation (9/12 MODELS COMPLETE)

### Current Status

9 models fully evaluated: 121,614 instances across 9 tasks × 3 conditions, zero failures.

| Stream | Models | Progress | Cost | Notes |
|--------|--------|----------|------|-------|
| Anthropic | Haiku 4.5 | **Complete** (27/27) | ~$15 | Tier 3 (2,000 RPM) |
| OpenAI | GPT-4o-mini, GPT-4o | **Complete** (54/54) | ~$60 | |
| OpenRouter | Llama 3.1 8B, Llama 3.1 70B | **Complete** (54/54) | ~$0.08 | |
| OpenRouter | Ministral 8B, Mistral Small 24B | **Complete** (54/54) | ~$0.06 | Ministral 8B replaced Mistral 7B v0.3 (unavailable on OpenRouter) |
| OpenRouter | Qwen 2.5 7B, Qwen 2.5 72B | **Complete** (54/54) | ~$0.08 | |

**Total evaluation cost: ~$75** (Anthropic ~$15, OpenAI ~$60, OpenRouter ~$0.22)

### Results Summary (Average Accuracy by Model)

| Model | Family | Size | Avg Accuracy | Provider |
|-------|--------|------|-------------|----------|
| Qwen 2.5 72B | Qwen | 72B | 71.5% | OpenRouter |
| GPT-4o | GPT | — | 68.4% | OpenAI |
| GPT-4o-mini | GPT | — | 64.0% | OpenAI |
| Haiku 4.5 | Claude | — | 62.8% | Anthropic |
| Llama 3.1 70B | Llama | 70B | 62.5% | OpenRouter |
| Ministral 8B | Mistral | 8B | 62.2% | OpenRouter |
| Mistral Small 24B | Mistral | 24B | 60.5% | OpenRouter |
| Qwen 2.5 7B | Qwen | 7B | 57.7% | OpenRouter |
| Llama 3.1 8B | Llama | 8B | 48.2% | OpenRouter |

Key observations:
- Qwen 72B leads overall at 71.5%
- Model size matters but not linearly (Ministral 8B > Mistral Small 24B)
- CoT lifts confirmed across all families, matching theoretical predictions
- budget_cot needs recalibration (B2 budget too tight: 13% vs 93% with full CoT)

### Remaining Evaluation Work

- [x] Complete Haiku 4.5 evaluation (27 combinations)
- [x] Complete GPT-4o-mini + GPT-4o evaluation (54 combinations)
- [x] Run Llama 3.1 (8B + 70B) via OpenRouter
- [x] Run Mistral family (Ministral 8B + Small 24B) via OpenRouter
- [x] Run Qwen 2.5 (7B + 72B) via OpenRouter
- [ ] Decide on Claude Sonnet 4.6 (~$55, 27 combinations)
- [ ] Decide on Claude Opus 4.6 (~$272 — worth it for scale analysis?)
- [ ] Decide on o3 (~$40 — worth it for reasoning-model comparison?)
- [ ] Recalibrate budget_cot budgets (B2 budget too tight: 20 words → model scores 13% vs 93% with unlimited CoT). Fix `_budget_b2` in budget_calculator.py and re-run budget_cot condition only. Note: current data is still valid — shows that insufficient reasoning budget hurts worse than no reasoning. Consider framing as finding in paper.
- [ ] Run analysis pipeline on complete results
- [ ] Manual review of results, check for extraction errors

### Evaluation Matrix

| Family | Models | Access | Est. Cost | Status |
|--------|--------|--------|-----------|--------|
| Claude | Haiku 4.5 | API (Tier 3) | ~$15 | **Complete** |
| Claude | Sonnet 4.6 | API (Tier 3) | ~$55 | Pending decision |
| Claude | Opus 4.6 | API (Tier 3) | ~$272 | Pending decision |
| GPT | 4o-mini | API | ~$2 | **Complete** |
| GPT | 4o | API | ~$18 | **Complete** |
| GPT | o3 | API | ~$40 | Pending decision |
| Llama 3.1 | 8B-Instruct | OpenRouter | ~$0.04 | **Complete** |
| Llama 3.1 | 70B-Instruct | OpenRouter | ~$0.04 | **Complete** |
| Mistral | Ministral-8B-2512 | OpenRouter | ~$0.03 | **Complete** |
| Mistral | Small-24B-Instruct | OpenRouter | ~$0.03 | **Complete** |
| Qwen 2.5 | 7B-Instruct | OpenRouter | ~$0.04 | **Complete** |
| Qwen 2.5 | 72B-Instruct | OpenRouter | ~$0.04 | **Complete** |

### Infrastructure Notes

| Provider | Purpose | Notes |
|----------|---------|-------|
| Anthropic API | Claude models | Tier 3 (2,000 RPM), ~$15 for Haiku |
| OpenAI API | GPT models | ~$60 for 4o-mini + 4o |
| OpenRouter API | Open-source models | All 6 models for ~$0.22 total. Simple API, no GPU management. Added as new provider alongside existing vLLM client |
| Modal (preserved) | vLLM GPU serving | Code preserved in modal_serving.py for reproducibility validation. Not deployed — OpenRouter was cheaper and simpler |
| vLLM client (preserved) | Local/Modal inference | Kept in codebase for future reproducibility runs on dedicated hardware |

### Modal Deployment Steps (preserved for reference)

1. `pip install modal && modal setup`
2. Accept Llama license at https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
3. `modal secret create huggingface HF_TOKEN=hf_xxx`
4. Deploy one model first: `modal deploy modal_serving.py::mistral_7b_app`
5. Smoke test: `modal run modal_serving.py::smoke_test --model mistral-7b`
6. Deploy remaining: deploy each `*_app` from modal_serving.py
7. `modal run modal_serving.py::write_endpoints` -> edit URLs -> save
8. Run evaluation: `python run_evaluation.py --models vllm:mistralai/Mistral-7B-Instruct-v0.3 --tasks B1 --max-instances 5 -y`

---

## Phase 3: Remote-First Infrastructure

**Goal**: Move all orchestration off the laptop onto a persistent server. Work continues 24/7 without the laptop. Visual monitoring via web dashboard.

### Architecture

```
Hetzner VPS (CPX21, $8/mo)                    External Services
┌──────────────────────────────────┐      ┌──────────────────────┐
│  systemd services                │      │  Anthropic API       │
│  ├── deepwork-daemon             │─────>│  OpenAI API          │
│  │   (TS orchestrator + API)     │      │  OpenRouter API      │
│  ├── deepwork-eval@.service      │─────>│  GitHub              │
│  │   (Python eval jobs)          │      │  Slack webhooks      │
│  └── deepwork-web                │      └──────────────────────┘
│      (Next.js dashboard backend) │
│                                  │      User (anywhere)
│  PostgreSQL                      │      ├── Browser -> dashboard
│  Git repo (source of truth)      │      ├── Slack -> notifications
│  Checkpoint files                │      ├── GitHub -> PRs, status
│  Session transcripts             │      └── SSH+tmux -> hands-on
└──────────────────────────────────┘
```

### 3.1 — VPS Foundation

**Goal**: Persistent Linux server with all dependencies, ready to take over from laptop.

- [ ] Provision Hetzner CPX21 (3 vCPU, 4GB RAM, 80GB SSD, ~$8/mo)
- [ ] Ubuntu 24.04, SSH keys, firewall (port 22 + 443), fail2ban
- [ ] Install: Node.js 22 LTS, Python 3.12, Git, tmux, Modal CLI
- [ ] Clone repo, install npm + Python deps
- [ ] Copy `.env` with all keys (Anthropic, OpenAI, OpenRouter, Slack webhook)
- [ ] Verify: `node orchestrator/dist/index.js list` reads project state
- [ ] Move running eval jobs to VPS (git pull, pip install, `python run_evaluation.py --resume`)

### 3.2 — Restore Orchestrator TypeScript Sources

**Goal**: Full TypeScript source for all orchestrator modules (7 exist only as compiled JS).

Existing source (5 files):
- `orchestrator/src/index.ts` — CLI entry point
- `orchestrator/src/project-manager.ts` — project discovery/scoring
- `orchestrator/src/session-manager.ts` — session lifecycle
- `orchestrator/src/git-engine.ts` — git operations (worktrees, PRs)
- `orchestrator/src/yaml.ts` — YAML parsing utilities

Need to restore from compiled JS (7 files):
- [ ] `daemon.ts` — main polling loop, project scoring, budget checks, session scheduling
- [ ] `session-runner.ts` — Claude Agent SDK integration, headless session execution
- [ ] `budget-tracker.ts` — spending limits, daily/monthly tracking, alert levels
- [ ] `notifier.ts` — Slack webhook notifications
- [ ] `monitor.ts` — health checks, heartbeat, disk/memory monitoring
- [ ] `transcript-writer.ts` — session transcript recording to JSONL
- [ ] `logger.ts` — structured logging

Wire up:
- [ ] SessionManager calls SessionRunner (currently prints "launch manually")
- [ ] Add CLI subcommands: `daemon`, `health`, `eval`, `logs`
- [ ] Create systemd service files for daemon and eval jobs

### 3.3 — Database

**Goal**: PostgreSQL for queryable state, dashboards, and historical tracking. Git/YAML stays as source of truth.

**Why Postgres** (not SQLite, not files-only):
- Web dashboard needs fast queries ("accuracy by model for last 3 runs")
- Concurrent reads (dashboard) + writes (daemon/eval) without locking
- Historical tracking (budget burn rate over time, eval progress curves)
- Full-text search on session transcripts and decisions

**Schema (core tables)**:
- [ ] `projects` — id, name, phase, status, updated_at (mirrors status.yaml)
- [ ] `eval_results` — instance_id, model, task, condition, difficulty, correct, latency_ms, response, created_at
- [ ] `eval_runs` — run_id, model, task, condition, status, started_at, completed_at, accuracy, instance_count
- [ ] `sessions` — session_id, project, prompt, model, tokens_used, cost_usd, commits_created, started_at, duration_s
- [ ] `decisions` — project, date, decision, rationale (mirrors status.yaml decisions_made)
- [ ] `budget_events` — timestamp, project, event_type, amount_usd, daily_total, monthly_total
- [ ] `checkpoints` — model, task, condition, completed_count, total_count, last_updated (aggregated view)

**Data flow**:
- Eval scripts write JSONL checkpoints (crash-safe) AND insert into Postgres
- Daemon syncs status.yaml changes into `projects` table on each cycle
- Budget tracker writes to both `spending.jsonl` and `budget_events` table
- Dashboard reads only from Postgres (fast, no file parsing)

### 3.4 — API Layer

**Goal**: REST + WebSocket API that the dashboard (and future tools) consume.

- [ ] REST endpoints:
  - `GET /api/projects` — list all projects with current status
  - `GET /api/projects/:id/eval` — eval progress, accuracy tables, checkpoint status
  - `GET /api/projects/:id/sessions` — session history with transcripts
  - `GET /api/projects/:id/decisions` — decision log
  - `GET /api/budget` — current spend, daily/monthly totals, burn rate
  - `GET /api/health` — daemon status, disk, memory, active processes
  - `POST /api/eval/start` — trigger eval run with model/task/condition params
  - `POST /api/eval/stop` — gracefully stop a running eval
- [ ] WebSocket:
  - `ws /api/ws/eval-progress` — real-time eval instance completions
  - `ws /api/ws/logs` — live daemon/eval log stream
- [ ] Auth: API key in header (single-user system, keep it simple)

**Implementation**: Add Express/Fastify routes to the daemon process itself (it's already a long-running Node.js process). No separate API service needed.

### 3.5 — Web Dashboard Integration

**Goal**: Visual monitoring of eval progress, budget, project state accessible from anywhere.

This integrates with the deepwork.site frontend. Two options:

**Option A — Dashboard on VPS**: Next.js app on the VPS behind nginx, accessible at `dashboard.deepwork.site`. Self-contained, all data local.

**Option B — Dashboard on Vercel/Cloudflare, API on VPS**: Frontend deployed to edge CDN (fast loads from anywhere), calls VPS API. Requires exposing VPS API to internet (HTTPS + auth).

**Recommended: Option B** — keeps the website deployment workflow you already have, only the API lives on the VPS.

Dashboard views:
- [ ] **Eval Monitor**: Real-time progress bars per model/task/condition, accuracy heatmap, ETA
- [ ] **Results Explorer**: Interactive accuracy tables with difficulty breakdowns, CoT lift visualization
- [ ] **Budget Tracker**: Daily/monthly spend chart, per-model cost breakdown, burn rate projection
- [ ] **Project Overview**: Phase status, recent sessions, decision log, next steps
- [ ] **Session Viewer**: Browse session transcripts, see what Claude decided and why
- [ ] **System Health**: Daemon uptime, active processes, disk usage, API rate limit status

### 3.6 — Notifications and Remote Monitoring

**Goal**: Know what's happening without checking the dashboard.

- [ ] Slack webhook integration (Notifier class already exists in orchestrator)
- [ ] Notifications for: eval completion, budget warnings, daemon failures, session outcomes
- [ ] Daily summary cron: budget status, eval progress, any errors
- [ ] GitHub Actions: compile LaTeX paper on push to research branch
- [ ] Nightly backup: rsync logs/transcripts to Hetzner Storage Box ($4/mo for 1TB)

---

## Phase 4: Paper Completion

After empirical results are collected and analyzed:

- [ ] Run full analysis pipeline on 9-model dataset (121,614 instances)
- [ ] Write Section 5 (Experiments) with generated figures and tables
- [ ] Complete Discussion section with empirical findings
- [ ] Finalize Related Work
- [ ] Write Appendix (full result tables, additional figures)
- [ ] Internal review and revision
- [ ] Submit to NeurIPS 2026

---

## Budget Summary

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Hetzner CPX21 VPS | $8 | 3 vCPU, 4GB RAM, 80GB SSD |
| Hetzner Storage Box | $4 | 1TB backup |
| Anthropic API | $200-400 | Eval + Claude Agent SDK sessions |
| OpenAI API | $50-100 | Eval only |
| OpenRouter API | $1-5 | Open-source model eval (extremely cheap) |
| Modal GPU | $0 | Not needed — OpenRouter replaced Modal for eval |
| Slack | $0 | Free tier |
| **Total** | **$263-517** | Within $1,000/month budget |

---

## Implementation Order

Phase 2 eval is largely complete (9/12 models). Immediate priorities:

1. **Analysis Pipeline** — Run full analysis on 121,614 instances. Day 1.
2. **Pending Model Decisions** — Decide on Sonnet 4.6, Opus 4.6, o3. Day 1-2.
3. **Budget_cot Recalibration** — Fix B2 budget, re-run affected conditions. Day 2-3.
4. **Paper Section 5** — Write experiments section with figures. Days 3-7.
5. **VPS Foundation** (3.1) — provision, clone, set up. Days 7-9.
6. **Restore Orchestrator** (3.2) — TS sources, wire daemon, systemd. Days 9-12.
7. **Database** (3.3) — Postgres schema, eval result ingestion. Days 12-14.
8. **API + Dashboard** (3.4-3.5) — REST/WebSocket + frontend. Days 14-21.
9. **Notifications** (3.6) — Slack, cron summaries, backups. Day 21.
10. **Paper Completion** (Phase 4) — Discussion, Related Work, Appendix. Ongoing.
