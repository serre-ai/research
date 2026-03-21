-- Literature intelligence tables
-- Requires pgvector extension (already enabled for knowledge graph)

-- Papers discovered by the literature scanner/monitor
CREATE TABLE IF NOT EXISTS lit_papers (
  id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  arxiv_id      TEXT,
  s2_id         TEXT,
  doi           TEXT,
  title         TEXT NOT NULL,
  abstract      TEXT,
  authors       JSONB NOT NULL DEFAULT '[]',
  venue         TEXT,
  year          INTEGER,
  published_at  TIMESTAMPTZ,
  categories    JSONB NOT NULL DEFAULT '[]',
  citation_count INTEGER DEFAULT 0,
  url           TEXT,
  pdf_url       TEXT,
  source        TEXT NOT NULL CHECK (source IN ('arxiv', 's2', 'manual')),
  embedding     vector(1024),
  discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata      JSONB NOT NULL DEFAULT '{}'
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_lit_papers_arxiv ON lit_papers (arxiv_id) WHERE arxiv_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_lit_papers_s2 ON lit_papers (s2_id) WHERE s2_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lit_papers_published ON lit_papers (published_at DESC);
CREATE INDEX IF NOT EXISTS idx_lit_papers_discovered ON lit_papers (discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_lit_papers_year ON lit_papers (year);

-- Alerts generated when a paper matches project claims/terms
CREATE TABLE IF NOT EXISTS lit_alerts (
  id            SERIAL PRIMARY KEY,
  paper_id      TEXT NOT NULL REFERENCES lit_papers(id) ON DELETE CASCADE,
  project       TEXT NOT NULL,
  priority      TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
  relation      TEXT NOT NULL CHECK (relation IN ('competes', 'supports', 'extends', 'contradicts', 'related')),
  similarity    REAL,
  matched_claim TEXT,
  matched_terms TEXT[],
  explanation   TEXT,
  triage_model  TEXT,
  acknowledged  BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lit_alerts_project ON lit_alerts (project, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lit_alerts_priority ON lit_alerts (priority, acknowledged, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lit_alerts_paper ON lit_alerts (paper_id);

-- Citation watch list — papers whose new citations we monitor
CREATE TABLE IF NOT EXISTS lit_citation_watches (
  id            SERIAL PRIMARY KEY,
  paper_id      TEXT REFERENCES lit_papers(id) ON DELETE SET NULL,
  arxiv_id      TEXT,
  s2_id         TEXT,
  title         TEXT NOT NULL,
  project       TEXT NOT NULL,
  reason        TEXT,
  last_checked  TIMESTAMPTZ,
  last_citation_count INTEGER DEFAULT 0,
  active        BOOLEAN NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lit_watches_project ON lit_citation_watches (project, active);
CREATE INDEX IF NOT EXISTS idx_lit_watches_active ON lit_citation_watches (active, last_checked);
