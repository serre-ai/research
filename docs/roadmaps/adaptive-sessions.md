# Adaptive Session Composition: Task-Specific Agent Configuration

**Status:** Proposed
**Author:** Oddur Sigurdsson
**Date:** 2026-03-16
**Estimated effort:** 13-17 hours

---

## Problem

Every session currently gets the same treatment. The `SessionManager.startProject()` method accepts an `agentType` and optional `maxTurns` / `maxDurationMs`, but the defaults are always the same:

- Model: Sonnet (hardcoded in `session-runner.ts` `calculateCost` default, and no model selection passed to `query()`)
- Thinking: not configured (standard by default)
- Max turns: 50
- Max duration: 45 minutes
- Tools: all 8 tools enabled for every session
- Context: full stack (global CLAUDE.md + agent definition + project CLAUDE.md + status.yaml + workflow instructions)

This is wasteful. A quick LaTeX typo fix burns 50 turns of Sonnet context on the full project state. A deep theoretical proof gets the same 50-turn budget as a formatting pass. Literature sweeps use expensive models when Haiku would suffice.

The `SessionRunner.buildPrompt()` method always composes the same 5 sections in the same order with no selectivity. The prompt never includes knowledge graph context, verification reports, literature alerts, or forum discussions -- because those systems do not exist yet, but when they do, injecting them indiscriminately would waste tokens.

---

## Design

### Session Profiles

Each intellectual task type maps to a profile that configures model, thinking level, turn budget, tool access, and context strategy.

| Profile | Model | Thinking | Max Turns | Duration | Tools | Context |
|---------|-------|----------|-----------|----------|-------|---------|
| `deep_proof` | Opus 4.6 | extended | 100 | 90 min | Read, Write, Edit | Narrow: proof file + prerequisites |
| `literature_sweep` | Haiku 4.5 (escalate to Sonnet) | standard | 30 | 20 min | WebSearch, WebFetch, Read | Broad: project state + search queries |
| `data_analysis` | Sonnet 4.6 | standard | 40 | 30 min | Bash (Python), Read, Write | Medium: data files + current claims |
| `latex_debug` | Haiku 4.5 | standard | 10 | 5 min | Read, Edit, Bash | Narrow: build log + erroring file |
| `strategic_planning` | Opus 4.6 | extended | 20 | 30 min | Read, WebSearch | Broad: all projects, budget, timeline |
| `paper_writing` | Opus 4.6 | extended | 80 | 60 min | Read, Write, Edit | Medium: section context + knowledge subgraph |
| `paper_editing` | Sonnet 4.6 | standard | 30 | 20 min | Read, Edit | Narrow: section being edited |
| `experiment_design` | Sonnet 4.6 | extended | 40 | 30 min | Read, Write, Bash | Medium: hypothesis + existing benchmarks |
| `review_response` | Opus 4.6 | extended | 60 | 45 min | Read, Write, Edit | Full: paper + reviews + knowledge graph |
| `quick_fix` | Haiku 4.5 | standard | 5 | 3 min | Read, Edit | Narrow: specific file only |
| `default` | Sonnet 4.6 | standard | 50 | 45 min | All | Full (current behavior) |

---

### SessionBrief: The Planner's Output

The planner does not just pick an agent type -- it composes a full session brief that tells the `SessionRunner` exactly how to configure the session.

```typescript
interface SessionBrief {
  // Identity
  projectName: string;
  agentType: AgentType;
  profile: SessionProfile;      // one of the profiles above
  taskDescription: string;      // what the agent should accomplish

  // Model configuration
  model: "opus-4.6" | "sonnet-4.6" | "haiku-4.5";
  thinkingLevel: "standard" | "extended";
  maxTurns: number;
  maxDurationMs: number;

  // Tool access
  allowedTools: string[];       // subset of available tools

  // Context composition
  context: ContextComposition;

  // Escalation policy
  escalation?: {
    escalateTo: "sonnet-4.6" | "opus-4.6";
    triggerAfterTurns: number;  // escalate if still running after N turns
    triggerOnQuality: number;   // escalate if quality signal drops below threshold
  };

  // Metadata
  chainId?: string;
  chainDepth?: number;
  priority: "low" | "normal" | "high" | "critical";
}
```

### Context Composition

The context window is the most expensive resource. Different tasks need different slices of the project's information.

```typescript
interface ContextComposition {
  // Always included (unless explicitly disabled)
  globalInstructions: boolean;     // CLAUDE.md
  agentDefinition: boolean;        // .claude/agents/{type}.md
  projectInstructions: boolean;    // projects/{name}/CLAUDE.md
  statusYaml: boolean;             // projects/{name}/status.yaml

  // Selectively included based on task
  knowledgeSubgraph?: {
    claimTypes: string[];          // e.g. ["theoretical", "empirical"]
    maxClaims: number;             // context budget for claims
    relevanceThreshold: number;    // 0.0-1.0, minimum similarity to task
  };
  specificFiles?: string[];        // exact files to include in context
  recentDecisions?: number;        // last N decisions from status.yaml
  recentSessions?: number;         // last N session summaries
  verificationReport?: boolean;    // include current claim verification status
  literatureAlerts?: number;       // last N unprocessed literature alerts
  forumContext?: boolean;          // include recent forum discussions

  // Exclusions
  excludePatterns?: string[];      // glob patterns to exclude from context
}
```

#### Context Examples by Profile

**`deep_proof` (narrow context)**
```typescript
{
  globalInstructions: true,
  agentDefinition: true,
  projectInstructions: true,
  statusYaml: true,
  specificFiles: ["paper/sections/theory.tex", "paper/sections/proofs.tex"],
  knowledgeSubgraph: { claimTypes: ["theoretical"], maxClaims: 20, relevanceThreshold: 0.7 },
  recentDecisions: 3,
}
```

**`literature_sweep` (broad context)**
```typescript
{
  globalInstructions: true,
  agentDefinition: true,
  projectInstructions: true,
  statusYaml: true,
  knowledgeSubgraph: { claimTypes: ["theoretical", "empirical", "methodological"], maxClaims: 50, relevanceThreshold: 0.3 },
  literatureAlerts: 20,
  recentSessions: 5,
}
```

**`latex_debug` (minimal context)**
```typescript
{
  globalInstructions: false,       // not needed for a build fix
  agentDefinition: false,
  projectInstructions: false,
  statusYaml: false,
  specificFiles: ["paper/build.log", "paper/main.tex"],  // dynamically set to erroring files
}
```

**`quick_fix` (surgical context)**
```typescript
{
  globalInstructions: false,
  agentDefinition: false,
  projectInstructions: false,
  statusYaml: false,
  specificFiles: ["path/to/file-with-issue.tex"],   // set by planner
}
```

---

### Model Selection Logic

The planner uses these heuristics to choose the model:

**Opus 4.6** -- tasks where depth of reasoning is critical and mistakes are costly:
- Theoretical proofs and formal arguments
- Strategic planning across the portfolio
- Writing new paper sections from scratch
- Responding to peer reviews
- Any task where the planner estimates high intellectual difficulty

**Sonnet 4.6** -- the default for general-purpose work:
- Experiment design and data analysis
- Editing and polishing existing text
- Code implementation
- Most routine research tasks

**Haiku 4.5** -- speed and cost efficiency:
- Literature searches (high-volume, low-depth queries)
- LaTeX build debugging
- Quick formatting fixes
- Simple file operations
- Any task the planner estimates is low-difficulty

**Escalation**: Some profiles start cheap and upgrade if the task proves harder than expected:
- `literature_sweep` starts with Haiku. If it uses more than 20 turns without completing, the next session escalates to Sonnet.
- Escalation is detected by comparing turn count to the profile's `escalation.triggerAfterTurns` threshold.
- Escalation metadata is passed to the next session via the event bus (`planner.brief_ready` event).

---

### Cost Optimization Loop

The platform tracks cost-effectiveness per profile over time:

```typescript
interface ProfileStats {
  profile: SessionProfile;
  sessionsRun: number;
  avgQualityScore: number;       // 0-100, from Daemon.assessQuality
  avgCostUsd: number;
  avgDurationMs: number;
  qualityPerDollar: number;      // avgQualityScore / avgCostUsd
  escalationRate: number;        // fraction of sessions that triggered escalation
  lastUpdated: string;
}
```

The planner consults profile stats when composing a brief:
- If `literature_sweep` with Haiku consistently produces quality < 30, the planner auto-upgrades the default model for that profile to Sonnet.
- If `paper_editing` with Sonnet consistently scores > 80 at low cost, the profile stays as-is.
- When daily budget remaining is low (`budget.threshold` event with level "warning"), the planner shifts to cheaper profiles: Opus tasks get downgraded to Sonnet, Sonnet tasks get downgraded to Haiku, unless the task is flagged as `priority: "critical"`.
- Stats are stored in the `sessions` PostgreSQL table (new columns: `profile`, `quality_score`) and queried by the planner.

---

## Implementation

### Changes to `orchestrator/src/session-runner.ts`

The `SessionRunner.run()` method currently accepts a `SessionConfig` with limited fields. It needs to accept the full `SessionBrief`:

```typescript
// Current
export interface SessionConfig {
  projectName: string;
  agentType: AgentType;
  maxTurns: number;
  maxDurationMs: number;
  thinkingLevel?: "standard" | "extended";
  worktreePath?: string;
}

// Proposed
export interface SessionConfig {
  projectName: string;
  agentType: AgentType;
  maxTurns: number;
  maxDurationMs: number;
  thinkingLevel?: "standard" | "extended";
  worktreePath?: string;

  // New fields from SessionBrief
  model?: string;                    // which Claude model to use
  allowedTools?: string[];           // restrict tool access
  context?: ContextComposition;      // what to include in prompt
  taskDescription?: string;          // specific task instructions
  profile?: string;                  // profile name for stats tracking
}
```

The `buildPrompt()` method becomes context-aware:

```typescript
private async buildPrompt(config: SessionConfig): Promise<string> {
  const sections: string[] = [];
  const ctx = config.context ?? DEFAULT_FULL_CONTEXT;

  if (ctx.globalInstructions) {
    const globalClaude = await this.readOptional(join(this.rootDir, "CLAUDE.md"));
    if (globalClaude) sections.push("# Global Platform Instructions\n\n" + globalClaude);
  }

  if (ctx.agentDefinition) {
    const agentDef = await this.readOptional(
      join(this.rootDir, ".claude", "agents", `${config.agentType}.md`)
    );
    if (agentDef) sections.push("# Agent Role Definition\n\n" + agentDef);
  }

  if (ctx.projectInstructions) {
    const projectClaude = await this.readOptional(
      join(this.rootDir, "projects", config.projectName, "CLAUDE.md")
    );
    if (projectClaude) sections.push("# Project-Specific Instructions\n\n" + projectClaude);
  }

  if (ctx.statusYaml) {
    const statusYaml = await this.readOptional(
      join(this.rootDir, "projects", config.projectName, "status.yaml")
    );
    if (statusYaml) sections.push("# Current Project Status\n\n```yaml\n" + statusYaml + "\n```");
  }

  // Inject specific files
  if (ctx.specificFiles) {
    for (const filePath of ctx.specificFiles) {
      const content = await this.readOptional(join(this.rootDir, filePath));
      if (content) sections.push(`# File: ${filePath}\n\n\`\`\`\n${content}\n\`\`\``);
    }
  }

  // Inject knowledge subgraph (future: query from knowledge graph DB)
  if (ctx.knowledgeSubgraph) {
    // Placeholder: will query knowledge graph when it exists
    sections.push("# Relevant Claims\n\n(Knowledge graph not yet available)");
  }

  // Inject recent decisions
  if (ctx.recentDecisions) {
    // Extract last N decisions from status.yaml decisions_made
    sections.push("# Recent Decisions\n\n(Extracted from status.yaml)");
  }

  // Task-specific instructions
  if (config.taskDescription) {
    sections.push("# Your Task\n\n" + config.taskDescription);
  }

  // Standard workflow suffix
  sections.push(this.buildWorkflowSuffix(config));

  return sections.join("\n\n---\n\n");
}
```

### Changes to `orchestrator/src/session-manager.ts`

`SessionManager.startProject()` accepts the full brief and passes it through:

```typescript
async startProject(
  projectName: string,
  agentType: AgentType = "researcher",
  options?: {
    maxTurns?: number;
    maxDurationMs?: number;
    model?: string;
    allowedTools?: string[];
    context?: ContextComposition;
    taskDescription?: string;
    profile?: string;
  },
): Promise<Session> {
  // ... existing worktree setup ...

  const result = await this.sessionRunner.run({
    projectName,
    agentType,
    maxTurns: options?.maxTurns ?? 50,
    maxDurationMs: options?.maxDurationMs ?? 45 * 60 * 1000,
    worktreePath,
    model: options?.model,
    allowedTools: options?.allowedTools,
    context: options?.context,
    taskDescription: options?.taskDescription,
    profile: options?.profile,
  });

  // ... rest unchanged ...
}
```

### Changes to `orchestrator/src/daemon.ts`

The `PHASE_TO_AGENT` mapping becomes richer. Instead of mapping phase -> agent type, it maps to a full profile:

```typescript
// Current: simple agent type mapping
const PHASE_TO_AGENT: Record<string, AgentType> = {
  "research": "researcher",
  "drafting": "writer",
  // ...
};

// Proposed: profile-aware mapping (used as fallback when planner is not available)
const PHASE_TO_PROFILE: Record<string, { agentType: AgentType; profile: string }> = {
  "research": { agentType: "researcher", profile: "default" },
  "literature-review": { agentType: "researcher", profile: "literature_sweep" },
  "empirical-evaluation": { agentType: "experimenter", profile: "experiment_design" },
  "analysis": { agentType: "experimenter", profile: "data_analysis" },
  "drafting": { agentType: "writer", profile: "paper_writing" },
  "revision": { agentType: "writer", profile: "paper_editing" },
  "paper-finalization": { agentType: "writer", profile: "paper_editing" },
  "final": { agentType: "editor", profile: "paper_editing" },
  "active": { agentType: "engineer", profile: "default" },
};
```

The `runSession()` method in the daemon looks up the profile and passes the full configuration to `SessionManager`:

```typescript
private async runSession(
  projectName: string,
  agentType: AgentType,
  chainId?: string,
  chainDepth: number = 0,
  profileOverride?: string
): Promise<void> {
  const profile = profileOverride
    ? PROFILES[profileOverride]
    : PROFILES[PHASE_TO_PROFILE[this.lastKnownPhases.get(projectName) ?? "research"]?.profile ?? "default"];

  const session = await this.sessionManager.startProject(projectName, agentType, {
    maxTurns: profile.maxTurns,
    maxDurationMs: profile.maxDurationMs,
    model: profile.model,
    allowedTools: profile.allowedTools,
    context: profile.context,
    profile: profile.name,
  });

  // ... existing quality assessment and chaining logic ...
}
```

### New: Profile Stats Tracking

Add columns to the `sessions` PostgreSQL table:

```sql
-- 003_session_profiles.sql
ALTER TABLE sessions ADD COLUMN profile TEXT;
ALTER TABLE sessions ADD COLUMN quality_score REAL;
ALTER TABLE sessions ADD COLUMN thinking_level TEXT DEFAULT 'standard';

CREATE INDEX idx_sessions_profile ON sessions (profile);

-- View for profile effectiveness
CREATE VIEW v_profile_stats AS
SELECT
    profile,
    model,
    COUNT(*) AS sessions_run,
    ROUND(AVG(quality_score)::numeric, 1) AS avg_quality,
    ROUND(AVG(cost_usd)::numeric, 4) AS avg_cost,
    ROUND(AVG(duration_s)::numeric, 0) AS avg_duration_s,
    ROUND((AVG(quality_score) / NULLIF(AVG(cost_usd), 0))::numeric, 1) AS quality_per_dollar
FROM sessions
WHERE profile IS NOT NULL AND quality_score IS NOT NULL
GROUP BY profile, model
ORDER BY quality_per_dollar DESC;
```

---

## Escalation Mechanism

Escalation handles the case where a cheap model is insufficient for the task.

### Detection

Two signals trigger escalation:

1. **Turn exhaustion**: Session hits `maxTurns` without the agent indicating completion. Detected from `SessionResult.status === "timeout"` with error `"Session exceeded maximum turns"`.

2. **Low quality**: The `assessQuality()` method in the daemon scores the session below the escalation threshold (e.g., < 25). This covers cases where the agent "completed" but produced nothing useful.

### Response

When escalation is triggered:

1. The daemon emits a `session.completed` event with `quality < escalation.triggerOnQuality`.
2. The `plan_next` event handler checks the session's profile for an escalation policy.
3. If an escalation policy exists, the handler creates a new `SessionBrief` with:
   - The escalation model (e.g., Haiku -> Sonnet)
   - The same task description
   - A note in the context: "Previous attempt with {model} was insufficient. This is an escalation."
4. The handler emits a `planner.brief_ready` event, which triggers a new session launch.

### Guardrails

- Escalation can only happen once per task (no Haiku -> Sonnet -> Opus chains unless explicitly configured).
- Escalation respects budget constraints. If daily budget is low, escalation is suppressed.
- Escalation metadata is logged so profile stats can track escalation rates.

---

## Task Breakdown

| # | Task | Estimate | Dependencies |
|---|------|----------|--------------|
| 1 | Define `SessionProfile`, `SessionBrief`, `ContextComposition` TypeScript interfaces | 1 hour | None |
| 2 | Update `SessionRunner.run()` to accept model, allowedTools, context params | 1 hour | #1 |
| 3 | Rewrite `SessionRunner.buildPrompt()` to use `ContextComposition` for selective inclusion | 2-3 hours | #1, #2 |
| 4 | Update `SessionManager.startProject()` to pass through full brief options | 1 hour | #2 |
| 5 | Create profile registry (static config defining all profiles and their defaults) | 1 hour | #1 |
| 6 | Update `Daemon` to use `PHASE_TO_PROFILE` mapping and pass profiles to sessions | 2 hours | #4, #5 |
| 7 | Implement escalation detection in `assessQuality` and event handler | 2-3 hours | #5, #6, event-bus |
| 8 | SQL migration: add profile/quality columns to sessions table, create `v_profile_stats` view | 1 hour | None |
| 9 | Cost-effectiveness tracking: record profile stats, planner queries them | 2 hours | #6, #8 |
| 10 | API endpoint: `GET /api/profiles/stats` | 1 hour | #8 |
| **Total** | | **13-17 hours** | |

---

## Files Changed

| File | Change |
|------|--------|
| `orchestrator/src/session-runner.ts` | Extend `SessionConfig`, rewrite `buildPrompt()` for context composition, add model selection |
| `orchestrator/src/session-manager.ts` | Pass through full brief options to `SessionRunner` |
| `orchestrator/src/daemon.ts` | Replace `PHASE_TO_AGENT` with `PHASE_TO_PROFILE`, pass profiles in `runSession()` |
| `orchestrator/src/types/profiles.ts` | New: `SessionProfile`, `SessionBrief`, `ContextComposition` interfaces |
| `orchestrator/src/profiles.ts` | New: static profile registry with all profile definitions |
| `orchestrator/sql/003_session_profiles.sql` | New: migration for profile columns and stats view |
| `orchestrator/src/api.ts` | Add `/api/profiles/stats` endpoint |
| `orchestrator/src/routes/` | New route file for profiles API |

---

## Interaction with Event Architecture

This roadmap is designed to work with the event-driven architecture (see `docs/roadmaps/event-architecture.md`). The key integration points:

1. **Session completion events carry profile metadata**: When `session.completed` fires, the payload includes the profile name, model used, and quality score. This feeds the profile stats tracking.

2. **Escalation is event-driven**: The `plan_next` handler on `session.completed` checks for escalation conditions and emits `planner.brief_ready` with an upgraded profile.

3. **Budget events adjust profile selection**: When `budget.threshold` fires with level "warning" or "critical", the planner shifts to cheaper profiles for non-critical tasks.

4. **Profile stats inform future planning**: The planner queries `v_profile_stats` before composing a brief. If a profile's quality-per-dollar is declining, the planner adjusts.

Without the event bus, escalation and budget-aware profile selection would require polling-based checks in the daemon cycle. With the event bus, they happen reactively within seconds.

---

## Success Criteria

1. **Model-task fit**: Deep theoretical work uses Opus with extended thinking; quick fixes use Haiku with 5 turns. No more one-size-fits-all.
2. **Context efficiency**: Prompts include only relevant context for the task. A `latex_debug` session does not load the full knowledge graph. A `deep_proof` session does not include literature alerts.
3. **Cost improvement**: Average cost per quality-point decreases over time as the platform learns which profiles work best. Target: 30% cost reduction within 4 weeks of deployment.
4. **Escalation effectiveness**: Sessions that would have failed with a cheap model are caught and re-run with a stronger model, with > 70% success rate on escalation.
5. **Backward compatibility**: The `default` profile reproduces current behavior exactly. Existing sessions continue to work without any changes to agent definitions or project configurations.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Planner picks wrong profile, wasting expensive Opus turns on easy tasks | Profile stats feedback loop corrects over time. Start with conservative defaults (Sonnet for everything new, only use Opus/Haiku for clearly appropriate tasks). |
| Context composition logic is fragile (wrong files injected) | Extensive logging of what was included in each session's prompt. Profile stats flag profiles with consistently low quality. |
| Escalation loops (Haiku fails, Sonnet fails, no further escalation) | Hard limit: one escalation per task. If the escalated session also fails, log it and move on. |
| Model API changes (new models, deprecations) | Profile registry is a single file. Model identifiers are centralized. Updating models requires changing one file. |
| Knowledge graph and verification systems are not built yet | Context composition gracefully degrades: if a knowledge subgraph is requested but the system is not available, the section is omitted. No errors. |
