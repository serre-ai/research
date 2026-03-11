import { appendFile, readFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { parse } from "yaml";
import { ActivityLogger } from "./logger.js";
import { Notifier } from "./notifier.js";

export interface SpendingRecord {
  timestamp: string;
  projectName: string;
  sessionId: string;
  agentType: string;
  tokensInput: number;
  tokensOutput: number;
  costUsd: number;
  model: string;
}

export interface BudgetStatus {
  dailySpent: number;
  dailyLimit: number;
  dailyRemaining: number;
  monthlySpent: number;
  monthlyLimit: number;
  monthlyRemaining: number;
  byProject: Record<string, number>;
  alertLevel: "ok" | "warning" | "critical" | "exceeded";
}

export class BudgetTracker {
  private readonly logsDir: string;
  private readonly spendingFile: string;
  private readonly rootDir: string;
  private readonly logger: ActivityLogger;
  private readonly notifier: Notifier | null;
  private lastAlertLevel: string = "ok";
  private monthlyLimit: number | null = null;
  private dirCreated = false;

  constructor(rootDir: string, logger: ActivityLogger, notifier?: Notifier) {
    this.rootDir = rootDir;
    this.logger = logger;
    this.notifier = notifier ?? null;
    this.logsDir = join(rootDir, ".logs");
    this.spendingFile = join(this.logsDir, "spending.jsonl");
  }

  async record(record: Omit<SpendingRecord, "timestamp">): Promise<void> {
    await this.ensureDir();
    const entry: SpendingRecord = {
      timestamp: new Date().toISOString(),
      ...record,
    };
    await appendFile(this.spendingFile, JSON.stringify(entry) + "\n", "utf-8");

    await this.logger.log({
      type: "budget_spend",
      project: record.projectName,
      agent: record.agentType,
      data: {
        sessionId: record.sessionId,
        costUsd: record.costUsd,
        tokensInput: record.tokensInput,
        tokensOutput: record.tokensOutput,
        model: record.model,
      },
    });
  }

  async getStatus(): Promise<BudgetStatus> {
    const limit = await this.getMonthlyLimit();
    const dailyLimit = limit / 30;
    const records = await this.readRecords();

    const today = new Date().toISOString().split("T")[0];
    const thisMonth = new Date().toISOString().slice(0, 7);

    let dailySpent = 0;
    let monthlySpent = 0;
    const byProject: Record<string, number> = {};

    for (const r of records) {
      const recordDate = r.timestamp.split("T")[0];
      const recordMonth = r.timestamp.slice(0, 7);

      if (recordMonth === thisMonth) {
        monthlySpent += r.costUsd;
        byProject[r.projectName] = (byProject[r.projectName] ?? 0) + r.costUsd;
      }

      if (recordDate === today) {
        dailySpent += r.costUsd;
      }
    }

    const dailyRemaining = Math.max(0, dailyLimit - dailySpent);
    const monthlyRemaining = Math.max(0, limit - monthlySpent);
    const alertLevel = this.computeAlertLevel(dailySpent, dailyLimit, monthlySpent, limit);

    if (this.notifier && alertLevel !== "ok" && alertLevel !== this.lastAlertLevel) {
      this.lastAlertLevel = alertLevel;
      await this.notifier.notify({
        event: `Budget ${alertLevel.charAt(0).toUpperCase() + alertLevel.slice(1)}`,
        summary: `Daily: $${dailySpent.toFixed(2)}/$${dailyLimit.toFixed(2)} | Monthly: $${monthlySpent.toFixed(2)}/$${limit.toFixed(2)}`,
        level: alertLevel === "exceeded" ? "error" : "warning",
      });
    }

    return {
      dailySpent,
      dailyLimit,
      dailyRemaining,
      monthlySpent,
      monthlyLimit: limit,
      monthlyRemaining,
      byProject,
      alertLevel,
    };
  }

  async canSpend(estimatedCostUsd: number): Promise<boolean> {
    const status = await this.getStatus();
    return (
      status.dailySpent + estimatedCostUsd <= status.dailyLimit &&
      status.monthlySpent + estimatedCostUsd <= status.monthlyLimit
    );
  }

  async getProjectSpending(projectName: string): Promise<number> {
    const records = await this.readRecords();
    const thisMonth = new Date().toISOString().slice(0, 7);
    let total = 0;
    for (const r of records) {
      if (r.projectName === projectName && r.timestamp.slice(0, 7) === thisMonth) {
        total += r.costUsd;
      }
    }
    return total;
  }

  private computeAlertLevel(
    dailySpent: number,
    dailyLimit: number,
    monthlySpent: number,
    monthlyLimit: number,
  ): BudgetStatus["alertLevel"] {
    const dailyPct = dailyLimit > 0 ? dailySpent / dailyLimit : 0;
    const monthlyPct = monthlyLimit > 0 ? monthlySpent / monthlyLimit : 0;

    if (dailyPct > 1 || monthlyPct > 1) return "exceeded";
    if (dailyPct >= 0.95 || monthlyPct >= 0.95) return "critical";
    if (dailyPct >= 0.8 || monthlyPct >= 0.8) return "warning";
    return "ok";
  }

  private async readRecords(): Promise<SpendingRecord[]> {
    let content: string;
    try {
      content = await readFile(this.spendingFile, "utf-8");
    } catch {
      return [];
    }
    return content
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((line) => JSON.parse(line) as SpendingRecord);
  }

  private async getMonthlyLimit(): Promise<number> {
    if (this.monthlyLimit !== null) return this.monthlyLimit;
    try {
      const configText = await readFile(join(this.rootDir, "config.yaml"), "utf-8");
      const config = parse(configText) as Record<string, unknown>;
      const budget = config.budget as Record<string, unknown> | undefined;
      this.monthlyLimit = (budget?.monthly_limit_usd as number) ?? 1000;
    } catch {
      this.monthlyLimit = 1000;
    }
    return this.monthlyLimit;
  }

  private async ensureDir(): Promise<void> {
    if (this.dirCreated) return;
    await mkdir(this.logsDir, { recursive: true });
    this.dirCreated = true;
  }
}
