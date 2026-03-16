import express, { type Request, type Response } from "express";
import type pg from "pg";

// ============================================================
// Agent state routes — relationships, learnings, calibration
// Mount at /api/agents
// ============================================================

export function agentStateRoutes(pool: pg.Pool): express.Router {
  const router = express.Router();

  // GET /api/agents/:agent/state — full agent state
  router.get("/:agent/state", async (req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT * FROM agent_state WHERE agent = $1`,
        [req.params.agent],
      );
      if (rows.length === 0) {
        res.status(404).json({ error: "Agent not found" });
        return;
      }
      res.json(rows[0]);
    } catch (err) {
      console.error("GET /api/agents/:agent/state error:", err);
      res.status(500).json({ error: "Failed to fetch agent state" });
    }
  });

  // PATCH /api/agents/:agent/state — partial update (JSONB merge)
  router.patch("/:agent/state", async (req: Request, res: Response) => {
    const agent = req.params.agent;
    const updates = req.body as Record<string, unknown>;

    if (!updates || Object.keys(updates).length === 0) {
      res.status(400).json({ error: "Request body must contain fields to update" });
      return;
    }

    const allowedFields = ["relationships", "learned", "calibration", "interaction_stats"];
    const setClauses: string[] = [];
    const params: unknown[] = [];
    let paramIdx = 1;

    for (const field of allowedFields) {
      if (field in updates) {
        // Deep merge for JSONB objects, replace for arrays
        if (field === "learned") {
          // learned is an array — replace entirely
          setClauses.push(`${field} = $${paramIdx++}`);
          params.push(JSON.stringify(updates[field]));
        } else {
          // JSONB objects — deep merge with ||
          setClauses.push(`${field} = ${field} || $${paramIdx++}`);
          params.push(JSON.stringify(updates[field]));
        }
      }
    }

    if (setClauses.length === 0) {
      res.status(400).json({ error: `Allowed fields: ${allowedFields.join(", ")}` });
      return;
    }

    setClauses.push("updated_at = NOW()");

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE agent_state SET ${setClauses.join(", ")} WHERE agent = $${paramIdx}
         RETURNING *`,
        [...params, agent],
      );

      if (rowCount === 0) {
        res.status(404).json({ error: "Agent not found" });
        return;
      }
      res.json(rows[0]);
    } catch (err) {
      console.error("PATCH /api/agents/:agent/state error:", err);
      res.status(500).json({ error: "Failed to update agent state" });
    }
  });

  // GET /api/agents/:agent/relationships — relationship data
  router.get("/:agent/relationships", async (req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT relationships FROM agent_state WHERE agent = $1`,
        [req.params.agent],
      );
      if (rows.length === 0) {
        res.status(404).json({ error: "Agent not found" });
        return;
      }
      res.json({ agent: req.params.agent, relationships: rows[0].relationships });
    } catch (err) {
      console.error("GET /api/agents/:agent/relationships error:", err);
      res.status(500).json({ error: "Failed to fetch relationships" });
    }
  });

  // PATCH /api/agents/:agent/relationships/:other — update relationship with another agent
  router.patch("/:agent/relationships/:other", async (req: Request, res: Response) => {
    const agent = req.params.agent as string;
    const other = req.params.other as string;
    const updates = req.body as Record<string, unknown>;

    if (!updates || Object.keys(updates).length === 0) {
      res.status(400).json({ error: "Request body must contain relationship fields to update" });
      return;
    }

    try {
      // Get current relationships
      const { rows } = await pool.query(
        `SELECT relationships FROM agent_state WHERE agent = $1`,
        [agent],
      );
      if (rows.length === 0) {
        res.status(404).json({ error: "Agent not found" });
        return;
      }

      const relationships = rows[0].relationships as Record<string, Record<string, unknown>>;
      const current = relationships[other] ?? {
        trust: 0.5,
        agreement_rate: 0.5,
        interaction_count: 0,
        dynamic: "",
      };

      // Merge updates
      const updated: Record<string, unknown> = { ...current, ...updates, last_interaction: new Date().toISOString().split("T")[0] };

      // Clamp trust to [0, 1]
      if (typeof updated.trust === "number") {
        updated.trust = Math.max(0, Math.min(1, updated.trust));
      }

      relationships[other] = updated;

      const { rows: result } = await pool.query(
        `UPDATE agent_state SET relationships = $1, updated_at = NOW()
         WHERE agent = $2
         RETURNING agent, relationships`,
        [JSON.stringify(relationships), agent],
      );

      res.json({ agent, relationship: { [other]: result[0].relationships[other] } });
    } catch (err) {
      console.error("PATCH /api/agents/:agent/relationships/:other error:", err);
      res.status(500).json({ error: "Failed to update relationship" });
    }
  });

  // POST /api/agents/:agent/learned — add a learning entry
  router.post("/:agent/learned", async (req: Request, res: Response) => {
    const agent = req.params.agent;
    const { lesson, source, category } = req.body as {
      lesson?: string;
      source?: string;
      category?: string;
    };

    if (!lesson || !source) {
      res.status(400).json({ error: "Required: lesson, source" });
      return;
    }

    const entry = {
      date: new Date().toISOString().split("T")[0],
      lesson,
      source,
      category: category ?? null,
    };

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE agent_state
         SET learned = learned || $1::jsonb, updated_at = NOW()
         WHERE agent = $2
         RETURNING agent, learned`,
        [JSON.stringify([entry]), agent],
      );

      if (rowCount === 0) {
        res.status(404).json({ error: "Agent not found" });
        return;
      }

      res.status(201).json({ agent, entry, total_learnings: (rows[0].learned as unknown[]).length });
    } catch (err) {
      console.error("POST /api/agents/:agent/learned error:", err);
      res.status(500).json({ error: "Failed to add learning" });
    }
  });

  // GET /api/agents/graph — full relationship graph
  router.get("/graph", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(
        `SELECT agent, display_name, relationships, calibration FROM agent_state ORDER BY agent`,
      );

      const nodes = rows.map((r) => ({
        id: r.agent,
        display_name: r.display_name,
        calibration: r.calibration,
      }));

      const edges: Array<{
        from: string;
        to: string;
        trust: number;
        agreement_rate: number;
        interaction_count: number;
      }> = [];

      for (const row of rows) {
        const rels = row.relationships as Record<string, Record<string, unknown>>;
        for (const [other, data] of Object.entries(rels)) {
          edges.push({
            from: row.agent,
            to: other,
            trust: (data.trust as number) ?? 0.5,
            agreement_rate: (data.agreement_rate as number) ?? 0.5,
            interaction_count: (data.interaction_count as number) ?? 0,
          });
        }
      }

      res.json({ nodes, edges });
    } catch (err) {
      console.error("GET /api/agents/graph error:", err);
      res.status(500).json({ error: "Failed to fetch relationship graph" });
    }
  });

  return router;
}
