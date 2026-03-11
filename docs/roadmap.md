# Deepwork Platform Roadmap

**Single source of truth for what's done, what's next, and what's planned.**
Supersedes `INFRASTRUCTURE-ROADMAP.md` and `projects/reasoning-gaps/EVAL-ROADMAP.md`.

**Created**: 2026-03-11
**Updated**: 2026-03-11

---

## Completed Work

### Platform Foundation (2026-03-07 through 2026-03-11)

**Orchestrator** (`orchestrator/`):
- 10 TypeScript source files on `main`: `index.ts`, `api.ts`, `git-engine.ts`, `project-manager.ts`, `session-manager.ts`, `monitor.ts`, `notifier.ts`, `logger.ts`, `transcript-writer.ts`, `yaml.ts`
- 3 compiled-only JS modules (TS sources exist on VPS/research branch, not yet merged to `main`): `daemon.js`, `session-runner.js`, `budget-tracker.js`
- `index.ts` wired with `run` command: starts daemon loop + API server
- `api.ts`: REST endpoints (projects, eval, budget, health) + WebSocket
- `session-runner.js`: Claude Agent SDK integration (needs SDK package at runtime)
- Build passes cleanly on `main`

**Git Automation** (`git-engine.ts`):
- Worktree creation and management for isolated project sessions
- Branch creation, switching, commit, push
- PR creation via GitHub CLI

**Database**:
- PostgreSQL 16 on VPS, 6 tables: `projects`, `eval_results`, `eval_runs`, `sessions`, `decisions`, `budget_events`
- Materialized view + 3 standard views for dashboard queries
- 121,146 eval results backfilled from checkpoint files

**VPS** (Hetzner CPX21 at 89.167.5.50):
- Ubuntu 24.04, Node.js 22, Python 3.12
- systemd-managed daemon (`deepwork-daemon.service`), polling every 30 minutes, auto-restart
- nginx reverse proxy on port 80 -> Express on port 3001
- fail2ban, UFW (ports 22/80/443), API key auth, `.env` chmod 600
- Python venv with all analysis/eval dependencies
- 243 checkpoint files (201MB) transferred from local

**CLI** (`cli/`):
- Ink/React terminal dashboard (read-only)
- Project status, eval progress, budget views

**Site** (`site/`):
- Astro + Tailwind, neo-brutalist design, IBM Plex Mono
- Dashboard pages: overview (`index.astro`), eval monitor (`eval.astro`), budget tracker (`budget.astro`)
- Currently renders mock data (TODO markers for API integration)

**Agent Definitions** (`.claude/agents/`):
- `researcher.md`: literature review, formal framework, benchmark design
- `writer.md`: paper drafting, LaTeX formatting, section writing
- `reviewer.md`: internal review, quality checks, revision suggestions

### reasoning-gaps Project (NeurIPS 2026)

**Literature Review** (complete):
- 80+ papers synthesized across transformer expressiveness, circuit complexity, and reasoning benchmarks
- Key references: Merrill & Sabharwal (TACL 2022/2023, ICLR 2024), Li et al. (ICLR 2024), Dziri et al. (NeurIPS 2023), Mirzadeh et al. (ICLR 2025)
- Synthesis in `projects/reasoning-gaps/notes/00-literature-synthesis.md`

**Formal Framework** (complete):
- 6-type reasoning gap taxonomy grounded in TC^0/NC^1/P complexity classes
- 5 formal propositions with proofs and proof sketches
- Predictions matrix: which gap types respond to CoT, which don't
- Framework in `notes/05-formal-framework.md`, proofs in `notes/07-proposition-proofs.md`

**Benchmark Suite** (complete):
- ReasonGap suite: 9 diagnostic tasks (B1-B9) with controlled difficulty parameters
- B1: multi-step arithmetic, B2: formula evaluation, B3: list reversal, B4: variable binding, B5: graph reachability, B6: parity checking, B7: compositional semantics, B8: state tracking, B9: recursive pattern matching
- Known ground truth for all tasks, parameterized difficulty
- Evaluation protocol: 3 conditions per task (direct, chain-of-thought, budget-constrained CoT)
- Implementation in `benchmarks/`
- 4 model clients: Anthropic, OpenAI, OpenRouter, vLLM
- Checkpoint/resume (crash-safe JSONL), dynamic CoT budgets, parallel evaluation

**Empirical Evaluation** (9/12 models complete):
- 121,614 instances across 9 models x 9 tasks x 3 conditions, zero failures
- Completed models:

| Model | Family | Size | Avg Accuracy | Provider | Cost |
|-------|--------|------|-------------|----------|------|
| Qwen 2.5 72B | Qwen | 72B | 71.5% | OpenRouter | ~$0.04 |
| GPT-4o | GPT | -- | 68.4% | OpenAI | ~$18 |
| GPT-4o-mini | GPT | -- | 64.0% | OpenAI | ~$2 |
| Haiku 4.5 | Claude | -- | 62.8% | Anthropic | ~$15 |
| Llama 3.1 70B | Llama | 70B | 62.5% | OpenRouter | ~$0.04 |
| Ministral 8B | Mistral | 8B | 62.2% | OpenRouter | ~$0.03 |
| Mistral Small 24B | Mistral | 24B | 60.5% | OpenRouter | ~$0.03 |
| Qwen 2.5 7B | Qwen | 7B | 57.7% | OpenRouter | ~$0.04 |
| Llama 3.1 8B | Llama | 8B | 48.2% | OpenRouter | ~$0.04 |

**Analysis Pipeline** (complete):
- Full pipeline in `experiments/`: `run_full_analysis.py`, `primary.py`, `stats_utils.py`, `viz_utils.py`, `figures.py`
- 4 tables, 5 figures, 243-group bootstrap confidence intervals
- Statistical tests: McNemar's test for condition comparisons, bootstrap CIs for accuracy estimates
- LaTeX output: `.tex` tables and `.pdf` figures ready for `\input{}` and `\includegraphics{}`

**Paper** (in progress):
- Sections 1-8 drafted in `paper/main.tex`
- Appendix A (proofs), B (benchmark details), C (per-model results) written
- Section 5 (experiments) placeholder awaiting final 11-model analysis
- Key finding: CoT lift +0.271 for Types 2,3 vs +0.037 for Types 5,6 -- confirms theoretical predictions

### In Progress (as of 2026-03-11)

- **Sonnet 4 evaluation**: 4/27 combinations complete, running locally (~$55 estimated)
- **o3 evaluation**: 4/27 combinations complete, running locally (~$40 estimated)
- **B2 budget_cot recalibration**: 4/9 models complete, running locally (~$3-5 estimated)
- **VPS daemon**: Running, spawns Claude sessions, worktree path fix deployed

---

## Phase 1: Complete the Loop (Week of 2026-03-11)

**Priority**: Get the daemon completing full autonomous research cycles. Finish reasoning-gaps paper.

- [ ] **1.1 Fix VPS status sync** -- Update `main` branch's `projects/reasoning-gaps/status.yaml` to reflect current state (`empirical-evaluation` phase), so daemon agents get correct context when spawned
- [ ] **1.2 Complete active evaluations** -- Finish Sonnet 4, o3, B2 recalibration (running locally, ETA ~6h). Transfer new checkpoints to VPS, ingest into PostgreSQL
- [ ] **1.3 Merge branches** -- Resolve conflicts between `main` and `research/reasoning-gaps`. Known conflicts: `.claude/agents/*.md`, `orchestrator/package.json`, utility TS files, `site/` layout. Get all 13 orchestrator modules as TS sources on one branch
- [ ] **1.4 Wire notifications** -- Add `SLACK_WEBHOOK_URL` to VPS `.env`. Implement daily digest (project progress, budget status, eval completions). Session completion alerts via `notifier.ts`
- [ ] **1.5 Add research-log.md** -- Create append-only research log per project (`projects/<name>/research-log.md`). Wire agents to read it on session start for continuity between sessions
- [ ] **1.6 Final analysis + paper integration** -- Re-run `run_full_analysis.py` with 11 models + recalibrated B2 data. Update Section 5 with final numbers, tables, figures. Compile and verify no LaTeX errors
- [ ] **1.7 Submit reasoning-gaps to NeurIPS 2026** -- Format with `neurips_2026.sty`, final review pass, arXiv preprint, camera-ready submission

---

## Phase 2: Research Radar + Taste Engine (Week 2)

**Priority**: The system should find research opportunities, not just execute on given ones.

- [ ] **2.1 Scout agent** -- Define `scout.md` agent role. Implement as cron job (daily, 6am UTC). Scan arXiv new submissions (cs.CL, cs.AI, cs.LG, cs.CC) via arXiv API. Query Semantic Scholar API for citation context. Score relevance to active projects using embedding similarity + keyword matching
- [ ] **2.2 Idea pipeline** -- Create `ideas.yaml` schema per project: `question`, `hypothesis`, `novelty_estimate` (1-5), `effort_days`, `venue_fit` (list of venues), `status` (proposed/approved/rejected/active). Scout populates with proposals. Human approves or vetoes via CLI or Slack reaction
- [ ] **2.3 Daily digest** -- Slack message at 7am UTC: relevant new papers (top 5 with one-line summaries), project progress per active project, decisions made in last 24h, budget burn rate, system health (daemon uptime, failed sessions)
- [ ] **2.4 Kill criteria** -- Every project gets explicit kill conditions at creation in `BRIEF.md`. Examples: "Kill if no novel contribution identified by week 3", "Kill if primary hypothesis falsified with >95% confidence". Daemon checks automatically at each phase transition
- [ ] **2.5 Literature knowledge base** -- Per-project persistent knowledge store of related work. Scout appends new relevant papers daily. Agents read on session start. Prevents the failure mode of rediscovering known concepts or missing recent related work

---

## Phase 3: Multi-Agent Orchestration (Week 3-4)

**Priority**: Move from single-agent sessions to specialized agent teams with defined handoffs.

- [ ] **3.1 Agent definitions** -- Create new agent files in `.claude/agents/`: `scout.md`, `theorist.md`, `experimenter.md`, `critic.md`, `editor.md`. Existing agents: `researcher.md`, `writer.md`, `reviewer.md`. Each agent file specifies: role, capabilities, inputs it expects, outputs it produces, quality criteria
- [ ] **3.2 Phase progression rules** -- Define prerequisites for each phase transition in a `phase-rules.yaml` schema. Example: `literature_review` -> `formal_framework` requires `literature/synthesis.md` exists and has 30+ references. Daemon validates before advancing `status.yaml`
- [ ] **3.3 Agent sequencing** -- Implement project lifecycle pipeline: scout -> researcher -> theorist -> experimenter -> writer -> critic -> editor. Each phase maps to one or more agent types. `session-runner` selects agent based on current phase
- [ ] **3.4 Critic gate** -- Critic review blocks submission. Critic produces structured review: {strengths, weaknesses, questions, verdict}. Verdict options: "accept" (proceed to editor), "revise" (loop back to writer with specific feedback, max 3 cycles), "reject" (flag for human review). Review stored in `reviews/` directory
- [ ] **3.5 Parallel execution** -- Run experimenter while writer drafts setup section (they don't depend on each other). Scout runs daily independent of project phase. `session-manager.ts` tracks dependencies and allows concurrent non-conflicting agents
- [ ] **3.6 Inter-agent communication** -- Agents share context via `research-log.md` (append-only), `status.yaml` (structured state), and phase-specific output files. No direct message passing between agents. Each agent reads shared state at session start

---

## Phase 4: Quality Framework (Month 2)

**Priority**: Systematic quality assurance so every output meets publication standards.

- [ ] **4.1 Quality gates** -- Implement 5 gates as automated checks, each with pass/fail criteria:
  1. **Novelty check**: Semantic Scholar overlap score < 0.8
  2. **Theoretical soundness**: All propositions have proofs or proof sketches; assumptions stated
  3. **Experimental rigor**: CIs computed, sample sizes >= 1000 per condition, effect sizes reported, multiple testing corrections applied
  4. **Adversarial review**: Critic agent finds no fatal flaws in 2 independent passes
  5. **Community value**: Benchmark is reproducible, code runs, data is accessible
- [ ] **4.2 Automated novelty check** -- Before formalizing a research direction: query Semantic Scholar for 50 most similar papers (by title + abstract embedding). Compute overlap score (cosine similarity of contribution claims). Flag if > 0.8, proceed with caution if 0.5-0.8, green light if < 0.5. Log results in `status.yaml`
- [ ] **4.3 Statistical rigor checks** -- Automated validation script that verifies: confidence intervals computed for all reported metrics, sample sizes meet minimum thresholds, effect sizes (Cohen's d or equivalent) reported alongside p-values, Bonferroni or Holm-Bonferroni correction applied when testing multiple hypotheses, no p-hacking patterns (all analyses pre-registered in analysis plan)
- [ ] **4.4 Reproducibility package** -- Auto-generate for each project: `requirements.txt` (pinned versions), `run.sh` (end-to-end execution), `data/README.md` (download instructions, checksums), `expected_outputs/` (reference results for validation). Test package runs in clean environment before submission
- [ ] **4.5 Internal review process** -- Critic agent runs after every major paper revision. Produces structured review with scores (1-5) on: novelty, clarity, correctness, significance, reproducibility. Track scores over revision history. Target: all scores >= 4 before submission

---

## Phase 5: Community Artifacts (Month 2)

**Priority**: Make every project produce reusable outputs that the research community adopts.

- [ ] **5.1 Benchmark packaging** -- Auto-generate pip-installable packages from `benchmarks/` code. Structure: `reasongap/` package with `tasks.py`, `evaluate.py`, `metrics.py`. Entry point: `pip install reasongap && python -m reasongap.evaluate --model openai:gpt-4o --tasks B1,B2,B3`. Include comprehensive docstrings and type hints
- [ ] **5.2 HuggingFace integration** -- Upload evaluation datasets with dataset cards: description, intended use, data format, splits (train/test/challenge), usage examples, citation info. Auto-generate cards from project metadata. Target: `deepwork/reasongap-benchmark` on HuggingFace Hub
- [ ] **5.3 GitHub releases** -- Tag releases matching paper versions (`v1.0` = submission, `v1.1` = camera-ready). Each release includes: benchmark code, evaluation data, analysis scripts, paper PDF. Automated via GitHub Actions on tag push
- [ ] **5.4 Blog post agent** -- New agent type that generates 1500-word accessible summaries. Input: paper + results. Output: markdown blog post with key findings, methodology overview, practical implications, figures. Published on `deepwork.site/blog/`. Target: one post per accepted paper
- [ ] **5.5 Leaderboard** -- Public page on `deepwork.site/leaderboards/<benchmark>`. Auto-updated when new evaluation results land in PostgreSQL. Shows: model name, overall accuracy, per-task breakdown, CoT lift, submission date. Community can submit results via PR to `leaderboard-submissions/` directory

---

## Phase 6: Infrastructure Scaling (Month 2-3)

- [ ] **6.1 VPS resize** -- CPX21 (3 vCPU, 4GB RAM, 80GB) -> CPX31 (4 vCPU, 8GB RAM, 160GB, ~$16/mo). Enables 4 concurrent agent sessions (currently 2). Add 2-4GB swap as safety net. Agent sessions are API-bound, not compute-bound, so CPU/RAM is the bottleneck for concurrency, not GPU
- [ ] **6.2 SSL/HTTPS** -- Point `api.deepwork.site` DNS A record to 89.167.5.50. Run `certbot --nginx -d api.deepwork.site`. Update nginx config for TLS termination. Required before dashboard goes live
- [ ] **6.3 Dashboard frontend** -- Wire Astro pages (`site/src/pages/dashboard/`) to VPS API. Replace mock data in `index.astro`, `eval.astro`, `budget.astro` with `fetch()` calls to `https://api.deepwork.site`. Add WebSocket connection for real-time eval progress. Deploy updated site to Vercel
- [ ] **6.4 Backup** -- Hetzner Storage Box (~$4/mo). Nightly cron: `pg_dump` PostgreSQL, rsync git repo + checkpoints. Retention: 7 daily, 4 weekly. Test restore procedure monthly
- [ ] **6.5 CI/CD** -- GitHub Actions workflows: (1) LaTeX compilation on push to `research/*` or `paper/*` branches, (2) orchestrator TypeScript build + lint, (3) evaluation pipeline tests (`pytest benchmarks/tests/`), (4) leaderboard update on new data

---

## Phase 7: Portfolio Management (Month 3+)

- [ ] **7.1 Cross-project resource allocation** -- Budget distribution algorithm: score projects by (priority x phase_urgency x expected_impact). Higher-scoring projects get more API budget and agent session time. Rebalance weekly. Enforce per-project budget caps in `budget-tracker`
- [ ] **7.2 Exploration/exploitation balance** -- Maintain portfolio mix: 60% safe bets (clear contribution, strong venue fit), 30% medium risk (novel angle, uncertain reception), 10% moonshots (high novelty, may not work). Scout agent proposes, human approves portfolio allocation
- [ ] **7.3 Venue calendar** -- Track submission deadlines for target venues (NeurIPS, ICML, ACL, EMNLP, ICLR, AAAI, COLM). Auto-generate project timelines working backward from deadline. Alert at T-4 weeks, T-2 weeks, T-3 days. Store in `venues.yaml`
- [ ] **7.4 Rejection recovery** -- When a paper is rejected: (1) ingest reviewer comments into `reviews/`, (2) critic agent analyzes feedback and produces revision plan, (3) identify next suitable venue from calendar, (4) writer + editor execute revision, (5) resubmit. Target turnaround: 2-3 weeks
- [ ] **7.5 Impact tracking** -- Monitor post-publication metrics: Semantic Scholar citations (weekly), HuggingFace dataset downloads (weekly), GitHub stars (daily), blog post analytics (weekly). Dashboard view showing impact trajectory per project. Alert when citation count crosses milestones (10, 50, 100)

---

## Budget Projections

| Phase | Timeline | Infra Cost | API Cost | Total |
|-------|----------|-----------|----------|-------|
| Phase 1 | Week 1 | $8 (VPS) | ~$150 (evals + sessions) | ~$158 |
| Phase 2 | Week 2 | $8 | ~$50 (scout + sessions) | ~$58 |
| Phase 3 | Week 3-4 | $16 (resize) | ~$200 (multi-agent) | ~$216 |
| Phase 4 | Month 2 | $16 | ~$100 (quality reviews) | ~$116 |
| Phase 5 | Month 2 | $16 | ~$50 (blog + packaging) | ~$66 |
| Phase 6 | Month 2-3 | $20 (SSL, backup) | $0 | ~$20 |
| Phase 7 | Month 3+ | $20 | ~$300 (portfolio) | ~$320 |

**Monthly steady-state estimate**: $500-700/month (within $1,000 budget).

### Spent to Date (as of 2026-03-11)

| Item | Cost | Notes |
|------|------|-------|
| Anthropic API (Haiku 4.5 eval) | ~$15 | 27/27 complete |
| OpenAI API (GPT-4o-mini + GPT-4o) | ~$60 | 54/54 complete |
| OpenRouter (6 open-source models) | ~$0.22 | 162/162 complete |
| Hetzner VPS (CPX21) | ~$8 | Running since 2026-03-10 |
| **Total spent** | **~$83** | |

### Committed Spend (in progress)

| Item | Est. Cost | Notes |
|------|-----------|-------|
| Sonnet 4 eval (27 combos) | ~$55 | 4/27 complete, running |
| o3 eval (27 combos) | ~$40 | 4/27 complete, running |
| B2 budget_cot recal (9 models) | ~$3-5 | 4/9 complete, running |
| **Total committed** | **~$98** | |

**Remaining budget (March)**: ~$267 after committed spend. Ample for revision rounds and Phase 2 work.

---

## Key Design Decisions

These decisions are locked in. Rationale preserved for future reference.

**PostgreSQL over SQLite**: Need concurrent reads (dashboard) + writes (daemon/eval). SQLite's write lock would block dashboard queries during eval ingestion.

**OpenRouter over Modal for open-source models**: OpenRouter costs $0.22 total vs estimated $100-200 for Modal GPU time. No cold starts, no GPU provisioning. Modal code preserved in `benchmarks/modal_serving.py` for reproducibility validation on dedicated hardware.

**Frontend on Vercel, API on VPS**: Website deployment stays on Vercel (fast, existing workflow). VPS exposes REST + WebSocket API. Single-user system, so API key auth is sufficient.

**Daemon + API in one process**: Daemon loop and Express routes run in the same Node.js process. No separate API service. Simpler deployment, shared state, single systemd unit.

**Opus 4 deferred**: $272 is 68% of remaining budget at time of decision. Sonnet 4 ($55) + o3 ($40) provide more marginal value per dollar -- two diverse model additions vs one expensive one.

**Agents communicate via files, not messages**: `research-log.md` (append-only narrative), `status.yaml` (structured state), and phase-specific output files. No direct agent-to-agent communication. Simpler, auditable, crash-safe.
