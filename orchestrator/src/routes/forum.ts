import express, { type Request, type Response } from "express";
import type pg from "pg";
import type { CollectiveSlack } from "../collective-slack.js";

// ============================================================
// Grounding enforcement — posts must contain verifiable data
// ============================================================

function isGrounded(body: string, metadata?: Record<string, unknown>): boolean {
  // Check metadata.data_references
  if (metadata?.data_references && Array.isArray(metadata.data_references) && metadata.data_references.length > 0) {
    return true;
  }

  // Check body for grounding signals: decimal numbers, dollar amounts, dates,
  // URLs, percentages, p-values, sample sizes, CIs, or arXiv IDs
  const patterns = [
    /\d+\.\d+/,                          // decimal numbers
    /\$\d+/,                             // dollar amounts
    /\d{4}-\d{2}-\d{2}/,                // dates (ISO format)
    /https?:\/\/\S+/,                    // URLs
    /\d+%/,                              // percentages
    /p\s*[<>=]\s*0?\.\d+/i,             // p-values
    /[Nn]\s*=\s*\d+/,                   // sample sizes
    /CI\s*[:=]?\s*\[/i,                 // confidence intervals
    /\d{4}\.\d{4,5}/,                   // arXiv IDs
  ];

  return patterns.some((p) => p.test(body));
}

// ============================================================
// Forum routes — threaded discussions, proposals, votes
// Mount at /api/forum
// ============================================================

export function forumRoutes(pool: pg.Pool, slack?: CollectiveSlack): express.Router {
  const router = express.Router();

  // GET /api/forum/threads — list threads
  router.get("/threads", async (req: Request, res: Response) => {
    const status = req.query["status"] as string | undefined;
    const type = req.query["type"] as string | undefined;
    const author = req.query["author"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 50, 200);
    const offset = parseInt(req.query["offset"] as string) || 0;

    try {
      const conditions: string[] = ["fp.parent_id IS NULL"]; // thread starters only
      const params: unknown[] = [];
      let paramIdx = 1;

      if (status) {
        conditions.push(`fp.status = $${paramIdx++}`);
        params.push(status);
      }
      if (type) {
        conditions.push(`fp.post_type = $${paramIdx++}`);
        params.push(type);
      }
      if (author) {
        conditions.push(`fp.author = $${paramIdx++}`);
        params.push(author);
      }

      const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";

      const { rows } = await pool.query(
        `SELECT fp.id, fp.thread_id, fp.author, fp.post_type, fp.title, fp.body,
                fp.status, fp.metadata, fp.created_at, fp.updated_at,
                (SELECT COUNT(*) FROM forum_posts r WHERE r.thread_id = fp.thread_id AND r.id != fp.id) AS reply_count,
                (SELECT COUNT(*) FROM votes v WHERE v.thread_id = fp.thread_id) AS vote_count
         FROM forum_posts fp
         ${where}
         ORDER BY fp.updated_at DESC
         LIMIT $${paramIdx++} OFFSET $${paramIdx++}`,
        [...params, limit, offset],
      );
      res.json(rows);
    } catch (err) {
      console.error("GET /api/forum/threads error:", err);
      res.status(500).json({ error: "Failed to fetch threads" });
    }
  });

  // GET /api/forum/threads/:id — full thread with all posts
  router.get("/threads/:id", async (req: Request, res: Response) => {
    const threadId = req.params.id;

    try {
      const { rows: posts } = await pool.query(
        `SELECT id, thread_id, parent_id, author, post_type, title, body,
                status, metadata, created_at, updated_at
         FROM forum_posts
         WHERE thread_id = $1
         ORDER BY created_at ASC`,
        [threadId],
      );

      if (posts.length === 0) {
        res.status(404).json({ error: "Thread not found" });
        return;
      }

      const { rows: threadVotes } = await pool.query(
        `SELECT id, thread_id, voter, position, rationale, confidence, created_at
         FROM votes
         WHERE thread_id = $1
         ORDER BY created_at ASC`,
        [threadId],
      );

      res.json({ thread_id: threadId, posts, votes: threadVotes });
    } catch (err) {
      console.error("GET /api/forum/threads/:id error:", err);
      res.status(500).json({ error: "Failed to fetch thread" });
    }
  });

  // POST /api/forum/threads — create a new thread
  router.post("/threads", async (req: Request, res: Response) => {
    const { author, post_type, title, body, metadata } = req.body as {
      author?: string;
      post_type?: string;
      title?: string;
      body?: string;
      metadata?: Record<string, unknown>;
    };

    if (!author || !post_type || !title || !body) {
      res.status(400).json({ error: "Required: author, post_type, title, body" });
      return;
    }

    const validTypes = ["proposal", "debate", "signal", "prediction"];
    if (!validTypes.includes(post_type)) {
      res.status(400).json({ error: `post_type must be one of: ${validTypes.join(", ")}` });
      return;
    }

    try {
      // Rate limit check
      const rl = await pool.query(
        `SELECT * FROM check_forum_rate_limit($1)`,
        [author],
      );
      const { hourly_ok, daily_ok } = rl.rows[0];
      if (!hourly_ok) {
        res.status(429).json({ error: "Rate limit: max 3 posts per hour" });
        return;
      }
      if (!daily_ok) {
        res.status(429).json({ error: "Rate limit: max 10 posts per day" });
        return;
      }

      // Grounding enforcement: if last 2 posts by this author were ungrounded, require grounding
      if (!isGrounded(body, metadata)) {
        const { rows: recentPosts } = await pool.query(
          `SELECT body, metadata FROM forum_posts
           WHERE author = $1
           ORDER BY created_at DESC LIMIT 2`,
          [author],
        );
        if (recentPosts.length >= 2 &&
            !isGrounded(recentPosts[0].body, recentPosts[0].metadata) &&
            !isGrounded(recentPosts[1].body, recentPosts[1].metadata)) {
          res.status(400).json({
            error: "Grounding required: your last 2 posts lacked verifiable data. Include numbers, citations, URLs, or data references.",
          });
          return;
        }
      }

      // Insert thread starter — thread_id is set to its own id after insert
      const { rows } = await pool.query(
        `INSERT INTO forum_posts (thread_id, author, post_type, title, body, metadata)
         VALUES ('__pending', $1, $2, $3, $4, $5)
         RETURNING id`,
        [author, post_type, title, body, metadata ? JSON.stringify(metadata) : "{}"],
      );

      const postId = rows[0].id;
      const threadId = String(postId);

      // Set thread_id to its own id
      const { rows: updated } = await pool.query(
        `UPDATE forum_posts SET thread_id = $1 WHERE id = $2
         RETURNING id, thread_id, author, post_type, title, body, status, metadata, created_at`,
        [threadId, postId],
      );

      res.status(201).json(updated[0]);
    } catch (err) {
      console.error("POST /api/forum/threads error:", err);
      res.status(500).json({ error: "Failed to create thread" });
    }
  });

  // POST /api/forum/threads/:id/reply — reply to a thread
  router.post("/threads/:id/reply", async (req: Request, res: Response) => {
    const threadId = req.params.id;
    const { author, body, metadata } = req.body as {
      author?: string;
      body?: string;
      metadata?: Record<string, unknown>;
    };

    if (!author || !body) {
      res.status(400).json({ error: "Required: author, body" });
      return;
    }

    try {
      // Check thread exists and is open
      const { rows: thread } = await pool.query(
        `SELECT id, status FROM forum_posts WHERE thread_id = $1 AND parent_id IS NULL`,
        [threadId],
      );
      if (thread.length === 0) {
        res.status(404).json({ error: "Thread not found" });
        return;
      }
      if (thread[0].status !== "open") {
        res.status(400).json({ error: "Thread is " + thread[0].status + " — cannot reply" });
        return;
      }

      // Rate limit
      const rl = await pool.query(`SELECT * FROM check_forum_rate_limit($1)`, [author]);
      if (!rl.rows[0].hourly_ok) {
        res.status(429).json({ error: "Rate limit: max 3 posts per hour" });
        return;
      }
      if (!rl.rows[0].daily_ok) {
        res.status(429).json({ error: "Rate limit: max 10 posts per day" });
        return;
      }

      // Self-reply check
      const selfOk = await pool.query(`SELECT check_no_self_reply($1, $2)`, [threadId, author]);
      if (!selfOk.rows[0].check_no_self_reply) {
        res.status(400).json({ error: "Cannot reply to yourself without an intervening post from another agent" });
        return;
      }

      // Grounding enforcement on replies
      if (!isGrounded(body, metadata)) {
        const { rows: recentPosts } = await pool.query(
          `SELECT body, metadata FROM forum_posts
           WHERE author = $1
           ORDER BY created_at DESC LIMIT 2`,
          [author],
        );
        if (recentPosts.length >= 2 &&
            !isGrounded(recentPosts[0].body, recentPosts[0].metadata) &&
            !isGrounded(recentPosts[1].body, recentPosts[1].metadata)) {
          res.status(400).json({
            error: "Grounding required: your last 2 posts lacked verifiable data. Include numbers, citations, URLs, or data references.",
          });
          return;
        }
      }

      // Thread depth check
      const { rows: depthRows } = await pool.query(
        `SELECT COUNT(*) AS depth FROM forum_posts WHERE thread_id = $1`,
        [threadId],
      );
      if (parseInt(depthRows[0].depth) >= 10) {
        res.status(400).json({ error: "Thread depth limit reached (10 posts) — synthesis required" });
        return;
      }

      // Insert reply
      const { rows } = await pool.query(
        `INSERT INTO forum_posts (thread_id, parent_id, author, post_type, body, metadata)
         VALUES ($1, $2, $3, 'reply', $4, $5)
         RETURNING id, thread_id, parent_id, author, post_type, body, metadata, created_at`,
        [threadId, thread[0].id, author, body, metadata ? JSON.stringify(metadata) : "{}"],
      );

      // Bump thread updated_at
      await pool.query(
        `UPDATE forum_posts SET updated_at = NOW() WHERE thread_id = $1 AND parent_id IS NULL`,
        [threadId],
      );

      res.status(201).json(rows[0]);
    } catch (err) {
      console.error("POST /api/forum/threads/:id/reply error:", err);
      res.status(500).json({ error: "Failed to post reply" });
    }
  });

  // POST /api/forum/threads/:id/vote — cast a vote on a proposal
  router.post("/threads/:id/vote", async (req: Request, res: Response) => {
    const threadId = req.params.id;
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
      // Check thread exists, is open, and is a proposal
      const { rows: thread } = await pool.query(
        `SELECT id, status, post_type FROM forum_posts WHERE thread_id = $1 AND parent_id IS NULL`,
        [threadId],
      );
      if (thread.length === 0) {
        res.status(404).json({ error: "Thread not found" });
        return;
      }
      if (thread[0].status !== "open") {
        res.status(400).json({ error: "Thread is " + thread[0].status + " — cannot vote" });
        return;
      }
      if (thread[0].post_type !== "proposal") {
        res.status(400).json({ error: "Can only vote on proposal threads" });
        return;
      }

      // Upsert vote
      const { rows } = await pool.query(
        `INSERT INTO votes (thread_id, voter, position, rationale, confidence)
         VALUES ($1, $2, $3, $4, $5)
         ON CONFLICT (thread_id, voter) DO UPDATE SET
           position = EXCLUDED.position,
           rationale = EXCLUDED.rationale,
           confidence = EXCLUDED.confidence,
           created_at = NOW()
         RETURNING id, thread_id, voter, position, rationale, confidence, created_at`,
        [threadId, voter, position, rationale ?? null, confidence ?? null],
      );

      res.status(201).json(rows[0]);
    } catch (err) {
      console.error("POST /api/forum/threads/:id/vote error:", err);
      res.status(500).json({ error: "Failed to cast vote" });
    }
  });

  // PATCH /api/forum/threads/:id/status — update thread status
  router.patch("/threads/:id/status", async (req: Request, res: Response) => {
    const threadId = req.params.id;
    const { status } = req.body as { status?: string };

    if (!status) {
      res.status(400).json({ error: "Required: status" });
      return;
    }

    const validStatuses = ["open", "resolved", "archived"];
    if (!validStatuses.includes(status)) {
      res.status(400).json({ error: `status must be one of: ${validStatuses.join(", ")}` });
      return;
    }

    try {
      const { rowCount, rows } = await pool.query(
        `UPDATE forum_posts SET status = $1, updated_at = NOW()
         WHERE thread_id = $2 AND parent_id IS NULL
         RETURNING id, thread_id, status, updated_at`,
        [status, threadId],
      );

      if (rowCount === 0) {
        res.status(404).json({ error: "Thread not found" });
        return;
      }

      // Cross-post to Slack on resolution
      if (slack && status === "resolved") {
        const threadTitle = (await pool.query(
          `SELECT title FROM forum_posts WHERE thread_id = $1 AND parent_id IS NULL`,
          [threadId],
        )).rows[0]?.title ?? "Untitled";

        slack.crossPostForumResolution({
          thread_id: String(threadId),
          title: threadTitle,
          status: "resolved",
        }).catch(() => {});
      }

      res.json(rows[0]);
    } catch (err) {
      console.error("PATCH /api/forum/threads/:id/status error:", err);
      res.status(500).json({ error: "Failed to update thread status" });
    }
  });

  // GET /api/forum/feed/:agent — threads needing this agent's input
  router.get("/feed/:agent", async (req: Request, res: Response) => {
    const agent = req.params.agent;

    try {
      // Find: open proposals where this agent hasn't voted
      const { rows: unvotedProposals } = await pool.query(
        `SELECT fp.id, fp.thread_id, fp.author, fp.post_type, fp.title,
                fp.body, fp.status, fp.metadata, fp.created_at,
                (SELECT COUNT(*) FROM votes v WHERE v.thread_id = fp.thread_id) AS vote_count
         FROM forum_posts fp
         WHERE fp.parent_id IS NULL
           AND fp.status = 'open'
           AND fp.post_type = 'proposal'
           AND NOT EXISTS (SELECT 1 FROM votes v WHERE v.thread_id = fp.thread_id AND v.voter = $1)
         ORDER BY fp.created_at DESC`,
        [agent],
      );

      // Find: open threads where this agent is mentioned in body or metadata
      const { rows: mentions } = await pool.query(
        `SELECT DISTINCT ON (fp2.thread_id)
                fp2.thread_id, fp_root.title, fp_root.post_type, fp_root.author AS thread_author,
                fp2.author AS mentioner, fp2.body AS mention_body, fp2.created_at
         FROM forum_posts fp2
         JOIN forum_posts fp_root ON fp_root.thread_id = fp2.thread_id AND fp_root.parent_id IS NULL
         WHERE fp_root.status = 'open'
           AND fp2.body ILIKE '%@' || $1 || '%'
           AND fp2.author != $1
         ORDER BY fp2.thread_id, fp2.created_at DESC`,
        [agent],
      );

      // Find: open threads this agent participated in that have new replies
      const { rows: activeThreads } = await pool.query(
        `SELECT DISTINCT ON (fp_root.thread_id)
                fp_root.thread_id, fp_root.title, fp_root.post_type, fp_root.author,
                latest.created_at AS latest_reply_at, latest.author AS latest_reply_by
         FROM forum_posts my_posts
         JOIN forum_posts fp_root ON fp_root.thread_id = my_posts.thread_id AND fp_root.parent_id IS NULL
         JOIN LATERAL (
           SELECT created_at, author FROM forum_posts
           WHERE thread_id = my_posts.thread_id
           ORDER BY created_at DESC LIMIT 1
         ) latest ON TRUE
         WHERE my_posts.author = $1
           AND fp_root.status = 'open'
           AND latest.author != $1
           AND latest.created_at > (
             SELECT MAX(created_at) FROM forum_posts
             WHERE thread_id = my_posts.thread_id AND author = $1
           )
         ORDER BY fp_root.thread_id, latest.created_at DESC`,
        [agent],
      );

      res.json({
        unvoted_proposals: unvotedProposals,
        mentions,
        threads_with_new_replies: activeThreads,
      });
    } catch (err) {
      console.error("GET /api/forum/feed/:agent error:", err);
      res.status(500).json({ error: "Failed to fetch feed" });
    }
  });

  // POST /api/forum/threads/:id/synthesize — post synthesis and resolve
  router.post("/threads/:id/synthesize", async (req: Request, res: Response) => {
    const threadId = req.params.id;
    const { author, body } = req.body as { author?: string; body?: string };

    if (!author || !body) {
      res.status(400).json({ error: "Required: author, body" });
      return;
    }

    try {
      // Check thread exists and is open
      const { rows: thread } = await pool.query(
        `SELECT id, status FROM forum_posts WHERE thread_id = $1 AND parent_id IS NULL`,
        [threadId],
      );
      if (thread.length === 0) {
        res.status(404).json({ error: "Thread not found" });
        return;
      }
      if (thread[0].status !== "open") {
        res.status(400).json({ error: "Thread is already " + thread[0].status });
        return;
      }

      // Insert synthesis post
      const { rows: post } = await pool.query(
        `INSERT INTO forum_posts (thread_id, parent_id, author, post_type, body)
         VALUES ($1, $2, $3, 'synthesis', $4)
         RETURNING id, thread_id, author, post_type, body, created_at`,
        [threadId, thread[0].id, author, body],
      );

      // Resolve the thread
      await pool.query(
        `UPDATE forum_posts SET status = 'resolved', updated_at = NOW()
         WHERE thread_id = $1 AND parent_id IS NULL`,
        [threadId],
      );

      // Cross-post to Slack
      if (slack) {
        const threadTitle = (await pool.query(
          `SELECT title FROM forum_posts WHERE thread_id = $1 AND parent_id IS NULL`,
          [threadId],
        )).rows[0]?.title ?? "Untitled";

        slack.crossPostSynthesis({
          thread_id: String(threadId),
          title: threadTitle,
          synthesizer: author,
          summary: body,
        }).catch(() => {});

        slack.crossPostForumResolution({
          thread_id: String(threadId),
          title: threadTitle,
          status: "resolved",
          author,
        }).catch(() => {});
      }

      res.status(201).json({ synthesis: post[0], thread_status: "resolved" });
    } catch (err) {
      console.error("POST /api/forum/threads/:id/synthesize error:", err);
      res.status(500).json({ error: "Failed to synthesize thread" });
    }
  });

  // GET /api/forum/stats — forum activity stats
  router.get("/stats", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query(`SELECT * FROM v_forum_activity`);
      const { rows: summary } = await pool.query(
        `SELECT
           COUNT(*) FILTER (WHERE status = 'open' AND parent_id IS NULL) AS open_threads,
           COUNT(*) FILTER (WHERE status = 'resolved' AND parent_id IS NULL) AS resolved_threads,
           COUNT(*) FILTER (WHERE status = 'archived' AND parent_id IS NULL) AS archived_threads,
           COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') AS posts_last_24h
         FROM forum_posts`,
      );
      res.json({ by_agent: rows, summary: summary[0] });
    } catch (err) {
      console.error("GET /api/forum/stats error:", err);
      res.status(500).json({ error: "Failed to fetch forum stats" });
    }
  });

  return router;
}
