/**
 * Literature intelligence API routes.
 *
 * Endpoints for alerts, papers, citation watches, and stats.
 */

import { Router, type Request, type Response } from "express";
import type { LiteratureMonitor } from "../literature-monitor.js";

type MonitorGetter = () => LiteratureMonitor | null;

export function literatureRoutes(getMonitor: MonitorGetter): Router {
  const r = Router();

  // GET /api/literature/alerts — list literature alerts
  r.get("/alerts", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      const alerts = await monitor.getAlerts({
        project: req.query.project as string | undefined,
        priority: req.query.priority as string | undefined,
        acknowledged: req.query.acknowledged === "true" ? true
          : req.query.acknowledged === "false" ? false
          : undefined,
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
      });
      res.json(alerts);
    } catch (err) {
      console.error("GET /api/literature/alerts error:", err);
      res.status(500).json({ error: "Failed to fetch alerts" });
    }
  });

  // PATCH /api/literature/alerts/:id/acknowledge — acknowledge an alert
  r.patch("/alerts/:id/acknowledge", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      const ok = await monitor.acknowledgeAlert(parseInt(req.params.id as string));
      if (!ok) {
        res.status(404).json({ error: "Alert not found" });
        return;
      }
      res.json({ acknowledged: true });
    } catch (err) {
      console.error("PATCH /api/literature/alerts/:id/acknowledge error:", err);
      res.status(500).json({ error: "Failed to acknowledge alert" });
    }
  });

  // GET /api/literature/papers — list discovered papers
  r.get("/papers", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      const papers = await monitor.getPapers({
        limit: req.query.limit ? parseInt(req.query.limit as string) : undefined,
        since: req.query.since as string | undefined,
      });
      res.json(papers);
    } catch (err) {
      console.error("GET /api/literature/papers error:", err);
      res.status(500).json({ error: "Failed to fetch papers" });
    }
  });

  // GET /api/literature/watches — list citation watches
  r.get("/watches", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      const watches = await monitor.getWatches({
        project: req.query.project as string | undefined,
        active: req.query.active === "true" ? true
          : req.query.active === "false" ? false
          : undefined,
      });
      res.json(watches);
    } catch (err) {
      console.error("GET /api/literature/watches error:", err);
      res.status(500).json({ error: "Failed to fetch watches" });
    }
  });

  // POST /api/literature/watches — add a citation watch
  r.post("/watches", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    const { arxiv_id, s2_id, title, project, reason } = req.body as {
      arxiv_id?: string;
      s2_id?: string;
      title?: string;
      project?: string;
      reason?: string;
    };

    if (!title || !project) {
      res.status(400).json({ error: "Required: title, project" });
      return;
    }

    try {
      const watch = await monitor.watchPaper({
        arxivId: arxiv_id,
        s2Id: s2_id,
        title,
        project,
        reason,
      });
      res.status(201).json(watch);
    } catch (err) {
      console.error("POST /api/literature/watches error:", err);
      res.status(500).json({ error: "Failed to create watch" });
    }
  });

  // DELETE /api/literature/watches/:id — remove a citation watch
  r.delete("/watches/:id", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      const ok = await monitor.unwatchPaper(parseInt(req.params.id as string));
      if (!ok) {
        res.status(404).json({ error: "Watch not found" });
        return;
      }
      res.json({ removed: true });
    } catch (err) {
      console.error("DELETE /api/literature/watches/:id error:", err);
      res.status(500).json({ error: "Failed to remove watch" });
    }
  });

  // GET /api/literature/stats — monitor statistics
  r.get("/stats", async (_req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      const stats = await monitor.getStats();
      res.json(stats);
    } catch (err) {
      console.error("GET /api/literature/stats error:", err);
      res.status(500).json({ error: "Failed to fetch stats" });
    }
  });

  // POST /api/literature/scan — trigger an immediate scan (manual)
  r.post("/scan", async (req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    const { project, key_terms } = req.body as {
      project?: string;
      key_terms?: string[];
    };

    if (!project || !key_terms?.length) {
      res.status(400).json({ error: "Required: project, key_terms" });
      return;
    }

    try {
      // Reset the tick timer to allow immediate scan
      await monitor.tick([{ project, keyTerms: key_terms }]);
      res.json({ status: "scan_triggered", project });
    } catch (err) {
      console.error("POST /api/literature/scan error:", err);
      res.status(500).json({ error: "Failed to trigger scan" });
    }
  });

  // POST /api/literature/citations/poll — trigger citation poll
  r.post("/citations/poll", async (_req: Request, res: Response) => {
    const monitor = getMonitor();
    if (!monitor) {
      res.status(503).json({ error: "Literature monitor not available" });
      return;
    }

    try {
      await monitor.pollCitations();
      res.json({ status: "citation_poll_completed" });
    } catch (err) {
      console.error("POST /api/literature/citations/poll error:", err);
      res.status(500).json({ error: "Failed to poll citations" });
    }
  });

  return r;
}
