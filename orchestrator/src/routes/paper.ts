import { spawn, type ChildProcess } from "node:child_process";
import { join } from "node:path";
import { stat } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { randomUUID } from "node:crypto";
import express, { type Request, type Response } from "express";

// ============================================================
// Paper build & download routes
// Mount at /api/paper
// ============================================================

interface BuildRecord {
  buildId: string;
  status: "building" | "done" | "error";
  startedAt: string;
  finishedAt: string | null;
  durationMs: number | null;
  log: string;
}

interface PaperBuildState {
  status: "idle" | "building" | "done" | "error";
  currentProcess: ChildProcess | null;
  lastBuild: BuildRecord | null;
}

export function paperRoutes(rootDir?: string): express.Router {
  const router = express.Router();

  const repoRoot = rootDir ?? process.cwd();
  const paperDir = join(repoRoot, "projects", "reasoning-gaps", "paper");
  const buildScript = join(paperDir, "build-paper.sh");
  const pdfPath = join(paperDir, "main.pdf");
  const zipPath = join(paperDir, "submission.zip");

  // In-memory build state — one build at a time
  const state: PaperBuildState = {
    status: "idle",
    currentProcess: null,
    lastBuild: null,
  };

  // ----------------------------------------------------------
  // POST /api/paper/build — trigger a paper build
  // ----------------------------------------------------------
  router.post("/build", async (req: Request, res: Response) => {
    if (state.status === "building") {
      res.status(409).json({
        error: "A build is already in progress",
        buildId: state.lastBuild?.buildId ?? null,
      });
      return;
    }

    const { skipAnalysis, skipCompile } = req.body as {
      skipAnalysis?: boolean;
      skipCompile?: boolean;
    };

    const buildId = randomUUID();
    const startedAt = new Date().toISOString();
    let log = "";

    const record: BuildRecord = {
      buildId,
      status: "building",
      startedAt,
      finishedAt: null,
      durationMs: null,
      log: "",
    };

    state.status = "building";
    state.lastBuild = record;

    // Build args
    const args: string[] = [];
    if (skipAnalysis) args.push("--skip-analysis");
    if (skipCompile) args.push("--skip-compile");

    const child = spawn("bash", [buildScript, ...args], {
      cwd: paperDir,
      env: { ...process.env },
      stdio: ["ignore", "pipe", "pipe"],
    });

    state.currentProcess = child;

    child.stdout.on("data", (chunk: Buffer) => {
      log += chunk.toString();
    });

    child.stderr.on("data", (chunk: Buffer) => {
      log += chunk.toString();
    });

    child.on("close", (code) => {
      const finishedAt = new Date().toISOString();
      const durationMs = new Date(finishedAt).getTime() - new Date(startedAt).getTime();

      record.log = log;
      record.finishedAt = finishedAt;
      record.durationMs = durationMs;

      if (code === 0) {
        record.status = "done";
        state.status = "done";
      } else {
        record.status = "error";
        state.status = "error";
        record.log += `\n[exit code: ${code}]`;
      }

      state.currentProcess = null;
    });

    child.on("error", (err) => {
      const finishedAt = new Date().toISOString();
      const durationMs = new Date(finishedAt).getTime() - new Date(startedAt).getTime();

      record.log = log + `\n[spawn error: ${err.message}]`;
      record.finishedAt = finishedAt;
      record.durationMs = durationMs;
      record.status = "error";
      state.status = "error";
      state.currentProcess = null;
    });

    res.json({ status: "building", buildId });
  });

  // ----------------------------------------------------------
  // GET /api/paper/status — current build status
  // ----------------------------------------------------------
  router.get("/status", (_req: Request, res: Response) => {
    const response: Record<string, unknown> = {
      status: state.status,
    };

    if (state.lastBuild) {
      response.lastBuild = {
        buildId: state.lastBuild.buildId,
        status: state.lastBuild.status,
        startedAt: state.lastBuild.startedAt,
        finishedAt: state.lastBuild.finishedAt,
        durationMs: state.lastBuild.durationMs,
      };
    }

    res.json(response);
  });

  // ----------------------------------------------------------
  // GET /api/paper/download — serve submission.zip
  // ----------------------------------------------------------
  router.get("/download", async (_req: Request, res: Response) => {
    try {
      await stat(zipPath);
    } catch {
      res.status(404).json({ error: "No submission.zip found — run a build first" });
      return;
    }

    res.setHeader("Content-Type", "application/zip");
    res.setHeader("Content-Disposition", 'attachment; filename="reasoning-gaps-submission.zip"');
    createReadStream(zipPath).pipe(res);
  });

  // ----------------------------------------------------------
  // GET /api/paper/pdf — serve the compiled PDF
  // ----------------------------------------------------------
  router.get("/pdf", async (_req: Request, res: Response) => {
    try {
      await stat(pdfPath);
    } catch {
      res.status(404).json({ error: "No main.pdf found — run a build first" });
      return;
    }

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", 'inline; filename="reasoning-gaps.pdf"');
    createReadStream(pdfPath).pipe(res);
  });

  // ----------------------------------------------------------
  // GET /api/paper/log — last build log
  // ----------------------------------------------------------
  router.get("/log", (_req: Request, res: Response) => {
    if (!state.lastBuild) {
      res.status(404).json({ error: "No build has been run yet" });
      return;
    }

    res.setHeader("Content-Type", "text/plain");
    res.send(state.lastBuild.log);
  });

  return router;
}
