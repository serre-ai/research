/**
 * Research Intelligence Engine API routes.
 *
 * Endpoints for signals, opportunities, and summary stats.
 */

import { Router, type Request, type Response } from "express";
import type pg from "pg";

export function researchIntelRoutes(pool: pg.Pool): Router {
  const r = Router();

  // GET /api/research-intel/signals — list signals
  // Query params: batch_date (YYYY-MM-DD), detector (gap|trend|...), limit (default 50)
  r.get("/signals", async (req: Request, res: Response) => {
    try {
      const batchDate = req.query.batch_date as string | undefined;
      const detector = req.query.detector as string | undefined;
      const limit = Math.min(parseInt(req.query.limit as string) || 50, 200);

      const conditions: string[] = [];
      const params: unknown[] = [];
      let idx = 1;

      if (batchDate) { conditions.push(`batch_date = $${idx++}`); params.push(batchDate); }
      if (detector) { conditions.push(`detector = $${idx++}`); params.push(detector); }

      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
      params.push(limit);

      const { rows } = await pool.query(
        `SELECT * FROM research_signals ${where} ORDER BY confidence DESC, created_at DESC LIMIT $${idx}`,
        params
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/research-intel/signals error:", err);
      res.status(500).json({ error: "Failed to fetch signals" });
    }
  });

  // GET /api/research-intel/opportunities — list opportunities
  // Query params: batch_date, status, limit
  r.get("/opportunities", async (req: Request, res: Response) => {
    try {
      const batchDate = req.query.batch_date as string | undefined;
      const status = req.query.status as string | undefined;
      const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);

      const conditions: string[] = [];
      const params: unknown[] = [];
      let idx = 1;

      if (batchDate) { conditions.push(`batch_date = $${idx++}`); params.push(batchDate); }
      if (status) { conditions.push(`status = $${idx++}`); params.push(status); }

      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
      params.push(limit);

      const { rows } = await pool.query(
        `SELECT * FROM research_opportunities ${where} ORDER BY composite_score DESC LIMIT $${idx}`,
        params
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/research-intel/opportunities error:", err);
      res.status(500).json({ error: "Failed to fetch opportunities" });
    }
  });

  // GET /api/research-intel/stats — summary stats
  r.get("/stats", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(`
        SELECT
          (SELECT COUNT(*)::int FROM research_signals WHERE batch_date = CURRENT_DATE) AS signals_today,
          (SELECT COUNT(*)::int FROM research_opportunities WHERE batch_date = CURRENT_DATE) AS opportunities_today,
          (SELECT COUNT(DISTINCT batch_date)::int FROM research_signals) AS total_batches,
          (SELECT COUNT(*)::int FROM research_signals) AS total_signals
      `);
      res.json(rows[0] || {});
    } catch (err) {
      console.error("GET /api/research-intel/stats error:", err);
      res.status(500).json({ error: "Failed to fetch stats" });
    }
  });

  return r;
}
