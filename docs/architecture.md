# Serre AI Platform Architecture

**Version**: 1.0
**Updated**: 2026-03-11
**Status**: Current state documented, target state specified

---

## 1. System Architecture

```
                          +-----------------------+
                          |     Human Layer       |
                          |                       |
                          |  Slack     CLI        |
                          |  GitHub    Dashboard  |
                          +----+------+-----+----+
                               |      |     |
                   +-----------+      |     +-------------+
                   |                  |                    |
                   v                  v                    v
+------------------+---+  +----------+---------+  +-------+----------+
|  deepwork.site       |  |  CLI (Ink/React)    |  |  Slack Webhooks  |
|  Astro + Tailwind    |  |  Terminal dashboard |  |  Notifications   |
|  Vercel deploy       |  |  Read-only status   |  |  Budget alerts   |
+---------+------------+  +----------+----------+  +------------------+
          |                          |
          |    REST + WebSocket      |  SSH / local
          +----------+---------------+
                     |
    +================+==========================================+
    |            Hetzner VPS (CPX21)                            |
    |            2 vCPU / 4 GB RAM / 80 GB NVMe                |
    |            Ubuntu 24.04 / 89.167.5.50                    |
    |                                                          |
    |  +---------------------------------------------------+   |
    |  |  nginx (port 80/443)                               |  |
    |  |  Reverse proxy -> localhost:3001                    |  |
    |  |  TLS via Let's Encrypt (certbot)                   |  |
    |  +----------------------------+-----------------------+  |
    |                               |                          |
    |  +----------------------------v-----------------------+  |
    |  |  deepwork-daemon (systemd)                          | |
    |  |                                                     | |
    |  |  Daemon Loop (30 min poll)                          | |
    |  |  +-- Score active projects                          | |
    |  |  +-- Launch Claude Agent SDK sessions               | |
    |  |  +-- Track budget, log activity                     | |
    |  |                                                     | |
    |  |  Express REST API (port 3001)                       | |
    |  |  +-- /api/health                                    | |
    |  |  +-- /api/projects, /api/projects/:id/eval          | |
    |  |  +-- /api/projects/:id/sessions                     | |
    |  |  +-- /api/projects/:id/decisions                    | |
    |  |  +-- /api/budget                                    | |
    |  |  +-- /api/eval/start, /api/eval/stop                | |
    |  |                                                     | |
    |  |  WebSocket (/api/ws)                                | |
    |  |  +-- eval-progress channel                          | |
    |  |  +-- logs channel                                   | |
    |  +----------------------------+-----------------------+  |
    |                               |                          |
    |  +----------------------------v-----------------------+  |
    |  |  PostgreSQL 16                                      | |
    |  |  Database: deepwork                                 | |
    |  |  Tables: projects, eval_results, eval_runs,         | |
    |  |          sessions, decisions, budget_events          | |
    |  |  Materialized views: checkpoints                    | |
    |  |  Views: v_accuracy_heatmap, v_cot_lift,             | |
    |  |         v_daily_spend                               | |
    |  |  121K+ eval result rows                             | |
    |  +----------------------------------------------------+  |
    |                                                          |
    |  +----------------------------------------------------+  |
    |  |  File Storage                                       | |
    |  |  Git repo (source of truth)                         | |
    |  |  .worktrees/<project>/ (isolated sessions)          | |
    |  |  .logs/activity.jsonl, .logs/spending.jsonl          | |
    |  |  .sessions/<project>/<month>/<id>.jsonl              | |
    |  |  benchmarks/results/checkpoints/ (JSONL)             | |
    |  +----------------------------------------------------+  |
    +===========================================================+
                     |               |              |
                     v               v              v
          +----------+--+  +--------+------+  +----+----------+
          | Anthropic    |  | OpenAI        |  | OpenRouter    |
          | API          |  | API           |  | API           |
          | Claude 4.6   |  | GPT-4o, o3   |  | Llama, Qwen   |
          | Haiku 4.5    |  | GPT-4o-mini  |  | Gemma, etc.   |
          +--------------+  +---------------+  +---------------+
                     |
                     v
          +----------+--+
          | GitHub       |
          | Repository   |
          | PR workflow  |
          | Branch prot. |
          +--------------+
```

---

## 2. Current Implementation

### 2.1 Orchestrator (`orchestrator/src/`)

The orchestrator is a TypeScript Node.js application using ESM modules. It manages the full lifecycle of autonomous research sessions.

**Dependencies**: `@anthropic-ai/claude-agent-sdk`, `express`, `pg`, `ws`

#### Source Files

| File | Lines | Purpose |
|------|-------|---------|
| `index.ts` | 39 | CLI entry point. Commands: `start <project>`, `list`. Wires ProjectManager, GitEngine, SessionManager. |
| `daemon.ts` | ~367 | Main polling loop. Scores projects, launches sessions, manages budget checks, heartbeat, graceful shutdown via SIGTERM/SIGINT. |
| `session-manager.ts` | 132 | Creates worktrees, builds agent prompts from BRIEF.md + CLAUDE.md + status.yaml, manages session lifecycle. |
| `session-runner.ts` | ~168 | Claude Agent SDK integration. Calls `query()` with streaming, tracks tokens/cost, handles timeouts and errors, writes transcripts. |
| `git-engine.ts` | 325 | Full git automation: branches, worktrees, commits, push/pull, PR creation via `gh` CLI, milestone PRs with commit lists. |
| `api.ts` | 510 | Express REST API + WebSocket. Routes for projects, eval data, budget, health, eval control. CORS, API key auth, PostgreSQL pool (max 10 connections). |
| `project-manager.ts` | 148 | YAML-based project CRUD. Lists projects from `projects/` directory, reads/writes status.yaml, creates project scaffolding (paper/, src/, data/, notes/), manages decisions. |
| `budget-tracker.ts` | ~143 | Reads spending from `.logs/spending.jsonl`. Tracks daily/monthly limits, per-project spending. Alert levels: ok, warning (80%), critical (95%), exceeded (100%). |
| `monitor.ts` | 196 | Health checks: daemon heartbeat age, budget status, disk usage (`df -k`), recent error count (24h window), last activity timestamp. |
| `notifier.ts` | 99 | Slack webhook notifications. Sends Block Kit messages with severity icons. Reads webhook URL from env or config.yaml. Fire-and-forget with 5s timeout. |
| `logger.ts` | 83 | Append-only JSONL activity log (`.logs/activity.jsonl`). 17 event types covering sessions, git, budget, daemon lifecycle. |
| `transcript-writer.ts` | 53 | Session transcript JSONL files in `.sessions/<project>/<month>/<id>.jsonl`. 50MB safety cap per file. |
| `yaml.ts` | 75 | Minimal YAML parser for status files. JSON-first with fallback to basic YAML parsing. Stringify outputs JSON (for machine-written files). |

#### Module Dependency Graph

```
index.ts
  +-> project-manager.ts  --> yaml.ts
  +-> session-manager.ts  --> project-manager.ts, git-engine.ts
  +-> git-engine.ts

daemon.ts
  +-> project-manager.ts
  +-> session-manager.ts
  +-> git-engine.ts
  +-> budget-tracker.ts   --> yaml.ts (config.yaml), logger.ts
  +-> logger.ts
  +-> notifier.ts         --> yaml.ts (config.yaml)

session-runner.ts
  +-> git-engine.ts
  +-> transcript-writer.ts
  +-> @anthropic-ai/claude-agent-sdk

api.ts
  +-> express, ws, pg
  +-> (reads from PostgreSQL, not from other modules)

monitor.ts
  +-> budget-tracker.ts
  +-> logger.ts
```

### 2.2 Database Schema

PostgreSQL 16, deployed on the VPS. Git/YAML remains the source of truth; Postgres is the read-optimized query layer for dashboards.

#### Tables

**`projects`** -- mirrors status.yaml per project
```sql
id              TEXT PRIMARY KEY        -- e.g. 'reasoning-gaps'
name            TEXT NOT NULL
title           TEXT NOT NULL
venue           TEXT                    -- e.g. 'NeurIPS 2026'
phase           TEXT DEFAULT 'research'
status          TEXT CHECK (IN: active, paused, review, completed)
confidence      REAL DEFAULT 0.5
current_focus   TEXT
current_activity TEXT
notes           TEXT
branch          TEXT
created_at      TIMESTAMPTZ
updated_at      TIMESTAMPTZ
```

**`eval_results`** -- individual evaluation instances (121K+ rows)
```sql
PRIMARY KEY (instance_id, model, condition)
instance_id     TEXT        -- e.g. 'B1_masked_majority_d1_0000'
model           TEXT        -- e.g. 'claude-haiku-4-5-20251001'
task            TEXT        -- e.g. 'B1_masked_majority'
condition       TEXT        -- 'direct', 'short_cot', 'budget_cot'
difficulty      INTEGER
correct         BOOLEAN
extracted_answer TEXT
ground_truth    TEXT
latency_ms      REAL
response        TEXT        -- full model response
metadata        JSONB       -- is_refusal, prompt_sent, etc.
```

**`eval_runs`** -- aggregated run-level tracking (243 rows)
```sql
run_id          TEXT PRIMARY KEY
model, task, condition  TEXT
status          TEXT CHECK (IN: running, completed, failed, cancelled)
started_at, completed_at  TIMESTAMPTZ
accuracy        REAL        -- 0.0-1.0
instance_count  INTEGER
total_expected  INTEGER
metadata        JSONB       -- avg_latency, cost_usd
```

**`sessions`** -- Claude agent session records
```sql
session_id      TEXT PRIMARY KEY
project         TEXT REFERENCES projects(id)
agent_type      TEXT CHECK (IN: researcher, writer, reviewer, editor, strategist)
model           TEXT
tokens_used     INTEGER
cost_usd        REAL
commits_created INTEGER
status          TEXT CHECK (IN: running, completed, failed, cancelled)
error           TEXT
started_at      TIMESTAMPTZ
duration_s      REAL
```

**`decisions`** -- autonomous decision log
```sql
id              SERIAL PRIMARY KEY
project         TEXT REFERENCES projects(id)
date            DATE
decision        TEXT
rationale       TEXT
```

**`budget_events`** -- per-API-call spending records
```sql
id              SERIAL PRIMARY KEY
timestamp       TIMESTAMPTZ
project         TEXT
session_id      TEXT
agent_type      TEXT
tokens_input, tokens_output  INTEGER
cost_usd        REAL
model           TEXT
daily_total, monthly_total   REAL    -- running totals at event time
```

#### Materialized Views

**`checkpoints`**: Pre-aggregated accuracy by (model, task, condition). Refreshed via `refresh_checkpoints()` function using `REFRESH MATERIALIZED VIEW CONCURRENTLY`.

#### Convenience Views

- **`v_accuracy_heatmap`**: model x task x condition accuracy grid
- **`v_cot_lift`**: Accuracy delta between direct and short_cot per model/task
- **`v_daily_spend`**: Daily budget burn by project and model

### 2.3 REST API

All endpoints require `X-Api-Key` header (except `/api/health`). WebSocket authenticates via `?api_key=` query parameter.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Public. Uptime, memory, CPU count, DB status |
| GET | `/api/projects` | List all projects from PostgreSQL |
| GET | `/api/projects/:id/eval` | Checkpoint progress, accuracy by difficulty, recent runs |
| GET | `/api/projects/:id/sessions` | Session history (paginated: `?limit=&offset=`) |
| GET | `/api/projects/:id/decisions` | Decision log for project |
| GET | `/api/budget` | Daily/monthly spend, by-project, by-model, 7-day burn rate |
| POST | `/api/eval/start` | Trigger eval run (model, task, condition, instances) |
| POST | `/api/eval/stop` | Cancel running eval (runId) |
| WS | `/api/ws` | Subscribe to channels: `eval-progress`, `logs` |

### 2.4 VPS Infrastructure

**Server**: Hetzner CPX21, 2 vCPU (AMD EPYC), 4 GB RAM, 80 GB NVMe, Ubuntu 24.04
**IP**: 89.167.5.50
**Cost**: ~$8/month

**systemd services**:
- `deepwork-daemon.service`: Runs the orchestrator daemon + API. Auto-restart on failure.
- `postgresql.service`: PostgreSQL 16

**nginx**: Reverse proxy on port 80, forwards to `localhost:3001`. HTTPS via certbot planned.

**Security**:
- UFW: ports 22 (SSH), 80, 443 only
- fail2ban active
- `.env` with chmod 600 (API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY, DEEPWORK_API_KEY)
- API key authentication on all non-health endpoints

**Python environment**: `~/deepwork/.venv` with analysis and eval dependencies for benchmark execution.

### 2.5 Frontend

**Site** (`site/`): Astro framework with Tailwind CSS, neo-brutalist design using IBM Plex Mono. Three dashboard pages with mock data:
- `dashboard/index.astro` -- project overview
- `dashboard/eval.astro` -- evaluation monitor
- `dashboard/budget.astro` -- budget tracker

Currently deployed on Vercel with mock data. Wiring to the VPS REST API is the next infrastructure task.

**CLI** (`cli/`): Ink/React terminal dashboard (3 source files: `index.tsx`, `app.tsx`, `data.ts`). Read-only status display.

### 2.6 Git Workflow

```
main                                        # Reviewed, stable
+-- research/reasoning-gaps                 # Active project branch
+-- research/agent-failure-taxonomy         # Active project branch
+-- paper/<project>/<version>               # Paper draft branches
+-- feature/<description>                   # Platform infrastructure
```

Each agent session operates in an isolated git worktree at `.worktrees/<project>/`. The session runner:
1. Creates or reuses worktree on the project's research branch
2. Agent makes conventional commits: `type(project): description`
3. Pushes after every commit
4. Creates a PR to main at milestones (phase transitions, significant findings)

---

## 3. Project Scoring Algorithm

The daemon scores all active projects each cycle to determine which gets a session slot. Implemented in `daemon.ts` `scoreProjects()`.

```
Score = base + deadline + staleness + steps + confidence - failures - budget_overrun

Components:
  +1   base                       Every active project gets minimum viability
  +10  deadline < 4 weeks         Upcoming venue deadlines get priority
  +5   no update in > 24 hours    Stale projects get attention
  +3   pending next_steps          Projects with clear work items
  +2   confidence >= 0.7          High-confidence projects worth investing in
  -5   confidence < 0.3           Low-confidence projects may need rethinking
  -N   failure backoff            min(failures * 5, 20) -- exponential penalty
  -10  budget exceeded            Per-project daily budget = dailyBudgetUsd / activeProjectCount
```

Projects are sorted by score descending. Those already running or with score <= 0 are filtered out. Top N candidates (where N = available session slots) are launched.

**Session slot allocation**: `maxConcurrentSessions` (default 2) minus currently running sessions.

**Failure backoff**: Each failed session increments a counter. Penalty = `min(failures * 5, 20)`. Successful sessions clear the counter.

**Phase-to-agent mapping**:
| Phase | Agent Type |
|-------|-----------|
| research | researcher |
| literature-review | researcher |
| drafting | writer |
| revision | reviewer |
| final | editor |

---

## 4. Session Lifecycle

```
                                  +-----------+
                                  | Daemon    |
                                  | cycle()   |
                                  +-----+-----+
                                        |
                              scoreProjects()
                                        |
                                        v
                               +--------+--------+
                               | SessionManager  |
                               | startProject()  |
                               +--------+--------+
                                        |
                          createWorktree() via GitEngine
                                        |
                                        v
                               +--------+--------+
                               | SessionRunner   |
                               | run()           |
                               +--------+--------+
                                        |
                          buildPrompt():
                          1. CLAUDE.md (global)
                          2. .claude/agents/<type>.md
                          3. projects/<name>/CLAUDE.md
                          4. projects/<name>/status.yaml
                          5. Session workflow instructions
                                        |
                                        v
                               +--------+--------+
                               | Claude Agent    |
                               | SDK query()     |
                               +--------+--------+
                                        |
                          Streaming messages:
                          - Tool calls (Read, Write, Bash, etc.)
                          - Transcript written to JSONL
                          - Agent makes commits in worktree
                                        |
                                        v
                               +--------+--------+
                               | Session Result  |
                               +--------+--------+
                                        |
                          Record: tokens, cost, commits,
                          duration, status, errors
                                        |
                        +---------------+--------------+
                        |               |              |
                        v               v              v
                  BudgetTracker   ActivityLogger   Notifier
                  (spending.jsonl) (activity.jsonl) (Slack)
```

**Session constraints** (from `session-runner.ts` and `daemon.ts`):
- Default max turns: 50
- Default max duration: 45 minutes
- Hard duration limit (daemon enforced): 60 minutes
- Retry: 1 retry after 5 minute delay on failure
- Max backoff between retries: 4 hours

**Cost tracking**: Uses Claude Sonnet 4 pricing ($3/M input, $15/M output). The SDK's `total_cost_usd` field is preferred when available, falling back to manual calculation.

**Allowed tools for agents**: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
**Permission mode**: `acceptEdits` (auto-approve file modifications)

---

## 5. Data Flow Diagrams

### 5.1 Research Idea to Published Paper

```
ideas.yaml             BRIEF.md                      status.yaml
(ranked backlog)       (research goals)              (machine state)
     |                      |                             |
     v                      v                             v
  [Scout]  -------->  [Researcher]  -------->  [Theorist]
  Daily scan           Literature review        Formal framework
  arXiv + S2           Gap identification       Proofs, definitions
                       Hypothesis dev.
                            |
                            v
                     [Experimenter]
                      Benchmark design
                      Run evaluations
                      Analyze results
                            |
                            v
                       [Writer]
                      Draft paper sections
                      LaTeX in paper/
                            |
                            v
                       [Critic]  <---- adversarial review
                      Read-only analysis    |
                      Structured review     |
                            |               |
               +---------- verdict --------+
               |            |
               v            v
          [Revise]     [Approve]
           loop          |
           (max 3)       v
                      [Editor]
                      Camera-ready
                      Venue formatting
                            |
                            v
                      paper.pdf
                      + HuggingFace dataset
                      + GitHub release
                      + Blog draft
```

### 5.2 Evaluation Data Flow

```
API Request (Anthropic/OpenAI/OpenRouter)
     |
     v
JSONL Checkpoint                    PostgreSQL
(.../checkpoints/<model>_<task>_<condition>.jsonl)
     |                                   ^
     |  backfill_to_postgres.py          |
     +---------------------------------->+
     |                                   |
     v                                   v
Analysis Scripts               Dashboard Queries
(analysis.py)                  (api.ts REST endpoints)
     |                                   |
     v                                   v
LaTeX Tables + Figures          Astro Dashboard Pages
(paper/tables/, paper/figures/)  (deepwork.site)
     |
     v
Paper (main.tex)
```

Data flows through two parallel paths: JSONL checkpoints are the durable source of truth (version-controlled, crash-safe), while PostgreSQL provides fast aggregation for dashboard queries. The `checkpoints` materialized view pre-computes accuracy by (model, task, condition) and is refreshed after bulk inserts.

### 5.3 Decision Flow

**Current state** (fully autonomous):
```
Agent encounters decision
     |
     v
Extended thinking (highest reasoning level)
     |
     v
Make decision immediately
     |
     v
Log to status.yaml decisions_made:
  - date: 2026-03-11
    decision: "Use bootstrap confidence intervals"
    rationale: "Non-parametric, no distribution assumptions"
     |
     v
Continue work
```

**Target state** (hybrid with optional human oversight):
```
Agent encounters decision
     |
     +-- Low stakes: decide autonomously, log to status.yaml
     |
     +-- High stakes: write to decisions_pending in status.yaml
              |
              v
         Slack notification with decision summary
              |
              v
         Human responds (Slack reaction or /decide command)
              |
              v
         decision_router resolves in status.yaml
              |
              v
         Next agent session reads resolved decision
```

---

## 6. Security Model

### API Key Management

| Key | Storage | Purpose |
|-----|---------|---------|
| ANTHROPIC_API_KEY | .env (chmod 600) | Claude SDK sessions, Haiku eval |
| OPENAI_API_KEY | .env | GPT-4o, GPT-4o-mini eval |
| OPENROUTER_API_KEY | .env | Open-source model eval |
| DEEPWORK_API_KEY | .env | REST API + WebSocket authentication |
| SLACK_WEBHOOK_URL | .env / config.yaml | Notifications |
| FIRECRAWL_API_KEY | .env | Web scraping for literature review |

**Principles**:
- `.env` is gitignored, chmod 600 on VPS
- API keys never appear in logs or transcripts
- API key auth on all REST endpoints except `/api/health`
- WebSocket auth via query parameter (single-user system, acceptable risk)
- No OAuth or user accounts -- single-operator system

### VPS Hardening

- UFW firewall: only ports 22, 80, 443
- fail2ban for SSH brute-force protection
- SSH key-only auth (no password)
- systemd service runs as dedicated user
- PostgreSQL listens on localhost only (no external connections)

### Agent Sandboxing

- Each agent session runs in an isolated git worktree
- `permissionMode: "acceptEdits"` allows file modifications only within the worktree
- Bash tool access is unrestricted (needed for git, LaTeX compilation, analysis scripts)
- Agents cannot access `.env` directly (it's in the repo root, not the worktree)

---

## 7. Deployment

### systemd Service

```ini
# /etc/systemd/system/deepwork-daemon.service
[Unit]
Description=Serre AI Research Platform Daemon
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=deepwork
WorkingDirectory=/home/deepwork/deepwork
ExecStart=/usr/bin/node orchestrator/dist/index.js run
Restart=always
RestartSec=10
EnvironmentFile=/home/deepwork/deepwork/.env

[Install]
WantedBy=multi-user.target
```

### nginx Configuration

```nginx
server {
    listen 80;
    server_name api.deepwork.site;

    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

WebSocket upgrade headers are included for `/api/ws` support.

### PostgreSQL Setup

```bash
sudo -u postgres createuser deepwork
sudo -u postgres createdb -O deepwork deepwork
psql -U deepwork -d deepwork -f orchestrator/sql/001_initial_schema.sql
```

Connection string: `postgresql://deepwork:deepwork@localhost:5432/deepwork`
Pool config: max 10 connections, 30s idle timeout, 5s connection timeout.

### Build and Deploy

```bash
cd orchestrator && npm run build   # tsc -> dist/
sudo systemctl restart deepwork-daemon
sudo systemctl status deepwork-daemon
```

### Backup Strategy

**Planned**: Nightly backup to Hetzner Storage Box (~$4/month)

```bash
# PostgreSQL dump
pg_dump deepwork | gzip > /backup/deepwork-$(date +%F).sql.gz

# JSONL checkpoints (rsync incremental)
rsync -az benchmarks/results/checkpoints/ /backup/checkpoints/

# Git is self-backing via GitHub remote
```

---

## 8. Target Architecture

The following sections describe planned extensions to the current system.

### 8.1 Research Radar Service

A daily cron job that scans academic literature for relevance to active projects and potential new research directions.

**Trigger**: Daily at 06:00 UTC via systemd timer
**Sources**: arXiv API (RSS feeds by category), Semantic Scholar API (citation graph, related papers)
**Process**:
1. Fetch new papers from tracked arXiv categories (cs.AI, cs.CL, cs.LG, stat.ML)
2. Score relevance against active project keywords and research questions
3. Check citation overlap with project bibliographies
4. Write daily digest to Slack
5. Append high-scoring papers to `ideas.yaml` with relevance scores

**Output format** (Slack):
```
Research Radar - 2026-03-12
3 papers relevant to reasoning-gaps:
  - "Chain-of-Thought Scaling Laws" (Chen et al., 2026) - score: 0.87
  - "Formal Verification of LLM Reasoning" (Park & Kim, 2026) - score: 0.72
  - "Benchmark Suite for Deductive Reasoning" (Wu et al., 2026) - score: 0.68
1 potential new direction:
  - "Compositional Generalization in Code LLMs" - score: 0.81
```

**Budget**: $2/day max (primarily Semantic Scholar API, which is free; cost is the Scout agent session)

### 8.2 Multi-Agent Pipeline

For each project, specialized agents run in a defined sequence with quality gates between stages.

```
Scout (daily)
  |
  v
Researcher (phase: research)
  |
  v
Theorist (phase: research, formal_framework in progress)
  |
  v
Experimenter (phase: empirical-evaluation)
  |
  v
Writer (phase: drafting)
  |
  v
Critic (post-draft) -----> verdict: revise? ---+
  |                                             |
  | verdict: accept                             |
  v                                             v
Editor (phase: final)                    Writer (revision)
  |                                             |
  v                                             v
Camera-ready paper                       Critic (re-review)
                                          max 3 cycles
```

See `docs/agents.md` for full agent specifications.

### 8.3 Quality Gate System

Automated checkpoints between phases. Each gate has explicit pass/fail criteria.

| Gate | From | To | Pass Criteria |
|------|------|----|---------------|
| Literature Gate | research | research (formal) | >= 20 papers reviewed, gap clearly identified, research questions formalized |
| Framework Gate | research | empirical-evaluation | All definitions precise, main theorems stated, proof sketches for key claims |
| Experiment Gate | empirical-evaluation | drafting | >= 3 model families tested, bootstrap CIs computed, pre-registered analyses complete |
| Draft Gate | drafting | review | All sections present, figures/tables generated, related work covers key papers |
| Critic Gate | review | final | Critic verdict = "accept", all major weaknesses addressed, novelty claims validated |
| Camera-Ready Gate | final | completed | LaTeX compiles cleanly, venue style applied, supplementary materials complete |

**Failure behavior**: Gate failure triggers a revision loop back to the previous phase's agent. The reason for failure is written to `status.yaml` and becomes part of the next agent's prompt context.

### 8.4 State Management Hierarchy

Five layers of state, from machine-parseable to human-auditable:

```
Layer 1: status.yaml (per project)
  - Current phase, confidence, next_steps
  - Decisions made and pending
  - Machine-readable, agent-writable
  - Updated after every significant action

Layer 2: research-log.md (per project)
  - Append-only narrative log
  - Findings, failed approaches, key insights
  - Human-readable research diary

Layer 3: ideas.yaml (global)
  - Ranked research idea backlog
  - Scout appends, human curates
  - Fields: title, description, relevance_score, source, date

Layer 4: Git history
  - Full audit trail of every change
  - Conventional commits enable automated changelogs
  - Branch structure shows project isolation

Layer 5: PostgreSQL
  - Queryable aggregates for dashboards
  - Eval results, session records, budget events
  - Derived from layers 1-4, not authoritative
```

### 8.5 Notification System

**Daily Digest** (06:00 UTC):
- Projects that advanced phases overnight
- Decisions made (with rationale summaries)
- Budget status (daily/monthly spend, burn rate)
- Eval completion status
- Critic verdicts from review cycles

**Real-Time Alerts**:
- Budget warning at 80% daily/monthly
- Budget critical at 95%
- Session failures (with error context)
- Phase transitions
- Critic "reject" verdicts (escalation to human)

**Channels**: Slack webhook (primary), email digest (planned)

### 8.6 Artifact Pipeline

Alongside each paper, automatically generate:

1. **HuggingFace Dataset Card**: For any benchmarks or datasets created. Includes task descriptions, data format, licensing, usage examples.
2. **GitHub Release**: Tagged release with compiled PDF, supplementary materials, benchmark code, analysis scripts.
3. **Blog Post Draft**: Lay-audience summary of findings. Markdown format ready for deepwork.site.
4. **Reproducibility Package**: Docker/requirements, random seeds, exact API versions, checkpoint files.

---

## 9. Scaling Plan

### Current: CPX21 (2 vCPU, 4 GB RAM)

- 2 concurrent agent sessions
- Single-process daemon + API
- PostgreSQL on same machine
- Sufficient for 2-3 active projects

### Near-term: CPX31 (4 vCPU, 8 GB RAM, ~$16/month)

- 4 concurrent agent sessions
- Co-located eval job execution (move from laptop)
- 2-4 GB swap as memory safety net
- Sufficient for 5-6 active projects

### Medium-term: Dedicated Server (~$40-60/month)

- 8+ vCPU, 32 GB RAM
- Local GPU inference via vLLM (Llama, Qwen for eval)
- PostgreSQL on dedicated storage
- 8+ concurrent agent sessions
- Multiple daemon processes with load balancing

### Architecture Changes at Scale

| Threshold | Change |
|-----------|--------|
| 4+ concurrent sessions | Add swap, increase pg connection pool |
| 6+ active projects | Split daemon and API into separate processes |
| GPU inference needed | Dedicated server or Modal for burst compute |
| Multi-user | Add OAuth, per-user API keys, RBAC |
| 10+ projects | Project queue with priority preemption |

**Key insight**: Agent sessions are API-bound (waiting on Anthropic/OpenAI responses), not CPU-bound. RAM is the limiting factor -- each Node.js process + Claude SDK session uses ~200-400 MB. Doubling RAM is consistently the highest-leverage upgrade.
