import { ProjectManager, type ProjectStatus } from "./project-manager.js";
import { SessionManager, type Session } from "./session-manager.js";
import { GitEngine } from "./git-engine.js";
import { BudgetTracker } from "./budget-tracker.js";
import { ActivityLogger } from "./logger.js";

export interface DaemonConfig {
  pollIntervalMs: number;
  maxConcurrentSessions: number;
  dailyBudgetUsd: number;
  rootDir: string;
}

interface ScoredProject {
  project: ProjectStatus;
  score: number;
  agentType: "researcher" | "writer" | "reviewer" | "editor" | "strategist";
}

const PHASE_TO_AGENT: Record<string, ScoredProject["agentType"]> = {
  "research": "researcher",
  "literature-review": "researcher",
  "drafting": "writer",
  "revision": "reviewer",
  "final": "editor",
};

const DEFAULT_CONFIG: DaemonConfig = {
  pollIntervalMs: 30 * 60 * 1000,
  maxConcurrentSessions: 2,
  dailyBudgetUsd: 40,
  rootDir: process.cwd(),
};

export class Daemon {
  private config: DaemonConfig;
  private projectManager: ProjectManager;
  private sessionManager: SessionManager;
  private gitEngine: GitEngine;
  private budgetTracker: BudgetTracker;
  private logger: ActivityLogger;
  private running = false;
  private activeSessions = new Map<string, Promise<Session>>();
  private abortController: AbortController | null = null;

  constructor(config: Partial<DaemonConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    const rootDir = this.config.rootDir;

    this.projectManager = new ProjectManager(rootDir);
    this.gitEngine = new GitEngine(rootDir);
    this.sessionManager = new SessionManager(this.projectManager, this.gitEngine, rootDir);
    this.logger = new ActivityLogger(rootDir);
    this.budgetTracker = new BudgetTracker(rootDir, this.logger);
  }

  async start(): Promise<void> {
    this.running = true;
    this.abortController = new AbortController();

    await this.logger.log({
      type: "daemon_start",
      data: {
        pollIntervalMs: this.config.pollIntervalMs,
        maxConcurrentSessions: this.config.maxConcurrentSessions,
        dailyBudgetUsd: this.config.dailyBudgetUsd,
      },
    });

    console.log("Deepwork daemon started");
    console.log(`  Poll interval: ${Math.round(this.config.pollIntervalMs / 60000)}m`);
    console.log(`  Max concurrent: ${this.config.maxConcurrentSessions}`);
    console.log(`  Daily budget: $${this.config.dailyBudgetUsd}`);

    process.on("SIGTERM", () => this.shutdown("SIGTERM"));
    process.on("SIGINT", () => this.shutdown("SIGINT"));

    while (this.running) {
      try {
        await this.cycle();
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

    await this.logger.log({ type: "daemon_stop", data: {} });
    console.log("Deepwork daemon stopped");
  }

  private async cycle(): Promise<void> {
    // Check budget before doing anything
    const budgetStatus = await this.budgetTracker.getStatus();
    if (budgetStatus.alertLevel === "exceeded") {
      console.log("Budget exceeded — skipping cycle");
      return;
    }

    // Clean up finished sessions
    for (const [name, promise] of this.activeSessions) {
      const settled = await Promise.race([promise.then(() => true), Promise.resolve(false)]);
      if (settled) {
        this.activeSessions.delete(name);
      }
    }

    const availableSlots = this.config.maxConcurrentSessions - this.activeSessions.size;
    if (availableSlots <= 0) {
      console.log(`All ${this.config.maxConcurrentSessions} session slots occupied — waiting`);
      return;
    }

    // Score and select projects
    const projects = await this.projectManager.listProjects();
    const scored = await this.scoreProjects(projects);

    // Filter out already-running projects and take top N
    const candidates = scored
      .filter((s) => !this.activeSessions.has(s.project.project))
      .filter((s) => s.score > 0)
      .slice(0, availableSlots);

    if (candidates.length === 0) {
      console.log("No eligible projects this cycle");
      return;
    }

    // Launch sessions for selected projects
    for (const candidate of candidates) {
      const { project, agentType } = candidate;
      console.log(`Launching ${agentType} session for ${project.project} (score: ${candidate.score})`);

      await this.logger.log({
        type: "session_start",
        project: project.project,
        agent: agentType,
        data: { score: candidate.score, phase: project.phase },
      });

      const sessionPromise = this.runSession(project.project, agentType);
      this.activeSessions.set(project.project, sessionPromise);
    }
  }

  private async runSession(
    projectName: string,
    agentType: ScoredProject["agentType"],
  ): Promise<Session> {
    try {
      const session = await this.sessionManager.startProject(projectName, agentType, {
        maxTurns: 50,
        maxDurationMs: 45 * 60 * 1000,
      });

      // Record spending
      if (session.result) {
        await this.budgetTracker.record({
          projectName,
          sessionId: session.result.sessionId,
          agentType,
          tokensInput: session.result.tokensUsed.input,
          tokensOutput: session.result.tokensUsed.output,
          costUsd: session.result.costUsd,
          model: "claude-sonnet-4-20250514",
        });

        await this.logger.log({
          type: "session_end",
          project: projectName,
          agent: agentType,
          data: {
            sessionId: session.result.sessionId,
            status: session.result.status,
            turnsUsed: session.result.turnsUsed,
            costUsd: session.result.costUsd,
            durationMs: session.result.durationMs,
            commitsCreated: session.result.commitsCreated.length,
            error: session.result.error,
          },
        });
      }

      return session;
    } catch (err) {
      await this.logger.log({
        type: "session_error",
        project: projectName,
        agent: agentType,
        data: { error: err instanceof Error ? err.message : String(err) },
      });
      throw err;
    }
  }

  private async scoreProjects(projects: ProjectStatus[]): Promise<ScoredProject[]> {
    const now = new Date();
    const scored: ScoredProject[] = [];

    for (const project of projects) {
      if (project.status !== "active") continue;

      let score = 0;
      const agentType = PHASE_TO_AGENT[project.phase] ?? "researcher";

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

      // -10: check if project has exhausted its daily budget
      const projectSpending = await this.budgetTracker.getProjectSpending(project.project);
      const perProjectDailyLimit = this.config.dailyBudgetUsd / Math.max(projects.filter((p) => p.status === "active").length, 1);
      if (projectSpending > perProjectDailyLimit) {
        score -= 10;
      }

      // Base score: every active project gets a minimum viability
      score += 1;

      scored.push({ project, score, agentType });
    }

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);
    return scored;
  }

  private hasUpcomingDeadline(project: ProjectStatus, now: Date, withinDays: number): boolean {
    // Check if project metrics or status has deadline info
    // Convention: status.yaml can have a `deadline` field in metrics as epoch ms
    const deadline = project.metrics?.deadline_epoch;
    if (!deadline) return false;
    const daysUntil = (deadline - now.getTime()) / (1000 * 60 * 60 * 24);
    return daysUntil > 0 && daysUntil <= withinDays;
  }

  private async shutdown(signal: string): Promise<void> {
    console.log(`\nReceived ${signal} — shutting down gracefully...`);
    this.running = false;
    this.abortController?.abort();

    // Wait for active sessions to finish
    if (this.activeSessions.size > 0) {
      console.log(`Waiting for ${this.activeSessions.size} active session(s) to finish...`);
      await Promise.allSettled(Array.from(this.activeSessions.values()));
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, ms);
      this.abortController?.signal.addEventListener("abort", () => {
        clearTimeout(timer);
        resolve();
      }, { once: true });
    });
  }
}
