import { join } from "node:path";
import { ProjectManager } from "./project-manager.js";
import { GitEngine } from "./git-engine.js";
import { SessionRunner, type SessionResult } from "./session-runner.js";
import { ActivityLogger } from "./logger.js";

export interface Session {
  projectName: string;
  sessionId?: string;
  worktreePath: string;
  branch: string;
  status: "running" | "paused" | "completed" | "failed";
  startedAt: string;
  result?: SessionResult;
}

export class SessionManager {
  private sessions = new Map<string, Session>();
  private projectManager: ProjectManager;
  private gitEngine: GitEngine;
  private sessionRunner: SessionRunner;
  private logger: ActivityLogger;
  private rootDir: string;

  constructor(projectManager: ProjectManager, gitEngine: GitEngine, rootDir: string = process.cwd()) {
    this.projectManager = projectManager;
    this.gitEngine = gitEngine;
    this.rootDir = rootDir;
    this.sessionRunner = new SessionRunner(rootDir);
    this.logger = new ActivityLogger(rootDir);
  }

  async startProject(
    projectName: string,
    agentType: "researcher" | "writer" | "reviewer" | "editor" | "strategist" = "researcher",
    options?: { maxTurns?: number; maxDurationMs?: number },
  ): Promise<Session> {
    const branch = `research/${projectName}`;
    const worktreePath = join(this.rootDir, ".worktrees", projectName);

    await this.gitEngine.createWorktree(worktreePath, branch);

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

    await this.stopProject(projectName);

    return session;
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
