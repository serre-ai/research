# Deepwork: AI-Driven Research Platform

## Vision

A platform that uses Claude Code to autonomously research, write, and iterate on Turing Award-caliber work — papers, lectures, code, and experiments. Multiple research projects run simultaneously, each with its own Claude Code agent, coordinated through automated git workflows with human oversight.

## Documentation Index

| Document | Purpose |
|----------|---------|
| [EXECUTION-PLAN.md](docs/EXECUTION-PLAN.md) | **Start here** — sprint-by-sprint plan to first running research |
| [BUILD-PLAN.md](docs/BUILD-PLAN.md) | Service architecture — interfaces, dependencies, technical specs |
| [OPERATIONS.md](docs/OPERATIONS.md) | How the platform runs day-to-day — lifecycle, cadences, failure recovery |
| [INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) | Servers, daemon setup, GPU compute, environment configuration |
| [SCALING.md](docs/SCALING.md) | Budget tiers, concurrent capacity, cost-per-paper estimates |
| [AGENT-TEAM.md](docs/AGENT-TEAM.md) | Agent roles, handoff protocols, session configuration |
| [PORTFOLIO.md](docs/PORTFOLIO.md) | Project mix, venue targeting, staggering strategy |
| [QUALITY-STANDARDS.md](docs/QUALITY-STANDARDS.md) | Publication standards, review rubrics, quality gates |
| [PUBLISHING.md](docs/PUBLISHING.md) | arXiv, conference submissions, website, social media |
| [IDEA-PIPELINE.md](docs/IDEA-PIPELINE.md) | How research ideas are captured, scored, and promoted to projects |
| [CREDIBILITY.md](docs/CREDIBILITY.md) | Building recognition as an independent researcher |
| [ROADMAP.md](docs/ROADMAP.md) | 12-month plan with milestones and budget projections |

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         Human Layer                              │
│  CLI Dashboard (deepwork)  ·  Research Website  ·  GitHub        │
│  Decision Queue  ·  Notifications  ·  Paper Preview              │
└──────────────────────────┬───────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                    Deepwork Daemon (Node.js)                      │
│                                                                   │
│  ┌────────────┐  ┌────────────────┐  ┌──────────────┐           │
│  │ Scheduler  │→ │ Session Runner │→ │ Budget       │           │
│  │            │  │ (Agent SDK)    │  │ Tracker      │           │
│  └────────────┘  └───────┬────────┘  └──────────────┘           │
│                          │                                       │
│  ┌───────────────┐  ┌────▼───────┐  ┌──────────────┐           │
│  │ Decision      │  │ Activity   │  │ Experiment   │           │
│  │ Router        │  │ Logger     │  │ Runner       │           │
│  └───────┬───────┘  └────────────┘  └──────┬───────┘           │
│          │                                  │                    │
│  ┌───────▼──────────────────────────────────▼───────────────┐   │
│  │  Project Manager  ·  Git Engine  ·  Monitor              │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────┬───────────────┬───────────────┬───────────────────────────┘
       │               │               │
┌──────▼─────┐  ┌──────▼─────┐  ┌──────▼─────┐
│  Project A  │  │  Project B  │  │  Project C  │
│  Claude SDK │  │  Claude SDK │  │  Claude SDK │
│  Worktree A │  │  Worktree B │  │  Worktree C │
│  Branch A   │  │  Branch B   │  │  Branch C   │
└─────────────┘  └─────────────┘  └─────────────┘
       │               │               │
┌──────▼───────────────▼───────────────▼──────────────┐
│                  Git Monorepo                         │
│  main ← PRs ← research/project-* branches           │
│  Automated commits · Conventional format · CI/CD     │
└──────────┬───────────────────────────┬──────────────┘
           │                           │
    ┌──────▼──────┐             ┌──────▼──────┐
    │   GitHub    │             │ Modal (GPUs) │
    │  Issues/PRs │             │ scale-to-zero│
    └──────┬──────┘             └──────────────┘
           │
    ┌──────▼──────┐
    │  Research   │
    │  Website    │
    └─────────────┘
```

---

## Key Design Decisions

### 1. Claude Code SDK (API Keys, not Max subscription)

The Claude Agent SDK (`@anthropic-ai/claude-agent-sdk`) is the programmatic interface. It spawns Claude Code as a subprocess with full tool access.

**Authentication**: Requires `ANTHROPIC_API_KEY` (pay-per-token). Claude Max subscription OAuth cannot be used for SDK-built products (Anthropic policy). However, each collaborator can use their own Claude Max subscription for **interactive** Claude Code sessions alongside the automated platform.

**Practical approach**:
- **Automated agents**: Use API key (shared team key from Anthropic Console)
- **Interactive work**: Each person uses their Claude Max subscription directly via `claude` CLI
- Both work in the same monorepo; automated agents create PRs that humans review

### 2. Monorepo with Git Worktrees

Single repository, multiple projects isolated via:
- **Branches**: `research/<project-name>` for each active project
- **Worktrees**: Each Claude SDK session operates in its own worktree, preventing conflicts
- **PRs**: All work merges to `main` via pull requests for review

### 3. Structured Status Files as Data Layer

Each project maintains a `status.yaml` file — the universal data layer consumed by CLI, dashboards, and the orchestrator. Agents write status; everything else reads it.

### 4. GitHub as Initial UI

MVP uses GitHub Issues (decision queue), Projects board (kanban), and PR reviews (approval workflow). Custom CLI tool for developer convenience. Web dashboard comes later.

---

## Repository Structure

```
deepwork/
├── ARCHITECTURE.md              # This file
├── CLAUDE.md                    # Instructions for Claude Code sessions
├── package.json                 # Monorepo root
├── turbo.json                   # (future) Task orchestration
│
├── orchestrator/                # Core platform engine
│   ├── src/
│   │   ├── index.ts             # Entry point
│   │   ├── project-manager.ts   # Create, configure, monitor projects
│   │   ├── session-manager.ts   # Claude SDK session lifecycle
│   │   ├── git-engine.ts        # Automated git operations
│   │   ├── decision-router.ts   # Route decisions to humans
│   │   └── status-writer.ts     # Update status.yaml files
│   ├── package.json
│   └── tsconfig.json
│
├── cli/                         # CLI dashboard tool
│   ├── src/
│   │   ├── index.tsx            # Ink-based CLI entry
│   │   ├── commands/
│   │   │   ├── status.tsx       # turing status
│   │   │   ├── start.tsx        # turing start <project>
│   │   │   ├── decide.tsx       # turing decide (review queue)
│   │   │   └── new.tsx          # turing new <project>
│   │   └── components/
│   │       ├── ProjectList.tsx
│   │       ├── StatusBar.tsx
│   │       └── DecisionPrompt.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── projects/                    # Research projects live here
│   └── <project-name>/
│       ├── status.yaml          # Machine-readable project state
│       ├── BRIEF.md             # Research brief / goals
│       ├── CLAUDE.md            # Project-specific Claude instructions
│       ├── paper/               # Paper drafts (LaTeX or Markdown)
│       │   ├── main.tex
│       │   └── figures/
│       ├── src/                 # Code / experiments
│       ├── data/                # Small datasets (large → Git LFS)
│       └── notes/               # Research notes, lecture drafts
│
├── shared/                      # Shared across projects
│   ├── templates/               # Paper templates, project scaffolds
│   ├── prompts/                 # Reusable Claude prompt fragments
│   └── utils/                   # Shared utilities
│
├── .github/
│   ├── workflows/
│   │   ├── paper-build.yml      # Compile LaTeX → PDF on push
│   │   ├── lint-prose.yml       # Vale prose linting
│   │   └── ci.yml               # Test orchestrator/CLI code
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       └── decision.yml         # Decision request template
│
└── .claude/
    ├── settings.json            # Claude Code project settings
    ├── commands/                 # Custom slash commands
    │   ├── research.md          # /research command
    │   ├── write-paper.md       # /write-paper command
    │   └── review.md            # /review command
    └── agents/                  # Custom agent definitions
        ├── researcher.md        # Deep research agent
        ├── writer.md            # Paper/lecture writing agent
        └── reviewer.md          # Critical review agent
```

---

## Status File Format

```yaml
# projects/<name>/status.yaml
project: quantum-error-correction
title: "Topological Quantum Error Correction via Machine Learning"
status: active          # active | paused | review | completed
phase: research         # research | drafting | revision | final
confidence: 0.7         # agent's confidence in current direction

created: 2026-03-07
updated: 2026-03-07T21:30:00Z

collaborators:
  - oddurs
  - colleague

current_focus: "Surveying recent advances in surface code decoders"
next_steps:
  - "Analyze 2025 papers on ML-assisted decoding"
  - "Draft methodology section"
  - "Implement baseline decoder"

decisions_pending:
  - id: d001
    question: "Should we focus on surface codes or color codes?"
    context: "Surface codes have more literature but color codes may yield novel results"
    options: ["Surface codes", "Color codes", "Both (comparative study)"]
    priority: high
    created: 2026-03-07

git:
  branch: research/quantum-error-correction
  latest_commit: "abc123"
  open_prs: []

metrics:
  papers_reviewed: 12
  sections_drafted: 1
  experiments_run: 0
```

---

## Git Workflow

### Branch Strategy
```
main                                    # Reviewed, stable
├── research/quantum-error-correction   # Active research project
├── research/neural-scaling-laws        # Another project
├── paper/qec/draft-v1                  # Paper draft branch
└── feature/orchestrator-session-mgmt   # Platform infrastructure
```

### Automated Agent Workflow
1. Agent works in a git worktree on `research/<project>` branch
2. Makes conventional commits: `paper(qec): add methodology section`
3. When a milestone is reached, agent creates a PR to `main`
4. PR triggers CI: compile paper, lint prose, run tests
5. Human reviews PR in GitHub (or via `deepwork decide`)
6. Merge to main on approval

### Commit Convention
```
type(project): description

Types:
  paper    - Paper content changes
  research - Research notes, literature review
  code     - Code/experiment changes
  data     - Dataset additions or changes
  feat     - Platform feature
  fix      - Bug fix
  docs     - Documentation
  chore    - Maintenance
```

---

## Orchestrator Design

### Session Manager
```typescript
// Simplified session lifecycle
import { query, ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

interface ProjectSession {
  projectName: string;
  sessionId?: string;
  worktreePath: string;
  branch: string;
  status: "running" | "paused" | "waiting_decision" | "completed";
}

async function runProjectSession(project: ProjectSession) {
  const brief = readFileSync(`projects/${project.projectName}/BRIEF.md`);
  const status = readYaml(`projects/${project.projectName}/status.yaml`);

  for await (const msg of query({
    prompt: buildPrompt(brief, status),
    options: {
      allowedTools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"],
      cwd: project.worktreePath,
      permissionMode: "acceptEdits",  // auto-approve file edits
      maxTurns: 50,
    }
  })) {
    handleMessage(msg, project);
  }
}
```

### Decision Router
When an agent encounters a decision point (low confidence, multiple approaches, needs domain expertise):
1. Agent writes to `decisions_pending` in `status.yaml`
2. Decision router creates a GitHub Issue with the `decision-needed` label
3. Human is notified (GitHub notification / Slack webhook)
4. Human responds on the Issue or via `deepwork decide`
5. Decision router updates `status.yaml` and resumes agent

---

## Implementation Status

### Phase 1: Foundation — COMPLETE
- [x] Research and architecture design
- [x] Git repo with monorepo structure (orchestrator + cli workspaces)
- [x] CLAUDE.md with project conventions
- [x] Git engine: full worktree/branch/commit/PR operations
- [x] Project manager: status.yaml CRUD, project scaffolding
- [x] Session manager: worktree setup, prompt building (SDK integration TODO)
- [x] CLI dashboard: projects, budget, activity, resources display
- [x] First research project (reasoning-gaps, NeurIPS 2026)
- [x] Agent definitions: researcher, writer, reviewer, strategist, editor
- [x] Shared templates, prompts, and standards library
- [x] Comprehensive documentation suite (12 docs)

### Phase 2: Core Autonomy — NEXT (see [BUILD-PLAN.md](docs/BUILD-PLAN.md))
- [ ] **Session Runner**: Claude Agent SDK integration (the critical missing piece)
- [ ] **Activity Logger**: centralized event logging
- [ ] **Budget Tracker**: per-session cost tracking, daily/monthly limits
- [ ] **Daemon Scheduler**: `deepwork run` — the always-on loop
- [ ] First fully autonomous research session

### Phase 3: Human Interface
- [ ] Enhanced CLI: `new`, `decide`, `status`, `health`, `logs`, `budget` commands
- [ ] Decision Router: status.yaml ↔ GitHub Issues bridge
- [ ] Monitor: health checks, stale detection, disk/budget alerts

### Phase 4: Research Output
- [ ] Research website (Astro static site, GitHub Pages)
- [ ] arXiv submission packager
- [ ] Blog post auto-generation from papers
- [ ] GitHub Actions: paper compilation, site deployment, status validation

### Phase 5: Compute
- [ ] Experiment Runner: GPU provisioning (Lambda Labs API)
- [ ] Experiment lifecycle: spec → provision → execute → collect → terminate
- [ ] Cost tracking for GPU compute

---

## Authentication & Collaboration Model

### For Automated Agents (Orchestrator)
- Single `ANTHROPIC_API_KEY` from Anthropic Console
- Pay-per-token billing
- Shared across all automated sessions
- Stored in `.env` (gitignored)

### For Interactive Work (You & Colleague)
- Each person uses their own Claude Max subscription
- Run `claude` CLI directly in the repo
- Work on any branch, create PRs normally
- The automated system and humans coexist in the same repo

### Access Control
- GitHub repository with collaborator access for both users
- Branch protection on `main` requiring PR review
- CODEOWNERS file routing reviews by project directory
