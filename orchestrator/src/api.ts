import { createServer, type Server as HttpServer } from "node:http";
import { readFile, readdir } from "node:fs/promises";
import { join, basename } from "node:path";
import { freemem, totalmem, cpus } from "node:os";
import express, { type Request, type Response, type NextFunction } from "express";
import { WebSocketServer, type WebSocket } from "ws";
import pg from "pg";
import { EvalJobManager, type EvalJobStatus } from "./eval-manager.js";
import { ActivityLogger, type EventType } from "./logger.js";
import type { Daemon } from "./daemon.js";
import type { BacklogManager } from "./backlog.js";
import type { DigestStore } from "./digest-store.js";
import { forumRoutes } from "./routes/forum.js";
import { messageRoutes } from "./routes/messages.js";
import { predictionRoutes } from "./routes/predictions.js";
import { agentStateRoutes } from "./routes/agent-state.js";
import { ritualRoutes } from "./routes/rituals.js";
import { governanceRoutes } from "./routes/governance.js";
import { collectiveContextRoutes } from "./routes/collective-context.js";
import { triggerRoutes } from "./routes/triggers.js";
import { CollectiveSlack } from "./collective-slack.js";
import { knowledgeRoutes } from "./routes/knowledge.js";
import { eventRoutes } from "./routes/events.js";
import { KnowledgeGraph } from "./knowledge-graph.js";
import { createEmbedFn } from "./embeddings.js";
import { EventBus } from "./event-bus.js";
import { plannerRoutes } from "./routes/planner.js";
import { verificationRoutes } from "./routes/verification.js";
import { ClaimVerifier } from "./verification.js";
import { paperRoutes } from "./routes/paper.js";
import { literatureRoutes } from "./routes/literature.js";
import { LinearClient } from "./linear.js";

const { Pool } = pg;

// ============================================================
// Types
// ============================================================

export interface ApiConfig {
  port: number;
  apiKey: string;
  databaseUrl: string;
  corsOrigin?: string;
  pool?: pg.Pool; // shared pool from daemon — avoids creating a duplicate
}

interface WsClient {
  ws: WebSocket;
  channels: Set<string>;
}

// ============================================================
// Database pool (module-level, initialized in createApi)
// ============================================================

let pool: pg.Pool;

// ============================================================
// Auth middleware
// ============================================================

function authMiddleware(apiKey: string) {
  return (req: Request, res: Response, next: NextFunction): void => {
    // Health endpoint is public
    if (req.path === "/api/health") {
      next();
      return;
    }

    const provided =
      req.headers["x-api-key"] as string | undefined ??
      req.query["api_key"] as string | undefined;

    if (!provided || provided !== apiKey) {
      res.status(401).json({ error: "Unauthorized — provide X-Api-Key header" });
      return;
    }
    next();
  };
}

// ============================================================
// REST routes
// ============================================================

function projectRoutes(): express.Router {
  const router = express.Router();

  // GET /api/projects — list all projects
  router.get("/", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT id, name, title, venue, phase, status, confidence,
                current_focus, current_activity, notes, branch,
                created_at, updated_at
         FROM projects
         ORDER BY updated_at DESC`,
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/projects error:", err);
      res.status(500).json({ error: "Failed to fetch projects" });
    }
  });

  // GET /api/projects/:id/eval — eval progress and accuracy tables
  router.get("/:id/eval", async (req: Request, res: Response) => {
    try {
      // Checkpoint progress (from materialized view)
      const { rows: progress } = await pool.query(
        `SELECT model, task, condition, completed_count, correct_count,
                accuracy, avg_latency_ms, last_updated
         FROM checkpoints
         ORDER BY model, task, condition`,
      );

      // Accuracy by difficulty for this project's tasks
      const { rows: byDifficulty } = await pool.query(
        `SELECT model, task, condition, difficulty,
                COUNT(*) AS n,
                ROUND(AVG(correct::int)::numeric, 4) AS accuracy
         FROM eval_results
         GROUP BY model, task, condition, difficulty
         ORDER BY model, task, condition, difficulty`,
      );

      // Active/recent runs
      const { rows: runs } = await pool.query(
        `SELECT run_id, model, task, condition, status,
                started_at, completed_at, accuracy, instance_count,
                total_expected, metadata
         FROM eval_runs
         ORDER BY started_at DESC
         LIMIT 100`,
      );

      res.json({ progress, byDifficulty, runs });
    } catch (err) {
      console.error("GET /api/projects/:id/eval error:", err);
      res.status(500).json({ error: "Failed to fetch eval data" });
    }
  });

  // GET /api/projects/:id/eval/instances — instance-level eval data
  router.get("/:id/eval/instances", async (req: Request, res: Response) => {
    const { model, task, condition } = req.query as {
      model?: string;
      task?: string;
      condition?: string;
    };

    if (!model || !task) {
      res.status(400).json({ error: "Required query params: model, task" });
      return;
    }

    try {
      const { rows } = await pool.query(
        `SELECT id, model, task, condition, difficulty, correct AS is_correct,
                latency_ms AS response_time_ms, tokens AS tokens_used, created_at
         FROM eval_results
         WHERE project_id = $1
           AND model = $2
           AND task = $3
           AND ($4::text IS NULL OR condition = $4)
         ORDER BY created_at DESC
         LIMIT 100`,
        [req.params.id, model, task, condition ?? null],
      );

      const { rows: countRows } = await pool.query(
        `SELECT COUNT(*) AS total
         FROM eval_results
         WHERE project_id = $1
           AND model = $2
           AND task = $3
           AND ($4::text IS NULL OR condition = $4)`,
        [req.params.id, model, task, condition ?? null],
      );

      res.json({
        instances: rows,
        total: parseInt(countRows[0]?.total ?? "0", 10),
      });
    } catch (err) {
      console.error("GET /api/projects/:id/eval/instances error:", err);
      res.status(500).json({ error: "Failed to fetch eval instances" });
    }
  });

  // GET /api/projects/:id/sessions — session history
  router.get("/:id/sessions", async (req: Request, res: Response) => {
    const limit = parseInt(req.query["limit"] as string) || 50;
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const { rows } = await pool.query(
        `SELECT session_id AS id, project AS project_id, agent_type, model,
                tokens_used AS token_usage, cost_usd AS cost, commits_created,
                status, error, started_at, duration_s AS duration_seconds
         FROM sessions
         WHERE project = $1
         ORDER BY started_at DESC
         LIMIT $2 OFFSET $3`,
        [req.params.id, limit, offset],
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/projects/:id/sessions error:", err);
      res.status(500).json({ error: "Failed to fetch sessions" });
    }
  });

  // GET /api/projects/:id/decisions — decision log
  router.get("/:id/decisions", async (req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT id, project, date, decision, rationale, created_at
         FROM decisions
         WHERE project = $1
         ORDER BY date DESC, created_at DESC`,
        [req.params.id],
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/projects/:id/decisions error:", err);
      res.status(500).json({ error: "Failed to fetch decisions" });
    }
  });

  return router;
}

function budgetRoutes(budgetTracker?: import("./budget-tracker.js").BudgetTracker, broadcast?: (channel: string, data: unknown) => void): express.Router {
  const router = express.Router();

  // GET /api/budget — comprehensive monthly budget with fixed + variable costs
  router.get("/", async (_req: Request, res: Response) => {
    try {
      // Variable API costs this month
      const { rows: monthlyRows } = await pool.query(
        `SELECT
           COALESCE(SUM(cost_usd), 0) AS variable_usd,
           COALESCE(SUM(tokens_input), 0) AS tokens_in,
           COALESCE(SUM(tokens_output), 0) AS tokens_out,
           COUNT(*) AS events
         FROM budget_events
         WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)`,
      );
      const variableUsd = parseFloat(monthlyRows[0].variable_usd);

      // Fixed costs this month
      const { rows: fixedRows } = await pool.query(
        `SELECT COALESCE(SUM(amount_usd), 0) AS fixed_usd
         FROM fixed_cost_entries
         WHERE month = DATE_TRUNC('month', CURRENT_DATE)::date`,
      );
      const fixedUsd = parseFloat(fixedRows[0].fixed_usd);
      const totalUsd = variableUsd + fixedUsd;

      // By provider (variable + fixed combined)
      const { rows: byProviderVariable } = await pool.query(
        `SELECT
           COALESCE(be.provider, 'unknown') AS provider,
           COALESCE(cp.display_name, be.provider, 'Unknown') AS display_name,
           COALESCE(cp.provider_type, 'api_variable') AS provider_type,
           SUM(be.cost_usd) AS cost_usd
         FROM budget_events be
         LEFT JOIN cost_providers cp ON cp.id = be.provider
         WHERE DATE_TRUNC('month', be.timestamp) = DATE_TRUNC('month', CURRENT_DATE)
         GROUP BY be.provider, cp.display_name, cp.provider_type
         ORDER BY cost_usd DESC`,
      );

      const { rows: byProviderFixed } = await pool.query(
        `SELECT
           f.provider,
           cp.display_name,
           cp.provider_type,
           SUM(f.amount_usd) AS cost_usd
         FROM fixed_cost_entries f
         JOIN cost_providers cp ON cp.id = f.provider
         WHERE f.month = DATE_TRUNC('month', CURRENT_DATE)::date
         GROUP BY f.provider, cp.display_name, cp.provider_type`,
      );

      // Merge variable and fixed into single provider list
      const providerMap = new Map<string, { provider: string; display_name: string; provider_type: string; cost_usd: number }>();
      for (const r of byProviderVariable) {
        providerMap.set(r.provider, {
          provider: r.provider,
          display_name: r.display_name,
          provider_type: r.provider_type,
          cost_usd: parseFloat(r.cost_usd),
        });
      }
      for (const r of byProviderFixed) {
        const existing = providerMap.get(r.provider);
        if (existing) {
          existing.cost_usd += parseFloat(r.cost_usd);
        } else {
          providerMap.set(r.provider, {
            provider: r.provider,
            display_name: r.display_name,
            provider_type: r.provider_type,
            cost_usd: parseFloat(r.cost_usd),
          });
        }
      }
      const byProvider = Array.from(providerMap.values()).sort((a, b) => b.cost_usd - a.cost_usd);

      // By project this month
      const { rows: byProject } = await pool.query(
        `SELECT project, SUM(cost_usd) AS cost_usd, COUNT(*) AS events
         FROM budget_events
         WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)
         GROUP BY project
         ORDER BY cost_usd DESC`,
      );

      // By model this month
      const { rows: byModel } = await pool.query(
        `SELECT model, SUM(cost_usd) AS cost_usd, COUNT(*) AS events
         FROM budget_events
         WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)
         GROUP BY model
         ORDER BY cost_usd DESC`,
      );

      // Burn rate (7-day daily average)
      const { rows: burnRows } = await pool.query(
        `SELECT
           COUNT(DISTINCT DATE(timestamp)) AS days,
           COALESCE(SUM(cost_usd), 0) AS total
         FROM budget_events
         WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'`,
      );
      const burnDays = Math.max(parseInt(burnRows[0].days) || 1, 1);
      const burnTotal = parseFloat(burnRows[0].total);
      const daily7dAvg = burnTotal / burnDays;

      const now = new Date();
      const daysRemaining = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate() - now.getDate();
      const projectedMonthEnd = totalUsd + (daily7dAvg * daysRemaining);

      // Reconciliation status
      const { rows: reconRows } = await pool.query(
        `SELECT provider, delta, polled_at
         FROM cost_snapshots
         WHERE polled_at >= CURRENT_DATE - INTERVAL '24 hours'
         ORDER BY polled_at DESC
         LIMIT 10`,
      );
      const maxDelta = reconRows.reduce((max, r) => Math.max(max, Math.abs(parseFloat(r.delta ?? "0"))), 0);

      // Daily spend history (last 7 days)
      const { rows: dailyHistory } = await pool.query(
        `SELECT DATE(timestamp) AS day, SUM(cost_usd) AS total
         FROM budget_events
         WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
         GROUP BY DATE(timestamp)
         ORDER BY day`,
      );

      const monthlyLimit = parseFloat(process.env.MONTHLY_BUDGET_USD ?? "1000");
      const dailyLimit = parseFloat(process.env.DAILY_BUDGET_USD ?? "40");

      res.json({
        monthly: {
          total_usd: totalUsd,
          variable_usd: variableUsd,
          fixed_usd: fixedUsd,
          tokens_in: parseInt(monthlyRows[0].tokens_in),
          tokens_out: parseInt(monthlyRows[0].tokens_out),
          events: parseInt(monthlyRows[0].events),
        },
        byProvider,
        byProject,
        byModel,
        burnRate: {
          daily_7d_avg: daily7dAvg,
          projected_month_end: projectedMonthEnd,
          daily_history: dailyHistory,
        },
        reconciliation: {
          last_check: reconRows[0]?.polled_at ?? null,
          max_delta: maxDelta,
          recent: reconRows,
        },
        limits: {
          daily_usd: dailyLimit,
          monthly_usd: monthlyLimit,
        },
      });
    } catch (err) {
      console.error("GET /api/budget error:", err);
      res.status(500).json({ error: "Failed to fetch budget data" });
    }
  });

  // POST /api/budget/manual — record a manual cost entry
  router.post("/manual", async (req: Request, res: Response) => {
    if (!budgetTracker) {
      res.status(503).json({ error: "Budget tracker not available" });
      return;
    }

    const { provider, cost_usd, description, category } = req.body as {
      provider?: string;
      cost_usd?: number;
      description?: string;
      category?: string;
    };

    if (!provider || cost_usd == null || !description) {
      res.status(400).json({ error: "Required: provider, cost_usd, description" });
      return;
    }

    try {
      await budgetTracker.recordManual({ provider, costUsd: cost_usd, description, category });
      broadcast?.("budget", { type: "cost_recorded", provider, cost_usd, description, timestamp: new Date().toISOString() });
      res.json({ recorded: true, provider, cost_usd, description });
    } catch (err) {
      console.error("POST /api/budget/manual error:", err);
      res.status(500).json({ error: "Failed to record manual entry" });
    }
  });

  // GET /api/budget/providers — list all registered cost providers
  router.get("/providers", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT id, display_name, provider_type, monthly_fixed, pricing_config, enabled, last_polled_at
         FROM cost_providers
         ORDER BY provider_type, display_name`,
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/budget/providers error:", err);
      res.status(500).json({ error: "Failed to fetch providers" });
    }
  });

  return router;
}

function evalControlRoutes(
  broadcast: (channel: string, data: unknown) => void,
  evalManager?: EvalJobManager,
): express.Router {
  const router = express.Router();

  // POST /api/eval/jobs — enqueue a new eval job
  router.post("/jobs", async (req: Request, res: Response) => {
    if (!evalManager) {
      res.status(503).json({ error: "Eval manager not available (daemon not running)" });
      return;
    }

    const { model, task, condition, project } = req.body as {
      model?: string;
      task?: string;
      condition?: string;
      project?: string;
    };

    if (!model || !task || !condition) {
      res.status(400).json({ error: "Required: model, task, condition" });
      return;
    }

    try {
      const job = await evalManager.enqueue({ model, task, condition, project });

      broadcast("eval-progress", {
        type: "job_queued",
        job,
        timestamp: new Date().toISOString(),
      });

      res.json(job);
    } catch (err) {
      console.error("POST /api/eval/jobs error:", err);
      res.status(500).json({ error: "Failed to enqueue eval job" });
    }
  });

  // GET /api/eval/jobs — list all eval jobs
  router.get("/jobs", async (req: Request, res: Response) => {
    if (!evalManager) {
      res.status(503).json({ error: "Eval manager not available" });
      return;
    }

    const status = req.query["status"] as EvalJobStatus | undefined;
    res.json(evalManager.listJobs(status));
  });

  // DELETE /api/eval/jobs/:id — cancel a job
  router.delete("/jobs/:id", async (req: Request, res: Response) => {
    if (!evalManager) {
      res.status(503).json({ error: "Eval manager not available" });
      return;
    }

    const jobId = req.params.id as string;
    const cancelled = await evalManager.cancel(jobId);
    if (!cancelled) {
      res.status(404).json({ error: "Job not found or not cancellable" });
      return;
    }

    broadcast("eval-progress", {
      type: "job_cancelled",
      jobId,
      timestamp: new Date().toISOString(),
    });

    res.json({ id: jobId, status: "cancelled" });
  });

  // GET /api/eval/status — summary of eval pipeline status
  router.get("/status", async (_req: Request, res: Response) => {
    if (!evalManager) {
      res.status(503).json({ error: "Eval manager not available" });
      return;
    }

    const jobs = evalManager.listJobs();
    const running = jobs.filter((j) => j.status === "running");
    const queued = jobs.filter((j) => j.status === "queued");
    const completed = jobs.filter((j) => j.status === "completed");
    const failed = jobs.filter((j) => j.status === "failed");

    res.json({
      running: running.length,
      queued: queued.length,
      completed: completed.length,
      failed: failed.length,
      total: jobs.length,
      runningJobs: running,
      queuedJobs: queued,
    });
  });

  // Legacy: POST /api/eval/start — DB-only run tracking (kept for compatibility)
  router.post("/start", async (req: Request, res: Response) => {
    const { model, task, condition, instances } = req.body as {
      model?: string;
      task?: string;
      condition?: string;
      instances?: number;
    };

    if (!model || !task || !condition) {
      res.status(400).json({ error: "Required: model, task, condition" });
      return;
    }

    const runId = `${model}_${task}_${condition}`;

    try {
      await pool.query(
        `INSERT INTO eval_runs (run_id, model, task, condition, status, total_expected)
         VALUES ($1, $2, $3, $4, 'running', $5)
         ON CONFLICT (run_id) DO UPDATE SET
           status = 'running',
           started_at = NOW(),
           total_expected = COALESCE($5, eval_runs.total_expected)`,
        [runId, model, task, condition, instances ?? null],
      );

      broadcast("eval-progress", {
        type: "run_started",
        runId,
        model,
        task,
        condition,
        timestamp: new Date().toISOString(),
      });

      res.json({ runId, status: "running" });
    } catch (err) {
      console.error("POST /api/eval/start error:", err);
      res.status(500).json({ error: "Failed to start eval run" });
    }
  });

  // Legacy: POST /api/eval/stop
  router.post("/stop", async (req: Request, res: Response) => {
    const { runId } = req.body as { runId?: string };

    if (!runId) {
      res.status(400).json({ error: "Required: runId" });
      return;
    }

    try {
      const { rowCount } = await pool.query(
        `UPDATE eval_runs SET status = 'cancelled', completed_at = NOW()
         WHERE run_id = $1 AND status = 'running'`,
        [runId],
      );

      if (rowCount === 0) {
        res.status(404).json({ error: "No running eval found with that runId" });
        return;
      }

      broadcast("eval-progress", {
        type: "run_stopped",
        runId,
        timestamp: new Date().toISOString(),
      });

      res.json({ runId, status: "cancelled" });
    } catch (err) {
      console.error("POST /api/eval/stop error:", err);
      res.status(500).json({ error: "Failed to stop eval run" });
    }
  });

  return router;
}

// ============================================================
// Health endpoint
// ============================================================

function healthRoute(startedAt: number, kg?: KnowledgeGraph): express.Router {
  const router = express.Router();

  router.get("/", async (_req: Request, res: Response) => {
    const mem = {
      free_mb: Math.round(freemem() / 1024 / 1024),
      total_mb: Math.round(totalmem() / 1024 / 1024),
      percent_used: Math.round(((totalmem() - freemem()) / totalmem()) * 100),
    };

    // Database health
    let dbOk = false;
    try {
      await pool.query("SELECT 1");
      dbOk = true;
    } catch {
      // db unavailable
    }

    // Knowledge graph stats
    let knowledgeGraph = null;
    if (kg) {
      try {
        knowledgeGraph = await kg.getStats();
      } catch {
        // knowledge graph not ready
      }
    }

    res.json({
      status: "ok",
      uptime_s: Math.round((Date.now() - startedAt) / 1000),
      started_at: new Date(startedAt).toISOString(),
      memory: mem,
      cpus: cpus().length,
      database: dbOk ? "connected" : "unavailable",
      knowledge_graph: knowledgeGraph,
      timestamp: new Date().toISOString(),
    });
  });

  return router;
}

// ============================================================
// WebSocket handler
// ============================================================

function setupWebSocket(
  server: HttpServer,
  apiKey: string,
): { wss: WebSocketServer; broadcast: (channel: string, data: unknown) => void } {
  const wss = new WebSocketServer({ server, path: "/api/ws" });
  const clients: Set<WsClient> = new Set();

  wss.on("connection", (ws, req) => {
    // Authenticate via query param: ws://host/api/ws?api_key=xxx
    const url = new URL(req.url ?? "", `http://${req.headers.host}`);
    const key = url.searchParams.get("api_key");
    if (key !== apiKey) {
      ws.close(4001, "Unauthorized");
      return;
    }

    const client: WsClient = { ws, channels: new Set() };
    clients.add(client);

    ws.on("message", (raw) => {
      try {
        const msg = JSON.parse(raw.toString()) as { type: string; channel?: string };

        if (msg.type === "subscribe" && msg.channel) {
          client.channels.add(msg.channel);
          ws.send(JSON.stringify({ type: "subscribed", channel: msg.channel }));
        }

        if (msg.type === "unsubscribe" && msg.channel) {
          client.channels.delete(msg.channel);
          ws.send(JSON.stringify({ type: "unsubscribed", channel: msg.channel }));
        }
      } catch {
        // Ignore malformed messages
      }
    });

    ws.on("close", () => {
      clients.delete(client);
    });

    ws.on("error", () => {
      clients.delete(client);
    });

    // Send welcome
    ws.send(
      JSON.stringify({
        type: "connected",
        channels: ["eval-progress", "logs", "budget", "health"],
        timestamp: new Date().toISOString(),
      }),
    );
  });

  const broadcast = (channel: string, data: unknown): void => {
    const msg = JSON.stringify({ channel, data, timestamp: new Date().toISOString() });
    for (const client of clients) {
      if (client.channels.has(channel) && client.ws.readyState === 1 /* OPEN */) {
        client.ws.send(msg);
      }
    }
  };

  return { wss, broadcast };
}

// ============================================================
// Public API: create and mount the Express app
// ============================================================

// ============================================================
// Dispatch routes (POST /api/sessions/dispatch)
// ============================================================

function dispatchRoutes(daemon?: Daemon): express.Router {
  const router = express.Router();

  // POST /api/sessions/dispatch — queue an external session dispatch
  router.post("/dispatch", async (req: Request, res: Response) => {
    if (!daemon) {
      res.status(503).json({ error: "Daemon not available" });
      return;
    }

    const { project, agent_type, priority, reason, triggered_by, chain_depth } = req.body as {
      project?: string;
      agent_type?: string;
      priority?: string;
      reason?: string;
      triggered_by?: string;
      chain_depth?: number;
    };

    if (!project || !agent_type || !reason || !triggered_by) {
      res.status(400).json({ error: "Required: project, agent_type, reason, triggered_by" });
      return;
    }

    try {
      const dispatch = await daemon.queueSession({
        project,
        agent_type: agent_type as any,
        priority: (priority as any) ?? "normal",
        reason,
        triggered_by,
        chain_depth,
      });
      res.json(dispatch);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("Rate limit") || msg.includes("Budget") || msg.includes("Chain depth") || msg.includes("active session")) {
        res.status(429).json({ error: msg });
      } else {
        res.status(500).json({ error: msg });
      }
    }
  });

  // GET /api/sessions/dispatch/queue — view dispatch queue
  router.get("/dispatch/queue", async (_req: Request, res: Response) => {
    if (!daemon) {
      res.status(503).json({ error: "Daemon not available" });
      return;
    }
    res.json({
      queue: daemon.getDispatchQueue(),
      recent: daemon.getDispatchLog().slice(-20),
    });
  });

  // POST /api/sessions/run-issue — trigger a session for a specific Linear issue
  router.post("/run-issue", async (req: Request, res: Response) => {
    const { identifier } = req.body as { identifier?: string };
    if (!identifier || typeof identifier !== "string") {
      res.status(400).json({ error: "identifier required (e.g., 'DW-141')" });
      return;
    }

    const linear = daemon?.getLinearClient();
    if (!linear) {
      res.status(503).json({ error: "Linear not configured" });
      return;
    }

    try {
      const issue = await linear.getIssueByIdentifier(identifier);
      if (!issue) {
        res.status(404).json({ error: "Issue " + identifier + " not found" });
        return;
      }

      const dwProject = LinearClient.projectNameToDW(issue.project?.name ?? "");
      if (!dwProject) {
        res.status(400).json({ error: "No project mapping for " + (issue.project?.name || "unknown") });
        return;
      }

      if (await linear.isBlocked(issue.id)) {
        const blockers = await linear.getBlockingIssues(issue.id);
        res.status(409).json({
          error: "Issue is blocked",
          blockedBy: blockers.map((b) => ({ identifier: b.identifier, title: b.title })),
        });
        return;
      }

      const briefData = linear.issueToBrief(issue, dwProject);

      if (!daemon) {
        res.status(503).json({ error: "Daemon not available" });
        return;
      }

      const result = await daemon.queueSession({
        project: briefData.projectName,
        agent_type: briefData.agentType as any,
        priority: "critical",
        reason: "Manual trigger: " + identifier,
        triggered_by: "run-issue-api",
      });

      await linear.transitionIssue(issue.id, "In Progress");

      res.json({
        status: "queued",
        identifier,
        title: issue.title,
        project: dwProject,
        agentType: briefData.agentType,
        dispatchId: result.id,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Internal error";
      if (msg.includes("Rate limit") || msg.includes("Budget") || msg.includes("active session")) {
        res.status(429).json({ error: msg });
      } else {
        res.status(500).json({ error: msg });
      }
    }
  });

  return router;
}

// ============================================================
// Backlog routes (GET/POST/PATCH /api/backlog)
// ============================================================

function backlogRoutes(backlog?: BacklogManager): express.Router {
  const router = express.Router();

  // GET /api/backlog — list tickets
  router.get("/", async (req: Request, res: Response) => {
    if (!backlog) {
      res.status(503).json({ error: "Backlog not available" });
      return;
    }
    const status = req.query["status"] as string | undefined;
    const priority = req.query["priority"] as string | undefined;
    const category = req.query["category"] as string | undefined;
    const tickets = await backlog.list({ status, priority, category });
    res.json(tickets);
  });

  // POST /api/backlog — create a ticket
  router.post("/", async (req: Request, res: Response) => {
    if (!backlog) {
      res.status(503).json({ error: "Backlog not available" });
      return;
    }

    const { title, filed_by, priority, category, description } = req.body as {
      title?: string;
      filed_by?: string;
      priority?: string;
      category?: string;
      description?: string;
    };

    if (!title || !filed_by || !priority || !category) {
      res.status(400).json({ error: "Required: title, filed_by, priority, category" });
      return;
    }

    const ticket = await backlog.create({
      title,
      filed_by,
      priority: priority as any,
      category: category as any,
      description,
    });
    res.status(201).json(ticket);
  });

  // PATCH /api/backlog/:id — update a ticket
  router.patch("/:id", async (req: Request, res: Response) => {
    if (!backlog) {
      res.status(503).json({ error: "Backlog not available" });
      return;
    }

    const { status, priority, assigned_to, session_id } = req.body as {
      status?: string;
      priority?: string;
      assigned_to?: string;
      session_id?: string;
    };

    const ticket = await backlog.update(req.params.id as string, {
      status: status as any,
      priority: priority as any,
      assigned_to,
      session_id,
    });

    if (!ticket) {
      res.status(404).json({ error: "Ticket not found" });
      return;
    }
    res.json(ticket);
  });

  // GET /api/backlog/:id — get a single ticket
  router.get("/:id", async (req: Request, res: Response) => {
    if (!backlog) {
      res.status(503).json({ error: "Backlog not available" });
      return;
    }
    const ticket = await backlog.get(req.params.id as string);
    if (!ticket) {
      res.status(404).json({ error: "Ticket not found" });
      return;
    }
    res.json(ticket);
  });

  return router;
}

// ============================================================
// Digest routes (POST/GET /api/memory/digest)
// ============================================================

function digestRoutes(digestStore?: DigestStore): express.Router {
  const router = express.Router();

  // POST /api/memory/digest — save a daily digest
  router.post("/", async (req: Request, res: Response) => {
    if (!digestStore) {
      res.status(503).json({ error: "Digest store not available" });
      return;
    }

    const { date, digest, key_events, filed_by } = req.body as {
      date?: string;
      digest?: string;
      key_events?: string[];
      filed_by?: string;
    };

    if (!date || !digest || !filed_by) {
      res.status(400).json({ error: "Required: date, digest, filed_by" });
      return;
    }

    const entry = await digestStore.save({
      date,
      digest,
      key_events: key_events ?? [],
      filed_by,
    });
    res.status(201).json(entry);
  });

  // GET /api/memory/digest/latest — get the most recent digest
  router.get("/latest", async (_req: Request, res: Response) => {
    if (!digestStore) {
      res.status(503).json({ error: "Digest store not available" });
      return;
    }
    const latest = await digestStore.getLatest();
    if (!latest) {
      res.status(404).json({ error: "No digests found" });
      return;
    }
    res.json(latest);
  });

  // GET /api/memory/digest/:date — get a digest by date
  router.get("/:date", async (req: Request, res: Response) => {
    if (!digestStore) {
      res.status(503).json({ error: "Digest store not available" });
      return;
    }
    const dateParam = req.params.date as string;
    const entry = await digestStore.getByDate(dateParam);
    if (!entry) {
      res.status(404).json({ error: "No digest for " + dateParam });
      return;
    }
    res.json(entry);
  });

  // GET /api/memory/digest — list available dates
  router.get("/", async (_req: Request, res: Response) => {
    if (!digestStore) {
      res.status(503).json({ error: "Digest store not available" });
      return;
    }
    const dates = await digestStore.listDates();
    res.json(dates);
  });

  return router;
}

// ============================================================
// Enhanced daemon health routes
// ============================================================

function daemonHealthRoutes(daemon?: Daemon): express.Router {
  const router = express.Router();

  // GET /api/daemon/health — full daemon state
  router.get("/", async (_req: Request, res: Response) => {
    if (!daemon) {
      res.status(503).json({ error: "Daemon not available" });
      return;
    }
    const health = await daemon.getHealth();
    res.json(health);
  });

  return router;
}

// ============================================================
// Project status update routes
// ============================================================

function projectStatusRoutes(): express.Router {
  const router = express.Router();

  // PATCH /api/projects/:id/status — update project status.yaml
  router.patch("/:id/status", async (req: Request, res: Response) => {
    const projectId = req.params.id as string;
    const updates = req.body as Record<string, unknown>;

    if (!updates || Object.keys(updates).length === 0) {
      res.status(400).json({ error: "Request body must contain fields to update" });
      return;
    }

    try {
      const { readFile, writeFile } = await import("node:fs/promises");
      const { join } = await import("node:path");
      const { parse, stringify } = await import("yaml");

      const statusPath = join(process.cwd(), "projects", projectId, "status.yaml");
      const content = await readFile(statusPath, "utf-8");
      const status = parse(content) as Record<string, unknown>;

      // Apply allowed updates
      const allowedFields = ["phase", "current_focus", "current_activity", "confidence", "notes", "status"];
      for (const field of allowedFields) {
        if (field in updates) {
          status[field] = updates[field];
        }
      }
      status.updated = new Date().toISOString().split("T")[0];

      await writeFile(statusPath, stringify(status), "utf-8");
      res.json({ updated: true, project: projectId, fields: Object.keys(updates).filter((k) => allowedFields.includes(k)) });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("ENOENT")) {
        res.status(404).json({ error: "Project not found: " + projectId });
      } else {
        res.status(500).json({ error: "Failed to update status: " + msg });
      }
    }
  });

  return router;
}

function qualityRoutes(getQuality?: (project: string) => unknown[]): express.Router {
  const router = express.Router();

  // GET /api/quality/:project — session quality history
  router.get("/:project", (req: Request, res: Response) => {
    if (!getQuality) {
      res.status(503).json({ error: "Quality tracking not available (daemon not running)" });
      return;
    }
    const projectId = req.params.project as string;
    const sessions = getQuality(projectId);
    const avg = sessions.length > 0
      ? sessions.reduce<number>((sum, s) => sum + ((s as Record<string, number>).score ?? 0), 0) / sessions.length
      : null;
    res.json({ project: projectId, averageQuality: avg, sessions });
  });

  return router;
}

function activityRoutes(logger?: ActivityLogger): express.Router {
  const router = express.Router();

  // GET /api/activity/recent?count=50&type=...&project=...
  router.get("/recent", async (req: Request, res: Response) => {
    if (!logger) {
      res.status(503).json({ error: "Activity logger not available" });
      return;
    }

    const count = Math.min(parseInt(req.query["count"] as string) || 50, 500);
    const type = req.query["type"] as EventType | undefined;
    const project = req.query["project"] as string | undefined;

    try {
      const events = await logger.recent(count, { type, project });
      res.json(events);
    } catch (err) {
      console.error("GET /api/activity/recent error:", err);
      res.status(500).json({ error: "Failed to fetch activity" });
    }
  });

  return router;
}

// ============================================================
// Session detail routes (GET /api/sessions/:id, /:id/transcript)
// ============================================================

function sessionDetailRoutes(): express.Router {
  const router = express.Router();

  // GET /api/sessions/:id — single session metadata
  router.get("/:id", async (req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT session_id, project, agent_type, model, status,
                started_at, duration_s, tokens_used, cost_usd,
                commits_created, error
         FROM sessions WHERE session_id = $1`,
        [req.params.id],
      );
      if (rows.length === 0) {
        res.status(404).json({ error: "Session not found" });
        return;
      }
      res.json(rows[0]);
    } catch (err) {
      console.error("GET /api/sessions/:id error:", err);
      res.status(500).json({ error: "Failed to fetch session" });
    }
  });

  // GET /api/sessions/:id/transcript — paginated transcript lines
  router.get("/:id/transcript", async (req: Request, res: Response) => {
    const offset = Math.max(parseInt(req.query["offset"] as string) || 0, 0);
    const limit = Math.min(Math.max(parseInt(req.query["limit"] as string) || 50, 1), 500);

    try {
      // Look up the session to find its project
      const { rows } = await pool.query(
        `SELECT project FROM sessions WHERE session_id = $1`,
        [req.params.id],
      );

      if (rows.length === 0) {
        res.status(404).json({ error: "Session not found" });
        return;
      }

      const project = rows[0].project as string;
      const transcriptPath = join(process.cwd(), "projects", project, "sessions", `${req.params.id}.jsonl`);

      let content: string;
      try {
        content = await readFile(transcriptPath, "utf-8");
      } catch {
        // No transcript file — return empty
        res.json({ lines: [], total: 0, offset, limit });
        return;
      }

      const allLines = content.split("\n").filter((l) => l.trim().length > 0);
      const total = allLines.length;
      const sliced = allLines.slice(offset, offset + limit);

      res.json({ lines: sliced, total, offset, limit });
    } catch (err) {
      console.error("GET /api/sessions/:id/transcript error:", err);
      res.status(500).json({ error: "Failed to fetch transcript" });
    }
  });

  return router;
}

// ============================================================
// Project phases route (GET /api/projects/:id/phases)
// ============================================================

function projectPhaseRoutes(): express.Router {
  const router = express.Router();

  // GET /api/projects/:id/phases — structured phase data from status.yaml
  router.get("/:id/phases", async (req: Request, res: Response) => {
    try {
      const { parse } = await import("yaml");
      const projectId = req.params.id as string;
      const statusPath = join(process.cwd(), "projects", projectId, "status.yaml");

      let content: string;
      try {
        content = await readFile(statusPath, "utf-8");
      } catch {
        res.status(404).json({ error: "Project not found or status.yaml missing" });
        return;
      }

      const status = parse(content) as Record<string, unknown>;

      // Extract current phase
      const currentPhase = (status.phase as string) ?? null;

      // Extract phases — handle various formats
      let phases: Array<{ name: string; status: string }> = [];

      if (Array.isArray(status.phases)) {
        // Already an array — normalize each entry
        phases = (status.phases as unknown[]).map((p) => {
          if (typeof p === "string") {
            return { name: p, status: p === currentPhase ? "active" : "pending" };
          }
          if (typeof p === "object" && p !== null) {
            const obj = p as Record<string, unknown>;
            return {
              name: (obj.name as string) ?? (obj.phase as string) ?? "unknown",
              status: (obj.status as string) ?? (obj.name === currentPhase || obj.phase === currentPhase ? "active" : "pending"),
            };
          }
          return { name: String(p), status: "pending" };
        });
      } else if (typeof status.phases === "object" && status.phases !== null) {
        // Object with phase names as keys
        phases = Object.entries(status.phases as Record<string, unknown>).map(([name, val]) => ({
          name,
          status: typeof val === "string" ? val : ((val as Record<string, unknown>)?.status as string) ?? "pending",
        }));
      }

      // If no phases field but we have a current phase, generate a basic structure
      if (phases.length === 0 && currentPhase) {
        const defaultPhases = [
          "literature_review", "framework", "benchmark_design",
          "evaluation", "paper_writing", "submission",
        ];
        const currentIdx = defaultPhases.indexOf(currentPhase);
        phases = defaultPhases.map((name, idx) => ({
          name,
          status: idx < currentIdx ? "complete" : idx === currentIdx ? "active" : "pending",
        }));
      }

      res.json({ current_phase: currentPhase, phases });
    } catch (err) {
      console.error("GET /api/projects/:id/phases error:", err);
      res.status(500).json({ error: "Failed to fetch project phases" });
    }
  });

  return router;
}

// ============================================================
// Budget daily history route (GET /api/budget/daily-history)
// ============================================================

function budgetDailyHistoryRoutes(): express.Router {
  const router = express.Router();

  // GET /api/budget/daily-history — 30-day daily spending history
  router.get("/daily-history", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT DATE(timestamp) AS date,
                SUM(cost_usd) AS total_usd,
                COUNT(*) AS event_count
         FROM budget_events
         WHERE timestamp >= NOW() - INTERVAL '30 days'
         GROUP BY DATE(timestamp)
         ORDER BY date ASC`,
      );

      const days = rows.map((r) => ({
        date: r.date instanceof Date ? r.date.toISOString().split("T")[0] : String(r.date),
        total_usd: parseFloat(r.total_usd),
        event_count: parseInt(r.event_count),
      }));

      res.json({ days });
    } catch (err) {
      console.error("GET /api/budget/daily-history error:", err);
      res.status(500).json({ error: "Failed to fetch daily budget history" });
    }
  });

  return router;
}

// ============================================================
// Agent definitions route (GET /api/agents/definitions)
// ============================================================

function agentDefinitionRoutes(): express.Router {
  const router = express.Router();

  // GET /api/agents/definitions — list agent definitions from .claude/agents/
  router.get("/definitions", async (_req: Request, res: Response) => {
    try {
      const agentsDir = join(process.cwd(), ".claude", "agents");

      let files: string[];
      try {
        const entries = await readdir(agentsDir);
        files = entries.filter((f) => f.endsWith(".md"));
      } catch {
        // Directory doesn't exist or unreadable
        res.json([]);
        return;
      }

      const agents = await Promise.all(
        files.map(async (file) => {
          const name = basename(file, ".md");
          let description = "";
          try {
            const content = await readFile(join(agentsDir, file), "utf-8");
            // Extract first non-heading, non-empty lines as description
            const lines = content.split("\n");
            const descLines: string[] = [];
            for (const line of lines) {
              if (line.startsWith("#")) continue;
              if (line.trim().length === 0 && descLines.length > 0) break;
              if (line.trim().length > 0) descLines.push(line.trim());
            }
            description = descLines.slice(0, 3).join(" ");
          } catch {
            // Could not read file
          }
          return { name, description, file };
        }),
      );

      res.json(agents);
    } catch (err) {
      console.error("GET /api/agents/definitions error:", err);
      res.status(500).json({ error: "Failed to fetch agent definitions" });
    }
  });

  return router;
}

// ============================================================
// Collective health route (GET /api/collective/health)
// ============================================================

function collectiveHealthRoutes(): express.Router {
  const router = express.Router();

  // GET /api/collective/health — aggregated collective health summary
  router.get("/health", async (_req: Request, res: Response) => {
    const result: {
      status: string;
      agents: { total: number; active: number };
      forum: { posts: number; threads: number };
      proposals: { active: number };
      last_activity: string | null;
    } = {
      status: "operational",
      agents: { total: 0, active: 0 },
      forum: { posts: 0, threads: 0 },
      proposals: { active: 0 },
      last_activity: null,
    };

    // Agent counts
    try {
      const { rows } = await pool.query(
        `SELECT COUNT(*) AS total,
                COUNT(*) FILTER (WHERE updated_at >= NOW() - INTERVAL '24 hours') AS active
         FROM agent_state`,
      );
      result.agents.total = parseInt(rows[0].total);
      result.agents.active = parseInt(rows[0].active);
    } catch {
      // Table may not exist yet
    }

    // Forum post/thread counts
    try {
      const { rows } = await pool.query(
        `SELECT COUNT(*) AS posts,
                COUNT(DISTINCT thread_id) AS threads
         FROM forum_posts`,
      );
      result.forum.posts = parseInt(rows[0].posts);
      result.forum.threads = parseInt(rows[0].threads);
    } catch {
      // Table may not exist yet
    }

    // Active proposals
    try {
      const { rows } = await pool.query(
        `SELECT COUNT(*) AS active
         FROM proposals
         WHERE status = 'open' OR status = 'voting'`,
      );
      result.proposals.active = parseInt(rows[0].active);
    } catch {
      // Table may not exist yet
    }

    // Last activity timestamp
    try {
      const { rows } = await pool.query(
        `SELECT MAX(created_at) AS last_activity FROM forum_posts`,
      );
      result.last_activity = rows[0].last_activity
        ? new Date(rows[0].last_activity).toISOString()
        : null;
    } catch {
      // Table may not exist yet
    }

    res.json(result);
  });

  return router;
}

export function createApi(
  config: ApiConfig,
  evalManager?: EvalJobManager,
  logger?: ActivityLogger,
  qualityGetter?: (project: string) => unknown[],
  daemon?: Daemon,
): {
  app: express.Application;
  server: HttpServer;
  broadcast: (channel: string, data: unknown) => void;
  close: () => Promise<void>;
} {
  const startedAt = Date.now();

  // Use shared pool if provided, else create own
  const ownPool = !config.pool;
  pool = config.pool ?? new Pool({
    connectionString: config.databaseUrl,
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 5000,
  });

  pool.on("error", (err) => {
    console.error("[API] Unexpected DB pool error:", err.message);
  });

  // Express app
  const app = express();
  app.use(express.json());

  // CORS
  app.use((_req: Request, res: Response, next: NextFunction) => {
    const origin = config.corsOrigin ?? "*";
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, X-Api-Key");
    if (_req.method === "OPTIONS") {
      res.sendStatus(204);
      return;
    }
    next();
  });

  // Auth
  app.use(authMiddleware(config.apiKey));

  // Create HTTP server (needed for WebSocket upgrade)
  const server = createServer(app);

  // WebSocket
  const { wss, broadcast } = setupWebSocket(server, config.apiKey);

  // Mount routes
  const kg = daemon?.getKnowledgeGraph() ?? new KnowledgeGraph(pool, createEmbedFn());

  // EventBus: use daemon's if available, otherwise create standalone
  const eventBus = daemon?.getEventBus() ?? new EventBus(pool);
  eventBus.setBroadcast(broadcast);

  app.use("/api/health", healthRoute(startedAt, kg));
  app.use("/api/knowledge", knowledgeRoutes(kg));
  app.use("/api/events", eventRoutes(eventBus));
  app.use("/api/projects", projectRoutes());
  app.use("/api/projects", projectStatusRoutes());
  app.use("/api/budget", budgetRoutes(daemon?.getBudgetTracker(), broadcast));
  app.use("/api/eval", evalControlRoutes(broadcast, evalManager));
  app.use("/api/activity", activityRoutes(logger));
  app.use("/api/quality", qualityRoutes(qualityGetter));
  app.use("/api/sessions", dispatchRoutes(daemon));
  app.use("/api/backlog", backlogRoutes(daemon?.getBacklogManager()));
  app.use("/api/memory/digest", digestRoutes(daemon?.getDigestStore()));
  app.use("/api/daemon/health", daemonHealthRoutes(daemon));

  // Collective routes (Sprints 2-3)
  const collectiveSlack = new CollectiveSlack();
  app.use("/api/forum", forumRoutes(pool, collectiveSlack));
  app.use("/api/messages", messageRoutes(pool));
  app.use("/api/predictions", predictionRoutes(pool));
  app.use("/api/agents", agentStateRoutes(pool));
  app.use("/api/rituals", ritualRoutes(pool));
  app.use("/api/governance", governanceRoutes(pool, collectiveSlack));

  // Collective integration routes (Sprint 9)
  app.use("/api/collective", collectiveContextRoutes(pool));
  app.use("/api/triggers", triggerRoutes(pool));

  // Research planner (Sprint 4)
  app.use("/api/planner", plannerRoutes(() => daemon?.getPlanner() ?? null));

  // Verification layer (Sprint 5)
  const verifier = daemon?.getVerifier() ?? new ClaimVerifier(pool, kg, process.cwd());
  app.use("/api/projects", verificationRoutes(verifier));

  // Paper build pipeline
  app.use("/api/paper", paperRoutes());

  // Literature intelligence
  app.use("/api/literature", literatureRoutes(() => daemon?.getLiteratureMonitor() ?? null));

  // Sprint 3C: New endpoints
  app.use("/api/sessions", sessionDetailRoutes());
  app.use("/api/projects", projectPhaseRoutes());
  app.use("/api/budget", budgetDailyHistoryRoutes());
  app.use("/api/agents", agentDefinitionRoutes());
  app.use("/api/collective", collectiveHealthRoutes());

  // Start listening
  server.listen(config.port, () => {
    console.log(`API server listening on port ${config.port}`);
  });

  // Broadcast health status every 60s
  const healthInterval = setInterval(() => {
    broadcast("health", {
      type: "health_check",
      status: "ok",
      uptime_s: Math.round((Date.now() - startedAt) / 1000),
      memory: { free_mb: Math.round(freemem() / 1048576), total_mb: Math.round(totalmem() / 1048576) },
      timestamp: new Date().toISOString(),
    });
  }, 60_000);

  const close = async (): Promise<void> => {
    clearInterval(healthInterval);

    // Close all WebSocket connections
    for (const client of wss.clients) {
      client.close(1001, "Server shutting down");
    }
    wss.close();

    // Wait for HTTP server to finish serving in-flight requests
    await new Promise<void>((resolve, reject) => {
      server.close((err) => (err ? reject(err) : resolve()));
    });

    // Only close pool if we created it (not shared from daemon)
    if (ownPool) {
      await pool.end();
    }
  };

  return { app, server, broadcast, close };
}

// ============================================================
// Standalone entry point (for testing without daemon)
// ============================================================

if (process.argv[1]?.endsWith("api.js")) {
  const config: ApiConfig = {
    port: parseInt(process.env.API_PORT ?? "3001", 10),
    apiKey: process.env.DEEPWORK_API_KEY ?? "",
    databaseUrl: process.env.DATABASE_URL ?? "postgresql://deepwork:deepwork@localhost:5432/deepwork",
    corsOrigin: process.env.CORS_ORIGIN,
  };

  if (!config.apiKey) {
    console.error("Error: DEEPWORK_API_KEY environment variable is required");
    process.exit(1);
  }

  createApi(config);
}
