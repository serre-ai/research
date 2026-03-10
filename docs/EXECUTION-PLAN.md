# Execution Plan: From Code to Running Research

Sprint-level plan to go from the current state to autonomous research projects running 24/7 on the VPS. Every task has a concrete deliverable.

**North Star:** First autonomous Claude agent session completes a meaningful research task, commits results, and pushes to GitHub — without human intervention.

---

## Current State (March 10, 2026)

### What Works
- Git engine: full worktree/branch/commit/PR operations ✓
- Project manager: status.yaml CRUD, project scaffolding ✓
- CLI dashboard: shows projects, budget, activity ✓
- Session manager: creates worktrees, builds prompts (but can't launch agents) ✓
- VPS: `89.167.5.50`, Ubuntu 24.04, Node.js 22, git, gh, Modal, `deepwork` user ✓
- Modal: authenticated, GPU verified (T4 test passed) ✓
- Documentation: comprehensive (31 files) ✓
- 1 project defined: reasoning-gaps (NeurIPS 2026, not started) ✓
- 10 research ideas scored in backlog ✓

### What's Missing (Critical Path)
1. ~~Claude Agent SDK integration~~ → **Session Runner** (can't do research without this)
2. ~~Scheduling loop~~ → **Daemon** (can't run unattended without this)
3. ~~Cost tracking~~ → **Budget Tracker** (can't enforce limits without this)
4. ~~Event logging~~ → **Activity Logger** (can't observe the system without this)
5. ~~VPS deployment~~ → **Deploy** (can't run 24/7 without this)

---

## Sprint 1: First Autonomous Session (Days 1-4)

**Goal:** A Claude agent session runs on the VPS, does real research on reasoning-gaps, commits and pushes results.

### Day 1: Session Runner

The single most important piece of code. Everything else is downstream.

**Task 1.1: Install Claude Agent SDK**
```
File: orchestrator/package.json
Action: npm install @anthropic-ai/claude-agent-sdk
Deliverable: SDK importable, types available
```

**Task 1.2: Build session-runner.ts**
```
File: orchestrator/src/session-runner.ts (NEW)
Deliverable: SessionRunner class that:
  - Takes project name + agent type
  - Builds composite prompt (global CLAUDE.md + agent def + project CLAUDE.md + status)
  - Launches Claude Agent SDK session in project worktree
  - Streams messages, tracks token usage
  - On completion: returns SessionResult with metrics
  - On error: captures error, returns failed result
Interface:
  run(config: SessionConfig) → Promise<SessionResult>
```

**Task 1.3: Wire session-manager.ts to session-runner.ts**
```
File: orchestrator/src/session-manager.ts (MODIFY)
Action: Replace the TODO on line 58 with actual SDK call
Deliverable: startProject() launches a real agent session
```

**Task 1.4: Replace yaml.ts with proper parser**
```
File: orchestrator/src/yaml.ts (REPLACE)
Action: npm install yaml; rewrite to use it
Deliverable: Complex YAML (nested objects, arrays) parses correctly
```

**Task 1.5: Smoke test locally**
```
Action: Run a short session on reasoning-gaps from local machine
Command: npx tsx orchestrator/src/index.ts start reasoning-gaps
Verify: Agent reads BRIEF.md, does some research, commits, pushes
Duration: Limit to 10 turns for testing
```

### Day 2: Activity Logger + Budget Tracker

**Task 2.1: Build logger.ts**
```
File: orchestrator/src/logger.ts (NEW)
Deliverable: ActivityLogger class that:
  - Appends events to .logs/activity.jsonl
  - Each event: { timestamp, type, project?, agent?, data }
  - Types: session_start, session_end, session_error, commit, push,
    budget_spend, phase_transition, daemon_start, daemon_stop
  - Query method: recent(count, filter?) → ActivityEvent[]
```

**Task 2.2: Build budget-tracker.ts**
```
File: orchestrator/src/budget-tracker.ts (NEW)
Deliverable: BudgetTracker class that:
  - Records per-session cost (tokens × price)
  - Reads pricing from config.yaml
  - Tracks daily + monthly totals
  - canSpend(estimatedUsd) → boolean
  - getStatus() → { dailySpent, monthlySpent, remaining, alertLevel }
  - Writes to .logs/spending.jsonl + updates budget.yaml
```

**Task 2.3: Add .logs/ to .gitignore**
```
File: .gitignore (MODIFY)
Action: Add .logs/, .sessions/, .deepwork.pid
```

### Day 3: Daemon Scheduler

**Task 3.1: Build daemon.ts**
```
File: orchestrator/src/daemon.ts (NEW)
Deliverable: Daemon class that:
  - Runs an infinite loop with configurable poll interval
  - Each cycle: read all projects, score priority, pick top N
  - Launch sessions via SessionRunner for selected projects
  - Wait for session completion, process results
  - Log all activity via ActivityLogger
  - Check budget via BudgetTracker before each session
  - Handle SIGTERM gracefully (finish current session, cleanup)
```

**Task 3.2: Prioritization algorithm**
```
Within daemon.ts:
  - Score each active project:
    +10 venue deadline within 4 weeks
    +5  no session in >24 hours
    +3  has pending next_steps
    -5  last session failed
    -10 daily budget for project exhausted
    -20 blocked on decision
  - Map phase → agent type:
    research → researcher
    drafting → writer
    revision → reviewer then writer
    final → editor
```

**Task 3.3: Update index.ts with daemon command**
```
File: orchestrator/src/index.ts (MODIFY)
Action: Add "run" command that starts the daemon
Command: deepwork run [--interval 30] [--max-sessions 2] [--budget 40]
```

**Task 3.4: End-to-end local test**
```
Action: Start daemon locally, verify it:
  1. Reads reasoning-gaps project
  2. Scores it as highest priority (only project)
  3. Launches researcher session
  4. Session does work, commits, pushes
  5. Daemon logs the session result
  6. Budget tracker records the cost
```

### Day 4: Deploy to VPS + First Real Run

**Task 4.1: Clone repo to VPS**
```
ssh deepwork-vps
git clone git@github.com:oddurs/deepwork.git
cd deepwork && npm install --workspaces
npm run build --workspaces
```

**Task 4.2: Configure VPS environment**
```
File: /home/deepwork/deepwork/.env (on VPS)
Contents:
  ANTHROPIC_API_KEY=<your key>
  MODAL_TOKEN_ID=ak-...
  MODAL_TOKEN_SECRET=as-...
  DAILY_BUDGET_USD=40
  MAX_CONCURRENT_SESSIONS=1  # Start conservative
  POLL_INTERVAL_MINUTES=30
```

**Task 4.3: Set up GitHub CLI auth on VPS**
```
ssh deepwork-vps
gh auth login  # Interactive, use browser or token
```

**Task 4.4: Create systemd service**
```
File: /etc/systemd/system/deepwork.service (on VPS)
Action: Install service from INFRASTRUCTURE.md template
Commands:
  sudo systemctl daemon-reload
  sudo systemctl enable deepwork
  sudo systemctl start deepwork
```

**Task 4.5: Verify first autonomous run**
```
Watch: journalctl -u deepwork -f
Verify:
  - Daemon starts
  - Picks up reasoning-gaps project
  - Launches researcher agent
  - Agent does literature review work
  - Commits appear on research/reasoning-gaps branch
  - status.yaml updated
  - Session cost logged
  - Daemon sleeps, wakes, considers next cycle
```

### Sprint 1 Milestone: FIRST AUTONOMOUS SESSION ✓
The platform is doing research by itself. One project, one agent, running on the VPS.

---

## Sprint 2: Second Project + Stability (Days 5-8)

**Goal:** Launch a second research project. Harden the daemon for continuous operation.

### Day 5: Launch Second Project

**Task 5.1: Select second project from backlog**

Recommended: **agent-failure-taxonomy** (composite score 4.25)
- Survey type = fast (2 months), lower risk
- Highly feasible (score 5) — mostly literature + analysis, no GPU needed yet
- Directly relevant to the platform itself (meta-research)
- Different type than reasoning-gaps (survey vs. theory) — portfolio diversification
- Targets ACL 2027 (Feb submission) — no immediate deadline pressure

Alternative: **reasoning-gap-benchmark** (4.15)
- Direct companion to reasoning-gaps — shared research
- Tool type = high citation potential
- Targets NeurIPS D&B 2026 (May) — tighter deadline but feasible

**Task 5.2: Create project from template**
```
Action: Use project manager to scaffold:
  projects/agent-failure-taxonomy/
    BRIEF.md       ← from backlog description + template
    CLAUDE.md      ← from template, customized
    status.yaml    ← from template
```

**Task 5.3: Create project branch**
```
git checkout -b research/agent-failure-taxonomy
git push -u origin research/agent-failure-taxonomy
```

**Task 5.4: Verify daemon picks up both projects**
```
Watch daemon logs. Verify:
  - Both projects scored and prioritized
  - Sessions alternate between projects
  - No worktree conflicts
```

### Day 6: Error Handling + Recovery

**Task 6.1: Session failure recovery**
```
File: orchestrator/src/session-runner.ts (MODIFY)
Add:
  - Retry logic: if session fails, wait 5 min, retry once
  - Partial work preservation: commit any changes before reporting failure
  - Timeout handling: kill session after maxDurationMs
  - OOM / rate limit detection from error messages
```

**Task 6.2: Daemon resilience**
```
File: orchestrator/src/daemon.ts (MODIFY)
Add:
  - Catch all errors in the main loop (never crash)
  - Exponential backoff on repeated failures for same project
  - Health heartbeat: write timestamp to .deepwork.heartbeat every cycle
  - Stale session detection: kill sessions running >2x expected duration
```

**Task 6.3: Log rotation**
```
File: orchestrator/src/logger.ts (MODIFY)
Add:
  - Rotate activity.jsonl monthly
  - Cap individual log files at 100MB
  - Archive old logs to .logs/archive/
```

### Day 7: Monitoring + Alerts

**Task 7.1: Build monitor.ts**
```
File: orchestrator/src/monitor.ts (NEW)
Deliverable: Monitor class with:
  - getHealth() → daemon status, active sessions, disk usage, budget status
  - checkDisk() → alert if >80% disk usage
  - checkStale() → flag projects with no activity in 48h
  - checkBudget() → alert levels (ok/warning/critical/exceeded)
```

**Task 7.2: Health command**
```
File: orchestrator/src/index.ts (MODIFY)
Add: deepwork health
Output:
  Daemon: running (uptime: 3d 4h)
  Active sessions: reasoning-gaps (researcher, 23 min)
  Budget: $12.40 / $40.00 today, $89.20 / $1000 this month
  Disk: 8.2 GB / 75 GB (11%)
  Last activity: 4 min ago
  Errors (24h): 0
```

**Task 7.3: Budget alert notification**
```
File: orchestrator/src/budget-tracker.ts (MODIFY)
Add: When spending crosses 80% threshold, log a warning event
Future: Hook into email/Slack notification
```

### Day 8: Enhanced CLI Commands

**Task 8.1: deepwork new <project>**
```
File: orchestrator/src/commands/new.ts (NEW)
Action: Interactive project creation from template
  - Reads shared/templates/BRIEF.md, status.yaml, CLAUDE.md
  - Fills in project name, title from args
  - Creates project directory + files
  - Creates git branch
  - Pushes to remote
```

**Task 8.2: deepwork status <project>**
```
File: orchestrator/src/commands/status.ts (NEW)
Action: Detailed project view
  - Current phase, focus, next steps
  - Recent commits on project branch
  - Session history (last 5 sessions with duration, cost)
  - Pending decisions
```

**Task 8.3: deepwork logs [project]**
```
File: orchestrator/src/commands/logs.ts (NEW)
Action: Tail activity log, optionally filtered by project
```

### Sprint 2 Milestone: TWO PROJECTS RUNNING, STABLE DAEMON ✓
Two research projects running autonomously. Daemon handles errors gracefully. Monitoring works.

---

## Sprint 3: Research Website + Third Project (Days 9-14)

**Goal:** Public research presence. Three projects running. First meaningful research output.

### Days 9-10: Research Website

**Task 9.1: Initialize Astro site**
```
Directory: site/ (NEW workspace)
npx create-astro@latest site -- --template minimal
Add to root package.json workspaces
```

**Task 9.2: Build site structure**
```
Pages:
  / — Homepage: mission, current projects, recent posts
  /papers — Publication list (empty for now, ready for entries)
  /blog — Blog index
  /blog/[slug] — Individual blog posts
  /about — About Oddur Sigurdsson + Deepwork Research
Components:
  Header, Footer, PaperCard, BlogCard
Content collections:
  papers/ — YAML frontmatter + abstract
  blog/ — Markdown posts
```

**Task 9.3: Write first blog post**
```
File: site/src/content/blog/introducing-deepwork.md
Content: What Deepwork Research is, what we're working on,
  the vision for AI-augmented research.
  Honest about the approach. Sets the narrative.
```

**Task 9.4: Deploy to GitHub Pages**
```
File: .github/workflows/site-deploy.yml (NEW)
Trigger: push to main (site/ changes)
Action: Build Astro → deploy to GitHub Pages
Setup: Enable GitHub Pages in repo settings, source: GitHub Actions
```

**Task 9.5: About page**
```
File: site/src/pages/about.astro
Content: Oddur Sigurdsson bio, Deepwork Research description,
  research agenda, links to profiles (Google Scholar, ORCID, Bluesky, GitHub)
```

### Days 11-12: Third Project + Decision Router

**Task 11.1: Launch third project**

Recommended: **reasoning-gap-benchmark** (composite 4.15)
- Direct artifact from reasoning-gaps — shared research
- Tool type = high citation potential, fills portfolio gap
- NeurIPS Datasets & Benchmarks 2026 (May deadline) — tight but feasible if reasoning-gaps lit review is complete
- 2-month estimated timeline — fast

**Task 11.2: Build decision-router.ts**
```
File: orchestrator/src/decision-router.ts (NEW)
Deliverable: DecisionRouter class that:
  - Scans all projects for decisions_pending without github_issue field
  - Creates GitHub Issues with label "decision-needed"
  - Checks closed issues for resolutions
  - Updates status.yaml with answers
  - Runs every daemon cycle
```

**Task 11.3: Integrate decision router into daemon**
```
File: orchestrator/src/daemon.ts (MODIFY)
Add: Call decisionRouter.sync() every cycle before scheduling sessions
```

### Days 13-14: Research Momentum

**Task 13.1: Review first week of research output**
```
Action: Check reasoning-gaps branch for progress
  - How many papers surveyed?
  - Quality of literature notes?
  - Any decisions made?
  - Status.yaml updated?
  - Commits look clean?
```

**Task 13.2: Adjust agent prompts based on output quality**
```
Files: .claude/agents/researcher.md, project CLAUDE.md files
Action: Refine based on what the agent did well/poorly
```

**Task 13.3: Write blog post about first research findings**
```
File: site/src/content/blog/reasoning-gaps-early-findings.md
Content: What we're learning from the literature review,
  interesting patterns, key papers. Accessible writing.
```

**Task 13.4: Create online profiles**
```
Action (manual, not code):
  - Google Scholar profile
  - ORCID iD
  - Semantic Scholar page
  - OpenReview profile (Deepwork Research affiliation)
  - Bluesky account
  - GitHub organization: deepwork-research
```

### Sprint 3 Milestone: PUBLIC PRESENCE + THREE PROJECTS ✓
Website live. Three research projects running. Blog publishing. Online profiles set up.

---

## Sprint 4: GPU Experiments + Quality Gates (Days 15-21)

**Goal:** Enable empirical research with Modal GPUs. Enforce quality standards at phase transitions.

### Days 15-16: Experiment Runner (Modal)

**Task 15.1: Build experiment-runner.ts**
```
File: orchestrator/src/experiment-runner.ts (NEW)
Deliverable: ExperimentRunner class using Modal TS SDK
  - run(spec) → deploys/calls Modal function, returns results
  - runSandbox(spec) → creates dynamic sandbox for one-off experiments
  - downloadResults() → pulls from Modal Volume to local project dir
```

**Task 15.2: Create base experiment template**
```
File: shared/templates/experiment/modal_eval.py
Template Modal Python script for LLM evaluation:
  - Configurable model, dataset, metrics
  - Results written to Modal Volume
  - Proper error handling and logging
```

**Task 15.3: Test experiment pipeline end-to-end**
```
Action:
  1. Write a simple eval script in reasoning-gaps/experiments/
  2. Trigger from orchestrator
  3. Verify: Modal provisions GPU, runs eval, returns results
  4. Results appear in project directory
```

### Days 17-18: Quality Gates

**Task 17.1: Build quality-gate.ts**
```
File: orchestrator/src/quality-gate.ts (NEW)
Deliverable: QualityGate class that:
  - Reads shared/standards/quality-checklist.yaml
  - For a given phase transition (e.g., research → drafting):
    - Checks required conditions
    - Returns pass/fail with details
  - Called by daemon before advancing project phase
```

**Task 17.2: Phase transition automation**
```
File: orchestrator/src/daemon.ts (MODIFY)
Add:
  - After each session, check if phase transition conditions are met
  - If quality gate passes, advance phase in status.yaml
  - If not, keep project in current phase
  - Log the gate result
```

**Task 17.3: Self-review integration**
```
When a project reaches drafting → revision:
  - Daemon schedules reviewer agent
  - Reviewer uses shared/prompts/self-review.md rubric
  - Review results written to project/reviews/
  - Only advance to submission if score >= 7/10 on all criteria
```

### Days 19-21: GitHub Actions + Paper Pipeline

**Task 19.1: Paper compilation workflow**
```
File: .github/workflows/paper-build.yml (NEW)
Trigger: push to research/* or paper/* branches (paper/ directory changes)
Action: Compile LaTeX → PDF, upload as PR artifact
```

**Task 19.2: Status validation workflow**
```
File: .github/workflows/status-check.yml (NEW)
Trigger: push (status.yaml changes)
Action: Validate YAML structure against schema
```

**Task 19.3: arXiv packager**
```
File: orchestrator/src/arxiv-packager.ts (NEW)
Deliverable:
  - Flatten LaTeX \input includes
  - Collect all dependencies
  - Create .tar.gz
  - Validate against arXiv requirements
  - Output submission instructions
```

### Sprint 4 Milestone: FULL RESEARCH PIPELINE ✓
GPU experiments work. Quality gates enforce standards. Papers compile in CI. arXiv packaging ready.

---

## Sprint 5: Scale to Steady State (Days 22-30)

**Goal:** 4-6 projects running. Monthly cadence. Platform running itself.

### Days 22-24: Portfolio Expansion

**Task 22.1: Launch projects 4 and 5**

From backlog, recommended:
- **verification-complexity** (score 4.50) — Theory paper, forms trilogy with reasoning-gaps + self-improvement-limits. Targets NeurIPS 2026 or ICLR 2027.
- **cot-faithfulness-audit** (score 3.95) — Empirical, fast (3 months), targets EMNLP 2026. Complements reasoning-gaps directly.

**Task 22.2: Increase daemon concurrency**
```
On VPS: Edit .env
  MAX_CONCURRENT_SESSIONS=2
  DAILY_BUDGET_USD=60
Restart: sudo systemctl restart deepwork
```

**Task 22.3: Implement session scheduling strategies**
```
File: orchestrator/src/daemon.ts (MODIFY)
Add phase-aware scheduling:
  - Writing-phase projects get priority (time-sensitive)
  - Research-phase projects can wait
  - Never run two sessions from the same project simultaneously
  - Stagger so different phases don't all compete
```

### Days 25-27: Strategist Agent + Portfolio Review

**Task 25.1: Implement strategist workflow**
```
Add to daemon: Monthly strategist run
  - Reads all status.yaml files
  - Evaluates portfolio health (type balance, phase distribution, venue coverage)
  - Reviews idea backlog
  - Generates portfolio report to docs/reports/portfolio-YYYY-MM.md
  - Recommends: start/stop/pivot projects
```

**Task 25.2: Idea generation pipeline**
```
Add to daemon: Monthly idea generation
  - Researcher agent with shared/prompts/idea-generation.md
  - Inputs: current portfolio, recent literature trends
  - Outputs: 5-10 new ideas appended to docs/ideas/backlog.yaml
```

### Days 28-30: Observability + Documentation

**Task 28.1: Daemon dashboard update**
```
File: cli/src/app.tsx (MODIFY)
Add:
  - Session history (last 10 sessions with duration, cost, outcome)
  - Budget burn rate visualization
  - Per-project phase indicators
  - Error count
```

**Task 28.2: Write operational runbook**
```
File: docs/RUNBOOK.md (NEW)
Content:
  - How to check if daemon is running
  - How to restart after failure
  - How to add a new project
  - How to manually trigger a session
  - How to kill a stuck session
  - How to pull down VPS changes locally
  - Common error messages and fixes
  - Emergency: how to stop everything
```

**Task 28.3: Update ARCHITECTURE.md with actual state**
```
File: ARCHITECTURE.md (MODIFY)
Update implementation status to reflect what's actually built
Mark Phase 2 items as complete
```

### Sprint 5 Milestone: STEADY STATE ✓
4-6 projects running. Budget tracking. Quality gates. Portfolio management. The platform runs itself.

---

## Project Launch Sequence

| # | Project | Type | Venue Target | Launch | Why This Order |
|---|---------|------|-------------|--------|----------------|
| 1 | reasoning-gaps | theory | NeurIPS 2026 (May) | Day 1 | Already defined, flagship project |
| 2 | agent-failure-taxonomy | survey | ACL 2027 (Feb) | Day 5 | Fast, feasible, meta-relevant, no GPU needed |
| 3 | reasoning-gap-benchmark | tool | NeurIPS D&B 2026 (May) | Day 11 | Companion to #1, high citation potential |
| 4 | verification-complexity | theory | ICLR 2027 (Oct) | Day 22 | Forms trilogy with #1, high novelty (4.50) |
| 5 | cot-faithfulness-audit | empirical | EMNLP 2026 (Jun) | Day 22 | Complements #1, needs GPU (Modal ready by then) |
| 6 | TBD (strategist picks) | varies | TBD | Day 30 | Based on portfolio review and backlog re-scoring |

### Phase Distribution at Steady State (Day 30+)

```
reasoning-gaps:          ████████░░░░ drafting (week 6-8)
agent-failure-taxonomy:  ██████░░░░░░ research (week 3-4)
reasoning-gap-benchmark: ████░░░░░░░░ research (week 2-3)
verification-complexity: ██░░░░░░░░░░ research (week 1-2)
cot-faithfulness-audit:  ██░░░░░░░░░░ research (week 1-2)
```

Projects staggered so resource usage is smooth. Only reasoning-gaps is in writing phase initially (highest token usage). Others are in cheaper research phase.

---

## Budget Projection (First 30 Days)

| Week | Projects | Daily Spend | Weekly Total | Cumulative |
|------|----------|------------|-------------|-----------|
| 1 | 1 (reasoning-gaps) | ~$8-12 | ~$70 | $70 |
| 2 | 2 | ~$15-20 | ~$120 | $190 |
| 3 | 3 | ~$20-25 | ~$160 | $350 |
| 4 | 5 | ~$30-40 | ~$245 | $595 |

Well within the $1,000/month budget. GPU experiments (Modal) add ~$50-100/month once they start in Sprint 4.

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Claude Agent SDK doesn't work as expected | Fallback: shell out to `claude` CLI with `-p` flag for prompts. Less control but functional. |
| Agent produces low-quality research | Quality gates prevent bad work from advancing. Review first output on Day 5 and adjust prompts. |
| Budget overrun | Conservative daily limits. Start with 1 session, scale up. Budget tracker enforces hard caps. |
| VPS disk fills up | Monitor alerts at 80%. Worktree cleanup after each session. Archive old logs. |
| Agent loops / gets stuck | Session timeout (45 min default). Daemon detects stale sessions and kills them. Backoff on repeated failures. |
| Git conflicts between projects | Each project has its own worktree and branch. No shared files modified during sessions. |
| Rate limiting from Anthropic API | Stagger sessions. Never run more than MAX_CONCURRENT_SESSIONS. Exponential backoff on 429 errors. |

---

## Definition of Done

The platform is "done" (v1.0) when all of these are true:

- [ ] Daemon runs 24/7 on VPS without human intervention
- [ ] 3+ projects actively progressing through phases
- [ ] Budget tracked accurately, limits enforced
- [ ] Quality gates prevent phase transitions without meeting standards
- [ ] Website live with blog posts and paper listings
- [ ] Online profiles created (Scholar, ORCID, OpenReview, Bluesky)
- [ ] First arXiv preprint posted
- [ ] At least one blog post published per project
- [ ] Monitoring: can check health with single command
- [ ] Runbook: anyone can operate the system with documentation

**Target date: April 10, 2026** (30 days from now)
