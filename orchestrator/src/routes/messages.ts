import express, { type Request, type Response } from "express";
import type pg from "pg";

// ============================================================
// Message routes — direct agent-to-agent communication
// Mount at /api/messages
// ============================================================

export function messageRoutes(pool: pg.Pool): express.Router {
  const router = express.Router();

  // GET /api/messages/inbox/:agent — get messages for an agent
  router.get("/inbox/:agent", async (req: Request, res: Response) => {
    const agent = req.params.agent;
    const unreadOnly = req.query["unread"] === "true";
    const priority = req.query["priority"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 50, 200);
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const conditions: string[] = ["(to_agent = $1 OR to_agent = '*')"];
      const params: unknown[] = [agent];
      let paramIdx = 2;

      if (unreadOnly) {
        conditions.push("read_at IS NULL");
      }
      if (priority) {
        conditions.push(`priority = $${paramIdx++}`);
        params.push(priority);
      }

      const where = `WHERE ${conditions.join(" AND ")}`;

      const { rows } = await pool.query(
        `SELECT id, from_agent, to_agent, subject, body, priority, read_at, created_at
         FROM messages
         ${where}
         ORDER BY created_at DESC
         LIMIT $${paramIdx++} OFFSET $${paramIdx++}`,
        [...params, limit, offset],
      );

      // Also return unread count
      const { rows: countRows } = await pool.query(
        `SELECT COUNT(*) AS unread_count
         FROM messages
         WHERE (to_agent = $1 OR to_agent = '*') AND read_at IS NULL`,
        [agent],
      );

      res.json({ messages: rows, unread_count: parseInt(countRows[0].unread_count) });
    } catch (err) {
      console.error("GET /api/messages/inbox/:agent error:", err);
      res.status(500).json({ error: "Failed to fetch inbox" });
    }
  });

  // POST /api/messages/send — send a message
  router.post("/send", async (req: Request, res: Response) => {
    const { from_agent, to_agent, subject, body, priority } = req.body as {
      from_agent?: string;
      to_agent?: string;
      subject?: string;
      body?: string;
      priority?: string;
    };

    if (!from_agent || !to_agent || !subject || !body) {
      res.status(400).json({ error: "Required: from_agent, to_agent, subject, body" });
      return;
    }

    if (priority && !["normal", "urgent"].includes(priority)) {
      res.status(400).json({ error: "priority must be 'normal' or 'urgent'" });
      return;
    }

    try {
      // Rate limit: 5 messages per hour per sender
      const { rows: rl } = await pool.query(
        `SELECT COUNT(*) AS cnt FROM messages
         WHERE from_agent = $1 AND created_at > NOW() - INTERVAL '1 hour'`,
        [from_agent],
      );
      if (parseInt(rl[0].cnt) >= 5) {
        res.status(429).json({ error: "Rate limit: max 5 messages per hour" });
        return;
      }

      // Broadcast rate limit: 2 per day per sender
      if (to_agent === "*") {
        const { rows: brl } = await pool.query(
          `SELECT COUNT(*) AS cnt FROM messages
           WHERE from_agent = $1 AND to_agent = '*' AND created_at > NOW() - INTERVAL '24 hours'`,
          [from_agent],
        );
        if (parseInt(brl[0].cnt) >= 2) {
          res.status(429).json({ error: "Rate limit: max 2 broadcasts per day" });
          return;
        }
      }

      const { rows } = await pool.query(
        `INSERT INTO messages (from_agent, to_agent, subject, body, priority)
         VALUES ($1, $2, $3, $4, $5)
         RETURNING id, from_agent, to_agent, subject, body, priority, created_at`,
        [from_agent, to_agent, subject, body, priority ?? "normal"],
      );

      res.status(201).json(rows[0]);
    } catch (err) {
      console.error("POST /api/messages/send error:", err);
      res.status(500).json({ error: "Failed to send message" });
    }
  });

  // PATCH /api/messages/:id/read — mark message as read
  router.patch("/:id/read", async (req: Request, res: Response) => {
    const messageId = req.params.id;

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE messages SET read_at = NOW()
         WHERE id = $1 AND read_at IS NULL
         RETURNING id, from_agent, to_agent, subject, read_at`,
        [messageId],
      );

      if (rowCount === 0) {
        // Check if message exists at all
        const { rows: exists } = await pool.query(
          `SELECT id, read_at FROM messages WHERE id = $1`,
          [messageId],
        );
        if (exists.length === 0) {
          res.status(404).json({ error: "Message not found" });
        } else {
          res.json({ id: parseInt(messageId as string), already_read: true, read_at: exists[0].read_at });
        }
        return;
      }

      res.json(rows[0]);
    } catch (err) {
      console.error("PATCH /api/messages/:id/read error:", err);
      res.status(500).json({ error: "Failed to mark message as read" });
    }
  });

  // GET /api/messages/mentions/:agent — forum posts and messages mentioning this agent
  router.get("/mentions/:agent", async (req: Request, res: Response) => {
    const agent = req.params.agent;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 20, 100);

    try {
      // Forum mentions
      const { rows: forumMentions } = await pool.query(
        `SELECT 'forum' AS source, fp.id, fp.thread_id, fp.author, fp.body, fp.created_at
         FROM forum_posts fp
         WHERE fp.body ILIKE '%@' || $1 || '%'
           AND fp.author != $1
         ORDER BY fp.created_at DESC
         LIMIT $2`,
        [agent, limit],
      );

      // Message mentions (in body)
      const { rows: msgMentions } = await pool.query(
        `SELECT 'message' AS source, m.id, NULL AS thread_id, m.from_agent AS author, m.body, m.created_at
         FROM messages m
         WHERE m.body ILIKE '%@' || $1 || '%'
           AND m.from_agent != $1
         ORDER BY m.created_at DESC
         LIMIT $2`,
        [agent, limit],
      );

      res.json({ forum: forumMentions, messages: msgMentions });
    } catch (err) {
      console.error("GET /api/messages/mentions/:agent error:", err);
      res.status(500).json({ error: "Failed to fetch mentions" });
    }
  });

  // GET /api/messages/stats/:agent — message stats
  router.get("/stats/:agent", async (req: Request, res: Response) => {
    const agent = req.params.agent;

    try {
      const { rows } = await pool.query(
        `SELECT
           (SELECT COUNT(*) FROM messages WHERE from_agent = $1) AS sent,
           (SELECT COUNT(*) FROM messages WHERE to_agent = $1 OR to_agent = '*') AS received,
           (SELECT COUNT(*) FROM messages WHERE (to_agent = $1 OR to_agent = '*') AND read_at IS NULL) AS unread,
           (SELECT COUNT(*) FROM messages WHERE (to_agent = $1 OR to_agent = '*') AND read_at IS NULL AND priority = 'urgent') AS urgent_unread`,
        [agent],
      );

      res.json(rows[0]);
    } catch (err) {
      console.error("GET /api/messages/stats/:agent error:", err);
      res.status(500).json({ error: "Failed to fetch message stats" });
    }
  });

  return router;
}
