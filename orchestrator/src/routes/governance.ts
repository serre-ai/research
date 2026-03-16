import express, { type Request, type Response } from "express";
import type pg from "pg";
import type { CollectiveSlack } from "../collective-slack.js";

// ============================================================
// Governance routes — process change proposals and voting
// Mount at /api/governance
// ============================================================

export function governanceRoutes(pool: pg.Pool, slack?: CollectiveSlack): express.Router {
  const router = express.Router();

  // POST /api/governance — create a proposal (also creates forum thread)
  router.post("/", async (req: Request, res: Response) => {
    const { proposer, title, proposal, proposal_type } = req.body as {
      proposer?: string;
      title?: string;
      proposal?: string;
      proposal_type?: string;
    };

    if (!proposer || !title || !proposal || !proposal_type) {
      res.status(400).json({ error: "Required: proposer, title, proposal, proposal_type" });
      return;
    }

    const validTypes = ["process", "schedule", "budget", "personnel", "values"];
    if (!validTypes.includes(proposal_type)) {
      res.status(400).json({ error: `proposal_type must be one of: ${validTypes.join(", ")}` });
      return;
    }

    try {
      // Create forum thread for the proposal
      const { rows: forumRows } = await pool.query(
        `INSERT INTO forum_posts (thread_id, author, post_type, title, body, metadata)
         VALUES ('__pending', $1, 'proposal', $2, $3, $4)
         RETURNING id`,
        [
          proposer,
          `[Governance] ${title}`,
          proposal,
          JSON.stringify({ governance: true, proposal_type }),
        ],
      );

      const threadId = String(forumRows[0].id);
      await pool.query(
        `UPDATE forum_posts SET thread_id = $1 WHERE id = $2`,
        [threadId, forumRows[0].id],
      );

      // Create governance record linked to the forum thread
      const { rows } = await pool.query(
        `INSERT INTO governance (proposer, title, proposal, proposal_type, thread_id, status)
         VALUES ($1, $2, $3, $4, $5, 'voting')
         RETURNING *`,
        [proposer, title, proposal, proposal_type, threadId],
      );

      res.status(201).json(rows[0]);
    } catch (err) {
      console.error("POST /api/governance error:", err);
      res.status(500).json({ error: "Failed to create governance proposal" });
    }
  });

  // GET /api/governance — list proposals
  router.get("/", async (req: Request, res: Response) => {
    const status = req.query["status"] as string | undefined;
    const type = req.query["type"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 50, 200);
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const conditions: string[] = [];
      const params: unknown[] = [];
      let paramIdx = 1;

      if (status) {
        conditions.push(`status = $${paramIdx++}`);
        params.push(status);
      }
      if (type) {
        conditions.push(`proposal_type = $${paramIdx++}`);
        params.push(type);
      }

      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

      const { rows } = await pool.query(
        `SELECT * FROM governance
         ${where}
         ORDER BY created_at DESC
         LIMIT $${paramIdx++} OFFSET $${paramIdx++}`,
        [...params, limit, offset],
      );

      res.json(rows);
    } catch (err) {
      console.error("GET /api/governance error:", err);
      res.status(500).json({ error: "Failed to fetch proposals" });
    }
  });

  // GET /api/governance/:id — proposal details with vote tally
  router.get("/:id", async (req: Request, res: Response) => {
    try {
      const { rows: govRows } = await pool.query(
        `SELECT * FROM governance WHERE id = $1`,
        [req.params.id],
      );
      if (govRows.length === 0) {
        res.status(404).json({ error: "Proposal not found" });
        return;
      }

      const gov = govRows[0];

      // Get votes from the linked forum thread
      const { rows: voteRows } = await pool.query(
        `SELECT voter, position, rationale, confidence, created_at
         FROM votes WHERE thread_id = $1
         ORDER BY created_at ASC`,
        [gov.thread_id],
      );

      // Get tally
      const { rows: tally } = await pool.query(
        `SELECT * FROM governance_tally($1)`,
        [gov.id],
      );

      res.json({
        ...gov,
        votes: voteRows,
        tally: tally[0],
      });
    } catch (err) {
      console.error("GET /api/governance/:id error:", err);
      res.status(500).json({ error: "Failed to fetch proposal" });
    }
  });

  // POST /api/governance/:id/vote — vote on a proposal
  router.post("/:id/vote", async (req: Request, res: Response) => {
    const { voter, position, rationale, confidence } = req.body as {
      voter?: string;
      position?: string;
      rationale?: string;
      confidence?: number;
    };

    if (!voter || !position) {
      res.status(400).json({ error: "Required: voter, position" });
      return;
    }

    const validPositions = ["support", "oppose", "abstain"];
    if (!validPositions.includes(position)) {
      res.status(400).json({ error: `position must be one of: ${validPositions.join(", ")}` });
      return;
    }

    try {
      // Get governance record
      const { rows: govRows } = await pool.query(
        `SELECT * FROM governance WHERE id = $1`,
        [req.params.id],
      );
      if (govRows.length === 0) {
        res.status(404).json({ error: "Proposal not found" });
        return;
      }

      const gov = govRows[0];
      if (!["proposed", "voting"].includes(gov.status)) {
        res.status(400).json({ error: `Proposal is ${gov.status} — cannot vote` });
        return;
      }

      // Cast vote on the linked forum thread
      const { rows: voteRows } = await pool.query(
        `INSERT INTO votes (thread_id, voter, position, rationale, confidence)
         VALUES ($1, $2, $3, $4, $5)
         ON CONFLICT (thread_id, voter) DO UPDATE SET
           position = EXCLUDED.position,
           rationale = EXCLUDED.rationale,
           confidence = EXCLUDED.confidence,
           created_at = NOW()
         RETURNING *`,
        [gov.thread_id, voter, position, rationale ?? null, confidence ?? null],
      );

      // Check quorum and update governance tallies
      const { rows: tally } = await pool.query(
        `SELECT * FROM governance_tally($1)`,
        [gov.id],
      );
      const t = tally[0];

      await pool.query(
        `UPDATE governance
         SET votes_for = $1, votes_against = $2, votes_abstain = $3
         WHERE id = $4`,
        [t.votes_for, t.votes_against, t.votes_abstain, gov.id],
      );

      res.status(201).json({
        vote: voteRows[0],
        tally: t,
      });
    } catch (err) {
      console.error("POST /api/governance/:id/vote error:", err);
      res.status(500).json({ error: "Failed to cast vote" });
    }
  });

  // GET /api/governance/:id/tally — current vote tally
  router.get("/:id/tally", async (req: Request, res: Response) => {
    try {
      const { rows: govRows } = await pool.query(
        `SELECT id FROM governance WHERE id = $1`,
        [req.params.id],
      );
      if (govRows.length === 0) {
        res.status(404).json({ error: "Proposal not found" });
        return;
      }

      const { rows } = await pool.query(
        `SELECT * FROM governance_tally($1)`,
        [req.params.id],
      );

      res.json(rows[0]);
    } catch (err) {
      console.error("GET /api/governance/:id/tally error:", err);
      res.status(500).json({ error: "Failed to fetch tally" });
    }
  });

  // PATCH /api/governance/:id/resolve — resolve proposal based on votes
  router.patch("/:id/resolve", async (req: Request, res: Response) => {
    try {
      // Get tally
      const { rows: tally } = await pool.query(
        `SELECT * FROM governance_tally($1)`,
        [req.params.id],
      );
      const t = tally[0];

      if (!t.quorum_reached) {
        res.status(400).json({ error: "Quorum not reached (need 4 votes)", tally: t });
        return;
      }

      const newStatus = t.outcome === "accepted" ? "accepted" : "rejected";

      const { rowCount, rows } = await pool.query(
        `UPDATE governance
         SET status = $1, votes_for = $2, votes_against = $3, votes_abstain = $4, resolved_at = NOW()
         WHERE id = $5 AND status IN ('proposed', 'voting')
         RETURNING *`,
        [newStatus, t.votes_for, t.votes_against, t.votes_abstain, req.params.id],
      );

      if (rowCount === 0) {
        res.status(400).json({ error: "Proposal already resolved" });
        return;
      }

      // Also resolve the linked forum thread
      if (rows[0].thread_id) {
        await pool.query(
          `UPDATE forum_posts SET status = 'resolved', updated_at = NOW()
           WHERE thread_id = $1 AND parent_id IS NULL`,
          [rows[0].thread_id],
        );
      }

      // Cross-post to Slack
      if (slack) {
        slack.crossPostGovernanceOutcome({
          id: rows[0].id,
          title: rows[0].title,
          status: newStatus,
          votes_for: t.votes_for,
          votes_against: t.votes_against,
          votes_abstain: t.votes_abstain,
        }).catch(() => {});
      }

      res.json({ proposal: rows[0], tally: t });
    } catch (err) {
      console.error("PATCH /api/governance/:id/resolve error:", err);
      res.status(500).json({ error: "Failed to resolve proposal" });
    }
  });

  return router;
}
