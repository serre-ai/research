-- Knowledge Graph: typed claims with vector embeddings and relationships
-- Migration: 005_knowledge_graph.sql
-- Created: 2026-03-16
--
-- Stores every claim, finding, hypothesis, citation, and decision as typed
-- nodes with directed relationships and pgvector embeddings for semantic search.

BEGIN;

-- Require pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Claims — atomic knowledge units
-- ============================================================
CREATE TABLE IF NOT EXISTS claims (
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
    source          TEXT,
    source_type     TEXT
                    CHECK (source_type IN (
                        'paper', 'eval', 'status_yaml', 'manual', 'agent_session'
                    )),
    embedding       vector(1024),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_claims_project       ON claims (project);
CREATE INDEX IF NOT EXISTS idx_claims_type          ON claims (claim_type);
CREATE INDEX IF NOT EXISTS idx_claims_confidence    ON claims (confidence);
CREATE INDEX IF NOT EXISTS idx_claims_created       ON claims (created_at);
CREATE INDEX IF NOT EXISTS idx_claims_project_type  ON claims (project, claim_type);

-- HNSW index for fast approximate nearest-neighbor search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_claims_embedding ON claims
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Full-text search on statement
CREATE INDEX IF NOT EXISTS idx_claims_statement_fts ON claims
    USING gin (to_tsvector('english', statement));


-- ============================================================
-- Claim Relations — directed edges between claims
-- ============================================================
CREATE TABLE IF NOT EXISTS claim_relations (
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
    evidence        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT no_self_relation CHECK (source_id != target_id),
    CONSTRAINT unique_relation UNIQUE (source_id, target_id, relation)
);

CREATE INDEX IF NOT EXISTS idx_relations_source   ON claim_relations (source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target   ON claim_relations (target_id);
CREATE INDEX IF NOT EXISTS idx_relations_type     ON claim_relations (relation);


-- ============================================================
-- Knowledge Snapshots — periodic state captures for time-travel
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    snapshot_date   DATE NOT NULL,
    claim_count     INTEGER NOT NULL,
    relation_count  INTEGER NOT NULL,
    summary         TEXT,
    claim_ids       UUID[] NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_project_date UNIQUE (project, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_snapshots_project  ON knowledge_snapshots (project);
CREATE INDEX IF NOT EXISTS idx_snapshots_date     ON knowledge_snapshots (snapshot_date);


-- ============================================================
-- Confidence History — track how claim confidence changes
-- ============================================================
CREATE TABLE IF NOT EXISTS confidence_history (
    id              SERIAL PRIMARY KEY,
    claim_id        UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    old_confidence  REAL NOT NULL,
    new_confidence  REAL NOT NULL,
    reason          TEXT NOT NULL,
    changed_by      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_confidence_claim   ON confidence_history (claim_id);


-- ============================================================
-- Convenience views
-- ============================================================

-- Contradictions: pairs of claims where one contradicts the other
CREATE OR REPLACE VIEW v_contradictions AS
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
CREATE OR REPLACE VIEW v_knowledge_summary AS
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
CREATE OR REPLACE VIEW v_unsupported_claims AS
SELECT c.id, c.project, c.claim_type, c.statement, c.confidence, c.source
FROM claims c
WHERE c.claim_type IN ('finding', 'result', 'hypothesis')
  AND NOT EXISTS (
      SELECT 1 FROM claim_relations cr
      WHERE cr.target_id = c.id AND cr.relation = 'supports'
  )
ORDER BY c.confidence DESC;

COMMIT;
