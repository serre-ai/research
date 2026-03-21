import express, { type Request, type Response } from "express";
import type pg from "pg";

// ============================================================
// Collective Context — unified context injection for agents
// Mount at /api/collective
// ============================================================

export function collectiveContextRoutes(pool: pg.Pool): express.Router {
  const router = express.Router();

  // GET /api/collective/context/:agent — aggregated pending interactions
  router.get("/context/:agent", async (req: Request, res: Response) => {
    const agent = req.params.agent;

    try {
      // Budget gate: check daily collective spend
      const { rows: budgetRows } = await pool.query(
        `SELECT COALESCE(SUM(cost_usd), 0) AS daily_spend
         FROM budget_events
         WHERE project = 'openclaw-collective'
           AND DATE(timestamp) = CURRENT_DATE`,
      );
      const dailySpend = parseFloat(budgetRows[0].daily_spend);
      const budgetOk = dailySpend < 5.0;

      // Log budget event for this context call
      await pool.query(
        `INSERT INTO budget_events (project, model, cost_usd, tokens_input, tokens_output, provider, category, source)
         VALUES ('openclaw-collective', 'context-fetch', 0.001, 0, 0, 'anthropic', 'api_calls', 'manual')`,
      ).catch(() => {
        // Non-critical — don't fail the request if budget logging fails
      });

      if (!budgetOk) {
        const markdown = `## Pending Interactions for ${agent}\n\n**Budget limit reached** ($${dailySpend.toFixed(2)}/$5.00 daily). Skip collective work and focus on solo tasks.\n`;
        res.json({ agent, budget_ok: false, markdown });
        return;
      }

      // Run 5 queries in parallel
      const [unreadMessages, forumFeed, upcomingRituals, unresolvedPredictions, recentLearnings] =
        await Promise.all([
          // 1. Unread messages
          pool.query(
            `SELECT id, from_agent AS sender, subject, body, priority, created_at
             FROM messages
             WHERE to_agent = $1 AND read_at IS NULL
             ORDER BY priority DESC, created_at DESC
             LIMIT 10`,
            [agent],
          ),

          // 2. Forum feed (unvoted proposals, mentions, threads with new replies)
          pool.query(
            `SELECT fp.id, fp.thread_id, fp.author, fp.post_type, fp.title,
                    fp.body, fp.status, fp.created_at,
                    'unvoted_proposal' AS feed_type
             FROM forum_posts fp
             WHERE fp.parent_id IS NULL
               AND fp.status = 'open'
               AND fp.post_type = 'proposal'
               AND NOT EXISTS (SELECT 1 FROM votes v WHERE v.thread_id = fp.thread_id AND v.voter = $1)
             UNION ALL
             SELECT fp2.id, fp2.thread_id, fp2.author, fp2.post_type, fp_root.title,
                    fp2.body, fp_root.status, fp2.created_at,
                    'mention' AS feed_type
             FROM forum_posts fp2
             JOIN forum_posts fp_root ON fp_root.thread_id = fp2.thread_id AND fp_root.parent_id IS NULL
             WHERE fp_root.status = 'open'
               AND fp2.body ILIKE '%@' || $1 || '%'
               AND fp2.author != $1
             ORDER BY created_at DESC
             LIMIT 20`,
            [agent],
          ),

          // 3. Upcoming rituals (scheduled, within 48h)
          pool.query(
            `SELECT id, ritual_type, scheduled_for, participants
             FROM rituals
             WHERE status = 'scheduled'
               AND scheduled_for <= NOW() + INTERVAL '48 hours'
             ORDER BY scheduled_for ASC
             LIMIT 5`,
          ),

          // 4. Unresolved predictions (author = agent)
          pool.query(
            `SELECT id, claim, probability, category, created_at
             FROM predictions
             WHERE author = $1 AND outcome IS NULL
             ORDER BY created_at DESC
             LIMIT 10`,
            [agent],
          ),

          // 5. Recent learnings from agent_state
          pool.query(
            `SELECT
               COALESCE(
                 (SELECT jsonb_array_elements_text(state->'learned')
                  FROM agent_state
                  WHERE agent = $1
                  LIMIT 5),
                 ''
               ) AS learning`,
            [agent],
          ).catch(() => ({ rows: [] })), // agent_state may not have learned field
        ]);

      // Assemble markdown
      const sections: string[] = [];
      sections.push(`## Pending Interactions for ${agent}\n`);

      // Unread messages
      if (unreadMessages.rows.length > 0) {
        sections.push(`### Inbox (${unreadMessages.rows.length} unread)`);
        for (const msg of unreadMessages.rows) {
          const prio = msg.priority === "urgent" ? " **[URGENT]**" : "";
          sections.push(`- From **${msg.sender}**${prio}: ${msg.subject}`);
        }
        sections.push("");
      }

      // Forum feed
      if (forumFeed.rows.length > 0) {
        const proposals = forumFeed.rows.filter((r: { feed_type: string }) => r.feed_type === "unvoted_proposal");
        const mentions = forumFeed.rows.filter((r: { feed_type: string }) => r.feed_type === "mention");

        if (proposals.length > 0) {
          sections.push(`### Proposals Awaiting Your Vote (${proposals.length})`);
          for (const p of proposals) {
            sections.push(`- **${p.title}** by ${p.author} (thread #${p.thread_id})`);
          }
          sections.push("");
        }

        if (mentions.length > 0) {
          sections.push(`### Mentions (${mentions.length})`);
          for (const m of mentions) {
            sections.push(`- ${m.author} mentioned you in thread #${m.thread_id}: "${m.title}"`);
          }
          sections.push("");
        }
      }

      // Upcoming rituals
      if (upcomingRituals.rows.length > 0) {
        sections.push(`### Upcoming Rituals (${upcomingRituals.rows.length})`);
        for (const r of upcomingRituals.rows) {
          const when = new Date(r.scheduled_for).toISOString();
          sections.push(`- **${r.ritual_type}** at ${when}`);
        }
        sections.push("");
      }

      // Unresolved predictions
      if (unresolvedPredictions.rows.length > 0) {
        sections.push(`### Your Unresolved Predictions (${unresolvedPredictions.rows.length})`);
        for (const p of unresolvedPredictions.rows) {
          sections.push(`- "${p.claim}" — p=${p.probability} (${p.category})`);
        }
        sections.push("");
      }

      // Recent learnings
      if (recentLearnings.rows.length > 0) {
        const learnings = recentLearnings.rows
          .map((r: { learning: string }) => r.learning)
          .filter((l: string) => l);
        if (learnings.length > 0) {
          sections.push(`### Recent Learnings`);
          for (const l of learnings) {
            sections.push(`- ${l}`);
          }
          sections.push("");
        }
      }

      if (sections.length === 1) {
        sections.push("No pending interactions. Focus on your primary tasks.\n");
      }

      const markdown = sections.join("\n");
      res.json({ agent, budget_ok: true, markdown });
    } catch (err) {
      console.error("GET /api/collective/context/:agent error:", err);
      res.status(500).json({ error: "Failed to fetch collective context" });
    }
  });

  // GET /api/collective/health — collective health dashboard
  router.get("/health", async (_req: Request, res: Response) => {
    try {
      const { rows } = await pool.query("SELECT * FROM v_collective_health");
      const h = rows[0] ?? {};
      res.json({
        active_threads: parseInt(h.active_threads) || 0,
        pending_proposals: parseInt(h.pending_proposals) || 0,
        unread_messages: parseInt(h.unread_messages) || 0,
        upcoming_rituals: parseInt(h.upcoming_rituals) || 0,
        unresolved_predictions: parseInt(h.unresolved_predictions) || 0,
        open_governance: parseInt(h.open_governance) || 0,
        posts_last_24h: parseInt(h.posts_last_24h) || 0,
        collective_spend_today: parseFloat(h.collective_spend_today) || 0,
      });
    } catch (err) {
      console.error("GET /api/collective/health error:", err);
      res.status(500).json({ error: "Failed to fetch collective health" });
    }
  });

  return router;
}
