-- Topic graph for research landscape mapping

CREATE TABLE IF NOT EXISTS research_topics (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    label           TEXT NOT NULL,
    description     TEXT,
    embedding       vector(1024),
    paper_count     INTEGER DEFAULT 0,
    claim_count     INTEGER DEFAULT 0,
    velocity        REAL DEFAULT 0,
    batch_date      DATE DEFAULT CURRENT_DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS topic_edges (
    source_id       TEXT NOT NULL REFERENCES research_topics(id) ON DELETE CASCADE,
    target_id       TEXT NOT NULL REFERENCES research_topics(id) ON DELETE CASCADE,
    strength        REAL DEFAULT 0,
    edge_type       TEXT DEFAULT 'co_occurrence',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (source_id, target_id)
);

CREATE INDEX IF NOT EXISTS idx_topics_velocity ON research_topics (velocity DESC);
CREATE INDEX IF NOT EXISTS idx_topics_batch ON research_topics (batch_date DESC);

-- Author/research group tables
CREATE TABLE IF NOT EXISTS research_groups (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    author_names    TEXT[] NOT NULL,
    paper_count     INTEGER DEFAULT 0,
    topic_ids       TEXT[] DEFAULT '{}',
    first_seen      TIMESTAMPTZ,
    last_seen       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS group_topic_edges (
    group_id        TEXT NOT NULL REFERENCES research_groups(id) ON DELETE CASCADE,
    topic_id        TEXT NOT NULL REFERENCES research_topics(id) ON DELETE CASCADE,
    paper_count     INTEGER DEFAULT 0,
    PRIMARY KEY (group_id, topic_id)
);
