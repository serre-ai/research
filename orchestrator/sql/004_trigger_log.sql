-- Trigger Log: Track fired triggers to prevent re-firing
-- Migration: 004_trigger_log.sql
-- Created: 2026-03-16

BEGIN;

CREATE TABLE IF NOT EXISTS trigger_log (
    id           SERIAL PRIMARY KEY,
    agent        TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    context      JSONB NOT NULL DEFAULT '{}',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acked_at     TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_trigger_log_agent        ON trigger_log (agent);
CREATE INDEX IF NOT EXISTS idx_trigger_log_type         ON trigger_log (trigger_type);
CREATE INDEX IF NOT EXISTS idx_trigger_log_created      ON trigger_log (created_at);
CREATE INDEX IF NOT EXISTS idx_trigger_log_pending      ON trigger_log (id) WHERE acked_at IS NULL;

COMMIT;
