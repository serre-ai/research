import { join } from "node:path";
import { readdir, readFile } from "node:fs/promises";
import { randomUUID } from "node:crypto";
import { ProjectManager } from "./project-manager.js";
import { GitEngine } from "./git-engine.js";
import { SessionRunner, type SessionResult, type AgentType } from "./session-runner.js";
import { ActivityLogger } from "./logger.js";
import type { KnowledgeGraph } from "./knowledge-graph.js";
import type { SessionBrief } from "./research-planner.js";

export type SessionOutputCategory = 'research' | 'writing' | 'infrastructure' | 'meta' | 'noise';

export interface SessionSignals {
  criticVerdict?: "ACCEPT" | "REVISE" | "REJECT";
  commitsCreated: number;
  statusYamlChanged: boolean;
  paperFilesChanged: boolean;
  experimentSpecCreated?: boolean;
  experimentSpecPath?: string;
  experimentSpecApproved?: boolean;
  experimentSpecRevisionRequested?: boolean;
  pushSkipped?: boolean;
  outputCategory?: SessionOutputCategory;
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
    dbPool?: import("pg").Pool | null,
  ) {
    this.projectManager = projectManager;
    this.gitEngine = gitEngine;
    this.rootDir = rootDir;
    this.sessionRunner = new SessionRunner(rootDir, knowledgeGraph, dbPool);
    this.logger = new ActivityLogger(rootDir);
  }

  async startProject(
    projectName: string,
    agentType: AgentType = "researcher",
    options?: { maxTurns?: number; maxDurationMs?: number },
  ): Promise<Session> {
    const sessionId = randomUUID().slice(0, 8);
    const branch = `agent/${projectName}/${sessionId}`;
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
    const sessionId = randomUUID().slice(0, 8);
    const branch = `agent/${brief.projectName}/${sessionId}`;
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

  private hasMeaningfulChanges(files: string[]): boolean {
    // Whitelist approach: a change is meaningful only if at least one file
    // matches a known productive pattern. Everything else (status reports,
    // session docs, strategist reviews) is considered noise.
    const MEANINGFUL_PATTERNS = [
      /\.tex$/, /\.bib$/,                    // Paper content
      /\.py$/, /\.ts$/, /\.tsx$/, /\.js$/,   // Code
      /\.sql$/, /\.csv$/, /\.jsonl$/,        // Data
      /experiments\//, /benchmarks\//,        // Experiment results
      /paper\//, /figures\//,                 // Paper artifacts
      /\.yaml$/, /\.yml$/,                   // Config (includes status.yaml)
    ];
    // Exclude status.yaml-only changes (just timestamp bumps)
    const meaningfulFiles = files.filter(f => {
      // Always noise
      if (/^\.forge|^\.worktrees|^node_modules|\.log$|^\.claude\/worktrees/.test(f)) return false;
      // Meaningful if matches whitelist
      return MEANINGFUL_PATTERNS.some(p => p.test(f));
    });
    // If the only yaml file changed is status.yaml and nothing else, it's noise
    if (meaningfulFiles.length === 1 && meaningfulFiles[0].endsWith('status.yaml')) return false;
    return meaningfulFiles.length > 0;
  }

  private classifyOutput(files: string[]): SessionOutputCategory {
    if (files.length === 0) return 'noise';

    let research = 0, writing = 0, infra = 0, meta = 0;

    for (const f of files) {
      if (/experiments\/|benchmarks\/|literature\/|\.csv$|\.jsonl$|results\//.test(f)) {
        research++;
      } else if (/projects\/.*\.py$/.test(f)) {
        // Python under projects/ is research, not infra
        research++;
      } else if (/paper\/.*\.tex$|paper\/.*\.bib$|figures\//.test(f)) {
        writing++;
      } else if (/orchestrator\/|site-next\/|scripts\/|\.ts$|\.tsx$|\.js$/.test(f)) {
        infra++;
      } else if (/\.py$/.test(f)) {
        // Python outside projects/ (scripts/, orchestrator/) is infra
        infra++;
      } else if (/status\.yaml$|docs\/reports\/|docs\/sessions\/|\.forge/.test(f)) {
        meta++;
      }
    }

    // If only status.yaml, it's meta
    if (files.length === 1 && files[0].endsWith('status.yaml')) return 'meta';

    // Return dominant category
    const ranked: [SessionOutputCategory, number][] = [
      ['research', research],
      ['writing', writing],
      ['infrastructure', infra],
      ['meta', meta],
    ];
    ranked.sort((a, b) => b[1] - a[1]);

    // If nothing matched any pattern, it's noise
    if (ranked[0][1] === 0) return 'noise';
    return ranked[0][0];
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

    // Check for experiment spec files in experiments/ subdirectories
    try {
      const experimentsDir = join(worktreePath, "experiments");
      const expDirs = await readdir(experimentsDir);
      for (const dir of expDirs) {
        try {
          const specPath = join(experimentsDir, dir, "spec.yaml");
          const specContent = await readFile(specPath, "utf-8");
          const statusMatch = specContent.match(/^status:\s*(\S+)/m);
          if (statusMatch) {
            const specStatus = statusMatch[1];
            const relativePath = `experiments/${dir}/spec.yaml`;
            if (specStatus === "draft") {
              signals.experimentSpecCreated = true;
              signals.experimentSpecPath = relativePath;
            }
            if (specStatus === "approved") {
              signals.experimentSpecApproved = true;
              signals.experimentSpecPath = relativePath;
            }
            // Parse the review block to find review.status
            const reviewBlock = specContent.match(/^review:\s*\n((?:\s+.*\n?)*)/m);
            if (reviewBlock) {
              const reviewStatusInBlock = reviewBlock[1].match(/status:\s*(\S+)/);
              if (reviewStatusInBlock) {
                const reviewStatus = reviewStatusInBlock[1];
                if (reviewStatus === "approved") {
                  signals.experimentSpecApproved = true;
                  signals.experimentSpecPath = relativePath;
                }
                if (reviewStatus === "revision_requested") {
                  signals.experimentSpecRevisionRequested = true;
                  signals.experimentSpecPath = relativePath;
                }
              }
            }
          }
        } catch {
          // No spec.yaml in this experiment directory — expected
        }
      }
    } catch {
      // No experiments directory — expected for non-experiment projects
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

    // Classify output
    try {
      const worktreeEngine = this.gitEngine.inDir(worktreePath);
      const changedFiles = await worktreeEngine.getPendingFiles();
      signals.outputCategory = this.classifyOutput(changedFiles);
    } catch {
      // Classification is best-effort
    }

    return signals;
  }

  async stopProject(projectName: string): Promise<void> {
    const session = this.sessions.get(projectName);
    if (!session) return;

    const worktreeEngine = this.gitEngine.inDir(session.worktreePath);

    // Check if there are any changes to commit
    const pendingFiles = await worktreeEngine.getPendingFiles();

    if (pendingFiles.length === 0) {
      // Nothing to commit — skip entirely
    } else if (this.hasMeaningfulChanges(pendingFiles)) {
      await worktreeEngine.commitAndPush(
        `chore(${projectName}): save session state`,
      );
    } else {
      // Still commit locally, but skip the push
      await worktreeEngine.commitAll(
        `chore(${projectName}): save session state`,
      );
      console.log(`[commit-gate] Skipping push for ${projectName} — no meaningful changes (${pendingFiles.length} noise-only files)`);
      if (session.signals) {
        session.signals.pushSkipped = true;
      }
    }

    if (session.status === "running") {
      session.status = "completed";
    }
    this.sessions.delete(projectName);

    await this.gitEngine.cleanupProjectWorktree(projectName);
    // Clean up agent branch
    if (session.branch && session.branch !== "main") {
      try {
        await this.gitEngine.deleteBranch(session.branch);
      } catch {
        // Branch may already be deleted or pushed to remote only
      }
    }
    console.log(`Stopped session for ${projectName}`);
  }

  getRunner(): SessionRunner {
    return this.sessionRunner;
  }

  getSession(projectName: string): Session | undefined {
    return this.sessions.get(projectName);
  }

  listSessions(): Session[] {
    return Array.from(this.sessions.values());
  }
}
