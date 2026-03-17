-- Event Bus: persistent event log with LISTEN/NOTIFY
-- Migration: 006_event_bus.sql
-- Created: 2026-03-17

BEGIN;

-- ============================================================
-- Domain Events — persistent audit log
-- ============================================================
CREATE TABLE IF NOT EXISTS domain_events (
    id          BIGSERIAL PRIMARY KEY,
    type        TEXT NOT NULL,
    payload     JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed   BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_domain_events_type ON domain_events (type);
CREATE INDEX IF NOT EXISTS idx_domain_events_created ON domain_events (created_at);
CREATE INDEX IF NOT EXISTS idx_domain_events_unprocessed ON domain_events (processed) WHERE NOT processed;

-- Trigger: pg_notify on insert for real-time dispatch
CREATE OR REPLACE FUNCTION notify_event() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('deepwork_events', json_build_object(
        'id', NEW.id,
        'type', NEW.type,
        'payload', NEW.payload
    )::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS event_notify ON domain_events;
CREATE TRIGGER event_notify AFTER INSERT ON domain_events
    FOR EACH ROW EXECUTE FUNCTION notify_event();

-- ============================================================
-- Dead-letter queue — failed handler executions
-- ============================================================
CREATE TABLE IF NOT EXISTS domain_events_dead_letter (
    id              BIGSERIAL PRIMARY KEY,
    event_id        BIGINT NOT NULL REFERENCES domain_events(id) ON DELETE CASCADE,
    handler_name    TEXT NOT NULL,
    error           TEXT NOT NULL,
    attempts        INTEGER NOT NULL DEFAULT 1,
    last_attempt_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved        BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_dead_letter_event ON domain_events_dead_letter (event_id);
CREATE INDEX IF NOT EXISTS idx_dead_letter_unresolved ON domain_events_dead_letter (resolved) WHERE NOT resolved;

COMMIT;
