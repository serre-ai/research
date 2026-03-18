BEGIN;

-- Session evaluations: structured post-session assessment by the research planner
CREATE TABLE IF NOT EXISTS session_evaluations (
    id                SERIAL PRIMARY KEY,
    session_id        TEXT NOT NULL,
    brief_id          TEXT NOT NULL,
    project           TEXT NOT NULL,
    agent_type        TEXT NOT NULL,
    strategy          TEXT NOT NULL,
    objective         TEXT NOT NULL,
    deliverables_met  INTEGER NOT NULL DEFAULT 0,
    deliverables_total INTEGER NOT NULL DEFAULT 0,
    quality_score     INTEGER NOT NULL DEFAULT 0
                      CHECK (quality_score >= 0 AND quality_score <= 100),
    claims_updated    TEXT[] DEFAULT '{}',
    reasoning         TEXT,
    cost_usd          REAL DEFAULT 0,
    duration_ms       INTEGER DEFAULT 0,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_eval_project ON session_evaluations (project);
CREATE INDEX IF NOT EXISTS idx_session_eval_strategy ON session_evaluations (strategy);
CREATE INDEX IF NOT EXISTS idx_session_eval_created ON session_evaluations (created_at);

-- Planner state: persistent strategy weights and metadata
CREATE TABLE IF NOT EXISTS planner_state (
    project     TEXT NOT NULL,
    key         TEXT NOT NULL,
    value       JSONB NOT NULL,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project, key)
);

COMMIT;
