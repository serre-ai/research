import { describe, it, expect, vi, beforeAll, afterAll, beforeEach } from "vitest";
import type { AddressInfo } from "node:net";
import { request } from "node:http";
import type pg from "pg";

// ------------------------------------------------------------------
// Mock pg Pool — passed via config.pool so createApi never calls
// `new Pool()`. This sidesteps constructor-mocking issues entirely.
// ------------------------------------------------------------------

let mockQuery: ReturnType<typeof vi.fn>;

function makePool(): pg.Pool {
  mockQuery = vi.fn().mockResolvedValue({ rows: [] });

  return {
    query: mockQuery,
    connect: vi.fn().mockResolvedValue({
      query: vi.fn().mockResolvedValue({ rows: [] }),
      on: vi.fn(),
      release: vi.fn(),
    }),
    on: vi.fn(),
    end: vi.fn().mockResolvedValue(undefined),
  } as unknown as pg.Pool;
}

// Mock embeddings — no API keys in test environment
vi.mock("../../embeddings.js", () => ({
  createEmbedFn: () => null,
  getEmbeddingDimension: () => 1024,
}));

// ------------------------------------------------------------------
// Helper: make HTTP requests against the test server
// ------------------------------------------------------------------

const API_KEY = "test-api-key-for-unit-tests";

function httpGet(
  port: number,
  path: string,
  headers: Record<string, string> = {},
): Promise<{ status: number; headers: Record<string, string>; body: unknown }> {
  return new Promise((resolve, reject) => {
    const req = request(
      {
        hostname: "127.0.0.1",
        port,
        path,
        method: "GET",
        headers: { "Content-Type": "application/json", ...headers },
      },
      (res) => {
        let data = "";
        res.on("data", (chunk: string) => (data += chunk));
        res.on("end", () => {
          const h: Record<string, string> = {};
          for (const [k, v] of Object.entries(res.headers)) {
            if (v) h[k] = Array.isArray(v) ? v[0] : v;
          }
          try {
            resolve({ status: res.statusCode ?? 0, headers: h, body: JSON.parse(data) });
          } catch {
            resolve({ status: res.statusCode ?? 0, headers: h, body: data });
          }
        });
      },
    );
    req.on("error", reject);
    req.end();
  });
}

// ------------------------------------------------------------------
// Bootstrap: create the API once for all tests in this file.
// Uses port 0 (OS-assigned) and a mock pool to avoid real DB.
// ------------------------------------------------------------------

let port: number;
let close: () => Promise<void>;

beforeAll(async () => {
  const { createApi } = await import("../../api.js");

  const pool = makePool();

  const result = createApi({
    port: 0,
    apiKey: API_KEY,
    databaseUrl: "postgresql://mock:mock@localhost:5432/mock",
    pool,
  });

  // Wait for the server to be listening
  await new Promise<void>((resolve) => {
    if (result.server.listening) {
      resolve();
    } else {
      result.server.on("listening", resolve);
    }
  });

  port = (result.server.address() as AddressInfo).port;
  close = result.close;
});

afterAll(async () => {
  await close();
});

beforeEach(() => {
  mockQuery.mockReset();
  mockQuery.mockResolvedValue({ rows: [] });
});

// ==================================================================
// Auth middleware
// ==================================================================

describe("auth middleware", () => {
  it("rejects requests without API key", async () => {
    const { status, body } = await httpGet(port, "/api/projects");
    expect(status).toBe(401);
    expect(body).toEqual(expect.objectContaining({ error: expect.stringContaining("Unauthorized") }));
  });

  it("rejects requests with wrong API key", async () => {
    const { status } = await httpGet(port, "/api/projects", { "X-Api-Key": "wrong-key" });
    expect(status).toBe(401);
  });

  it("allows health endpoint without API key", async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ "?column?": 1 }] }); // SELECT 1
    const { status } = await httpGet(port, "/api/health");
    expect(status).toBe(200);
  });
});

// ==================================================================
// GET /api/health
// ==================================================================

describe("GET /api/health", () => {
  it("returns 200 with status ok when database is reachable", async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ "?column?": 1 }] });

    const { status, body } = await httpGet(port, "/api/health");

    expect(status).toBe(200);
    const data = body as Record<string, unknown>;
    expect(data.status).toBe("ok");
    expect(data.database).toBe("connected");
  });

  it("returns memory info", async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ "?column?": 1 }] });

    const { body } = await httpGet(port, "/api/health");

    const data = body as Record<string, unknown>;
    const mem = data.memory as Record<string, number>;
    expect(mem).toBeDefined();
    expect(typeof mem.free_mb).toBe("number");
    expect(typeof mem.total_mb).toBe("number");
    expect(typeof mem.percent_used).toBe("number");
    expect(mem.total_mb).toBeGreaterThan(0);
  });

  it("returns uptime and cpu count", async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ "?column?": 1 }] });

    const { body } = await httpGet(port, "/api/health");

    const data = body as Record<string, unknown>;
    expect(typeof data.uptime_s).toBe("number");
    expect(typeof data.cpus).toBe("number");
    expect((data.cpus as number)).toBeGreaterThan(0);
    expect(data.timestamp).toBeDefined();
    expect(data.started_at).toBeDefined();
  });

  it("returns 503 with status degraded when database is unreachable", async () => {
    mockQuery.mockRejectedValueOnce(new Error("connection refused"));

    const { status, body } = await httpGet(port, "/api/health");

    expect(status).toBe(503);
    const data = body as Record<string, unknown>;
    expect(data.status).toBe("degraded");
    expect(data.database).toBe("unavailable");
  });
});

// ==================================================================
// GET /api/budget
// ==================================================================

describe("GET /api/budget", () => {
  function setupBudgetMocks() {
    // The budget route runs 9 sequential queries. Mock each in order.
    // 1. Monthly variable costs
    mockQuery.mockResolvedValueOnce({
      rows: [{ variable_usd: "123.45", tokens_in: "500000", tokens_out: "200000", events: "42" }],
    });
    // 2. Fixed costs
    mockQuery.mockResolvedValueOnce({
      rows: [{ fixed_usd: "50.00" }],
    });
    // 3. By provider (variable)
    mockQuery.mockResolvedValueOnce({
      rows: [
        { provider: "anthropic", display_name: "Anthropic", provider_type: "api_variable", cost_usd: "100.00" },
      ],
    });
    // 4. By provider (fixed)
    mockQuery.mockResolvedValueOnce({
      rows: [],
    });
    // 5. By project
    mockQuery.mockResolvedValueOnce({
      rows: [{ project: "reasoning-gaps", cost_usd: "80.00", events: "30" }],
    });
    // 6. By model
    mockQuery.mockResolvedValueOnce({
      rows: [{ model: "claude-sonnet-4-6", cost_usd: "90.00", events: "35" }],
    });
    // 7. Burn rate (7-day)
    mockQuery.mockResolvedValueOnce({
      rows: [{ days: "7", total: "140.00" }],
    });
    // 8. Reconciliation snapshots
    mockQuery.mockResolvedValueOnce({
      rows: [],
    });
    // 9. Daily spend history
    mockQuery.mockResolvedValueOnce({
      rows: [{ day: "2026-03-30", total: "20.00" }],
    });
  }

  it("returns budget shape with monthly, burnRate, and limits", async () => {
    setupBudgetMocks();

    const { status, body } = await httpGet(port, "/api/budget", { "X-Api-Key": API_KEY });

    expect(status).toBe(200);
    const data = body as Record<string, unknown>;

    // Monthly breakdown
    const monthly = data.monthly as Record<string, unknown>;
    expect(monthly).toBeDefined();
    expect(typeof monthly.total_usd).toBe("number");
    expect(typeof monthly.variable_usd).toBe("number");
    expect(typeof monthly.fixed_usd).toBe("number");
    expect(monthly.total_usd).toBeCloseTo(173.45, 2);

    // Burn rate
    const burnRate = data.burnRate as Record<string, unknown>;
    expect(burnRate).toBeDefined();
    expect(typeof burnRate.daily_7d_avg).toBe("number");
    expect(typeof burnRate.projected_month_end).toBe("number");

    // Limits
    const limits = data.limits as Record<string, unknown>;
    expect(limits).toBeDefined();
    expect(typeof limits.daily_usd).toBe("number");
    expect(typeof limits.monthly_usd).toBe("number");
  });

  it("returns provider and project breakdowns as arrays", async () => {
    setupBudgetMocks();

    const { body } = await httpGet(port, "/api/budget", { "X-Api-Key": API_KEY });

    const data = body as Record<string, unknown>;
    expect(Array.isArray(data.byProvider)).toBe(true);
    expect(Array.isArray(data.byProject)).toBe(true);
    expect(Array.isArray(data.byModel)).toBe(true);
  });

  it("returns 500 when database query fails", async () => {
    mockQuery.mockRejectedValueOnce(new Error("table does not exist"));

    const { status, body } = await httpGet(port, "/api/budget", { "X-Api-Key": API_KEY });

    expect(status).toBe(500);
    expect(body).toEqual(expect.objectContaining({ error: expect.any(String) }));
  });
});

// ==================================================================
// GET /api/projects
// ==================================================================

describe("GET /api/projects", () => {
  it("returns array of projects", async () => {
    mockQuery.mockResolvedValueOnce({
      rows: [
        {
          id: "proj-1",
          name: "reasoning-gaps",
          title: "Reasoning Gaps",
          venue: "NeurIPS",
          phase: "writing",
          status: "active",
          confidence: 0.85,
          current_focus: "polish",
          current_activity: null,
          notes: null,
          branch: "main",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-03-30T12:00:00Z",
        },
        {
          id: "proj-2",
          name: "verification-complexity",
          title: "Verification Complexity",
          venue: "ICLR",
          phase: "experiments",
          status: "active",
          confidence: 0.70,
          current_focus: "benchmarks",
          current_activity: null,
          notes: null,
          branch: "main",
          created_at: "2026-02-01T00:00:00Z",
          updated_at: "2026-03-28T12:00:00Z",
        },
      ],
    });

    const { status, body } = await httpGet(port, "/api/projects", { "X-Api-Key": API_KEY });

    expect(status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
    const projects = body as Record<string, unknown>[];
    expect(projects).toHaveLength(2);
    expect(projects[0].name).toBe("reasoning-gaps");
    expect(projects[1].name).toBe("verification-complexity");
  });

  it("returns empty array when no projects exist", async () => {
    mockQuery.mockResolvedValueOnce({ rows: [] });

    const { status, body } = await httpGet(port, "/api/projects", { "X-Api-Key": API_KEY });

    expect(status).toBe(200);
    expect(body).toEqual([]);
  });

  it("returns 500 when database query fails", async () => {
    mockQuery.mockRejectedValueOnce(new Error("connection lost"));

    const { status, body } = await httpGet(port, "/api/projects", { "X-Api-Key": API_KEY });

    expect(status).toBe(500);
    expect(body).toEqual(expect.objectContaining({ error: expect.any(String) }));
  });
});

// ==================================================================
// Security headers
// ==================================================================

describe("security headers", () => {
  it("includes standard security headers on responses", async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ "?column?": 1 }] });

    const { headers } = await httpGet(port, "/api/health");

    expect(headers["x-content-type-options"]).toBe("nosniff");
    expect(headers["x-frame-options"]).toBe("DENY");
    expect(headers["content-security-policy"]).toContain("default-src 'none'");
    expect(headers["referrer-policy"]).toBe("strict-origin-when-cross-origin");
  });
});
