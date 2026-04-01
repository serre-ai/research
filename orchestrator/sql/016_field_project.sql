-- Synthetic project for field-level claims extracted from literature
INSERT INTO projects (id, name, title, phase, status)
VALUES ('_field', '_field', 'Field-Level Knowledge Graph', 'active', 'active')
ON CONFLICT (id) DO NOTHING;

-- Add paper_id column to claims for linking back to lit_papers
ALTER TABLE claims ADD COLUMN IF NOT EXISTS paper_id TEXT;
CREATE INDEX IF NOT EXISTS idx_claims_paper ON claims (paper_id) WHERE paper_id IS NOT NULL;
