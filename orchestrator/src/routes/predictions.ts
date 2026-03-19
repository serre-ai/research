import express, { type Request, type Response } from "express";
import type pg from "pg";

// ============================================================
// Prediction routes — claims, resolution, calibration
// Mount at /api/predictions
// ============================================================

export function predictionRoutes(pool: pg.Pool): express.Router {
  const router = express.Router();

  // POST /api/predictions — make a new prediction
  router.post("/", async (req: Request, res: Response) => {
    const { author, claim, probability, category, project } = req.body as {
      author?: string;
      claim?: string;
      probability?: number;
      category?: string;
      project?: string;
    };

    if (!author || !claim || probability === undefined) {
      res.status(400).json({ error: "Required: author, claim, probability" });
      return;
    }

    if (probability < 0 || probability > 1) {
      res.status(400).json({ error: "probability must be between 0.0 and 1.0" });
      return;
    }

    const validCategories = ["eval", "deadline", "field", "quality", "platform", "other"];
    if (category && !validCategories.includes(category)) {
      res.status(400).json({ error: `category must be one of: ${validCategories.join(", ")}` });
      return;
    }

    try {
      const { rows } = await pool.query(
        `INSERT INTO predictions (author, claim, probability, category, project)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING *`,
        [author, claim, probability, category ?? null, project ?? null],
      );

      res.status(201).json(rows[0]);
    } catch (err) {
      console.error("POST /api/predictions error:", err);
      res.status(500).json({ error: "Failed to create prediction" });
    }
  });

  // GET /api/predictions — list predictions
  router.get("/", async (req: Request, res: Response) => {
    const author = req.query["author"] as string | undefined;
    const resolved = req.query["resolved"] as string | undefined;
    const category = req.query["category"] as string | undefined;
    const project = req.query["project"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 50, 200);
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const conditions: string[] = [];
      const params: unknown[] = [];
      let paramIdx = 1;

      if (author) {
        conditions.push(`author = $${paramIdx++}`);
        params.push(author);
      }
      if (resolved === "true") {
        conditions.push("outcome IS NOT NULL");
      } else if (resolved === "false") {
        conditions.push("outcome IS NULL");
      }
      if (category) {
        conditions.push(`category = $${paramIdx++}`);
        params.push(category);
      }
      if (project) {
        conditions.push(`project = $${paramIdx++}`);
        params.push(project);
      }

      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

      const { rows } = await pool.query(
        `SELECT * FROM predictions
         ${where}
         ORDER BY created_at DESC
         LIMIT $${paramIdx++} OFFSET $${paramIdx++}`,
        [...params, limit, offset],
      );

      res.json(rows);
    } catch (err) {
      console.error("GET /api/predictions error:", err);
      res.status(500).json({ error: "Failed to fetch predictions" });
    }
  });

  // GET /api/predictions/calibration/:agent — calibration stats
  // (must be before /:id to avoid matching "calibration" as an ID)
  router.get("/calibration/:agent", async (req: Request, res: Response) => {
    const agent = req.params.agent as string;

    try {
      const calibration = await getCalibration(pool, agent);
      res.json(calibration);
    } catch (err) {
      console.error("GET /api/predictions/calibration/:agent error:", err);
      res.status(500).json({ error: "Failed to fetch calibration" });
    }
  });

  // GET /api/predictions/leaderboard — all agents ranked by Brier score
  // (must be before /:id to avoid matching "leaderboard" as an ID)
  router.get("/leaderboard", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT * FROM v_prediction_calibration ORDER BY brier_score ASC`,
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/predictions/leaderboard error:", err);
      res.status(500).json({ error: "Failed to fetch leaderboard" });
    }
  });

  // GET /api/predictions/:id — single prediction
  router.get("/:id", async (req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT * FROM predictions WHERE id = $1`,
        [req.params.id],
      );
      if (rows.length === 0) {
        res.status(404).json({ error: "Prediction not found" });
        return;
      }
      res.json(rows[0]);
    } catch (err) {
      console.error("GET /api/predictions/:id error:", err);
      res.status(500).json({ error: "Failed to fetch prediction" });
    }
  });

  // PATCH /api/predictions/:id/resolve — resolve a prediction
  router.patch("/:id/resolve", async (req: Request, res: Response) => {
    const { outcome, resolved_by, resolution_note } = req.body as {
      outcome?: boolean;
      resolved_by?: string;
      resolution_note?: string;
    };

    if (outcome === undefined || !resolved_by) {
      res.status(400).json({ error: "Required: outcome (boolean), resolved_by" });
      return;
    }

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE predictions
         SET outcome = $1, resolved_by = $2, resolution_note = $3, resolved_at = NOW()
         WHERE id = $4 AND outcome IS NULL
         RETURNING *`,
        [outcome, resolved_by, resolution_note ?? null, req.params.id],
      );

      if (rowCount === 0) {
        const { rows: exists } = await pool.query(
          `SELECT id, outcome FROM predictions WHERE id = $1`,
          [req.params.id],
        );
        if (exists.length === 0) {
          res.status(404).json({ error: "Prediction not found" });
        } else {
          res.status(400).json({ error: "Prediction already resolved" });
        }
        return;
      }

      // Update author's calibration in agent_state
      await updateCalibration(pool, rows[0].author);

      res.json(rows[0]);
    } catch (err) {
      console.error("PATCH /api/predictions/:id/resolve error:", err);
      res.status(500).json({ error: "Failed to resolve prediction" });
    }
  });

  return router;
}

// ============================================================
// Helpers
// ============================================================

async function getCalibration(pool: pg.Pool, agent: string) {
  // Overall Brier score
  const { rows: overall } = await pool.query(
    `SELECT
       COUNT(*) AS total_resolved,
       ROUND(AVG((probability - outcome::int) * (probability - outcome::int))::numeric, 4) AS brier_score,
       COUNT(*) FILTER (WHERE outcome = TRUE) AS correct,
       COUNT(*) FILTER (WHERE outcome = FALSE) AS incorrect
     FROM predictions
     WHERE author = $1 AND outcome IS NOT NULL`,
    [agent],
  );

  // By confidence bucket
  const { rows: buckets } = await pool.query(
    `SELECT
       CASE
         WHEN probability < 0.2 THEN '0.0-0.2'
         WHEN probability < 0.4 THEN '0.2-0.4'
         WHEN probability < 0.6 THEN '0.4-0.6'
         WHEN probability < 0.8 THEN '0.6-0.8'
         ELSE '0.8-1.0'
       END AS bucket,
       COUNT(*) AS count,
       ROUND(AVG(outcome::int)::numeric, 4) AS actual_rate,
       ROUND(AVG(probability)::numeric, 4) AS mean_predicted
     FROM predictions
     WHERE author = $1 AND outcome IS NOT NULL
     GROUP BY bucket
     ORDER BY bucket`,
    [agent],
  );

  // By category
  const { rows: byCategory } = await pool.query(
    `SELECT
       category,
       COUNT(*) AS count,
       ROUND(AVG((probability - outcome::int) * (probability - outcome::int))::numeric, 4) AS brier_score
     FROM predictions
     WHERE author = $1 AND outcome IS NOT NULL AND category IS NOT NULL
     GROUP BY category
     ORDER BY brier_score ASC`,
    [agent],
  );

  return {
    agent,
    ...overall[0],
    by_bucket: buckets,
    by_category: byCategory,
  };
}

async function updateCalibration(pool: pg.Pool, agent: string) {
  const calibration = await getCalibration(pool, agent);
  await pool.query(
    `UPDATE agent_state
     SET calibration = $1, updated_at = NOW()
     WHERE agent = $2`,
    [JSON.stringify(calibration), agent],
  );
}
