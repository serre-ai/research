import express, { type Request, type Response } from "express";
import type { EventBus } from "../event-bus.js";

// ============================================================
// Domain event routes
// Mount at /api/events
// ============================================================

export function eventRoutes(bus: EventBus): express.Router {
  const router = express.Router();

  // GET /api/events — recent domain events
  router.get("/", async (req: Request, res: Response) => {
    const limit = Math.min(parseInt(req.query["limit"] as string) || 50, 500);
    const type = req.query["type"] as string | undefined;
    const since = req.query["since"] as string | undefined;

    try {
      const events = await bus.getRecent({ limit, type, since });
      res.json(events);
    } catch (err) {
      console.error("GET /api/events error:", err);
      res.status(500).json({ error: "Failed to fetch events" });
    }
  });

  // POST /api/events — emit a custom domain event
  router.post("/", async (req: Request, res: Response) => {
    const { type, payload } = req.body as {
      type?: string;
      payload?: Record<string, unknown>;
    };

    if (!type) {
      res.status(400).json({ error: "Required: type" });
      return;
    }

    try {
      const id = await bus.emit(type, payload ?? {});
      res.status(201).json({ id, type });
    } catch (err) {
      console.error("POST /api/events error:", err);
      res.status(500).json({ error: "Failed to emit event" });
    }
  });

  // GET /api/events/dead-letters — list unresolved dead-letter entries
  router.get("/dead-letters", async (req: Request, res: Response) => {
    const resolved = req.query["resolved"] === "true";

    try {
      const entries = await bus.getDeadLetters(resolved);
      res.json(entries);
    } catch (err) {
      console.error("GET /api/events/dead-letters error:", err);
      res.status(500).json({ error: "Failed to fetch dead letters" });
    }
  });

  // POST /api/events/dead-letters/:id/retry — retry a dead-letter entry
  router.post("/dead-letters/:id/retry", async (req: Request<{ id: string }>, res: Response) => {
    const deadLetterId = parseInt(req.params.id);
    if (isNaN(deadLetterId)) {
      res.status(400).json({ error: "Invalid dead letter ID" });
      return;
    }

    try {
      const success = await bus.retryDeadLetter(deadLetterId);
      if (!success) {
        res.status(404).json({ error: "Dead letter not found or already resolved" });
        return;
      }
      res.json({ retried: true, id: deadLetterId });
    } catch (err) {
      console.error("POST /api/events/dead-letters/:id/retry error:", err);
      res.status(500).json({ error: "Failed to retry dead letter" });
    }
  });

  return router;
}
