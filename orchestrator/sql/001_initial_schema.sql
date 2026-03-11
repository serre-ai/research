-- Deepwork Research Platform — Initial PostgreSQL Schema
-- Created: 2026-03-11
--
-- Design principles:
--   - Git/YAML remains source of truth; Postgres is the read-optimized mirror
--   - Eval scripts write JSONL checkpoints AND insert into Postgres
--   - Dashboard reads only from Postgres (fast, no file parsing)
--   - All timestamps stored as TIMESTAMPTZ (UTC)

BEGIN;

-- ============================================================
-- Projects — mirrors status.yaml per project
-- ============================================================
CREATE TABLE projects (
    id              TEXT PRIMARY KEY,           -- e.g. 'reasoning-gaps'
    name            TEXT NOT NULL,              -- display name
    title           TEXT NOT NULL,
    venue           TEXT,                       -- e.g. 'NeurIPS 2026'
    phase           TEXT NOT NULL DEFAULT 'research',
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'paused', 'review', 'completed')),
    confidence      REAL DEFAULT 0.5,
    current_focus   TEXT,
    current_activity TEXT,
    notes           TEXT,
    branch          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_status ON projects (status);


-- ============================================================
-- Eval Results — individual evaluation instances
-- ============================================================
CREATE TABLE eval_results (
    instance_id     TEXT NOT NULL,              -- e.g. 'B1_masked_majority_d1_0000'
    model           TEXT NOT NULL,              -- e.g. 'claude-haiku-4-5-20251001'
    task            TEXT NOT NULL,              -- e.g. 'B1_masked_majority'
    condition       TEXT NOT NULL,              -- 'direct', 'short_cot', 'budget_cot'
    difficulty      INTEGER NOT NULL,
    correct         BOOLEAN NOT NULL,
    extracted_answer TEXT,
    ground_truth    TEXT NOT NULL,
    latency_ms      REAL,
    response        TEXT,                       -- full model response
    metadata        JSONB DEFAULT '{}',         -- is_refusal, prompt_sent, etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (instance_id, model, condition)
);

-- Dashboard queries: accuracy by model, by task, by condition
CREATE INDEX idx_eval_results_model       ON eval_results (model);
CREATE INDEX idx_eval_results_task        ON eval_results (task);
CREATE INDEX idx_eval_results_condition   ON eval_results (condition);
CREATE INDEX idx_eval_results_model_task  ON eval_results (model, task, condition);
CREATE INDEX idx_eval_results_created     ON eval_results (created_at);
CREATE INDEX idx_eval_results_difficulty  ON eval_results (task, difficulty);


-- ============================================================
-- Eval Runs — aggregated run-level data
-- ============================================================
CREATE TABLE eval_runs (
    run_id          TEXT PRIMARY KEY,           -- e.g. 'claude-haiku-4-5-20251001_B1_masked_majority_direct'
    model           TEXT NOT NULL,
    task            TEXT NOT NULL,
    condition       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    accuracy        REAL,                       -- 0.0-1.0, computed after completion
    instance_count  INTEGER DEFAULT 0,
    total_expected  INTEGER,                    -- total instances expected for this run
    metadata        JSONB DEFAULT '{}'          -- avg_latency, cost_usd, etc.
);

CREATE INDEX idx_eval_runs_model     ON eval_runs (model);
CREATE INDEX idx_eval_runs_task      ON eval_runs (task);
CREATE INDEX idx_eval_runs_status    ON eval_runs (status);
CREATE INDEX idx_eval_runs_started   ON eval_runs (started_at);


-- ============================================================
-- Sessions — Claude agent sessions
-- ============================================================
CREATE TABLE sessions (
    session_id      TEXT PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    prompt          TEXT,                       -- initial prompt/task description
    agent_type      TEXT NOT NULL DEFAULT 'researcher'
                    CHECK (agent_type IN ('researcher', 'writer', 'reviewer', 'editor', 'strategist')),
    model           TEXT,                       -- e.g. 'claude-sonnet-4-20250514'
    tokens_used     INTEGER DEFAULT 0,
    cost_usd        REAL DEFAULT 0,
    commits_created INTEGER DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'running'
                    CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    error           TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_s      REAL
);

CREATE INDEX idx_sessions_project    ON sessions (project);
CREATE INDEX idx_sessions_started    ON sessions (started_at);
CREATE INDEX idx_sessions_status     ON sessions (status);
CREATE INDEX idx_sessions_model      ON sessions (model);


-- ============================================================
-- Decisions — autonomous decision log (mirrors status.yaml decisions_made)
-- ============================================================
CREATE TABLE decisions (
    id              SERIAL PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    date            DATE NOT NULL,
    decision        TEXT NOT NULL,
    rationale       TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_decisions_project   ON decisions (project);
CREATE INDEX idx_decisions_date      ON decisions (date);


-- ============================================================
-- Budget Events — spending records
-- ============================================================
CREATE TABLE budget_events (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    project         TEXT NOT NULL,
    session_id      TEXT,
    agent_type      TEXT,
    tokens_input    INTEGER DEFAULT 0,
    tokens_output   INTEGER DEFAULT 0,
    cost_usd        REAL NOT NULL DEFAULT 0,
    model           TEXT,
    daily_total     REAL,                       -- running daily total at time of event
    monthly_total   REAL                        -- running monthly total at time of event
);

CREATE INDEX idx_budget_events_timestamp  ON budget_events (timestamp);
CREATE INDEX idx_budget_events_project    ON budget_events (project);
CREATE INDEX idx_budget_events_date       ON budget_events (DATE(timestamp));
CREATE INDEX idx_budget_events_month      ON budget_events (DATE_TRUNC('month', timestamp));


-- ============================================================
-- Checkpoints — materialized view of eval progress
-- ============================================================
CREATE MATERIALIZED VIEW checkpoints AS
SELECT
    model,
    task,
    condition,
    COUNT(*)                          AS completed_count,
    SUM(correct::int)                 AS correct_count,
    ROUND(AVG(correct::int)::numeric, 4)  AS accuracy,
    ROUND(AVG(latency_ms)::numeric, 1)    AS avg_latency_ms,
    MAX(created_at)                   AS last_updated
FROM eval_results
GROUP BY model, task, condition;

CREATE UNIQUE INDEX idx_checkpoints_unique ON checkpoints (model, task, condition);


-- ============================================================
-- Helper: refresh checkpoints view
-- ============================================================
CREATE OR REPLACE FUNCTION refresh_checkpoints()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY checkpoints;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- Convenience views for dashboard
-- ============================================================

-- Accuracy heatmap: model x task x condition
CREATE VIEW v_accuracy_heatmap AS
SELECT
    model,
    task,
    condition,
    COUNT(*) AS n,
    ROUND(AVG(correct::int)::numeric, 4) AS accuracy,
    ROUND(AVG(latency_ms)::numeric, 1) AS avg_latency_ms
FROM eval_results
GROUP BY model, task, condition
ORDER BY model, task, condition;

-- CoT lift: accuracy difference between direct and short_cot per model/task
CREATE VIEW v_cot_lift AS
SELECT
    d.model,
    d.task,
    d.accuracy AS direct_accuracy,
    c.accuracy AS cot_accuracy,
    ROUND((c.accuracy - d.accuracy)::numeric, 4) AS cot_lift
FROM
    (SELECT model, task, AVG(correct::int) AS accuracy FROM eval_results WHERE condition = 'direct' GROUP BY model, task) d
JOIN
    (SELECT model, task, AVG(correct::int) AS accuracy FROM eval_results WHERE condition = 'short_cot' GROUP BY model, task) c
ON d.model = c.model AND d.task = c.task
ORDER BY cot_lift DESC;

-- Daily budget burn
CREATE VIEW v_daily_spend AS
SELECT
    DATE(timestamp) AS day,
    project,
    model,
    SUM(cost_usd) AS total_cost,
    SUM(tokens_input) AS total_tokens_in,
    SUM(tokens_output) AS total_tokens_out,
    COUNT(*) AS event_count
FROM budget_events
GROUP BY DATE(timestamp), project, model
ORDER BY day DESC, project;

COMMIT;
