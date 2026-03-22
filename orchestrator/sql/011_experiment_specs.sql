BEGIN;

CREATE TABLE IF NOT EXISTS experiment_specs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project TEXT NOT NULL,
  experiment_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'reviewed', 'approved', 'running', 'complete', 'failed')),
  review_verdict TEXT CHECK (review_verdict IN ('approve', 'revise', 'reject')),
  canary_passed BOOLEAN,
  estimated_cost REAL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (project, experiment_name)
);

CREATE INDEX IF NOT EXISTS idx_experiment_specs_project ON experiment_specs (project);

-- Reusable trigger function: set updated_at = NOW() on any UPDATE
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_experiment_specs_updated_at
  BEFORE UPDATE ON experiment_specs
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

COMMIT;
