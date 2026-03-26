# Deepwork Roadmap

**Last updated**: 2026-03-21

Single source of truth for what's left to do. Organized by priority.

---

## 1. NeurIPS Submission — reasoning-gaps

**Deadline**: Abstract ~late May, full paper ~early June 2026
**Branch**: `research/reasoning-gaps`
**Phase**: `submission-prep`

All evaluations complete (12 models, 159,162 instances, tool-use + budget sweep done). Paper structurally complete at ~18 pages. What remains:

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | **Page compression (18→9 pages)** | Not started | Move detailed results to appendix, compress §3–§5. See `neurips-submission.md` for section-by-section plan |
| 1.2 | NeurIPS checklist + ethics statement | Not started | Blocked by 1.1 |
| 1.3 | Double-blind anonymization | Not started | "Deepwork Research" → "Anonymous", remove email |
| 1.4 | Supplementary materials package | Not started | Code, summary data, configs. See `SUPPLEMENTARY-MATERIALS-PLAN.md` |
| 1.5 | Figure quality pass (vector PDF, colorblind-safe, font sizes) | Not started | Blocked by 1.1 |
| 1.6 | Number consistency audit (209K instances, 12 models, all `\stat*` macros) | Not started | Blocked by 1.1 |
| 1.7 | Final LaTeX checks + proofreading | Not started | Blocked by 1.1–1.6 |
| 1.8 | Upload datasets to Zenodo + Hugging Face | Not started | Raw data too large for supplementary ZIP |
| 1.9 | Submit on OpenReview | Not started | Final step |

**Detailed plan**: `docs/roadmaps/neurips-submission.md` (Phase 3 sprint plan with agent assignments)
**Supplementary details**: `projects/reasoning-gaps/SUPPLEMENTARY-MATERIALS-PLAN.md`

---

## 2. Daemon — Make It Actually Work

**Just implemented** (Sprint 14–15, 2026-03-21): Fixed the work generation pipeline so the daemon can schedule meaningful sessions. Needs deploy + verification.

| # | Task | Status | Notes |
|---|------|--------|-------|
| 2.1 | Deploy Sprint 14–15 changes to VPS | Not started | Build, push, restart `deepwork-daemon.service` |
| 2.2 | Verify daemon generates briefs for `reasoning-gaps` | Not started | Check logs after next cycle |
| 2.3 | Verify no FK errors for ghost projects | Not started | `agent-failure-taxonomy`, `platform-engineering` should sync to DB |
| 2.4 | Verify `GET /api/planner/insights/reasoning-gaps` returns data | Not started | Was returning 503 |
| 2.5 | Verify daemon launches a writer session for `reasoning-gaps` | Not started | First real autonomous research session |

---

## 3. Infrastructure & Observability

VPS is live (Hetzner CPX21, daemon + API + PostgreSQL). Remaining hardening:

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 3.1 | SSL/HTTPS | High | Point `api.deepwork.site` DNS → 89.167.5.50, then `certbot --nginx` |
| 3.2 | Slack workspace + webhook | High | Daemon notifications (session complete, budget warnings, errors, eval results). `Notifier` class already built, just needs `SLACK_WEBHOOK_URL` in `.env`. See `docs/roadmaps/external-integrations.md` |
| 3.3 | Uptime monitoring | High | HTTP ping on `/api/health` with SMS/email alerts. Had an 11-hour VPS outage with zero alerting. Free tier on UptimeRobot or Betterstack covers this |
| 3.4 | Error tracking (Sentry) | Medium | Daemon silently swallows errors to journalctl. Sentry gives structured error tracking, deduplication, and alerts. Would have surfaced ghost project FK errors and planner 503s immediately |
| 3.5 | Nightly DB backup | Medium | Hetzner Storage Box ($4/mo), rsync cron |
| 3.6 | Merge `main` ↔ `research/reasoning-gaps` | Medium | Diverged. Conflicts in `.claude/agents/*.md`, `orchestrator/package.json`, site layout |
| 3.7 | VPS scale-up (CPX21→CPX31) | Low | 8GB RAM, 4 vCPU. Enables 4 concurrent sessions. ~$16/mo. Do when running >2 projects |

---

## 4. External Integrations

APIs and services that give the platform eyes on the research landscape, the community, and itself. Ordered by impact.

**Detailed plan**: `docs/roadmaps/external-integrations.md`

### 4.1 Semantic Scholar API (research awareness)
The single highest-value integration. Gives the scout agent and literature intelligence pipeline actual data to work with. Free API, no cost.
- Paper search by topic/keyword with embeddings
- Citation graph traversal (who cites what)
- Related paper recommendations
- Scoop detection (alert when someone publishes in your space)
- Author and venue metadata for knowledge graph enrichment
- **Feeds into**: §7.1 Literature Intelligence, scout agent, knowledge graph

### 4.2 arXiv API (daily paper feeds)
Daily ingestion of new papers in target categories (cs.CL, cs.AI, cs.LG, cs.CC). Free, no auth. Companion to Semantic Scholar — arXiv gives you the firehose, Semantic Scholar gives you the intelligence.
- **Feeds into**: §7.1 Literature Intelligence, scout agent

### 4.3 Hugging Face Hub API (publish benchmarks + datasets)
Publish ReasonGap benchmark suite, evaluation datasets, and model results. NeurIPS reviewers expect this. Community adoption = citations.
- Upload datasets with dataset cards
- Leaderboard for benchmark results
- Versioned releases tied to paper submissions
- **Feeds into**: §1 NeurIPS Submission (task 1.8), artifact release pipeline

### 4.4 Zenodo API (permanent DOIs)
Permanent citable identifiers for datasets and code. Reviewers and the community take your work more seriously with DOIs. Free, CERN-backed.
- Automatic DOI minting on upload
- Versioned deposits linked to GitHub releases
- Long-term archival guarantee
- **Feeds into**: §1 NeurIPS Submission (task 1.8), supplementary materials

### 4.5 OpenReview API (venue intelligence)
Access to accepted/rejected papers, reviewer comments, and decision data at target venues (NeurIPS, ICLR, ACL). Informs review simulation with real reviewer behavior instead of guesswork.
- Scrape reviewer comments on related papers at target venues
- Understand what reviewers care about (common objections, praise patterns)
- Track submission outcomes for positioning
- **Feeds into**: §7.2 Review Simulation

---

## 5. Next.js Dashboard (site-next)

Replaces the Astro static site with a full-featured Next.js app. Already scaffolded at `site-next/` with Next.js 16, React 19, TanStack Query, Tailwind.

**Detailed plans** (5 files in `docs/roadmaps/`):
- `nextjs-master-roadmap.md` — Overview + sprint sequence
- `nextjs-frontend.md` — App structure, design system, components, data layer
- `nextjs-infrastructure.md` — Vercel + VPS split, Auth.js, DNS, SSL
- `nextjs-openclaw-ui.md` — Collective intelligence UI (7 pages, ~35 components)
- `nextjs-pipelines-tooling.md` — Pipeline visualization, logging, budget dashboard

**Current state**: Sprint 10 pages/components exist. Needs wiring to live API data.

---

## 6. Adaptive Sessions

Sessions currently get a one-size-fits-all config (Sonnet, 50 turns, 45 min, all tools). Different tasks need different profiles.

**Key idea**: 11 session profiles (`deep_proof`, `literature_sweep`, `latex_debug`, `quick_fix`, `paper_writing`, etc.) with tailored model, thinking level, turn budget, tools, and context composition. Escalation from cheap→expensive models when tasks prove harder than expected. Cost optimization feedback loop.

**Estimated effort**: 13–17 hours
**Detailed plan**: `docs/roadmaps/adaptive-sessions.md`

---

## 7. Intelligence Stack — Future Features

These extend the platform's autonomous capabilities. Ordered by expected value.

### 7.1 Literature Intelligence
Monitor arXiv/Semantic Scholar for papers relevant to active projects. Embed new papers, match against knowledge graph, surface to planner. Depends on §4.1 (Semantic Scholar) and §4.2 (arXiv) integrations.
- **Effort**: 16–22 hours
- **Detail**: `docs/roadmaps/literature-intelligence.md`

### 7.2 Review Simulation
Synthetic reviewer personas predict acceptance probability. Run adversarial reviews before submission to catch weaknesses early. Quality improves dramatically with §4.5 (OpenReview) data on real reviewer behavior.
- **Effort**: 12–16 hours
- **Detail**: `docs/roadmaps/review-simulation.md`

### 7.3 Meta-Learning
Track session quality over time. Learn which profiles, models, and strategies work best per task type. Platform improves itself.
- **Effort**: 18–24 hours
- **Detail**: `docs/roadmaps/meta-learning.md`

### 7.4 Closed-Loop Experiments
Automated hypothesis → experiment → analysis → belief update cycle. Planner generates hypotheses, experiment runner tests them, knowledge graph updates.
- **Effort**: 18–23 hours
- **Detail**: `docs/roadmaps/closed-loop-experiments.md`

### 7.5 Cross-Project Intelligence
Knowledge graph queries across projects. Automatic insight transfer when findings in one project are relevant to another.
- **Effort**: 12–17 hours
- **Detail**: `docs/roadmaps/cross-project-intelligence.md`

---

## What's Done

Everything below is complete and the detailed planning docs are now archived reference only.

### Platform Foundation
- Git monorepo with orchestrator + cli + site-next workspaces
- TypeScript orchestrator: daemon, session runner, budget tracker, activity logger, API
- PostgreSQL 16: 9 schema migrations, 159K+ eval results, knowledge graph tables
- Express REST API + WebSocket on port 3001 (14 route modules)
- Hetzner VPS: Ubuntu 24.04, Node.js 22, systemd daemon, nginx reverse proxy
- Knowledge graph with pgvector embeddings, semantic search, contradiction detection
- Event bus (PostgreSQL LISTEN/NOTIFY) with handler registration
- Research planner with 5 strategies (gap-filling, contradiction, deadline, quality, collective)
- Verification layer (claim extraction, evidence linking, gap reports)
- Agent definitions: researcher, writer, reviewer, strategist, editor, experimenter, theorist, engineer, scout, critic
- OpenClaw collective: forum, messaging, predictions, rituals, governance, agent personas

### reasoning-gaps Research
- 12 models evaluated: Haiku 4.5, Sonnet 4.6, Opus 4.6, GPT-4o-mini, GPT-4o, o3, Llama 3.1 8B/70B, Ministral 8B, Mistral Small 24B, Qwen 2.5 7B/72B
- 159,162 evaluation instances across 9 tasks × 3+ conditions, zero failures
- Tool-use evaluation (B5+B6, 3 models)
- Budget sensitivity sweep (B2+B3, 5 multipliers, 3 models)
- Full analysis pipeline: 4 LaTeX tables, 5 PDF+PNG figures, bootstrap CIs
- Paper structurally complete (1,542 lines LaTeX, NeurIPS format)
- Auto-build pipeline on VPS: `POST /api/paper/build` → analyze → compile → zip

### Archived Planning Docs
These were useful during development but are now historical:
- `docs/EXECUTION-PLAN.md` — Sprint 1–5 plan (all complete)
- `INFRASTRUCTURE-ROADMAP.md` — Phases 1–4 complete (5–7 folded into §3 above)
- `projects/reasoning-gaps/EVAL-ROADMAP.md` — Phases 1–3 complete, Phase 4 superseded by `neurips-submission.md`
- `projects/reasoning-gaps/POST-EVALUATION-ACTION-PLAN.md` — Superseded by `neurips-submission.md`
- `openclaw/ROADMAP.md` — Sprints 1–8 complete
- `docs/roadmaps/knowledge-graph.md` — Implemented
- `docs/roadmaps/event-architecture.md` — Implemented
- `docs/roadmaps/research-planner.md` — Implemented
- `docs/roadmaps/verification-layer.md` — Implemented
