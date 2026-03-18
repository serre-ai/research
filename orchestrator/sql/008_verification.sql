BEGIN;

CREATE TABLE IF NOT EXISTS verification_reports (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project         TEXT NOT NULL,
    latex_path      TEXT NOT NULL,
    total_claims    INTEGER NOT NULL DEFAULT 0,
    verified_claims INTEGER NOT NULL DEFAULT 0,
    unverified_claims INTEGER NOT NULL DEFAULT 0,
    inconsistencies INTEGER NOT NULL DEFAULT 0,
    missing_evidence INTEGER NOT NULL DEFAULT 0,
    report          JSONB NOT NULL DEFAULT '{}',
    triggered_by    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verification_project ON verification_reports (project);
CREATE INDEX IF NOT EXISTS idx_verification_created ON verification_reports (created_at);

COMMIT;
