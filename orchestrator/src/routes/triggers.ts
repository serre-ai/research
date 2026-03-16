import express, { type Request, type Response } from "express";
import type pg from "pg";

// ============================================================
// Trigger routes — detect and acknowledge collective triggers
// Mount at /api/triggers
// ============================================================

interface Trigger {
  id: number;
  agent: string;
  trigger_type: string;
  context: Record<string, unknown>;
}

export function triggerRoutes(pool: pg.Pool): express.Router {
  const router = express.Router();

  // GET /api/triggers/pending — detect all pending triggers
  router.get("/pending", async (_req: Request, res: Response) => {
    try {
      const triggers: Trigger[] = [];

      // Run 5 detection queries in parallel
      const [unanimousSupport, stalledThreads, governanceProposed, ritualsDue, forumMentions] =
        await Promise.all([
          // 1. forum:unanimous_support — open proposals where all votes are "support" and count >= 2
          pool.query(
            `SELECT fp.thread_id, fp.title, fp.author,
                    COUNT(v.id) AS vote_count
             FROM forum_posts fp
             JOIN votes v ON v.thread_id = fp.thread_id
             WHERE fp.parent_id IS NULL
               AND fp.status = 'open'
               AND fp.post_type = 'proposal'
               AND NOT EXISTS (
                 SELECT 1 FROM votes v2
                 WHERE v2.thread_id = fp.thread_id AND v2.position != 'support'
               )
               AND NOT EXISTS (
                 SELECT 1 FROM trigger_log tl
                 WHERE tl.trigger_type = 'forum:unanimous_support'
                   AND tl.agent = 'rho'
                   AND (tl.context->>'thread_id')::text = fp.thread_id
                   AND tl.created_at > NOW() - INTERVAL '24 hours'
               )
             GROUP BY fp.thread_id, fp.title, fp.author
             HAVING COUNT(v.id) >= 2`,
          ),

          // 2. forum:stalled — open threads with no activity for 48h
          pool.query(
            `SELECT fp.thread_id, fp.title, fp.author, fp.updated_at
             FROM forum_posts fp
             WHERE fp.parent_id IS NULL
               AND fp.status = 'open'
               AND fp.updated_at < NOW() - INTERVAL '48 hours'
               AND NOT EXISTS (
                 SELECT 1 FROM trigger_log tl
                 WHERE tl.trigger_type = 'forum:stalled'
                   AND tl.agent = 'sage'
                   AND (tl.context->>'thread_id')::text = fp.thread_id
                   AND tl.created_at > NOW() - INTERVAL '48 hours'
               )`,
          ),

          // 3. governance:proposed — governance in voting status, not yet triggered for rho
          pool.query(
            `SELECT g.id, g.title, g.proposer, g.proposal_type, g.thread_id
             FROM governance g
             WHERE g.status = 'voting'
               AND NOT EXISTS (
                 SELECT 1 FROM trigger_log tl
                 WHERE tl.trigger_type = 'governance:proposed'
                   AND tl.agent = 'rho'
                   AND (tl.context->>'governance_id')::text = g.id::text
               )`,
          ),

          // 4. ritual:scheduled — rituals within 1 hour
          pool.query(
            `SELECT r.id, r.name, r.ritual_type, r.scheduled_at
             FROM rituals r
             WHERE r.status = 'scheduled'
               AND r.scheduled_at <= NOW() + INTERVAL '1 hour'
               AND r.scheduled_at > NOW() - INTERVAL '1 hour'
               AND NOT EXISTS (
                 SELECT 1 FROM trigger_log tl
                 WHERE tl.trigger_type = 'ritual:scheduled'
                   AND (tl.context->>'ritual_id')::text = r.id::text
               )`,
          ),

          // 5. forum:mention — posts containing @agent_name, not yet triggered
          pool.query(
            `SELECT fp.id AS post_id, fp.thread_id, fp.author, fp.body,
                    fp_root.title, fp_root.status
             FROM forum_posts fp
             JOIN forum_posts fp_root ON fp_root.thread_id = fp.thread_id AND fp_root.parent_id IS NULL
             WHERE fp_root.status = 'open'
               AND fp.body ~ '@[a-z]+'
               AND NOT EXISTS (
                 SELECT 1 FROM trigger_log tl
                 WHERE tl.trigger_type = 'forum:mention'
                   AND (tl.context->>'post_id')::text = fp.id::text
               )`,
          ),
        ]);

      // Process unanimous support triggers → target: rho
      for (const row of unanimousSupport.rows) {
        const { rows: [inserted] } = await pool.query(
          `INSERT INTO trigger_log (agent, trigger_type, context)
           VALUES ('rho', 'forum:unanimous_support', $1)
           RETURNING id`,
          [JSON.stringify({ thread_id: row.thread_id, title: row.title, vote_count: parseInt(row.vote_count) })],
        );
        triggers.push({
          id: inserted.id,
          agent: "rho",
          trigger_type: "forum:unanimous_support",
          context: { thread_id: row.thread_id, title: row.title, vote_count: parseInt(row.vote_count) },
        });
      }

      // Process stalled threads → target: sage
      for (const row of stalledThreads.rows) {
        const { rows: [inserted] } = await pool.query(
          `INSERT INTO trigger_log (agent, trigger_type, context)
           VALUES ('sage', 'forum:stalled', $1)
           RETURNING id`,
          [JSON.stringify({ thread_id: row.thread_id, title: row.title, stalled_since: row.updated_at })],
        );
        triggers.push({
          id: inserted.id,
          agent: "sage",
          trigger_type: "forum:stalled",
          context: { thread_id: row.thread_id, title: row.title, stalled_since: row.updated_at },
        });
      }

      // Process governance proposed → target: rho
      for (const row of governanceProposed.rows) {
        const { rows: [inserted] } = await pool.query(
          `INSERT INTO trigger_log (agent, trigger_type, context)
           VALUES ('rho', 'governance:proposed', $1)
           RETURNING id`,
          [JSON.stringify({ governance_id: row.id, title: row.title, proposer: row.proposer, thread_id: row.thread_id })],
        );
        triggers.push({
          id: inserted.id,
          agent: "rho",
          trigger_type: "governance:proposed",
          context: { governance_id: row.id, title: row.title, proposer: row.proposer, thread_id: row.thread_id },
        });
      }

      // Process rituals due → target: sage (or from ritual participants)
      for (const row of ritualsDue.rows) {
        const { rows: [inserted] } = await pool.query(
          `INSERT INTO trigger_log (agent, trigger_type, context)
           VALUES ('sage', 'ritual:scheduled', $1)
           RETURNING id`,
          [JSON.stringify({ ritual_id: row.id, name: row.name, ritual_type: row.ritual_type, scheduled_at: row.scheduled_at })],
        );
        triggers.push({
          id: inserted.id,
          agent: "sage",
          trigger_type: "ritual:scheduled",
          context: { ritual_id: row.id, name: row.name, ritual_type: row.ritual_type, scheduled_at: row.scheduled_at },
        });
      }

      // Process forum mentions → extract agent names and target them
      const agentNames = ["sol", "noor", "vera", "kit", "maren", "eli", "lev", "rho", "sage"];
      for (const row of forumMentions.rows) {
        for (const name of agentNames) {
          if (row.body.includes(`@${name}`) && row.author !== name) {
            const { rows: [inserted] } = await pool.query(
              `INSERT INTO trigger_log (agent, trigger_type, context)
               VALUES ($1, 'forum:mention', $2)
               RETURNING id`,
              [name, JSON.stringify({ post_id: row.post_id, thread_id: row.thread_id, title: row.title, mentioner: row.author })],
            );
            triggers.push({
              id: inserted.id,
              agent: name,
              trigger_type: "forum:mention",
              context: { post_id: row.post_id, thread_id: row.thread_id, title: row.title, mentioner: row.author },
            });
          }
        }
      }

      res.json(triggers);
    } catch (err) {
      console.error("GET /api/triggers/pending error:", err);
      res.status(500).json({ error: "Failed to detect triggers" });
    }
  });

  // POST /api/triggers/:id/ack — acknowledge a trigger
  router.post("/:id/ack", async (req: Request, res: Response) => {
    const triggerId = req.params.id;

    try {
      const { rowCount } = await pool.query(
        `UPDATE trigger_log SET acked_at = NOW() WHERE id = $1 AND acked_at IS NULL`,
        [triggerId],
      );

      if (rowCount === 0) {
        res.status(404).json({ error: "Trigger not found or already acknowledged" });
        return;
      }

      res.json({ id: parseInt(String(triggerId)), acked: true });
    } catch (err) {
      console.error("POST /api/triggers/:id/ack error:", err);
      res.status(500).json({ error: "Failed to acknowledge trigger" });
    }
  });

  return router;
}
