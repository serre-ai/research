# Knowledge Graph / Semantic Memory System

**Status:** Planned
**Target:** Sprint 10+
**Estimated effort:** 12-16 hours
**Dependencies:** PostgreSQL with pgvector extension (VPS already runs PostgreSQL 16)

---

## Problem

Every agent session starts nearly from scratch. The session runner (`orchestrator/src/session-runner.ts`) builds a prompt from `CLAUDE.md`, agent role definitions, and `status.yaml` -- but none of these capture the accumulated knowledge a research project has produced. An agent writing Section 4 of a paper cannot query "what did we find about CoT lift on intractability tasks?" without re-reading raw analysis files.

The platform needs persistent, queryable semantic memory that stores typed knowledge claims with provenance, relationships, and vector embeddings for natural-language retrieval.

---

## Architecture Overview

The knowledge graph stores every claim, finding, hypothesis, citation, and decision as **typed nodes** with **directed relationships**. It lives in PostgreSQL alongside the existing schema (tables in `orchestrator/sql/001_initial_schema.sql` through `004_trigger_log.sql`) and uses **pgvector** for embedding-based similarity search.

```
                   +------------------+
                   |  Agent Session   |
                   +--------+---------+
                            |
           +----------------+----------------+
           |                                 |
   [query relevant           [addClaim / addRelation
    claims via embedding      after findings]
    similarity]
           |                                 |
           v                                 v
  +--------+---------------------------------+--------+
  |              KnowledgeGraph class                  |
  |  orchestrator/src/knowledge-graph.ts               |
  +---+----------------------------+------------------+
      |                            |
      v                            v
  +---+---+                +-------+-------+
  | claims |                | claim_relations|
  | (pgvector)             |               |
  +--------+               +---------------+
```

Key design constraints:
- PostgreSQL is the store (no separate graph database -- keep infra simple)
- Embeddings computed on write, not on read
- Claims are scoped to projects but cross-project queries are supported
- The `decisions` table already exists; decision claims link back to it via `source` field

---

## Schema Design

### Migration: `orchestrator/sql/005_knowledge_graph.sql`

```sql
-- Knowledge Graph: typed claims with vector embeddings and relationships
-- Migration: 005_knowledge_graph.sql

BEGIN;

-- Require pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Claims — atomic knowledge units
-- ============================================================
CREATE TABLE claims (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    claim_type      TEXT NOT NULL
                    CHECK (claim_type IN (
                        'hypothesis', 'finding', 'definition', 'proof',
                        'citation', 'method', 'result', 'observation',
                        'decision', 'question'
                    )),
    statement       TEXT NOT NULL,
    confidence      REAL NOT NULL DEFAULT 0.5
                    CHECK (confidence >= 0.0 AND confidence <= 1.0),
    source          TEXT,              -- file path, DOI, status.yaml, etc.
    source_type     TEXT               -- 'paper', 'eval', 'status_yaml', 'manual', 'agent_session'
                    CHECK (source_type IN (
                        'paper', 'eval', 'status_yaml', 'manual', 'agent_session'
                    )),
    embedding       vector(1024),      -- voyage-3-lite produces 1024-dim vectors
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_claims_project       ON claims (project);
CREATE INDEX idx_claims_type          ON claims (claim_type);
CREATE INDEX idx_claims_confidence    ON claims (confidence);
CREATE INDEX idx_claims_created       ON claims (created_at);
CREATE INDEX idx_claims_project_type  ON claims (project, claim_type);

-- HNSW index for fast approximate nearest-neighbor search
-- Use cosine distance (embeddings are normalized)
CREATE INDEX idx_claims_embedding ON claims
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Full-text search on statement
CREATE INDEX idx_claims_statement_fts ON claims
    USING gin (to_tsvector('english', statement));


-- ============================================================
-- Claim Relations — directed edges between claims
-- ============================================================
CREATE TABLE claim_relations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    target_id       UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    relation        TEXT NOT NULL
                    CHECK (relation IN (
                        'supports', 'contradicts', 'derives_from', 'cited_in',
                        'supersedes', 'refines', 'depends_on', 'related_to'
                    )),
    strength        REAL NOT NULL DEFAULT 1.0
                    CHECK (strength >= 0.0 AND strength <= 1.0),
    evidence        TEXT,              -- why this relation exists
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT no_self_relation CHECK (source_id != target_id),
    CONSTRAINT unique_relation UNIQUE (source_id, target_id, relation)
);

CREATE INDEX idx_relations_source   ON claim_relations (source_id);
CREATE INDEX idx_relations_target   ON claim_relations (target_id);
CREATE INDEX idx_relations_type     ON claim_relations (relation);


-- ============================================================
-- Knowledge Snapshots — periodic state captures for time-travel
-- ============================================================
CREATE TABLE knowledge_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    snapshot_date   DATE NOT NULL,
    claim_count     INTEGER NOT NULL,
    relation_count  INTEGER NOT NULL,
    summary         TEXT,              -- auto-generated summary of knowledge state
    claim_ids       UUID[] NOT NULL,   -- which claims existed at snapshot time
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_project_date UNIQUE (project, snapshot_date)
);

CREATE INDEX idx_snapshots_project  ON knowledge_snapshots (project);
CREATE INDEX idx_snapshots_date     ON knowledge_snapshots (snapshot_date);


-- ============================================================
-- Confidence History — track how claim confidence changes
-- ============================================================
CREATE TABLE confidence_history (
    id              SERIAL PRIMARY KEY,
    claim_id        UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    old_confidence  REAL NOT NULL,
    new_confidence  REAL NOT NULL,
    reason          TEXT NOT NULL,
    changed_by      TEXT,              -- agent type or 'manual'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_confidence_claim   ON confidence_history (claim_id);


-- ============================================================
-- Convenience views
-- ============================================================

-- Contradictions: pairs of claims where one contradicts the other
CREATE VIEW v_contradictions AS
SELECT
    cr.id AS relation_id,
    c1.project,
    c1.id AS claim_a_id,
    c1.statement AS claim_a,
    c1.confidence AS confidence_a,
    c2.id AS claim_b_id,
    c2.statement AS claim_b,
    c2.confidence AS confidence_b,
    cr.evidence,
    cr.strength
FROM claim_relations cr
JOIN claims c1 ON cr.source_id = c1.id
JOIN claims c2 ON cr.target_id = c2.id
WHERE cr.relation = 'contradicts'
ORDER BY cr.strength DESC, cr.created_at DESC;

-- Knowledge summary per project
CREATE VIEW v_knowledge_summary AS
SELECT
    c.project,
    c.claim_type,
    COUNT(*) AS count,
    ROUND(AVG(c.confidence)::numeric, 3) AS avg_confidence,
    MAX(c.updated_at) AS last_updated
FROM claims c
GROUP BY c.project, c.claim_type
ORDER BY c.project, count DESC;

-- Unsupported claims: findings/results with no 'supports' relations pointing to them
CREATE VIEW v_unsupported_claims AS
SELECT c.id, c.project, c.claim_type, c.statement, c.confidence, c.source
FROM claims c
WHERE c.claim_type IN ('finding', 'result', 'hypothesis')
  AND NOT EXISTS (
      SELECT 1 FROM claim_relations cr
      WHERE cr.target_id = c.id AND cr.relation = 'supports'
  )
ORDER BY c.confidence DESC;

COMMIT;
```

### Embedding Dimension Note

The schema uses `vector(1024)` for Voyage-3-Lite. If switching to OpenAI `text-embedding-3-small` (1536 dimensions), change the column definition accordingly. The HNSW index parameters are tuned for corpora under 100K claims -- no adjustment needed for years.

---

## KnowledgeGraph Class

### File: `orchestrator/src/knowledge-graph.ts`

```typescript
import pg from "pg";
import { randomUUID } from "node:crypto";

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

export type ClaimType =
  | "hypothesis" | "finding" | "definition" | "proof"
  | "citation"  | "method"  | "result"     | "observation"
  | "decision"  | "question";

export type SourceType =
  | "paper" | "eval" | "status_yaml" | "manual" | "agent_session";

export type RelationType =
  | "supports"    | "contradicts" | "derives_from" | "cited_in"
  | "supersedes"  | "refines"     | "depends_on"   | "related_to";

export interface ClaimRelation {
  sourceId: string;
  targetId: string;
  relation: RelationType;
  strength?: number;
  evidence?: string;
}

export interface ClaimRow extends Claim {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface SubgraphResult {
  claims: ClaimRow[];
  relations: Array<ClaimRelation & { id: string }>;
}

export class KnowledgeGraph {
  private pool: pg.Pool;
  private embedFn: (text: string) => Promise<number[]>;

  constructor(
    pool: pg.Pool,
    embedFn: (text: string) => Promise<number[]>,
  ) {
    this.pool = pool;
    this.embedFn = embedFn;
  }

  /** Insert a new claim with auto-computed embedding. */
  async addClaim(claim: Claim): Promise<ClaimRow> {
    const id = claim.id ?? randomUUID();
    const embedding = await this.embedFn(claim.statement);
    const embeddingStr = `[${embedding.join(",")}]`;

    const { rows } = await this.pool.query(
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
    return this.rowToClaim(rows[0]);
  }

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

  /** Semantic search: find claims similar to a natural-language query. */
  async query(
    naturalLanguageQuery: string,
    opts?: { project?: string; type?: ClaimType; limit?: number; threshold?: number },
  ): Promise<ClaimRow[]> {
    const embedding = await this.embedFn(naturalLanguageQuery);
    const embeddingStr = `[${embedding.join(",")}]`;
    const limit = opts?.limit ?? 10;
    const threshold = opts?.threshold ?? 0.15; // cosine distance < 0.15 ≈ similarity > 0.85

    let sql = `
      SELECT *, (embedding <=> $1::vector) AS distance
      FROM claims
      WHERE (embedding <=> $1::vector) < $2
    `;
    const params: unknown[] = [embeddingStr, threshold];
    let paramIdx = 3;

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

    sql += ` ORDER BY distance ASC LIMIT $${paramIdx}`;
    params.push(limit);

    const { rows } = await this.pool.query(sql, params);
    return rows.map((r) => this.rowToClaim(r));
  }

  /** Get all claims connected within N hops of a given claim. */
  async getSubgraph(claimId: string, depth: number = 2): Promise<SubgraphResult> {
    // Recursive CTE to walk the graph
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

    const claimIds = claimRows.map((r) => r.id);
    const { rows: relRows } = await this.pool.query(
      `SELECT * FROM claim_relations
       WHERE source_id = ANY($1) AND target_id = ANY($1)`,
      [claimIds],
    );

    return {
      claims: claimRows.map((r) => this.rowToClaim(r)),
      relations: relRows.map((r) => ({
        id: r.id,
        sourceId: r.source_id,
        targetId: r.target_id,
        relation: r.relation,
        strength: r.strength,
        evidence: r.evidence,
      })),
    };
  }

  /** All claims for a project, optionally filtered by type. */
  async getProjectClaims(
    project: string,
    type?: ClaimType,
  ): Promise<ClaimRow[]> {
    let sql = "SELECT * FROM claims WHERE project = $1";
    const params: unknown[] = [project];
    if (type) {
      sql += " AND claim_type = $2";
      params.push(type);
    }
    sql += " ORDER BY confidence DESC, created_at DESC";
    const { rows } = await this.pool.query(sql, params);
    return rows.map((r) => this.rowToClaim(r));
  }

  /** Find pairs of claims that contradict each other. */
  async findContradictions(project: string): Promise<SubgraphResult["relations"]> {
    const { rows } = await this.pool.query(
      `SELECT cr.* FROM claim_relations cr
       JOIN claims c1 ON cr.source_id = c1.id
       JOIN claims c2 ON cr.target_id = c2.id
       WHERE cr.relation = 'contradicts'
         AND c1.project = $1
       ORDER BY cr.strength DESC`,
      [project],
    );
    return rows.map((r) => ({
      id: r.id,
      sourceId: r.source_id,
      targetId: r.target_id,
      relation: r.relation as RelationType,
      strength: r.strength,
      evidence: r.evidence,
    }));
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
    return rows.map((r) => this.rowToClaim(r));
  }

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

  /** Check for near-duplicate claims (cosine distance < 0.05). */
  async findNearDuplicates(
    statement: string,
    project: string,
  ): Promise<ClaimRow[]> {
    const embedding = await this.embedFn(statement);
    const embeddingStr = `[${embedding.join(",")}]`;
    const { rows } = await this.pool.query(
      `SELECT *, (embedding <=> $1::vector) AS distance
       FROM claims
       WHERE project = $2 AND (embedding <=> $1::vector) < 0.05
       ORDER BY distance ASC
       LIMIT 5`,
      [embeddingStr, project],
    );
    return rows.map((r) => this.rowToClaim(r));
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
        parseInt(relCount[0].cnt), claims.map((r) => r.id),
      ],
    );
  }

  /** Knowledge graph stats for the health endpoint. */
  async getStats(): Promise<Record<string, unknown>> {
    const { rows } = await this.pool.query(`
      SELECT
        (SELECT COUNT(*) FROM claims) AS total_claims,
        (SELECT COUNT(*) FROM claim_relations) AS total_relations,
        (SELECT COUNT(*) FROM claims WHERE embedding IS NOT NULL) AS embedded_claims,
        (SELECT COUNT(DISTINCT project) FROM claims) AS projects_with_claims
    `);
    return rows[0];
  }

  // -- internal --

  private rowToClaim(row: Record<string, unknown>): ClaimRow {
    return {
      id: row.id as string,
      project: row.project as string,
      claimType: row.claim_type as ClaimType,
      statement: row.statement as string,
      confidence: row.confidence as number,
      source: row.source as string | undefined,
      sourceType: row.source_type as SourceType | undefined,
      metadata: (row.metadata ?? {}) as Record<string, unknown>,
      createdAt: row.created_at as Date,
      updatedAt: row.updated_at as Date,
    };
  }
}
```

---

## Embedding Strategy

### Provider Selection

| Provider | Model | Dimensions | Cost / 1M tokens | Latency | Notes |
|----------|-------|-----------|-------------------|---------|-------|
| **Voyage AI** | voyage-3-lite | 1024 | $0.02 | ~50ms | Best quality/cost ratio for research text |
| OpenAI | text-embedding-3-small | 1536 | $0.02 | ~30ms | Good fallback, wider ecosystem |
| Local | nomic-embed-text | 768 | $0 | ~100ms | Requires local GPU, no API cost |

**Recommended:** Voyage-3-Lite via the Anthropic partnership. Use `VOYAGE_API_KEY` in `.env`. Fall back to OpenAI if Voyage is unavailable.

### Embed Function Implementation

```typescript
// orchestrator/src/embeddings.ts

export async function createEmbedFn(
  provider: "voyage" | "openai" = "voyage",
): Promise<(text: string) => Promise<number[]>> {

  if (provider === "voyage") {
    const apiKey = process.env.VOYAGE_API_KEY;
    if (!apiKey) throw new Error("VOYAGE_API_KEY not set");

    return async (text: string) => {
      const res = await fetch("https://api.voyageai.com/v1/embeddings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "voyage-3-lite",
          input: [text],
          input_type: "document",
        }),
      });
      const json = await res.json() as { data: Array<{ embedding: number[] }> };
      return json.data[0].embedding;
    };
  }

  // OpenAI fallback
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY not set");

  return async (text: string) => {
    const res = await fetch("https://api.openai.com/v1/embeddings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "text-embedding-3-small",
        input: text,
      }),
    });
    const json = await res.json() as { data: Array<{ embedding: number[] }> };
    return json.data[0].embedding;
  };
}
```

### Cost Estimate

- Average claim: ~50 tokens
- 1000 claims: ~50K tokens = ~$0.001 (voyage-3-lite)
- Query embedding: negligible (single embedding per query)
- At full scale (10K claims across all projects): ~$0.01/month for embeddings
- **Budget impact: negligible** -- well under $1/month even with aggressive use

### Similarity Thresholds

| Threshold (cosine distance) | Meaning | Use Case |
|-----------------------------|---------|----------|
| < 0.05 | Near-duplicate | Deduplication check before insert |
| < 0.15 | Highly related | Default semantic query threshold |
| < 0.30 | Loosely related | Broad exploration queries |

---

## OpenClaw Skill: `knowledge`

### Directory: `openclaw/skills/knowledge/`

```
openclaw/skills/knowledge/
  SKILL.md
  scripts/
    knowledge.sh
```

### SKILL.md

```markdown
# knowledge

Read and write claims to the project knowledge graph. Provides persistent
semantic memory across agent sessions.

## Usage
Used by all agents to record findings, query existing knowledge, and
check for contradictions before making claims.

## Functions

### Add a claim
  ./scripts/knowledge.sh add <project> <claim_type> <statement> [confidence] [source]

### Query (semantic search)
  ./scripts/knowledge.sh query <project> "<natural language question>" [limit]

### List claims by type
  ./scripts/knowledge.sh list <project> [claim_type]

### Add a relation
  ./scripts/knowledge.sh relate <source_id> <target_id> <relation> [evidence]

### Find contradictions
  ./scripts/knowledge.sh contradictions <project>

### Find unsupported claims
  ./scripts/knowledge.sh unsupported <project>

### Get evidence chain
  ./scripts/knowledge.sh evidence <claim_id>

## Claim Types
hypothesis, finding, definition, proof, citation, method, result,
observation, decision, question

## Relation Types
supports, contradicts, derives_from, cited_in, supersedes, refines,
depends_on, related_to

## Notes
- Duplicate detection runs automatically on add -- if a near-duplicate
  exists (cosine similarity > 0.95), the skill warns and returns the
  existing claim instead of creating a new one.
- Always check for existing claims before adding new ones.
- Set confidence explicitly: 0.9+ for well-supported findings, 0.5 for
  hypotheses, 0.3 for speculative observations.
```

### scripts/knowledge.sh

The shell script calls the Deepwork API endpoints for the knowledge graph. The API routes are mounted at `/api/knowledge/`.

---

## Integration Points

### 1. Session Prompt Builder

The most impactful integration. Modify `SessionRunner.buildPrompt()` in `orchestrator/src/session-runner.ts` to inject relevant knowledge context.

```typescript
// In SessionRunner.buildPrompt(), after loading status.yaml:

// Auto-inject relevant knowledge claims
const knowledgeContext = await this.getKnowledgeContext(projectName, agentType);
if (knowledgeContext) {
  sections.push("# Existing Knowledge (from Knowledge Graph)\n\n" + knowledgeContext);
}
```

The `getKnowledgeContext` method:
1. Reads the current task description from `status.yaml` (`current_focus` field)
2. Runs a semantic query against the knowledge graph using that task as the query
3. Formats the top 15-20 most relevant claims as a structured list
4. Includes any known contradictions for the project
5. Keeps the injected context under 2000 tokens to avoid prompt bloat

**Token budget for knowledge context:**

| Agent Type | Max Claims Injected | Rationale |
|------------|--------------------:|-----------|
| writer     | 25 | Needs broad knowledge for paper sections |
| critic     | 20 | Needs to check claims against evidence |
| reviewer   | 20 | Needs full picture for review |
| researcher | 15 | Working on specific sub-questions |
| experimenter | 10 | Focused on specific eval tasks |
| editor     | 10 | Mostly formatting, less knowledge-heavy |

### 2. Eval Pipeline Integration

After an eval run completes, automatically create `finding` and `result` claims. Hook into the eval completion handler in `orchestrator/src/eval-manager.ts`:

```typescript
// After eval run completes and accuracy is computed:
await knowledgeGraph.addClaim({
  project: "reasoning-gaps",
  claimType: "result",
  statement: `${model} achieves ${accuracy} accuracy on ${task} under ${condition} condition (n=${instanceCount})`,
  confidence: 0.95, // empirical results are high-confidence
  source: `eval_runs/${runId}`,
  sourceType: "eval",
  metadata: { model, task, condition, accuracy, instanceCount, runId },
});
```

### 3. Paper Writer Integration

The writer agent can query claims relevant to the section being written:

```bash
# Get all findings related to Section 3 (CoT analysis)
./scripts/knowledge.sh query reasoning-gaps "chain of thought lift analysis by reasoning type" 20

# Get all citations
./scripts/knowledge.sh list reasoning-gaps citation
```

### 4. Critic Integration

The critic agent queries for contradictions and unsupported claims before reviewing:

```bash
# Surface contradictions
./scripts/knowledge.sh contradictions reasoning-gaps

# Find claims without supporting evidence
./scripts/knowledge.sh unsupported reasoning-gaps
```

### 5. Health Endpoint

Add knowledge graph stats to the existing health route in `orchestrator/src/api.ts`:

```typescript
// In healthRoute handler, after database check:
let knowledgeStats = null;
try {
  knowledgeStats = await knowledgeGraph.getStats();
} catch { /* knowledge graph not initialized */ }

// Include in response:
res.json({
  // ... existing fields ...
  knowledge_graph: knowledgeStats,
});
```

### 6. Daemon Periodic Tasks

Add to the daemon cycle in `orchestrator/src/daemon.ts`:

- **Daily snapshot:** Create a knowledge snapshot for each active project at the end of each day
- **Consistency check:** Run `findContradictions()` weekly; if new contradictions found, log to activity feed and optionally trigger a critic session
- **Stale claim detection:** Flag claims older than 30 days with confidence < 0.5 that have no supporting relations

---

## API Routes

Mount at `/api/knowledge` in `orchestrator/src/api.ts`.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/knowledge/claims` | Add a new claim |
| GET | `/api/knowledge/claims?project=X&type=Y` | List claims |
| GET | `/api/knowledge/claims/:id` | Get a single claim |
| PATCH | `/api/knowledge/claims/:id` | Update claim (confidence, metadata) |
| POST | `/api/knowledge/query` | Semantic search (body: `{ query, project?, type?, limit? }`) |
| POST | `/api/knowledge/relations` | Add a relation |
| GET | `/api/knowledge/subgraph/:id?depth=2` | Get connected subgraph |
| GET | `/api/knowledge/contradictions/:project` | List contradictions |
| GET | `/api/knowledge/unsupported/:project` | List unsupported claims |
| GET | `/api/knowledge/evidence/:id` | Trace evidence chain |
| GET | `/api/knowledge/stats` | Knowledge graph statistics |
| POST | `/api/knowledge/snapshot/:project` | Trigger a snapshot |

---

## Migration / Backfill Plan

Backfill existing knowledge from the reasoning-gaps project to bootstrap the graph.

### Source 1: Eval Results (high confidence, automated)

Extract from the `eval_results` and `checkpoints` tables. Creates `result` claims.

```sql
-- Generate one claim per model/task/condition combination
SELECT
    model, task, condition,
    COUNT(*) AS n,
    ROUND(AVG(correct::int)::numeric, 4) AS accuracy
FROM eval_results
GROUP BY model, task, condition;
```

Expected yield: ~243 result claims (9 models x 9 tasks x 3 conditions).

### Source 2: Paper Claims (medium confidence, semi-automated)

Parse the LaTeX paper at `projects/reasoning-gaps/paper/main.tex` for:
- `\begin{theorem}` / `\begin{proposition}` / `\begin{definition}` blocks --> `proof`, `definition` claims
- Sentences containing "we find that", "our results show", "we hypothesize" --> `finding`, `hypothesis` claims
- `\cite{}` references --> `citation` claims linked to the citing claim

Expected yield: ~30-50 claims.

### Source 3: Status.yaml Decisions (high confidence, automated)

Import from `projects/reasoning-gaps/status.yaml` `decisions_made` entries and from the `decisions` table.

```typescript
// For each decision in status.yaml:
await kg.addClaim({
  project: "reasoning-gaps",
  claimType: "decision",
  statement: decision.decision,
  confidence: 0.9,
  source: "status.yaml",
  sourceType: "status_yaml",
  metadata: { date: decision.date, rationale: decision.rationale },
});
```

Expected yield: ~15-25 claims.

### Source 4: Analysis Summary (high confidence, automated)

Import from `projects/reasoning-gaps/benchmarks/results/analysis/summary.md`. Parse key findings (lines starting with `-` or `*` in findings sections).

Expected yield: ~10-15 claims.

### Backfill Script

Create `orchestrator/scripts/backfill-knowledge.ts`:
1. Connect to PostgreSQL
2. Initialize KnowledgeGraph with embedding function
3. Run each source extractor
4. Check for near-duplicates before inserting
5. Create `supports` relations between findings and their source results
6. Create a snapshot after backfill completes
7. Print summary: claims added, relations created, duplicates skipped

---

## Task Breakdown

Ordered for implementation. Each task is independently mergeable.

### Task 1: SQL Migration
**File:** `orchestrator/sql/005_knowledge_graph.sql`
**Effort:** 1 hour
**Dependencies:** None (pgvector must be installed on VPS)
**Deliverables:**
- [ ] `claims` table with pgvector HNSW index
- [ ] `claim_relations` table with uniqueness constraint
- [ ] `knowledge_snapshots` table
- [ ] `confidence_history` table
- [ ] `v_contradictions`, `v_knowledge_summary`, `v_unsupported_claims` views
- [ ] Run migration on VPS: `psql $DATABASE_URL < orchestrator/sql/005_knowledge_graph.sql`
- [ ] Verify pgvector extension is available: `CREATE EXTENSION IF NOT EXISTS vector;`

### Task 2: Embedding Integration
**File:** `orchestrator/src/embeddings.ts`
**Effort:** 2 hours
**Dependencies:** Task 1
**Deliverables:**
- [ ] `createEmbedFn()` with Voyage and OpenAI providers
- [ ] Add `VOYAGE_API_KEY` to VPS `.env`
- [ ] Verify embeddings work: test with a sample sentence, confirm 1024-dim vector returned
- [ ] Add batch embedding support (for backfill efficiency)

### Task 3: KnowledgeGraph Class
**File:** `orchestrator/src/knowledge-graph.ts`
**Effort:** 3-4 hours
**Dependencies:** Tasks 1, 2
**Deliverables:**
- [ ] `addClaim()` with auto-embedding and duplicate detection
- [ ] `addRelation()` with upsert behavior
- [ ] `query()` with vector similarity search
- [ ] `getSubgraph()` with recursive CTE
- [ ] `getProjectClaims()` with optional type filter
- [ ] `findContradictions()` and `findNearDuplicates()`
- [ ] `getEvidenceChain()` with recursive traversal
- [ ] `updateConfidence()` with audit trail
- [ ] `createSnapshot()` and `getStats()`
- [ ] Unit tests for all methods

### Task 4: API Routes
**File:** `orchestrator/src/routes/knowledge.ts`
**Effort:** 2 hours
**Dependencies:** Task 3
**Deliverables:**
- [ ] REST routes for all CRUD operations
- [ ] Semantic query endpoint
- [ ] Mount routes in `api.ts` at `/api/knowledge`
- [ ] Auth middleware applied (existing `authMiddleware`)

### Task 5: OpenClaw Knowledge Skill
**Directory:** `openclaw/skills/knowledge/`
**Effort:** 1-2 hours
**Dependencies:** Task 4
**Deliverables:**
- [ ] `SKILL.md` with full usage documentation
- [ ] `scripts/knowledge.sh` calling API endpoints
- [ ] Test all skill commands manually

### Task 6: Session Prompt Integration
**File:** `orchestrator/src/session-runner.ts`
**Effort:** 2-3 hours
**Dependencies:** Task 3
**Deliverables:**
- [ ] `getKnowledgeContext()` method on `SessionRunner`
- [ ] Inject relevant claims into prompt based on `current_focus`
- [ ] Agent-type-aware token budgeting for knowledge context
- [ ] Include contradiction warnings in prompt when relevant
- [ ] Test with a dry-run session to verify prompt quality

### Task 7: Backfill from Reasoning-Gaps
**File:** `orchestrator/scripts/backfill-knowledge.ts`
**Effort:** 2-3 hours
**Dependencies:** Tasks 2, 3
**Deliverables:**
- [ ] Extract eval results from `checkpoints` materialized view
- [ ] Parse LaTeX paper for structured claims
- [ ] Import decisions from `decisions` table and `status.yaml`
- [ ] Import analysis summary findings
- [ ] Create `supports` / `derives_from` relations between related claims
- [ ] Run backfill on VPS, verify claim count and relation integrity
- [ ] Create initial snapshot

### Task 8: Daemon and Health Integration
**Files:** `orchestrator/src/daemon.ts`, `orchestrator/src/api.ts`
**Effort:** 1-2 hours
**Dependencies:** Task 3
**Deliverables:**
- [ ] Add `knowledge_graph` stats to `/api/health` response
- [ ] Daily snapshot creation in daemon cycle
- [ ] Weekly contradiction check with activity logging
- [ ] Stale claim detection (optional, low priority)

---

## Success Criteria

1. **Queryable memory:** An agent can run `./scripts/knowledge.sh query reasoning-gaps "CoT lift on intractability tasks"` and get back the specific result claims with accuracy numbers and confidence levels.

2. **Auto-populated context:** When a writer session starts for reasoning-gaps, the prompt includes the 15-25 most relevant claims for the current focus area, formatted as a knowledge brief. The agent does not need to re-read analysis files.

3. **Provenance tracking:** Every claim has a `source` and `source_type`. Running `./scripts/knowledge.sh evidence <claim_id>` traces back to the raw eval run or paper section that generated it.

4. **Contradiction surfacing:** `findContradictions()` returns pairs of claims with conflicting statements. The critic agent receives these in its prompt context. The daemon logs new contradictions to the activity feed.

5. **No manual curation:** The backfill script runs once. After that, new claims are added automatically by eval completions and agent sessions. The knowledge graph grows as the project progresses.

6. **Low overhead:** Embedding costs stay under $1/month. Knowledge context injection adds < 3 seconds to session startup. The HNSW index keeps query latency under 50ms for corpora up to 100K claims.

---

## Future Extensions (not in scope for initial implementation)

- **Cross-project knowledge transfer:** Query claims from project A while working on project B. Useful when agent-failure-taxonomy shares concepts with reasoning-gaps.
- **Claim versioning:** Track how a claim's statement evolves over time, not just its confidence.
- **Graph visualization:** D3-based visualization of the knowledge graph on the Astro dashboard site.
- **Automatic relation inference:** Use an LLM to propose relations between unconnected claims that are semantically similar.
- **Export to paper:** Generate a BibTeX-compatible bibliography from all `citation` claims, or auto-generate a "Related Work" section from the graph.
