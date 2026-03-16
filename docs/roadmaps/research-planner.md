# Research Planner — Implementation Roadmap

> Replaces the daemon's weighted scoring heuristic with an intelligent planning layer that reasons about the intellectual state of each project.

**Status**: Proposed
**Target**: Sprint 10+
**Estimated Effort**: 15-21 hours across 5 sprints

---

## 1. Problem Statement

The current daemon (`orchestrator/src/daemon.ts`) uses project management metrics to decide what to work on:

```typescript
// Current: scoreProjects() in daemon.ts (lines 752-836)
+10  venue deadline within 4 weeks
+5   no session in >24 hours (stale)
+3   has pending next_steps
+2   confidence >= 0.7
-5   confidence < 0.3
-N   exponential backoff for failures
-10  project over daily budget share
-3   recent sessions had low quality
```

Agent type is a static lookup from project phase:

```typescript
// Current: PHASE_TO_AGENT map (lines 17-27)
const PHASE_TO_AGENT: Record<string, AgentType> = {
  "research":             "researcher",
  "analysis":             "experimenter",
  "drafting":             "writer",
  "paper-finalization":   "writer",
  // ...
};
```

This produces sessions like "launch a writer for reasoning-gaps because it's stale and in the drafting phase." There is no awareness of:

- What specific intellectual gaps exist in the research
- Which claims are weakly evidenced and most likely to cause reviewer rejection
- Whether two claims contradict each other
- What the highest-value next action is given the current state of understanding
- Which model (Opus vs. Sonnet vs. Haiku) matches the cognitive demands of the task

The Research Planner replaces scoring-by-staleness with reasoning-about-knowledge.

---

## 2. Architecture

### 2.1 New Files

| File | Purpose |
|------|---------|
| `orchestrator/src/research-planner.ts` | Core planner: gap detection, risk assessment, brief composition |
| `orchestrator/src/knowledge-graph.ts` | In-memory knowledge graph built from status.yaml, decisions, claims, eval results |
| `orchestrator/sql/005_planner_schema.sql` | DB tables for claims, evidence links, session evaluations |

### 2.2 Modified Files

| File | Change |
|------|--------|
| `orchestrator/src/daemon.ts` | Replace `scoreProjects()` + `PHASE_TO_AGENT` with `planner.planNextActions()` |
| `orchestrator/src/session-runner.ts` | Accept full `SessionBrief` instead of `SessionConfig`; inject brief into prompt |
| `orchestrator/src/session-manager.ts` | Pass `SessionBrief` through to runner; return structured evaluation data |
| `orchestrator/src/api.ts` | Add `/api/planner/*` routes for state inspection |
| `orchestrator/src/routes/collective-context.ts` | Extend context injection with planner insights per agent |

### 2.3 System Flow

```
Daemon Cycle
  │
  ├── Before (current)
  │     scoreProjects() → ScoredProject[] → launch by score
  │
  └── After (planner)
        planner.planNextActions(maxActions)
          │
          ├── Load knowledge graph per project
          │     ├── status.yaml (phase, confidence, next_steps)
          │     ├── decisions table (past choices + rationale)
          │     ├── claims table (NEW: tracked assertions)
          │     ├── eval_results (empirical evidence)
          │     └── forum_posts (collective insights)
          │
          ├── Identify gaps, contradictions, risks
          │
          ├── Score by intellectual value (not staleness)
          │
          └── Compose SessionBrief[]
                ├── Specific objective ("Test whether B2 budget_cot
                │    negative lift persists at difficulty > 5")
                ├── Relevant files and knowledge subgraph
                ├── Model selection (Opus for theory, Haiku for sweep)
                ├── Turn budget and constraints
                └── Measurable deliverables

Session Completes
  │
  └── planner.evaluateSession(brief, result)
        ├── Check deliverables against outputs
        ├── Update claim confidence
        ├── Record evaluation in DB
        └── Adjust priority weights for next cycle
```

---

## 3. Data Model

### 3.1 Knowledge Graph (In-Memory)

The knowledge graph is rebuilt at the start of each daemon cycle from DB + YAML. It is not persisted as a graph — the canonical data lives in Postgres tables and project files. The in-memory representation exists only for reasoning.

```typescript
// orchestrator/src/knowledge-graph.ts

interface Claim {
  id: string;                          // e.g. "rg-claim-001"
  project: string;
  statement: string;                   // "CoT lift is negligible for Type 5/6 tasks"
  confidence: number;                  // 0.0-1.0
  evidence: Evidence[];
  status: "hypothesis" | "supported" | "contested" | "refuted";
  source: "framework" | "empirical" | "literature" | "agent";
  sourceAgent?: string;                // which agent proposed this
  createdAt: string;
  updatedAt: string;
}

interface Evidence {
  type: "eval_result" | "literature" | "decision" | "forum_post" | "analysis";
  reference: string;                   // eval run ID, paper DOI, decision ID, etc.
  supports: boolean;                   // true = supports claim, false = contradicts
  strength: "weak" | "moderate" | "strong";
  summary: string;
}

interface Gap {
  id: string;
  project: string;
  type: "untested_hypothesis" | "missing_evidence" | "unexplored_condition"
      | "missing_comparison" | "unwritten_section";
  description: string;
  relatedClaims: string[];             // claim IDs
  severity: "low" | "medium" | "high" | "critical";
  estimatedEffort: number;             // hours
  suggestedAgent: AgentType;
  suggestedModel: string;
}

interface Contradiction {
  id: string;
  project: string;
  claimA: string;                      // claim ID
  claimB: string;                      // claim ID
  description: string;
  severity: "low" | "medium" | "high";
  suggestedResolution: string;
}

interface Risk {
  id: string;
  project: string;
  type: "reviewer_rejection" | "methodology_flaw" | "missing_baseline"
      | "scope_creep" | "deadline_miss" | "novelty_loss";
  description: string;
  probability: number;                 // 0.0-1.0
  impact: "low" | "medium" | "high" | "critical";
  relatedClaims: string[];
  mitigationStrategy: string;
}

class KnowledgeGraph {
  private claims = new Map<string, Claim>();
  private gaps: Gap[] = [];
  private contradictions: Contradiction[] = [];
  private risks: Risk[] = [];

  constructor(private pool: pg.Pool) {}

  /** Rebuild graph from all data sources for a project */
  async buildForProject(project: string): Promise<void>;

  /** Query claims by status, confidence threshold, etc. */
  queryClaims(filter: Partial<Claim>): Claim[];

  /** Find claims with insufficient evidence */
  findWeakClaims(minEvidence: number): Claim[];

  /** Find pairs of claims that contradict */
  detectContradictions(): Contradiction[];

  /** Identify gaps in the research coverage */
  detectGaps(): Gap[];

  /** Assess risks based on claim state + project phase + deadline */
  assessRisks(): Risk[];

  /** Get a subgraph relevant to a specific gap or risk */
  getSubgraph(claimIds: string[]): { claims: Claim[]; evidence: Evidence[] };
}
```

### 3.2 Session Brief

The `SessionBrief` replaces `SessionConfig` as the input to the session runner. It carries intellectual context, not just project name and agent type.

```typescript
// orchestrator/src/research-planner.ts

interface SessionBrief {
  id: string;                          // UUID
  projectName: string;
  agentType: AgentType;
  objective: string;                   // specific task description
  context: {
    knowledgeSubgraph: Claim[];        // relevant claims and evidence
    files: string[];                   // specific files the agent should read
    relevantDecisions: Decision[];     // past decisions that inform this task
    forumContext?: string;             // relevant forum discussion summary
  };
  constraints: {
    maxTurns: number;
    maxDurationMs: number;
    maxBudgetUsd: number;
    model: string;                     // "claude-opus-4-6", "claude-sonnet-4-6", etc.
    thinkingLevel: "standard" | "extended";
    allowedTools?: string[];           // restrict tool access if needed
  };
  deliverables: Deliverable[];
  priority: number;                    // 0-100, computed by planner
  reasoning: string;                   // why this task was chosen (logged for transparency)
  strategy: PlanningStrategy;          // which heuristic selected this task
}

interface Deliverable {
  description: string;
  type: "commit" | "file" | "status_update" | "claim_update" | "analysis";
  verificationMethod: "file_exists" | "commit_count" | "status_changed"
                    | "claim_confidence_changed" | "manual";
  target?: string;                     // file path, claim ID, etc.
}

type PlanningStrategy =
  | "gap_filling"
  | "contradiction_resolution"
  | "risk_mitigation"
  | "deadline_driven"
  | "opportunity_driven"
  | "cross_project_transfer"
  | "quality_improvement";
```

### 3.3 Database Schema

```sql
-- orchestrator/sql/005_planner_schema.sql

-- Claims: tracked assertions within a project
CREATE TABLE claims (
    id              TEXT PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id),
    statement       TEXT NOT NULL,
    confidence      REAL NOT NULL DEFAULT 0.5
                    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    status          TEXT NOT NULL DEFAULT 'hypothesis'
                    CHECK (status IN ('hypothesis', 'supported', 'contested', 'refuted')),
    source          TEXT NOT NULL DEFAULT 'agent'
                    CHECK (source IN ('framework', 'empirical', 'literature', 'agent')),
    source_agent    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_claims_project    ON claims (project);
CREATE INDEX idx_claims_status     ON claims (status);
CREATE INDEX idx_claims_confidence ON claims (confidence);

-- Evidence links: connect claims to supporting/contradicting data
CREATE TABLE evidence (
    id              SERIAL PRIMARY KEY,
    claim_id        TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    evidence_type   TEXT NOT NULL
                    CHECK (evidence_type IN (
                        'eval_result', 'literature', 'decision',
                        'forum_post', 'analysis'
                    )),
    reference       TEXT NOT NULL,
    supports        BOOLEAN NOT NULL,
    strength        TEXT NOT NULL DEFAULT 'moderate'
                    CHECK (strength IN ('weak', 'moderate', 'strong')),
    summary         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_claim    ON evidence (claim_id);
CREATE INDEX idx_evidence_type     ON evidence (evidence_type);
CREATE INDEX idx_evidence_ref      ON evidence (reference);

-- Session evaluations: structured post-session assessment
CREATE TABLE session_evaluations (
    id              SERIAL PRIMARY KEY,
    session_id      TEXT NOT NULL,
    brief_id        TEXT NOT NULL,
    project         TEXT NOT NULL REFERENCES projects(id),
    agent_type      TEXT NOT NULL,
    strategy        TEXT NOT NULL,
    objective       TEXT NOT NULL,
    deliverables_met INTEGER NOT NULL DEFAULT 0,
    deliverables_total INTEGER NOT NULL DEFAULT 0,
    quality_score   INTEGER NOT NULL DEFAULT 0
                    CHECK (quality_score >= 0 AND quality_score <= 100),
    claims_updated  TEXT[] DEFAULT '{}',
    reasoning       TEXT,
    cost_usd        REAL DEFAULT 0,
    duration_ms     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_session_eval_project  ON session_evaluations (project);
CREATE INDEX idx_session_eval_strategy ON session_evaluations (strategy);
CREATE INDEX idx_session_eval_quality  ON session_evaluations (quality_score);
CREATE INDEX idx_session_eval_created  ON session_evaluations (created_at);

-- Planner state: persistent planner metadata
CREATE TABLE planner_state (
    project         TEXT NOT NULL REFERENCES projects(id),
    key             TEXT NOT NULL,
    value           JSONB NOT NULL,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project, key)
);

CREATE INDEX idx_planner_state_project ON planner_state (project);
```

---

## 4. Core Class: ResearchPlanner

```typescript
// orchestrator/src/research-planner.ts

class ResearchPlanner {
  private kg: KnowledgeGraph;
  private pool: pg.Pool;
  private projectManager: ProjectManager;
  private strategyWeights: Map<PlanningStrategy, number>;

  constructor(pool: pg.Pool, projectManager: ProjectManager) {
    this.pool = pool;
    this.projectManager = projectManager;
    this.kg = new KnowledgeGraph(pool);
    this.strategyWeights = new Map([
      ["risk_mitigation",          1.5],
      ["contradiction_resolution", 1.4],
      ["deadline_driven",          1.3],
      ["gap_filling",              1.0],
      ["quality_improvement",      0.9],
      ["opportunity_driven",       0.8],
      ["cross_project_transfer",   0.6],
    ]);
  }

  /**
   * Main entry point. Called by daemon at the start of each cycle.
   * Returns ranked session briefs ready for execution.
   */
  async planNextActions(maxActions: number): Promise<SessionBrief[]> {
    const projects = await this.projectManager.listProjects();
    const activeProjects = projects.filter(p => p.status === "active");
    const candidates: SessionBrief[] = [];

    for (const project of activeProjects) {
      await this.kg.buildForProject(project.project);

      const gaps = this.kg.detectGaps();
      const contradictions = this.kg.detectContradictions();
      const risks = this.kg.assessRisks();

      // Generate candidate briefs from each strategy
      candidates.push(...await this.gapFillingBriefs(project, gaps));
      candidates.push(...await this.contradictionBriefs(project, contradictions));
      candidates.push(...await this.riskMitigationBriefs(project, risks));
      candidates.push(...await this.deadlineBriefs(project));
      candidates.push(...await this.opportunityBriefs(project));
    }

    // Cross-project analysis (runs across all projects)
    candidates.push(...await this.crossProjectBriefs(activeProjects));

    // Apply strategy weights, deduplicate, rank, and return top N
    return this.rankAndSelect(candidates, maxActions);
  }

  /**
   * Post-session evaluation. Called after each session completes.
   * Checks deliverables, updates claims, records evaluation.
   */
  async evaluateSession(
    brief: SessionBrief,
    result: SessionResult,
  ): Promise<SessionEvaluation> {
    let deliverablesMet = 0;

    for (const d of brief.deliverables) {
      const met = await this.checkDeliverable(d, result, brief.projectName);
      if (met) deliverablesMet++;
    }

    const qualityScore = this.computeEvalQuality(
      deliverablesMet,
      brief.deliverables.length,
      result,
    );

    const evaluation: SessionEvaluation = {
      sessionId: result.sessionId,
      briefId: brief.id,
      project: brief.projectName,
      agentType: brief.agentType,
      strategy: brief.strategy,
      objective: brief.objective,
      deliverablesMet,
      deliverablesTotal: brief.deliverables.length,
      qualityScore,
      claimsUpdated: [],
      reasoning: this.generateEvalReasoning(brief, result, deliverablesMet),
      costUsd: result.costUsd,
      durationMs: result.durationMs,
    };

    await this.persistEvaluation(evaluation);
    await this.updateStrategyWeights(evaluation);

    return evaluation;
  }

  // ── Strategy Implementations ──────────────────────────────

  /**
   * Gap-filling: untested hypothesis -> design experiment or gather evidence.
   */
  private async gapFillingBriefs(
    project: ProjectStatus,
    gaps: Gap[],
  ): Promise<SessionBrief[]>;

  /**
   * Contradiction resolution: conflicting claims -> investigate which is correct.
   */
  private async contradictionBriefs(
    project: ProjectStatus,
    contradictions: Contradiction[],
  ): Promise<SessionBrief[]>;

  /**
   * Risk mitigation: weak evidence for key claim -> strengthen or revise.
   * Prioritizes claims most likely to cause reviewer rejection.
   */
  private async riskMitigationBriefs(
    project: ProjectStatus,
    risks: Risk[],
  ): Promise<SessionBrief[]>;

  /**
   * Deadline-driven: venue deadline approaching -> focus on polish and completeness.
   * Triggers writer/editor agents with specific section targets.
   */
  private async deadlineBriefs(project: ProjectStatus): Promise<SessionBrief[]>;

  /**
   * Opportunity-driven: new literature found, strong unexpected result, etc.
   * Triggers scout or researcher agents to assess implications.
   */
  private async opportunityBriefs(
    project: ProjectStatus,
  ): Promise<SessionBrief[]>;

  /**
   * Cross-project transfer: finding in project A has implications for project B.
   * Compares claim sets across projects to find overlap.
   */
  private async crossProjectBriefs(
    projects: ProjectStatus[],
  ): Promise<SessionBrief[]>;

  // ── Model Selection ───────────────────────────────────────

  /**
   * Select the appropriate model based on task cognitive demands.
   *
   *   Opus   → deep theoretical reasoning, novel framework development,
   *            contradiction resolution, risk assessment
   *   Sonnet → general research, writing, experiment design, analysis
   *   Haiku  → literature sweeps, data formatting, routine checks
   */
  private selectModel(
    strategy: PlanningStrategy,
    agentType: AgentType,
    severity: string,
  ): { model: string; thinkingLevel: "standard" | "extended" } {
    // Critical theory work -> Opus + extended thinking
    if (
      (strategy === "contradiction_resolution" && severity === "high") ||
      (strategy === "risk_mitigation" && severity === "critical") ||
      agentType === "theorist"
    ) {
      return { model: "claude-opus-4-6", thinkingLevel: "extended" };
    }

    // Routine scanning -> Haiku
    if (
      agentType === "scout" ||
      strategy === "opportunity_driven"
    ) {
      return { model: "claude-haiku-4-5", thinkingLevel: "standard" };
    }

    // Default -> Sonnet
    return { model: "claude-sonnet-4-6", thinkingLevel: "standard" };
  }

  // ── Ranking ───────────────────────────────────────────────

  private rankAndSelect(
    candidates: SessionBrief[],
    maxActions: number,
  ): SessionBrief[] {
    // Apply strategy weights to priority scores
    for (const brief of candidates) {
      const weight = this.strategyWeights.get(brief.strategy) ?? 1.0;
      brief.priority = Math.round(brief.priority * weight);
    }

    // Deduplicate: one brief per project (take highest priority)
    const byProject = new Map<string, SessionBrief>();
    candidates.sort((a, b) => b.priority - a.priority);
    for (const brief of candidates) {
      if (!byProject.has(brief.projectName)) {
        byProject.set(brief.projectName, brief);
      }
    }

    return Array.from(byProject.values())
      .sort((a, b) => b.priority - a.priority)
      .slice(0, maxActions);
  }
}
```

---

## 5. Integration Points

### 5.1 Daemon Integration

The planner replaces `scoreProjects()` and `PHASE_TO_AGENT` inside the daemon's `cycle()` method.

**Before** (daemon.ts lines 442-478):
```typescript
const projects = await this.projectManager.listProjects();
const scored = await this.scoreProjects(projects);
const candidates = scored
  .filter(s => !this.activeSessions.has(s.project.project))
  .filter(s => s.score > 0)
  .slice(0, availableSlots);

for (const candidate of candidates) {
  const { project, agentType } = candidate;
  // launch generic session
}
```

**After**:
```typescript
const briefs = await this.planner.planNextActions(availableSlots);
const candidates = briefs
  .filter(b => !this.activeSessions.has(b.projectName));

for (const brief of candidates) {
  // launch session with full intellectual context
  await this.runSessionFromBrief(brief);
}
```

The follow-up queue and external dispatch queue remain unchanged. The planner handles the organic scheduling; chained sessions and external dispatches bypass it.

### 5.2 Session Runner Integration

The session runner's `buildPrompt()` method (session-runner.ts lines 147-195) currently assembles a generic prompt from:
1. Global CLAUDE.md
2. Agent role definition
3. Project CLAUDE.md
4. status.yaml
5. Generic workflow instructions

With the planner, a new section is injected:

```typescript
// Added to buildPrompt when a SessionBrief is provided
private buildBriefSection(brief: SessionBrief): string {
  const sections: string[] = [];

  sections.push("# Session Objective\n");
  sections.push(brief.objective + "\n");

  sections.push("## Why This Task Was Selected\n");
  sections.push(brief.reasoning + "\n");

  if (brief.context.knowledgeSubgraph.length > 0) {
    sections.push("## Relevant Claims\n");
    for (const claim of brief.context.knowledgeSubgraph) {
      const status = claim.status.toUpperCase();
      const conf = (claim.confidence * 100).toFixed(0);
      sections.push(
        `- [${status}] (${conf}% confidence) ${claim.statement}`
      );
      for (const ev of claim.evidence) {
        const dir = ev.supports ? "supports" : "contradicts";
        sections.push(`  - ${ev.strength} ${dir}: ${ev.summary}`);
      }
    }
    sections.push("");
  }

  if (brief.context.files.length > 0) {
    sections.push("## Files to Read First\n");
    for (const f of brief.context.files) {
      sections.push(`- ${f}`);
    }
    sections.push("");
  }

  sections.push("## Deliverables\n");
  for (const d of brief.deliverables) {
    sections.push(`- [ ] ${d.description}`);
  }
  sections.push("");

  sections.push("## Constraints\n");
  sections.push(`- Max turns: ${brief.constraints.maxTurns}`);
  sections.push(`- Budget: $${brief.constraints.maxBudgetUsd.toFixed(2)}`);
  sections.push(`- Thinking: ${brief.constraints.thinkingLevel}`);

  return sections.join("\n");
}
```

### 5.3 OpenClaw Integration

Sol's morning standup (currently a ritual scheduled via the rituals table) becomes a real planning session. Instead of Sol generating a standup post from generic status data, Sol queries the planner:

```typescript
// In Sol's heartbeat handler
const briefs = await planner.planNextActions(5);
const standupPost = formatStandupFromBriefs(briefs, collectiveContext);
await postToForum(standupPost);
```

Other agents can request planner consultation via the API:

```
GET /api/planner/brief/:project
  → Returns current highest-priority brief for that project

GET /api/planner/gaps/:project
  → Returns identified gaps and their severity

GET /api/planner/risks/:project
  → Returns risk assessment for the project

POST /api/planner/suggest
  { project, context }
  → Returns a suggested next action based on the provided context
```

### 5.4 Claim Lifecycle

Claims flow through the system as follows:

1. **Creation**: Agent sessions create claims when they assert something about the research (e.g., "CoT lift is negligible for architectural mismatch tasks"). Claims start as `hypothesis` with default 0.5 confidence.

2. **Evidence accumulation**: As eval results come in, literature is reviewed, or forum discussions occur, evidence links are added. Each evidence link either supports or contradicts the claim.

3. **Status transitions**:
   - `hypothesis` -> `supported`: 2+ strong supporting evidence, no contradicting evidence
   - `hypothesis` -> `contested`: supporting AND contradicting evidence exists
   - `supported` -> `contested`: new contradicting evidence arrives
   - `contested` -> `supported` or `refuted`: resolution session determines outcome

4. **Confidence updates**: After each session, the planner recalculates claim confidence based on the evidence portfolio. Bayesian update: prior = current confidence, likelihood = evidence strength and direction.

---

## 6. Planning Strategies — Detailed Heuristics

### 6.1 Gap-Filling

**Trigger**: A claim exists with `status: hypothesis` and fewer than 2 evidence links.

**Action**: Design an experiment, literature search, or analysis to test the hypothesis.

**Agent selection**:
- Empirical gap -> `experimenter` (design and run eval)
- Literature gap -> `scout` (search for related work)
- Theoretical gap -> `theorist` (develop formal argument)

**Priority formula**: `base_priority * (1 + gap.severity_weight) * claim.importance_weight`

Where `claim.importance_weight` is higher for claims that appear in the paper's core contribution section.

**Example brief**:
> **Objective**: Test whether the negative CoT lift for B2 budget_cot persists when controlling for difficulty level. The current evidence shows -0.254 aggregate lift, but this may be driven by easy instances where budget allocation overhead hurts performance.
>
> **Deliverables**:
> - Run B2 budget_cot at difficulty levels 3, 5, 7 separately for claude-sonnet-4-6
> - Produce accuracy-by-difficulty breakdown
> - Update claim rg-claim-007 confidence based on results

### 6.2 Contradiction Resolution

**Trigger**: Two claims in the same project have conflicting evidence, or an agent posts a forum signal challenging an existing claim.

**Action**: Investigate which claim is correct. This may require re-running experiments, closer examination of methodology, or theoretical analysis.

**Agent selection**: Usually `theorist` or `experimenter`, depending on whether the contradiction is theoretical or empirical.

**Priority**: High. Contradictions left unresolved become reviewer ammunition.

**Example brief**:
> **Objective**: Resolve contradiction between claim rg-claim-003 ("CoT provides consistent benefit for serial-dependency tasks") and the B2 budget_cot result showing -0.254 lift on a serial-dependency task. Determine whether budget_cot is a special case or whether the serial-dependency claim needs qualification.

### 6.3 Risk Mitigation

**Trigger**: A key claim (one referenced in the paper's contributions section) has confidence below 0.6, or a reviewer-facing weakness is identified.

**Risk types**:
- `reviewer_rejection`: A central claim is weakly evidenced
- `methodology_flaw`: The experimental design has a known limitation
- `missing_baseline`: A comparison that reviewers will expect is absent
- `novelty_loss`: A new publication makes part of the contribution less novel

**Priority**: Highest. Risk mitigation briefs get a 1.5x strategy weight.

**Example brief**:
> **Objective**: Strengthen evidence for claim rg-claim-001 ("The 6-type reasoning taxonomy is necessary and sufficient"). Currently supported by framework analysis only. Add empirical evidence by showing that collapsing adjacent types degrades predictive power of the CoT lift model.

### 6.4 Deadline-Driven

**Trigger**: Venue deadline within 4 weeks and the paper is not in `paper-finalization` phase.

**Action**: Focus on completeness and polish. Identify missing sections, incomplete figures, citation gaps.

**Agent selection**: `writer` for sections, `editor` for polish, `critic` for review.

**Priority**: Escalates as deadline approaches. At 2 weeks: 1.3x. At 1 week: 1.8x. At 3 days: 2.5x.

### 6.5 Opportunity-Driven

**Trigger**: Scout finds a new relevant publication, eval results show an unexpected pattern, or a forum post identifies a new angle.

**Action**: Assess whether the opportunity changes the research direction, strengthens the contribution, or requires a response.

**Agent selection**: `scout` for literature assessment, `researcher` for deeper investigation.

**Priority**: Lower baseline, but can be boosted if the opportunity is time-sensitive (e.g., concurrent submission window).

### 6.6 Cross-Project Transfer

**Trigger**: A claim or finding in project A overlaps with the research questions of project B. Detected by comparing claim statements across projects using semantic similarity (initially keyword-based, later embedding-based).

**Action**: Investigate whether the finding transfers, and if so, how to incorporate it.

**Example**: If reasoning-gaps discovers that model X fails on architectural-mismatch tasks, and agent-failure-taxonomy is studying failure modes, the planner creates a brief to check whether that failure mode fits the taxonomy.

---

## 7. Post-Session Evaluation

After each session, the planner evaluates outcomes:

```typescript
interface SessionEvaluation {
  sessionId: string;
  briefId: string;
  project: string;
  agentType: string;
  strategy: PlanningStrategy;
  objective: string;
  deliverablesMet: number;
  deliverablesTotal: number;
  qualityScore: number;           // 0-100
  claimsUpdated: string[];        // claim IDs whose confidence changed
  reasoning: string;              // why the score was assigned
  costUsd: number;
  durationMs: number;
}
```

**Quality scoring** (replaces daemon's `assessQuality`):

| Factor | Points | Method |
|--------|--------|--------|
| Deliverables met | 0-40 | `(deliverablesMet / deliverablesTotal) * 40` |
| Claims advanced | 0-20 | Points per claim that changed status or gained evidence |
| Session completed | 0-15 | 15 if completed, 5 if timeout, 0 if failed |
| Cost efficiency | 0-15 | Lower cost per deliverable = more points |
| Commits created | 0-10 | `min(commits * 3, 10)` |

**Strategy weight adaptation**: After each evaluation, the planner adjusts strategy weights. If risk_mitigation sessions consistently score well, the weight increases. If opportunity_driven sessions score poorly, the weight decreases. Adaptation is slow (exponential moving average with alpha=0.1) to prevent oscillation.

---

## 8. Task Breakdown

### Sprint 10: Types and Knowledge Graph Foundation

| Task | Description | Est. |
|------|-------------|------|
| 10.1 | Define all TypeScript interfaces: `Claim`, `Evidence`, `Gap`, `Contradiction`, `Risk`, `SessionBrief`, `Deliverable`, `SessionEvaluation` | 1h |
| 10.2 | Create `005_planner_schema.sql` with claims, evidence, session_evaluations, planner_state tables | 1h |
| 10.3 | Implement `KnowledgeGraph` class: `buildForProject()` loading from status.yaml, decisions, eval_results | 2h |
| 10.4 | Implement `KnowledgeGraph.detectGaps()` and `detectContradictions()` | 2h |
| | **Sprint 10 total** | **6h** |

### Sprint 11: Core Planner Logic

| Task | Description | Est. |
|------|-------------|------|
| 11.1 | Implement `ResearchPlanner` class skeleton with `planNextActions()` | 1h |
| 11.2 | Implement gap-filling strategy: generate briefs from gaps | 1.5h |
| 11.3 | Implement contradiction resolution strategy | 1h |
| 11.4 | Implement risk mitigation strategy with `assessRisks()` | 1.5h |
| 11.5 | Implement deadline-driven strategy with escalating priority | 1h |
| 11.6 | Implement model selection logic (`selectModel()`) | 0.5h |
| 11.7 | Implement ranking and deduplication (`rankAndSelect()`) | 1h |
| | **Sprint 11 total** | **7.5h** |

### Sprint 12: Daemon and Session Runner Integration

| Task | Description | Est. |
|------|-------------|------|
| 12.1 | Replace `scoreProjects()` in daemon.ts with `planner.planNextActions()` | 1.5h |
| 12.2 | Add `runSessionFromBrief()` to daemon that passes full brief to session-manager | 1h |
| 12.3 | Update `SessionRunner.buildPrompt()` to inject brief section when available | 1.5h |
| 12.4 | Update `SessionManager.startProject()` to accept `SessionBrief` | 1h |
| 12.5 | Preserve backward compatibility: `scoreProjects()` remains as fallback if planner has no candidates | 0.5h |
| | **Sprint 12 total** | **5.5h** |

### Sprint 13: Post-Session Evaluation and Learning

| Task | Description | Est. |
|------|-------------|------|
| 13.1 | Implement `evaluateSession()` with deliverable checking | 2h |
| 13.2 | Implement claim confidence updates (Bayesian update from session results) | 1.5h |
| 13.3 | Implement strategy weight adaptation | 1h |
| 13.4 | Replace daemon's `assessQuality()` with planner's evaluation | 0.5h |
| 13.5 | Persist evaluations to `session_evaluations` table | 0.5h |
| | **Sprint 13 total** | **5.5h** |

### Sprint 14: API, OpenClaw, and Cross-Project

| Task | Description | Est. |
|------|-------------|------|
| 14.1 | Add `/api/planner/*` routes (brief, gaps, risks, suggest) | 1.5h |
| 14.2 | Wire Sol's standup to use planner briefs | 1h |
| 14.3 | Extend collective-context with planner insights | 1h |
| 14.4 | Implement cross-project transfer detection | 1.5h |
| 14.5 | Implement opportunity-driven strategy (forum signals, unexpected results) | 1h |
| | **Sprint 14 total** | **6h** |

**Grand total**: ~30.5 hours across 5 sprints

---

## 9. Migration Strategy

The planner is additive. At no point does the existing system break.

1. **Sprint 10-11**: The planner and knowledge graph are standalone modules. No daemon changes. Can be tested independently by calling `planNextActions()` and inspecting output.

2. **Sprint 12**: The daemon gains a `usePlanner` flag (default: false). When false, the existing `scoreProjects()` path runs. When true, the planner runs. Controlled by environment variable `USE_RESEARCH_PLANNER=1`.

3. **Sprint 13**: Evaluation runs in parallel with the existing `assessQuality()`. Both scores are logged. The planner's evaluation populates a separate table.

4. **Sprint 14**: Once planner quality is validated, the feature flag can be turned on permanently and `scoreProjects()` removed in a cleanup commit.

---

## 10. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| **Specificity** | Session briefs contain specific objectives (not "run a writer") | 100% of planner-generated briefs |
| **Deliverable completion** | Percentage of deliverables met per session | > 60% within 4 weeks of launch |
| **Quality improvement** | Average quality score vs. pre-planner baseline | > 15% improvement |
| **Gap identification** | Planner identifies gaps that human review confirms | > 80% precision |
| **Intellectual awareness** | Briefs reference specific claims and evidence | 100% of briefs include knowledge context |
| **Model selection ROI** | Opus sessions produce higher-quality theoretical work | Opus sessions score > 20% above Sonnet for theory tasks |
| **Cross-project transfer** | At least one cross-project insight surfaced per month | >= 1 per month with 2+ active projects |
| **Autonomous operation** | No human intervention required for task selection | 0 manual dispatches for tasks planner should have caught |

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Knowledge graph is too sparse in early stages | Planner generates low-quality briefs | Fall back to `scoreProjects()` when claim count < threshold; bootstrap claims from existing status.yaml and eval data |
| Claim confidence updates diverge from reality | Planner pursues wrong priorities | Manual claim review by strategist agent monthly; cap confidence delta per update at 0.2 |
| Model selection overuses Opus, blowing budget | Monthly budget exceeded | Hard budget cap per model tier; daily Opus limit of $10 |
| Session briefs are too long for context window | Agent ignores or misreads the brief | Cap knowledge subgraph at 10 claims; summarize evidence; keep brief section < 2000 tokens |
| Planner adds latency to daemon cycle | Cycle takes too long, sessions start late | Cache knowledge graph between cycles; only rebuild for projects with new data (check `updated_at`) |
| Cross-project detection produces false positives | Wasted sessions investigating non-connections | Start with keyword matching, add embedding similarity later; require 2+ keyword overlap |

---

## 12. Future Extensions (Post-Sprint 14)

- **Embedding-based claim similarity**: Use Claude embeddings to detect semantic overlap between claims across projects, replacing keyword matching.
- **Reviewer simulation**: Before submission, run a simulated review where the critic agent uses the risk assessment to write a mock review. Use the mock review to generate final revision briefs.
- **Multi-session planning**: Plan sequences of 2-3 sessions as a unit (e.g., "experimenter runs eval, then theorist analyzes results, then writer updates paper section").
- **Claim provenance graph**: Visualize which claims depend on which evidence, showing the full chain from raw data to paper assertions. Surface in the Astro dashboard.
- **Active learning for claims**: When multiple claims compete for evidence, prioritize the one where new evidence would most reduce uncertainty (information gain maximization).
