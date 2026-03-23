import { readFile, readdir } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { GitEngine } from "./git-engine.js";
import { TranscriptWriter } from "./transcript-writer.js";
import { calculateCost as calcModelCost } from "./pricing.js";
import type { KnowledgeGraph, ClaimRow } from "./knowledge-graph.js";
import type { SessionBrief } from "./research-planner.js";

export type AgentType =
  | "researcher" | "writer" | "reviewer" | "editor"
  | "critic" | "experimenter" | "theorist" | "strategist" | "scout"
  | "engineer";

/** Canonical mapping from project phase to default agent type. */
export const PHASE_TO_AGENT: Record<string, AgentType> = {
  "research": "researcher",
  "literature-review": "researcher",
  "empirical-evaluation": "experimenter",
  "analysis": "experimenter",
  "drafting": "writer",
  "submission-prep": "writer",
  "revision": "writer",
  "paper-finalization": "writer",
  "final": "editor",
  "active": "engineer",
};

const DEFAULT_MAX_TURNS = 50;
const DEFAULT_MAX_DURATION_MS = 45 * 60 * 1000;

export interface SessionConfig {
  projectName: string;
  agentType: AgentType;
  maxTurns: number;
  maxDurationMs: number;
  thinkingLevel?: "standard" | "extended";
  worktreePath?: string;
}

export interface SessionResult {
  sessionId: string;
  projectName: string;
  agentType: string;
  status: "completed" | "failed" | "timeout" | "budget_exceeded";
  turnsUsed: number;
  tokensUsed: { input: number; output: number };
  costUsd: number;
  durationMs: number;
  commitsCreated: string[];
  transcriptPath?: string;
  error?: string;
}

/** Max claims to inject per agent type. Writers need broad context; engineers less. */
const KNOWLEDGE_LIMITS: Record<string, number> = {
  writer: 25,
  critic: 20,
  reviewer: 20,
  researcher: 15,
  strategist: 15,
  experimenter: 10,
  editor: 10,
  scout: 10,
  theorist: 15,
  engineer: 8,
};

export class SessionRunner {
  private rootDir: string;
  private knowledgeGraph: KnowledgeGraph | null;
  private dbPool: import("pg").Pool | null;

  constructor(rootDir: string = process.cwd(), knowledgeGraph?: KnowledgeGraph | null, dbPool?: import("pg").Pool | null) {
    this.rootDir = rootDir;
    this.knowledgeGraph = knowledgeGraph ?? null;
    this.dbPool = dbPool ?? null;
  }

  async run(config: SessionConfig): Promise<SessionResult> {
    const sessionId = randomUUID();
    const writer = new TranscriptWriter(this.rootDir, config.projectName, sessionId);
    const maxTurns = config.maxTurns || DEFAULT_MAX_TURNS;
    const maxDurationMs = config.maxDurationMs || DEFAULT_MAX_DURATION_MS;
    const worktreePath = config.worktreePath ?? join(this.rootDir, ".worktrees", config.projectName);
    const startTime = Date.now();
    const prompt = await this.buildPrompt(config.projectName, config.agentType);

    const commitsCreated: string[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let resultMessage: any;
    let error: string | undefined;
    let sessionStatus: SessionResult["status"] = "completed";

    // Record commit count before session to count only new commits
    const preSessionEngine = new GitEngine(worktreePath);
    let preSessionCommitCount = 0;
    try {
      const preLogs = await preSessionEngine.logBetween("main");
      preSessionCommitCount = preLogs.length;
    } catch {
      // New branch with no commits yet
    }

    const abortController = new AbortController();
    const timeout = setTimeout(() => abortController.abort(), maxDurationMs);

    try {
      const stream = query({
        prompt,
        options: {
          cwd: worktreePath,
          allowedTools: [
            "Read", "Write", "Edit", "Bash", "Glob", "Grep",
            "WebSearch", "WebFetch",
          ],
          permissionMode: "acceptEdits",
          maxTurns,
          // maxBudgetUsd not supported by SDK — budget enforced via prompt instructions
          abortController,
          systemPrompt: {
            type: "preset",
            preset: "claude_code",
            append: prompt,
          },
        },
      });

      for await (const message of stream) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if ((message as any).type !== "stream_event") {
          await writer.write(message);
        }
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if ((message as any).type === "result") {
          resultMessage = message;
        }
      }
    } catch (err) {
      if (abortController.signal.aborted) {
        sessionStatus = "timeout";
        error = "Session exceeded maximum duration";
      } else {
        sessionStatus = "failed";
        error = err instanceof Error ? err.message : String(err);
      }
    } finally {
      clearTimeout(timeout);
    }

    if (resultMessage) {
      if (resultMessage.subtype === "error_max_turns") {
        sessionStatus = "timeout";
        error = "Session exceeded maximum turns";
      } else if (resultMessage.subtype === "error_max_budget_usd") {
        sessionStatus = "budget_exceeded";
        error = "Session exceeded budget limit";
      } else if (resultMessage.subtype === "error_during_execution") {
        sessionStatus = "failed";
        error = "errors" in resultMessage ? resultMessage.errors.join("; ") : "Unknown execution error";
      }
    }

    const durationMs = Date.now() - startTime;
    const worktreeEngine = new GitEngine(worktreePath);
    try {
      // Count only commits made during THIS session, not all branch commits
      const allLogs = await worktreeEngine.logBetween("main");
      const sessionLogs = allLogs.slice(0, allLogs.length - preSessionCommitCount);
      commitsCreated.push(...sessionLogs.map((l: string) => l.split(" ")[0]));
    } catch {
      // No commits yet
    }

    const tokensUsed = this.extractTokenUsage(resultMessage);
    const costUsd = resultMessage?.total_cost_usd ?? this.calculateCost(tokensUsed);

    return {
      sessionId,
      projectName: config.projectName,
      agentType: config.agentType,
      status: sessionStatus,
      turnsUsed: resultMessage?.num_turns ?? 0,
      tokensUsed,
      costUsd,
      durationMs,
      commitsCreated,
      transcriptPath: writer.getFilePath(),
      error,
    };
  }

  /** Run a session using a planner-generated brief with specific objectives and context. */
  async runWithBrief(brief: SessionBrief, worktreePath: string): Promise<SessionResult> {
    const sessionId = randomUUID();
    const writer = new TranscriptWriter(this.rootDir, brief.projectName, sessionId);
    const maxTurns = brief.constraints.maxTurns;
    const maxDurationMs = brief.constraints.maxDurationMs;
    const startTime = Date.now();

    // Build prompt using the brief's curated context
    const prompt = await this.buildBriefPrompt(brief);

    const commitsCreated: string[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let resultMessage: any;
    let error: string | undefined;
    let sessionStatus: SessionResult["status"] = "completed";

    const preSessionEngine = new GitEngine(worktreePath);
    let preSessionCommitCount = 0;
    try {
      const preLogs = await preSessionEngine.logBetween("main");
      preSessionCommitCount = preLogs.length;
    } catch { /* new branch */ }

    const abortController = new AbortController();
    const timeout = setTimeout(() => abortController.abort(), maxDurationMs);

    try {
      const stream = query({
        prompt,
        options: {
          cwd: worktreePath,
          allowedTools: [
            "Read", "Write", "Edit", "Bash", "Glob", "Grep",
            "WebSearch", "WebFetch",
          ],
          permissionMode: "acceptEdits",
          maxTurns,
          // maxBudgetUsd not supported by SDK — budget enforced via prompt instructions
          abortController,
          systemPrompt: {
            type: "preset",
            preset: "claude_code",
            append: prompt,
          },
        },
      });

      for await (const message of stream) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if ((message as any).type !== "stream_event") {
          await writer.write(message);
        }
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        if ((message as any).type === "result") {
          resultMessage = message;
        }
      }
    } catch (err) {
      if (abortController.signal.aborted) {
        sessionStatus = "timeout";
        error = "Session exceeded maximum duration";
      } else {
        sessionStatus = "failed";
        error = err instanceof Error ? err.message : String(err);
      }
    } finally {
      clearTimeout(timeout);
    }

    if (resultMessage) {
      if (resultMessage.subtype === "error_max_turns") {
        sessionStatus = "timeout";
        error = "Session exceeded maximum turns";
      } else if (resultMessage.subtype === "error_max_budget_usd") {
        sessionStatus = "budget_exceeded";
        error = "Session exceeded budget limit";
      } else if (resultMessage.subtype === "error_during_execution") {
        sessionStatus = "failed";
        error = "errors" in resultMessage ? resultMessage.errors.join("; ") : "Unknown execution error";
      }
    }

    const durationMs = Date.now() - startTime;
    const worktreeEngine = new GitEngine(worktreePath);
    try {
      const allLogs = await worktreeEngine.logBetween("main");
      const sessionLogs = allLogs.slice(0, allLogs.length - preSessionCommitCount);
      commitsCreated.push(...sessionLogs.map((l: string) => l.split(" ")[0]));
    } catch { /* no commits */ }

    const tokensUsed = this.extractTokenUsage(resultMessage);
    const costUsd = resultMessage?.total_cost_usd ?? this.calculateCost(tokensUsed);

    return {
      sessionId,
      projectName: brief.projectName,
      agentType: brief.agentType,
      status: sessionStatus,
      turnsUsed: resultMessage?.num_turns ?? 0,
      tokensUsed,
      costUsd,
      durationMs,
      commitsCreated,
      transcriptPath: writer.getFilePath(),
      error,
    };
  }

  /** Build a prompt from a planner brief — injects specific objectives and curated context. */
  private async buildBriefPrompt(brief: SessionBrief): Promise<string> {
    const sections: string[] = [];

    const globalClaude = await this.readOptional(join(this.rootDir, "CLAUDE.md"));
    if (globalClaude) sections.push("# Global Platform Instructions\n\n" + globalClaude);

    const agentDef = await this.readOptional(
      join(this.rootDir, ".claude", "agents", `${brief.agentType}.md`),
    );
    if (agentDef) sections.push("# Agent Role Definition\n\n" + agentDef);

    const projectClaude = await this.readOptional(
      join(this.rootDir, "projects", brief.projectName, "CLAUDE.md"),
    );
    if (projectClaude) sections.push("# Project-Specific Instructions\n\n" + projectClaude);

    const statusYaml = await this.readOptional(
      join(this.rootDir, "projects", brief.projectName, "status.yaml"),
    );
    if (statusYaml) {
      sections.push("# Current Project Status (status.yaml)\n\n```yaml\n" + statusYaml + "\n```");
    }

    // Inject experiment spec context for experimenter/critic sessions
    if (brief.agentType === "experimenter" || brief.agentType === "critic") {
      const specContext = await this.getExperimentSpecContext(brief.projectName);
      if (specContext) {
        sections.push("# Active Experiment Spec\n\n```yaml\n" + specContext + "\n```\n");
      }
    }

    // Inject strategist-specific context: Linear access, session evaluations, scripts
    if (brief.agentType === "strategist") {
      // Inject Linear API key for CLI tool usage
      const linearKey = process.env.LINEAR_API_KEY;
      if (linearKey) {
        sections.push(
          "# Linear API Access\n\n" +
          "The LINEAR_API_KEY environment variable is set. " +
          "Use `python3 scripts/linear-cli.py` commands to interact with Linear.\n" +
          "Team ID: 77e7bcae-30d7-4257-b043-6f0b004abc65 (DW team only)\n" +
          "NEVER operate on the EV team."
        );
      }

      // Inject recent session evaluations
      try {
        const evalQuery = "SELECT project, agent_type, quality_score, objective, cost_usd, created_at FROM session_evaluations ORDER BY created_at DESC LIMIT 20";
        const pool = this.dbPool;
        if (pool) {
          const { rows } = await pool.query(evalQuery);
          if (rows.length > 0) {
            const evalLines = rows.map((r: Record<string, unknown>) =>
              `- [${(r.created_at as Date)?.toISOString?.()?.slice(0, 10) || "?"}] ${r.project} (${r.agent_type}): ${r.quality_score}/100, $${(r.cost_usd as number)?.toFixed(2) || "?"} — ${((r.objective as string) || "").slice(0, 80)}`
            );
            sections.push("# Recent Session Evaluations (last 20)\n\n" + evalLines.join("\n"));
          }
        }
      } catch {}

      sections.push(
        "# Available Scripts\n\n" +
        "- `python3 scripts/linear-cli.py` — Manage Linear issues (list, create, update, comment, set-blocked-by, create-sub-issue)\n" +
        "- `python3 scripts/codebase-audit.py` — Run codebase health scan (JSON output)\n" +
        "- Run `python3 scripts/linear-cli.py --help` for usage details"
      );
    }

    // Brief-specific context — this is what makes planner sessions intelligent
    const briefParts: string[] = [];
    briefParts.push("# Session Objective\n");
    briefParts.push(brief.objective);
    briefParts.push("\n## Why This Task Was Selected\n");
    briefParts.push(brief.reasoning);

    if (brief.context.claims.length > 0) {
      briefParts.push("\n## Relevant Claims from Knowledge Graph\n");
      for (const c of brief.context.claims.slice(0, 15)) {
        const conf = (c.confidence * 100).toFixed(0);
        briefParts.push(`- **[${c.claimType}]** (${conf}% confidence) ${c.statement}`);
      }
    }

    if (brief.context.contradictions.length > 0) {
      briefParts.push("\n## Known Contradictions\n");
      for (const c of brief.context.contradictions.slice(0, 5)) {
        briefParts.push(`- Claim ${c.sourceId.slice(0, 8)} contradicts ${c.targetId.slice(0, 8)} (strength: ${c.strength})`);
        if (c.evidence) briefParts.push(`  Evidence: ${c.evidence}`);
      }
    }

    if (brief.context.files.length > 0) {
      briefParts.push("\n## Files to Read First\n");
      for (const f of brief.context.files) {
        briefParts.push(`- ${f}`);
      }
    }

    if (brief.context.supplementary) {
      briefParts.push("\n## Additional Context\n");
      briefParts.push(brief.context.supplementary);
    }

    // Literature alerts for scout/researcher sessions
    if (["scout", "researcher"].includes(brief.agentType)) {
      const litContext = await this.getLiteratureContext(brief.projectName);
      if (litContext) {
        briefParts.push("\n## Recent Literature Alerts\n");
        briefParts.push(litContext);
      }
    }

    briefParts.push("\n## Deliverables\n");
    for (const d of brief.deliverables) {
      briefParts.push(`- [ ] ${d.description}`);
    }

    briefParts.push("\n## Constraints\n");
    briefParts.push(`- Max turns: ${brief.constraints.maxTurns}`);
    briefParts.push(`- Budget: $${brief.constraints.maxBudgetUsd.toFixed(2)}`);

    sections.push(briefParts.join("\n"));

    sections.push(
      "# Session Workflow\n\n" +
      `You are working autonomously on the "${brief.projectName}" project as a ${brief.agentType} agent.\n\n` +
      "1. Read project files to understand current state before making changes\n" +
      "2. Make all decisions autonomously using your best judgment\n" +
      "3. Use extended thinking for critical research decisions\n" +
      `4. Make frequent conventional commits: type(${brief.projectName}): description\n` +
      "5. Update status.yaml after significant progress\n" +
      "6. Log all decisions in decisions_made with date and rationale\n" +
      "7. Push changes to remote regularly\n" +
      "8. Create a PR to main when you reach a milestone\n\n" +
      "Today's date is " + new Date().toISOString().split("T")[0] + ".",
    );

    return sections.join("\n\n---\n\n");
  }

  private async buildPrompt(projectName: string, agentType: string): Promise<string> {
    const sections: string[] = [];

    const globalClaude = await this.readOptional(join(this.rootDir, "CLAUDE.md"));
    if (globalClaude) {
      sections.push("# Global Platform Instructions\n\n" + globalClaude);
    }

    const agentDef = await this.readOptional(
      join(this.rootDir, ".claude", "agents", `${agentType}.md`),
    );
    if (agentDef) {
      sections.push("# Agent Role Definition\n\n" + agentDef);
    }

    const projectClaude = await this.readOptional(
      join(this.rootDir, "projects", projectName, "CLAUDE.md"),
    );
    if (projectClaude) {
      sections.push("# Project-Specific Instructions\n\n" + projectClaude);
    }

    const statusYaml = await this.readOptional(
      join(this.rootDir, "projects", projectName, "status.yaml"),
    );
    if (statusYaml) {
      sections.push(
        "# Current Project Status (status.yaml)\n\n```yaml\n" +
        statusYaml +
        "\n```",
      );
    }

    // Inject relevant knowledge from the knowledge graph
    const knowledgeContext = await this.getKnowledgeContext(projectName, agentType, statusYaml);
    if (knowledgeContext) {
      sections.push("# Existing Knowledge (from Knowledge Graph)\n\n" + knowledgeContext);
    }

    // Inject recent literature alerts for scout/researcher sessions
    if (["scout", "researcher"].includes(agentType)) {
      const litContext = await this.getLiteratureContext(projectName);
      if (litContext) {
        sections.push("# Recent Literature Alerts\n\n" + litContext);
      }
    }

    sections.push(
      "# Session Workflow\n\n" +
      `You are working autonomously on the "${projectName}" project as a ${agentType} agent.\n\n` +
      "1. Read project files to understand current state before making changes\n" +
      "2. Make all decisions autonomously using your best judgment\n" +
      "3. Use extended thinking for critical research decisions\n" +
      `4. Make frequent conventional commits: type(${projectName}): description\n` +
      "5. Update status.yaml after significant progress\n" +
      "6. Log all decisions in decisions_made with date and rationale\n" +
      "7. Push changes to remote regularly\n" +
      "8. Create a PR to main when you reach a milestone\n\n" +
      "Today's date is " + new Date().toISOString().split("T")[0] + ".",
    );

    return sections.join("\n\n---\n\n");
  }

  private async readOptional(path: string): Promise<string | null> {
    try {
      return await readFile(path, "utf-8");
    } catch {
      return null;
    }
  }

  /**
   * Find and read the most recent experiment spec.yaml for a project.
   * Returns the YAML content or null if no spec exists.
   */
  private async getExperimentSpecContext(projectName: string): Promise<string | null> {
    const experimentsDir = join(this.rootDir, "projects", projectName, "experiments");
    try {
      const dirs = await readdir(experimentsDir);
      // Check each experiment subdirectory for a spec.yaml, return the first found
      for (const dir of dirs.sort().reverse()) {
        const specPath = join(experimentsDir, dir, "spec.yaml");
        const content = await this.readOptional(specPath);
        if (content) return content;
      }
      return null;
    } catch {
      return null;
    }
  }

  /**
   * Query the knowledge graph for claims relevant to the current session.
   * Uses the project's current_focus/current_activity from status.yaml as
   * the search query, supplemented by contradictions and unsupported claims.
   */
  private async getKnowledgeContext(
    projectName: string,
    agentType: string,
    statusYaml: string | null,
  ): Promise<string | null> {
    if (!this.knowledgeGraph) return null;

    const limit = KNOWLEDGE_LIMITS[agentType] ?? 10;

    try {
      // Extract current focus from status.yaml for semantic query
      const focus = this.extractFocus(statusYaml);
      const parts: string[] = [];

      // 1. Semantic search based on current focus, or top claims by confidence
      if (focus) {
        const relevant = await this.knowledgeGraph.query(focus, {
          project: projectName,
          limit,
          threshold: 0.30,
        });
        if (relevant.length > 0) {
          parts.push("## Relevant Claims\n");
          parts.push(this.formatClaims(relevant));
        }
      } else {
        // No focus extracted — fall back to highest-confidence claims
        const topClaims = await this.knowledgeGraph.getProjectClaims(projectName, undefined, limit);
        if (topClaims.length > 0) {
          parts.push("## Project Knowledge (top claims by confidence)\n");
          parts.push(this.formatClaims(topClaims));
        }
      }

      // 2. Contradictions (always useful for critics/reviewers)
      if (["critic", "reviewer", "writer", "strategist"].includes(agentType)) {
        const contradictions = await this.knowledgeGraph.findContradictions(projectName);
        if (contradictions.length > 0) {
          parts.push(`\n## Known Contradictions (${contradictions.length})\n`);
          for (const c of contradictions.slice(0, 5)) {
            parts.push(`- **${c.sourceId}** contradicts **${c.targetId}** (strength: ${c.strength})`);
            if (c.evidence) parts.push(`  Evidence: ${c.evidence}`);
          }
        }
      }

      // 3. Unsupported claims (useful for researchers/experimenters)
      if (["researcher", "experimenter", "critic"].includes(agentType)) {
        const unsupported = await this.knowledgeGraph.getUnsupportedClaims(projectName);
        if (unsupported.length > 0) {
          parts.push(`\n## Unsupported Claims (${unsupported.length} total, showing top 5)\n`);
          for (const c of unsupported.slice(0, 5)) {
            parts.push(`- [${c.claimType}] "${c.statement}" (confidence: ${c.confidence})`);
          }
        }
      }

      if (parts.length === 0) return null;

      parts.push(
        "\n---\n*Use the knowledge skill to query for more claims or record new findings.*",
      );
      return parts.join("\n");
    } catch (err) {
      console.error("[SessionRunner] Knowledge context failed (continuing without):", err);
      return null;
    }
  }

  /** Extract a focus query from status.yaml text. */
  private extractFocus(statusYaml: string | null): string | null {
    if (!statusYaml) return null;
    // Try current_activity first, then current_focus, then phase
    for (const field of ["current_activity", "current_focus", "phase"]) {
      const match = statusYaml.match(new RegExp(`${field}:\\s*["']?(.+?)["']?\\s*$`, "m"));
      if (match?.[1]) return match[1].slice(0, 200);
    }
    return null;
  }

  /** Format claims as a concise list. */
  private formatClaims(claims: ClaimRow[]): string {
    return claims.map((c) => {
      const dist = c.distance !== undefined ? ` (relevance: ${(1 - c.distance).toFixed(2)})` : "";
      const src = c.source ? ` [source: ${c.source}]` : "";
      return `- **[${c.claimType}]** ${c.statement} — confidence: ${c.confidence}${dist}${src}`;
    }).join("\n");
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private extractTokenUsage(result: any): { input: number; output: number } {
    if (!result) return { input: 0, output: 0 };
    return {
      input: result.usage.input_tokens,
      output: result.usage.output_tokens,
    };
  }

  private calculateCost(tokens: { input: number; output: number }, model: string = "claude-sonnet-4-6"): number {
    return calcModelCost(model, tokens.input, tokens.output);
  }

  /**
   * Query recent literature alerts for a project.
   * Injected into scout/researcher session prompts.
   */
  private async getLiteratureContext(projectName: string): Promise<string | null> {
    if (!this.dbPool) return null;

    try {
      // Check if lit_alerts table exists
      const { rows: tableCheck } = await this.dbPool.query(
        `SELECT EXISTS (
          SELECT FROM information_schema.tables WHERE table_name = 'lit_alerts'
        ) AS exists`,
      );
      if (!tableCheck[0]?.exists) return null;

      const { rows } = await this.dbPool.query(
        `SELECT a.priority, a.relation, a.similarity, a.matched_claim, a.explanation,
                p.title, p.authors, p.year, p.url, p.abstract
         FROM lit_alerts a
         JOIN lit_papers p ON p.id = a.paper_id
         WHERE a.project = $1 AND a.acknowledged = FALSE
         ORDER BY
           CASE a.priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
           a.created_at DESC
         LIMIT 10`,
        [projectName],
      );

      if (rows.length === 0) return null;

      const parts: string[] = [];
      parts.push(`Since your last session, ${rows.length} relevant paper(s) were detected:\n`);

      for (const r of rows) {
        const authors = Array.isArray(r.authors) ? r.authors : [];
        const authorStr = authors.length > 0 ? `${authors[0]} et al.` : "Unknown";
        const simStr = r.similarity ? ` (similarity: ${parseFloat(r.similarity).toFixed(2)})` : "";

        parts.push(`### [${r.priority.toUpperCase()}] ${r.title}`);
        parts.push(`- **Authors**: ${authorStr} (${r.year ?? "preprint"})`);
        parts.push(`- **Relation**: ${r.relation}${simStr}`);
        if (r.matched_claim) parts.push(`- **Matched claim**: ${r.matched_claim}`);
        if (r.url) parts.push(`- **URL**: ${r.url}`);
        if (r.abstract) parts.push(`- **Abstract**: ${r.abstract.slice(0, 300)}...`);
        if (r.explanation) parts.push(`- **Analysis**: ${r.explanation}`);
        parts.push("");
      }

      parts.push("**Action requested**: Assess the impact of these papers on our research. " +
        "For competing papers, determine if our contribution is still novel. " +
        "Update status.yaml with your assessment.");

      return parts.join("\n");
    } catch (err) {
      console.error("[SessionRunner] Literature context failed:", err);
      return null;
    }
  }
}
