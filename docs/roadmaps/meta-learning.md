# Meta-Learning — The Engine That Improves Itself

**Status:** Planned
**Priority:** High — compounds over time, most valuable feature for long-term platform viability
**Estimated effort:** 18-24 hours
**Dependencies:** PostgreSQL with session data (complete), daemon quality scoring (complete), budget tracker (complete)

## Motivation

The deepwork platform already collects rich data about its own operation. Every session produces a quality score (0-100), a cost, a duration, a token count, a set of commits, and a critic verdict. The budget tracker records daily spend. The daemon tracks failure counts and backoff penalties. Session transcripts capture the full agent reasoning trace.

But this data is only used for one thing: failure backoff penalties in the daemon's project scoring. A project that fails gets deprioritized. That is the extent of the platform's self-awareness.

This is a waste. The platform has enough operational data to answer questions that would meaningfully improve its research output:

- **Which model produces the best work for which task?** Haiku might be fine for literature scouting but terrible for experiment design. Sonnet might be cost-effective for writing but Opus might produce higher quality per dollar on theory work.
- **What is the optimal session length?** Do 50-turn sessions produce diminishing returns after turn 30? Should certain agents get fewer turns?
- **Which prompt structures work?** When the planner includes knowledge graph context, does session quality improve? Does including recent decisions help or clutter?
- **When should we stop iterating?** After how many revision cycles does paper quality plateau? At what confidence level should research transition to writing?
- **What time of day produces the best sessions?** API latency varies. Model performance may vary with load.

The meta-learning system answers these questions by analyzing the platform's own operational data, then feeding those answers back into the planner, the session runner, and the budget allocator.

## What We Already Track

Data already flowing into PostgreSQL and local files:

| Data source | Location | Fields |
|-------------|----------|--------|
| Session quality | `daemon.ts` qualityHistory | score, commitsCreated, statusAdvanced, criticVerdict, costUsd, durationMs, agentType, timestamp |
| Session results | `session-runner.ts` | sessionId, projectName, agentType, status, turnsUsed, tokensUsed, costUsd, durationMs, commitsCreated |
| Budget spend | `budget-tracker.ts` | daily totals, per-session costs, remaining budget |
| Eval results | `eval_results` table | 121,614 instances with model, task, condition, correctness |
| Eval runs | `eval_runs` table | 243 runs with model, task, condition, cost, duration |
| Critic verdicts | Session transcripts | ACCEPT/REVISE/REJECT with detailed reasoning |
| Project phases | `status.yaml` | phase transitions with timestamps |
| Backlog tickets | `backlog.ts` | ticket completion rate, priority accuracy |
| Dispatches | `daemon.ts` externalQueue | dispatch success rate, chain depth, trigger source |

## What We Learn

### 1. Session Effectiveness Model

The core analytical unit. For each combination of (agentType, model, taskType, projectPhase), compute:

```typescript
interface SessionEffectivenessModel {
  // Identity
  agentType: string;
  model: string;
  taskType: string | null;
  projectPhase: string | null;

  // Performance metrics
  avgQualityScore: number;
  medianQualityScore: number;
  stddevQuality: number;
  avgCostUsd: number;
  qualityPerDollar: number; // the key efficiency metric
  avgTurnsUsed: number;
  avgDurationMs: number;
  successRate: number; // % of sessions with quality > 50

  // Derived insights
  commonFailureModes: string[]; // extracted from low-quality session transcripts
  optimalTurnCount: number; // point of diminishing returns
  optimalContextSize: number; // too much context hurts?
  costEfficiencyTrend: number; // improving or degrading over time?

  // Sample size
  sessionsAnalyzed: number;
  periodStart: Date;
  periodEnd: Date;
}
```

This answers the question: "What is the best way to run a session for this type of work?"

### 2. Prompt Effectiveness Analysis

Which prompt components correlate with higher session quality?

| Prompt component | Hypothesis | Measurement |
|-----------------|------------|-------------|
| Knowledge graph context included | Improves relevance of findings | Compare quality scores with/without KG context |
| Recent decisions included | Prevents redundant work | Compare sessions that repeat vs. advance |
| Cross-project context included | Enables novel connections | Compare insight generation rate |
| Detailed agent persona | Improves role adherence | Compare commit relevance to agent type |
| Specific task instructions | Reduces scope creep | Compare status advancement rate |

Analysis approach: Natural experiment. The planner already varies prompt content based on availability (KG context exists only after it's built, cross-project context only after that system exists). Compare sessions from before and after each feature's introduction, controlling for other variables.

### 3. Temporal Patterns

```sql
-- Do sessions started at certain hours produce better quality?
SELECT
    EXTRACT(HOUR FROM started_at) AS hour_utc,
    AVG(quality_score) AS avg_quality,
    AVG(cost_usd) AS avg_cost,
    COUNT(*) AS sessions
FROM sessions
GROUP BY hour_utc
ORDER BY avg_quality DESC;
```

Potential findings:
- API latency is lower during off-peak hours (better for long sessions)
- Model performance degrades under high load (weekend vs. weekday patterns)
- Session quality varies with project phase (early phases have easier wins)

### 4. Research Strategy Patterns

Higher-order learning about how to do research:

- **Theory-first vs. empirical-first**: Which approach produces papers with higher review simulation scores?
- **Iteration depth**: How many research-review cycles before diminishing returns?
- **Transition timing**: At what confidence level does transitioning from research to writing produce the best outcomes?
- **Parallel vs. serial experiments**: Does running multiple experiments concurrently hurt quality?

These are harder to measure (small sample size per project) but become valuable as the platform runs more projects.

## Schema Additions

New migration file: `orchestrator/sql/006_meta_learning.sql`

```sql
BEGIN;

-- ============================================================
-- Session Effectiveness — aggregated performance metrics
-- ============================================================
CREATE TABLE session_effectiveness (
    id                  SERIAL PRIMARY KEY,
    agent_type          TEXT NOT NULL,
    model               TEXT NOT NULL,
    task_type           TEXT,                   -- null = all task types
    project_phase       TEXT,                   -- null = all phases
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    sessions_count      INTEGER NOT NULL,
    avg_quality         REAL NOT NULL,
    median_quality      REAL,
    stddev_quality      REAL,
    avg_cost_usd        REAL NOT NULL,
    quality_per_dollar  REAL NOT NULL,
    avg_turns_used      REAL,
    avg_duration_ms     REAL,
    success_rate        REAL NOT NULL,          -- quality > 50
    optimal_turn_count  INTEGER,                -- diminishing returns analysis
    cost_efficiency_trend REAL,                 -- slope of quality_per_dollar over time
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sess_eff_agent   ON session_effectiveness (agent_type, model);
CREATE INDEX idx_sess_eff_phase   ON session_effectiveness (project_phase);
CREATE INDEX idx_sess_eff_period  ON session_effectiveness (period_start, period_end);

-- ============================================================
-- Optimization Log — record of suggested and applied improvements
-- ============================================================
CREATE TABLE optimization_log (
    id              SERIAL PRIMARY KEY,
    category        TEXT NOT NULL
                    CHECK (category IN (
                        'model_selection',    -- use a different model for this task
                        'turn_count',         -- adjust max turns
                        'context_size',       -- adjust context inclusion
                        'session_frequency',  -- change how often a project gets sessions
                        'budget_allocation',  -- shift spend between agents/projects
                        'prompt_structure',   -- change prompt template
                        'agent_definition',   -- update agent persona
                        'phase_transition'    -- change when phases transition
                    )),
    optimization    TEXT NOT NULL,           -- what to change
    reasoning       TEXT NOT NULL,           -- why, with supporting data
    expected_impact TEXT NOT NULL,           -- predicted improvement
    applied         BOOLEAN NOT NULL DEFAULT FALSE,
    applied_at      TIMESTAMPTZ,
    actual_impact   REAL,                   -- measured after application (quality_per_dollar delta)
    measurement_period_days INTEGER,        -- how long after application was impact measured
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_optlog_category ON optimization_log (category);
CREATE INDEX idx_optlog_applied  ON optimization_log (applied);

-- ============================================================
-- Weekly Insights — periodic meta-analysis summaries
-- ============================================================
CREATE TABLE weekly_insights (
    id              SERIAL PRIMARY KEY,
    week_start      DATE NOT NULL,
    week_end        DATE NOT NULL,
    sessions_total  INTEGER NOT NULL,
    total_spend_usd REAL NOT NULL,
    avg_quality     REAL NOT NULL,
    quality_trend   REAL,                   -- vs. previous week
    top_finding     TEXT NOT NULL,           -- most interesting insight
    optimizations   JSONB NOT NULL DEFAULT '[]',
    effectiveness_summary JSONB NOT NULL DEFAULT '{}',
    raw_analysis    JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (week_start)
);

-- ============================================================
-- Session Defaults — auto-tuned parameters per agent/task
-- ============================================================
CREATE TABLE session_defaults (
    id              SERIAL PRIMARY KEY,
    agent_type      TEXT NOT NULL,
    task_type       TEXT,                   -- null = default for all tasks
    project_phase   TEXT,                   -- null = default for all phases
    recommended_model TEXT NOT NULL,
    recommended_max_turns INTEGER NOT NULL,
    recommended_thinking_level TEXT NOT NULL
                    CHECK (recommended_thinking_level IN ('standard', 'extended')),
    context_include_kg BOOLEAN DEFAULT TRUE,
    context_include_decisions BOOLEAN DEFAULT TRUE,
    context_include_cross_project BOOLEAN DEFAULT FALSE,
    confidence      REAL NOT NULL DEFAULT 0.5,  -- how confident we are in these defaults
    sessions_basis  INTEGER NOT NULL,           -- how many sessions informed this
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (agent_type, task_type, project_phase)
);

-- ============================================================
-- Convenience view: current best configuration per agent type
-- ============================================================
CREATE VIEW v_best_config AS
SELECT DISTINCT ON (agent_type, task_type)
    agent_type,
    task_type,
    recommended_model,
    recommended_max_turns,
    recommended_thinking_level,
    confidence,
    sessions_basis,
    updated_at
FROM session_defaults
ORDER BY agent_type, task_type, confidence DESC, updated_at DESC;

COMMIT;
```

## New Files

### `orchestrator/src/meta-learning.ts` — MetaLearner class

Core module for analyzing platform performance and generating optimizations. Follows existing codebase patterns (ESM, async/await, `pg.Pool`).

```typescript
import type pg from "pg";
import { ActivityLogger } from "./logger.js";

// ============================================================
// Types
// ============================================================

export interface EffectivenessReport {
  period: { start: Date; end: Date };
  totalSessions: number;
  totalSpendUsd: number;
  overallQualityPerDollar: number;
  byAgent: Record<string, AgentEffectiveness>;
  byModel: Record<string, ModelEffectiveness>;
  byPhase: Record<string, PhaseEffectiveness>;
  trends: TrendAnalysis;
}

export interface AgentEffectiveness {
  agentType: string;
  sessions: number;
  avgQuality: number;
  avgCost: number;
  qualityPerDollar: number;
  successRate: number;
  bestModel: string;
  worstModel: string;
}

export interface ModelEffectiveness {
  model: string;
  sessions: number;
  avgQuality: number;
  avgCost: number;
  qualityPerDollar: number;
  bestForAgentTypes: string[];
  worstForAgentTypes: string[];
}

export interface PhaseEffectiveness {
  phase: string;
  sessions: number;
  avgQuality: number;
  avgIterations: number;
  typicalDurationDays: number;
}

export interface TrendAnalysis {
  qualityTrend: "improving" | "stable" | "degrading";
  costTrend: "decreasing" | "stable" | "increasing";
  efficiencyTrend: "improving" | "stable" | "degrading";
  weekOverWeekQualityDelta: number;
  weekOverWeekCostDelta: number;
}

export interface Optimization {
  category: string;
  optimization: string;
  reasoning: string;
  expectedImpact: string;
  confidence: number;
  dataPoints: number;
}

export interface SessionDefaults {
  agentType: string;
  taskType: string | null;
  projectPhase: string | null;
  recommendedModel: string;
  recommendedMaxTurns: number;
  recommendedThinkingLevel: "standard" | "extended";
  contextIncludeKg: boolean;
  contextIncludeDecisions: boolean;
  contextIncludeCrossProject: boolean;
  confidence: number;
  sessionsBasis: number;
}

export interface WeeklyInsight {
  weekStart: Date;
  weekEnd: Date;
  sessionsTotal: number;
  totalSpendUsd: number;
  avgQuality: number;
  qualityTrend: number;
  topFinding: string;
  optimizations: Optimization[];
  effectivenessSummary: Record<string, unknown>;
}

// ============================================================
// MetaLearner
// ============================================================

export class MetaLearner {
  constructor(
    private pool: pg.Pool,
    private logger: ActivityLogger,
  ) {}

  /**
   * Comprehensive analysis of session effectiveness.
   *
   * Queries the sessions table (or quality history) to compute
   * effectiveness metrics for every (agent, model, task, phase) combination.
   * Identifies which configurations produce the highest quality per dollar.
   *
   * Analysis steps:
   *   1. Aggregate session data by agent type, model, task type, phase
   *   2. Compute quality-per-dollar for each combination
   *   3. Identify the best and worst configurations
   *   4. Compute trends (week-over-week improvement or degradation)
   *   5. Run diminishing returns analysis on turn count vs. quality
   *   6. Persist results to session_effectiveness table
   *
   * @param periodDays - How many days of history to analyze (default: 30)
   */
  async analyzeEffectiveness(periodDays?: number): Promise<EffectivenessReport> {
    const days = periodDays ?? 30;
    const periodEnd = new Date();
    const periodStart = new Date(periodEnd.getTime() - days * 24 * 60 * 60 * 1000);

    // Core aggregation query
    const { rows } = await this.pool.query(
      `SELECT
          agent_type,
          model,
          project_phase,
          COUNT(*) AS sessions,
          AVG(quality_score) AS avg_quality,
          PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY quality_score) AS median_quality,
          STDDEV(quality_score) AS stddev_quality,
          AVG(cost_usd) AS avg_cost,
          AVG(quality_score) / NULLIF(AVG(cost_usd), 0) AS quality_per_dollar,
          AVG(turns_used) AS avg_turns,
          AVG(duration_ms) AS avg_duration,
          AVG(CASE WHEN quality_score > 50 THEN 1.0 ELSE 0.0 END) AS success_rate
       FROM sessions
       WHERE started_at >= $1 AND started_at <= $2
         AND status = 'completed'
       GROUP BY agent_type, model, project_phase
       HAVING COUNT(*) >= 3`,
      [periodStart, periodEnd],
    );

    // ... build EffectivenessReport from rows
    // ... compute trends by comparing to previous period
    // ... persist to session_effectiveness table

    return {} as EffectivenessReport; // placeholder
  }

  /**
   * Generate actionable optimization suggestions.
   *
   * Uses the effectiveness data to identify improvements:
   *   - If model A consistently outperforms model B for agent type X,
   *     suggest switching to model A.
   *   - If sessions beyond N turns show no quality improvement,
   *     suggest reducing max turns.
   *   - If a project phase has declining quality, suggest reassessing approach.
   *   - If budget allocation doesn't match quality-per-dollar rankings,
   *     suggest reallocation.
   *
   * Each optimization includes reasoning with specific data points
   * and an expected impact estimate.
   *
   * Persists suggestions to optimization_log table.
   */
  async suggestOptimizations(): Promise<Optimization[]> {
    const optimizations: Optimization[] = [];

    // --- Model selection optimizations ---
    // Find cases where a cheaper model produces similar quality
    const modelComps = await this.pool.query(
      `SELECT
          se1.agent_type,
          se1.model AS current_model,
          se2.model AS better_model,
          se1.avg_quality AS current_quality,
          se2.avg_quality AS better_quality,
          se1.avg_cost_usd AS current_cost,
          se2.avg_cost_usd AS better_cost,
          se2.quality_per_dollar AS better_qpd,
          se1.quality_per_dollar AS current_qpd
       FROM session_effectiveness se1
       JOIN session_effectiveness se2
         ON se1.agent_type = se2.agent_type
         AND se1.project_phase = se2.project_phase
         AND se1.model != se2.model
       WHERE se2.quality_per_dollar > se1.quality_per_dollar * 1.2
         AND se2.sessions_count >= 5
         AND se1.period_end = (SELECT MAX(period_end) FROM session_effectiveness)
       ORDER BY (se2.quality_per_dollar - se1.quality_per_dollar) DESC`,
    );

    for (const row of modelComps.rows) {
      optimizations.push({
        category: "model_selection",
        optimization: `Switch ${row.agent_type} from ${row.current_model} to ${row.better_model}`,
        reasoning:
          `${row.better_model} produces ${row.better_quality.toFixed(1)} avg quality ` +
          `at $${row.better_cost.toFixed(3)}/session vs ${row.current_model} at ` +
          `${row.current_quality.toFixed(1)} quality for $${row.current_cost.toFixed(3)}. ` +
          `Quality-per-dollar: ${row.better_qpd.toFixed(1)} vs ${row.current_qpd.toFixed(1)}.`,
        expectedImpact: `+${((row.better_qpd / row.current_qpd - 1) * 100).toFixed(0)}% efficiency`,
        confidence: Math.min(row.better_qpd / row.current_qpd / 2, 0.95),
        dataPoints: row.sessions_count,
      });
    }

    // --- Turn count optimizations ---
    // Find diminishing returns in turn usage
    // ... similar query pattern for turns analysis

    // --- Budget allocation optimizations ---
    // Compare quality-per-dollar across agents, suggest reallocation
    // ... similar query pattern

    // Persist to optimization_log
    for (const opt of optimizations) {
      await this.pool.query(
        `INSERT INTO optimization_log (category, optimization, reasoning, expected_impact)
         VALUES ($1, $2, $3, $4)`,
        [opt.category, opt.optimization, opt.reasoning, opt.expectedImpact],
      );
    }

    return optimizations;
  }

  /**
   * Auto-tune session configuration defaults.
   *
   * For each (agentType, taskType, projectPhase) combination with
   * sufficient data (>=10 sessions), compute the optimal configuration:
   *   - Best model (highest quality-per-dollar)
   *   - Optimal turn count (diminishing returns threshold)
   *   - Thinking level (extended only if quality delta justifies cost)
   *   - Context inclusion (which prompt components correlate with quality)
   *
   * Updates the session_defaults table. The planner reads this table
   * when building session configs, making the feedback loop complete.
   *
   * Confidence increases with sample size:
   *   - 10-20 sessions: confidence 0.4-0.6 (use as suggestion, don't override)
   *   - 20-50 sessions: confidence 0.6-0.8 (use as default, allow override)
   *   - 50+ sessions: confidence 0.8-0.95 (use as strong default)
   */
  async updateSessionDefaults(
    agentType: string,
    taskType?: string,
  ): Promise<SessionDefaults> {
    // Query effectiveness data for this agent/task combination
    // Compute optimal configuration
    // Upsert into session_defaults table
    return {} as SessionDefaults; // placeholder
  }

  /**
   * Generate weekly meta-analysis insights.
   *
   * Runs every Monday (triggered by daemon weekly job).
   * Produces a structured summary of what we learned about our own
   * process during the past week.
   *
   * Sections:
   *   1. Efficiency summary: quality-per-dollar trend, total spend vs. output
   *   2. Agent performance: which agents performed well/poorly and why
   *   3. Model comparison: any model switches recommended?
   *   4. Phase analysis: are any projects stuck? Progressing efficiently?
   *   5. Optimization results: did previous optimizations have impact?
   *   6. Top finding: single most interesting/actionable insight
   *
   * Uses LLM (Haiku) to synthesize the statistical data into a readable
   * narrative. Cost: ~$0.02 per weekly insight.
   */
  async generateWeeklyInsights(): Promise<WeeklyInsight> {
    // 1. Compute this week's effectiveness
    const thisWeek = await this.analyzeEffectiveness(7);

    // 2. Compare to previous week
    // (shift period back 7 days)

    // 3. Check optimization impact
    const { rows: appliedOpts } = await this.pool.query(
      `SELECT * FROM optimization_log
       WHERE applied = TRUE
         AND applied_at >= NOW() - INTERVAL '14 days'
         AND actual_impact IS NULL`,
    );

    // For each applied optimization, measure impact
    for (const opt of appliedOpts) {
      // Compare quality-per-dollar before and after application
      // Update actual_impact field
    }

    // 4. Generate new optimization suggestions
    const newOpts = await this.suggestOptimizations();

    // 5. Use LLM to synthesize into narrative
    // ...

    // 6. Persist to weekly_insights table
    // 7. Return structured insight

    return {} as WeeklyInsight; // placeholder
  }

  /**
   * Analyze diminishing returns for a given agent type.
   *
   * Groups sessions by turn count buckets and computes marginal
   * quality gain per additional turn. Returns the optimal turn
   * count where marginal gain drops below threshold.
   */
  async analyzeDiminishingReturns(
    agentType: string,
  ): Promise<{ optimalTurns: number; marginalGainCurve: number[] }> {
    const { rows } = await this.pool.query(
      `SELECT
          FLOOR(turns_used / 5) * 5 AS turn_bucket,
          AVG(quality_score) AS avg_quality,
          COUNT(*) AS sessions
       FROM sessions
       WHERE agent_type = $1 AND status = 'completed'
       GROUP BY turn_bucket
       HAVING COUNT(*) >= 3
       ORDER BY turn_bucket`,
      [agentType],
    );

    // Compute marginal quality gain between buckets
    const marginalGains: number[] = [];
    for (let i = 1; i < rows.length; i++) {
      const gain = rows[i].avg_quality - rows[i - 1].avg_quality;
      marginalGains.push(gain);
    }

    // Find the point where marginal gain drops below 2 quality points per 5 turns
    const threshold = 2.0;
    let optimalBucket = rows.length > 0 ? rows[rows.length - 1].turn_bucket : 50;
    for (let i = 0; i < marginalGains.length; i++) {
      if (marginalGains[i] < threshold) {
        optimalBucket = rows[i].turn_bucket;
        break;
      }
    }

    return {
      optimalTurns: optimalBucket,
      marginalGainCurve: marginalGains,
    };
  }
}
```

**Key implementation details:**

1. **Minimum sample sizes.** No conclusions from fewer than 3 sessions per combination. Confidence scales with sample size. This prevents overfitting to early data when the platform has limited history.

2. **Causal vs. correlational.** The meta-learner is careful about causation. It can observe that Sonnet produces higher quality for writing tasks, but it cannot conclude that switching to Sonnet *will* improve quality (the tasks might have been easier). The `confidence` field reflects this uncertainty. True causal inference requires A/B testing (see "How It Feeds Back" below).

3. **Diminishing returns analysis.** For turn count optimization, the system groups sessions into turn-count buckets (0-5, 5-10, 10-15, ...) and computes marginal quality gain per bucket. The optimal turn count is where marginal gain drops below a configurable threshold.

4. **Cost includes API costs only.** Session cost is the direct API spend (tokens * pricing). It does not include infrastructure cost (VPS, database) or opportunity cost (what else could have been researched). Future versions might incorporate opportunity cost via the strategist's portfolio analysis.

5. **Temporal windowing.** All analyses use rolling windows (default 30 days) to adapt to changing conditions. A model that was effective 3 months ago may not be effective today due to provider changes, degradation, or new model releases.

## How It Feeds Back

The meta-learning loop has five concrete feedback channels:

### 1. Planner Uses Effectiveness Data

When the daemon's planner selects a model and turn count for a session, it consults `session_defaults`:

```typescript
// In daemon.ts, when building SessionConfig:
private async getOptimalConfig(
  agentType: AgentType,
  projectPhase: string,
): Promise<Partial<SessionConfig>> {
  if (!this.dbPool) return {};

  const { rows } = await this.dbPool.query(
    `SELECT recommended_model, recommended_max_turns, recommended_thinking_level,
            context_include_kg, context_include_decisions, context_include_cross_project,
            confidence
     FROM session_defaults
     WHERE agent_type = $1
       AND (project_phase = $2 OR project_phase IS NULL)
     ORDER BY
       CASE WHEN project_phase = $2 THEN 0 ELSE 1 END,
       confidence DESC
     LIMIT 1`,
    [agentType, projectPhase],
  );

  if (rows.length === 0 || rows[0].confidence < 0.4) {
    return {}; // not enough data, use hardcoded defaults
  }

  return {
    maxTurns: rows[0].recommended_max_turns,
    thinkingLevel: rows[0].recommended_thinking_level,
    // model selection handled separately in session runner
  };
}
```

### 2. Session Defaults Auto-Tune

The meta-learner runs periodically (weekly, or after every N sessions) and updates `session_defaults`. This is fully automatic — no human approval needed for configuration changes below a confidence threshold. The system is conservative:

- Only override defaults when confidence > 0.6 (minimum 20 sessions of evidence)
- Never increase cost by more than 50% without human approval
- Log every change to `optimization_log` for audit
- Measure impact after application and revert if negative

### 3. Agent Definitions Evolve (Human-Approved)

When the meta-learner identifies prompt patterns that correlate with higher session quality, it generates suggested updates to agent definitions. These are *not* auto-applied — they go into `optimization_log` with `category = 'agent_definition'` and `applied = FALSE`, awaiting human review.

Example optimization:
```
category: agent_definition
optimization: Add "always verify numerical claims against eval_results before
              including them in paper text" to writer agent definition
reasoning: Writer sessions that included a verification step (detected in
           transcript) had 23% higher critic acceptance rate (n=14, p<0.05)
expected_impact: +15-25% critic acceptance rate for writer sessions
```

### 4. Budget Allocation Optimizes

The budget tracker currently enforces a flat daily budget. With meta-learning, budget allocation becomes intelligent:

```typescript
// Allocate more budget to high-ROI session types
interface BudgetAllocation {
  agentType: string;
  budgetSharePct: number; // % of daily budget allocated to this agent type
  reasoning: string;
}

// Example output:
// researcher: 35% (quality-per-dollar: 42.1, highest ROI)
// experimenter: 25% (quality-per-dollar: 31.7, essential for eval)
// writer: 20% (quality-per-dollar: 28.3, needed for paper progress)
// critic: 10% (quality-per-dollar: 55.0, cheap but high impact)
// scout: 5% (quality-per-dollar: 22.1, diminishing returns)
// strategist: 5% (quality-per-dollar: 18.4, weekly is sufficient)
```

### 5. Weekly Insights Posted to Forum

Every Monday, the meta-learner generates a weekly insight report and posts it to the OpenClaw forum (via Lev, the archivist agent). This gives the entire collective awareness of what is and isn't working:

```
## Platform Meta-Learning Report — Week of 2026-03-16

### Efficiency
- 23 sessions this week, $18.42 total spend
- Average quality: 62.3 (up from 58.1 last week, +7.2%)
- Quality-per-dollar: 3.38 (up from 3.12, +8.3%)

### Key Finding
Experimenter sessions using extended thinking produced 31% higher quality
at only 18% higher cost. Recommend: enable extended thinking for all
experimenter sessions in empirical-evaluation phase.

### Model Performance
- Claude Sonnet 4: best for writing (quality 71.2, cost $0.43)
- Claude Haiku 3.5: best for scouting (quality 54.1, cost $0.02)
- Claude Opus 4: best for theory (quality 82.4, cost $1.12) — but
  quality-per-dollar is lower than Sonnet for non-theory tasks

### Applied Optimizations
- Reduced writer max turns from 50 to 35 (applied 2026-03-10)
  Impact: quality unchanged (69.8 vs 70.2), cost reduced 22%. SUCCESS.

### New Suggestions
1. Switch scout from Sonnet to Haiku (saves $0.35/session, quality drop <5%)
2. Increase experimenter thinking level to extended (quality +31%, cost +18%)
```

## Integration with Existing Systems

### Daemon Weekly Job

The daemon already runs on a polling interval (`pollIntervalMs`). Add a weekly meta-learning cycle:

```typescript
// In daemon.ts, within the main poll loop:
private async maybeRunMetaLearning(): Promise<void> {
  if (!this.dbPool) return;

  const lastRun = await this.pool.query(
    `SELECT MAX(created_at) AS last FROM weekly_insights`,
  );
  const daysSinceLastRun = lastRun.rows[0]?.last
    ? (Date.now() - new Date(lastRun.rows[0].last).getTime()) / 86400000
    : Infinity;

  if (daysSinceLastRun < 6.5) return; // run weekly

  const learner = new MetaLearner(this.dbPool, this.logger);
  const insights = await learner.generateWeeklyInsights();

  this.logger.log("meta_learning_complete", {
    sessions: insights.sessionsTotal,
    avgQuality: insights.avgQuality,
    optimizations: insights.optimizations.length,
  });

  // Post to forum via Lev
  // ... format and post
}
```

### API Endpoints

```typescript
// In orchestrator/src/routes/meta.ts:
import { Router, type Request, type Response } from "express";
import type pg from "pg";
import { MetaLearner } from "../meta-learning.js";
import { ActivityLogger } from "../logger.js";

export function metaRoutes(pool: pg.Pool, logger: ActivityLogger): Router {
  const router = Router();
  const learner = new MetaLearner(pool, logger);

  // GET /api/meta/effectiveness
  // Returns the latest effectiveness report.
  // Query params: ?period=30 (days), ?agent=researcher, ?model=claude-sonnet-4
  router.get("/effectiveness", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/meta/effectiveness/history
  // Returns effectiveness trend over time for charts.
  // Query params: ?metric=quality_per_dollar&agent=writer&granularity=weekly
  router.get("/effectiveness/history", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/meta/optimizations
  // List all optimization suggestions. Query params: ?applied=false&category=model_selection
  router.get("/optimizations", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/meta/optimizations/:id/apply
  // Mark an optimization as applied. Starts impact measurement.
  router.post(
    "/optimizations/:id/apply",
    async (req: Request, res: Response) => {
      /* ... */
    },
  );

  // POST /api/meta/optimizations/:id/dismiss
  // Dismiss an optimization suggestion.
  router.post(
    "/optimizations/:id/dismiss",
    async (req: Request, res: Response) => {
      /* ... */
    },
  );

  // GET /api/meta/insights
  // List weekly insights. Query params: ?limit=10
  router.get("/insights", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/meta/defaults
  // Current auto-tuned session defaults.
  router.get("/defaults", async (req: Request, res: Response) => {
    /* ... */
  });

  // POST /api/meta/analyze
  // Trigger an on-demand meta-analysis. Body: { periodDays?: number }
  router.post("/analyze", async (req: Request, res: Response) => {
    /* ... */
  });

  return router;
}
```

### Dashboard Visualizations

The Astro dashboard at `site/` should show:

- **Effectiveness heatmap**: Agent types on Y-axis, models on X-axis, quality-per-dollar as color intensity. Instantly shows which model works best for which agent.
- **Trend charts**: Quality, cost, and efficiency over time (weekly granularity). Overlay optimization application points to show impact.
- **Diminishing returns curves**: Turns on X-axis, marginal quality gain on Y-axis, per agent type. Shows where sessions should stop.
- **Optimization pipeline**: Kanban-style view of suggested, applied, and measured optimizations.
- **Weekly insight cards**: Scrollable feed of weekly meta-analysis summaries.

### A/B Testing Framework

For high-confidence causal inference, the meta-learner can run A/B tests:

```typescript
interface ABTest {
  id: string;
  name: string;
  controlConfig: Partial<SessionConfig>;
  treatmentConfig: Partial<SessionConfig>;
  agentType: string;
  minSessions: number; // per arm
  metric: "quality_score" | "quality_per_dollar" | "success_rate";
  status: "running" | "completed" | "inconclusive";
  controlResults: number[];
  treatmentResults: number[];
  pValue: number | null;
  effectSize: number | null;
}
```

The daemon randomly assigns sessions to control or treatment based on the test configuration. After minimum sample size is reached, compute statistical significance and auto-apply if treatment wins.

## Task Breakdown

| # | Task | Est. hours | Dependencies |
|---|------|-----------|--------------|
| 1 | SQL migration (`006_meta_learning.sql`) | 1.0 | None |
| 2 | Session effectiveness analysis queries | 2.5 | Task 1 |
| 3 | `MetaLearner` class — `analyzeEffectiveness` | 3.0 | Task 2 |
| 4 | `MetaLearner` class — `suggestOptimizations` | 3.0 | Task 3 |
| 5 | `MetaLearner` class — `updateSessionDefaults` | 2.0 | Task 3 |
| 6 | `MetaLearner` class — `generateWeeklyInsights` | 2.0 | Tasks 3-4 |
| 7 | Diminishing returns analysis | 1.5 | Task 3 |
| 8 | Planner integration (daemon reads session_defaults) | 2.0 | Task 5 |
| 9 | Daemon weekly job hook | 1.0 | Task 6 |
| 10 | API routes (`routes/meta.ts`) | 2.0 | Tasks 3-6 |
| 11 | Dashboard effectiveness heatmap and trend charts | 2.5 | Task 10 |
| 12 | Dashboard optimization pipeline view | 1.5 | Task 10 |
| 13 | Forum integration (Lev posts weekly insights) | 1.0 | Task 6 |
| 14 | A/B testing framework (stretch goal) | 3.0 | Tasks 5, 8 |
| **Total** | | **~28 hours** (24 without A/B testing) | |

### Suggested Implementation Order

**Phase 1 — Data Foundation (Tasks 1-3, ~6.5 hours)**
Schema, aggregation queries, and core effectiveness analysis. After this phase, the system can answer "how is each agent/model combination performing?"

**Phase 2 — Optimization Engine (Tasks 4-7, ~8.5 hours)**
Suggestion generation, auto-tuning, weekly insights, and diminishing returns analysis. After this phase, the system actively recommends improvements.

**Phase 3 — Feedback Loop (Tasks 8-9, ~3 hours)**
Wire the meta-learner's outputs into the daemon's planning. After this phase, the platform self-improves: better sessions lead to better data lead to better sessions.

**Phase 4 — Visibility (Tasks 10-13, ~7 hours)**
API endpoints, dashboard visualizations, and forum integration. After this phase, humans can see what the platform has learned about itself.

**Phase 5 — Causal Inference (Task 14, ~3 hours, stretch goal)**
A/B testing framework for rigorous causal claims about configuration changes.

## Success Criteria

1. **Quality-per-dollar increases month over month.** The primary metric. After 3 months of meta-learning, the platform should be producing measurably better research per dollar spent than it was at launch.

2. **Auto-tuning produces measurable improvements.** When the meta-learner changes a session default (model, turns, thinking level), the change should produce a statistically significant improvement within 2 weeks of application, measured via before/after comparison.

3. **Weekly insights are genuinely informative.** Not just statistics dumps. Each weekly insight should contain at least one finding that an informed human researcher would consider non-obvious and actionable.

4. **Optimization suggestions are actionable and effective.** Target: >50% of optimization suggestions get applied (either auto-applied or human-approved). Of those applied, >60% produce measurable positive impact.

5. **The platform knows what it doesn't know.** When the meta-learner lacks data for a conclusion (small sample size, confounded variables), it says so explicitly rather than making a low-confidence recommendation.

6. **2x efficiency target.** After 3 months of operation, the platform's quality-per-dollar should be at least 2x what it was during its first month. This is the headline metric for whether meta-learning is working.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient data early on | Recommendations based on <10 sessions are unreliable | Minimum sample size requirements, confidence scaling, no auto-apply below 0.6 confidence |
| Confounding variables | Attributing quality to model when it was actually the task difficulty | Phase and task type stratification in all analyses; A/B testing for causal claims |
| Goodhart's law (optimizing for quality score instead of actual quality) | Sessions get high scores without producing good research | Quality score includes multiple signals (commits, status advancement, critic verdict); periodic human calibration of the scoring function |
| Auto-tuning oscillation | System keeps switching between two configurations | Hysteresis: require sustained improvement over 2 weeks before switching; minimum 10 sessions on new config before re-evaluating |
| Cost of meta-learning itself | Weekly analysis costs API dollars | Use Haiku for synthesis ($0.02/week); SQL aggregation is free; total meta-learning overhead <1% of research budget |
| Stale defaults | Config optimized for 3 months ago doesn't work today | Rolling windows (30-day default), recency weighting, automatic staleness detection when new models are available |

## Open Questions

1. **How to credit improvements?** When quality improves, is it the meta-learner's optimization, the agent's learning from previous sessions, or external factors (model updates, easier project phase)? Rigorous attribution requires controlled experiments, which are expensive.

2. **Should the meta-learner have access to session transcripts?** Currently planned: no (just structured metrics). But transcript analysis could reveal *why* sessions fail, not just *that* they fail. Tradeoff: reading transcripts requires LLM calls, increasing cost. Start with metrics-only, add transcript analysis if failure modes remain opaque.

3. **Multi-objective optimization?** Quality-per-dollar is the headline metric, but sometimes you want maximum quality regardless of cost (final revision before submission) or minimum cost with acceptable quality (literature scouting). Should the meta-learner support multiple optimization targets?

4. **Cross-platform learning?** If multiple deepwork instances run on different machines or for different research groups, should meta-learning be shared? This raises privacy and generalizability questions but could dramatically increase the data available for learning.
