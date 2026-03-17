import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { query } from "@anthropic-ai/claude-agent-sdk";
import { GitEngine } from "./git-engine.js";
import { TranscriptWriter } from "./transcript-writer.js";
import { calculateCost as calcModelCost } from "./pricing.js";
import type { KnowledgeGraph, ClaimRow } from "./knowledge-graph.js";

export type AgentType =
  | "researcher" | "writer" | "reviewer" | "editor"
  | "critic" | "experimenter" | "theorist" | "strategist" | "scout"
  | "engineer";

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

  constructor(rootDir: string = process.cwd(), knowledgeGraph?: KnowledgeGraph | null) {
    this.rootDir = rootDir;
    this.knowledgeGraph = knowledgeGraph ?? null;
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
}
