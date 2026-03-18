import express, { type Request, type Response } from "express";
import type { ResearchPlanner } from "../research-planner.js";

export function plannerRoutes(planner: ResearchPlanner | null): express.Router {
  const router = express.Router();

  // GET /api/planner/status
  router.get("/status", async (_req: Request, res: Response) => {
    if (!planner) {
      res.status(503).json({ error: "Planner not enabled (set USE_RESEARCH_PLANNER=1)" });
      return;
    }
    res.json(await planner.getState());
  });

  // GET /api/planner/insights/:project
  router.get("/insights/:project", async (req: Request, res: Response) => {
    if (!planner) {
      res.status(503).json({ error: "Planner not enabled" });
      return;
    }
    const insight = await planner.getProjectInsight(req.params.project as string);
    if (!insight) {
      res.status(404).json({ error: "Project not found or knowledge graph unavailable" });
      return;
    }
    res.json(insight);
  });

  // GET /api/planner/evaluations
  router.get("/evaluations", async (req: Request, res: Response) => {
    if (!planner) {
      res.status(503).json({ error: "Planner not enabled" });
      return;
    }
    const limitParam = req.query["limit"];
    const limit = parseInt(typeof limitParam === "string" ? limitParam : "20") || 20;
    res.json(await planner.getRecentEvaluations(limit));
  });

  return router;
}
