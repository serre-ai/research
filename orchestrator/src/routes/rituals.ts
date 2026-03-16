import express, { type Request, type Response } from "express";
import type pg from "pg";

// ============================================================
// Ritual routes — scheduled collective interactions
// Mount at /api/rituals
// ============================================================

export function ritualRoutes(pool: pg.Pool): express.Router {
  const router = express.Router();

  // POST /api/rituals — schedule a new ritual
  router.post("/", async (req: Request, res: Response) => {
    const { ritual_type, scheduled_for, facilitator, participants, metadata } = req.body as {
      ritual_type?: string;
      scheduled_for?: string;
      facilitator?: string;
      participants?: string[];
      metadata?: Record<string, unknown>;
    };

    if (!ritual_type || !scheduled_for) {
      res.status(400).json({ error: "Required: ritual_type, scheduled_for" });
      return;
    }

    const validTypes = [
      "standup", "retrospective", "pre_mortem",
      "reading_club", "calibration_review", "values_review",
    ];
    if (!validTypes.includes(ritual_type)) {
      res.status(400).json({ error: `ritual_type must be one of: ${validTypes.join(", ")}` });
      return;
    }

    try {
      const { rows } = await pool.query(
        `INSERT INTO rituals (ritual_type, scheduled_for, facilitator, participants, metadata)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING *`,
        [
          ritual_type,
          scheduled_for,
          facilitator ?? null,
          participants ?? [],
          metadata ? JSON.stringify(metadata) : "{}",
        ],
      );

      res.status(201).json(rows[0]);
    } catch (err) {
      console.error("POST /api/rituals error:", err);
      res.status(500).json({ error: "Failed to schedule ritual" });
    }
  });

  // GET /api/rituals — list rituals
  router.get("/", async (req: Request, res: Response) => {
    const type = req.query["type"] as string | undefined;
    const status = req.query["status"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 50, 200);
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const conditions: string[] = [];
      const params: unknown[] = [];
      let paramIdx = 1;

      if (type) {
        conditions.push(`ritual_type = $${paramIdx++}`);
        params.push(type);
      }
      if (status) {
        conditions.push(`status = $${paramIdx++}`);
        params.push(status);
      }

      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

      const { rows } = await pool.query(
        `SELECT * FROM rituals
         ${where}
         ORDER BY scheduled_for DESC
         LIMIT $${paramIdx++} OFFSET $${paramIdx++}`,
        [...params, limit, offset],
      );

      res.json(rows);
    } catch (err) {
      console.error("GET /api/rituals error:", err);
      res.status(500).json({ error: "Failed to fetch rituals" });
    }
  });

  // GET /api/rituals/upcoming — rituals in next 48h
  router.get("/upcoming", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT * FROM rituals
         WHERE status = 'scheduled'
           AND scheduled_for BETWEEN NOW() AND NOW() + INTERVAL '48 hours'
         ORDER BY scheduled_for ASC`,
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/rituals/upcoming error:", err);
      res.status(500).json({ error: "Failed to fetch upcoming rituals" });
    }
  });

  // GET /api/rituals/history — past rituals with outcomes
  router.get("/history", async (req: Request, res: Response) => {
    const type = req.query["type"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 20, 100);

    try {
      const conditions = ["status = 'completed'"];
      const params: unknown[] = [];
      let paramIdx = 1;

      if (type) {
        conditions.push(`ritual_type = $${paramIdx++}`);
        params.push(type);
      }

      const { rows } = await pool.query(
        `SELECT * FROM rituals
         WHERE ${conditions.join(" AND ")}
         ORDER BY scheduled_for DESC
         LIMIT $${paramIdx++}`,
        [...params, limit],
      );

      res.json(rows);
    } catch (err) {
      console.error("GET /api/rituals/history error:", err);
      res.status(500).json({ error: "Failed to fetch ritual history" });
    }
  });

  // GET /api/rituals/:id — ritual details
  router.get("/:id", async (req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT * FROM rituals WHERE id = $1`,
        [req.params.id],
      );
      if (rows.length === 0) {
        res.status(404).json({ error: "Ritual not found" });
        return;
      }
      res.json(rows[0]);
    } catch (err) {
      console.error("GET /api/rituals/:id error:", err);
      res.status(500).json({ error: "Failed to fetch ritual" });
    }
  });

  // PATCH /api/rituals/:id/start — start a ritual (create forum thread)
  router.patch("/:id/start", async (req: Request, res: Response) => {
    const { thread_id } = req.body as { thread_id?: string };

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE rituals
         SET status = 'active', thread_id = COALESCE($1, thread_id)
         WHERE id = $2 AND status = 'scheduled'
         RETURNING *`,
        [thread_id ?? null, req.params.id],
      );

      if (rowCount === 0) {
        const { rows: exists } = await pool.query(
          `SELECT id, status FROM rituals WHERE id = $1`,
          [req.params.id],
        );
        if (exists.length === 0) {
          res.status(404).json({ error: "Ritual not found" });
        } else {
          res.status(400).json({ error: `Ritual is ${exists[0].status}, not scheduled` });
        }
        return;
      }

      res.json(rows[0]);
    } catch (err) {
      console.error("PATCH /api/rituals/:id/start error:", err);
      res.status(500).json({ error: "Failed to start ritual" });
    }
  });

  // PATCH /api/rituals/:id/complete — complete a ritual with outcome
  router.patch("/:id/complete", async (req: Request, res: Response) => {
    const { outcome } = req.body as { outcome?: string };

    if (!outcome) {
      res.status(400).json({ error: "Required: outcome" });
      return;
    }

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE rituals
         SET status = 'completed', outcome = $1
         WHERE id = $2 AND status = 'active'
         RETURNING *`,
        [outcome, req.params.id],
      );

      if (rowCount === 0) {
        const { rows: exists } = await pool.query(
          `SELECT id, status FROM rituals WHERE id = $1`,
          [req.params.id],
        );
        if (exists.length === 0) {
          res.status(404).json({ error: "Ritual not found" });
        } else {
          res.status(400).json({ error: `Ritual is ${exists[0].status}, not active` });
        }
        return;
      }

      res.json(rows[0]);
    } catch (err) {
      console.error("PATCH /api/rituals/:id/complete error:", err);
      res.status(500).json({ error: "Failed to complete ritual" });
    }
  });

  return router;
}
