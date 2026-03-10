import { writeFile } from "node:fs/promises";
import { join } from "node:path";
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

interface SessionTracker {
  promise: Promise<Session>;
  projectName: string;
  startedAt: number;
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

const MAX_SESSION_DURATION_MS = 60 * 60 * 1000; // 1 hour hard limit
const RETRY_DELAY_MS = 5 * 60 * 1000; // 5 min before retry
const MAX_BACKOFF_MS = 4 * 60 * 60 * 1000; // 4 hour max backoff

export class Daemon {
  private config: DaemonConfig;
  private projectManager: ProjectManager;
  private sessionManager: SessionManager;
  private gitEngine: GitEngine;
  private budgetTracker: BudgetTracker;
  private logger: ActivityLogger;
  private running = false;
  private activeSessions = new Map<string, SessionTracker>();
  private abortController: AbortController | null = null;
  private failureCounts = new Map<string, number>();
  private cycleCount = 0;
  private startedAt = 0;

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

    console.log("Deepwork daemon started");
    console.log(`  Poll interval: ${Math.round(this.config.pollIntervalMs / 60000)}m`);
    console.log(`  Max concurrent: ${this.config.maxConcurrentSessions}`);
    console.log(`  Daily budget: $${this.config.dailyBudgetUsd}`);

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

    await this.logger.log({ type: "daemon_stop", data: { cyclesCompleted: this.cycleCount } });
    console.log("Deepwork daemon stopped");
  }

  async getHealth(): Promise<{
    running: boolean;
    uptimeMs: number;
    cyclesCompleted: number;
    activeSessions: { project: string; runningMs: number }[];
    failureCounts: Record<string, number>;
  }> {
    const sessions = Array.from(this.activeSessions.values()).map((t) => ({
      project: t.projectName,
      runningMs: Date.now() - t.startedAt,
    }));

    return {
      running: this.running,
      uptimeMs: Date.now() - this.startedAt,
      cyclesCompleted: this.cycleCount,
      activeSessions: sessions,
      failureCounts: Object.fromEntries(this.failureCounts),
    };
  }

  private async cycle(): Promise<void> {
    this.cycleCount++;
    console.log(`\n--- Cycle ${this.cycleCount} ---`);

    // Check budget before doing anything
    const budgetStatus = await this.budgetTracker.getStatus();
    if (budgetStatus.alertLevel === "exceeded") {
      console.log("Budget exceeded — skipping cycle");
      return;
    }
    if (budgetStatus.alertLevel === "critical") {
      console.log(`Budget critical: $${budgetStatus.dailySpent.toFixed(2)}/$${budgetStatus.dailyLimit.toFixed(2)} daily`);
    }

    // Clean up finished sessions + detect stale ones
    await this.cleanupSessions();

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

      const promise = this.runSession(project.project, agentType);
      this.activeSessions.set(project.project, {
        promise,
        projectName: project.project,
        startedAt: Date.now(),
      });
    }
  }

  private async cleanupSessions(): Promise<void> {
    for (const [name, tracker] of this.activeSessions) {
      const settled = await Promise.race([tracker.promise.then(() => true), Promise.resolve(false)]);
      if (settled) {
        this.activeSessions.delete(name);
        continue;
      }

      // Stale session detection: kill if running > hard limit
      const runningMs = Date.now() - tracker.startedAt;
      if (runningMs > MAX_SESSION_DURATION_MS) {
        console.log(`Session for ${name} exceeded ${MAX_SESSION_DURATION_MS / 60000}min hard limit — marking stale`);
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

  private async runSession(
    projectName: string,
    agentType: ScoredProject["agentType"],
  ): Promise<Session> {
    const attempt = async (): Promise<Session> => {
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

        if (session.result.status === "completed") {
          this.clearFailure(projectName);
        } else {
          this.recordFailure(projectName);
        }
      }

      return session;
    };

    try {
      return await attempt();
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error(`Session failed for ${projectName}: ${errorMsg}`);

      await this.logger.log({
        type: "session_error",
        project: projectName,
        agent: agentType,
        data: { error: errorMsg, willRetry: true },
      });

      this.recordFailure(projectName);

      // Retry once after delay
      console.log(`Retrying ${projectName} in ${RETRY_DELAY_MS / 1000}s...`);
      await this.sleep(RETRY_DELAY_MS);

      try {
        return await attempt();
      } catch (retryErr) {
        const retryMsg = retryErr instanceof Error ? retryErr.message : String(retryErr);
        console.error(`Retry also failed for ${projectName}: ${retryMsg}`);

        await this.logger.log({
          type: "session_error",
          project: projectName,
          agent: agentType,
          data: { error: retryMsg, retryFailed: true },
        });

        this.recordFailure(projectName);
        throw retryErr;
      }
    }
  }

  private async scoreProjects(projects: ProjectStatus[]): Promise<ScoredProject[]> {
    const now = new Date();
    const activeProjects = projects.filter((p) => p.status === "active");
    const scored: ScoredProject[] = [];

    for (const project of activeProjects) {
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

      // Exponential backoff penalty for repeated failures
      const failures = this.failureCounts.get(project.project) ?? 0;
      if (failures > 0) {
        const backoffPenalty = Math.min(failures * 5, 20);
        score -= backoffPenalty;
        console.log(`  ${project.project}: -${backoffPenalty} (${failures} recent failures)`);
      }

      // -10: check if project has exhausted its per-project daily budget
      const projectSpending = await this.budgetTracker.getProjectSpending(project.project);
      const perProjectDailyLimit = this.config.dailyBudgetUsd / Math.max(activeProjects.length, 1);
      if (projectSpending > perProjectDailyLimit) {
        score -= 10;
      }

      // Base score: every active project gets a minimum viability
      score += 1;

      scored.push({ project, score, agentType });
    }

    // Sort by score descending
    scored.sort((a, b) => b.score - a.score);

    // Log scoring summary
    for (const s of scored) {
      console.log(`  ${s.project.project}: score=${s.score} agent=${s.agentType}`);
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
    console.log(`\nReceived ${signal} — shutting down gracefully...`);
    this.running = false;
    this.abortController?.abort();

    if (this.activeSessions.size > 0) {
      console.log(`Waiting for ${this.activeSessions.size} active session(s) to finish...`);
      await Promise.allSettled(Array.from(this.activeSessions.values()).map((t) => t.promise));
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const timer = setTimeout(resolve, ms);
      this.abortController?.signal.addEventListener("abort", () => {
        clearTimeout(timer);
        resolve();
      }, { once: true });
    });
  }
}
