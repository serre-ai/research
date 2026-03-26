import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { join } from "node:path";
import { rm, access } from "node:fs/promises";

const execAsync = promisify(execFile);

export interface WorktreeInfo {
  path: string;
  branch: string;
  head: string;
}

export interface PRInfo {
  number: number;
  title: string;
  headRefName: string;
  url?: string;
}

export class GitEngine {
  private cwd: string;

  constructor(cwd: string = process.cwd()) {
    this.cwd = cwd;
  }

  /** Run a git command in the engine's working directory. */
  private async git(...args: string[]): Promise<string> {
    const { stdout } = await execAsync("git", args, { cwd: this.cwd });
    return stdout.trim();
  }

  /** Run a gh CLI command. */
  private async gh(...args: string[]): Promise<string> {
    const { stdout } = await execAsync("gh", args, { cwd: this.cwd });
    return stdout.trim();
  }

  /** Create a GitEngine that operates in a different directory. */
  inDir(dir: string): GitEngine {
    return new GitEngine(dir);
  }

  // ── Branch operations ──────────────────────────────────────

  async createBranch(name: string, base: string = "main"): Promise<void> {
    await this.git("checkout", "-b", name, base);
  }

  async checkout(branch: string): Promise<void> {
    await this.git("checkout", branch);
  }

  async currentBranch(): Promise<string> {
    return this.git("rev-parse", "--abbrev-ref", "HEAD");
  }

  async branchExists(name: string): Promise<boolean> {
    try {
      await this.git("rev-parse", "--verify", name);
      return true;
    } catch {
      return false;
    }
  }

  async deleteBranch(name: string): Promise<void> {
    await this.git("branch", "-d", name);
  }

  // ── Sync operations ──────────────────────────────────────

  /** Fetch from origin and fast-forward the local branch ref to match remote.
   *  Uses update-ref instead of checkout+reset to avoid conflicts with worktrees
   *  and to avoid destroying any uncommitted changes in the working tree. */
  async syncToRemote(branch: string = "main"): Promise<void> {
    await this.git("fetch", "origin", branch);

    // Check for uncommitted changes — skip reset if working tree is dirty
    const status = await this.git("status", "--porcelain");
    if (status.length > 0) {
      console.log(`[GitEngine] Working tree dirty (${status.split("\n").length} files) — skipping reset`);
      return;
    }

    // Update the local branch ref without needing to be on that branch
    // (avoids "already checked out in worktree" errors)
    await this.git("update-ref", `refs/heads/${branch}`, `origin/${branch}`);
  }

  // ── Worktree operations ────────────────────────────────────

  async createWorktree(path: string, branch: string): Promise<string> {
    // Check if the branch is already checked out in an existing worktree
    const worktrees = await this.listWorktrees();
    const existing = worktrees.find((w) => w.branch === branch);
    if (existing) {
      console.log(`Branch '${branch}' already checked out at ${existing.path}, reusing`);
      return existing.path;
    }

    // Clean up stale directory not tracked by git
    try {
      await access(path);
      console.log(`Stale worktree directory at ${path}, removing`);
      await rm(path, { recursive: true, force: true });
      await this.git("worktree", "prune");
    } catch {
      // Directory doesn't exist — good
    }

    const exists = await this.branchExists(branch);
    if (exists) {
      await this.git("worktree", "add", path, branch);
    } else {
      await this.git("worktree", "add", "-b", branch, path);
    }
    return path;
  }

  async removeWorktree(path: string): Promise<void> {
    await this.git("worktree", "remove", path, "--force");
  }

  async listWorktrees(): Promise<WorktreeInfo[]> {
    const output = await this.git("worktree", "list", "--porcelain");
    const worktrees: WorktreeInfo[] = [];
    let current: Partial<WorktreeInfo> = {};

    for (const line of output.split("\n")) {
      if (line.startsWith("worktree ")) {
        current.path = line.slice(9);
      } else if (line.startsWith("HEAD ")) {
        current.head = line.slice(5, 12);
      } else if (line.startsWith("branch ")) {
        current.branch = line.replace("branch refs/heads/", "");
      } else if (line === "") {
        if (current.path) {
          worktrees.push(current as WorktreeInfo);
        }
        current = {};
      }
    }
    if (current.path) worktrees.push(current as WorktreeInfo);
    return worktrees;
  }

  // ── Working tree status ────────────────────────────────────

  async isDirty(): Promise<boolean> {
    const output = await this.git("status", "--porcelain");
    return output.length > 0;
  }

  async status(): Promise<string> {
    return this.git("status", "--short");
  }

  async diffStat(): Promise<string> {
    try {
      return await this.git("diff", "--stat");
    } catch {
      return "";
    }
  }

  async diffFrom(base: string): Promise<string> {
    try {
      return await this.git("diff", `${base}...HEAD`, "--stat");
    } catch {
      return "";
    }
  }

  /** List files with uncommitted changes (staged + unstaged). */
  async getPendingFiles(): Promise<string[]> {
    try {
      const output = await this.git("status", "--porcelain");
      return output.split("\n").filter(Boolean).map(line => line.slice(3).trim());
    } catch {
      return [];
    }
  }

  /** Compute a content hash of uncommitted changes. */
  async diffContentHash(): Promise<string> {
    try {
      const diff = await this.git("diff", "HEAD");
      if (!diff) return "";
      const { createHash } = await import("node:crypto");
      return createHash("sha256").update(diff).digest("hex").slice(0, 16);
    } catch {
      return "";
    }
  }

  // ── Commit operations ──────────────────────────────────────

  async stageAll(): Promise<void> {
    await this.git("add", "-A");
  }

  async stageFiles(...files: string[]): Promise<void> {
    await this.git("add", ...files);
  }

  async commit(message: string): Promise<string> {
    await this.git("commit", "-m", message);
    return this.git("rev-parse", "--short", "HEAD");
  }

  /** Stage all changes and commit. Returns null if nothing to commit. */
  async commitAll(message: string): Promise<string | null> {
    if (!(await this.isDirty())) return null;
    await this.stageAll();
    return this.commit(message);
  }

  async latestCommitHash(): Promise<string> {
    return this.git("rev-parse", "--short", "HEAD");
  }

  async log(count: number = 10): Promise<string[]> {
    const output = await this.git("log", "--oneline", `-${count}`);
    return output.split("\n").filter(Boolean);
  }

  async logBetween(base: string, head: string = "HEAD"): Promise<string[]> {
    try {
      const output = await this.git("log", "--oneline", `${base}..${head}`);
      return output.split("\n").filter(Boolean);
    } catch {
      return [];
    }
  }

  /**
   * Get files changed between two refs.
   */
  async filesBetween(base: string, head: string = "HEAD"): Promise<string[]> {
    try {
      const output = await this.git("diff", "--name-only", `${base}...${head}`);
      return output.split("\n").filter(Boolean);
    } catch {
      return [];
    }
  }

  /**
   * Check that all changed files are within the allowed scope for a project.
   * Returns list of out-of-scope files. Empty list = all files in scope.
   */
  scopeCheck(changedFiles: string[], projectName: string): string[] {
    // Platform sessions can touch orchestrator, scripts, docs, .claude, shared
    const platformPrefixes = [
      "orchestrator/", "scripts/", "docs/", ".claude/", "shared/",
      "ideas/", "CLAUDE.md", "config.yaml", "budget.yaml",
    ];

    return changedFiles.filter((file) => {
      if (projectName === "_platform") {
        return !platformPrefixes.some((p) => file.startsWith(p));
      }
      // Project sessions can only touch their project directory
      const projectPrefix = `projects/${projectName}/`;
      return !file.startsWith(projectPrefix);
    });
  }

  /**
   * Remove out-of-scope changes by resetting those files to the base branch state.
   * Returns the list of files that were reset.
   */
  async enforceScopeGuard(projectName: string, base: string = "main"): Promise<string[]> {
    const changedFiles = await this.filesBetween(base);
    const violations = this.scopeCheck(changedFiles, projectName);

    if (violations.length === 0) return [];

    console.log(`[ScopeGuard] ${violations.length} out-of-scope file(s) in ${projectName} session:`);
    for (const f of violations.slice(0, 10)) {
      console.log(`  - ${f}`);
    }
    if (violations.length > 10) {
      console.log(`  ... and ${violations.length - 10} more`);
    }

    // Reset out-of-scope files to their state on the base branch
    for (const file of violations) {
      try {
        await this.git("checkout", base, "--", file);
      } catch {
        // File may not exist on base (was newly created) — remove it
        try {
          await this.git("rm", "-f", file);
        } catch { /* ignore */ }
      }
    }

    // Amend the last commit if there are staged changes from the resets
    try {
      const status = await this.git("status", "--porcelain");
      if (status.trim()) {
        await this.git("add", "-A");
        await this.git("commit", "--amend", "--no-edit");
        console.log(`[ScopeGuard] Amended last commit to remove ${violations.length} out-of-scope file(s)`);
      }
    } catch { /* ignore */ }

    return violations;
  }

  // ── Remote operations ──────────────────────────────────────

  async push(branch?: string): Promise<void> {
    const b = branch ?? (await this.currentBranch());
    await this.git("push", "-u", "origin", b);
  }

  async pushSafe(branch?: string): Promise<boolean> {
    try {
      await this.push(branch);
      return true;
    } catch {
      return false;
    }
  }

  async pull(branch?: string): Promise<void> {
    const b = branch ?? (await this.currentBranch());
    await this.git("pull", "origin", b);
  }

  async fetch(): Promise<void> {
    await this.git("fetch", "--all", "--prune");
  }

  // ── PR operations ──────────────────────────────────────────

  async createPR(opts: {
    title: string;
    body: string;
    base?: string;
    draft?: boolean;
  }): Promise<string> {
    const args = [
      "pr",
      "create",
      "--title",
      opts.title,
      "--body",
      opts.body,
      "--base",
      opts.base ?? "main",
    ];
    if (opts.draft) args.push("--draft");
    return this.gh(...args);
  }

  async listOpenPRs(branch?: string): Promise<PRInfo[]> {
    const args = [
      "pr",
      "list",
      "--state",
      "open",
      "--json",
      "number,title,headRefName,url",
    ];
    if (branch) args.push("--head", branch);
    try {
      const output = await this.gh(...args);
      return JSON.parse(output);
    } catch {
      return [];
    }
  }

  async mergePR(number: number): Promise<void> {
    await this.gh("pr", "merge", String(number), "--merge", "--delete-branch");
  }

  /** Create a PR summarizing session work. Returns PR URL or null if skipped. */
  async createSessionPR(opts: {
    projectName: string;
    branch: string;
    sessionId: string;
    status: string;
    turnsUsed: number;
    costUsd: number;
    durationMs: number;
    commits: string[];
  }): Promise<string | null> {
    // Enforce scope guard — remove any out-of-scope changes before pushing
    await this.enforceScopeGuard(opts.projectName);

    // Skip if no commits ahead of main (scope guard may have removed all changes)
    const newCommits = await this.logBetween("main", "HEAD");
    if (newCommits.length === 0) return null;

    // Use the current branch if already on an agent branch, otherwise create ephemeral
    const currentBranch = await this.currentBranch();
    let prBranch: string;
    if (currentBranch !== "main" && currentBranch !== "HEAD") {
      prBranch = currentBranch; // Already on agent branch
    } else {
      // Legacy: create ephemeral branch
      const shortId = opts.sessionId.slice(0, 8);
      prBranch = `session/${opts.projectName}/${shortId}`;
      await this.git("checkout", "-b", prBranch);
    }

    // Skip if PR already open for this branch
    const openPRs = await this.listOpenPRs(prBranch);
    if (openPRs.length > 0) return null;

    // Push the branch to remote
    await this.pushSafe(prBranch);

    const shortId = opts.sessionId.slice(0, 8);
    const commitList = newCommits.slice(0, 15).map((c) => `- ${c}`).join("\n");
    const durationMin = Math.round(opts.durationMs / 60000);

    return this.createPR({
      title: `research(${opts.projectName}): session ${shortId}`,
      body: [
        `## Session Summary`,
        ``,
        `| Metric | Value |`,
        `|--------|-------|`,
        `| Status | ${opts.status} |`,
        `| Turns | ${opts.turnsUsed} |`,
        `| Cost | $${opts.costUsd.toFixed(4)} |`,
        `| Duration | ${durationMin}m |`,
        `| Commits | ${newCommits.length} |`,
        ``,
        `## Commits`,
        commitList,
        newCommits.length > 15 ? `\n...and ${newCommits.length - 15} more` : "",
        ``,
        `## Project`,
        `- **Branch**: \`${prBranch}\``,
        `- **Session**: \`${opts.sessionId}\``,
      ].join("\n"),
    });
  }

  // ── High-level workflow ────────────────────────────────────

  /**
   * Set up an isolated worktree for a research project.
   * Creates the branch if it doesn't exist, reuses it if it does.
   */
  async setupProjectWorktree(
    projectName: string,
    basePath: string = ".worktrees",
  ): Promise<{ worktreePath: string; branch: string; engine: GitEngine }> {
    const branch = "main";
    const requestedPath = join(basePath, projectName);
    const actualPath = await this.createWorktree(requestedPath, branch);
    return {
      worktreePath: actualPath,
      branch,
      engine: this.inDir(actualPath),
    };
  }

  /** Commit all changes and push to remote. */
  async commitAndPush(message: string): Promise<string | null> {
    const hash = await this.commitAll(message);
    if (hash) await this.pushSafe();
    return hash;
  }

  /** Create a milestone PR from the current branch to main. */
  async createMilestonePR(opts: {
    projectName: string;
    milestone: string;
    summary: string;
  }): Promise<string> {
    const branch = await this.currentBranch();
    await this.pushSafe(branch);

    const commits = await this.logBetween("main", "HEAD");
    const commitList = commits
      .slice(0, 10)
      .map((c) => `- ${c}`)
      .join("\n");

    return this.createPR({
      title: `research(${opts.projectName}): ${opts.milestone}`,
      body: [
        `## Summary`,
        opts.summary,
        ``,
        `## Commits`,
        commitList,
        ``,
        `## Project`,
        `- **Name**: ${opts.projectName}`,
        `- **Branch**: \`${branch}\``,
        `- **Milestone**: ${opts.milestone}`,
      ].join("\n"),
    });
  }

  /** Clean up a project's worktree. */
  async cleanupProjectWorktree(
    projectName: string,
    basePath: string = ".worktrees",
  ): Promise<void> {
    const worktreePath = join(basePath, projectName);
    try {
      await this.removeWorktree(worktreePath);
    } catch {
      // Already cleaned up
    }
  }
}
