import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import { query, type SDKMessage, type SDKResultMessage } from "@anthropic-ai/claude-agent-sdk";
import { GitEngine } from "./git-engine.js";
import { TranscriptWriter } from "./transcript-writer.js";

export interface SessionConfig {
  projectName: string;
  agentType: "researcher" | "writer" | "reviewer" | "editor" | "strategist";
  maxTurns: number;
  maxDurationMs: number;
  thinkingLevel?: "standard" | "extended";
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

const DEFAULT_MAX_TURNS = 50;
const DEFAULT_MAX_DURATION_MS = 45 * 60 * 1000;

const SONNET_PRICING = {
  inputPer1MTokens: 3,
  outputPer1MTokens: 15,
};

export class SessionRunner {
  private rootDir: string;

  constructor(rootDir: string = process.cwd()) {
    this.rootDir = rootDir;
  }

  async run(config: SessionConfig): Promise<SessionResult> {
    const sessionId = randomUUID();
    const writer = new TranscriptWriter(this.rootDir, config.projectName, sessionId);
    const maxTurns = config.maxTurns || DEFAULT_MAX_TURNS;
    const maxDurationMs = config.maxDurationMs || DEFAULT_MAX_DURATION_MS;
    const worktreePath = join(this.rootDir, ".worktrees", config.projectName);
    const startTime = Date.now();

    const prompt = await this.buildPrompt(config.projectName, config.agentType);
    const commitsCreated: string[] = [];

    let resultMessage: SDKResultMessage | undefined;
    let error: string | undefined;
    let sessionStatus: SessionResult["status"] = "completed";

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
        if ((message as any).type !== "stream_event") {
          await writer.write(message);
        }
        if (message.type === "result") {
          resultMessage = message as SDKResultMessage;
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
      const logs = await worktreeEngine.logBetween("main");
      commitsCreated.push(...logs.map((l) => l.split(" ")[0]));
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

  private async buildPrompt(
    projectName: string,
    agentType: string,
  ): Promise<string> {
    const sections: string[] = [];

    const globalClaude = await this.readOptional(
      join(this.rootDir, "CLAUDE.md"),
    );
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

    sections.push(`# Session Workflow

You are working autonomously on the "${projectName}" project as a ${agentType} agent.

1. Read project files to understand current state before making changes
2. Make all decisions autonomously using your best judgment
3. Use extended thinking for critical research decisions
4. Make frequent conventional commits: type(${projectName}): description
5. Update status.yaml after significant progress
6. Log all decisions in decisions_made with date and rationale
7. Push changes to remote regularly
8. Create a PR to main when you reach a milestone

Today's date is ${new Date().toISOString().split("T")[0]}.`);

    return sections.join("\n\n---\n\n");
  }

  private async readOptional(path: string): Promise<string | null> {
    try {
      return await readFile(path, "utf-8");
    } catch {
      return null;
    }
  }

  private extractTokenUsage(
    result: SDKResultMessage | undefined,
  ): { input: number; output: number } {
    if (!result) return { input: 0, output: 0 };
    return {
      input: result.usage.input_tokens,
      output: result.usage.output_tokens,
    };
  }

  private calculateCost(tokens: { input: number; output: number }): number {
    return (
      (tokens.input / 1_000_000) * SONNET_PRICING.inputPer1MTokens +
      (tokens.output / 1_000_000) * SONNET_PRICING.outputPer1MTokens
    );
  }
}
