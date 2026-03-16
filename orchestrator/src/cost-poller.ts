/**
 * CostPoller — polls provider APIs for usage data,
 * stores snapshots for reconciliation, and auto-generates
 * fixed cost entries each month.
 */

import pg from "pg";

interface ProviderRow {
  id: string;
  display_name: string;
  provider_type: string;
  monthly_fixed: number;
  pricing_config: Record<string, unknown>;
  enabled: boolean;
  last_polled_at: string | null;
}

export class CostPoller {
  constructor(private pool: pg.Pool) {}

  /**
   * Run all polls. Called once per daemon cycle.
   */
  async pollAll(): Promise<void> {
    console.log("[CostPoller] Starting provider polls...");

    try {
      await this.generateFixedCosts();
    } catch (err) {
      console.error("[CostPoller] generateFixedCosts error:", err);
    }

    try {
      await this.pollAnthropic();
    } catch (err) {
      console.error("[CostPoller] pollAnthropic error:", err);
    }

    try {
      await this.pollOpenRouter();
    } catch (err) {
      console.error("[CostPoller] pollOpenRouter error:", err);
    }

    try {
      await this.pollFirecrawl();
    } catch (err) {
      console.error("[CostPoller] pollFirecrawl error:", err);
    }

    console.log("[CostPoller] Polls complete.");
  }

  /**
   * Poll Anthropic usage API.
   * GET /v1/organizations/{org}/usage with Bearer token.
   */
  private async pollAnthropic(): Promise<void> {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      console.log("[CostPoller] ANTHROPIC_API_KEY not set — skipping Anthropic poll");
      return;
    }

    // The Anthropic usage API requires an admin/org key and org ID.
    // If not available, we skip gracefully.
    const orgId = process.env.ANTHROPIC_ORG_ID;
    if (!orgId) {
      console.log("[CostPoller] ANTHROPIC_ORG_ID not set — skipping Anthropic usage poll");
      return;
    }

    const now = new Date();
    const periodStart = new Date(now.getFullYear(), now.getMonth(), 1);
    const periodEnd = now;

    try {
      const url = `https://api.anthropic.com/v1/organizations/${orgId}/usage?start_date=${periodStart.toISOString().split("T")[0]}&end_date=${periodEnd.toISOString().split("T")[0]}`;
      const resp = await fetch(url, {
        headers: {
          "Authorization": `Bearer ${apiKey}`,
          "anthropic-version": "2023-06-01",
        },
      });

      if (!resp.ok) {
        console.log(`[CostPoller] Anthropic usage API returned ${resp.status} — skipping`);
        return;
      }

      const data = await resp.json() as Record<string, unknown>;
      const reportedTotal = typeof data.total_cost === "number" ? data.total_cost : 0;

      await this.recordSnapshot(
        "anthropic",
        periodStart,
        periodEnd,
        reportedTotal,
        data,
      );
    } catch (err) {
      console.error("[CostPoller] Anthropic API fetch failed:", err);
    }
  }

  /**
   * Poll OpenRouter usage.
   * GET /api/v1/auth/key returns { data: { usage, limit } }
   */
  private async pollOpenRouter(): Promise<void> {
    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      console.log("[CostPoller] OPENROUTER_API_KEY not set — skipping OpenRouter poll");
      return;
    }

    const now = new Date();
    const periodStart = new Date(now.getFullYear(), now.getMonth(), 1);

    try {
      const resp = await fetch("https://openrouter.ai/api/v1/auth/key", {
        headers: { "Authorization": `Bearer ${apiKey}` },
      });

      if (!resp.ok) {
        console.log(`[CostPoller] OpenRouter API returned ${resp.status} — skipping`);
        return;
      }

      const json = await resp.json() as { data?: { usage?: number; limit?: number } };
      const reportedTotal = json.data?.usage ?? 0;

      await this.recordSnapshot(
        "openrouter",
        periodStart,
        now,
        reportedTotal,
        json,
      );
    } catch (err) {
      console.error("[CostPoller] OpenRouter API fetch failed:", err);
    }
  }

  /**
   * Poll Firecrawl credit usage.
   * GET /v2/team/credit-usage
   */
  private async pollFirecrawl(): Promise<void> {
    const apiKey = process.env.FIRECRAWL_API_KEY;
    if (!apiKey) {
      console.log("[CostPoller] FIRECRAWL_API_KEY not set — skipping Firecrawl poll");
      return;
    }

    const now = new Date();
    const periodStart = new Date(now.getFullYear(), now.getMonth(), 1);

    try {
      const resp = await fetch("https://api.firecrawl.dev/v2/team/credit-usage", {
        headers: { "Authorization": `Bearer ${apiKey}` },
      });

      if (!resp.ok) {
        console.log(`[CostPoller] Firecrawl API returned ${resp.status} — skipping`);
        return;
      }

      const json = await resp.json() as Record<string, unknown>;
      // Firecrawl returns remaining credits vs plan credits.
      // We estimate usage as (plan_credits - remaining_credits) mapped to dollar value.
      const planCredits = typeof json.plan_credits === "number" ? json.plan_credits : 0;
      const remaining = typeof json.remaining_credits === "number" ? json.remaining_credits : planCredits;
      const usedFraction = planCredits > 0 ? (planCredits - remaining) / planCredits : 0;
      // Monthly cost is $50 for standard plan
      const reportedTotal = usedFraction * 50;

      await this.recordSnapshot(
        "firecrawl",
        periodStart,
        now,
        reportedTotal,
        json,
      );
    } catch (err) {
      console.error("[CostPoller] Firecrawl API fetch failed:", err);
    }
  }

  /**
   * Auto-insert fixed cost entries for the current month if they don't exist yet.
   */
  private async generateFixedCosts(): Promise<void> {
    const now = new Date();
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
      .toISOString()
      .split("T")[0];

    const { rows: providers } = await this.pool.query<ProviderRow>(
      `SELECT * FROM cost_providers WHERE provider_type = 'fixed_subscription' AND enabled = TRUE`,
    );

    for (const p of providers) {
      if (p.monthly_fixed <= 0) continue;

      await this.pool.query(
        `INSERT INTO fixed_cost_entries (provider, month, amount_usd, description)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT (provider, month) DO NOTHING`,
        [p.id, monthStart, p.monthly_fixed, `${p.display_name} — auto-generated`],
      );
    }

    // Also insert api_subscription providers (like Firecrawl) as fixed costs
    const { rows: apiSubs } = await this.pool.query<ProviderRow>(
      `SELECT * FROM cost_providers WHERE provider_type = 'api_subscription' AND enabled = TRUE AND monthly_fixed > 0`,
    );

    for (const p of apiSubs) {
      await this.pool.query(
        `INSERT INTO fixed_cost_entries (provider, month, amount_usd, description)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT (provider, month) DO NOTHING`,
        [p.id, monthStart, p.monthly_fixed, `${p.display_name} subscription — auto-generated`],
      );
    }
  }

  /**
   * Record a cost snapshot and reconcile against our budget_events.
   */
  private async recordSnapshot(
    provider: string,
    periodStart: Date,
    periodEnd: Date,
    reportedTotal: number,
    rawResponse: unknown,
  ): Promise<void> {
    // Compute our total from budget_events for the same period
    const { rows } = await this.pool.query<{ computed: string }>(
      `SELECT COALESCE(SUM(cost_usd), 0) AS computed
       FROM budget_events
       WHERE provider = $1
         AND timestamp >= $2
         AND timestamp <= $3`,
      [provider, periodStart.toISOString(), periodEnd.toISOString()],
    );
    const computedTotal = parseFloat(rows[0]?.computed ?? "0");
    const delta = reportedTotal - computedTotal;

    await this.pool.query(
      `INSERT INTO cost_snapshots (provider, period_start, period_end, reported_total, computed_total, delta, raw_response)
       VALUES ($1, $2, $3, $4, $5, $6, $7)`,
      [
        provider,
        periodStart.toISOString().split("T")[0],
        periodEnd.toISOString().split("T")[0],
        reportedTotal,
        computedTotal,
        delta,
        JSON.stringify(rawResponse),
      ],
    );

    // Update last_polled_at
    await this.pool.query(
      `UPDATE cost_providers SET last_polled_at = NOW() WHERE id = $1`,
      [provider],
    );

    // If delta > $5, insert a reconciliation budget_event to close the gap
    if (Math.abs(delta) > 5) {
      console.log(`[CostPoller] ${provider}: reconciliation needed — delta $${delta.toFixed(2)} (reported: $${reportedTotal.toFixed(2)}, computed: $${computedTotal.toFixed(2)})`);
      await this.pool.query(
        `INSERT INTO budget_events (timestamp, project, cost_usd, model, provider, category, source)
         VALUES (NOW(), 'platform', $1, $2, $3, 'api_calls', 'provider_poll')`,
        [delta, provider, provider],
      );
    } else {
      console.log(`[CostPoller] ${provider}: in sync (delta $${delta.toFixed(2)})`);
    }
  }
}
