import express, { type Request, type Response } from "express";
import type { ClaimVerifier } from "../verification.js";
import { isValidProjectName } from "../path-validation.js";

export function verificationRoutes(verifier: ClaimVerifier | null): express.Router {
  const router = express.Router();

  // GET /api/projects/:id/verification — latest report
  router.get("/:id/verification", async (req: Request, res: Response) => {
    if (!verifier) {
      res.status(503).json({ error: "Verifier not available" });
      return;
    }
    if (!isValidProjectName(req.params.id as string)) {
      res.status(400).json({ error: "Invalid project name" });
      return;
    }
    const report = await verifier.getLatestReport(req.params.id as string);
    if (!report) {
      res.status(404).json({ error: "No verification report found" });
      return;
    }
    res.json(report);
  });

  // POST /api/projects/:id/verification — trigger a new verification run
  router.post("/:id/verification", async (req: Request, res: Response) => {
    if (!verifier) {
      res.status(503).json({ error: "Verifier not available" });
      return;
    }
    if (!isValidProjectName(req.params.id as string)) {
      res.status(400).json({ error: "Invalid project name" });
      return;
    }
    try {
      const report = await verifier.verifyAll(req.params.id as string);
      res.json({
        id: report.id,
        totalClaims: report.totalClaims,
        verified: report.verifiedClaims,
        inconsistencies: report.inconsistencies,
        missingEvidence: report.missingEvidence,
      });
    } catch (err) {
      res.status(500).json({ error: err instanceof Error ? err.message : "Verification failed" });
    }
  });

  // GET /api/projects/:id/verification/history — past reports
  router.get("/:id/verification/history", async (req: Request, res: Response) => {
    if (!verifier) {
      res.status(503).json({ error: "Verifier not available" });
      return;
    }
    if (!isValidProjectName(req.params.id as string)) {
      res.status(400).json({ error: "Invalid project name" });
      return;
    }
    const limitParam = req.query["limit"];
    const limit = parseInt(typeof limitParam === "string" ? limitParam : "10") || 10;
    res.json(await verifier.getReportHistory(req.params.id as string, limit));
  });

  return router;
}
