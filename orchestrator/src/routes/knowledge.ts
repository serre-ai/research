import express, { type Request, type Response } from "express";
import type { KnowledgeGraph, ClaimType, RelationType, SourceType } from "../knowledge-graph.js";

// ============================================================
// Knowledge graph routes
// Mount at /api/knowledge
// ============================================================

const VALID_CLAIM_TYPES = new Set<string>([
  "hypothesis", "finding", "definition", "proof",
  "citation", "method", "result", "observation",
  "decision", "question",
]);

const VALID_RELATION_TYPES = new Set<string>([
  "supports", "contradicts", "derives_from", "cited_in",
  "supersedes", "refines", "depends_on", "related_to",
]);

const VALID_SOURCE_TYPES = new Set<string>([
  "paper", "eval", "status_yaml", "manual", "agent_session",
]);

export function knowledgeRoutes(kg: KnowledgeGraph): express.Router {
  const router = express.Router();

  // POST /api/knowledge/claims — add a new claim
  router.post("/claims", async (req: Request, res: Response) => {
    const { project, claim_type, statement, confidence, source, source_type, metadata } = req.body as {
      project?: string;
      claim_type?: string;
      statement?: string;
      confidence?: number;
      source?: string;
      source_type?: string;
      metadata?: Record<string, unknown>;
    };

    if (!project || !claim_type || !statement) {
      res.status(400).json({ error: "Required: project, claim_type, statement" });
      return;
    }
    if (!VALID_CLAIM_TYPES.has(claim_type)) {
      res.status(400).json({ error: `Invalid claim_type: ${claim_type}` });
      return;
    }
    if (source_type && !VALID_SOURCE_TYPES.has(source_type)) {
      res.status(400).json({ error: `Invalid source_type: ${source_type}` });
      return;
    }
    if (confidence !== undefined && (confidence < 0 || confidence > 1)) {
      res.status(400).json({ error: "confidence must be between 0 and 1" });
      return;
    }

    try {
      const claim = await kg.addClaim({
        project,
        claimType: claim_type as ClaimType,
        statement,
        confidence: confidence ?? 0.5,
        source,
        sourceType: source_type as SourceType | undefined,
        metadata,
      });
      res.status(201).json(claim);
    } catch (err) {
      console.error("POST /api/knowledge/claims error:", err);
      res.status(500).json({ error: "Failed to add claim" });
    }
  });

  // GET /api/knowledge/claims — list claims (filtered)
  router.get("/claims", async (req: Request, res: Response) => {
    const project = req.query["project"] as string | undefined;
    const type = req.query["type"] as string | undefined;
    const limit = Math.min(parseInt(req.query["limit"] as string) || 100, 500);
    const offset = Math.max(parseInt(req.query["offset"] as string) || 0, 0);

    if (!project) {
      res.status(400).json({ error: "Required query param: project" });
      return;
    }
    if (type && !VALID_CLAIM_TYPES.has(type)) {
      res.status(400).json({ error: `Invalid type: ${type}` });
      return;
    }

    try {
      const claims = await kg.getProjectClaims(project, type as ClaimType | undefined, limit, offset);
      res.json(claims);
    } catch (err) {
      console.error("GET /api/knowledge/claims error:", err);
      res.status(500).json({ error: "Failed to fetch claims" });
    }
  });

  // GET /api/knowledge/claims/:id — get a single claim
  router.get("/claims/:id", async (req: Request<{ id: string }>, res: Response) => {
    try {
      const claim = await kg.getClaim(req.params.id);
      if (!claim) {
        res.status(404).json({ error: "Claim not found" });
        return;
      }
      res.json(claim);
    } catch (err) {
      console.error("GET /api/knowledge/claims/:id error:", err);
      res.status(500).json({ error: "Failed to fetch claim" });
    }
  });

  // PATCH /api/knowledge/claims/:id — update claim
  router.patch("/claims/:id", async (req: Request<{ id: string }>, res: Response) => {
    const { confidence, metadata, statement } = req.body as {
      confidence?: number;
      metadata?: Record<string, unknown>;
      statement?: string;
    };

    try {
      const claim = await kg.updateClaim(req.params.id, { confidence, metadata, statement });
      if (!claim) {
        res.status(404).json({ error: "Claim not found" });
        return;
      }
      res.json(claim);
    } catch (err) {
      console.error("PATCH /api/knowledge/claims/:id error:", err);
      res.status(500).json({ error: "Failed to update claim" });
    }
  });

  // POST /api/knowledge/query — semantic search
  router.post("/query", async (req: Request, res: Response) => {
    const { query, project, exclude_project, type, limit, threshold } = req.body as {
      query?: string;
      project?: string;
      exclude_project?: string;
      type?: string;
      limit?: number;
      threshold?: number;
    };

    if (!query) {
      res.status(400).json({ error: "Required: query" });
      return;
    }

    try {
      const claims = await kg.query(query, {
        project,
        excludeProject: exclude_project,
        type: type as ClaimType | undefined,
        limit,
        threshold,
      });
      res.json(claims);
    } catch (err) {
      console.error("POST /api/knowledge/query error:", err);
      res.status(500).json({ error: "Failed to search claims" });
    }
  });

  // POST /api/knowledge/relations — add a relation
  router.post("/relations", async (req: Request, res: Response) => {
    const { source_id, target_id, relation, strength, evidence } = req.body as {
      source_id?: string;
      target_id?: string;
      relation?: string;
      strength?: number;
      evidence?: string;
    };

    if (!source_id || !target_id || !relation) {
      res.status(400).json({ error: "Required: source_id, target_id, relation" });
      return;
    }
    if (!VALID_RELATION_TYPES.has(relation)) {
      res.status(400).json({ error: `Invalid relation: ${relation}` });
      return;
    }

    try {
      await kg.addRelation({
        sourceId: source_id,
        targetId: target_id,
        relation: relation as RelationType,
        strength,
        evidence,
      });
      res.status(201).json({ created: true });
    } catch (err) {
      console.error("POST /api/knowledge/relations error:", err);
      res.status(500).json({ error: "Failed to add relation" });
    }
  });

  // GET /api/knowledge/subgraph/:id — get connected subgraph
  router.get("/subgraph/:id", async (req: Request<{ id: string }>, res: Response) => {
    const depth = Math.min(Math.max(parseInt(req.query["depth"] as string) || 2, 1), 5);

    try {
      const subgraph = await kg.getSubgraph(req.params.id, depth);
      res.json(subgraph);
    } catch (err) {
      console.error("GET /api/knowledge/subgraph/:id error:", err);
      res.status(500).json({ error: "Failed to fetch subgraph" });
    }
  });

  // GET /api/knowledge/contradictions/:project — list contradictions
  router.get("/contradictions/:project", async (req: Request<{ project: string }>, res: Response) => {
    try {
      const contradictions = await kg.findContradictions(req.params.project);
      res.json(contradictions);
    } catch (err) {
      console.error("GET /api/knowledge/contradictions error:", err);
      res.status(500).json({ error: "Failed to fetch contradictions" });
    }
  });

  // GET /api/knowledge/unsupported/:project — list unsupported claims
  router.get("/unsupported/:project", async (req: Request<{ project: string }>, res: Response) => {
    try {
      const claims = await kg.getUnsupportedClaims(req.params.project);
      res.json(claims);
    } catch (err) {
      console.error("GET /api/knowledge/unsupported error:", err);
      res.status(500).json({ error: "Failed to fetch unsupported claims" });
    }
  });

  // GET /api/knowledge/evidence/:id — trace evidence chain
  router.get("/evidence/:id", async (req: Request<{ id: string }>, res: Response) => {
    try {
      const chain = await kg.getEvidenceChain(req.params.id);
      res.json(chain);
    } catch (err) {
      console.error("GET /api/knowledge/evidence/:id error:", err);
      res.status(500).json({ error: "Failed to trace evidence chain" });
    }
  });

  // GET /api/knowledge/stats — knowledge graph statistics
  router.get("/stats", async (_req: Request, res: Response) => {
    try {
      const stats = await kg.getStats();
      res.json(stats);
    } catch (err) {
      console.error("GET /api/knowledge/stats error:", err);
      res.status(500).json({ error: "Failed to fetch stats" });
    }
  });

  // POST /api/knowledge/snapshot/:project — trigger a snapshot
  router.post("/snapshot/:project", async (req: Request<{ project: string }>, res: Response) => {
    try {
      await kg.createSnapshot(req.params.project);
      res.json({ created: true, project: req.params.project });
    } catch (err) {
      console.error("POST /api/knowledge/snapshot error:", err);
      res.status(500).json({ error: "Failed to create snapshot" });
    }
  });

  // PUT /api/knowledge/confidence/:id — update confidence with audit trail
  router.put("/confidence/:id", async (req: Request<{ id: string }>, res: Response) => {
    const { confidence, reason, changed_by } = req.body as {
      confidence?: number;
      reason?: string;
      changed_by?: string;
    };

    if (confidence == null || !reason) {
      res.status(400).json({ error: "Required: confidence, reason" });
      return;
    }
    if (confidence < 0 || confidence > 1) {
      res.status(400).json({ error: "confidence must be between 0 and 1" });
      return;
    }

    try {
      await kg.updateConfidence(req.params.id, confidence, reason, changed_by);
      res.json({ updated: true });
    } catch (err) {
      console.error("PUT /api/knowledge/confidence/:id error:", err);
      res.status(500).json({ error: "Failed to update confidence" });
    }
  });

  return router;
}
