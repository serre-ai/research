# Deepwork: Architecture

## Vision

A platform that uses Claude Code to autonomously research, write, and iterate on Turing Award-caliber work -- papers, lectures, code, and experiments. Multiple research projects run simultaneously, each coordinated through an intelligence stack that combines persistent knowledge, intelligent planning, and autonomous execution.

## Documentation Index

| Document | Purpose |
|----------|---------|
| [VISION.md](VISION.md) | Mission, principles, philosophy, success metrics |
| [EXECUTION-PLAN.md](docs/EXECUTION-PLAN.md) | Sprint-by-sprint plan to first running research |
| [BUILD-PLAN.md](docs/BUILD-PLAN.md) | Service architecture -- interfaces, dependencies, technical specs |
| [OPERATIONS.md](docs/OPERATIONS.md) | Day-to-day operations -- lifecycle, cadences, failure recovery |
| [INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) | Servers, daemon setup, GPU compute, environment configuration |
| [SCALING.md](docs/SCALING.md) | Budget tiers, concurrent capacity, cost-per-paper estimates |
| [AGENT-TEAM.md](docs/AGENT-TEAM.md) | Agent roles, handoff protocols, session configuration |
| [PORTFOLIO.md](docs/PORTFOLIO.md) | Project mix, venue targeting, staggering strategy |
| [QUALITY-STANDARDS.md](docs/QUALITY-STANDARDS.md) | Publication standards, review rubrics, quality gates |
| [PUBLISHING.md](docs/PUBLISHING.md) | arXiv, conference submissions, website, social media |
| [IDEA-PIPELINE.md](docs/IDEA-PIPELINE.md) | Research idea capture, scoring, and promotion |
| [CREDIBILITY.md](docs/CREDIBILITY.md) | Building recognition as an independent researcher |
| [ROADMAP.md](docs/ROADMAP.md) | 12-month plan with milestones and budget projections |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Human Layer                                │
│  CLI Dashboard  ·  Research Website  ·  GitHub  ·  Notifications    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                     Event Bus (PostgreSQL LISTEN/NOTIFY)             │
│  session.complete · knowledge.updated · review.requested            │
│  literature.match · experiment.result · planner.task_ready          │
└──┬──────────────┬──────────────┬──────────────┬─────────────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐
│Research│  │Literature│  │ Review   │  │  Meta-Learning   │
│Planner │  │ Monitor  │  │Simulator │  │  (session quality │
│        │  │          │  │          │  │   → improvements) │
└───┬────┘  └────┬─────┘  └────┬─────┘  └──────────────────┘
    │            │              │
    │   ┌────────▼──────────────▼──────────────────────────┐
    │   │           Knowledge Graph (PostgreSQL + pgvector) │
    │   │  Claims · Findings · Hypotheses · Citations       │
    │   │  Evidence chains · Confidence weights · Embeddings│
    │   │  Cross-project queries · Semantic retrieval       │
    │   └──────────────────────┬───────────────────────────┘
    │                          │
    ▼                          ▼
┌───────────────────────────────────────────────────────────┐
│                    Execution Engine                        │
│                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │Session Runner│  │ Experiment   │  │  Verification   │  │
│  │(Claude SDK) │  │ Runner       │  │  Layer          │  │
│  │             │  │ (hyp→eval→   │  │  (claim↔evidence│  │
│  │ adaptive    │  │  belief      │  │   traceability) │  │
│  │ composition │  │  update)     │  │                 │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                │                    │           │
│  ┌──────▼────────────────▼────────────────────▼────────┐  │
│  │  Git Engine · Budget Tracker · Activity Logger      │  │
│  └─────────────────────────────────────────────────────┘  │
└──────┬───────────────┬───────────────┬────────────────────┘
       │               │               │
┌──────▼─────┐  ┌──────▼─────┐  ┌──────▼─────┐
│  Project A  │  │  Project B  │  │  Project C  │
│  Worktree A │  │  Worktree B │  │  Worktree C │
│  Branch A   │  │  Branch B   │  │  Branch C   │
└─────────────┘  └─────────────┘  └─────────────┘
       │               │               │
┌──────▼───────────────▼───────────────▼──────────────┐
│                  Git Monorepo                         │
│  main ← PRs ← research/project-* branches           │
└──────────────────────────────────────────────────────┘
```

---

## Knowledge Graph

### Purpose

The knowledge graph is the platform's long-term memory. Every meaningful artifact -- claims, findings, hypotheses, citations, experimental results, failed approaches -- is stored as a node with pgvector embeddings for semantic retrieval. Relationships encode provenance: which experiment supports which claim, which paper inspired which hypothesis.

### Schema Design

```
knowledge_nodes
  id            UUID PRIMARY KEY
  project_id    UUID REFERENCES projects(id)  -- NULL for cross-project
  node_type     ENUM('claim', 'finding', 'hypothesis', 'citation',
                     'experiment', 'method', 'dataset', 'decision')
  content       TEXT
  embedding     VECTOR(1536)                  -- pgvector, text-embedding-3-small
  confidence    FLOAT                         -- 0.0 to 1.0
  metadata      JSONB
  created_at    TIMESTAMPTZ
  updated_at    TIMESTAMPTZ

knowledge_edges
  id            UUID PRIMARY KEY
  source_id     UUID REFERENCES knowledge_nodes(id)
  target_id     UUID REFERENCES knowledge_nodes(id)
  edge_type     ENUM('supports', 'contradicts', 'derives_from',
                     'cites', 'refines', 'supersedes', 'related_to')
  weight        FLOAT
  metadata      JSONB
  created_at    TIMESTAMPTZ
```

### Key Operations

- **Semantic search**: Find nodes nearest to an embedding query, filtered by type or project
- **Evidence chains**: Traverse edges from a claim to all supporting/contradicting evidence
- **Cross-project queries**: Find related findings across all projects, enabling automatic insight transfer
- **Belief updates**: When new evidence arrives, propagate confidence changes through connected claims
- **Gap detection**: Identify claims with low confidence or thin evidence chains

### Why PostgreSQL + pgvector (not Neo4j)

- Already running PostgreSQL for eval results, sessions, and project state
- pgvector provides production-quality vector similarity search without a separate service
- Graph traversal needs are bounded (evidence chains are shallow, typically 2-4 hops)
- Single database simplifies operations, backups, and transactions
- Neo4j adds operational complexity and a learning curve with marginal benefit for our graph patterns

---

## Research Planner

### Purpose

The planner replaces rigid phase-based scheduling (research → drafting → revision → final) with intelligent task composition. It is a dedicated agent that reasons about what work would most advance each active project, then composes concrete session specifications.

### How It Works

1. **State assessment**: Reads the knowledge graph, status files, recent session outcomes, and project briefs
2. **Task generation**: Produces a ranked list of candidate tasks with expected value estimates
3. **Session specification**: For each selected task, specifies:
   - Model (Sonnet for literature review, Opus for theoretical reasoning, etc.)
   - Max turns and timeout
   - Tools to enable
   - Context to inject (relevant knowledge graph nodes, prior session summaries)
   - Success criteria (what constitutes a useful outcome)
4. **Scheduling**: Respects budget constraints, parallelism limits, and priority ordering
5. **Evaluation**: After session completion, compares actual outcome to expected value and logs the delta

### Adaptive Session Composition

Different task types require different configurations. The planner learns which configurations work:

| Task Type | Typical Model | Turns | Key Tools | Context |
|-----------|--------------|-------|-----------|---------|
| Literature review | Sonnet 4.6 | 30 | WebSearch, WebFetch, Read | Related graph nodes, search queries |
| Formal reasoning | Opus 4.6 | 50 | Read, Write, Edit | Full theoretical framework, prior proofs |
| Benchmark design | Sonnet 4.6 | 40 | Bash, Read, Write | Task specifications, ground truths |
| Statistical analysis | Sonnet 4.6 | 25 | Bash, Read, Write | Raw data paths, analysis pipeline |
| Paper drafting | Opus 4.6 | 60 | Read, Write, Edit | Full paper state, reviewer feedback |
| Adversarial review | Opus 4.6 | 30 | Read | Full draft, venue rubric, evidence chains |

### Planner vs. Daemon Scheduler

The current daemon scheduler polls on a fixed interval, checks which projects need work, and runs a generic session. The planner replaces this with value-driven task selection: it asks "what is the single most valuable thing to do right now?" and produces a precise specification for doing it. The daemon becomes a thin event loop that executes planner decisions.

---

## Verification Layer

### Purpose

Every claim in a paper draft must trace to specific evidence in the knowledge graph. The verification layer enforces this traceability and flags unsupported claims before they reach adversarial review.

### Workflow

1. **Claim extraction**: Parse the paper draft to identify all empirical claims, theoretical assertions, and comparative statements
2. **Evidence linking**: For each claim, query the knowledge graph for supporting evidence nodes
3. **Gap report**: Produce a structured report of:
   - Well-supported claims (evidence chain depth >= 2, confidence >= 0.8)
   - Weakly supported claims (evidence exists but is thin)
   - Unsupported claims (no evidence chain found)
   - Contradicted claims (evidence chain points against the claim)
4. **Resolution**: Unsupported claims are either removed, weakened to hedged language, or queued as tasks for the planner to gather evidence

### Integration with Review Simulation

The verification report feeds directly into review simulation. Synthetic reviewers are given the evidence chains and gap report alongside the draft, enabling them to raise specific, grounded objections rather than generic complaints.

---

## Event-Driven Architecture

### Purpose

Replace the polling daemon with an event-driven system built on PostgreSQL LISTEN/NOTIFY. Events trigger handlers immediately instead of waiting for the next poll cycle.

### Event Types

```
session.started      — agent session begins
session.complete     — agent session ends, results available
session.failed       — agent session errored or timed out

knowledge.updated    — new node or edge added to knowledge graph
knowledge.conflict   — contradictory evidence detected

planner.task_ready   — planner has composed a new task
planner.replan       — conditions changed, replanning needed

literature.new_paper — relevant paper detected on arXiv/Semantic Scholar
literature.match     — new paper semantically matches existing knowledge

experiment.started   — experiment execution begins
experiment.result    — experiment completed with results

review.requested     — paper ready for adversarial review
review.complete      — review finished, objections filed

decision.needed      — human input required
decision.resolved    — human provided decision
```

### Why Event-Driven (not Polling)

- Eliminates wasted cycles: the system only acts when something meaningful happens
- Lower latency: a completed session triggers follow-up immediately, not at next poll interval
- Cleaner composition: handlers are independent, testable, and composable
- PostgreSQL LISTEN/NOTIFY is zero-cost infrastructure (already running Postgres)
- Polling required tuning interval trade-offs (fast polling = wasted resources, slow polling = high latency)

### Migration Path

The current daemon loop (`setInterval` polling every 60 minutes) will be refactored into:
1. An event emitter that publishes to PostgreSQL channels
2. A listener process that subscribes to relevant channels and dispatches to handlers
3. Handlers for each event type (most existing daemon logic maps 1:1 to handlers)

---

## Continuous Literature Intelligence

### Purpose

Monitor arXiv and Semantic Scholar for papers relevant to active projects. New papers are embedded and matched against the knowledge graph. High-relevance matches are surfaced to the planner as potential tasks (read and integrate, update related work, check if findings affect our claims).

### Pipeline

1. **Ingestion**: Daily fetch of new arXiv papers in target categories (cs.CL, cs.AI, cs.LG)
2. **Embedding**: Title + abstract embedded via text-embedding-3-small
3. **Matching**: Cosine similarity against knowledge graph nodes, thresholded at 0.75
4. **Triage**: Matches above threshold emit `literature.match` events
5. **Integration**: Planner decides whether to schedule a review session

---

## Repository Structure

```
deepwork/
├── ARCHITECTURE.md              # This file
├── VISION.md                    # Mission, principles, philosophy
├── CLAUDE.md                    # Instructions for Claude Code sessions
├── package.json                 # Monorepo root
│
├── orchestrator/                # Core platform engine
│   ├── src/
│   │   ├── index.ts             # Entry point
│   │   ├── daemon.ts            # Event loop and handler dispatch
│   │   ├── session-runner.ts    # Claude SDK session lifecycle
│   │   ├── planner.ts           # Research planner agent
│   │   ├── knowledge-graph.ts   # Knowledge graph CRUD and queries
│   │   ├── verification.ts      # Claim-evidence traceability
│   │   ├── literature.ts        # arXiv/Semantic Scholar monitoring
│   │   ├── review-simulator.ts  # Synthetic reviewer personas
│   │   ├── events.ts            # Event bus (LISTEN/NOTIFY)
│   │   ├── git-engine.ts        # Automated git operations
│   │   ├── project-manager.ts   # Project state management
│   │   ├── budget-tracker.ts    # Per-session cost tracking
│   │   ├── activity-logger.ts   # Centralized event logging
│   │   └── api.ts               # REST + WebSocket API
│   ├── sql/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_knowledge_graph.sql
│   │   └── 003_events.sql
│   ├── package.json
│   └── tsconfig.json
│
├── cli/                         # CLI dashboard tool
│   ├── src/
│   │   ├── index.tsx            # Ink-based CLI entry
│   │   ├── commands/
│   │   └── components/
│   ├── package.json
│   └── tsconfig.json
│
├── projects/                    # Research projects
│   └── <project-name>/
│       ├── status.yaml          # Machine-readable project state
│       ├── BRIEF.md             # Research brief / goals
│       ├── CLAUDE.md            # Project-specific Claude instructions
│       ├── paper/               # Paper drafts (LaTeX)
│       ├── benchmarks/          # Benchmark code and results
│       ├── data/                # Datasets (large → Git LFS)
│       └── notes/               # Research notes
│
├── shared/                      # Shared across projects
│   ├── templates/               # Paper templates, project scaffolds
│   ├── prompts/                 # Reusable prompt fragments
│   └── utils/                   # Shared utilities
│
├── site/                        # Research website (Astro + Tailwind)
│   └── src/
│
├── .github/
│   └── workflows/
│       ├── paper-build.yml      # Compile LaTeX → PDF on push
│       ├── lint-prose.yml       # Vale prose linting
│       └── ci.yml               # Test orchestrator/CLI code
│
└── .claude/
    ├── settings.json
    ├── commands/                 # Custom slash commands
    └── agents/                  # Agent definitions
```

---

## Key Design Decisions

### 1. Claude Code SDK (API Keys)

The Claude Agent SDK (`@anthropic-ai/claude-agent-sdk`) is the programmatic interface. It spawns Claude Code as a subprocess with full tool access. Automated agents use `ANTHROPIC_API_KEY` (pay-per-token). Interactive work uses Claude Max subscriptions. Both coexist in the same monorepo.

### 2. Monorepo with Git Worktrees

Single repository, multiple projects isolated via branches (`research/<project-name>`) and worktrees. All work merges to `main` via pull requests.

### 3. PostgreSQL + pgvector for Knowledge Graph

Single database for everything: eval results, session state, knowledge graph with vector embeddings. No separate graph database. PostgreSQL's JSONB handles semi-structured metadata. pgvector handles similarity search. Graph traversals are bounded (2-4 hops) so SQL with recursive CTEs is sufficient.

### 4. Event-Driven over Polling

PostgreSQL LISTEN/NOTIFY replaces the fixed-interval daemon loop. Zero additional infrastructure. Events trigger handlers immediately. The daemon becomes a thin event dispatcher rather than a polling scheduler.

### 5. Planner Agent over Phase Machine

Research does not proceed in fixed phases. The planner agent reasons about task value dynamically, composes sessions with task-appropriate configurations, and adapts to what the system has learned. This replaces the rigid research→drafting→revision→final state machine.

### 6. Verification Before Review

Claims are checked against the knowledge graph before adversarial review, not after. This prevents the common failure mode of generating a fluent paper with unsupported claims. The reviewer receives evidence chains alongside the draft.

### 7. Structured Status Files as Operational State

Each project maintains `status.yaml` as the operational source of truth, consumed by CLI, dashboards, and the orchestrator. The knowledge graph stores long-term research memory. Status files store current state. These are complementary, not redundant.

### 8. GitHub as Collaboration Surface

GitHub Issues (decision queue), PR reviews (approval workflow), and Actions (CI/CD). Custom CLI for developer convenience. The research website serves the public-facing output.

---

## Git Workflow

### Branch Strategy
```
main                                    # Reviewed, stable
├── research/reasoning-gaps             # Active research project
├── research/agent-failure-taxonomy     # Another project
├── paper/reasoning-gaps/draft-v1       # Paper draft branch
└── feature/knowledge-graph             # Platform infrastructure
```

### Automated Agent Workflow
1. Agent works in a git worktree on `research/<project>` branch
2. Makes conventional commits: `paper(reasoning-gaps): add methodology section`
3. At milestones, agent creates a PR to `main`
4. PR triggers CI: compile paper, lint prose, run tests
5. Human reviews and merges

### Commit Convention
```
type(project): description

Types: paper, research, code, data, feat, fix, docs, chore
```

---

## Status File Format

```yaml
# projects/<name>/status.yaml
project: reasoning-gaps
title: "Reasoning Gaps: A Diagnostic Framework"
status: active          # active | paused | review | completed
phase: research         # research | drafting | revision | final
confidence: 0.85

created: 2026-03-01
updated: 2026-03-16T10:00:00Z

current_focus: "Running model evaluations across 9 benchmark tasks"
next_steps:
  - "Complete evaluation of remaining 3 model families"
  - "Run analysis pipeline on full results"
  - "Draft results section"

decisions_made:
  - date: 2026-03-05
    decision: "Use TC^0/NC^1 separation as theoretical foundation"
    rationale: "Well-established conjecture, testable predictions"

git:
  branch: research/reasoning-gaps
  latest_commit: "989f91a"
  open_prs: []

metrics:
  papers_reviewed: 47
  experiments_run: 243
  eval_instances: 121614
```

---

## Implementation Status

### Deployed and Running
- [x] Git monorepo with orchestrator + cli + site workspaces
- [x] TypeScript orchestrator: daemon, session runner, budget tracker, activity logger, API
- [x] PostgreSQL database: 6 tables, materialized view, 121K+ eval results
- [x] Express REST API + WebSocket on port 3001
- [x] Hetzner VPS: Ubuntu 24.04, Node.js 22, systemd daemon, nginx reverse proxy
- [x] CLI dashboard: projects, budget, activity display
- [x] Agent definitions: researcher, writer, reviewer, strategist, editor
- [x] First research project (reasoning-gaps): 9 benchmarks, 9 models, full analysis pipeline
- [x] Research website (Astro + Tailwind)
- [x] Shared templates, prompts, and standards library

### In Progress — Intelligence Stack
- [ ] **Knowledge graph schema** (SQL migration, pgvector extension)
- [ ] **Knowledge graph API** (CRUD, semantic search, evidence chain traversal)
- [ ] **Event bus** (LISTEN/NOTIFY wrapper, handler registration)
- [ ] **Daemon refactor** (polling → event-driven dispatch)
- [ ] **Research planner** (agent-based task composition)
- [ ] **Adaptive session composition** (model/turns/tools per task type)

### Next — Verification and Intelligence
- [ ] **Verification layer** (claim extraction, evidence linking, gap reports)
- [ ] **Review simulation** (synthetic personas, acceptance probability prediction)
- [ ] **Literature monitor** (arXiv/Semantic Scholar ingestion, embedding, matching)
- [ ] **Cross-project intelligence** (graph queries across projects)
- [ ] **Closed-loop experimentation** (hypothesis → experiment → analysis → belief update)

### Future — Meta-Learning and Maturity
- [ ] **Meta-learning** (session quality tracking, planner improvement from outcomes)
- [ ] **Artifact release pipeline** (HuggingFace, GitHub, blog automation)
- [ ] **Project proposal generation** (literature gaps → research questions)
- [ ] **Community feedback integration** (citation tracking, benchmark adoption)

---

## Authentication & Collaboration Model

### Automated Agents (Orchestrator)
- Single `ANTHROPIC_API_KEY` from Anthropic Console (pay-per-token)
- Additional keys: `OPENAI_API_KEY`, `OPENROUTER_API_KEY` for multi-model evaluation
- Stored in `.env` (gitignored)

### Interactive Work
- Each collaborator uses their own Claude Max subscription via `claude` CLI
- Work on any branch, create PRs normally
- Automated system and humans coexist in the same repo

### Access Control
- GitHub repository with collaborator access
- Branch protection on `main` requiring PR review
- API key: `DEEPWORK_API_KEY` for REST/WebSocket access
