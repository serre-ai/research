/**
 * KnowledgeGraph — persistent semantic memory for research projects.
 * Stores typed claims with relationships and vector embeddings.
 */

import pg from "pg";
import { randomUUID } from "node:crypto";
import type { EmbedFn } from "./embeddings.js";

// ============================================================
// Types
// ============================================================

export type ClaimType =
  | "hypothesis" | "finding" | "definition" | "proof"
  | "citation"   | "method"  | "result"     | "observation"
  | "decision"   | "question";

export type SourceType =
  | "paper" | "eval" | "status_yaml" | "manual" | "agent_session";

export type RelationType =
  | "supports"    | "contradicts" | "derives_from" | "cited_in"
  | "supersedes"  | "refines"     | "depends_on"   | "related_to";

export interface Claim {
  id?: string;
  project: string;
  claimType: ClaimType;
  statement: string;
  confidence: number;
  source?: string;
  sourceType?: SourceType;
  metadata?: Record<string, unknown>;
}

export interface ClaimRow extends Claim {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  distance?: number;
}

export interface ClaimRelation {
  sourceId: string;
  targetId: string;
  relation: RelationType;
  strength?: number;
  evidence?: string;
}

export interface ClaimRelationRow extends ClaimRelation {
  id: string;
  createdAt: Date;
}

export interface SubgraphResult {
  claims: ClaimRow[];
  relations: ClaimRelationRow[];
}

export interface KnowledgeStats {
  total_claims: number;
  total_relations: number;
  embedded_claims: number;
  projects_with_claims: number;
}

// ============================================================
// Class
// ============================================================

export class KnowledgeGraph {
  private pool: pg.Pool;
  private embedFn: EmbedFn | null;

  constructor(pool: pg.Pool, embedFn: EmbedFn | null) {
    this.pool = pool;
    this.embedFn = embedFn;
  }

  // --------------------------------------------------------
  // Claims CRUD
  // --------------------------------------------------------

  /** Insert a new claim with auto-computed embedding.
   *  Dedup check + insert are wrapped in a single transaction to prevent
   *  race conditions where two identical claims both pass dedup. */
  async addClaim(claim: Claim): Promise<ClaimRow> {
    const id = claim.id ?? randomUUID();

    // Compute embedding outside the transaction (network call)
    let embeddingStr: string | null = null;
    if (this.embedFn) {
      try {
        const embedding = await this.embedFn(claim.statement);
        embeddingStr = `[${embedding.join(",")}]`;
      } catch (err) {
        console.error("[KnowledgeGraph] Embedding failed (inserting without):", err);
      }
    }

    // Wrap dedup check + insert in a transaction to avoid duplicate inserts
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");

      // Check for near-duplicates inside the transaction
      if (embeddingStr) {
        const { rows: dupeRows } = await client.query(
          `SELECT *, (embedding <=> $1::vector) AS distance
           FROM claims
           WHERE project = $2 AND embedding IS NOT NULL AND (embedding <=> $1::vector) < 0.05
           ORDER BY distance ASC
           LIMIT 1`,
          [embeddingStr, claim.project],
        );
        if (dupeRows.length > 0) {
          await client.query("COMMIT");
          console.log(`[KnowledgeGraph] Near-duplicate found for "${claim.statement.slice(0, 60)}..." — returning existing claim ${dupeRows[0].id}`);
          return this.rowToClaim(dupeRows[0]);
        }
      }

      const { rows } = await client.query(
        `INSERT INTO claims (id, project, claim_type, statement, confidence,
                             source, source_type, embedding, metadata)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector, $9)
         RETURNING *`,
        [
          id, claim.project, claim.claimType, claim.statement,
          claim.confidence, claim.source ?? null, claim.sourceType ?? null,
          embeddingStr, JSON.stringify(claim.metadata ?? {}),
        ],
      );

      await client.query("COMMIT");
      return this.rowToClaim(rows[0]);
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  }

  /** Get a single claim by ID. */
  async getClaim(claimId: string): Promise<ClaimRow | null> {
    const { rows } = await this.pool.query(
      "SELECT * FROM claims WHERE id = $1",
      [claimId],
    );
    return rows.length > 0 ? this.rowToClaim(rows[0]) : null;
  }

  /** Update claim metadata or confidence. */
  async updateClaim(
    claimId: string,
    updates: { confidence?: number; metadata?: Record<string, unknown>; statement?: string },
  ): Promise<ClaimRow | null> {
    const sets: string[] = ["updated_at = NOW()"];
    const params: unknown[] = [];
    let idx = 1;

    if (updates.confidence !== undefined) {
      sets.push(`confidence = $${idx}`);
      params.push(updates.confidence);
      idx++;
    }
    if (updates.metadata !== undefined) {
      sets.push(`metadata = $${idx}`);
      params.push(JSON.stringify(updates.metadata));
      idx++;
    }
    if (updates.statement !== undefined) {
      sets.push(`statement = $${idx}`);
      params.push(updates.statement);
      idx++;
      // Re-embed if statement changes
      if (this.embedFn) {
        try {
          const embedding = await this.embedFn(updates.statement);
          sets.push(`embedding = $${idx}::vector`);
          params.push(`[${embedding.join(",")}]`);
          idx++;
        } catch { /* keep old embedding */ }
      }
    }

    params.push(claimId);
    const { rows } = await this.pool.query(
      `UPDATE claims SET ${sets.join(", ")} WHERE id = $${idx} RETURNING *`,
      params,
    );
    return rows.length > 0 ? this.rowToClaim(rows[0]) : null;
  }

  // --------------------------------------------------------
  // Relations
  // --------------------------------------------------------

  /** Create a directed relationship between two claims. */
  async addRelation(rel: ClaimRelation): Promise<void> {
    await this.pool.query(
      `INSERT INTO claim_relations (source_id, target_id, relation, strength, evidence)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (source_id, target_id, relation) DO UPDATE SET
         strength = EXCLUDED.strength,
         evidence = EXCLUDED.evidence`,
      [rel.sourceId, rel.targetId, rel.relation, rel.strength ?? 1.0, rel.evidence ?? null],
    );
  }

  // --------------------------------------------------------
  // Semantic search
  // --------------------------------------------------------

  /** Find claims similar to a natural-language query via vector similarity. */
  async query(
    naturalLanguageQuery: string,
    opts?: {
      project?: string;
      excludeProject?: string;
      type?: ClaimType;
      limit?: number;
      threshold?: number;
    },
  ): Promise<ClaimRow[]> {
    if (!this.embedFn) {
      // Fall back to full-text search
      return this.textSearch(naturalLanguageQuery, opts);
    }

    const embedding = await this.embedFn(naturalLanguageQuery);
    const embeddingStr = `[${embedding.join(",")}]`;
    const limit = opts?.limit ?? 10;
    const threshold = opts?.threshold ?? 0.30; // cosine distance

    let sql = `
      SELECT *, (embedding <=> $1::vector) AS distance
      FROM claims
      WHERE embedding IS NOT NULL AND (embedding <=> $1::vector) < $2
    `;
    const params: unknown[] = [embeddingStr, threshold];
    let paramIdx = 3;

    if (opts?.project) {
      sql += ` AND project = $${paramIdx}`;
      params.push(opts.project);
      paramIdx++;
    }
    if (opts?.excludeProject) {
      sql += ` AND project != $${paramIdx}`;
      params.push(opts.excludeProject);
      paramIdx++;
    }
    if (opts?.type) {
      sql += ` AND claim_type = $${paramIdx}`;
      params.push(opts.type);
      paramIdx++;
    }

    sql += ` ORDER BY distance ASC LIMIT $${paramIdx}`;
    params.push(limit);

    const { rows } = await this.pool.query(sql, params);
    return rows.map((r) => this.rowToClaim(r));
  }

  /** Full-text search fallback when no embedding function available. */
  private async textSearch(
    query: string,
    opts?: { project?: string; type?: ClaimType; limit?: number },
  ): Promise<ClaimRow[]> {
    const limit = opts?.limit ?? 10;
    let sql = `
      SELECT *, ts_rank(to_tsvector('english', statement), plainto_tsquery('english', $1)) AS rank
      FROM claims
      WHERE to_tsvector('english', statement) @@ plainto_tsquery('english', $1)
    `;
    const params: unknown[] = [query];
    let paramIdx = 2;

    if (opts?.project) {
      sql += ` AND project = $${paramIdx}`;
      params.push(opts.project);
      paramIdx++;
    }
    if (opts?.type) {
      sql += ` AND claim_type = $${paramIdx}`;
      params.push(opts.type);
      paramIdx++;
    }

    sql += ` ORDER BY rank DESC LIMIT $${paramIdx}`;
    params.push(limit);

    const { rows } = await this.pool.query(sql, params);
    return rows.map((r) => this.rowToClaim(r));
  }

  // --------------------------------------------------------
  // Graph traversal
  // --------------------------------------------------------

  /** Get all claims connected within N hops of a given claim. */
  async getSubgraph(claimId: string, depth: number = 2): Promise<SubgraphResult> {
    const { rows: claimRows } = await this.pool.query(
      `WITH RECURSIVE connected AS (
         SELECT id, 0 AS depth FROM claims WHERE id = $1
         UNION
         SELECT DISTINCT
           CASE WHEN cr.source_id = c.id THEN cr.target_id ELSE cr.source_id END,
           c.depth + 1
         FROM connected c
         JOIN claim_relations cr ON cr.source_id = c.id OR cr.target_id = c.id
         WHERE c.depth < $2
       )
       SELECT cl.* FROM connected co JOIN claims cl ON cl.id = co.id`,
      [claimId, depth],
    );

    const claimIds = claimRows.map((r: Record<string, unknown>) => r.id as string);
    if (claimIds.length === 0) {
      return { claims: [], relations: [] };
    }

    const { rows: relRows } = await this.pool.query(
      `SELECT * FROM claim_relations
       WHERE source_id = ANY($1) AND target_id = ANY($1)`,
      [claimIds],
    );

    return {
      claims: claimRows.map((r: Record<string, unknown>) => this.rowToClaim(r)),
      relations: relRows.map((r: Record<string, unknown>) => this.rowToRelation(r)),
    };
  }

  /** All claims for a project, optionally filtered by type. */
  async getProjectClaims(project: string, type?: ClaimType, limit: number = 100, offset: number = 0): Promise<ClaimRow[]> {
    let sql = "SELECT * FROM claims WHERE project = $1";
    const params: unknown[] = [project];
    let idx = 2;
    if (type) {
      sql += ` AND claim_type = $${idx}`;
      params.push(type);
      idx++;
    }
    sql += ` ORDER BY confidence DESC, created_at DESC LIMIT $${idx} OFFSET $${idx + 1}`;
    params.push(limit, offset);
    const { rows } = await this.pool.query(sql, params);
    return rows.map((r: Record<string, unknown>) => this.rowToClaim(r));
  }

  /** Find pairs of claims that contradict each other. */
  async findContradictions(project: string): Promise<ClaimRelationRow[]> {
    const { rows } = await this.pool.query(
      `SELECT cr.* FROM claim_relations cr
       JOIN claims c1 ON cr.source_id = c1.id
       WHERE cr.relation = 'contradicts' AND c1.project = $1
       ORDER BY cr.strength DESC`,
      [project],
    );
    return rows.map((r: Record<string, unknown>) => this.rowToRelation(r));
  }

  /** Trace evidence chain back from a claim to its root sources. */
  async getEvidenceChain(claimId: string): Promise<ClaimRow[]> {
    const { rows } = await this.pool.query(
      `WITH RECURSIVE chain AS (
         SELECT id, 0 AS depth FROM claims WHERE id = $1
         UNION
         SELECT cr.source_id, ch.depth + 1
         FROM chain ch
         JOIN claim_relations cr ON cr.target_id = ch.id
         WHERE cr.relation IN ('supports', 'derives_from', 'cited_in')
           AND ch.depth < 10
       )
       SELECT cl.* FROM chain ch JOIN claims cl ON cl.id = ch.id
       ORDER BY ch.depth ASC`,
      [claimId],
    );
    return rows.map((r: Record<string, unknown>) => this.rowToClaim(r));
  }

  // --------------------------------------------------------
  // Confidence management
  // --------------------------------------------------------

  /** Update confidence with audit trail. */
  async updateConfidence(
    claimId: string,
    newConfidence: number,
    reason: string,
    changedBy?: string,
  ): Promise<void> {
    const client = await this.pool.connect();
    try {
      await client.query("BEGIN");

      const { rows } = await client.query(
        "SELECT confidence FROM claims WHERE id = $1 FOR UPDATE",
        [claimId],
      );
      if (rows.length === 0) throw new Error(`Claim ${claimId} not found`);
      const oldConfidence = rows[0].confidence;

      await client.query(
        `INSERT INTO confidence_history (claim_id, old_confidence, new_confidence, reason, changed_by)
         VALUES ($1, $2, $3, $4, $5)`,
        [claimId, oldConfidence, newConfidence, reason, changedBy ?? null],
      );

      await client.query(
        "UPDATE claims SET confidence = $1, updated_at = NOW() WHERE id = $2",
        [newConfidence, claimId],
      );

      await client.query("COMMIT");
    } catch (err) {
      await client.query("ROLLBACK");
      throw err;
    } finally {
      client.release();
    }
  }

  // --------------------------------------------------------
  // Deduplication & snapshots
  // --------------------------------------------------------

  /** Check for near-duplicate claims (cosine distance < 0.05). */
  async findNearDuplicates(statement: string, project: string): Promise<ClaimRow[]> {
    if (!this.embedFn) return [];
    const embedding = await this.embedFn(statement);
    return this.findNearDuplicatesWithVector(`[${embedding.join(",")}]`, project);
  }

  /** Check for near-duplicates using a pre-computed embedding vector string. */
  private async findNearDuplicatesWithVector(embeddingStr: string, project: string): Promise<ClaimRow[]> {
    const { rows } = await this.pool.query(
      `SELECT *, (embedding <=> $1::vector) AS distance
       FROM claims
       WHERE project = $2 AND embedding IS NOT NULL AND (embedding <=> $1::vector) < 0.05
       ORDER BY distance ASC
       LIMIT 5`,
      [embeddingStr, project],
    );
    return rows.map((r: Record<string, unknown>) => this.rowToClaim(r));
  }

  /** Create a daily snapshot of knowledge state for a project. */
  async createSnapshot(project: string): Promise<void> {
    const today = new Date().toISOString().split("T")[0];
    const { rows: claims } = await this.pool.query(
      "SELECT id FROM claims WHERE project = $1",
      [project],
    );
    const { rows: relCount } = await this.pool.query(
      `SELECT COUNT(*) AS cnt FROM claim_relations cr
       JOIN claims c ON cr.source_id = c.id
       WHERE c.project = $1`,
      [project],
    );

    await this.pool.query(
      `INSERT INTO knowledge_snapshots (project, snapshot_date, claim_count, relation_count, claim_ids)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (project, snapshot_date) DO UPDATE SET
         claim_count = EXCLUDED.claim_count,
         relation_count = EXCLUDED.relation_count,
         claim_ids = EXCLUDED.claim_ids`,
      [
        project, today, claims.length,
        parseInt(relCount[0].cnt),
        claims.map((r: Record<string, unknown>) => r.id as string),
      ],
    );
  }

  // --------------------------------------------------------
  // Stats
  // --------------------------------------------------------

  /** List unsupported claims (findings/results/hypotheses with no 'supports' relation). */
  async getUnsupportedClaims(project: string): Promise<ClaimRow[]> {
    const { rows } = await this.pool.query(
      `SELECT * FROM v_unsupported_claims WHERE project = $1`,
      [project],
    );
    return rows.map((r: Record<string, unknown>) => this.rowToClaim(r));
  }

  /** Knowledge graph stats for the health endpoint. */
  async getStats(): Promise<KnowledgeStats> {
    const { rows } = await this.pool.query(`
      SELECT
        (SELECT COUNT(*) FROM claims)::int AS total_claims,
        (SELECT COUNT(*) FROM claim_relations)::int AS total_relations,
        (SELECT COUNT(*) FROM claims WHERE embedding IS NOT NULL)::int AS embedded_claims,
        (SELECT COUNT(DISTINCT project) FROM claims)::int AS projects_with_claims
    `);
    return rows[0] as KnowledgeStats;
  }

  // --------------------------------------------------------
  // Internal helpers
  // --------------------------------------------------------

  private rowToClaim(row: Record<string, unknown>): ClaimRow {
    return {
      id: row.id as string,
      project: row.project as string,
      claimType: row.claim_type as ClaimType,
      statement: row.statement as string,
      confidence: row.confidence as number,
      source: (row.source as string) ?? undefined,
      sourceType: (row.source_type as SourceType) ?? undefined,
      metadata: (row.metadata ?? {}) as Record<string, unknown>,
      createdAt: row.created_at as Date,
      updatedAt: row.updated_at as Date,
      distance: row.distance as number | undefined,
    };
  }

  private rowToRelation(row: Record<string, unknown>): ClaimRelationRow {
    return {
      id: row.id as string,
      sourceId: row.source_id as string,
      targetId: row.target_id as string,
      relation: row.relation as RelationType,
      strength: row.strength as number,
      evidence: (row.evidence as string) ?? undefined,
      createdAt: row.created_at as Date,
    };
  }
}
