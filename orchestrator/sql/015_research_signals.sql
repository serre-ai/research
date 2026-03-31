-- Research Intelligence Engine tables

CREATE TABLE IF NOT EXISTS research_signals (
  id            TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  detector      TEXT NOT NULL,
  signal_type   TEXT NOT NULL,
  title         TEXT NOT NULL,
  description   TEXT,
  confidence    REAL NOT NULL DEFAULT 0.5,
  source_papers TEXT[] DEFAULT '{}',
  source_claims TEXT[] DEFAULT '{}',
  topics        TEXT[] DEFAULT '{}',
  relevance     REAL DEFAULT 0,
  timing_score  REAL DEFAULT 0,
  metadata      JSONB DEFAULT '{}',
  batch_date    DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_batch ON research_signals (batch_date DESC);
CREATE INDEX IF NOT EXISTS idx_signals_detector ON research_signals (detector, batch_date DESC);

CREATE TABLE IF NOT EXISTS research_opportunities (
  id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  title           TEXT NOT NULL,
  thesis          TEXT,
  composite_score REAL NOT NULL,
  signal_ids      TEXT[] DEFAULT '{}',
  detectors_hit   TEXT[] DEFAULT '{}',
  topics          TEXT[] DEFAULT '{}',
  target_venue    TEXT,
  portfolio_fit   REAL DEFAULT 0,
  timing_urgency  REAL DEFAULT 0,
  venue_receptivity REAL DEFAULT 0,
  rationale       TEXT,
  batch_date      DATE NOT NULL DEFAULT CURRENT_DATE,
  status          TEXT DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'accepted', 'rejected')),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_opportunities_batch ON research_opportunities (batch_date DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_score ON research_opportunities (composite_score DESC);
