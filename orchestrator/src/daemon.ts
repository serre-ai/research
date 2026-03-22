import { writeFile, readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import pg from "pg";
import { ProjectManager, ProjectStatus } from "./project-manager.js";
import { SessionManager, type Session, type SessionSignals } from "./session-manager.js";
import { type AgentType, type SessionResult, PHASE_TO_AGENT } from "./session-runner.js";
import { GitEngine } from "./git-engine.js";
import { BudgetTracker } from "./budget-tracker.js";
import { ActivityLogger } from "./logger.js";
import { Notifier } from "./notifier.js";
import { EvalJobManager } from "./eval-manager.js";
import { BacklogManager, type BacklogTicket } from "./backlog.js";
import { DigestStore, type DailyDigest } from "./digest-store.js";
import { CostPoller } from "./cost-poller.js";
import { KnowledgeGraph } from "./knowledge-graph.js";
import { createEmbedFn } from "./embeddings.js";
import { EventBus } from "./event-bus.js";
import { registerHandlers } from "./event-handlers.js";
import { ResearchPlanner, type SessionBrief } from "./research-planner.js";
import { ClaimVerifier } from "./verification.js";
import { LiteratureScanner } from "./literature-scanner.js";
import { LiteratureMonitor } from "./literature-monitor.js";
import { ArxivClient } from "./arxiv.js";
import { SemanticScholarClient } from "./semantic-scholar.js";
import { LinearClient } from "./linear.js";

/** Agent sequences for multi-step phases. After one agent finishes, the next in the sequence runs. */
const PHASE_SEQUENCES: Record<string, string[]> = {
  "paper-finalization": ["writer", "critic", "editor"],
  "revision": ["writer", "critic"],
  "analysis": ["experimenter", "writer"],
  "experiment-validation": ["experimenter", "critic", "experimenter"],
};

export interface DaemonConfig {
  pollIntervalMs: number;
  maxConcurrentSessions: number;
  dailyBudgetUsd: number;
  rootDir: string;
}

const DEFAULT_CONFIG: DaemonConfig = {
  pollIntervalMs: 30 * 60 * 1000,
  maxConcurrentSessions: 2,
  dailyBudgetUsd: 40,
  rootDir: process.cwd(),
};

const MAX_SESSION_DURATION_MS = 60 * 60 * 1000; // 1 hour hard limit
const RETRY_DELAY_MS = 5 * 60 * 1000; // 5 min before retry

interface SessionTracker {
  promise: Promise<unknown>;
  projectName: string;
  startedAt: number;
  settled: boolean;
}

interface ScoredProject {
  project: ProjectStatus;
  score: number;
  agentType: AgentType;
}

interface FollowUp {
  projectName: string;
  agentType: AgentType;
  chainId: string;
  reason: string;
  queuedAt: number;
  chainDepth?: number;
}

export interface ExternalDispatch {
  id: string;
  project: string;
  agent_type: AgentType;
  priority: "low" | "normal" | "high" | "critical";
  reason: string;
  triggered_by: string;
  status: "queued" | "running" | "completed" | "rejected";
  created_at: string;
  chain_depth?: number;
}

const MAX_CHAIN_DEPTH = 3;
const MAX_DISPATCHES_PER_HOUR_PER_AGENT = 5;
const MAX_DISPATCHES_PER_DAY = 10;

export interface SessionQuality {
  score: number; // 0-100
  commitsCreated: number;
  statusAdvanced: boolean;
  criticVerdict?: string;
  costUsd: number;
  durationMs: number;
  agentType: string;
  timestamp: string;
}

export class Daemon {
  private config: DaemonConfig;
  private projectManager: ProjectManager;
  private sessionManager: SessionManager;
  private gitEngine: GitEngine;
  private budgetTracker: BudgetTracker;
  private logger: ActivityLogger;
  private notifier: Notifier;
  private evalManager: EvalJobManager;
  private running = false;
  private activeSessions = new Map<string, SessionTracker>();
  private abortController: AbortController | null = null;
  private failureCounts = new Map<string, number>();
  private followUpQueue: FollowUp[] = [];
  private externalQueue: ExternalDispatch[] = [];
  private dispatchLog: ExternalDispatch[] = [];
  private qualityHistory = new Map<string, SessionQuality[]>();
  private lastKnownPhases = new Map<string, string>();
  private cycleCount = 0;
  private startedAt = 0;
  private backlogManager: BacklogManager;
  private digestStore: DigestStore;
  private costPoller: CostPoller | null = null;
  private dbPool: pg.Pool | null = null;
  private knowledgeGraph: KnowledgeGraph | null = null;
  private eventBus: EventBus | null = null;
  private planner: ResearchPlanner | null = null;
  private verifier: ClaimVerifier | null = null;
  private literatureScanner: LiteratureScanner | null = null;
  private literatureMonitor: LiteratureMonitor | null = null;
  private linearClient: LinearClient | null = null;
  private lastMaintenanceAt = 0;
  private lastLiteratureScanAt = 0;

  constructor(config: Partial<DaemonConfig> = {}, dbPool?: pg.Pool) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    const rootDir = this.config.rootDir;
    this.dbPool = dbPool ?? null;

    // Knowledge graph (requires DB)
    if (this.dbPool) {
      this.knowledgeGraph = new KnowledgeGraph(this.dbPool, createEmbedFn());
    }

    this.projectManager = new ProjectManager(rootDir);
    this.gitEngine = new GitEngine(rootDir);
    this.sessionManager = new SessionManager(this.projectManager, this.gitEngine, rootDir, this.knowledgeGraph, this.dbPool);
    this.logger = new ActivityLogger(rootDir);
    this.notifier = new Notifier(rootDir);
    this.budgetTracker = new BudgetTracker(rootDir, this.logger, this.notifier, this.dbPool ?? undefined);
    this.evalManager = new EvalJobManager(rootDir, this.logger, this.notifier);
    this.backlogManager = new BacklogManager(rootDir);
    this.digestStore = new DigestStore(rootDir);

    if (this.dbPool) {
      this.costPoller = new CostPoller(this.dbPool);
      this.verifier = new ClaimVerifier(this.dbPool, this.knowledgeGraph, rootDir);
      this.eventBus = new EventBus(this.dbPool);
      registerHandlers(this.eventBus, {
        knowledgeGraph: this.knowledgeGraph,
        notifier: this.notifier,
        logger: this.logger,
        verifier: this.verifier,
        queueSession: (req) => this.queueSession(req as Parameters<typeof this.queueSession>[0]),
      });
    }

    // Literature intelligence
    const s2Client = new SemanticScholarClient();
    const arxivClient = new ArxivClient();

    // Level 1: Lightweight scanner (always on, no DB required)
    this.literatureScanner = new LiteratureScanner(
      s2Client,
      arxivClient,
      this.logger,
      this.notifier,
      this.eventBus,
      this.dbPool,
    );

    // Level 2: Full monitor (requires DB for paper storage + alerts)
    if (this.dbPool) {
      this.literatureMonitor = new LiteratureMonitor(
        this.dbPool,
        s2Client,
        arxivClient,
        createEmbedFn(),
        this.knowledgeGraph,
        this.logger,
        this.notifier,
        this.eventBus,
      );
    }

    // Linear integration
    if (process.env.LINEAR_API_KEY && process.env.LINEAR_TEAM_ID) {
      this.linearClient = new LinearClient(
        process.env.LINEAR_API_KEY,
        process.env.LINEAR_TEAM_ID,
      );
      console.log("Linear integration enabled");
    }

    // Research planner (feature flag: USE_RESEARCH_PLANNER=1)
    if (process.env.USE_RESEARCH_PLANNER === "1") {
      this.planner = new ResearchPlanner(
        this.dbPool,
        this.projectManager,
        this.knowledgeGraph,
        this.budgetTracker,
        this.backlogManager,
        this.linearClient,
      );
      console.log("Research planner enabled");
    }
  }

  getEvalManager(): EvalJobManager {
    return this.evalManager;
  }

  getLogger(): ActivityLogger {
    return this.logger;
  }

  getBacklogManager(): BacklogManager {
    return this.backlogManager;
  }

  getDigestStore(): DigestStore {
    return this.digestStore;
  }

  getBudgetTracker(): BudgetTracker {
    return this.budgetTracker;
  }

  getEventBus(): EventBus | null {
    return this.eventBus;
  }

  getPlanner(): ResearchPlanner | null {
    return this.planner;
  }

  getKnowledgeGraph(): KnowledgeGraph | null {
    return this.knowledgeGraph;
  }

  getLiteratureScanner(): LiteratureScanner | null {
    return this.literatureScanner;
  }

  getLiteratureMonitor(): LiteratureMonitor | null {
    return this.literatureMonitor;
  }

  getVerifier(): ClaimVerifier | null {
    return this.verifier;
  }

  getLinearClient(): LinearClient | null {
    return this.linearClient;
  }

  /**
   * Queue an external dispatch from an OpenClaw agent.
   * Returns the dispatch object or throws if rate-limited/rejected.
   */
  async queueSession(request: {
    project: string;
    agent_type: AgentType;
    priority?: "low" | "normal" | "high" | "critical";
    reason: string;
    triggered_by: string;
    chain_depth?: number;
  }): Promise<ExternalDispatch> {
    // Rate limit: per-agent per-hour
    const hourAgo = Date.now() - 60 * 60 * 1000;
    const recentByAgent = this.dispatchLog.filter(
      (d) => d.triggered_by === request.triggered_by && new Date(d.created_at).getTime() > hourAgo,
    );
    if (recentByAgent.length >= MAX_DISPATCHES_PER_HOUR_PER_AGENT) {
      throw new Error(`Rate limit: ${request.triggered_by} has ${recentByAgent.length} dispatches in the last hour (max ${MAX_DISPATCHES_PER_HOUR_PER_AGENT})`);
    }

    // Rate limit: daily total
    const dayStart = new Date();
    dayStart.setUTCHours(0, 0, 0, 0);
    const todayDispatches = this.dispatchLog.filter(
      (d) => new Date(d.created_at).getTime() > dayStart.getTime(),
    );
    if (todayDispatches.length >= MAX_DISPATCHES_PER_DAY) {
      throw new Error(`Rate limit: ${todayDispatches.length} dispatches today (max ${MAX_DISPATCHES_PER_DAY})`);
    }

    // Chain depth limit
    const chainDepth = request.chain_depth ?? 0;
    if (chainDepth >= MAX_CHAIN_DEPTH) {
      throw new Error(`Chain depth limit: depth ${chainDepth} exceeds max ${MAX_CHAIN_DEPTH}`);
    }

    // Budget check
    const budgetStatus = await this.budgetTracker.getStatus();
    if (budgetStatus.alertLevel === "exceeded") {
      throw new Error("Budget exceeded — dispatch rejected");
    }
    if (budgetStatus.monthlySpent > 900) {
      throw new Error("Monthly spend exceeds $900 — dispatch rejected for safety");
    }

    // Don't dispatch to a project with an active session
    if (this.activeSessions.has(request.project)) {
      throw new Error(`Project ${request.project} already has an active session`);
    }

    const dispatch: ExternalDispatch = {
      id: randomUUID().slice(0, 8),
      project: request.project,
      agent_type: request.agent_type,
      priority: request.priority ?? "normal",
      reason: request.reason,
      triggered_by: request.triggered_by,
      status: "queued",
      created_at: new Date().toISOString(),
      chain_depth: chainDepth,
    };

    this.externalQueue.push(dispatch);
    this.dispatchLog.push(dispatch);

    await this.logger.log({
      type: "session_start",
      project: request.project,
      agent: request.agent_type,
      data: {
        dispatchId: dispatch.id,
        triggeredBy: request.triggered_by,
        priority: dispatch.priority,
        reason: request.reason,
        source: "external_dispatch",
      },
    });

    return dispatch;
  }

  getDispatchQueue(): ExternalDispatch[] {
    return [...this.externalQueue];
  }

  getDispatchLog(): ExternalDispatch[] {
    return [...this.dispatchLog];
  }

  async start(): Promise<void> {
    this.running = true;
    this.startedAt = Date.now();
    this.abortController = new AbortController();

    await this.logger.log({
      type: "daemon_start",
      data: {
        pollIntervalMs: this.config.pollIntervalMs,
        maxConcurrentSessions: this.config.maxConcurrentSessions,
        dailyBudgetUsd: this.config.dailyBudgetUsd,
      },
    });

    // Start event bus listening
    if (this.eventBus) {
      await this.eventBus.start();
    }

    // Sync filesystem projects to DB before first cycle
    await this.syncProjectsToDb();

    console.log("Deepwork daemon started");
    console.log("  Poll interval: " + Math.round(this.config.pollIntervalMs / 60000) + "m");
    console.log("  Max concurrent: " + this.config.maxConcurrentSessions);
    console.log("  Daily budget: $" + this.config.dailyBudgetUsd);

    process.on("SIGTERM", () => this.shutdown("SIGTERM"));
    process.on("SIGINT", () => this.shutdown("SIGINT"));

    while (this.running) {
      try {
        await this.cycle();
        await this.writeHeartbeat();
      } catch (err) {
        console.error("Daemon cycle error:", err);
        await this.logger.log({
          type: "daemon_error",
          data: { error: err instanceof Error ? err.message : String(err) },
        });
      }
      if (!this.running) break;
      await this.sleep(this.config.pollIntervalMs);
    }

    // Stop event bus
    if (this.eventBus) {
      await this.eventBus.stop();
    }

    await this.logger.log({ type: "daemon_stop", data: { cyclesCompleted: this.cycleCount } });
    console.log("Deepwork daemon stopped");
  }

  async getHealth() {
    const sessions = Array.from(this.activeSessions.values()).map((t) => ({
      project: t.projectName,
      runningMs: Date.now() - t.startedAt,
    }));
    const qualitySummary: Record<string, { avg: number | undefined; recent: SessionQuality[] }> = {};
    for (const [project, history] of this.qualityHistory) {
      qualitySummary[project] = {
        avg: this.getRecentQualityAvg(project),
        recent: history.slice(-3),
      };
    }
    return {
      running: this.running,
      uptimeMs: Date.now() - this.startedAt,
      cyclesCompleted: this.cycleCount,
      activeSessions: sessions,
      failureCounts: Object.fromEntries(this.failureCounts),
      pendingFollowUps: this.followUpQueue.length,
      pendingDispatches: this.externalQueue.length,
      dispatchQueue: this.externalQueue,
      recentDispatches: this.dispatchLog.slice(-10),
      quality: qualitySummary,
    };
  }

  private async cycle(): Promise<void> {
    this.cycleCount++;
    console.log("\n--- Cycle " + this.cycleCount + " ---");

    // Check budget before doing anything
    const budgetStatus = await this.budgetTracker.getStatus();
    if (budgetStatus.alertLevel === "exceeded") {
      console.log("Budget exceeded -- skipping cycle");
      await this.notifier.notify({
        event: "Budget Exceeded",
        summary: "Daily: $" + budgetStatus.dailySpent.toFixed(2) + "/$" + budgetStatus.dailyLimit.toFixed(2) + " | Monthly: $" + budgetStatus.monthlySpent.toFixed(2) + "/$" + budgetStatus.monthlyLimit.toFixed(2),
        level: "error",
      });
      return;
    }

    if (budgetStatus.alertLevel === "critical") {
      console.log("Budget critical: $" + budgetStatus.dailySpent.toFixed(2) + "/$" + budgetStatus.dailyLimit.toFixed(2) + " daily");
      await this.notifier.notify({
        event: "Budget Critical",
        summary: "Daily: $" + budgetStatus.dailySpent.toFixed(2) + "/$" + budgetStatus.dailyLimit.toFixed(2),
        level: "warning",
      });
    }

    // Clean up finished sessions + detect stale ones
    await this.cleanupSessions();

    let availableSlots = this.config.maxConcurrentSessions - this.activeSessions.size;
    if (availableSlots <= 0) {
      console.log("All " + this.config.maxConcurrentSessions + " session slots occupied -- waiting");
      return;
    }

    // Process follow-up queue first (chained sessions take priority)
    while (this.followUpQueue.length > 0 && availableSlots > 0) {
      const followUp = this.followUpQueue.shift()!;
      if (this.activeSessions.has(followUp.projectName)) continue; // Skip if project already running

      // Chain depth check
      const depth = followUp.chainDepth ?? 0;
      if (depth >= MAX_CHAIN_DEPTH) {
        console.log("Skipping chained session for " + followUp.projectName + " — chain depth " + depth + " exceeds max " + MAX_CHAIN_DEPTH);
        continue;
      }

      console.log("Launching chained " + followUp.agentType + " session for " + followUp.projectName + " (reason: " + followUp.reason + ")");

      await this.logger.log({
        type: "session_start",
        project: followUp.projectName,
        agent: followUp.agentType,
        data: { chainId: followUp.chainId, reason: followUp.reason, chained: true, chainDepth: depth },
      });

      const tracker: SessionTracker = {
        promise: Promise.resolve(),
        projectName: followUp.projectName,
        startedAt: Date.now(),
        settled: false,
      };
      tracker.promise = this.runSession(followUp.projectName, followUp.agentType, followUp.chainId, depth + 1).finally(() => {
        tracker.settled = true;
      });
      this.activeSessions.set(followUp.projectName, tracker);
      availableSlots--;
    }

    // Process external dispatch queue (from OpenClaw agents)
    // Sort by priority: critical > high > normal > low
    const priorityOrder: Record<string, number> = { critical: 0, high: 1, normal: 2, low: 3 };
    this.externalQueue.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);

    while (this.externalQueue.length > 0 && availableSlots > 0) {
      const dispatch = this.externalQueue.shift()!;
      if (this.activeSessions.has(dispatch.project)) {
        dispatch.status = "rejected";
        continue;
      }

      console.log("Launching externally dispatched " + dispatch.agent_type + " session for " + dispatch.project + " (by: " + dispatch.triggered_by + ", reason: " + dispatch.reason + ")");

      dispatch.status = "running";
      const chainId = randomUUID();
      const chainDepth = dispatch.chain_depth ?? 0;

      await this.logger.log({
        type: "session_start",
        project: dispatch.project,
        agent: dispatch.agent_type,
        data: {
          dispatchId: dispatch.id,
          triggeredBy: dispatch.triggered_by,
          reason: dispatch.reason,
          source: "external_dispatch",
          chainDepth,
        },
      });

      const tracker: SessionTracker = {
        promise: Promise.resolve(),
        projectName: dispatch.project,
        startedAt: Date.now(),
        settled: false,
      };
      tracker.promise = this.runSession(dispatch.project, dispatch.agent_type, chainId, chainDepth).then(() => {
        dispatch.status = "completed";
      }).catch(() => {
        dispatch.status = "rejected";
      }).finally(() => {
        tracker.settled = true;
      });
      this.activeSessions.set(dispatch.project, tracker);
      availableSlots--;
    }

    if (availableSlots <= 0) return;

    if (this.planner) {
      // ---- Planner path ----
      const activeSet = new Set(this.activeSessions.keys());
      const briefs = await this.planner.planNextActions(availableSlots, activeSet);

      if (briefs.length === 0) {
        console.log("Planner: no actions this cycle");
      }

      for (const brief of briefs) {
        if (this.activeSessions.has(brief.projectName)) continue;

        console.log("Planner: launching " + brief.agentType + " for " + brief.projectName + " (strategy: " + brief.strategy + ", pri=" + brief.priority + ")");
        console.log("  Objective: " + brief.objective.slice(0, 120));

        // Transition Linear issue to "In Progress" when starting
        if (brief.strategy === "linear_driven" && this.linearClient && brief.context.supplementary) {
          const issueIdMatch = brief.context.supplementary.match(/Linear issue ID: ([a-f0-9-]+)/);
          if (issueIdMatch) {
            this.linearClient.transitionIssue(issueIdMatch[1], "In Progress").catch((err) => {
              console.error(`[Linear] Failed to transition issue to In Progress:`, err);
            });
          }
        }

        await this.logger.log({
          type: "session_start",
          project: brief.projectName,
          agent: brief.agentType,
          data: {
            briefId: brief.id,
            strategy: brief.strategy,
            priority: brief.priority,
            objective: brief.objective,
            model: brief.constraints.model,
            source: "planner",
          },
        });

        const tracker: SessionTracker = {
          promise: Promise.resolve(),
          projectName: brief.projectName,
          startedAt: Date.now(),
          settled: false,
        };
        tracker.promise = this.runSessionFromBrief(brief).finally(() => {
          tracker.settled = true;
        });
        this.activeSessions.set(brief.projectName, tracker);
      }
    } else {
      // ---- Legacy scoring path ----
      const projects = await this.projectManager.listProjects();
      const scored = await this.scoreProjects(projects);

      const candidates = scored
        .filter((s) => !this.activeSessions.has(s.project.project))
        .filter((s) => s.score > 0)
        .slice(0, availableSlots);

      if (candidates.length === 0 && this.followUpQueue.length === 0) {
        console.log("No eligible projects this cycle");
      } else {
        for (const candidate of candidates) {
          const { project, agentType } = candidate;

          if (this.isStuckLoop(project.project, agentType)) {
            console.log("⚠ Loop detected: " + project.project + " has 3+ consecutive low-quality " + agentType + " sessions — skipping this cycle");
            await this.logger.log({
              type: "loop_detected",
              project: project.project,
              agent: agentType,
              data: { reason: "3+ consecutive sessions with quality < 70, same agent type" },
            });
            continue;
          }

          console.log("Launching " + agentType + " session for " + project.project + " (score: " + candidate.score + ")");

          await this.logger.log({
            type: "session_start",
            project: project.project,
            agent: agentType,
            data: { score: candidate.score, phase: project.phase },
          });

          const tracker: SessionTracker = {
            promise: Promise.resolve(),
            projectName: project.project,
            startedAt: Date.now(),
            settled: false,
          };
          tracker.promise = this.runSession(project.project, agentType).finally(() => {
            tracker.settled = true;
          });
          this.activeSessions.set(project.project, tracker);
        }
      }
    }

    // Tick eval job manager — check running jobs, start queued ones
    try {
      await this.evalManager.tick();
    } catch (err) {
      console.error("Eval manager tick error:", err);
      await this.logger.log({
        type: "daemon_error",
        data: { error: "Eval manager tick failed: " + (err instanceof Error ? err.message : String(err)) },
      });
    }

    // Poll cost providers for usage data and reconciliation
    if (this.costPoller) {
      try {
        await this.costPoller.pollAll();
      } catch (err) {
        console.error("Cost poller error:", err);
        await this.logger.log({
          type: "daemon_error",
          data: { error: "Cost poller failed: " + (err instanceof Error ? err.message : String(err)) },
        });
      }
    }

    // Knowledge graph maintenance — snapshots and contradiction checks
    if (this.knowledgeGraph) {
      try {
        await this.knowledgeGraphMaintenance();
      } catch (err) {
        console.error("Knowledge graph maintenance error:", err);
      }
    }

    // Literature scan — daily keyword search for competing papers
    if (this.literatureMonitor || this.literatureScanner) {
      try {
        await this.runLiteratureScan();
      } catch (err) {
        console.error("Literature scan error:", err);
      }
    }

    // Ack triggers that the planner has processed into briefs
    if (this.dbPool) {
      try {
        await this.dbPool.query(
          `UPDATE trigger_log SET acked_at = NOW()
           WHERE acked_at IS NULL AND created_at < NOW() - INTERVAL '1 hour'`,
        );
      } catch { /* non-critical */ }
    }

    // Dead-letter auto-retry and domain_events cleanup
    if (this.eventBus) {
      try {
        const retried = await this.eventBus.retryAllDeadLetters();
        if (retried > 0) {
          console.log("Retried " + retried + " dead letter(s)");
        }
      } catch (err) {
        console.error("Dead letter retry error:", err);
      }

      // Prune old domain_events (keep 30 days)
      if (this.dbPool && this.cycleCount % 24 === 0) {
        try {
          const { rowCount } = await this.dbPool.query(
            "DELETE FROM domain_events WHERE processed = TRUE AND created_at < NOW() - INTERVAL '30 days'",
          );
          if (rowCount && rowCount > 0) {
            console.log("Pruned " + rowCount + " old domain events");
          }
        } catch { /* non-critical */ }
      }
    }
  }

  /** Sync filesystem projects to the DB on startup so FK references never break. */
  private async syncProjectsToDb(): Promise<void> {
    if (!this.dbPool) return;
    try {
      const projects = await this.projectManager.listProjects();
      for (const p of projects) {
        await this.dbPool.query(
          `INSERT INTO projects (id, name, title, venue, phase, status, confidence, current_focus, current_activity, branch, updated_at)
           VALUES ($1, $1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
           ON CONFLICT (id) DO UPDATE SET
             phase = EXCLUDED.phase,
             status = EXCLUDED.status,
             confidence = EXCLUDED.confidence,
             current_focus = EXCLUDED.current_focus,
             current_activity = EXCLUDED.current_activity,
             updated_at = NOW()`,
          [
            p.project,
            p.title,
            p.venue ?? null,
            p.phase,
            p.status === "in-progress" ? "active" : p.status,
            p.confidence,
            p.current_focus,
            p.current_activity ?? null,
            p.git?.branch ?? null,
          ],
        );
      }
      console.log(`Synced ${projects.length} project(s) to DB`);
    } catch (err) {
      console.error("Failed to sync projects to DB:", err);
    }
  }

  /** Periodic knowledge graph tasks: daily snapshots, contradiction logging. */
  private async knowledgeGraphMaintenance(): Promise<void> {
    if (!this.knowledgeGraph) return;

    // Run once per 24 hours regardless of poll interval
    const hoursSinceLast = (Date.now() - this.lastMaintenanceAt) / (1000 * 60 * 60);
    if (this.lastMaintenanceAt > 0 && hoursSinceLast < 24) return;
    this.lastMaintenanceAt = Date.now();

    const projects = await this.projectManager.listProjects();

    // Only run maintenance for projects that exist in DB
    const dbProjectIds = this.dbPool
      ? (await this.dbPool.query("SELECT id FROM projects")).rows.map((r: Record<string, unknown>) => r.id as string)
      : [];

    for (const project of projects) {
      if (dbProjectIds.length > 0 && !dbProjectIds.includes(project.project)) continue;
      try {
        // Create daily snapshot
        await this.knowledgeGraph.createSnapshot(project.project);

        // Check for contradictions and log new ones
        const contradictions = await this.knowledgeGraph.findContradictions(project.project);
        if (contradictions.length > 0) {
          await this.logger.log({
            type: "knowledge_contradictions",
            project: project.project,
            data: { count: contradictions.length },
          });
        }
      } catch (err) {
        console.error(`Knowledge maintenance failed for ${project.project}:`, err);
      }
    }
  }

  /** Daily literature scan — keyword search for competing papers. */
  private async runLiteratureScan(): Promise<void> {
    // Run once per 24 hours regardless of poll interval
    const hoursSinceLast = (Date.now() - this.lastLiteratureScanAt) / (1000 * 60 * 60);
    if (this.lastLiteratureScanAt > 0 && hoursSinceLast < 24) return;
    this.lastLiteratureScanAt = Date.now();

    const projects = await this.projectManager.listProjects();
    const activeProjects = projects.filter(
      (p) => p.status === "active" || p.status === "in-progress",
    );

    if (activeProjects.length === 0) return;

    console.log(`[LitScan] Scanning ${activeProjects.length} active project(s)`);

    // Prefer Level 2 monitor (DB-backed) over Level 1 scanner
    if (this.literatureMonitor) {
      await this.literatureMonitor.tick(
        activeProjects.map((p) => ({ project: p.project, keyTerms: p.key_terms ?? [] })),
      );
    } else if (this.literatureScanner) {
      await this.literatureScanner.scan(activeProjects);
    }
  }

  private async cleanupSessions(): Promise<void> {
    for (const [name, tracker] of this.activeSessions) {
      if (tracker.settled) {
        this.activeSessions.delete(name);
        continue;
      }

      // Stale session detection: kill if running > hard limit
      const runningMs = Date.now() - tracker.startedAt;
      if (runningMs > MAX_SESSION_DURATION_MS) {
        console.log("Session for " + name + " exceeded " + (MAX_SESSION_DURATION_MS / 60000) + "min hard limit -- marking stale");
        await this.logger.log({
          type: "session_error",
          project: name,
          data: { error: "Session exceeded hard duration limit", runningMs },
        });
        this.activeSessions.delete(name);
        this.recordFailure(name);
      }
    }
  }

  private async runSession(projectName: string, agentType: AgentType, chainId?: string, chainDepth: number = 0): Promise<void> {
    const currentChainId = chainId ?? randomUUID();

    const attempt = async (): Promise<Session> => {
      // startProject sets up worktree, runs agent, and returns session info
      const session = await this.sessionManager.startProject(projectName, agentType);

      const result = session.result;
      const quality = this.assessQuality(session, agentType);
      this.recordQuality(projectName, quality);
      if (result) await this.persistSession(result);

      await this.logger.log({
        type: "session_end",
        project: projectName,
        agent: agentType,
        data: {
          worktreePath: session.worktreePath,
          branch: session.branch,
          status: session.status,
          chainId: currentChainId,
          quality: quality.score,
          commits: result?.commitsCreated.length ?? 0,
          cost: result?.costUsd ?? 0,
          signals: session.signals,
        },
      });

      // Enriched notification with session details
      const commitCount = result?.commitsCreated.length ?? 0;
      const cost = result?.costUsd?.toFixed(2) ?? "0.00";
      const verdictStr = session.signals?.criticVerdict ? " | verdict: " + session.signals.criticVerdict : "";
      await this.notifier.notify({
        event: "Session Completed",
        project: projectName,
        summary: agentType + ": " + commitCount + " commits, $" + cost + verdictStr + " (quality: " + quality.score + "/100)",
        details: {
          agent: agentType,
          commits: commitCount,
          cost: "$" + cost,
          duration: Math.round((result?.durationMs ?? 0) / 1000) + "s",
          quality: quality.score,
          chainId: currentChainId,
        },
        level: "info",
      });

      // Emit domain event
      if (this.eventBus) {
        await this.eventBus.emit("session.completed", {
          sessionId: result?.sessionId,
          project: projectName,
          agentType,
          commits: result?.commitsCreated.length ?? 0,
          costUsd: result?.costUsd ?? 0,
          quality: quality.score,
          chainId: currentChainId,
        }).catch(() => { /* best effort */ });
      }

      this.clearFailure(projectName);
      return session;
    };

    let session: Session | undefined;
    try {
      session = await attempt();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error("Session failed for " + projectName + ": " + errorMsg);

      await this.logger.log({
        type: "session_error",
        project: projectName,
        agent: agentType,
        data: { error: errorMsg, willRetry: true, chainId: currentChainId },
      });

      this.recordFailure(projectName);

      // Emit failure event
      if (this.eventBus) {
        await this.eventBus.emit("session.failed", {
          project: projectName,
          agentType,
          error: errorMsg,
          chainId: currentChainId,
        }).catch(() => { /* best effort */ });
      }

      await this.notifier.notify({
        event: "Session Failed",
        project: projectName,
        summary: agentType + ": " + errorMsg,
        level: "error",
      });

      // Retry once after delay
      console.log("Retrying " + projectName + " in " + (RETRY_DELAY_MS / 1000) + "s...");
      await this.sleep(RETRY_DELAY_MS);

      try {
        session = await attempt();
      } catch (retryErr) {
        const retryMsg = retryErr instanceof Error ? retryErr.message : String(retryErr);
        console.error("Retry also failed for " + projectName + ": " + retryMsg);
        await this.logger.log({
          type: "session_error",
          project: projectName,
          agent: agentType,
          data: { error: retryMsg, retryFailed: true, chainId: currentChainId },
        });
        this.recordFailure(projectName);
        throw retryErr;
      }
    }

    // Session chaining: determine and queue follow-up based on signals
    if (session?.signals && session.status === "completed") {
      this.processSessionSignals(projectName, agentType, session.signals, currentChainId, chainDepth);

      // Emit paper.edited if paper files changed
      if (session.signals.paperFilesChanged && this.eventBus) {
        await this.eventBus.emit("paper.edited", {
          project: projectName,
          agentType,
          sessionId: session.result?.sessionId,
        }).catch(() => {});
      }
    }
  }

  private async runSessionFromBrief(brief: SessionBrief): Promise<void> {
    // Collective actions use API calls, not git worktrees
    if (brief.strategy === "collective_action") {
      return this.runCollectiveSession(brief);
    }

    // Budget gate: experimenter sessions with estimated cost >$2 require an approved spec
    if (brief.agentType === "experimenter" && brief.constraints.maxBudgetUsd > 2) {
      const specState = await this.checkExperimentSpec(brief.projectName);
      if (specState === "needs_spec") {
        // Redirect to spec-writing mode
        brief.objective = `Create experiment pre-registration spec for: ${brief.objective}. ` +
          `Write experiments/<name>/spec.yaml using the template at shared/templates/experiment/spec.yaml. ` +
          `Cross-reference design conditions against the paper's theoretical framework.`;
        brief.deliverables = [
          { description: "Create experiment spec.yaml", type: "file" as const, verificationMethod: "file_exists" as const },
          { description: "Update status.yaml", type: "status_update" as const, verificationMethod: "status_changed" as const },
        ];
        console.log("  Budget gate: no spec found for " + brief.projectName + " — redirecting to spec-writing mode");
      } else if (specState === "needs_review") {
        console.log("  Budget gate: experiment spec for " + brief.projectName + " needs review — queuing critic");
        this.followUpQueue.push({
          projectName: brief.projectName,
          agentType: "critic" as AgentType,
          chainId: randomUUID(),
          reason: "Experiment spec pending review",
          queuedAt: Date.now(),
        });
        return;
      }
    }

    const chainId = randomUUID();
    try {
      const session = await this.sessionManager.startProjectWithBrief(brief);
      const quality = this.assessQuality(session, brief.agentType);
      this.recordQuality(brief.projectName, quality);
      if (session.result) await this.persistSession(session.result, brief.constraints.model);

      // Planner evaluation
      if (this.planner && session.result) {
        const evaluation = await this.planner.evaluateSession(brief, session.result, session.signals);
        await this.logger.log({
          type: "session_end",
          project: brief.projectName,
          agent: brief.agentType,
          data: {
            briefId: brief.id,
            strategy: brief.strategy,
            deliverablesMet: evaluation.deliverablesMet,
            deliverablesTotal: evaluation.deliverablesTotal,
            evaluationScore: evaluation.qualityScore,
            legacyScore: quality.score,
            cost: session.result.costUsd,
            commits: session.result.commitsCreated.length,
          },
        });
      }

      // Linear issue update (if linear_driven)
      if (brief.strategy === "linear_driven" && this.linearClient && brief.context.supplementary) {
        const issueIdMatch = brief.context.supplementary.match(/Linear issue ID: ([a-f0-9-]+)/);
        if (issueIdMatch) {
          const linearIssueId = issueIdMatch[1];
          const commitCount = session.result?.commitsCreated.length ?? 0;
          const cost = session.result?.costUsd?.toFixed(2) ?? "0.00";
          const duration = session.result?.durationMs
            ? Math.round(session.result.durationMs / 60000) + "min"
            : "unknown";

          try {
            // Transition to Done if session completed successfully with commits
            const targetState = commitCount > 0 ? "Done" : "In Review";
            await this.linearClient.transitionIssue(linearIssueId, targetState);

            // Add comment with session summary
            const comment = [
              `**Session completed** (${brief.agentType})`,
              "",
              `- Quality: ${quality.score}/100`,
              `- Commits: ${commitCount}`,
              `- Cost: $${cost}`,
              `- Duration: ${duration}`,
              commitCount > 0
                ? `- Commits: ${session.result?.commitsCreated.map((c) => `\`${c.slice(0, 7)}\``).join(", ")}`
                : "",
              "",
              `State → **${targetState}**`,
            ].filter(Boolean).join("\n");

            await this.linearClient.addComment(linearIssueId, comment);
          } catch (err) {
            console.error(`[Linear] Failed to update issue ${linearIssueId}:`, err);
          }
        }
      }

      // Notification
      const commitCount = session.result?.commitsCreated.length ?? 0;
      const cost = session.result?.costUsd?.toFixed(2) ?? "0.00";
      await this.notifier.notify({
        event: "Session Completed",
        project: brief.projectName,
        summary: `${brief.agentType}/${brief.strategy}: ${commitCount} commits, $${cost} (quality: ${quality.score}/100)`,
        level: "info",
      });

      this.clearFailure(brief.projectName);

      // Session chaining
      if (session.signals && session.status === "completed") {
        this.processSessionSignals(brief.projectName, brief.agentType, session.signals, chainId, 0);

        if (session.signals.paperFilesChanged && this.eventBus) {
          await this.eventBus.emit("paper.edited", {
            project: brief.projectName,
            agentType: brief.agentType,
            sessionId: session.result?.sessionId,
          }).catch(() => {});
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error("Planner session failed for " + brief.projectName + ": " + msg);
      this.recordFailure(brief.projectName);
      await this.notifier.notify({
        event: "Session Failed",
        project: brief.projectName,
        summary: `${brief.agentType}/${brief.strategy}: ${msg}`,
        level: "error",
      });
    }
  }

  /** Run a collective action session — no worktree, agent uses API calls. */
  private async runCollectiveSession(brief: SessionBrief): Promise<void> {
    try {
      const result = await this.sessionManager.getRunner().runCollective(brief);

      console.log(`Collective session finished: ${result.status} ($${result.costUsd.toFixed(2)}, ${result.turnsUsed} turns)`);
      await this.persistSession(result, brief.constraints.model);

      if (this.planner) {
        const evaluation = await this.planner.evaluateSession(brief, result);
        await this.logger.log({
          type: "session_end",
          project: brief.projectName,
          agent: brief.agentType,
          data: {
            briefId: brief.id,
            strategy: brief.strategy,
            evaluationScore: evaluation.qualityScore,
            cost: result.costUsd,
            source: "collective",
          },
        });
      }

      await this.notifier.notify({
        event: "Collective Action",
        project: brief.projectName,
        summary: `${brief.agentType}: ${brief.objective.slice(0, 100)} ($${result.costUsd.toFixed(2)})`,
        level: "info",
      });

      this.clearFailure(brief.projectName);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error("Collective session failed: " + msg);
      this.recordFailure(brief.projectName);
    }
  }

  private processSessionSignals(
    projectName: string,
    agentType: AgentType,
    signals: SessionSignals,
    chainId: string,
    chainDepth: number = 0,
  ): void {
    // Experiment spec created → chain to critic for review
    if (agentType === "experimenter" && signals.experimentSpecCreated) {
      this.followUpQueue.push({
        projectName,
        agentType: "critic",
        chainId,
        reason: "Experiment spec needs critic review before execution",
        queuedAt: Date.now(),
        chainDepth: chainDepth + 1,
      });
      console.log("  Chaining: experimenter spec → queued critic review for " + projectName);
      return;
    }

    // Critic approved experiment spec → chain to experimenter for execution
    if (agentType === "critic" && signals.experimentSpecApproved) {
      this.followUpQueue.push({
        projectName,
        agentType: "experimenter",
        chainId,
        reason: "Experiment spec approved — proceed to canary and full run",
        queuedAt: Date.now(),
        chainDepth: chainDepth + 1,
      });
      console.log("  Chaining: critic approved spec → queued experimenter execution for " + projectName);
      return;
    }

    // Critic verdict drives follow-up
    if (agentType === "critic" && signals.criticVerdict === "REVISE") {
      this.followUpQueue.push({
        projectName,
        agentType: "writer",
        chainId,
        reason: "Critic verdict: REVISE — writer needed to address feedback",
        queuedAt: Date.now(),
        chainDepth: chainDepth + 1,
      });
      console.log("  Chaining: critic REVISE → queued writer follow-up for " + projectName);
      return;
    }

    if (agentType === "critic" && signals.criticVerdict === "ACCEPT") {
      this.followUpQueue.push({
        projectName,
        agentType: "editor",
        chainId,
        reason: "Critic verdict: ACCEPT — editor pass for final polish",
        queuedAt: Date.now(),
        chainDepth: chainDepth + 1,
      });
      console.log("  Chaining: critic ACCEPT → queued editor follow-up for " + projectName);
      return;
    }

    // Phase-based sequence advancement
    const project = this.getProjectPhase(projectName);
    if (project) {
      const sequence = PHASE_SEQUENCES[project];
      if (sequence) {
        const currentIdx = sequence.indexOf(agentType);
        if (currentIdx >= 0 && currentIdx < sequence.length - 1) {
          const nextAgent = sequence[currentIdx + 1] as AgentType;
          this.followUpQueue.push({
            projectName,
            agentType: nextAgent,
            chainId,
            reason: "Phase sequence " + project + ": " + agentType + " → " + nextAgent,
            queuedAt: Date.now(),
            chainDepth: chainDepth + 1,
          });
          console.log("  Chaining: sequence " + agentType + " → " + nextAgent + " for " + projectName);
        }
      }
    }
  }

  private getProjectPhase(projectName: string): string | undefined {
    // Check cached phase from last scoring cycle
    // This avoids async reads during signal processing
    return this.lastKnownPhases.get(projectName);
  }

  /**
   * Check whether a project's experiment spec is in a state that allows execution.
   * Returns:
   * - "needs_spec": No spec found — experimenter should create one
   * - "needs_review": Spec exists but not yet reviewed
   * - "approved": Spec approved — experimenter can proceed
   * - "not_required": No experiments directory or not an experiment-oriented project
   */
  async checkExperimentSpec(
    projectName: string,
  ): Promise<"needs_spec" | "needs_review" | "approved" | "not_required"> {
    const experimentsDir = join(this.config.rootDir, "projects", projectName, "experiments");
    try {
      const dirs = await readdir(experimentsDir);
      for (const dir of dirs) {
        try {
          const specPath = join(experimentsDir, dir, "spec.yaml");
          const content = await readFile(specPath, "utf-8");
          const statusMatch = content.match(/^status:\s*(\S+)/m);
          if (statusMatch) {
            const specStatus = statusMatch[1];
            if (specStatus === "approved" || specStatus === "running" || specStatus === "complete") {
              return "approved";
            }
            // Parse the review block to find review.status
            const reviewBlock = content.match(/^review:\s*\n((?:\s+.*\n?)*)/m);
            if (reviewBlock) {
              const reviewStatusInBlock = reviewBlock[1].match(/status:\s*(\S+)/);
              if (reviewStatusInBlock) {
                const reviewStatus = reviewStatusInBlock[1];
                if (reviewStatus === "approved") return "approved";
                if (reviewStatus === "pending" || reviewStatus === "revision_requested") return "needs_review";
              }
            }
            if (specStatus === "draft") return "needs_review";
          }
        } catch {
          // No spec.yaml in this directory
        }
      }
      return "not_required";
    } catch {
      return "not_required";
    }
  }

  private assessQuality(session: Session, agentType: string): SessionQuality {
    const result = session.result;
    let score = 0;

    // Commits created (up to 30 points)
    const commits = result?.commitsCreated.length ?? 0;
    score += Math.min(commits * 10, 30);

    // Session completed successfully (20 points)
    if (session.status === "completed" && result?.status === "completed") {
      score += 20;
    }

    // Status.yaml was updated (15 points)
    if (session.signals?.statusYamlChanged) {
      score += 15;
    }

    // Critic provided a verdict (15 points)
    if (session.signals?.criticVerdict) {
      score += 15;
    }

    // Reasonable cost efficiency (up to 20 points)
    // Lower cost per commit is better
    if (commits > 0 && result) {
      const costPerCommit = result.costUsd / commits;
      if (costPerCommit < 1) score += 20;
      else if (costPerCommit < 3) score += 15;
      else if (costPerCommit < 5) score += 10;
      else score += 5;
    }

    return {
      score: Math.min(score, 100),
      commitsCreated: commits,
      statusAdvanced: session.signals?.statusYamlChanged ?? false,
      criticVerdict: session.signals?.criticVerdict,
      costUsd: result?.costUsd ?? 0,
      durationMs: result?.durationMs ?? 0,
      agentType,
      timestamp: new Date().toISOString(),
    };
  }

  private async persistSession(
    result: SessionResult,
    model?: string,
  ): Promise<void> {
    if (!this.dbPool) return;
    try {
      await this.dbPool.query(
        `INSERT INTO sessions (session_id, project, agent_type, model, tokens_used, cost_usd, commits_created, status, error, started_at, duration_s)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW() - INTERVAL '1 second' * $10, $11)
         ON CONFLICT (session_id) DO NOTHING`,
        [
          result.sessionId,
          result.projectName,
          result.agentType,
          model ?? "claude-sonnet-4-6",
          result.tokensUsed.input + result.tokensUsed.output,
          result.costUsd,
          result.commitsCreated.length,
          result.status === "budget_exceeded" || result.status === "timeout" ? "failed" : result.status,
          result.error ?? null,
          result.durationMs / 1000,
          result.durationMs / 1000,
        ],
      );
    } catch (err) {
      console.error("[Daemon] Failed to persist session:", err);
    }
  }

  private recordQuality(projectName: string, quality: SessionQuality): void {
    const history = this.qualityHistory.get(projectName) ?? [];
    history.push(quality);
    // Keep last 10 quality records
    if (history.length > 10) history.shift();
    this.qualityHistory.set(projectName, history);
  }

  getQualityHistory(projectName: string): SessionQuality[] {
    return this.qualityHistory.get(projectName) ?? [];
  }

  /**
   * Detect stuck loops. Two conditions (either triggers):
   * 1. Last 3 sessions: same agent type AND all quality < 70
   * 2. Last 5 sessions: same agent type (hard cap — no agent should run 5x consecutively)
   */
  private isStuckLoop(projectName: string, agentType: string): boolean {
    const history = this.qualityHistory.get(projectName);
    if (!history || history.length < 3) return false;

    // Check 1: 3 consecutive low-quality sessions with same agent
    const last3 = history.slice(-3);
    if (last3.every((q) => q.score < 70 && q.agentType === agentType)) {
      return true;
    }

    // Check 2: 5 consecutive sessions with same agent (regardless of quality)
    if (history.length >= 5) {
      const last5 = history.slice(-5);
      if (last5.every((q) => q.agentType === agentType)) {
        return true;
      }
    }

    return false;
  }

  private getRecentQualityAvg(projectName: string, count: number = 3): number | undefined {
    const history = this.qualityHistory.get(projectName);
    if (!history || history.length === 0) return undefined;
    const recent = history.slice(-count);
    return recent.reduce((sum, q) => sum + q.score, 0) / recent.length;
  }

  private async scoreProjects(projects: ProjectStatus[]): Promise<ScoredProject[]> {
    const now = new Date();
    const activeProjects = projects.filter((p) => p.status === "active");
    const scored: ScoredProject[] = [];

    for (const project of activeProjects) {
      let score = 0;
      let agentType = PHASE_TO_AGENT[project.phase] ?? "researcher" as AgentType;

      // Cache phase for signal processing
      this.lastKnownPhases.set(project.project, project.phase);

      // +10: venue deadline within 4 weeks
      if (this.hasUpcomingDeadline(project, now, 28)) {
        score += 10;
      }

      // +5: no session in >24 hours (use updated timestamp as proxy)
      const lastUpdated = new Date(project.updated);
      const hoursSinceUpdate = (now.getTime() - lastUpdated.getTime()) / (1000 * 60 * 60);
      if (hoursSinceUpdate > 24) {
        score += 5;
      }

      // +3: has pending next_steps
      if (project.next_steps && project.next_steps.length > 0) {
        score += 3;
      }

      // +2: higher confidence projects are more worth investing in
      if (project.confidence >= 0.7) {
        score += 2;
      }

      // -5: low confidence (might need rethinking)
      if (project.confidence < 0.3) {
        score -= 5;
      }

      // Exponential backoff penalty for repeated failures
      const failures = this.failureCounts.get(project.project) ?? 0;
      if (failures > 0) {
        const backoffPenalty = Math.min(failures * 5, 20);
        score -= backoffPenalty;
        console.log("  " + project.project + ": -" + backoffPenalty + " (" + failures + " recent failures)");
      }

      // -10: check if project has exhausted its per-project daily budget
      const projectSpending = await this.budgetTracker.getProjectSpending(project.project);
      const perProjectDailyLimit = this.config.dailyBudgetUsd / Math.max(activeProjects.length, 1);
      if (projectSpending > perProjectDailyLimit) {
        score -= 10;
      }

      // Empty backlog guard: engineer agents with no open tickets get score 0
      if (agentType === "engineer") {
        try {
          const openTickets = await this.backlogManager.list({ status: "open" });
          if (openTickets.length === 0) {
            console.log("  " + project.project + ": no open backlog tickets — skipping");
            scored.push({ project, score: 0, agentType });
            continue;
          }
        } catch {
          // Backlog read failed — allow session to proceed
        }
      }

      // Quality-weighted scoring: if last 3 sessions were low-quality, try different agent
      const avgQuality = this.getRecentQualityAvg(project.project);
      if (avgQuality !== undefined && avgQuality < 25) {
        // Recent sessions unproductive — try a different agent type
        const sequence = PHASE_SEQUENCES[project.phase];
        if (sequence) {
          const currentIdx = sequence.indexOf(agentType);
          const nextIdx = (currentIdx + 1) % sequence.length;
          const altAgent = sequence[nextIdx] as AgentType;
          console.log("  " + project.project + ": low quality avg (" + avgQuality.toFixed(0) + ") — switching " + agentType + " → " + altAgent);
          agentType = altAgent;
        }
        score -= 3; // Slight penalty for low quality
      }

      // Base score: every active project gets a minimum viability
      score += 1;

      scored.push({ project, score, agentType });
    }

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    // Log scoring summary
    for (const s of scored) {
      console.log("  " + s.project.project + ": score=" + s.score + " agent=" + s.agentType);
    }

    return scored;
  }

  private hasUpcomingDeadline(project: ProjectStatus, now: Date, withinDays: number): boolean {
    const deadline = project.metrics?.deadline_epoch;
    if (!deadline) return false;
    const daysUntil = (deadline - now.getTime()) / (1000 * 60 * 60 * 24);
    return daysUntil > 0 && daysUntil <= withinDays;
  }

  private recordFailure(projectName: string): void {
    const current = this.failureCounts.get(projectName) ?? 0;
    this.failureCounts.set(projectName, current + 1);
  }

  private clearFailure(projectName: string): void {
    this.failureCounts.delete(projectName);
  }

  private async writeHeartbeat(): Promise<void> {
    const heartbeatPath = join(this.config.rootDir, ".deepwork.heartbeat");
    const data = {
      timestamp: new Date().toISOString(),
      cycle: this.cycleCount,
      activeSessions: Array.from(this.activeSessions.keys()),
      uptimeMs: Date.now() - this.startedAt,
    };
    await writeFile(heartbeatPath, JSON.stringify(data, null, 2), "utf-8");
  }

  private async shutdown(signal: string): Promise<void> {
    console.log("\nReceived " + signal + " -- shutting down gracefully...");
    this.running = false;
    this.abortController?.abort();
    if (this.activeSessions.size > 0) {
      console.log("Waiting for " + this.activeSessions.size + " active session(s) to finish...");
      await Promise.allSettled(
        Array.from(this.activeSessions.values()).map((t) => t.promise),
      );
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const timer = setTimeout(resolve, ms);
      this.abortController?.signal.addEventListener(
        "abort",
        () => {
          clearTimeout(timer);
          resolve();
        },
        { once: true },
      );
    });
  }
}
