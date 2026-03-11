# Build Plan: What Needs to Be Built

Detailed technical specification of every service, component, and system required to make Deepwork a fully autonomous, always-running research platform.

---

## Current State

**What works today:**
- Git engine: full worktree/branch/commit/PR operations (316 lines, production-ready)
- Project manager: reads/writes status.yaml, lists projects, scaffolds new projects (148 lines)
- Session manager: creates worktrees and builds prompts, but **cannot launch Claude sessions** (132 lines, stub)
- CLI dashboard: displays projects, budget, activity in terminal (233 lines, read-only)

**What doesn't work:**
- No autonomous agent sessions (Claude SDK integration is a TODO)
- No daemon loop (can't run unattended)
- No decision routing to GitHub
- No budget tracking (budget.yaml is empty)
- No experiment execution on GPU servers
- No publishing pipeline (no website, no arXiv automation)
- No monitoring or alerting
- No tests

**The gap:** The platform can show you a dashboard but cannot do any work by itself.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        deepwork daemon                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Scheduler  │  │  Session   │  │  Budget    │  │ Monitor   │ │
│  │            │→ │  Runner    │→ │  Tracker   │  │           │ │
│  └────────────┘  └─────┬──────┘  └────────────┘  └───────────┘ │
│                        │                                         │
│  ┌─────────────────────▼────────────────────────────────────────┐│
│  │                  Claude Agent SDK                            ││
│  │  research session │ writing session │ review session         ││
│  └──────────────────────────────────────────────────────────────┘│
│                        │                                         │
│  ┌─────────────────────▼────────────────────────────────────────┐│
│  │                   Git Engine (existing)                      ││
│  │  worktrees │ branches │ commits │ PRs │ push                ││
│  └──────────────────────────────────────────────────────────────┘│
└──────────┬───────────────────────────────────┬───────────────────┘
           │                                   │
    ┌──────▼──────┐                    ┌───────▼──────┐
    │   GitHub    │                    │ Modal (GPUs) │
    │  Issues/PRs │                    │ scale-to-zero│
    └─────────────┘                    └──────────────┘
           │
    ┌──────▼──────┐
    │  Website    │
    │  (Astro)    │
    └─────────────┘
```

---

## Service 1: Session Runner

**Priority: CRITICAL — nothing else works without this**

The core missing piece. Programmatically launches Claude Code sessions using the Agent SDK, manages their lifecycle, and captures output.

### What it does
1. Takes a project name and agent type (researcher/writer/reviewer)
2. Sets up an isolated worktree for the session
3. Builds a system prompt from: global CLAUDE.md + agent definition + project CLAUDE.md + current status.yaml
4. Launches a Claude Agent SDK session with the prompt
5. Monitors the session (token usage, duration, progress)
6. On completion: commits changes, pushes, updates status.yaml, cleans up
7. On failure: logs error, saves partial work, marks session as failed

### File: `orchestrator/src/session-runner.ts`

```typescript
// Core interface
interface SessionConfig {
  projectName: string;
  agentType: "researcher" | "writer" | "reviewer" | "editor" | "strategist";
  maxTurns: number;
  maxDurationMs: number;
  thinkingLevel: "standard" | "extended";
  allowedTools: string[];
}

interface SessionResult {
  sessionId: string;
  projectName: string;
  agentType: string;
  status: "completed" | "failed" | "timeout" | "budget_exceeded";
  turnsUsed: number;
  tokensUsed: { input: number; output: number };
  costUsd: number;
  durationMs: number;
  commitsCreated: string[];
  statusUpdates: Record<string, unknown>;
  error?: string;
}

// Key methods
class SessionRunner {
  // Launch a session and return when complete
  async run(config: SessionConfig): Promise<SessionResult>;

  // Build the composite prompt for the agent
  private buildPrompt(project: string, agent: string): Promise<string>;

  // Monitor token/cost budget during session
  private checkBudget(session: ActiveSession): boolean;

  // Graceful shutdown: commit work, update status, cleanup
  private finalize(session: ActiveSession): Promise<void>;
}
```

### Dependencies
- `@anthropic-ai/claude-agent-sdk` — the actual SDK (already in package.json)
- Existing `GitEngine` — for worktree/commit/push operations
- Existing `ProjectManager` — for reading/writing status.yaml

### Implementation notes
- The SDK's `query()` function spawns Claude Code as a subprocess with tool access
- Each session runs in its own worktree at `.worktrees/<project>/`
- Session output (messages, tool calls) should be logged to `.sessions/<project>/<timestamp>.jsonl`
- Token usage must be tracked per-session and aggregated per-project for budget tracking
- Set `permissionMode: "acceptEdits"` for autonomous operation (auto-approve file edits)
- Use `maxTurns` to prevent runaway sessions (50 for research, 80 for writing, 30 for review)

### Estimated effort: 4-6 hours

---

## Service 2: Daemon Scheduler

**Priority: CRITICAL — makes the platform autonomous**

The main loop that runs forever, cycling through projects and launching sessions based on priority, phase, and resource availability.

### What it does
1. Runs as a long-lived process (systemd/launchd managed)
2. Every N minutes, evaluates all projects and decides what to work on
3. Respects budget limits, rate limits, and concurrent session limits
4. Schedules the right agent type based on project phase
5. Handles session results: success → advance project, failure → retry or flag
6. Logs all activity for the dashboard

### File: `orchestrator/src/daemon.ts`

```typescript
interface DaemonConfig {
  pollIntervalMs: number;        // How often to check for work (default: 30min)
  maxConcurrentSessions: number; // How many sessions can run at once (default: 2)
  dailyBudgetUsd: number;        // Max spend per day
  quietHoursStart?: number;      // Optional: pause overnight (hour, 0-23)
  quietHoursEnd?: number;
}

interface ProjectPriority {
  projectName: string;
  score: number;              // Higher = work on this next
  reason: string;             // Why this score
  suggestedAgent: string;     // Which agent type to use
  suggestedMaxTurns: number;
}

class Daemon {
  // Main loop — runs forever
  async start(config: DaemonConfig): Promise<never>;

  // Evaluate all projects, return sorted priority list
  private async prioritize(): Promise<ProjectPriority[]>;

  // Check if we can afford to run a session
  private async canAfford(estimatedCostUsd: number): Promise<boolean>;

  // Check rate limits (Anthropic API, GitHub API)
  private async checkRateLimits(): Promise<boolean>;

  // Handle session completion
  private async onSessionComplete(result: SessionResult): Promise<void>;

  // Graceful shutdown (SIGTERM handler)
  private async shutdown(): Promise<void>;
}
```

### Scheduling algorithm

```
every 30 minutes:
  1. Read all projects/ status.yaml files
  2. Filter to status: active
  3. Score each project:
     - +10 if in a deadline-sensitive phase (revision, close to venue deadline)
     - +5 if no session has run in >24 hours
     - +3 if phase has pending work items in next_steps
     - -5 if last session failed (backoff)
     - -10 if daily budget for this project is exhausted
     - -20 if project is blocked on a decision
  4. Sort by score descending
  5. For top N projects (N = maxConcurrentSessions - running sessions):
     - Determine agent type from phase:
       research → researcher
       drafting → writer
       revision → reviewer first, then writer
       final → editor
     - Launch session via SessionRunner
  6. Wait for any running session to complete
  7. Process results, update status, log activity
  8. Sleep until next poll
```

### CLI entry point: `deepwork run`

```typescript
// orchestrator/src/index.ts additions
case "run":
  const daemon = new Daemon(rootDir);
  await daemon.start({
    pollIntervalMs: 30 * 60 * 1000,
    maxConcurrentSessions: 2,
    dailyBudgetUsd: parseFloat(process.env.DAILY_BUDGET_USD ?? "40"),
  });
  break;
```

### Process management
- systemd unit file (Linux) or launchd plist (macOS) — templates already in INFRASTRUCTURE.md
- Writes PID to `.deepwork.pid` for status checks
- SIGTERM → graceful shutdown (finish current session, commit, cleanup)
- SIGHUP → reload config.yaml without restart
- Stdout/stderr → `.logs/daemon.log` (rotated daily)

### Estimated effort: 6-8 hours

---

## Service 3: Budget Tracker

**Priority: HIGH — prevents runaway spending**

Tracks actual API spending per session, per project, per day. Enforces limits and sends alerts.

### What it does
1. Records cost of every session (tokens × price per token)
2. Aggregates by project, by day, by month
3. Enforces daily and monthly budget caps
4. Writes spending data to budget.yaml
5. Alerts when approaching thresholds (80% of budget)

### File: `orchestrator/src/budget-tracker.ts`

```typescript
interface SpendingRecord {
  timestamp: string;
  projectName: string;
  sessionId: string;
  agentType: string;
  tokensInput: number;
  tokensOutput: number;
  costUsd: number;
  model: string;
}

interface BudgetStatus {
  dailySpent: number;
  dailyLimit: number;
  dailyRemaining: number;
  monthlySpent: number;
  monthlyLimit: number;
  monthlyRemaining: number;
  byProject: Record<string, number>;  // project → month total
  alertLevel: "ok" | "warning" | "critical" | "exceeded";
}

class BudgetTracker {
  // Record a session's cost
  async record(record: SpendingRecord): Promise<void>;

  // Get current budget status
  async getStatus(): Promise<BudgetStatus>;

  // Check if a projected cost is within budget
  canSpend(estimatedCostUsd: number): Promise<boolean>;

  // Get spending history for a time range
  async getHistory(from: string, to: string): Promise<SpendingRecord[]>;
}
```

### Storage
- Append-only JSONL file: `.logs/spending.jsonl` (one record per session)
- Aggregated view written to `budget.yaml` after each session for dashboard consumption
- Monthly archives: `.logs/spending-2026-03.jsonl`

### Pricing model (hardcoded initially, configurable later)

```yaml
# Current Anthropic API pricing (as of March 2026)
pricing:
  claude-opus-4:
    input_per_1m_tokens: 15.00
    output_per_1m_tokens: 75.00
  claude-sonnet-4:
    input_per_1m_tokens: 3.00
    output_per_1m_tokens: 15.00
```

### Estimated effort: 2-3 hours

---

## Service 4: Decision Router

**Priority: MEDIUM — needed for human-in-the-loop oversight**

Bridges `decisions_pending` in status.yaml with GitHub Issues for human visibility and resolution.

### What it does
1. When an agent writes a decision to `decisions_pending`, create a GitHub Issue
2. Label the issue `decision-needed`, tag with project name
3. When a human comments on/closes the issue, update status.yaml
4. Poll GitHub Issues periodically for resolved decisions

### File: `orchestrator/src/decision-router.ts`

```typescript
class DecisionRouter {
  // Scan all projects for new unsynced decisions
  async syncToGitHub(): Promise<void>;

  // Check GitHub for resolved decisions
  async syncFromGitHub(): Promise<void>;

  // Create a GitHub Issue for a decision
  private async createIssue(project: string, decision: Decision): Promise<string>;

  // Parse a GitHub Issue comment as a decision answer
  private parseResolution(issue: GitHubIssue): string | null;
}
```

### Implementation
- Uses `gh` CLI (already available via GitEngine's exec pattern)
- `gh issue create --label "decision-needed" --title "..." --body "..."`
- `gh issue list --label "decision-needed" --state closed --json number,title,comments`
- Decisions get a `github_issue` field in status.yaml tracking the issue number
- Poll frequency: every daemon cycle (30 min)

### Estimated effort: 3-4 hours

---

## Service 5: Experiment Runner (Modal)

**Priority: MEDIUM — needed for empirical projects**

Manages GPU compute via Modal for running benchmarks, evaluations, and training runs. No SSH, no Docker builds, no server management.

### What it does
1. Agent designs an experiment and writes a Modal Python script + config
2. Orchestrator invokes the experiment via Modal's TypeScript SDK
3. Modal auto-provisions GPU, runs the experiment, streams logs
4. Results are written to Modal Volumes
5. Orchestrator reads results back and updates the project directory
6. GPU scales to zero automatically — no cleanup needed

### File: `orchestrator/src/experiment-runner.ts`

```typescript
import { ModalClient } from "modal";

interface ExperimentSpec {
  name: string;
  projectName: string;
  gpu: "T4" | "A10G" | "L4" | "A100" | "A100-80GB" | "H100";
  estimatedHours: number;
  estimatedCostUsd: number;
  modalApp: string;          // Modal app name (e.g., "reasoning-gaps-eval")
  modalFunction: string;     // Function name to call
  config: Record<string, unknown>;  // Experiment config passed as argument
}

interface ExperimentResult {
  name: string;
  status: "completed" | "failed" | "timeout";
  durationMs: number;
  costUsd: number;
  metrics: Record<string, number>;
  artifacts: string[];     // Paths to downloaded result files
  logs: string;            // Path to log file
}

class ExperimentRunner {
  private modal: ModalClient;

  constructor() {
    this.modal = new ModalClient();
  }

  // Launch an experiment via Modal
  async run(spec: ExperimentSpec): Promise<ExperimentResult> {
    const fn = await this.modal.functions.fromName(spec.modalApp, spec.modalFunction);
    const call = await fn.spawn([spec.config]);

    // Poll for completion, stream logs
    const result = await call.get();
    return this.processResult(spec, result);
  }

  // For one-off experiments: create a sandbox with custom image
  async runSandbox(spec: SandboxExperimentSpec): Promise<ExperimentResult> {
    const app = await this.modal.apps.fromName("deepwork", { createIfMissing: true });
    const image = this.buildImage(spec.requirements);
    const sb = await this.modal.sandboxes.create(app, image, { gpu: spec.gpu });

    // Upload experiment files, exec, download results
    const proc = await sb.exec(["python", spec.script, "--config", JSON.stringify(spec.config)]);
    const output = await proc.stdout.readText();
    await sb.terminate();

    return this.parseOutput(spec, output);
  }

  // Download results from Modal Volume to local project directory
  async downloadResults(volumeName: string, remotePath: string, localPath: string): Promise<void>;

  // Check if a Modal app/function is deployed
  async isDeployed(appName: string): Promise<boolean>;
}
```

### Two integration paths

**Path A: Pre-deployed functions (recommended for stable experiments)**
```
Agent writes experiments/eval_models.py with Modal decorators
  → Human or CI deploys: modal deploy experiments/eval_models.py
  → Orchestrator calls function via TS SDK: fn.spawn([config])
  → Results written to Modal Volume
  → Orchestrator downloads results
```

**Path B: Sandboxes (for dynamic/one-off experiments)**
```
Agent writes a plain Python script + requirements
  → Orchestrator creates Modal Sandbox from TS SDK
  → Sandbox gets custom image built from requirements
  → Orchestrator execs the script in the sandbox
  → Reads stdout/results, terminates sandbox
```

### Safety
- `timeout` set on every Modal function (max 6 hours default, 24 hours absolute max)
- Budget tracker checks before launching (estimated cost vs. remaining budget)
- Modal dashboard provides real-time cost monitoring
- `modal app stop <name>` as emergency kill switch
- Scale-to-zero means no forgotten running servers

### Dependencies
- `modal` npm package (TypeScript SDK, currently v0.7.x, Beta)
- `modal` Python package (for experiment scripts)
- Modal account with MODAL_TOKEN_ID and MODAL_TOKEN_SECRET in .env

### Estimated effort: 4-6 hours (simpler than SSH-based approach)

---

## Service 6: Publishing Pipeline

**Priority: MEDIUM — needed for web presence**

Automates the path from research output to public-facing content.

### 6a. Research Website

Static site generated from project outputs. Serves as the public face of Deepwork Research.

### File structure

```
site/
├── astro.config.mjs
├── package.json
├── src/
│   ├── layouts/
│   │   └── Base.astro          # Shared layout
│   ├── pages/
│   │   ├── index.astro         # Homepage: research agenda, recent work
│   │   ├── papers.astro        # Publications list
│   │   ├── blog/
│   │   │   ├── index.astro     # Blog index
│   │   │   └── [...slug].astro # Blog post pages
│   │   └── tools.astro         # Open-source tools and benchmarks
│   ├── content/
│   │   ├── papers/             # Paper metadata (YAML frontmatter + summary)
│   │   └── blog/               # Blog posts (Markdown)
│   └── components/
│       ├── Header.astro
│       ├── PaperCard.astro
│       └── Footer.astro
├── public/
│   ├── papers/                 # PDFs of published papers
│   └── figures/                # Figures from papers
└── .github/
    └── workflows/
        └── deploy.yml          # Build and deploy on push to main
```

### Tech choice: Astro
- Static site generator, perfect for content-heavy research sites
- Markdown/MDX support for blog posts
- Zero JS by default (fast loading)
- Deploy to GitHub Pages (free) or Cloudflare Pages

### Content flow
```
Paper completes →
  Writer agent generates blog post (shared/prompts/blog-post.md) →
  Blog post saved to site/src/content/blog/<slug>.md →
  Paper PDF copied to site/public/papers/<name>.pdf →
  Paper metadata added to site/src/content/papers/<name>.yaml →
  Git push triggers GitHub Actions → site deploys
```

### 6b. arXiv Submission Automation

Semi-automated — prepares the submission package, human clicks submit.

### File: `orchestrator/src/arxiv-packager.ts`

```typescript
class ArxivPackager {
  // Package a project's paper for arXiv submission
  async package(projectName: string): Promise<string>; // Returns path to .tar.gz

  // Steps:
  // 1. Compile LaTeX to verify it builds
  // 2. Flatten \input includes into single .tex file
  // 3. Collect figures, .bib, .bst, style files
  // 4. Create tar.gz with correct structure
  // 5. Validate against arXiv requirements (file sizes, formats)
  // 6. Output instructions for manual submission
}
```

### 6c. Social Media Templates

Not a service — just structured templates the writer agent fills in:

```
site/src/content/social/
├── twitter-thread-template.md
└── linkedin-post-template.md
```

Generated by the writer agent alongside each blog post. Human posts manually (for now).

### Estimated effort: 6-8 hours (website), 2-3 hours (arXiv packager)

---

## Service 7: Activity Logger & Monitor

**Priority: HIGH — needed for observability**

Centralized logging for all platform activity. Powers the CLI dashboard and future web dashboard.

### What it does
1. Logs every event: session start/stop, commits, decisions, budget changes, errors
2. Stores in append-only JSONL files
3. Provides query interface for dashboard consumption
4. Health checks for running sessions and daemon process

### File: `orchestrator/src/logger.ts`

```typescript
type EventType =
  | "session_start" | "session_end" | "session_error"
  | "commit" | "push" | "pr_created" | "pr_merged"
  | "decision_created" | "decision_resolved"
  | "budget_spend" | "budget_alert"
  | "experiment_start" | "experiment_end"
  | "phase_transition"
  | "daemon_start" | "daemon_stop" | "daemon_error";

interface ActivityEvent {
  timestamp: string;
  type: EventType;
  project?: string;
  agent?: string;
  data: Record<string, unknown>;
}

class ActivityLogger {
  // Log an event
  async log(event: Omit<ActivityEvent, "timestamp">): Promise<void>;

  // Query recent events
  async recent(count: number, filter?: { type?: EventType; project?: string }): Promise<ActivityEvent[]>;

  // Get events for a time range
  async range(from: string, to: string): Promise<ActivityEvent[]>;
}
```

### Storage layout

```
.logs/
├── activity.jsonl           # All events (append-only, current month)
├── activity-2026-03.jsonl   # Monthly archives
├── spending.jsonl           # Budget-specific (BudgetTracker writes here)
├── daemon.log               # Daemon process stdout/stderr
├── sessions/
│   └── <project>/
│       └── <timestamp>.jsonl  # Per-session transcript
└── experiments/
    └── <experiment-name>.log  # GPU experiment logs
```

### File: `orchestrator/src/monitor.ts`

```typescript
interface HealthStatus {
  daemon: "running" | "stopped" | "error";
  daemonUptime: number;
  activeSessions: { project: string; agent: string; duration: number }[];
  diskUsage: { total: number; used: number; worktrees: number };
  budgetStatus: BudgetStatus;
  lastActivity: ActivityEvent;
  staleProjects: string[];  // No activity in >48h
  errors: ActivityEvent[];  // Recent errors
}

class Monitor {
  async getHealth(): Promise<HealthStatus>;
  async checkDisk(): Promise<void>;      // Alert if disk >80%
  async checkStale(): Promise<void>;     // Flag projects with no recent activity
  async checkBudget(): Promise<void>;    // Alert on budget thresholds
}
```

### Estimated effort: 3-4 hours

---

## Service 8: Enhanced CLI

**Priority: MEDIUM — improves human oversight**

Extend the existing Ink CLI with interactive commands and richer displays.

### New commands

```
deepwork                    # Dashboard (existing, works)
deepwork run                # Start daemon (Service 2)
deepwork start <project>    # Manual session start (existing, needs SDK)
deepwork stop <project>     # Stop running session
deepwork new <project>      # Create project from template (needs implementation)
deepwork status <project>   # Detailed project view (needs implementation)
deepwork decide             # List/resolve pending decisions (needs implementation)
deepwork logs [project]     # Tail activity log
deepwork budget             # Detailed budget breakdown
deepwork health             # System health check
```

### File changes

```
orchestrator/src/index.ts         # Add new command routing
orchestrator/src/commands/
├── run.ts                        # Daemon start
├── new.ts                        # Project creation from template
├── status.ts                     # Detailed project view
├── decide.ts                     # Decision resolution
├── logs.ts                       # Log tailing
├── budget.ts                     # Budget detail
└── health.ts                     # Health check
```

### Interactive `decide` command

```
$ deepwork decide

Pending Decisions:

[1] reasoning-gaps (HIGH)
    Should we focus on TC⁰ or NC¹ complexity class for formal framework?
    Options:
      a) TC⁰ (tighter connection to transformers)
      b) NC¹ (broader applicability)
      c) Both (comparative approach)

    Context: TC⁰ captures threshold circuits, directly modeling...

Enter choice (1a/1b/1c) or 's' to skip:
```

### Estimated effort: 4-6 hours

---

## Service 9: GitHub Actions CI/CD

**Priority: LOW initially, HIGH once publishing**

Automated workflows triggered on git events.

### Workflows to create

```yaml
# .github/workflows/paper-build.yml
# Trigger: push to research/* or paper/* branches
# Action: Compile LaTeX → PDF, upload as artifact
# Why: Verify paper compiles, make PDF reviewable in PRs

# .github/workflows/site-deploy.yml
# Trigger: push to main (site/ directory changes)
# Action: Build Astro site, deploy to GitHub Pages
# Why: Auto-publish blog posts and paper summaries

# .github/workflows/status-check.yml
# Trigger: push (status.yaml changes)
# Action: Validate status.yaml against schema
# Why: Catch malformed status files before they break the dashboard

# .github/workflows/lint.yml
# Trigger: push to any branch
# Action: TypeScript type-check, ESLint, prose linting (Vale)
# Why: Maintain code and writing quality
```

### Estimated effort: 3-4 hours

---

## Build Order

### Phase 1: Core Autonomy (Week 1)

Must be built first — everything else depends on these.

```
Session Runner (Service 1)     ← CRITICAL PATH
    ↓
Activity Logger (Service 7)    ← needed by everything that follows
    ↓
Budget Tracker (Service 3)     ← needed before daemon can enforce limits
    ↓
Daemon Scheduler (Service 2)   ← the main loop that ties it all together
```

**Milestone:** `deepwork run` starts the daemon, which autonomously launches Claude sessions on the reasoning-gaps project, commits work, tracks spending.

**Estimated total: 16-20 hours of implementation**

### Phase 2: Human Interface (Week 2)

Makes the platform observable and controllable.

```
Enhanced CLI (Service 8)       ← new commands: new, decide, status, health
    +
Decision Router (Service 4)    ← GitHub Issues integration
    +
Monitor (part of Service 7)    ← health checks, stale detection
```

**Milestone:** Human can create projects from templates, resolve decisions via CLI or GitHub Issues, monitor platform health.

**Estimated total: 8-12 hours**

### Phase 3: Research Output (Week 3-4)

Produces visible output.

```
Research Website (Service 6a)  ← Astro site with blog and papers
    +
arXiv Packager (Service 6b)    ← LaTeX packaging for submission
    +
GitHub Actions (Service 9)     ← Paper compilation, site deployment
```

**Milestone:** First blog post published on research website. Paper compilation automated. Site auto-deploys on push.

**Estimated total: 10-14 hours**

### Phase 4: Compute (Week 4-6)

Enables empirical research.

```
Experiment Runner (Service 5)  ← GPU provisioning and execution
```

**Milestone:** Agent can design an experiment, the runner provisions a GPU, executes it, and returns results.

**Estimated total: 8-10 hours**

---

## Complete File Inventory: What Gets Created

### New orchestrator source files

```
orchestrator/src/
├── index.ts                    # MODIFY: add command routing
├── session-runner.ts           # NEW: Claude Agent SDK integration
├── daemon.ts                   # NEW: scheduling loop
├── budget-tracker.ts           # NEW: spending tracking
├── decision-router.ts          # NEW: GitHub Issues bridge
├── experiment-runner.ts        # NEW: GPU compute management
├── logger.ts                   # NEW: activity logging
├── monitor.ts                  # NEW: health checks
├── commands/
│   ├── run.ts                  # NEW: daemon start command
│   ├── new.ts                  # NEW: project creation
│   ├── status.ts               # NEW: project detail
│   ├── decide.ts               # NEW: decision resolution
│   ├── logs.ts                 # NEW: log viewer
│   ├── budget.ts               # NEW: budget detail
│   └── health.ts               # NEW: health check
├── experiment-runner.ts         # NEW: Modal integration for GPU compute
├── session-manager.ts          # MODIFY: wire to session-runner
├── project-manager.ts          # MODIFY: add validation, template support
├── git-engine.ts               # EXISTING: no changes needed
└── yaml.ts                     # REPLACE: use 'yaml' npm package
```

### New site directory

```
site/
├── astro.config.mjs
├── package.json
├── tsconfig.json
├── src/
│   ├── layouts/Base.astro
│   ├── pages/
│   │   ├── index.astro
│   │   ├── papers.astro
│   │   ├── blog/index.astro
│   │   └── blog/[...slug].astro
│   ├── content/
│   │   ├── config.ts
│   │   ├── papers/
│   │   └── blog/
│   └── components/
│       ├── Header.astro
│       ├── PaperCard.astro
│       └── Footer.astro
└── public/
    └── papers/
```

### New GitHub Actions

```
.github/workflows/
├── paper-build.yml
├── site-deploy.yml
├── status-check.yml
└── lint.yml
```

### New dependencies to add

```json
// orchestrator/package.json
{
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.0",  // already listed
    "yaml": "^2.7.0",                             // proper YAML parser
    "modal": "^0.7.0"                             // Modal TypeScript SDK (GPU compute)
  }
}

// site/package.json (new workspace)
{
  "dependencies": {
    "astro": "^5.0.0",
    "@astrojs/mdx": "^4.0.0"
  }
}
```

```bash
# Python dependencies (for experiment scripts, not in package.json)
pip install modal  # Modal CLI + Python SDK
```

### Runtime directories (gitignored)

```
.worktrees/           # Git worktrees for active sessions
.logs/                # Activity logs, session transcripts, spending
  activity.jsonl
  spending.jsonl
  daemon.log
  sessions/<project>/<timestamp>.jsonl
  experiments/<name>.log
.sessions/            # Session state files
.deepwork.pid         # Daemon PID file
```

### .gitignore additions

```
.worktrees/
.logs/
.sessions/
.deepwork.pid
.env
```

---

## Dependency Graph

```
                    Session Runner
                    /      |       \
                   /       |        \
          Budget Tracker  Logger   Git Engine (existing)
                |          |
                +-----+----+
                      |
                   Daemon
                  /   |   \
                 /    |    \
    Decision Router  Monitor  Experiment Runner
         |                         |
      GitHub API              GPU Provider API
         |
    Enhanced CLI
         |
    Research Website
```

Everything flows up from Session Runner. Build bottom-up.

---

## Configuration Changes

### .env structure (full)

```bash
# Claude API (required)
ANTHROPIC_API_KEY=sk-ant-...

# GitHub (uses gh CLI auth, no key needed)
# Ensure: gh auth status shows authenticated

# Firecrawl (optional, for web research)
FIRECRAWL_API_KEY=fc-...

# Modal (GPU compute — modal.com)
MODAL_TOKEN_ID=ak-...
MODAL_TOKEN_SECRET=as-...

# Daemon
DAILY_BUDGET_USD=40
MAX_CONCURRENT_SESSIONS=2
POLL_INTERVAL_MINUTES=30

# Site
SITE_URL=https://deepwork.research
```

### config.yaml additions

```yaml
# Add to existing config.yaml
daemon:
  poll_interval_minutes: 30
  max_concurrent_sessions: 2
  daily_budget_usd: 40
  quiet_hours:
    start: 2   # 2 AM
    end: 6     # 6 AM
  session_defaults:
    researcher:
      max_turns: 50
      max_duration_minutes: 45
      thinking: extended
    writer:
      max_turns: 80
      max_duration_minutes: 60
      thinking: extended
    reviewer:
      max_turns: 30
      max_duration_minutes: 30
      thinking: extended
    editor:
      max_turns: 40
      max_duration_minutes: 30
      thinking: standard
    strategist:
      max_turns: 60
      max_duration_minutes: 45
      thinking: extended

compute:
  provider: modal
  default_gpu: A100-80GB
  max_hours_per_experiment: 8
  monthly_budget_usd: 500

site:
  url: https://deepwork.research
  deploy: github-pages
  auto_blog: true       # Generate blog post for every completed paper
```

---

## Total Effort Estimate

| Service | Hours | Priority | Week |
|---------|-------|----------|------|
| Session Runner | 4-6 | Critical | 1 |
| Activity Logger | 3-4 | Critical | 1 |
| Budget Tracker | 2-3 | High | 1 |
| Daemon Scheduler | 6-8 | Critical | 1 |
| Enhanced CLI | 4-6 | Medium | 2 |
| Decision Router | 3-4 | Medium | 2 |
| Research Website | 6-8 | Medium | 3 |
| arXiv Packager | 2-3 | Medium | 3 |
| GitHub Actions | 3-4 | Low | 3 |
| Experiment Runner (Modal) | 4-6 | Medium | 4 |
| **Total** | **38-50** | | **3-5 weeks** |

With Claude Code writing the implementation, realistic timeline is **2-3 weeks** for Phase 1-3 (core autonomy + human interface + website).
