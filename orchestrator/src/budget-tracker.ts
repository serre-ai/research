import { readFile, mkdir } from "node:fs/promises";
import { join } from "node:path";
import { parse } from "yaml";
import pg from "pg";
import { ActivityLogger } from "./logger.js";
import { Notifier } from "./notifier.js";
import { atomicAppendJsonl } from "./utils/atomic-write.js";

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

export interface ProviderSpend {
  provider: string;
  displayName: string;
  providerType: string;
  costUsd: number;
}

export interface BudgetStatus {
  dailySpent: number;
  dailyLimit: number;
  dailyRemaining: number;
  monthlySpent: number;
  monthlyLimit: number;
  monthlyRemaining: number;
  /** Variable API costs this month */
  variableSpent: number;
  /** Fixed subscription costs this month */
  fixedSpent: number;
  byProject: Record<string, number>;
  byProvider: ProviderSpend[];
  burnRate: {
    daily7dAvg: number;
    projectedMonthEnd: number;
  };
  sessionsToday: number;
  avgCostPerSession: number;
  alertLevel: "ok" | "warning" | "critical" | "exceeded";
}

export class BudgetTracker {
  private readonly logsDir: string;
  private readonly spendingFile: string;
  private readonly rootDir: string;
  private readonly logger: ActivityLogger;
  private readonly notifier: Notifier | null;
  private readonly pool: pg.Pool | null;
  private lastAlertLevel: string = "ok";
  private monthlyLimit: number | null = null;
  private dirCreated = false;

  constructor(rootDir: string, logger: ActivityLogger, notifier?: Notifier, dbPool?: pg.Pool) {
    this.rootDir = rootDir;
    this.logger = logger;
    this.notifier = notifier ?? null;
    this.pool = dbPool ?? null;
    this.logsDir = join(rootDir, ".logs");
    this.spendingFile = join(this.logsDir, "spending.jsonl");
  }

  /**
   * Record a spending event. Writes to JSONL (immediate) and DB (best-effort).
   * Uses atomic append to prevent corruption during crashes.
   */
  async record(record: Omit<SpendingRecord, "timestamp">): Promise<void> {
    await this.ensureDir();
    const entry = {
      timestamp: new Date().toISOString(),
      ...record,
    };

    // JSONL — atomic append prevents corruption during crashes
    await atomicAppendJsonl(this.spendingFile, JSON.stringify(entry));

    // DB — best-effort
    if (this.pool) {
      try {
        const provider = this.inferProvider(record.model);
        await this.pool.query(
          `INSERT INTO budget_events (timestamp, project, session_id, agent_type, tokens_input, tokens_output, cost_usd, model, provider, category, source)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'api_calls', 'session')`,
          [
            entry.timestamp,
            record.projectName,
            record.sessionId,
            record.agentType,
            record.tokensInput,
            record.tokensOutput,
            record.costUsd,
            record.model,
            provider,
          ],
        );
      } catch (err) {
        console.error("[BudgetTracker] DB write failed (non-fatal):", err);
      }
    }

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

  /**
   * Get comprehensive budget status.
   * Reads from DB when available, falls back to JSONL.
   */
  async getStatus(): Promise<BudgetStatus> {
    const limit = await this.getMonthlyLimit();
    const dailyLimit = limit / 30;

    if (this.pool) {
      try {
        return await this.getStatusFromDb(limit, dailyLimit);
      } catch (err) {
        console.error("[BudgetTracker] DB read failed, falling back to JSONL:", err);
      }
    }

    return this.getStatusFromJsonl(limit, dailyLimit);
  }

  async canSpend(estimatedCostUsd: number): Promise<boolean> {
    const status = await this.getStatus();
    return (
      status.dailySpent + estimatedCostUsd <= status.dailyLimit &&
      status.monthlySpent + estimatedCostUsd <= status.monthlyLimit
    );
  }

  async getProjectSpending(projectName: string): Promise<number> {
    if (this.pool) {
      try {
        const { rows } = await this.pool.query<{ total: string }>(
          `SELECT COALESCE(SUM(cost_usd), 0) AS total
           FROM budget_events
           WHERE project = $1
             AND DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)`,
          [projectName],
        );
        return parseFloat(rows[0]?.total ?? "0");
      } catch {
        // fall through to JSONL
      }
    }

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

  /**
   * Get total monthly spend including fixed costs.
   */
  async getTotalMonthlySpend(): Promise<number> {
    const status = await this.getStatus();
    return status.variableSpent + status.fixedSpent;
  }

  /**
   * Sync any JSONL entries not yet in DB.
   */
  async flushToDb(): Promise<number> {
    if (!this.pool) return 0;

    const records = await this.readRecords();
    if (records.length === 0) return 0;

    // Get the latest DB timestamp to avoid duplicates
    const { rows } = await this.pool.query<{ latest: string | null }>(
      `SELECT MAX(timestamp) AS latest FROM budget_events WHERE source = 'session'`,
    );
    const latestDb = rows[0]?.latest ? new Date(rows[0].latest).getTime() : 0;

    let synced = 0;
    for (const r of records) {
      const ts = new Date(r.timestamp).getTime();
      if (ts <= latestDb) continue;

      const provider = this.inferProvider(r.model);
      try {
        await this.pool.query(
          `INSERT INTO budget_events (timestamp, project, session_id, agent_type, tokens_input, tokens_output, cost_usd, model, provider, category, source)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'api_calls', 'session')
           ON CONFLICT DO NOTHING`,
          [
            r.timestamp,
            r.projectName,
            r.sessionId,
            r.agentType,
            r.tokensInput,
            r.tokensOutput,
            r.costUsd,
            r.model,
            provider,
          ],
        );
        synced++;
      } catch (err) {
        console.error("[BudgetTracker] flushToDb row error:", err);
      }
    }

    if (synced > 0) {
      console.log(`[BudgetTracker] Flushed ${synced} JSONL records to DB`);
    }
    return synced;
  }

  /**
   * Record a manual cost entry (e.g. one-off purchases).
   */
  async recordManual(entry: {
    provider: string;
    costUsd: number;
    description: string;
    category?: string;
  }): Promise<void> {
    if (!this.pool) throw new Error("DB not available for manual entries");

    await this.pool.query(
      `INSERT INTO budget_events (timestamp, project, cost_usd, model, provider, category, source)
       VALUES (NOW(), 'platform', $1, $2, $3, $4, 'manual')`,
      [entry.costUsd, entry.description, entry.provider, entry.category ?? "api_calls"],
    );
  }

  // ============================================================
  // Private: DB-backed status
  // ============================================================

  private async getStatusFromDb(limit: number, dailyLimit: number): Promise<BudgetStatus> {
    // Variable spend: today + this month
    const { rows: dailyRows } = await this.pool!.query<{ total: string }>(
      `SELECT COALESCE(SUM(cost_usd), 0) AS total FROM budget_events WHERE DATE(timestamp) = CURRENT_DATE`,
    );
    const dailySpent = parseFloat(dailyRows[0].total);

    const { rows: monthlyRows } = await this.pool!.query<{ total: string }>(
      `SELECT COALESCE(SUM(cost_usd), 0) AS total FROM budget_events
       WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)`,
    );
    const variableSpent = parseFloat(monthlyRows[0].total);

    // Fixed spend this month
    const { rows: fixedRows } = await this.pool!.query<{ total: string }>(
      `SELECT COALESCE(SUM(amount_usd), 0) AS total FROM fixed_cost_entries
       WHERE month = DATE_TRUNC('month', CURRENT_DATE)::date`,
    );
    const fixedSpent = parseFloat(fixedRows[0].total);

    const monthlySpent = variableSpent + fixedSpent;

    // By project
    const { rows: projRows } = await this.pool!.query<{ project: string; cost: string }>(
      `SELECT project, SUM(cost_usd) AS cost FROM budget_events
       WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)
       GROUP BY project`,
    );
    const byProject: Record<string, number> = {};
    for (const r of projRows) {
      byProject[r.project] = parseFloat(r.cost);
    }

    // By provider
    const byProvider = await this.getProviderBreakdown();

    // Burn rate (7-day average)
    const { rows: burnRows } = await this.pool!.query<{ days: string; total: string }>(
      `SELECT COUNT(DISTINCT DATE(timestamp)) AS days, COALESCE(SUM(cost_usd), 0) AS total
       FROM budget_events
       WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'`,
    );
    const burnDays = Math.max(parseInt(burnRows[0].days) || 1, 1);
    const burnTotal = parseFloat(burnRows[0].total);
    const daily7dAvg = burnTotal / burnDays;

    // Project to month end
    const now = new Date();
    const daysRemaining = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate() - now.getDate();
    const projectedMonthEnd = monthlySpent + (daily7dAvg * daysRemaining);

    // Session count today and 7-day average cost per session
    const { rows: sessionRows } = await this.pool!.query<{ today: string; avg7d: string }>(
      `SELECT
        (SELECT COUNT(*) FROM sessions WHERE started_at > CURRENT_DATE) AS today,
        (SELECT COALESCE(AVG(cost_usd), 2.0) FROM sessions
         WHERE started_at > NOW() - INTERVAL '7 days' AND status = 'completed' AND cost_usd > 0) AS avg7d`,
    );
    const sessionsToday = parseInt(sessionRows[0].today);
    const avgCostPerSession = parseFloat(sessionRows[0].avg7d);

    const dailyRemaining = Math.max(0, dailyLimit - dailySpent);
    const monthlyRemaining = Math.max(0, limit - monthlySpent);
    const alertLevel = this.computeAlertLevel(dailySpent, dailyLimit, monthlySpent, limit);

    await this.checkAlerts(alertLevel, dailySpent, dailyLimit, monthlySpent, limit);

    return {
      dailySpent,
      dailyLimit,
      dailyRemaining,
      monthlySpent,
      monthlyLimit: limit,
      monthlyRemaining,
      variableSpent,
      fixedSpent,
      byProject,
      byProvider,
      burnRate: { daily7dAvg, projectedMonthEnd },
      sessionsToday,
      avgCostPerSession,
      alertLevel,
    };
  }

  private async getProviderBreakdown(): Promise<ProviderSpend[]> {
    if (!this.pool) return [];

    try {
      const { rows } = await this.pool.query<{
        provider: string;
        display_name: string;
        provider_type: string;
        cost: string;
      }>(
        `SELECT
           COALESCE(be.provider, 'unknown') AS provider,
           COALESCE(cp.display_name, be.provider, 'Unknown') AS display_name,
           COALESCE(cp.provider_type, 'api_variable') AS provider_type,
           SUM(be.cost_usd) AS cost
         FROM budget_events be
         LEFT JOIN cost_providers cp ON cp.id = be.provider
         WHERE DATE_TRUNC('month', be.timestamp) = DATE_TRUNC('month', CURRENT_DATE)
         GROUP BY be.provider, cp.display_name, cp.provider_type
         ORDER BY cost DESC`,
      );

      const result: ProviderSpend[] = rows.map((r) => ({
        provider: r.provider,
        displayName: r.display_name,
        providerType: r.provider_type,
        costUsd: parseFloat(r.cost),
      }));

      // Add fixed cost providers
      const { rows: fixedRows } = await this.pool.query<{
        provider: string;
        display_name: string;
        provider_type: string;
        cost: string;
      }>(
        `SELECT
           f.provider,
           cp.display_name,
           cp.provider_type,
           SUM(f.amount_usd) AS cost
         FROM fixed_cost_entries f
         JOIN cost_providers cp ON cp.id = f.provider
         WHERE f.month = DATE_TRUNC('month', CURRENT_DATE)::date
         GROUP BY f.provider, cp.display_name, cp.provider_type`,
      );

      for (const r of fixedRows) {
        const existing = result.find((p) => p.provider === r.provider);
        if (existing) {
          existing.costUsd += parseFloat(r.cost);
        } else {
          result.push({
            provider: r.provider,
            displayName: r.display_name,
            providerType: r.provider_type,
            costUsd: parseFloat(r.cost),
          });
        }
      }

      return result.sort((a, b) => b.costUsd - a.costUsd);
    } catch {
      return [];
    }
  }

  // ============================================================
  // Private: JSONL fallback
  // ============================================================

  private async getStatusFromJsonl(limit: number, dailyLimit: number): Promise<BudgetStatus> {
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

    // Estimate fixed costs from config when DB not available.
    // NOTE: Keep this value in sync with fixed_cost_entries in DB / config.yaml.
    const fixedSpent = 455.50; // $400 Claude Code Max + $5.50 Hetzner + $50 Firecrawl
    const totalMonthly = monthlySpent + fixedSpent;

    const dailyRemaining = Math.max(0, dailyLimit - dailySpent);
    const monthlyRemaining = Math.max(0, limit - totalMonthly);
    const alertLevel = this.computeAlertLevel(dailySpent, dailyLimit, totalMonthly, limit);

    await this.checkAlerts(alertLevel, dailySpent, dailyLimit, totalMonthly, limit);

    return {
      dailySpent,
      dailyLimit,
      dailyRemaining,
      monthlySpent: totalMonthly,
      monthlyLimit: limit,
      monthlyRemaining,
      variableSpent: monthlySpent,
      fixedSpent,
      byProject,
      byProvider: [],
      burnRate: { daily7dAvg: 0, projectedMonthEnd: 0 },
      sessionsToday: 0,
      avgCostPerSession: 2.0,
      alertLevel,
    };
  }

  // ============================================================
  // Private: shared helpers
  // ============================================================

  private async checkAlerts(
    alertLevel: string,
    dailySpent: number,
    dailyLimit: number,
    monthlySpent: number,
    limit: number,
  ): Promise<void> {
    if (this.notifier && alertLevel !== "ok" && alertLevel !== this.lastAlertLevel) {
      this.lastAlertLevel = alertLevel;
      await this.notifier.notify({
        event: `Budget ${alertLevel.charAt(0).toUpperCase() + alertLevel.slice(1)}`,
        summary: `Daily: $${dailySpent.toFixed(2)}/$${dailyLimit.toFixed(2)} | Monthly: $${monthlySpent.toFixed(2)}/$${limit.toFixed(2)}`,
        level: alertLevel === "exceeded" ? "error" : "warning",
      });
    }
  }

  private computeAlertLevel(
    dailySpent: number,
    dailyLimit: number,
    monthlySpent: number,
    monthlyLimit: number,
  ): "ok" | "warning" | "critical" | "exceeded" {
    const dailyPct = dailyLimit > 0 ? dailySpent / dailyLimit : 0;
    const monthlyPct = monthlyLimit > 0 ? monthlySpent / monthlyLimit : 0;
    if (dailyPct > 1 || monthlyPct > 1) return "exceeded";
    if (dailyPct >= 0.95 || monthlyPct >= 0.95) return "critical";
    if (dailyPct >= 0.8 || monthlyPct >= 0.8) return "warning";
    return "ok";
  }

  private inferProvider(model: string): string | null {
    if (model.startsWith("claude")) return "anthropic";
    if (model.startsWith("gpt") || model.startsWith("o1") || model.startsWith("o3")) return "openai";
    if (model.includes("/")) return "openrouter";
    return null;
  }

  private async readRecords(): Promise<SpendingRecord[]> {
    let content: string;
    try {
      content = await readFile(this.spendingFile, "utf-8");
    } catch {
      return [];
    }
    const records: SpendingRecord[] = [];
    for (const line of content.trim().split("\n")) {
      if (!line) continue;
      try {
        records.push(JSON.parse(line));
      } catch (err) {
        console.warn("[BudgetTracker] Skipping malformed JSONL line:", (err as Error).message);
      }
    }
    return records;
  }

  private async getMonthlyLimit(): Promise<number> {
    if (this.monthlyLimit !== null) return this.monthlyLimit;
    try {
      const configText = await readFile(join(this.rootDir, "config.yaml"), "utf-8");
      const config = parse(configText);
      const budget = config.budget;
      this.monthlyLimit = budget?.monthly_limit_usd ?? 1000;
    } catch {
      this.monthlyLimit = 1000;
    }
    return this.monthlyLimit!;
  }

  private async ensureDir(): Promise<void> {
    if (this.dirCreated) return;
    await mkdir(this.logsDir, { recursive: true });
    this.dirCreated = true;
  }
}
