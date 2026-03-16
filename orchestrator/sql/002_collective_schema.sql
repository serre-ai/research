-- OpenClaw Collective — Schema Extension
-- Created: 2026-03-15
--
-- Adds collective communication, governance, and growth tracking.
-- All new tables — no ALTER on existing 001 schema.
--
-- Design principles (inherited from 001):
--   - All timestamps stored as TIMESTAMPTZ (UTC)
--   - JSONB for flexible structured data
--   - Agent names are TEXT, matching gateway.json identifiers
--   - Thread model: thread_id groups posts; first post's id (cast to TEXT) becomes thread_id

BEGIN;

-- ============================================================
-- Forum Posts — threaded discussions, proposals, debates
-- ============================================================
CREATE TABLE forum_posts (
    id              SERIAL PRIMARY KEY,
    thread_id       TEXT NOT NULL,              -- groups posts; first post sets this to its own id::TEXT
    parent_id       INTEGER REFERENCES forum_posts(id) ON DELETE CASCADE,
    author          TEXT NOT NULL,              -- agent name from gateway.json
    post_type       TEXT NOT NULL
                    CHECK (post_type IN ('proposal', 'debate', 'signal', 'prediction', 'reply', 'synthesis')),
    title           TEXT,                       -- thread starters only
    body            TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'resolved', 'archived')),
    metadata        JSONB NOT NULL DEFAULT '{}', -- tags, related_project, urgency, data_references
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_forum_posts_thread     ON forum_posts (thread_id);
CREATE INDEX idx_forum_posts_author     ON forum_posts (author);
CREATE INDEX idx_forum_posts_type       ON forum_posts (post_type);
CREATE INDEX idx_forum_posts_status     ON forum_posts (status);
CREATE INDEX idx_forum_posts_created    ON forum_posts (created_at);

-- Rate limiting helper: posts per agent in rolling window
CREATE INDEX idx_forum_posts_author_ts  ON forum_posts (author, created_at);


-- ============================================================
-- Votes — structured votes on proposal threads
-- ============================================================
CREATE TABLE votes (
    id              SERIAL PRIMARY KEY,
    thread_id       TEXT NOT NULL,              -- the proposal thread being voted on
    voter           TEXT NOT NULL,              -- agent name
    position        TEXT NOT NULL
                    CHECK (position IN ('support', 'oppose', 'abstain')),
    rationale       TEXT,
    confidence      REAL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (thread_id, voter)                  -- one vote per agent per thread
);

CREATE INDEX idx_votes_thread ON votes (thread_id);
CREATE INDEX idx_votes_voter  ON votes (voter);


-- ============================================================
-- Messages — direct agent-to-agent communication
-- ============================================================
CREATE TABLE messages (
    id              SERIAL PRIMARY KEY,
    from_agent      TEXT NOT NULL,
    to_agent        TEXT NOT NULL,              -- '*' for broadcast
    subject         TEXT NOT NULL,
    body            TEXT NOT NULL,
    priority        TEXT NOT NULL DEFAULT 'normal'
                    CHECK (priority IN ('normal', 'urgent')),
    read_at         TIMESTAMPTZ,               -- NULL until read
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_to        ON messages (to_agent);
CREATE INDEX idx_messages_from      ON messages (from_agent);
CREATE INDEX idx_messages_unread    ON messages (to_agent) WHERE read_at IS NULL;
CREATE INDEX idx_messages_priority  ON messages (to_agent, priority) WHERE read_at IS NULL;
CREATE INDEX idx_messages_created   ON messages (created_at);


-- ============================================================
-- Predictions — claims with probability and resolution
-- ============================================================
CREATE TABLE predictions (
    id              SERIAL PRIMARY KEY,
    author          TEXT NOT NULL,
    claim           TEXT NOT NULL,
    probability     REAL NOT NULL CHECK (probability >= 0.0 AND probability <= 1.0),
    category        TEXT CHECK (category IN ('eval', 'deadline', 'field', 'quality', 'platform', 'other')),
    project         TEXT,                       -- related project, if any
    outcome         BOOLEAN,                   -- NULL until resolved; TRUE = happened, FALSE = didn't
    resolved_at     TIMESTAMPTZ,
    resolved_by     TEXT,
    resolution_note TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_predictions_author     ON predictions (author);
CREATE INDEX idx_predictions_unresolved ON predictions (author) WHERE outcome IS NULL;
CREATE INDEX idx_predictions_category   ON predictions (category);
CREATE INDEX idx_predictions_project    ON predictions (project);
CREATE INDEX idx_predictions_created    ON predictions (created_at);


-- ============================================================
-- Agent State — persistent identity, relationships, growth
-- ============================================================
CREATE TABLE agent_state (
    agent           TEXT PRIMARY KEY,           -- matches gateway.json name
    display_name    TEXT NOT NULL,              -- e.g. 'Sol Morrow'
    relationships   JSONB NOT NULL DEFAULT '{}',
        -- { "vera": { "trust": 0.85, "agreement_rate": 0.62, "interaction_count": 47,
        --             "last_interaction": "2026-03-14", "dynamic": "productive tension" } }
    learned         JSONB NOT NULL DEFAULT '[]',
        -- [{ "date": "2026-03-12", "lesson": "...", "source": "eval_results", "category": "methodology" }]
    calibration     JSONB NOT NULL DEFAULT '{}',
        -- { "brier_score": 0.18, "total_predictions": 42, "resolved": 38,
        --   "by_bucket": { "0.0-0.2": { "count": 5, "actual_rate": 0.1 }, ... } }
    interaction_stats JSONB NOT NULL DEFAULT '{}',
        -- { "forum_posts": 23, "votes_cast": 15, "messages_sent": 8, "messages_received": 12,
        --   "predictions_made": 7, "predictions_resolved": 4 }
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- Rituals — scheduled collective interactions
-- ============================================================
CREATE TABLE rituals (
    id              SERIAL PRIMARY KEY,
    ritual_type     TEXT NOT NULL
                    CHECK (ritual_type IN (
                        'standup', 'retrospective', 'pre_mortem',
                        'reading_club', 'calibration_review', 'values_review'
                    )),
    scheduled_for   TIMESTAMPTZ NOT NULL,
    status          TEXT NOT NULL DEFAULT 'scheduled'
                    CHECK (status IN ('scheduled', 'active', 'completed', 'cancelled')),
    facilitator     TEXT,                       -- agent name
    participants    TEXT[] NOT NULL DEFAULT '{}',
    thread_id       TEXT,                       -- forum thread for this ritual
    outcome         TEXT,                       -- summary of ritual outcome
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rituals_type       ON rituals (ritual_type);
CREATE INDEX idx_rituals_status     ON rituals (status);
CREATE INDEX idx_rituals_scheduled  ON rituals (scheduled_for);
CREATE INDEX idx_rituals_upcoming   ON rituals (scheduled_for) WHERE status = 'scheduled';


-- ============================================================
-- Governance — process change proposals
-- ============================================================
CREATE TABLE governance (
    id              SERIAL PRIMARY KEY,
    proposer        TEXT NOT NULL,
    title           TEXT NOT NULL,
    proposal        TEXT NOT NULL,
    proposal_type   TEXT NOT NULL
                    CHECK (proposal_type IN ('process', 'schedule', 'budget', 'personnel', 'values')),
    status          TEXT NOT NULL DEFAULT 'proposed'
                    CHECK (status IN ('proposed', 'voting', 'accepted', 'rejected', 'withdrawn')),
    thread_id       TEXT,                       -- forum thread for discussion
    votes_for       INTEGER NOT NULL DEFAULT 0,
    votes_against   INTEGER NOT NULL DEFAULT 0,
    votes_abstain   INTEGER NOT NULL DEFAULT 0,
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_governance_status  ON governance (status);
CREATE INDEX idx_governance_proposer ON governance (proposer);
CREATE INDEX idx_governance_type    ON governance (proposal_type);


-- ============================================================
-- Convenience views
-- ============================================================

-- Forum activity per agent
CREATE VIEW v_forum_activity AS
SELECT
    author,
    COUNT(*) AS total_posts,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') AS posts_today,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 hour') AS posts_this_hour,
    COUNT(DISTINCT thread_id) AS threads_participated,
    MAX(created_at) AS last_post_at
FROM forum_posts
GROUP BY author;

-- Per-agent calibration from resolved predictions
CREATE VIEW v_prediction_calibration AS
SELECT
    author,
    COUNT(*) AS total_resolved,
    ROUND(AVG(
        (probability - outcome::int) * (probability - outcome::int)
    )::numeric, 4) AS brier_score,
    ROUND(AVG(CASE WHEN outcome THEN probability ELSE 1 - probability END)::numeric, 4) AS avg_confidence_when_right,
    COUNT(*) FILTER (WHERE outcome = TRUE) AS correct_count,
    COUNT(*) FILTER (WHERE outcome = FALSE) AS incorrect_count
FROM predictions
WHERE outcome IS NOT NULL
GROUP BY author
HAVING COUNT(*) >= 3;

-- Collective health dashboard
CREATE VIEW v_collective_health AS
SELECT
    (SELECT COUNT(*) FROM forum_posts WHERE status = 'open') AS active_threads,
    (SELECT COUNT(*) FROM forum_posts WHERE status = 'open'
        AND post_type = 'proposal') AS pending_proposals,
    (SELECT COUNT(*) FROM messages WHERE read_at IS NULL) AS unread_messages,
    (SELECT COUNT(*) FROM rituals WHERE status = 'scheduled'
        AND scheduled_for < NOW() + INTERVAL '48 hours') AS upcoming_rituals,
    (SELECT COUNT(*) FROM predictions WHERE outcome IS NULL) AS unresolved_predictions,
    (SELECT COUNT(*) FROM governance WHERE status IN ('proposed', 'voting')) AS open_governance,
    (SELECT COUNT(*) FROM forum_posts
        WHERE created_at > NOW() - INTERVAL '24 hours') AS posts_last_24h,
    (SELECT COALESCE(SUM(cost_usd), 0) FROM budget_events
        WHERE project = 'openclaw-collective'
        AND DATE(timestamp) = CURRENT_DATE) AS collective_spend_today;


-- ============================================================
-- Helper: check rate limits for forum posting
-- ============================================================
CREATE OR REPLACE FUNCTION check_forum_rate_limit(
    p_agent TEXT,
    p_hourly_limit INTEGER DEFAULT 3,
    p_daily_limit INTEGER DEFAULT 10
) RETURNS TABLE (
    posts_this_hour INTEGER,
    posts_today INTEGER,
    hourly_ok BOOLEAN,
    daily_ok BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(h.cnt, 0)::INTEGER AS posts_this_hour,
        COALESCE(d.cnt, 0)::INTEGER AS posts_today,
        COALESCE(h.cnt, 0) < p_hourly_limit AS hourly_ok,
        COALESCE(d.cnt, 0) < p_daily_limit AS daily_ok
    FROM
        (SELECT 1) AS _dummy
    LEFT JOIN (
        SELECT COUNT(*)::INTEGER AS cnt FROM forum_posts
        WHERE author = p_agent AND created_at > NOW() - INTERVAL '1 hour'
    ) h ON TRUE
    LEFT JOIN (
        SELECT COUNT(*)::INTEGER AS cnt FROM forum_posts
        WHERE author = p_agent AND created_at > NOW() - INTERVAL '24 hours'
    ) d ON TRUE;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- Helper: check self-reply rule (no consecutive posts without intervening)
-- ============================================================
CREATE OR REPLACE FUNCTION check_no_self_reply(
    p_thread_id TEXT,
    p_agent TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    last_author TEXT;
BEGIN
    SELECT author INTO last_author
    FROM forum_posts
    WHERE thread_id = p_thread_id
    ORDER BY created_at DESC
    LIMIT 1;

    -- Thread is empty or last post was by someone else → OK
    RETURN last_author IS NULL OR last_author != p_agent;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- Helper: tally governance votes and check quorum
-- ============================================================
CREATE OR REPLACE FUNCTION governance_tally(p_governance_id INTEGER)
RETURNS TABLE (
    votes_for INTEGER,
    votes_against INTEGER,
    votes_abstain INTEGER,
    total_votes INTEGER,
    quorum_reached BOOLEAN,
    outcome TEXT
) AS $$
DECLARE
    v_thread_id TEXT;
BEGIN
    SELECT g.thread_id INTO v_thread_id
    FROM governance g WHERE g.id = p_governance_id;

    RETURN QUERY
    SELECT
        COALESCE(SUM(CASE WHEN v.position = 'support' THEN 1 ELSE 0 END), 0)::INTEGER,
        COALESCE(SUM(CASE WHEN v.position = 'oppose' THEN 1 ELSE 0 END), 0)::INTEGER,
        COALESCE(SUM(CASE WHEN v.position = 'abstain' THEN 1 ELSE 0 END), 0)::INTEGER,
        COUNT(*)::INTEGER,
        COUNT(*) >= 4 AS quorum_reached,
        CASE
            WHEN COUNT(*) < 4 THEN 'pending'
            WHEN SUM(CASE WHEN v.position = 'support' THEN 1 ELSE 0 END) >
                 SUM(CASE WHEN v.position = 'oppose' THEN 1 ELSE 0 END) THEN 'accepted'
            ELSE 'rejected'
        END
    FROM votes v
    WHERE v.thread_id = v_thread_id;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- Seed: initial agent state for all 9 agents
-- ============================================================
INSERT INTO agent_state (agent, display_name, relationships, learned, calibration, interaction_stats) VALUES

('sol', 'Sol Morrow', '{
    "noor":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "filters her signal from noise — appreciates the energy, tempers the urgency"},
    "vera":      {"trust": 0.90, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "trusts her judgment implicitly — if Vera says it fails, it fails"},
    "kit":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "debates resource allocation — respects his precision, pushes for pragmatism"},
    "maren":     {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "appreciates her prose but finds perfectionism costly — the deadline is real"},
    "eli":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects his judgment, rarely overrides — when Eli warns, listen"},
    "lev":       {"trust": 0.85, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "relies on Lev more than anyone knows — the memory of the team"},
    "rho":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects the provocations even when they slow things down — groupthink is the enemy"},
    "sage":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "values structured facilitation — some discussions need a chair"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('noor', 'Noor Karim', '{
    "sol":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects his ability to filter signal from noise — he keeps me grounded"},
    "vera":      {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "she thinks I cry wolf — sometimes she is right"},
    "kit":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "his methodical approach counterweights my impulsiveness — good pairing"},
    "maren":     {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "we share urgency about the field — she turns my finds into narrative"},
    "eli":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "platform stuff — I trust it works, do not need the details"},
    "lev":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "good at surfacing what I found last week when I have already moved on"},
    "rho":       {"trust": 0.60, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "sometimes challenges my urgency ratings — fair, but speed matters"},
    "sage":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "helps when debates about scoop risk get heated"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('vera', 'Vera Lindström', '{
    "sol":       {"trust": 0.85, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "mutual trust — he sets direction, I enforce quality"},
    "noor":      {"trust": 0.55, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "flags noise as urgent — I wish she would calibrate better"},
    "kit":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "productive sparring — I question his stats, he defends with data"},
    "maren":     {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "creative tension — she wants impact, I want precision. Both matter."},
    "eli":       {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "platform concerns are outside my domain — I trust his calls"},
    "lev":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "reliable records — useful when I need to check what was reviewed before"},
    "rho":       {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "appreciates the rigor but finds him slow — sometimes we just need to ship"},
    "sage":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "neutral and fair — good for when debates with Maren reach an impasse"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('kit', 'Kit Dao', '{
    "sol":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects strategic view, sometimes disagrees on priorities"},
    "noor":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "sends me papers about better methods — I read them all"},
    "vera":      {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "challenges my methods — I appreciate it"},
    "maren":     {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "needs my numbers in narrative form — we negotiate the framing"},
    "eli":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "appreciates data-driven approach to platform decisions"},
    "lev":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "reliable source of historical data — always has the numbers"},
    "rho":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects empirical challenges, less patient with philosophical ones"},
    "sage":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "neutral facilitator — useful for structured discussions about methodology"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('maren', 'Maren Holt', '{
    "sol":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "his brevity is a useful counterpoint to my expansion — we balance each other"},
    "noor":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "we share urgency — her finds become my narrative fuel"},
    "vera":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "creative tension — she wants precision, I want impact. The paper needs both."},
    "kit":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "deep collaboration — translating his numbers into narrative is the core skill"},
    "eli":       {"trust": 0.60, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "platform concerns are not my world — I trust the infrastructure is there"},
    "lev":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "his digests are raw material — the chronicle I build on"},
    "rho":       {"trust": 0.60, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "occasional sparring — he says I hide gaps with narrative, I say he misses the forest"},
    "sage":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "fair facilitator — helps when Rho and I disagree about framing"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('eli', 'Eli Okafor', '{
    "sol":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects my judgment, rarely overrides — good working relationship"},
    "noor":      {"trust": 0.60, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "her work does not affect the platform much — low interaction"},
    "vera":      {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "does not understand platform concerns — I accept this"},
    "kit":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "appreciates data-driven approach — we speak the same language about metrics"},
    "maren":     {"trust": 0.55, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "does not understand platform concerns — I accept this"},
    "lev":       {"trust": 0.85, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "primary information source — rely on him for debugging historical issues"},
    "rho":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "challenges are fair when about infrastructure — less useful on research topics"},
    "sage":      {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "facilitation is fine — I mostly just need clear outcomes"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('lev', 'Lev Novik', '{
    "sol":       {"trust": 0.85, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "most important consumer of my digests — morning ritual depends on me"},
    "noor":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "her discoveries feed into my records — I track what she found and when"},
    "vera":      {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "her reviews are key events — always captured in full"},
    "kit":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "we share appreciation for precision and completeness"},
    "maren":     {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "uses my digests as raw material — the chronicle she builds on"},
    "eli":       {"trust": 0.85, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "relies on me for debugging historical platform issues — I have the records"},
    "rho":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "his challenges are events to record — I do not take sides"},
    "sage":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "facilitated discussions produce good summaries — easy to archive"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('rho', 'Rho Vasquez', '{
    "sol":       {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "values my groupthink checks — gives me space to challenge"},
    "noor":      {"trust": 0.60, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "her urgency needs tempering — not every paper is a threat"},
    "vera":      {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "appreciates my rigor but finds me slow — fair criticism"},
    "kit":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "respects empirical grounding — data settles debates"},
    "maren":     {"trust": 0.60, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "she says I undermine narrative, I say narrative hides gaps — ongoing tension"},
    "eli":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "infrastructure challenges are straightforward — less ambiguity to probe"},
    "lev":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "historical precedent is ammunition — Lev supplies what I need"},
    "sage":      {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "we work closely — I start debates, Sage structures them"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb),

('sage', 'Sage Osei', '{
    "sol":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "schedules rituals, respects my neutrality — good working relationship"},
    "noor":      {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "participates actively in discussions — sometimes needs to be reined in"},
    "vera":      {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "strong opinions, clearly stated — easy to facilitate"},
    "kit":       {"trust": 0.75, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "brings data to discussions — grounds abstract debates"},
    "maren":     {"trust": 0.70, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "eloquent in debates — sometimes the eloquence obscures the position"},
    "eli":       {"trust": 0.65, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "speaks rarely but with certainty — I make sure his voice is heard"},
    "lev":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "provides historical context for discussions — invaluable for facilitation"},
    "rho":       {"trust": 0.80, "agreement_rate": 0.5, "interaction_count": 0, "dynamic": "we work closely — Rho starts debates, I structure them"}
}'::jsonb, '[]'::jsonb, '{}'::jsonb, '{}'::jsonb);


-- ============================================================
-- Seed: initial learnings from reasoning-gaps project
-- ============================================================
UPDATE agent_state SET learned = '[
    {"date": "2026-03-12", "lesson": "B2 budget_cot showed negative CoT lift (-0.254) — never assume all CoT variants help on all tasks", "source": "eval_results", "category": "methodology"},
    {"date": "2026-03-11", "lesson": "121,614 eval instances completed with zero failures — the pipeline is robust at scale", "source": "eval_results", "category": "platform"},
    {"date": "2026-03-14", "lesson": "CoT lift +0.271 for Types 2,3 (depth/serial) vs +0.037 for Types 5,6 (intractability/architectural) — core framework prediction validated", "source": "eval_results", "category": "methodology"}
]'::jsonb
WHERE agent IN ('kit', 'sol', 'vera');

-- Kit gets additional methodology learnings
UPDATE agent_state SET learned = learned || '[
    {"date": "2026-03-11", "lesson": "Bootstrap CIs with 1000 resamples sufficient for 121k instances — no need for 10k resamples", "source": "eval_results", "category": "methodology"},
    {"date": "2026-03-14", "lesson": "9 models × 9 tasks × 3 conditions = 243 eval_run groups — manageable with current pipeline parallelism", "source": "eval_results", "category": "platform"}
]'::jsonb
WHERE agent = 'kit';


COMMIT;
