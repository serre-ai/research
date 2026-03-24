-- Extend lit_papers with research intelligence fields
BEGIN;

ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS contribution_type TEXT;
ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS key_finding TEXT;
ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS gap_left TEXT;
ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS portfolio_relevance REAL;
ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS citation_velocity REAL;
ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS topics TEXT[];
ALTER TABLE lit_papers ADD COLUMN IF NOT EXISTS analyzed_at TIMESTAMPTZ;

-- Index for finding unanalyzed papers
CREATE INDEX IF NOT EXISTS idx_lit_papers_analyzed ON lit_papers (analyzed_at) WHERE analyzed_at IS NULL;

-- Index for topic-based queries
CREATE INDEX IF NOT EXISTS idx_lit_papers_topics ON lit_papers USING gin (topics);

-- Index for citation velocity (find trending papers)
CREATE INDEX IF NOT EXISTS idx_lit_papers_velocity ON lit_papers (citation_velocity DESC NULLS LAST) WHERE citation_velocity IS NOT NULL;

COMMIT;
