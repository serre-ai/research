import { createServer, type Server as HttpServer } from "node:http";
import { freemem, totalmem, cpus } from "node:os";
import express, { type Request, type Response, type NextFunction } from "express";
import { WebSocketServer, type WebSocket } from "ws";
import pg from "pg";
import { EvalJobManager, type EvalJobStatus } from "./eval-manager.js";
import { ActivityLogger, type EventType } from "./logger.js";

const { Pool } = pg;

// ============================================================
// Types
// ============================================================

export interface ApiConfig {
  port: number;
  apiKey: string;
  databaseUrl: string;
  corsOrigin?: string;
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

  // GET /api/projects/:id/sessions — session history
  router.get("/:id/sessions", async (req: Request, res: Response) => {
    const limit = parseInt(req.query["limit"] as string) || 50;
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const { rows } = await pool.query(
        `SELECT session_id, project, agent_type, model,
                tokens_used, cost_usd, commits_created, status,
                error, started_at, duration_s
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

function budgetRoutes(): express.Router {
  const router = express.Router();

  // GET /api/budget — current spend, daily/monthly totals
  router.get("/", async (_req: Request, res: Response) => {
    try {
      // Today's spend
      const { rows: dailyRows } = await pool.query(
        `SELECT
           COALESCE(SUM(cost_usd), 0) AS daily_total,
           COALESCE(SUM(tokens_input), 0) AS daily_tokens_in,
           COALESCE(SUM(tokens_output), 0) AS daily_tokens_out,
           COUNT(*) AS daily_events
         FROM budget_events
         WHERE DATE(timestamp) = CURRENT_DATE`,
      );

      // This month's spend
      const { rows: monthlyRows } = await pool.query(
        `SELECT
           COALESCE(SUM(cost_usd), 0) AS monthly_total,
           COALESCE(SUM(tokens_input), 0) AS monthly_tokens_in,
           COALESCE(SUM(tokens_output), 0) AS monthly_tokens_out,
           COUNT(*) AS monthly_events
         FROM budget_events
         WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)`,
      );

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

      // Daily burn rate (last 7 days)
      const { rows: burnRate } = await pool.query(
        `SELECT DATE(timestamp) AS day, SUM(cost_usd) AS total
         FROM budget_events
         WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
         GROUP BY DATE(timestamp)
         ORDER BY day`,
      );

      res.json({
        daily: dailyRows[0],
        monthly: monthlyRows[0],
        byProject,
        byModel,
        burnRate,
        limits: {
          daily_usd: parseFloat(process.env.DAILY_BUDGET_USD ?? "40"),
          monthly_usd: parseFloat(process.env.MONTHLY_BUDGET_USD ?? "1000"),
        },
      });
    } catch (err) {
      console.error("GET /api/budget error:", err);
      res.status(500).json({ error: "Failed to fetch budget data" });
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

function healthRoute(startedAt: number): express.Router {
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

    res.json({
      status: "ok",
      uptime_s: Math.round((Date.now() - startedAt) / 1000),
      started_at: new Date(startedAt).toISOString(),
      memory: mem,
      cpus: cpus().length,
      database: dbOk ? "connected" : "unavailable",
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
        channels: ["eval-progress", "logs"],
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

export function createApi(config: ApiConfig, evalManager?: EvalJobManager, logger?: ActivityLogger): {
  app: express.Application;
  server: HttpServer;
  broadcast: (channel: string, data: unknown) => void;
  close: () => Promise<void>;
} {
  const startedAt = Date.now();

  // Initialize database pool
  pool = new Pool({
    connectionString: config.databaseUrl,
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 5000,
  });

  // Express app
  const app = express();
  app.use(express.json());

  // CORS
  app.use((_req: Request, res: Response, next: NextFunction) => {
    const origin = config.corsOrigin ?? "*";
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
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
  app.use("/api/health", healthRoute(startedAt));
  app.use("/api/projects", projectRoutes());
  app.use("/api/budget", budgetRoutes());
  app.use("/api/eval", evalControlRoutes(broadcast, evalManager));
  app.use("/api/activity", activityRoutes(logger));

  // Start listening
  server.listen(config.port, () => {
    console.log(`API server listening on port ${config.port}`);
  });

  const close = async (): Promise<void> => {
    wss.close();
    server.close();
    await pool.end();
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
