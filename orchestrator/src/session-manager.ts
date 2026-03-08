import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ProjectManager } from "./project-manager.js";
import { GitEngine } from "./git-engine.js";

interface Session {
  projectName: string;
  sessionId?: string;
  worktreePath: string;
  branch: string;
  status: "running" | "paused" | "completed";
  startedAt: string;
}

export class SessionManager {
  private sessions = new Map<string, Session>();
  private projectManager: ProjectManager;
  private gitEngine: GitEngine;

  constructor(projectManager: ProjectManager, gitEngine: GitEngine) {
    this.projectManager = projectManager;
    this.gitEngine = gitEngine;
  }

  async startProject(projectName: string): Promise<Session> {
    const status = await this.projectManager.getProjectStatus(projectName);
    const branch = `research/${projectName}`;
    const worktreePath = join(process.cwd(), ".worktrees", projectName);

    // Set up isolated worktree
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
    console.log(`  Branch: ${branch}`);
    console.log(`  Worktree: ${worktreePath}`);

    // Read project files for the agent prompt
    const brief = await readFile(
      join("projects", projectName, "BRIEF.md"),
      "utf-8",
    );
    const projectClaude = await readFile(
      join("projects", projectName, "CLAUDE.md"),
      "utf-8",
    ).catch(() => "");

    const prompt = this.buildPrompt(projectName, brief, projectClaude, status);

    // TODO: Integrate with @anthropic-ai/claude-agent-sdk
    console.log("\nAgent prompt prepared. Launch with Claude SDK or manually:\n");
    console.log(`  cd ${worktreePath}`);
    console.log(`  claude -p "${prompt.slice(0, 80)}..."\n`);

    return session;
  }

  private buildPrompt(
    projectName: string,
    brief: string,
    projectClaude: string,
    status: {
      phase: string;
      current_focus?: string;
      next_steps?: string[];
      progress?: Record<string, unknown>;
    },
  ): string {
    const nextSteps = status.next_steps
      ?.map((s: string) => `  - ${s}`)
      .join("\n") ?? "  - Check status.yaml for current tasks";

    return `You are an autonomous research agent working on the "${projectName}" project.

## Research Brief
${brief}

## Project Instructions
${projectClaude}

## Current State
- Phase: ${status.phase}
- Focus: ${status.current_focus ?? "See status.yaml"}
- Next steps:
${nextSteps}

## Workflow
1. Read the project files to understand current state
2. Work autonomously — make all decisions yourself using your best judgment
3. Use extended thinking for critical research decisions
4. Make frequent conventional commits: type(${projectName}): description
5. Update status.yaml after significant progress
6. Log all decisions in decisions_made with date and rationale
7. Push changes to remote regularly
8. Create a PR to main when you reach a milestone
`;
  }

  async stopProject(projectName: string): Promise<void> {
    const session = this.sessions.get(projectName);
    if (!session) return;

    // Commit any pending changes
    const worktreeEngine = this.gitEngine.inDir(session.worktreePath);
    await worktreeEngine.commitAndPush(
      `chore(${projectName}): save session state`,
    );

    session.status = "completed";
    this.sessions.delete(projectName);

    // Clean up worktree
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
