import { join } from "node:path";
import { readdir, readFile } from "node:fs/promises";
import { ProjectManager } from "./project-manager.js";
import { GitEngine } from "./git-engine.js";
import { SessionRunner, type SessionResult, type AgentType } from "./session-runner.js";
import { ActivityLogger } from "./logger.js";
import type { KnowledgeGraph } from "./knowledge-graph.js";
import type { SessionBrief } from "./research-planner.js";

export interface SessionSignals {
  criticVerdict?: "ACCEPT" | "REVISE" | "REJECT";
  commitsCreated: number;
  statusYamlChanged: boolean;
  paperFilesChanged: boolean;
}

export interface Session {
  projectName: string;
  sessionId?: string;
  worktreePath: string;
  branch: string;
  status: "running" | "paused" | "completed" | "failed";
  startedAt: string;
  result?: SessionResult;
  signals?: SessionSignals;
}

export class SessionManager {
  private sessions = new Map<string, Session>();
  private projectManager: ProjectManager;
  private gitEngine: GitEngine;
  private sessionRunner: SessionRunner;
  private logger: ActivityLogger;
  private rootDir: string;

  constructor(
    projectManager: ProjectManager,
    gitEngine: GitEngine,
    rootDir: string = process.cwd(),
    knowledgeGraph?: KnowledgeGraph | null,
  ) {
    this.projectManager = projectManager;
    this.gitEngine = gitEngine;
    this.rootDir = rootDir;
    this.sessionRunner = new SessionRunner(rootDir, knowledgeGraph);
    this.logger = new ActivityLogger(rootDir);
  }

  async startProject(
    projectName: string,
    agentType: AgentType = "researcher",
    options?: { maxTurns?: number; maxDurationMs?: number },
  ): Promise<Session> {
    const branch = `research/${projectName}`;
    const requestedPath = join(this.rootDir, ".worktrees", projectName);
    const worktreePath = await this.gitEngine.createWorktree(requestedPath, branch);

    const session: Session = {
      projectName,
      worktreePath,
      branch,
      status: "running",
      startedAt: new Date().toISOString(),
    };
    this.sessions.set(projectName, session);

    console.log(`Started session for ${projectName}`);
    console.log(`  Agent: ${agentType}`);
    console.log(`  Branch: ${branch}`);
    console.log(`  Worktree: ${worktreePath}`);

    try {
      const result = await this.sessionRunner.run({
        projectName,
        agentType,
        maxTurns: options?.maxTurns ?? 50,
        maxDurationMs: options?.maxDurationMs ?? 45 * 60 * 1000,
        worktreePath,
      });

      session.sessionId = result.sessionId;
      session.result = result;
      session.status = result.status === "completed" ? "completed" : "failed";

      console.log(`Session finished for ${projectName}: ${result.status}`);
      console.log(`  Turns: ${result.turnsUsed} | Cost: $${result.costUsd.toFixed(4)} | Duration: ${Math.round(result.durationMs / 1000)}s`);

      if (result.error) {
        console.log(`  Error: ${result.error}`);
      }
    } catch (err) {
      session.status = "failed";
      console.error(`Session crashed for ${projectName}:`, err);
    }

    // Auto-create PR if session produced commits
    if (session.result && session.result.commitsCreated.length > 0) {
      try {
        const worktreeEngine = this.gitEngine.inDir(session.worktreePath);
        const prUrl = await worktreeEngine.createSessionPR({
          projectName,
          branch: session.branch,
          sessionId: session.result.sessionId,
          status: session.result.status,
          turnsUsed: session.result.turnsUsed,
          costUsd: session.result.costUsd,
          durationMs: session.result.durationMs,
          commits: session.result.commitsCreated,
        });

        if (prUrl) {
          console.log(`  PR created: ${prUrl}`);
          await this.logger.log({
            type: "pr_created",
            project: projectName,
            data: { url: prUrl, sessionId: session.result.sessionId },
          });
        }
      } catch (err) {
        console.error(`  Failed to create PR: ${err instanceof Error ? err.message : err}`);
      }
    }

    // Detect session signals before worktree cleanup
    session.signals = await this.detectSignals(session.worktreePath, session.result);

    await this.stopProject(projectName);

    return session;
  }

  /** Start a session using a planner-generated brief with specific objectives and constraints. */
  async startProjectWithBrief(brief: SessionBrief): Promise<Session> {
    const branch = `research/${brief.projectName}`;
    const requestedPath = join(this.rootDir, ".worktrees", brief.projectName);
    const worktreePath = await this.gitEngine.createWorktree(requestedPath, branch);

    const session: Session = {
      projectName: brief.projectName,
      worktreePath,
      branch,
      status: "running",
      startedAt: new Date().toISOString(),
    };
    this.sessions.set(brief.projectName, session);

    console.log(`Started session for ${brief.projectName}`);
    console.log(`  Agent: ${brief.agentType} | Strategy: ${brief.strategy}`);
    console.log(`  Branch: ${branch}`);
    console.log(`  Objective: ${brief.objective.slice(0, 120)}`);

    try {
      const result = await this.sessionRunner.runWithBrief(brief, worktreePath);
      session.sessionId = result.sessionId;
      session.result = result;
      session.status = result.status === "completed" ? "completed" : "failed";

      console.log(`Session finished for ${brief.projectName}: ${result.status}`);
      console.log(`  Turns: ${result.turnsUsed} | Cost: $${result.costUsd.toFixed(4)} | Duration: ${Math.round(result.durationMs / 1000)}s`);

      if (result.error) console.log(`  Error: ${result.error}`);
    } catch (err) {
      session.status = "failed";
      console.error(`Session crashed for ${brief.projectName}:`, err);
    }

    // Auto-create PR if session produced commits
    if (session.result && session.result.commitsCreated.length > 0) {
      try {
        const worktreeEngine = this.gitEngine.inDir(session.worktreePath);
        const prUrl = await worktreeEngine.createSessionPR({
          projectName: brief.projectName,
          branch: session.branch,
          sessionId: session.result.sessionId,
          status: session.result.status,
          turnsUsed: session.result.turnsUsed,
          costUsd: session.result.costUsd,
          durationMs: session.result.durationMs,
          commits: session.result.commitsCreated,
        });

        if (prUrl) {
          console.log(`  PR created: ${prUrl}`);
          await this.logger.log({
            type: "pr_created",
            project: brief.projectName,
            data: { url: prUrl, sessionId: session.result.sessionId },
          });
        }
      } catch (err) {
        console.error(`  Failed to create PR: ${err instanceof Error ? err.message : err}`);
      }
    }

    session.signals = await this.detectSignals(session.worktreePath, session.result);
    await this.stopProject(brief.projectName);
    return session;
  }

  private async detectSignals(worktreePath: string, result?: SessionResult): Promise<SessionSignals> {
    const signals: SessionSignals = {
      commitsCreated: result?.commitsCreated.length ?? 0,
      statusYamlChanged: false,
      paperFilesChanged: false,
    };

    // Check for critic verdict in most recent review file
    try {
      const reviewsDir = join(worktreePath, "reviews");
      const files = await readdir(reviewsDir);
      const criticReviews = files.filter((f) => f.startsWith("critic-review-")).sort().reverse();
      if (criticReviews.length > 0) {
        const content = await readFile(join(reviewsDir, criticReviews[0]), "utf-8");
        const match = content.match(/\*\*Verdict\*\*:\s*(ACCEPT|REVISE|REJECT)/i);
        if (match) {
          signals.criticVerdict = match[1].toUpperCase() as SessionSignals["criticVerdict"];
        }
      }
    } catch {
      // No reviews directory — expected for non-critic sessions
    }

    // Check which files were modified by this session
    if (result && result.commitsCreated.length > 0) {
      try {
        const { execSync } = await import("node:child_process");
        const diff = execSync(
          `git diff --name-only HEAD~${result.commitsCreated.length} HEAD`,
          { cwd: worktreePath, encoding: "utf-8", timeout: 5000 },
        ).trim();
        signals.statusYamlChanged = diff.includes("status.yaml");
        signals.paperFilesChanged = /\.tex$/m.test(diff);
      } catch {
        signals.statusYamlChanged = result.commitsCreated.length > 1;
      }
    }

    return signals;
  }

  async stopProject(projectName: string): Promise<void> {
    const session = this.sessions.get(projectName);
    if (!session) return;

    const worktreeEngine = this.gitEngine.inDir(session.worktreePath);
    await worktreeEngine.commitAndPush(
      `chore(${projectName}): save session state`,
    );

    if (session.status === "running") {
      session.status = "completed";
    }
    this.sessions.delete(projectName);

    await this.gitEngine.cleanupProjectWorktree(projectName);
    console.log(`Stopped session for ${projectName}`);
  }

  getSession(projectName: string): Session | undefined {
    return this.sessions.get(projectName);
  }

  listSessions(): Session[] {
    return Array.from(this.sessions.values());
  }
}
