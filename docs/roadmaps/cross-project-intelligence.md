# Cross-Project Intelligence — Knowledge Transfer Between Research Projects

**Status:** Planned
**Priority:** Medium-High — becomes critical as project count grows beyond 2
**Estimated effort:** 12-17 hours
**Dependencies:** Knowledge graph (planned), OpenClaw agent definitions, PostgreSQL schema

## Motivation

Projects in deepwork are currently siloed. Each project runs in its own worktree on its own branch, with its own `status.yaml`, `BRIEF.md`, and agent context. The daemon schedules sessions per-project. The planner builds prompts per-project. There is no mechanism for findings in one project to inform work in another.

This is a real problem today. The two active research projects — `reasoning-gaps` (what LLMs fail at cognitively) and `agent-failure-taxonomy` (how LLM agents fail in practice) — are deeply related. Reasoning gaps are a *cause* of agent failures. Agent failures are *evidence* of reasoning gaps. Findings from one should actively feed the other:

- `reasoning-gaps` discovers that GPT-4o has weak recursive reasoning (Task B5). This is directly relevant to `agent-failure-taxonomy`'s planned experiment on state tracking in multi-step agents.
- `agent-failure-taxonomy` finds that CoT-based planning sometimes degrades agent performance. This contradicts `reasoning-gaps`' finding that CoT always helps for depth-bounded tasks — a productive tension worth investigating.
- A method developed in `reasoning-gaps` (state machine evaluation for B4) could be adapted for agent evaluation in `agent-failure-taxonomy`.

Without cross-project intelligence, these connections depend on the human researcher remembering them. The platform should surface them automatically.

## Architecture

Cross-project intelligence operates at three levels:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Level 3: Portfolio Strategy                                        │
│  Strategist agent assesses coherence, synergies, conflicts          │
│  Runs: weekly or on-demand                                          │
├─────────────────────────────────────────────────────────────────────┤
│  Level 2: Event-Driven Matching                                     │
│  When a finding is added to project A, check relevance to project B │
│  Runs: per-session (post-hook in daemon)                            │
├─────────────────────────────────────────────────────────────────────┤
│  Level 1: Queryable Cross-Project Data                              │
│  Claims, methods, and findings tagged by project but queryable      │
│  globally via KnowledgeGraph and PostgreSQL                         │
│  Runs: always available                                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Level 1: Cross-Project Query Layer

The knowledge graph (once implemented) enables cross-project queries naturally if claims are tagged by project but queryable globally. The key insight is that claims, methods, and findings already have semantic content — we just need to make them searchable across project boundaries.

```typescript
// Find claims in other projects that relate to a claim in this project
async function findCrossProjectInsights(
  claimId: string,
  sourceProject: string,
): Promise<CrossProjectInsight[]> {
  const claim = await kg.getClaim(claimId);
  const similar = await kg.query(claim.statement, {
    excludeProject: sourceProject,
  });
  return similar
    .filter((s) => s.relevanceScore > 0.8)
    .map((s) => ({
      sourceProject,
      targetProject: s.project,
      sourceClaim: claim,
      relatedClaim: s,
      potentialImplication: "", // LLM generates this
    }));
}
```

In practice, the cross-project query layer also needs to work before the full knowledge graph exists. An interim implementation can use PostgreSQL full-text search over `status.yaml` decisions, session transcripts, and paper claims (from the verification layer):

```sql
-- Find decisions in other projects relevant to a new finding
SELECT d.project, d.decision, d.rationale,
       ts_rank(to_tsvector('english', d.decision || ' ' || d.rationale),
               plainto_tsquery('english', $1)) AS relevance
FROM project_decisions d
WHERE d.project != $2
  AND to_tsvector('english', d.decision || ' ' || d.rationale)
      @@ plainto_tsquery('english', $1)
ORDER BY relevance DESC
LIMIT 10;
```

### Level 2: Event-Driven Cross-Project Matching

Triggers that fire when new information enters any project:

| Event | Source | Action |
|-------|--------|--------|
| New finding added to `status.yaml` | Session post-hook | Check if finding relates to other projects' active hypotheses |
| New paper claim verified | Verification layer | Check if claim contradicts or supports claims in other projects |
| Literature alert matches | Scout agent | If alert is relevant to multiple projects, notify both |
| Method developed | Session transcript | Check if method is applicable to other projects' current phase |
| Experiment completed | Eval manager | Check if results inform other projects' open questions |

The event handler is lightweight — it runs an LLM call (Haiku) with the new information and a summary of other projects' current state. Cost per event: ~$0.01.

### Level 3: Portfolio-Level Strategy

The strategist agent already exists as an `AgentType` in `session-runner.ts`. Its role expands to include cross-project coordination:

- **Synergy detection**: "reasoning-gaps Task B7 (variable binding) is directly relevant to agent-failure-taxonomy's planned experiment on state tracking"
- **Conflict detection**: "reasoning-gaps claims CoT always helps for depth tasks, but agent-failure-taxonomy finds that agent planning with CoT sometimes degrades performance — this tension is worth investigating"
- **Transfer suggestions**: "The state machine evaluation method used in reasoning-gaps B4 should be adapted for agent evaluation in agent-failure-taxonomy"
- **Portfolio coherence**: Are the projects complementary? Are there gaps in coverage? Is effort allocated proportionally to impact?

## Schema Additions

New migration file: `orchestrator/sql/007_cross_project.sql`

```sql
BEGIN;

-- ============================================================
-- Cross-Project Insights — discovered connections between projects
-- ============================================================
CREATE TABLE cross_project_insights (
    id                  SERIAL PRIMARY KEY,
    source_project      TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    target_project      TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    insight_type        TEXT NOT NULL
                        CHECK (insight_type IN (
                            'synergy',           -- finding in A supports work in B
                            'conflict',          -- finding in A contradicts finding in B
                            'method_transfer',   -- method from A applicable to B
                            'shared_evidence',   -- same data/paper relevant to both
                            'gap',               -- neither project covers an important area
                            'duplication'        -- both projects working on the same thing
                        )),
    source_ref          TEXT NOT NULL,           -- claim ID, decision ID, or finding description
    target_ref          TEXT,                    -- what in the target project this relates to
    description         TEXT NOT NULL,           -- human-readable explanation
    implication         TEXT NOT NULL,           -- actionable next step
    relevance_score     REAL NOT NULL DEFAULT 0, -- 0.0-1.0 confidence in the connection
    status              TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN (
                            'pending',           -- awaiting review
                            'acknowledged',      -- seen, no action needed
                            'actioned',          -- led to concrete work
                            'dismissed'          -- not relevant after review
                        )),
    actioned_in_session TEXT,                   -- session ID where this was acted on
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_xp_insights_source ON cross_project_insights (source_project);
CREATE INDEX idx_xp_insights_target ON cross_project_insights (target_project);
CREATE INDEX idx_xp_insights_type   ON cross_project_insights (insight_type);
CREATE INDEX idx_xp_insights_status ON cross_project_insights (status);

-- ============================================================
-- Method Registry — reusable methods across projects
-- ============================================================
CREATE TABLE project_methods (
    id              SERIAL PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    method_name     TEXT NOT NULL,
    description     TEXT NOT NULL,
    implementation  TEXT,                       -- file path or code reference
    applicable_to   TEXT[] DEFAULT '{}',        -- other projects this could apply to
    tags            TEXT[] DEFAULT '{}',        -- semantic tags for matching
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_methods_project ON project_methods (project);
CREATE INDEX idx_methods_tags    ON project_methods USING GIN (tags);

-- ============================================================
-- Portfolio Coherence Reports — periodic strategic assessments
-- ============================================================
CREATE TABLE portfolio_reports (
    id              SERIAL PRIMARY KEY,
    report_type     TEXT NOT NULL
                    CHECK (report_type IN ('weekly', 'on_demand', 'milestone')),
    projects        TEXT[] NOT NULL,            -- projects included in assessment
    coherence_score REAL,                       -- 0.0-1.0 how well projects complement
    synergies       JSONB NOT NULL DEFAULT '[]',
    conflicts       JSONB NOT NULL DEFAULT '[]',
    gaps            JSONB NOT NULL DEFAULT '[]',
    recommendations JSONB NOT NULL DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Convenience view: active cross-project connections
-- ============================================================
CREATE VIEW v_cross_project_active AS
SELECT
    xpi.id,
    xpi.source_project,
    xpi.target_project,
    xpi.insight_type,
    xpi.description,
    xpi.implication,
    xpi.relevance_score,
    xpi.status,
    xpi.created_at
FROM cross_project_insights xpi
WHERE xpi.status IN ('pending', 'acknowledged')
ORDER BY xpi.relevance_score DESC, xpi.created_at DESC;

COMMIT;
```

## New Files

### `orchestrator/src/cross-project.ts` — CrossProjectAnalyzer class

Core module for discovering and managing cross-project connections. Follows existing codebase patterns (ESM, async/await, `pg.Pool`).

```typescript
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type pg from "pg";
import { ProjectManager, type ProjectStatus } from "./project-manager.js";

// ============================================================
// Types
// ============================================================

export interface CrossProjectInsight {
  sourceProject: string;
  targetProject: string;
  insightType:
    | "synergy"
    | "conflict"
    | "method_transfer"
    | "shared_evidence"
    | "gap"
    | "duplication";
  sourceRef: string;
  targetRef: string | null;
  description: string;
  implication: string;
  relevanceScore: number;
}

export interface MethodTransfer {
  fromProject: string;
  toProject: string;
  methodName: string;
  adaptationNotes: string;
}

export interface CoherenceReport {
  projects: string[];
  coherenceScore: number; // 0.0–1.0
  synergies: CrossProjectInsight[];
  conflicts: CrossProjectInsight[];
  gaps: string[];
  recommendations: string[];
  computedAt: string;
}

// ============================================================
// CrossProjectAnalyzer
// ============================================================

export class CrossProjectAnalyzer {
  constructor(
    private pool: pg.Pool,
    private rootDir: string,
    private projectManager: ProjectManager,
  ) {}

  /**
   * Find insights relevant to a specific project from all other projects.
   *
   * Strategy:
   *   1. Load the target project's current state (status.yaml, recent decisions,
   *      active hypotheses, current focus).
   *   2. For each other active project, load its recent findings, decisions,
   *      and methods.
   *   3. Use LLM (Haiku) to assess relevance of each cross-project item
   *      to the target project's current work.
   *   4. Filter by relevance threshold (>0.8) and persist to
   *      cross_project_insights table.
   *
   * Cost: ~$0.02 per project pair per invocation.
   */
  async findInsights(project: string): Promise<CrossProjectInsight[]> {
    /* ... */
  }

  /**
   * Check a single new finding against all other projects.
   *
   * Called as a post-hook when a session produces a new finding
   * (detected by comparing status.yaml before and after the session).
   *
   * Lighter than findInsights() — only checks one finding, not all.
   * Cost: ~$0.005 per finding.
   */
  async checkFinding(
    project: string,
    finding: string,
  ): Promise<CrossProjectInsight[]> {
    /* ... */
  }

  /**
   * Copy/adapt a method from one project to another.
   *
   * Steps:
   *   1. Look up the method in project_methods table.
   *   2. Read the implementation file(s) from the source project.
   *   3. Use LLM to generate an adaptation plan for the target project.
   *   4. Create a backlog ticket in the target project for implementation.
   *   5. Record the transfer in cross_project_insights as 'actioned'.
   */
  async transferMethod(
    fromProject: string,
    toProject: string,
    methodId: string,
  ): Promise<MethodTransfer> {
    /* ... */
  }

  /**
   * Assess how well all active projects complement each other.
   *
   * Evaluates:
   *   - Coverage: Do the projects collectively address a coherent research space?
   *   - Synergy: Are findings in one project actively useful to others?
   *   - Conflict: Are any projects producing contradictory findings?
   *   - Duplication: Are any projects unknowingly working on the same problem?
   *   - Gaps: Are there important areas that no project covers?
   *
   * Uses LLM (Sonnet) for the strategic assessment — this is a high-stakes
   * analysis that benefits from stronger reasoning.
   * Cost: ~$0.10 per portfolio assessment.
   */
  async portfolioCoherence(): Promise<CoherenceReport> {
    /* ... */
  }

  /**
   * Register a method developed in a project for cross-project reuse.
   *
   * Called by session post-hooks when a session creates new evaluation
   * infrastructure, analysis pipelines, or experimental methods.
   */
  async registerMethod(
    project: string,
    methodName: string,
    description: string,
    implementation: string,
    tags: string[],
  ): Promise<void> {
    /* ... */
  }
}
```

### `orchestrator/src/routes/cross-project.ts` — API routes

```typescript
import { Router, type Request, type Response } from "express";
import type pg from "pg";
import { CrossProjectAnalyzer } from "../cross-project.js";
import { ProjectManager } from "../project-manager.js";

export function crossProjectRoutes(pool: pg.Pool, rootDir: string): Router {
  const router = Router();
  const pm = new ProjectManager(rootDir);
  const analyzer = new CrossProjectAnalyzer(pool, rootDir, pm);

  // GET /api/cross-project/insights
  // List all cross-project insights. Query params: ?project=reasoning-gaps&status=pending&type=synergy
  router.get("/insights", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/cross-project/insights/:id
  // Get a single insight with full context.
  router.get("/insights/:id", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/cross-project/insights/:id/action
  // Mark an insight as acknowledged, actioned, or dismissed. Body: { status, sessionId? }
  router.post("/insights/:id/action", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/cross-project/scan
  // Trigger a full cross-project scan for a specific project. Body: { project }
  router.post("/scan", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/cross-project/portfolio
  // Get the latest portfolio coherence report.
  router.get("/portfolio", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/cross-project/portfolio
  // Trigger a new portfolio coherence assessment.
  router.post("/portfolio", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/cross-project/methods
  // List all registered methods. Query params: ?project=reasoning-gaps&tags=evaluation
  router.get("/methods", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/cross-project/methods/:id/transfer
  // Initiate a method transfer. Body: { toProject }
  router.post(
    "/methods/:id/transfer",
    async (req: Request, res: Response) => {
      /* ... */
    },
  );

  return router;
}
```

## OpenClaw Integration

### Cross-Project Triggers in the Daemon

The daemon's session post-processing (after quality scoring) adds a cross-project check:

```typescript
// In daemon.ts, after session completes and quality is scored:
private async postSessionCrossProject(
  projectName: string,
  sessionResult: SessionResult,
): Promise<void> {
  if (!this.dbPool) return;

  const analyzer = new CrossProjectAnalyzer(
    this.dbPool,
    this.config.rootDir,
    this.projectManager,
  );

  // Compare status.yaml before/after to detect new findings
  const newFindings = await this.detectNewFindings(projectName);

  for (const finding of newFindings) {
    const insights = await analyzer.checkFinding(projectName, finding);
    for (const insight of insights) {
      // Log to activity feed
      this.logger.log("cross_project_insight", {
        source: insight.sourceProject,
        target: insight.targetProject,
        type: insight.insightType,
        description: insight.description,
      });

      // Post to forum if relevance is high
      if (insight.relevanceScore > 0.9) {
        await this.notifier.send(
          `Cross-project insight: ${insight.description}`,
        );
      }
    }
  }
}
```

### Sol's Morning Standup Integration

Sol (the coordinator agent in OpenClaw) already runs morning standups. The standup prompt expands to include cross-project intelligence:

```
## Cross-Project Connections (new section in standup)

Before generating the standup, query GET /api/cross-project/insights?status=pending
for any unacknowledged cross-project connections.

For each pending insight:
- Summarize the connection in plain language
- Recommend an action (investigate, create backlog ticket, schedule session, dismiss)
- Tag the relevant agents who should be aware

Example standup addition:
  "Cross-project alert: reasoning-gaps found that GPT-4o struggles with
   recursive state tracking (Task B5, accuracy 34%). This directly relates
   to agent-failure-taxonomy's planned experiment on multi-step agent state
   management. Recommend: @experimenter adapt the B5 evaluation harness
   for agent contexts before running the state tracking experiment."
```

### Noor (Scout) Multi-Project Awareness

Noor already scouts for literature relevant to the current project. The scout prompt expands:

```
When evaluating a paper or preprint for relevance, check against ALL active
projects, not just the one you were dispatched for. If a paper is relevant
to multiple projects:
1. Create a literature alert for each relevant project
2. Note the cross-project relevance explicitly
3. If the paper connects two projects' research questions, flag it as
   a potential cross-project insight via POST /api/cross-project/scan
```

### The Strategist Role — Cross-Project Coordinator

The strategist agent definition (`.claude/agents/strategist.md`) expands significantly:

```
## Cross-Project Responsibilities

You are the portfolio-level thinker. Beyond strategizing for individual
projects, you assess how all active projects relate to each other.

### Weekly Portfolio Review
Every Monday (or when triggered), run a portfolio coherence assessment:
1. GET /api/cross-project/portfolio — read the latest report
2. If stale (>7 days), POST /api/cross-project/portfolio to generate a new one
3. For each recommendation in the report, create actionable backlog tickets
4. Post a portfolio summary to the forum

### On-Demand Cross-Project Analysis
When dispatched with reason containing "cross-project":
1. GET /api/cross-project/insights?status=pending
2. For each pending insight, assess whether it's genuinely actionable
3. For synergies: create a plan to exploit the connection
4. For conflicts: design an experiment or analysis to resolve the tension
5. For method transfers: assess feasibility and create implementation tickets
6. Update insight status via POST /api/cross-project/insights/:id/action

### Conflict Resolution
When two projects produce contradictory findings:
1. Verify both findings are well-supported (check verification reports)
2. Identify the source of disagreement (different definitions? different data?)
3. Propose a resolution (additional experiment, refined claim, scope limitation)
4. Create backlog tickets in both projects
```

### Forum Cross-Project Tagging

Forum discussions (from the OpenClaw collective schema) gain cross-project awareness:

```sql
-- Add cross-project tag support to forum posts
ALTER TABLE forum_posts ADD COLUMN cross_project_refs TEXT[] DEFAULT '{}';

-- When creating a forum post that references multiple projects,
-- tag it with all relevant project IDs. Forum queries can then
-- filter for posts relevant to a specific project OR spanning multiple.
```

## Integration with Existing Systems

### Session Runner Hook

In `orchestrator/src/session-runner.ts`, after a session completes:

```typescript
// After building the session result, check for cross-project relevance
if (result.status === "completed" && result.commitsCreated.length > 0) {
  // Defer to daemon's postSessionCrossProject — the session runner
  // doesn't have a DB pool, so this runs in the daemon's post-processing
  result.metadata = {
    ...result.metadata,
    needsCrossProjectCheck: true,
  };
}
```

### Planner Integration

When the daemon's planner builds session prompts, it can now include cross-project context:

```typescript
// In daemon.ts, when building session config:
private async buildCrossProjectContext(project: string): Promise<string> {
  if (!this.dbPool) return "";

  const { rows } = await this.dbPool.query(
    `SELECT description, implication FROM cross_project_insights
     WHERE target_project = $1 AND status IN ('pending', 'acknowledged')
     ORDER BY relevance_score DESC LIMIT 5`,
    [project],
  );

  if (rows.length === 0) return "";

  return `\n## Cross-Project Context\n` +
    rows
      .map((r) => `- ${r.description}\n  Implication: ${r.implication}`)
      .join("\n");
}
```

This context gets appended to the agent's prompt, so a researcher working on `agent-failure-taxonomy` might see:

```
## Cross-Project Context
- reasoning-gaps found that recursive state tracking is a primary failure mode
  for GPT-4o (34% accuracy on B5). Implication: Design your agent state
  tracking experiments to specifically test recursive depth.
```

### Dashboard Display

The Astro dashboard at `site/` should show:

- **Cross-project insights feed**: List of pending connections, sortable by relevance and type
- **Portfolio coherence score**: Single number (0-100) with trend sparkline
- **Network visualization**: Projects as nodes, insights as edges, colored by type (green=synergy, red=conflict, blue=transfer)
- **Method registry**: Browsable list of reusable methods with transfer status

## Task Breakdown

| # | Task | Est. hours | Dependencies |
|---|------|-----------|--------------|
| 1 | Schema migration (`007_cross_project.sql`) | 1.0 | None |
| 2 | Cross-project query functions (full-text search interim) | 2.0 | Task 1 |
| 3 | `CrossProjectAnalyzer` class — `findInsights`, `checkFinding` | 3.0 | Task 2 |
| 4 | `CrossProjectAnalyzer` class — `portfolioCoherence` | 1.5 | Task 3 |
| 5 | `CrossProjectAnalyzer` class — `transferMethod`, `registerMethod` | 1.5 | Task 3 |
| 6 | Event handler — daemon post-session cross-project check | 2.0 | Task 3 |
| 7 | Strategist agent definition updates | 1.5 | Task 4 |
| 8 | Forum cross-project tagging (schema + query changes) | 1.0 | Task 1 |
| 9 | Sol standup integration (prompt updates) | 1.0 | Task 3 |
| 10 | Noor scout multi-project awareness (prompt updates) | 0.5 | Task 3 |
| 11 | API routes (`routes/cross-project.ts`) | 1.5 | Tasks 3-5 |
| 12 | Dashboard cross-project view | 2.0 | Task 11 |
| **Total** | | **~18.5 hours** | |

### Suggested Implementation Order

**Phase 1 — Foundation (Tasks 1-3, ~6 hours)**
Schema, query layer, and core analyzer. After this phase, the system can discover cross-project connections on demand.

**Phase 2 — Automation (Tasks 4-6, ~5 hours)**
Portfolio coherence, method transfers, and event-driven matching. After this phase, connections are discovered automatically as sessions run.

**Phase 3 — Agent Integration (Tasks 7-10, ~4 hours)**
Strategist, Sol, Noor, and forum integration. After this phase, the OpenClaw collective is cross-project-aware.

**Phase 4 — API and Dashboard (Tasks 11-12, ~3.5 hours)**
External visibility and human oversight.

## Success Criteria

1. **Automatic detection within one daemon cycle.** When a finding in project A is relevant to project B, the system surfaces it as a `cross_project_insight` before the next session in project B starts.

2. **Actionable insights, not noise.** Insights should include a concrete `implication` field that tells an agent what to do. "These are related" is not sufficient. "Adapt reasoning-gaps' B4 state machine method for agent evaluation — estimated 2 hours, creates a reusable eval harness" is.

3. **Methods are reusable.** The method registry should contain at least one transferred method within the first month of operation. Transfer should produce a working adaptation, not just a copy.

4. **Portfolio coherence improves.** The strategist's weekly assessment should show increasing coherence as cross-project insights are actioned.

5. **Low overhead.** Cross-project checks should add less than $0.05 per session and less than 30 seconds of latency to post-session processing.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False connections (noise) | Agents waste time on irrelevant cross-project "insights" | High relevance threshold (0.8), human-reviewable status workflow, dismiss option |
| LLM hallucinated connections | Insights that sound plausible but are wrong | Ground all insights in specific claims/findings with references; verification step before actioning |
| Overhead per session increases | Slower daemon cycles, higher cost | Lightweight check (Haiku, single call) for per-session; heavy analysis (Sonnet) only weekly |
| Method transfers produce broken code | Adapted methods don't work in target project | Transfer creates a backlog ticket with adaptation plan, not direct code; human or agent reviews before merging |
| Cross-project context clutters prompts | Agents distracted by irrelevant context from other projects | Limit to top 5 insights by relevance; only include pending/acknowledged status |

## Open Questions

1. **When should cross-project insights block work?** Current design: never. Insights are advisory. But should a confirmed conflict between projects pause the conflicting work until resolved?

2. **How to handle project-specific terminology?** `reasoning-gaps` talks about "CoT lift" while `agent-failure-taxonomy` might call the same concept "planning benefit." The system needs to recognize semantic equivalence across different project vocabularies.

3. **Scale beyond 2 projects?** With N projects, cross-project checks are O(N) per session. At 10+ projects, this may need batching or a more efficient matching strategy (embedding-based rather than LLM-based).

4. **Knowledge graph dependency?** The full vision requires a knowledge graph for semantic matching. The interim full-text search approach works but produces lower-quality matches. Should we prioritize the knowledge graph roadmap to unlock better cross-project intelligence?
