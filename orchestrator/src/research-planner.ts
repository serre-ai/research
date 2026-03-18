import { randomUUID } from "node:crypto";
import type pg from "pg";
import type { ProjectManager, ProjectStatus } from "./project-manager.js";
import type { KnowledgeGraph, ClaimRow, ClaimRelationRow } from "./knowledge-graph.js";
import type { BudgetTracker } from "./budget-tracker.js";
import type { BacklogManager } from "./backlog.js";
import { type AgentType, PHASE_TO_AGENT, type SessionResult } from "./session-runner.js";
import type { SessionSignals } from "./session-manager.js";

// ============================================================
// Types
// ============================================================

export type PlanningStrategy =
  | "gap_filling"
  | "contradiction_resolution"
  | "risk_mitigation"
  | "deadline_driven"
  | "quality_improvement"
  | "collective_action";

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
  "gap_filling": 1.0,
  "quality_improvement": 0.9,
  "collective_action": 1.1,
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
  ) {
    this.pool = pool;
    this.projectManager = projectManager;
    this.kg = kg;
    this.budgetTracker = budgetTracker;
    this.backlogManager = backlogManager ?? null;
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
    const active = projects.filter((p) => p.status === "active");
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

    // Collective actions (forum signals, triggers, overdue rituals)
    if (this.pool) {
      try {
        const collectiveBriefs = await this.collectiveActionBriefs(budgetStatus.dailyRemaining);
        if (collectiveBriefs.length > 0) {
          console.log("  Planner: " + collectiveBriefs.length + " collective action(s)");
        }
        candidates.push(...collectiveBriefs);
      } catch (err) {
        console.error("Planner: collective action planning failed:", err);
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

    // Strategy 5: Quality improvement (meta-review if stuck)
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
    if (daysUntil <= 0 || daysUntil > 28) return [];

    let priority: number;
    if (daysUntil <= 3) priority = 95;
    else if (daysUntil <= 7) priority = 85;
    else if (daysUntil <= 14) priority = 70;
    else priority = 50;

    const agentType: AgentType =
      project.phase === "drafting" || project.phase === "revision" ? "writer" :
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

    return [{
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType: "researcher",
      objective: `Meta-review: Last ${recentEvals.length} sessions scored avg ${avgScore.toFixed(0)}/100. Strategies tried: ${failedStrategies.join(", ")}. Assess project state and recommend concrete next steps. Do NOT repeat previous approaches.`,
      context: {
        claims: allClaims.slice(0, 10),
        contradictions: [],
        files: [`projects/${project.project}/status.yaml`, `projects/${project.project}/BRIEF.md`],
        recentDecisions: project.next_steps ?? [],
        supplementary: `Recent failed sessions:\n${recentEvals.map((e) => `- ${e.agentType}/${e.strategy}: score ${e.qualityScore}, objective: ${e.objective.slice(0, 80)}`).join("\n")}`,
      },
      constraints: this.buildConstraints("researcher", budgetUsd),
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
    const agentType = PHASE_TO_AGENT[project.phase] ?? "researcher" as AgentType;

    return {
      id: randomUUID().slice(0, 8),
      projectName: project.project,
      agentType,
      objective: `Progress ${project.phase} phase. Focus: ${project.current_focus || project.next_steps?.[0] || "continue current work"}.`,
      context: {
        claims: [],
        contradictions: [],
        files: this.phaseFiles(project),
        recentDecisions: project.next_steps?.slice(0, 3) ?? [],
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
  // Strategy: Collective action (forum, governance, rituals)
  // --------------------------------------------------------

  private async collectiveActionBriefs(budgetUsd: number): Promise<SessionBrief[]> {
    if (!this.pool) return [];
    const briefs: SessionBrief[] = [];
    const budget = Math.min(budgetUsd, 2);

    // 1. Un-acked triggers
    try {
      const { rows: triggers } = await this.pool.query(
        `SELECT tl.id, tl.agent, tl.trigger_type, tl.context
         FROM trigger_log tl WHERE tl.acked_at IS NULL
         ORDER BY tl.created_at ASC LIMIT 5`,
      );
      for (const trigger of triggers) {
        const ctx = trigger.context as Record<string, unknown>;
        const agentType = this.triggerToAgent(trigger.trigger_type as string);
        briefs.push({
          id: randomUUID().slice(0, 8),
          projectName: "openclaw-collective",
          agentType,
          objective: `Process trigger: ${trigger.trigger_type}. ${ctx.title ?? ""} (trigger #${trigger.id}). Respond appropriately via forum post or governance action.`,
          context: {
            claims: [],
            contradictions: [],
            files: [],
            recentDecisions: [],
            supplementary: `Trigger type: ${trigger.trigger_type}\nTarget agent: ${trigger.agent}\nContext: ${JSON.stringify(ctx)}`,
          },
          constraints: { maxTurns: 15, maxDurationMs: 10 * 60 * 1000, maxBudgetUsd: budget, model: "claude-haiku-4-5-20251001" },
          deliverables: [
            { description: "Respond to the trigger via API call", type: "commit", verificationMethod: "manual" },
          ],
          priority: 55,
          reasoning: `Un-acked trigger (${trigger.trigger_type}) waiting since creation. Agent ${trigger.agent} should respond.`,
          strategy: "collective_action",
        });
      }
    } catch { /* triggers table may not exist */ }

    // 2. Forum signals with high scores and no replies
    try {
      const { rows: signals } = await this.pool.query(
        `SELECT fp.thread_id, fp.title, fp.author, fp.body
         FROM forum_posts fp
         WHERE fp.parent_id IS NULL
           AND fp.post_type = 'signal'
           AND fp.status = 'open'
           AND NOT EXISTS (
             SELECT 1 FROM forum_posts fp2
             WHERE fp2.thread_id = fp.thread_id AND fp2.parent_id IS NOT NULL
             AND fp2.created_at > NOW() - INTERVAL '24 hours'
           )
         ORDER BY fp.created_at ASC LIMIT 3`,
      );
      for (const signal of signals) {
        // Determine which project this signal relates to
        const relatedProject = await this.findRelatedProject(signal.body as string);
        briefs.push({
          id: randomUUID().slice(0, 8),
          projectName: relatedProject ?? "openclaw-collective",
          agentType: "researcher",
          objective: `Investigate forum signal from ${signal.author}: "${(signal.title as string).slice(0, 100)}". Research the referenced paper/finding and post a substantive reply to thread #${signal.thread_id}.`,
          context: {
            claims: [],
            contradictions: [],
            files: relatedProject ? [`projects/${relatedProject}/status.yaml`] : [],
            recentDecisions: [],
            supplementary: `Forum signal:\nTitle: ${signal.title}\nAuthor: ${signal.author}\nBody: ${signal.body}`,
          },
          constraints: { maxTurns: 25, maxDurationMs: 20 * 60 * 1000, maxBudgetUsd: budget, model: "claude-sonnet-4-6" },
          deliverables: [
            { description: "Research the signal topic", type: "commit", verificationMethod: "commit_count" },
            { description: "Post a reply to the forum thread", type: "commit", verificationMethod: "manual" },
          ],
          priority: 45,
          reasoning: `Forum signal "${(signal.title as string).slice(0, 60)}" has no recent replies. Collective should respond.`,
          strategy: "collective_action",
        });
      }
    } catch { /* forum table may not exist */ }

    // 3. Overdue rituals
    try {
      const { rows: overdue } = await this.pool.query(
        `SELECT id, ritual_type, scheduled_for, facilitator
         FROM rituals
         WHERE status = 'scheduled' AND scheduled_for < NOW()
         ORDER BY scheduled_for ASC LIMIT 2`,
      );
      for (const ritual of overdue) {
        briefs.push({
          id: randomUUID().slice(0, 8),
          projectName: "openclaw-collective",
          agentType: "strategist",
          objective: `Facilitate overdue ${ritual.ritual_type} ritual (scheduled for ${(ritual.scheduled_for as Date).toISOString().slice(0, 16)}). Post facilitation thread to forum, collect inputs from agents, summarize outcomes.`,
          context: {
            claims: [],
            contradictions: [],
            files: [],
            recentDecisions: [],
            supplementary: `Ritual: ${ritual.ritual_type}\nScheduled: ${ritual.scheduled_for}\nFacilitator: ${ritual.facilitator ?? "sage"}`,
          },
          constraints: { maxTurns: 20, maxDurationMs: 15 * 60 * 1000, maxBudgetUsd: budget, model: "claude-sonnet-4-6" },
          deliverables: [
            { description: "Post ritual facilitation to forum", type: "commit", verificationMethod: "manual" },
          ],
          priority: 40,
          reasoning: `${ritual.ritual_type} ritual is overdue (was scheduled for ${(ritual.scheduled_for as Date).toISOString().slice(0, 10)}).`,
          strategy: "collective_action",
        });
      }
    } catch { /* rituals table may not exist */ }

    // 4. Open proposals with enough votes for auto-resolution
    try {
      const { rows: resolvable } = await this.pool.query(
        `SELECT fp.thread_id, fp.title, fp.author,
                COUNT(v.id) AS vote_count,
                COUNT(CASE WHEN v.position = 'support' THEN 1 END) AS support_count,
                COUNT(CASE WHEN v.position = 'oppose' THEN 1 END) AS oppose_count
         FROM forum_posts fp
         JOIN votes v ON v.thread_id = fp.thread_id
         WHERE fp.parent_id IS NULL
           AND fp.status = 'open'
           AND fp.post_type = 'proposal'
           AND fp.created_at < NOW() - INTERVAL '24 hours'
         GROUP BY fp.thread_id, fp.title, fp.author
         HAVING COUNT(v.id) >= 3 AND COUNT(CASE WHEN v.position = 'oppose' THEN 1 END) = 0`,
      );
      for (const proposal of resolvable) {
        // Auto-resolve directly — no session needed
        await this.autoResolveProposal(proposal.thread_id as string, proposal.title as string, parseInt(proposal.support_count as string));
      }
    } catch { /* votes/governance tables may not exist */ }

    return briefs;
  }

  /** Auto-resolve a proposal that has enough unanimous votes. */
  private async autoResolveProposal(threadId: string, title: string, votes: number): Promise<void> {
    if (!this.pool) return;
    try {
      // Check if already in governance
      const { rows: existing } = await this.pool.query(
        `SELECT id FROM governance WHERE thread_id = $1`,
        [threadId],
      );
      if (existing.length > 0) return; // Already resolved

      // Create governance entry
      await this.pool.query(
        `INSERT INTO governance (proposer, title, proposal, proposal_type, status, thread_id, votes_for, votes_against, votes_abstain, resolved_at)
         SELECT fp.author, fp.title, fp.body, 'process', 'accepted', fp.thread_id, $2, 0, 0, NOW()
         FROM forum_posts fp WHERE fp.thread_id = $1 AND fp.parent_id IS NULL`,
        [threadId, votes],
      );

      // Update forum post status
      await this.pool.query(
        `UPDATE forum_posts SET status = 'resolved' WHERE thread_id = $1 AND parent_id IS NULL`,
        [threadId],
      );

      console.log(`  Planner: auto-resolved proposal "${title}" (${votes} unanimous votes)`);
    } catch (err) {
      console.error(`  Planner: failed to auto-resolve proposal "${title}":`, err);
    }
  }

  /** Map trigger types to the agent that should handle them. */
  private triggerToAgent(triggerType: string): AgentType {
    if (triggerType.includes("governance") || triggerType.includes("unanimous")) return "strategist";
    if (triggerType.includes("stalled")) return "researcher";
    if (triggerType.includes("mention")) return "researcher";
    if (triggerType.includes("ritual")) return "strategist";
    return "researcher";
  }

  /** Find which project a forum signal relates to via KG semantic search. */
  private async findRelatedProject(text: string): Promise<string | null> {
    if (!this.kg) return null;
    try {
      const matches = await this.kg.query(text, { limit: 1, threshold: 0.3 });
      return matches.length > 0 ? matches[0].project : null;
    } catch {
      return null;
    }
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

  async getState(): Promise<PlannerState & { collective?: Record<string, number> }> {
    const state: PlannerState & { collective?: Record<string, number> } = {
      enabled: true,
      lastPlanCycleAt: this.lastPlanCycleAt,
      lastPlanDurationMs: this.lastPlanDurationMs,
      recentEvaluations: this.evaluationHistory.slice(-10),
      strategyWeights: Object.fromEntries(this.strategyWeights) as Record<PlanningStrategy, number>,
    };

    // Add collective state summary
    if (this.pool) {
      try {
        const [triggers, signals, overdue, openProposals] = await Promise.all([
          this.pool.query("SELECT COUNT(*) AS cnt FROM trigger_log WHERE acked_at IS NULL"),
          this.pool.query("SELECT COUNT(*) AS cnt FROM forum_posts WHERE parent_id IS NULL AND post_type = 'signal' AND status = 'open'"),
          this.pool.query("SELECT COUNT(*) AS cnt FROM rituals WHERE status = 'scheduled' AND scheduled_for < NOW()"),
          this.pool.query("SELECT COUNT(*) AS cnt FROM forum_posts WHERE parent_id IS NULL AND post_type = 'proposal' AND status = 'open'"),
        ]);
        state.collective = {
          unackedTriggers: parseInt(triggers.rows[0].cnt),
          openSignals: parseInt(signals.rows[0].cnt),
          overdueRituals: parseInt(overdue.rows[0].cnt),
          openProposals: parseInt(openProposals.rows[0].cnt),
        };
      } catch { /* non-critical */ }
    }

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
    // Model selection based on agent type and stakes
    let model = "claude-sonnet-4-6";
    if (highStakes || agentType === "critic") {
      model = "claude-sonnet-4-6"; // Opus too expensive for routine; use Sonnet even for high-stakes
    }
    if (agentType === "scout") {
      model = "claude-haiku-4-5-20251001";
    }

    // Budget-aware downgrade
    if (budgetUsd < 3) {
      model = "claude-haiku-4-5-20251001";
    }

    return {
      maxTurns: agentType === "editor" ? 20 : 40,
      maxDurationMs: 45 * 60 * 1000,
      maxBudgetUsd: Math.min(budgetUsd, 5),
      model,
    };
  }
}
