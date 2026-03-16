# Master Roadmap: Intelligence Stack

> From session scheduler to research intelligence engine.

This roadmap sequences 10 capability roadmaps into agent-team sprints. Each sprint is scoped for a single focused context window — one agent team, one coherent deliverable, 1-2 days of implementation.

## Overview

### The Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: EVOLUTION                                         │
│  Meta-learning, cross-project intelligence, self-tuning     │
│  Sprint 9-10                                                │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: INTELLIGENCE                                      │
│  Research planner, closed-loop experiments, verification,   │
│  review simulation, literature intelligence                  │
│  Sprints 4-8                                                │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: FOUNDATION                                        │
│  Knowledge graph, event architecture, adaptive sessions     │
│  Sprints 1-3                                                │
├─────────────────────────────────────────────────────────────┤
│  EXISTING: Daemon, sessions, agents, OpenClaw, budget, API  │
└─────────────────────────────────────────────────────────────┘
```

### Capability Map

| # | Capability | Roadmap | Layer | Est. Hours |
|---|-----------|---------|-------|-----------|
| 1 | Knowledge Graph | [knowledge-graph.md](roadmaps/knowledge-graph.md) | Foundation | 12-16h |
| 2 | Event Architecture | [event-architecture.md](roadmaps/event-architecture.md) | Foundation | 14-19h |
| 3 | Adaptive Sessions | [adaptive-sessions.md](roadmaps/adaptive-sessions.md) | Foundation | 13-17h |
| 4 | Research Planner | [research-planner.md](roadmaps/research-planner.md) | Intelligence | 15-21h |
| 5 | Verification Layer | [verification-layer.md](roadmaps/verification-layer.md) | Intelligence | 12-16h |
| 6 | Literature Intelligence | [literature-intelligence.md](roadmaps/literature-intelligence.md) | Intelligence | 16-22h |
| 7 | Closed-Loop Experiments | [closed-loop-experiments.md](roadmaps/closed-loop-experiments.md) | Intelligence | 17-23h |
| 8 | Review Simulation | [review-simulation.md](roadmaps/review-simulation.md) | Intelligence | 12-16h |
| 9 | Cross-Project Intelligence | [cross-project-intelligence.md](roadmaps/cross-project-intelligence.md) | Evolution | 12-17h |
| 10 | Meta-Learning | [meta-learning.md](roadmaps/meta-learning.md) | Evolution | 24-28h |
| | **Total** | | | **147-195h** |

### Dependencies

```
Knowledge Graph ──┬── Research Planner ──── Adaptive Sessions
                  ├── Verification Layer
                  ├── Literature Intelligence
                  ├── Closed-Loop Experiments
                  ├── Cross-Project Intelligence
                  └── Meta-Learning

Event Architecture ── Research Planner
                   ── Literature Intelligence
                   ── Verification Layer (auto-trigger)

Review Simulation ── Verification Layer (consults report)

Meta-Learning ── all above (consumes data from everything)
```

Knowledge Graph and Event Architecture are the critical path. Everything else depends on one or both.

---

## Sprint Plan

### Phase 1: Foundation (Sprints 1-3)

---

#### Sprint 1: Knowledge Graph — Schema & Core

**Team**: Engineer + Researcher
**Duration**: 1-2 days
**Branch**: `feature/knowledge-graph`

The knowledge graph is the foundation everything else builds on. This sprint creates the schema, core class, and embedding pipeline.

**Deliverables**:
1. SQL migration `005_knowledge_graph.sql` — `claims`, `claim_relations`, `knowledge_snapshots`, `confidence_history` tables with pgvector
2. `orchestrator/src/knowledge-graph.ts` — KnowledgeGraph class with full CRUD:
   - `addClaim()`, `addRelation()`, `getClaim()`, `getSubgraph()`
   - `query()` via vector similarity (pgvector cosine distance)
   - `findContradictions()`, `getEvidenceChain()`
   - `updateConfidence()`
3. Embedding integration — Voyage-3-Lite or OpenAI text-embedding-3-small
4. API routes: `GET/POST /api/knowledge/claims`, `GET /api/knowledge/query`
5. Unit test: add claim, query by similarity, verify retrieval

**Files created/modified**:
- `orchestrator/sql/005_knowledge_graph.sql` (new)
- `orchestrator/src/knowledge-graph.ts` (new)
- `orchestrator/src/api.ts` (add knowledge routes)

**Roadmap ref**: [knowledge-graph.md](roadmaps/knowledge-graph.md) — Tasks 1-3

---

#### Sprint 2: Knowledge Graph — Integration & Backfill

**Team**: Engineer + Researcher
**Duration**: 1-2 days
**Branch**: `feature/knowledge-graph`

Wire the knowledge graph into the session runner and backfill from existing project data.

**Deliverables**:
1. OpenClaw `knowledge` skill — agents can read/write claims during sessions
2. Session runner integration — auto-inject relevant knowledge subgraph into prompt context
3. Backfill script — extract claims from:
   - reasoning-gaps eval results (~243 finding claims)
   - reasoning-gaps paper LaTeX (~30-50 paper claims)
   - status.yaml decisions (~15-25 decision claims)
   - Literature notes (~20-30 citation claims)
4. Knowledge graph stats in health/daemon endpoints
5. Deploy migration to VPS PostgreSQL

**Files created/modified**:
- `openclaw/skills/knowledge/` (new skill directory)
- `orchestrator/src/session-runner.ts` (inject knowledge context)
- `scripts/backfill-knowledge-graph.ts` (new)
- `orchestrator/src/api.ts` (health endpoint update)

**Roadmap ref**: [knowledge-graph.md](roadmaps/knowledge-graph.md) — Tasks 4-8

---

#### Sprint 3: Event Architecture

**Team**: Engineer
**Duration**: 1-2 days
**Branch**: `feature/event-bus`

Replace polling with events. Hybrid approach — add EventBus alongside existing daemon loop.

**Deliverables**:
1. SQL migration — `domain_events` table with trigger for `pg_notify`
2. `orchestrator/src/event-bus.ts` — EventBus class:
   - `emit(event)` — insert into domain_events, triggers LISTEN/NOTIFY
   - `on(type, handler)` — register handler
   - `start()` / `stop()` — subscribe/unsubscribe to pg_notify channel
   - Dead-letter handling for failed handlers
3. `orchestrator/src/event-handlers.ts` — handler registry
4. Migrate session chaining to events (critic.verdict → chain next agent)
5. Migrate budget alerts to events
6. API endpoint: `GET /api/events/recent`
7. WebSocket broadcast of events to dashboard

**Files created/modified**:
- `orchestrator/sql/006_event_bus.sql` (new)
- `orchestrator/src/event-bus.ts` (new)
- `orchestrator/src/event-handlers.ts` (new)
- `orchestrator/src/daemon.ts` (initialize EventBus, hybrid mode)
- `orchestrator/src/api.ts` (events endpoint)

**Roadmap ref**: [event-architecture.md](roadmaps/event-architecture.md) — Tasks 1-7

---

### Phase 2: Intelligence (Sprints 4-8)

---

#### Sprint 4: Research Planner

**Team**: Engineer + Strategist
**Duration**: 2 days
**Branch**: `feature/research-planner`

The planner replaces the daemon's scoring heuristic with intelligent task composition. Depends on knowledge graph (Sprint 1-2) and event bus (Sprint 3).

**Deliverables**:
1. `orchestrator/src/research-planner.ts` — ResearchPlanner class:
   - `planNextActions(maxActions)` → `SessionBrief[]`
   - Gap identification from knowledge graph
   - Contradiction detection
   - Risk assessment (which issues threaten reviewer rejection?)
   - Session brief composition with model selection, context composition, deliverables
2. `SessionBrief` interface with full adaptive session config
3. Replace daemon's `scoreProjects()` with `planner.planNextActions()`
4. Update session-runner to accept `SessionBrief` (context composition, model override, turn budget)
5. Post-session evaluation: did the session achieve its deliverables?
6. Feature flag: `USE_RESEARCH_PLANNER=1` for safe rollout
7. Wire into Sol's morning standup heartbeat

**Files created/modified**:
- `orchestrator/src/research-planner.ts` (new)
- `orchestrator/src/session-runner.ts` (accept SessionBrief)
- `orchestrator/src/daemon.ts` (replace scoreProjects)
- `orchestrator/src/api.ts` (planner status endpoint)
- `openclaw/agents/sol/HEARTBEAT.md` (update standup to use planner)

**Roadmap refs**: [research-planner.md](roadmaps/research-planner.md), [adaptive-sessions.md](roadmaps/adaptive-sessions.md)

---

#### Sprint 5: Verification Layer

**Team**: Engineer + Critic
**Duration**: 1-2 days
**Branch**: `feature/verification`

Every paper claim gets traced to supporting evidence. Runs automatically after paper edits.

**Deliverables**:
1. `orchestrator/src/verification.ts` — ClaimVerifier class:
   - `extractClaims(latexPath)` → structured claims from LaTeX
   - `linkEvidence(claim)` → find supporting data/figures/tables
   - `verifyAll(project)` → full verification report
   - `checkConsistency(project)` → cross-reference all numbers
2. Integration with knowledge graph (claim confidence updates)
3. Event handler: `paper.edited` → auto-run verification
4. API endpoint: `GET /api/projects/:id/verification`
5. OpenClaw `verify` skill for agent access
6. Test with reasoning-gaps paper

**Files created/modified**:
- `orchestrator/src/verification.ts` (new)
- `orchestrator/sql/007_verification.sql` (new)
- `orchestrator/src/event-handlers.ts` (add paper.edited handler)
- `orchestrator/src/api.ts` (verification endpoint)
- `openclaw/skills/verify/` (new skill)

**Roadmap ref**: [verification-layer.md](roadmaps/verification-layer.md)

---

#### Sprint 6: Literature Intelligence

**Team**: Engineer + Scout
**Duration**: 1-2 days
**Branch**: `feature/literature-intel`

Continuous monitoring of arXiv and Semantic Scholar with semantic matching against the knowledge graph.

**Deliverables**:
1. `orchestrator/src/literature-monitor.ts` — LiteratureMonitor class:
   - `pollArxiv(categories)` → parse daily RSS feed
   - `pollCitations(paperIds)` → Semantic Scholar citation monitoring
   - `matchAgainstKnowledgeGraph(papers)` → semantic similarity matching
   - `generateAlert(paper, matchedClaims)` → structured alert with implications
2. Semantic Scholar API client (no key required for basic usage)
3. arXiv RSS parser
4. Embedding and similarity matching (reuse knowledge graph's embedding pipeline)
5. Event emission: `literature.alert` when relevant paper found
6. Daemon integration: poll per cycle
7. Forum auto-posting for high-priority alerts (via Noor)
8. API endpoint: `GET /api/literature/alerts`

**Files created/modified**:
- `orchestrator/src/literature-monitor.ts` (new)
- `orchestrator/src/lit-types.ts` (new)
- `orchestrator/src/event-handlers.ts` (literature.alert handler)
- `orchestrator/src/daemon.ts` (add literature poll to cycle)
- `orchestrator/src/api.ts` (literature endpoints)
- `openclaw/agents/noor/HEARTBEAT.md` (update to consume alerts)

**Roadmap ref**: [literature-intelligence.md](roadmaps/literature-intelligence.md)

---

#### Sprint 7: Closed-Loop Experiments

**Team**: Engineer + Experimenter
**Duration**: 2 days
**Branch**: `feature/experiment-loop`

Automated hypothesis → experiment → analysis → belief update loop.

**Deliverables**:
1. `orchestrator/src/experiment-loop.ts` — ExperimentLoop class:
   - `designExperiment(hypothesis)` → ExperimentSpec
   - `execute(spec)` → run via eval pipeline
   - `analyze(spec, rawResults)` → statistical analysis with effect sizes, CIs
   - `updateBeliefs(result)` → update knowledge graph
   - `suggestFollowUp(result)` → generate next experiments
2. `orchestrator/src/eval-bridge.ts` — TypeScript↔Python bridge:
   - Spawns Python eval scripts with structured JSON I/O
   - Collects results, writes to PostgreSQL
   - Progress reporting via WebSocket
3. Statistical analysis module (effect sizes, confidence intervals)
4. Knowledge graph integration (auto-create finding claims)
5. Planner integration (planner can trigger experiment loops)
6. Test with reasoning-gaps B2 anomaly

**Files created/modified**:
- `orchestrator/src/experiment-loop.ts` (new)
- `orchestrator/src/eval-bridge.ts` (new)
- `orchestrator/src/stats.ts` (new)
- `orchestrator/src/research-planner.ts` (add experiment planning)
- `orchestrator/src/api.ts` (experiment status endpoints)

**Roadmap ref**: [closed-loop-experiments.md](roadmaps/closed-loop-experiments.md)

---

#### Sprint 8: Review Simulation

**Team**: Engineer + Critic
**Duration**: 1-2 days
**Branch**: `feature/review-simulation`

Synthetic peer review with calibrated reviewer personas. Predicts acceptance probability.

**Deliverables**:
1. `shared/prompts/reviewer-personas.yaml` — 5 reviewer profiles (methodologist, theorist, empiricist, domain expert, area chair)
2. `orchestrator/src/review-simulator.ts` — ReviewSimulator class:
   - `simulate(paperPath, venue, numReviewers)` → SimulatedReview[]
   - `aggregate(reviews)` → AcceptancePrediction (probability, consensus, top weaknesses)
   - `prioritizeRevisions(reviews)` → ranked actionable improvements
3. Score-to-probability calibration (NeurIPS acceptance curves)
4. SQL migration for review history
5. API endpoints: `POST /api/projects/:id/simulate-review`, `GET /api/projects/:id/reviews`
6. Integration with verification report (reviewers see evidence status)
7. Test with reasoning-gaps paper — run full 5-reviewer simulation

**Files created/modified**:
- `orchestrator/src/review-simulator.ts` (new)
- `shared/prompts/reviewer-personas.yaml` (new)
- `orchestrator/sql/008_review_simulation.sql` (new)
- `orchestrator/src/api.ts` (review simulation endpoints)
- `openclaw/skills/review-simulate/` (new skill)

**Roadmap ref**: [review-simulation.md](roadmaps/review-simulation.md)

---

### Phase 3: Evolution (Sprints 9-10)

---

#### Sprint 9: Cross-Project Intelligence

**Team**: Engineer + Strategist
**Duration**: 1-2 days
**Branch**: `feature/cross-project`

Knowledge transfer between projects. The strategist becomes a cross-project coordinator.

**Deliverables**:
1. `orchestrator/src/cross-project.ts` — CrossProjectAnalyzer class:
   - `findInsights(project)` → cross-project connections via knowledge graph
   - `transferMethod(fromProject, toProject, methodId)` → adapt methods across projects
   - `portfolioCoherence()` → how well do projects complement each other?
2. Event handler: when finding added to project A, check relevance to project B
3. Strategist agent update: cross-project responsibilities
4. Sol standup integration: surface cross-project insights
5. Forum cross-project tagging
6. API endpoint: `GET /api/cross-project/insights`
7. Dashboard cross-project view

**Files created/modified**:
- `orchestrator/src/cross-project.ts` (new)
- `orchestrator/src/event-handlers.ts` (cross-project matching)
- `.claude/agents/strategist.md` (update with cross-project role)
- `orchestrator/src/api.ts` (cross-project endpoints)
- `openclaw/agents/sol/HEARTBEAT.md` (cross-project in standup)

**Roadmap ref**: [cross-project-intelligence.md](roadmaps/cross-project-intelligence.md)

---

#### Sprint 10: Meta-Learning

**Team**: Engineer + Strategist
**Duration**: 2-3 days
**Branch**: `feature/meta-learning`

The platform learns from its own data to improve over time.

**Deliverables**:
1. `orchestrator/src/meta-learning.ts` — MetaLearner class:
   - `analyzeEffectiveness()` → session effectiveness by agent/model/task/phase
   - `suggestOptimizations()` → actionable platform improvements
   - `updateSessionDefaults(agentType, taskType)` → auto-tune configs
   - `generateWeeklyInsights()` → what we learned about our process
2. SQL migration for aggregation tables (`session_effectiveness`, `optimization_log`)
3. Planner integration: consult effectiveness data when selecting model/turns
4. A/B testing framework: compare old vs new session defaults
5. Weekly insights posted to forum by Lev
6. API endpoints: `GET /api/meta/effectiveness`, `GET /api/meta/optimizations`
7. Dashboard: effectiveness heatmaps, trend charts

**Files created/modified**:
- `orchestrator/src/meta-learning.ts` (new)
- `orchestrator/sql/009_meta_learning.sql` (new)
- `orchestrator/src/research-planner.ts` (consult effectiveness data)
- `orchestrator/src/api.ts` (meta-learning endpoints)
- `openclaw/agents/lev/HEARTBEAT.md` (weekly insights posting)

**Roadmap ref**: [meta-learning.md](roadmaps/meta-learning.md)

---

## Sprint Summary

| Sprint | Capability | Team | Days | Depends On |
|--------|-----------|------|------|-----------|
| **1** | Knowledge Graph — Schema & Core | Engineer + Researcher | 1-2 | — |
| **2** | Knowledge Graph — Integration & Backfill | Engineer + Researcher | 1-2 | Sprint 1 |
| **3** | Event Architecture | Engineer | 1-2 | — |
| **4** | Research Planner + Adaptive Sessions | Engineer + Strategist | 2 | Sprints 1-3 |
| **5** | Verification Layer | Engineer + Critic | 1-2 | Sprints 1-3 |
| **6** | Literature Intelligence | Engineer + Scout | 1-2 | Sprints 1-3 |
| **7** | Closed-Loop Experiments | Engineer + Experimenter | 2 | Sprints 1-4 |
| **8** | Review Simulation | Engineer + Critic | 1-2 | Sprint 5 |
| **9** | Cross-Project Intelligence | Engineer + Strategist | 1-2 | Sprints 1-4 |
| **10** | Meta-Learning | Engineer + Strategist | 2-3 | All above |

**Critical path**: Sprint 1 → Sprint 2 → Sprint 4 → Sprint 7

**Parallelizable**: Sprints 1+3 can run in parallel. Sprints 5+6 can run in parallel. Sprints 8+9 can run in parallel.

### Optimal Execution Timeline

```
Week 1:  Sprint 1 (KG schema)  +  Sprint 3 (events)     — parallel
Week 2:  Sprint 2 (KG backfill) → Sprint 4 (planner)     — sequential
Week 3:  Sprint 5 (verification) + Sprint 6 (literature)  — parallel
Week 4:  Sprint 7 (experiments)  + Sprint 8 (review sim)  — parallel*
Week 5:  Sprint 9 (cross-project) + Sprint 10 (meta)      — parallel start
Week 6:  Sprint 10 continued + integration testing

* Sprint 8 depends on Sprint 5, so start 8 mid-week after 5 completes
```

**Total elapsed time**: ~6 weeks
**Total effort**: ~150-200 hours

---

## Budget Impact

### Implementation Cost

All implementation is done by Claude Code agents, so cost = API tokens.

| Phase | Sprints | Est. Sessions | Est. Cost |
|-------|---------|--------------|-----------|
| Foundation | 1-3 | 15-20 | $30-60 |
| Intelligence | 4-8 | 25-35 | $60-120 |
| Evolution | 9-10 | 15-20 | $30-60 |
| **Total** | 1-10 | 55-75 | **$120-240** |

### Ongoing Operating Cost

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| Embeddings (knowledge graph + literature) | ~$1-2 | Voyage-3-Lite or text-embedding-3-small |
| Literature polling | ~$0 | Semantic Scholar API is free |
| Review simulations | ~$15-25/paper | 5 Opus reviews per simulation |
| Meta-learning analysis | ~$2-5 | Weekly Sonnet analysis session |
| Existing costs unchanged | ~$550 | Claude Code Max, Hetzner, Firecrawl, API calls |
| **Total new operating cost** | **~$20-35/month** | |

The intelligence stack adds minimal ongoing cost. The biggest expense (review simulation) is per-paper, not continuous.

---

## Success Metrics

### After Phase 1 (Sprints 1-3)
- [ ] Knowledge graph has 300+ claims from reasoning-gaps backfill
- [ ] Agents can query "what do we know about X" and get relevant claims
- [ ] Events propagate in < 5 seconds (not 60-minute cycles)
- [ ] `npx tsc --noEmit` passes with all new code

### After Phase 2 (Sprints 4-8)
- [ ] Planner produces specific session briefs (not generic "run a writer")
- [ ] Session quality scores increase measurably (>10% avg improvement)
- [ ] Every paper claim has a verification link
- [ ] New arXiv papers detected within 24 hours
- [ ] At least one hypothesis tested via closed-loop without human intervention
- [ ] Review simulation predicts acceptance within 15% of actual

### After Phase 3 (Sprints 9-10)
- [ ] Cross-project insights surfaced automatically (at least 1/week)
- [ ] Quality-per-dollar improves month over month
- [ ] Platform auto-tunes session configs based on effectiveness data
- [ ] Weekly meta-learning insights posted to forum

### North Star
A single researcher with Deepwork produces work that competes with well-funded lab teams — not by working harder, but by having an intelligent system that reasons about research, learns from its own process, and continuously improves.

---

## How to Execute

Each sprint is designed to be executed by a **single Claude Code agent session** (or a small sequence of sessions). The sprint descriptions above serve as the session brief — copy the deliverables and file lists into the agent's prompt.

**Workflow per sprint**:
1. Create feature branch
2. Run engineer agent with sprint deliverables as prompt
3. Run `npx tsc --noEmit` to verify compilation
4. Deploy migration to VPS
5. Test new endpoints via API
6. Create PR to main
7. Merge and start next sprint

Sprints 1+3 should be the first to execute — they're independent and form the foundation for everything else.
