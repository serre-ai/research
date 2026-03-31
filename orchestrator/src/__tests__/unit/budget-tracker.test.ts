import { describe, it, expect, vi, beforeEach } from "vitest";
import { BudgetTracker } from "../../budget-tracker.js";
import type { ActivityLogger } from "../../logger.js";

// Mock pg — we never want real database connections in unit tests
vi.mock("pg", () => {
  return { default: { Pool: vi.fn() } };
});

// Mock fs operations
vi.mock("node:fs/promises", () => ({
  readFile: vi.fn(),
  mkdir: vi.fn().mockResolvedValue(undefined),
}));

// Mock atomic write
vi.mock("../../utils/atomic-write.js", () => ({
  atomicAppendJsonl: vi.fn().mockResolvedValue(undefined),
}));

import { readFile } from "node:fs/promises";

const mockReadFile = vi.mocked(readFile);

/** Minimal ActivityLogger stub. */
function makeLogger(): ActivityLogger {
  return { log: vi.fn().mockResolvedValue(undefined) } as unknown as ActivityLogger;
}

describe("BudgetTracker", () => {
  let tracker: BudgetTracker;
  let logger: ActivityLogger;

  beforeEach(() => {
    vi.clearAllMocks();
    logger = makeLogger();
    tracker = new BudgetTracker("/fake/root", logger);
  });

  // ------------------------------------------------------------------
  // computeAlertLevel (tested via getStatus → JSONL fallback)
  // ------------------------------------------------------------------
  describe("alert level calculation", () => {
    it("returns 'ok' when spending is below 80%", async () => {
      // Config: monthly_limit_usd = 1000, daily limit = 1000/30 ≈ 33.33
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 1000";
        if (p.endsWith("spending.jsonl")) {
          // Spend $5 today — well under 80% of ~$33/day
          const today = new Date().toISOString();
          return JSON.stringify({
            timestamp: today,
            projectName: "test",
            sessionId: "s1",
            agentType: "researcher",
            tokensInput: 1000,
            tokensOutput: 500,
            costUsd: 5,
            model: "claude-sonnet-4-6",
          });
        }
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.alertLevel).toBe("ok");
    });

    it("returns 'warning' when daily spend reaches 80%", async () => {
      // monthly_limit = 3000 (high enough that fixed=$455.50 doesn't push monthly over limit)
      // daily_limit = 3000/30 = 100
      // Spend $82 today → 82% of daily → "warning"
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 3000";
        if (p.endsWith("spending.jsonl")) {
          const today = new Date().toISOString();
          return JSON.stringify({
            timestamp: today,
            projectName: "test",
            sessionId: "s1",
            agentType: "researcher",
            tokensInput: 1000,
            tokensOutput: 500,
            costUsd: 82,
            model: "claude-sonnet-4-6",
          });
        }
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.alertLevel).toBe("warning");
    });

    it("returns 'critical' when daily spend reaches 95%", async () => {
      // monthly_limit = 3000, daily_limit = 100
      // Spend $96 today → 96% of daily → "critical"
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 3000";
        if (p.endsWith("spending.jsonl")) {
          const today = new Date().toISOString();
          return JSON.stringify({
            timestamp: today,
            projectName: "test",
            sessionId: "s1",
            agentType: "researcher",
            tokensInput: 1000,
            tokensOutput: 500,
            costUsd: 96,
            model: "claude-sonnet-4-6",
          });
        }
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.alertLevel).toBe("critical");
    });

    it("returns 'exceeded' when monthly spend exceeds limit", async () => {
      // monthly_limit = 100, fixed = 455.50
      // Variable spend = 0 but fixed alone exceeds 100
      // Total monthly = 0 + 455.50 = 455.50 > 100
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 100";
        if (p.endsWith("spending.jsonl")) return "";
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.alertLevel).toBe("exceeded");
    });
  });

  // ------------------------------------------------------------------
  // canSpend
  // ------------------------------------------------------------------
  describe("canSpend", () => {
    it("returns true when within both daily and monthly limits", async () => {
      // Large budget, minimal spending
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 10000";
        if (p.endsWith("spending.jsonl")) return "";
        throw new Error("ENOENT");
      });

      const result = await tracker.canSpend(5);
      expect(result).toBe(true);
    });

    it("returns false when estimated cost would exceed daily limit", async () => {
      // monthly_limit = 300, daily_limit = 10
      // Already spent $9 today, trying to spend $2 more
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 300";
        if (p.endsWith("spending.jsonl")) {
          const today = new Date().toISOString();
          return JSON.stringify({
            timestamp: today,
            projectName: "test",
            sessionId: "s1",
            agentType: "researcher",
            tokensInput: 1000,
            tokensOutput: 500,
            costUsd: 9,
            model: "claude-sonnet-4-6",
          });
        }
        throw new Error("ENOENT");
      });

      const result = await tracker.canSpend(2);
      expect(result).toBe(false);
    });

    it("returns false when estimated cost would exceed monthly limit", async () => {
      // monthly_limit = 500
      // Fixed costs = 455.50, variable = $40 → total = $495.50
      // Trying to spend $10 more → $505.50 > $500
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 500";
        if (p.endsWith("spending.jsonl")) {
          const today = new Date().toISOString();
          return JSON.stringify({
            timestamp: today,
            projectName: "test",
            sessionId: "s1",
            agentType: "researcher",
            tokensInput: 1000,
            tokensOutput: 500,
            costUsd: 40,
            model: "claude-sonnet-4-6",
          });
        }
        throw new Error("ENOENT");
      });

      const result = await tracker.canSpend(10);
      expect(result).toBe(false);
    });
  });

  // ------------------------------------------------------------------
  // JSONL fallback parsing
  // ------------------------------------------------------------------
  describe("JSONL fallback parsing", () => {
    it("aggregates spending by project", async () => {
      const thisMonth = new Date().toISOString().slice(0, 7);
      const today = new Date().toISOString().split("T")[0];
      const lines = [
        JSON.stringify({
          timestamp: `${today}T10:00:00Z`,
          projectName: "alpha",
          sessionId: "s1",
          agentType: "researcher",
          tokensInput: 1000,
          tokensOutput: 500,
          costUsd: 3.5,
          model: "claude-sonnet-4-6",
        }),
        JSON.stringify({
          timestamp: `${today}T11:00:00Z`,
          projectName: "beta",
          sessionId: "s2",
          agentType: "writer",
          tokensInput: 2000,
          tokensOutput: 1000,
          costUsd: 7.0,
          model: "claude-opus-4-6",
        }),
        JSON.stringify({
          timestamp: `${today}T12:00:00Z`,
          projectName: "alpha",
          sessionId: "s3",
          agentType: "experimenter",
          tokensInput: 500,
          tokensOutput: 200,
          costUsd: 1.5,
          model: "claude-haiku-4-5-20251001",
        }),
      ].join("\n");

      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 10000";
        if (p.endsWith("spending.jsonl")) return lines;
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.byProject["alpha"]).toBeCloseTo(5.0);
      expect(status.byProject["beta"]).toBeCloseTo(7.0);
      expect(status.dailySpent).toBeCloseTo(12.0);
      expect(status.variableSpent).toBeCloseTo(12.0);
    });

    it("skips malformed JSONL lines gracefully", async () => {
      const today = new Date().toISOString().split("T")[0];
      const lines = [
        "NOT VALID JSON",
        JSON.stringify({
          timestamp: `${today}T10:00:00Z`,
          projectName: "test",
          sessionId: "s1",
          agentType: "researcher",
          tokensInput: 1000,
          tokensOutput: 500,
          costUsd: 2.0,
          model: "claude-sonnet-4-6",
        }),
        "{broken",
      ].join("\n");

      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 10000";
        if (p.endsWith("spending.jsonl")) return lines;
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      // Only the valid line should be counted
      expect(status.dailySpent).toBeCloseTo(2.0);
    });

    it("returns zero spending when JSONL file does not exist", async () => {
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 10000";
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.dailySpent).toBe(0);
      expect(status.variableSpent).toBe(0);
    });

    it("defaults monthly limit to 1000 when config is missing", async () => {
      mockReadFile.mockImplementation(async () => {
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.monthlyLimit).toBe(1000);
      expect(status.dailyLimit).toBeCloseTo(1000 / 30);
    });
  });

  // ------------------------------------------------------------------
  // Burn rate in JSONL fallback
  // ------------------------------------------------------------------
  describe("burn rate (JSONL fallback)", () => {
    it("returns zero burn rate when no DB is available", async () => {
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 1000";
        if (p.endsWith("spending.jsonl")) return "";
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.burnRate.daily7dAvg).toBe(0);
      expect(status.burnRate.projectedMonthEnd).toBe(0);
    });
  });

  // ------------------------------------------------------------------
  // Status fields
  // ------------------------------------------------------------------
  describe("status shape", () => {
    it("includes fixed costs in JSONL fallback mode", async () => {
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 1000";
        if (p.endsWith("spending.jsonl")) return "";
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.fixedSpent).toBe(455.50);
      expect(status.monthlySpent).toBe(455.50); // fixed only, no variable
    });

    it("defaults avgCostPerSession and sessionsToday in JSONL fallback", async () => {
      mockReadFile.mockImplementation(async (path) => {
        const p = String(path);
        if (p.endsWith("config.yaml")) return "budget:\n  monthly_limit_usd: 1000";
        if (p.endsWith("spending.jsonl")) return "";
        throw new Error("ENOENT");
      });

      const status = await tracker.getStatus();
      expect(status.sessionsToday).toBe(0);
      expect(status.avgCostPerSession).toBe(2.0);
    });
  });
});
