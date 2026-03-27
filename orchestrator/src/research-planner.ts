import { randomUUID } from "node:crypto";
import type pg from "pg";
import type { ProjectManager, ProjectStatus } from "./project-manager.js";
import type { KnowledgeGraph, ClaimRow, ClaimRelationRow } from "./knowledge-graph.js";
import type { BudgetTracker } from "./budget-tracker.js";
import type { BacklogManager } from "./backlog.js";
import { type AgentType, PHASE_TO_AGENT, type SessionResult } from "./session-runner.js";
import type { SessionSignals } from "./session-manager.js";
import { LinearClient } from "./linear.js";

// ============================================================
// Types
// ============================================================

export type PlanningStrategy =
  | "gap_filling"
  | "contradiction_resolution"
  | "risk_mitigation"
  | "deadline_driven"
  | "quality_improvement"
  | "literature_driven"
  | "linear_driven";

export interface SessionBrief {
  id: string;
  projectName: string;
  agentType: AgentType;
  objective: string;
  context: BriefContext;
  constraints: BriefConstraints;
  deliverables: Deliverable[];
  priority: number;
  reasoning: string;
  strategy: PlanningStrategy;
}

export interface BriefContext {
  claims: ClaimRow[];
  contradictions: ClaimRelationRow[];
  files: string[];
  recentDecisions: string[];
  supplementary?: string;
}

export interface BriefConstraints {
  maxTurns: number;
  maxDurationMs: number;
  maxBudgetUsd: number;
  model: string;
}

export interface Deliverable {
  description: string;
  type: "commit" | "file" | "status_update" | "claim_update" | "analysis";
  verificationMethod: "file_exists" | "commit_count" | "status_changed" | "manual";
  target?: string;
}

export interface SessionEvaluation {
  sessionId: string;
  briefId: string;
  project: string;
  agentType: string;
  strategy: PlanningStrategy;
  objective: string;
  deliverablesMet: number;
  deliverablesTotal: number;
  qualityScore: number;
  reasoning: string;
  costUsd: number;
  durationMs: number;
  createdAt: string;
}

export interface ProjectInsight {
  project: string;
  gapCount: number;
  contradictionCount: number;
  unsupportedClaimCount: number;
  weakClaimCount: number;
  totalClaims: number;
  lastSessionQuality: number | null;
  suggestedAction: string;
}

export interface PlannerState {
  enabled: boolean;
  lastPlanCycleAt: string | null;
  lastPlanDurationMs: number;
  recentEvaluations: SessionEvaluation[];
  strategyWeights: Record<PlanningStrategy, number>;
}

// ============================================================
// Constants
// ============================================================

const DEFAULT_STRATEGY_WEIGHTS: Record<PlanningStrategy, number> = {
  "risk_mitigation": 1.5,
  "contradiction_resolution": 1.4,
  "deadline_driven": 1.3,
  "linear_driven": 1.2,
  "literature_driven": 1.2,
  "gap_filling": 1.0,
  "quality_improvement": 0.9,
};

const MAX_CLAIMS_IN_CONTEXT = 15;
const MAX_CONTRADICTIONS_IN_CONTEXT = 5;
const STRATEGY_WEIGHT_ALPHA = 0.1;
const MIN_WEIGHT = 0.3;
const MAX_WEIGHT = 2.0;

// ============================================================
// ResearchPlanner
// ============================================================

export class ResearchPlanner {
  private pool: pg.Pool | null;
  private projectManager: ProjectManager;
  private kg: KnowledgeGraph | null;
  private budgetTracker: BudgetTracker;
  private backlogManager: BacklogManager | null;
  private linearClient: LinearClient | null;
  private strategyWeights: Map<PlanningStrategy, number>;
  private evaluationHistory: SessionEvaluation[] = [];
  private lastPlanCycleAt: string | null = null;
  private lastPlanDurationMs = 0;

  constructor(
    pool: pg.Pool | null,
    projectManager: ProjectManager,
    kg: KnowledgeGraph | null,
    budgetTracker: BudgetTracker,
    backlogManager?: BacklogManager | null,
    linearClient?: LinearClient | null,
  ) {
    this.pool = pool;
    this.projectManager = projectManager;
    this.kg = kg;
    this.budgetTracker = budgetTracker;
    this.backlogManager = backlogManager ?? null;
    this.linearClient = linearClient ?? null;
    this.strategyWeights = new Map(
      Object.entries(DEFAULT_STRATEGY_WEIGHTS) as [PlanningStrategy, number][],
    );

    // Load persisted state from DB (non-blocking)
    this.loadPersistedState().catch((err) => {
      console.error("[Planner] Failed to load persisted state:", err);
    });
  }

  /** Load evaluation history and strategy weights from DB to survive restarts. */
  private async loadPersistedState(): Promise<void> {
    if (!this.pool) return;

    // Load recent evaluations
    try {
      const { rows } = await this.pool.query(
        `SELECT session_id, brief_id, project, agent_type, strategy, objective,
                deliverables_met, deliverables_total, quality_score, reasoning,
                cost_usd, duration_ms, created_at
         FROM session_evaluations ORDER BY created_at DESC LIMIT 50`,
      );
      this.evaluationHistory = rows.map((r: Record<string, unknown>) => ({
        sessionId: r.session_id as string,
        briefId: r.brief_id as string,
        project: r.project as string,
        agentType: r.agent_type as string,
        strategy: r.strategy as PlanningStrategy,
        objective: r.objective as string,
        deliverablesMet: r.deliverables_met as number,
        deliverablesTotal: r.deliverables_total as number,
        qualityScore: r.quality_score as number,
        reasoning: r.reasoning as string,
        costUsd: r.cost_usd as number,
        durationMs: r.duration_ms as number,
        createdAt: (r.created_at as Date).toISOString(),
      })).reverse(); // oldest first for slice(-N) operations
      if (this.evaluationHistory.length > 0) {
        console.log(`[Planner] Loaded ${this.evaluationHistory.length} evaluations from DB`);
      }
    } catch {
      // Table might not exist yet
    }

    // Load strategy weights
    try {
      const { rows } = await this.pool.query(
        `SELECT key, value FROM planner_state WHERE project = '_global'`,
      );
      for (const row of rows) {
        const key = row.key as string;
        if (key === "strategy_weights") {
          const weights = row.value as Record<string, number>;
          for (const [strategy, weight] of Object.entries(weights)) {
            this.strategyWeights.set(strategy as PlanningStrategy, weight);
          }
          console.log("[Planner] Loaded strategy weights from DB");
        }
      }
    } catch {
      // Table might not exist yet
    }
  }

  // --------------------------------------------------------
  // Core: planNextActions
  // --------------------------------------------------------

  async planNextActions(
    maxActions: number,
    activeProjects?: Set<string>,
  ): Promise<SessionBrief[]> {
    const start = Date.now();
    const candidates: SessionBrief[] = [];

    const projects = await this.projectManager.listProjects();
    const active = projects.filter((p) => p.status === "active" || p.status === "in-progress");
    const budgetStatus = await this.budgetTracker.getStatus();

    if (budgetStatus.alertLevel === "exceeded") {
      console.log("Planner: budget exceeded — no actions");
      this.lastPlanDurationMs = Date.now() - start;
      this.lastPlanCycleAt = new Date().toISOString();
      return [];
    }

    // Per-project daily budget (only for project-level planning)
    const perProjectBudget = active.length > 0
      ? budgetStatus.dailyRemaining / active.length
      : 0;

    if (perProjectBudget >= 0.5) {
      for (const project of active) {
        if (activeProjects?.has(project.project)) continue;
        try {
          const briefs = await this.generateBriefsForProject(project, perProjectBudget);
          candidates.push(...briefs);
        } catch (err) {
          console.error(`Planner: failed to plan for ${project.project}:`, err);
        }
      }
    }

    // Linear-driven briefs (human-created issues from Linear)
    // DISABLED: daemon should not autonomously execute Linear issues.
    // Use POST /api/sessions/run-issue for manual triggers.
    // Strategist manages the backlog (read-only) on a daily schedule.
    if (false && this.linearClient) {
      try {
        const linearBriefs = await this.linearDrivenBriefs(budgetStatus.dailyRemaining);
        if (linearBriefs.length > 0) {
          console.log("  Planner: " + linearBriefs.length + " Linear-driven brief(s)");
        }
        candidates.push(...linearBriefs);
      } catch (err) {
        console.error("Planner: Linear-driven planning failed:", err);
      }
    }

    // Apply strategy weights to priority
    for (const brief of candidates) {
      const weight = this.strategyWeights.get(brief.strategy) ?? 1.0;
      brief.priority = Math.round(brief.priority * weight);
    }

    // Deduplicate: one brief per project (highest priority wins)
    const perProject = new Map<string, SessionBrief>();
    candidates.sort((a, b) => b.priority - a.priority);
    for (const brief of candidates) {
      if (!perProject.has(brief.projectName)) {
        perProject.set(brief.projectName, brief);
      }
    }

    const selected = Array.from(perProject.values())
      .sort((a, b) => b.priority - a.priority)
      .slice(0, maxActions);

    this.lastPlanDurationMs = Date.now() - start;
    this.lastPlanCycleAt = new Date().toISOString();

    for (const s of selected) {
      console.log(`  Planner: ${s.projectName} → ${s.agentType} (${s.strategy}, pri=${s.priority})`);
      console.log(`    ${s.objective.slice(0, 120)}`);
    }

    return selected;
  }

  // --------------------------------------------------------
  // Per-project brief generation
  // --------------------------------------------------------

  private async generateBriefsForProject(
    project: ProjectStatus,
    budgetUsd: number,
  ): Promise<SessionBrief[]> {
    const briefs: SessionBrief[] = [];

    // Engineer agents with empty backlog: skip entirely
    const agentForPhase = PHASE_TO_AGENT[project.phase];
    if (agentForPhase === "engineer" && this.backlogManager) {
      try {
        const openTickets = await this.backlogManager.list({ status: "open" });
        if (openTickets.length === 0) {
          console.log("  Planner: " + project.project + " — no open backlog tickets, skipping");
          return [];
        }
      } catch {
        // Backlog read failed — skip engineer projects to be safe
        return [];
      }
    }

    // Load KG data if available
    let claims: ClaimRow[] = [];
    let contradictions: ClaimRelationRow[] = [];
    let unsupported: ClaimRow[] = [];

    if (this.kg) {
      try {
        [claims, contradictions, unsupported] = await Promise.all([
          this.kg.getProjectClaims(project.project),
          this.kg.findContradictions(project.project),
          this.kg.getUnsupportedClaims(project.project),
        ]);
      } catch {
        // KG unavailable — proceed with phase-based planning
      }
    }

    const weakClaims = claims.filter((c) => c.confidence < 0.4);

    // Check for recent low-quality sessions (loop suppression)
    const recentEvals = this.getProjectEvaluations(project.project, 3);
    const recentAllLow = recentEvals.length >= 3 &&
      recentEvals.every((e) => e.qualityScore < 40);
    const lastAgentType = recentEvals.length > 0 ? recentEvals[0].agentType : null;

    // Strategy 1: Gap filling
    if (unsupported.length > 0 && !recentAllLow) {
      briefs.push(...this.gapFillingBriefs(project, unsupported, claims, budgetUsd));
    }

    // Strategy 2: Contradiction resolution
    if (contradictions.length > 0 && !recentAllLow) {
      briefs.push(...this.contradictionBriefs(project, contradictions, claims, budgetUsd));
    }

    // Strategy 3: Risk mitigation (weak claims in late phases)
    if (weakClaims.length > 0 && !recentAllLow) {
      briefs.push(...this.riskMitigationBriefs(project, weakClaims, claims, budgetUsd));
    }

    // Strategy 4: Deadline-driven
    briefs.push(...this.deadlineBriefs(project, claims, budgetUsd));

    // Strategy 5: Literature-driven (respond to new competing papers)
    if (this.pool && !recentAllLow) {
      const litBriefs = await this.literatureDrivenBriefs(project, claims, budgetUsd);
      briefs.push(...litBriefs);
    }

    // Strategy 6: Quality improvement (meta-review if stuck)
    if (recentAllLow) {
      briefs.push(...this.qualityImprovementBriefs(project, recentEvals, claims, budgetUsd));
    }

    // Fallback: if KG is empty and no strategies produced briefs, use phase-based
    if (briefs.length === 0 && claims.length < 5) {
      briefs.push(this.phaseBasedFallback(project, budgetUsd));
    }

    // Loop suppression: don't repeat same agent consecutively unless scored > 70
    const lastScore = recentEvals.length > 0 ? recentEvals[0].qualityScore : 100;
    if (lastAgentType && lastScore < 70) {
      for (const brief of briefs) {
        if (brief.agentType === lastAgentType) {
          brief.priority = Math.max(brief.priority - 30, 0);
        }
      }
    }

    return briefs;
  }

  // --------------------------------------------------------
  // Strategy: Gap filling
  // --------------------------------------------------------

  private gapFillingBriefs(
    project: ProjectStatus,
    unsupported: ClaimRow[],
    allClaims: ClaimRow[],
    budgetUsd: number,
  ): SessionBrief[] {
    // Pick the highest-priority unsupported claim
    const sorted = unsupported.sort((a, b) => a.confidence - b.confidence);
    const target = sorted[0];
    if (!target) return [];

    const agentType: AgentType =
      target.claimType === "hypothesis" ? "experimenter" :
      target.claimType === "result" ? "experimenter" :
      "researcher";

    const priority = Math.round(40 + (1 - target.confidence) * 30);

    return [{
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType,
      objective: `Find supporting evidence for unsupported ${target.claimType}: "${target.statement.slice(0, 150)}"`,
      context: {
        claims: this.selectRelevantClaims(allClaims, target, MAX_CLAIMS_IN_CONTEXT),
        contradictions: [],
        files: this.phaseFiles(project),
        recentDecisions: project.next_steps?.slice(0, 3) ?? [],
      },
      constraints: this.buildConstraints(agentType, budgetUsd),
      deliverables: [
        { description: "Gather evidence supporting or refuting the claim", type: "commit", verificationMethod: "commit_count" },
        { description: "Update status.yaml with findings", type: "status_update", verificationMethod: "status_changed" },
      ],
      priority,
      reasoning: `Unsupported ${target.claimType} with ${(target.confidence * 100).toFixed(0)}% confidence needs evidence. ${unsupported.length} total gaps in project.`,
      strategy: "gap_filling",
    }];
  }

  // --------------------------------------------------------
  // Strategy: Contradiction resolution
  // --------------------------------------------------------

  private contradictionBriefs(
    project: ProjectStatus,
    contradictions: ClaimRelationRow[],
    allClaims: ClaimRow[],
    budgetUsd: number,
  ): SessionBrief[] {
    const strongest = contradictions.sort((a, b) => (b.strength ?? 0) - (a.strength ?? 0))[0];
    if (!strongest) return [];

    const priority = Math.round(70 + (strongest.strength ?? 0.5) * 20);

    return [{
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType: "researcher",
      objective: `Resolve contradiction between claims ${strongest.sourceId.slice(0, 8)} and ${strongest.targetId.slice(0, 8)}. ${strongest.evidence ?? "Investigate which claim is better supported."}`,
      context: {
        claims: allClaims.filter((c) =>
          c.id === strongest.sourceId || c.id === strongest.targetId,
        ).concat(allClaims.slice(0, MAX_CLAIMS_IN_CONTEXT - 2)),
        contradictions: contradictions.slice(0, MAX_CONTRADICTIONS_IN_CONTEXT),
        files: this.phaseFiles(project),
        recentDecisions: [],
      },
      constraints: this.buildConstraints("researcher", budgetUsd, true),
      deliverables: [
        { description: "Determine which contradicting claim is correct", type: "commit", verificationMethod: "commit_count" },
        { description: "Update or remove the weaker claim", type: "claim_update", verificationMethod: "manual" },
      ],
      priority,
      reasoning: `${contradictions.length} contradiction(s) found. Strongest has strength ${(strongest.strength ?? 0).toFixed(2)}. Contradictions threaten paper coherence.`,
      strategy: "contradiction_resolution",
    }];
  }

  // --------------------------------------------------------
  // Strategy: Risk mitigation
  // --------------------------------------------------------

  private riskMitigationBriefs(
    project: ProjectStatus,
    weakClaims: ClaimRow[],
    allClaims: ClaimRow[],
    budgetUsd: number,
  ): SessionBrief[] {
    const latePhases = ["drafting", "revision", "paper-finalization", "final"];
    const isLatePhase = latePhases.includes(project.phase);
    if (!isLatePhase && weakClaims.length < 5) return [];

    const weakest = weakClaims.sort((a, b) => a.confidence - b.confidence)[0];
    if (!weakest) return [];

    const basePriority = Math.round(60 + (1 - weakest.confidence) * 30);
    const priority = isLatePhase ? Math.round(basePriority * 1.3) : basePriority;

    const agentType: AgentType = weakest.claimType === "hypothesis" || weakest.claimType === "result"
      ? "experimenter" : "researcher";

    return [{
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType,
      objective: `Strengthen weak claim (${(weakest.confidence * 100).toFixed(0)}% confidence): "${weakest.statement.slice(0, 150)}"`,
      context: {
        claims: this.selectRelevantClaims(allClaims, weakest, MAX_CLAIMS_IN_CONTEXT),
        contradictions: [],
        files: this.phaseFiles(project),
        recentDecisions: [],
      },
      constraints: this.buildConstraints(agentType, budgetUsd),
      deliverables: [
        { description: "Gather additional evidence for the weak claim", type: "commit", verificationMethod: "commit_count" },
        { description: "Update claim confidence based on findings", type: "claim_update", verificationMethod: "manual" },
      ],
      priority,
      reasoning: `${weakClaims.length} weak claims (confidence < 40%). In ${project.phase} phase${isLatePhase ? " — reviewer rejection risk" : ""}. Weakest: ${(weakest.confidence * 100).toFixed(0)}%.`,
      strategy: "risk_mitigation",
    }];
  }

  // --------------------------------------------------------
  // Strategy: Deadline-driven
  // --------------------------------------------------------

  private deadlineBriefs(
    project: ProjectStatus,
    allClaims: ClaimRow[],
    budgetUsd: number,
  ): SessionBrief[] {
    const deadline = project.metrics?.deadline_epoch;
    if (!deadline) return [];

    const now = Date.now();
    const daysUntil = (deadline - now) / (1000 * 60 * 60 * 24);
    if (daysUntil <= 0 || daysUntil > 60) return [];

    let priority: number;
    if (daysUntil <= 3) priority = 95;
    else if (daysUntil <= 7) priority = 85;
    else if (daysUntil <= 14) priority = 70;
    else priority = 50;

    const agentType: AgentType =
      project.phase === "drafting" || project.phase === "revision" || project.phase === "submission-prep" ? "writer" :
      project.phase === "paper-finalization" || project.phase === "final" ? "editor" :
      PHASE_TO_AGENT[project.phase] ?? "researcher";

    const objective = daysUntil <= 7
      ? `URGENT: ${Math.round(daysUntil)} days to deadline. Focus on completing ${project.phase} phase deliverables.`
      : `Deadline in ${Math.round(daysUntil)} days. Progress ${project.phase} phase toward completion.`;

    return [{
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType,
      objective,
      context: {
        claims: allClaims.slice(0, MAX_CLAIMS_IN_CONTEXT),
        contradictions: [],
        files: this.phaseFiles(project),
        recentDecisions: project.next_steps?.slice(0, 5) ?? [],
      },
      constraints: this.buildConstraints(agentType, budgetUsd),
      deliverables: [
        { description: `Make progress on ${project.phase} phase`, type: "commit", verificationMethod: "commit_count" },
        { description: "Update status.yaml with progress", type: "status_update", verificationMethod: "status_changed" },
      ],
      priority,
      reasoning: `Venue deadline in ${Math.round(daysUntil)} days. Current phase: ${project.phase}.`,
      strategy: "deadline_driven",
    }];
  }

  // --------------------------------------------------------
  // Strategy: Literature-driven (respond to new competing papers)
  // --------------------------------------------------------

  private async literatureDrivenBriefs(
    project: ProjectStatus,
    allClaims: ClaimRow[],
    budgetUsd: number,
  ): Promise<SessionBrief[]> {
    if (!this.pool) return [];

    try {
      // Check if lit_alerts table exists
      const { rows: tableCheck } = await this.pool.query(
        `SELECT EXISTS (
          SELECT FROM information_schema.tables WHERE table_name = 'lit_alerts'
        ) AS exists`,
      );
      if (!tableCheck[0]?.exists) return [];

      // Find unacknowledged high/critical alerts
      const { rows: alerts } = await this.pool.query(
        `SELECT a.priority, a.relation, a.similarity,
                p.title, p.authors, p.year, p.url
         FROM lit_alerts a
         JOIN lit_papers p ON p.id = a.paper_id
         WHERE a.project = $1 AND a.acknowledged = FALSE
           AND a.priority IN ('high', 'critical')
         ORDER BY a.created_at DESC
         LIMIT 5`,
        [project.project],
      );

      if (alerts.length === 0) return [];

      const alertSummary = alerts.map((a: Record<string, unknown>) => {
        const authors = Array.isArray(a.authors) ? a.authors : [];
        return `"${a.title}" by ${authors[0] ?? "Unknown"} (${a.relation}, sim=${a.similarity ?? "keyword"})`;
      }).join("; ");

      const hasCritical = alerts.some((a: Record<string, unknown>) => a.priority === "critical");
      const priority = hasCritical ? 90 : 80;

      return [{
        id: randomUUID().slice(0, 8),
        projectName: project.project,
        agentType: "scout" as AgentType,
        objective: `Assess ${alerts.length} new competing paper(s): ${alertSummary}. ` +
          "Determine overlap with our contribution, identify differentiation opportunities, " +
          "and recommend positioning adjustments.",
        context: {
          claims: allClaims.slice(0, MAX_CLAIMS_IN_CONTEXT),
          contradictions: [],
          files: ["paper/main.tex", "BRIEF.md", "status.yaml"],
          recentDecisions: project.next_steps?.slice(0, 3) ?? [],
          supplementary: `Literature alerts: ${alertSummary}`,
        },
        constraints: this.buildConstraints("scout", budgetUsd),
        deliverables: [
          { description: "Assess relevance and overlap of detected papers", type: "analysis", verificationMethod: "manual" },
          { description: "Update status.yaml with literature findings", type: "status_update", verificationMethod: "status_changed" },
        ],
        priority,
        reasoning: `${alerts.length} high-priority literature alert(s) detected. Scout session needed to assess competitive landscape.`,
        strategy: "literature_driven",
      }];
    } catch (err) {
      console.error(`Planner: literature strategy failed for ${project.project}:`, err);
      return [];
    }
  }

  // --------------------------------------------------------
  // Strategy: Linear-driven (human-created issues from Linear)
  // --------------------------------------------------------

  private async linearDrivenBriefs(budgetUsd: number): Promise<SessionBrief[]> {
    if (!this.linearClient) return [];

    try {
      const todoIssues = await this.linearClient.getTodoIssues();
      if (todoIssues.length === 0) return [];

      // Filter out blocked issues
      const unblockedIssues = [];
      for (const issue of todoIssues) {
        try {
          if (!(await this.linearClient.isBlocked(issue.id))) {
            unblockedIssues.push(issue);
          } else {
            console.log("  [Planner] Skipping blocked issue: " + issue.identifier);
          }
        } catch {
          unblockedIssues.push(issue); // Don't block on relation check failure
        }
      }

      const briefs: SessionBrief[] = [];

      for (const issue of unblockedIssues) {
        // Map Linear project to DW project
        const dwProject = issue.project
          ? LinearClient.projectNameToDW(issue.project.name)
          : null;
        if (!dwProject) continue;

        const mapped = this.linearClient.issueToBrief(issue, dwProject);

        briefs.push({
          id: randomUUID().slice(0, 8),
          projectName: mapped.projectName,
          agentType: mapped.agentType as AgentType,
          objective: mapped.objective,
          context: {
            claims: [],
            contradictions: [],
            files: dwProject === "_platform"
              ? ["orchestrator/src/"]
              : [`projects/${dwProject}/status.yaml`, `projects/${dwProject}/BRIEF.md`],
            recentDecisions: [],
            supplementary: mapped.supplementary,
          },
          constraints: this.buildConstraints(mapped.agentType as AgentType, budgetUsd),
          deliverables: [
            { description: issue.title, type: "commit", verificationMethod: "commit_count" },
          ],
          priority: mapped.priority,
          reasoning: `Human-created Linear issue ${mapped.linearIdentifier}: "${issue.title}" (priority ${issue.priority}).`,
          strategy: "linear_driven",
        });
      }

      return briefs;
    } catch (err) {
      console.error("Planner: Linear query failed:", err);
      return [];
    }
  }

  // --------------------------------------------------------
  // Linear quality gate: retry + critic review tracking
  // --------------------------------------------------------

  async shouldRetry(projectName: string, linearIdentifier: string, quality: number): Promise<boolean> {
    if (quality >= 40) return false;
    if (!this.pool) return false;
    try {
      const { rows } = await this.pool.query(
        "SELECT value FROM planner_state WHERE project = $1 AND key = $2",
        [projectName, "retry:" + linearIdentifier],
      );
      if (rows.length === 0) return true; // first retry
      const data = typeof rows[0].value === "string" ? JSON.parse(rows[0].value) : rows[0].value;
      const attempts = (data as Record<string, unknown>).attempts as number || 1;
      return attempts < 3; // allow up to 3 attempts total
    } catch { return false; }
  }

  async markRetried(projectName: string, linearIdentifier: string, quality: number): Promise<void> {
    if (!this.pool) return;
    try {
      // Get current attempt count
      const { rows } = await this.pool.query(
        "SELECT value FROM planner_state WHERE project = $1 AND key = $2",
        [projectName, "retry:" + linearIdentifier],
      );
      const prev = rows.length > 0
        ? (typeof rows[0].value === "string" ? JSON.parse(rows[0].value) : rows[0].value)
        : {};
      const prevAttempts = (prev as Record<string, unknown>).attempts as number || 0;

      await this.pool.query(
        `INSERT INTO planner_state (project, key, value, updated_at) VALUES ($1, $2, $3, NOW())
         ON CONFLICT (project, key) DO UPDATE SET value = $3, updated_at = NOW()`,
        [projectName, "retry:" + linearIdentifier,
         JSON.stringify({ attempts: prevAttempts + 1, lastQuality: quality, ts: Date.now() })],
      );
    } catch { /* ignore */ }
  }

  async storePendingCriticReview(projectName: string, linearIssueId: string, linearIdentifier: string): Promise<void> {
    if (!this.pool) return;
    await this.pool.query(
      `INSERT INTO planner_state (project, key, value, updated_at) VALUES ($1, 'pending_critic_review', $2, NOW())
       ON CONFLICT (project, key) DO UPDATE SET value = $2, updated_at = NOW()`,
      [projectName, JSON.stringify({ linearIssueId, linearIdentifier })],
    ).catch(() => {});
  }

  async getPendingCriticReview(projectName: string): Promise<{ linearIssueId: string; linearIdentifier: string } | null> {
    if (!this.pool) return null;
    try {
      const { rows } = await this.pool.query(
        "SELECT value FROM planner_state WHERE project = $1 AND key = 'pending_critic_review'",
        [projectName],
      );
      if (rows.length === 0) return null;
      return typeof rows[0].value === "string" ? JSON.parse(rows[0].value) : rows[0].value;
    } catch { return null; }
  }

  async clearPendingCriticReview(projectName: string): Promise<void> {
    if (!this.pool) return;
    await this.pool.query(
      "DELETE FROM planner_state WHERE project = $1 AND key = 'pending_critic_review'",
      [projectName],
    ).catch(() => {});
  }

  // --------------------------------------------------------
  // Strategy: Quality improvement (meta-review when stuck)
  // --------------------------------------------------------

  private qualityImprovementBriefs(
    project: ProjectStatus,
    recentEvals: SessionEvaluation[],
    allClaims: ClaimRow[],
    budgetUsd: number,
  ): SessionBrief[] {
    const avgScore = recentEvals.reduce((s, e) => s + e.qualityScore, 0) / recentEvals.length;
    const failedStrategies = [...new Set(recentEvals.map((e) => e.strategy))];
    const agentType: AgentType = PHASE_TO_AGENT[project.phase] ?? "researcher";
    if (!PHASE_TO_AGENT[project.phase]) {
      console.warn(`[Planner] Unknown phase "${project.phase}" for ${project.project} — falling back to researcher. Add this phase to PHASE_TO_AGENT in session-runner.ts.`);
    }

    return [{
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType,
      objective: `Quality improvement: Last ${recentEvals.length} sessions scored avg ${avgScore.toFixed(0)}/100. Strategies tried: ${failedStrategies.join(", ")}. Review project state, identify what's blocking progress, and execute concrete work appropriate to the current phase (${project.phase}). Do NOT repeat previous approaches.`,
      context: {
        claims: allClaims.slice(0, 10),
        contradictions: [],
        files: [`projects/${project.project}/status.yaml`, `projects/${project.project}/BRIEF.md`],
        recentDecisions: project.next_steps ?? [],
        supplementary: `Recent failed sessions:\n${recentEvals.map((e) => `- ${e.agentType}/${e.strategy}: score ${e.qualityScore}, objective: ${e.objective.slice(0, 80)}`).join("\n")}`,
      },
      constraints: this.buildConstraints(agentType, budgetUsd),
      deliverables: [
        { description: "Update status.yaml with revised next_steps and current_focus", type: "status_update", verificationMethod: "status_changed" },
        { description: "Identify concrete, actionable work items", type: "commit", verificationMethod: "commit_count" },
      ],
      priority: 45,
      reasoning: `Project appears stuck. ${recentEvals.length} consecutive sessions with quality < 40. Needs strategic reassessment before more agent work.`,
      strategy: "quality_improvement",
    }];
  }

  // --------------------------------------------------------
  // Fallback: phase-based (when KG is empty)
  // --------------------------------------------------------

  private phaseBasedFallback(project: ProjectStatus, budgetUsd: number): SessionBrief {
    const agentType: AgentType = PHASE_TO_AGENT[project.phase] ?? "researcher";
    if (!PHASE_TO_AGENT[project.phase]) {
      console.warn(`[Planner] Unknown phase "${project.phase}" for ${project.project} — falling back to researcher. Add this phase to PHASE_TO_AGENT in session-runner.ts.`);
    }

    const PHASE_OBJECTIVES: Record<string, string> = {
      "submission-prep": "Polish paper for submission: integrate pending results, check formatting, verify anonymization, review figures and tables",
      "revision": "Revise paper based on reviews: address reviewer comments, strengthen weak sections",
      "paper-finalization": "Final paper polish: copyedit, verify references, check page limits",
      "analysis": "Run analysis pipeline and interpret results",
      "empirical-evaluation": "Execute evaluation experiments and collect data",
    };

    const objective = PHASE_OBJECTIVES[project.phase]
      ?? `Progress ${project.phase} phase. Focus: ${project.current_focus || project.next_steps?.[0] || "continue current work"}.`;

    // For experimenter sessions in empirical phases, remind about pre-registration requirement
    const supplementary = agentType === "experimenter"
      ? "NOTE: Experiments estimated at >$2 require a pre-registration spec (experiments/<name>/spec.yaml) before execution. " +
        "Check if a spec already exists. If not, create one using the template at shared/templates/experiment/spec.yaml. " +
        "The spec must be reviewed by the critic before the full experiment can proceed."
      : undefined;

    return {
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType,
      objective,
      context: {
        claims: [],
        contradictions: [],
        files: this.phaseFiles(project),
        recentDecisions: project.next_steps?.slice(0, 3) ?? [],
        supplementary,
      },
      constraints: this.buildConstraints(agentType, budgetUsd),
      deliverables: [
        { description: "Make substantive progress on current phase", type: "commit", verificationMethod: "commit_count" },
        { description: "Update status.yaml", type: "status_update", verificationMethod: "status_changed" },
      ],
      priority: 20,
      reasoning: `Knowledge graph sparse (< 5 claims). Using phase-based scheduling: ${project.phase} → ${agentType}.`,
      strategy: "gap_filling",
    };
  }

  // --------------------------------------------------------
  // Post-session evaluation
  // --------------------------------------------------------

  async evaluateSession(
    brief: SessionBrief,
    result: SessionResult,
    signals?: SessionSignals,
  ): Promise<SessionEvaluation> {
    let deliverablesMet = 0;
    for (const d of brief.deliverables) {
      if (this.checkDeliverable(d, result, signals)) deliverablesMet++;
    }

    let score = 0;

    // Deliverables met: up to 40 points
    const ratio = brief.deliverables.length > 0
      ? deliverablesMet / brief.deliverables.length : 0;
    score += Math.round(ratio * 40);

    // Session completed: 15 points
    if (result.status === "completed") score += 15;
    else if (result.status === "timeout") score += 5;

    // Commits: up to 10 points
    score += Math.min(result.commitsCreated.length * 3, 10);

    // Status advanced: 15 points
    if (signals?.statusYamlChanged) score += 15;

    // Cost efficiency: up to 20 points
    if (result.commitsCreated.length > 0) {
      const cpc = result.costUsd / result.commitsCreated.length;
      if (cpc < 1) score += 20;
      else if (cpc < 3) score += 15;
      else if (cpc < 5) score += 10;
      else score += 5;
    }

    score = Math.min(score, 100);

    const evaluation: SessionEvaluation = {
      sessionId: result.sessionId,
      briefId: brief.id,
      project: brief.projectName,
      agentType: brief.agentType,
      strategy: brief.strategy,
      objective: brief.objective,
      deliverablesMet,
      deliverablesTotal: brief.deliverables.length,
      qualityScore: score,
      reasoning: `${deliverablesMet}/${brief.deliverables.length} deliverables met. ${result.commitsCreated.length} commits, $${result.costUsd.toFixed(2)} cost.`,
      costUsd: result.costUsd,
      durationMs: result.durationMs,
      createdAt: new Date().toISOString(),
    };

    // Persist
    this.evaluationHistory.push(evaluation);
    if (this.evaluationHistory.length > 100) this.evaluationHistory.shift();
    await this.persistEvaluation(evaluation);

    // Update strategy weights
    this.updateStrategyWeight(brief.strategy, score);

    return evaluation;
  }

  private checkDeliverable(d: Deliverable, result: SessionResult, signals?: SessionSignals): boolean {
    switch (d.verificationMethod) {
      case "commit_count": return result.commitsCreated.length > 0;
      case "status_changed": return signals?.statusYamlChanged ?? false;
      case "file_exists": return result.commitsCreated.length > 0;
      case "manual": return result.status === "completed";
      default: return false;
    }
  }

  private async persistEvaluation(evaluation: SessionEvaluation): Promise<void> {
    if (!this.pool) return;
    try {
      await this.pool.query(
        `INSERT INTO session_evaluations
         (session_id, brief_id, project, agent_type, strategy, objective,
          deliverables_met, deliverables_total, quality_score, reasoning, cost_usd, duration_ms)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`,
        [
          evaluation.sessionId, evaluation.briefId, evaluation.project,
          evaluation.agentType, evaluation.strategy, evaluation.objective,
          evaluation.deliverablesMet, evaluation.deliverablesTotal,
          evaluation.qualityScore, evaluation.reasoning,
          evaluation.costUsd, evaluation.durationMs,
        ],
      );
    } catch {
      // Non-fatal
    }
  }

  private updateStrategyWeight(strategy: PlanningStrategy, score: number): void {
    const current = this.strategyWeights.get(strategy) ?? 1.0;
    const adjustment = score / 50; // score 50 = neutral, 100 = 2x, 0 = 0x
    const updated = STRATEGY_WEIGHT_ALPHA * adjustment + (1 - STRATEGY_WEIGHT_ALPHA) * current;
    this.strategyWeights.set(strategy, Math.max(MIN_WEIGHT, Math.min(MAX_WEIGHT, updated)));
    this.persistStrategyWeights().catch(() => {});
  }

  private async persistStrategyWeights(): Promise<void> {
    if (!this.pool) return;
    const weights = Object.fromEntries(this.strategyWeights);
    await this.pool.query(
      `INSERT INTO planner_state (project, key, value, updated_at)
       VALUES ('_global', 'strategy_weights', $1, NOW())
       ON CONFLICT (project, key) DO UPDATE SET value = $1, updated_at = NOW()`,
      [JSON.stringify(weights)],
    );
  }

  // --------------------------------------------------------
  // State and insights (for API)
  // --------------------------------------------------------

  async getState(): Promise<PlannerState> {
    const state: PlannerState = {
      enabled: true,
      lastPlanCycleAt: this.lastPlanCycleAt,
      lastPlanDurationMs: this.lastPlanDurationMs,
      recentEvaluations: this.evaluationHistory.slice(-10),
      strategyWeights: Object.fromEntries(this.strategyWeights) as Record<PlanningStrategy, number>,
    };

    return state;
  }

  async getProjectInsight(projectName: string): Promise<ProjectInsight | null> {
    if (!this.kg) return null;

    try {
      const [claims, contradictions, unsupported] = await Promise.all([
        this.kg.getProjectClaims(projectName),
        this.kg.findContradictions(projectName),
        this.kg.getUnsupportedClaims(projectName),
      ]);

      const weakClaims = claims.filter((c) => c.confidence < 0.4);
      const recentEvals = this.getProjectEvaluations(projectName, 1);

      let suggestedAction = "Continue current phase work";
      if (contradictions.length > 0) suggestedAction = "Resolve contradictions";
      else if (unsupported.length > 5) suggestedAction = "Fill evidence gaps";
      else if (weakClaims.length > 3) suggestedAction = "Strengthen weak claims";

      return {
        project: projectName,
        gapCount: unsupported.length,
        contradictionCount: contradictions.length,
        unsupportedClaimCount: unsupported.length,
        weakClaimCount: weakClaims.length,
        totalClaims: claims.length,
        lastSessionQuality: recentEvals[0]?.qualityScore ?? null,
        suggestedAction,
      };
    } catch {
      return null;
    }
  }

  async getRecentEvaluations(limit: number = 20): Promise<SessionEvaluation[]> {
    if (this.pool) {
      try {
        const { rows } = await this.pool.query(
          `SELECT session_id, brief_id, project, agent_type, strategy, objective,
                  deliverables_met, deliverables_total, quality_score, reasoning,
                  cost_usd, duration_ms, created_at
           FROM session_evaluations ORDER BY created_at DESC LIMIT $1`,
          [limit],
        );
        return rows.map((r: Record<string, unknown>) => ({
          sessionId: r.session_id as string,
          briefId: r.brief_id as string,
          project: r.project as string,
          agentType: r.agent_type as string,
          strategy: r.strategy as PlanningStrategy,
          objective: r.objective as string,
          deliverablesMet: r.deliverables_met as number,
          deliverablesTotal: r.deliverables_total as number,
          qualityScore: r.quality_score as number,
          reasoning: r.reasoning as string,
          costUsd: r.cost_usd as number,
          durationMs: r.duration_ms as number,
          createdAt: (r.created_at as Date).toISOString(),
        }));
      } catch {
        // Fall through to in-memory
      }
    }
    return this.evaluationHistory.slice(-limit);
  }

  // --------------------------------------------------------
  // Helpers
  // --------------------------------------------------------

  private getProjectEvaluations(project: string, limit: number): SessionEvaluation[] {
    return this.evaluationHistory
      .filter((e) => e.project === project)
      .slice(-limit);
  }

  private selectRelevantClaims(allClaims: ClaimRow[], target: ClaimRow, limit: number): ClaimRow[] {
    // Put the target claim first, then fill with others
    const result = [target];
    for (const c of allClaims) {
      if (c.id !== target.id && result.length < limit) {
        result.push(c);
      }
    }
    return result;
  }

  private phaseFiles(project: ProjectStatus): string[] {
    const base = `projects/${project.project}`;
    const files = [`${base}/status.yaml`];

    switch (project.phase) {
      case "research":
      case "literature-review":
        files.push(`${base}/notes/`, `${base}/literature/`);
        break;
      case "empirical-evaluation":
      case "analysis":
        files.push(`${base}/experiments/`, `${base}/benchmarks/`);
        break;
      case "drafting":
      case "revision":
      case "paper-finalization":
      case "final":
        files.push(`${base}/paper/`);
        break;
    }
    return files;
  }

  private buildConstraints(
    agentType: AgentType,
    budgetUsd: number,
    highStakes: boolean = false,
  ): BriefConstraints {
    // Tiered model selection:
    // Tier 1 — Opus ($15/$75): theory, first-draft writing, final critic review
    // Tier 2 — Sonnet ($3/$15): research, engineering, experiment design, revisions
    // Tier 3 — Haiku ($0.80/$4): scanning, auditing, script execution, polish

    let model = "claude-sonnet-4-6"; // Tier 2 default
    let maxBudget = 5;

    // Tier 1 — Opus for the work where quality matters most
    if (agentType === "theorist") {
      model = "claude-opus-4-6";
      maxBudget = 15;
    }
    if (agentType === "writer") {
      model = "claude-opus-4-6"; // first drafts set the quality bar
      maxBudget = 15;
    }
    if (agentType === "critic" && highStakes) {
      model = "claude-opus-4-6"; // final paper review
      maxBudget = 10;
    }

    // Tier 3 — Haiku for high-volume, low-reasoning tasks
    if (agentType === "scout" || agentType === "strategist" || agentType === "editor") {
      model = "claude-haiku-4-5-20251001";
      maxBudget = 2;
    }

    // Budget-aware downgrades
    if (budgetUsd < 10 && model.includes("opus")) {
      model = "claude-sonnet-4-6"; // can't afford Opus, use Sonnet
      maxBudget = 5;
    }
    if (budgetUsd < 3) {
      model = "claude-haiku-4-5-20251001"; // emergency: everything on Haiku
      maxBudget = 2;
    }

    return {
      maxTurns: agentType === "editor" ? 20 : agentType === "experimenter" ? 80 : 40,
      maxDurationMs: 45 * 60 * 1000,
      maxBudgetUsd: Math.min(budgetUsd, maxBudget),
      model,
    };
  }
}
